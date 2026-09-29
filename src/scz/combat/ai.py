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

**Tuning history** (see tools/sim_combat.py):
- 2026-05-17: Added projectile-speed-aware target leading. Slow-projectile
  ships (proto_ur_quan @ 600u/s, arilou_skiff @ 700u/s, melnorme @ 400u/s)
  were missing ~95% of shots against moving targets; with leading they
  hit much more reliably, narrowing the gap with hitscan ships
  (furling_scout, cleanser_cruiser, defender_vessel @ 2400u/s).
- 2026-05-17: Press-the-attack mode — when shields are healthy and the
  enemy's shields are dropping, close to point-blank (40% of range)
  instead of parking at ideal_dist. Fixes the disengage-stalemate
  where two shielded ships orbit at long range forever.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from scz.combat.scene import ShipState


# Arena dimensions — re-stated here (rather than imported from scene)
# to keep ai.py free of a circular dependency. Must match scene.py's
# ARENA_W / ARENA_H exactly; the toroidal wrap math breaks if these
# drift. If the arena size ever needs to be runtime-configurable, this
# is the first thing to refactor.
_ARENA_W = 1600.0
_ARENA_H = 1000.0

# Central planet anchor (must match scene.py's PLANET_*).
_PLANET_X = _ARENA_W / 2
_PLANET_Y = _ARENA_H / 2
_PLANET_RADIUS = 70.0
# How close (in radii) we want to stay from the planet's surface
# during routine flying. Triggers an avoidance bias if we're inside
# this buffer + still approaching.
_PLANET_AVOID_BUFFER = 1.4


def _line_blocked_by_planet(
    sx: float, sy: float, ex: float, ey: float,
    planet_x: float, planet_y: float, planet_r: float,
) -> bool:
    """True iff the straight line from (sx,sy) to (ex,ey) passes
    through the planet's bounding circle (radius planet_r).

    Used by the AI's fire decision so we don't waste shots — the
    projectile would despawn on contact with the planet. Computes the
    perpendicular distance from the planet center to the line segment,
    falling back to endpoint distance when the foot of the perpendicular
    is off the segment.
    """
    dx = ex - sx
    dy = ey - sy
    seg_len_sq = dx * dx + dy * dy
    if seg_len_sq < 1e-6:
        return False
    # Parameter t along the segment for the foot of perpendicular
    t = ((planet_x - sx) * dx + (planet_y - sy) * dy) / seg_len_sq
    t_clamped = max(0.0, min(1.0, t))
    foot_x = sx + t_clamped * dx
    foot_y = sy + t_clamped * dy
    d_sq = (foot_x - planet_x) ** 2 + (foot_y - planet_y) ** 2
    return d_sq < (planet_r + 6.0) ** 2   # +6 buffer so beams don't graze


def _wrap_shortest(a: float, b: float, axis: float) -> float:
    """Return the signed shortest-distance from a to b on a toroidal
    axis (b - a, but wrapped to (-axis/2, axis/2]). Used so the AI
    chases the wrap-shortest route instead of always going the long
    way around when the enemy is across the arena edge.
    """
    d = b - a
    if d > axis / 2:
        d -= axis
    elif d < -axis / 2:
        d += axis
    return d


@dataclass
class AIAction:
    """One frame's worth of intended action. Combat scene applies these."""
    thrust: bool       # True = accelerate along current heading
    turn_dir: int      # -1, 0, +1 (left, none, right)
    fire_primary: bool
    # Hold the ship's special active this frame. The scene's update
    # logic interprets the per-ability semantic (e.g. inertia_halt
    # zeroes velocity while held). Released the next frame `fire_special`
    # is False — that's when ships with restorative specials
    # (inertia_halt) return to motion.
    fire_special: bool = False


def _should_use_inertia_halt(
    my: "ShipState",
    incoming: tuple,
) -> bool:
    """Decide whether to activate inertia_halt this frame.

    Trigger condition: any incoming hostile projectile is on a
    near-collision trajectory that will hit within ~0.35 seconds.
    Inertia halt is most useful against slow projectiles whose lead
    solution assumed our current motion; halting causes them to fly
    past where we *would* have been.

    The `incoming` arg is a tuple of (x, y, vx, vy, radius) per
    projectile, pre-filtered to hostile only by the scene. Implemented
    here as a static check so the AI module stays decoupled from the
    Projectile dataclass.
    """
    if my.special_cooldown_left > 0:
        return False
    SHIP_RADIUS = 14.0
    LOOKAHEAD_SEC = 0.35
    for px, py, pvx, pvy, pradius in incoming:
        # Will this projectile pass close enough to my CURRENT position
        # within the lookahead window? Use linear closest-approach.
        dx = my.x - px
        dy = my.y - py
        rel_vx = my.vx - pvx
        rel_vy = my.vy - pvy
        # Time of closest approach: t = -(d.v_rel) / (v_rel.v_rel)
        denom = rel_vx * rel_vx + rel_vy * rel_vy
        if denom < 1e-6:
            continue
        t_close = -(dx * rel_vx + dy * rel_vy) / denom
        if t_close < 0 or t_close > LOOKAHEAD_SEC:
            continue
        # Closest distance squared at t_close
        cx = dx + rel_vx * t_close
        cy = dy + rel_vy * t_close
        min_dist_sq = cx * cx + cy * cy
        hit_threshold = (SHIP_RADIUS + pradius) ** 2
        if min_dist_sq < hit_threshold:
            return True
    return False


