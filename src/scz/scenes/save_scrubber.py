"""Save scrubber — pick a minute-save to restore.

Aaron 2026-05-18: "Make it so each 1m save has a thumbnail of the
screengrab at that moment, and when you die or want to load, you can
scroll through which available minute you can load, but it drops off
after 20min of saves... And the time drive does that as well."

Same UI is reachable via:
- Main menu → Load Campaign → (pick campaign) → scrubber on that campaign
- Time Drive button (input.rewind) → scrubber on the ACTIVE campaign,
  default cursor focused on the save closest to 5 minutes ago

Layout (1280×720 reference):
┌────────────────────────────────────────────────────────────────┐
│  LOAD A MOMENT — Stardate 2026-05-18 1234                      │
│                                                                │
│  ┌────┐                ┌────────────────────────┐              │
│  │tn 1│ #1   0m ago    │                        │              │
│  ├────┤                │                        │              │
│  │tn 2│ #2   1m ago    │      BIG PREVIEW       │              │
│  ├────┤                │      (selected save)   │              │
│  │tn 3│ #3   2m ago    │                        │              │
│  ├────┤◀ selected ─────│                        │              │
│  │tn 4│ #4   3m ago    │                        │              │
│  ├────┤                └────────────────────────┘              │
│  │tn 5│ #5   4m ago        4m ago • frame 5432                 │
│  └────┘                                                        │
│  ...                                                           │
│                                                                │
│  [↑/↓] navigate    [A] restore    [B] back                     │
└────────────────────────────────────────────────────────────────┘
"""

from __future__ import annotations

import os
from pathlib import Path

import pygame

from scz.engine.persistence import (
    SaveInfo, TIME_DRIVE_DEFAULT_CURSOR_S, restore_game,
)
from scz.engine.scene import Scene


COL_BG = (6, 6, 18)
COL_TITLE = (240, 230, 200)
COL_SUB = (180, 200, 230)
COL_DETAIL = (160, 170, 190)
COL_SELECTED = (255, 240, 200)
COL_UNSELECTED = (140, 150, 180)
COL_LOCKED = (90, 95, 115)             # greyed label for barred saves
COL_LOCKED_OVERLAY = (10, 10, 22, 170)  # alpha overlay over locked thumbs
COL_BORDER = (60, 70, 100)
COL_BORDER_LOCKED = (40, 45, 60)
COL_BORDER_HOT = (220, 200, 130)
COL_CONTROLS = (120, 140, 170)


