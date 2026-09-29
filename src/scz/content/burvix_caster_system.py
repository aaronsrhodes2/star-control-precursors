"""The Burvix Caster — Burvixese homeworld + the Be-Loud doctrine
installation.

Canon (per `references/lore/species-sheets.md §10 Burvixese` +
`references/lore/furling-artifacts-and-callforwards.md §The Burv
Caster`):

The Burvixese are four-armed engineers who have committed their entire
species to the **Be-Loud doctrine**: build a planetary-scale broadcaster
(*the Burv Caster*) plus a galaxy-wide network of smaller amplifier
nodes that will broadcast their cognition at unprecedented amplitude.
Their reasoning: the Others harvest minds; if Burvixese cognition is
*the most significant signal in the local cosmos,* the Others will
register them as peers, or at minimum as too costly to harvest, and
pass them over.

**The doctrine fails catastrophically.** Activation flares the cluster
to the Others' attention; the Others arrive faster, not slower; the
Caster keeps firing while its operators die. A small contingent off-
world during activation migrates to Andromeda. The smaller broadcaster
nodes scattered pre-activation survive autonomously — they become the
SC2-canonical Burv Broadcasters that Captain Zelnick-era species use
as comms infrastructure, the carrier-band still faintly broadcasting
the original Burvixese cognitive-signature long after the Burvixese
themselves are gone.

Astronomical canon: Delta Cassiopeiae (3911, 5116) — yellow dwarf,
mid-cluster, the canonical "Burvix Caster" system. Yellow dwarf is
the right thermal environment for a four-armed industrial-civilization
to thrive in; the mid-cluster position makes the broadcast network's
galaxy-wide propagation feasible.
"""

from __future__ import annotations

import math

from scz.system.planet import PLANET_VISUAL, Planet


# The Caster's home planet is at planet index 1 in this system. Arrival
# handler + Caster-installation visibility key on this index.
BURVIX_HOMEWORLD_NAME = "Burvix Caster"


def burvix_caster_planets() -> list[Planet]:
    """Hand-built planet list for the Burvix Caster system.

    Four planets. The homeworld (index 1) is the Caster's planet —
    industrial, heavily-built, the planetary-scale broadcaster's
    primary array embedded in the crust. Pre-activation the world
    is visible from orbit as a *resonator network* — concentric
    construction-rings around the cognitive-amplifier core. Post-
    activation it goes dark.

    The other three planets are atmospheric texture — a scorched
    inner rock (mining base for Caster materials), an outer ice
    giant, and a small ICE outlier.
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
            orbit_angle=(index * 2.5) % (2 * math.pi),
            orbit_speed=orbit_speed,
            size=size,
            color=vis["color"],
        )

    return [
        # Inner mining rock — supplies Caster construction
        _planet(0, "Burvix I",           "ROCKY",       110.0, 0.05),
        # The Burvixese world. Industrial; the Caster installation is
        # the canonical Burvixese megastructure project (planet-scale
        # broadcaster). Slightly oversized for emphasis on first scan.
        _planet(1, BURVIX_HOMEWORLD_NAME, "TERRESTRIAL", 220.0, 0.030, size_override=24),
        # Outer ice giant — never colonized; the Burvixese committed
        # their entire engineering capacity to the Caster, not to
        # ordinary expansion.
        _planet(2, "Burvix III",         "GAS_GIANT",   380.0, 0.014, size_override=48),
        # Small ICE outlier on a long orbit.
        _planet(3, "Burvix IV",          "ICE",         500.0, 0.009),
    ]
