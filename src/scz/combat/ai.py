"""Static combat AI — the Layer 1 decision function from combat-ai.md.

Reads ship + enemy state, returns action bits (thrust, turn-direction,
fire). Same code path flies any ship — per-ship behavior comes from
the ship's `ai_style` field (brawler / kiter / circler) and from its
stats (turning rate, range, etc.).

Per the doctrine in `references/lore/combat-ai.md`:
- Non-shielded ships avoid camping at long range against a regenerating
  enemy — they need to *close* and burst-damage during the shield gap.
- Shielded ships value patience; they want their shields up before
  engaging, so they will retreat briefly when shields are low.

No personality variation here — that's Phase 4+. The same decision
function is used by player auto-fight and by enemy AI.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from scz.combat.scene import ShipState


@dataclass
class AIAction:
    """One frame's worth of intended action. Combat scene applies these."""
    thrust: bool       # True = accelerate along current heading
    turn_dir: int      # -1, 0, +1 (left, none, right)
    fire_primary: bool


def decide(my: "ShipState", enemy: "ShipState") -> AIAction:
    """Static decision function. Same code for every ship.

    Steps:
    1. Compute angle to enemy.
    2. Turn to face them (the cost of turning is the ship's turn_rate).
    3. Decide engagement distance from style + shield state.
    4. Thrust forward unless we're already past optimal distance.
    5. Fire if facing the enemy and in range and we have energy.
    """
    cls = my.cls

    # --- Geometry ---
    dx = enemy.x - my.x
    dy = enemy.y - my.y
    dist = math.hypot(dx, dy) or 0.001
    # Heading from current position to enemy
    target_heading = math.atan2(dx, -dy)   # same convention as scenes (0 = up)
    # Shortest angular delta
    delta = (target_heading - my.heading + math.pi) % (2 * math.pi) - math.pi

    # --- Engagement distance preference ---
    base_range = cls.primary_range
    if cls.ai_style == "brawler":
        # Want to be at 40-60% of range — close fight
        ideal_dist = base_range * 0.5
    elif cls.ai_style == "kiter":
        # Stay at 80-95% of range — far enough to back out
        ideal_dist = base_range * 0.85
    else:  # circler (default)
        ideal_dist = base_range * 0.7

    # --- Shield-doctrine adjustment ---
    if cls.shield_max > 0:
        # We have shields. Slight retreat-preference when shields are low,
        # so they can regen.
        shield_frac = my.shield / cls.shield_max if cls.shield_max else 1.0
        if shield_frac < 0.25 and my.shield_regen_cooldown <= 0:
            # Shields just dropped low. Back off to let them regen.
            ideal_dist = base_range * 1.05
    else:
        # No shields — we bleed one-way. If the enemy has shields and is
        # regenerating, close to deny the regen window.
        if enemy.cls.shield_max > 0 and enemy.shield_regen_cooldown <= 0:
            ideal_dist = max(60.0, base_range * 0.4)

    # --- Decide turn ---
    if abs(delta) > 0.05:
        turn_dir = 1 if delta > 0 else -1
    else:
        turn_dir = 0

    # --- Decide thrust ---
    # If we're already roughly facing the target AND we want to close,
    # thrust. If we want to back off, thrust *away* (which means we'd
    # need to turn around first — handled by the simple delta logic
    # above. For "back off" the brain says "ideal_dist > current_dist",
    # which here means: don't thrust forward.).
    facing_target = abs(delta) < math.radians(35)
    want_to_close = dist > ideal_dist
    thrust = facing_target and want_to_close

    # --- Decide fire ---
    fire = False
    in_range = dist <= cls.primary_range * 0.98
    facing_for_shot = abs(delta) < math.radians(8)
    has_energy = my.energy >= cls.primary_energy
    cool = my.primary_cooldown <= 0
    if in_range and facing_for_shot and has_energy and cool:
        fire = True

    return AIAction(thrust=thrust, turn_dir=turn_dir, fire_primary=fire)
