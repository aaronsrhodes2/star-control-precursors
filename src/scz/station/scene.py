"""StationScene — Mh-Lai Station, the Furling home base.

The slice's hub. Where the player starts, returns to trade, upgrades the
ship, talks to the commander. A simple top-level menu lists the available
actions; each opens the relevant scene.

Visual: backdrop with a stylized station silhouette + the Mh-Lai planet
behind it + a starfield. The menu floats on the left side. The right side
shows current ship stats. Real station art will come later via Flask-SD.
"""

from __future__ import annotations

import math
import random

import pygame

from scz.engine.scene import Scene


# Menu actions — label and action key.
ACTIONS: list[tuple[str, str]] = [
    ("Talk to Commander Halia", "talk"),
    ("Trade resources", "trade"),
    ("Upgrade ship", "upgrade"),
    ("Undock — Mh-Lai system view", "undock"),
]


class StationScene(Scene):
    """Mh-Lai Station hub view."""

    # Class-level seeded starfield so it doesn't shimmer on re-entry
    _starfield: list[tuple[int, int, int]] | None = None

    def __init__(self) -> None:
        super().__init__()
        self.selected_action: int = 0
        self.fonts: dict[str, pygame.font.Font] = {}
        self.time_in_scene: float = 0.0

    def on_enter(self) -> None:
        self.fonts["title"] = pygame.font.SysFont("consolas", 56, bold=True)
        self.fonts["subtitle"] = pygame.font.SysFont("consolas", 22)
        self.fonts["menu"] = pygame.font.SysFont("consolas", 28)
        self.fonts["small"] = pygame.font.SysFont("consolas", 16)
        # Initialize the starfield once
        if StationScene._starfield is None:
            rng = random.Random(7331)
            stars = []
            for _ in range(220):
                x = rng.randint(0, 1920)
                y = rng.randint(0, 1080)
                brightness = rng.randint(80, 220)
                stars.append((x, y, brightness))
            StationScene._starfield = stars

    def update(self, dt: float, inp) -> None:  # type: ignore[no-untyped-def]
        self.time_in_scene += dt

        # B → quit (Station is the top-level scene; backing out exits)
        if inp.cancel and self.game is not None:
            self.game.quit()
            return

        # Menu navigation
        n = len(ACTIONS)
        if inp.menu_up:
            self.selected_action = (self.selected_action - 1) % n
        elif inp.menu_down:
            self.selected_action = (self.selected_action + 1) % n

        # Confirm → trigger action
        if inp.confirm and self.game is not None:
            label, action = ACTIONS[self.selected_action]
            if action == "talk":
                from scz.dialog.characters import commander_halia
                from scz.dialog.scene import DialogScene
                self.game.set_scene(
                    DialogScene(
                        character=commander_halia(self.game),
                        parent_factory=lambda: StationScene(),
                    )
                )
            elif action == "trade":
                from scz.station.trade import TradeScene
                self.game.set_scene(TradeScene())
            elif action == "upgrade":
                from scz.station.customization import ShipCustomizationScene
                self.game.set_scene(ShipCustomizationScene())
            elif action == "undock":
                # Tutorial Beat 6 — sentry drone hails the player on the
                # FIRST undock after they install the Scanner Mk III.
                # Triggers iff scanner_mk3_installed AND not yet fought.
                if (
                    self.game.flags.get("scanner_mk3_installed")
                    and not self.game.flags.get("fought_sentry_drone")
                ):
                    from scz.dialog.characters import sentry_drone_47t
                    from scz.dialog.scene import DialogScene
                    self.game.set_scene(DialogScene(character=sentry_drone_47t()))
                    return
                # Normal undock — drops the player into the Mh-Lai system
                # view. From there the player flies past the outer orbit
                # to enter hyperspace.
                from scz.content.home_system import home_star
                from scz.system.scene import SystemScene
                self.game.set_scene(SystemScene(home_star()))

    def render(self, screen: pygame.Surface) -> None:
        screen.fill((6, 8, 20))

        # Starfield backdrop
        if StationScene._starfield is not None:
            for sx, sy, b in StationScene._starfield:
                pygame.draw.circle(screen, (b, b, min(255, b + 30)), (sx, sy), 1)

        # Mh-Lai planet — large terrestrial blue-green orb, lower-right
        sw, sh = screen.get_size()
        planet_x = sw - 300
        planet_y = sh - 220
        planet_r = 280
        # Atmosphere halo
        for r in range(planet_r + 30, planet_r, -3):
            alpha = (r - planet_r) / 30
            color = (
                int(40 + (1 - alpha) * 30),
                int(80 + (1 - alpha) * 80),
                int(120 + (1 - alpha) * 80),
            )
            pygame.draw.circle(screen, color, (planet_x, planet_y), r)
        # Body
        pygame.draw.circle(screen, (45, 110, 90), (planet_x, planet_y), planet_r)
        # Continent suggestion (a few off-center brown patches)
        for offset, size in (((-80, -30), 60), ((40, 70), 90), ((110, -100), 40)):
            ox, oy = offset
            pygame.draw.circle(
                screen, (90, 130, 80), (planet_x + ox, planet_y + oy), size
            )
        # Light/shadow hint — opposite side darker
        shadow_color = (15, 50, 40)
        pygame.draw.circle(screen, shadow_color, (planet_x + 60, planet_y + 40), planet_r - 20)
        pygame.draw.circle(screen, (45, 110, 90), (planet_x - 30, planet_y - 30), planet_r - 50)

        # Station silhouette — a rotating disc in the foreground (left side)
        station_x = 1000
        station_y = sh // 2 - 40
        # Slow rotation
        rot = self.time_in_scene * 0.08
        # Outer ring
        pygame.draw.circle(screen, (60, 70, 100), (station_x, station_y), 90, 3)
        pygame.draw.circle(screen, (90, 110, 150), (station_x, station_y), 60, 2)
        # Spokes
        for i in range(6):
            a = rot + i * math.pi / 3
            x1 = station_x + math.cos(a) * 60
            y1 = station_y + math.sin(a) * 60
            x2 = station_x + math.cos(a) * 90
            y2 = station_y + math.sin(a) * 90
            pygame.draw.line(screen, (140, 160, 200), (x1, y1), (x2, y2), 2)
        # Central hub
        pygame.draw.circle(screen, (200, 220, 240), (station_x, station_y), 18)
        pygame.draw.circle(screen, (100, 140, 200), (station_x, station_y), 18, 2)
        # Beacon — pulsing light
        pulse = (math.sin(self.time_in_scene * 3) + 1) / 2
        beacon = (
            int(120 + pulse * 100),
            int(180 + pulse * 60),
            int(220 + pulse * 30),
        )
        pygame.draw.circle(screen, beacon, (station_x, station_y), 6)

        # Title block (top-left)
        title = self.fonts["title"].render("MH-LAI STATION", True, (240, 230, 200))
        screen.blit(title, (60, 60))
        subtitle = self.fonts["subtitle"].render(
            "The Hearth · Furling Home System",
            True,
            (180, 180, 210),
        )
        screen.blit(subtitle, (60, 130))
        small = self.fonts["small"].render(
            "Docked.   Furling Scout (default loadout).   Steward on duty.",
            True,
            (130, 150, 180),
        )
        screen.blit(small, (60, 170))

        # Menu panel (left side, vertical list)
        menu_x = 100
        menu_y = 260
        panel_w = 720
        panel_h = len(ACTIONS) * 70 + 60

        # Panel background
        panel_rect = pygame.Rect(menu_x - 20, menu_y - 30, panel_w, panel_h)
        panel_bg = pygame.Surface((panel_w, panel_h), pygame.SRCALPHA)
        panel_bg.fill((10, 14, 30, 200))
        screen.blit(panel_bg, panel_rect.topleft)
        pygame.draw.rect(screen, (60, 80, 120), panel_rect, 1)

        # Menu header
        header = self.fonts["subtitle"].render(
            "STATION ACTIONS", True, (180, 200, 230)
        )
        screen.blit(header, (menu_x, menu_y))

        # Menu items
        for idx, (label, _) in enumerate(ACTIONS):
            is_selected = idx == self.selected_action
            y = menu_y + 50 + idx * 70
            if is_selected:
                # Highlight bar
                hilite = pygame.Rect(menu_x - 10, y - 8, panel_w - 20, 60)
                pygame.draw.rect(screen, (40, 60, 100), hilite)
                pygame.draw.rect(screen, (180, 200, 240), hilite, 1)
                marker = "►"
                color = (255, 240, 200)
            else:
                marker = " "
                color = (180, 190, 210)
            line = self.fonts["menu"].render(
                f"  {marker}   {label}", True, color
            )
            screen.blit(line, (menu_x, y))

        # Footer / controls hint
        hint = self.fonts["small"].render(
            "Up/Down (D-pad, arrows, L-stick)   ·   A / Space confirm   ·   B / Esc quit",
            True,
            (130, 150, 180),
        )
        hw, _ = hint.get_size()
        screen.blit(hint, ((sw - hw) // 2, sh - 40))
