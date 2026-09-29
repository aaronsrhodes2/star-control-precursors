"""Planet surface life forms — moving fauna the lander catches.

Canon (Aaron, 2026-05-18): "We DO need to seed life on the planets.
The old SC2 had it seeded and it moved and you had to catch it. Same
here but they can't damage us unless it's a flying creature."

Direct port of SC2's moving-creature pickup mechanic, with one
canonical safety adjustment: **ground-bound creatures CANNOT damage
the lander; only flying creatures can.**

Each LifeForm has:
- a position on the surface (0..1 normalized — same coords as Deposit)
- a velocity (movement vector; updated per frame by `step_motion`)
- a TIER — ground / flying — that gates damage
- a temperament — flee / wander / curious — that drives movement AI
- a BIO value — yield in BIO cargo on capture
- a flying-damage stat — only used when tier == "flying"

Generation is per (planet_id, planet_type) deterministic. Different
planet biomes seed different fauna mixes:

- TERRESTRIAL : abundant ground fauna; one or two flying scouts
- OCEAN       : ground swimmers (treated as ground), few flying
- ROCKY       : sparse ground; occasional flying predator
- DESERT      : ground burrowers; flying scavengers
- ICE         : cold-adapted ground; no flying
- VOLCANIC    : sparse heat-tolerant ground; flying ash-skimmers
- PRIMORDIAL  : sparse; one signature life form (early-form ammonites)
- GAS_GIANT   : no surface, no life (lander can't land anyway)

The movement AI is intentionally minimal — see step_motion for the
three temperaments. The point is "catch the bouncing creature";
nothing more elaborate than that is needed for the slice.
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass


# ---------------------------------------------------------------------------
# Public constants — tiers, temperaments, biome configs
# ---------------------------------------------------------------------------

TIER_GROUND = "ground"
TIER_FLYING = "flying"

TEMP_FLEE = "flee"        # accelerates away from the lander
TEMP_WANDER = "wander"    # ignores the lander; brownian motion
TEMP_CURIOUS = "curious"  # weakly approaches the lander


# Visual config per tier — color + size (lander screen pixels at base).
# Ground critters are warm-tone organic dots; flying are paler with a
# trailing wing-blur (rendered in the scene layer).
LIFE_VISUAL: dict[str, dict] = {
    TIER_GROUND: {"color": (200, 220, 120), "size": 6},   # warm green-yellow
    TIER_FLYING: {"color": (240, 200, 240), "size": 7},   # pale violet-pink
}


# Per-planet-type spawn distribution. Each entry: {tier: (min, max)}
# Total count per planet is the sum across tiers. Empty dict → no life.
PLANET_LIFE: dict[str, dict[str, tuple[int, int]]] = {
    "TERRESTRIAL": {TIER_GROUND: (4, 7), TIER_FLYING: (1, 2)},
    "OCEAN":       {TIER_GROUND: (3, 6), TIER_FLYING: (0, 1)},
    "ROCKY":       {TIER_GROUND: (1, 3), TIER_FLYING: (0, 1)},
    "DESERT":      {TIER_GROUND: (2, 4), TIER_FLYING: (0, 2)},
    "ICE":         {TIER_GROUND: (1, 3), TIER_FLYING: (0, 0)},
    "GAS_GIANT":   {},
    "PRIMORDIAL":  {TIER_GROUND: (1, 2), TIER_FLYING: (0, 0)},
    "VOLCANIC":    {TIER_GROUND: (0, 2), TIER_FLYING: (1, 2)},
}


# Per-tier max speed (surface-normalized units / sec). Ground fauna is
# *slower* than the lander's base LANDER_SPEED (0.20) so the player can
# always close — that's the canon: ground fauna is safe BY DEFINITION
# because the lander can outrun it. Flying fauna is fast enough to
# pose a chase challenge.
SPEED_BY_TIER: dict[str, float] = {
    TIER_GROUND: 0.10,
    TIER_FLYING: 0.22,
}


# Per-tier contact-damage (HP/sec while inside the lander's collision
# radius). Ground is 0 by canon — flying is the only fauna threat.
DAMAGE_PER_SEC_BY_TIER: dict[str, float] = {
    TIER_GROUND: 0.0,
    TIER_FLYING: 1.5,
}


# Catch radius (surface-local). When a life form enters this distance
# of the lander, it's captured (tractor pulls it in same as a deposit).
# Slightly larger than the deposit tractor radius because life moves —
# without a wider hitbox, capture would be too twitchy.
CATCH_RADIUS_BASE = 0.040


# ---------------------------------------------------------------------------
# Dataclass
# ---------------------------------------------------------------------------

@dataclass
class LifeForm:
    """A single mobile fauna creature on a planet's surface."""

    tier: str                # TIER_GROUND or TIER_FLYING
    temperament: str         # TEMP_FLEE / TEMP_WANDER / TEMP_CURIOUS
    x: float                 # surface-local coords (0..1)
    y: float                 # surface-local coords (0..1)
    vx: float                # velocity x (units/sec)
    vy: float                # velocity y (units/sec)
    bio_value: int           # yield in BIO cargo on capture (1..6)
    caught: bool = False
    # Per-frame phase for wander brownian-noise — gives each creature
    # an independent random-walk seed so they don't all jitter in sync.
    _phase: float = 0.0


