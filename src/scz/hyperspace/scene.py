"""The hyperspace scene: top-down view of the precursor-era galaxy with the
player ship marker moving across it. Foundation for everything else.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

import pygame

from scz.content.species_visual import get_warp_pod_colors
from scz.engine.scene import Scene
from scz.hyperspace.search import SearchOverlay
from scz.hyperspace.starmap import Starmap, UNIVERSE_MAX
from scz.hyperspace.zones import ZoneRenderer, build_default_zones


# Radius within which a hyperspace encounter point auto-triggers on collision
ENCOUNTER_TRIGGER_RADIUS = 220.0


@dataclass
class EncounterPoint:
    """A transient encounter in hyperspace. When the player ship enters
    `trigger_radius`, the on_trigger callback fires (typically opens a
    dialog scene). The encounter is removed after firing.
    """
    x: float
    y: float
    label: str
    color: tuple[int, int, int]
    on_trigger: Callable[["HyperspaceScene"], None]
    trigger_radius: float = ENCOUNTER_TRIGGER_RADIUS
    fired: bool = False


@dataclass
class HyperspaceBroadcast:
    """An incoming hail rendered as a text crawl across the hyperspace
    HUD before an encounter dialog auto-launches.

    Per the Cleanser climax design doc (`references/lore/cleanser-encounter-design.md`
    §Encounter Flow Step 1), big interceptions broadcast a first-hail
    *before* materialization — building anticipation between sensor
    detection and dialog launch. Currently those transitions are
    instantaneous; this overlay fixes that.

    The player can keep flying during the broadcast; the on_complete
    callback fires after `duration` game-seconds and typically opens a
    DialogScene. Cancel (B) is intentionally NOT intercepted — if the
    player needs to flee, the broadcast just keeps playing while they
    move; the callback fires when the timer expires regardless.
    """
    sender: str        # short banner (e.g. "INCOMING HAIL · CLEANSER VESSEL")
    text: str          # body — multi-paragraph crawl, \n separates lines
    color: tuple[int, int, int]
    on_complete: Callable[["HyperspaceScene"], None]
    duration: float = 5.0
    elapsed: float = 0.0
    fired: bool = False


# Where the package finds its content files
_CONTENT_ROOT = Path(__file__).resolve().parent.parent / "content"
STARMAP_JSON = _CONTENT_ROOT / "universe" / "stars.json"

# Ship movement speed in universe units per second
PLAYER_SPEED = 1200.0

# How close (universe units) the player must be to a star to "enter" it.
STAR_ENTER_RADIUS = 250.0

# Sol's coordinates in the precursor-era universe (the player's home, before
# humans exist). From src/scz/content/universe/stars.json.
SOL_X = 1793.0
SOL_Y = 1450.0

# UI margins. Sized to look good at 1920x1080. The HUD scales naturally to
# fit narrower windows because the map area auto-fits the remaining space.
HUD_WIDTH = 360
MAP_MARGIN = 40

# Zoom: 1.0 fits the whole galaxy in the map view. Higher = zoomed in.
# Default starts close enough that the player ship is unmistakable; press
# LB / - to zoom out to the full-galaxy view (the "map screen" feel).
DEFAULT_ZOOM = 5.0
MIN_ZOOM = 0.8
MAX_ZOOM = 25.0
ZOOM_STEP = 1.4        # button-press multiplier
ZOOM_LERP = 8.0        # smoothing per second (higher = snappier)

# Autopilot: aiming cone (half-angle) for star target acquisition. A wider
# cone makes "press Y to autopilot toward whatever's ahead of me" forgiving.
AUTOPILOT_CONE_DEG = 45.0
# Manual stick deflection magnitude that cancels autopilot
AUTOPILOT_CANCEL_THRESHOLD = 0.4


def _trigger_coel_tessar(scene: "HyperspaceScene") -> None:
    """Beat 4 trigger — open dialog with the Androsynth refugee leader."""
    from scz.dialog.characters import coel_tessar
    from scz.dialog.scene import DialogScene
    assert scene.game is not None
    # Parent factory returns a fresh hyperspace at the same player pos
    px, py = scene.player_x, scene.player_y

    def _back_to_hyperspace() -> "HyperspaceScene":
        h = HyperspaceScene()
        h.player_x = px
        h.player_y = py
        return h

    scene.game.set_scene(
        DialogScene(character=coel_tessar(), parent_factory=_back_to_hyperspace)
    )


def _trigger_cleanser_climax(scene: "HyperspaceScene") -> None:
    """Cleanser climax encounter — broadcast incoming hail, then open
    dialog with Vael-Souren. The hail crawl plays across the
    hyperspace HUD for ~5 game-seconds before the dialog scene
    actually opens (per `references/lore/cleanser-encounter-design.md`
    §Encounter Flow Step 1).

    The decision tree handles all branches (cooperate, negotiate,
    refuse). The refuse branch's side-effect launches combat directly
    via `_cleanser_engage_combat` in dialog/characters.py.

    Parent factory restores hyperspace at the encounter location after
    dialog ends (cooperate / negotiate paths). The combat path's own
    on_finish does the hyperspace return.
    """
    from scz.dialog.characters import cleanser_vael_souren
    from scz.dialog.scene import DialogScene
    assert scene.game is not None
    px, py = scene.player_x, scene.player_y

    def _back_to_hyperspace() -> "HyperspaceScene":
        h = HyperspaceScene()
        h.player_x = px
        h.player_y = py
        return h

    def _open_dialog(scn: "HyperspaceScene") -> None:
        scn.game.set_scene(
            DialogScene(
                character=cleanser_vael_souren(),
                parent_factory=_back_to_hyperspace,
            )
        )

    # Cleanser hail: gentle, sorrowful, certain — never triumphant.
    # Voice notes per Vael-Souren's design doc.
    scene.start_broadcast(
        sender="INCOMING HAIL  ·  CLEANSER VESSEL  ·  THE BELL OF THE QUIET LEDGER",
        text=(
            "Steward of Mh-Lai. I am Vael-Souren, captain of the "
            "Bell of the Quiet Ledger. Hold your course; I am "
            "matching velocity.\n\n"
            "I have come because your cluster has not concluded. We "
            "will speak."
        ),
        color=(200, 180, 240),     # Cleanser cold violet — per species_visual canon
        on_complete=_open_dialog,
        duration=5.0,
    )


def _make_salvage_trigger(
    flag_suffix: str,
    common: int = 8,
    useful: int = 4,
) -> "Callable[[HyperspaceScene], None]":
    """Build a salvage-wreck trigger callback. On proximity, awards
    `common` COMMON + `useful` USEFUL cargo, sets `salvaged_<suffix>`
    flag (which the encounter spec's `not_flag` reads to retire), and
    returns the player to HyperspaceScene at the encounter location.

    Each salvage gives a single small bundle — the wrecks aren't a
    grind loop. Visiting all four nets ~32 COMMON + 16 USEFUL, less
    than a single good lander run.
    """
    def trigger(scene: "HyperspaceScene") -> None:
        assert scene.game is not None
        game = scene.game
        flag = f"salvaged_{flag_suffix}"
        if game.flags.get(flag):
            return   # already salvaged; encounter should have retired
        game.flags[flag] = True
        game.cargo["COMMON"] = game.cargo.get("COMMON", 0) + common
        game.cargo["USEFUL"] = game.cargo.get("USEFUL", 0) + useful
        # No scene transition — we stay in hyperspace. The encounter
        # auto-retires next frame via not_flag, removing the
        # EncounterPoint so collision doesn't re-fire on the same tick.
        # But the existing EncounterPoint in this scene's list is
        # already marked `fired=True` by the proximity-check caller,
        # so re-fire is also guarded there.
    return trigger


def _trigger_cleanser_patrol(scene: "HyperspaceScene") -> None:
    """Cleanser patrol encounter — flying close auto-starts combat
    against a Cleanser Furling Cruiser. First taste of the slice's
    central faction conflict (Furling-vs-Furling, Cleansers enforcing
    kill orders against species the Steward is trying to save).

    Outcome: regardless of winner, sets `met_cleanser_patrol` so the
    encounter retires from the registry. Win/loss is captured in
    `last_combat_winner_side` for the harness. Returns to hyperspace
    at the same player position on combat finish.
    """
    from scz.combat.scene import (
        ARENA_STYLE_HYPERSPACE,
        MeleeCombatScene,
    )
    from scz.combat.ships import CLEANSER_CRUISER, FURLING_SCOUT
    assert scene.game is not None
    game = scene.game
    px, py = scene.player_x, scene.player_y

    def _on_finish(result) -> None:  # type: ignore[no-untyped-def]
        game.flags["met_cleanser_patrol"] = True
        game.flags["last_combat_winner_side"] = result.winner_side
        game.flags["last_combat_timed_out"] = result.timed_out
        h = HyperspaceScene()
        h.player_x = px
        h.player_y = py
        game.set_scene(h)

    # arena_style=hyperspace — the central body is the coaxial
    # interference tunnel that forms between two hyperspace bubbles
    # closing for combat (diegetically: not a planet, mechanically:
    # same gravity well + collision). No moon — the tunnel is a
    # singular phenomenon.
    game.set_scene(
        MeleeCombatScene(
            precursor_ship=FURLING_SCOUT,
            homesteader_ship=CLEANSER_CRUISER,
            max_duration=60.0,
            on_finish=_on_finish,
            arena_style=ARENA_STYLE_HYPERSPACE,
        )
    )


# Lookup table for the canonical ship classes a SpeciesDomain might
# reference. Kept inside the scene module so the content layer stays
# free of combat imports. New domain ship_class_ids land here.
def _resolve_domain_ship_class(ship_class_id: str):  # type: ignore[no-untyped-def]
    from scz.combat.ships import (
        CLEANSER_CRUISER,
        MELNORME_TRADER,
        MYCON_PODSHIP,
    )
    table = {
        "CLEANSER_CRUISER": CLEANSER_CRUISER,
        "MELNORME_TRADER":  MELNORME_TRADER,
        "MYCON_PODSHIP":    MYCON_PODSHIP,
    }
    return table.get(ship_class_id)


def _make_domain_patrol_trigger(
    domain_id: str, patrol_index: int,
):  # type: ignore[no-untyped-def]
    """Build a patrol trigger callback for one (domain, index) pair.

    Behavior depends on the domain's `friendly` flag:
    - friendly=False → combat encounter vs. the domain's canonical ship
    - friendly=True  → peaceful contact (just sets the met flag and
      returns to hyperspace; future iterations can wire dialog here)

    Either way: sets `patrol_<domain>_<index>_met` so the encounter
    retires next time hyperspace re-spawns.
    """
    def trigger(scene: "HyperspaceScene") -> None:
        from scz.content.species_domains import DOMAINS
        domain = next((d for d in DOMAINS if d.id == domain_id), None)
        assert scene.game is not None and domain is not None
        game = scene.game
        met_flag = f"patrol_{domain_id}_{patrol_index}_met"
        game.flags[met_flag] = True

        if domain.friendly or domain.ship_class_id is None:
            # Peaceful: no combat. Future work can route to a dialog
            # scene per species. For now just stay in hyperspace at the
            # same position; the encounter retires via the met flag.
            return

        ship_class = _resolve_domain_ship_class(domain.ship_class_id)
        if ship_class is None:
            # Unknown ship — fail quiet rather than crash
            return

        from scz.combat.scene import (
            ARENA_STYLE_HYPERSPACE,
            MeleeCombatScene,
        )
        from scz.combat.ships import FURLING_SCOUT
        px, py = scene.player_x, scene.player_y

        def _on_finish(result) -> None:  # type: ignore[no-untyped-def]
            game.flags["last_combat_winner_side"] = result.winner_side
            game.flags["last_combat_timed_out"] = result.timed_out
            h = HyperspaceScene()
            h.player_x = px
            h.player_y = py
            game.set_scene(h)

        game.set_scene(
            MeleeCombatScene(
                precursor_ship=FURLING_SCOUT,
                homesteader_ship=ship_class,
                max_duration=60.0,
                on_finish=_on_finish,
                arena_style=ARENA_STYLE_HYPERSPACE,
            )
        )
    return trigger


# Register encounter triggers with the content layer. The content
# registry stores `trigger_id` strings and resolves them at spawn time
# via `get_trigger`. This indirection keeps content/engine decoupled.
def _register_encounter_triggers() -> None:
    from scz.content.hyperspace_encounters import register_trigger
    register_trigger("cleanser_patrol_alpha", _trigger_cleanser_patrol)
    register_trigger("cleanser_climax_alpha", _trigger_cleanser_climax)
    # Salvage wrecks — 4 fixed-location interactives across deep space.
    # Each gives a unique cargo bundle and retires via not_flag.
    register_trigger("salvage_wreck_alpha", _make_salvage_trigger("alpha"))
    register_trigger("salvage_wreck_beta",  _make_salvage_trigger("beta"))
    register_trigger("salvage_wreck_gamma", _make_salvage_trigger("gamma"))
    register_trigger("salvage_wreck_delta", _make_salvage_trigger("delta"))

    # Domain-patrol triggers — one per (domain, patrol_index) pair.
    # The trigger_id format is `domain_patrol_<id>_<n>`, matching the
    # spawning code in `_maybe_spawn_encounters`.
    from scz.content.species_domains import DOMAINS
    for d in DOMAINS:
        for i in range(d.encounter_density):
            register_trigger(
                f"domain_patrol_{d.id}_{i}",
                _make_domain_patrol_trigger(d.id, i),
            )


_register_encounter_triggers()


class HyperspaceScene(Scene):
    """The galactic map view with a movable player ship."""

    music_context = "hyperspace"  # assets/music/hyperspace/

    def __init__(self) -> None:
        super().__init__()
        self.starmap = Starmap(STARMAP_JSON)
        # Toggleable species control-zone overlay (Z key). Default off so
        # the map reads cleanly; the player explicitly asks for it.
        self.zone_renderer = ZoneRenderer(build_default_zones(self.starmap.stars))
        # Star-name search overlay (/ to open). Modal: while open, ALL
        # keyboard input is captured by the overlay so the ship doesn't
        # accidentally move while typing.
        self.search_overlay = SearchOverlay(self.starmap)
        self.player_x: float = SOL_X
        self.player_y: float = SOL_Y
        self.player_heading: float = 0.0  # radians, 0 = up

        # Zoom + camera. Camera always tries to follow the ship; at very low
        # zoom (whole galaxy visible) the clamp keeps it centered on the
        # universe so we don't show empty space beyond the map edges.
        self.zoom: float = DEFAULT_ZOOM
        self.target_zoom: float = DEFAULT_ZOOM
        self.camera_x: float = SOL_X
        self.camera_y: float = SOL_Y

        # Autopilot — when set, the ship auto-thrusts toward target_star
        # until it enters the star's system (auto-confirm). Manual stick
        # movement of significant magnitude cancels.
        self.autopilot_target: dict | None = None

        # Hyperspace encounters — transient points that fire a callback
        # when the player ship enters their trigger_radius. Used for
        # Beat 4 Androsynth, the Cleanser climax intercept, and any
        # future "you ran into someone in hyperspace" beats.
        self.encounter_points: list[EncounterPoint] = []

        # Active incoming-hail broadcast (the text-crawl overlay before
        # a big interception). None when no hail is in flight. Set by
        # encounter triggers via `start_broadcast()`; advanced in
        # update(); rendered each frame; on_complete fires when elapsed
        # exceeds duration.
        self.broadcast: HyperspaceBroadcast | None = None

        # SC2 starmap backdrop image + a (target_w, target_h) → scaled
        # Surface cache so we don't pygame.transform.scale every frame
        self._starmap_image: pygame.Surface | None = None
        self._starmap_scaled_cache: tuple[int, int, pygame.Surface] | None = None

        # Set in on_enter once we know the screen size
        self.map_view_x: int = 0
        self.map_view_y: int = 0
        self.map_view_w: int = 0
        self.map_view_h: int = 0
        self.base_scale: float = 1.0   # scale at zoom == 1.0
        self.font: pygame.font.Font | None = None
        self.title_font: pygame.font.Font | None = None
        self.small_font: pygame.font.Font | None = None

    # --- transform between universe and screen coordinates ---

    def _effective_scale(self) -> float:
        return self.base_scale * self.zoom

    def universe_to_screen(self, ux: float, uy: float) -> tuple[float, float]:
        es = self._effective_scale()
        center_x = self.map_view_x + self.map_view_w / 2
        center_y = self.map_view_y + self.map_view_h / 2
        return (
            center_x + (ux - self.camera_x) * es,
            center_y + (uy - self.camera_y) * es,
        )

    # --- Scene API ---

    def on_enter(self) -> None:
        assert self.game is not None
        w, h = self.game.screen.get_size()
        self.map_view_x = HUD_WIDTH + MAP_MARGIN
        self.map_view_y = MAP_MARGIN
        self.map_view_w = w - HUD_WIDTH - 2 * MAP_MARGIN
        self.map_view_h = h - 2 * MAP_MARGIN
        # base_scale: zoom=1.0 fits the whole universe in the SMALLER dimension
        # of the map view (so it's never cropped at full zoom-out).
        self.base_scale = min(self.map_view_w, self.map_view_h) / UNIVERSE_MAX

        self.font = pygame.font.SysFont("consolas", 18)
        self.title_font = pygame.font.SysFont("consolas", 26, bold=True)
        self.small_font = pygame.font.SysFont("consolas", 14)

        # SC2 starmap backdrop — per Rule 4 (keep), the canonical SC2
        # hyperspace map is the primary visual. Actual interactive stars
        # render ON TOP of this image so the player can autopilot to them.
        self._load_starmap_image()

        # The Fall of Mh-Lai — slice-critical forced beat. Checked
        # before encounter spawning so a fall-trigger doesn't compete
        # with a routine encounter. When all prereqs are met (per
        # `fall_of_mhlai.should_fire_fall`), the scene auto-fires
        # *immediately* on hyperspace entry; encounter spawning is
        # skipped (the Fall scene returns to a fresh hyperspace on
        # completion, which re-runs on_enter).
        from scz.content.fall_of_mhlai import should_fire_fall
        if should_fire_fall(self.game):
            from scz.scenes.fall_of_mhlai import FallOfMhLaiScene
            self.game.set_scene(FallOfMhLaiScene())
            return

        # The Final Conflict — slice climax. Auto-fires once the Fall
        # has resolved AND the Rainbow Resonator is in the player's
        # possession. Captures current hyperspace coords so the loss
        # path (Time Drive restore) can return the player here. After
        # a loss-rewind, `final_conflict_just_rewound` is set; we clear
        # it without re-firing so the player gets a chance to
        # re-engage on their next hyperspace entry instead of an
        # infinite-loop bounce.
        if self.game.flags.pop("final_conflict_just_rewound", False):
            pass
        else:
            from scz.content.final_conflict import should_fire_final_conflict
            if should_fire_final_conflict(self.game):
                from scz.scenes.final_conflict import FinalConflictScene
                scene = FinalConflictScene()
                scene.set_restore_position(self.player_x, self.player_y)
                self.game.set_scene(scene)
                return

        # Spawn any encounter points whose triggers fire on this entry
        self._maybe_spawn_encounters()

    def _load_starmap_image(self) -> None:
        """Load the SC2 hyperspace starmap as a backdrop image. Per Rule 4
        in references/project-rules.md, the SC2 map is the canonical visual
        for hyperspace; interactive stars (the autopilot targets) render on
        top of it. Loaded once on scene entry; scaled lazily per viewport.
        Silently no-ops if the file is missing.
        """
        img_path = (
            Path(__file__).resolve().parent.parent.parent.parent
            / "assets" / "maps" / "sc2-starmap.png"
        )
        if not img_path.exists():
            self._starmap_image = None
            return
        try:
            self._starmap_image = pygame.image.load(str(img_path)).convert()
        except pygame.error:
            self._starmap_image = None

    def _get_scaled_starmap(
        self, target_w: int, target_h: int
    ) -> pygame.Surface | None:
        """Return the SC2 starmap scaled to (target_w, target_h), cached.
        Quantized to 16px so smooth zoom doesn't rebuild every frame.
        """
        if self._starmap_image is None or target_w <= 0 or target_h <= 0:
            return None
        bw = max(16, ((target_w + 8) // 16) * 16)
        bh = max(16, ((target_h + 8) // 16) * 16)
        if (
            self._starmap_scaled_cache is not None
            and self._starmap_scaled_cache[0] == bw
            and self._starmap_scaled_cache[1] == bh
        ):
            return self._starmap_scaled_cache[2]
        scaled = pygame.transform.smoothscale(
            self._starmap_image, (bw, bh)
        )
        self._starmap_scaled_cache = (bw, bh, scaled)
        return scaled

    def _maybe_spawn_encounters(self) -> None:
        """Check game.flags and spawn transient encounter points based on
        story progress. Called on hyperspace-scene entry.

        Two sources, in order:
        1. **Hardcoded beat-specific encounters** — Beat 4 Coel Tessar.
           Lives here because the spawn position depends on the player's
           current heading (placed ahead of them, not at a fixed coord).
        2. **Content registry** — `hyperspace_encounters.ENCOUNTERS`.
           Fixed-coord encounters (Cleanser patrols, future story beats)
           with flag-gated visibility.
        """
        if self.game is None:
            return
        flags = self.game.flags

        # Beat 4 — Coel Tessar arrival (heading-relative placement
        # warrants the special case here, not in the registry).
        if (
            flags.get("scanner_mk3_installed")
            and not flags.get("met_androsynth")
            and not any(ep.label == "Coel Tessar" for ep in self.encounter_points)
        ):
            # Place the encounter ~600 units ahead of the player at
            # scene-entry. Direction = +x by default (Mh-Lai is at
            # 1900,1600; Sol is at 1793,1450 so +x heads away from home
            # which feels right for a "found her on the way out" beat).
            self.encounter_points.append(EncounterPoint(
                x=self.player_x + 600.0,
                y=self.player_y + 200.0,
                label="Coel Tessar",
                color=(220, 130, 220),
                on_trigger=_trigger_coel_tessar,
            ))

        # Registry-driven encounters — fixed coordinates, flag-gated.
        # Only spawn interactive ones as EncounterPoints (ambient ripples
        # only render via the Echo Sensor; they have no collision body).
        from scz.content.hyperspace_encounters import (
            encounters_visible,
            get_trigger,
        )
        from scz.content.hyperspace_ripples import RIPPLE_COLORS
        already = {ep.label for ep in self.encounter_points}
        for spec in encounters_visible(self.game):
            if not spec.interactive:
                continue
            if spec.label in already:
                continue
            if spec.trigger_id is None:
                continue
            trigger = get_trigger(spec.trigger_id)
            if trigger is None:
                # No callback registered for this id — skip rather than
                # crash. Lets content land before engine wiring.
                continue
            self.encounter_points.append(EncounterPoint(
                x=spec.x, y=spec.y,
                label=spec.label,
                color=RIPPLE_COLORS.get(spec.kind, (200, 200, 200)),
                on_trigger=trigger,
            ))

        # Species-domain patrols — per-domain, per-index spawning.
        # Deterministic positions from `patrol_positions(domain)`;
        # retired per-patrol via `patrol_<id>_<n>_met` flags.
        from scz.content.species_domains import active_patrols
        for domain, dx, dy, idx in active_patrols(self.game):
            label = f"{domain.name} patrol"
            # Dedupe by exact label-and-position so re-entering hyperspace
            # mid-scene doesn't accumulate duplicates
            if any(
                ep.label == label
                and abs(ep.x - dx) < 1.0
                and abs(ep.y - dy) < 1.0
                for ep in self.encounter_points
            ):
                continue
            trigger = get_trigger(f"domain_patrol_{domain.id}_{idx}")
            if trigger is None:
                continue
            self.encounter_points.append(EncounterPoint(
                x=dx, y=dy,
                label=label,
                color=domain.color,
                on_trigger=trigger,
            ))

    def update(self, dt: float, inp) -> None:  # type: ignore[no-untyped-def]
        # --- Search overlay (/) ---
        # If open, consume all input this frame so the ship doesn't drift.
        if inp.open_search and not self.search_overlay.visible:
            self.search_overlay.open()
            pygame.key.start_text_input()
            return
        if self.search_overlay.visible:
            events = getattr(inp, "recent_events", [])
            self.search_overlay.update_events(events)
            if not self.search_overlay.visible:
                pygame.key.stop_text_input()
            # Don't move the ship or zoom while typing.
            return
        # After-search jump: if the player picked a star, pan + select it.
        target = self.search_overlay.pending_target
        if target is not None:
            self.search_overlay.pending_target = None
            tx, ty = float(target["x"]), float(target["y"])
            self.player_x = tx
            self.player_y = ty
            self.camera_x = tx
            self.camera_y = ty
            self.autopilot_target = target

        # --- Zone overlay toggle (Z) ---
        if inp.toggle_zones:
            self.zone_renderer.toggle()

        # --- Zoom (LB / RB on controller, - / = on keyboard) ---
        if inp.zoom_out:
            self.target_zoom = max(self.target_zoom / ZOOM_STEP, MIN_ZOOM)
        if inp.zoom_in:
            self.target_zoom = min(self.target_zoom * ZOOM_STEP, MAX_ZOOM)
        # Smooth toward target zoom
        if abs(self.target_zoom - self.zoom) > 1e-4:
            t = min(1.0, dt * ZOOM_LERP)
            self.zoom += (self.target_zoom - self.zoom) * t

        # --- Autopilot engage / disengage ---
        # A / Space (confirm) toggles autopilot: if off, snap to nearest star
        # in heading cone; if on, another press (or manual stick deflection)
        # disengages.
        if inp.confirm:
            if self.autopilot_target is None:
                self.autopilot_target = self._find_autopilot_target()
            else:
                self.autopilot_target = None

        # --- Movement ---
        mx, my = inp.move_x, inp.move_y
        manual = math.hypot(mx, my)

        if self.autopilot_target is not None:
            # Manual stick deflection cancels autopilot
            if manual > AUTOPILOT_CANCEL_THRESHOLD:
                self.autopilot_target = None
            else:
                # Auto-steer toward target
                t = self.autopilot_target
                dx = t["x"] - self.player_x
                dy = t["y"] - self.player_y
                dist = math.hypot(dx, dy) or 1.0
                ax, ay = dx / dist, dy / dist
                # Forward-thrust along bearing
                mx = ax
                my = ay
                self.player_heading = math.atan2(mx, -my)

                # Auto-enter when within the system's "entry" radius
                if dist <= STAR_ENTER_RADIUS and self.game is not None:
                    target = self.autopilot_target
                    self.autopilot_target = None
                    from scz.system.scene import SystemScene
                    self.game.set_scene(SystemScene(target))
                    return

        if mx != 0.0 or my != 0.0:
            mag = math.hypot(mx, my)
            if mag > 1.0:
                mx /= mag
                my /= mag
            self.player_heading = math.atan2(mx, -my)  # 0 = up
        speed = PLAYER_SPEED * dt
        self.player_x += mx * speed
        self.player_y += my * speed
        self.player_x = max(0.0, min(UNIVERSE_MAX - 1, self.player_x))
        self.player_y = max(0.0, min(UNIVERSE_MAX - 1, self.player_y))

        # --- Camera follows ship (with map-edge clamp) ---
        self._update_camera()

        # --- Hyperspace broadcast crawl (incoming-hail overlay) ---
        # Advances if a broadcast is active; fires its on_complete when
        # the duration elapses. The callback typically opens a dialog,
        # which is why we return immediately after firing.
        if self.broadcast is not None and not self.broadcast.fired:
            self.broadcast.elapsed += dt
            if self.broadcast.elapsed >= self.broadcast.duration:
                self.broadcast.fired = True
                cb = self.broadcast.on_complete
                # Clear broadcast BEFORE firing — the callback typically
                # set_scene's away, but if it doesn't, the overlay
                # shouldn't keep rendering on top of the new scene state.
                self.broadcast = None
                cb(self)
                return

        # --- Encounter proximity check (auto-trigger on collision) ---
        for ep in self.encounter_points:
            if ep.fired:
                continue
            d = math.hypot(self.player_x - ep.x, self.player_y - ep.y)
            if d <= ep.trigger_radius:
                ep.fired = True
                ep.on_trigger(self)
                return  # the trigger likely changed scenes

        # Y (fire_secondary) → open a Quasi-Space portal, IF the Sage has
        # gifted the portal spawner. The flag is set by Arilou-Sage dialog
        # side-effects. Without the gift, Y does nothing here.
        if inp.fire_secondary and self.game is not None:
            if self.game.flags.get("has_quasispace_portal"):
                from scz.quasispace.scene import QuasiSpaceScene
                # Spawn the player at the portal nearest to our hyperspace
                # position — the "near the Hearth" portal is closest to
                # Mh-Lai. For the slice we just spawn at portal 1 (Arilou)
                # when leaving the Outpost, portal 0 (Hearth) otherwise.
                # Distance to each portal's exit_x/exit_y picks the right one.
                from scz.quasispace.scene import build_portal_map
                portals = build_portal_map()
                # The entry-portal index is the portal whose exit point is
                # closest to where we currently are in hyperspace. (i.e. you
                # show up *next to* the portal you'd use to come back here.)
                best_i = 0
                best_d = float("inf")
                for i, p in enumerate(portals):
                    d = math.hypot(p.exit_x - self.player_x, p.exit_y - self.player_y)
                    if d < best_d:
                        best_d = d
                        best_i = i
                self.game.set_scene(QuasiSpaceScene(entry_portal_index=best_i))
                return

        # Cancel at top-level scene → open the pause menu overlay
        # (replaces the legacy "cancel quits" behavior per the
        # 2026-05-18 UX bug dispatch). Underlying scene stays loaded;
        # selecting Resume in the overlay returns control here.
        if inp.cancel and self.game is not None and self.game.overlay_scene is None:
            from scz.scenes.pause_menu import PauseMenuScene
            self.game.open_overlay(PauseMenuScene())
            return

        # Note: pressing A near a star engages autopilot (handled above);
        # autopilot then auto-enters the system as soon as the ship is
        # within STAR_ENTER_RADIUS. So there's no separate "press A to
        # enter system" branch — A always means "engage autopilot." If
        # you're already adjacent to a star, the engage-and-auto-enter
        # happens in the same frame and feels like a direct enter.

    def _find_autopilot_target(self) -> dict | None:
        """Find the nearest star ahead of the ship within AUTOPILOT_CONE_DEG.

        Returns the star dict, or None if nothing is in the cone (autopilot
        won't engage if you're not pointing at anything).
        """
        # Heading direction unit vector (heading 0 = up, +y is down)
        fx = math.sin(self.player_heading)
        fy = -math.cos(self.player_heading)
        cone_dot = math.cos(math.radians(AUTOPILOT_CONE_DEG))

        best = None
        best_dist = float("inf")
        for star in self.starmap.stars:
            dx = star["x"] - self.player_x
            dy = star["y"] - self.player_y
            dist = math.hypot(dx, dy)
            if dist < 1.0:
                continue   # we're already on top of it
            # Normalize and dot with forward
            d = (dx * fx + dy * fy) / dist
            if d < cone_dot:
                continue   # not in our forward cone
            if dist < best_dist:
                best_dist = dist
                best = star
        return best

    def _update_camera(self) -> None:
        """Center camera on the ship, clamping to keep view inside the map."""
        self.camera_x = self.player_x
        self.camera_y = self.player_y
        es = self._effective_scale()
        # Half the visible area, in universe units
        half_w_uni = (self.map_view_w / 2) / es
        half_h_uni = (self.map_view_h / 2) / es
        if half_w_uni >= UNIVERSE_MAX / 2:
            # Zoomed out enough that the whole universe fits; center on map
            self.camera_x = UNIVERSE_MAX / 2
        else:
            self.camera_x = max(half_w_uni, min(UNIVERSE_MAX - half_w_uni, self.camera_x))
        if half_h_uni >= UNIVERSE_MAX / 2:
            self.camera_y = UNIVERSE_MAX / 2
        else:
            self.camera_y = max(half_h_uni, min(UNIVERSE_MAX - half_h_uni, self.camera_y))

    def snapshot(self) -> dict | None:
        return {
            "player_x": self.player_x,
            "player_y": self.player_y,
            "player_heading": self.player_heading,
            "zoom": self.zoom,
            "target_zoom": self.target_zoom,
        }

    def restore(self, state: dict) -> None:
        self.player_x = float(state["player_x"])
        self.player_y = float(state["player_y"])
        self.player_heading = float(state["player_heading"])
        if "zoom" in state:
            self.zoom = float(state["zoom"])
        if "target_zoom" in state:
            self.target_zoom = float(state["target_zoom"])

    def render(self, screen: pygame.Surface) -> None:
        screen.fill((6, 6, 18))

        # Clip drawing to the map view area so stars don't paint over the HUD
        # while we're panning/zooming.
        map_rect = pygame.Rect(
            self.map_view_x, self.map_view_y, self.map_view_w, self.map_view_h
        )
        screen.set_clip(map_rect)

        # Universe boundary
        ux0, uy0 = self.universe_to_screen(0.0, 0.0)
        ux1, uy1 = self.universe_to_screen(UNIVERSE_MAX, UNIVERSE_MAX)

        # SC2 starmap backdrop — fills the universe rect, scaled+cached.
        # Drawn BEFORE interactive stars so they sit on top as autopilot
        # targets. Per Rule 4 (KEEP literally): the SC2 map is canonical.
        backdrop_w = int(ux1 - ux0)
        backdrop_h = int(uy1 - uy0)
        backdrop = self._get_scaled_starmap(backdrop_w, backdrop_h)
        if backdrop is not None:
            screen.blit(backdrop, (int(ux0), int(uy0)))

        pygame.draw.rect(
            screen, (30, 30, 60), (ux0, uy0, ux1 - ux0, uy1 - uy0), 1
        )

        # Species-domain boundaries — drawn AFTER backdrop, BEFORE stars
        # so star sprites and labels read on top of the faint territory
        # rings.
        self._draw_species_domains(screen)

        # Stars — pass game so visited / drained systems dim out
        self.starmap.render(screen, self.universe_to_screen, self.game)
        # Star-name labels — tiered by star size (supergiants from far out,
        # dwarfs only when zoomed in close; lore-tagged + Rainbow stars
        # always visible).
        if self.small_font is not None:
            self.starmap.render_labels(
                screen, self.universe_to_screen, self.zoom, self.small_font
            )

        # Echo Sensor ripples — drawn AFTER stars but BEFORE encounter points
        # so that any actual encounter (Coel Tessar pod, etc.) sits on top of
        # the lower-intensity sensor reading. Passive — only renders if the
        # Hyperspace-Echo Sensor module is installed in the player's sensor slot.
        self._draw_ripples(screen)

        # Encounter points — drawn BEFORE the ship so the pod sits on top
        self._draw_encounter_points(screen)

        # Autopilot line — drawn BEFORE the ship so the pod sits on top
        if self.autopilot_target is not None:
            self._draw_autopilot_line(screen)

        # Player ship + always-visible "FURLING SCOUT" label
        px, py = self.universe_to_screen(self.player_x, self.player_y)
        self._draw_player_ship(screen, px, py, self.player_heading)

        # Nearest-star indicator
        nearest = self.starmap.find_nearest_star(
            self.player_x, self.player_y, max_distance=400.0
        )
        in_entry_range = False
        if nearest is not None:
            dx = nearest["x"] - self.player_x
            dy = nearest["y"] - self.player_y
            in_entry_range = math.hypot(dx, dy) <= STAR_ENTER_RADIUS
            if in_entry_range:
                psx, psy = self.universe_to_screen(nearest["x"], nearest["y"])
                pulse = (math.sin(pygame.time.get_ticks() / 200) + 1) / 2
                ring_r = int(14 + pulse * 4)
                pygame.draw.circle(
                    screen,
                    (180 + int(pulse * 50), 220, 255),
                    (int(psx), int(psy)),
                    ring_r,
                    1,
                )

        # Reset clip so HUD draws normally
        screen.set_clip(None)

        # HUD
        self._draw_hud(screen, nearest, in_entry_range)

        # Incoming-hail broadcast overlay — drawn LAST so it sits on top
        # of everything else (HUD included).
        if self.broadcast is not None:
            self._draw_broadcast_overlay(screen)

    # --- helpers ---

    def _draw_player_ship(
        self, screen: pygame.Surface, x: float, y: float, heading: float
    ) -> None:
        # Draw the Furling warp pod (red field wrapping the ship).
        # Player is always FURLING_SCOUT for now; other species' ships will
        # get their own colors when encounter rendering lands.
        self._draw_warp_pod(screen, x, y, heading, "FURLING_SCOUT")

        # The ship itself — a structural ring (carries modular upgrades)
        # with a central oriented "football" hull (crew, engineering,
        # propulsion, command). Heading communicated by the football's
        # orientation, not a separate triangle.
        self._draw_furling_scout(screen, x, y, heading)

        # Always-visible locator ring + pulsing outer ring so the ship is
        # findable even when zoomed all the way out.
        pulse = (math.sin(pygame.time.get_ticks() / 400) + 1) / 2  # 0..1
        pygame.draw.circle(screen, (90, 180, 255), (int(x), int(y)), 38, 1)
        pygame.draw.circle(
            screen,
            (60 + int(pulse * 70), 130 + int(pulse * 60), 200),
            (int(x), int(y)),
            int(48 + pulse * 6),
            1,
        )

        # "FURLING SCOUT" label below the ship, always rendered (small font
        # so it doesn't clutter when zoomed in).
        if self.small_font is not None:
            label = self.small_font.render("FURLING SCOUT", True, (180, 220, 255))
            lw, _ = label.get_size()
            screen.blit(label, (x - lw / 2, y + 50))

    def _draw_furling_scout(
        self, screen: pygame.Surface, x: float, y: float, heading: float
    ) -> None:
        """Draw the ship: a thick structural ring (modular upgrade slots)
        wrapping a long oriented football (crew + engineering + propulsion
        + command). Module slots are visible on the ring — filled ones
        show their installed-module marker; empty ones are faint outlines.

        Reference: the Alcubierre warp-metric image Aaron shared, blue
        ring + central body, but with a longer body and a thicker ring.
        """
        # Forward unit vector (heading 0 = up, +y down in screen)
        fx = math.sin(heading)
        fy = -math.cos(heading)
        # Sideways unit vector
        sx = math.cos(heading)
        sy = math.sin(heading)

        # Central football hull — LONGER along the heading (was 6×3, now 11×3.5)
        football_long = 11.0
        football_short = 3.5
        n_points = 18
        football_pts = []
        for i in range(n_points):
            t = i / n_points * 2.0 * math.pi
            local_forward = football_long * math.cos(t)
            local_side = football_short * math.sin(t)
            football_pts.append(
                (
                    x + local_forward * fx + local_side * sx,
                    y + local_forward * fy + local_side * sy,
                )
            )
        pygame.draw.polygon(screen, (240, 245, 255), football_pts)
        pygame.draw.polygon(screen, (100, 140, 200), football_pts, 1)

        # Cross-hatching ribs along the football (the "stitched" look from
        # the warp-field reference image — suggests hull segmentation).
        for rib_t in (-0.7, -0.35, 0.0, 0.35, 0.7):
            rib_forward = rib_t * football_long * 0.85
            ax = x + rib_forward * fx - football_short * 0.7 * sx
            ay = y + rib_forward * fy - football_short * 0.7 * sy
            bx = x + rib_forward * fx + football_short * 0.7 * sx
            by = y + rib_forward * fy + football_short * 0.7 * sy
            pygame.draw.line(screen, (100, 140, 200), (ax, ay), (bx, by), 1)

        # The ring nacelle — BIGGER + THICKER than the original. Carries
        # the modular upgrade slots; each slot is rendered as a marker
        # on the ring (filled if a module is installed, faint outline if
        # empty).
        ring_outer = 17
        ring_thickness = 4
        # Draw the ring as a thick blue annulus (filled outer minus filled inner)
        pygame.draw.circle(screen, (60, 130, 220), (int(x), int(y)), ring_outer, 0)
        pygame.draw.circle(screen, (10, 20, 40), (int(x), int(y)), ring_outer - ring_thickness, 0)
        # Outline highlights
        pygame.draw.circle(screen, (160, 210, 255), (int(x), int(y)), ring_outer, 1)
        pygame.draw.circle(screen, (90, 140, 200), (int(x), int(y)), ring_outer - ring_thickness, 1)

        # Module slot markers — 7 slots arranged evenly around the ring,
        # starting at the top and going clockwise. Filled slots get a
        # bright dot; empty slots get a thin outline ring.
        self._draw_module_slots(screen, x, y, heading, ring_outer)

    # Module slot order on the ring (canonical) — top, then clockwise.
    # Post 2026-05-18 stacking refactor: 12 generic slots; the ring
    # visual now shows all 12 markers. Slot order matches `SLOTS` in
    # modules.py.
    _MODULE_SLOT_ORDER: tuple[str, ...] = tuple(
        f"slot_{i + 1}" for i in range(12)
    )

    # Module-id → marker color. Falls back to a neutral pale color.
    _MODULE_COLOR_DEFAULTS: dict[str, tuple[int, int, int]] = {
        # Existing modules
        "scanner_mk3": (140, 230, 200),
        "hyperspace_echo_sensor": (200, 140, 230),
        "bio_architect": (130, 230, 130),
        "rainbow_resonator": (255, 220, 100),
        "backup_capacitor": (220, 180, 100),
        "shield_booster_i": (120, 180, 240),
        "beam_mod_i": (255, 200, 130),
        "cargo_pod_plus_50": (180, 200, 220),
        "quasi_drive_compact": (180, 230, 200),
        "crew_archivist": (200, 220, 240),
        "crew_warden": (220, 160, 140),
        "crew_tunneler": (160, 220, 200),
        # New tier-0 quest-reward sensors (2026-05-18 expansion)
        "karavem_aerial_sentry": (240, 200, 240),    # Karavem violet-pink
        "arilou_portal_pathfinder": (140, 220, 200), # Arilou teal-cyan
        "council_migration_beacon": (180, 200, 140), # Council olive-warm
        "stelloth_artifact_locator": (200, 180, 230),# Stelloth lavender
        "taalo_strata_tomography": (180, 160, 140),  # Taalo silicon-tan
        # New tier-1+ purchasable sensors
        "mineral_spectrometer": (200, 160, 230),     # USEFUL-violet kin
        "schematic_resonance_reader": (220, 200, 130),# Schematic gold
        "wreck_pattern_reader": (200, 180, 160),     # Salvage neutral
        "danger_zone_forecaster": (220, 150, 130),   # Warning red-brown
        "melnorme_stellar_class_reader": (180, 140, 220),# Melnorme purple
        # Pre-existing sensor stubs now wired
        "bio_sense_scanner": (150, 220, 150),        # green-bio
        "enemy_scanner": (220, 160, 140),            # enemy red-brown
        "anomaly_scanner": (220, 180, 200),          # anomaly pink
        "hazard_scanner": (240, 180, 100),           # hazard amber
        "lr_mineral_scanner": (180, 130, 220),       # mineral violet
    }

    def _draw_module_slots(
        self, screen: pygame.Surface, x: float, y: float, heading: float, ring_outer: int
    ) -> None:
        """Draw one marker per module slot around the ring.

        Slot positions are static relative to the ship (they rotate with
        the ship's heading so the visual is consistent for each slot
        across orientations).
        """
        if self.game is None:
            return
        slot_count = len(self._MODULE_SLOT_ORDER)
        for i, slot_name in enumerate(self._MODULE_SLOT_ORDER):
            # Angle around the ring, measured from "forward" (top). +y is
            # screen-down so we negate for natural top-clockwise.
            angle = -math.pi / 2 + (i / slot_count) * 2 * math.pi
            # Rotate by ship heading so slots stay in fixed positions
            # relative to the ship body
            world_angle = angle + heading
            sx = math.sin(world_angle)
            sy = -math.cos(world_angle)
            # Position the marker centered on the ring (between inner and outer edges)
            marker_r_offset = ring_outer - 2
            mx = x + sx * marker_r_offset
            my = y + sy * marker_r_offset

            mod_id = self.game.ship_modules.get(slot_name)
            if mod_id is not None:
                # Filled — bright dot in module's color
                color = self._MODULE_COLOR_DEFAULTS.get(mod_id, (220, 230, 250))
                pygame.draw.circle(screen, color, (int(mx), int(my)), 3)
                pygame.draw.circle(screen, (255, 255, 255), (int(mx), int(my)), 4, 1)
            else:
                # Empty — faint dark dot
                pygame.draw.circle(screen, (30, 50, 80), (int(mx), int(my)), 3)
                pygame.draw.circle(screen, (80, 100, 130), (int(mx), int(my)), 3, 1)

    def _draw_warp_pod(
        self,
        screen: pygame.Surface,
        x: float,
        y: float,
        heading: float,
        species_id: str = "FURLING_SCOUT",
    ) -> None:
        """Draw a warp-drive field — round body with a long forward needle.

        Per Aaron's design (Alcubierre-style metric viewed top-down): the
        front of the warp field points 'indefinitely out' from the ship,
        a sharp leading-edge of compressed spacetime. The back is round,
        where the calm 'bubble' contains the ship.

        Forward is *always* extended, even when the ship isn't moving —
        the field is a property of the pod, not a thrust effect.
        """
        colors = get_warp_pod_colors(species_id)
        interior = colors["interior"]
        rim = colors["rim"]
        glow = colors["glow"]

        # Forward and sideways unit vectors (heading 0 = up, +y down in screen)
        fx = math.sin(heading)
        fy = -math.cos(heading)
        sx = math.cos(heading)
        sy = math.sin(heading)

        # Field geometry
        forward_tip = 56.0     # how far ahead the field's leading edge points
        body_radius = 12.0     # round body where the ship sits
        # Where the needle attaches to the body, measured as a half-angle
        # from forward. Smaller = pointier needle; larger = stubbier.
        needle_half_angle = math.radians(24)

        # Build the outline polygon. Start at the tip, go around the right
        # side along the body's back-half arc, end back at the tip.
        outline = []
        # 1. The forward tip
        outline.append(
            (x + forward_tip * fx, y + forward_tip * fy)
        )
        # 2. Body arc — from right needle-attach all the way around the
        # back to the left needle-attach.
        #
        # Right needle attach is at angle (-needle_half_angle) from forward
        # (i.e. just to the right of straight ahead, at the body's edge).
        # Left needle attach is at angle (+needle_half_angle).
        #
        # We sweep from the right side AROUND THE BACK to the left side.
        # In our local frame: forward = +1 along the f-axis; right = +1
        # along the s-axis. An angle of 0 is forward; positive angles rotate
        # counterclockwise (i.e. toward +s = right).
        # The right needle attach sits at angle = -needle_half_angle (toward right).
        # The left needle attach sits at angle = +needle_half_angle (toward left).
        # We go from -needle_half_angle through -π (straight back) to +needle_half_angle.
        # That's a sweep of (2π - 2*needle_half_angle) in the counterclockwise direction.
        arc_start = -needle_half_angle
        arc_end = needle_half_angle - 2 * math.pi   # going counterclockwise
        n_arc = 22
        for i in range(n_arc + 1):
            t = i / n_arc
            angle = arc_start + (arc_end - arc_start) * t
            # In local frame: forward component, side component
            local_forward = math.cos(angle) * body_radius
            local_side = -math.sin(angle) * body_radius
            outline.append(
                (
                    x + local_forward * fx + local_side * sx,
                    y + local_forward * fy + local_side * sy,
                )
            )

        # Outer field glow — translucent, species-tinted halo
        # Stretched along forward direction since the field is asymmetric
        glow_long = int(forward_tip * 1.6)
        glow_wide = int(body_radius * 3)
        glow_surf = pygame.Surface((glow_long * 2, glow_wide * 2), pygame.SRCALPHA)
        cx, cy = glow_long, glow_wide
        glow_rgb = glow[:3]
        glow_a = glow[3] if len(glow) > 3 else 60
        # Draw concentric ellipses (decreasing size, decreasing alpha)
        for scale, alpha_frac in ((1.0, 0.18), (0.75, 0.35), (0.55, 0.6)):
            rect = pygame.Rect(
                int(cx - glow_long * scale),
                int(cy - glow_wide * scale),
                int(2 * glow_long * scale),
                int(2 * glow_wide * scale),
            )
            pygame.draw.ellipse(
                glow_surf,
                (*glow_rgb, int(glow_a * alpha_frac)),
                rect,
            )
        # The glow surface is oriented horizontally with major axis along x.
        # Rotate to match heading. pygame.transform.rotate uses degrees and
        # treats the surface's "right" as 0°. Our heading 0 = up, so we
        # rotate by (90 - heading_degrees) to align the long axis forward.
        heading_deg = math.degrees(heading)
        rotated = pygame.transform.rotate(glow_surf, -heading_deg + 90)
        rrect = rotated.get_rect(center=(int(x), int(y)))
        # Shift the glow forward slightly so its center isn't at the ship
        # but somewhere ahead — biases the bloom toward the leading edge.
        shift = forward_tip * 0.18
        rrect = rrect.move(int(shift * fx), int(shift * fy))
        screen.blit(rotated, rrect, special_flags=pygame.BLEND_PREMULTIPLIED)

        # Field fill (dark interior — the warp bubble's calm region)
        pygame.draw.polygon(screen, interior, outline)
        # Field outline (brighter rim — the edge of warped spacetime)
        pygame.draw.polygon(screen, rim, outline, 2)
        # Brighter tip emphasis — the leading edge of the field
        front_hi_color = tuple(min(255, c + 60) for c in rim)
        # The first three outline points form the tip wedge
        if len(outline) >= 4:
            tip_pts = [outline[1], outline[0], outline[-1]]
            pygame.draw.lines(screen, front_hi_color, False, tip_pts, 2)

    def _echo_sensor_active(self) -> bool:
        """True iff the player's sensor slot holds the Hyperspace-Echo Sensor.

        The Echo Sensor is a *passive, always-on* module — installing it is
        the only action the player takes. From there it continuously surfaces
        dimensional ripples in the hyperspace view.
        """
        if self.game is None:
            return False
        from scz.content.hyperspace_ripples import echo_sensor_installed
        return echo_sensor_installed(self.game)

    def _visible_ripples(self) -> list:
        """Return ripples currently in sensor range of the player ship.

        The sensor is gated by `_echo_sensor_active()` and the per-ripple
        distance is gated by `effective_ripple_range(game)` — upgraded
        sensors (currently only the Echo Sensor; future modules can stack
        the `other_detection_range` delta) see further. Returns [] when
        the sensor isn't installed, no ripples exist, or all ripples are
        out of range.
        """
        if self.game is None or not self._echo_sensor_active():
            return []
        from scz.content.hyperspace_ripples import (
            current_ripples,
            effective_ripple_range,
        )
        ripples = current_ripples(self.game)
        if not ripples:
            return []
        max_range = effective_ripple_range(self.game)
        if max_range <= 0.0:
            return []
        px, py = self.player_x, self.player_y
        max_range_sq = max_range * max_range
        return [
            r for r in ripples
            if (r.x - px) * (r.x - px) + (r.y - py) * (r.y - py) <= max_range_sq
        ]

    def _draw_ripples(self, screen: pygame.Surface) -> None:
        """Render in-range Echo Sensor ripples as pulsing concentric circles.

        Visually distinct from encounter points: smaller base radius, faster
        pulse, faint outer ring + bright inner dot. Reads as "sensor readout
        of something distant" rather than "thing is here right now." Drawn
        before encounter points so actual encounter pods always sit on top.

        Cheap to call every frame; returns immediately if the sensor isn't
        installed, no ripples exist, or all ripples are out of range.
        """
        from scz.content.hyperspace_ripples import RIPPLE_COLORS
        ripples = self._visible_ripples()
        if not ripples:
            return
        ticks = pygame.time.get_ticks()
        for rip in ripples:
            sx, sy = self.universe_to_screen(rip.x, rip.y)
            color = RIPPLE_COLORS.get(rip.kind, (180, 180, 180))
            # Higher intensity → faster pulse (180-360ms period)
            period_ms = 360 - int(rip.intensity * 180)
            pulse = (math.sin(ticks / period_ms) + 1) / 2
            # 6px (faint) to 12px (urgent), modulated by pulse
            base_r = int(6 + rip.intensity * 6)
            outer_r = int(base_r + pulse * 4)
            # Faint halo (sensor "echo")
            halo = (
                min(255, color[0] // 2 + 40),
                min(255, color[1] // 2 + 40),
                min(255, color[2] // 2 + 40),
            )
            pygame.draw.circle(screen, halo, (int(sx), int(sy)), outer_r + 5, 1)
            # Main ring
            pygame.draw.circle(screen, color, (int(sx), int(sy)), outer_r, 1)
            # Bright center dot — the sensor pulse itself
            pygame.draw.circle(screen, color, (int(sx), int(sy)), 2)
            # Optional label below
            if rip.label and self.small_font is not None:
                label = self.small_font.render(rip.label, True, color)
                lw, _ = label.get_size()
                screen.blit(label, (sx - lw // 2, sy + outer_r + 6))

    def _draw_lr_scanner_hud(
        self,
        screen: pygame.Surface,
        x: int,
        y: int,
        nearest: dict | None,
    ) -> int:
        """Render long-range scanner output for the nearest star (if any).

        Reads `system_resource_scan` / `system_anomaly_scan` capability
        stats and surfaces matching `SystemScan` fields. Each capability
        is independent — a module can provide one without the other. The
        cache in `scan_system()` makes this safe to call every frame.

        Returns the updated `y` cursor so the caller can continue stacking
        HUD lines below the scanner output.
        """
        if nearest is None or self.game is None:
            return y
        from scz.content.system_scan import (
            can_scan_anomalies,
            can_scan_resources,
            scan_system,
            visible_anomalies,
        )
        show_resources = can_scan_resources(self.game)
        show_anomalies = can_scan_anomalies(self.game)
        if not (show_resources or show_anomalies):
            return y
        scan = scan_system(nearest)

        # Header for the scanner block
        self._hud_line(screen, x, y, "LR SCAN", (180, 200, 220))
        y += 22

        if show_resources:
            # Mineral totals, color-coded per deposit type. Lines are short
            # so we render them tight (18px row instead of 22).
            tm = scan.total_minerals
            mineral_palette: dict[str, tuple[int, int, int]] = {
                "COMMON": (200, 200, 210),
                "USEFUL": (200, 160, 230),
                "BIO":    (150, 230, 160),
                "ENERGY": (255, 230, 130),
            }
            self._hud_line(
                screen, x + 8, y,
                f"{scan.planet_count} planet{'s' if scan.planet_count != 1 else ''}",
                (180, 190, 200),
            )
            y += 20
            for kind in ("COMMON", "USEFUL", "BIO", "ENERGY"):
                n = tm.get(kind, 0)
                self._hud_line(
                    screen, x + 8, y,
                    f"  {kind:7s}  {n:4d}",
                    mineral_palette[kind] if n > 0 else (110, 110, 130),
                )
                y += 18
            y += 4

        if show_anomalies:
            anomalies = visible_anomalies(scan, self.game)
            if anomalies:
                self._hud_line(
                    screen, x + 8, y,
                    f"{len(anomalies)} anomaly{'s' if len(anomalies) != 1 else ''}",
                    (220, 180, 200),
                )
                y += 20
                # Importance-sorted, most-important-first
                for a in sorted(anomalies, key=lambda x: -x.importance):
                    self._hud_line(
                        screen, x + 8, y, f"  · {a.label}", (200, 170, 200),
                    )
                    y += 18
                y += 4
            else:
                self._hud_line(
                    screen, x + 8, y, "no anomalies", (110, 110, 130),
                )
                y += 20

        return y

    def _draw_extra_sensor_hud(
        self,
        screen: pygame.Surface,
        x: int,
        y: int,
        nearest: dict | None,
    ) -> int:
        """Render status lines for each installed specialty sensor.

        Each line surfaces actionable info from the sensor's primary
        delta. Sensors with no useful info to display (e.g. Migration
        Beacon Receiver with no active migration) still render an
        "online" line so the player sees that the slot is being used.
        """
        if self.game is None:
            return y
        flags = self.game.flags
        eff = self.game.effective_stat

        # Schematic Resonance Reader — show held-schematic count + the
        # carrot-home reminder. The deeper "ping the source system"
        # wiring lands when per-system schematic placement exists.
        if eff("schematic_resonance", 0.0) > 0.0:
            held = self.game.schematics
            n = len(held) if hasattr(held, "__len__") else 0
            if n > 0:
                self._hud_line(
                    screen, x, y,
                    f"SCHEMATIC RESONANCE  {n} held - deliver to Mh-Lai",
                    (220, 200, 130),
                )
            else:
                self._hud_line(
                    screen, x, y,
                    "SCHEMATIC RESONANCE  no schematics held",
                    (130, 130, 150),
                )
            y += 22

        # Wreck Pattern Reader — extended salvage-derelict range.
        if eff("wreck_detect_range", 0.0) > 0.0:
            bonus = eff("wreck_detect_range", 0.0) * 100.0
            self._hud_line(
                screen, x, y,
                f"WRECK READER  +{bonus:.0f}% salvage detect range",
                (200, 180, 160),
            )
            y += 22

        # Stellar Class Reader — show class of nearest star.
        if eff("stellar_class_visible", 0.0) > 0.0 and nearest is not None:
            cls = nearest.get("type") or nearest.get("color") or "unknown"
            self._hud_line(
                screen, x, y,
                f"STELLAR CLASS  {cls}",
                (200, 200, 230),
            )
            y += 22

        # Migration Beacon Receiver — Migration phase indicator.
        if eff("migration_beacon_visible", 0.0) > 0.0:
            phase = flags.get("migration_phase", "phase-1 (assembly)")
            self._hud_line(
                screen, x, y,
                f"MIGRATION BEACON  {phase}",
                (180, 200, 140),
            )
            y += 22

        # Danger-Zone Forecaster — paints the warning text; the
        # zone-overlay render lands when those regions are authored.
        if eff("danger_zone_visible", 0.0) > 0.0:
            zone_count = flags.get("known_danger_zones", 0)
            try:
                n = int(zone_count)
            except (TypeError, ValueError):
                n = 0
            self._hud_line(
                screen, x, y,
                f"DANGER-ZONE FORECAST  {n} zone(s) charted",
                (220, 150, 130),
            )
            y += 22

        # Quasispace Pathfinder — count of pre-revealed portals.
        if eff("qs_portal_pre_reveal", 0.0) > 0.0:
            self._hud_line(
                screen, x, y,
                "QS PATHFINDER  portals pre-mapped",
                (140, 220, 200),
            )
            y += 22

        # Enemy Scanner — extended enemy-ripple detection range.
        if eff("enemy_detect_range", 0.0) > 0.0:
            cloak = eff("cloak_pierce", 0.0)
            label = "ENEMY SCANNER  enemy ripples online"
            if cloak > 0.0:
                label += f"  ·  cloak-pierce {cloak:.1f}"
            self._hud_line(screen, x, y, label, (220, 160, 140))
            y += 22

        # Bio-Sense Scanner — life-detection range bonus shown for the
        # lander-surface mini-game. Visible from hyperspace as
        # confirmation the upgrade is live (the actual extended
        # visibility renders on the planet surface scene).
        if eff("life_detect_range", 0.0) > 0.0:
            self._hud_line(
                screen, x, y,
                "BIO-SENSE  surface life-detect extended",
                (150, 220, 150),
            )
            y += 22

        return y

    def start_broadcast(
        self,
        sender: str,
        text: str,
        color: tuple[int, int, int],
        on_complete: "Callable[[HyperspaceScene], None]",
        duration: float = 5.0,
    ) -> None:
        """Begin a hyperspace incoming-hail crawl. Called from encounter
        triggers that want to build anticipation before opening dialog.

        The text-crawl plays for `duration` game-seconds (in addition to
        whatever the player's stick input does to the ship in that time
        — manual flight is not paused). After the duration elapses,
        `on_complete(scene)` fires; typically that callback opens a
        DialogScene with the actual character.
        """
        self.broadcast = HyperspaceBroadcast(
            sender=sender,
            text=text,
            color=color,
            on_complete=on_complete,
            duration=duration,
        )

    def _draw_broadcast_overlay(self, screen: pygame.Surface) -> None:
        """Render the incoming-hail crawl across the top of the screen.

        Layout: a translucent strip across the upper third, with:
        - A pulsing banner line (sender / "INCOMING HAIL" tag)
        - Body text revealed progressively as `elapsed` grows
        - A subtle progress bar at the bottom of the strip
        """
        assert self.broadcast is not None
        b = self.broadcast
        if self.font is None or self.small_font is None:
            return
        sw, sh = screen.get_size()
        strip_h = int(sh * 0.32)
        # Translucent dark overlay so map shows through faintly
        overlay = pygame.Surface((sw, strip_h), pygame.SRCALPHA)
        overlay.fill((6, 4, 14, 200))
        screen.blit(overlay, (0, 0))
        # Top + bottom border lines in the broadcast color
        pygame.draw.line(screen, b.color, (0, 0), (sw, 0), 2)
        pygame.draw.line(screen, b.color, (0, strip_h), (sw, strip_h), 1)

        # Pulsing sender banner
        ticks = pygame.time.get_ticks()
        pulse = (math.sin(ticks / 220) + 1) / 2
        banner_color = (
            min(255, int(b.color[0] * (0.7 + pulse * 0.3))),
            min(255, int(b.color[1] * (0.7 + pulse * 0.3))),
            min(255, int(b.color[2] * (0.7 + pulse * 0.3))),
        )
        banner = self.font.render(b.sender, True, banner_color)
        bw, _ = banner.get_size()
        screen.blit(banner, ((sw - bw) // 2, 14))

        # Body text — revealed character-by-character over the duration.
        # Word-wrap to fit the strip width with margins.
        reveal_frac = min(1.0, b.elapsed / max(0.1, b.duration * 0.85))
        full_text = b.text
        n_show = int(len(full_text) * reveal_frac)
        shown = full_text[:n_show]
        # Word-wrap shown text
        max_text_w = sw - 120
        line_h = self.font.get_linesize()
        cy = 56
        for raw_line in shown.split("\n"):
            words = raw_line.split(" ")
            line: list[str] = []
            for word in words:
                test = " ".join(line + [word])
                if self.font.size(test)[0] <= max_text_w:
                    line.append(word)
                else:
                    if line:
                        rendered = self.font.render(
                            " ".join(line), True, (220, 220, 240),
                        )
                        screen.blit(rendered, (60, cy))
                        cy += line_h
                    line = [word]
            if line:
                rendered = self.font.render(
                    " ".join(line), True, (220, 220, 240),
                )
                screen.blit(rendered, (60, cy))
                cy += line_h

        # Progress bar at the bottom of the strip
        bar_y = strip_h - 16
        bar_w = sw - 120
        pygame.draw.rect(
            screen, (40, 40, 60), (60, bar_y, bar_w, 4),
        )
        fill_w = int(bar_w * min(1.0, b.elapsed / max(0.1, b.duration)))
        pygame.draw.rect(
            screen, b.color, (60, bar_y, fill_w, 4),
        )

    def _draw_species_domains(self, screen: pygame.Surface) -> None:
        """Render species-domain territory rings.

        Each domain renders as a faint outer boundary + a translucent
        center halo so the player can see who owns what region. Drawn
        before stars so star sprites + autopilot reticles read on top.
        Hidden at very low zoom (whole-galaxy view) where the rings
        would clutter; visible from medium zoom outward.
        """
        from scz.content.species_domains import DOMAINS
        # Don't draw at extreme zoom-out — the galaxy view should be
        # uncluttered. Threshold matches roughly the zoom at which star
        # labels start to appear.
        if self.zoom < 1.5:
            return
        scale = self._effective_scale()
        for d in DOMAINS:
            cx, cy = self.universe_to_screen(d.center_x, d.center_y)
            screen_r = int(d.radius * scale)
            if screen_r < 18:
                continue
            # Outer ring — faint solid color, 2px stroke
            pygame.draw.circle(
                screen, d.color, (int(cx), int(cy)), screen_r, 2,
            )
            # Inner faint glow — uses a temp surface for alpha
            inner_r = max(8, int(screen_r * 0.92))
            glow = pygame.Surface((inner_r * 2, inner_r * 2), pygame.SRCALPHA)
            glow_color = (*d.color, 18)   # very faint fill
            pygame.draw.circle(glow, glow_color, (inner_r, inner_r), inner_r)
            screen.blit(glow, (int(cx) - inner_r, int(cy) - inner_r))
            # Domain name label near center — small, low-key
            if self.small_font is not None and self.zoom >= 2.5:
                label = self.small_font.render(d.name, True, d.color)
                lw, lh = label.get_size()
                screen.blit(label, (int(cx) - lw // 2, int(cy) - screen_r - lh - 4))

    def _draw_encounter_points(self, screen: pygame.Surface) -> None:
        """Render any active hyperspace encounter points as pulsing rings
        with their label. Players see these as 'someone is over there'.
        """
        if not self.encounter_points:
            return
        ticks = pygame.time.get_ticks()
        for ep in self.encounter_points:
            if ep.fired:
                continue
            sx, sy = self.universe_to_screen(ep.x, ep.y)
            pulse = (math.sin(ticks / 240) + 1) / 2
            base_r = 14
            outer_r = int(base_r + pulse * 8)
            pygame.draw.circle(screen, ep.color, (int(sx), int(sy)), outer_r, 2)
            pygame.draw.circle(screen, ep.color, (int(sx), int(sy)), base_r - 4)
            # Label below the ring
            if self.small_font is not None:
                label = self.small_font.render(ep.label, True, ep.color)
                lw, _ = label.get_size()
                screen.blit(label, (sx - lw // 2, sy + outer_r + 4))

    def _draw_autopilot_line(self, screen: pygame.Surface) -> None:
        """Line from ship to autopilot target, with a pulsing marker at the destination."""
        assert self.autopilot_target is not None
        sx, sy = self.universe_to_screen(self.player_x, self.player_y)
        tx, ty = self.universe_to_screen(
            self.autopilot_target["x"], self.autopilot_target["y"]
        )
        # Animated dashed line
        ticks = pygame.time.get_ticks()
        pulse = (math.sin(ticks / 300) + 1) / 2
        col_a = (200 + int(pulse * 55), 180, 100)
        col_b = (140, 100, 60)
        # Simple dashed effect: draw alternating segments
        dx = tx - sx
        dy = ty - sy
        length = math.hypot(dx, dy) or 1.0
        ux, uy = dx / length, dy / length
        segment = 14.0
        gap = 8.0
        step = segment + gap
        offset = (ticks / 30) % step
        d = -offset
        while d < length:
            s0 = max(0.0, d)
            s1 = min(length, d + segment)
            if s1 > s0:
                pygame.draw.line(
                    screen,
                    col_a,
                    (sx + ux * s0, sy + uy * s0),
                    (sx + ux * s1, sy + uy * s1),
                    2,
                )
            d += step

        # Pulsing target reticle
        r = int(18 + pulse * 8)
        pygame.draw.circle(screen, col_a, (int(tx), int(ty)), r, 2)
        pygame.draw.circle(screen, col_b, (int(tx), int(ty)), r + 6, 1)
        # Target name label
        if self.font is not None:
            name = self.autopilot_target.get("cluster_name", "")
            if name:
                txt = self.font.render(f"→ {name}", True, (240, 200, 120))
                screen.blit(txt, (int(tx) + r + 8, int(ty) - 10))

    def _draw_hud(
        self,
        screen: pygame.Surface,
        nearest: dict | None,
        in_entry_range: bool = False,
    ) -> None:
        assert self.font is not None
        assert self.title_font is not None

        # HUD panel background
        pygame.draw.rect(screen, (10, 10, 26), (0, 0, HUD_WIDTH, screen.get_height()))
        pygame.draw.line(
            screen, (40, 40, 70), (HUD_WIDTH, 0), (HUD_WIDTH, screen.get_height()), 1
        )

        x = 22
        y = 24

        title = self.title_font.render(
            "STAR CONTROL ZERO", True, (210, 220, 240)
        )
        screen.blit(title, (x, y))
        y += 34
        sub = self.font.render("The Precursors", True, (140, 160, 200))
        screen.blit(sub, (x, y))
        y += 22
        sub2 = self.font.render("Furling Era", True, (140, 160, 200))
        screen.blit(sub2, (x, y))
        y += 36

        # Player state
        self._hud_line(screen, x, y, "FURLING SCOUT", (180, 220, 255))
        y += 24
        self._hud_line(
            screen, x, y, f"Pos {self.player_x:7.0f} {self.player_y:7.0f}", (150, 170, 200)
        )
        y += 22

        # Domain readout — which species' territory the player ship is
        # currently inside (Wild space if no domain contains the ship).
        from scz.content.species_domains import domain_at
        dom = domain_at(self.player_x, self.player_y)
        if dom is not None:
            self._hud_line(screen, x, y, dom.name, dom.color)
        else:
            self._hud_line(screen, x, y, "Wild space", (130, 130, 150))
        y += 22

        # Time Drive indicator
        if self.game is not None:
            td = self.game.time_drive
            if td.is_ready():
                self._hud_line(screen, x, y, "TIME DRIVE  READY", (130, 230, 180))
            else:
                remaining = td.time_until_ready()
                mm = int(remaining) // 60
                ss = int(remaining) % 60
                self._hud_line(
                    screen,
                    x,
                    y,
                    f"TIME DRIVE  charging {mm}:{ss:02d}",
                    (180, 160, 110),
                )
        y += 32

        # Nearest star
        if nearest is not None:
            self._hud_line(screen, x, y, "NEAREST STAR", (220, 200, 140))
            y += 24
            label = nearest.get("cluster_name", "<unknown>")
            self._hud_line(screen, x, y, label, (240, 230, 200))
            y += 22
            sub = f"{nearest.get('type', '?').replace('_STAR', '').lower()}, {nearest.get('color', '?').replace('_BODY', '').lower()}"
            self._hud_line(screen, x, y, sub, (180, 170, 150))
            y += 22

            # Visit / depletion readout — visible when the player has
            # entered this system at least once. Tracks remaining
            # resource % and undiscovered-anomaly count so the player
            # can decide whether to revisit.
            if self.game is not None:
                from scz.content.system_scan import (
                    is_system_visited,
                    system_anomalies_undiscovered_count,
                    system_dim_tier,
                    system_resources_remaining_pct,
                )
                if is_system_visited(self.game, nearest):
                    tier = system_dim_tier(self.game, nearest)
                    pct = system_resources_remaining_pct(self.game, nearest)
                    n_undisc = system_anomalies_undiscovered_count(
                        self.game, nearest,
                    )
                    if tier == 2:
                        badge_color = (110, 110, 130)   # very dim — drained
                        badge_text = "DRAINED · explored"
                    else:
                        badge_color = (170, 200, 170)   # visited, still worth
                        badge_text = "VISITED"
                    self._hud_line(screen, x, y, badge_text, badge_color)
                    y += 22
                    self._hud_line(
                        screen, x, y,
                        f"resources {int(pct * 100):3d}%   anomalies {n_undisc}",
                        (160, 170, 190),
                    )
                    y += 22
                else:
                    self._hud_line(screen, x, y, "(unexplored)", (130, 160, 180))
                    y += 22

            if nearest.get("defined_name"):
                self._hud_line(
                    screen, x, y, nearest["defined_name"], (180, 220, 180)
                )
                y += 22
            if nearest.get("primordial"):
                self._hud_line(screen, x, y, "(primordial)", (180, 130, 200))
                y += 22
            if in_entry_range:
                # Pulse the prompt color
                pulse = (math.sin(pygame.time.get_ticks() / 200) + 1) / 2
                c = (
                    int(180 + pulse * 75),
                    int(220 + pulse * 35),
                    255,
                )
                self._hud_line(screen, x, y, "[ENTER:  A / Space]", c)
                y += 22

            # LR scanner readout — only rendered if any installed module
            # provides `system_resource_scan` capability. Shows aggregate
            # mineral totals across all planets in the system; these are
            # the same numbers `SystemScene` will surface on entry, since
            # both consume the deterministic `scan_system()` data.
            y = self._draw_lr_scanner_hud(screen, x, y, nearest)
            y += 10
        else:
            self._hud_line(screen, x, y, "Empty space.", (100, 110, 130))
            y += 32

        # Zoom indicator
        zoom_label = f"ZOOM  {self.zoom:.1f}x"
        if abs(self.zoom - self.target_zoom) > 0.05:
            zoom_label += f"  →  {self.target_zoom:.1f}x"
        self._hud_line(screen, x, y, zoom_label, (180, 200, 220))
        y += 22

        # Stats
        self._hud_line(
            screen, x, y, f"{len(self.starmap.stars)} stars", (130, 150, 180)
        )
        y += 22
        self._hud_line(
            screen,
            x,
            y,
            f"{len(self.starmap.rainbow_stars)} Rainbow seeds",
            (200, 180, 120),
        )
        y += 22

        # Echo Sensor status — passive, always-on once installed. Surfaces
        # dimensional ripples in the hyperspace view, filtered to in-range
        # readings only. Empty-state ("online · no ripples in range") is
        # still shown so the player knows the module is doing its job.
        # An upgraded sensor (larger `other_detection_range` delta) sees
        # further; the displayed range reflects current loadout.
        if self._echo_sensor_active():
            from scz.content.hyperspace_ripples import effective_ripple_range
            assert self.game is not None
            n = len(self._visible_ripples())
            r = effective_ripple_range(self.game)
            if n > 0:
                self._hud_line(
                    screen, x, y,
                    f"ECHO SENSOR  range {r:.0f}  ·  {n} ripple{'s' if n != 1 else ''}",
                    (180, 100, 220),
                )
            else:
                self._hud_line(
                    screen, x, y,
                    f"ECHO SENSOR  range {r:.0f}  ·  no ripples in range",
                    (130, 100, 160),
                )
            y += 22

        # Extended sensor HUD (2026-05-18) — each installed specialty
        # sensor gets one status line confirming it's online + showing
        # what it's contributing. Reads effective_stat for each sensor's
        # primary delta; if > 0, renders a line. Lines stack vertically.
        y = self._draw_extra_sensor_hud(screen, x, y, nearest)

        # Autopilot status (prominent if active)
        if self.autopilot_target is not None:
            y += 12
            target_name = self.autopilot_target.get("cluster_name", "?")
            self._hud_line(
                screen, x, y, f"AUTOPILOT  →  {target_name}", (240, 200, 120)
            )
            y += 22
            dx = self.autopilot_target["x"] - self.player_x
            dy = self.autopilot_target["y"] - self.player_y
            self._hud_line(
                screen, x, y, f"  distance: {math.hypot(dx, dy):.0f}", (180, 160, 120)
            )

        # Controls hint pinned to bottom
        controls_y = screen.get_height() - 254
        self._hud_line(screen, x, controls_y, "CONTROLS", (200, 210, 230))
        controls_y += 28
        self._hud_line(
            screen, x, controls_y, "Move:      WASD / L-stick", (130, 150, 180)
        )
        controls_y += 22
        self._hud_line(
            screen, x, controls_y, "Zoom:      - / =  /  LB / RB", (130, 150, 180)
        )
        controls_y += 22
        self._hud_line(
            screen, x, controls_y, "Autopilot: Space / A   (also M / Y)", (130, 150, 180)
        )
        controls_y += 22
        self._hud_line(
            screen, x, controls_y, "Rewind:    R / Back", (130, 150, 180)
        )
        controls_y += 22
        # ("Switch: F1 / R3" debug hint hidden 2026-05-19 — switcher is
        # a development surface, not exposed in normal play. Hotkey
        # still functional silently for dev/testing.)
        self._hud_line(
            screen, x, controls_y, "Pause:     Esc / B", (130, 150, 180)
        )
        controls_y += 22
        # On controller, Start quits directly. On keyboard there's no
        # direct quit binding — the pause menu has a Quit Game item.
        self._hud_line(
            screen, x, controls_y, "Quit:      Start (or Pause -> Quit)",
            (130, 150, 180),
        )

    def _hud_line(
        self,
        screen: pygame.Surface,
        x: int,
        y: int,
        text: str,
        color: tuple[int, int, int],
    ) -> None:
        assert self.font is not None
        surface = self.font.render(text, True, color)
        screen.blit(surface, (x, y))
