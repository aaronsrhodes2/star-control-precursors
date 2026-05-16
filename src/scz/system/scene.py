"""SystemScene — zoomed-in view of a single star system.

Entered from HyperspaceScene by pressing CONFIRM near a star. Renders the
star at center, planets in orbits, player ship in system-local coordinates.
Press CANCEL to return to hyperspace (player's universe position is restored).

The procedural planet layout is generated from the star's hyperspace coords
as RNG seed (UQM convention). Same star → same planets always.
"""

from __future__ import annotations

import math

import pygame

from scz.engine.scene import Scene
from scz.hyperspace.starmap import STAR_COLOR_RGB, STAR_TYPE_RADIUS
from scz.system.planet import Planet, generate_system


# How big the system is in system-local coords; the scene auto-fits to window
SYSTEM_VIEW_MARGIN = 60   # pixels around the edges

# Player ship moves faster within a system (smaller scale)
SYSTEM_PLAYER_SPEED = 220.0  # system-local units / sec

# Distance at which the player can "enter orbit" of a planet (system-local units)
PLANET_INTERACT_RADIUS = 40.0


class SystemScene(Scene):
    """View of a single star system with orbiting planets."""

    def __init__(self, star: dict) -> None:
        """
        star: the star dict from the starmap (must include x, y, type, color,
              and cluster_name fields).
        """
        super().__init__()
        self.star = star
        self.planets: list[Planet] = generate_system(
            star_x=star["x"],
            star_y=star["y"],
            star_type=star["type"],
            star_color=star["color"],
            cluster_name=star.get("cluster_name", "unknown"),
        )
        # Player position in system-local coords, starts at the "edge"
        max_orbit = max((p.orbit_radius for p in self.planets), default=200.0)
        self.player_x: float = max_orbit + 80.0
        self.player_y: float = 0.0
        self.player_heading: float = math.pi  # facing inward

        # Time within the scene; used for orbit animation
        self.time_in_scene: float = 0.0

        # Set in on_enter
        self.scale: float = 1.0           # system-units to screen-pixels
        self.center_x: float = 0.0
        self.center_y: float = 0.0
        self.font: pygame.font.Font | None = None
        self.title_font: pygame.font.Font | None = None

    # ------------------------------------------------------------------
    # Scene API
    # ------------------------------------------------------------------

    def on_enter(self) -> None:
        assert self.game is not None
        w, h = self.game.screen.get_size()
        # Fit the maximum orbit (plus the player's spawn distance) in the view
        max_orbit = max((p.orbit_radius for p in self.planets), default=200.0)
        view_radius = max_orbit + 120.0  # extra space for player movement
        half = min(w, h) / 2 - SYSTEM_VIEW_MARGIN
        self.scale = half / view_radius
        self.center_x = w / 2
        self.center_y = h / 2
        self.font = pygame.font.SysFont("consolas", 18)
        self.title_font = pygame.font.SysFont("consolas", 26, bold=True)

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
        # Clamp to a reasonable bounding box
        max_orbit = max((p.orbit_radius for p in self.planets), default=200.0)
        max_dist = max_orbit + 150.0
        dist = math.hypot(self.player_x, self.player_y)
        if dist > max_dist:
            self.player_x = self.player_x * (max_dist / dist)
            self.player_y = self.player_y * (max_dist / dist)

        # Exit to hyperspace on CANCEL (B / Backspace)
        if inp.cancel and self.game is not None:
            # Lazy import to avoid circular dependency
            from scz.hyperspace.scene import HyperspaceScene
            # Build a hyperspace scene at the position of this star
            hyper = HyperspaceScene()
            hyper.player_x = float(self.star["x"])
            hyper.player_y = float(self.star["y"])
            self.game.set_scene(hyper)

    def render(self, screen: pygame.Surface) -> None:
        screen.fill((4, 4, 14))

        # Draw orbit guides (faint)
        for planet in self.planets:
            r = planet.orbit_radius * self.scale
            pygame.draw.circle(
                screen, (28, 28, 48),
                (int(self.center_x), int(self.center_y)),
                int(r),
                1,
            )

        # Star at center
        self._draw_star(screen)

        # Planets
        for planet in self.planets:
            self._draw_planet(screen, planet)

        # Player ship
        self._draw_player(screen)

        # HUD
        self._draw_hud(screen)

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

    def _system_to_screen(self, sx: float, sy: float) -> tuple[float, float]:
        return (self.center_x + sx * self.scale, self.center_y + sy * self.scale)

    def _draw_star(self, screen: pygame.Surface) -> None:
        color = STAR_COLOR_RGB.get(self.star["color"], (220, 200, 120))
        base_radius = STAR_TYPE_RADIUS.get(self.star["type"], 2) * 8 + 14
        cx, cy = self.center_x, self.center_y
        # Outer glow
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
        # Body
        pygame.draw.circle(screen, planet.color, (int(x), int(y)), planet.size)
        # Light/shadow hint (a faint darker arc opposite the star)
        dx, dy = sx, sy
        d = math.hypot(dx, dy) or 1.0
        ox = -dx / d * planet.size * 0.3
        oy = -dy / d * planet.size * 0.3
        shadow = (planet.color[0] // 3, planet.color[1] // 3, planet.color[2] // 3)
        pygame.draw.circle(
            screen, shadow, (int(x + ox), int(y + oy)), int(planet.size * 0.85)
        )
        # Repaint the lit side
        ox2 = dx / d * planet.size * 0.2
        oy2 = dy / d * planet.size * 0.2
        pygame.draw.circle(
            screen, planet.color, (int(x + ox2), int(y + oy2)), int(planet.size * 0.7)
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
        if best is not None and best_d <= PLANET_INTERACT_RADIUS + best.size / self.scale:
            return best
        return best  # always return nearest; let HUD show interact-range separately

    def _draw_hud(self, screen: pygame.Surface) -> None:
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
        # List planets briefly
        for p in self.planets:
            label = f"  {p.name}  —  {p.type.lower()}"
            screen.blit(self.font.render(label, True, (150, 160, 180)), (x, y))
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
