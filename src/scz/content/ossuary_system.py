"""Ossuary — the Mmrnmhrm Sentinels' homeworld system.

Canon (per references/lore/the-mmrnmhrm-and-chenjesu.md):

The Mmrnmhrm are self-modifying mechanical guardians built by an organic
species — the **First-Makers**, whose name is lost — three to eight
million years ago. The First-Makers built the Mmrnmhrm as planetary
defenders against the Others. The Others arrived. The Mmrnmhrm fought.
Their weapons dissipated like spray hitting fog. The Others ignored the
Mmrnmhrm entirely and killed the First-Makers.

The Mmrnmhrm have continued to operate, alone, since. Their archives
are extensive. They maintain a perfect defensive posture against an
enemy that never noticed them.

Ossuary is the planet. The Mmrnmhrm walk its iron-rich crust among the
ruins of the First-Makers' cities, executing maintenance routines,
adding to the archive, slowly self-improving their cognition. They
receive Furling visitors courteously.

Astronomical canon: red dwarf at Gamma Trianguli (7926, 270), far NE
cluster edge per the slice's `defined_name` tagging. The cluster-edge
placement matches the lore's "deep cut the curious player finds" beat —
players who hit Ossuary have wandered out to the far edge of mapped
space and have been rewarded with a load-bearing canon revelation.
"""

from __future__ import annotations

import math

from scz.system.planet import PLANET_VISUAL, Planet


# The Mmrnmhrm world's display name in the system view + dialog HUD.
# Scene code reads `OSSUARY_HOMEWORLD_NAME` to gate the "you are over
# Ossuary itself" affordance, the same way Arilou Outpost uses
# ARILOU_HOMEWORLD_NAME.
OSSUARY_HOMEWORLD_NAME = "Ossuary"


def ossuary_planets() -> list[Planet]:
    """Hand-built planet list for the Gamma Trianguli / Ossuary system.

    Four planets: a scorched inner rock close to the red dwarf, the
    iron-rich Mmrnmhrm world (Ossuary itself), a silent ice giant, and
    a methane gas-giant on a long orbit. Ossuary sits at index 1 — the
    arrival handler + orbital "hail" affordance read this index for
    the Mmrnmhrm dialog auto-launch.
    """
    def _planet(index, name, ptype, orbit_radius, orbit_speed, size_override=None):
        vis = PLANET_VISUAL[ptype]
        size = size_override if size_override is not None else (
            vis["size_range"][0] + vis["size_range"][1]
        ) // 2
        return Planet(
            index=index,
            name=name,
            type=ptype,
            orbit_radius=orbit_radius,
            orbit_angle=(index * 2.3) % (2 * math.pi),
            orbit_speed=orbit_speed,
            size=size,
            color=vis["color"],
        )

    return [
        # Inner scorched rock — red dwarfs run cool but close orbits
        # still bake. No atmosphere, no Mmrnmhrm presence.
        _planet(0, "Ossuary I",          "ROCKY",    100.0,  0.05),
        # The Mmrnmhrm world. Rocky (iron-rich), primordial, covered
        # in the silent imposing ruins of the First-Makers' vanished
        # civilization. The Mmrnmhrm walk among the ruins maintaining
        # their last orders. Slightly oversized so it reads as the
        # plot-relevant world on first scan.
        _planet(1, OSSUARY_HOMEWORLD_NAME, "ROCKY",  220.0,  0.030, size_override=24),
        # An ice world — quiet, never colonized.
        _planet(2, "Ossuary III",        "ICE",      360.0,  0.018),
        # A methane gas giant on a long orbit, marking the system's
        # outer edge.
        _planet(3, "Ossuary IV",         "GAS_GIANT", 500.0, 0.010, size_override=52),
    ]
