"""Procedural planet generation, seeded by star coordinates.

Follows the UQM convention from doc/devel/generate: each solar system's
planet layout is generated deterministically from the star's hyperspace
coordinates as the RNG seed. Same star → same planets forever (until we
change this code).

For the slice MVP this is purely visual — planets don't yet have surfaces,
mineral deposits, or biological data. Those come in Phase 2 / 4.
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass


# Planet type drives appearance + (later) resources/biology
PLANET_TYPES: list[str] = [
    "ROCKY",         # Mercury-like, hot or cold
    "TERRESTRIAL",   # Earth-like, biosphere candidate
    "OCEAN",         # Water-covered
    "ICE",           # Frozen surface
    "DESERT",        # Arid rocky
    "GAS_GIANT",     # Jovian
    "PRIMORDIAL",    # Still forming, hot, hostile
    "VOLCANIC",      # Lava-active
]


# Per-type tint and size range. Visual only for now.
PLANET_VISUAL: dict[str, dict] = {
    "ROCKY":       {"color": (180, 160, 130), "size_range": (10, 22)},
    "TERRESTRIAL": {"color": (90,  180, 130), "size_range": (14, 26)},
    "OCEAN":       {"color": (90,  140, 220), "size_range": (14, 28)},
    "ICE":         {"color": (200, 220, 240), "size_range": (10, 22)},
    "DESERT":      {"color": (220, 180, 100), "size_range": (12, 22)},
    "GAS_GIANT":   {"color": (200, 180, 140), "size_range": (40, 70)},
    "PRIMORDIAL":  {"color": (220, 110, 80),  "size_range": (16, 30)},
    "VOLCANIC":    {"color": (200, 90,  70),  "size_range": (12, 22)},
}


# Star-type biases: hot/blue stars tend to have more primordial/volcanic
# planets; cool/red stars more rocky/ice. Loose, for flavor.
STAR_TYPE_BIAS: dict[str, list[str]] = {
    "BLUE_BODY":  ["PRIMORDIAL", "VOLCANIC", "ROCKY",  "GAS_GIANT", "DESERT"],
    "WHITE_BODY": ["ROCKY",      "DESERT",   "GAS_GIANT", "ICE",    "VOLCANIC"],
    "YELLOW_BODY":["ROCKY",      "TERRESTRIAL", "OCEAN", "GAS_GIANT", "ICE", "DESERT"],
    "GREEN_BODY": ["GAS_GIANT",  "OCEAN",    "TERRESTRIAL", "ICE",   "ROCKY"],
    "ORANGE_BODY":["ROCKY",      "DESERT",   "ICE",     "GAS_GIANT", "TERRESTRIAL"],
    "RED_BODY":   ["ICE",        "ROCKY",    "DESERT",  "GAS_GIANT"],
}


@dataclass
class Planet:
    """A planet in a star system."""

    index: int                  # 0 = innermost
    name: str                   # e.g. "Sol III"
    type: str                   # PLANET_TYPES entry
    orbit_radius: float         # system-local units
    orbit_angle: float          # radians at t=0
    orbit_speed: float          # radians per second (slow)
    size: int                   # render radius in pixels
    color: tuple[int, int, int]

    def position_at(self, t: float) -> tuple[float, float]:
        """Return (x, y) in system-local coords at time t (seconds)."""
        angle = self.orbit_angle + self.orbit_speed * t
        return (
            self.orbit_radius * math.cos(angle),
            self.orbit_radius * math.sin(angle),
        )


# Greek-letter prefixes for naming planets (Roman numerals would be canonical
# for SC2-style; we'll use I-VIII)
ROMAN: list[str] = ["I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX"]


def generate_system(
    star_x: int,
    star_y: int,
    star_type: str,
    star_color: str,
    cluster_name: str,
) -> list[Planet]:
    """Procedurally generate the planet list for a star.

    Deterministic per (star_x, star_y) — same star always yields same planets.
    Closely mirrors UQM's convention: seed by hyperspace coords, generate
    planet count + orbits + properties.
    """
    seed = star_x * 10001 + star_y
    rng = random.Random(seed)

    # Planet count biased by star type
    type_count_range = {
        "SUPER_GIANT_STAR": (1, 4),   # often blown out
        "GIANT_STAR":       (2, 6),
        "DWARF_STAR":       (3, 8),
    }
    lo, hi = type_count_range.get(star_type, (3, 7))
    planet_count = rng.randint(lo, hi)

    bias = STAR_TYPE_BIAS.get(star_color, PLANET_TYPES)

    # First orbit: between 60 and 110 system-units from star
    # (system-units are arbitrary; the SystemScene scales to fit)
    orbit = rng.uniform(60.0, 110.0)
    planets: list[Planet] = []
    for i in range(planet_count):
        # Each subsequent orbit is 1.4× to 2.0× the previous (loose Titius-Bode)
        if i > 0:
            orbit *= rng.uniform(1.4, 2.0)

        # Inner planets favor rocky/primordial; outer planets favor gas-giant/ice
        if i < planet_count // 3:
            # Inner — favor hot types
            inner_types = [t for t in bias if t in {"PRIMORDIAL", "VOLCANIC", "ROCKY", "DESERT"}]
            type_pool = inner_types if inner_types else bias
        elif i > 2 * planet_count // 3:
            # Outer — favor cold / gas
            outer_types = [t for t in bias if t in {"GAS_GIANT", "ICE", "OCEAN"}]
            type_pool = outer_types if outer_types else bias
        else:
            # Middle — full bias range, terrestrial possible
            type_pool = bias

        ptype = rng.choice(type_pool)
        vis = PLANET_VISUAL[ptype]
        size = rng.randint(*vis["size_range"])
        # Random initial orbit angle
        angle = rng.uniform(0.0, 2.0 * math.pi)
        # Inner planets faster; outer slower. Cap to slow visual rotation.
        orbit_speed = 0.10 / max(1.0, orbit / 100.0)

        roman = ROMAN[i] if i < len(ROMAN) else str(i + 1)
        planets.append(
            Planet(
                index=i,
                name=f"{cluster_name} {roman}",
                type=ptype,
                orbit_radius=orbit,
                orbit_angle=angle,
                orbit_speed=orbit_speed,
                size=size,
                color=vis["color"],
            )
        )

    return planets
