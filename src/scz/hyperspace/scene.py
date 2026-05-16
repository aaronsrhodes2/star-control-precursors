"""The hyperspace scene: top-down view of the precursor-era galaxy with the
player ship marker moving across it. Foundation for everything else.
"""

from __future__ import annotations

import math
from pathlib import Path

import pygame

from scz.engine.scene import Scene
from scz.hyperspace.starmap import Starmap, UNIVERSE_MAX


# Where the package finds its content files
_CONTENT_ROOT = Path(__file__).resolve().parent.parent / "content"
STARMAP_JSON = _CONTENT_ROOT / "universe" / "stars.json"

# Ship movement speed in universe units per second
PLAYER_SPEED = 1200.0

# Sol's coordinates in the precursor-era universe (the player's home, before
# humans exist). From src/scz/content/universe/stars.json.
SOL_X = 1793.0
SOL_Y = 1450.0

# UI margins. Sized to look good at 1920x1080. The HUD scales naturally to
# fit narrower windows because the map area auto-fits the remaining space.
HUD_WIDTH = 360
MAP_MARGIN = 40


class HyperspaceScene(Scene):
    """The galactic map view with a movable player ship."""

    def __init__(self) -> None:
        super().__init__()
        self.starmap = Starmap(STARMAP_JSON)
        self.player_x: float = SOL_X
        self.player_y: float = SOL_Y
        self.player_heading: float = 0.0  # radians, 0 = up

        # Set in on_enter once we know the screen size
        self.map_scale: float = 1.0
        self.map_offset_x: float = 0.0
        self.map_offset_y: float = 0.0
        self.font: pygame.font.Font | None = None
        self.title_font: pygame.font.Font | None = None

    # --- transform between universe and screen coordinates ---

    def universe_to_screen(self, ux: float, uy: float) -> tuple[float, float]:
        sx = self.map_offset_x + ux * self.map_scale
        sy = self.map_offset_y + uy * self.map_scale
        return sx, sy

    # --- Scene API ---

    def on_enter(self) -> None:
        assert self.game is not None
        w, h = self.game.screen.get_size()
        map_area_w = w - HUD_WIDTH - 2 * MAP_MARGIN
        map_area_h = h - 2 * MAP_MARGIN
        scale = min(map_area_w / UNIVERSE_MAX, map_area_h / UNIVERSE_MAX)
        self.map_scale = scale
        map_w = UNIVERSE_MAX * scale
        map_h = UNIVERSE_MAX * scale
        self.map_offset_x = HUD_WIDTH + MAP_MARGIN + (map_area_w - map_w) / 2
        self.map_offset_y = MAP_MARGIN + (map_area_h - map_h) / 2

        # Init fonts — sized for 1920x1080. We could scale by window height
        # but for now keep them fixed since 1920x1080 is the target.
        self.font = pygame.font.SysFont("consolas", 18)
        self.title_font = pygame.font.SysFont("consolas", 26, bold=True)

    def update(self, dt: float, inp) -> None:  # type: ignore[no-untyped-def]
        # Move the player ship in universe space
        mx, my = inp.move_x, inp.move_y
        if mx != 0.0 or my != 0.0:
            # Normalize so diagonal isn't faster
            mag = math.hypot(mx, my)
            if mag > 1.0:
                mx /= mag
                my /= mag
            # Update heading (where the ship points)
            self.player_heading = math.atan2(mx, -my)  # 0 = up
        speed = PLAYER_SPEED * dt
        self.player_x += mx * speed
        self.player_y += my * speed
        # Clamp to universe bounds
        self.player_x = max(0.0, min(UNIVERSE_MAX - 1, self.player_x))
        self.player_y = max(0.0, min(UNIVERSE_MAX - 1, self.player_y))

    def snapshot(self) -> dict | None:
        return {
            "player_x": self.player_x,
            "player_y": self.player_y,
            "player_heading": self.player_heading,
        }

    def restore(self, state: dict) -> None:
        self.player_x = float(state["player_x"])
        self.player_y = float(state["player_y"])
        self.player_heading = float(state["player_heading"])

    def render(self, screen: pygame.Surface) -> None:
        screen.fill((6, 6, 18))

        # Universe boundary
        ux0, uy0 = self.universe_to_screen(0.0, 0.0)
        ubw = UNIVERSE_MAX * self.map_scale
        ubh = UNIVERSE_MAX * self.map_scale
        pygame.draw.rect(screen, (30, 30, 60), (ux0, uy0, ubw, ubh), 1)

        # Stars
        self.starmap.render(screen, self.universe_to_screen)

        # Player ship — small triangle pointing in heading direction
        px, py = self.universe_to_screen(self.player_x, self.player_y)
        self._draw_player_ship(screen, px, py, self.player_heading)

        # Nearest-star indicator
        nearest = self.starmap.find_nearest_star(
            self.player_x, self.player_y, max_distance=400.0
        )

        # HUD
        self._draw_hud(screen, nearest)

    # --- helpers ---

    def _draw_player_ship(
        self, screen: pygame.Surface, x: float, y: float, heading: float
    ) -> None:
        # Triangle with tip in heading direction
        size = 10
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

        # Player position crosshair (subtle)
        pygame.draw.circle(screen, (60, 90, 130), (int(x), int(y)), 18, 1)

    def _draw_hud(self, screen: pygame.Surface, nearest: dict | None) -> None:
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
            y += 10
        else:
            self._hud_line(screen, x, y, "Empty space.", (100, 110, 130))
            y += 32

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

        # Controls hint pinned to bottom
        controls_y = screen.get_height() - 180
        self._hud_line(screen, x, controls_y, "CONTROLS", (200, 210, 230))
        controls_y += 28
        self._hud_line(
            screen, x, controls_y, "Move:    WASD / L-stick", (130, 150, 180)
        )
        controls_y += 22
        self._hud_line(
            screen, x, controls_y, "Map:     M / Y", (130, 150, 180)
        )
        controls_y += 22
        self._hud_line(
            screen, x, controls_y, "Rewind:  R / Back", (130, 150, 180)
        )
        controls_y += 22
        self._hud_line(
            screen, x, controls_y, "Quit:    Esc / Start", (130, 150, 180)
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
