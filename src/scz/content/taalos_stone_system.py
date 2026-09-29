"""Taalo's Stone — the Taalo Mountain-Range Sentience's homeworld system.

Canon (per `references/lore/species-sheets.md §9 Taalo` +
`references/lore/furling-artifacts-and-callforwards.md §Taalo Shield`):

The Taalo are silicon-based "rock-like" sentients whose body is a
**single ~2,000 km mountain range** on a high-silicate continental
world. Individuals are mobile fragments of the mountain — separate
enough to walk and converse, embedded enough that the mountain *is*
the species. They cannot leave the planet (their metabolism depends
on the local silicate-biological ecosystem; transplantation kills a
fragment within months) and they cannot be evacuated.

In our era they are alive but **doomed**. The Furlings have known them
for ~5,000 years. The Taalo are building the **Taalo Shield** — a
planetary-scale defensive barrier intended to block the Others from
reaching their world. The Shield will not hold. The Taalo will be
consumed in the Culling regardless of any Steward intervention.

The Steward who arrives in the slice is the **fourth Furling Steward**
to visit this ridge in the friendship's five-thousand-year history.
Their work with the Taalo is repeated visits across the slice;
contribution choices accumulate; the Shield activates late; the
Others arrive; the Shield fails; the Taalo go quiet.

**The bodies calcify into ordinary rock within decades**. From orbit,
the extinct Taalo civilization is invisible — the homeworld reads as a
normal silicate-rich rocky planet with an unusual long mountain range
and some old industrial-looking structures (the inert Shield
generators) embedded in the flanks. This is the SC2 canon-explanation
for why the Taalo's *bodies* are not mentioned in SC2 lore; only their
Shield is recovered.

Astronomical canon: synthetic dwarf star at **(700, 4800)** per slice
canon — no SC2-era star fits the spec precisely, and Taalo's Stone is
*unique to our era* anyway (the world does not appear on SC2 maps
because its mountain has weathered into unremarkable rock by then).
Red dwarf, warm, silicate-rich, geothermally active — the right kind
of stellar environment for a silicon-based ecosystem.
"""

from __future__ import annotations

import math

from scz.system.planet import PLANET_VISUAL, Planet


# Universe coordinates for Taalo's Stone — synthetic, per slice canon.
TAALOS_STONE_X = 700
TAALOS_STONE_Y = 4800

# The Taalo homeworld is at planet index 1 in this system. Arrival
# handler + dialog auto-launch read this index for the Mountain-side
# affordance. Naming follows the canon: the system is "Taalo's Stone";
# the homeworld is "Taalo's Stone II" (the second planet, the
# continental high-silicate world that hosts the Mountain).
TAALO_HOMEWORLD_NAME = "Taalo's Stone II"


def taalos_stone_star() -> dict:
    """Star dict, same shape as starmap entries. Appended to the
    starmap's stars list at load time (parallel to home_star() and
    arilou_outpost_star()).

    Red dwarf, warm and silicate-rich — the canonical environment a
    silicon mountain-substrate consciousness can thrive in. SC2
    archaeology eventually labels this system Delta Vulpeculae in their
    own catalog; the canonical naming for our era is "Taalo's Stone"
    per the species' own preferred name for their home.
    """
    return {
        "x": TAALOS_STONE_X,
        "y": TAALOS_STONE_Y,
        "type": "DWARF_STAR",
        "color": "RED_BODY",
        "cluster_name": "Taalo's Stone",
        "defined_name": "TAALOS_STONE",
        "taalos_stone": True,
    }


def taalos_stone_planets() -> list[Planet]:
    """Hand-built planet list for the Taalo's Stone system.

    Four planets, sparse — the system is a quiet single-star setup.
    Taalo's Stone II at index 1 is the Mountain's home; the other
    three are atmospheric texture (an inner scorched rock, an outer
    ice giant, a small icy outlier). The Mountain-range's 8-12 km
    peaks and 2,000 km span are visible from orbit as an unusually
    long single arc across one continent.
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
            orbit_angle=(index * 1.7) % (2 * math.pi),
            orbit_speed=orbit_speed,
            size=size,
            color=vis["color"],
        )

    return [
        # Scorched inner rock — no atmosphere, no life. Mineral-bright.
        _planet(0, "Taalo's Stone I",       "ROCKY",     110.0, 0.05),
        # The Mountain's world — high-silicate continental planet,
        # canonical home of the Taalo species. Slightly oversized so
        # it reads as the system's plot-relevant target on first scan;
        # mountain-range arc would be visible from orbit at high zoom
        # (future renderer detail; for now standard rocky sprite).
        _planet(1, TAALO_HOMEWORLD_NAME,    "ROCKY",     230.0, 0.030, size_override=26),
        # Outer ice giant — never colonized; deep cold.
        _planet(2, "Taalo's Stone III",     "GAS_GIANT", 380.0, 0.014, size_override=48),
        # Small icy outlier on a long orbit.
        _planet(3, "Taalo's Stone IV",      "ICE",       520.0, 0.009),
    ]