# ---------------------------------------------------------------------------
# Generation
# ---------------------------------------------------------------------------

def generate_life_forms(
    planet_id: tuple[int, int, int],
    planet_type: str,
) -> list[LifeForm]:
    """Generate the list of life forms for a planet.

    Deterministic per (planet_id, planet_type) — replays of the same
    planet always produce the same fauna layout. Independent RNG seed
    from `generate_deposits` so a planet's fauna is distinct from its
    mineral roll.
    """
    if planet_type not in PLANET_LIFE or not PLANET_LIFE[planet_type]:
        return []

    # Distinct seed from deposits (which uses *100001+*7+ pattern). Add
    # a constant to fork the RNG stream.
    seed = planet_id[0] * 100001 + planet_id[1] * 7 + planet_id[2] + 31337
    rng = random.Random(seed)
    life: list[LifeForm] = []

    for tier, (lo, hi) in PLANET_LIFE[planet_type].items():
        count = rng.randint(lo, hi)
        max_speed = SPEED_BY_TIER[tier]
        for _ in range(count):
            x = rng.uniform(0.08, 0.92)
            y = rng.uniform(0.08, 0.92)
            # Initial velocity — small random direction at fraction of max.
            angle = rng.uniform(0.0, 2.0 * math.pi)
            speed = rng.uniform(0.3, 0.7) * max_speed
            vx = math.cos(angle) * speed
            vy = math.sin(angle) * speed
            temperament = rng.choice(
                (TEMP_FLEE, TEMP_WANDER, TEMP_CURIOUS)
                if tier == TIER_GROUND
                # Flying fauna doesn't flee — flying = the threat tier;
                # it's curious-or-wandering (curious = attacking pattern).
                else (TEMP_WANDER, TEMP_CURIOUS)
            )
            bio_value = rng.randint(1, 4) if tier == TIER_GROUND else rng.randint(2, 6)
            phase = rng.uniform(0.0, 2.0 * math.pi)
            life.append(LifeForm(
                tier=tier, temperament=temperament,
                x=x, y=y, vx=vx, vy=vy,
                bio_value=bio_value, _phase=phase,
            ))

    return life


# ---------------------------------------------------------------------------
# Per-frame movement AI
# ---------------------------------------------------------------------------

# How quickly the wander temperament reorients (radians/sec of drift).
_WANDER_TURN_RATE = 0.7
# Force scale per temperament when reacting to the lander.
_FLEE_ACCEL = 0.30
_CURIOUS_ACCEL = 0.18
# Detection radius — fauna only reacts to the lander within this radius.
# Outside it, they wander.
_REACT_RADIUS = 0.20


def step_motion(
    life: list[LifeForm],
    lander_x: float,
    lander_y: float,
    dt: float,
) -> None:
    """Update each non-caught life form's position. Mutates in place.

    Three temperaments:
      - FLEE: accelerates AWAY from the lander when in detection range
      - CURIOUS: accelerates TOWARD the lander when in detection range
        (flying-curious is the "swooping attacker" pattern)
      - WANDER: ignores the lander; brownian-noise heading drift

    Positions are clamped to [0.02, 0.98] so creatures bounce off the
    surface edges rather than walking off-screen. Velocity is clamped
    to the tier's max speed.
    """
    for lf in life:
        if lf.caught:
            continue

        max_speed = SPEED_BY_TIER[lf.tier]

        # Vector from creature to lander
        dx = lander_x - lf.x
        dy = lander_y - lf.y
        dist = math.hypot(dx, dy)

        # Apply temperament force
        if lf.temperament == TEMP_FLEE and dist > 1e-6 and dist <= _REACT_RADIUS:
            # Away from lander
            inv = 1.0 / dist
            lf.vx -= dx * inv * _FLEE_ACCEL * dt
            lf.vy -= dy * inv * _FLEE_ACCEL * dt
        elif lf.temperament == TEMP_CURIOUS and dist > 1e-6 and dist <= _REACT_RADIUS:
            # Toward lander
            inv = 1.0 / dist
            lf.vx += dx * inv * _CURIOUS_ACCEL * dt
            lf.vy += dy * inv * _CURIOUS_ACCEL * dt
        else:
            # Wander — slight heading rotation based on per-creature phase
            lf._phase += _WANDER_TURN_RATE * dt
            # Add a small noise to the velocity
            lf.vx += math.cos(lf._phase) * 0.04 * dt
            lf.vy += math.sin(lf._phase * 1.3) * 0.04 * dt

        # Clamp velocity magnitude to tier max
        v = math.hypot(lf.vx, lf.vy)
        if v > max_speed:
            scale = max_speed / v
            lf.vx *= scale
            lf.vy *= scale

        # Step position
        lf.x += lf.vx * dt
        lf.y += lf.vy * dt

        # Bounce off surface edges (keep within [0.02, 0.98])
        if lf.x < 0.02:
            lf.x = 0.02
            lf.vx = abs(lf.vx)
        elif lf.x > 0.98:
            lf.x = 0.98
            lf.vx = -abs(lf.vx)
        if lf.y < 0.02:
            lf.y = 0.02
            lf.vy = abs(lf.vy)
        elif lf.y > 0.98:
            lf.y = 0.98
            lf.vy = -abs(lf.vy)
