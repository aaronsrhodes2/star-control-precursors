"""Save/load + campaign management.

Aaron 2026-05-18: "Fix save/load and add to the main menu. You simply
have campaigns. The game auto-saves every minute, hopefully it can do
it without interrupting the game, so our time drive can go back 5
saves to the closest save to 5 minutes ago."

## Design

- **Campaign** = a named save dossier. The player creates one when
  starting a new game; all auto-saves write into that campaign's dir.
- **Save file** = JSON dump of game state at one point in time. Each
  campaign holds a rolling history of recent saves; the newest 64 are
  kept, older ones pruned automatically (so 64 × 60s = ~64 minutes
  of rewindable history at the auto-save cadence).
- **Auto-save** fires every `AUTO_SAVE_INTERVAL_S` (60 seconds of
  real time). The serialization is on the main thread (cheap — game
  state is small dicts and primitives); disk I/O is dispatched to a
  daemon thread so a slow disk doesn't hitch a frame.
- **Time Drive integration**: rewind = restore the save closest to
  5 minutes (300 s) ago by timestamp. Aaron's phrasing: "5 saves
  back to the closest save to 5 minutes ago".

## File layout

```
~/.scz/campaigns/
├── _registry.json           # active-campaign pointer + creation timestamps
├── <campaign_name>/
│   ├── meta.json            # display name, created/updated timestamps
│   ├── save_<unix_ms>.json  # rolling auto-saves (newest 64 kept)
│   └── save_<unix_ms>.json
```

Campaign names are user-typed and sanitized for filesystem safety.
"""

from __future__ import annotations

import json
import os
import re
import threading
import time
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from scz.engine.game import Game


# Tunables.
AUTO_SAVE_INTERVAL_S: float = 60.0     # Aaron's spec: "auto-saves every minute"
# Aaron 2026-05-18 amendment: "drops off after 20min of saves, auto-deleting
# the past so you are stuck within the last 20 minutes of time."
SAVES_PER_CAMPAIGN: int = 20           # 20 × 60s = 20 minutes of history

# Thumbnail dimensions for the screen-grab preview saved alongside each
# JSON. ~16:9 aspect at 256 wide. ~5-10KB on disk per PNG.
THUMB_W: int = 256
THUMB_H: int = 144

# Default cursor target when opening the save scrubber via Time Drive
# (Aaron 2026-05-18: "the time drive literally is 'load game' and lets
# you pick from the last 5 minutes or older"). The scrubber starts
# focused on the save closest to this many seconds ago.
TIME_DRIVE_DEFAULT_CURSOR_S: float = 300.0
# The most-recent N seconds of saves are BARRED from the load picker
# (Aaron 2026-05-18 amendment: "we bar the last 4 minutes of saves
# from you... we are actively encouraging save-scumming with the time
# drive, don't fight what people want"). Save-scumming is the feature,
# not the bug — the lockout just gates TRIVIAL save-scumming (undoing
# a 30-second mistake) while permitting MEANINGFUL rewinds (undoing
# a 5-10 minute bad decision tree). The locked saves still exist on
# disk and in the scrubber list (greyed); they just can't be picked.
# Continue (one-shot resume from main menu) is exempt — only the
# scrubber UI enforces the lockout.
LOAD_LOCKOUT_S: float = 240.0


def _campaign_root() -> Path:
    """Top-level directory for all campaigns. Created if absent."""
    root = Path.home() / ".scz" / "campaigns"
    root.mkdir(parents=True, exist_ok=True)
    return root


def _sanitize_name(name: str) -> str:
    """Sanitize a user-typed campaign name to a filesystem-safe slug.
    Empty / all-stripped results in 'campaign'.
    """
    safe = re.sub(r"[^A-Za-z0-9_\- ]+", "", name).strip()
    safe = re.sub(r"\s+", "_", safe)
    return safe or "campaign"


# ---------------------------------------------------------------------------
# Game-state serialization
# ---------------------------------------------------------------------------

