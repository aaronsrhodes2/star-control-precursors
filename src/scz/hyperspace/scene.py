"""The hyperspace scene: top-down view of the precursor-era galaxy with the
player ship marker moving across it. Foundation for everything else.
"""

from __future__ import annotations

import math
from pathlib import Path

import pygame

from scz.content.species_visual import get_warp_pod_colors
from scz.engine.scene import Scene
from scz.hyperspace.starmap import Starmap, UNIVERSE_MAX


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


class HyperspaceScene(Scene):
    """The galactic map view with a movable player ship."""

    def __init__(self) -> None:
        super().__init__()
        self.starmap = Starmap(STARMAP_JSON)
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

    def update(self, dt: float, inp) -> None:  # type: ignore[no-untyped-def]
        # --- Zoom (LB / RB on controller, - / = on keyboard) ---
        if inp.menu_prev:
            self.target_zoom = max(self.target_zoom / ZOOM_STEP, MIN_ZOOM)
        if inp.menu_next:
            self.target_zoom = min(self.target_zoom * ZOOM_STEP, MAX_ZOOM)
        # Smooth toward target zoom
        if abs(self.target_zoom - self.zoom) > 1e-4:
            t = min(1.0, dt * ZOOM_LERP)
            self.zoom += (self.target_zoom - self.zoom) * t

        # --- Autopilot engage / disengage ---
        # Y / open_map toggles autopilot: if off, snap to nearest star in
        # heading cone; if on, manual stick deflection (or another press)
        # disengages.
        if inp.open_map:
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

        # Esc/cancel at top-level scene → quit game (no parent to back to)
        if inp.cancel and self.game is not None:
            self.game.quit()
            return

        # Confirm near a star → enter that system (manual override of autopilot)
        if inp.confirm and self.game is not None:
            nearby = self.starmap.find_nearest_star(
                self.player_x, self.player_y, max_distance=STAR_ENTER_RADIUS
            )
            if nearby is not None:
                dx = nearby["x"] - self.player_x
                dy = nearby["y"] - self.player_y
                if math.hypot(dx, dy) <= STAR_ENTER_RADIUS:
                    from scz.system.scene import SystemScene
                    self.game.set_scene(SystemScene(nearby))

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
        pygame.draw.rect(
            screen, (30, 30, 60), (ux0, uy0, ux1 - ux0, uy1 - uy0), 1
        )

        # Stars
        self.starmap.render(screen, self.universe_to_screen)
        # Star-name labels — tiered by star size (supergiants from far out,
        # dwarfs only when zoomed in close; lore-tagged + Rainbow stars
        # always visible).
        if self.small_font is not None:
            self.starmap.render_labels(
                screen, self.universe_to_screen, self.zoom, self.small_font
            )

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

    # --- helpers ---

    def _draw_player_ship(
        self, screen: pygame.Surface, x: float, y: float, heading: float
    ) -> None:
        # Draw the Furling warp pod (red teardrop wrapping the ship).
        # Player is always FURLING_SCOUT for now; other species' ships will
        # get their own colors when encounter rendering lands.
        self._draw_warp_pod(screen, x, y, heading, "FURLING_SCOUT")

        # Triangle with tip in heading direction — the ship itself, inside
        # the pod
        size = 8
        local = [(0, -size), (-size * 0.6, size * 0.5), (size * 0.6, size * 0.5)]
        cos_h = math.cos(heading)
        sin_h = math.sin(heading)
        pts = []
        for lx, ly in local:
            rx = lx * cos_h - ly * sin_h
            ry = lx * sin_h + ly * cos_h
            pts.append((x + rx, y + ry))
        pygame.draw.polygon(screen, (255, 255, 255), pts)
        pygame.draw.polygon(screen, (90, 180, 255), pts, 1)

        # Always-visible locator ring + pulsing outer ring so the ship is
        # findable even when zoomed all the way out.
        pulse = (math.sin(pygame.time.get_ticks() / 400) + 1) / 2  # 0..1
        pygame.draw.circle(screen, (90, 180, 255), (int(x), int(y)), 32, 1)
        pygame.draw.circle(
            screen,
            (60 + int(pulse * 70), 130 + int(pulse * 60), 200),
            (int(x), int(y)),
            int(42 + pulse * 6),
            1,
        )

        # "FURLING SCOUT" label below the ship, always rendered (small font
        # so it doesn't clutter when zoomed in).
        if self.small_font is not None:
            label = self.small_font.render("FURLING SCOUT", True, (180, 220, 255))
            lw, _ = label.get_size()
            screen.blit(label, (x - lw / 2, y + 42))

    def _draw_warp_pod(
        self,
        screen: pygame.Surface,
        x: float,
        y: float,
        heading: float,
        species_id: str = "FURLING_SCOUT",
    ) -> None:
        """Draw a warp-drive pod — an asymmetric teardrop oriented along
        heading. Color set comes from the species palette so each species
        is identifiable on sight in hyperspace.
        """
        colors = get_warp_pod_colors(species_id)
        interior = colors["interior"]
        rim = colors["rim"]
        glow = colors["glow"]

        # Forward unit vector (heading 0 = up, +y down in screen)
        fx = math.sin(heading)
        fy = -math.cos(heading)
        # Sideways unit vector (perpendicular, right of forward)
        sx = math.cos(heading)
        sy = math.sin(heading)

        # Pod dimensions in pixels
        pod_forward = 22.0   # length from center toward heading
        pod_back = 14.0      # length from center away from heading
        pod_side = 14.0      # half-width

        # Build the pod outline as a polygon
        n_points = 28
        outer = []
        for i in range(n_points):
            t = i / n_points * 2.0 * math.pi
            cos_t = math.cos(t)
            sin_t = math.sin(t)
            forward_amount = (pod_forward if cos_t > 0 else pod_back) * cos_t
            side_amount = pod_side * sin_t
            outer.append(
                (
                    x + forward_amount * fx + side_amount * sx,
                    y + forward_amount * fy + side_amount * sy,
                )
            )

        # Outer glow — concentric translucent circles, species-tinted
        glow_pad = 18
        glow_w = int(max(pod_forward, pod_back) * 2 + glow_pad * 2)
        glow_h = int(pod_side * 2 + glow_pad * 2)
        glow_surf = pygame.Surface((glow_w, glow_h), pygame.SRCALPHA)
        cx, cy = glow_w // 2, glow_h // 2
        glow_rgb = glow[:3]
        glow_a = glow[3] if len(glow) > 3 else 60
        for r, alpha_frac in (
            (glow_w // 2, 0.25), (glow_w // 2 - 6, 0.5), (glow_w // 2 - 14, 0.85)
        ):
            if r > 0:
                pygame.draw.circle(
                    glow_surf,
                    (*glow_rgb, int(glow_a * alpha_frac)),
                    (cx, cy),
                    r,
                )
        screen.blit(
            glow_surf, (int(x - cx), int(y - cy)),
            special_flags=pygame.BLEND_PREMULTIPLIED,
        )

        # Pod fill (dark interior)
        pygame.draw.polygon(screen, interior, outer)
        # Pod outline (brighter rim)
        pygame.draw.polygon(screen, rim, outer, 2)
        # Brighter front "arc" for direction sense — slightly brightened rim
        front_hi_color = tuple(min(255, c + 50) for c in rim)
        front_pts = [outer[0], outer[1], outer[n_points - 1]]
        pygame.draw.lines(screen, front_hi_color, False, front_pts, 2)

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
            screen, x, controls_y, "Enter:     Space / A", (130, 150, 180)
        )
        controls_y += 22
        self._hud_line(
            screen, x, controls_y, "Autopilot: M / Y", (130, 150, 180)
        )
        controls_y += 22
        self._hud_line(
            screen, x, controls_y, "Rewind:    R / Back", (130, 150, 180)
        )
        controls_y += 22
        self._hud_line(
            screen, x, controls_y, "Switch:    F1 / R3", (130, 150, 180)
        )
        controls_y += 22
        self._hud_line(
            screen, x, controls_y, "Quit:      Esc / Start", (130, 150, 180)
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
