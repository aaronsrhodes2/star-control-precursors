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
import random
from typing import TYPE_CHECKING

import pygame

from scz.engine.scene import Scene
from scz.planet.deposits import (
    Deposit,
    RESOURCE_VISUAL,
    generate_deposits,
)
from scz.planet.hazards import (
    Hazard,
    LANDER_HP_BASE,
    LANDER_REPLACEMENT_COST,
    generate_hazards,
)
from scz.system.planet import PLANET_VISUAL

if TYPE_CHECKING:
    from scz.system.scene import SystemScene


class _ReconstitutedPlanet:
    """Minimal Planet stand-in for handing back to PlanetOrbitScene on lift-off.

    We've forgotten the original orbit geometry by the time we leave the
    surface, but PlanetOrbitScene only needs name/type/index/color. This
    avoids carrying the full Planet dataclass through PlanetSurfaceScene.
    """
    __slots__ = ("index", "name", "type", "color")

    def __init__(self, index: int, name: str, type: str, color):
        self.index = index
        self.name = name
        self.type = type
        self.color = color


# Lander movement speed in surface-local units per second.
# Surface coords are 0..1; this is "screen-fractions per second."
LANDER_SPEED = 0.20

# Lander cargo capacity (BASE; modules add to this via game.effective_stat)
LANDER_CARGO_BASE = 200