class SaveScrubberScene(Scene):
    """Browse and restore minute-saves. Same scene serves both
    "Load Game" (cursor on newest) and "Time Drive" (cursor on
    save closest to 5 minutes ago).
    """

    THUMB_W = 128
    THUMB_H = 72
    PREVIEW_W = 480
    PREVIEW_H = 270

    def __init__(
        self,
        slug: str,
        default_cursor_age_s: float = 0.0,
        title_prefix: str = "LOAD A MOMENT",
    ) -> None:
        super().__init__()
        self.slug = slug
        self.default_cursor_age_s = default_cursor_age_s
        self.title_prefix = title_prefix
        # Populated in on_enter.
        self.saves: list[SaveInfo] = []
        self.cursor: int = 0
        # Pygame fonts (built in on_enter).
        self.title_font: pygame.font.Font | None = None
        self.line_font: pygame.font.Font | None = None
        self.small_font: pygame.font.Font | None = None
        # Thumbnail surface cache — keyed by str(thumb_path). Two sizes
        # cached (small list-thumb + big preview) because pygame's
        # smoothscale is fast enough that re-scaling per frame is fine,
        # but a static cache is even faster and idle-friendly.
        self._thumb_cache: dict[str, pygame.Surface] = {}
        self._preview_cache: dict[str, pygame.Surface] = {}
        # Display-name lookup for the campaign header.
        self.campaign_display_name: str = slug

    def on_enter(self) -> None:
        assert self.game is not None
        self.title_font = pygame.font.SysFont("consolas", 28, bold=True)
        self.line_font = pygame.font.SysFont("consolas", 18)
        self.small_font = pygame.font.SysFont("consolas", 14)
        # Pull save list off disk.
        mgr = self.game.campaign_manager
        self.saves = mgr.list_saves(self.slug)
        # Display name from meta.json if available.
        meta_path = mgr._campaign_dir(self.slug) / "meta.json"
        if meta_path.exists():
            try:
                import json
                meta = json.loads(meta_path.read_text(encoding="utf-8"))
                self.campaign_display_name = meta.get("display_name", self.slug)
            except Exception:
                pass
        # Default cursor — pick save closest to default_cursor_age_s
        # ago, BUT only among loadable (non-locked) saves. The 4-minute
        # lockout (Aaron 2026-05-18) bars cursor-landing on the most
        # recent saves; cursor jumps to the first selectable one.
        # If no save is loadable yet (player just started), cursor
        # parks on the oldest visible row but confirm is a no-op.
        if self.saves:
            loadable_indices = [
                i for i, s in enumerate(self.saves) if s.is_loadable()
            ]
            if loadable_indices:
                best = loadable_indices[0]
                best_diff = float("inf")
                for i in loadable_indices:
                    diff = abs(
                        self.saves[i].age_seconds()
                        - self.default_cursor_age_s
                    )
                    if diff < best_diff:
                        best = i
                        best_diff = diff
                self.cursor = best
            else:
                # All saves are locked — cursor on the oldest of the
                # locked group (closest to being unlocked).
                self.cursor = len(self.saves) - 1

    def snapshot(self) -> dict | None:
        # Don't put the scrubber itself in the per-scene Time Drive
        # buffer — it's a UI sub-scene.
        return None

    # ------------------------------------------------------------------
    # Input
    # ------------------------------------------------------------------

    def update(self, dt: float, inp) -> None:  # type: ignore[no-untyped-def]
        if self.game is None:
            return
        if inp.cancel:
            self._back()
            return
        if not self.saves:
            return
        if inp.menu_up:
            self._step_cursor(-1)
        elif inp.menu_down:
            self._step_cursor(1)
        if inp.confirm:
            # Only loadable saves can be restored; locked saves are
            # visible-but-barred. Trivial save-scumming gate.
            if self.saves[self.cursor].is_loadable():
                self._restore_selected()

    def _step_cursor(self, direction: int) -> None:
        """Move cursor by ±1, skipping over locked saves. If no
        loadable save exists in the chosen direction, wrap to the
        first loadable save from the other end. If NO save is
        loadable, the cursor stays put (cosmetic — confirm is a no-op
        anyway)."""
        n = len(self.saves)
        if n == 0:
            return
        # Build the loadable-indices list once per nav so cursor
        # math is straightforward.
        loadable = [i for i, s in enumerate(self.saves) if s.is_loadable()]
        if not loadable:
            return
        if self.cursor not in loadable:
            # Cursor on a locked row (shouldn't happen post-on_enter,
            # but defensive). Snap to nearest loadable in direction.
            if direction > 0:
                forward = [i for i in loadable if i > self.cursor]
                self.cursor = forward[0] if forward else loadable[0]
            else:
                backward = [i for i in loadable if i < self.cursor]
                self.cursor = backward[-1] if backward else loadable[-1]
            return
        # Move to the next loadable index in the chosen direction,
        # wrapping around the loadable list.
        idx_in_loadable = loadable.index(self.cursor)
        next_idx = (idx_in_loadable + direction) % len(loadable)
        self.cursor = loadable[next_idx]

    def _back(self) -> None:
        from scz.scenes.stubs import MainMenuScene
        self.game.set_scene(MainMenuScene())

    def _restore_selected(self) -> None:
        if not self.saves:
            return
        info = self.saves[self.cursor]
        state = self.game.campaign_manager.load_state(info.save_path)
        if state is None:
            return
        restore_game(self.game, state)
        # Ensure the campaign is active so subsequent auto-saves write
        # back into the same dossier.
        self.game.campaign_manager.set_active(self.slug)
        # Reuse the existing Time Drive chronometric flash for
        # visual feedback regardless of which entry-point opened the
        # scrubber (the player FEELS the rewind).
        self.game.time_drive.flash_remaining = (
            self.game.time_drive.FLASH_DURATION
        )
        # Restart auto-save timer so the next auto-save lands a full
        # 60s after the restore moment (not immediately).
        self.game.campaign_manager._time_since_save = 0.0
        # Drop the player at Mh-Lai as the safe landing scene.
        from scz.station.scene import StationScene
        self.game.set_scene(StationScene())

    # ------------------------------------------------------------------
    # Render
    # ------------------------------------------------------------------

    def _load_thumb(self, info: SaveInfo, size: tuple[int, int],
                     cache: dict[str, pygame.Surface]) -> pygame.Surface | None:
        """Load a thumbnail at the given size, cached by path. Returns
        None if the PNG is missing or fails to load."""
        key = f"{info.thumb_path}|{size[0]}x{size[1]}"
        if key in cache:
            return cache[key]
        if not info.thumb_path.exists():
            cache[key] = self._placeholder_surface(size)
            return cache[key]
        try:
            img = pygame.image.load(str(info.thumb_path))
            scaled = pygame.transform.smoothscale(img, size)
            cache[key] = scaled
            return scaled
        except (pygame.error, OSError):
            cache[key] = self._placeholder_surface(size)
            return cache[key]

    def _placeholder_surface(self, size: tuple[int, int]) -> pygame.Surface:
        """A neutral 'no thumbnail' placeholder so the scrubber doesn't
        have empty slots when an old PNG is missing."""
        surf = pygame.Surface(size)
        surf.fill((30, 30, 50))
        if size[0] > 32:
            pygame.draw.line(surf, (60, 60, 90), (0, 0), size, 1)
            pygame.draw.line(
                surf, (60, 60, 90), (0, size[1]), (size[0], 0), 1,
            )
        return surf

    def render(self, screen: pygame.Surface) -> None:
        screen.fill(COL_BG)
        w, h = screen.get_size()

        # Header
        if self.title_font is not None:
            header_text = f"{self.title_prefix} — {self.campaign_display_name}"
            hdr = self.title_font.render(header_text, True, COL_TITLE)
            screen.blit(hdr, (40, 30))

        if not self.saves:
            if self.line_font is not None:
                empty = self.line_font.render(
                    "(no saves in this campaign yet — play for one minute"
                    " to land your first auto-save)",
                    True, COL_DETAIL,
                )
                screen.blit(empty, (40, 100))
            self._render_controls(screen, w, h)
            return

        # --- Left column: vertical list of small thumbnails ---
        list_x = 40
        list_y = 90
        row_h = self.THUMB_H + 12
        # Compute the slice of saves visible. With 20-save cap and
        # row_h=84, viewport accommodates ~6-7 rows on a 720p screen
        # below the header — center the list around the cursor.
        viewport_top_px = list_y
        viewport_bottom_px = h - 80
        viewport_rows = max(1, (viewport_bottom_px - viewport_top_px) // row_h)
        half = viewport_rows // 2
        start = max(0, self.cursor - half)
        end = min(len(self.saves), start + viewport_rows)
        if end - start < viewport_rows:
            start = max(0, end - viewport_rows)

        for vi, abs_i in enumerate(range(start, end)):
            info = self.saves[abs_i]
            is_selected = (abs_i == self.cursor)
            is_locked = not info.is_loadable()
            row_y = list_y + vi * row_h
            thumb = self._load_thumb(
                info, (self.THUMB_W, self.THUMB_H), self._thumb_cache,
            )
            # Thumbnail
            if thumb is not None:
                screen.blit(thumb, (list_x, row_y))
            # Locked overlay — alpha-dark wash over the thumbnail so
            # the player visually understands "you have a save here
            # but can't pick it yet."
            if is_locked:
                lock_surf = pygame.Surface(
                    (self.THUMB_W, self.THUMB_H), pygame.SRCALPHA,
                )
                lock_surf.fill(COL_LOCKED_OVERLAY)
                screen.blit(lock_surf, (list_x, row_y))
            # Border colour reflects state.
            if is_locked:
                border_color = COL_BORDER_LOCKED
                border_width = 1
            elif is_selected:
                border_color = COL_BORDER_HOT
                border_width = 2
            else:
                border_color = COL_BORDER
                border_width = 1
            pygame.draw.rect(
                screen, border_color,
                (list_x, row_y, self.THUMB_W, self.THUMB_H),
                border_width,
            )
            # Label colour + content varies with state.
            if is_locked:
                label_color = COL_LOCKED
                wait_s = info.time_until_loadable()
                wait_label = f"{int(wait_s / 60)}m {int(wait_s % 60):02d}s"
                label = f"#{abs_i + 1}   {info.age_human()}   🔒 unlocks in {wait_label}"
            else:
                label_color = COL_SELECTED if is_selected else COL_UNSELECTED
                label = f"#{abs_i + 1}   {info.age_human()}"
            if self.line_font is not None:
                surf = self.line_font.render(label, True, label_color)
                screen.blit(
                    surf,
                    (list_x + self.THUMB_W + 16, row_y + 26),
                )

        # Scroll indicator
        if self.small_font is not None:
            count_text = f"{self.cursor + 1} / {len(self.saves)}"
            ctxt = self.small_font.render(count_text, True, COL_DETAIL)
            screen.blit(ctxt, (list_x, list_y + viewport_rows * row_h + 8))

        # --- Right column: big preview ---
        preview_x = w - self.PREVIEW_W - 60
        preview_y = 120
        info = self.saves[self.cursor]
        is_locked = not info.is_loadable()
        preview = self._load_thumb(
            info, (self.PREVIEW_W, self.PREVIEW_H), self._preview_cache,
        )
        if preview is not None:
            screen.blit(preview, (preview_x, preview_y))
        # Locked-overlay on the big preview too, matching the small thumbs.
        if is_locked:
            lock_surf = pygame.Surface(
                (self.PREVIEW_W, self.PREVIEW_H), pygame.SRCALPHA,
            )
            lock_surf.fill(COL_LOCKED_OVERLAY)
            screen.blit(lock_surf, (preview_x, preview_y))
        pygame.draw.rect(
            screen,
            COL_BORDER_LOCKED if is_locked else COL_BORDER_HOT,
            (preview_x, preview_y, self.PREVIEW_W, self.PREVIEW_H),
            2,
        )
        # Preview details
        if self.line_font is not None:
            detail_y = preview_y + self.PREVIEW_H + 24
            line1 = f"Save #{self.cursor + 1} of {len(self.saves)}"
            line2 = f"Captured {info.age_human()}"
            if is_locked:
                wait_s = info.time_until_loadable()
                wait_label = f"{int(wait_s / 60)}m {int(wait_s % 60):02d}s"
                line3 = (
                    f"\U0001F512 BARRED — unlocks in {wait_label}"
                )
                lines = (line1, line2, line3)
                colors = (COL_SUB, COL_SUB, COL_LOCKED)
            else:
                lines = (line1, line2)
                colors = (COL_SUB, COL_SUB)
            for i, (txt, col) in enumerate(zip(lines, colors)):
                surf = self.line_font.render(txt, True, col)
                screen.blit(surf, (preview_x, detail_y + i * 26))

        self._render_controls(screen, w, h)

    def _render_controls(self, screen: pygame.Surface, w: int, h: int) -> None:
        if self.line_font is None or self.small_font is None:
            return
        controls = (
            "[↑/↓] navigate     [A / Space] restore     [B / Esc] back"
        )
        ctxt = self.line_font.render(controls, True, COL_CONTROLS)
        cw, _ = ctxt.get_size()
        screen.blit(ctxt, ((w - cw) // 2, h - 50))
        # Lockout note — explain why the most recent saves are greyed.
        note = (
            "🔒 The most recent 4 minutes of saves are barred — meaningful "
            "rewinds only. Older saves auto-delete past 20 minutes."
        )
        ntxt = self.small_font.render(note, True, COL_DETAIL)
        nw, _ = ntxt.get_size()
        screen.blit(ntxt, ((w - nw) // 2, h - 24))
