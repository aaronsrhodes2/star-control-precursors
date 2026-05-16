"""QuasiSpaceScene — navigable shortcut layer with fixed portals."""

from __future__ import annotations

import math
from dataclasses import dataclass

import pygame

from scz.engine.scene import Scene


# Quasi-Space coordinate range — much smaller than hyperspace's 10000.
# The whole map fits on screen at zoom=1, but we still let the player
# fly to feel the navigation.
QS_MAX = 2000.0

# Player speed in Quasi-Space — fast (it's "thinner" per the Sage)
QS_PLAYER_SPEED = 900.0

# Distance at which the player can "use" a portal
PORTAL_USE_RADIUS = 80.0


@dataclass
class QSPortal:
    """One Quasi-Space portal. Position is in QS coords. Exit is in
    hyperspace coords. Label is shown next to the portal in the HUD/map."""

    qs_x: float
    qs_y: float
    exit_x: float       # hyperspace coords
    exit_y: float
    label: str          # e.g. "near Mh-Lai", "near Arilou Outpost"
    color: tuple[int, int, int]


def build_portal_map() -> list[QSPortal]:
    """The 12-portal canonical map, slice-trimmed to a few key destinations.

    Per Sage Lwen-Olou: "Twelve in all. One quite near your Hearth." We
    expose the three slice-relevant portals; the rest can be added as
    content lands.
    """
    return [
        # The one near the Hearth — exits just outside Mh-Lai system.
        QSPortal(
            qs_x=400.0,
            qs_y=1000.0,
            exit_x=1900.0 + 800.0,   # offset so we don't re-enter Mh-Lai instantly
            exit_y=1600.0,
            label="near the Hearth",
            color=(255, 220, 140),
        ),
        # The Arilou Outpost portal — exits at the Outpost coords.
        QSPortal(
            qs_x=1600.0,
            qs_y=1000.0,
            exit_x=3500.0,
            exit_y=2400.0,
            label="Arilou Outpost",
            color=(140, 240, 210),
        ),
        # A distant fold — exits far across the cluster.
        QSPortal(
            qs_x=1000.0,
            qs_y=300.0,
            exit_x=6000.0,
            exit_y=5500.0,
            label="distant fold",
            color=(200, 160, 240),
        ),
    ]


