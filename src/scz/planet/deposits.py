"""Resource deposits on a planet's surface.

Deterministic per (planet_id, planet_type) seed. Each deposit has a type,
a value, and a position on the surface. Collection is by lander contact.

MVP resource categories (simpler than SC2's full element table — we can
expand later):
- COMMON     : silicate/iron/base metal — always present, low value
- USEFUL     : the rare elements Rainbow seeding needs — medium value
- BIO        : biological-data nodes — value scales with planet biome
- ENERGY     : artifact / power source — rare, high value

Planet type biases what's available:
- TERRESTRIAL  → high bio, medium common, low energy
- OCEAN        → high bio, no useful (covered)
- ROCKY        → high common, medium useful, no bio
- DESERT       → medium common, low bio
- ICE          → low everything but occasional rare useful
- GAS_GIANT    → no surface deposits at all (the lander can't land — handled in scene)
- PRIMORDIAL   → medium useful, high energy, no bio (too hot)
- VOLCANIC     → high common, medium useful, high energy, no bio
"""

from __future__ import annotations

import random
from dataclasses import dataclass


RESOURCE_TYPES: list[str] = ["COMMON", "USEFUL", "BIO", "ENERGY"]


RESOURCE_VISUAL: dict[str, dict] = {
    "COMMON":  {"color": (180, 180, 180), "size": 5},   # silver-gray
    "USEFUL":  {"color": (180, 130, 220), "size": 6},   # violet
    "BIO":     {"color": (120, 230, 130), "size": 6},   # green
    "ENERGY":  {"color": (255, 220, 100), "size": 7},   # gold
    # Quest-item "deposits" — special pickups that aren't real resources.
    # They sit on the surface visually like a deposit and the tractor
    # beam collects them, but PlanetSurfaceScene routes them to game
    # flags / uninstalled_modules instead of game.cargo.
    "PACKAGE_SCANNER_MK3": {"color": (255, 230, 140), "size": 10},  # bright gold
}


# Per-planet-type deposit distribution: (count_range_per_type)
# Format: planet_type -> {resource_type: (min_count, max_count)}
PLANET_DEPOSITS: dict[str, dict[str, tuple[int, int]]] = {
    "TERRESTRIAL": {"COMMON": (3, 6), "USEFUL": (1, 3), "BIO": (6, 10), "ENERGY": (0, 1)},
    "OCEAN":       {"COMMON": (2, 4), "USEFUL": (0, 0), "BIO": (8, 12), "ENERGY": (0, 1)},
    "ROCKY":       {"COMMON": (8, 14), "USEFUL": (2, 5), "BIO": (0, 0), "ENERGY": (0, 1)},
    "DESERT":      {"COMMON": (4, 8), "USEFUL": (1, 3), "BIO": (0, 2), "ENERGY": (0, 1)},
    "ICE":         {"COMMON": (2, 4), "USEFUL": (1, 4), "BIO": (0, 1), "ENERGY": (0, 0)},
    "GAS_GIANT":   {},  # no surface, lander can't land
    "PRIMORDIAL":  {"COMMON": (3, 6), "USEFUL": (2, 5), "BIO": (0, 0), "ENERGY": (3, 6)},
    "VOLCANIC":    {"COMMON": (6, 10), "USEFUL": (2, 4), "BIO": (0, 0), "ENERGY": (2, 5)},
}


@dataclass
class Deposit:
    """A single resource node on a planet's surface."""

    type: str          # one of RESOURCE_TYPES
    x: float           # surface-local coords (0..1 normalized)
    y: float           # surface-local coords (0..1 normalized)
    value: int         # how many units this deposit yields when collected
    collected: bool = False


def generate_deposits(planet_id: tuple[int, int, int], planet_type: str) -> list[Deposit]:
    """Generate the list of deposits for a planet.

    planet_id: (star_x, star_y, planet_index) — unique per planet, used as RNG seed.
    Returns an empty list for GAS_GIANT (lander can't land).
    """
    if planet_type not in PLANET_DEPOSITS or not PLANET_DEPOSITS[planet_type]:
        return []

    seed = planet_id[0] * 100001 + planet_id[1] * 7 + planet_id[2]
    rng = random.Random(seed)
    deposits: list[Deposit] = []

    for rtype, (lo, hi) in PLANET_DEPOSITS[planet_type].items():
        count = rng.randint(lo, hi)
        for _ in range(count):
            # Distribute across the surface; avoid the very edges
            x = rng.uniform(0.05, 0.95)
            y = rng.uniform(0.05, 0.95)
            # Value scales with type — bigger numbers for rarer resources
            if rtype == "COMMON":
                value = rng.randint(1, 3)
            elif rtype == "USEFUL":
                value = rng.randint(2, 5)
            elif rtype == "BIO":
                value = rng.randint(1, 4)
            else:  # ENERGY
                value = rng.randint(5, 10)
            deposits.append(Deposit(type=rtype, x=x, y=y, value=value))

    return deposits
