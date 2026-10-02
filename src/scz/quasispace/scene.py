"""QuasiSpaceScene — interactive QS map with 12 canonical portals.

Parity goals with `HyperspaceScene`:
- Smooth zoom (LB/RB) with target-zoom lerp
- Camera follows the ship at zoom > 1; clamps to map bounds at low zoom
- **Autopilot to nearest in-cone portal** (A / confirm) — analog to
  hyperspace autopilot-to-stars
- Zoom-tier-appropriate portal labels (always visible at default zoom
  since there are only 12, but the bigger labels are reserved for
  higher zoom)
- The SC2 poster map remains the backdrop per Rule 4 (KEEP the SC2
  canonical visual); the interactive layer renders on top

Per Sage Lwen-Olou's canon: *"Twelve in all. One quite near your
Hearth."* The map has 12 portals total. Three are known by default
(canonical slice introduction: Hearth, Arilou Outpost, Distant Fold);
the other nine are **destination-hidden** until first traversal.
Flying through an undiscovered portal sets its
`portal_<id>_discovered` flag and reveals its destination label on
subsequent visits — the QS map is a *discovery puzzle*, not a static
mass-transit grid.

Auto-capture-on-collision is preserved from the prior MVP (per
project canon `feedback_auto_trigger_over_button_press.md` — portals
are navigation completion, not choices). Autopilot doesn't replace
the auto-capture; it just provides a guided thrust toward a selected
portal that will eventually trip the proximity check.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from pathlib import Path

import pygame

from scz.engine.scene import Scene


# --- Map geometry ---------------------------------------------------------
# Quasi-Space coordinate range — much smaller than hyperspace's 10000.
# Whole map fits on screen at base zoom = 1.0.
QS_MAX = 2000.0

# Player speed in Quasi-Space — fast (it's "thinner" per the Sage).
QS_PLAYER_SPEED = 900.0

# Distance at which the player auto-captures into a portal (collision-radius).
PORTAL_USE_RADIUS = 80.0


# --- Zoom + autopilot tuning (mirrors HyperspaceScene constants) ----------
DEFAULT_QS_ZOOM = 1.0
MIN_QS_ZOOM = 0.6
MAX_QS_ZOOM = 6.0
QS_ZOOM_STEP = 1.4         # button-press multiplier
QS_ZOOM_LERP = 8.0          # smoothing per second

# Autopilot aiming cone (half-angle) for portal target acquisition.
QS_AUTOPILOT_CONE_DEG = 60.0   # wider than hyperspace — only 12 targets
QS_AUTOPILOT_CANCEL_THRESHOLD = 0.4

# UI margins (mirror HyperspaceScene)
QS_HUD_WIDTH = 360
QS_MAP_MARGIN = 40


@dataclass
class QSPortal:
    """One Quasi-Space portal. Position is in QS coords; exit is in
    hyperspace coords.

    A portal is *known* if it appears in the slice's introductory
    canon (Sage names three). It is *discovered* once the player has
    flown through it at least once (game flag `portal_<id>_discovered`).
    An undiscovered unknown portal renders its label as "??? fold" or
    similar; once discovered, its real destination label appears.
    """
    id: str             # stable key for the discovered-flag
    qs_x: float
    qs_y: float
    exit_x: float       # hyperspace coords of the exit
    exit_y: float
    label: str          # human-readable destination name
    color: tuple[int, int, int]
    known: bool = False     # True if the slice introduces it by name


def build_portal_map() -> list[QSPortal]:
    """The 12 canonical portals.

    Layout: roughly concentric around (1000, 1000) with the three
    slice-introduced portals at their canonical positions (matching
    the prior MVP), and nine additional portals filling the
    constellation. The 12 exits cover most of the slice's hand-authored
    destinations — Mh-Lai, Arilou Outpost, the three Phase-2 species
    homeworlds (Ossuary / Procyon / Taalo's Stone), Slylandro home,
    Mycon hive, Dnyarri trail, Orz rift, and two "deep folds" for
    distant exploration.

    Sized for the QS_MAX=2000 world with the 200-300px clearance
    around the perimeter so portals don't render under the HUD.
    """
    return [
        # ---- The three slice-introduced (known) portals ----
        QSPortal(
            id="hearth",
            qs_x=400.0,    qs_y=1000.0,
            exit_x=2700.0, exit_y=1600.0,   # near Mh-Lai
            label="near the Hearth",
            color=(255, 220, 140),          # warm amber — home color
            known=True,
        ),
        QSPortal(
            id="arilou_outpost",
            qs_x=1600.0,   qs_y=1000.0,
            exit_x=3500.0, exit_y=2400.0,   # Arilou Outpost
            label="Arilou Outpost",
            color=(140, 240, 210),          # arilou mint
            known=True,
        ),
        QSPortal(
            id="distant_fold",
            qs_x=1000.0,   qs_y=300.0,
            exit_x=6000.0, exit_y=5500.0,   # deep mid-cluster
            label="distant fold",
            color=(200, 160, 240),          # violet
            known=True,
        ),

        # ---- The nine unknown-until-traversed portals ----
        # Each colored with its destination species' canonical hue.
        # Position-arrangement: clock-pattern around the QS map.

        QSPortal(   # NE-ish — Mmrnmhrm Ossuary
            id="ossuary_fold",
            qs_x=1700.0,   qs_y=500.0,
            exit_x=7926.0, exit_y=270.0,
            label="Ossuary",
            color=(220, 220, 240),          # mmrnmhrm silver-white
        ),
        QSPortal(   # E-mid — Mycon hive
            id="mycon_fold",
            qs_x=1800.0,   qs_y=1300.0,
            exit_x=6162.0, exit_y=2263.0,
            label="Mycon hive",
            color=(180, 200, 80),           # mycon chartreuse
        ),
        QSPortal(   # SE — Slylandro home
            id="slylandro_fold",
            qs_x=1500.0,   qs_y=1700.0,
            exit_x=276.0,  exit_y=9810.0,
            label="Slylandro home",
            color=(240, 220, 140),          # slylandro pale gold
        ),
        QSPortal(   # S — Taalo's Stone
            id="taalo_fold",
            qs_x=900.0,    qs_y=1700.0,
            exit_x=700.0,  exit_y=4800.0,
            label="Taalo's Stone",
            color=(140, 220, 240),          # taalo pale crystal-cyan
        ),
        QSPortal(   # SW — Dnyarri trail
            id="dnyarri_fold",
            qs_x=300.0,    qs_y=1500.0,
            exit_x=1984.0, exit_y=6086.0,
            label="Dnyarri trail",
            color=(220, 220, 80),           # dnyarri sickly-yellow
        ),
        QSPortal(   # W-mid — Chenjesu Procyon
            id="procyon_fold",
            qs_x=300.0,    qs_y=600.0,
            exit_x=736.0,  exit_y=2292.0,
            label="Procyon",
            color=(140, 220, 240),          # chenjesu pale cyan
        ),
        QSPortal(   # NW — deep east fold (kept clear of Arilou's exit)
            id="deep_east",
            qs_x=600.0,    qs_y=400.0,
            exit_x=8500.0, exit_y=4500.0,
            label="deep east fold",
            color=(200, 80, 80),            # furling red — frontier
        ),
        QSPortal(   # Central-N — deep north void
            id="deep_north",
            qs_x=1100.0,   qs_y=550.0,
            exit_x=4500.0, exit_y=400.0,
            label="deep north void",
            color=(120, 140, 200),          # cool blue — wild
        ),
        QSPortal(   # Central-S — far SE deep void
            id="deep_se",
            qs_x=1100.0,   qs_y=1450.0,
            exit_x=9500.0, exit_y=9500.0,
            label="deep SE void",
            color=(120, 140, 200),          # cool blue — wild
        ),
    ]


class QuasiSpaceScene(Scene):
    """Interactive Quasi-Space navigation scene with 12 portals.

    Movement: WASD / left-stick. Zoom: -/+ or LB/RB. Autopilot:
    A / Space toggles a guided thrust toward the nearest portal in
    the player's heading cone; manual stick deflection cancels.
    Auto-capture: flying within `PORTAL_USE_RADIUS` of any portal
    transitions the player to HyperspaceScene at the portal's exit.
    B / Backspace bails out (returns to HyperspaceScene at the entry
    portal's exit if known; otherwise at Sol's neighborhood as a
    safe-fallback).
    """

    music_context = "quasispace_travel"  # assets/music/quasispace_travel/

    def __init__(
        self,
        entry_portal_index: int | None = None,
    ) -> None:
        super().__init__()
        self.portals = build_portal_map()

        # Spawn position: at the chosen entry portal, or at the map
        # center for the debug/switcher entry.
        if entry_portal_index is not None and 0 <= entry_portal_index < len(self.portals):
            ep = self.portals[entry_portal_index]
            self.player_x: float = ep.qs_x
            self.player_y: float = ep.qs_y
        else:
            self.player_x = QS_MAX / 2
            self.player_y = QS_MAX / 2
        self.player_heading: float = math.pi
        self.time_in_scene: float = 0.0

        # Entry portal is "muted" for auto-capture until the player
        # leaves its radius — prevents instant re-eject through the
        # portal we just arrived from.
        self.entry_portal_index: int | None = entry_portal_index
        self.entry_portal_muted: bool = entry_portal_index is not None

        # Zoom + camera-follow (mirrors HyperspaceScene)
        self.zoom: float = DEFAULT_QS_ZOOM
        self.target_zoom: float = DEFAULT_QS_ZOOM
        self.camera_x: float = QS_MAX / 2
        self.camera_y: float = QS_MAX / 2

        # Autopilot — when set, the ship auto-thrusts toward this
        # portal until it captures. Stick deflection or A-toggle cancels.
        self.autopilot_target: QSPortal | None = None

        # Set in on_enter once we know the screen size
        self.screen_w: int = 0
        self.screen_h: int = 0
        self.map_view_x: int = 0
        self.map_view_y: int = 0
        self.map_view_w: int = 0
        self.map_view_h: int = 0
        self.base_scale: float = 1.0   # scale at zoom == 1.0
        self.font: pygame.font.Font | None = None
        self.title_font: pygame.font.Font | None = None
        self.small_font: pygame.font.Font | None = None

        # SC2 quasi-space backdrop image + (target_w, target_h) → scaled
        # surface cache (Rule 4: SC2 map is the canonical visual; portals
        # render on top).
        self._qs_image: pygame.Surface | None = None
        self._qs_scaled_cache: tuple[int, int, pygame.Surface] | None = None

    # ------------------------------------------------------------------
    # Scene API
    # ------------------------------------------------------------------

    def on_enter(self) -> None:
        assert self.game is not None
        w, h = self.game.screen.get_size()
        self.screen_w = w
        self.screen_h = h
        # Map view occupies the area right of the HUD panel
        self.map_view_x = QS_HUD_WIDTH + QS_MAP_MARGIN
        self.map_view_y = QS_MAP_MARGIN
        self.map_view_w = w - QS_HUD_WIDTH - 2 * QS_MAP_MARGIN
        self.map_view_h = h - 2 * QS_MAP_MARGIN
        # Base scale fits the whole QS world in the map view at zoom 1.0.
        self.base_scale = min(self.map_view_w, self.map_view_h) / QS_MAX
        self.font = pygame.font.SysFont("consolas", 18)
        self.title_font = pygame.font.SysFont("consolas", 26, bold=True)
        self.small_font = pygame.font.SysFont("consolas", 14)
        self._load_qs_image()

    def _load_qs_image(self) -> None:
        img_path = (
            Path(__file__).resolve().parent.parent.parent.parent
            / "assets" / "maps" / "quasispace.png"
        )
        if not img_path.exists():
            self._qs_image = None
            return
        try:
            self._qs_image = pygame.image.load(str(img_path)).convert()
        except pygame.error:
            self._qs_image = None

    def _get_scaled_qs(
        self, target_w: int, target_h: int
    ) -> pygame.Surface | None:
        """Scaled+cached QS map, quantized to 16px so zoom doesn't
        rebuild every frame."""
        if self._qs_image is None or target_w <= 0 or target_h <= 0:
            return None
        bw = max(16, ((target_w + 8) // 16) * 16)
        bh = max(16, ((target_h + 8) // 16) * 16)
        if (
            self._qs_scaled_cache is not None
            and self._qs_scaled_cache[0] == bw
            and self._qs_scaled_cache[1] == bh
        ):
            return self._qs_scaled_cache[2]
        scaled = pygame.transform.smoothscale(self._qs_image, (bw, bh))
        self._qs_scaled_cache = (bw, bh, scaled)
        return scaled

    # --- transform between QS-space and screen coordinates ---

    def _effective_scale(self) -> float:
        return self.base_scale * self.zoom

    def _qs_to_screen(self, qx: float, qy: float) -> tuple[float, float]:
        es = self._effective_scale()
        center_x = self.map_view_x + self.map_view_w / 2
        center_y = self.map_view_y + self.map_view_h / 2
        return (
            center_x + (qx - self.camera_x) * es,
            center_y + (qy - self.camera_y) * es,
        )

    def update(self, dt: float, inp) -> None:  # type: ignore[no-untyped-def]
        self.time_in_scene += dt

        # --- Zoom (LB/RB on controller, -/= on keyboard) ---
        if inp.zoom_out:
            self.target_zoom = max(self.target_zoom / QS_ZOOM_STEP, MIN_QS_ZOOM)
        if inp.zoom_in:
            self.target_zoom = min(self.target_zoom * QS_ZOOM_STEP, MAX_QS_ZOOM)
        if abs(self.target_zoom - self.zoom) > 1e-4:
            t = min(1.0, dt * QS_ZOOM_LERP)
            self.zoom += (self.target_zoom - self.zoom) * t

        # --- Autopilot toggle (A / Space) ---
        # First press picks the nearest in-cone portal; second press
        # cancels. Manual stick deflection also cancels.
        if inp.confirm:
            if self.autopilot_target is None:
                self.autopilot_target = self._find_autopilot_target()
            else:
                self.autopilot_target = None

        # --- Movement ---
        mx, my = inp.move_x, inp.move_y
        manual_mag = math.hypot(mx, my)

        if self.autopilot_target is not None:
            if manual_mag > QS_AUTOPILOT_CANCEL_THRESHOLD:
                self.autopilot_target = None
            else:
                # Steer toward the target portal
                t = self.autopilot_target
                dx = t.qs_x - self.player_x
                dy = t.qs_y - self.player_y
                dist = math.hypot(dx, dy) or 1.0
                mx, my = dx / dist, dy / dist
                self.player_heading = math.atan2(mx, -my)

        if mx != 0.0 or my != 0.0:
            mag = math.hypot(mx, my)
            if mag > 1.0:
                mx /= mag
                my /= mag
            self.player_heading = math.atan2(mx, -my)
        speed = QS_PLAYER_SPEED * dt
        self.player_x += mx * speed
        self.player_y += my * speed
        self.player_x = max(0.0, min(QS_MAX, self.player_x))
        self.player_y = max(0.0, min(QS_MAX, self.player_y))

        # --- Camera follows ship (clamped at low zoom) ---
        self._update_camera()

        # --- Auto-capture on portal proximity ---
        # The entry portal is muted until the player leaves its radius.
        if self.game is not None:
            if self.entry_portal_muted and self.entry_portal_index is not None:
                ep = self.portals[self.entry_portal_index]
                d_entry = math.hypot(
                    self.player_x - ep.qs_x, self.player_y - ep.qs_y
                )
                if d_entry > PORTAL_USE_RADIUS:
                    self.entry_portal_muted = False
            portal = self._portal_in_range()
            if portal is not None and not (
                self.entry_portal_muted
                and self.entry_portal_index is not None
                and portal is self.portals[self.entry_portal_index]
            ):
                # Reveal the portal's destination on first traversal.
                self.game.flags[f"portal_{portal.id}_discovered"] = True
                from scz.hyperspace.scene import HyperspaceScene
                hyper = HyperspaceScene()
                hyper.player_x = float(portal.exit_x)
                hyper.player_y = float(portal.exit_y)
                self.game.set_scene(hyper)
                return

        # B / Backspace → bail out to hyperspace at the entry portal's
        # exit (or near the Hearth if there's no entry-portal context,
        # e.g. switcher debug).
        if inp.cancel and self.game is not None:
            from scz.hyperspace.scene import HyperspaceScene
            hyper = HyperspaceScene()
            if self.entry_portal_index is not None:
                ep = self.portals[self.entry_portal_index]
                hyper.player_x = float(ep.exit_x)
                hyper.player_y = float(ep.exit_y)
            else:
                # Safe fallback — exit near Sol
                hyper.player_x = 1793.0
                hyper.player_y = 1450.0
            self.game.set_scene(hyper)

    def _update_camera(self) -> None:
        """Center camera on the ship, clamping to keep the view inside
        the QS world bounds at low zoom.
        """
        self.camera_x = self.player_x
        self.camera_y = self.player_y
        es = self._effective_scale()
        half_w = (self.map_view_w / 2) / es
        half_h = (self.map_view_h / 2) / es
        if half_w >= QS_MAX / 2:
            self.camera_x = QS_MAX / 2
        else:
            self.camera_x = max(half_w, min(QS_MAX - half_w, self.camera_x))
        if half_h >= QS_MAX / 2:
            self.camera_y = QS_MAX / 2
        else:
            self.camera_y = max(half_h, min(QS_MAX - half_h, self.camera_y))

    def _find_autopilot_target(self) -> QSPortal | None:
        """Find the nearest portal ahead of the ship within the
        autopilot cone. Returns None if nothing is in the cone."""
        fx = math.sin(self.player_heading)
        fy = -math.cos(self.player_heading)
        cone_dot = math.cos(math.radians(QS_AUTOPILOT_CONE_DEG))
        best: QSPortal | None = None
        best_dist = float("inf")
        for p in self.portals:
            dx = p.qs_x - self.player_x
            dy = p.qs_y - self.player_y
            dist = math.hypot(dx, dy)
            if dist < 1.0:
                continue
            d = (dx * fx + dy * fy) / dist
            if d < cone_dot:
                continue
            if dist < best_dist:
                best_dist = dist
                best = p
        return best

    def render(self, screen: pygame.Surface) -> None:
        # Quasi-Space ambient — deep teal/violet
        screen.fill((12, 8, 26))

        # Clip drawing to the map view area so the QS canvas doesn't
        # paint over the HUD while we're panning/zooming.
        map_rect = pygame.Rect(
            self.map_view_x, self.map_view_y, self.map_view_w, self.map_view_h
        )
        screen.set_clip(map_rect)

        # QS world bounds
        ux0, uy0 = self._qs_to_screen(0.0, 0.0)
        ux1, uy1 = self._qs_to_screen(QS_MAX, QS_MAX)

        # SC2 quasi-space poster backdrop — scaled to the QS world rect,
        # cached per zoom-level. Per Rule 4 the SC2 visual is canonical;
        # the interactive layer renders on top.
        backdrop_w = int(ux1 - ux0)
        backdrop_h = int(uy1 - uy0)
        backdrop = self._get_scaled_qs(backdrop_w, backdrop_h)
        if backdrop is not None:
            screen.blit(backdrop, (int(ux0), int(uy0)))

        # Faint fold-pattern drift dots — ambient parallax texture
        # animated subtly with time_in_scene so the QS feels alive.
        for i in range(120):
            seed = 4242 + i * 9377
            qx = (seed % 10007) / 10007.0 * QS_MAX
            qy = ((seed // 10007) % 10007) / 10007.0 * QS_MAX
            qx = (qx + self.time_in_scene * 8) % QS_MAX
            sx, sy = self._qs_to_screen(qx, qy)
            shade = 30 + (i * 7) % 40
            pygame.draw.circle(
                screen, (shade, shade // 2, shade + 20), (int(sx), int(sy)), 1
            )

        # QS world boundary — faint ring marking the limits
        cx, cy = self._qs_to_screen(QS_MAX / 2, QS_MAX / 2)
        r = int((QS_MAX / 2) * self._effective_scale())
        pygame.draw.circle(screen, (60, 50, 90), (int(cx), int(cy)), r, 1)

        # Portals (with discovery state)
        in_range = self._portal_in_range()
        for p in self.portals:
            discovered = self._is_discovered(p)
            self._draw_portal(
                screen, p, highlighted=(p is in_range), discovered=discovered,
            )

        # Autopilot line — drawn before the ship so the pod sits on top
        if self.autopilot_target is not None:
            self._draw_autopilot_line(screen)

        # Player ship
        self._draw_player(screen)

        # Reset clip so HUD draws normally
        screen.set_clip(None)

        # HUD
        self._draw_hud(screen, in_range)

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _is_discovered(self, portal: QSPortal) -> bool:
        """A portal's destination is shown if it's a known canonical
        portal OR if the player has flown through it at least once.
        """
        if portal.known:
            return True
        if self.game is None:
            return False
        return bool(self.game.flags.get(f"portal_{portal.id}_discovered"))

    def _portal_in_range(self) -> QSPortal | None:
        for p in self.portals:
            d = math.hypot(self.player_x - p.qs_x, self.player_y - p.qs_y)
            if d <= PORTAL_USE_RADIUS:
                return p
        return None

    def _draw_portal(
        self, screen: pygame.Surface, portal: QSPortal,
        highlighted: bool, discovered: bool,
    ) -> None:
        x, y = self._qs_to_screen(portal.qs_x, portal.qs_y)
        es = self._effective_scale()
        # Pulsing ring (highlighted is brighter)
        base_r = max(8, int(22 * es / self.base_scale * 0.6))
        # Cap so very-high-zoom doesn't get absurd
        base_r = min(base_r, 40)
        pulse = (math.sin(self.time_in_scene * 2.0) + 1) / 2

        if discovered:
            color = portal.color
        else:
            # Undiscovered: muted gray-violet — present but unknown
            color = (110, 90, 130)

        if highlighted:
            outer_r = base_r + 14 + int(pulse * 4)
            ring_color = (
                min(255, color[0] + 30),
                min(255, color[1] + 30),
                min(255, color[2] + 30),
            )
        else:
            outer_r = base_r + 8
            ring_color = color
        pygame.draw.circle(screen, ring_color, (int(x), int(y)), outer_r, 2)
        pygame.draw.circle(screen, ring_color, (int(x), int(y)), base_r, 1)
        # Inner glow
        glow = (color[0] // 3, color[1] // 3, color[2] // 3)
        pygame.draw.circle(screen, glow, (int(x), int(y)), max(2, base_r - 6))

        # Label — only at zoom >= 1.0 to avoid clutter at very-zoomed-out
        # views (or at default zoom where the whole map is on screen);
        # discovered portals show their real label, undiscovered show
        # "??? fold".
        if self.font is not None and self.zoom >= 0.9:
            label = portal.label if discovered else "??? fold"
            text = self.font.render(label, True, ring_color)
            screen.blit(text, (x - text.get_width() / 2, y + outer_r + 6))

    def _draw_autopilot_line(self, screen: pygame.Surface) -> None:
        """Animated dashed line from ship to autopilot-target portal."""
        assert self.autopilot_target is not None
        sx, sy = self._qs_to_screen(self.player_x, self.player_y)
        tx, ty = self._qs_to_screen(
            self.autopilot_target.qs_x, self.autopilot_target.qs_y,
        )
        ticks = pygame.time.get_ticks()
        pulse = (math.sin(ticks / 300) + 1) / 2
        col_a = (180, 220 + int(pulse * 35), 200)
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
                    screen, col_a,
                    (sx + ux * s0, sy + uy * s0),
                    (sx + ux * s1, sy + uy * s1),
                    2,
                )
            d += step

    def _draw_player(self, screen: pygame.Surface) -> None:
        x, y = self._qs_to_screen(self.player_x, self.player_y)
        size = 12
        cos_h = math.cos(self.player_heading)
        sin_h = math.sin(self.player_heading)
        local = [(0, -size), (-size * 0.6, size * 0.5), (size * 0.6, size * 0.5)]
        pts = []
        for lx, ly in local:
            rx = lx * cos_h - ly * sin_h
            ry = lx * sin_h + ly * cos_h
            pts.append((x + rx, y + ry))
        pygame.draw.polygon(screen, (240, 240, 255), pts)
        pygame.draw.polygon(screen, (140, 240, 210), pts, 1)
        # Quasi-Space halo — the ship is half-folded too
        pygame.draw.circle(screen, (90, 200, 180), (int(x), int(y)), 20, 1)
        # Always-visible locator pulse so the ship is findable when
        # zoomed all the way out
        pulse = (math.sin(pygame.time.get_ticks() / 400) + 1) / 2
        pygame.draw.circle(
            screen,
            (60 + int(pulse * 70), 130 + int(pulse * 60), 200),
            (int(x), int(y)),
            int(28 + pulse * 6),
            1,
        )

    def _draw_hud(
        self, screen: pygame.Surface, in_range: QSPortal | None,
    ) -> None:
        assert self.font is not None and self.title_font is not None
        pygame.draw.rect(
            screen, (10, 6, 22),
            (0, 0, QS_HUD_WIDTH, screen.get_height()),
        )
        pygame.draw.line(
            screen, (40, 28, 70),
            (QS_HUD_WIDTH, 0), (QS_HUD_WIDTH, screen.get_height()), 1,
        )
        x = 22
        y = 24

        # Title block
        screen.blit(
            self.title_font.render("QUASI-SPACE", True, (210, 220, 250)),
            (x, y),
        )
        y += 34
        # Count discovered / known portals
        discovered_count = sum(
            1 for p in self.portals if self._is_discovered(p)
        )
        screen.blit(
            self.font.render(
                f"the Arilou fold-layer · {discovered_count}/12 folds known",
                True, (160, 180, 220),
            ),
            (x, y),
        )
        y += 28

        # Position + zoom readout
        screen.blit(
            self.font.render(
                f"Pos {self.player_x:5.0f} {self.player_y:5.0f}  "
                f"Zoom {self.zoom:.1f}x",
                True, (150, 170, 200),
            ),
            (x, y),
        )
        y += 28

        # Autopilot status
        if self.autopilot_target is not None:
            label = (
                self.autopilot_target.label
                if self._is_discovered(self.autopilot_target)
                else "??? fold"
            )
            screen.blit(
                self.font.render(
                    f"AUTOPILOT  →  {label}",
                    True, (240, 200, 120),
                ),
                (x, y),
            )
            y += 28
        else:
            y += 8

        # Portal list — discovered shown by destination, unknown by "?"
        screen.blit(
            self.font.render("FOLDS", True, (200, 200, 220)), (x, y),
        )
        y += 26
        for p in self.portals:
            d = math.hypot(self.player_x - p.qs_x, self.player_y - p.qs_y)
            discovered = self._is_discovered(p)
            if p is in_range:
                color = p.color if discovered else (200, 180, 220)
            else:
                color = (150, 160, 180) if discovered else (90, 80, 110)
            label = p.label if discovered else "??? fold"
            screen.blit(
                self.font.render(
                    f"  {label:20s}  d={int(d):4d}",
                    True, color,
                ),
                (x, y),
            )
            y += 20

        # Capture prompt
        y += 6
        if in_range is not None:
            pulse = (math.sin(pygame.time.get_ticks() / 200) + 1) / 2
            c = (
                int(180 + pulse * 75),
                int(220 + pulse * 35),
                int(150 + pulse * 50),
            )
            dest_label = (
                in_range.label if self._is_discovered(in_range) else "???"
            )
            screen.blit(
                self.font.render(
                    f"CAPTURING  ·  exit at {dest_label}",
                    True, c,
                ),
                (x, y),
            )
            y += 22
        else:
            screen.blit(
                self.font.render(
                    "Fly into a fold — capture is automatic",
                    True, (150, 160, 180),
                ),
                (x, y),
            )
            y += 22

        # Controls hint pinned to bottom
        controls_y = screen.get_height() - 200
        screen.blit(
            self.font.render("CONTROLS", True, (200, 210, 230)),
            (x, controls_y),
        )
        controls_y += 28
        for line in (
            "Move:      WASD / L-stick",
            "Autopilot: A / Space",
            "Zoom:      -/+ or LB/RB",
            "Fold:      fly into one (auto-capture)",
            "Bail:      Esc / B / Backspace",
            "Quit:      Start (or Bail -> Pause -> Quit)",
        ):
            screen.blit(
                self.font.render(line, True, (130, 150, 180)),
                (x, controls_y),
            )
            controls_y += 22

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
