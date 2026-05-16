"""Planet surface hazards — damage the lander, lose the trip haul.

Per Aaron's design (and furling-tech-mechanics canon):
- Landers are remote-piloted drones, not crewed
- Hazards (weather, heat, tectonics, caustic pools, hostile life) can
  damage and destroy the lander
- Losing the lander loses the cargo it had collected on THIS trip
- Building a replacement costs minerals; never grounds the player

This module defines hazard types + per-planet-type profiles. The
PlanetSurfaceScene constructs the hazard list from the planet's seed
and ticks them each frame.

First-pass hazards: `lava` (continuous damage when overlapping) and
`lightning` (periodic high-damage strike). More types (earthquake,
caustic pool, hostile-bio) land as content authoring continues.
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass, field


# Base lander HP. Modules can buff this later (hull / shield additions).
LANDER_HP_BASE = 100.0


# Replacement cost when the lander is destroyed. Paid out of game.cargo
# at lift-off / destruction. Modest by design — death stings but doesn't
# grind.
LANDER_REPLACEMENT_COST: dict[str, int] = {"COMMON": 30}


@dataclass
class Hazard:
    """A single surface hazard. Position + radius + damage profile."""
    type: str                    # "lava" | "lightning" | "earthquake" | ...
    x: float                     # 0..1 surface-local coords
    y: float
    radius: float                # 0..1 surface-local radius
    damage_per_sec: float        # while active and lander overlaps
    color: tuple[int, int, int]
    # Periodic activation. period == 0 means always-on (lava).
    # Otherwise: hazard is active for (period * duty_cycle) seconds,
    # then inactive for the rest of the period (lightning).
    period: float = 0.0
    duty_cycle: float = 1.0
    phase: float = 0.0           # offset so multiple hazards don't all pulse together

    def is_active(self, t: float) -> bool:
        if self.period == 0.0:
            return True
        within_period = (t + self.phase) % self.period
        return within_period < self.period * self.duty_cycle


# Per-planet-type hazard profile: a list of (hazard_type, count_range,
# radius_range, dmg_per_sec, color, period, duty_cycle) tuples that the
# generator uses.
HazardProfile = list[dict]

PROFILES: dict[str, HazardProfile] = {
    "ROCKY": [
        {
            "type": "earthquake", "count": (1, 3),
            "radius": (0.06, 0.10), "dmg": 15.0,
            "color": (180, 130, 80),
            "period": 4.0, "duty_cycle": 0.35,
        },
    ],
    "DESERT": [
        {
            "type": "heat", "count": (2, 4),
            "radius": (0.08, 0.14), "dmg": 8.0,
            "color": (240, 160, 60),
            "period": 0.0, "duty_cycle": 1.0,
        },
    ],
    "ICE": [
        {
            "type": "crack", "count": (1, 3),
            "radius": (0.05, 0.09), "dmg": 22.0,
            "color": (160, 200, 240),
            "period": 5.0, "duty_cycle": 0.25,
        },
    ],
    "PRIMORDIAL": [
        {
            "type": "lava", "count": (3, 6),
            "radius": (0.07, 0.13), "dmg": 25.0,
            "color": (220, 80, 40),
            "period": 0.0, "duty_cycle": 1.0,
        },
    ],
    "VOLCANIC": [
        {
            "type": "lava", "count": (4, 7),
            "radius": (0.06, 0.12), "dmg": 30.0,
            "color": (220, 80, 40),
            "period": 0.0, "duty_cycle": 1.0,
        },
        {
            "type": "lightning", "count": (1, 2),
            "radius": (0.04, 0.07), "dmg": 40.0,
            "color": (255, 240, 180),
            "period": 3.0, "duty_cycle": 0.15,
        },
    ],
    "TERRESTRIAL": [
        {
            "type": "lightning", "count": (1, 2),
            "radius": (0.04, 0.06), "dmg": 18.0,
            "color": (255, 240, 180),
            "period": 4.0, "duty_cycle": 0.12,
        },
    ],
    "OCEAN": [
        {
            "type": "thermal_vent", "count": (1, 2),
            "radius": (0.05, 0.08), "dmg": 12.0,
            "color": (140, 200, 240),
            "period": 6.0, "duty_cycle": 0.3,
        },
    ],
}


def generate_hazards(
    planet_seed: tuple[int, int, int],
    planet_type: str,
    planet_name: str = "",
) -> list[Hazard]:
    """Generate the hazard list for a planet. Deterministic per seed.

    Furlmart is canonically a safe warehouse moon — explicitly hazard-
    free regardless of its planet_type. The tutorial flow assumes it.
    """
    if planet_name == "Furlmart":
        return []
    profile = PROFILES.get(planet_type)
    if not profile:
        return []
    rng = random.Random(
        planet_seed[0] * 100003 + planet_seed[1] * 11 + planet_seed[2] * 3 + 9001
    )
    out: list[Hazard] = []
    for entry in profile:
        count = rng.randint(*entry["count"])
        for _ in range(count):
            x = rng.uniform(0.10, 0.90)
            y = rng.uniform(0.10, 0.90)
            radius = rng.uniform(*entry["radius"])
            phase = rng.uniform(0.0, entry.get("period", 1.0) or 1.0)
            out.append(Hazard(
                type=entry["type"],
                x=x, y=y, radius=radius,
                damage_per_sec=entry["dmg"],
                color=entry["color"],
                period=entry["period"],
                duty_cycle=entry["duty_cycle"],
                phase=phase,
            ))
    return out
