"""PlanetSurfaceScene — top-down lander view of a planet's surface.

Entered from SystemScene by pressing CONFIRM near a planet. Lander deploys,
player controls a small surface vehicle, gathers resource deposits by contact.
Press CANCEL to return the lander to orbit (back to SystemScene at the same
planet's position).

Per Furling tech canon (furling-tech-mechanics.md): landers are remote-piloted
drones, replicated by the ship's fabricator on demand. Loss is annoying but
not gating — no permanent failure.

Phase 2 MVP scope:
- Top-down view of a rectangular surface (palette-tinted by planet type)
- Lander as a small distinct vehicle
- Resource deposits scattered procedurally (see deposits.py)
- Movement, contact-collection, cargo tracking
- No hazards yet (earthquakes/lava/lightning/hostile-life come later)
- Cargo capacity is generous; no forced returns
"""

from __future__ import annotations

import math
from typing import TYPE_CHECKING

import pygame

from scz.engine.scene import Scene
from scz.planet.deposits import (
    Deposit,
    RESOURCE_VISUAL,
    generate_deposits,
)
from scz.system.planet import PLANET_VISUAL

if TYPE_CHECKING:
    from scz.system.scene import SystemScene


# Lander movement speed in surface-local units per second.
# Surface coords are 0..1; this is "screen-fractions per second."
LANDER_SPEED = 0.20

# Lander cargo capacity (MVP: generous)
LANDER_CARGO_MAX = 200

# Tractor beam radius (surface-local units). The lander doesn't have to
# *touch* a deposit — anything inside this radius is pulled in. Future
# lander upgrades grow this radius. Per Aaron's design: life and minerals
# are both tractored, never shot. No "kill the creature for bio-data"
# mechanic exists in this game.
TRACTOR_BEAM_RADIUS = 0.030

# Per-planet-type surface palette: (background, terrain_overlay)
# Background is the "sky" color; terrain is the surface tint.
SURFACE_PALETTES: dict[str, tuple[tuple[int, int, int], tuple[int, int, int]]] = {
    "TERRESTRIAL": ((90, 140, 180), (120, 150, 110)),   # blue sky, green-ish ground
    "OCEAN":       ((60, 100, 160), (70, 110, 170)),    # mostly water
    "ROCKY":       ((40, 30, 30), (110, 90, 70)),       # dark sky, rocky brown
    "DESERT":      ((140, 110, 70), (200, 170, 100)),   # tan sky, lighter ground
    "ICE":         ((180, 200, 220), (220, 230, 240)),  # cold-light, pale ice
    "PRIMORDIAL":  ((100, 30, 30), (200, 80, 50)),      # red-hot sky, lava ground
    "VOLCANIC":    ((50, 20, 20), (140, 50, 30)),       # dark red, ground glows
    # GAS_GIANT handled separately — lander cannot land
}


