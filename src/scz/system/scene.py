"""SystemScene — zoomed-in view of a single star system.

Entered from HyperspaceScene by pressing CONFIRM near a star. Renders the
star at center, planets in orbits, player ship in system-local coordinates.
Press CANCEL to return to hyperspace (player's universe position is restored).

The procedural planet layout is generated from the star's hyperspace coords
as RNG seed (UQM convention). Same star → same planets always.
"""

from __future__ import annotations

import math
import os

import pygame

from scz.engine.scene import Scene
from scz.hyperspace.starmap import STAR_COLOR_RGB, STAR_TYPE_RADIUS
from scz.system.planet import Planet  # generate_system kept for legacy/test paths


# Painted-star sprite cache. Maps STAR_COLOR_RGB key (e.g. "BLUE_BODY") to
# a loaded surface, or False if we've tried and the PNG is missing.
# Populated lazily by _load_star_sprite at first use; survives across
# SystemScene instances since stars are static art.
_STAR_SPRITE_CACHE: dict[str, "pygame.Surface | bool"] = {}

# Maps the UQM-style color name to the painted star sprite filename. Files
# live at assets/stars/star_<color>.png and are 1024×1024 painted disc +
# corona sprites authored from tools/firefly_prompts/tier1_stars/.
_STAR_SPRITE_FILENAMES: dict[str, str] = {
    "BLUE_BODY":   "star_blue.png",
    "WHITE_BODY":  "star_white.png",
    "YELLOW_BODY": "star_yellow.png",
    "GREEN_BODY":  "star_green.png",
    "ORANGE_BODY": "star_orange.png",
    "RED_BODY":    "star_red.png",
}


def _load_star_sprite(color_name: str) -> "pygame.Surface | None":
    """Return the painted star sprite for a STAR_COLOR_RGB key, or None
    if the PNG is missing / failed to load. Result is cached forever.
    """
    cached = _STAR_SPRITE_CACHE.get(color_name)
    if cached is False:
        return None
    if isinstance(cached, pygame.Surface):
        return cached
    fname = _STAR_SPRITE_FILENAMES.get(color_name)
    if fname is None:
        _STAR_SPRITE_CACHE[color_name] = False
        return None
    path = os.path.join("assets", "stars", fname)
    if not os.path.isfile(path):
        _STAR_SPRITE_CACHE[color_name] = False
        return None
    try:
        surf = pygame.image.load(path).convert_alpha()
        _STAR_SPRITE_CACHE[color_name] = surf
        return surf
    except (pygame.error, OSError):
        _STAR_SPRITE_CACHE[color_name] = False
        return None


# How big the system is in system-local coords; the scene auto-fits to window
SYSTEM_VIEW_MARGIN = 60   # pixels around the edges

# Player ship moves faster within a system (smaller scale)
SYSTEM_PLAYER_SPEED = 220.0  # system-local units / sec

# Distance at which the player can "enter orbit" of a planet (system-local units)
PLANET_INTERACT_RADIUS = 40.0

# Auto-zoom — the view tightens as the ship approaches a planet so the
# player isn't squinting at a tiny dot near a tiny dot. Distances are in
# system-local units; zoom is a multiplier on the base "fit the whole
# system" scale.
#
# Near a planet (closer than ZOOM_NEAR_DIST) → MAX_AUTO_ZOOM.
# Far from any planet (farther than ZOOM_FAR_DIST) → MIN_AUTO_ZOOM.
# Linear blend between. ZOOM_LERP_RATE controls how snappily we slide.
MIN_AUTO_ZOOM = 1.0
MAX_AUTO_ZOOM = 4.0
ZOOM_NEAR_DIST = 70.0
ZOOM_FAR_DIST = 300.0
ZOOM_LERP_RATE = 5.5

# System boundary — a circle around the star. Crossing it leaves the
# system to hyperspace at the star's coords. Padding past the outermost
# orbit so the player has room to maneuver around the edge planets.
SYSTEM_BOUNDARY_PAD = 220.0


