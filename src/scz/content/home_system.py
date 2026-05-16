"""The Mh-Lai home system — hand-built, not procgen.

Canonical layout per references/lore/tutorial-arc.md: a yellow-orange dwarf
star with a small handful of planets, including:

  - Mh-Lai (terrestrial blue-green) — the Furling home, "the Hearth"
  - A gas giant with Furlmart, a small warehouse moon, in close orbit
  - A couple of background planets to make the system feel real

Mh-Lai does NOT appear on the SC2 starmap (canon: Furlings unmade it
before the Migration sealed). We give it synthetic universe coordinates
that don't collide with any SC2 star, so leaving the system drops the
player into a defensible region of hyperspace.
"""

from __future__ import annotations

import math

from scz.system.planet import PLANET_VISUAL, Planet


# Universe coordinates for Mh-Lai — chosen to sit in an empty patch of
# the SC2 starmap, near Sol but not on top of it. The Hyperspace scene
# uses this when the player leaves the home system.
HOME_X = 1900
HOME_Y = 1600


def home_star() -> dict:
    """The Mh-Lai star dict, in the same shape as starmap entries."""
    return {
        "x": HOME_X,
        "y": HOME_Y,
        "type": "DWARF_STAR",
        "color": "YELLOW_BODY",
        "cluster_name": "Mh-Lai",
        "defined_name": "MH_LAI_HOME",
        "home_system": True,
    }


def home_planets() -> list[Planet]:
    """The hand-built planet list for Mh-Lai."""
    def _planet(index, name, ptype, orbit_radius, orbit_speed, size_override=None):
        vis = PLANET_VISUAL[ptype]
        size = size_override if size_override is not None else (vis["size_range"][0] + vis["size_range"][1]) // 2
        return Planet(
            index=index,
            name=name,
            type=ptype,
            orbit_radius=orbit_radius,
            orbit_angle=(index * 1.7) % (2 * math.pi),
            orbit_speed=orbit_speed,
            size=size,
            color=vis["color"],
        )

    return [
        _planet(0, "Mh-Lai I",  "ROCKY",       80.0,  0.06),
        _planet(1, "Mh-Lai II", "DESERT",     140.0,  0.045),
        # Mh-Lai itself — the Hearth
        _planet(2, "Mh-Lai",    "TERRESTRIAL", 220.0,  0.030, size_override=24),
        # The big sibling — gas giant. Furlmart is conceptually its moon.
        _planet(3, "Mh-Lai IV", "GAS_GIANT",   340.0,  0.020, size_override=55),
        # Furlmart — small warehouse rock orbiting just outside the gas
        # giant. We model it as a separate planet (no moons yet); the
        # orbit_radius is just past the giant so it looks like a moon.
        _planet(4, "Furlmart",  "ROCKY",       380.0,  0.020, size_override=12),
        _planet(5, "Mh-Lai VI", "ICE",         500.0,  0.014),
    ]