class PlanetSurfaceScene(Scene):
    """Top-down lander view of a planet's surface."""

    def __init__(
        self,
        planet,            # planet dict OR Planet dataclass with .name, .type, .index
        star: dict,        # parent star dict
        parent_scene_cls=None,  # the scene class to return to (SystemScene)
        ship_cargo: dict | None = None,  # cumulative cargo across visits (TBD persistence)
    ) -> None:
        super().__init__()
        # Accept either a Planet dataclass or a dict
        if hasattr(planet, "name"):
            self.planet_name: str = planet.name
            self.planet_type: str = planet.type
            self.planet_index: int = planet.index
            self.planet_color: tuple[int, int, int] = planet.color
        else:
            self.planet_name = planet["name"]
            self.planet_type = planet["type"]
            self.planet_index = planet.get("index", 0)
            self.planet_color = planet.get("color", (180, 180, 180))

        self.star = star
        self.parent_scene_cls = parent_scene_cls

        # Lander position in surface-local coords (0..1)
        self.lander_x: float = 0.5
        self.lander_y: float = 0.95   # spawn at the top (entry from orbit)
        self.lander_heading: float = math.pi  # facing down/inward
        self.lander_returning: bool = False    # set True briefly on exit

        # Cumulative cargo (per resource type)
        self.cargo: dict[str, int] = ship_cargo if ship_cargo is not None else {
            "COMMON": 0, "USEFUL": 0, "BIO": 0, "ENERGY": 0,
        }
        self.cargo_total: int = sum(self.cargo.values())

        # Procedurally place deposits (deterministic per planet)
        self.deposits: list[Deposit] = generate_deposits(
            (star["x"], star["y"], self.planet_index),
            self.planet_type,
        )

        # Track collection events for the HUD (recent pickups)
        self.recent_pickup: tuple[str, int] | None = None  # (type, value)
        self.recent_pickup_age: float = 0.0

        # Set in on_enter
        self.surface_rect: pygame.Rect | None = None
        self.font: pygame.font.Font | None = None
        self.title_font: pygame.font.Font | None = None

    # ------------------------------------------------------------------
    # Scene API
    # ------------------------------------------------------------------

    def on_enter(self) -> None:
        assert self.game is not None
        w, h = self.game.screen.get_size()
        # Reserve a HUD on the left, surface fills the rest with margin
        HUD_W = 360
        margin = 40
        sw = w - HUD_W - 2 * margin
        sh = h - 2 * margin
        # Make it square if possible (keep top-down feel)
        side = min(sw, sh)
        sx = HUD_W + margin + (sw - side) // 2
        sy = margin + (sh - side) // 2
        self.surface_rect = pygame.Rect(sx, sy, side, side)
        self.font = pygame.font.SysFont("consolas", 18)
        self.title_font = pygame.font.SysFont("consolas", 26, bold=True)

    def update(self, dt: float, inp) -> None:  # type: ignore[no-untyped-def]
        # Movement
        mx, my = inp.move_x, inp.move_y
        if mx != 0.0 or my != 0.0:
            mag = math.hypot(mx, my)
            if mag > 1.0:
                mx /= mag
                my /= mag
            self.lander_heading = math.atan2(mx, -my)
        speed = LANDER_SPEED * dt
        self.lander_x += mx * speed
        self.lander_y += my * speed
        # Clamp to surface bounds
        self.lander_x = max(0.0, min(1.0, self.lander_x))
        self.lander_y = max(0.0, min(1.0, self.lander_y))

        # Tractor-beam pull: anything inside TRACTOR_BEAM_RADIUS is collected
        # (no shooting, no killing — life and minerals are both pulled).
        for d in self.deposits:
            if d.collected:
                continue
            dx = d.x - self.lander_x
            dy = d.y - self.lander_y
            if math.hypot(dx, dy) <= TRACTOR_BEAM_RADIUS:
                d.collected = True
                self.cargo[d.type] = self.cargo.get(d.type, 0) + d.value
                self.cargo_total += d.value
                self.recent_pickup = (d.type, d.value)
                self.recent_pickup_age = 0.0

        if self.recent_pickup is not None:
            self.recent_pickup_age += dt
            if self.recent_pickup_age > 2.5:
                self.recent_pickup = None

        # Exit to system scene on CANCEL
        if inp.cancel and self.game is not None and self.parent_scene_cls is not None:
            # Build a system scene at the same star
            sys_scene = self.parent_scene_cls(self.star)
            self.game.set_scene(sys_scene)

    def render(self, screen: pygame.Surface) -> None:
        screen.fill((6, 6, 18))

        # Surface area
        assert self.surface_rect is not None
        palette = SURFACE_PALETTES.get(
            self.planet_type, ((50, 50, 60), (110, 100, 100))
        )
        bg, terrain = palette
        pygame.draw.rect(screen, bg, self.surface_rect)
        # Inner ground rect (slightly inset to suggest horizon)
        inset = 10
        ground_rect = self.surface_rect.inflate(-inset * 2, -inset * 2)
        pygame.draw.rect(screen, terrain, ground_rect)
        # Border
        pygame.draw.rect(screen, (40, 40, 70), self.surface_rect, 2)

        # Persistent LIFT OFF prompt in top-right of the surface area
        # (very visible — players miss the bottom-left controls hint)
        if self.font is not None:
            liftoff_font = pygame.font.SysFont("consolas", 22, bold=True)
            liftoff_text = "[ LIFT OFF: Esc / B ]"
            text_surf = liftoff_font.render(liftoff_text, True, (255, 230, 140))
            tw, th = text_surf.get_size()
            tx = self.surface_rect.right - tw - 16
            ty = self.surface_rect.top + 16
            # Background box for legibility against any terrain palette
            pad = 8
            box = pygame.Rect(tx - pad, ty - pad, tw + pad * 2, th + pad * 2)
            pygame.draw.rect(screen, (20, 20, 40, 200), box)
            pygame.draw.rect(screen, (180, 160, 100), box, 1)
            screen.blit(text_surf, (tx, ty))

        # Deposits
        for d in self.deposits:
            if d.collected:
                continue
            vis = RESOURCE_VISUAL[d.type]
            sx = ground_rect.x + d.x * ground_rect.width
            sy = ground_rect.y + d.y * ground_rect.height
            pygame.draw.circle(screen, vis["color"], (int(sx), int(sy)), vis["size"])
            # Subtle glow
            glow = (vis["color"][0] // 3, vis["color"][1] // 3, vis["color"][2] // 3)
            pygame.draw.circle(
                screen, glow, (int(sx), int(sy)), vis["size"] + 4, 1
            )

        # Lander
        self._draw_lander(screen, ground_rect)

        # Recent pickup floater
        if self.recent_pickup is not None and self.font is not None:
            rtype, rvalue = self.recent_pickup
            color = RESOURCE_VISUAL[rtype]["color"]
            alpha = max(0, 255 - int(self.recent_pickup_age / 2.5 * 255))
            text = self.font.render(f"tractored  +{rvalue} {rtype.lower()}", True, color)
            text.set_alpha(alpha)
            tw, _ = text.get_size()
            # Float above the lander
            lx = ground_rect.x + self.lander_x * ground_rect.width
            ly = ground_rect.y + self.lander_y * ground_rect.height
            screen.blit(text, (lx - tw / 2, ly - 30 - self.recent_pickup_age * 12))

        # HUD
        self._draw_hud(screen)

    # ------------------------------------------------------------------
    # Time Drive
    # ------------------------------------------------------------------

    def snapshot(self) -> dict | None:
        """Surface visits ARE rewindable — restore position + collected state."""
        return {
            "scene": "PlanetSurfaceScene",
            "planet_name": self.planet_name,
            "lander_x": self.lander_x,
            "lander_y": self.lander_y,
            "lander_heading": self.lander_heading,
            "cargo": dict(self.cargo),
            "collected_indices": [i for i, d in enumerate(self.deposits) if d.collected],
        }

    def restore(self, state: dict) -> None:
        # Only restore if it's the same planet
        if state.get("planet_name") != self.planet_name:
            return
        self.lander_x = float(state["lander_x"])
        self.lander_y = float(state["lander_y"])
        self.lander_heading = float(state["lander_heading"])
        self.cargo = dict(state["cargo"])
        self.cargo_total = sum(self.cargo.values())
        collected = set(state.get("collected_indices", []))
        for i, d in enumerate(self.deposits):
            d.collected = i in collected

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _draw_lander(self, screen: pygame.Surface, ground_rect: pygame.Rect) -> None:
        x = ground_rect.x + self.lander_x * ground_rect.width
        y = ground_rect.y + self.lander_y * ground_rect.height
        # Tractor-beam radius — faint pulsing circle that visualizes the
        # collection range. Anything inside this ring gets tractored in.
        tractor_pixel_radius = TRACTOR_BEAM_RADIUS * ground_rect.width
        pulse = (math.sin(pygame.time.get_ticks() / 280) + 1) / 2
        beam_color = (
            int(180 + pulse * 60),
            int(200 + pulse * 40),
            int(140 + pulse * 30),
        )
        pygame.draw.circle(
            screen, beam_color, (int(x), int(y)), int(tractor_pixel_radius), 1
        )
        # Distinct lander shape — diamond outline, yellow-white (distinct from ship's triangle/cyan)
        size = 9
        cos_h = math.cos(self.lander_heading)
        sin_h = math.sin(self.lander_heading)
        local = [(0, -size), (size * 0.7, 0), (0, size), (-size * 0.7, 0)]
        pts = []
        for lx, ly in local:
            rx = lx * cos_h - ly * sin_h
            ry = lx * sin_h + ly * cos_h
            pts.append((x + rx, y + ry))
        pygame.draw.polygon(screen, (255, 240, 150), pts)
        pygame.draw.polygon(screen, (200, 160, 60), pts, 1)
        # Small directional dot ahead of the lander
        ahead_x = x + cos_h * (size + 4)
        ahead_y = y + sin_h * (size + 4)
        pygame.draw.circle(screen, (255, 240, 150), (int(ahead_x), int(ahead_y)), 2)

    def _draw_hud(self, screen: pygame.Surface) -> None:
        assert self.font is not None
        assert self.title_font is not None

        HUD_W = 360
        pygame.draw.rect(screen, (10, 10, 26), (0, 0, HUD_W, screen.get_height()))
        pygame.draw.line(screen, (40, 40, 70), (HUD_W, 0), (HUD_W, screen.get_height()), 1)

        x = 22
        y = 24
        screen.blit(self.title_font.render(self.planet_name, True, (210, 220, 240)), (x, y))
        y += 34
        screen.blit(
            self.font.render(
                f"{self.planet_type.lower()}", True, (160, 180, 210)
            ),
            (x, y),
        )
        y += 28

        # Lander status
        screen.blit(self.font.render("LANDER DEPLOYED", True, (200, 200, 220)), (x, y))
        y += 24
        screen.blit(
            self.font.render(f"Cargo: {self.cargo_total} / {LANDER_CARGO_MAX}", True, (160, 180, 200)),
            (x, y),
        )
        y += 32

        # Per-resource breakdown
        screen.blit(self.font.render("HOLD CONTENTS", True, (200, 210, 230)), (x, y))
        y += 24
        for rtype in ("COMMON", "USEFUL", "BIO", "ENERGY"):
            color = RESOURCE_VISUAL[rtype]["color"]
            label = f"  {rtype.lower():8s}  {self.cargo.get(rtype, 0):4d}"
            screen.blit(self.font.render(label, True, color), (x, y))
            y += 22

        # Deposit count remaining
        remaining = sum(1 for d in self.deposits if not d.collected)
        total = len(self.deposits)
        y += 16
        screen.blit(
            self.font.render(
                f"DEPOSITS REMAINING  {remaining} / {total}", True, (200, 200, 220)
            ),
            (x, y),
        )
        y += 24

        # Time Drive
        y += 16
        if self.game is not None:
            td = self.game.time_drive
            if td.is_ready():
                screen.blit(
                    self.font.render("TIME DRIVE  READY", True, (130, 230, 180)),
                    (x, y),
                )
            else:
                remaining_s = td.time_until_ready()
                mm = int(remaining_s) // 60
                ss = int(remaining_s) % 60
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
            "Return:  Backspace / B",
            "Rewind:  R / Back",
            "Quit:    Esc / Start",
        ):
            screen.blit(self.font.render(line, True, (130, 150, 180)), (x, controls_y))
            controls_y += 22
