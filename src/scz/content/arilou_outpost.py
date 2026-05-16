"""The Arilou Outpost — a hand-built system on the edge of Furling space.

Arilou are genetic cousins of the Furlings, already partway into Quasi-Space.
For the slice we put their outpost in normal hyperspace at coordinates that
make it reachable from Mh-Lai by autopilot in under two seconds. Crossing
the system boundary returns the player to the same hyperspace coords.

The outpost is a single habitable world (the Sage's seat) around a green
dwarf, with a few uninteresting siblings for navigational texture. The
Sage hails the player from orbit — pressing Y over the homeworld opens
the dialog.
"""

from __future__ import annotations

import math

from scz.system.planet import PLANET_VISUAL, Planet


# Place the outpost across the cluster from Mh-Lai (which sits at 1900,1600).
# At hyperspace PLAYER_SPEED = 1200 units/sec, this is ~1.7 seconds of
# straight-line autopilot — a real journey but harness-friendly.
OUTPOST_X = 3500
OUTPOST_Y = 2400

# The Arilou homeworld is at planet index 1 in this system. The orbit
# scene's "hail" prompt is conditional on the planet name matching.
ARILOU_HOMEWORLD_NAME = "Arilou Sanctuary"


def arilou_outpost_star() -> dict:
    """Star dict, in the same shape as starmap entries."""
    return {
        "x": OUTPOST_X,
        "y": OUTPOST_Y,
        "type": "DWARF_STAR",
        "color": "GREEN_BODY",
        "cluster_name": "Arilou Outpost",
        "defined_name": "ARILOU_OUTPOST",
        "arilou_outpost": True,
    }


def arilou_outpost_planets() -> list[Planet]:
    """The hand-built planet list for the Arilou Outpost system."""
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
            orbit_angle=(index * 2.1) % (2 * math.pi),
            orbit_speed=orbit_speed,
            size=size,
            color=vis["color"],
        )

    return [
        _planet(0, "Outpost I",            "ROCKY",       100.0,  0.05),
        # The Sage's world — terrestrial, mint-tinted in the lore (we use
        # the standard terrestrial palette; Phase 3.5 variation can recolor).
        _planet(1, ARILOU_HOMEWORLD_NAME,  "TERRESTRIAL", 200.0,  0.035, size_override=22),
        _planet(2, "Outpost III",          "ICE",         320.0,  0.02),
        _planet(3, "Outpost IV",           "GAS_GIANT",   450.0,  0.012, size_override=50),
    ]