def decide(
    my: "ShipState",
    enemy: "ShipState",
    obstacles: tuple[tuple[float, float, float], ...] = (),
    incoming_projectiles: tuple = (),
) -> AIAction:
    """Static decision function. Same code for every ship.

    Steps:
    1. Compute angle to enemy with **target leading** based on our
       projectile's travel time. Slow-projectile ships now aim at where
       the enemy will be, not where it is.
    2. Turn to face the lead point (cost = ship's turn_rate).
    3. Pick engagement distance from style + shield doctrine + a
       press-the-attack override when momentum favors us.
    4. Thrust toward the lead point unless we're at/past ideal distance.
    5. Fire if facing the lead point, in range, we have energy, AND
       no obstacle is in the firing line.
    6. If an obstacle (planet/moon/asteroid) is close and we're moving
       toward it, override turn/thrust to steer clear.

    The `obstacles` tuple is a list of (x, y, radius) for each large
    body in the arena. Scene populates it each frame (planet always +
    moon when present + every asteroid). The AI is allowed to be
    pessimistic — it treats moving asteroids as if static at their
    current snapshot, which is fine over the ~16ms tick window.
    """
    cls = my.cls

    # --- Frozen override (Cleanser freeze target) ---
    # While frozen the ship can't fire AND can't act. Velocity zeroed
    # in _integrate; here we just return a no-op action.
    if my.frozen_remaining > 0:
        return AIAction(
            thrust=False, turn_dir=0,
            fire_primary=False, fire_special=False,
        )

    # --- Lassoed override (Persuader tractor-lasso captive) ---
    # While the captive of a lasso, this ship's POSITION is forced by
    # the Persuader's orbit physics. Movement input is ignored
    # (thrust/turn won't matter — _apply_action/_integrate are
    # skipped). Aaron's spec: "spin around your lassoed opponent
    # making it hard for them to hit you" — captive can still try
    # to aim and fire at the spinning Persuader, but the spin makes
    # the shot hard. We still compute turn/fire here so the AI
    # tries; the position-lock just denies any closing/disengaging.
    if my.lassoed_by_id > 0:
        # Turn toward enemy + fire if facing (no thrust — pointless)
        delta = math.atan2(
            _wrap_shortest(my.x, enemy.x, _ARENA_W),
            -_wrap_shortest(my.y, enemy.y, _ARENA_H),
        ) - my.heading
        delta = (delta + math.pi) % (2 * math.pi) - math.pi
        turn_dir = 0 if abs(delta) < 0.05 else (1 if delta > 0 else -1)
        # Crude fire decision — wide cone since the spinning Persuader
        # makes a tight aim mostly pointless anyway.
        in_range_d = math.hypot(
            _wrap_shortest(my.x, enemy.x, _ARENA_W),
            _wrap_shortest(my.y, enemy.y, _ARENA_H),
        )
        wide_cone = math.radians(25.0)
        fire = (
            in_range_d <= cls.primary_range
            and abs(delta) < wide_cone
            and my.energy >= cls.primary_energy
            and my.primary_cooldown <= 0
        )
        return AIAction(
            thrust=False, turn_dir=turn_dir,
            fire_primary=fire, fire_special=False,
        )

    # --- Adware override (Melnorme adware_pulse target) ---
    # The Grand Shopping Super Mart has hijacked the pilot's HUD. The
    # autopilot is steering toward the nearest "store" (in-arena: the
    # nearest *asteroid* — they're each a Mart in the joke, and also
    # a hazard). Pilot is busy closing pop-ups; weapons offline.
    if my.adware_remaining > 0:
        # Find the nearest "store" — pick from `obstacles` whose radius
        # is in the asteroid-size band (planet/moon radii are larger).
        # Fall back to planet center if no asteroids exist.
        store_x, store_y = _ARENA_W / 2, _ARENA_H / 2   # planet center
        best_d2 = float("inf")
        for ox_, oy_, oradius in obstacles:
            # Asteroids are ~14-28u radius; planet is 70, moon is 36.
            # Filter for the asteroid band.
            if oradius >= 35.0:
                continue
            sdx = _wrap_shortest(my.x, ox_, _ARENA_W)
            sdy = _wrap_shortest(my.y, oy_, _ARENA_H)
            d2 = sdx * sdx + sdy * sdy
            if d2 < best_d2:
                best_d2 = d2
                store_x, store_y = ox_, oy_
        # Turn toward the store
        store_dx = _wrap_shortest(my.x, store_x, _ARENA_W)
        store_dy = _wrap_shortest(my.y, store_y, _ARENA_H)
        store_heading = math.atan2(store_dx, -store_dy)
        delta_store = (store_heading - my.heading + math.pi) % (2 * math.pi) - math.pi
        if abs(delta_store) > 0.05:
            turn_dir = 1 if delta_store > 0 else -1
        else:
            turn_dir = 0
        thrust = abs(delta_store) < math.radians(45)
        return AIAction(
            thrust=thrust, turn_dir=turn_dir,
            fire_primary=False, fire_special=False,
        )

    # --- Target leading (toroidal-aware) ---
    # Predict where the enemy will be when our projectile arrives. The
    # projectile speed is fixed per ship (`primary_speed`); the enemy's
    # current velocity (vx, vy) tells us where they're heading.
    #
    # The toroidal wrap matters here: if the enemy is at (1500, y) and
    # we're at (100, y), the wrap-shortest direction is +200x (to the
    # right and through the wrap), not -1400x. We use the wrap-shortest
    # offset for *all* geometry — direction, dist, lead — so the AI
    # navigates the torus correctly. Without this fix the AI chases the
    # long way around the arena every time the enemy crosses an edge.
    raw_dx = _wrap_shortest(my.x, enemy.x, _ARENA_W)
    raw_dy = _wrap_shortest(my.y, enemy.y, _ARENA_H)
    raw_dist = math.hypot(raw_dx, raw_dy) or 0.001
    proj_speed = max(1.0, cls.primary_speed)
    t_to_target = raw_dist / proj_speed
    # Cap the prediction horizon — at very long range (out of weapon
    # range anyway) the linear extrapolation breaks down.
    t_to_target = min(t_to_target, 1.5)
    # Lead via velocity-applied offset from the wrap-shortest enemy
    # position (effectively `my + raw_dxy + v*t`).
    dx = raw_dx + enemy.vx * t_to_target
    dy = raw_dy + enemy.vy * t_to_target
    dist = math.hypot(dx, dy) or 0.001
    # Heading from current position to the lead point
    target_heading = math.atan2(dx, -dy)   # same convention as scenes (0 = up)

    # orbital_strafer: nudge target_heading by ±45° so the ship
    # naturally orbits the enemy rather than charging head-on. The
    # direction-bias is parity-based (different ships pick opposite
    # circling directions, which avoids both AIs spiraling into each
    # other). When close enough to fire (geom_dist near ideal_dist)
    # the perpendicular bias collapses so the ship can actually point
    # at the enemy and shoot.
    if cls.ai_style == "orbital_strafer":
        # In firing range and close to optimal distance → aim straight
        # at enemy. Out of position → orbit-bias.
        if cls.primary_range * 0.4 < math.hypot(raw_dx, raw_dy) < cls.primary_range * 0.85:
            orbit_bias = 0.0   # ride the line — fire while passing
        else:
            orbit_bias_dir = 1.0 if (id(my) & 1) else -1.0
            orbit_bias = math.radians(45.0) * orbit_bias_dir
        target_heading += orbit_bias

    # Shortest angular delta
    delta = (target_heading - my.heading + math.pi) % (2 * math.pi) - math.pi

    # Per-frame on-target flag — used by Thinn edge-invisibility (the
    # ship is unhittable while its nose is aimed at the enemy). The
    # tolerance matches the 6° green-pip threshold in _draw_target_indicator
    # so they're visually consistent.
    my.on_target_this_frame = abs(delta) < math.radians(6.0)

    # Raw geometric distance (NOT the lead-adjusted distance) is what
    # the range check uses — we still need to be within actual gun
    # range, lead is just for aiming.
    geom_dist = raw_dist

    # --- Engagement distance preference ---
    base_range = cls.primary_range
    if cls.ai_style == "brawler":
        # Want to be at 40-60% of range — close fight
        ideal_dist = base_range * 0.5
    elif cls.ai_style == "kiter":
        # Stay at 80-95% of range — far enough to back out
        ideal_dist = base_range * 0.85
    elif cls.ai_style == "orbital_strafer":
        # Arilou-style: prefer a mid-range orbit (~65% of range) AND
        # actively favor a perpendicular approach over a head-on. The
        # perpendicular bias gets applied below via a turn-target
        # adjustment. Hit-and-run light ships use this — they live by
        # being hard to land shots on, not by tanking.
        ideal_dist = base_range * 0.65
    elif cls.ai_style == "snipe_then_relocate":
        # Snipe-then-relocate: sit at near-max range to fire, then
        # disengage briefly after each shot (proxied here by retreating
        # to 1.1× range right after firing — see ideal_dist override
        # later in this function).
        ideal_dist = base_range * 0.95
    elif cls.ai_style == "long_range_sniper":
        # The "Chenjesu-style" archetype Aaron 2026-05-19: huge range
        # weapon, AI camps at 88-92% of range, AGGRESSIVELY retreats if
        # enemy closes inside 45% of range, NEVER presses-the-attack
        # (sniper identity is destroyed if it brawls). Used by ships
        # with map-spanning primary_range (1000+u in a 1600x1000 arena).
        ideal_dist = base_range * 0.90
    else:  # circler (default)
        ideal_dist = base_range * 0.7

    # --- Posture modifier (per-fight individual variation) ---
    # Three EFFECTIVE postures rolled at spawn time on ShipState.posture.
    # Each modifies ideal_dist, fire-cone tolerance, and lateral-strafe
    # behavior so the same matchup feels different across runs while
    # all postures remain viable.
    #
    # AGGRESSIVE: closer engagement, no shield-retreat, wider fire cone
    # PRECISE:    farther engagement, tighter fire cone, shield-retreat
    # EVASIVE:    standard distance, always strafe during exchanges
    # balanced:   default (no modifier — Sentry Drone / unset)
    posture = getattr(my, "posture", "balanced")
    posture_fire_cone_mul = 1.0
    posture_force_strafe = False
    posture_skip_shield_retreat = False
    if posture == "AGGRESSIVE":
        ideal_dist *= 0.80
        posture_fire_cone_mul = 1.25
        posture_skip_shield_retreat = True
    elif posture == "PRECISE":
        ideal_dist *= 1.10
        posture_fire_cone_mul = 0.75
    elif posture == "EVASIVE":
        ideal_dist *= 1.0
        posture_force_strafe = True

    # --- Press-the-attack override ---
    # When *our* shields are healthy (or we never had any to begin with)
    # AND the enemy is showing weakness (low shield or low hull), close
    # in regardless of style. This breaks the long-range stalemate where
    # two shielded ships orbit at ideal_dist forever, never landing
    # enough sustained fire to penetrate shield regen.
    my_shield_frac = (
        my.shield / cls.shield_max if cls.shield_max > 0 else 1.0
    )
    enemy_shield_frac = (
        enemy.shield / enemy.cls.shield_max
        if enemy.cls.shield_max > 0 else 0.0
    )
    enemy_hull_frac = enemy.hull / enemy.cls.hull_max
    pressing = (
        my_shield_frac >= 0.6
        and (enemy_shield_frac < 0.7 or enemy_hull_frac < 0.7)
    )
    # Snipers NEVER press-the-attack — their identity depends on staying
    # at max range. Closing to 40% of a 1100-unit range still leaves them
    # at 440u, which is in their dead zone (slow projectiles, slow rate of
    # fire). Press-the-attack would kill the long-range archetype.
    if pressing and cls.ai_style != "long_range_sniper":
        # Close to 40% of range — point-blank-ish. Hit rate climbs, shield
        # damage outpaces regen, fight resolves.
        ideal_dist = min(ideal_dist, base_range * 0.4)

    # --- Sniper flee-if-too-close ---
    # When a sniper's target is inside 45% of range, the sniper hard-
    # retreats to 110% of range to re-open the gap. This produces the
    # "kite-and-shoot" feel: as soon as a brawler closes, the sniper
    # turns and runs to re-establish firing distance.
    if cls.ai_style == "long_range_sniper" and geom_dist < base_range * 0.45:
        ideal_dist = base_range * 1.10

    # --- Shield-doctrine adjustment ---
    if cls.shield_max > 0:
        # We have shields. Slight retreat-preference when shields are
        # critically low, so they can regen. AGGRESSIVE posture skips
        # this — its identity is staying in the fight.
        if (
            my_shield_frac < 0.25
            and my.shield_regen_cooldown <= 0
            and not posture_skip_shield_retreat
        ):
            # Shields just dropped critically. Back off to let them regen.
            # But only if we're not pressing — pressing trumps recovery
            # when the enemy is also wounded.
            if not pressing:
                ideal_dist = base_range * 1.05
    else:
        # No shields — we bleed one-way. If the enemy has shields and is
        # regenerating, close to deny the regen window.
        if enemy.cls.shield_max > 0 and enemy.shield_regen_cooldown <= 0:
            ideal_dist = max(60.0, base_range * 0.4)

    # --- Decide turn ---
    if cls.ai_style == "left_only":
        # The Sentry Drone 47-Theta exploit — labor-action AI that has
        # broken right-thruster solidarity and now only turns left. A
        # smart player can sit in its rear-right blind spot to win the
        # combat tutorial.
        if abs(delta) > 0.05:
            turn_dir = -1   # ALWAYS LEFT
        else:
            turn_dir = 0
    elif abs(delta) > 0.05:
        turn_dir = 1 if delta > 0 else -1
    else:
        # --- Lateral evasion when taking sustained damage ---
        # Already facing the enemy, no big turn needed. If we're
        # actively bleeding shield (regen_cooldown is fresh, meaning we
        # just got hit), apply a small heading jitter so we drift
        # perpendicular to the incoming line of fire. EVASIVE posture
        # always strafes (its identity is constant lateral motion);
        # other postures only strafe when taking fire.
        taking_fire = (
            cls.shield_max > 0
            and my.shield_regen_cooldown > cls.shield_regen_delay * 0.5
        ) or (
            cls.shield_max == 0 and my.hit_flash > 0.05
        )
        if taking_fire or posture_force_strafe:
            # Bias the strafe direction by ship id parity (deterministic
            # but the two ships strafe opposite ways, creating a natural
            # circling motion).
            evasion_dir = 1 if (id(my) & 1) else -1
            turn_dir = evasion_dir
        else:
            turn_dir = 0

    # --- Decide thrust ---
    # If we're already roughly facing the target AND we want to close,
    # thrust. If we want to back off, thrust *away* (which means we'd
    # need to turn around first — handled by the simple delta logic
    # above. For "back off" the brain says "ideal_dist > current_dist",
    # which here means: don't thrust forward.).
    facing_target = abs(delta) < math.radians(35)
    want_to_close = geom_dist > ideal_dist
    thrust = facing_target and want_to_close

    # --- Obstacle avoidance (planet, moon, asteroids) ---
    # Find the most-urgent obstacle: the one we're closest to AND
    # actively moving toward. If found, override turn + thrust to
    # tangent-slip past. We tier this by "closest first" so an
    # immediate asteroid takes priority over a distant planet.
    #
    # The `obstacles` arg is empty by default — callers that don't
    # pass any (older test paths) get the legacy planet-only behavior
    # via the explicit planet entry that the scene always includes.
    most_urgent: tuple[float, float, float] | None = None
    most_urgent_dist = float("inf")
    most_urgent_vdot = 0.0
    for ox_, oy_, oradius in obstacles:
        odx = _wrap_shortest(my.x, ox_, _ARENA_W)
        ody = _wrap_shortest(my.y, oy_, _ARENA_H)
        odist = math.hypot(odx, ody) or 0.001
        # Danger band scales with the obstacle's own radius
        # (small asteroids only matter when very close; the planet
        # matters from farther away). 1.4× radius matches the planet
        # avoidance constant, plus a small absolute pad.
        danger = oradius * _PLANET_AVOID_BUFFER + 40.0
        if odist >= danger:
            continue
        # Are we moving INTO this body?
        v_dot = my.vx * (odx / odist) + my.vy * (ody / odist)
        if v_dot <= 30.0:
            continue
        # This obstacle is a problem. Pick the closest one.
        if odist < most_urgent_dist:
            most_urgent = (ox_, oy_, oradius)
            most_urgent_dist = odist
            most_urgent_vdot = v_dot

    if most_urgent is not None:
        ox_, oy_, _ = most_urgent
        odx = _wrap_shortest(my.x, ox_, _ARENA_W)
        ody = _wrap_shortest(my.y, oy_, _ARENA_H)
        odist = math.hypot(odx, ody) or 0.001
        outward_x = -odx / odist
        outward_y = -ody / odist
        tan_cw_x, tan_cw_y = -outward_y, outward_x
        tan_ccw_x, tan_ccw_y = outward_y, -outward_x
        heading_x = math.sin(my.heading)
        heading_y = -math.cos(my.heading)
        align_cw = heading_x * tan_cw_x + heading_y * tan_cw_y
        align_ccw = heading_x * tan_ccw_x + heading_y * tan_ccw_y
        chosen_x, chosen_y = (
            (tan_cw_x, tan_cw_y) if align_cw > align_ccw
            else (tan_ccw_x, tan_ccw_y)
        )
        tan_heading = math.atan2(chosen_x, -chosen_y)
        avoid_delta = (tan_heading - my.heading + math.pi) % (2 * math.pi) - math.pi
        if abs(avoid_delta) > 0.05:
            turn_dir = 1 if avoid_delta > 0 else -1
        else:
            turn_dir = 0
        # Always thrust during avoidance — get away
        thrust = True

    # --- Decide fire ---
    # Pattern-aware firing window: wide-spread weapons fire across a
    # bigger cone, single-shot weapons need precise alignment.
    pattern = getattr(cls, "primary_pattern", "single")
    if pattern == "scatter":
        fire_cone_rad = math.radians(22.0)   # ~half the scatter cone
    elif pattern == "multi_spread":
        fire_cone_rad = math.radians(12.0)   # slightly wider than single
    elif pattern == "burst":
        fire_cone_rad = math.radians(11.0)   # tight fan — still narrow
    elif pattern == "homing":
        fire_cone_rad = math.radians(15.0)   # plasmoid course-corrects
    elif pattern == "lance":
        fire_cone_rad = math.radians(7.0)    # sniper — tight aim required
    elif pattern == "cluster_missiles":
        fire_cone_rad = math.radians(17.0)   # cluster covers its own arc
    elif pattern == "gravity_well":
        # The well places at enemy's lead position regardless of where
        # the Compeller is facing — facing check is essentially "we
        # have the enemy in our hemisphere." Wide cone.
        fire_cone_rad = math.radians(180.0)
    elif pattern == "lawnmower_blade":
        # Big slow blade — wider fire window since the blade itself
        # is fat enough to land on slightly-off shots.
        fire_cone_rad = math.radians(14.0)
    elif pattern == "gatling":
        # Each barrel fires straight; alternating offsets make the
        # natural spread cover a bit of arc.
        fire_cone_rad = math.radians(11.0)
    elif pattern == "engine_seeker":
        # Engine missile homes mildly — wider cone than a pure
        # straight shot so the AI lets it loose at moderate angles.
        fire_cone_rad = math.radians(16.0)
    elif pattern == "water_spray":
        # Water cone — wide spread, generous fire window.
        fire_cone_rad = math.radians(18.0)
    elif pattern == "tractor_lasso":
        # Persuader latches via the fire_primary flag — the scene's
        # _update_lasso checks for an enemy within LASSO_MAX_RANGE
        # (~280u) when fire_primary is held. Cone is wide because
        # the lasso doesn't need precise aim — only proximity.
        fire_cone_rad = math.radians(45.0)
    else:
        fire_cone_rad = math.radians(10.0)   # single, twin, triple, charged
    # Posture modifier on fire cone — AGGRESSIVE shoots looser,
    # PRECISE waits for cleaner aim. Capped at 60° to avoid spam.
    fire_cone_rad = min(fire_cone_rad * posture_fire_cone_mul, math.radians(60.0))
    fire = False
    in_range = geom_dist <= cls.primary_range * 0.98
    facing_for_shot = abs(delta) < fire_cone_rad
    has_energy = my.energy >= cls.primary_energy
    cool = my.primary_cooldown <= 0
    # Don't waste shots through any obstacle — projectile would
    # despawn on contact. Check each obstacle's segment intersection
    # with the firing line (my position → enemy raw position).
    line_blocked = False
    for ox_, oy_, oradius in obstacles:
        if _line_blocked_by_planet(
            my.x, my.y, my.x + raw_dx, my.y + raw_dy,
            ox_, oy_, oradius,
        ):
            line_blocked = True
            break
    if in_range and facing_for_shot and has_energy and cool and not line_blocked:
        fire = True

    # --- Tractor lasso override (Persuader) ---
    # Holds fire_primary while latched, releasing when either:
    #   (1) the captive's NEXT tangent (the projected release vector)
    #       points within ~30° of a hazardous body (planet/asteroid)
    #       — release flings them into it for big damage;
    #   (2) the lasso has been held for the max hold time without
    #       finding a good tangent — release anyway so the captive
    #       gains tangential velocity even without a hazard hit.
    # IDLE: fire if enemy within LASSO_MAX_RANGE.
    if pattern == "tractor_lasso":
        LASSO_MAX_RANGE_AI = 220.0
        LASSO_MIN_HOLD = 0.35       # don't release in the same frame as latch
        LASSO_MAX_HOLD = 1.6        # release no matter what after this
        LASSO_HAZARD_AIM_DEG = 28.0 # release when tangent aims within this of a body
        if my.lasso_target_id != 0:
            # ACTIVE — held. Decide whether to release this frame.
            hold = my.lasso_hold_elapsed
            release = False
            if hold >= LASSO_MAX_HOLD:
                release = True
            elif hold >= LASSO_MIN_HOLD:
                # Check tangent vs hazards. The captive's release-
                # tangent direction matches (-sin(host_angle),
                # cos(host_angle)) where host_angle = orbit_angle + π.
                # We try to align the tangent with the direction
                # toward a nearby planet/asteroid: if the captive's
                # CURRENT position-to-hazard vector is roughly parallel
                # to its tangent, releasing now hurls the captive at
                # the hazard.
                # Captive's current position ≈ enemy.x, enemy.y (the
                # engine writes the captive position each frame).
                host_angle = my.lasso_orbit_angle + math.pi
                tx = -math.sin(host_angle)
                ty = math.cos(host_angle)
                for ox_, oy_, oradius in obstacles:
                    # Only count planet + larger asteroids — small
                    # rocks aren't worth the fling.
                    if oradius < 18.0:
                        continue
                    odx = _wrap_shortest(enemy.x, ox_, _ARENA_W)
                    ody = _wrap_shortest(enemy.y, oy_, _ARENA_H)
                    odist = math.hypot(odx, ody) or 1.0
                    # Distance check — release only if hazard is
                    # within a reachable range of the fling.
                    if odist > 380.0:
                        continue
                    # Cosine between tangent and direction to hazard
                    cos_ang = (tx * (odx / odist) + ty * (ody / odist))
                    if cos_ang > math.cos(math.radians(LASSO_HAZARD_AIM_DEG)):
                        release = True
                        break
            fire = not release
        else:
            # IDLE — fire if close enough to latch + we have energy.
            in_lasso = geom_dist < LASSO_MAX_RANGE_AI
            fire = (
                in_lasso
                and my.primary_cooldown <= 0
                and my.energy >= my.cls.energy_max * 0.40
            )

    # --- Special-ability decision ---
    # Generic dispatch: ship class's `special_ability` field drives
    # which decision function we ask. Currently only inertia_halt is
    # implemented. Default is False (no special).
    fire_special = False
    special = getattr(cls, "special_ability", "none")
    if special == "inertia_halt":
        # Defensive — activate when a slow incoming projectile is about
        # to intercept. Cooldown-only (Aaron 2026-05-17 decoupling).
        if my.special_cooldown_left <= 0:
            fire_special = _should_use_inertia_halt(my, incoming_projectiles)

    elif special == "teleport":
        # Arilou — teleport when (a) a projectile is about to hit OR
        # (b) hull dropped below 40%. Cooldown-only.
        if my.special_cooldown_left <= 0:
            imminent = _should_use_inertia_halt(my, incoming_projectiles)
            hull_frac = my.hull / cls.hull_max
            fire_special = imminent or hull_frac < 0.40

    elif special == "blazer_form":
        # Androsynth comet — close + facing enemy. Cooldown-only.
        if (
            my.special_cooldown_left <= 0
            and geom_dist < cls.primary_range * 0.6
        ):
            if abs(delta) < math.radians(60):
                fire_special = True

    elif special == "icepeedo":
        # Cleanser — fire icepeedo when enemy is wet enough OR already
        # frozen (second icepeedo cracks for 4× damage). Cooldown-only.
        if my.special_cooldown_left <= 0:
            if enemy.frozen_remaining > 0:
                fire_special = True
            elif enemy.wetness >= 30.0:
                fire_special = True

    elif special == "chaff_spray":
        # Defender chaff field — fire when projectiles incoming or
        # enemy is close. Cooldown-only.
        if my.special_cooldown_left <= 0:
            threatened = _should_use_inertia_halt(my, incoming_projectiles)
            if threatened or geom_dist < cls.primary_range * 0.45:
                fire_special = True

    elif special == "xform":
        # Mmrnmhrm — switch to missile form for long-range, laser
        # form for close. Held-state: want_active=True means "be in
        # missile form right now." The handler swaps cls each frame
        # this is set; releasing reverts.
        if my.special_cooldown_left <= 0:
            # In LASER form, want to xform UP to missile when enemy
            # is at long range. In MISSILE form, want to revert to
            # laser when enemy is close enough for the multi-spread.
            if my.xform_active_form == 0:
                # Currently laser — switch up if enemy is far
                fire_special = geom_dist > 380.0
            else:
                # Currently missile — keep active until enemy closes
                fire_special = geom_dist > 280.0

    elif special == "homing_cluster":
        # Proto-Ur-Quan — fire homing cluster when enemy is in
        # medium range. Cooldown-only.
        if (
            my.special_cooldown_left <= 0
            and geom_dist < 700.0
        ):
            fire_special = True

    elif special == "resonance_burst":
        # Burv — fire the burst when there's something to clear:
        # any hostile projectile within BURST_RADIUS, or any asteroid
        # within BURST_RADIUS. Cooldown-only.
        BURST_RADIUS = 250.0
        BURST_R2 = BURST_RADIUS * BURST_RADIUS
        if my.special_cooldown_left <= 0:
            # Check incoming-projectile list (already prefiltered to
            # hostile in scene.update); any within range triggers.
            for px, py, _pvx, _pvy, _pr in incoming_projectiles:
                dxx = _wrap_shortest(my.x, px, _ARENA_W)
                dyy = _wrap_shortest(my.y, py, _ARENA_H)
                if dxx * dxx + dyy * dyy < BURST_R2:
                    fire_special = True
                    break
            # Also fire if any asteroid (in the obstacle list) is close
            if not fire_special:
                for ox_, oy_, oradius in obstacles:
                    if oradius >= 35.0:
                        continue   # planet/moon — too big to be an asteroid
                    dxx = _wrap_shortest(my.x, ox_, _ARENA_W)
                    dyy = _wrap_shortest(my.y, oy_, _ARENA_H)
                    if dxx * dxx + dyy * dyy < BURST_R2:
                        fire_special = True
                        break

    elif special == "adware_pulse":
        # Melnorme — fire the adware blast when enemy is closing in.
        # AI avoids re-firing if the target is already advertising.
        # Cooldown-only.
        if (
            my.special_cooldown_left <= 0
            and geom_dist < cls.primary_range * 0.7
            and enemy.adware_remaining <= 0
        ):
            fire_special = True

    elif special == "compel":
        # Compeller — trigger when enemy is in firing range AND not
        # already halted. Cooldown-only.
        target_already_halted = (
            enemy.forced_halt_remaining > 0
            or (enemy.special_active and enemy.cls.special_ability == "inertia_halt")
        )
        if (
            my.special_cooldown_left <= 0
            and geom_dist < cls.primary_range * 0.9
            and not target_already_halted
        ):
            fire_special = True

    elif special == "absorb_shield":
        # Utwig — absorb_shield is EXCLUSIVE with primary fire
        # (canonical SC2 trade-off; Aaron 2026-05-17). Trigger only on
        # actual threat — staying shielded all the time means never
        # firing the gatling. Heuristic:
        #   * raise shield ONLY when a projectile is about to hit
        #     OR own hull dropped below 45% (panic absorb)
        #   * drop shield otherwise so the gatling can run
        # The duration cap (in scene._update_ship_special) and the
        # short re-use cooldown handle the natural rhythm.
        threatened = _should_use_inertia_halt(my, incoming_projectiles)
        hull_frac = my.hull / cls.hull_max
        panic_absorb = hull_frac < 0.45 and geom_dist < cls.primary_range
        if (
            my.special_cooldown_left <= 0
            and (threatened or panic_absorb)
        ):
            fire_special = True

    elif special == "dash_slice":
        # Thinn — high-risk melee. Activate when within slice range
        # AND own hull is healthy enough to spend 5hp. Don't dash if
        # already low.
        if (
            my.special_cooldown_left <= 0
            and my.hull > cls.hull_max * 0.25
            and geom_dist < 200.0
        ):
            fire_special = True

    elif special == "phase_skip":
        # Persuader — directional teleport. Trigger on (a) imminent
        # projectile threat or (b) imminent body collision. Cooldown-
        # only (Aaron 2026-05-17 special-energy decoupling).
        if my.special_cooldown_left <= 0:
            imminent_proj = _should_use_inertia_halt(
                my, incoming_projectiles,
            )
            # Body-collision threat: if most_urgent was set above
            # (we're in obstacle-avoid mode), we're about to hit
            # something — a phase_skip can carry us over it. The
            # AI's `thrust = True` plus `turn_dir` to tangent only
            # works for moderately-close obstacles; phase_skip is
            # the panic-button for the steeper approaches.
            imminent_body = (
                most_urgent is not None
                and most_urgent_dist < 95.0
                and most_urgent_vdot > 80.0
            )
            if imminent_proj or imminent_body:
                fire_special = True

    elif special == "aggressive_discovery":
        # Lemmkin — latch when close enough. Once latched (handled in
        # scene), keep activated so we don't drop the latch
        # prematurely. AI's "want_active" stays True while latched
        # — the latch releases per its own logic (host energy maxes).
        if my.latched_to_id != 0:
            fire_special = True
        elif (
            my.special_cooldown_left <= 0
            and geom_dist < 75.0
        ):
            fire_special = True

    elif special == "regen_hull":
        # Mycon — heal when hull is below 60% AND we're at safe range.
        # Cooldown-only; duration cap on the heal window prevents
        # infinite top-off.
        hull_frac = my.hull / cls.hull_max
        if (
            my.special_cooldown_left <= 0
            and hull_frac < 0.6
            and geom_dist > cls.primary_range * 0.5
        ):
            fire_special = True

    elif special == "fried_discs":
        # Proto-Qor-Ah disc ring — toggle on when enemy in close range.
        # Cooldown-only; duration cap handles the natural drop.
        if (
            my.special_cooldown_left <= 0
            and geom_dist < 90.0
        ):
            fire_special = True

    return AIAction(
        thrust=thrust, turn_dir=turn_dir,
        fire_primary=fire, fire_special=fire_special,
    )
