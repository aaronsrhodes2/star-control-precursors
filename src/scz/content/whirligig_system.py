"""Whirligig — the Lemmkin homeworld system.

Canon (per `references/lore/species-the-lemmkin.md`):

The Lemmkin are fast-breeding, eclectic-research-temperament archivists
who have *chosen no survival strategy* in the face of the Others.
Their alternative: spend the remaining time *learning everything they
can*. They will be Eliminated; their archives may outlive them.

Whirligig is a densely-forested terrestrial world with **rapid axial
rotation (~6-hour day)** — the Lemmkin named the planet themselves
after the rotation. Forest canopy is the primary habitat; cities are
built into the upper branches of kilometer-tall trees.

Astronomical canon: Beta Crucis (5499, 6669) — green dwarf, mid-
southern slice, ample habitable-zone for forest biomes. Isolated from
the other tagged systems; next-closest defined-name star is Mycon
Hive ~4500 units away.
"""

from __future__ import annotations

import math

from scz.system.planet import PLANET_VISUAL, Planet


# The Lemmkin homeworld is at planet index 1 in this system. Arrival
# handler reads this index for the contemplation-greet auto-launch.
WHIRLIGIG_HOMEWORLD_NAME = "Whirligig"


def whirligig_planets() -> list[Planet]:
    """Hand-built planet list for the Beta Crucis / Whirligig system.

    Three planets — the Lemmkin have not expanded beyond Whirligig
    (they don't have the spare cycles for it; archive work consumes
    every adult's day). An inner scorched rock, **Whirligig** (the
    forested home), and a small outer ICE.
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
            orbit_angle=(index * 1.9) % (2 * math.pi),
            orbit_speed=orbit_speed,
            size=size,
            color=vis["color"],
        )

    return [
        _planet(0, "Beta Crucis I",         "ROCKY",       110.0, 0.05),
        # Whirligig — the Lemmkin homeworld. Densely forested terrestrial;
        # kilometer-tall trees; cities in the upper canopy. Slightly
        # oversized for emphasis on first scan.
        _planet(1, WHIRLIGIG_HOMEWORLD_NAME, "TERRESTRIAL", 220.0, 0.030, size_override=22),
        # Outer ice outlier on a long orbit.
        _planet(2, "Beta Crucis III",        "ICE",         420.0, 0.012),
    ]
