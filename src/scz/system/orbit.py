"""PlanetOrbitScene — cloaked orbit + scan view for a single planet.

Slots between SystemScene and PlanetSurfaceScene. When the player gets
close enough to a planet in the system view and presses CONFIRM, they
enter ORBIT instead of dropping straight to the surface.

Per Furling tech canon (furling-tech-mechanics.md + orbital-and-pursuit
notes): in orbit, the Furling ship engages its cloak field. The orbit
is the safe zone — Time Drive snapshots here, you can scan, you can
decide whether to deploy the lander or move on. Leaving orbit drops the
cloak; deploying the lander launches a remote-piloted drone.

UI:
  - Right: large rotating planet, cloak shimmer indicating safe-zone
  - Left: HUD with planet stats, scan results (deposit summary), Time Drive
  - Bottom: action prompts (A deploy / B leave)
"""

from __future__ import annotations

import math
from typing import TYPE_CHECKING

import pygame

from scz.engine.scene import Scene
from scz.planet.deposits import RESOURCE_VISUAL, generate_deposits
from scz.system.planet import PLANET_VISUAL, Planet

if TYPE_CHECKING:
    pass


# How fast the planet appears to rotate in this view (visual only)
PLANET_ROT_SPEED = 0.18  # radians/sec


# Per-planet-type backdrop tone: deep space tinted by the planet's character
ORBIT_BACKDROP: dict[str, tuple[int, int, int]] = {
    "TERRESTRIAL": (6, 12, 22),
    "OCEAN":       (6, 14, 26),
    "ROCKY":       (12, 8, 6),
    "DESERT":      (18, 14, 8),
    "ICE":         (10, 14, 20),
    "PRIMORDIAL":  (22, 8, 6),
    "VOLCANIC":    (18, 6, 6),
    "GAS_GIANT":   (16, 12, 8),
}