class SystemScene(Scene):
    """View of a single star system with orbiting planets."""

    music_context = "system_travel"  # assets/music/system_travel/

    def __init__(
        self,
        star: dict,
        planets: list[Planet] | None = None,
        skip_arrival_event: bool = False,
    ) -> None:
        """
        star: the star dict from the starmap (must include x, y, type, color,
              and cluster_name fields).
        planets: optional override. If None, planets are procedurally
                 generated from the star's coordinates (UQM convention).
                 The home system and other lore-significant systems pass a
                 hand-built list.
        skip_arrival_event: True suppresses any auto-launched arrival
                 encounter (e.g. the Melnorme trader at super-giant systems).
                 Used when returning from such an encounter so the player
                 can navigate the system without re-triggering the dialog.
        """
        super().__init__()
        self.star = star
        self.skip_arrival_event = skip_arrival_event
        if planets is not None:
            self.planets = planets
        elif star.get("home_system"):
            # Mh-Lai / home star — hand-built planet layout
            from scz.content.home_system import home_planets
            self.planets = home_planets()
        elif star.get("arilou_outpost"):
            from scz.content.arilou_outpost import arilou_outpost_planets
            self.planets = arilou_outpost_planets()
        elif star.get("defined_name") == "SLYLANDRO":
            from scz.content.beta_corvi import beta_corvi_planets
            self.planets = beta_corvi_planets()
        else:
            # UQM-faithful procgen — mirrors SC2's planet placement for
            # every unnamed star. Uses the ORIGINAL SC2-era star coords
            # as the RNG seed so the resulting maps match canonical SC2,
            # then applies small Furling-era tweaks per system on top.
            from scz.system.uqm_procgen import generate_uqm_system
            # The star dict may have been time-shifted by the precursor-
            # era derivation. If it carries an "original_x/y" pair, use
            # that for the seed; otherwise use the current x/y.
            seed_star = dict(star)
            if "original_x" in star and "original_y" in star:
                seed_star["x"] = star["original_x"]
                seed_star["y"] = star["original_y"]
            self.planets = generate_uqm_system(seed_star)
        # Player position in system-local coords (origin = the star).
        # Spawn just inside the boundary on the +x axis facing inward.
        max_orbit = max((p.orbit_radius for p in self.planets), default=200.0)
        self.system_radius: float = max_orbit + SYSTEM_BOUNDARY_PAD
        self.player_x: float = max_orbit + 80.0
        self.player_y: float = 0.0
        self.player_heading: float = math.pi  # facing inward

        # Time within the scene; used for orbit animation
        self.time_in_scene: float = 0.0

        # Auto-zoom state — zoom is the multiplier on base_scale. The
        # camera follows the ship at high zoom and clamps to the system
        # bounds at low zoom (so the system stays centered when zoomed out).
        self.zoom: float = MIN_AUTO_ZOOM
        self.target_zoom: float = MIN_AUTO_ZOOM
        self.camera_x: float = 0.0
        self.camera_y: float = 0.0

        # Set in on_enter
        self.base_scale: float = 1.0      # system-units to screen-pixels at zoom=1
        self.screen_w: int = 0
        self.screen_h: int = 0
        self.font: pygame.font.Font | None = None
        self.title_font: pygame.font.Font | None = None

    # ------------------------------------------------------------------
    # Scene API
    # ------------------------------------------------------------------

    def on_enter(self) -> None:
        assert self.game is not None
        w, h = self.game.screen.get_size()
        self.screen_w = w
        self.screen_h = h
        # Base scale: at zoom=1.0 the whole system circle fits in the smaller
        # screen dimension (so the boundary is fully visible at zoom-out).
        half = min(w, h) / 2 - SYSTEM_VIEW_MARGIN
        self.base_scale = half / self.system_radius
        self.font = pygame.font.SysFont("consolas", 18)
        self.title_font = pygame.font.SysFont("consolas", 26, bold=True)
        self._update_camera()

        # Arrival event — Melnorme nomadic trader at any super-giant system
        # (tagged MELNORME_PROTO in the precursor-era universe data). The
        # dialog auto-launches on entry; closing it returns to a fresh
        # SystemScene with skip_arrival_event=True so the player can fly
        # around without re-triggering the encounter.
        if (
            not self.skip_arrival_event
            and self.star.get("defined_name") == "MELNORME_PROTO"
        ):
            from scz.dialog.characters import melnorme
            from scz.dialog.scene import DialogScene
            star = self.star
            planets = self.planets

            def _back_to_system() -> "SystemScene":
                return SystemScene(
                    star=star, planets=planets, skip_arrival_event=True
                )

            self.game.set_scene(
                DialogScene(
                    character=melnorme(), parent_factory=_back_to_system
                )
            )
            return

    def update(self, dt: float, inp) -> None:  # type: ignore[no-untyped-def]
        self.time_in_scene += dt

        # Movement
        mx, my = inp.move_x, inp.move_y
        if mx != 0.0 or my != 0.0:
            mag = math.hypot(mx, my)
            if mag > 1.0:
                mx /= mag
                my /= mag
            self.player_heading = math.atan2(mx, -my)
        speed = SYSTEM_PLAYER_SPEED * dt
        self.player_x += mx * speed
        self.player_y += my * speed

        # Crossing the system boundary leaves the system back to hyperspace.
        # Position the player at the boundary on the way out (no teleport
        # snap) and hand off.
        dist_from_star = math.hypot(self.player_x, self.player_y)
        if dist_from_star > self.system_radius and self.game is not None:
            self._exit_to_hyperspace()
            return

        # Auto-zoom: target zoom is high near a planet, low far from any.
        self._update_zoom(dt)

        # Camera follows ship (clamped at low zoom so the boundary stays
        # in frame)
        self._update_camera()

        # Confirm near a planet → enter orbit (unless gas giant).
        # The orbit scene is the canonical safe-zone where Furling cloak
        # engages and Time Drive snapshots; from there A deploys lander.
        if inp.confirm and self.game is not None:
            target = self._planet_in_landing_range()
            if target is not None and target.type != "GAS_GIANT":
                from scz.system.orbit import PlanetOrbitScene
                self.game.set_scene(
                    PlanetOrbitScene(
                        planet=target,
                        star=self.star,
                        parent_scene_cls=SystemScene,
                    )
                )

        # Exit to hyperspace on CANCEL (B / Backspace) — same as crossing
        # the boundary; this just lets the player back out manually.
        if inp.cancel and self.game is not None:
            self._exit_to_hyperspace()

    def _exit_to_hyperspace(self) -> None:
        from scz.hyperspace.scene import HyperspaceScene
        hyper = HyperspaceScene()
        hyper.player_x = float(self.star["x"])
        hyper.player_y = float(self.star["y"])
        self.game.set_scene(hyper)

    def render(self, screen: pygame.Surface) -> None:
        screen.fill((4, 4, 14))

        es = self._effective_scale()
        star_sx, star_sy = self._system_to_screen(0.0, 0.0)

        # System boundary — faint dashed circle. Pulses brighter when the
        # ship is near it (warning that crossing leaves the system).
        dist_from_star = math.hypot(self.player_x, self.player_y)
        edge_frac = min(1.0, dist_from_star / self.system_radius)
        boundary_alpha = int(30 + 70 * edge_frac)
        boundary_color = (
            min(255, 60 + int(120 * edge_frac)),
            min(255, 70 + int(60 * edge_frac)),
            min(255, 100 + int(20 * edge_frac)),
        )
        pygame.draw.circle(
            screen,
            boundary_color,
            (int(star_sx), int(star_sy)),
            int(self.system_radius * es),
            1,
        )

        # Draw orbit guides (faint), camera-relative
        for planet in self.planets:
            r_pix = planet.orbit_radius * es
            pygame.draw.circle(
                screen, (28, 28, 48),
                (int(star_sx), int(star_sy)),
                int(r_pix),
                1,
            )

        # Star at center
        self._draw_star(screen)

        # Planets
        for planet in self.planets:
            self._draw_planet(screen, planet)

        # Player ship
        self._draw_player(screen)

        # Landing-range indicator on the nearest in-range planet
        landing_target = self._planet_in_landing_range()
        if landing_target is not None:
            psx, psy = landing_target.position_at(self.time_in_scene)
            x, y = self._system_to_screen(psx, psy)
            pulse = (math.sin(pygame.time.get_ticks() / 200) + 1) / 2
            ring_color = (
                int(255 - pulse * 60),
                int(240 - pulse * 30),
                int(150 + pulse * 40),
            )
            # Match the scaled planet size used in _draw_planet
            scaled_size = max(3, int(landing_target.size * max(0.6, self.zoom * 0.55)))
            pygame.draw.circle(
                screen,
                ring_color,
                (int(x), int(y)),
                scaled_size + 8 + int(pulse * 4),
                1,
            )

        # HUD
        self._draw_hud(screen, landing_target)

    # ------------------------------------------------------------------
    # Time Drive integration
    # ------------------------------------------------------------------

    def snapshot(self) -> dict | None:
        """The SystemScene IS rewindable — return the rewindable state."""
        return {
            "scene": "SystemScene",
            "star_x": self.star["x"],
            "star_y": self.star["y"],
            "player_x": self.player_x,
            "player_y": self.player_y,
            "player_heading": self.player_heading,
        }

    def restore(self, state: dict) -> None:
        # Only restore if the snapshot was from the same star;
        # cross-system rewinds aren't supported by this simple version.
        if state.get("star_x") == self.star["x"] and state.get("star_y") == self.star["y"]:
            self.player_x = float(state["player_x"])
            self.player_y = float(state["player_y"])
            self.player_heading = float(state["player_heading"])

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    # ------------------------------------------------------------------
    # Camera + zoom
    # ------------------------------------------------------------------

    def _effective_scale(self) -> float:
        return self.base_scale * self.zoom

    def _system_to_screen(self, sx: float, sy: float) -> tuple[float, float]:
        es = self._effective_scale()
        return (
            self.screen_w / 2 + (sx - self.camera_x) * es,
            self.screen_h / 2 + (sy - self.camera_y) * es,
        )

    def _update_zoom(self, dt: float) -> None:
        """Auto-zoom toward MAX near a planet, toward MIN far from any.

        Uses the *raw* distance to the nearest planet (no scale factor).
        Linear blend between ZOOM_NEAR_DIST and ZOOM_FAR_DIST.
        """
        nearest = self._nearest_planet()
        if nearest is None:
            self.target_zoom = MIN_AUTO_ZOOM
        else:
            psx, psy = nearest.position_at(self.time_in_scene)
            d = math.hypot(self.player_x - psx, self.player_y - psy)
            if d <= ZOOM_NEAR_DIST:
                self.target_zoom = MAX_AUTO_ZOOM
            elif d >= ZOOM_FAR_DIST:
                self.target_zoom = MIN_AUTO_ZOOM
            else:
                frac = (ZOOM_FAR_DIST - d) / (ZOOM_FAR_DIST - ZOOM_NEAR_DIST)
                self.target_zoom = (
                    MIN_AUTO_ZOOM + frac * (MAX_AUTO_ZOOM - MIN_AUTO_ZOOM)
                )
        if abs(self.target_zoom - self.zoom) > 1e-4:
            t = min(1.0, dt * ZOOM_LERP_RATE)
            self.zoom += (self.target_zoom - self.zoom) * t

    def _update_camera(self) -> None:
        """Camera follows the ship, clamped at low zoom so the whole
        system boundary stays in frame."""
        self.camera_x = self.player_x
        self.camera_y = self.player_y
        es = self._effective_scale()
        half_w_sys = (self.screen_w / 2) / es
        half_h_sys = (self.screen_h / 2) / es
        R = self.system_radius
        # If the whole circle fits on this axis, center the system.
        if half_w_sys >= R:
            self.camera_x = 0.0
        else:
            self.camera_x = max(-R + half_w_sys, min(R - half_w_sys, self.camera_x))
        if half_h_sys >= R:
            self.camera_y = 0.0
        else:
            self.camera_y = max(-R + half_h_sys, min(R - half_h_sys, self.camera_y))

    def _draw_star(self, screen: pygame.Surface) -> None:
        color = STAR_COLOR_RGB.get(self.star["color"], (220, 200, 120))
        # Star sprite size scales modestly with zoom so it doesn't dominate
        # at high zoom or vanish at low zoom.
        z = max(0.7, min(1.6, self.zoom * 0.7))
        base_radius = int((STAR_TYPE_RADIUS.get(self.star["type"], 2) * 8 + 14) * z)
        cx, cy = self._system_to_screen(0.0, 0.0)

        # Painted-star sprite path — if assets/stars/star_<color>.png
        # exists, blit the painted disc+corona scaled to the same overall
        # size as the procedural render would produce. The sprite's
        # corona extends ~2× the disc radius, so we scale by base_radius*2.
        star_surf = _load_star_sprite(self.star.get("color", ""))
        if star_surf is not None:
            target_diam = base_radius * 4  # disc + corona
            sw, sh = star_surf.get_size()
            longest = max(sw, sh)
            if longest != target_diam and longest > 0:
                f = target_diam / longest
                star_surf = pygame.transform.smoothscale(
                    star_surf, (max(1, int(sw * f)), max(1, int(sh * f))),
                )
            rect = star_surf.get_rect(center=(int(cx), int(cy)))
            screen.blit(star_surf, rect)
            return

        # Procedural fallback — layered concentric circles, used when the
        # painted star sprite isn't installed yet.
        for i in range(4):
            r = base_radius + i * 8
            alpha_color = (color[0] // (i + 2), color[1] // (i + 2), color[2] // (i + 2))
            pygame.draw.circle(screen, alpha_color, (int(cx), int(cy)), int(r))
        # Core
        pygame.draw.circle(screen, color, (int(cx), int(cy)), int(base_radius))
        # Subtle white-hot core dot
        pygame.draw.circle(
            screen,
            (
                min(255, color[0] + 50),
                min(255, color[1] + 50),
                min(255, color[2] + 50),
            ),
            (int(cx), int(cy)),
            int(base_radius / 3),
        )

    def _draw_planet(self, screen: pygame.Surface, planet: Planet) -> None:
        sx, sy = planet.position_at(self.time_in_scene)
        x, y = self._system_to_screen(sx, sy)
        # Planet sprite size scales with zoom so it grows as we close in.
        size = max(3, int(planet.size * max(0.6, self.zoom * 0.55)))

        # Try the canonical UQM sprite. Use "med" at moderate zoom, "big"
        # when zoomed in (size * 2 is the rendered diameter; the sprite
        # gets nearest-neighbor scaled to that).
        diam = size * 2
        sprite = None
        # 1. Animated rotation sphere (named planets) — same texture as
        #    orbit + combat view so the planet IS consistent across
        #    view transitions
        from scz.content.planet_sphere import has_sphere, get_frame
        planet_id = getattr(planet, "id", None) or planet.name.lower().replace(" ", "_")
        if has_sphere(planet_id):
            sprite = get_frame(planet_id, self.time_in_scene, diameter=diam)
        if sprite is None:
            from scz.content.planet_sprites import (
                scaled_sprite, scaled_sprite_for_legacy,
            )
            which_size = "sml" if diam <= 24 else ("med" if diam <= 48 else "big")
            uqm_type = getattr(planet, "uqm_type", None)
            if uqm_type:
                sprite = scaled_sprite(uqm_type, diam, size=which_size)
            if sprite is None:
                sprite = scaled_sprite_for_legacy(planet.type, diam, size=which_size)

        if sprite is not None:
            ssw, ssh = sprite.get_size()
            screen.blit(sprite, (int(x) - ssw // 2, int(y) - ssh // 2))
            return

        # Procedural fallback (shouldn't fire for slice planets)
        pygame.draw.circle(screen, planet.color, (int(x), int(y)), size)
        dx, dy = sx, sy
        d = math.hypot(dx, dy) or 1.0
        ox = -dx / d * size * 0.3
        oy = -dy / d * size * 0.3
        shadow = (planet.color[0] // 3, planet.color[1] // 3, planet.color[2] // 3)
        pygame.draw.circle(
            screen, shadow, (int(x + ox), int(y + oy)), int(size * 0.85)
        )
        ox2 = dx / d * size * 0.2
        oy2 = dy / d * size * 0.2
        pygame.draw.circle(
            screen, planet.color, (int(x + ox2), int(y + oy2)), int(size * 0.7)
        )

    def _draw_player(self, screen: pygame.Surface) -> None:
        x, y = self._system_to_screen(self.player_x, self.player_y)
        size = 10
        cos_h = math.cos(self.player_heading)
        sin_h = math.sin(self.player_heading)
        local = [(0, -size), (-size * 0.6, size * 0.5), (size * 0.6, size * 0.5)]
        pts = []
        for lx, ly in local:
            rx = lx * cos_h - ly * sin_h
            ry = lx * sin_h + ly * cos_h
            pts.append((x + rx, y + ry))
        pygame.draw.polygon(screen, (255, 255, 255), pts)
        pygame.draw.polygon(screen, (90, 180, 255), pts, 1)
        pygame.draw.circle(screen, (60, 90, 130), (int(x), int(y)), 18, 1)

    def _nearest_planet(self) -> Planet | None:
        best = None
        best_d = float("inf")
        for p in self.planets:
            psx, psy = p.position_at(self.time_in_scene)
            d = math.hypot(self.player_x - psx, self.player_y - psy)
            if d < best_d:
                best_d = d
                best = p
        return best

    def _planet_in_landing_range(self) -> Planet | None:
        """Return the nearest planet if it's within landing range, else None."""
        for p in self.planets:
            psx, psy = p.position_at(self.time_in_scene)
            d = math.hypot(self.player_x - psx, self.player_y - psy)
            # Landing range scales with planet size (gas giants visible from
            # further). Use the base scale so the range is zoom-independent.
            range_units = PLANET_INTERACT_RADIUS + p.size / self.base_scale
            if d <= range_units:
                return p
        return None

    def _draw_hud(
        self, screen: pygame.Surface, landing_target: Planet | None = None
    ) -> None:
        assert self.font is not None
        assert self.title_font is not None

        HUD_W = 360
        pygame.draw.rect(screen, (10, 10, 26), (0, 0, HUD_W, screen.get_height()))
        pygame.draw.line(screen, (40, 40, 70), (HUD_W, 0), (HUD_W, screen.get_height()), 1)

        x = 22
        y = 24
        title = self.title_font.render(
            self.star.get("cluster_name", "Unknown System"), True, (210, 220, 240)
        )
        screen.blit(title, (x, y))
        y += 34

        line = (
            f"{self.star.get('type', '?').replace('_STAR', '').lower()}, "
            f"{self.star.get('color', '?').replace('_BODY', '').lower()}"
        )
        screen.blit(self.font.render(line, True, (160, 180, 210)), (x, y))
        y += 24

        if self.star.get("defined_name"):
            screen.blit(
                self.font.render(self.star["defined_name"], True, (180, 220, 180)),
                (x, y),
            )
            y += 24
        if self.star.get("primordial"):
            screen.blit(
                self.font.render("(primordial)", True, (180, 130, 200)), (x, y)
            )
            y += 24

        y += 12
        screen.blit(
            self.font.render(f"PLANETS  {len(self.planets)}", True, (200, 200, 220)),
            (x, y),
        )
        y += 26
        # List planets briefly; highlight the landing target
        for p in self.planets:
            label = f"  {p.name}  —  {p.type.lower()}"
            if p is landing_target:
                color = (220, 230, 180)
            else:
                color = (150, 160, 180)
            screen.blit(self.font.render(label, True, color), (x, y))
            y += 22

        # Edge-of-system warning
        dist = math.hypot(self.player_x, self.player_y)
        edge_frac = dist / self.system_radius
        if edge_frac > 0.85:
            y += 8
            pulse = (math.sin(pygame.time.get_ticks() / 180) + 1) / 2
            warn_color = (
                int(220 - pulse * 30),
                int(160 - pulse * 60),
                int(80 - pulse * 30),
            )
            screen.blit(
                self.font.render(
                    "APPROACHING SYSTEM EDGE", True, warn_color
                ),
                (x, y),
            )
            y += 22
            screen.blit(
                self.font.render(
                    "  cross to exit to hyperspace", True, (180, 160, 130)
                ),
                (x, y),
            )
            y += 22

        # Landing prompt
        if landing_target is not None:
            y += 8
            if landing_target.type == "GAS_GIANT":
                screen.blit(
                    self.font.render(
                        "Cannot land on gas giant", True, (220, 130, 100)
                    ),
                    (x, y),
                )
            else:
                pulse = (math.sin(pygame.time.get_ticks() / 200) + 1) / 2
                c = (
                    int(180 + pulse * 75),
                    int(220 + pulse * 35),
                    int(150 + pulse * 50),
                )
                screen.blit(
                    self.font.render(
                        f"[ENTER ORBIT of {landing_target.name}:  A / Space]", True, c
                    ),
                    (x, y),
                )
            y += 22

        # Time Drive readout (consistent with hyperspace HUD)
        y += 12
        if self.game is not None:
            td = self.game.time_drive
            if td.is_ready():
                screen.blit(
                    self.font.render("TIME DRIVE  READY", True, (130, 230, 180)),
                    (x, y),
                )
            else:
                remaining = td.time_until_ready()
                mm = int(remaining) // 60
                ss = int(remaining) % 60
                screen.blit(
                    self.font.render(
                        f"TIME DRIVE  charging {mm}:{ss:02d}", True, (180, 160, 110)
                    ),
                    (x, y),
                )

        # Controls hint pinned to bottom
        controls_y = screen.get_height() - 180
        screen.blit(self.font.render("CONTROLS", True, (200, 210, 230)), (x, controls_y))
        controls_y += 28
        for line in (
            "Move:    WASD / L-stick",
            "Leave:   Backspace / B",
            "Rewind:  R / Back",
            "Quit:    Esc / Start",
        ):
            screen.blit(self.font.render(line, True, (130, 150, 180)), (x, controls_y))
            controls_y += 22