def serialize_game(game: "Game") -> dict[str, Any]:
    """Take a complete snapshot of the player-state-relevant `Game`
    fields. Returns a dict that can be passed to `restore_game()` later
    (in this process or after a load from disk).

    Excludes engine-side ephemera (pygame surfaces, the current scene,
    test harness, time-drive snapshots — those reset on restore).
    """
    return {
        # Schema versioning so future changes can migrate old saves.
        "schema_version": 1,
        # Wall-clock timestamp at save time (used by Time Drive to
        # pick the right save for "5 minutes ago" rewind).
        "saved_at_monotonic": time.monotonic(),
        "saved_at_unix": time.time(),
        "frame_count": int(game.frame_count),
        # Persistent state.
        "flags": dict(game.flags),
        "cargo": dict(game.cargo),
        "credits": int(game.credits),
        "ship_modules": dict(game.ship_modules),
        "uninstalled_modules": dict(game.uninstalled_modules),
        "fleet": list(game.fleet),
        "schematics": sorted(game.schematics),
        "consumed_schematics": sorted(game.consumed_schematics),
        # Scene identity at save time (for "continue where you left
        # off" support). Saves the class name; restore_game looks it
        # up via a SCENE_REGISTRY rather than picking arbitrary
        # scenes — only "safe" scenes can be the resume target.
        "current_scene_class": (
            type(game.current_scene).__name__
            if game.current_scene is not None
            else None
        ),
    }


def restore_game(game: "Game", state: dict[str, Any]) -> None:
    """Apply a serialized state dict back onto `game`. Replaces all
    persistent fields. Does NOT touch the current scene — caller is
    responsible for calling `game.set_scene(...)` to drop the player
    into the right place (typically Station after a load).
    """
    schema = state.get("schema_version", 0)
    if schema not in (1,):
        # Forward-compat: silently accept; migration path TBD.
        pass
    game.flags = dict(state.get("flags", {}))
    game.cargo = dict(state.get("cargo", {
        "COMMON": 0, "USEFUL": 0, "BIO": 0, "ENERGY": 0,
    }))
    game.credits = int(state.get("credits", 0))
    # Module restore — migrate legacy 7-slot dict (hull/drive/weapon/
    # sensor/field/crew_1/crew_2) onto the new 12-generic-slot model.
    # Pre-refactor saves had a 7-key dict; post-refactor saves have a
    # 12-key dict with slot_1..slot_12. This block accepts either.
    from scz.content.modules import SLOTS, LEGACY_SLOT_NAMES
    raw_mods = state.get("ship_modules", {}) or {}
    new_mods: dict[str, str | None] = {slot: None for slot in SLOTS}
    legacy_present = any(k in raw_mods for k in LEGACY_SLOT_NAMES)
    if legacy_present:
        # Legacy save — map the 7 named slots to slot_1..slot_7 in order.
        for i, legacy in enumerate(LEGACY_SLOT_NAMES):
            if i < len(SLOTS):
                new_mods[SLOTS[i]] = raw_mods.get(legacy)
    else:
        # New-format save — adopt directly.
        for slot, mid in raw_mods.items():
            if slot in new_mods:
                new_mods[slot] = mid
    game.ship_modules = new_mods
    game.uninstalled_modules = dict(state.get("uninstalled_modules", {}))
    game.fleet = list(state.get("fleet", ["FURLING_SCOUT"]))
    game.schematics = set(state.get("schematics", []))
    game.consumed_schematics = set(state.get("consumed_schematics", []))
    game.frame_count = int(state.get("frame_count", 0))


# ---------------------------------------------------------------------------
# Campaign manager
# ---------------------------------------------------------------------------

