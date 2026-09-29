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
from pathlib import Path
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


# Surface-deposit sensor radius (normalized — fraction of the ground-rect
# width). Deposits beyond this distance from the lander are invisible.
# Inside this radius, deposits render as a fuzz-to-sharp gradient — wide
# dim halo at the sensor edge, tight bright marker when the lander is
# nearly on top. The mechanic turns deposit-hunting into a "hot/cold"
# navigation mini-game: the player can see roughly which way to go but
# not the exact position until they get close.
#
# Modules with a `surface_sensor_range` delta extend this radius — the
# Scanner Mk III adds +0.10 (base 0.20 → 0.30). Future ground-specialised
# scanners (e.g. a Planetary Anomaly Scanner) would add more.
SURFACE_SENSOR_BASE = 0.20


# Surface-hazard sensor radius (normalized). Parallel to SURFACE_SENSOR_BASE
# but for the danger-sensing system. Hazards beyond this distance render
# only as faint position-cues (or not at all at the very edge); hazards
# nearby render at full visibility so the player can navigate around them.
#
# Without a hazard-capable sensor, the lander has a generous baseline of
# 0.30 (most hazards visible from most positions). The Scanner Mk III
# adds +0.05; a future dedicated HAZARD_SCANNER would add more (+0.15+).
# The mini-game tension: upgrade your sensor stack and you'll be warned
# of lethal hazards from further away — drive without an upgrade and you
# might roll into a hazard you didn't see from across the surface.
#
# Lethal contact-damage is unchanged by visibility — hazards still hurt
# the lander whether or not the player saw them coming. Visibility is
# purely an information layer.
SURFACE_HAZARD_BASE = 0.30

