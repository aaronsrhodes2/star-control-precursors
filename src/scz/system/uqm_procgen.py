"""UQM-faithful procedural planet generation.

Mirrors the SC2 source so the planets at each star match the canonical
SC2 universe. Per Aaron's design: 250kya is short geologically, so we
use the same procgen seed (the SC2-era star coords) and apply only
small Furling-era tweaks on top.

Sources ported (see `tools/extract_uqm_planet_data.py` for data
extraction):
  - libs/math/random2.c   → UqmRandom (Park-Miller LCG, A=16807)
  - planets/orbits.c       → FillOrbits + the six XxxDistribution tables
  - planets/plandata.c     → 59 PlanetFrame entries (data)
  - planets/planets.h      → SCALE_RADIUS, MIN/MAX_PLANET_RADIUS, etc.
  - solarsys.c             → GetRandomSeedForStar (DWORD(x, y))
  - units.h                → CIRCLE_SHIFT=6 → FULL_CIRCLE=64

Critical correctness rule: bit-exact match to SC2 requires the RNG
+ the seed source + the bit manipulation in FillOrbits to be 1:1. We
keep all arithmetic in 32-bit unsigned space.

Output is converted from UQM's internal radius units into the (x, y)
system-local coordinates the existing SystemScene already understands.
"""

from __future__ import annotations

import json
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Any


# ---------------------------------------------------------------------------
# Constants ported from UQM headers
# ---------------------------------------------------------------------------

# planets.h
SCALE_SHIFT = 6
EARTH_RADIUS = 8 << SCALE_SHIFT           # 512
MIN_PLANET_RADIUS = 4 << SCALE_SHIFT      # 256
MAX_PLANET_RADIUS = 124 << SCALE_SHIFT    # 7936
MIN_MOON_RADIUS = 35
MOON_DELTA = 20
MAX_MOONS = 4

# orbits.c — min orbit distance per (star_size, rocky-vs-gas) combination
DWARF_ROCK_DIST = MIN_PLANET_RADIUS
DWARF_GASG_DIST = 12 << SCALE_SHIFT       # 768
GIANT_ROCK_DIST = 8 << SCALE_SHIFT        # 512
GIANT_GASG_DIST = 13 << SCALE_SHIFT       # 832
SUPERGIANT_ROCK_DIST = 16 << SCALE_SHIFT  # 1024
SUPERGIANT_GASG_DIST = 33 << SCALE_SHIFT  # 2112

# Indexed by star size (DWARF=0, GIANT=1, SUPERGIANT=2)
SUN_MIN_DISTS = [
    (DWARF_ROCK_DIST, DWARF_GASG_DIST),
    (GIANT_ROCK_DIST, GIANT_GASG_DIST),
    (SUPERGIANT_ROCK_DIST, SUPERGIANT_GASG_DIST),
]

MAX_GENERATED_PLANETS = 9

# units.h
CIRCLE_SHIFT = 6
FULL_CIRCLE = 1 << CIRCLE_SHIFT           # 64

# Planet enum boundaries (must match plandata.h)
NUMBER_OF_PLANET_TYPES = 59
FIRST_SMALL_ROCKY_WORLD = 0
LAST_SMALL_ROCKY_WORLD = 28
FIRST_LARGE_ROCKY_WORLD = 29
LAST_LARGE_ROCKY_WORLD = 49
FIRST_GAS_GIANT = 50
LAST_GAS_GIANT = 58


# Star-type names → indices (matches extract_sc2_universe.py STAR_TYPES)
STAR_TYPE_TO_IDX = {
    "DWARF_STAR": 0,
    "GIANT_STAR": 1,
    "SUPER_GIANT_STAR": 2,
}


# ---------------------------------------------------------------------------
# Park-Miller LCG ported from libs/math/random2.c
# ---------------------------------------------------------------------------

_A = 16807
_M = 2147483647   # 2^31 - 1
_Q = 127773       # M // A
_R = 2836         # M % A