# Tractor beam radius (surface-local units). The lander doesn't have to
# *touch* a deposit — anything inside this radius is pulled in. The
# Mycon Bio-Architect module grows it via game.effective_stat
# ("tractor_radius_bonus"). Per Aaron's design: life and minerals are
# both tractored, never shot. No "kill the creature for bio-data"
# mechanic exists in this game.
TRACTOR_BEAM_BASE = 0.030

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

    music_context = "planet_lander"  # assets/music/planet_lander/ (Round-2 queued)

    def __init__(
        self,
        planet,            # planet dict OR Planet dataclass with .name, .type, .index
        star: dict,        # parent star dict
        parent_scene_cls=None,  # the scene class to return to (SystemScene)
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

        # Cargo lives on Game (game.cargo) so it persists across planet
        # visits, dialog scenes, station screens, etc. The reference is
        # resolved in on_enter so we can access self.game.

        # Procedurally place deposits (deterministic per planet)
        self.deposits: list[Deposit] = generate_deposits(
            (star["x"], star["y"], self.planet_index),
            self.planet_type,
        )

        # Track collection events for the HUD (recent pickups)
        self.recent_pickup: tuple[str, int] | None = None  # (type, value)
        self.recent_pickup_age: float = 0.0
        self.recent_pickup_label: str = ""    # custom label (e.g. for the package)

        # Trip haul — staged here per pickup; commits to game.cargo on
        # successful lift-off. If the lander is destroyed, this haul is
        # LOST. The player has to balance "should I keep tractoring, or
        # lift off with what I have?"
        self.trip_haul: dict[str, int] = {
            "COMMON": 0, "USEFUL": 0, "BIO": 0, "ENERGY": 0,
        }

        # Hazards on this planet (deterministic per seed; empty on safe
        # worlds like Furlmart).
        self.hazards: list[Hazard] = generate_hazards(
            (star["x"], star["y"], self.planet_index),
            self.planet_type,
            planet_name=self.planet_name,
        )

        # Lander HP — starts full each surface visit. Future hull
        # modules can grow this via effective_stat("lander_hp_bonus").
        self.lander_hp: float = LANDER_HP_BASE
        self.lander_destroyed: bool = False
        self.destruction_msg: str = ""
        self.destruction_age: float = 0.0

        # Time on the surface; used by periodic hazards
        self.surface_time: float = 0.0

        # Set in on_enter
        self.surface_rect: pygame.Rect | None = None
        self.font: pygame.font.Font | None = None
        self.title_font: pygame.font.Font | None = None

    # ------------------------------------------------------------------
    # Scene API
    # ------------------------------------------------------------------

    def on_enter(self) -> None:
        assert self.game is not None
        # SFX: lander drone deploying from orbit + arrival swoosh.
        # Both play together — deploy is the thruster ignition + flight
        # down (~1.6s), arrive is the hover-into-position over surface.
        # The slight overlap reads as "ship → deploy → arrive at surface".
        if hasattr(self.game, "sfx"):
            self.game.sfx.play("lander/lander_deploy")
            self.game.sfx.play("lander/lander_arrive")
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

        # Quest-item injection — Tutorial Beat 3. On Furlmart, if the
        # Scanner Mk III hasn't been collected yet, place the package
        # at the center of the surface so the player can't miss it.
        if (
            self.planet_name == "Furlmart"
            and not self.game.flags.get("scanner_mk3_collected", False)
        ):
            self.deposits.append(
                Deposit(type="PACKAGE_SCANNER_MK3", x=0.5, y=0.5, value=1)
            )

    def update(self, dt: float, inp) -> None:  # type: ignore[no-untyped-def]
        self.surface_time += dt

        # If the lander already died, hold on the wreck for a moment,
        # then auto-eject to orbit (player can re-deploy from there).
        if self.lander_destroyed:
            self.destruction_age += dt
            if self.destruction_age >= 2.5:
                self._exit_to_orbit(committed=False)
            return

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

        # Hazards — apply damage to the lander when in contact with an
        # active hazard. lander_hp is per-trip; reaches 0 → destroyed.
        for h in self.hazards:
            if not h.is_active(self.surface_time):
                continue
            dx = h.x - self.lander_x
            dy = h.y - self.lander_y
            if math.hypot(dx, dy) <= h.radius:
                self.lander_hp -= h.damage_per_sec * dt
                if self.lander_hp <= 0.0:
                    self.lander_hp = 0.0
                    self._destroy_lander(h.type)
                    return

        # Tractor-beam pull: anything inside the effective radius is
        # collected (no shooting, no killing — life and minerals both
        # pulled). Bio-Architect module grows the radius.
        assert self.game is not None
        tractor_radius = self.game.effective_stat(
            "tractor_radius_bonus", TRACTOR_BEAM_BASE
        )
        for d in self.deposits:
            if d.collected:
                continue
            dx = d.x - self.lander_x
            dy = d.y - self.lander_y
            if math.hypot(dx, dy) <= tractor_radius:
                d.collected = True
                self._on_pickup(d)

        if self.recent_pickup is not None:
            self.recent_pickup_age += dt
            if self.recent_pickup_age > 2.5:
                self.recent_pickup = None

        # Exit on CANCEL — lift off back to orbit. Trip haul commits
        # to game.cargo on successful lift-off.
        if inp.cancel and self.game is not None:
            self._exit_to_orbit(committed=True)

    def _exit_to_orbit(self, committed: bool) -> None:
        """Leave the surface back to PlanetOrbitScene.

        committed=True (lift-off): commit trip_haul to game.cargo.
        committed=False (destruction): trip_haul is LOST; pay
        replacement cost from game.cargo.
        """
        assert self.game is not None
        # SFX: dedicated lift_off — Furling warm-tech engine surge
        # (departure thrust, ~2.5s). Aaron 2026-05-19 wire-everything
        # pass: this replaces the old "reuse lander_arrive in reverse"
        # placeholder; lift_off.wav now exists and sounds right.
        if hasattr(self.game, "sfx"):
            self.game.sfx.play("lander/lift_off")
        if committed:
            for t, v in self.trip_haul.items():
                if v > 0:
                    self.game.cargo[t] = self.game.cargo.get(t, 0) + v
        else:
            # Lander destruction — pay replacement cost out of game.cargo
            # (already-banked minerals from prior trips). The trip's haul
            # is lost; only previously-committed cargo can pay the bill.
            for t, cost in LANDER_REPLACEMENT_COST.items():
                have = self.game.cargo.get(t, 0)
                paid = min(have, cost)
                self.game.cargo[t] = have - paid
                # If we couldn't fully pay, the rest is "on credit" —
                # for slice MVP we just absorb it. The lander always
                # gets rebuilt (no soft-lock).

        from scz.system.orbit import PlanetOrbitScene
        from scz.system.scene import SystemScene as _Sys
        planet = _ReconstitutedPlanet(
            index=self.planet_index,
            name=self.planet_name,
            type=self.planet_type,
            color=self.planet_color,
        )
        self.game.set_scene(
            PlanetOrbitScene(
                planet=planet,
                star=self.star,
                parent_scene_cls=_Sys,
            )
        )

    def _destroy_lander(self, hazard_type: str) -> None:
        """Begin the lander-destruction sequence. The scene holds on the
        wreck for a couple seconds, then auto-ejects to orbit. Trip haul
        is lost; cost flagged in destruction_msg for the HUD."""
        assert self.game is not None
        self.lander_destroyed = True
        self.destruction_age = 0.0
        haul_summary = ", ".join(
            f"{v} {t.lower()}" for t, v in self.trip_haul.items() if v > 0
        ) or "no haul"
        cost_summary = ", ".join(
            f"{cost} {t.lower()}" for t, cost in LANDER_REPLACEMENT_COST.items()
        )
        self.destruction_msg = (
            f"LANDER LOST  ·  {hazard_type}\n"
            f"trip haul lost: {haul_summary}\n"
            f"replacement: {cost_summary}"
        )
        # Track total losses for player awareness / future achievements
        losses = self.game.flags.get("landers_lost", 0)
        self.game.flags["landers_lost"] = (losses if isinstance(losses, int) else 0) + 1
        print(f"[lander] destroyed by {hazard_type} on {self.planet_name}; "
              f"trip lost: {haul_summary}; replacement cost: {cost_summary}")

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

        # Hazards (rendered UNDER deposits + lander so deposits are
        # still readable when one's inside a hazard zone)
        self._draw_hazards(screen, ground_rect)

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

        # Destruction overlay
        if self.lander_destroyed:
            self._draw_destruction_overlay(screen)

        # Recent pickup floater
        if self.recent_pickup is not None and self.font is not None:
            rtype, rvalue = self.recent_pickup
            color = RESOURCE_VISUAL.get(rtype, {"color": (255, 240, 160)})["color"]
            alpha = max(0, 255 - int(self.recent_pickup_age / 2.5 * 255))
            label = self.recent_pickup_label or f"tractored  +{rvalue} {rtype.lower()}"
            text = self.font.render(label, True, color)
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
        """Surface visits ARE rewindable — restore position + collected state.

        Game.cargo + game.flags survive rewinds independently (Time Drive
        treats them as the player's accumulated state — collected loot
        stays collected, mineral counts are not rewound). Only the
        scene-local geometry (lander pos, which deposits THIS visit
        cleared) is captured here.
        """
        return {
            "scene": "PlanetSurfaceScene",
            "planet_name": self.planet_name,
            "lander_x": self.lander_x,
            "lander_y": self.lander_y,
            "lander_heading": self.lander_heading,
            "collected_indices": [i for i, d in enumerate(self.deposits) if d.collected],
        }

    def restore(self, state: dict) -> None:
        # Only restore if it's the same planet
        if state.get("planet_name") != self.planet_name:
            return
        self.lander_x = float(state["lander_x"])
        self.lander_y = float(state["lander_y"])
        self.lander_heading = float(state["lander_heading"])
        collected = set(state.get("collected_indices", []))
        for i, d in enumerate(self.deposits):
            d.collected = i in collected

    def _on_pickup(self, d: Deposit) -> None:
        """Apply the side-effects of a tractor collection.

        Ordinary minerals go to the TRIP HAUL — staged until the lander
        lifts off cleanly. If the lander is destroyed by a hazard, the
        trip haul is lost. Quest items (Scanner Mk III, etc.) commit
        immediately and survive destruction — they're routed via the
        ship's stasis bay, not the cargo hold.

        Cargo capacity (effective_stat("cargo_max", LANDER_CARGO_BASE))
        applies to the COMBINED total of ship cargo + this trip's haul
        — you can't bring back more than your hold can fit even if you
        survive the trip.
        """
        assert self.game is not None
        # SFX hook: per-resource-type pickup sound. Aaron's 3-bucket
        # SFX library (pickup_animal / pickup_vegetable / pickup_mineral)
        # maps onto the current 4-type deposit classification:
        #   BIO     -> pickup_animal   (organic-life sample)
        #   ENERGY  -> pickup_mineral  (energy-crystal class)
        #   COMMON / USEFUL -> pickup_mineral (rock class)
        # pickup_vegetable currently unused — reserved for a future FLORA
        # deposit type. When that lands, add a branch here.
        if hasattr(self.game, "sfx"):
            sfx_name = {
                "BIO": "lander/pickup_animal",
                "ENERGY": "lander/pickup_mineral",
                "COMMON": "lander/pickup_mineral",
                "USEFUL": "lander/pickup_mineral",
                "PACKAGE_SCANNER_MK3": "ui/notification",  # quest pickup
            }.get(d.type, "lander/pickup_mineral")
            self.game.sfx.play(sfx_name)
            # Layer a "resource detected" chime over the quick pickup tone
            # so the pickup feels weighty. Different chime per resource
            # family: warm/organic for BIO, bright/metallic for minerals.
            chime = {
                "BIO": "lander/resource_chime_bio",
                "ENERGY": "lander/resource_chime_mineral",
                "COMMON": "lander/resource_chime_mineral",
                "USEFUL": "lander/resource_chime_mineral",
            }.get(d.type)
            if chime is not None:
                self.game.sfx.play(chime)
        if d.type == "PACKAGE_SCANNER_MK3":
            # Quest item — immediate commit; survives lander destruction
            self.game.flags["scanner_mk3_in_cargo"] = True
            self.game.flags["scanner_mk3_collected"] = True
            self.game.uninstalled_modules["scanner_mk3"] = (
                self.game.uninstalled_modules.get("scanner_mk3", 0) + 1
            )
            self.recent_pickup = ("PACKAGE_SCANNER_MK3", 1)
            self.recent_pickup_label = "Scanner Mk III  ·  install at station"
            self.recent_pickup_age = 0.0
            return
        # Ordinary mineral — respect combined cargo_max (ship hold +
        # trip haul). Out of room → tractor visibly fails.
        ship_total = sum(self.game.cargo.values())
        haul_total = sum(self.trip_haul.values())
        cargo_max = int(self.game.effective_stat("cargo_max", LANDER_CARGO_BASE))
        remaining = cargo_max - ship_total - haul_total
        if remaining <= 0:
            d.collected = False
            self.recent_pickup = (d.type, 0)
            self.recent_pickup_label = "cargo full — upgrade hold at station"
            self.recent_pickup_age = 0.0
            return
        added = min(d.value, remaining)
        self.trip_haul[d.type] = self.trip_haul.get(d.type, 0) + added
        self.recent_pickup = (d.type, added)
        self.recent_pickup_label = ""
        self.recent_pickup_age = 0.0

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _draw_hazards(
        self, screen: pygame.Surface, ground_rect: pygame.Rect
    ) -> None:
        """Render hazards with per-type animated graphics so they read
        as distinct threats, not just colored circles. Active and
        inactive states are visually distinct so the player can plan
        around pulse cycles.
        """
        t = self.surface_time
        for h in self.hazards:
            cx = int(ground_rect.x + h.x * ground_rect.width)
            cy = int(ground_rect.y + h.y * ground_rect.height)
            r = int(h.radius * ground_rect.width)
            active = h.is_active(t)
            renderer = self._HAZARD_RENDERERS.get(h.type, self._draw_hazard_generic)
            renderer(self, screen, cx, cy, r, h, t, active)

    # Per-type hazard renderers ------------------------------------------------

    def _draw_hazard_generic(
        self, screen, cx, cy, r, h, t, active,
    ) -> None:
        if active:
            surf = pygame.Surface((r * 2 + 4, r * 2 + 4), pygame.SRCALPHA)
            pygame.draw.circle(surf, (*h.color, 110), (r + 2, r + 2), r)
            pygame.draw.circle(surf, (*h.color, 220), (r + 2, r + 2), r, 2)
            screen.blit(surf, (cx - r - 2, cy - r - 2))
        else:
            dim = (h.color[0] // 3, h.color[1] // 3, h.color[2] // 3)
            pygame.draw.circle(screen, dim, (cx, cy), r, 1)

    def _draw_hazard_lava(self, screen, cx, cy, r, h, t, active) -> None:
        # Lava pools are always active. Glowing molten core with darker
        # crusted rim, animated ember sparks rising, heat-shimmer ring.
        surf = pygame.Surface((r * 2 + 16, r * 2 + 16), pygame.SRCALPHA)
        center = (r + 8, r + 8)
        # Outer heat shimmer (faint pulse)
        pulse = (math.sin(t * 1.5 + h.phase) + 1) * 0.5
        glow_r = r + int(6 * pulse)
        pygame.draw.circle(surf, (255, 120, 40, 25), center, glow_r)
        # Crust rim — dark red-black
        crust = (max(0, h.color[0] - 80), max(0, h.color[1] - 40), max(0, h.color[2] - 20))
        pygame.draw.circle(surf, (*crust, 200), center, r)
        # Molten core
        molten_r = max(2, int(r * 0.78))
        pygame.draw.circle(surf, (*h.color, 230), center, molten_r)
        # Bright hot spots (3 nested bands)
        pygame.draw.circle(surf, (255, 180, 80, 200), center, max(2, int(r * 0.55)))
        pygame.draw.circle(surf, (255, 230, 160, 230), center, max(1, int(r * 0.30)))
        screen.blit(surf, (cx - r - 8, cy - r - 8))
        # Ember sparks rising — 4 sparks per pool at different phases
        for i in range(4):
            phase = (t * 0.8 + h.phase + i * 0.71) % 1.0
            ang = (h.phase * 53 + i * 1.7) % (math.pi * 2)
            sx = cx + math.cos(ang) * r * (0.4 + 0.5 * phase)
            sy = cy + math.sin(ang) * r * (0.4 + 0.5 * phase) - phase * 10
            alpha = int(255 * (1 - phase))
            spk = pygame.Surface((4, 4), pygame.SRCALPHA)
            pygame.draw.circle(spk, (255, 200, 100, alpha), (2, 2), 2)
            screen.blit(spk, (int(sx) - 2, int(sy) - 2))

    def _draw_hazard_lightning(self, screen, cx, cy, r, h, t, active) -> None:
        # Storm cell: faint outline always, bright jagged bolts when active.
        if active:
            # Dramatic flash + jagged bolts radiating from center
            surf = pygame.Surface((r * 2 + 16, r * 2 + 16), pygame.SRCALPHA)
            center = (r + 8, r + 8)
            # Flash halo
            pygame.draw.circle(surf, (200, 220, 255, 70), center, r + 6)
            pygame.draw.circle(surf, (255, 255, 255, 140), center, max(2, int(r * 0.4)))
            screen.blit(surf, (cx - r - 8, cy - r - 8))
            # Three jagged bolts radiating out
            rng = random.Random(int(t * 12) ^ int(h.phase * 1000))
            for _ in range(3):
                ang = rng.uniform(0, math.pi * 2)
                tip_x = cx + math.cos(ang) * r
                tip_y = cy + math.sin(ang) * r
                # Zigzag from center to tip
                pts = [(cx, cy)]
                segs = 4
                for s in range(1, segs + 1):
                    f = s / segs
                    px = cx + math.cos(ang) * r * f + rng.uniform(-r * 0.18, r * 0.18)
                    py = cy + math.sin(ang) * r * f + rng.uniform(-r * 0.18, r * 0.18)
                    pts.append((px, py))
                pts.append((tip_x, tip_y))
                # Bolt + glow
                pygame.draw.lines(screen, (200, 220, 255), False, pts, 3)
                pygame.draw.lines(screen, (255, 255, 255), False, pts, 1)
        else:
            # Faint storm cloud — pulsing inner darkness with sparkle hints
            charge = (math.sin(t * 3 + h.phase) + 1) * 0.5  # 0..1 charging
            cloud = pygame.Surface((r * 2 + 4, r * 2 + 4), pygame.SRCALPHA)
            center = (r + 2, r + 2)
            pygame.draw.circle(cloud, (40, 45, 70, 130), center, r)
            pygame.draw.circle(cloud, (90, 100, 140, 180), center, r, 2)
            # Faint inner spark hint as charge builds
            spark_a = int(80 * charge)
            pygame.draw.circle(cloud, (180, 200, 255, spark_a), center, max(1, int(r * 0.5)))
            screen.blit(cloud, (cx - r - 2, cy - r - 2))

    def _draw_hazard_earthquake(self, screen, cx, cy, r, h, t, active) -> None:
        # Cracked ground with jagged fissure lines. When active: shake
        # offset + brighter fissures + dust puff.
        rng = random.Random(int(h.phase * 1000) ^ 0xEA)
        shake_x, shake_y = 0, 0
        if active:
            # Small shake offset on the whole pattern
            shake_x = int(math.sin(t * 30 + h.phase) * 2)
            shake_y = int(math.cos(t * 27 + h.phase) * 2)
        surf = pygame.Surface((r * 2 + 8, r * 2 + 8), pygame.SRCALPHA)
        center = (r + 4, r + 4)
        # Faint ground discoloration ring
        pygame.draw.circle(surf, (90, 60, 40, 80), center, r)
        # 5 jagged fissure lines from center to edge
        for i in range(5):
            ang = rng.uniform(0, math.pi * 2)
            pts = [(center[0], center[1])]
            segs = 3
            for s in range(1, segs + 1):
                f = s / segs
                px = center[0] + math.cos(ang) * r * f + rng.uniform(-r * 0.15, r * 0.15)
                py = center[1] + math.sin(ang) * r * f + rng.uniform(-r * 0.15, r * 0.15)
                pts.append((px, py))
            color = (220, 160, 80, 240) if active else (h.color[0], h.color[1], h.color[2], 160)
            pygame.draw.lines(surf, color, False, pts, 2 if active else 1)
        # Hot rim when active
        if active:
            pygame.draw.circle(surf, (240, 140, 60, 180), center, r, 2)
        else:
            pygame.draw.circle(surf, (120, 80, 50, 160), center, r, 1)
        screen.blit(surf, (cx - r - 4 + shake_x, cy - r - 4 + shake_y))

    def _draw_hazard_heat(self, screen, cx, cy, r, h, t, active) -> None:
        # Heat shimmer — animated expanding rings, always active.
        surf = pygame.Surface((r * 2 + 8, r * 2 + 8), pygame.SRCALPHA)
        center = (r + 4, r + 4)
        # Base orange ground discoloration
        pygame.draw.circle(surf, (*h.color, 80), center, r)
        # 3 expanding shimmer rings at staggered phases
        for i in range(3):
            phase = (t * 0.6 + h.phase + i * 0.33) % 1.0
            ring_r = int(r * (0.2 + 0.8 * phase))
            alpha = int(180 * (1 - phase))
            if ring_r > 0:
                pygame.draw.circle(surf, (255, 200, 120, alpha), center, ring_r, 2)
        # Stable outer rim
        pygame.draw.circle(surf, (*h.color, 200), center, r, 2)
        screen.blit(surf, (cx - r - 4, cy - r - 4))

    def _draw_hazard_crack(self, screen, cx, cy, r, h, t, active) -> None:
        # Ice fissure — jagged shattered ice lines.
        rng = random.Random(int(h.phase * 100) ^ 0x1CE)
        surf = pygame.Surface((r * 2 + 8, r * 2 + 8), pygame.SRCALPHA)
        center = (r + 4, r + 4)
        # Faint cold blue ground
        pygame.draw.circle(surf, (140, 180, 220, 60), center, r)
        # 6 jagged crack lines radiating out
        for i in range(6):
            ang = rng.uniform(0, math.pi * 2)
            pts = [center]
            segs = 4
            for s in range(1, segs + 1):
                f = s / segs
                px = center[0] + math.cos(ang) * r * f + rng.uniform(-r * 0.12, r * 0.12)
                py = center[1] + math.sin(ang) * r * f + rng.uniform(-r * 0.12, r * 0.12)
                pts.append((px, py))
            if active:
                # Bright icy white-blue when cracking
                pygame.draw.lines(surf, (220, 240, 255, 230), False, pts, 3)
                pygame.draw.lines(surf, (255, 255, 255, 255), False, pts, 1)
            else:
                pygame.draw.lines(surf, (140, 170, 220, 160), False, pts, 1)
        if active:
            pygame.draw.circle(surf, (220, 240, 255, 200), center, r, 2)
        screen.blit(surf, (cx - r - 4, cy - r - 4))

    def _draw_hazard_thermal_vent(self, screen, cx, cy, r, h, t, active) -> None:
        # Underwater thermal vent: rising bubble column + steam.
        surf = pygame.Surface((r * 2 + 8, r * 2 + 8), pygame.SRCALPHA)
        center = (r + 4, r + 4)
        # Cool blue water disc
        pygame.draw.circle(surf, (90, 130, 180, 100), center, r)
        # Vent mouth
        pygame.draw.circle(surf, (40, 60, 90, 200), center, max(2, int(r * 0.3)))
        if active:
            # Erupting — rising bubble + hot column
            pygame.draw.circle(surf, (255, 220, 140, 120), center, max(2, int(r * 0.5)))
            for i in range(6):
                phase = (t * 1.2 + h.phase + i * 0.16) % 1.0
                bx = center[0] + math.sin(t * 2 + i) * r * 0.15
                by = center[1] - phase * r * 0.85
                br = max(1, int(2 + 2 * (1 - phase)))
                alpha = int(220 * (1 - phase))
                pygame.draw.circle(surf, (220, 240, 255, alpha), (int(bx), int(by)), br)
            pygame.draw.circle(surf, (180, 220, 250, 230), center, r, 2)
        else:
            # Calm — faint bubbles only
            for i in range(3):
                phase = (t * 0.4 + h.phase + i * 0.33) % 1.0
                by = center[1] - phase * r * 0.7
                pygame.draw.circle(surf, (200, 220, 240, 120), (center[0], int(by)), 1)
            pygame.draw.circle(surf, (100, 150, 200, 160), center, r, 1)
        screen.blit(surf, (cx - r - 4, cy - r - 4))

    @property
    def _HAZARD_RENDERERS(self):
        return {
            "lava": PlanetSurfaceScene._draw_hazard_lava,
            "lightning": PlanetSurfaceScene._draw_hazard_lightning,
            "earthquake": PlanetSurfaceScene._draw_hazard_earthquake,
            "heat": PlanetSurfaceScene._draw_hazard_heat,
            "crack": PlanetSurfaceScene._draw_hazard_crack,
            "thermal_vent": PlanetSurfaceScene._draw_hazard_thermal_vent,
        }

    def _draw_destruction_overlay(self, screen: pygame.Surface) -> None:
        """Fullscreen wreck banner. Held for ~2.5s then we auto-eject."""
        if self.font is None or self.title_font is None:
            return
        w, h = screen.get_size()
        # Dim layer
        dim = pygame.Surface((w, h), pygame.SRCALPHA)
        dim.fill((30, 0, 0, 140))
        screen.blit(dim, (0, 0))
        # Big banner
        title = self.title_font.render(
            "LANDER DESTROYED", True, (255, 120, 100)
        )
        tw, th = title.get_size()
        screen.blit(title, ((w - tw) // 2, h // 2 - th - 20))
        for i, line in enumerate(self.destruction_msg.split("\n")[1:]):
            text = self.font.render(line, True, (240, 230, 220))
            lw, _ = text.get_size()
            screen.blit(text, ((w - lw) // 2, h // 2 + 4 + i * 26))

    def _draw_lander(self, screen: pygame.Surface, ground_rect: pygame.Rect) -> None:
        x = ground_rect.x + self.lander_x * ground_rect.width
        y = ground_rect.y + self.lander_y * ground_rect.height
        # Tractor-beam radius — faint pulsing circle that visualizes the
        # collection range. Anything inside this ring gets tractored in.
        assert self.game is not None
        tractor_radius = self.game.effective_stat(
            "tractor_radius_bonus", TRACTOR_BEAM_BASE
        )
        tractor_pixel_radius = tractor_radius * ground_rect.width
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

        # Lander HP bar — color shifts red as HP drops
        screen.blit(self.font.render("LANDER", True, (200, 200, 220)), (x, y))
        y += 24
        assert self.game is not None
        hp_frac = max(0.0, self.lander_hp / LANDER_HP_BASE)
        # Bar
        bar_w = 280
        bar_h = 12
        pygame.draw.rect(screen, (30, 30, 50), (x, y, bar_w, bar_h))
        hp_color = (
            int(220 - 80 * hp_frac),
            int(80 + 140 * hp_frac),
            int(80 + 60 * hp_frac),
        )
        pygame.draw.rect(screen, hp_color, (x, y, int(bar_w * hp_frac), bar_h))
        pygame.draw.rect(screen, (90, 100, 130), (x, y, bar_w, bar_h), 1)
        screen.blit(
            self.font.render(
                f"  HP {int(self.lander_hp)} / {int(LANDER_HP_BASE)}",
                True, (180, 200, 220),
            ),
            (x + bar_w + 6, y - 3),
        )
        y += 24

        cargo = self.game.cargo
        cargo_total = sum(cargo.values())
        haul_total = sum(self.trip_haul.values())
        cargo_max = int(self.game.effective_stat("cargo_max", LANDER_CARGO_BASE))
        screen.blit(
            self.font.render(
                f"Ship hold: {cargo_total} + {haul_total} trip  /  {cargo_max} max",
                True, (160, 180, 200),
            ),
            (x, y),
        )
        y += 32

        # Per-resource breakdown — trip haul + ship hold side-by-side
        screen.blit(self.font.render("THIS TRIP   ·   SHIP HOLD", True, (200, 210, 230)), (x, y))
        y += 24
        for rtype in ("COMMON", "USEFUL", "BIO", "ENERGY"):
            color = RESOURCE_VISUAL[rtype]["color"]
            trip = self.trip_haul.get(rtype, 0)
            held = cargo.get(rtype, 0)
            label = f"  {rtype.lower():7s}  {trip:4d}     {held:4d}"
            screen.blit(self.font.render(label, True, color), (x, y))
            y += 22

        # Hazards summary
        if self.hazards:
            y += 8
            n_active = sum(1 for h in self.hazards if h.is_active(self.surface_time))
            warn_color = (220, 130, 80) if n_active > 0 else (140, 140, 160)
            screen.blit(
                self.font.render(
                    f"HAZARDS  {n_active} active / {len(self.hazards)} total",
                    True, warn_color,
                ),
                (x, y),
            )
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