@dataclass
class CampaignInfo:
    """Lightweight metadata about a single campaign on disk."""
    name: str                 # display name (user-typed)
    slug: str                 # filesystem-safe directory name
    created_unix: float       # when the campaign was started
    updated_unix: float       # when the most-recent save was written
    save_count: int           # current number of save files

    def updated_ago_human(self) -> str:
        """Human-readable 'how long ago was the last save'."""
        delta = max(0.0, time.time() - self.updated_unix)
        if delta < 60:
            return f"{int(delta)}s ago"
        if delta < 3600:
            return f"{int(delta / 60)}m ago"
        if delta < 86400:
            return f"{int(delta / 3600)}h ago"
        return f"{int(delta / 86400)}d ago"


@dataclass
class SaveInfo:
    """One individual minute-save within a campaign. Used by the save
    scrubber UI to show thumbnails + timestamps and to identify which
    save the player picks to restore.
    """
    slug: str                 # campaign slug
    save_path: Path           # .json file
    thumb_path: Path          # .png sibling (may not exist on disk)
    saved_unix: float         # wall-clock when this save was written

    def age_seconds(self) -> float:
        """Wall-clock seconds since this save was written."""
        return max(0.0, time.time() - self.saved_unix)

    def age_human(self) -> str:
        """Compact 'Nm ago' / 'Ns ago' label for the scrubber UI."""
        delta = self.age_seconds()
        if delta < 60:
            return f"{int(delta)}s ago"
        if delta < 3600:
            return f"{int(delta / 60)}m ago"
        if delta < 86400:
            return f"{int(delta / 3600)}h ago"
        return f"{int(delta / 86400)}d ago"

    def is_loadable(self) -> bool:
        """True if this save is old enough to be selectable in the
        scrubber. Saves younger than LOAD_LOCKOUT_S are visible but
        greyed (Aaron 2026-05-18: trivial save-scumming is gated;
        meaningful rewinds are encouraged).
        """
        return self.age_seconds() >= LOAD_LOCKOUT_S

    def time_until_loadable(self) -> float:
        """Seconds until this save becomes loadable. 0 if already
        loadable. Used by the scrubber to show 'unlocks in Nm' tags
        on the greyed rows."""
        if self.is_loadable():
            return 0.0
        return LOAD_LOCKOUT_S - self.age_seconds()