class UqmRandom:
    """Bit-for-bit port of UQM's RandomContext (random2.c). 32-bit
    unsigned arithmetic; the same seed produces the same sequence as
    the original C code.
    """
    __slots__ = ("seed",)

    def __init__(self, seed: int = 12345) -> None:
        self.seed = seed & 0xFFFFFFFF

    def reseed(self, new_seed: int) -> int:
        new_seed &= 0xFFFFFFFF
        if new_seed == 0:
            new_seed = 1
        elif new_seed > _M:
            new_seed -= _M
        old = self.seed
        self.seed = new_seed
        return old

    def random(self) -> int:
        # seed = A * (seed % Q) - R * (seed / Q)
        s = self.seed
        new = (_A * (s % _Q) - _R * (s // _Q)) & 0xFFFFFFFF
        if new > _M:
            new = (new - _M) & 0xFFFFFFFF
        elif new == 0:
            new = 1
        self.seed = new
        return new


def get_random_seed_for_star(x: int, y: int) -> int:
    """Mirror of solarsys.c:361 — MAKE_DWORD(star_pt.x, star_pt.y).
    The DWORD packs (x as low 16 bits, y as high 16 bits)."""
    return ((y & 0xFFFF) << 16) | (x & 0xFFFF)


# UQM macros — local helpers
def _LOWORD(d: int) -> int:
    return d & 0xFFFF


def _HIBYTE(w: int) -> int:
    return (w >> 8) & 0xFF


def _LOBYTE(w: int) -> int:
    return w & 0xFF


# ---------------------------------------------------------------------------
# Data tables — loaded once from the extraction outputs
# ---------------------------------------------------------------------------

_DATA_DIR = Path(__file__).resolve().parent.parent / "content" / "universe"
_PLANET_TYPES: list[dict[str, Any]] | None = None
_STAR_DISTRIBUTIONS: dict[str, list[int]] | None = None


def planet_types() -> list[dict[str, Any]]:
    global _PLANET_TYPES
    if _PLANET_TYPES is None:
        _PLANET_TYPES = json.loads(
            (_DATA_DIR / "uqm_planet_types.json").read_text(encoding="utf-8")
        )
        if len(_PLANET_TYPES) != NUMBER_OF_PLANET_TYPES:
            raise RuntimeError(
                f"expected {NUMBER_OF_PLANET_TYPES} types, got {len(_PLANET_TYPES)}"
            )
    return _PLANET_TYPES


def star_distributions() -> dict[str, list[int]]:
    global _STAR_DISTRIBUTIONS
    if _STAR_DISTRIBUTIONS is None:
        d = json.loads(
            (_DATA_DIR / "uqm_star_distributions.json").read_text(encoding="utf-8")
        )
        _STAR_DISTRIBUTIONS = d["distributions"]
    return _STAR_DISTRIBUTIONS


# ---------------------------------------------------------------------------
# Result type — what the procgen returns per planet
# ---------------------------------------------------------------------------

@dataclass
class UqmPlanetDesc:
    """One planet as generated by FillOrbits. The radius is in UQM
    internal units (SCALE_RADIUS-scaled); convert via the helper below
    when feeding into the existing SystemScene which uses its own units.
    """
    data_index: int                  # 0..58 planet type
    type_name: str                   # human-readable name (e.g. WATER_WORLD)
    type_byte: int                   # bit-packed Type from plandata.c
    color: str                       # "BLUE_BODY" / ... — render hint
    radius: int                      # UQM internal units (orbit radius)
    angle: int                       # 0..63 (NORMALIZE_ANGLE'd)
    x: int                           # COSINE(angle, radius)
    y: int                           # SINE(angle, radius)
    rand_seed: int                   # MAKE_DWORD(x, y) — per-planet seed
    is_gas_giant: bool
    is_large_rocky: bool

    @property
    def orbit_radius_systemunits(self) -> float:
        """Convert UQM radius into system-local units used by SystemScene.

        UQM radii roughly span [256, 7936]. The existing SystemScene
        planet generator outputs orbits in the rough range [60, 600],
        so divide by ~13 to land in a comparable range. This keeps the
        view auto-fit + auto-zoom values sensible.
        """
        return self.radius / 13.0

    def to_legacy_planet(self, index: int, cluster_name: str) -> "Planet":
        """Adapt to the existing Planet dataclass (system/planet.py)
        so the rest of the engine (SystemScene render, PlanetOrbitScene,
        PlanetSurfaceScene) consumes it unchanged.
        """
        from scz.system.planet import PLANET_VISUAL, Planet
        # Map UQM size + color to one of our existing 8 planet-types
        # (GAS_GIANT / TERRESTRIAL / ROCKY / DESERT / ICE / OCEAN /
        # PRIMORDIAL / VOLCANIC). For now: gas giants stay gas giants;
        # everything else routes by color + density.
        legacy_type = _map_uqm_to_legacy_type(self)
        vis = PLANET_VISUAL[legacy_type]
        size = max(
            vis["size_range"][0],
            min(vis["size_range"][1],
                vis["size_range"][0] + (self.radius % (vis["size_range"][1] - vis["size_range"][0] + 1)))
        )
        return Planet(
            index=index,
            name=f"{cluster_name} {_ROMAN[index] if index < len(_ROMAN) else str(index+1)}",
            type=legacy_type,
            orbit_radius=self.orbit_radius_systemunits,
            orbit_angle=(self.angle / FULL_CIRCLE) * 2 * math.pi,
            # Inner planets faster; cap orbit_speed like the existing procgen
            orbit_speed=0.10 / max(1.0, self.orbit_radius_systemunits / 100.0),
            size=size,
            color=vis["color"],
            uqm_type=self.type_name,
        )


_ROMAN = ["I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX"]


def _map_uqm_to_legacy_type(p: UqmPlanetDesc) -> str:
    """Bridge from UQM's 59 types into our existing 8-bucket render
    palette. First-pass heuristic; we can extend the palette to all
    59 later. The key is: same UQM type → same legacy bucket every
    time (deterministic), so the visual is stable per planet."""
    if p.is_gas_giant:
        return "GAS_GIANT"
    # Lookup the full PlanetFrame entry for atmospheric/density hints
    pf = planet_types()[p.data_index]
    # Tectonics + density + atmosphere drive the legacy bucket
    tect = pf["tectonics_val"]
    den = pf["density_val"]
    color = pf["color"]
    atmo = pf["atmosphere_val"]
    name = pf["name"]

    # Special-case a few common identifiable types
    if name == "WATER_WORLD":
        return "OCEAN"
    if name in ("ORGANIC_WORLD", "PRIMORDIAL_WORLD", "EMERALD_WORLD"):
        return "TERRESTRIAL" if atmo >= 1 else "ROCKY"
    if name in ("MAGMA_WORLD", "MAROON_WORLD", "RUBY_WORLD"):
        return "VOLCANIC"
    if name in ("DUST_WORLD", "SELENIC_WORLD"):
        return "DESERT"
    if name in ("SHATTERED_WORLD", "CHONDRITE_WORLD"):
        return "ROCKY"

    # Color-based fallback
    if color == "RED_BODY" and tect >= 80:
        return "VOLCANIC"
    if color == "BLUE_BODY" or color == "CYAN_BODY":
        return "ICE" if atmo == 0 else "OCEAN"
    if color == "ORANGE_BODY" or color == "YELLOW_BODY":
        return "DESERT" if atmo <= 1 else "TERRESTRIAL"
    if color == "GREEN_BODY":
        return "TERRESTRIAL"
    if tect >= 140:
        return "VOLCANIC"
    if atmo == 0:
        return "ROCKY"
    return "TERRESTRIAL"


# ---------------------------------------------------------------------------
# FillOrbits — the heart of the port
# ---------------------------------------------------------------------------

def fill_orbits(
    rng: UqmRandom,
    star_size_idx: int,     # 0=DWARF, 1=GIANT, 2=SUPER_GIANT
    star_color: str,        # "BLUE_BODY" / etc.
    num_planets: int | None = None,
) -> list[UqmPlanetDesc]:
    """Port of orbits.c:FillOrbits. Generates planets (NOT moons) for
    a system. RNG should be pre-seeded with the star's seed.
    """
    types = planet_types()
    dist = star_distributions().get(star_color)
    if dist is None:
        raise ValueError(f"no distribution for star color {star_color}")
    max_planet = NUMBER_OF_PLANET_TYPES   # not generating moons

    # Planet count — UQM's quirky "spin until non-zero" loop
    if num_planets is None:
        while True:
            n = _LOWORD(rng.random()) % (MAX_GENERATED_PLANETS + 1)
            if n != 0:
                num_planets = n
                break

    descs: list[UqmPlanetDesc] = []
    min_rock, min_gas = SUN_MIN_DISTS[star_size_idx]

    for _ in range(num_planets):
        # Pick a planet type — reject-sample via star-color distribution
        while True:
            rand_val = rng.random()
            data_index = _HIBYTE(_LOWORD(rand_val)) % max_planet
            chance = dist[data_index]
            if _LOBYTE(_LOWORD(rand_val)) < chance:
                break

        min_radius = min_rock if data_index < FIRST_GAS_GIANT else min_gas

        # Place at a unique radius (reject any within 1/5 of an existing one)
        while True:
            rand_val = rng.random()
            radius = (
                _LOWORD(rand_val) % (MAX_PLANET_RADIUS - min_radius)
            ) + min_radius
            ok = True
            for prev in descs:
                # UNSCALE_RADIUS(r) = r >> 6; UQM rejects if |prev/5 - this/5| <= 1
                delta = abs((prev.radius >> SCALE_SHIFT) // 5
                            - (radius >> SCALE_SHIFT) // 5)
                if delta <= 1:
                    ok = False
                    break
            if ok:
                break

        # Place angle
        rand_val = rng.random()
        angle = _LOWORD(rand_val) & (FULL_CIRCLE - 1)
        # UQM uses fixed-point COSINE/SINE tables. We approximate with
        # math.cos/sin at this radius — the result is only used as the
        # planet's local coord which feeds rand_seed (next layer); the
        # actual visual orbit comes from radius + angle separately, so
        # this approximation only affects the deeper "moons / surface
        # generation" seed, not the displayed orbits.
        a_rad = (angle / FULL_CIRCLE) * 2 * math.pi
        x = int(math.cos(a_rad) * radius) & 0xFFFFFFFF
        y = int(math.sin(a_rad) * radius) & 0xFFFFFFFF
        rand_seed = ((y & 0xFFFF) << 16) | (x & 0xFFFF)

        pf = types[data_index]
        descs.append(UqmPlanetDesc(
            data_index=data_index,
            type_name=pf["name"],
            type_byte=pf["type_byte"],
            color=pf["color"],
            radius=radius,
            angle=angle,
            x=x, y=y,
            rand_seed=rand_seed,
            is_gas_giant=data_index >= FIRST_GAS_GIANT,
            is_large_rocky=(FIRST_LARGE_ROCKY_WORLD
                            <= data_index <= LAST_LARGE_ROCKY_WORLD),
        ))

    # Sort by ascending radius (innermost → outermost), mirroring UQM
    descs.sort(key=lambda p: p.radius)
    return descs


def generate_uqm_system(star: dict[str, Any]) -> list:
    """End-to-end UQM-faithful generation for one star.

    Takes our internal star dict (must have x, y, type, color,
    cluster_name) and returns a list of Planet dataclass instances
    ready for SystemScene.

    Special-case planet layouts (Mh-Lai, Arilou Outpost, Beta Corvi,
    SOL_PROTO Sol, etc.) are handled separately by SystemScene and
    don't go through this path.
    """
    rng = UqmRandom()
    rng.reseed(get_random_seed_for_star(int(star["x"]), int(star["y"])))
    star_size_idx = STAR_TYPE_TO_IDX.get(star["type"], 0)
    descs = fill_orbits(rng, star_size_idx, star["color"])
    cluster_name = star.get("cluster_name", "?")
    return [d.to_legacy_planet(i, cluster_name) for i, d in enumerate(descs)]