class PlanetOrbitScene(Scene):
    """Cloaked orbital view of a single planet."""

    def __init__(
        self,
        planet: Planet,
        star: dict,
        parent_scene_cls=None,
    ) -> None:
        super().__init__()
        self.planet = planet
        self.star = star
        self.parent_scene_cls = parent_scene_cls
        self.time_in_scene: float = 0.0

        # Pre-generate the deposit list so we can report scan totals.
        # Same seed used by PlanetSurfaceScene, so what you see in orbit
        # matches what you'll find on the surface.
        self.deposits = generate_deposits(
            (star["x"], star["y"], planet.index),
            planet.type,
        )
        self.deposit_count_by_type: dict[str, int] = {}
        for d in self.deposits:
            self.deposit_count_by_type[d.type] = (
                self.deposit_count_by_type.get(d.type, 0) + 1
            )

        # Set in on_enter
        self.font: pygame.font.Font | None = None
        self.title_font: pygame.font.Font | None = None
        self.small_font: pygame.font.Font | None = None

    # ------------------------------------------------------------------
    # Scene API
    # ------------------------------------------------------------------

    def on_enter(self) -> None:
        self.font = pygame.font.SysFont("consolas", 18)
        self.title_font = pygame.font.SysFont("consolas", 32, bold=True)
        self.small_font = pygame.font.SysFont("consolas", 14)

    def update(self, dt: float, inp) -> None:  # type: ignore[no-untyped-def]
        self.time_in_scene += dt

        # B → leave orbit, back to system view
        if inp.cancel and self.game is not None and self.parent_scene_cls is not None:
            sys_scene = self.parent_scene_cls(self.star)
            self.game.set_scene(sys_scene)
            return

        # A → deploy lander, drop to surface
        if inp.confirm and self.game is not None:
            from scz.planet.scene import PlanetSurfaceScene
            from scz.system.scene import SystemScene
            self.game.set_scene(
                PlanetSurfaceScene(
                    planet=self.planet,
                    star=self.star,
                    parent_scene_cls=SystemScene,
                )
            )
            return

    def render(self, screen: pygame.Surface) -> None:
        backdrop = ORBIT_BACKDROP.get(self.planet.type, (6, 6, 18))
        screen.fill(backdrop)

        w, h = screen.get_size()

        # --- Planet (right half) ---
        # Big rotating sphere with a couple of light/shadow passes to suggest
        # 3D. The "rotation" is faked with a slowly drifting highlight.
        p_center_x = w - w // 4
        p_center_y = h // 2
        p_radius = min(h, w // 2) // 3
        base_color = self.planet.color

        # Atmosphere / cloak halo — Furling cloak field shimmer
        cloak_pulse = (math.sin(self.time_in_scene * 1.3) + 1) / 2
        for i in range(8, 0, -1):
            halo_r = p_radius + i * 6
            tint = (
                int(base_color[0] * 0.2 + 30 * cloak_pulse),
                int(base_color[1] * 0.2 + 60 * cloak_pulse),
                int(base_color[2] * 0.2 + 90 * cloak_pulse),
            )
            pygame.draw.circle(screen, tint, (p_center_x, p_center_y), halo_r, 1)

        # Body
        pygame.draw.circle(screen, base_color, (p_center_x, p_center_y), p_radius)

        # Day/night terminator — moving with rotation
        sweep = self.time_in_scene * PLANET_ROT_SPEED
        shadow_dx = math.cos(sweep) * p_radius * 0.55
        shadow_dy = math.sin(sweep * 0.3) * p_radius * 0.15
        shadow = (
            base_color[0] // 4,
            base_color[1] // 4,
            base_color[2] // 4,
        )
        pygame.draw.circle(
            screen, shadow,
            (int(p_center_x + shadow_dx), int(p_center_y + shadow_dy)),
            int(p_radius * 0.92),
        )
        # Lit side — repaint a bit smaller offset opposite
        pygame.draw.circle(
            screen, base_color,
            (int(p_center_x - shadow_dx * 0.4), int(p_center_y - shadow_dy * 0.4)),
            int(p_radius * 0.78),
        )

        # Surface flecks — fake continents/clouds based on a stable hash of
        # planet index + star coords; rotate with sweep so it looks alive
        rng_seed = self.star["x"] * 10001 + self.star["y"] * 17 + self.planet.index
        for i in range(7):
            theta = ((rng_seed >> (i * 3)) & 0xFF) / 255.0 * math.tau + sweep
            r_frac = 0.3 + ((rng_seed >> (i * 4 + 4)) & 0x7F) / 127.0 * 0.55
            patch_r = p_radius * 0.18 - i * 2
            ox = math.cos(theta) * p_radius * r_frac
            oy = math.sin(theta) * p_radius * r_frac * 0.6
            if patch_r > 2:
                fleck_color = (
                    max(0, base_color[0] - 30),
                    max(0, base_color[1] - 15),
                    max(0, base_color[2] - 40),
                )
                pygame.draw.circle(
                    screen, fleck_color,
                    (int(p_center_x + ox), int(p_center_y + oy)),
                    int(patch_r),
                )

        # Cloak shimmer overlay — concentric thin rings, pulsing
        for i in range(3):
            r = p_radius + 14 + i * 9
            alpha = int(60 * (1 - i / 3) * (0.5 + 0.5 * cloak_pulse))
            ring = pygame.Surface((r * 2 + 4, r * 2 + 4), pygame.SRCALPHA)
            pygame.draw.circle(ring, (140, 200, 255, alpha), (r + 2, r + 2), r, 1)
            screen.blit(ring, (p_center_x - r - 2, p_center_y - r - 2))

        # --- HUD (left) ---
        self._draw_hud(screen)

    # ------------------------------------------------------------------
    # Time Drive
    # ------------------------------------------------------------------

    def snapshot(self) -> dict | None:
        """Orbit IS a safe-zone — return rewindable state."""
        return {
            "scene": "PlanetOrbitScene",
            "planet_name": self.planet.name,
            "planet_index": self.planet.index,
            "star_x": self.star["x"],
            "star_y": self.star["y"],
        }

    def restore(self, state: dict) -> None:
        # Same-planet rewinds are no-ops (we're already here); cross-planet
        # rewinds aren't supported by this simple version.
        pass

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _draw_hud(self, screen: pygame.Surface) -> None:
        assert self.font is not None and self.title_font is not None
        HUD_W = 420
        pygame.draw.rect(screen, (10, 10, 26), (0, 0, HUD_W, screen.get_height()))
        pygame.draw.line(
            screen, (40, 40, 70), (HUD_W, 0), (HUD_W, screen.get_height()), 1
        )

        x = 22
        y = 24
        # Title — planet name
        screen.blit(
            self.title_font.render(self.planet.name, True, (220, 230, 250)),
            (x, y),
        )
        y += 42
        # Subtitle — planet type, star name
        sub = f"{self.planet.type.lower()}  ·  {self.star.get('cluster_name', '')}"
        screen.blit(self.font.render(sub, True, (160, 180, 210)), (x, y))
        y += 28

        # Cloak status — Furling field engaged
        cloak_pulse = (math.sin(self.time_in_scene * 1.3) + 1) / 2
        cloak_color = (
            int(80 + 100 * cloak_pulse),
            int(180 + 60 * cloak_pulse),
            int(220 + 30 * cloak_pulse),
        )
        screen.blit(
            self.font.render(
                "FURLING CLOAK  engaged in orbit",
                True,
                cloak_color,
            ),
            (x, y),
        )
        y += 24
        screen.blit(
            self.font.render(
                "  surface drone is sensor-quiet",
                True,
                (120, 150, 180),
            ),
            (x, y),
        )
        y += 32

        # Scan results — deposits by type
        screen.blit(
            self.font.render("SCAN RESULTS", True, (200, 210, 230)),
            (x, y),
        )
        y += 26
        total = len(self.deposits)
        screen.blit(
            self.font.render(
                f"  {total} deposit{'s' if total != 1 else ''} detected",
                True,
                (180, 200, 220),
            ),
            (x, y),
        )
        y += 26
        for rtype in ("COMMON", "USEFUL", "BIO", "ENERGY"):
            n = self.deposit_count_by_type.get(rtype, 0)
            color = RESOURCE_VISUAL[rtype]["color"]
            label = f"   {rtype.lower():8s}  {n:3d}"
            screen.blit(self.font.render(label, True, color), (x, y))
            y += 22

        # Atmosphere / world summary (just flavor)
        y += 12
        screen.blit(
            self.font.render("WORLD SUMMARY", True, (200, 210, 230)),
            (x, y),
        )
        y += 24
        for line in _summary_lines(self.planet.type):
            screen.blit(
                self.font.render(f"  {line}", True, (150, 170, 190)), (x, y)
            )
            y += 22

        # Time Drive
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
                        f"TIME DRIVE  charging {mm}:{ss:02d}",
                        True,
                        (180, 160, 110),
                    ),
                    (x, y),
                )

        # Action prompts pinned to bottom
        bottom = screen.get_height() - 180
        screen.blit(
            self.font.render("ORBITAL ACTIONS", True, (200, 210, 230)),
            (x, bottom),
        )
        bottom += 30
        pulse = (math.sin(pygame.time.get_ticks() / 280) + 1) / 2
        a_color = (
            int(180 + pulse * 75),
            int(220 + pulse * 35),
            int(150 + pulse * 50),
        )
        prompts = [
            ("[A]  Deploy Lander", a_color),
            ("[B]  Leave Orbit",   (200, 200, 220)),
            ("[R]  Rewind",        (150, 170, 190)),
        ]
        for label, color in prompts:
            screen.blit(self.font.render(label, True, color), (x, bottom))
            bottom += 24


def _summary_lines(planet_type: str) -> list[str]:
    return {
        "TERRESTRIAL": [
            "atmosphere breathable, biosphere active",
            "lander conditions: nominal",
        ],
        "OCEAN": [
            "surface ~95% liquid water",
            "lander floats; collection restricted",
        ],
        "ROCKY": [
            "thin or no atmosphere",
            "lander conditions: dry, dusty",
        ],
        "DESERT": [
            "arid, mostly silicate",
            "lander conditions: hot, abrasive",
        ],
        "ICE": [
            "frozen surface, thin atmosphere",
            "lander conditions: very cold",
        ],
        "PRIMORDIAL": [
            "still forming, hot, hostile",
            "lander conditions: dangerous",
        ],
        "VOLCANIC": [
            "active mantle, lava flows",
            "lander conditions: hazardous",
        ],
        "GAS_GIANT": [
            "no solid surface",
            "lander cannot deploy",
        ],
    }.get(planet_type, [])