class CampaignManager:
    """Owns campaign discovery + auto-save scheduling.

    A `Game` holds exactly one `CampaignManager`. The manager is
    created at game start with no active campaign; the main menu's
    'New' / 'Load' / 'Continue' flow sets the active campaign. Once
    active, the per-frame `tick(dt, game)` call schedules auto-saves
    every `AUTO_SAVE_INTERVAL_S`.

    Disk writes are dispatched to a daemon thread so a slow disk
    doesn't stall the render loop. Serialization (the dict build)
    happens on the calling thread — it's cheap and gives a consistent
    snapshot of game state without needing locks.
    """

    def __init__(self) -> None:
        self.active_slug: str | None = None
        # Seconds of game time since the last auto-save fired. Reset
        # whenever a save is queued. Not the wall-clock — uses game
        # `dt` so test-mode speed-multipliers don't burn through
        # 1000 saves a minute.
        self._time_since_save: float = 0.0
        # Pending in-memory save dicts (newest first) — kept in addition
        # to the on-disk file so Time Drive doesn't have to round-trip
        # through JSON to pick a rewind target.
        self._save_stack: list[tuple[float, dict[str, Any]]] = []
        # Worker thread for disk writes. Reused across saves.
        self._lock = threading.Lock()
        self._pending_writes: list[tuple[Path, dict[str, Any]]] = []
        self._worker: threading.Thread | None = None
        self._worker_wake = threading.Event()
        self._worker_stop = False

    # ---- Active campaign management ----

    def set_active(self, slug: str | None) -> None:
        """Activate a campaign by slug, or None to deactivate."""
        self.active_slug = slug
        self._time_since_save = 0.0
        self._save_stack = []
        # On entering an active campaign, prime the in-memory save
        # stack from the most-recent on-disk saves so Time Drive
        # rewinds work immediately after a Load (without waiting a
        # full minute for the first new auto-save).
        if slug is not None:
            self._prime_save_stack_from_disk(slug)

    def has_active(self) -> bool:
        return self.active_slug is not None

    def _campaign_dir(self, slug: str) -> Path:
        return _campaign_root() / slug

    # ---- Campaign discovery / creation ----

    def list_campaigns(self) -> list[CampaignInfo]:
        """Return all campaigns sorted by most-recently-updated first."""
        root = _campaign_root()
        out: list[CampaignInfo] = []
        for child in root.iterdir():
            if not child.is_dir():
                continue
            meta_path = child / "meta.json"
            if not meta_path.exists():
                continue
            try:
                meta = json.loads(meta_path.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                continue
            saves = list(child.glob("save_*.json"))
            out.append(CampaignInfo(
                name=str(meta.get("display_name", child.name)),
                slug=child.name,
                created_unix=float(meta.get("created_unix", 0.0)),
                updated_unix=float(meta.get("updated_unix", 0.0)),
                save_count=len(saves),
            ))
        out.sort(key=lambda c: c.updated_unix, reverse=True)
        return out

    def create_campaign(self, display_name: str) -> str:
        """Create a fresh campaign dir with meta.json. Returns its slug.
        Appends a numeric suffix if the slug already exists so the user
        never overwrites another campaign by accidental name collision.
        """
        base_slug = _sanitize_name(display_name)
        slug = base_slug
        n = 2
        while (_campaign_root() / slug).exists():
            slug = f"{base_slug}_{n}"
            n += 1
        cdir = _campaign_root() / slug
        cdir.mkdir(parents=True, exist_ok=False)
        now = time.time()
        meta = {
            "display_name": display_name.strip() or slug,
            "slug": slug,
            "created_unix": now,
            "updated_unix": now,
            "schema_version": 1,
        }
        (cdir / "meta.json").write_text(
            json.dumps(meta, indent=2), encoding="utf-8",
        )
        return slug

    def delete_campaign(self, slug: str) -> None:
        """Delete an entire campaign dir + all its saves + thumbnails.
        Tolerates missing files; never raises."""
        cdir = self._campaign_dir(slug)
        if not cdir.exists():
            return
        for f in cdir.iterdir():
            try:
                f.unlink()
            except OSError:
                pass
        try:
            cdir.rmdir()
        except OSError:
            pass
        if self.active_slug == slug:
            self.active_slug = None
            self._save_stack = []

    # ---- Auto-save scheduling ----

    def tick(self, dt: float, game: "Game") -> None:
        """Per-frame call from Game.run. Increments the save-clock and
        fires an auto-save when the interval elapses. No-op if no
        active campaign."""
        if self.active_slug is None:
            return
        self._time_since_save += dt
        if self._time_since_save >= AUTO_SAVE_INTERVAL_S:
            self._time_since_save = 0.0
            self.snapshot(game)

    def snapshot(self, game: "Game") -> None:
        """Take a snapshot RIGHT NOW (synchronous serialization on
        calling thread; async disk write). Used by the tick-driven
        auto-save AND can be called by player-initiated saves.

        Captures a 256×144 thumbnail of the current screen for the
        save scrubber UI (Aaron 2026-05-18). Thumbnail capture +
        downscale happens on the calling thread (cheap — ~1ms); the
        PNG write is dispatched to the daemon worker.
        """
        if self.active_slug is None:
            return
        state = serialize_game(game)
        # Capture screen thumbnail. Wrap in try/except — if the game
        # has no display (headless tests) or pygame error, we just
        # skip the thumbnail and keep the JSON save.
        thumb_surface = None
        try:
            import pygame as _pg
            screen = getattr(game, "screen", None)
            if screen is not None:
                # `.copy()` detaches the thumbnail from the display's
                # pixel format so the worker thread can safely save it.
                thumb_surface = _pg.transform.smoothscale(
                    screen, (THUMB_W, THUMB_H),
                ).copy()
        except Exception:
            thumb_surface = None
        # Push into in-memory stack (newest first) for the scrubber.
        ts = time.monotonic()
        self._save_stack.insert(0, (ts, state))
        if len(self._save_stack) > SAVES_PER_CAMPAIGN:
            self._save_stack = self._save_stack[:SAVES_PER_CAMPAIGN]
        # Queue for async disk write.
        unix_ms = int(state["saved_at_unix"] * 1000)
        cdir = self._campaign_dir(self.active_slug)
        save_path = cdir / f"save_{unix_ms}.json"
        thumb_path = cdir / f"save_{unix_ms}.png"
        with self._lock:
            self._pending_writes.append((save_path, state, thumb_path, thumb_surface))
        self._ensure_worker_running()

    # ---- Disk-write worker thread ----

    def _ensure_worker_running(self) -> None:
        """Spawn the daemon disk-writer thread if not already running.
        Daemon so Python exit doesn't block on pending writes."""
        if self._worker is not None and self._worker.is_alive():
            self._worker_wake.set()
            return
        self._worker_stop = False
        self._worker = threading.Thread(
            target=self._worker_loop,
            name="scz-save-writer",
            daemon=True,
        )
        self._worker.start()
        self._worker_wake.set()

    def _worker_loop(self) -> None:
        """Background writer. Wakes when `_worker_wake` is set, drains
        the pending-writes queue (JSON + PNG thumbnail), sleeps until
        next wake. Exits when `_worker_stop` is set."""
        while not self._worker_stop:
            self._worker_wake.wait(timeout=2.0)
            self._worker_wake.clear()
            with self._lock:
                pending = self._pending_writes
                self._pending_writes = []
            for save_path, state, thumb_path, thumb_surface in pending:
                try:
                    save_path.parent.mkdir(parents=True, exist_ok=True)
                    save_path.write_text(
                        json.dumps(state), encoding="utf-8",
                    )
                    # Thumbnail PNG (best-effort — skip on error).
                    if thumb_surface is not None:
                        try:
                            import pygame as _pg
                            _pg.image.save(thumb_surface, str(thumb_path))
                        except Exception as e:
                            print(f"[save] thumbnail write failed: {e}")
                    # Update meta.json's updated_unix so the campaign
                    # list reflects the freshness.
                    meta_path = save_path.parent / "meta.json"
                    if meta_path.exists():
                        try:
                            meta = json.loads(
                                meta_path.read_text(encoding="utf-8"),
                            )
                        except (OSError, json.JSONDecodeError):
                            meta = {}
                        meta["updated_unix"] = state.get(
                            "saved_at_unix", time.time(),
                        )
                        try:
                            meta_path.write_text(
                                json.dumps(meta, indent=2),
                                encoding="utf-8",
                            )
                        except OSError:
                            pass
                    self._prune_old_saves(save_path.parent)
                except OSError as e:
                    print(f"[save] write failed: {e}")

    def _prune_old_saves(self, campaign_dir: Path) -> None:
        """Keep only the newest `SAVES_PER_CAMPAIGN` save_*.json files
        (plus their .png thumbnail siblings). Deletes the older ones
        — Aaron 2026-05-18 spec: "drops off after 20min of saves,
        auto-deleting the past so you are stuck within the last 20
        minutes of time."
        """
        saves = sorted(campaign_dir.glob("save_*.json"))
        if len(saves) <= SAVES_PER_CAMPAIGN:
            return
        to_delete = saves[:len(saves) - SAVES_PER_CAMPAIGN]
        for f in to_delete:
            try:
                f.unlink()
            except OSError:
                pass
            # Delete sibling thumbnail too.
            png_sibling = f.with_suffix(".png")
            if png_sibling.exists():
                try:
                    png_sibling.unlink()
                except OSError:
                    pass

    def shutdown(self) -> None:
        """Stop the worker thread cleanly. Called by Game on shutdown."""
        self._worker_stop = True
        self._worker_wake.set()
        if self._worker is not None:
            self._worker.join(timeout=1.0)

    # ---- Load / restore ----

    def _prime_save_stack_from_disk(self, slug: str) -> None:
        """Seed the in-memory save stack from disk (newest 8 entries
        sufficient — Time Drive needs only the ones near 5min ago)."""
        cdir = self._campaign_dir(slug)
        if not cdir.exists():
            return
        save_paths = sorted(cdir.glob("save_*.json"), reverse=True)[:8]
        for p in save_paths:
            try:
                state = json.loads(p.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                continue
            # Synthesize a monotonic-ish timestamp from the file's
            # saved_at_unix delta to now; the relative spacing is what
            # Time Drive cares about.
            unix_t = float(state.get("saved_at_unix", time.time()))
            ts_mono = time.monotonic() - (time.time() - unix_t)
            self._save_stack.append((ts_mono, state))

    def load_latest(self, slug: str) -> dict[str, Any] | None:
        """Return the most-recent save state for `slug`, or None if no
        saves exist. Caller is responsible for passing to restore_game.
        """
        cdir = self._campaign_dir(slug)
        if not cdir.exists():
            return None
        saves = sorted(cdir.glob("save_*.json"), reverse=True)
        if not saves:
            return None
        try:
            return json.loads(saves[0].read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return None

    def list_saves(self, slug: str) -> list[SaveInfo]:
        """Return all minute-saves for a campaign, sorted newest-first.
        Each entry includes its thumbnail PNG path (which may not exist
        if the screen capture failed at save time). Used by the save
        scrubber UI (Aaron 2026-05-18: thumbnail-driven save picker)."""
        cdir = self._campaign_dir(slug)
        if not cdir.exists():
            return []
        out: list[SaveInfo] = []
        for json_path in sorted(cdir.glob("save_*.json"), reverse=True):
            # Filename pattern: save_<unix_ms>.json
            stem = json_path.stem  # "save_1716000000123"
            try:
                unix_ms = int(stem.split("_", 1)[1])
            except (ValueError, IndexError):
                continue
            out.append(SaveInfo(
                slug=slug,
                save_path=json_path,
                thumb_path=json_path.with_suffix(".png"),
                saved_unix=unix_ms / 1000.0,
            ))
        return out

    def load_state(self, save_path: Path) -> dict[str, Any] | None:
        """Load a specific save file by path (used by the scrubber when
        the player picks a non-latest save). Returns None on any error.
        """
        try:
            return json.loads(save_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return None

    # ---- Time Drive integration ----

    def pick_rewind_target(self) -> dict[str, Any] | None:
        """Return the save state closest to `TIME_DRIVE_REWIND_S` ago
        from in-memory stack. Returns None if buffer isn't ready (less
        than `TIME_DRIVE_READY_THRESHOLD_S` of history accumulated).
        """
        if not self._save_stack:
            return None
        now = time.monotonic()
        oldest_age = now - self._save_stack[-1][0]
        if oldest_age < TIME_DRIVE_READY_THRESHOLD_S:
            return None
        target_age = TIME_DRIVE_REWIND_S
        best = None
        best_diff = float("inf")
        for ts, state in self._save_stack:
            age = now - ts
            diff = abs(age - target_age)
            if diff < best_diff:
                best = state
                best_diff = diff
        return best

    def is_rewind_ready(self) -> bool:
        """True if `pick_rewind_target()` would return a save."""
        return self.pick_rewind_target() is not None

    def time_until_rewind_ready(self) -> float:
        """Seconds until enough save history accumulates for Time Drive
        rewind. 0 if already ready."""
        if not self._save_stack:
            return TIME_DRIVE_READY_THRESHOLD_S
        now = time.monotonic()
        oldest_age = now - self._save_stack[-1][0]
        return max(0.0, TIME_DRIVE_READY_THRESHOLD_S - oldest_age)