class QuasiSpaceScene(Scene):
    """The Quasi-Space navigation scene."""

    def __init__(
        self,
        entry_portal_index: int | None = None,
    ) -> None:
        super().__init__()
        self.portals = build_portal_map()
        # Spawn the player at the chosen entry portal, or at the map center
        # for the debug/switcher entry.
        if entry_portal_index is not None and 0 <= entry_portal_index < len(self.portals):
            ep = self.portals[entry_portal_index]
            self.player_x: float = ep.qs_x
            self.player_y: float = ep.qs_y
        else:
            self.player_x = QS_MAX / 2
            self.player_y = QS_MAX / 2
        self.player_heading: float = math.pi
        self.time_in_scene: float = 0.0

        # The entry portal is "muted" for auto-capture until the player
        # leaves its radius — otherwise spawning on a portal would
        # immediately re-eject through it. Set to None for the debug/
        # switcher entry (no spawn portal, no mute).
        self.entry_portal_index: int | None = entry_portal_index
        self.entry_portal_muted: bool = entry_portal_index is not None

        # Set in on_enter
        self.screen_w: int = 0
        self.screen_h: int = 0
        self.scale: float = 1.0
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
        self.scale = (min(w, h) - 120) / QS_MAX
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
        speed = QS_PLAYER_SPEED * dt
        self.player_x += mx * speed
        self.player_y += my * speed
        self.player_x = max(0.0, min(QS_MAX, self.player_x))
        self.player_y = max(0.0, min(QS_MAX, self.player_y))

        # Auto-suck — when the ship enters a portal's radius, it's pulled
        # through automatically (gravitational capture, no button press).
        # The entry portal is muted until the player leaves its radius
        # (so spawning on it doesn't immediately re-eject).
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
                from scz.hyperspace.scene import HyperspaceScene
                hyper = HyperspaceScene()
                hyper.player_x = float(portal.exit_x)
                hyper.player_y = float(portal.exit_y)
                self.game.set_scene(hyper)
                return

        # B → bail out of Quasi-Space without a portal transition. We snap
        # back to hyperspace at "wherever we came in" — for the slice this
        # is the entry portal's exit_x/y.
        if inp.cancel and self.game is not None:
            from scz.hyperspace.scene import HyperspaceScene
            hyper = HyperspaceScene()
            ep = self.portals[0]
            hyper.player_x = float(ep.exit_x)
            hyper.player_y = float(ep.exit_y)
            self.game.set_scene(hyper)

    def render(self, screen: pygame.Surface) -> None:
        # Quasi-Space ambient — deep teal/violet
        screen.fill((12, 8, 26))

        # Soft parallax — drift dots forming a fold-pattern texture
        rng_seed = 4242
        for i in range(120):
            seed = rng_seed + i * 9377
            qx = (seed % 10007) / 10007.0 * QS_MAX
            qy = ((seed // 10007) % 10007) / 10007.0 * QS_MAX
            # Slow drift offset
            qx = (qx + self.time_in_scene * 8) % QS_MAX
            sx, sy = self._qs_to_screen(qx, qy)
            shade = 30 + (i * 7) % 40
            pygame.draw.circle(
                screen, (shade, shade // 2, shade + 20), (int(sx), int(sy)), 1
            )

        # Map border — faint ring marking the QS bounds
        cx, cy = self._qs_to_screen(QS_MAX / 2, QS_MAX / 2)
        r = (QS_MAX / 2) * self.scale
        pygame.draw.circle(
            screen, (60, 50, 90), (int(cx), int(cy)), int(r), 1
        )

        # Portals
        in_range = self._portal_in_range()
        for p in self.portals:
            self._draw_portal(screen, p, highlighted=(p is in_range))

        # Player ship
        self._draw_player(screen)

        # HUD
        self._draw_hud(screen, in_range)

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _qs_to_screen(self, qx: float, qy: float) -> tuple[float, float]:
        return (
            self.screen_w / 2 + (qx - QS_MAX / 2) * self.scale,
            self.screen_h / 2 + (qy - QS_MAX / 2) * self.scale,
        )

    def _portal_in_range(self) -> QSPortal | None:
        for p in self.portals:
            d = math.hypot(self.player_x - p.qs_x, self.player_y - p.qs_y)
            if d <= PORTAL_USE_RADIUS:
                return p
        return None

    def _draw_portal(
        self, screen: pygame.Surface, portal: QSPortal, highlighted: bool
    ) -> None:
        x, y = self._qs_to_screen(portal.qs_x, portal.qs_y)
        # Pulsing ring (highlighted is brighter)
        base_r = 22
        pulse = (math.sin(self.time_in_scene * 2.0) + 1) / 2
        if highlighted:
            outer_r = base_r + 14 + int(pulse * 4)
            ring_color = (
                min(255, portal.color[0] + 30),
                min(255, portal.color[1] + 30),
                min(255, portal.color[2] + 30),
            )
        else:
            outer_r = base_r + 8
            ring_color = portal.color
        pygame.draw.circle(screen, ring_color, (int(x), int(y)), outer_r, 2)
        pygame.draw.circle(screen, ring_color, (int(x), int(y)), base_r, 1)
        # Inner glow
        glow = (portal.color[0] // 3, portal.color[1] // 3, portal.color[2] // 3)
        pygame.draw.circle(screen, glow, (int(x), int(y)), base_r - 6)
        # Label
        if self.font is not None:
            label = self.font.render(portal.label, True, ring_color)
            screen.blit(label, (x - label.get_width() / 2, y + outer_r + 6))

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

    def _draw_hud(
        self, screen: pygame.Surface, in_range: QSPortal | None
    ) -> None:
        assert self.font is not None and self.title_font is not None
        HUD_W = 360
        pygame.draw.rect(screen, (10, 6, 22), (0, 0, HUD_W, screen.get_height()))
        pygame.draw.line(
            screen, (40, 28, 70), (HUD_W, 0), (HUD_W, screen.get_height()), 1
        )
        x = 22
        y = 24
        screen.blit(
            self.title_font.render("QUASI-SPACE", True, (210, 220, 250)),
            (x, y),
        )
        y += 34
        screen.blit(
            self.font.render(
                "the Arilou fold-layer · 12 portals known",
                True,
                (160, 180, 220),
            ),
            (x, y),
        )
        y += 36
        screen.blit(
            self.font.render("PORTALS", True, (200, 200, 220)), (x, y)
        )
        y += 26
        for p in self.portals:
            d = math.hypot(self.player_x - p.qs_x, self.player_y - p.qs_y)
            color = p.color if p is in_range else (150, 160, 180)
            screen.blit(
                self.font.render(
                    f"  {p.label:18s}  d={int(d):4d}", True, color
                ),
                (x, y),
            )
            y += 22

        # Capture prompt
        if in_range is not None:
            y += 8
            pulse = (math.sin(pygame.time.get_ticks() / 200) + 1) / 2
            c = (
                int(180 + pulse * 75),
                int(220 + pulse * 35),
                int(150 + pulse * 50),
            )
            screen.blit(
                self.font.render(
                    f"CAPTURING  ·  exit at {in_range.label}", True, c
                ),
                (x, y),
            )
            y += 22
        else:
            y += 8
            screen.blit(
                self.font.render(
                    "Fly into a portal — capture is automatic",
                    True,
                    (150, 160, 180),
                ),
                (x, y),
            )
            y += 22

        # Controls hint pinned to bottom
        controls_y = screen.get_height() - 180
        screen.blit(self.font.render("CONTROLS", True, (200, 210, 230)), (x, controls_y))
        controls_y += 28
        for line in (
            "Move:    WASD / L-stick",
            "Portal:  fly into it (automatic capture)",
            "Bail:    Backspace / B",
            "Quit:    Esc / Start",
        ):
            screen.blit(self.font.render(line, True, (130, 150, 180)), (x, controls_y))
            controls_y += 22