# Where Firefly-authored surface-terrain textures live. The image chat
# generates these per planet type (one PNG per SURFACE_PALETTES key,
# lowercase, e.g. `terrain_rocky.png`). When a file exists it overrides
# the procedural _generate_terrain_texture fallback below. See
# `references/lore/HANDOFF_image_chat.md` for the prompt brief.
_TERRAIN_ASSETS_DIR = (
    Path(__file__).resolve().parent.parent.parent.parent / "assets" / "planets"
)


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

        # Procedurally seed life forms — moving fauna the lander catches
        # for BIO cargo. Ground fauna is harmless (lander outruns it);
        # flying fauna can damage. See `scz.planet.life` for canon.
        from scz.planet.life import generate_life_forms
        self.life: list = generate_life_forms(
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
        # Procedural surface-texture overlay — cached once per planet so we
        # don't redraw the boulder/dune/crack pattern every frame.
        # Generated deterministically from planet name + type so re-entering
        # the same planet shows the same terrain.
        self._terrain_texture: pygame.Surface | None = None

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

        # Cache the surface terrain texture. Prefer a Firefly-authored
        # asset at `assets/planets/terrain_<type>.png` when one exists;
        # fall back to the procedural pattern generator otherwise. This
        # lets the image chat ship beautiful per-type backdrops without
        # any engine changes — drop a PNG into the right path and the
        # next planet entry picks it up.
        inset = 10
        tex_w = side - 2 * inset
        tex_h = side - 2 * inset
        if tex_w > 0 and tex_h > 0:
            firefly_tex = self._load_firefly_terrain(tex_w, tex_h)
            if firefly_tex is not None:
                self._terrain_texture = firefly_tex
            else:
                self._terrain_texture = self._generate_terrain_texture(
                    tex_w, tex_h,
                )

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

        # Life forms — step movement, check flying-tier damage, check
        # capture. Ground fauna can never damage; flying does damage on
        # contact (per canon). Capture works like deposit pickup but
        # the radius is wider since the target moves.
        from scz.planet.life import (
            CATCH_RADIUS_BASE, DAMAGE_PER_SEC_BY_TIER,
            TIER_FLYING, step_motion,
        )
        step_motion(self.life, self.lander_x, self.lander_y, dt)
        catch_radius = max(tractor_radius, CATCH_RADIUS_BASE)
        for lf in self.life:
            if lf.caught:
                continue
            dx = lf.x - self.lander_x
            dy = lf.y - self.lander_y
            dist = math.hypot(dx, dy)
            # Flying-tier damage on contact (within catch radius is
            # close enough to graze). Ground tier is 0 by canon.
            if lf.tier == TIER_FLYING and dist <= catch_radius:
                dmg = DAMAGE_PER_SEC_BY_TIER[TIER_FLYING] * dt
                self.lander_hp -= dmg
                if self.lander_hp <= 0.0:
                    self.lander_hp = 0.0
                    self._destroy_lander("flying_fauna")
                    return
            # Capture — same radius gates pickup. Both tiers convert
            # to BIO cargo on the way to the trip haul.
            if dist <= catch_radius:
                lf.caught = True
                self._on_life_capture(lf)

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

        committed=True (lift-off): commit trip_haul to game.cargo, plus
            record the extraction in `game.flags['extracted_by_system']`
            so the hyperspace map can dim-out depleted systems.
        committed=False (destruction): trip_haul is LOST; pay
        replacement cost from game.cargo.
        """
        assert self.game is not None
        if committed:
            for t, v in self.trip_haul.items():
                if v > 0:
                    self.game.cargo[t] = self.game.cargo.get(t, 0) + v
            # Record extraction at the system level for hyperspace dim
            # logic. Keyed by the star's integer coords so the same
            # system across multiple visits accumulates correctly.
            sys_key = f"{int(self.star['x'])}_{int(self.star['y'])}"
            extracted_all = self.game.flags.setdefault(
                "extracted_by_system", {}
            )
            sys_extracted = extracted_all.setdefault(sys_key, {})
            for t, v in self.trip_haul.items():
                if v > 0:
                    sys_extracted[t] = sys_extracted.get(t, 0) + v
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
        # Procedural texture overlay (boulders / dunes / lava veins / etc.)
        if self._terrain_texture is not None:
            screen.blit(self._terrain_texture, ground_rect)
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

        # Deposits — rendered as fuzz-to-sharp blobs by sensor distance.
        # Out of sensor range: invisible. At the sensor edge: wide dim halo
        # (player can see direction, not precise position). Close to the
        # lander: tight bright marker (precise position resolved). The
        # sensor radius extends with `surface_sensor_range` module deltas.
        self._draw_deposits(screen, ground_rect)

        # Life forms — moving fauna with the same sensor-range gating.
        # Rendered above deposits (so a creature standing on a deposit
        # is visible) but below the lander.
        self._render_life(screen, ground_rect)

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
        # trip haul). When the incoming pickup is more valuable per-unit
        # than something the player is already carrying, auto-discard
        # the cheapest such cargo to make room. Same intent as the
        # player manually selling-and-coming-back, just folded into the
        # tractor.
        from scz.content.modules import MINERAL_PRICES

        ship_total = sum(self.game.cargo.values())
        haul_total = sum(self.trip_haul.values())
        cargo_max = int(self.game.effective_stat("cargo_max", LANDER_CARGO_BASE))
        remaining = cargo_max - ship_total - haul_total

        # `direct_fit` is what we can pick up without touching existing
        # cargo. `shortfall` is what STILL doesn't fit and could be made
        # room for by discarding lower-value cargo.
        direct_fit = max(0, min(d.value, remaining))
        shortfall = d.value - direct_fit

        swapped_total = 0
        swapped_breakdown: list[tuple[str, int]] = []
        if shortfall > 0:
            incoming_price = MINERAL_PRICES.get(d.type, 0)
            # Strictly-cheaper mineral types the player has at least
            # one unit of (combined ship cargo + trip haul). Sort
            # cheapest-first so we always discard the lowest-value
            # mineral before the next-lowest.
            candidates = sorted(
                (
                    (
                        t,
                        MINERAL_PRICES.get(t, 0),
                        self.trip_haul.get(t, 0) + self.game.cargo.get(t, 0),
                    )
                    for t in ("COMMON", "USEFUL", "BIO", "ENERGY")
                    if t != d.type
                    and MINERAL_PRICES.get(t, 0) < incoming_price
                    and (self.trip_haul.get(t, 0) + self.game.cargo.get(t, 0)) > 0
                ),
                key=lambda c: c[1],
            )
            for discard_type, _price, available in candidates:
                if shortfall <= 0:
                    break
                to_discard = min(available, shortfall)
                # Drain trip_haul first (cheaper to "lose" — never
                # committed to the ship anyway), then game.cargo.
                haul_drain = min(self.trip_haul.get(discard_type, 0), to_discard)
                if haul_drain > 0:
                    self.trip_haul[discard_type] = (
                        self.trip_haul.get(discard_type, 0) - haul_drain
                    )
                cargo_drain = to_discard - haul_drain
                if cargo_drain > 0:
                    self.game.cargo[discard_type] = (
                        self.game.cargo.get(discard_type, 0) - cargo_drain
                    )
                shortfall -= to_discard
                swapped_total += to_discard
                swapped_breakdown.append((discard_type, to_discard))

        added = direct_fit + swapped_total
        if added <= 0:
            # No room AND nothing cheaper to swap out — tractor visibly
            # fails, deposit stays put. Same refusal-floater as before.
            d.collected = False
            self.recent_pickup = (d.type, 0)
            self.recent_pickup_label = "cargo full — upgrade hold at station"
            self.recent_pickup_age = 0.0
            return

        self.trip_haul[d.type] = self.trip_haul.get(d.type, 0) + added

        # Floater: distinguish "clean pickup", "swap happened", "partial
        # swap". The clean-pickup case keeps its empty label (existing
        # behavior). The swap case names what got discarded so the
        # player learns the mechanic the first time they see it.
        if swapped_total > 0:
            disc_label = " + ".join(
                f"{n} {t.lower()}" for t, n in swapped_breakdown
            )
            # ASCII arrow only — Windows cp1252 console chokes on the
            # unicode arrow in logs/walks.
            self.recent_pickup_label = (
                f"swapped {disc_label} -> {added} {d.type.lower()}"
            )
        else:
            self.recent_pickup_label = ""
        self.recent_pickup = (d.type, added)
        self.recent_pickup_age = 0.0

    def _on_life_capture(self, lf) -> None:  # type: ignore[no-untyped-def]
        """Captured life form → BIO cargo (trip haul).

        Same trip-haul / cargo-cap rules as mineral pickups: yield
        stages in `self.trip_haul["BIO"]` and commits to game.cargo on
        lift-off. Bio-Architect / cargo modules affect the cap via
        `effective_stat("cargo_max", ...)`. Overflow is silently
        dropped — fauna capture doesn't compete with mineral auto-swap
        since both feed BIO; if the hold is full, the catch is logged
        but the value is clipped to remaining space.
        """
        assert self.game is not None
        ship_total = sum(self.game.cargo.values())
        haul_total = sum(self.trip_haul.values())
        cargo_max = int(self.game.effective_stat("cargo_max", LANDER_CARGO_BASE))
        remaining = cargo_max - ship_total - haul_total
        added = max(0, min(int(lf.bio_value), remaining))
        if added > 0:
            self.trip_haul["BIO"] = self.trip_haul.get("BIO", 0) + added
            tier_label = "fauna" if lf.tier == "ground" else "flying fauna"
            self.recent_pickup = ("BIO", added)
            self.recent_pickup_label = f"caught {tier_label}  ·  +{added} bio"
        else:
            self.recent_pickup = ("BIO", 0)
            self.recent_pickup_label = "cargo full - fauna released"
        self.recent_pickup_age = 0.0

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _load_firefly_terrain(
        self, w: int, h: int,
    ) -> pygame.Surface | None:
        """Try to load a Firefly-authored surface-terrain texture for
        this planet type. Returns a scaled pygame Surface, or None if
        no asset exists yet (caller falls back to the procedural pattern).

        Lookup is by planet type — `assets/planets/terrain_<type>.png`,
        all lowercase. Examples: `terrain_rocky.png`, `terrain_terrestrial.png`.
        The image chat owns the contents of that directory; this loader
        is read-only and tolerant of missing files (no shouting in logs;
        the procedural fallback is a perfectly valid render mode).
        """
        candidate = (
            _TERRAIN_ASSETS_DIR / f"terrain_{self.planet_type.lower()}.png"
        )
        if not candidate.exists():
            return None
        try:
            raw = pygame.image.load(str(candidate)).convert()
        except (pygame.error, FileNotFoundError):
            # If pygame can't decode (corrupt, unsupported), drop back
            # to the procedural pattern silently.
            return None
        # Scale to the inset ground rect. smoothscale gives a clean
        # blit at any HUD size; the source asset doesn't need to be
        # exactly square.
        return pygame.transform.smoothscale(raw, (w, h))

    def _generate_terrain_texture(
        self, w: int, h: int,
    ) -> pygame.Surface:
        """Generate a procedural surface-texture overlay for this planet.

        Per-type pattern (boulders / dunes / cracks / lava veins / etc.)
        layered onto an alpha surface, ready to blit on top of the flat
        terrain rect. Deterministic by planet name + type seed so each
        planet looks the same on re-entry but different from its
        neighbors.

        Cheap to call once at scene-load; reused every frame via cache.
        """
        import random as _random
        surf = pygame.Surface((w, h), pygame.SRCALPHA)
        seed = (hash(self.planet_name) ^ hash(self.planet_type)) & 0x7FFFFFFF
        rng = _random.Random(seed)
        _, terrain = SURFACE_PALETTES.get(
            self.planet_type, ((50, 50, 60), (110, 100, 100)),
        )

        def shade(amount: int) -> tuple[int, int, int]:
            return (
                max(0, min(255, terrain[0] + amount)),
                max(0, min(255, terrain[1] + amount)),
                max(0, min(255, terrain[2] + amount)),
            )

        pt = self.planet_type
        if pt == "ROCKY":
            # Boulders — dark scatter
            for _ in range(140):
                x, y = rng.randint(0, w), rng.randint(0, h)
                r = rng.randint(2, 9)
                c = shade(rng.randint(-50, -10))
                pygame.draw.circle(surf, (*c, 200), (x, y), r)
            # Fracture lines
            for _ in range(12):
                x, y = rng.randint(0, w), rng.randint(0, h)
                length = rng.randint(40, 120)
                angle = rng.uniform(0, math.tau)
                pts = [(x, y)]
                for _ in range(rng.randint(3, 6)):
                    seg = length / 5
                    angle += rng.uniform(-0.4, 0.4)
                    x += seg * math.cos(angle)
                    y += seg * math.sin(angle)
                    pts.append((x, y))
                pygame.draw.lines(surf, (*shade(-60), 180), False, pts, 2)

        elif pt == "DESERT":
            # Sinusoidal dune ridges
            for band in range(10):
                band_y = (band + 0.5) * h / 10
                pts = []
                for x_step in range(0, w + 8, 8):
                    phase = band * 1.3 + (x_step / w) * math.pi * 3
                    y = band_y + math.sin(phase) * (h / 20)
                    pts.append((x_step, y))
                pygame.draw.lines(surf, (*shade(20), 150), False, pts, 2)
            # Dust spots
            for _ in range(70):
                x, y = rng.randint(0, w), rng.randint(0, h)
                r = rng.randint(2, 6)
                pygame.draw.circle(
                    surf, (*shade(rng.randint(-20, 10)), 120), (x, y), r,
                )

        elif pt == "ICE":
            # Crack lines (light)
            for _ in range(25):
                x, y = rng.randint(0, w), rng.randint(0, h)
                length = rng.randint(30, 100)
                angle = rng.uniform(0, math.tau)
                pts = [(x, y)]
                for _ in range(rng.randint(2, 5)):
                    seg = length / 4
                    angle += rng.uniform(-0.5, 0.5)
                    x += seg * math.cos(angle)
                    y += seg * math.sin(angle)
                    pts.append((x, y))
                pygame.draw.lines(surf, (255, 255, 255, 100), False, pts, 1)
            # Ice patches (slightly lighter circles)
            for _ in range(90):
                x, y = rng.randint(0, w), rng.randint(0, h)
                r = rng.randint(4, 14)
                pygame.draw.circle(surf, (255, 255, 255, 50), (x, y), r)

        elif pt == "VOLCANIC":
            # Lava veins — bright glowing thin lines
            for _ in range(28):
                x, y = rng.randint(0, w), rng.randint(0, h)
                length = rng.randint(40, 140)
                angle = rng.uniform(0, math.tau)
                pts = [(x, y)]
                for _ in range(rng.randint(4, 8)):
                    seg = length / 6
                    angle += rng.uniform(-0.3, 0.3)
                    x += seg * math.cos(angle)
                    y += seg * math.sin(angle)
                    pts.append((x, y))
                pygame.draw.lines(surf, (255, 140, 60, 220), False, pts, 2)
            # Ash patches (dark)
            for _ in range(60):
                x, y = rng.randint(0, w), rng.randint(0, h)
                r = rng.randint(3, 10)
                pygame.draw.circle(surf, (30, 20, 20, 160), (x, y), r)

        elif pt == "OCEAN":
            # Horizontal wave bands
            for band in range(22):
                band_y = (band + 0.5) * h / 22 + rng.uniform(-5, 5)
                pts = []
                for x_step in range(0, w + 16, 16):
                    phase = band * 0.7 + (x_step / w) * math.pi * 4
                    y = band_y + math.sin(phase) * 3
                    pts.append((x_step, y))
                pygame.draw.lines(surf, (220, 230, 250, 60), False, pts, 1)

        elif pt == "PRIMORDIAL":
            # Glowing lava blotches
            for _ in range(45):
                x, y = rng.randint(0, w), rng.randint(0, h)
                r = rng.randint(8, 24)
                glow = pygame.Surface(
                    (r * 2 + 4, r * 2 + 4), pygame.SRCALPHA,
                )
                for rr in range(r, 0, -3):
                    a = int(80 * (1 - rr / r))
                    pygame.draw.circle(
                        glow, (255, 200, 80, a), (r + 2, r + 2), rr,
                    )
                surf.blit(glow, (x - r - 2, y - r - 2))
            # Dark cracks
            for _ in range(18):
                x, y = rng.randint(0, w), rng.randint(0, h)
                length = rng.randint(20, 60)
                angle = rng.uniform(0, math.tau)
                pts = [(x, y)]
                for _ in range(rng.randint(2, 4)):
                    seg = length / 3
                    angle += rng.uniform(-0.5, 0.5)
                    x += seg * math.cos(angle)
                    y += seg * math.sin(angle)
                    pts.append((x, y))
                pygame.draw.lines(surf, (60, 20, 10, 220), False, pts, 2)

        elif pt == "TERRESTRIAL":
            # Vegetation patches — greener-than-base circles
            for _ in range(95):
                x, y = rng.randint(0, w), rng.randint(0, h)
                r = rng.randint(4, 16)
                green = rng.randint(10, 40)
                color = (
                    max(0, terrain[0] - green // 2),
                    min(255, terrain[1] + green),
                    max(0, terrain[2] - green // 2),
                    140,
                )
                pygame.draw.circle(surf, color, (x, y), r)
            # Small water spots
            for _ in range(18):
                x, y = rng.randint(0, w), rng.randint(0, h)
                r = rng.randint(5, 14)
                pygame.draw.circle(surf, (80, 130, 180, 140), (x, y), r)

        # Other planet types (or unknown) get no overlay — the flat terrain
        # color suffices.
        return surf

    def _draw_hazards(
        self, screen: pygame.Surface, ground_rect: pygame.Rect
    ) -> None:
        """Render each hazard fuzz-to-sharp by lander distance.

        Out-of-range hazards (beyond `surface_hazard_range`) render
        invisible — *dangerous*: the lander can roll into them blind.
        Near-edge hazards render as faint danger-color clouds that hint
        at position but not precise extent. Close-in hazards render at
        full visibility (the original active/inactive distinction).

        Lethal contact damage is unchanged by visibility. The
        information-layer (can the player see this hazard?) is upgraded
        via `surface_hazard_range` deltas; the damage-layer (what
        happens when the lander overlaps an active hazard?) is unchanged.
        """
        assert self.game is not None
        hazard_range = self.game.effective_stat(
            "surface_hazard_range", SURFACE_HAZARD_BASE,
        )
        hazard_range = max(0.05, min(1.5, hazard_range))

        for h in self.hazards:
            # Distance from lander to hazard CENTER. Hazards have radius;
            # we don't subtract the radius (so a hazard's outer edge can
            # poke into visibility before its center crosses the sensor
            # threshold). This matches the player's intuition: a wide
            # lava field becomes faintly visible before you're "in range
            # of its middle."
            dx = h.x - self.lander_x
            dy = h.y - self.lander_y
            dist = math.hypot(dx, dy)
            if dist >= hazard_range + h.radius:
                continue   # well out of sensor range — invisible

            # Effective fuzz: 0 when the lander is on top of the hazard
            # center, 1 when the hazard center is at the very sensor edge.
            # Clamped so a hazard inside the sensor range never reads as
            # over-faded.
            fuzz = max(0.0, min(1.0, dist / hazard_range))

            cx = ground_rect.x + h.x * ground_rect.width
            cy = ground_rect.y + h.y * ground_rect.height
            r = int(h.radius * ground_rect.width)
            active = h.is_active(self.surface_time)

            if active:
                # Translucent filled disc + bright outline; both
                # alpha-modulated by fuzz so distant hazards read as
                # faint danger-clouds, close hazards as full warnings
                fill_a = int(110 * (1.0 - 0.7 * fuzz))
                outline_a = int(220 * (1.0 - 0.6 * fuzz))
                if fill_a > 8 or outline_a > 16:
                    surf = pygame.Surface((r * 2 + 4, r * 2 + 4), pygame.SRCALPHA)
                    if fill_a > 8:
                        pygame.draw.circle(
                            surf, (*h.color, fill_a), (r + 2, r + 2), r,
                        )
                    if outline_a > 16:
                        pygame.draw.circle(
                            surf, (*h.color, outline_a), (r + 2, r + 2), r, 2,
                        )
                    screen.blit(surf, (int(cx) - r - 2, int(cy) - r - 2))
            else:
                # Faint outline ring — already-dim, just additionally
                # faded by fuzz. At max fuzz the inactive ring vanishes
                # entirely (you can't see a between-pulse hazard from
                # across the surface)
                base_dim = (
                    h.color[0] // 3, h.color[1] // 3, h.color[2] // 3,
                )
                outline_a = int(255 * (1.0 - fuzz))
                if outline_a > 16:
                    surf = pygame.Surface((r * 2 + 4, r * 2 + 4), pygame.SRCALPHA)
                    pygame.draw.circle(
                        surf, (*base_dim, outline_a), (r + 2, r + 2), r, 1,
                    )
                    screen.blit(surf, (int(cx) - r - 2, int(cy) - r - 2))

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

    def _draw_deposits(
        self, screen: pygame.Surface, ground_rect: pygame.Rect,
    ) -> None:
        """Render deposits as fuzz-to-sharp blobs based on lander distance.

        The lander has a sensor radius (`surface_sensor_range` stat;
        default `SURFACE_SENSOR_BASE` = 0.20 = 20% of ground width). For
        each uncollected deposit:

        - **Out of range**: not drawn — completely invisible
        - **At the sensor edge** (fuzz≈1.0): wide dim halo centered on the
          actual deposit position. The player can see *roughly which way
          to go* but not the exact spot
        - **Closer in** (fuzz declining): halo shrinks, an inner bright
          marker fades in
        - **Near the lander** (fuzz≈0): tight bright marker — the original
          flat-rendering, fully resolved position

        Sensor radius scales with installed modules' `surface_sensor_range`
        deltas — the Scanner Mk III is the standard upgrade (+0.10).
        """
        assert self.game is not None
        sensor_radius = self.game.effective_stat(
            "surface_sensor_range", SURFACE_SENSOR_BASE,
        )
        # Safety clamp — surface space is normalized [0, 1], anything past
        # ~sqrt(2) covers the entire visible diagonal
        sensor_radius = max(0.05, min(1.5, sensor_radius))

        # Per-type range bonuses from specialty sensors (2026-05-18):
        # - `deep_strata_visibility` extends range for ENERGY+USEFUL
        # - `artifact_visibility_full` makes PACKAGE always visible
        # - `mineral_type_clarity` shows type letter even at fuzz-edge
        deep_strata = self.game.effective_stat("deep_strata_visibility", 0.0)
        artifact_full = self.game.effective_stat("artifact_visibility_full", 0.0)
        type_clarity = self.game.effective_stat("mineral_type_clarity", 0.0)

        for d in self.deposits:
            if d.collected:
                continue
            dx = d.x - self.lander_x
            dy = d.y - self.lander_y
            dist = math.hypot(dx, dy)
            # Per-type effective range. Artifacts (PACKAGE_*) are
            # always rendered when the Stelloth locator is installed
            # — diagonal covers the whole surface.
            type_radius = sensor_radius
            if d.type == "ENERGY" or d.type == "USEFUL":
                type_radius += deep_strata
            if d.type.startswith("PACKAGE_") and artifact_full > 0.0:
                type_radius = 2.0    # whole-surface visibility
            if dist >= type_radius:
                continue   # out of sensor — invisible

            # 0.0 = lander on top of deposit (sharp); 1.0 = at sensor edge (max fuzz)
            fuzz = dist / type_radius

            sx = int(ground_rect.x + d.x * ground_rect.width)
            sy = int(ground_rect.y + d.y * ground_rect.height)

            vis = RESOURCE_VISUAL[d.type]
            base_color = vis["color"]
            base_size = vis["size"]

            # Outer halo — radius grows from base_size to base_size+30 with fuzz,
            # alpha stays modest so several deposits in a cluster don't overload
            halo_r = base_size + int(30 * fuzz)
            halo_alpha = int(70 * (1.0 - 0.3 * fuzz))   # 70 at sharp, 49 at edge
            if halo_r > 0 and halo_alpha > 0:
                size = halo_r * 2 + 2
                halo_surf = pygame.Surface((size, size), pygame.SRCALPHA)
                # Three concentric rings approximate a Gaussian-ish falloff
                for frac, alpha_mult in ((1.0, 0.35), (0.65, 0.55), (0.35, 0.80)):
                    r = int(halo_r * frac)
                    if r <= 0:
                        continue
                    a = int(halo_alpha * alpha_mult)
                    pygame.draw.circle(
                        halo_surf,
                        (*base_color, a),
                        (halo_r + 1, halo_r + 1),
                        r,
                    )
                screen.blit(halo_surf, (sx - halo_r - 1, sy - halo_r - 1))

            # Inner bright marker — fades to zero by fuzz≈0.7 so the very edge
            # of sensor range gives DIRECTION ONLY, not position precision
            inner_alpha = int(255 * max(0.0, 1.0 - fuzz / 0.7))
            if inner_alpha > 5:
                inner_size = base_size + 2
                inner_surf = pygame.Surface(
                    (inner_size * 2 + 2, inner_size * 2 + 2), pygame.SRCALPHA,
                )
                # Bright center dot + dim outer ring (original flat-render look,
                # alpha-modulated for the close-in transition)
                pygame.draw.circle(
                    inner_surf,
                    (*base_color, inner_alpha),
                    (inner_size + 1, inner_size + 1),
                    base_size,
                )
                glow_color = (
                    base_color[0] // 3,
                    base_color[1] // 3,
                    base_color[2] // 3,
                    inner_alpha // 2,
                )
                pygame.draw.circle(
                    inner_surf,
                    glow_color,
                    (inner_size + 1, inner_size + 1),
                    base_size + 2, 1,
                )
                screen.blit(
                    inner_surf, (sx - inner_size - 1, sy - inner_size - 1),
                )

            # Mineral Spectrometer — type letter visible at sensor edge,
            # not just at close range. Renders a single character (C/U/B/E
            # or 'P' for PACKAGE_*) next to the deposit when type-clarity
            # is installed AND the standard inner marker is too faint to
            # read (i.e. we're past the inner-fade fuzz threshold).
            if type_clarity > 0.0 and inner_alpha <= 80 and self.font is not None:
                if d.type.startswith("PACKAGE_"):
                    letter = "P"
                else:
                    letter = d.type[:1]
                glyph = self.font.render(letter, True, base_color)
                gw, gh = glyph.get_size()
                screen.blit(glyph, (sx + base_size + 4, sy - gh // 2))

    def _render_life(
        self, screen: pygame.Surface, ground_rect: pygame.Rect,
    ) -> None:
        """Render uncaught life forms onto the ground rect.

        Same sensor-range gating as deposits — fauna outside the
        surface sensor radius is invisible. Inside, ground tier
        renders as a warm-tone dot with a small motion-trail; flying
        tier gets a paler dot with a wider halo to telegraph the
        damage threat.
        """
        assert self.game is not None
        from scz.planet.life import LIFE_VISUAL, TIER_FLYING

        sensor_radius = self.game.effective_stat(
            "surface_sensor_range", SURFACE_SENSOR_BASE,
        )
        sensor_radius = max(0.05, min(1.5, sensor_radius))

        # Bio-Sense Scanner extends the general sensor reach for fauna
        # specifically. Karavem Aerial Sentry adds extra range JUST for
        # flying-tier creatures. Both deltas stack.
        bio_bonus = self.game.effective_stat("life_detect_range", 0.0)
        flying_bonus = self.game.effective_stat("flying_threat_range", 0.0)

        for lf in self.life:
            if lf.caught:
                continue
            dx = lf.x - self.lander_x
            dy = lf.y - self.lander_y
            dist = math.hypot(dx, dy)
            # Tier-dependent effective range
            eff_radius = sensor_radius + bio_bonus
            if lf.tier == TIER_FLYING:
                eff_radius += flying_bonus
            if dist >= eff_radius:
                continue
            fuzz = dist / eff_radius

            sx = int(ground_rect.x + lf.x * ground_rect.width)
            sy = int(ground_rect.y + lf.y * ground_rect.height)
            vis = LIFE_VISUAL[lf.tier]
            base_color = vis["color"]
            base_size = vis["size"]
            # Flying tier gets a bigger halo — visual cue: threat radius
            halo_r = base_size + (16 if lf.tier == TIER_FLYING else 8)
            halo_alpha = int(80 * (1.0 - 0.3 * fuzz))
            if halo_r > 0 and halo_alpha > 0:
                size = halo_r * 2 + 2
                halo_surf = pygame.Surface((size, size), pygame.SRCALPHA)
                for frac, mult in ((1.0, 0.30), (0.6, 0.55)):
                    r = int(halo_r * frac)
                    if r <= 0:
                        continue
                    a = int(halo_alpha * mult)
                    pygame.draw.circle(
                        halo_surf, (*base_color, a),
                        (halo_r + 1, halo_r + 1), r,
                    )
                screen.blit(halo_surf, (sx - halo_r - 1, sy - halo_r - 1))
            inner_alpha = int(255 * max(0.0, 1.0 - fuzz / 0.7))
            if inner_alpha > 5:
                inner_size = base_size + 2
                inner_surf = pygame.Surface(
                    (inner_size * 2 + 2, inner_size * 2 + 2), pygame.SRCALPHA,
                )
                pygame.draw.circle(
                    inner_surf, (*base_color, inner_alpha),
                    (inner_size + 1, inner_size + 1), base_size,
                )
                screen.blit(
                    inner_surf, (sx - inner_size - 1, sy - inner_size - 1),
                )

    def _draw_sensor_ring(
        self, screen: pygame.Surface, ground_rect: pygame.Rect,
        cx: int, cy: int,
    ) -> None:
        """Draw a faint dashed ring around the lander showing current
        surface-deposit-sensor radius. Visually communicates what the
        installed sensor module can see — the ring expands when the
        player upgrades.
        """
        assert self.game is not None
        sensor_radius = self.game.effective_stat(
            "surface_sensor_range", SURFACE_SENSOR_BASE,
        )
        ring_px = int(sensor_radius * ground_rect.width)
        if ring_px < 8:
            return
        # Dashed ring — a slow rotation animates it ("active sweeping")
        ticks = pygame.time.get_ticks() / 1000.0
        n_segments = 36
        rot = (ticks * 0.5) % (math.tau / n_segments)
        for i in range(n_segments):
            if i % 2 != 0:
                continue   # gap segments
            a0 = rot + i * (math.tau / n_segments)
            a1 = a0 + (math.tau / n_segments) * 0.8
            x0 = cx + ring_px * math.cos(a0)
            y0 = cy + ring_px * math.sin(a0)
            x1 = cx + ring_px * math.cos(a1)
            y1 = cy + ring_px * math.sin(a1)
            pygame.draw.line(screen, (160, 200, 220, 110), (x0, y0), (x1, y1), 1)

    def _draw_scan_pulse(
        self, screen: pygame.Surface, ground_rect: pygame.Rect,
        cx: int, cy: int,
    ) -> None:
        """Slow expanding ripple from the lander — visualizes the sensor
        actively scanning. The ripple expands to the sensor radius then
        restarts. Single pulse at a time; non-intrusive.
        """
        assert self.game is not None
        sensor_radius = self.game.effective_stat(
            "surface_sensor_range", SURFACE_SENSOR_BASE,
        )
        max_r_px = int(sensor_radius * ground_rect.width)
        if max_r_px < 8:
            return
        # Pulse period: 2.4 seconds. Phase progresses 0→1 over that window.
        period = 2.4
        phase = (pygame.time.get_ticks() / 1000.0 % period) / period
        # Radius grows linearly; alpha fades as radius approaches max
        r = int(max_r_px * phase)
        if r < 4:
            return
        alpha = int(140 * (1.0 - phase) ** 2)
        if alpha < 8:
            return
        ring_size = r * 2 + 4
        ring_surf = pygame.Surface((ring_size, ring_size), pygame.SRCALPHA)
        pygame.draw.circle(
            ring_surf, (180, 220, 240, alpha), (r + 2, r + 2), r, 2,
        )
        screen.blit(ring_surf, (cx - r - 2, cy - r - 2))

    def _draw_hazard_warning(
        self, screen: pygame.Surface, ground_rect: pygame.Rect,
        cx: int, cy: int,
    ) -> None:
        """Render a 'DANGER NEARBY' warning when an *active* hazard is
        close to but not currently overlapping the lander. The threshold
        is half the hazard's radius outside its edge — close enough that
        a careless drift could kill the lander.

        Cued visually as a pulsing red warning arc on the lander side
        facing the nearest dangerous hazard.
        """
        # Find the nearest active hazard within warning distance
        nearest = None
        nearest_dist = float("inf")
        warning_band = 0.05   # half a normalized unit beyond hazard edge
        for h in self.hazards:
            if not h.is_active(self.surface_time):
                continue
            dx = h.x - self.lander_x
            dy = h.y - self.lander_y
            dist = math.hypot(dx, dy)
            outer_edge = dist - h.radius
            if 0 < outer_edge < warning_band and dist < nearest_dist:
                nearest = h
                nearest_dist = dist
        if nearest is None:
            return
        # Direction from lander to hazard (in normalized coords)
        dx = nearest.x - self.lander_x
        dy = nearest.y - self.lander_y
        ang = math.atan2(dy, dx)
        # Pulsing warning chevron — drawn slightly outside the lander on
        # the side facing the hazard
        ticks = pygame.time.get_ticks() / 1000.0
        pulse = (math.sin(ticks * 6) + 1) / 2   # fast pulse, urgent feel
        offset_px = 20
        wx = cx + offset_px * math.cos(ang)
        wy = cy + offset_px * math.sin(ang)
        # Three short red ticks forming a "look out" indicator
        red = (255, int(80 + pulse * 100), int(60 + pulse * 60))
        for i in range(3):
            r_off = 4 + i * 4
            tx = cx + (offset_px - r_off) * math.cos(ang)
            ty = cy + (offset_px - r_off) * math.sin(ang)
            # Short perpendicular tick
            px = -math.sin(ang) * (5 - i)
            py = math.cos(ang) * (5 - i)
            pygame.draw.line(
                screen, red,
                (tx - px, ty - py), (tx + px, ty + py), 2,
            )
        # Triangle pointing at the hazard
        tip = (cx + (offset_px + 6) * math.cos(ang),
               cy + (offset_px + 6) * math.sin(ang))
        base_l = (cx + (offset_px - 2) * math.cos(ang) - 4 * math.sin(ang),
                  cy + (offset_px - 2) * math.sin(ang) + 4 * math.cos(ang))
        base_r = (cx + (offset_px - 2) * math.cos(ang) + 4 * math.sin(ang),
                  cy + (offset_px - 2) * math.sin(ang) - 4 * math.cos(ang))
        pygame.draw.polygon(screen, red, (tip, base_l, base_r))

    def _draw_lander(self, screen: pygame.Surface, ground_rect: pygame.Rect) -> None:
        x = ground_rect.x + self.lander_x * ground_rect.width
        y = ground_rect.y + self.lander_y * ground_rect.height
        cx_i = int(x)
        cy_i = int(y)

        # Sensor visualization layers — drawn UNDER the lander so the
        # lander icon stays clearly on top. Dashed sensor ring shows the
        # current surface-sensor reach; expanding pulse animates the
        # "actively scanning" feel. Both expand when the player installs
        # better sensor modules — visible feedback for the upgrade pillar.
        self._draw_sensor_ring(screen, ground_rect, cx_i, cy_i)
        self._draw_scan_pulse(screen, ground_rect, cx_i, cy_i)

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
            screen, beam_color, (cx_i, cy_i), int(tractor_pixel_radius), 1
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

        # Hazard proximity warning — drawn ON TOP of the lander so the
        # chevron is immediately visible when an active hazard is within
        # the warning band. Only fires when a hazard scanner is installed
        # and an active hazard is close.
        self._draw_hazard_warning(screen, ground_rect, cx_i, cy_i)

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

        # Sensors readout — surfaces the player's currently-effective
        # sensor radii so they can read why blobs are fuzzy or sharp.
        # Highlights the upgrade pillar: install a better scanner →
        # numbers go up → ring + scan pulse visibly expand on the surface.
        y += 12
        sensor_color = (160, 200, 220)
        sensor_dim = (110, 140, 160)
        screen.blit(self.font.render("SENSORS", True, sensor_color), (x, y))
        y += 22
        deposit_range = self.game.effective_stat(
            "surface_sensor_range", SURFACE_SENSOR_BASE,
        )
        hazard_range = self.game.effective_stat(
            "surface_hazard_range", SURFACE_HAZARD_BASE,
        )
        tractor_radius = self.game.effective_stat(
            "tractor_radius_bonus", TRACTOR_BEAM_BASE,
        )
        # Indicate "base" vs upgraded with a subtle color shift —
        # upgraded values render brighter so the player notices.
        def _stat_color(value: float, base: float) -> tuple[int, int, int]:
            return sensor_color if value > base + 1e-3 else sensor_dim
        screen.blit(
            self.font.render(
                f"  deposit  {deposit_range:.2f}", True,
                _stat_color(deposit_range, SURFACE_SENSOR_BASE),
            ),
            (x, y),
        )
        y += 20
        screen.blit(
            self.font.render(
                f"  hazard   {hazard_range:.2f}", True,
                _stat_color(hazard_range, SURFACE_HAZARD_BASE),
            ),
            (x, y),
        )
        y += 20
        screen.blit(
            self.font.render(
                f"  tractor  {tractor_radius:.2f}", True,
                _stat_color(tractor_radius, TRACTOR_BEAM_BASE),
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
            "Lift off: Esc / B / Backspace",
            "Rewind:  R / Back",
            "Quit:    Start (or Lift off -> Pause -> Quit)",
        ):
            screen.blit(self.font.render(line, True, (130, 150, 180)), (x, controls_y))
            controls_y += 22
