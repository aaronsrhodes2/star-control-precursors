"""Beta Corvi — the Slylandro Observers' home system.

Canonical SC2 star at (276, 9810), green giant, defined_name SLYLANDRO.
Hand-built planet list overrides the procgen layout to ensure the
**Slylandro Sky-Vault** (their homeworld) is present at a predictable
index and orbit. From orbit, Y hails the Slylandro Keeper.

Per species-sheets.md §1, Slylandro are gas-bag physiology and live
in the upper troposphere of a gas giant. For slice mechanics the
Sky-Vault is modeled as a TERRESTRIAL world — the player's ship hovers
at the gas-giant's upper atmosphere where the Slylandro drift. Visual
flavor matches the gas-giant register; the type label is a slice-MVP
compromise so PlanetOrbitScene's "deploy lander" still gates cleanly
on type != GAS_GIANT.
"""

from __future__ import annotations

import math

from scz.system.planet import PLANET_VISUAL, Planet


SLYLANDRO_HOMEWORLD_NAME = "Slylandro Sky-Vault"


def beta_corvi_planets() -> list[Planet]:
    """Hand-built planets for Beta Corvi. The Sky-Vault is at index 2."""
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
        _planet(0, "Beta Corvi I",          "ROCKY",      100.0, 0.045),
        _planet(1, "Beta Corvi II",         "DESERT",     180.0, 0.030),
        # Slylandro Sky-Vault — the player hovers at the upper-atmosphere
        # interface where Slylandro drift. TERRESTRIAL classification per
        # the module docstring; visual flavor will lean gas-giant later.
        _planet(2, SLYLANDRO_HOMEWORLD_NAME, "TERRESTRIAL", 280.0, 0.022, size_override=26),
        _planet(3, "Beta Corvi IV",         "GAS_GIANT",  420.0, 0.014, size_override=52),
        _planet(4, "Beta Corvi V",          "ICE",        560.0, 0.010),
    ]
