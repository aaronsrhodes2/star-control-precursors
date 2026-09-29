"""MeleeCombatScene — 1v1 ship combat with Newtonian movement.

Both sides AI-controlled by default (the auto-fight commitment). The
test harness uses this to drive Super Melee fights to completion. A
player-control path will land later; the engine treats it as just
another action source feeding the same physics + weapons code.

Slice scope per the design canon:
- 2D top-down, screen-wrapping arena
- Newtonian momentum (velocity persists; thrust adds to it)
- Projectile primary weapons (no specials yet — those land in pass 2)
- Hull + regenerating shield (shields only on Furling-faction ships)
- Win = one ship's hull hits 0; the surviving side is the winner

When the fight ends the scene calls `on_finish(winner_side)` if provided,
else falls back to set_scene(SuperMeleeScene). The win callback is what
the SuperMelee picker uses to advance to a result screen.
"""

from __future__ import annotations

import math
import os
import random
from dataclasses import dataclass, field
from typing import Callable

import pygame

from scz.combat.ai import AIAction, decide
from scz.combat.ships import ShipClass
from scz.engine.scene import Scene


# Arena dimensions in world units — wraps at edges.
ARENA_W = 1600.0
ARENA_H = 1000.0

# Arena style — picks which central-body visual + which extra
# furniture is generated. Physics is identical regardless of style;
# the central body has the same gravity/collision profile.
#
# "solar_system" (default): planet visual + chance of a moon. SC2
# canonical solar-system combat (e.g. super-melee training, system
# encounters). The planet diegetically belongs to a star system.
#
# "hyperspace": no moon (the planet visual is replaced with a
# "coaxial interference tunnel" — the interference figure that forms
# between two hyperspace bubbles closing for combat. SC2-faithful
# rationalization for why you "fight around a planet" in hyperspace
# even though you're nowhere near one). Hyperspace encounters
# (Cleanser patrol, future intercept beats) pass this style.
#
# Both styles share asteroids, nebulae, background star, starfield.
ARENA_STYLE_SOLAR_SYSTEM = "solar_system"
ARENA_STYLE_HYPERSPACE = "hyperspace"


# Central planet anchor — the SC2-canonical arena feature. A planet
# sits at the center, exerts gravity on ships AND projectiles, and
# collisions damage. Per Aaron's call (2026-05-17): keep SC2-style
# wrap-around arena + planet, NOT the Origins shrinking-boundary
# mechanic. Tunable knobs:
#
# - PLANET_RADIUS: visual + collision radius. SC2's planet was ~60-80px
#   on a smaller arena; scaled here for a 1600×1000 arena.
# - PLANET_GRAVITY: g-force constant. Field strength at the surface
#   determines how strongly a ship gets pulled in. Tuned to "noticeable
#   when nearby, ignorable at long range" — the gravity falls off with
#   inverse-square distance.
# - PLANET_COLLISION_DAMAGE: hp inflicted when a ship grazes the planet.
#   Bouncy collision (velocity reflects) + this much hull damage per hit
#   moment. Prevents a slow-circling ship from sitting on the planet.
PLANET_X = ARENA_W / 2
PLANET_Y = ARENA_H / 2
PLANET_RADIUS = 70.0
PLANET_GRAVITY = 80000.0     # at r=80 (surface skim), accel = G/r^2 = 12.5 u/s^2
PLANET_COLLISION_DAMAGE = 25.0
# Projectiles are also affected by gravity. The factor scales the
# strength relative to ships — beams (fast-moving) curve only slightly
# (their effective gravity-exposure-time is tiny), plasma globs (slow)
# arc dramatically. The shared constant means a single tune-knob.
PROJECTILE_GRAVITY_FACTOR = 1.0

# Asteroids — small movable hazards. Drift through the arena, get
# pulled around by planet gravity (cool slingshot orbits), damage
# ships on contact, absorb projectiles. Indestructible — the player
# evades them, doesn't shoot them.
ASTEROID_COUNT_MIN = 3      # at least this many per fight
ASTEROID_COUNT_MAX = 6      # up to this many
ASTEROID_RADIUS_MIN = 14.0
ASTEROID_RADIUS_MAX = 28.0
ASTEROID_DRIFT_MIN = 30.0   # u/s; lower bound on initial speed
ASTEROID_DRIFT_MAX = 90.0
ASTEROID_COLLISION_DAMAGE = 12.0   # half what the planet does — they're smaller

# UQM-derived sprite keys for asteroid art — each name matches a file
# in `assets/planets/<key>-sml-000.png`. The 50+ planet-type sprites
# get reused as varied asteroid visuals. Picked deterministically per
# asteroid from the per-fight RNG so re-runs of the same seed produce
# the same field. Curated subset — favors rocky / dusty / metallic
# textures (avoiding gas-giant + jewel-toned types that don't read
# as "small rock").
ASTEROID_SPRITE_KEYS: tuple[str, ...] = (
    "chondrite", "carbide", "chlorine", "cimmerian", "copper",
    "dust", "halide", "iodine", "lanthanide", "magnetic",
    "maroon", "metal", "noble", "oolite", "plutonic",
    "radioactive", "selenic", "shattered", "telluric",
    "urea", "vinylogous", "xenolithic", "yttric", "alkali",
    "auric",
)
# Asteroids spawn at least this far from the planet center (prevents
# immediate-collision spawn).
ASTEROID_PLANET_BUFFER = 220.0
# And at least this far from either ship spawn (ship_x ± this).
ASTEROID_SHIP_SPAWN_BUFFER = 180.0

# Moon — when present, a smaller satellite orbits the planet on a
# circular path. Same collision and gravity treatment as the planet
# (scaled down). Per-fight toggle: ~50% of seeded fights get one.
MOON_RADIUS = 36.0
# Aaron's spec: 8 moon-diameters from the planet center. moon-diameter
# = MOON_RADIUS * 2, so orbit radius is 16 * MOON_RADIUS.
MOON_ORBIT_RADIUS = MOON_RADIUS * 16.0
# Angular speed (rad/s). One orbit takes ~30 game-seconds at 0.21 —
# slow enough to feel "almost static" within a single fight, fast
# enough that the position visibly changes over the 60s max.
MOON_ANGULAR_SPEED = 0.21
MOON_GRAVITY = PLANET_GRAVITY * 0.18   # ~ (MOON_RADIUS/PLANET_RADIUS)^2 = 0.26 — slightly weaker
MOON_COLLISION_DAMAGE = PLANET_COLLISION_DAMAGE * 0.6

# --- SC2-style battlefield camera (2026-05-18) ---
# Reference: references/uqm-source/sc2/src/uqm/process.c CalcReduction +
# CalcView. SC2 used a large logical play space (32× viewport) with the
# camera tracking the midpoint between the two ships and the zoom level
# computed from inter-ship distance. The planet wraps just like the
# ships do; it's just another object in the wrapping toroidal world.
#
# Our arena bounds (ARENA_W=1600, ARENA_H=1000) define the toroidal
# wrap; the camera fits a window of viewable area whose size depends on
# the ships' separation. When ships are close together, camera zooms in
# (high `camera_scale`); when they're far apart, camera pulls back (low
# scale) so both ships fit in the frame.
CAMERA_MIN_SCALE = 0.55         # max zoom-out — both ships visible at far distance
CAMERA_MAX_SCALE = 1.45         # max zoom-in  — close-quarters detail
# Target: ships should occupy at most this fraction of viewport — bigger
# value = more headroom (ships closer to center); smaller = tighter framing.
CAMERA_TARGET_FRAC = 0.55
# Smoothing factor per frame (60fps); lower = smoother / more lag.
CAMERA_LERP = 0.10
# Margin (world units) added to ship-distance when computing zoom so the
# camera doesn't tracking-jitter at the framing edge.
CAMERA_DIST_MARGIN = 220.0

# --- Tractor-lasso tunables (Persuader Vessel signature) ---
# Aaron's 2026-05-17 spec: hold-to-charge, release-to-fling. The
# Persuader catches an enemy and orbits at full thrust around them;
# release flings the target tangentially. Damage comes from the
# target slamming into a planet/asteroid after release.
LASSO_MAX_RANGE = 220.0              # how far the lasso can reach to latch
LASSO_ORBIT_RADIUS_PERSUADER = 95.0  # Persuader's orbit distance from center
LASSO_ORBIT_RADIUS_TARGET = 28.0     # captive's wobble radius (target as anchor)
LASSO_ORBITAL_SPEED = 4.6            # rad/sec — fast spin (Persuader thrusters max)
LASSO_FLING_MULTIPLIER = 1.6         # captive's release velocity multiplier
LASSO_ENERGY_PER_SEC = 4.0           # drain while latched; exhaustion = no-fling release
LASSO_RELEASE_COOLDOWN = 6.5         # seconds before next latch attempt
# On release, the Persuader keeps only this fraction of its orbit
# tangent velocity. The lighter ship at the end of the lasso is
# "pulling back to end the spin" — most of the kinetic energy
# transfers to the captive (which is the slingshot identity).
# Without this damper the Persuader's release speed is several
# multiples of its top_speed and it slams into the nearest planet.
LASSO_PERSUADER_RELEASE_FRAC = 0.30
# Energy threshold below which the Persuader AI auto-releases (to keep
# enough juice for an emergency phase_skip).
LASSO_AI_RELEASE_ENERGY_FRAC = 0.30

# Phase-skip tunable (Persuader special). Aaron's 2026-05-17 spec:
# short directional teleport in the ship's facing — skips OVER
# planets/ships/projectiles. Collision-immune during the jump (it's
# a teleport, not a dash).
PHASE_SKIP_DISTANCE = 140.0          # units forward

# Nebulae — colored gas clouds. Slow ships proportional to ship mass
# (heavies bog down, light ships barely notice — asymmetric meta lever
# that favors low-mass ships chasing high-mass ones). Projectiles pass
# through unaffected (gas doesn't stop kinetic shots).
NEBULA_COUNT_MAX = 3       # 0..N per fight, seeded
NEBULA_RADIUS_MIN = 150.0
NEBULA_RADIUS_MAX = 280.0
# Slow factor at the nebula's CENTER for a reference ship (mass=100).
# A mass-180 Defender hits ~1.8× this slow; a mass-55 Arilou hits ~0.55×.
NEBULA_REFERENCE_MASS = 100.0
NEBULA_CENTER_SLOW = 0.6   # at center, velocity is reduced to (1 - 0.6 * mass_factor) per damping
# Minimum velocity multiplier per frame — so even a heavy ship in a
# dense nebula slows over many frames, never instant-stops.
NEBULA_MIN_VELOCITY_FRAC = 0.25
# Palette options — picked per nebula at spawn for variety.
NEBULA_COLOR_OPTIONS: tuple[tuple[int, int, int], ...] = (
    (180,  90, 200),   # violet — Eta Carinae vibe
    (200, 120, 160),   # pink — Lagoon nebula
    ( 90, 130, 220),   # deep blue — reflection nebula
    ( 90, 200, 160),   # teal — green planetary nebula
    (220, 140,  90),   # warm orange — emission nebula
    (160, 100, 220),   # purple
)

# Background star — single distant sun-like body, visual only. Ships
# pass over it without collision. Adds light-source ambience to the
# arena without affecting gameplay. Positioned at a fixed offset from
# the planet so it reads as "the star this system orbits."
BG_STAR_OFFSET_X = -550.0    # negative = "off to the left"; wraps to right
BG_STAR_OFFSET_Y = -380.0    # negative = "up"; wraps to bottom
BG_STAR_RADIUS = 90.0
# Star color options (G/K/M class roughly). Picked per fight via seeded RNG.
BG_STAR_COLOR_OPTIONS: tuple[tuple[int, int, int], ...] = (
    (255, 230, 160),   # yellow G-type (Sol)
    (255, 200, 130),   # orange K-type
    (255, 160, 110),   # red M-type
    (200, 220, 255),   # blue-white F-type
    (255, 255, 230),   # white A-type
)

# Hyperspace warp-tunnel starfield. Replaces the static procedural
# starfield when arena_style=hyperspace. Streaks radiate outward from
# the arena center (Star Trek warp-flight vibe), with each streak
# tinted by a position-dependent blend between the player's warp
# bubble color (red — Furling signature) and the enemy's bubble color
# (from their ship's accent palette). Creates the "two bubbles closing
# for combat" visual hand-in-glove with the coaxial interference tunnel.
WARP_STAR_COUNT = 180
WARP_STAR_SPEED_MIN = 180.0       # u/s; closer to center = slower
WARP_STAR_SPEED_MAX = 480.0       # near edge — full streak feel
WARP_STAR_LENGTH_MIN = 6.0
WARP_STAR_LENGTH_MAX = 22.0
# Player ("us") warp bubble color — canonical Furling-side red. Aaron
# called this "our red warp bubble." Enemy color is derived per-fight
# from the homesteader ship's accent_color so each opponent has a
# visually distinct bubble.
WARP_BUBBLE_COLOR_PLAYER: tuple[int, int, int] = (220, 80, 80)


def _wrap_shortest_delta(a: float, b: float, axis: float) -> float:
    """Signed wrap-shortest distance from a to b on a toroidal axis.
    Result is in (-axis/2, axis/2]. Used by the gravity + collision
    physics to evaluate "where is the planet from here" correctly
    even when the ship is across the wrap edge from the planet.

    Note: there's also a method `MeleeCombatScene._wrap_delta` that
    does the same thing — kept as method for the projectile-hit-check
    code path; this module-level twin is for the physics code paths
    that don't have a scene instance handy (helpers called from
    _integrate / _update_projectiles).
    """
    d = b - a
    if d > axis / 2:
        d -= axis
    elif d < -axis / 2:
        d += axis
    return d

# Alpha-cutout ship sprite directory + per-ship-id filename map.
# Generated by tools/generate_ship_sprites.py from approved Firefly hero
# images. When a sprite is missing we fall back to the procedural polygon
# silhouette in _draw_ship — the existing code remains the safety net.
SHIP_SPRITE_DIR = os.path.join(
    "assets", "ships", "sprites",
)
SHIP_SPRITES: dict[str, str] = {
    "furling_scout":     "ship_furling_scout.png",
    "persuader_vessel":  "ship_persuader_vessel.png",
    "arilou_skiff":      "ship_arilou_skiff.png",
    "androsynth_cruiser":"ship_androsynth_cruiser.png",
    "burv_broadcaster":  "ship_burv_broadcaster.png",
    "cleanser_cruiser":  "ship_cleanser_cruiser.png",
    "compeller_vessel":  "ship_compeller_vessel.png",
    "melnorme_trader":   "ship_melnorme_trader.png",
    "defender_vessel":   "ship_defender_vessel.png",
    "lemmkin_skitter":   "ship_lemmkin_skitter.png",
    "mmrnmhrm_sentinel": "ship_mmrnmhrm_sentinel.png",
    "mycon_podship":     "ship_mycon_podship.png",
    "proto_ur_quan":     "ship_proto_urquan.png",
    "proto_qor_ah":      "ship_proto_qor_ah.png",
    "sentry_drone_47t":  "ship_sentry_drone_47t.png",
    "thinn_blade":       "ship_thinn_blade.png",
    "utwig_jugger":      "ship_utwig_jugger.png",
}
# Nominal sprite size in world units along the longest axis. Tuned so a
# sprite reads about the same size as the legacy polygon at typical
# viewport scale (~0.7 → ~36px on screen).
SHIP_SPRITE_BASE_SIZE = 56
# Fallback collision radius for ships without sprites (procedural-polygon
# fallback). Sprite-loaded ships derive a per-sprite radius from the
# non-transparent bounding box at load time.
SHIP_RADIUS_FALLBACK = 14.0


def _make_near_black_transparent(surface, threshold: int = 10) -> None:
    """Zero the alpha channel for pixels whose RGB are all below `threshold`.

    Many Firefly outputs come back with opaque black backgrounds rather
    than alpha-zero; this is the runtime fix that makes the visible
    silhouette the actual ship instead of a black square. Operates
    in-place on the surface.

    Uses pygame.surfarray when numpy is available (fast — vectorized
    mask over the pixel array). Falls back to a slow per-pixel Python
    loop if numpy isn't installed (only runs once per ship-class load).
    """
    try:
        import numpy as np  # noqa: F401
        arr_rgb = pygame.surfarray.pixels3d(surface)
        arr_alpha = pygame.surfarray.pixels_alpha(surface)
        mask = (
            (arr_rgb[..., 0] < threshold)
            & (arr_rgb[..., 1] < threshold)
            & (arr_rgb[..., 2] < threshold)
        )
        arr_alpha[mask] = 0
        del arr_rgb
        del arr_alpha
    except (ImportError, ValueError, pygame.error):
        # Slow fallback path.
        w, h = surface.get_size()
        for y in range(h):
            for x in range(w):
                px = surface.get_at((x, y))
                if px[0] < threshold and px[1] < threshold and px[2] < threshold:
                    surface.set_at((x, y), (0, 0, 0, 0))

# Per-ship projectile sprites live in the same dir keyed by ship_id —
# `projectile_<ship_id>.png`. Missing files fall back to the legacy
# colored-circle rendering. Authored as glowing FX on black background;
# tools/extract_projectile_alpha.py produces luma-alpha PNGs that
# composite correctly over the game's black play area.
PROJECTILE_SPRITE_BASE_SIZE = 28

# Projectile pool cap (slice — we won't approach this)
MAX_PROJECTILES = 200

# How long after fight-end before the scene auto-exits
FIGHT_END_DWELL = 2.5

# Damage smear constant — when shields take damage they refill more
# slowly while damage continues. We do this by resetting the regen
# cooldown each tick of damage taken.
SHIELD_HIT_REGEN_DELAY_RESET = True


@dataclass
class ShipState:
    """Runtime state of one ship in combat. The ShipClass is the read-only
    spec; this is the mutable counterpart.
    """
    cls: ShipClass
    side: str
    x: float
    y: float
    heading: float
    vx: float = 0.0
    vy: float = 0.0
    hull: float = 0.0
    shield: float = 0.0
    # One-shot SFX flags so the alert chimes fire on threshold crossing,
    # not every damage tick. Reset implicit-True (default False); set to
    # True the first time the threshold is crossed downward.
    alert_warning_fired: bool = False   # shield dropped < 25%
    alert_danger_fired: bool = False    # hull dropped < 25%
    energy: float = 0.0
    shield_regen_cooldown: float = 0.0
    primary_cooldown: float = 0.0
    alive: bool = True
    hit_flash: float = 0.0     # render flash on damage

    # --- Special-ability state (Phase 1.5 — first user is the Furling
    # Scout's inertia_halt; see ShipClass.special_ability). ---
    special_active: bool = False
    # vx/vy snapshot taken on special activate, restored on release.
    # Used by inertia_halt — the ship's pre-halt motion is preserved
    # and returned when the player lets go.
    special_saved_vx: float = 0.0
    special_saved_vy: float = 0.0
    # Cooldown timer — counts down while > 0; special unavailable until 0.
    special_cooldown_left: float = 0.0
    # Seconds the held-special has been active in this hold. Used by
    # specials with a `special_duration` cap (Aaron 2026-05-17: specials
    # don't drain weapon energy anymore — held abilities are capped by
    # duration instead). Reset to 0 on each activation; force-release
    # triggers when this exceeds cls.special_duration (if non-zero).
    special_held_elapsed: float = 0.0

    # --- Cross-ship-imposed effect states ---
    # forced_halt_remaining: seconds left of externally-applied inertia
    # halt (Compeller's "compel" power forces this on the enemy). While
    # > 0, the ship's velocity zeros each frame in _integrate.
    forced_halt_remaining: float = 0.0
    # adware_remaining: seconds left of Melnorme adware-pulse exposure.
    # The target's HUD has been blasted with Grand Shopping Super Mart
    # pop-ups; their pilot is busy clicking close-X buttons and the
    # autopilot is steering them toward the nearest "store" (in-arena
    # = nearest asteroid). While > 0: AI doesn't fire, turns toward
    # nearest asteroid (or planet if none), accelerates.
    adware_remaining: float = 0.0
    # Lemmkin latch state. When latched_to_id > 0, this ship sticks to
    # the target ship's position with a small offset and damages it
    # over time. Releases when the target's energy maxes out.
    latched_to_id: int = 0
    latched_offset_x: float = 0.0
    latched_offset_y: float = 0.0
    # Per-frame flag — set during the AI step when this ship's heading
    # aligns with its enemy (green target-lock pip lit). Thinn's
    # edge-invisibility reads this: while on-target, incoming
    # projectiles miss.
    on_target_this_frame: bool = False
    # gatling_barrel: Utwig gatling-laser barrel rotation counter.
    # Each fire increments this; the pattern uses it modulo 3 to
    # pick which of three barrels is firing (left / center / right
    # offset) — gives the visible alternating cadence.
    gatling_barrel: int = 0
    # engine_damage_accumulated: permanent slowdown applied to this
    # ship by Defender engine-seeker missile hits. Subtracts from
    # effective top_speed + acceleration (each clamped to a minimum
    # floor so a ship is never fully immobile). Resets per fight.
    engine_damage_accumulated: float = 0.0
    # wetness: 0..100 buildup from Cleanser water-spray hits. The
    # Cleanser's `freeze` special checks this to determine if the
    # target is wet enough to be frozen in place. Drains slowly
    # over time when not being soaked.
    wetness: float = 0.0
    # frozen_remaining: seconds left of Cleanser-induced freeze.
    # While > 0: ship cannot move AND cannot fire. Water hits do
    # 3x damage (ice cracks split the hull). Colliding with a
    # planet / moon / asteroid while frozen deals BIG damage
    # (60 hp burst — meant to be a positional kill).
    frozen_remaining: float = 0.0
    # ice_buildup: 0..100 accumulator from Cleanser water-spike
    # outer-spike hits on a WET ship (wetness >= 30). When this
    # reaches 100, the ship freezes automatically — equivalent to
    # the special-freeze trigger. The optimal Cleanser combo: wet
    # close, freeze with special OR back up and spike-freeze, then
    # spike-crack. Drains slowly when not being spiked.
    ice_buildup: float = 0.0
    # xform_active_form: form id for ships with xform_alt. 0 = base
    # cls, 1 = alt cls. Mmrnmhrm: 0 = laser fighter, 1 = missile jet.
    xform_active_form: int = 0
    # xform_base_cls: stored reference to the base ship class so we
    # can revert from alt form. Set on first xform activation.
    xform_base_cls: "ShipClass | None" = None

    # --- Scout module-mod effects (Aaron 2026-05-18 mod catalog) ---
    # Behavior-flag deltas cached at spawn time from
    # game.effective_stat() so the combat hot path doesn't reach back
    # into game state every frame. All default to 0 for ships that
    # aren't the player's modded Scout.
    #
    # mod_damage_reduction: 0.0..0.95 — Crystalline Plating flat
    # reduction. Multiplies incoming damage by (1 - reduction).
    mod_damage_reduction: float = 0.0
    # mod_bounce_chance: 0.0..1.0 — Reactive Plating probability per
    # hit that the projectile bounces off without damage. Sampled at
    # apply_damage time.
    mod_bounce_chance: float = 0.0
    # mod_hull_regen_passive: HP/sec — Repair Drone slow auto-heal.
    # Applied in _regen.
    mod_hull_regen_passive: float = 0.0
    # mod_ablative_remaining: HP — Ablative Coating sacrificial layer.
    # First damage of the fight goes here until depleted; doesn't
    # regen during combat. Initialized from `ablative_pool` delta.
    mod_ablative_remaining: float = 0.0
    # mod_engine_damage_on_hit: per primary-shot engine-debuff applied
    # to enemy via Engine Disruptor Coil mod. Defender's missile uses
    # this hardcoded; the mod lets the Scout's beam do the same.
    mod_engine_damage_on_hit: float = 0.0
    # --- 2026-05-18 functional-mod overhaul (Aaron: "no boring upgrades") ---
    # All Scout mod-effect deltas/flags below — populated at on_enter
    # by _init_scout_mod_effects from game.effective_stat. Each one
    # corresponds to a Scout mod whose deltas dict declares the same
    # key. 0.0 / 0 / False = mod not installed (no-op).
    mod_chain_lightning_damage: float = 0.0     # child-bolt damage from primary hits
    mod_reflect_chance: float = 0.0             # shield hits bounce back
    mod_thorn_pulse_radius: float = 0.0         # shield absorption radial damage
    mod_thorn_pulse_frac: float = 0.0           # fraction of absorbed damage emitted
    mod_crash_damage_frac: float = 1.0          # multiplier on body-collision self-damage
    mod_crash_push_mult: float = 0.0            # asteroid push velocity multiplier
    mod_afterburners: bool = False              # sustained thrust ignites boost
    mod_inertia_dump: bool = False              # reverse-thrust zeros velocity
    mod_strafing_jets_force: float = 0.0        # lateral impulse per turn frame
    mod_capacitor_surge: bool = False           # next-shot 3x when energy full
    mod_cross_wired_ratio: float = 0.0          # primary fire → shield regen
    mod_phase_shift_hull_threshold: float = 0.0 # auto-phase-shift on hull drop
    mod_energy_absorb_frac: float = 0.0         # laser/beam damage reduction
    mod_hit_negate_interval: float = 0.0        # first-hit-per-N-sec ignored
    mod_lance_charge_max_dmg: float = 0.0       # Furling Coil Lance charge cap
    mod_pulse_stack_bonus: float = 0.0          # Pulse Cannon stacking damage
    # --- Crew-perk hooks (2026-05-18 functional crew overhaul) ---
    mod_primary_energy_reduction: float = 0.0   # Bren-Vor normal: shots cost less energy
    mod_kill_stack_damage: float = 0.0          # Bren-Vor post-quest: damage per kill
    mod_combat_start_shield_overcharge: float = 0.0  # Yelena post-quest: 1+x shield at fight start
    mod_cooldown_reduce_per_hit: float = 0.0    # Mira normal: special-cd shaved per primary hit
    mod_hit_negate_first_per_fight: bool = False  # Warden normal: 1st hit per fight ignored
    # Per-fight crew-perk state
    kills_this_fight: int = 0
    first_hit_negated_used: bool = False
    # --- Runtime state for the above behaviors (combat-only) ---
    # Afterburners
    afterburner_thrust_held: float = 0.0        # seconds of continuous thrust
    afterburner_active_remaining: float = 0.0   # seconds of boost left
    afterburner_cooldown_remaining: float = 0.0
    # Capacitor surge — armed when energy hits max
    surge_armed: bool = False
    # Phase shift — one-shot per fight when hull crosses threshold
    phase_shift_used: bool = False
    phase_shift_active_remaining: float = 0.0
    # Hit-negate timer (Arilou Phase Dampener)
    hit_negate_cooldown_remaining: float = 0.0
    # Pulse Cannon stacking damage — per-target counter (target id → stacks)
    pulse_stacks: dict = field(default_factory=dict)
    # Coil Lance charge-up state
    coil_lance_charge_held: float = 0.0
    coil_lance_was_firing: bool = False

    # --- AI posture (per-fight individual variation) ---
    # Per Aaron 2026-05-17: combat AIs should "not always behav[e]
    # the same, but don't adopt limp/ineffective postures." Three
    # effective postures rolled at spawn time:
    #   "AGGRESSIVE" — closes harder, fires at wider angles, no
    #                  shield-retreat. Good vs slow shooters.
    #   "PRECISE"    — patient at ideal distance, narrower fire
    #                  cone (waits for clean shots), shield-retreat
    #                  honored. Good vs fast brawlers.
    #   "EVASIVE"    — constant lateral strafing during exchanges,
    #                  takes hits less, slightly farther engagement
    #                  distance. Good vs heavy hitters.
    # Sentry-drone (left_only) keeps its canonical no-posture flag
    # via ai_style override; postures only apply to combat-capable
    # ai_styles. Stored as a string for AI dispatch readability.
    posture: str = "balanced"

    # --- Tractor-lasso state (Persuader Vessel signature weapon) ---
    # Aaron's 2026-05-17 spec: hold-to-charge, release-to-fling. While
    # held, the Persuader thrusts to max around its lassoed target;
    # release flings the target at high speed in the tangential
    # direction of the orbit at the moment of release. Damage comes
    # from the target slamming into a planet/asteroid post-fling.
    #
    # lasso_target_id: id() of the ship being lassoed (the captive).
    # 0 = no active lasso. While > 0, _update_lasso owns this ship's
    # position; standard _apply_action/_integrate are skipped.
    lasso_target_id: int = 0
    # lassoed_by_id: set on the CAPTIVE side while it's whirled.
    # While > 0, the captive's AI returns a no-op for movement (still
    # allowed to turn + fire — Aaron: "making it hard for them to hit
    # you", implying they're trying). Position is forced by the lasso
    # owner's orbit physics.
    lassoed_by_id: int = 0
    # Frozen orbit center, set at latch and unchanged through the swing.
    lasso_orbit_cx: float = 0.0
    lasso_orbit_cy: float = 0.0
    # Persuader's angle around the orbit center (rad). Advances each
    # frame at LASSO_ORBITAL_SPEED.
    lasso_orbit_angle: float = 0.0
    # Seconds the lasso has been active in the current hold. Used by
    # AI to time releases (the fling damage requires hitting something,
    # so holding too long just wastes energy + makes the captive's
    # tangent rotate past the hazard). Resets to 0 on latch / release.
    lasso_hold_elapsed: float = 0.0

    @classmethod
    def spawn(cls, ship_cls: ShipClass, x: float, y: float, heading: float) -> "ShipState":
        return cls(
            cls=ship_cls,
            side=ship_cls.side,
            x=x, y=y, heading=heading,
            hull=ship_cls.hull_max,
            shield=ship_cls.shield_max,
            energy=ship_cls.energy_max,
        )

    def apply_damage(self, amount: float, damage_kind: str = "kinetic") -> None:
        """Apply incoming damage. Shields absorb first, then hull.

        `damage_kind`: optional tag used by mods that care about the
        category of incoming damage. Currently supported:
        - "kinetic" (default) — bullets, missiles, plasma, collisions
        - "energy" — beams, lasers, scatter, lance, twin, single
          (anything from the hitscan/beam patterns)

        Cross-ability hooks:
        - Thinn edge-invisibility: ignored when nose-on-target.
        - Utwig absorb_shield: converts to energy.
        - Scout mod stack (Aaron 2026-05-18 functional overhaul):
          Phase Shift, Arilou Hit-Negate, Mmrnmhrm Energy Absorb,
          Reactive Plating bounce, Crystalline reduction, Thorn pulse,
          Ablative pool. Resolved in roughly that order.
        """
        if amount <= 0 or not self.alive:
            return
        # Scout mod: Dimensional Armor — phase-shift on hull crit. If
        # this hit would drop hull below threshold AND we haven't
        # used the phase shift yet this fight, grant 1.5s of
        # invulnerability instead.
        if (
            self.mod_phase_shift_hull_threshold > 0
            and not self.phase_shift_used
            and self.phase_shift_active_remaining <= 0
        ):
            crit_threshold = self.cls.hull_max * self.mod_phase_shift_hull_threshold
            would_drop_below = (
                (self.hull - max(0, amount - self.shield)) < crit_threshold
            )
            if would_drop_below:
                self.phase_shift_used = True
                self.phase_shift_active_remaining = 1.5
                self.hit_flash = 0.25
                return
        # Crew perk: Furling Warden — first damaging hit of the fight
        # is fully negated. One-shot per fight (resets between fights
        # because ShipState is fresh-spawned per MeleeCombatScene).
        if (
            self.mod_hit_negate_first_per_fight
            and not self.first_hit_negated_used
        ):
            self.first_hit_negated_used = True
            self.hit_flash = 0.18
            return
        # Scout mod: Arilou Phase Dampener — first damaging hit each
        # N seconds is fully negated. Sustained DPS still bites.
        if (
            self.mod_hit_negate_interval > 0
            and self.hit_negate_cooldown_remaining <= 0
        ):
            self.hit_negate_cooldown_remaining = self.mod_hit_negate_interval
            self.hit_flash = 0.12
            return
        # Scout mod: Phase Shift active = invulnerable
        if self.phase_shift_active_remaining > 0:
            return
        # Scout mod: Mmrnmhrm Reinforced Plating — energy/beam damage
        # is heavily reduced (First-Maker doctrine).
        if (
            damage_kind == "energy"
            and self.mod_energy_absorb_frac > 0
        ):
            amount *= max(0.05, 1.0 - self.mod_energy_absorb_frac)
        # Thinn edge-invisibility — short-circuit the damage
        if (
            self.cls.id == "thinn_blade"
            and self.on_target_this_frame
        ):
            self.hit_flash = 0.10
            return
        # Scout mod: Reactive Plating bounce chance — sampled per hit.
        if self.mod_bounce_chance > 0.0:
            import random as _random
            if _random.random() < self.mod_bounce_chance:
                self.hit_flash = 0.15
                return
        # Scout mod: Crystalline Plating flat damage reduction.
        if self.mod_damage_reduction > 0.0:
            amount *= max(0.05, 1.0 - self.mod_damage_reduction)
        # Scout mod: Ablative Coating — sacrificial pool.
        if self.mod_ablative_remaining > 0.0:
            absorbed = min(self.mod_ablative_remaining, amount)
            self.mod_ablative_remaining -= absorbed
            amount -= absorbed
            self.hit_flash = 0.18
            if amount <= 0:
                return
        # Utwig absorb_shield — convert incoming damage to energy
        if (
            self.cls.special_ability == "absorb_shield"
            and self.special_active
        ):
            energy_gain = amount * 0.8
            self.energy = min(self.cls.energy_max, self.energy + energy_gain)
            residual = amount * 0.2
            self.hit_flash = 0.12
            amount = residual
            if amount <= 0:
                return
        self.hit_flash = 0.25
        shield_absorbed = 0.0
        if self.shield > 0:
            shield_absorbed = min(self.shield, amount)
            self.shield -= shield_absorbed
            amount -= shield_absorbed
            if SHIELD_HIT_REGEN_DELAY_RESET:
                self.shield_regen_cooldown = self.cls.shield_regen_delay
            # Scout mod: Thorn Shield — when shield absorbs damage,
            # emit a radial pulse that hurts nearby enemies. The
            # actual radial-sweep is in scene-level code; here we
            # just flag the absorbed amount on the ship for the
            # scene's per-frame thorn-resolve to consume.
            if self.mod_thorn_pulse_radius > 0 and shield_absorbed > 0:
                # We don't have scene access here. The scene reads
                # this via `_pending_thorn_pulse_amount` after
                # apply_damage returns.
                self._pending_thorn_pulse_amount = (
                    getattr(self, "_pending_thorn_pulse_amount", 0.0)
                    + shield_absorbed * self.mod_thorn_pulse_frac
                )
        if amount > 0:
            self.hull -= amount
            if self.hull <= 0:
                self.hull = 0
                self.alive = False


@dataclass
class Asteroid:
    """Movable indestructible hazard. Drifts through the arena, swayed
    by planet gravity. Collides with ships (damage + bounce) and
    absorbs projectiles. Color is a deterministic gray-brown variation
    seeded per asteroid so the field reads varied at a glance.

    2026-05-18 sprite refactor: each asteroid carries a `sprite_key`
    naming an `assets/planets/*-sml-000.png` to use as its visual
    art — 50+ UQM-style small-planet sprites get reused as varied
    asteroid art. `rotation_deg` is per-asteroid for visual variety;
    `spin_rate_deg_per_s` rotates each asteroid slowly while drifting.
    """
    x: float
    y: float
    vx: float
    vy: float
    radius: float
    color: tuple[int, int, int]
    sprite_key: str = ""           # e.g. "chondrite", "metal", "shattered"
    rotation_deg: float = 0.0      # current orientation
    spin_rate_deg_per_s: float = 0.0  # spin while drifting


@dataclass
class Nebula:
    """Static colored gas cloud. Slows ships inside it proportional to
    ship mass (heavies are penalized more — small fast ships gain a
    chasing advantage). Projectiles pass through unaffected. No
    collision; ships overlap freely.

    Visual: layered alpha-blended soft circles for a hazy-cloud look.
    """
    x: float
    y: float
    radius: float
    color: tuple[int, int, int]


@dataclass
class ThrusterParticle:
    """One puff of dissipating engine exhaust. Emitted from a ship's
    tail each frame the ship is actively thrusting. Pure visual — no
    physics interaction with anything (gravity-immune to keep behavior
    legible; real-gas dynamics aren't worth the complexity at these
    speeds).

    The particle grows in radius and fades in alpha over its lifetime,
    giving the "gas dissipating into vacuum" look. Color is hot at
    spawn (engine-glow tint) and unchanged through its life — the
    fade is alpha-only, which reads as "becoming transparent" rather
    than "cooling," appropriate for vented gas.
    """
    x: float
    y: float
    vx: float
    vy: float
    lifetime: float       # total seconds before despawn
    base_radius: float    # starting world-unit radius
    color: tuple[int, int, int]
    age: float = 0.0


# Thruster trail tunables. The trail is one of those features that
# reads better tuned conservatively — too many particles and it
# becomes visual noise; too few and ships read as silent gliders.
THRUSTER_EMIT_PER_FRAME = 2          # particles per ship per tick while thrusting
THRUSTER_PARTICLE_LIFETIME_MIN = 0.45  # seconds
THRUSTER_PARTICLE_LIFETIME_MAX = 0.95
THRUSTER_PARTICLE_RADIUS_MIN = 2.8    # world units at spawn
THRUSTER_PARTICLE_RADIUS_MAX = 4.5
THRUSTER_PARTICLE_RADIUS_GROW = 2.0   # multiplier at end-of-life vs spawn
THRUSTER_EXIT_SPEED = 90.0            # u/s ejection speed relative to ship
THRUSTER_LATERAL_JITTER = 18.0        # +/- u/s random spread
THRUSTER_DRAG_PER_SEC = 0.55          # velocity multiplier per second
THRUSTER_TAIL_OFFSET = 14.0           # how far behind ship center the emit point sits
# Hard cap to prevent runaway particle counts on long fights.
THRUSTER_PARTICLE_CAP = 400


@dataclass
class WarpStar:
    """One streaking star in the hyperspace warp-tunnel backdrop.
    Pure visual — no physics interaction with ships or projectiles.
    Originates near the arena center and streaks outward; when off
    arena it respawns near center with a new direction.
    """
    x: float
    y: float
    vx: float
    vy: float
    brightness: int   # 0..255, modulates the final tint
    base_length: float   # streak length added to distance-scaled component


@dataclass
class Projectile:
    x: float
    y: float
    vx: float
    vy: float
    damage: float
    range_left: float   # max distance before despawn
    owner_side: str
    color: tuple[int, int, int]
    owner_ship_id: str = ""   # used to look up projectile_<id>.png sprite
    radius: float = 3.0
    # Homing — when True, projectile turns toward the enemy each frame
    # at `homing_turn_rate` radians/sec. Used by Melnorme plasmoids;
    # default False keeps the projectile straight.
    homing: bool = False
    homing_turn_rate: float = 0.0
    # Multi-hit — number of additional hits before despawn. 0 = standard
    # (despawn on first contact). Used by Androsynth bubbles (SC2 canon:
    # 3 hits before pop).
    hits_remaining: int = 0
    # Returning ("RHC" — Returning Howitzer Cannon, Kohr-Ah). After
    # `return_at_age` seconds, velocity flips and projectile becomes
    # owner-side neutral (it'll hit either ship on the way back).
    # 0.0 = non-returning.
    return_at_age: float = 0.0
    age: float = 0.0
    has_returned: bool = False
    # Orbital — bound to a ship at a fixed orbital radius, NOT integrated
    # as a free projectile. Used by Kohr-Ah FRIED blades. When set, the
    # owner_ship is the host; the projectile's (orbital_angle, radius)
    # define its position relative to the host's center.
    orbital: bool = False
    orbital_host_id: int = 0   # python id() of host ShipState
    orbital_angle: float = 0.0
    orbital_radius: float = 0.0
    orbital_angular_speed: float = 0.0
    # is_blade: when True, orbital_angle is interpreted as an OFFSET
    # from the host's heading (so the blade tracks ship orientation).
    # The hit detection samples 3 points along the blade line (base /
    # mid / tip) so the hit zone is the BLADE itself, not a disc — fly
    # past a blade's broadside at the right moment and you miss it.
    # Aaron's spec 2026-05-17: "two large blades that spring out,
    # static, hit-box only on the blades."
    is_blade: bool = False
    # is_gravity_well: stationary projectile (vx=vy=0) that persists
    # for `lifetime` seconds and damages any enemy ship within its
    # radius continuously per tick. Used by the Compeller's gravity-
    # well weapon. Aaron's spec 2026-05-17: "form on top of a stopped
    # enemy and it does damage over time, or place somewhere for the
    # enemy to fly through."
    is_gravity_well: bool = False
    lifetime: float = 0.0   # seconds until despawn (0 = no time limit)
    # spawn_debris_on_hit: when a projectile is removed on contact,
    # spawns N visual-only "ship debris" particles flying outward from
    # the impact point. Used by the Burv resonance pulse — the target
    # vibrates a piece of itself off on every hit.
    spawn_debris_on_hit: bool = False
    # is_resonance_wave: Burv Broadcaster's full-map-range wavefront.
    # The projectile grows in radius over time (wave_growth_per_sec)
    # and its damage falls off proportionally with distance traveled
    # (wave_damage_floor sets the minimum at max range). Renders as a
    # curved arc/wavefront perpendicular to direction of travel rather
    # than a disc. Owner is immune via the standard owner_side check.
    # Aaron 2026-05-19 spec: "curved wave that gets bigger and weaker
    # the further it goes ... immune to their own weapon ... long
    # range, like full map length."
    is_resonance_wave: bool = False
    wave_growth_per_sec: float = 0.0
    wave_damage_floor: float = 0.25
    # homing_delay: when > 0, the projectile flies straight for this
    # many seconds AFTER spawn before its `homing` flag activates.
    # Used by Proto-Ur-Quan's homing_cluster special — missiles
    # spread out from the launch arc, THEN start tracking the enemy.
    homing_delay: float = 0.0
    # engine_damage_on_hit: when > 0, hitting a ship adds this much
    # to that ship's engine_damage_accumulated (permanent slow).
    # Used by Defender engine_seeker missile.
    engine_damage_on_hit: float = 0.0
    # is_chaff: when True, projectile is a stationary chaff cloud that
    # slows enemy projectiles passing through it (Defender chaff_spray).
    is_chaff: bool = False
    # is_water: Cleanser water-spray droplet. Pushes asteroids (without
    # damaging them), adds wetness to ships, doesn't damage as much as
    # standard projectiles. At water_freeze_at_age, it converts to ice
    # (is_water -> False, color shifts to icy blue) and continues
    # flying as a normal low-damage projectile.
    is_water: bool = False
    water_freeze_at_age: float = 0.0
    # initial_range: range_left at spawn time. Used to compute the
    # "fraction traveled" for mechanics that care about whether the
    # projectile is near the start or far end of its flight. Cleanser
    # water spray cracking a frozen ship: only the OUTER SPIKES (i.e.,
    # droplets at the far end of their range — fired from a distance)
    # split the ice for crack damage.
    initial_range: float = 0.0
    # is_icepeedo: Cleanser ice-torpedo. Replaces the SC2-canon ice
    # ray with a projectile. On hit (Aaron 2026-05-17):
    #   - dry target → small damage + significant wetness
    #   - wet target (wetness >= 30) → freeze (frozen_remaining=3.0)
    #     + small damage
    #   - frozen target → CRACK (4× damage; second icepeedo finishes
    #     the job, just like outer-spike water on frozen)
    is_icepeedo: bool = False
    # spin_visual: rate at which the projectile's visual rotation
    # increments per second (radians). Used for lawnmower-blade
    # projectiles + spinning-blade orbital ring; visual-only.
    spin_visual: float = 0.0
    spin_angle: float = 0.0
    # Damage category — "energy" (beams/lasers/scatter/lance/twin/
    # single/burst/tracking/gatling) or "kinetic" (missiles, plasma,
    # bubbles, water, blades, ramming). Read by Scout-mod hooks like
    # Mmrnmhrm Reinforced Plating's energy-weapon absorber.
    damage_kind: str = "kinetic"
    # Chain Lightning state — if > 0, on hit the projectile spawns a
    # child bolt aimed at the nearest OTHER target. Set on spawn by
    # ships with `mod_chain_lightning_damage > 0`. Decrements per
    # chain to bound the cascade.
    chain_remaining: int = 0
    chain_damage: float = 0.0   # damage of the child bolt


@dataclass
class ImpactFx:
    """Short-lived blast-puff at the point a projectile hit a ship.
    Tracked + rendered each frame, retired when t > duration.
    """
    x: float
    y: float
    t: float = 0.0
    duration: float = 0.35
    color: tuple[int, int, int] = (255, 200, 120)
    max_radius: float = 22.0


@dataclass
class DeathFx:
    """Ship-destruction animation: ring shockwave + colored debris
    radiating outward. Plays at the ship's last position for ~1.2 sec
    before the wreck-stub render takes over.
    """
    x: float
    y: float
    color: tuple[int, int, int]
    t: float = 0.0
    duration: float = 1.1
    # Per-debris seed so the particle pattern is deterministic per fx.
    seed: int = 0


@dataclass
class CombatResult:
    winner_side: str | None
    winner_ship: ShipClass | None
    loser_ship: ShipClass | None
    duration: float
    timed_out: bool


class MeleeCombatScene(Scene):
    """1v1 ship combat. Both ships AI-driven by default."""

    # Default to low-risk; runtime can swap to combat_high / combat_boss
    # when those tracks land + when the combat AI flags stakes.
    music_context = "combat_low"  # assets/music/combat_low/

    def __init__(
        self,
        precursor_ship: ShipClass,
        homesteader_ship: ShipClass,
        max_duration: float = 60.0,
        on_finish: Callable[[CombatResult], None] | None = None,
        seed: int | None = None,
        # Arena style — ARENA_STYLE_SOLAR_SYSTEM (default, planet + maybe
        # moon) or ARENA_STYLE_HYPERSPACE (coaxial interference tunnel,
        # no moon). Hyperspace encounters (Cleanser patrol, etc.) pass
        # the hyperspace style so the central body reads as a tunnel,
        # not a planet.
        arena_style: str = ARENA_STYLE_SOLAR_SYSTEM,
        # Arena-furniture overrides. Pass True/False to FORCE the moon
        # on/off for narrative fights (e.g. the Cleanser climax could
        # be set in a binary-system encounter and force moon=True).
        # None means "seeded random — ~50% of fights get a moon."
        # Ignored when arena_style=hyperspace (always moonless).
        moon: bool | None = None,
        # Pass an explicit count to override the random asteroid count.
        # Useful for scenario fights ("dense asteroid field"), test
        # cases ("zero asteroids for deterministic balance"), or the
        # tutorial sentry-drone fight (clean arena).
        asteroids: int | None = None,
        planet_id: str | None = None,
    ) -> None:
        super().__init__()
        self.max_duration = max_duration
        self.on_finish = on_finish
        # When combat is happening "near planet X", pass the planet's
        # id so the combat backdrop shows the same rotating sphere as
        # the orbit/system views did. Visual continuity across the
        # transition.
        self.planet_id = planet_id
        # A per-fight RNG so spawns aren't pixel-perfect identical each
        # run — Aaron specifically wants "somewhat but not perfectly
        # predictable" outcomes. The seed comes from the wall clock if
        # not provided.
        self.rng = random.Random(seed) if seed is not None else random.Random()

        # Spawn at opposite ends, facing each other, with a little jitter
        margin = 200.0
        spread_y = 200.0
        p_y = ARENA_H / 2 + self.rng.uniform(-spread_y, spread_y)
        h_y = ARENA_H / 2 + self.rng.uniform(-spread_y, spread_y)
        self.precursor = ShipState.spawn(
            precursor_ship, margin, p_y, heading=math.pi / 2  # facing +x
        )
        self.homesteader = ShipState.spawn(
            homesteader_ship, ARENA_W - margin, h_y, heading=-math.pi / 2  # facing -x
        )
        # Roll per-fight AI postures. Both ships pick INDEPENDENTLY
        # so the same matchup plays differently across runs — Aaron's
        # "not always behaving the same" variation requirement. The
        # Sentry Drone keeps its canonical posture-less behavior so
        # the tutorial fight stays predictable for the player.
        self.precursor.posture = self._roll_posture(precursor_ship)
        self.homesteader.posture = self._roll_posture(homesteader_ship)

        # Scout mod-effect hookup happens in on_enter after self.game
        # is wired — __init__ runs before set_scene attaches the game.

        self.projectiles: list[Projectile] = []
        # Thruster exhaust particles — emitted from ship tails while
        # thrusting, drift + fade out. Pure visual layer.
        self.thruster_particles: list[ThrusterParticle] = []
        # Transient radial-wave visuals (Burv resonance_burst). Each
        # entry: {"x", "y", "radius", "age", "lifetime", "color"}.
        # Drawn as expanding ring; lifetime expiry removes it.
        self._burst_visuals: list[dict] = []

        # --- Arena style + furniture (planet/tunnel, moon, asteroids) ---
        self.arena_style = arena_style
        # Moon: per-fight seeded toggle unless explicitly overridden.
        # Hyperspace fights are ALWAYS moonless (the coaxial interference
        # tunnel is a singular phenomenon — no satellite makes sense
        # diegetically).
        if arena_style == ARENA_STYLE_HYPERSPACE:
            self.has_moon = False
        elif moon is None:
            self.has_moon = self.rng.random() < 0.5
        else:
            self.has_moon = bool(moon)
        # Moon starts at a random angle (seeded) so different fights
        # have it in different positions even when toggled on.
        self.moon_angle: float = self.rng.uniform(0.0, math.tau)
        # Cache so we don't recompute the cos/sin every frame.
        self._refresh_moon_position()

        # Asteroids: spawned in random positions outside the planet
        # buffer and away from both ship spawn positions, with a
        # random drift velocity. Gravity acts on them so the field
        # evolves over the fight — they swing around the planet,
        # cross the arena via wrap, etc.
        n_asteroids = (
            self.rng.randint(ASTEROID_COUNT_MIN, ASTEROID_COUNT_MAX)
            if asteroids is None else asteroids
        )
        self.asteroids: list[Asteroid] = self._spawn_asteroids(n_asteroids, margin)

        # Nebulae: 0..NEBULA_COUNT_MAX, seeded. Tactical hazards that
        # slow heavy ships more than light ones — asymmetric meta lever.
        n_nebulae = self.rng.randint(0, NEBULA_COUNT_MAX)
        self.nebulae: list[Nebula] = self._spawn_nebulae(n_nebulae, margin)

        # Background star — visual only, no collision. Positioned at a
        # fixed offset from the planet center (wraps if it goes off the
        # arena edge, which it intentionally does — looks "off to the
        # side from the inhabited zone"). Color seeded per fight.
        # Solar-system style only; the warp tunnel replaces it in
        # hyperspace.
        self.bg_star_x = (PLANET_X + BG_STAR_OFFSET_X) % ARENA_W
        self.bg_star_y = (PLANET_Y + BG_STAR_OFFSET_Y) % ARENA_H
        self.bg_star_color = self.rng.choice(BG_STAR_COLOR_OPTIONS)

        # Warp-tunnel starfield — only populated in hyperspace style.
        # Streaks emanate from arena center; the enemy color is sampled
        # from the homesteader ship's accent_color so each matchup has
        # a distinct visual signature for the bubble-interference look.
        if self.arena_style == ARENA_STYLE_HYPERSPACE:
            self.warp_stars: list[WarpStar] = self._spawn_warp_stars(
                WARP_STAR_COUNT,
            )
            self.warp_enemy_color: tuple[int, int, int] = (
                homesteader_ship.accent_color
            )
        else:
            self.warp_stars = []
            self.warp_enemy_color = (255, 255, 255)

        self.impact_fx: list[ImpactFx] = []
        self.death_fx: list[DeathFx] = []
        # Tracks which ships we've already spawned a death FX for, so
        # we don't double-spawn when both projectile + cleanup paths
        # observe the alive=False transition.
        self._death_fx_spawned: set[str] = set()
        # Last scene-time a ship's fire SFX played (dedupes multi-shot).
        self._fire_sfx_stamp: dict[str, float] = {}

        # Scene-time
        self.time_in_scene: float = 0.0
        self.result: CombatResult | None = None
        self.time_since_result: float = 0.0

        # SC2-style camera state. Initialized to arena center at scale 1.0
        # — the first call to _update_camera() snaps to the target on
        # frame zero so we don't see a zoom-in animation at fight start.
        self.camera_x: float = ARENA_W / 2
        self.camera_y: float = ARENA_H / 2
        self.camera_scale: float = 1.0
        self._camera_initialized: bool = False

        # Sprite + effective-radius caches. Headless sim paths bypass
        # on_enter, so these must exist from __init__ to satisfy the
        # _effective_radius lookups in _update_projectiles.
        self._ship_sprite_cache: dict = {}
        self._ship_effective_radius: dict = {}

        # Set in on_enter
        self.font: pygame.font.Font | None = None
        self.big_font: pygame.font.Font | None = None
        self.screen_w: int = 0
        self.screen_h: int = 0

    # ------------------------------------------------------------------
    # Scene API
    # ------------------------------------------------------------------

    def on_enter(self) -> None:
        assert self.game is not None
        # Scout mod-effect snapshot — done now (game is wired here).
        self._init_scout_mod_effects(self.precursor)
        self._init_scout_mod_effects(self.homesteader)
        self.screen_w, self.screen_h = self.game.screen.get_size()
        self.font = pygame.font.SysFont("consolas", 18)
        self.big_font = pygame.font.SysFont("consolas", 36, bold=True)
        # Sprite cache keyed by ship.cls.id. None = sprite missing / failed.
        self._ship_sprite_cache: dict[str, pygame.Surface | None] = {}
        # Per-ship effective collision radius — populated by
        # _load_ship_sprite from the non-transparent bounding box. Falls
        # back to SHIP_RADIUS_FALLBACK for ships without sprites.
        self._ship_effective_radius: dict[str, float] = {}
        # Authored-starfield override — drop a PNG at this path and the
        # render method will blit it as the arena backdrop instead of
        # running the procedural cross-star scatter. The Image chat owns
        # this asset (see references/lore/HANDOFF_image_chat.md entry
        # "Combat-arena starfield backdrop"). Loader is tolerant of
        # missing files; falls back to procedural silently.
        self._starfield_image: pygame.Surface | None = None
        from pathlib import Path
        assets_combat_dir = (
            Path(__file__).resolve().parent.parent.parent.parent
            / "assets" / "combat"
        )
        sf_path = assets_combat_dir / "starfield.png"
        if sf_path.exists():
            try:
                self._starfield_image = pygame.image.load(str(sf_path)).convert()
            except pygame.error:
                self._starfield_image = None
        # Hyperspace tunnel — central-body sprite for arena_style=hyperspace.
        # See references/lore/HANDOFF_image_chat.md "Hyperspace combat —
        # coaxial interference tunnel" for the spec. Loader is tolerant
        # of missing files; falls back to a procedural concentric-ring
        # render in `_draw_central_body` so playability never depends on
        # the image being present.
        self._tunnel_image: pygame.Surface | None = None
        if self.arena_style == ARENA_STYLE_HYPERSPACE:
            tunnel_path = assets_combat_dir / "hyperspace_tunnel.png"
            if tunnel_path.exists():
                try:
                    self._tunnel_image = pygame.image.load(
                        str(tunnel_path),
                    ).convert_alpha()
                except pygame.error:
                    self._tunnel_image = None
        self._projectile_sprite_cache: dict[str, pygame.Surface | None] = {}

    def snapshot(self) -> dict | None:
        # Combat is intentionally NOT rewindable — committing to a fight
        # is committing. Time Drive rewinds you to BEFORE the combat
        # started, not partway through.
        return None

    def update(self, dt: float, inp) -> None:  # type: ignore[no-untyped-def]
        self.time_in_scene += dt

        if self.result is not None:
            # Fight is over — dwell briefly, then finish.
            self.time_since_result += dt
            if self.time_since_result >= FIGHT_END_DWELL:
                self._finish()
            return

        # --- Moon orbit (before ships so they read the moon's current
        # position when computing gravity/collision/AI).
        if self.has_moon:
            self.moon_angle = (self.moon_angle + MOON_ANGULAR_SPEED * dt) % math.tau
            self._refresh_moon_position()

        # --- Asteroid drift (also before ships so collision uses the
        # asteroid's post-tick position).
        self._integrate_asteroids(dt)

        # --- Warp tunnel (hyperspace style only — visual, no physics
        # impact on ships/projectiles).
        if self.warp_stars:
            self._update_warp_stars(dt)

        # --- Orbital projectiles (Kohr-Ah FRIED discs) — track their
        # host ship's position. Done before standard projectile motion
        # so their next-frame position is used for hit checks below.
        self._update_orbital_projectiles(dt)

        # --- Burst visuals (Burv resonance_burst) — age + cull.
        if self._burst_visuals:
            survivors = []
            for bv in self._burst_visuals:
                bv["age"] += dt
                if bv["age"] < bv["lifetime"]:
                    survivors.append(bv)
            self._burst_visuals = survivors

        # --- Build the AI obstacle list once per frame (shared by
        # both ships' decide() calls; identical for both since they
        # both see the same arena state).
        obstacles: list[tuple[float, float, float]] = [
            (PLANET_X, PLANET_Y, PLANET_RADIUS),
        ]
        if self.has_moon:
            obstacles.append((self.moon_x, self.moon_y, MOON_RADIUS))
        for ast in self.asteroids:
            obstacles.append((ast.x, ast.y, ast.radius))
        obstacles_tuple = tuple(obstacles)

        # --- Per-ship update ---
        for me, other in (
            (self.precursor, self.homesteader),
            (self.homesteader, self.precursor),
        ):
            if not me.alive:
                continue
            # Build the incoming-hostile-projectiles list for special
            # decision (defensive specials like inertia_halt scan
            # incoming threats). Cheap: usually <10 projectiles in
            # flight at any moment.
            incoming = tuple(
                (p.x, p.y, p.vx, p.vy, p.radius)
                for p in self.projectiles
                # Hostile + linear-motion projectiles only. Orbital
                # discs (FRIED) move in circles, not linearly — the
                # AI's straight-line collision prediction would
                # misjudge them.
                if p.owner_side != me.side and not p.orbital
            )
            action = decide(
                me, other,
                obstacles=obstacles_tuple,
                incoming_projectiles=incoming,
            )
            # Tractor-lasso state machine. Runs every frame regardless
            # of fire button state — needs to detect release. Owns the
            # Persuader's position while a lasso is active and the
            # captive's position too. No-op for any other ship class.
            self._update_lasso(me, action.fire_primary, dt)
            # Apply special FIRST (it can zero velocity, which affects
            # _apply_action's thrust integration).
            self._update_ship_special(me, action.fire_special, dt)
            # Skip _apply_action / _integrate for ships under lasso
            # control. Either side: the Persuader (owning the orbit)
            # has its position written by _update_lasso, and the
            # captive (lassoed_by_id != 0) is positionally locked too.
            # Both still get _regen (a captive Furling regenerates
            # shields normally — only their movement is controlled).
            if me.lasso_target_id != 0 or me.lassoed_by_id != 0:
                self._regen(me, dt)
                if me.hit_flash > 0:
                    me.hit_flash = max(0.0, me.hit_flash - dt)
                # Even while lassoed, the captive can still fire their
                # primary (they're trying to shoot the spinning Persuader).
                # The Persuader cannot fire primary the normal way
                # because its primary IS the lasso (handled in
                # _update_lasso); _fire_primary is a no-op for the
                # tractor_lasso pattern anyway.
                if me.lassoed_by_id != 0 and action.fire_primary:
                    self._fire_primary(me)
                continue
            self._apply_action(me, action, dt)
            self._integrate(me, dt)
            self._regen(me, dt)
            if action.thrust and not me.special_active:
                # Don't emit thruster gas while inertia-halted —
                # engines aren't pushing the ship, they're locked.
                self._emit_thruster_particles(me)
            if action.fire_primary:
                self._fire_primary(me)
            # Resolve any pending Thorn Shield pulse — done at the end
            # of the per-ship pass so we hit enemies AFTER all damage
            # has been booked this frame.
            if (
                me.mod_thorn_pulse_radius > 0
                and getattr(me, "_pending_thorn_pulse_amount", 0.0) > 0
            ):
                self._emit_thorn_pulse(me)
            if me.hit_flash > 0:
                me.hit_flash = max(0.0, me.hit_flash - dt)

        # --- Thruster particle drift + cull (after ship updates so
        # newly-emitted particles get one frame of motion before render).
        self._update_thruster_particles(dt)

        # --- Projectiles ---
        self._update_projectiles(dt)

        # --- SC2-style camera update: follow midpoint between ships,
        # zoom from inter-ship distance. Done after ship updates so the
        # camera reads post-tick positions.
        self._update_camera()

        # --- Combat FX ---
        for fx in self.impact_fx:
            fx.t += dt
        self.impact_fx = [fx for fx in self.impact_fx if fx.t < fx.duration]
        for fx in self.death_fx:
            fx.t += dt
        self.death_fx = [fx for fx in self.death_fx if fx.t < fx.duration]

        # --- Win detection ---
        if not self.precursor.alive and self.homesteader.alive:
            self._record_result(self.homesteader, self.precursor)
        elif not self.homesteader.alive and self.precursor.alive:
            self._record_result(self.precursor, self.homesteader)
        elif not self.precursor.alive and not self.homesteader.alive:
            # Double-KO. Call it a draw by treating Precursor as not winning.
            self._record_result(None, None)
        elif self.time_in_scene >= self.max_duration:
            # Timeout — whoever has more total HP wins. Near-ties
            # (within 3% of the larger score) are broken by the RNG
            # rather than always favoring Precursor — that bias was a
            # sim artifact where same-side fights all "wonby Ship A".
            p_score = self.precursor.hull + self.precursor.shield
            h_score = self.homesteader.hull + self.homesteader.shield
            margin = abs(p_score - h_score)
            threshold = 0.03 * max(p_score, h_score, 1.0)
            if margin <= threshold:
                # Near-tie — coin flip
                p_wins = self.rng.random() < 0.5
            else:
                p_wins = p_score > h_score
            if p_wins:
                self._record_result(self.precursor, self.homesteader, timed_out=True)
            else:
                self._record_result(self.homesteader, self.precursor, timed_out=True)

    # ------------------------------------------------------------------
    # Arena furniture helpers (planet, moon, asteroids)
    # ------------------------------------------------------------------

    def _refresh_moon_position(self) -> None:
        """Recompute the moon's x/y from its current angle. Called
        every frame the moon exists. Wraps around the arena so a moon
        whose orbit is partly outside the arena bounds correctly
        appears on the opposite edge — same toroidal logic as the
        ships.
        """
        self.moon_x = (PLANET_X + math.cos(self.moon_angle) * MOON_ORBIT_RADIUS) % ARENA_W
        self.moon_y = (PLANET_Y + math.sin(self.moon_angle) * MOON_ORBIT_RADIUS) % ARENA_H

    def _spawn_warp_stars(self, n: int) -> list[WarpStar]:
        """Initial warp-tunnel star scatter. Stars start at varied
        distances from center so the field is already populated on
        frame 1 — without this you'd see them streaming out from a
        single point for the first second of combat.
        """
        cx = ARENA_W / 2
        cy = ARENA_H / 2
        out: list[WarpStar] = []
        for _ in range(n):
            ang = self.rng.uniform(0, math.tau)
            # Initial distance distribution biased toward "spread across
            # the visible arena" rather than all near center.
            dist = self.rng.uniform(20.0, ARENA_W * 0.55)
            x = cx + math.cos(ang) * dist
            y = cy + math.sin(ang) * dist
            speed = self.rng.uniform(
                WARP_STAR_SPEED_MIN, WARP_STAR_SPEED_MAX,
            )
            vx = math.cos(ang) * speed
            vy = math.sin(ang) * speed
            length = self.rng.uniform(
                WARP_STAR_LENGTH_MIN, WARP_STAR_LENGTH_MAX,
            )
            brightness = self.rng.randint(120, 240)
            out.append(WarpStar(
                x=x, y=y, vx=vx, vy=vy,
                brightness=brightness, base_length=length,
            ))
        return out

    def _update_warp_stars(self, dt: float) -> None:
        """Advance each warp star outward. When a star leaves the arena
        bounds, respawn it near the center with a new random angle and
        speed — gives the continuous tunnel-flow effect without an
        ever-growing star count.
        """
        cx = ARENA_W / 2
        cy = ARENA_H / 2
        for star in self.warp_stars:
            star.x += star.vx * dt
            star.y += star.vy * dt
            # Off-arena (no wrap for the warp tunnel — these are visual,
            # they read better re-spawning near center as a fresh streak)
            if (
                star.x < -50 or star.x > ARENA_W + 50
                or star.y < -50 or star.y > ARENA_H + 50
            ):
                ang = self.rng.uniform(0, math.tau)
                dist = self.rng.uniform(15.0, 60.0)
                star.x = cx + math.cos(ang) * dist
                star.y = cy + math.sin(ang) * dist
                speed = self.rng.uniform(
                    WARP_STAR_SPEED_MIN, WARP_STAR_SPEED_MAX,
                )
                star.vx = math.cos(ang) * speed
                star.vy = math.sin(ang) * speed
                star.brightness = self.rng.randint(120, 240)
                star.base_length = self.rng.uniform(
                    WARP_STAR_LENGTH_MIN, WARP_STAR_LENGTH_MAX,
                )

    def _emit_thruster_particles(self, ship: ShipState) -> None:
        """Spawn THRUSTER_EMIT_PER_FRAME exhaust particles at the ship's
        tail. Particle velocity inherits a fraction of the ship's
        velocity (so they fall behind it naturally) plus a backward
        push along the ship's heading + lateral jitter (gas plume
        spread). Color is the ship's hull_color (its identity tint)
        lifted toward hot-white so the plume reads as glowing exhaust
        while still carrying the ship's signature color — Cruiser
        runs amber-orange, Skiff runs teal, Proto-Ur-Quan runs deep-
        blue, etc. (Previous build pulled from accent_color which on
        a few ships was near-black; the plume read as dirty gray.)
        """
        cls = ship.cls
        # Ship's tail is opposite the heading direction.
        # Recall: scene physics treats heading=0 as "up", so:
        #   forward unit = (sin(h), -cos(h))
        #   backward unit = (-sin(h), cos(h))
        back_x = -math.sin(ship.heading)
        back_y = math.cos(ship.heading)
        tail_x = ship.x + back_x * THRUSTER_TAIL_OFFSET
        tail_y = ship.y + back_y * THRUSTER_TAIL_OFFSET
        # Hot-engine tint: lift hull_color toward white. R+G bias is
        # slightly heavier than B so the plume reads warmer than the
        # cold paint of the hull (engines = combustion, not paint).
        # min-floor of 80 keeps dark-hulled ships (Mmrnmhrm deep blue,
        # Mycon burgundy) visible against the black arena background.
        # Same color for all particles in this puff so a sequence reads
        # as a coherent plume.
        hue = cls.hull_color
        hot = (
            min(255, max(hue[0], 80) + 50),
            min(255, max(hue[1], 80) + 50),
            min(255, max(hue[2], 80) + 30),
        )
        for _ in range(THRUSTER_EMIT_PER_FRAME):
            jitter_x = self.rng.uniform(
                -THRUSTER_LATERAL_JITTER, THRUSTER_LATERAL_JITTER,
            )
            jitter_y = self.rng.uniform(
                -THRUSTER_LATERAL_JITTER, THRUSTER_LATERAL_JITTER,
            )
            self.thruster_particles.append(ThrusterParticle(
                x=tail_x + self.rng.uniform(-3.0, 3.0),
                y=tail_y + self.rng.uniform(-3.0, 3.0),
                # Particle velocity = ship's velocity (partial inherit)
                # + backward push + lateral jitter. Ships moving forward
                # leave particles that visually fall behind them.
                vx=ship.vx * 0.4 + back_x * THRUSTER_EXIT_SPEED + jitter_x,
                vy=ship.vy * 0.4 + back_y * THRUSTER_EXIT_SPEED + jitter_y,
                lifetime=self.rng.uniform(
                    THRUSTER_PARTICLE_LIFETIME_MIN,
                    THRUSTER_PARTICLE_LIFETIME_MAX,
                ),
                base_radius=self.rng.uniform(
                    THRUSTER_PARTICLE_RADIUS_MIN,
                    THRUSTER_PARTICLE_RADIUS_MAX,
                ),
                color=hot,
            ))
        # Hard cap — keep the last N particles. New particles are added
        # at the tail so old ones get dropped first; visually the cap is
        # invisible during normal play but prevents pathological growth.
        if len(self.thruster_particles) > THRUSTER_PARTICLE_CAP:
            del self.thruster_particles[:-THRUSTER_PARTICLE_CAP]

    def _update_thruster_particles(self, dt: float) -> None:
        """Age + integrate position + cull expired thruster particles.
        Drag applies a slight velocity decay each tick so plumes don't
        fly off forever — they cool and pool. Arena wraps just like
        ships.
        """
        if not self.thruster_particles:
            return
        # Continuous drag factor: vel(t+dt) = vel(t) * drag_per_sec^dt
        drag = THRUSTER_DRAG_PER_SEC ** dt
        survivors: list[ThrusterParticle] = []
        for p in self.thruster_particles:
            p.age += dt
            if p.age >= p.lifetime:
                continue
            p.x = (p.x + p.vx * dt) % ARENA_W
            p.y = (p.y + p.vy * dt) % ARENA_H
            p.vx *= drag
            p.vy *= drag
            survivors.append(p)
        self.thruster_particles = survivors

    def _render_thruster_particles(
        self, screen: pygame.Surface,
        ox: float, oy: float, scale: float,
    ) -> None:
        """Draw each particle as an alpha-blended soft circle. Radius
        grows over the particle's lifetime and alpha fades to zero,
        giving the "dissipating gas" look. Particles are independent
        surfaces — at THRUSTER_PARTICLE_CAP=400 that's a manageable
        draw count.
        """
        if not self.thruster_particles:
            return
        for p in self.thruster_particles:
            sx, sy = self._world_to_screen(p.x, p.y, ox, oy, scale)
            life_frac = p.age / p.lifetime  # 0..1
            # Radius grows toward end-of-life — visualizes expansion
            radius_world = p.base_radius * (
                1.0 + life_frac * (THRUSTER_PARTICLE_RADIUS_GROW - 1.0)
            )
            radius_px = int(radius_world * scale)
            if radius_px < 1:
                continue
            # Alpha: peaks at ~spawn-ish (15% of life — let the spawn
            # frames build first), then linearly fades to 0.
            if life_frac < 0.15:
                alpha = int(220 * (life_frac / 0.15))
            else:
                alpha = int(220 * (1.0 - (life_frac - 0.15) / 0.85))
            if alpha < 12:
                continue
            surf_size = radius_px * 2 + 4
            surf = pygame.Surface((surf_size, surf_size), pygame.SRCALPHA)
            pygame.draw.circle(
                surf, (*p.color, alpha),
                (radius_px + 2, radius_px + 2), radius_px,
            )
            screen.blit(
                surf,
                (int(sx) - radius_px - 2, int(sy) - radius_px - 2),
            )

    def _spawn_nebulae(self, n: int, ship_spawn_margin: float) -> list[Nebula]:
        """Place n nebulae. Rejects positions that overlap the planet
        (would mask the central anchor) or either ship spawn (instant
        slow-stun would be unfair). Asteroid overlap is fine — they
        co-exist with nebulae.
        """
        out: list[Nebula] = []
        attempts = 0
        ship_spawn_a_x = ship_spawn_margin
        ship_spawn_b_x = ARENA_W - ship_spawn_margin
        while len(out) < n and attempts < 40:
            attempts += 1
            radius = self.rng.uniform(NEBULA_RADIUS_MIN, NEBULA_RADIUS_MAX)
            x = self.rng.uniform(radius * 0.3, ARENA_W - radius * 0.3)
            y = self.rng.uniform(radius * 0.3, ARENA_H - radius * 0.3)
            # Reject near-planet overlap
            pdx = _wrap_shortest_delta(x, PLANET_X, ARENA_W)
            pdy = _wrap_shortest_delta(y, PLANET_Y, ARENA_H)
            if pdx * pdx + pdy * pdy < (PLANET_RADIUS + radius * 0.8) ** 2:
                continue
            # Reject ships getting bogged at spawn
            if abs(x - ship_spawn_a_x) < radius * 0.7:
                continue
            if abs(x - ship_spawn_b_x) < radius * 0.7:
                continue
            color = self.rng.choice(NEBULA_COLOR_OPTIONS)
            out.append(Nebula(x=x, y=y, radius=radius, color=color))
        return out

    def _spawn_asteroids(self, n: int, ship_spawn_margin: float) -> list[Asteroid]:
        """Place n asteroids at safe positions. Rejects positions too
        close to the planet (instant-collision spawn would be bad) or
        too close to either ship's spawn position (ships shouldn't be
        born inside an asteroid). Uses the fight RNG so re-runs of the
        same seed are reproducible.
        """
        out: list[Asteroid] = []
        attempts = 0
        ship_spawn_a_x = ship_spawn_margin
        ship_spawn_b_x = ARENA_W - ship_spawn_margin
        while len(out) < n and attempts < 60:
            attempts += 1
            x = self.rng.uniform(40.0, ARENA_W - 40.0)
            y = self.rng.uniform(40.0, ARENA_H - 40.0)
            radius = self.rng.uniform(ASTEROID_RADIUS_MIN, ASTEROID_RADIUS_MAX)
            # Reject near-planet spawn
            pdx = _wrap_shortest_delta(x, PLANET_X, ARENA_W)
            pdy = _wrap_shortest_delta(y, PLANET_Y, ARENA_H)
            if pdx * pdx + pdy * pdy < (ASTEROID_PLANET_BUFFER + radius) ** 2:
                continue
            # Reject near-moon spawn (if moon present)
            if self.has_moon:
                mdx = _wrap_shortest_delta(x, self.moon_x, ARENA_W)
                mdy = _wrap_shortest_delta(y, self.moon_y, ARENA_H)
                if mdx * mdx + mdy * mdy < (MOON_RADIUS + radius + 80.0) ** 2:
                    continue
            # Reject near-ship-spawn (either side)
            if abs(x - ship_spawn_a_x) < ASTEROID_SHIP_SPAWN_BUFFER:
                continue
            if abs(x - ship_spawn_b_x) < ASTEROID_SHIP_SPAWN_BUFFER:
                continue
            # Random drift velocity (slow — they're drifting, not racing)
            ang = self.rng.uniform(0, math.tau)
            speed = self.rng.uniform(ASTEROID_DRIFT_MIN, ASTEROID_DRIFT_MAX)
            vx = math.cos(ang) * speed
            vy = math.sin(ang) * speed
            # Gray-brown variation
            gray = self.rng.randint(110, 170)
            warm = self.rng.randint(-20, 25)
            color = (
                max(0, min(255, gray + warm)),
                max(0, min(255, gray + warm // 2)),
                max(0, min(255, gray - 10)),
            )
            # Per-asteroid sprite + rotation (2026-05-18 art refactor)
            sprite_key = self.rng.choice(ASTEROID_SPRITE_KEYS)
            rotation_deg = self.rng.uniform(0.0, 360.0)
            spin_rate = self.rng.uniform(-25.0, 25.0)
            out.append(Asteroid(
                x=x, y=y, vx=vx, vy=vy, radius=radius, color=color,
                sprite_key=sprite_key,
                rotation_deg=rotation_deg,
                spin_rate_deg_per_s=spin_rate,
            ))
        return out

    def _render_warp_tunnel(
        self, screen: pygame.Surface,
        ox: float, oy: float, scale: float,
    ) -> None:
        """Hyperspace warp-tunnel backdrop — streaking stars radiating
        outward from arena center, tinted by a left-to-right blend
        between the player's red warp bubble color and the enemy ship's
        accent color. Replaces the static starfield in hyperspace
        combat. The two color zones meet near the center, suggesting
        the interference surface where the bubbles overlap.

        Per-frame: cheap iteration over WARP_STAR_COUNT particles,
        each drawn as a short streak (tail toward center, head outward).
        """
        cx_w = ARENA_W / 2
        cy_w = ARENA_H / 2
        cx_s, cy_s = self._world_to_screen(cx_w, cy_w, ox, oy, scale)
        pl = WARP_BUBBLE_COLOR_PLAYER
        en = self.warp_enemy_color
        # Maximum distance from arena center for tint normalization
        max_norm = ARENA_W * 0.5
        for star in self.warp_stars:
            sx, sy = self._world_to_screen(star.x, star.y, ox, oy, scale)
            # Direction from center to star (in WORLD space, not screen).
            wdx = star.x - cx_w
            wdy = star.y - cy_w
            wd = math.hypot(wdx, wdy) or 1.0
            # Position-based tint blend. The x coordinate dominates the
            # gradient (ships sit on x = margin and x = ARENA_W - margin)
            # so a left/right gradient maps cleanly. We bias by sign(wdx)
            # so a star at the very left of the arena is 100% player
            # color, very right is 100% enemy. Smooth blend in between.
            t = max(0.0, min(1.0, (star.x / ARENA_W)))
            # Brightness falloff toward arena edges adds the "warp depth"
            # feel — the streaks that just spawned at center are bright;
            # those about to exit are slightly faded.
            depth = min(1.0, wd / max_norm)
            edge_fade = 1.0 - 0.35 * max(0.0, depth - 0.7) / 0.3
            edge_fade = max(0.45, edge_fade)
            r = int((pl[0] * (1.0 - t) + en[0] * t) * (star.brightness / 255.0) * edge_fade)
            g = int((pl[1] * (1.0 - t) + en[1] * t) * (star.brightness / 255.0) * edge_fade)
            b = int((pl[2] * (1.0 - t) + en[2] * t) * (star.brightness / 255.0) * edge_fade)
            color = (
                max(0, min(255, r)),
                max(0, min(255, g)),
                max(0, min(255, b)),
            )
            # Streak — tail points BACK toward arena center, head is
            # the star's current position. Length scales with distance
            # from center: closer = short dot, farther = long streak
            # (proper warp-flight feel).
            length_factor = star.base_length + depth * 28.0
            tail_len_px = length_factor * scale
            ux = wdx / wd
            uy = wdy / wd
            tx = sx - ux * tail_len_px
            ty = sy - uy * tail_len_px
            pygame.draw.line(
                screen, color,
                (int(tx), int(ty)), (int(sx), int(sy)),
                1,
            )
            # Bright head dot when the star is far out (heads near
            # center are too close to the tunnel mouth to read)
            if depth > 0.15:
                pygame.draw.circle(
                    screen, color, (int(sx), int(sy)), 1,
                )

    def _draw_planet(
        self, screen: pygame.Surface, cx: int, cy: int, r: int,
    ) -> None:
        """Solar-system central body. Aaron 2026-05-18: use Firefly-
        rendered planet PNGs from `assets/generated_drafts/firefly/
        tier1_planets/` instead of procedural circles. The planet for
        a given fight is picked deterministically from the per-fight
        RNG so re-running a seed gets the same planet but seed-to-seed
        varies. Procedural circle is kept as the fallback when no
        planet PNG can be loaded.
        """
        planet_surf = self._get_planet_sprite()
        if planet_surf is not None:
            # Cache the per-radius scaled surface (radius can change as
            # the camera zoom changes, so we cache by integer pixel
            # diameter for cheap reuse across frames at the same zoom).
            diameter = max(8, r * 2)
            cached = getattr(self, "_planet_scaled_cache", None)
            if cached is None or cached[0] != diameter:
                scaled = pygame.transform.smoothscale(
                    planet_surf, (diameter, diameter),
                )
                self._planet_scaled_cache = (diameter, scaled)
            screen.blit(
                self._planet_scaled_cache[1],
                (cx - diameter // 2, cy - diameter // 2),
            )
            return
        # --- Procedural fallback (per-fight seeded color) ---
        if getattr(self, "_planet_color", None) is None:
            hue_r = self.rng.randint(80, 200)
            hue_g = self.rng.randint(60, 180)
            hue_b = self.rng.randint(60, 200)
            self._planet_color = (hue_r, hue_g, hue_b)
            self._planet_outline = (
                min(255, hue_r + 60),
                min(255, hue_g + 60),
                min(255, hue_b + 80),
            )
        for i in range(3):
            glow_r = r + 6 + i * 4
            glow_alpha = 60 - i * 18
            if glow_alpha > 0:
                glow_surf = pygame.Surface(
                    (glow_r * 2 + 4, glow_r * 2 + 4), pygame.SRCALPHA,
                )
                pygame.draw.circle(
                    glow_surf, (*self._planet_color, glow_alpha),
                    (glow_r + 2, glow_r + 2), glow_r,
                )
                screen.blit(
                    glow_surf, (cx - glow_r - 2, cy - glow_r - 2),
                )
        pygame.draw.circle(screen, self._planet_color, (cx, cy), r)
        pygame.draw.circle(screen, self._planet_outline, (cx, cy), r, 2)

    def _get_asteroid_sprite(self, sprite_key: str) -> "pygame.Surface | None":
        """Load + cache a `<key>-sml-000.png` asteroid sprite from
        `assets/planets/`. Returns None if file missing / load failed
        (caller falls back to procedural circle).

        2026-05-18: leverages the existing 50+ UQM-style small planet
        sprites in `assets/planets/` as a cheap-and-varied asteroid
        art library. Each asteroid carries a `sprite_key` set at spawn.
        """
        if not sprite_key:
            return None
        cache = getattr(self, "_asteroid_sprite_cache", None)
        if cache is None:
            cache = {}
            self._asteroid_sprite_cache = cache
        if sprite_key in cache:
            return cache[sprite_key]
        path = os.path.join(
            "assets", "planets", f"{sprite_key}-sml-000.png",
        )
        if not os.path.isfile(path):
            cache[sprite_key] = None
            return None
        try:
            img = pygame.image.load(path).convert_alpha()
            # The UQM small-planet sprites have opaque-black backgrounds
            # outside the disc. Use the same near-black-to-transparent
            # trick as ship + planet sprites for a clean silhouette.
            _make_near_black_transparent(img, threshold=12)
        except (pygame.error, OSError):
            cache[sprite_key] = None
            return None
        cache[sprite_key] = img
        return img

    def _get_planet_sprite(self) -> "pygame.Surface | None":
        """Load + cache the central-body planet sprite for this fight.

        Picks a planet deterministically from `self.rng` on first call
        so the choice is stable across the fight's lifetime. Returns
        None if no planet PNG is available (procedural fallback path).

        2026-05-18: pool now combines BOTH sprite libraries:
        - `assets/generated_drafts/firefly/tier1_planets/*.png` — 9
          hand-crafted Firefly portraits (1280×1280, gorgeous detail)
        - `assets/planets/*-big-000.png` — 57 UQM-style pixel-art
          planets (75×67, lots of variety: rocky / gas / jewel-toned
          / radioactive / etc.)

        Firefly portraits are 7× more likely to be picked per pool
        weight (the iconic-named ones look more like a planet you'd
        recognize); the UQM pool gives variety for any-other fight.
        """
        cached = getattr(self, "_planet_sprite_cached", "UNSET")
        if cached != "UNSET":
            return cached
        # Pool 1: Firefly portraits
        firefly_dir = os.path.join(
            "assets", "generated_drafts", "firefly", "tier1_planets",
        )
        firefly = []
        if os.path.isdir(firefly_dir):
            firefly = [
                os.path.join(firefly_dir, f)
                for f in os.listdir(firefly_dir)
                if f.endswith(".png") and "_v1" not in f and "_misread" not in f
            ]
        # Pool 2: UQM pixel-art planets (*-big-000.png subset).
        uqm_dir = os.path.join("assets", "planets")
        uqm = []
        if os.path.isdir(uqm_dir):
            uqm = [
                os.path.join(uqm_dir, f)
                for f in os.listdir(uqm_dir)
                if f.endswith("-big-000.png")
            ]
        # Weighted pool: each Firefly entry counted 7x, each UQM once.
        # Then a single rng.choice picks. Skips empty pools cleanly.
        weighted: list[str] = []
        for p in firefly:
            weighted.extend([p] * 7)
        weighted.extend(uqm)
        if not weighted:
            self._planet_sprite_cached = None
            return None
        pick = self.rng.choice(sorted(weighted))
        try:
            img = pygame.image.load(pick).convert_alpha()
            # Both pools have black background outside the disc — same
            # near-black-to-transparent trick as ship/asteroid sprites.
            _make_near_black_transparent(img, threshold=12)
        except (pygame.error, OSError):
            self._planet_sprite_cached = None
            return None
        self._planet_sprite_cached = img
        return img

    def _draw_hyperspace_tunnel(
        self, screen: pygame.Surface, cx: int, cy: int, r: int,
    ) -> None:
        """Hyperspace coaxial-interference-tunnel central body. The
        interference figure formed between two hyperspace bubbles
        closing for combat — diegetically the same role as a planet
        (gravity anchor + collision body) without diegetically being
        a planet.

        Visual treatment, in priority order:
        1. Authored Firefly image at `assets/combat/hyperspace_tunnel.png`
           (see HANDOFF_image_chat.md) — blitted scaled to the body
           radius.
        2. Procedural fallback — concentric pulsing violet-cyan rings,
           slowly rotating, suggesting layered interference and
           "looking into a tunnel." Holds the slot until the image
           lands.
        """
        if self._tunnel_image is not None:
            # Scale authored image to a square covering the tunnel
            # disc. Cache the scaled surface to avoid re-scaling each
            # frame.
            size = r * 2
            cached = getattr(self, "_tunnel_scaled", None)
            if cached is None or cached[0] != size:
                scaled = pygame.transform.smoothscale(
                    self._tunnel_image, (size, size),
                )
                self._tunnel_scaled = (size, scaled)
            screen.blit(self._tunnel_scaled[1], (cx - r, cy - r))
            return
        # --- Procedural fallback ---
        # Pulsing concentric rings — violet base, cyan accent. Subtle
        # rotation so it doesn't read static.
        ticks = pygame.time.get_ticks() / 1000.0
        pulse = (math.sin(ticks * 1.8) + 1) / 2   # 0..1 over ~3.5s
        # Outer glow (violet)
        for i in range(4):
            glow_r = r + 8 + i * 6
            glow_alpha = max(0, 70 - i * 14 - int(pulse * 18))
            if glow_alpha > 0:
                glow_surf = pygame.Surface(
                    (glow_r * 2 + 4, glow_r * 2 + 4), pygame.SRCALPHA,
                )
                pygame.draw.circle(
                    glow_surf, (140, 80, 220, glow_alpha),
                    (glow_r + 2, glow_r + 2), glow_r,
                )
                screen.blit(
                    glow_surf, (cx - glow_r - 2, cy - glow_r - 2),
                )
        # Tunnel core — dark center with concentric "tunnel rings"
        # giving the looking-down-a-tube feeling
        pygame.draw.circle(screen, (18, 6, 32), (cx, cy), r)
        # Outer ring (most visible)
        ring_color = (
            int(160 + pulse * 60),
            int(80 + pulse * 50),
            int(220 + pulse * 30),
        )
        pygame.draw.circle(screen, ring_color, (cx, cy), r, 3)
        # Inner concentric rings — alpha falls off toward center
        n_rings = 6
        for i in range(1, n_rings):
            inner_r = int(r * (n_rings - i) / n_rings)
            inner_alpha = int(150 * (i / n_rings) + pulse * 30)
            if inner_r < 3 or inner_alpha < 20:
                continue
            ring_surf = pygame.Surface(
                (inner_r * 2 + 4, inner_r * 2 + 4), pygame.SRCALPHA,
            )
            ring_col = (
                100 + i * 18,
                60 + i * 14,
                180 + i * 10,
                inner_alpha,
            )
            pygame.draw.circle(
                ring_surf, ring_col,
                (inner_r + 2, inner_r + 2), inner_r, 1,
            )
            screen.blit(
                ring_surf, (cx - inner_r - 2, cy - inner_r - 2),
            )
        # Cyan accent spiral arms — two short diagonals across the
        # tunnel, rotating slowly. Reads as "interference fringes."
        rot = ticks * 0.4
        accent = (120, 220, 230)
        for arm_i in (0, 1):
            arm_angle = rot + arm_i * math.pi
            ax_end = cx + math.cos(arm_angle) * r * 0.55
            ay_end = cy + math.sin(arm_angle) * r * 0.55
            ax_start = cx - math.cos(arm_angle) * r * 0.55
            ay_start = cy - math.sin(arm_angle) * r * 0.55
            pygame.draw.line(
                screen, accent,
                (int(ax_start), int(ay_start)),
                (int(ax_end), int(ay_end)), 1,
            )

    def render(self, screen: pygame.Surface) -> None:
        screen.fill((4, 4, 14))

        # SC2-style camera — the world wraps invisibly; no visible
        # arena boundary. `scale` is the camera scale; ox/oy below are
        # legacy hand-off params for renderers that still take them
        # (the actual transformation is camera-driven inside
        # `_world_to_screen`).
        scale = self.camera_scale
        ox = 0.0
        oy = 0.0

        # Starfield backdrop. Three paths:
        # 1. **Hyperspace warp tunnel** — when arena_style=hyperspace,
        #    streaking stars radiate outward from arena center, tinted
        #    by a per-position gradient between the player's red warp
        #    bubble color and the enemy ship's accent color. Replaces
        #    everything below.
        # 2. **Authored starfield asset** — if Image chat has dropped a
        #    starfield PNG in `assets/combat/starfield.png`, we use that.
        # 3. **Procedural fallback** — SC2-style scattered points + cross
        #    stars + tiny galaxy swirls. Better than monochrome dots
        #    while we wait for the authored art.
        if self.arena_style == ARENA_STYLE_HYPERSPACE:
            self._render_warp_tunnel(screen, ox, oy, scale)
        elif self._starfield_image is not None:
            arena_w_px = max(1, int(ARENA_W * scale))
            arena_h_px = max(1, int(ARENA_H * scale))
            # Cache the scaled version per arena size (changes only on
            # window resize). Stored as (size, surface) to invalidate
            # cleanly when scale changes.
            cached = getattr(self, "_starfield_scaled", None)
            if cached is None or cached[0] != (arena_w_px, arena_h_px):
                scaled = pygame.transform.smoothscale(
                    self._starfield_image, (arena_w_px, arena_h_px),
                )
                self._starfield_scaled = ((arena_w_px, arena_h_px), scaled)
            screen.blit(self._starfield_scaled[1], (int(ox), int(oy)))
        else:
            # Procedural — deterministic seed so it doesn't shimmer
            rng = random.Random(101)
            for _ in range(220):
                sx = ox + rng.uniform(0, ARENA_W * scale)
                sy = oy + rng.uniform(0, ARENA_H * scale)
                b = rng.randint(40, 220)
                # Faint warm/cool tint based on parity of brightness —
                # cheap variety without lookups
                if b % 7 == 0:
                    color = (b, b // 2, b // 2)        # warm (red giant)
                elif b % 5 == 0:
                    color = (b // 2, b // 2, b)        # cool (blue)
                else:
                    color = (b * 2 // 3, b * 2 // 3, b)  # neutral
                pygame.draw.circle(screen, color, (int(sx), int(sy)), 1)
            # Bright cross-stars (the SC2 4-point sprites). 6-10 of them.
            n_cross = 8
            for _ in range(n_cross):
                cx = ox + rng.uniform(0, ARENA_W * scale)
                cy = oy + rng.uniform(0, ARENA_H * scale)
                tint = rng.choice([
                    (210, 230, 255),   # blue-white
                    (255, 230, 200),   # warm-white
                    (200, 240, 230),   # cool-white
                ])
                # Center bright pixel
                pygame.draw.circle(screen, tint, (int(cx), int(cy)), 2)
                # 4-point cross — 2px lines extending outward
                dim = (tint[0] // 2, tint[1] // 2, tint[2] // 2)
                pygame.draw.line(
                    screen, dim, (cx - 4, cy), (cx + 4, cy), 1,
                )
                pygame.draw.line(
                    screen, dim, (cx, cy - 4), (cx, cy + 4), 1,
                )

            # Distant galaxy swirls — tiny spiral patterns scattered
            # across the field. Faint, atmospheric; they read as
            # "background galaxies" through the lens of "we are very
            # far from them." 3-5 per arena, each a few-pixel logarithmic
            # spiral with subtle color tint.
            n_galaxies = rng.randint(3, 5)
            for _ in range(n_galaxies):
                gx = ox + rng.uniform(40, ARENA_W * scale - 40)
                gy = oy + rng.uniform(40, ARENA_H * scale - 40)
                tilt = rng.uniform(0, math.tau)
                # Pick a galaxy tint — most are pale-yellow (old stars)
                # but some are dusty blue (active star formation).
                galaxy_tint = rng.choice([
                    (200, 190, 160),   # pale yellow (most common)
                    (170, 180, 200),   # cool blue-white
                    (210, 180, 150),   # warm dusty
                    (160, 170, 200),   # cool
                ])
                # Bright core
                pygame.draw.circle(
                    screen, galaxy_tint, (int(gx), int(gy)), 1,
                )
                # Two spiral arms — small logarithmic spirals (8-12 steps)
                for arm in (0.0, math.pi):
                    n_steps = rng.randint(8, 12)
                    for step in range(n_steps):
                        t = step / n_steps
                        # Logarithmic spiral: r = a * exp(b*theta)
                        # We use small a/b so the spiral fits in ~6-10px
                        r_step = 1.0 + t * 8.0
                        theta = arm + tilt + t * 1.6
                        sx2 = gx + math.cos(theta) * r_step
                        sy2 = gy + math.sin(theta) * r_step
                        # Fade with distance from core
                        alpha = max(40, int(160 * (1.0 - t)))
                        # Render via a 1-px circle with a per-step
                        # color decay (we don't have alpha at the
                        # drawing call level here; approximate by
                        # darkening toward edges).
                        decay = (
                            int(galaxy_tint[0] * alpha / 255),
                            int(galaxy_tint[1] * alpha / 255),
                            int(galaxy_tint[2] * alpha / 255),
                        )
                        pygame.draw.circle(
                            screen, decay, (int(sx2), int(sy2)), 1,
                        )

        # Background star — visual-only, ships fly over it without
        # collision. Sits behind the planet/moon/asteroids and acts as
        # a distant light source / system reference. Drawn after the
        # starfield (so its glow can show through the dust) but before
        # the planet/moon/asteroids (so they occlude it cleanly).
        # Skipped in hyperspace style — the warp tunnel IS the
        # backdrop; a star wouldn't make sense.
        if self.arena_style != ARENA_STYLE_HYPERSPACE:
            bg_star_sx, bg_star_sy = self._world_to_screen(
                self.bg_star_x, self.bg_star_y, ox, oy, scale,
            )
            bg_star_sr = int(BG_STAR_RADIUS * scale)
            # Glow halo (multi-layer alpha decay)
            for i in range(5):
                halo_r = bg_star_sr + 8 + i * 12
                halo_alpha = 60 - i * 10
                if halo_alpha <= 0:
                    continue
                halo_surf = pygame.Surface(
                    (halo_r * 2 + 4, halo_r * 2 + 4), pygame.SRCALPHA,
                )
                pygame.draw.circle(
                    halo_surf, (*self.bg_star_color, halo_alpha),
                    (halo_r + 2, halo_r + 2), halo_r,
                )
                screen.blit(
                    halo_surf,
                    (int(bg_star_sx) - halo_r - 2,
                     int(bg_star_sy) - halo_r - 2),
                )
            # Bright core
            pygame.draw.circle(
                screen, self.bg_star_color,
                (int(bg_star_sx), int(bg_star_sy)), bg_star_sr,
            )

        # Nebulae — soft alpha-blended cloud regions. Drawn AFTER the
        # background star (so the star can light them from behind) and
        # AFTER the starfield (so stars don't shine through the gas)
        # but BEFORE the planet/asteroids/ships (which occlude the gas).
        for neb in self.nebulae:
            nsx, nsy = self._world_to_screen(neb.x, neb.y, ox, oy, scale)
            n_sr = int(neb.radius * scale)
            if n_sr < 4:
                continue
            # 4 concentric layers, decreasing radius + increasing alpha
            # toward the center, gives the soft falloff a real cloud has.
            for i, (r_frac, a) in enumerate(
                [(1.0, 28), (0.75, 36), (0.50, 44), (0.30, 52)],
            ):
                rr = max(2, int(n_sr * r_frac))
                cloud_surf = pygame.Surface(
                    (rr * 2 + 4, rr * 2 + 4), pygame.SRCALPHA,
                )
                pygame.draw.circle(
                    cloud_surf, (*neb.color, a),
                    (rr + 2, rr + 2), rr,
                )
                screen.blit(
                    cloud_surf,
                    (int(nsx) - rr - 2, int(nsy) - rr - 2),
                )

        # Central body — either the canonical planet (solar-system
        # style) or the coaxial interference tunnel (hyperspace style).
        # Position + collision physics are identical; only the visual
        # changes. The "hyperspace fights always have a planet" model
        # is preserved diegetically by the tunnel being a SC2-faithful
        # rationalization of the same arena geometry.
        center_sx, center_sy = self._world_to_screen(
            PLANET_X, PLANET_Y, ox, oy, scale,
        )
        center_sr = int(PLANET_RADIUS * scale)
        if self.arena_style == ARENA_STYLE_HYPERSPACE:
            self._draw_hyperspace_tunnel(
                screen, int(center_sx), int(center_sy), center_sr,
            )
        else:
            self._draw_planet(
                screen, int(center_sx), int(center_sy), center_sr,
            )

        # Moon (if present) — smaller cousin of the planet with the
        # same outline-ring treatment so the eye reads it as another
        # solid body.
        if self.has_moon:
            moon_sx, moon_sy = self._world_to_screen(
                self.moon_x, self.moon_y, ox, oy, scale,
            )
            moon_sr = int(MOON_RADIUS * scale)
            # Derive moon color as a paler/cooler variant of the planet
            # (it's the planet's child, visually). When the planet is a
            # sprite (not procedural-color), pick a neutral pale-grey
            # for the moon since there's no `_planet_color` reference.
            if getattr(self, "_moon_color", None) is None:
                planet_color = getattr(self, "_planet_color", None)
                if planet_color is None:
                    self._moon_color = (180, 180, 180)
                    self._moon_outline = (220, 220, 220)
                else:
                    pr, pg, pb = planet_color
                    self._moon_color = (
                        min(255, pr + 40),
                        min(255, pg + 40),
                        min(255, pb + 30),
                    )
                    self._moon_outline = (
                        min(255, self._moon_color[0] + 40),
                        min(255, self._moon_color[1] + 40),
                        min(255, self._moon_color[2] + 40),
                    )
            pygame.draw.circle(
                screen, self._moon_color,
                (int(moon_sx), int(moon_sy)), moon_sr,
            )
            pygame.draw.circle(
                screen, self._moon_outline,
                (int(moon_sx), int(moon_sy)), moon_sr, 1,
            )

        # Asteroids — drawn after planet/moon (their gravity arcs may
        # take them in front of planet sometimes; readable layering).
        # 2026-05-18 art refactor: per-asteroid `sprite_key` selects
        # one of `assets/planets/<key>-sml-000.png` for visual variety.
        # Falls back to the procedural colored circle if the sprite
        # fails to load. Rotation is animated by `spin_rate_deg_per_s`.
        for ast in self.asteroids:
            ax_s, ay_s = self._world_to_screen(ast.x, ast.y, ox, oy, scale)
            ar_s = max(2, int(ast.radius * scale))
            sprite = self._get_asteroid_sprite(ast.sprite_key)
            if sprite is not None:
                # Scale + rotate the sprite each frame. Cheap enough at
                # ~6 asteroids per fight; rotozoom does both in one pass.
                diameter = ar_s * 2
                rotated = pygame.transform.rotozoom(
                    sprite, ast.rotation_deg, diameter / sprite.get_width(),
                )
                r_rect = rotated.get_rect(center=(int(ax_s), int(ay_s)))
                screen.blit(rotated, r_rect)
            else:
                # Procedural fallback (sprite missing / load failed).
                pygame.draw.circle(
                    screen, ast.color, (int(ax_s), int(ay_s)), ar_s,
                )
                rim = (
                    max(0, ast.color[0] - 50),
                    max(0, ast.color[1] - 50),
                    max(0, ast.color[2] - 50),
                )
                pygame.draw.circle(
                    screen, rim, (int(ax_s), int(ay_s)), ar_s, 1,
                )

        # Thruster exhaust — drawn after asteroids (so a ship trailing
        # across an asteroid leaves visible gas) but BEFORE projectiles
        # and ships (so the ship sprite occludes its own emit point
        # cleanly and projectiles read sharply over the gas).
        self._render_thruster_particles(screen, ox, oy, scale)

        # Burv resonance-burst wave visuals — expanding ring at the
        # burst center, fading as it grows. Drawn after thruster gas
        # so the wave overlays exhaust trails legibly.
        for bv in self._burst_visuals:
            life_frac = bv["age"] / bv["lifetime"]
            # Wave radius grows from 0 to bv["radius"] over lifetime
            current_r_world = bv["radius"] * life_frac
            current_r_px = int(current_r_world * scale)
            if current_r_px < 4:
                continue
            alpha = max(0, int(220 * (1.0 - life_frac)))
            if alpha < 10:
                continue
            bsx, bsy = self._world_to_screen(
                bv["x"], bv["y"], ox, oy, scale,
            )
            wave_surf = pygame.Surface(
                (current_r_px * 2 + 4, current_r_px * 2 + 4),
                pygame.SRCALPHA,
            )
            pygame.draw.circle(
                wave_surf, (*bv["color"], alpha),
                (current_r_px + 2, current_r_px + 2),
                current_r_px, 3,
            )
            screen.blit(
                wave_surf,
                (int(bsx) - current_r_px - 2,
                 int(bsy) - current_r_px - 2),
            )

        # Planet backdrop — same rotating sphere as the orbit/system
        # views, anchored in a corner so it doesn't dominate the arena.
        # Time-synced via self.time_in_scene so rotation continues
        # smoothly across the system->combat transition.
        if self.planet_id:
            from scz.content.planet_sphere import has_sphere, get_frame
            if has_sphere(self.planet_id):
                planet_diam = max(180, int(min(self.screen_w, self.screen_h) * 0.32))
                surf = get_frame(self.planet_id, self.time_in_scene, diameter=planet_diam)
                if surf is not None:
                    # Anchor in the upper-right corner of the viewport.
                    pad = 24
                    px = self.screen_w - planet_diam - pad
                    py = pad
                    screen.blit(surf, (px, py))

        # Projectiles
        for p in self.projectiles:
            if p.is_icepeedo:
                # Chunky ice torpedo — pale cyan body with white
                # frost-ring + faint comet trail.
                isx, isy = self._world_to_screen(p.x, p.y, ox, oy, scale)
                ir = max(4, int(p.radius * scale))
                # Trail: faint blue puff offset behind motion direction
                speed = math.hypot(p.vx, p.vy) or 1.0
                bx = isx - (p.vx / speed) * ir * 1.6
                by = isy - (p.vy / speed) * ir * 1.6
                trail_surf = pygame.Surface(
                    (ir * 3, ir * 3), pygame.SRCALPHA,
                )
                pygame.draw.circle(
                    trail_surf, (140, 200, 230, 90),
                    (ir * 3 // 2, ir * 3 // 2), int(ir * 1.3),
                )
                screen.blit(
                    trail_surf,
                    (int(bx) - ir * 3 // 2, int(by) - ir * 3 // 2),
                )
                # Body
                pygame.draw.circle(
                    screen, p.color, (int(isx), int(isy)), ir,
                )
                # Frost-ring outline (white)
                pygame.draw.circle(
                    screen, (255, 255, 255),
                    (int(isx), int(isy)), ir, 1,
                )
                continue
            if p.is_chaff:
                # Chaff cloud — fuzzy alpha-blended puff. Fade as it
                # ages. Multiple overlapping puffs in a cone create
                # the visible chaff field.
                csx, csy = self._world_to_screen(p.x, p.y, ox, oy, scale)
                life_frac = p.age / p.lifetime if p.lifetime > 0 else 0.5
                # Alpha envelope: ramp up over first 12%, fade over
                # final 35%
                if life_frac < 0.12:
                    a_mul = life_frac / 0.12
                elif life_frac > 0.65:
                    a_mul = max(0.0, (1.0 - life_frac) / 0.35)
                else:
                    a_mul = 1.0
                cr_px = int(p.radius * scale)
                # Two concentric layers — outer dim, inner brighter
                for layer_r_frac, layer_alpha_base in (
                    (1.0, 70),
                    (0.55, 110),
                ):
                    rr = max(2, int(cr_px * layer_r_frac))
                    layer_alpha = int(layer_alpha_base * a_mul)
                    if layer_alpha < 6:
                        continue
                    chaff_surf = pygame.Surface(
                        (rr * 2 + 4, rr * 2 + 4), pygame.SRCALPHA,
                    )
                    pygame.draw.circle(
                        chaff_surf, (*p.color, layer_alpha),
                        (rr + 2, rr + 2), rr,
                    )
                    screen.blit(
                        chaff_surf,
                        (int(csx) - rr - 2, int(csy) - rr - 2),
                    )
                continue
            if p.is_gravity_well:
                # Swirling-distortion visual — pulsing concentric rings
                # at the placement point. Reads as "do not enter," not
                # as "incoming projectile." Fade-in at start, fade-out
                # at end of lifetime.
                gsx, gsy = self._world_to_screen(p.x, p.y, ox, oy, scale)
                well_r = int(p.radius * scale)
                life_frac = p.age / p.lifetime if p.lifetime > 0 else 0.5
                # Alpha envelope: ramp up over first 15%, sustain, fade
                # over final 30%.
                if life_frac < 0.15:
                    alpha_mul = life_frac / 0.15
                elif life_frac > 0.70:
                    alpha_mul = max(0.0, (1.0 - life_frac) / 0.30)
                else:
                    alpha_mul = 1.0
                ticks = pygame.time.get_ticks() / 1000.0
                pulse = (math.sin(ticks * 5.5) + 1) / 2
                # Outer ring (faint)
                for i in range(3):
                    rr = well_r - i * 8
                    if rr < 4:
                        break
                    ring_alpha = int(160 * alpha_mul * (1.0 - i * 0.25))
                    if ring_alpha < 10:
                        continue
                    ring_surf = pygame.Surface(
                        (rr * 2 + 4, rr * 2 + 4), pygame.SRCALPHA,
                    )
                    ring_color = (
                        max(0, min(255, p.color[0] + int(pulse * 40))),
                        max(0, min(255, p.color[1] + int(pulse * 40))),
                        max(0, min(255, p.color[2] + int(pulse * 60))),
                        ring_alpha,
                    )
                    pygame.draw.circle(
                        ring_surf, ring_color,
                        (rr + 2, rr + 2), rr, 2,
                    )
                    screen.blit(
                        ring_surf,
                        (int(gsx) - rr - 2, int(gsy) - rr - 2),
                    )
                # Inner core dot
                core_alpha = int(220 * alpha_mul)
                core_surf = pygame.Surface((12, 12), pygame.SRCALPHA)
                pygame.draw.circle(
                    core_surf, (*p.color, core_alpha), (6, 6), 4,
                )
                screen.blit(core_surf, (int(gsx) - 6, int(gsy) - 6))
                continue
            if p.is_resonance_wave:
                # Curved wavefront — draw two concentric arcs centered
                # BEHIND the wave (in the opposite direction of travel).
                # The outer arc is at p.radius, the inner is slightly
                # inside; together they read as a "sonic-boom front."
                # Alpha fades and arc thickness widens as the wave
                # travels and decays.
                wsx, wsy = self._world_to_screen(p.x, p.y, ox, oy, scale)
                wr_px = int(p.radius * scale)
                if wr_px < 4:
                    continue
                # Forward direction unit vector
                speed_p = math.hypot(p.vx, p.vy) or 1.0
                fwd_x = p.vx / speed_p
                fwd_y = p.vy / speed_p
                # Arc center sits BEHIND the wave at distance r_world.
                # The arc passes through the wave's actual (p.x, p.y).
                arc_cx = int(wsx - fwd_x * wr_px)
                arc_cy = int(wsy - fwd_y * wr_px)
                # pygame.draw.arc uses standard math angles (0° = east,
                # CCW positive). Convert the screen-space forward dir
                # to that convention (screen y inverted vs math y).
                fwd_angle = math.atan2(-fwd_y, fwd_x)
                arc_span = math.radians(80)
                a0 = fwd_angle - arc_span / 2
                a1 = fwd_angle + arc_span / 2
                # Fade alpha + widen thickness with distance traveled
                frac = 1.0 - (p.range_left / max(1.0, p.initial_range))
                alpha = max(35, int(230 * (1.0 - 0.70 * frac)))
                thickness_outer = max(2, int(3 + 4 * frac))
                thickness_inner = max(1, int(2 + 2 * frac))
                # Off-screen surface so the arc can have alpha.
                pad = wr_px + 12
                arc_surf = pygame.Surface(
                    (pad * 2, pad * 2), pygame.SRCALPHA,
                )
                rect_outer = pygame.Rect(0, 0, wr_px * 2, wr_px * 2)
                rect_outer.center = (pad, pad)
                pygame.draw.arc(
                    arc_surf, (*p.color, alpha),
                    rect_outer, a0, a1, thickness_outer,
                )
                # Inner arc — slightly smaller radius, brighter, thinner.
                inner_r = max(4, wr_px - max(4, wr_px // 8))
                rect_inner = pygame.Rect(0, 0, inner_r * 2, inner_r * 2)
                rect_inner.center = (pad, pad)
                inner_color = (
                    min(255, p.color[0] + 35),
                    min(255, p.color[1] + 35),
                    min(255, p.color[2] + 20),
                )
                pygame.draw.arc(
                    arc_surf, (*inner_color, alpha),
                    rect_inner, a0, a1, thickness_inner,
                )
                screen.blit(arc_surf, (arc_cx - pad, arc_cy - pad))
                continue
            if p.spin_visual > 0 and not p.is_blade:
                # Spinning-blade visual — 4-pointed star polygon
                # rotated by spin_angle. Used by Proto-Qor-Ah's
                # lawnmower-blade primary AND its ring-of-blades
                # special (each ring blade spins individually).
                bsx, bsy = self._world_to_screen(p.x, p.y, ox, oy, scale)
                blade_size = max(4, int(p.radius * scale))
                points = []
                for k in range(4):
                    pt_ang = p.spin_angle + k * (math.tau / 4)
                    rad = blade_size if (k % 2 == 0) else blade_size * 0.4
                    points.append((
                        bsx + math.cos(pt_ang) * rad,
                        bsy + math.sin(pt_ang) * rad,
                    ))
                pygame.draw.polygon(screen, p.color, points)
                outline = (
                    max(0, p.color[0] // 2),
                    max(0, p.color[1] // 2),
                    max(0, p.color[2] // 2),
                )
                pygame.draw.polygon(screen, outline, points, 1)
                continue
            if p.is_blade:
                # FRIED blade — draw a tapered line from host center
                # to blade tip, with a brighter tip-disc that reads as
                # the dangerous business end. Two passes: dim outer
                # line (3px), brighter inner line (1px), bright tip.
                host = (
                    self.precursor
                    if id(self.precursor) == p.orbital_host_id
                    else self.homesteader
                )
                hsx, hsy = self._world_to_screen(host.x, host.y, ox, oy, scale)
                tsx, tsy = self._world_to_screen(p.x, p.y, ox, oy, scale)
                # Wrap-aware: if the line would cross the wrap edge,
                # draw to the host-side displacement so it doesn't
                # streak across the arena.
                base_dx = _wrap_shortest_delta(host.x, p.x, ARENA_W)
                base_dy = _wrap_shortest_delta(host.y, p.y, ARENA_H)
                tsx = hsx + base_dx * scale
                tsy = hsy + base_dy * scale
                outer = (
                    max(0, min(255, p.color[0] // 2 + 60)),
                    max(0, min(255, p.color[1] // 2 + 60)),
                    max(0, min(255, p.color[2] // 2 + 60)),
                )
                # Outer halo line
                pygame.draw.line(
                    screen, outer,
                    (int(hsx), int(hsy)), (int(tsx), int(tsy)), 4,
                )
                # Inner bright line
                pygame.draw.line(
                    screen, p.color,
                    (int(hsx), int(hsy)), (int(tsx), int(tsy)), 2,
                )
                # Tip disc — the visibly dangerous edge
                pygame.draw.circle(
                    screen, p.color,
                    (int(tsx), int(tsy)),
                    max(3, int(p.radius * scale)),
                )
                continue
            sx, sy = self._world_to_screen(p.x, p.y, ox, oy, scale)
            sprite = self._load_projectile_sprite(p.owner_ship_id) if p.owner_ship_id else None
            if sprite is not None:
                # rotate to match velocity direction (sprite authored nose-up)
                heading = math.atan2(p.vx, -p.vy)
                angle_deg = -math.degrees(heading)
                rotated = pygame.transform.rotozoom(sprite, angle_deg, scale)
                rect = rotated.get_rect(center=(int(sx), int(sy)))
                screen.blit(rotated, rect)
            else:
                pygame.draw.circle(screen, p.color, (int(sx), int(sy)), max(2, int(p.radius * scale)))

        # Tractor-lasso rope visuals — drawn under the ships so the
        # ships sit on top of the rope. Yellow zig-zag energy tether
        # between Persuader and captive while the lasso is active.
        self._draw_lassos(screen, ox, oy, scale)

        # Ships — pass the other ship so the target-lock indicator can
        # tell whether the heading aligns with the opponent.
        self._draw_ship(
            screen, self.precursor, self.homesteader, ox, oy, scale,
        )
        self._draw_ship(
            screen, self.homesteader, self.precursor, ox, oy, scale,
        )

        # Combat FX — impact blast-puffs + ship-death explosions.
        # Drawn AFTER ships so they overlay; impacts fade fast, death
        # FX is a longer expanding-ring + colored debris animation.
        for fx in self.impact_fx:
            self._draw_impact_fx(screen, fx, ox, oy, scale)
        for fx in self.death_fx:
            self._draw_death_fx(screen, fx, ox, oy, scale)

        # HUDs (one per side)
        self._draw_hud(screen)

        # Big result overlay — richer multi-line panel showing the
        # canonical fight summary: kind (VICTORY / TIMEOUT / DOUBLE KO),
        # winner ship + side, loser ship + side, duration, and the
        # winner's remaining hull. Bottom of panel shows the auto-
        # continue countdown.
        if self.result is not None and self.big_font is not None:
            self._draw_result_panel(screen)

    def _draw_result_panel(self, screen: pygame.Surface) -> None:
        """Render the end-of-fight summary overlay. Called every frame
        while `self.result` is set; the panel sits over the arena until
        `FIGHT_END_DWELL` elapses and `_finish()` fires.
        """
        assert self.result is not None
        assert self.big_font is not None
        assert self.font is not None

        # Panel content lines — composed top-to-bottom
        result = self.result
        if result.winner_side is None:
            kind_text = "DOUBLE KO"
            kind_color = (220, 180, 180)
        elif result.timed_out:
            kind_text = "TIMEOUT"
            kind_color = (220, 200, 130)
        else:
            kind_text = "VICTORY"
            kind_color = (255, 230, 180)

        winner_line = ""
        loser_line = ""
        winner_hull_pct = 0
        if result.winner_ship is not None:
            winner_line = f"{result.winner_ship.name}"
            # Determine which ShipState corresponds to the winner so we
            # can read its remaining hull. Match by ShipClass identity.
            for s in (self.precursor, self.homesteader):
                if s.cls is result.winner_ship:
                    winner_hull_pct = int(
                        100 * s.hull / max(1, s.cls.hull_max),
                    )
                    winner_line += (
                        f"  ({s.cls.side})  ·  hull {winner_hull_pct}%"
                    )
                    break
        if result.loser_ship is not None:
            loser_line = (
                f"{result.loser_ship.name}  ({result.loser_ship.side})"
            )

        duration_line = f"Duration: {result.duration:.1f}s"
        if result.timed_out:
            duration_line += "  ·  hit the time cap"

        # Continue countdown — auto-advance dwell
        remaining_dwell = max(0.0, FIGHT_END_DWELL - self.time_since_result)
        countdown_line = f"continuing in {remaining_dwell:.1f}s ..."

        # Panel size — fit content with comfortable padding
        line_h = self.font.get_linesize() + 4
        kind_h = self.big_font.get_linesize()
        panel_w = 700
        panel_h = (
            kind_h + line_h * 4 + 80
        )
        panel_x = (self.screen_w - panel_w) // 2
        panel_y = (self.screen_h - panel_h) // 2

        # Translucent dark box with a thin border in the kind-color
        box = pygame.Surface((panel_w, panel_h), pygame.SRCALPHA)
        box.fill((10, 10, 30, 230))
        screen.blit(box, (panel_x, panel_y))
        pygame.draw.rect(
            screen, kind_color,
            (panel_x, panel_y, panel_w, panel_h), 2,
        )

        # Kind label — big font, centered horizontally
        kind = self.big_font.render(kind_text, True, kind_color)
        kw, kh = kind.get_size()
        screen.blit(
            kind,
            (panel_x + (panel_w - kw) // 2, panel_y + 20),
        )

        # Body lines — winner / loser / duration
        cy = panel_y + 30 + kh + 10
        if winner_line:
            txt = self.font.render(
                winner_line, True, (220, 230, 200),
            )
            tw_, _ = txt.get_size()
            screen.blit(
                txt, (panel_x + (panel_w - tw_) // 2, cy),
            )
            cy += line_h
        if loser_line and result.winner_side is not None:
            sub = self.font.render(
                f"defeated  {loser_line}", True, (180, 170, 170),
            )
            sw_, _ = sub.get_size()
            screen.blit(
                sub, (panel_x + (panel_w - sw_) // 2, cy),
            )
            cy += line_h
        duration_text = self.font.render(
            duration_line, True, (170, 180, 210),
        )
        dw_, _ = duration_text.get_size()
        screen.blit(
            duration_text, (panel_x + (panel_w - dw_) // 2, cy),
        )
        cy += line_h + 8

        # Auto-continue countdown
        countdown_text = self.font.render(
            countdown_line, True, (150, 160, 190),
        )
        cw_, _ = countdown_text.get_size()
        screen.blit(
            countdown_text,
            (panel_x + (panel_w - cw_) // 2, cy),
        )

    # ------------------------------------------------------------------
    # Physics + actions
    # ------------------------------------------------------------------

    def _spawn_debris_particles(
        self, target: ShipState, base_color: tuple[int, int, int],
    ) -> None:
        """Spawn 6-8 ship-hull-fragment particles flying outward from
        the target's position. Visual only — reuses the thruster
        particle system since both are alpha-blended cooling debris.
        Used by the Burv resonance pulse: the target "vibrates a
        piece off" on each hit.
        """
        # Hull color is a deeper tint than the projectile's pulse
        # color — debris reads as material torn from the ship.
        h_r, h_g, h_b = target.cls.hull_color
        debris_color = (
            max(0, min(255, h_r // 2 + 80)),
            max(0, min(255, h_g // 2 + 80)),
            max(0, min(255, h_b // 2 + 60)),
        )
        n = self.rng.randint(6, 9)
        for _ in range(n):
            ang = self.rng.uniform(0, math.tau)
            speed = self.rng.uniform(80.0, 200.0)
            vx = math.cos(ang) * speed
            vy = math.sin(ang) * speed
            self.thruster_particles.append(ThrusterParticle(
                x=target.x + self.rng.uniform(-5.0, 5.0),
                y=target.y + self.rng.uniform(-5.0, 5.0),
                vx=vx, vy=vy,
                lifetime=self.rng.uniform(0.6, 1.1),
                base_radius=self.rng.uniform(1.5, 3.0),
                color=debris_color,
            ))
        # Cap at the same hard limit as thruster gas
        if len(self.thruster_particles) > THRUSTER_PARTICLE_CAP:
            del self.thruster_particles[:-THRUSTER_PARTICLE_CAP]

    def _apply_resonance_burst(
        self, ship: ShipState, burst_radius: float, speed_mul: float,
    ) -> None:
        """Burv resonance-burst effect. Every projectile AND asteroid
        within `burst_radius` of `ship` is redirected to fly away from
        the ship and its speed multiplied by `speed_mul`.

        Aaron's 2026-05-17 spec: "pushes all projectile weapons and
        meteors away from it and doubles their speed." Affects *all*
        projectiles including the Burv's own — characterful chaos.
        Also records the burst location for the render layer to draw
        a radial wave.
        """
        sx, sy = ship.x, ship.y
        for p in self.projectiles:
            if p.orbital or p.is_gravity_well:
                continue   # static / orbital projectiles aren't pushed
            dx = _wrap_shortest_delta(sx, p.x, ARENA_W)
            dy = _wrap_shortest_delta(sy, p.y, ARENA_H)
            d = math.hypot(dx, dy)
            if d > burst_radius or d < 1.0:
                continue
            # Away direction = from ship to projectile
            ux = dx / d
            uy = dy / d
            old_speed = math.hypot(p.vx, p.vy) or 1.0
            new_speed = old_speed * speed_mul
            p.vx = ux * new_speed
            p.vy = uy * new_speed
        for ast in self.asteroids:
            dx = _wrap_shortest_delta(sx, ast.x, ARENA_W)
            dy = _wrap_shortest_delta(sy, ast.y, ARENA_H)
            d = math.hypot(dx, dy)
            if d > burst_radius or d < 1.0:
                continue
            ux = dx / d
            uy = dy / d
            old_speed = math.hypot(ast.vx, ast.vy) or 1.0
            new_speed = old_speed * speed_mul
            ast.vx = ux * new_speed
            ast.vy = uy * new_speed
        # Record the burst for visual rendering — animated radial wave
        self._burst_visuals.append({
            "x": sx, "y": sy, "radius": burst_radius,
            "age": 0.0, "lifetime": 0.55,
            "color": ship.cls.primary_color,
        })

    def _init_scout_mod_effects(self, ship: ShipState) -> None:
        """Snapshot Scout-only mod-effect deltas from game.effective_stat()
        onto the ShipState. Called once at spawn time. No-op for any
        non-Scout ship (mod effects are player-Scout-exclusive — enemy
        ships use their own ShipClass stats with no mod layer).

        The Scout's ShipClass stats (hull, shield, primary_damage, etc.)
        are already mod-adjusted via apply_scout_mods() in
        combat/ships.py before scene construction. This second pass
        only handles BEHAVIOR-FLAG deltas (damage_reduction,
        bounce_chance, hull_regen_passive, ablative_pool,
        engine_damage_on_hit) — values that don't map onto plain
        ShipClass numeric fields but trigger hooks in apply_damage,
        _regen, or _fire_primary.
        """
        if ship.cls.id != "furling_scout":
            return
        game = getattr(self, "game", None)
        if game is None:
            return
        ship.mod_damage_reduction = game.effective_stat("damage_reduction", 0.0)
        ship.mod_bounce_chance = game.effective_stat("bounce_chance", 0.0)
        ship.mod_hull_regen_passive = game.effective_stat("hull_regen_passive", 0.0)
        ablative = game.effective_stat("ablative_pool", 0.0)
        ship.mod_ablative_remaining = ablative
        ship.mod_engine_damage_on_hit = game.effective_stat(
            "engine_damage_on_hit", 0.0,
        )
        # --- Functional-mod overhaul deltas (Aaron 2026-05-18) ---
        ship.mod_chain_lightning_damage = game.effective_stat(
            "chain_lightning_damage", 0.0,
        )
        ship.mod_reflect_chance = game.effective_stat("reflect_chance", 0.0)
        ship.mod_thorn_pulse_radius = game.effective_stat(
            "thorn_pulse_radius", 0.0,
        )
        ship.mod_thorn_pulse_frac = game.effective_stat(
            "thorn_pulse_frac", 0.0,
        )
        crash_red = game.effective_stat("crash_damage_reduction", 0.0)
        ship.mod_crash_damage_frac = max(0.05, 1.0 - crash_red)
        ship.mod_crash_push_mult = game.effective_stat("crash_push_mult", 0.0)
        ship.mod_afterburners = (
            game.effective_stat("afterburners", 0.0) > 0.0
        )
        ship.mod_inertia_dump = (
            game.effective_stat("inertia_dump", 0.0) > 0.0
        )
        ship.mod_strafing_jets_force = game.effective_stat(
            "strafing_jets_force", 0.0,
        )
        ship.mod_capacitor_surge = (
            game.effective_stat("capacitor_surge", 0.0) > 0.0
        )
        ship.mod_cross_wired_ratio = game.effective_stat(
            "cross_wired_ratio", 0.0,
        )
        ship.mod_phase_shift_hull_threshold = game.effective_stat(
            "phase_shift_hull_threshold", 0.0,
        )
        ship.mod_energy_absorb_frac = game.effective_stat(
            "energy_absorb_frac", 0.0,
        )
        ship.mod_hit_negate_interval = game.effective_stat(
            "hit_negate_interval", 0.0,
        )
        ship.mod_lance_charge_max_dmg = game.effective_stat(
            "lance_charge_max_dmg", 0.0,
        )
        ship.mod_pulse_stack_bonus = game.effective_stat(
            "pulse_stack_bonus", 0.0,
        )
        # --- Crew-perk hooks ---
        ship.mod_primary_energy_reduction = game.effective_stat(
            "primary_energy_reduction", 0.0,
        )
        ship.mod_kill_stack_damage = game.effective_stat(
            "kill_stack_damage", 0.0,
        )
        ship.mod_combat_start_shield_overcharge = game.effective_stat(
            "combat_start_shield_overcharge", 0.0,
        )
        ship.mod_cooldown_reduce_per_hit = game.effective_stat(
            "cooldown_reduce_per_hit", 0.0,
        )
        ship.mod_hit_negate_first_per_fight = (
            game.effective_stat("hit_negate_first_per_fight", 0.0) > 0.0
        )
        # Apply combat-start shield overcharge — Yelena's post-quest
        # "Alphabetized Tools" perk. Shield starts at 1+X of max; the
        # cap allows the natural shield_regen + damage interactions
        # to bleed it back to normal.
        if ship.mod_combat_start_shield_overcharge > 0:
            ship.shield = min(
                ship.cls.shield_max * (1.0 + ship.mod_combat_start_shield_overcharge),
                ship.cls.shield_max * 2.0,  # safety cap
            )

    def _roll_posture(self, ship_cls: ShipClass) -> str:
        """Per-fight AI posture selection (Aaron 2026-05-17). Three
        EFFECTIVE postures — each plays differently but competes well.
        Returns the posture string the AI reads to modify its behavior.

        Posture pool by ai_style:
          - "left_only" (Sentry Drone): tutorial ship — always "balanced".
          - All combat ai_styles: random pick from
            (AGGRESSIVE, PRECISE, EVASIVE).

        Aaron's directive: "don't adopt limp/ineffective postures."
        Each of the three options is a viable winning strategy with
        a different texture; none is a self-handicap.
        """
        if ship_cls.ai_style == "left_only":
            return "balanced"
        return self.rng.choice(("AGGRESSIVE", "PRECISE", "EVASIVE"))

    def _enemy_of(self, ship: ShipState) -> ShipState | None:
        """Return the (single) opposing ship — the one whose side
        differs from `ship`. Returns None if no such ship exists
        (shouldn't happen in 1v1 but guarded).
        """
        for candidate in (self.precursor, self.homesteader):
            if candidate is ship:
                continue
            if candidate.side != ship.side:
                return candidate
        return None

    def _find_ship_by_id(self, ship_id: int) -> ShipState | None:
        """Look up a ShipState by Python id(). Used by mechanics that
        store a reference-by-id (Lemmkin latch). Returns None if the
        id no longer matches either combatant.
        """
        if id(self.precursor) == ship_id:
            return self.precursor
        if id(self.homesteader) == ship_id:
            return self.homesteader
        return None

    def _spawn_fried_discs(self, ship: ShipState) -> None:
        """Spawn 4 rotating blade-shaped orbitals around the host
        (Aaron's 2026-05-17 revised spec: "ring of these blades around
        the ship like the fireball ring used to do"). Each orbital
        rotates around the host AND spins individually as a visible
        blade shape. Hit detection uses the legacy disc-style single
        point check.
        """
        cls = ship.cls
        host_id = id(ship)
        RING_RADIUS = 38.0
        RING_ANGULAR_SPEED = 3.2
        BLADE_DAMAGE = 5.0
        BLADE_SPIN = 9.0   # rad/sec individual-blade visual rotation
        for i in range(4):
            base_angle = i * (math.tau / 4)
            self.projectiles.append(Projectile(
                x=ship.x + math.cos(base_angle) * RING_RADIUS,
                y=ship.y + math.sin(base_angle) * RING_RADIUS,
                vx=0.0, vy=0.0,
                damage=BLADE_DAMAGE,
                range_left=1e9,
                owner_side=ship.side,
                color=cls.primary_color,
                radius=10.0,
                orbital=True,
                orbital_host_id=host_id,
                orbital_angle=base_angle,
                orbital_radius=RING_RADIUS,
                orbital_angular_speed=RING_ANGULAR_SPEED,
                # is_blade stays False — uses LEGACY orbital code path
                # (single hit-disc per blade), but the blade visual is
                # rendered as a spinning multi-pointed shape via the
                # spin_visual + spin_angle fields.
                is_blade=False,
                spin_visual=BLADE_SPIN,
            ))

    def _despawn_fried_discs(self, ship: ShipState) -> None:
        """Remove this ship's orbital projectiles when the special is
        released."""
        host_id = id(ship)
        self.projectiles = [
            p for p in self.projectiles
            if not (p.orbital and p.orbital_host_id == host_id)
        ]

    def _update_orbital_projectiles(self, dt: float) -> None:
        """Update orbital projectiles (FRIED discs). They follow their
        host ship at a fixed radius, rotating with their angular speed.
        Called each frame before standard projectile integration.
        """
        if not self.projectiles:
            return
        host_map = {
            id(self.precursor): self.precursor,
            id(self.homesteader): self.homesteader,
        }
        for p in self.projectiles:
            if not p.orbital:
                continue
            host = host_map.get(p.orbital_host_id)
            if host is None or not host.alive:
                # Host died — orbital despawns
                p.range_left = -1.0
                continue
            if p.is_blade:
                # Blade tracks the host's heading: orbital_angle is
                # an OFFSET from heading, not an absolute angle. The
                # blade rotates with the ship but not independently.
                effective_angle = host.heading + p.orbital_angle
            else:
                # Free orbital (legacy disc spin)
                p.orbital_angle = (
                    p.orbital_angle + p.orbital_angular_speed * dt
                ) % math.tau
                effective_angle = p.orbital_angle
            p.x = (host.x + math.cos(effective_angle) * p.orbital_radius) % ARENA_W
            p.y = (host.y + math.sin(effective_angle) * p.orbital_radius) % ARENA_H

    def _update_lasso(
        self, ship: ShipState, want_fire: bool, dt: float,
    ) -> None:
        """Tractor-lasso state machine for the Persuader Vessel.

        Called every frame BEFORE _apply_action so the orbit-physics
        can override standard movement integration. Three states:

        IDLE  (lasso_target_id == 0): if want_fire and an enemy is in
              LASSO_MAX_RANGE and not already-lassoed, latch onto them.
              Picks the orbit center as the midpoint between the two
              ships and freezes it for the duration of the swing.

        ACTIVE (lasso_target_id != 0, want_fire == True): advance the
              orbit angle, force Persuader + captive positions onto
              the orbit. Drain energy. On exhaustion, force release
              with NO fling (the captive just stops being pulled).

        RELEASE (lasso_target_id != 0, want_fire == False): compute
              the captive's release velocity from the current orbit
              tangent × LASSO_FLING_MULTIPLIER, apply it, clear the
              lasso link, start cooldown.

        This is a no-op for ships whose primary_pattern isn't
        tractor_lasso (currently just the Persuader Vessel).
        """
        cls = ship.cls
        if cls.primary_pattern != "tractor_lasso":
            return

        # Tick the primary_cooldown counter so the cooldown after
        # release works the same as other ships' primary fire gating.
        if ship.primary_cooldown > 0:
            ship.primary_cooldown = max(0.0, ship.primary_cooldown - dt)

        # ---- ACTIVE / RELEASE branch (we already have a captive) ----
        if ship.lasso_target_id != 0:
            captive = self._find_ship_by_id(ship.lasso_target_id)
            if captive is None or not captive.alive:
                # Captive died mid-swing — clear state, start cooldown.
                ship.lasso_target_id = 0
                ship.lasso_hold_elapsed = 0.0
                ship.primary_cooldown = LASSO_RELEASE_COOLDOWN
                return

            if not want_fire:
                # RELEASE → fling captive tangentially. Captive's
                # current position on the orbit determines the tangent
                # direction (perpendicular to its radial vector from
                # the orbit center, in the direction of orbit motion).
                host_angle = ship.lasso_orbit_angle + math.pi
                # Tangent for counter-clockwise orbit (matches angle
                # increment direction). Tangent = (-sin, cos) at angle.
                tangent_x = -math.sin(host_angle)
                tangent_y = math.cos(host_angle)
                # Captive's tangential speed during orbit, amplified
                # by the release multiplier for the slingshot effect.
                host_speed = (
                    LASSO_ORBITAL_SPEED
                    * LASSO_ORBIT_RADIUS_TARGET
                    * LASSO_FLING_MULTIPLIER
                )
                captive.vx = tangent_x * host_speed
                captive.vy = tangent_y * host_speed
                # Persuader also flies off in its own tangent direction
                # — but DAMPED. The Persuader can't ride out its own
                # orbit velocity (which is ω × r_persuader, well above
                # its top_speed); without the damper it slams into the
                # planet immediately after release.
                p_tangent_x = -math.sin(ship.lasso_orbit_angle)
                p_tangent_y = math.cos(ship.lasso_orbit_angle)
                p_speed = (
                    LASSO_ORBITAL_SPEED
                    * LASSO_ORBIT_RADIUS_PERSUADER
                    * LASSO_PERSUADER_RELEASE_FRAC
                )
                ship.vx = p_tangent_x * p_speed
                ship.vy = p_tangent_y * p_speed
                # Clear state.
                captive.lassoed_by_id = 0
                ship.lasso_target_id = 0
                ship.lasso_hold_elapsed = 0.0
                ship.primary_cooldown = LASSO_RELEASE_COOLDOWN
                # Brief flash for visual legibility.
                ship.hit_flash = 0.10
                captive.hit_flash = 0.18
                return

            # Hold — drain energy. If exhausted, forced release with
            # no fling (slow stop, captive keeps the orbital tangent
            # speed but without the slingshot multiplier).
            ship.energy = max(0.0, ship.energy - LASSO_ENERGY_PER_SEC * dt)
            if ship.energy <= 0.0:
                host_angle = ship.lasso_orbit_angle + math.pi
                tangent_x = -math.sin(host_angle)
                tangent_y = math.cos(host_angle)
                host_speed = (
                    LASSO_ORBITAL_SPEED * LASSO_ORBIT_RADIUS_TARGET
                )
                captive.vx = tangent_x * host_speed
                captive.vy = tangent_y * host_speed
                captive.lassoed_by_id = 0
                ship.lasso_target_id = 0
                ship.lasso_hold_elapsed = 0.0
                ship.primary_cooldown = LASSO_RELEASE_COOLDOWN
                return

            # Tick the hold timer (used by AI for release timing).
            ship.lasso_hold_elapsed += dt

            # Advance orbit angle; force both ships onto their orbit
            # positions. The captive sits opposite the Persuader (phase
            # + pi) at a smaller radius — reads as "the heavier ship is
            # mostly anchoring while the lighter Persuader whips around."
            ship.lasso_orbit_angle = (
                ship.lasso_orbit_angle + LASSO_ORBITAL_SPEED * dt
            ) % math.tau
            host_angle = ship.lasso_orbit_angle + math.pi
            ship.x = (
                ship.lasso_orbit_cx
                + math.cos(ship.lasso_orbit_angle) * LASSO_ORBIT_RADIUS_PERSUADER
            ) % ARENA_W
            ship.y = (
                ship.lasso_orbit_cy
                + math.sin(ship.lasso_orbit_angle) * LASSO_ORBIT_RADIUS_PERSUADER
            ) % ARENA_H
            captive.x = (
                ship.lasso_orbit_cx + math.cos(host_angle) * LASSO_ORBIT_RADIUS_TARGET
            ) % ARENA_W
            captive.y = (
                ship.lasso_orbit_cy + math.sin(host_angle) * LASSO_ORBIT_RADIUS_TARGET
            ) % ARENA_H
            # Track tangent velocities so death/release branches read
            # consistent state. Tangent direction = (-sin, cos) at angle.
            p_tan_x = -math.sin(ship.lasso_orbit_angle)
            p_tan_y = math.cos(ship.lasso_orbit_angle)
            ship.vx = p_tan_x * (LASSO_ORBITAL_SPEED * LASSO_ORBIT_RADIUS_PERSUADER)
            ship.vy = p_tan_y * (LASSO_ORBITAL_SPEED * LASSO_ORBIT_RADIUS_PERSUADER)
            c_tan_x = -math.sin(host_angle)
            c_tan_y = math.cos(host_angle)
            captive.vx = c_tan_x * (LASSO_ORBITAL_SPEED * LASSO_ORBIT_RADIUS_TARGET)
            captive.vy = c_tan_y * (LASSO_ORBITAL_SPEED * LASSO_ORBIT_RADIUS_TARGET)
            # Persuader heading — lean into the spin (tangent direction).
            ship.heading = math.atan2(p_tan_x, -p_tan_y)
            return

        # ---- IDLE branch — try to latch ----
        if not want_fire:
            return
        if ship.primary_cooldown > 0:
            return
        # Need enough energy to MEANINGFULLY hold (otherwise the
        # cooldown trigger fires almost immediately on energy drain).
        if ship.energy < LASSO_ENERGY_PER_SEC * 0.5:
            return
        enemy = self._enemy_of(ship)
        if enemy is None or not enemy.alive:
            return
        if enemy.lassoed_by_id != 0:
            return  # already lassoed by someone else
        # Skip lassoing a target that's currently inertia-halted or
        # under forced-halt — they can't be flung from a dead stop in
        # a way that reads as physics. Leaves more room for the
        # Persuader vs Compeller-style "stacked stuns" interaction
        # to be designed deliberately later.
        if enemy.frozen_remaining > 0:
            return
        dx = _wrap_shortest_delta(enemy.x, ship.x, ARENA_W)
        dy = _wrap_shortest_delta(enemy.y, ship.y, ARENA_H)
        d = math.hypot(dx, dy)
        if d > LASSO_MAX_RANGE:
            return
        # Latch. Orbit center = the midpoint between Persuader and
        # enemy at this instant. We compute it via wrap-aware delta
        # then add half-delta to the Persuader's position.
        cx = (ship.x + dx * 0.5) % ARENA_W
        cy = (ship.y + dy * 0.5) % ARENA_H
        ship.lasso_orbit_cx = cx
        ship.lasso_orbit_cy = cy
        # Persuader's initial orbit angle = the angle from center to
        # the Persuader (i.e., its current relative position).
        pcx = _wrap_shortest_delta(ship.x, cx, ARENA_W)
        pcy = _wrap_shortest_delta(ship.y, cy, ARENA_H)
        ship.lasso_orbit_angle = math.atan2(pcy, pcx)
        ship.lasso_target_id = id(enemy)
        ship.lasso_hold_elapsed = 0.0
        enemy.lassoed_by_id = id(ship)
        # Quick flash so the latch reads visually.
        enemy.hit_flash = 0.20

    def _update_ship_special(
        self, ship: ShipState, want_active: bool, dt: float,
    ) -> None:
        """Apply the ship's special-ability state machine for this
        frame. Generic dispatch on ship.cls.special_ability — the
        current implementation handles inertia_halt; future specials
        (teleport, butt_missiles, etc.) plug in here.

        The semantic for inertia_halt:
        - On ACTIVATE (not already active, want_active=True, cooldown
          elapsed, enough energy): save (vx, vy), zero them, mark
          active.
        - While ACTIVE (want_active=True): keep velocity zeroed each
          frame, drain energy. If energy runs out → forced release.
        - On RELEASE (was active, want_active=False): restore saved
          (vx, vy), mark inactive, start cooldown.
        """
        cls = ship.cls
        ability = cls.special_ability

        # Tick cooldown regardless
        if ship.special_cooldown_left > 0:
            ship.special_cooldown_left = max(
                0.0, ship.special_cooldown_left - dt,
            )

        if ability == "none":
            return

        if ability == "phase_skip":
            # Persuader Vessel directional teleport (Aaron 2026-05-17).
            # Short blink forward in facing direction; pass-through
            # planets/asteroids/projectiles since it's a teleport, not
            # a dash. Single-frame trigger; cooldown-only (no energy
            # cost — specials don't share the weapon pool).
            if want_active and ship.special_cooldown_left <= 0:
                fx_local = math.sin(ship.heading)
                fy_local = -math.cos(ship.heading)
                ship.x = (ship.x + fx_local * PHASE_SKIP_DISTANCE) % ARENA_W
                ship.y = (ship.y + fy_local * PHASE_SKIP_DISTANCE) % ARENA_H
                # Brief flash for legibility — the player should
                # see the skip happen.
                ship.hit_flash = 0.18
                ship.special_cooldown_left = cls.special_cooldown
            return

        if ability == "icepeedo":
            # Cleanser ice torpedo. Cooldown-only (Aaron 2026-05-17 —
            # specials don't share the weapon energy pool).
            if want_active and ship.special_cooldown_left <= 0:
                fx_local = math.sin(ship.heading)
                fy_local = -math.cos(ship.heading)
                nose_x = ship.x + fx_local * 18.0
                nose_y = ship.y + fy_local * 18.0
                ICEPEEDO_SPEED = 720.0
                self._spawn_projectile(
                    ship,
                    nose_x, nose_y,
                    fx_local * ICEPEEDO_SPEED + ship.vx * 0.3,
                    fy_local * ICEPEEDO_SPEED + ship.vy * 0.3,
                    damage=5.0,         # modest base damage on hit
                    range_left=560.0,
                    color=(180, 230, 255),
                    radius=7.0,         # chunky torpedo
                    homing=True,
                    homing_turn_rate=1.6,
                    is_icepeedo=True,
                )
                ship.special_cooldown_left = cls.special_cooldown
            return

        if ability == "chaff_spray":
            # Defender chaff spray — single-frame trigger. Spawns
            # ~12 stationary chaff puffs in a forward cone from the
            # Defender's nose. Each chaff puff is a small zone (radius
            # 22u) that slows any enemy projectile passing through.
            # Multiple stacked puffs in the cone make a corridor of
            # decay — enemy bullets entering the cone slow toward zero.
            if want_active and ship.special_cooldown_left <= 0:
                if True:  # cooldown-only — no energy gate
                    fx_local = math.sin(ship.heading)
                    fy_local = -math.cos(ship.heading)
                    rx_local = -fy_local
                    ry_local = fx_local
                    CHAFF_COUNT = 12
                    for _ in range(CHAFF_COUNT):
                        # Forward distance 50..200, perpendicular
                        # offset ±70 (cone shape)
                        fwd = self.rng.uniform(50.0, 200.0)
                        side = self.rng.uniform(-70.0, 70.0)
                        cx = (ship.x + fx_local * fwd + rx_local * side) % ARENA_W
                        cy = (ship.y + fy_local * fwd + ry_local * side) % ARENA_H
                        # Drift slightly forward to mimic chaff
                        # dispersing in front of the ship
                        drift_speed = self.rng.uniform(20.0, 50.0)
                        self.projectiles.append(Projectile(
                            x=cx, y=cy,
                            vx=fx_local * drift_speed,
                            vy=fy_local * drift_speed,
                            damage=0.0,            # chaff doesn't damage
                            range_left=1e9,
                            owner_side=ship.side,
                            color=(220, 220, 200),
                            radius=22.0,
                            is_chaff=True,
                            lifetime=self.rng.uniform(2.0, 3.0),
                        ))
                    ship.special_cooldown_left = cls.special_cooldown
            return

        if ability == "xform":
            # Mmrnmhrm X-Form transform — held-state. While active,
            # ship.cls swaps to xform_alt (different form: missile
            # jet vs laser fighter). Hull/shield/energy values are
            # preserved across the swap. Cooldown-only now; if a
            # special_duration is set, force-revert when exceeded.
            if want_active:
                if not ship.special_active:
                    if ship.special_cooldown_left > 0:
                        return
                    alt = cls.xform_alt
                    if alt is None:
                        return
                    ship.special_active = True
                    ship.special_held_elapsed = 0.0
                    ship.xform_base_cls = cls
                    ship.cls = alt
                    ship.xform_active_form = 1
                # Tick hold timer; force revert if exceeding duration
                ship.special_held_elapsed += dt
                if (
                    cls.special_duration > 0
                    and ship.special_held_elapsed > cls.special_duration
                ):
                    self._revert_xform(ship)
            else:
                if ship.special_active and ship.xform_active_form == 1:
                    self._revert_xform(ship)
            return

        if ability == "homing_cluster":
            # Proto-Ur-Quan replacement for SC2 launch-fighters.
            # Single-frame TRIGGER. Spawns 5 missiles in a forward
            # arc with random spread; each starts flying straight
            # but after `homing_delay` (~0.4s) they begin to home
            # on the enemy. Mimics fighter-launch flavor without
            # the child-entity infrastructure.
            if want_active and ship.special_cooldown_left <= 0:
                fx_local = math.sin(ship.heading)
                fy_local = -math.cos(ship.heading)
                nose_x = ship.x + fx_local * 16.0
                nose_y = ship.y + fy_local * 16.0
                for ang_offset_deg in (-30.0, -15.0, 0.0, 15.0, 30.0):
                    a = ship.heading + math.radians(ang_offset_deg)
                    launch_speed = 450.0
                    mvx = math.sin(a) * launch_speed + ship.vx * 0.2
                    mvy = -math.cos(a) * launch_speed + ship.vy * 0.2
                    self._spawn_projectile(
                        ship,
                        nose_x, nose_y,
                        mvx, mvy,
                        damage=12.0,
                        range_left=800.0,
                        color=cls.primary_color,
                        radius=3.0,
                        homing_delay=0.40,
                        homing_turn_rate=2.8,
                    )
                ship.special_cooldown_left = cls.special_cooldown
            return

        if ability == "resonance_burst":
            # Burv Broadcaster resonance burst — single-frame TRIGGER.
            # Every projectile + asteroid within burst_radius is
            # redirected to fly AWAY from the Burv and has its speed
            # DOUBLED. Affects own projectiles too (Aaron's spec:
            # "all projectile weapons and meteors"). Defensive
            # panic-button + arena-clear effect.
            if want_active and ship.special_cooldown_left <= 0:
                BURST_RADIUS = 250.0
                SPEED_MUL = 2.0
                self._apply_resonance_burst(ship, BURST_RADIUS, SPEED_MUL)
                ship.special_cooldown_left = cls.special_cooldown
            return

        if ability == "adware_pulse":
            # Melnorme adware pulse — single-frame TRIGGER. Blasts the
            # target's HUD with Grand Shopping Super Mart pop-ups and
            # buy-buttons. Their pilot is busy closing dialogs; the
            # autopilot redirects toward the "nearest store" — in our
            # arena, the nearest asteroid (each is canonically a
            # franchise outlet, and also a collision hazard, so this
            # is doubly bad for the target). Aaron's spec 2026-05-17:
            # replaces the SC2 confusion-pulse (key-reverse, useless
            # vs AI) with this Melnorme-flavored commercial assault.
            if want_active and ship.special_cooldown_left <= 0:
                for target in (self.precursor, self.homesteader):
                    if target is ship or not target.alive:
                        continue
                    if target.side == ship.side:
                        continue
                    target.adware_remaining = 2.5
                    target.hit_flash = 0.15
                    break
                ship.special_cooldown_left = cls.special_cooldown
            return

        if ability == "compel":
            # Compeller forced-halt. Single-frame TRIGGER. Applies
            # forced_halt_remaining = 2.0s to the enemy. While halted,
            # the enemy's vx/vy zero in _integrate (same as the
            # voluntary halt, but enemy can't release). The Compeller
            # gets two free seconds of fire on a stationary target.
            if want_active and ship.special_cooldown_left <= 0:
                for target in (self.precursor, self.homesteader):
                    if target is ship or not target.alive:
                        continue
                    if target.side == ship.side:
                        continue
                    target.forced_halt_remaining = 2.0
                    target.hit_flash = 0.15
                    break
                ship.special_cooldown_left = cls.special_cooldown
            return

        if ability == "absorb_shield":
            # Utwig absorption shield. Held state. While active, the
            # apply_damage hook redirects incoming damage to energy
            # instead of hull/shield (see ShipState.apply_damage for
            # the redirect logic). Cooldown-only now (no longer drains
            # the weapon energy pool); held for at most special_duration
            # seconds before forced release.
            if want_active:
                if not ship.special_active:
                    if ship.special_cooldown_left > 0:
                        return
                    ship.special_active = True
                    ship.special_held_elapsed = 0.0
                # Tick hold timer; force release at duration cap.
                ship.special_held_elapsed += dt
                if (
                    cls.special_duration > 0
                    and ship.special_held_elapsed > cls.special_duration
                ):
                    ship.special_active = False
                    ship.special_cooldown_left = cls.special_cooldown
            else:
                if ship.special_active:
                    ship.special_active = False
                    ship.special_cooldown_left = cls.special_cooldown
            return

        if ability == "dash_slice":
            # Thinn dash-slice — single-frame trigger; free (no energy).
            # The ship gains a big forward velocity impulse + if it
            # contacts the enemy, applies high damage AND takes small
            # self-damage. Brief cooldown after to prevent spam.
            if want_active and ship.special_cooldown_left <= 0:
                # Forward impulse — additive to current velocity
                DASH_BOOST = 380.0
                fx = math.sin(ship.heading)
                fy = -math.cos(ship.heading)
                ship.vx += fx * DASH_BOOST
                ship.vy += fy * DASH_BOOST
                # Damage check — if enemy is in front + close, hit
                SLICE_DAMAGE = 35.0
                SELF_DAMAGE = 5.0
                SLICE_RANGE = 60.0
                for target in (self.precursor, self.homesteader):
                    if target is ship or not target.alive:
                        continue
                    if target.side == ship.side:
                        continue
                    tdx = _wrap_shortest_delta(ship.x, target.x, ARENA_W)
                    tdy = _wrap_shortest_delta(ship.y, target.y, ARENA_H)
                    if math.hypot(tdx, tdy) < SLICE_RANGE:
                        target.apply_damage(SLICE_DAMAGE)
                        ship.apply_damage(SELF_DAMAGE)
                        break
                ship.special_cooldown_left = cls.special_cooldown
            return

        if ability == "aggressive_discovery":
            # Lemmkin Skitter latches onto enemy and does damage over
            # time. Releases when the enemy's energy reaches max
            # (they have to fully recharge to "force the Skitter off").
            # Activation requires being near the enemy.
            LATCH_RANGE = 80.0
            # Latch DPS — 22 overshot to 61% win rate, dialed back
            # to 14 (Lemmkin FIGHTER target 35%).
            LATCH_DAMAGE_PER_SEC = 14.0
            if want_active and ship.special_cooldown_left <= 0:
                if ship.latched_to_id == 0:
                    # Not yet latched — try to attach
                    for target in (self.precursor, self.homesteader):
                        if target is ship or not target.alive:
                            continue
                        if target.side == ship.side:
                            continue
                        tdx = _wrap_shortest_delta(ship.x, target.x, ARENA_W)
                        tdy = _wrap_shortest_delta(ship.y, target.y, ARENA_H)
                        if math.hypot(tdx, tdy) < LATCH_RANGE:
                            ship.latched_to_id = id(target)
                            # Pick an offset on the enemy's hull —
                            # pin to the side they're facing away from
                            # so the visual reads as "stuck to them"
                            ship.latched_offset_x = tdx
                            ship.latched_offset_y = tdy
                            # Normalize the offset to a fixed distance
                            d = math.hypot(
                                ship.latched_offset_x,
                                ship.latched_offset_y,
                            ) or 1.0
                            LATCH_PIN_DIST = 22.0
                            ship.latched_offset_x = (
                                ship.latched_offset_x / d * LATCH_PIN_DIST
                            )
                            ship.latched_offset_y = (
                                ship.latched_offset_y / d * LATCH_PIN_DIST
                            )
                            break
                # While latched, drain damage from enemy + check release
                if ship.latched_to_id != 0:
                    host = self._find_ship_by_id(ship.latched_to_id)
                    if host is None or not host.alive:
                        ship.latched_to_id = 0
                        ship.special_cooldown_left = cls.special_cooldown
                    else:
                        host.apply_damage(LATCH_DAMAGE_PER_SEC * dt)
                        # Release condition: host's energy hits max
                        if host.energy >= host.cls.energy_max:
                            ship.latched_to_id = 0
                            ship.special_cooldown_left = cls.special_cooldown
            else:
                # Player released voluntarily — drop latch
                if ship.latched_to_id != 0:
                    ship.latched_to_id = 0
                    ship.special_cooldown_left = cls.special_cooldown
            return

        if ability == "regen_hull":
            # Mycon Podship regeneration. Held; heals hull continuously
            # while active. Cooldown-only (no energy drain); capped by
            # special_duration so it can't infinitely top off.
            REGEN_RATE_HP_PER_SEC = 10.0
            if want_active:
                if not ship.special_active:
                    if ship.special_cooldown_left > 0:
                        return
                    ship.special_active = True
                    ship.special_held_elapsed = 0.0
                ship.special_held_elapsed += dt
                if (
                    cls.special_duration > 0
                    and ship.special_held_elapsed > cls.special_duration
                ):
                    ship.special_active = False
                    ship.special_cooldown_left = cls.special_cooldown
                    return
                # Heal — cap at hull_max
                ship.hull = min(
                    cls.hull_max,
                    ship.hull + REGEN_RATE_HP_PER_SEC * dt,
                )
            else:
                if ship.special_active:
                    ship.special_active = False
                    ship.special_cooldown_left = cls.special_cooldown
            return

        if ability == "teleport":
            # Arilou teleport — instantaneous random-jump. Cooldown-only.
            if want_active and ship.special_cooldown_left <= 0:
                ship.x = self.rng.uniform(60.0, ARENA_W - 60.0)
                ship.y = self.rng.uniform(60.0, ARENA_H - 60.0)
                ship.vx = 0.0
                ship.vy = 0.0
                ship.special_cooldown_left = cls.special_cooldown
                ship.hit_flash = 0.2
            return

        if ability == "blazer_form":
            # Androsynth Comet — transform into a ramming form. While
            # active: contact damages the enemy. Cooldown-only;
            # special_duration caps the held time so the ram is a
            # committed window, not a permanent state.
            if want_active:
                if not ship.special_active:
                    if ship.special_cooldown_left > 0:
                        return
                    ship.special_active = True
                    ship.special_held_elapsed = 0.0
                ship.special_held_elapsed += dt
                if (
                    cls.special_duration > 0
                    and ship.special_held_elapsed > cls.special_duration
                ):
                    ship.special_active = False
                    ship.special_cooldown_left = cls.special_cooldown
                    return
                # Apply ram damage if touching the enemy.
                BLAZER_RAM_DAMAGE = 35.0
                SHIP_RADIUS = 14.0
                for target in (self.precursor, self.homesteader):
                    if target is ship or not target.alive:
                        continue
                    if target.side == ship.side:
                        continue
                    tdx = _wrap_shortest_delta(ship.x, target.x, ARENA_W)
                    tdy = _wrap_shortest_delta(ship.y, target.y, ARENA_H)
                    if tdx * tdx + tdy * tdy < (SHIP_RADIUS * 2) ** 2:
                        target.apply_damage(BLAZER_RAM_DAMAGE * dt)
            else:
                if ship.special_active:
                    ship.special_active = False
                    ship.special_cooldown_left = cls.special_cooldown
            return

        if ability == "fried_discs":
            # Proto-Qor-Ah disc ring — spawn 4 orbital projectiles around
            # the ship; they damage any enemy on contact. Cooldown-only,
            # capped by special_duration so the ring eventually drops
            # and the Marauder has to commit to re-summoning.
            if want_active:
                if not ship.special_active:
                    if ship.special_cooldown_left > 0:
                        return
                    ship.special_active = True
                    ship.special_held_elapsed = 0.0
                    self._spawn_fried_discs(ship)
                ship.special_held_elapsed += dt
                if (
                    cls.special_duration > 0
                    and ship.special_held_elapsed > cls.special_duration
                ):
                    self._despawn_fried_discs(ship)
                    ship.special_active = False
                    ship.special_cooldown_left = cls.special_cooldown
            else:
                if ship.special_active:
                    self._despawn_fried_discs(ship)
                    ship.special_active = False
                    ship.special_cooldown_left = cls.special_cooldown
            return

        if ability == "inertia_halt":
            # Furling Scout dodge-halt. While held, velocity is zeroed;
            # on release, the pre-halt velocity is restored. Cooldown-
            # only, capped by special_duration so the Scout can't camp
            # the halt forever (was previously "free, only cooldown" —
            # the duration cap is the new natural ceiling).
            if want_active:
                if not ship.special_active:
                    if ship.special_cooldown_left > 0:
                        return
                    ship.special_active = True
                    ship.special_held_elapsed = 0.0
                    ship.special_saved_vx = ship.vx
                    ship.special_saved_vy = ship.vy
                # Velocity zeroed each frame.
                ship.vx = 0.0
                ship.vy = 0.0
                ship.special_held_elapsed += dt
                if (
                    cls.special_duration > 0
                    and ship.special_held_elapsed > cls.special_duration
                ):
                    self._release_inertia_halt(ship)
            else:
                if ship.special_active:
                    self._release_inertia_halt(ship)

    def _revert_xform(self, ship: ShipState) -> None:
        """Mmrnmhrm xform reverter — swap cls back to the stored
        base form, clear active flag, start cooldown."""
        if ship.xform_base_cls is not None:
            ship.cls = ship.xform_base_cls
            ship.xform_base_cls = None
        ship.special_active = False
        ship.xform_active_form = 0
        ship.special_cooldown_left = ship.cls.special_cooldown

    def _release_inertia_halt(self, ship: ShipState) -> None:
        """End an inertia_halt activation — restore pre-halt velocity
        and start the cooldown."""
        ship.special_active = False
        ship.vx = ship.special_saved_vx
        ship.vy = ship.special_saved_vy
        ship.special_cooldown_left = ship.cls.special_cooldown

    def _apply_action(self, ship: ShipState, action: AIAction, dt: float) -> None:
        cls = ship.cls
        # Permanent engine debuff from Defender's engine_seeker hits.
        # Subtracted from top_speed AND acceleration; each clamped to
        # a minimum floor (a fully-engine-damaged ship still moves at
        # a crawl, can't be made immobile).
        MIN_TOP_SPEED = 60.0
        MIN_ACCELERATION = 80.0
        # Wetness slow (Aaron's 2026-05-17 spec: "being wet slows a
        # ship but doesn't freeze their controls"). Multiplicative
        # factor; at wetness=100, top_speed and acceleration are 60%
        # of base. Linear interpolation; full slowdown is gradual.
        wetness_factor = 1.0 - (ship.wetness / 100.0) * 0.40
        effective_top_speed = max(
            MIN_TOP_SPEED,
            cls.top_speed * wetness_factor - ship.engine_damage_accumulated,
        )
        effective_acceleration = max(
            MIN_ACCELERATION,
            cls.acceleration * wetness_factor - ship.engine_damage_accumulated,
        )
        # --- Scout mod: Afterburners — sustained thrust 2+ sec ignites
        # a 3-sec speed boost (1.6x top + accel), then 4-sec cooldown.
        if ship.mod_afterburners:
            if action.thrust and ship.afterburner_cooldown_remaining <= 0:
                ship.afterburner_thrust_held += dt
                if (
                    ship.afterburner_thrust_held >= 2.0
                    and ship.afterburner_active_remaining <= 0
                ):
                    ship.afterburner_active_remaining = 3.0
                    ship.afterburner_thrust_held = 0.0
            else:
                ship.afterburner_thrust_held = 0.0
            if ship.afterburner_active_remaining > 0:
                ship.afterburner_active_remaining = max(
                    0.0, ship.afterburner_active_remaining - dt,
                )
                effective_top_speed *= 1.6
                effective_acceleration *= 1.6
                if ship.afterburner_active_remaining == 0.0:
                    ship.afterburner_cooldown_remaining = 4.0
            if ship.afterburner_cooldown_remaining > 0:
                ship.afterburner_cooldown_remaining = max(
                    0.0, ship.afterburner_cooldown_remaining - dt,
                )
        # Rotation
        if action.turn_dir != 0:
            ship.heading += action.turn_dir * cls.turn_rate * dt
            ship.heading = (ship.heading + math.pi) % (2 * math.pi) - math.pi
            # --- Scout mod: Strafing Jets — turning while not thrusting
            # emits a perpendicular impulse for sideways dodge.
            if ship.mod_strafing_jets_force > 0 and not action.thrust:
                # Perpendicular to current heading. Direction = sign of turn_dir.
                fx_h = math.sin(ship.heading)
                fy_h = -math.cos(ship.heading)
                perp_x = -fy_h * action.turn_dir
                perp_y = fx_h * action.turn_dir
                ship.vx += perp_x * ship.mod_strafing_jets_force * dt
                ship.vy += perp_y * ship.mod_strafing_jets_force * dt
        # Thrust
        if action.thrust:
            # --- Scout mod: Inertia Dump — if thrust is opposite to
            # current velocity, zero velocity before applying new thrust.
            if ship.mod_inertia_dump:
                fx_h = math.sin(ship.heading)
                fy_h = -math.cos(ship.heading)
                # Dot product of thrust direction with current velocity.
                v_dot_h = fx_h * ship.vx + fy_h * ship.vy
                if v_dot_h < -30.0:  # reverse-thrusting through current motion
                    ship.vx = 0.0
                    ship.vy = 0.0
            fx = math.sin(ship.heading) * effective_acceleration * dt
            fy = -math.cos(ship.heading) * effective_acceleration * dt
            ship.vx += fx
            ship.vy += fy
            speed = math.hypot(ship.vx, ship.vy)
            if speed > effective_top_speed:
                # Cap
                ship.vx *= effective_top_speed / speed
                ship.vy *= effective_top_speed / speed
        # Primary cooldown decrement (independent of fire decision)
        if ship.primary_cooldown > 0:
            ship.primary_cooldown = max(0.0, ship.primary_cooldown - dt)
        # --- Scout mod: Capacitor Surge — energy hitting max arms a
        # surge shot. The actual damage triple happens in _fire_primary.
        if ship.mod_capacitor_surge:
            if ship.energy >= cls.energy_max and not ship.surge_armed:
                ship.surge_armed = True
        # --- Scout mod: Hit-negate cooldown decrement (Arilou Phase Dampener)
        if ship.hit_negate_cooldown_remaining > 0:
            ship.hit_negate_cooldown_remaining = max(
                0.0, ship.hit_negate_cooldown_remaining - dt,
            )
        # --- Scout mod: Phase Shift remaining timer
        if ship.phase_shift_active_remaining > 0:
            ship.phase_shift_active_remaining = max(
                0.0, ship.phase_shift_active_remaining - dt,
            )

    # ------------------------------------------------------------------
    # Gravity + collision helpers (used by ships, asteroids, projectiles)
    # ------------------------------------------------------------------

    def _gravity_accel(self, x: float, y: float) -> tuple[float, float]:
        """Total gravitational acceleration vector at (x, y) from all
        large bodies (planet always; moon when present). Inverse-square
        falloff, wrap-aware. Used by ship + asteroid + projectile
        integration.
        """
        # Planet (always present)
        dx = _wrap_shortest_delta(x, PLANET_X, ARENA_W)
        dy = _wrap_shortest_delta(y, PLANET_Y, ARENA_H)
        r2 = max((PLANET_RADIUS * 0.5) ** 2, dx * dx + dy * dy)
        r = math.sqrt(r2)
        a_mag = PLANET_GRAVITY / r2
        ax = (dx / r) * a_mag
        ay = (dy / r) * a_mag
        # Moon (when present — it has its own gravity well)
        if self.has_moon:
            mdx = _wrap_shortest_delta(x, self.moon_x, ARENA_W)
            mdy = _wrap_shortest_delta(y, self.moon_y, ARENA_H)
            mr2 = max((MOON_RADIUS * 0.5) ** 2, mdx * mdx + mdy * mdy)
            mr = math.sqrt(mr2)
            ma_mag = MOON_GRAVITY / mr2
            ax += (mdx / mr) * ma_mag
            ay += (mdy / mr) * ma_mag
        return ax, ay

    def _resolve_body_collision(
        self,
        target_x: float, target_y: float, target_r: float,
        target_vx: float, target_vy: float,
        body_x: float, body_y: float, body_r: float,
        bounce_factor: float = 0.6,
    ) -> tuple[float, float, float, float, bool] | None:
        """Check collision of a circle (target) against a fixed circle
        (body) and return the resolved position + reflected velocity if
        contact occurred, plus a True/False flag for "collision
        happened." Returns None if no contact.

        Caller decides how to apply damage. Wrap-aware (the body is
        evaluated at its wrap-shortest position relative to the target).
        """
        dx = _wrap_shortest_delta(target_x, body_x, ARENA_W)
        dy = _wrap_shortest_delta(target_y, body_y, ARENA_H)
        contact_r = body_r + target_r
        r2 = dx * dx + dy * dy
        if r2 >= contact_r * contact_r:
            return None
        r = math.sqrt(r2) or 0.001
        # Outward normal (from body center to target position)
        nx = dx / r
        ny = dy / r
        push = contact_r - r
        new_x = target_x + nx * push
        new_y = target_y + ny * push
        # Reflect velocity across the surface normal (target's normal
        # points outward from body center, i.e. (nx, ny)).
        v_dot_n = target_vx * nx + target_vy * ny
        new_vx, new_vy = target_vx, target_vy
        if v_dot_n < 0:   # moving INTO the body
            new_vx -= 2 * v_dot_n * nx
            new_vy -= 2 * v_dot_n * ny
            new_vx *= bounce_factor
            new_vy *= bounce_factor
        return new_x, new_y, new_vx, new_vy, True

    def _integrate(self, ship: ShipState, dt: float) -> None:
        # Tick the cross-imposed effect timers each frame
        if ship.forced_halt_remaining > 0:
            ship.forced_halt_remaining = max(
                0.0, ship.forced_halt_remaining - dt,
            )
        if ship.adware_remaining > 0:
            ship.adware_remaining = max(0.0, ship.adware_remaining - dt)
        # Wetness drains slowly when not being hit by water.
        if ship.wetness > 0:
            ship.wetness = max(0.0, ship.wetness - 4.0 * dt)
        # Ice buildup also drains — outer-spike water hits accumulate
        # this; if not sustained, the cold dissipates.
        if ship.ice_buildup > 0:
            ship.ice_buildup = max(0.0, ship.ice_buildup - 6.0 * dt)
        # Frozen ticks down; while > 0, ship can't fire (and AI
        # returns a no-op so it just drifts on momentum).
        if ship.frozen_remaining > 0:
            ship.frozen_remaining = max(
                0.0, ship.frozen_remaining - dt,
            )

        # Latched-to-host (Lemmkin aggressive_discovery): override
        # position to track the host with a fixed offset; zero velocity.
        if ship.latched_to_id != 0:
            host = self._find_ship_by_id(ship.latched_to_id)
            if host is not None and host.alive:
                ship.x = (host.x + ship.latched_offset_x) % ARENA_W
                ship.y = (host.y + ship.latched_offset_y) % ARENA_H
                ship.vx = 0.0
                ship.vy = 0.0
                return
            else:
                ship.latched_to_id = 0

        # Inertia-halted ships are stationary — skip gravity, skip
        # position integration. The special drains energy and the
        # ship resumes motion on release. The forced-halt branch
        # handles the Compeller compel target.
        #
        # NOTE: Cleanser-frozen ships are NOT in this branch (Aaron's
        # 2026-05-17 spec: "don't freeze them in space, only lock
        # their controls"). A frozen ship retains its velocity at
        # freeze-time and continues to drift; gravity still affects
        # it; it can still hit bodies for the catastrophic shatter
        # damage. The AI early-returns to no-thrust no-turn no-fire
        # for frozen ships, so they coast on momentum alone.
        if (
            (ship.special_active and ship.cls.special_ability == "inertia_halt")
            or ship.forced_halt_remaining > 0
        ):
            # Zero velocity, no position update
            ship.vx = 0.0
            ship.vy = 0.0
            return

        # Gravity from all bodies (planet always + moon when present).
        ax, ay = self._gravity_accel(ship.x, ship.y)
        ship.vx += ax * dt
        ship.vy += ay * dt

        # Nebula slow — heavier ships are slowed more. Damping is
        # applied as a velocity multiplier per frame; nesting in multiple
        # nebulae stacks (deliberate — overlapping nebulae are denser).
        # Net effect: a Defender (mass 180) at a nebula center loses
        # ~80% of its velocity per second; an Arilou skiff (mass 55)
        # loses ~30%.
        for neb in self.nebulae:
            ndx = _wrap_shortest_delta(ship.x, neb.x, ARENA_W)
            ndy = _wrap_shortest_delta(ship.y, neb.y, ARENA_H)
            nd2 = ndx * ndx + ndy * ndy
            r2 = neb.radius * neb.radius
            if nd2 >= r2:
                continue
            # depth = 0 at the edge, 1 at the center. Linear fade.
            depth = 1.0 - math.sqrt(nd2) / neb.radius
            mass_factor = ship.cls.mass / NEBULA_REFERENCE_MASS
            # Velocity multiplier this frame; the dt factor makes the
            # slow-rate roughly frame-rate-independent.
            slow_per_sec = NEBULA_CENTER_SLOW * depth * mass_factor
            mult = max(NEBULA_MIN_VELOCITY_FRAC, 1.0 - slow_per_sec * dt)
            ship.vx *= mult
            ship.vy *= mult

        # Integrate position
        ship.x += ship.vx * dt
        ship.y += ship.vy * dt

        # Body collisions — planet, moon, asteroids. Order matters
        # mostly for damage accounting; each collision applies its own
        # bounce + damage independently.
        SHIP_RADIUS = 14.0
        bodies: list[tuple[float, float, float, float]] = [
            (PLANET_X, PLANET_Y, PLANET_RADIUS, PLANET_COLLISION_DAMAGE),
        ]
        if self.has_moon:
            bodies.append(
                (self.moon_x, self.moon_y, MOON_RADIUS, MOON_COLLISION_DAMAGE)
            )
        for ast in self.asteroids:
            bodies.append(
                (ast.x, ast.y, ast.radius, ASTEROID_COLLISION_DAMAGE)
            )

        # Scout mod: Crash Plating — body collision damage reduced
        # AND asteroids get shoved away at multiplier velocity. The
        # damage reduction is per-ship; the asteroid push happens
        # only when the body in question IS an asteroid (matched by
        # iterating self.asteroids).
        crash_dmg_frac = ship.mod_crash_damage_frac
        crash_push = ship.mod_crash_push_mult
        for bx, by, br, dmg in bodies:
            res = self._resolve_body_collision(
                ship.x, ship.y, SHIP_RADIUS,
                ship.vx, ship.vy,
                bx, by, br,
                bounce_factor=0.6,
            )
            if res is not None:
                ship.x, ship.y, ship.vx, ship.vy, _ = res
                # Frozen ship + body impact = catastrophic shatter
                # (Aaron 2026-05-17 Cleanser spec: "if it hits a planet
                # or an asteroid while frozen, super damage")
                if ship.frozen_remaining > 0:
                    ship.apply_damage(60.0)
                    ship.frozen_remaining = 0.0
                else:
                    ship.apply_damage(dmg * crash_dmg_frac)
                # Crash Plating push — if this body is an asteroid,
                # shove it away in the collision direction at
                # `crash_push_mult` × the ship's pre-impact speed.
                if crash_push > 0:
                    for ast in self.asteroids:
                        if abs(ast.x - bx) < 0.5 and abs(ast.y - by) < 0.5:
                            # Push direction = from ship through asteroid.
                            push_dx = _wrap_shortest_delta(ship.x, ast.x, ARENA_W)
                            push_dy = _wrap_shortest_delta(ship.y, ast.y, ARENA_H)
                            d = math.hypot(push_dx, push_dy) or 1.0
                            speed = math.hypot(ship.vx, ship.vy)
                            ast.vx += (push_dx / d) * speed * crash_push
                            ast.vy += (push_dy / d) * speed * crash_push
                            break

        # Arena wrap (post-collision so a ship pushed off a body
        # doesn't immediately wrap to the opposite edge).
        ship.x %= ARENA_W
        ship.y %= ARENA_H

    def _integrate_asteroids(self, dt: float) -> None:
        """Asteroids drift through the arena under gravity, bouncing
        off the planet and the moon (if present). They do not collide
        with each other (avoids n² and adds little gameplay value).
        Asteroids are indestructible — they take no damage but can
        damage ships and absorb projectiles.
        """
        AST_BOUNCE = 0.85   # less energy loss than ships — they're rocks
        for ast in self.asteroids:
            # Spin while drifting — purely visual (sprite rotation).
            if ast.spin_rate_deg_per_s:
                ast.rotation_deg = (
                    ast.rotation_deg + ast.spin_rate_deg_per_s * dt
                ) % 360.0
            # Apply gravity from planet (and moon if present)
            ax, ay = self._gravity_accel(ast.x, ast.y)
            ast.vx += ax * dt
            ast.vy += ay * dt
            # Integrate position
            ast.x += ast.vx * dt
            ast.y += ast.vy * dt
            # Bounce off planet
            res = self._resolve_body_collision(
                ast.x, ast.y, ast.radius,
                ast.vx, ast.vy,
                PLANET_X, PLANET_Y, PLANET_RADIUS,
                bounce_factor=AST_BOUNCE,
            )
            if res is not None:
                ast.x, ast.y, ast.vx, ast.vy, _ = res
            if self.has_moon:
                res = self._resolve_body_collision(
                    ast.x, ast.y, ast.radius,
                    ast.vx, ast.vy,
                    self.moon_x, self.moon_y, MOON_RADIUS,
                    bounce_factor=AST_BOUNCE,
                )
                if res is not None:
                    ast.x, ast.y, ast.vx, ast.vy, _ = res
            # Wrap
            ast.x %= ARENA_W
            ast.y %= ARENA_H

    def _regen(self, ship: ShipState, dt: float) -> None:
        cls = ship.cls
        if ship.shield_regen_cooldown > 0:
            ship.shield_regen_cooldown = max(0.0, ship.shield_regen_cooldown - dt)
        elif ship.shield < cls.shield_max:
            ship.shield = min(cls.shield_max, ship.shield + cls.shield_regen * dt)
        if ship.energy < cls.energy_max:
            ship.energy = min(cls.energy_max, ship.energy + cls.energy_regen * dt)
        # Scout module: Repair Drone passive hull regen
        if ship.mod_hull_regen_passive > 0.0 and ship.hull < cls.hull_max:
            ship.hull = min(
                cls.hull_max,
                ship.hull + ship.mod_hull_regen_passive * dt,
            )

    def _fire_primary(self, ship: ShipState) -> None:
        """Fire the ship's primary weapon according to its
        primary_pattern. Each pattern emits 1..N projectiles per call,
        all sharing the same cooldown + energy cost (volleys are one
        trigger pull, not staggered).
        """
        cls = ship.cls
        # tractor_lasso has no per-frame projectile — the entire weapon
        # is implemented as a held state in _update_lasso. _fire_primary
        # being called for a Persuader is a no-op (the action.fire_primary
        # flag is consumed by _update_lasso instead).
        if cls.primary_pattern == "tractor_lasso":
            return
        # Utwig absorb_shield is EXCLUSIVE with primary fire (Aaron
        # 2026-05-17: "Utwig can't shield and fire at the same time,
        # one of their limitations"). Canonical SC2 trade-off: the
        # Jugger raises the absorption shield OR uses the gatling
        # gun, never both. This makes the shield a real choice —
        # eat hits and convert to energy, OR shoot back, not both.
        if (
            cls.special_ability == "absorb_shield"
            and ship.special_active
        ):
            return
        # Crew perk: Bren-Vor's Patient Eye — primary_energy_reduction
        # cuts the shot's energy cost. Lets the Scout shoot more often
        # before having to wait for energy regen.
        effective_energy_cost = cls.primary_energy
        if ship.mod_primary_energy_reduction > 0:
            effective_energy_cost = max(
                0.0,
                cls.primary_energy * (1.0 - min(0.95, ship.mod_primary_energy_reduction)),
            )
        if ship.energy < effective_energy_cost:
            return
        ship.energy -= effective_energy_cost
        ship.primary_cooldown = 1.0 / max(0.5, cls.primary_rate)
        # Common nose-spawn geometry — all patterns originate here.
        nose_offset = 16.0
        # Forward unit vector
        fx = math.sin(ship.heading)
        fy = -math.cos(ship.heading)
        # Perpendicular unit vector (right side from ship's perspective)
        rx = -fy
        ry = fx
        sx_base = ship.x + fx * nose_offset
        sy_base = ship.y + fy * nose_offset
        # Inherited ship velocity (looks right + helps fast ships lead)
        inh_vx = ship.vx * 0.3
        inh_vy = ship.vy * 0.3

        # Scout mod: Capacitor Surge — if armed, this volley is 3x
        # damage. Save current damage so we can restore after firing.
        surge_mult = 1.0
        if ship.surge_armed:
            surge_mult = 3.0
            ship.surge_armed = False
        # Bake the surge multiplier directly into the class damage via
        # a transient class mutation? Simpler: scale the spawned bolts
        # post-spawn (in the same projectile-len-before pass below).

        # Track projectile-list length so the Scout-mod hook below can
        # tag newly-spawned bolts with engine_damage_on_hit (Engine
        # Disruptor Coil mod) AND apply Surge/Chain Lightning props.
        proj_len_before = len(self.projectiles)
        pattern = cls.primary_pattern

        if pattern == "twin":
            # Two parallel bolts, ±8 perpendicular offset from nose.
            offset = 8.0
            for side_sign in (-1, 1):
                self._spawn_projectile(
                    ship,
                    sx_base + rx * offset * side_sign,
                    sy_base + ry * offset * side_sign,
                    fx * cls.primary_speed + inh_vx,
                    fy * cls.primary_speed + inh_vy,
                    cls.primary_damage,
                    cls.primary_range,
                    cls.primary_color,
                    radius=3.0,
                )

        elif pattern == "triple":
            # Three parallel slow plasma bolts (Proto-Ur-Quan broadside).
            # Wider spacing than twin so the volley reads as three
            # distinct streams, not a tight pair.
            for side_sign, offset in ((-1, 14.0), (0, 0.0), (1, 14.0)):
                self._spawn_projectile(
                    ship,
                    sx_base + rx * offset * side_sign,
                    sy_base + ry * offset * side_sign,
                    fx * cls.primary_speed + inh_vx,
                    fy * cls.primary_speed + inh_vy,
                    cls.primary_damage,
                    cls.primary_range,
                    cls.primary_color,
                    radius=3.5,
                )

        elif pattern == "burst":
            # Three bolts in a tight ±3° fan — reads as a measured
            # 3-shot burst (Persuader). Tighter than multi_spread so
            # all three usually land at modest range.
            for angle_offset_deg in (-3.0, 0.0, 3.0):
                a = ship.heading + math.radians(angle_offset_deg)
                bvx = math.sin(a) * cls.primary_speed + inh_vx
                bvy = -math.cos(a) * cls.primary_speed + inh_vy
                self._spawn_projectile(
                    ship,
                    sx_base, sy_base, bvx, bvy,
                    cls.primary_damage,
                    cls.primary_range,
                    cls.primary_color,
                    radius=2.5,
                )

        elif pattern == "water_spray":
            # Cleanser Cruiser water spray — fires 5 droplets in a
            # forward cone (±10°). Each droplet soaks the target
            # (adds wetness) AND deals modest damage. Pushes asteroids
            # without damaging them. After water_freeze_at_age (1.0s
            # of flight), droplets convert to ice — still flying,
            # damage halves, no longer adds wetness.
            DROPLET_COUNT = 5
            for i in range(DROPLET_COUNT):
                ang_offset_deg = self.rng.uniform(-10.0, 10.0)
                # Random speed jitter for natural spray look
                speed_jitter = self.rng.uniform(0.85, 1.15)
                a = ship.heading + math.radians(ang_offset_deg)
                bvx = math.sin(a) * cls.primary_speed * speed_jitter + inh_vx
                bvy = -math.cos(a) * cls.primary_speed * speed_jitter + inh_vy
                self._spawn_projectile(
                    ship,
                    sx_base + self.rng.uniform(-2.0, 2.0),
                    sy_base + self.rng.uniform(-2.0, 2.0),
                    bvx, bvy,
                    cls.primary_damage,
                    cls.primary_range,
                    (90, 160, 230),   # water blue (overrides ship color)
                    radius=3.5,
                    is_water=True,
                    water_freeze_at_age=1.0,
                )

        elif pattern == "engine_seeker":
            # Defender Vessel engine-seeking missile. Single long-range
            # tracking missile; on hit applies engine damage to the
            # target (permanent slow accumulating over multiple hits).
            # Slower than a beam but accurate via mild homing.
            self._spawn_projectile(
                ship,
                sx_base, sy_base,
                fx * cls.primary_speed + inh_vx,
                fy * cls.primary_speed + inh_vy,
                cls.primary_damage,
                cls.primary_range,
                cls.primary_color,
                radius=4.0,
                homing=True,
                homing_turn_rate=2.0,
                engine_damage_on_hit=30.0,
            )

        elif pattern == "gatling":
            # Utwig Jugger gatling laser — one big bolt per fire,
            # cycling through 3 lateral barrels (left/center/right).
            # Across sustained fire this reads as alternating gatling
            # cadence. Per-bolt damage is large because each "barrel"
            # is a fat energy bolt, not a thin laser.
            barrel = ship.gatling_barrel % 3
            ship.gatling_barrel = (ship.gatling_barrel + 1) % 3
            # Offsets: -10 (left), 0 (center), +10 (right)
            barrel_offset = (-10.0, 0.0, 10.0)[barrel]
            self._spawn_projectile(
                ship,
                sx_base + rx * barrel_offset,
                sy_base + ry * barrel_offset,
                fx * cls.primary_speed + inh_vx,
                fy * cls.primary_speed + inh_vy,
                cls.primary_damage,
                cls.primary_range,
                cls.primary_color,
                radius=5.5,   # fat bolts
            )

        elif pattern == "lawnmower_blade":
            # Proto-Qor-Ah lawnmower blade — single big spinning blade
            # flying straight forward. No homing (Aaron explicit:
            # "doesn't home in on ships"). Wide hit radius so it
            # mows through anything in its path. Visual: rotating
            # multi-pointed blade shape.
            self._spawn_projectile(
                ship,
                sx_base, sy_base,
                fx * cls.primary_speed + inh_vx,
                fy * cls.primary_speed + inh_vy,
                cls.primary_damage,
                cls.primary_range,
                cls.primary_color,
                radius=14.0,   # WIDE — it's a lawnmower
                spin_visual=10.0,   # rad/sec rotation
            )

        elif pattern == "resonance_pulse":
            # Burv Broadcaster — full-map-range RESONANCE WAVE.
            # Aaron 2026-05-19 spec: "curved wave that gets bigger and
            # weaker the further it goes until it fades, but it has a
            # long range. like full map length ... immune to their own
            # weapon."
            #
            # Mechanics:
            #   - Slow projectile (primary_speed on the ShipClass) so
            #     the wave reads as a propagating sound front, not a
            #     hitscan beam — players have time to see and react.
            #   - Radius grows continuously (wave_growth_per_sec). The
            #     spawn radius is small (Burv-mouth-sized); by the time
            #     the wave reaches the far side of the arena it's
            #     ~250u across — a hazard zone, not a pencil.
            #   - Damage falls from full at spawn → wave_damage_floor
            #     fraction at max range (linear with distance traveled).
            #   - Owner is immune: handled by the standard owner_side
            #     check in _update_projectiles (line ~4831).
            #   - Renders as a curved arc/wavefront, not a disc — see
            #     the `is_resonance_wave` branch in the projectile
            #     renderer.
            self._spawn_projectile(
                ship,
                sx_base, sy_base,
                fx * cls.primary_speed + inh_vx,
                fy * cls.primary_speed + inh_vy,
                cls.primary_damage,
                cls.primary_range,
                cls.primary_color,
                radius=10.0,                 # spawn radius — grows
                spawn_debris_on_hit=True,
                is_resonance_wave=True,
                wave_growth_per_sec=55.0,    # ~250u over 4.5s flight
                wave_damage_floor=0.45,      # 45% dmg at max range
            )

        elif pattern == "gravity_well":
            # Compeller gravity-well placer (Aaron's 2026-05-17 spec).
            # Spawns a stationary, damaging well AT THE ENEMY'S CURRENT
            # POSITION. The well lasts 3 seconds and ticks damage
            # continuously to any enemy inside its radius. Designed to
            # combo with `compel`: halt the enemy, then drop the well
            # on their stopped silhouette. Even uncombo'd, the well
            # is a placed hazard the enemy must navigate around.
            enemy_ship = self._enemy_of(ship)
            if enemy_ship is None or not enemy_ship.alive:
                return
            # Lead the placement slightly using enemy velocity — gives
            # the well a fighting chance against moving targets.
            LEAD_TIME = 0.45
            place_x = (enemy_ship.x + enemy_ship.vx * LEAD_TIME) % ARENA_W
            place_y = (enemy_ship.y + enemy_ship.vy * LEAD_TIME) % ARENA_H
            self.projectiles.append(Projectile(
                x=place_x, y=place_y, vx=0.0, vy=0.0,
                damage=cls.primary_damage,   # dps when target inside
                range_left=1e9,               # despawn via lifetime
                owner_side=ship.side,
                color=cls.primary_color,
                radius=42.0,                  # well radius
                is_gravity_well=True,
                lifetime=2.0,
            ))
            # Proto-Ur-Quan replacement for the SC2 "launch fighters"
            # special. SC2 canon adapted to our pre-fighter-tech era:
            # the warship fires a CLUSTER of 5 slow missiles in a
            # tight forward arc, each independently flying out. Lower
            # per-missile damage than charged, but the cluster blanket
            # makes it hard to dodge entirely. Spawned in a fan
            # ±15° wide with slight position offset per missile.
            for i, ang_offset_deg in enumerate((-15.0, -7.5, 0.0, 7.5, 15.0)):
                a = ship.heading + math.radians(ang_offset_deg)
                # Stagger missiles slightly along the perpendicular
                # so they don't all spawn at the same point
                perp_offset = (i - 2) * 6.0
                bvx = math.sin(a) * cls.primary_speed + inh_vx
                bvy = -math.cos(a) * cls.primary_speed + inh_vy
                self._spawn_projectile(
                    ship,
                    sx_base + rx * perp_offset,
                    sy_base + ry * perp_offset,
                    bvx, bvy,
                    cls.primary_damage,
                    cls.primary_range,
                    cls.primary_color,
                    radius=3.5,
                )

        elif pattern == "lance":
            # Precision sniper — single bolt at 1.5× speed + 1.3× range.
            # The stat block records the nominal values; the engine
            # bumps them at render time for the lance flavor.
            self._spawn_projectile(
                ship,
                sx_base, sy_base,
                fx * cls.primary_speed * 1.5 + inh_vx,
                fy * cls.primary_speed * 1.5 + inh_vy,
                cls.primary_damage,
                cls.primary_range * 1.3,
                cls.primary_color,
                radius=2.5,
            )

        elif pattern == "tracking":
            # Arilou tracking laser — SC2-canon AUTO-AIM IMMEDIATE
            # weapon. We model it as a near-hitscan projectile with a
            # very high turn rate (sharp tracking) and short range.
            self._spawn_projectile(
                ship,
                sx_base, sy_base,
                fx * cls.primary_speed + inh_vx,
                fy * cls.primary_speed + inh_vy,
                cls.primary_damage,
                cls.primary_range,
                cls.primary_color,
                radius=2.5,
                homing=True,
                homing_turn_rate=8.0,   # very sharp — true tracking
            )

        elif pattern == "bubble":
            # Androsynth bubble missile — slow projectile that can hit
            # multiple times (SC2 canon: 3 hits before pop). Per-hit
            # damage is the stat block damage. Range is doubled because
            # bubbles drift longer than standard shots.
            self._spawn_projectile(
                ship,
                sx_base, sy_base,
                fx * cls.primary_speed + inh_vx,
                fy * cls.primary_speed + inh_vy,
                cls.primary_damage,
                cls.primary_range * 1.5,
                cls.primary_color,
                radius=5.0,
                hits_remaining=2,   # 1 initial + 2 = 3 hits total
            )

        elif pattern == "returning":
            # Kohr-Ah Returning Howitzer Cannon (RHC). Projectile flies
            # forward, then reverses direction after a flight-time and
            # threatens both ships on its return path. Modeled here:
            # spawn a normal projectile with `return_at_age` set; the
            # _update_projectiles loop flips velocity at that age.
            flight_time = cls.primary_range / cls.primary_speed * 0.6
            self._spawn_projectile(
                ship,
                sx_base, sy_base,
                fx * cls.primary_speed + inh_vx,
                fy * cls.primary_speed + inh_vy,
                cls.primary_damage,
                cls.primary_range * 1.8,   # extended to allow the return leg
                cls.primary_color,
                radius=4.0,
                return_at_age=flight_time,
            )

        elif pattern == "tier_plasma":
            # Melnorme 3-tier plasma. The ship accumulates "charge" on
            # ShipState while not firing; releasing fires at tier 1, 2,
            # or 3 depending on how much charge built up. We use the
            # ship's `energy` as proxy for charge — the more energy at
            # fire time, the bigger the shot.
            tier = 1
            damage_mul = 1.0
            radius_mul = 1.0
            speed_mul = 1.0
            if ship.energy >= cls.energy_max * 0.66:
                tier = 3
                damage_mul = 3.0
                radius_mul = 1.8
                speed_mul = 1.1
                # Tier 3 drains a lot of energy (full charge spent)
                ship.energy = max(0.0, ship.energy - cls.energy_max * 0.5)
            elif ship.energy >= cls.energy_max * 0.33:
                tier = 2
                damage_mul = 2.0
                radius_mul = 1.4
                # Tier 2 drains a moderate amount
                ship.energy = max(0.0, ship.energy - cls.energy_max * 0.25)
            # tier 1 — standard cost already deducted at top of fn
            self._spawn_projectile(
                ship,
                sx_base, sy_base,
                fx * cls.primary_speed * speed_mul + inh_vx,
                fy * cls.primary_speed * speed_mul + inh_vy,
                cls.primary_damage * damage_mul,
                cls.primary_range,
                cls.primary_color,
                radius=4.0 * radius_mul,
            )

        elif pattern == "multi_spread":
            # Three bolts in a narrow forward fan (±10°).
            for angle_offset_deg in (-10.0, 0.0, 10.0):
                a = ship.heading + math.radians(angle_offset_deg)
                bvx = math.sin(a) * cls.primary_speed + inh_vx
                bvy = -math.cos(a) * cls.primary_speed + inh_vy
                self._spawn_projectile(
                    ship,
                    sx_base, sy_base, bvx, bvy,
                    cls.primary_damage,
                    cls.primary_range,
                    cls.primary_color,
                    radius=2.5,
                )

        elif pattern == "scatter":
            # Five bolts in a wide forward cone with random jitter so
            # repeat volleys spread differently. ±20° wide; the bolts
            # at extremes rarely hit at range, all five at point-blank.
            base_angles_deg = (-20.0, -10.0, 0.0, 10.0, 20.0)
            for base in base_angles_deg:
                jitter = self.rng.uniform(-3.0, 3.0)
                a = ship.heading + math.radians(base + jitter)
                # Speed jitter too — keeps the cone "alive" visually
                spd = cls.primary_speed * self.rng.uniform(0.9, 1.1)
                bvx = math.sin(a) * spd + inh_vx
                bvy = -math.cos(a) * spd + inh_vy
                self._spawn_projectile(
                    ship,
                    sx_base, sy_base, bvx, bvy,
                    cls.primary_damage,
                    cls.primary_range,
                    cls.primary_color,
                    radius=2.2,
                )

        elif pattern == "homing":
            # Single plasmoid that turns toward enemy each frame. Slow
            # exit speed (so the homing has time to bend the path) but
            # the projectile speed is already low (Melnorme 400 u/s).
            # Turn rate: ~2.5 rad/sec is enough to track a circling
            # ship at medium range without making evasion impossible.
            self._spawn_projectile(
                ship,
                sx_base, sy_base,
                fx * cls.primary_speed + inh_vx,
                fy * cls.primary_speed + inh_vy,
                cls.primary_damage,
                cls.primary_range,
                cls.primary_color,
                radius=4.0,
                homing=True,
                homing_turn_rate=2.5,
            )

        elif pattern == "charged":
            # Oversized heavy shot — 2× damage, 2× radius. Slow rate
            # is on the ship-stat side; the per-shot effect is here.
            self._spawn_projectile(
                ship,
                sx_base, sy_base,
                fx * cls.primary_speed + inh_vx,
                fy * cls.primary_speed + inh_vy,
                cls.primary_damage * 2.0,
                cls.primary_range,
                cls.primary_color,
                radius=6.0,
            )

        else:
            # "single" (default) — one bolt straight ahead.
            self._spawn_projectile(
                ship,
                sx_base, sy_base,
                fx * cls.primary_speed + inh_vx,
                fy * cls.primary_speed + inh_vy,
                cls.primary_damage,
                cls.primary_range,
                cls.primary_color,
                radius=3.0,
            )

        # Scout-mod hook: Engine Disruptor Coil. Tag every projectile
        # spawned by this call with engine_damage_on_hit so each hit
        # accumulates engine-debuff on the target. Works across all
        # primary patterns — twin, scatter, lance, even lawnmower.
        if ship.mod_engine_damage_on_hit > 0:
            for p in self.projectiles[proj_len_before:]:
                if p.engine_damage_on_hit < ship.mod_engine_damage_on_hit:
                    p.engine_damage_on_hit = ship.mod_engine_damage_on_hit
        # Scout-mod hook: tag hitscan-pattern bolts as "energy" damage.
        # The Mmrnmhrm Reinforced Plating absorbs these heavily.
        ENERGY_PATTERNS = {
            "single", "twin", "triple", "multi_spread", "burst",
            "lance", "scatter", "tracking", "gatling",
        }
        if pattern in ENERGY_PATTERNS:
            for p in self.projectiles[proj_len_before:]:
                p.damage_kind = "energy"
        # Scout-mod hook: Capacitor Surge — scale damage 3x for all
        # bolts in this volley (already gated above via surge_armed).
        if surge_mult > 1.0:
            for p in self.projectiles[proj_len_before:]:
                p.damage *= surge_mult
                # Visual: brighter color + bigger radius
                p.radius = max(p.radius, p.radius * 1.3)
        # Crew perk: Bren-Vor post-quest "Velt-Ra's Mark" — each
        # enemy killed in this fight adds `mod_kill_stack_damage`
        # to every primary bolt's damage for the rest of the fight.
        # Stack count resets to 0 at spawn (per-fight ShipState).
        if ship.mod_kill_stack_damage > 0 and ship.kills_this_fight > 0:
            kill_bonus = ship.mod_kill_stack_damage * ship.kills_this_fight
            for p in self.projectiles[proj_len_before:]:
                p.damage += kill_bonus
        # Scout-mod hook: Chain Lightning — tag every bolt with chain
        # propagation. On hit, _spawn_chain_child fires a follow-up.
        if ship.mod_chain_lightning_damage > 0:
            for p in self.projectiles[proj_len_before:]:
                p.chain_remaining = max(p.chain_remaining, 2)
                p.chain_damage = ship.mod_chain_lightning_damage
        # Scout-mod hook: Cross-Wired Capacitors — primary fire ALSO
        # restores shield (`mod_cross_wired_ratio` shield per energy
        # spent). The energy was already deducted earlier; here we
        # add the matching shield based on what was spent this shot.
        if ship.mod_cross_wired_ratio > 0 and cls.shield_max > 0:
            shield_gain = cls.primary_energy * ship.mod_cross_wired_ratio
            ship.shield = min(cls.shield_max, ship.shield + shield_gain)
        # Scout-mod hook: Coil Lance — fire a SECOND identical volley
        # in the reverse direction (rear defense while shooting forward).
        # Only happens when the Coil Lance schematic-mod is installed
        # (`mod_lance_charge_max_dmg > 0` flag check) AND we spawned
        # at least one bolt in the forward direction this call.
        if (
            ship.mod_lance_charge_max_dmg > 0
            and len(self.projectiles) > proj_len_before
        ):
            forward_bolts = list(self.projectiles[proj_len_before:])
            for fwd in forward_bolts:
                # Rear-mirror — flip velocity, spawn an opposing copy.
                rear_x = ship.x - fx * nose_offset
                rear_y = ship.y - fy * nose_offset
                self._spawn_projectile(
                    ship,
                    rear_x, rear_y,
                    -fwd.vx, -fwd.vy,
                    fwd.damage,
                    fwd.range_left,
                    fwd.color,
                    radius=fwd.radius,
                    damage_kind=fwd.damage_kind,
                )

    def _spawn_projectile(
        self,
        ship: ShipState,
        x: float, y: float,
        vx: float, vy: float,
        damage: float,
        range_left: float,
        color: tuple[int, int, int],
        radius: float = 3.0,
        homing: bool = False,
        homing_turn_rate: float = 0.0,
        hits_remaining: int = 0,
        return_at_age: float = 0.0,
        spawn_debris_on_hit: bool = False,
        homing_delay: float = 0.0,
        spin_visual: float = 0.0,
        engine_damage_on_hit: float = 0.0,
        is_water: bool = False,
        water_freeze_at_age: float = 0.0,
        initial_range: float = 0.0,
        is_icepeedo: bool = False,
        damage_kind: str = "kinetic",
        chain_remaining: int = 0,
        chain_damage: float = 0.0,
        is_resonance_wave: bool = False,
        wave_growth_per_sec: float = 0.0,
        wave_damage_floor: float = 0.25,
    ) -> None:
        """Append a projectile to the active list. Centralized so the
        MAX_PROJECTILES cap is enforced once regardless of pattern.
        """
        if len(self.projectiles) >= MAX_PROJECTILES:
            return
        self.projectiles.append(Projectile(
            x=x, y=y, vx=vx, vy=vy,
            damage=damage,
            range_left=range_left,
            owner_side=ship.side,
            color=color,
            owner_ship_id=ship.cls.id,
            radius=radius,
            homing=homing,
            homing_turn_rate=homing_turn_rate,
            hits_remaining=hits_remaining,
            return_at_age=return_at_age,
            spawn_debris_on_hit=spawn_debris_on_hit,
            homing_delay=homing_delay,
            spin_visual=spin_visual,
            engine_damage_on_hit=engine_damage_on_hit,
            is_water=is_water,
            water_freeze_at_age=water_freeze_at_age,
            # initial_range defaults to range_left at spawn so the
            # "fraction traveled" check (Cleanser outer-spike crack)
            # has a stable baseline.
            initial_range=(initial_range if initial_range > 0 else range_left),
            is_icepeedo=is_icepeedo,
            damage_kind=damage_kind,
            chain_remaining=chain_remaining,
            chain_damage=chain_damage,
            is_resonance_wave=is_resonance_wave,
            wave_growth_per_sec=wave_growth_per_sec,
            wave_damage_floor=wave_damage_floor,
        ))
        # Muzzle flash — small bright puff at the firing point, tinted
        # to the ship's primary_color. Reuses ImpactFx with tighter
        # params so the visual style stays unified with impact bursts.
        self.impact_fx.append(ImpactFx(
            x=x, y=y,
            color=color,
            max_radius=9.0,
            duration=0.10,
        ))
        # SFX hook: play this ship's primary_fire.wav from the
        # assets/sfx/ships/<ship_id>/ directory the SFX-gen pipeline
        # wrote. Multi-shot patterns spawn several projectiles in one
        # frame, so play once per ship per frame. If the asset isn't
        # there yet the SfxBus logs once and stays silent.
        if self.game is not None and hasattr(self.game, "sfx"):
            if self._fire_sfx_stamp.get(ship.side) != self.time_in_scene:
                self._fire_sfx_stamp[ship.side] = self.time_in_scene
                self.game.sfx.play(f"ships/{ship.cls.id}/primary_fire")

    def _find_owner_for_projectile(self, p: Projectile) -> ShipState | None:
        """Return the ship that fired this projectile, identified by
        side. None for projectiles whose owner is dead/unknown. Used
        by per-firer mod effects (Pulse Cannon stacking, etc.)."""
        for ship in (self.precursor, self.homesteader):
            if ship.side == p.owner_side and ship.alive:
                return ship
        return None

    def _spawn_chain_child(self, parent: Projectile, hit_target: ShipState) -> None:
        """Chain Lightning — spawn a child bolt aimed at the nearest
        OTHER target (asteroid or enemy ship). Bounded by
        `parent.chain_remaining` so the cascade has a finite tail.
        """
        if parent.chain_remaining <= 0:
            return
        # Pick the nearest viable target that isn't the one just hit.
        best = None
        best_d2 = float("inf")
        for ship in (self.precursor, self.homesteader):
            if ship is hit_target or not ship.alive:
                continue
            if ship.side == parent.owner_side:
                continue
            dx = _wrap_shortest_delta(hit_target.x, ship.x, ARENA_W)
            dy = _wrap_shortest_delta(hit_target.y, ship.y, ARENA_H)
            d2 = dx * dx + dy * dy
            if d2 < best_d2:
                best_d2 = d2
                best = (ship.x, ship.y)
        # Fall back to nearest asteroid if no other ship found.
        if best is None:
            for ast in self.asteroids:
                dx = _wrap_shortest_delta(hit_target.x, ast.x, ARENA_W)
                dy = _wrap_shortest_delta(hit_target.y, ast.y, ARENA_H)
                d2 = dx * dx + dy * dy
                if d2 < best_d2:
                    best_d2 = d2
                    best = (ast.x, ast.y)
        if best is None:
            return
        # Direction toward best target.
        dx = _wrap_shortest_delta(hit_target.x, best[0], ARENA_W)
        dy = _wrap_shortest_delta(hit_target.y, best[1], ARENA_H)
        d = math.hypot(dx, dy) or 1.0
        # Child bolt velocity = 700 u/s along direction. Faster than
        # most projectiles since it's hitscan-y.
        bvx = (dx / d) * 700.0
        bvy = (dy / d) * 700.0
        owner_proxy = ShipState(
            cls=self.precursor.cls,  # placeholder — only `.side` matters
            side=parent.owner_side,
            x=hit_target.x, y=hit_target.y, heading=0.0,
        )
        self._spawn_projectile(
            owner_proxy,
            hit_target.x, hit_target.y, bvx, bvy,
            damage=parent.chain_damage,
            range_left=300.0,
            color=(180, 220, 255),
            radius=2.5,
            damage_kind=parent.damage_kind,
            chain_remaining=parent.chain_remaining - 1,
            chain_damage=parent.chain_damage * 0.7,  # diminishing returns
        )

    def _emit_thorn_pulse(self, ship: ShipState) -> None:
        """Thorn Shield — emit a radial damage pulse around `ship` for
        any `_pending_thorn_pulse_amount` accumulated this frame. The
        pulse hits any enemy ship within `mod_thorn_pulse_radius` of
        `ship` for the pending amount. Called once per ship per frame
        after apply_damage has settled.
        """
        pending = getattr(ship, "_pending_thorn_pulse_amount", 0.0)
        if pending <= 0:
            return
        radius2 = ship.mod_thorn_pulse_radius * ship.mod_thorn_pulse_radius
        for other in (self.precursor, self.homesteader):
            if other is ship or not other.alive:
                continue
            if other.side == ship.side:
                continue
            dx = _wrap_shortest_delta(ship.x, other.x, ARENA_W)
            dy = _wrap_shortest_delta(ship.y, other.y, ARENA_H)
            if dx * dx + dy * dy <= radius2:
                other.apply_damage(pending, "energy")
        # Visual ring (reuse burst-visual system).
        self._burst_visuals.append({
            "x": ship.x, "y": ship.y,
            "radius": ship.mod_thorn_pulse_radius,
            "age": 0.0, "lifetime": 0.35,
            "color": (220, 100, 100),
        })
        ship._pending_thorn_pulse_amount = 0.0

    def _homing_target_for(self, p: Projectile) -> ShipState | None:
        """Return the ship a homing projectile should track — the
        only-living-non-side-owner enemy. Returns None if no valid
        target (both dead, or both same-side as owner, which shouldn't
        happen but is guarded for safety).
        """
        for ship in (self.precursor, self.homesteader):
            if ship.alive and ship.side != p.owner_side:
                return ship
        return None

    def _update_projectiles(self, dt: float) -> None:
        survivors: list[Projectile] = []
        for p in self.projectiles:
            # Tick visual spin (lawnmower blade, blade-ring orbitals)
            if p.spin_visual > 0:
                p.spin_angle = (p.spin_angle + p.spin_visual * dt) % math.tau

            # Water → ice conversion mid-flight (Cleanser water spray).
            # After water_freeze_at_age elapses, the droplet "space-
            # freezes" into a normal low-damage ice projectile. Damage
            # halves, color shifts to icy cyan, wetness/push effects
            # turn off (becomes a normal projectile).
            if p.is_water and p.water_freeze_at_age > 0 and p.age >= p.water_freeze_at_age:
                p.is_water = False
                p.damage = max(0.5, p.damage * 0.5)
                p.color = (180, 220, 240)

            # Activate homing after `homing_delay` elapses. Used by
            # Proto-Ur-Quan homing_cluster: missiles spread straight,
            # then start tracking once they're a bit apart.
            if not p.homing and p.homing_delay > 0 and p.age >= p.homing_delay:
                p.homing = True

            # Homing — Melnorme plasmoids. The projectile turns toward
            # the nearest enemy ship each frame, capped at
            # `homing_turn_rate` rad/sec. We pick whichever live ship
            # is NOT the owner's side; if neither is valid, we skip
            # homing this frame.
            if p.homing:
                target = self._homing_target_for(p)
                if target is not None:
                    # Wrap-aware direction to target
                    tdx = _wrap_shortest_delta(p.x, target.x, ARENA_W)
                    tdy = _wrap_shortest_delta(p.y, target.y, ARENA_H)
                    target_heading = math.atan2(tdx, -tdy)
                    # Projectile's current heading (from its velocity)
                    cur_heading = math.atan2(p.vx, -p.vy)
                    delta = (
                        target_heading - cur_heading + math.pi
                    ) % (2 * math.pi) - math.pi
                    max_turn = p.homing_turn_rate * dt
                    turn = max(-max_turn, min(max_turn, delta))
                    new_heading = cur_heading + turn
                    speed = math.hypot(p.vx, p.vy)
                    p.vx = math.sin(new_heading) * speed
                    p.vy = -math.cos(new_heading) * speed

            # Apply gravity from all bodies (planet always + moon when
            # present). Fast beams curve slightly; slow plasma globs
            # arc dramatically — the Pkunk-Mauler vibe. Asteroids do
            # NOT contribute to projectile gravity (they're too small
            # to matter at projectile speeds, and including them would
            # n²-blow up the cost).
            ax, ay = self._gravity_accel(p.x, p.y)
            p.vx += ax * PROJECTILE_GRAVITY_FACTOR * dt
            p.vy += ay * PROJECTILE_GRAVITY_FACTOR * dt

            # Chaff cloud (Defender chaff_spray). Drifts slowly, has
            # a lifetime, doesn't damage. The SLOWDOWN effect on
            # enemy projectiles is applied in a second pass below
            # (after all projectiles have moved this frame).
            if p.is_chaff:
                p.age += dt
                if p.lifetime > 0 and p.age >= p.lifetime:
                    continue   # expired
                # Slow drift only
                p.x = (p.x + p.vx * dt) % ARENA_W
                p.y = (p.y + p.vy * dt) % ARENA_H
                # Drag the drift over time
                p.vx *= 0.985
                p.vy *= 0.985
                survivors.append(p)
                continue

            # Gravity wells — stationary, time-limited, damage anything
            # inside their radius continuously. Skip all other physics.
            if p.is_gravity_well:
                p.age += dt
                if p.lifetime > 0 and p.age >= p.lifetime:
                    continue   # expired
                for target in (self.precursor, self.homesteader):
                    if not target.alive:
                        continue
                    if target.side == p.owner_side:
                        continue
                    dx = self._wrap_delta(p.x, target.x, ARENA_W)
                    dy = self._wrap_delta(p.y, target.y, ARENA_H)
                    if math.hypot(dx, dy) <= p.radius:
                        target.apply_damage(p.damage * dt)
                survivors.append(p)
                continue

            # Age the projectile + handle RHC return — Kohr-Ah Returning
            # Howitzer Cannon. Once the projectile reaches return_at_age,
            # its velocity flips. SC2 canon: the shot would also hit the
            # firing ship on the way back, but without smart AI dodging
            # that's pure self-damage. We keep ownership intact so the
            # return leg only threatens the enemy. (Revisit when player
            # control + smart dodge AI lands.)
            p.age += dt
            if p.return_at_age > 0 and not p.has_returned and p.age >= p.return_at_age:
                p.vx = -p.vx
                p.vy = -p.vy
                p.has_returned = True

            # Resonance wave (Burv Broadcaster) — radius grows linearly
            # over time. The wave's hit zone gets bigger as it propagates,
            # so a near-miss at the firing point becomes a wide hit at
            # the far side of the arena. Combined with the damage falloff
            # below, the wave's identity is: dodge-while-close, easy hit
            # but reduced impact at long range.
            if p.is_resonance_wave and p.wave_growth_per_sec > 0:
                p.radius += p.wave_growth_per_sec * dt

            # Orbital projectiles (FRIED blades / legacy discs) are
            # positioned by `_update_orbital_projectiles` above and
            # skip the normal physics/range path. Hit detection
            # differs by orbital kind:
            #   - Blades (is_blade=True): sample 3 points along the
            #     blade line (base / mid / tip) so the hit zone is the
            #     blade swath, not a disc. Player can fly past at the
            #     right angle and miss.
            #   - Free orbitals (is_blade=False, legacy): single hit
            #     check at the projectile center.
            if p.orbital:
                if p.range_left < 0:
                    continue
                if p.is_blade:
                    host = (
                        self.precursor
                        if id(self.precursor) == p.orbital_host_id
                        else self.homesteader
                    )
                    # Sample 3 points along the blade: base (40% of
                    # blade-length from host), mid (70%), tip (100%).
                    # The 40% lower bound keeps the host's own
                    # collision zone out of the blade sampling — the
                    # blade can't damage someone overlapping the host.
                    blade_axis_x = p.x - host.x
                    blade_axis_y = p.y - host.y
                    # Account for wrap — pick wrap-shortest delta
                    blade_axis_x = _wrap_shortest_delta(host.x, p.x, ARENA_W)
                    blade_axis_y = _wrap_shortest_delta(host.y, p.y, ARENA_H)
                    sample_offsets = (0.40, 0.70, 1.00)
                    BLADE_SAMPLE_RADIUS = 14.0
                    for target in (self.precursor, self.homesteader):
                        if not target.alive:
                            continue
                        if target.side == p.owner_side:
                            continue
                        hit = False
                        for s in sample_offsets:
                            sx = (host.x + blade_axis_x * s) % ARENA_W
                            sy = (host.y + blade_axis_y * s) % ARENA_H
                            dx = self._wrap_delta(sx, target.x, ARENA_W)
                            dy = self._wrap_delta(sy, target.y, ARENA_H)
                            if math.hypot(dx, dy) <= BLADE_SAMPLE_RADIUS + 14.0:
                                hit = True
                                break
                        if hit:
                            target.apply_damage(p.damage * dt)
                    survivors.append(p)
                    continue
                # Free orbital (legacy disc — kept for any future ship
                # that wants the old SC2-style rotating discs).
                despawn = False
                for target in (self.precursor, self.homesteader):
                    if not target.alive:
                        continue
                    if target.side == p.owner_side:
                        continue
                    dx = self._wrap_delta(p.x, target.x, ARENA_W)
                    dy = self._wrap_delta(p.y, target.y, ARENA_H)
                    if math.hypot(dx, dy) <= 18.0 + p.radius:
                        target.apply_damage(p.damage * dt * 4.0)
                survivors.append(p)
                continue

            speed = math.hypot(p.vx, p.vy)
            step = speed * dt
            if step > p.range_left:
                continue
            p.x = (p.x + p.vx * dt) % ARENA_W
            p.y = (p.y + p.vy * dt) % ARENA_H
            p.range_left -= step

            # Body absorption — projectile despawns on contact with
            # planet, moon (when present), or any asteroid. Quick
            # squared-distance check per body; cheap even with several
            # asteroids.
            absorbed = False
            cdx = _wrap_shortest_delta(p.x, PLANET_X, ARENA_W)
            cdy = _wrap_shortest_delta(p.y, PLANET_Y, ARENA_H)
            if cdx * cdx + cdy * cdy < (PLANET_RADIUS + p.radius) ** 2:
                absorbed = True
            if not absorbed and self.has_moon:
                cdx = _wrap_shortest_delta(p.x, self.moon_x, ARENA_W)
                cdy = _wrap_shortest_delta(p.y, self.moon_y, ARENA_H)
                if cdx * cdx + cdy * cdy < (MOON_RADIUS + p.radius) ** 2:
                    absorbed = True
            if not absorbed:
                for ast in self.asteroids:
                    adx = _wrap_shortest_delta(p.x, ast.x, ARENA_W)
                    ady = _wrap_shortest_delta(p.y, ast.y, ARENA_H)
                    if adx * adx + ady * ady < (ast.radius + p.radius) ** 2:
                        # Water droplets PUSH asteroids without
                        # damaging or being absorbed (Aaron's spec
                        # 2026-05-17). Pass through after applying
                        # a small momentum transfer.
                        if p.is_water:
                            proj_speed = max(1.0, math.hypot(p.vx, p.vy))
                            push_strength = 0.6 / max(ast.radius, 10.0)
                            ast.vx += p.vx * push_strength
                            ast.vy += p.vy * push_strength
                            # Cap asteroid speed so a long water stream
                            # doesn't accelerate them indefinitely.
                            ast_speed = math.hypot(ast.vx, ast.vy)
                            MAX_AST_SPEED = 200.0
                            if ast_speed > MAX_AST_SPEED:
                                ast.vx *= MAX_AST_SPEED / ast_speed
                                ast.vy *= MAX_AST_SPEED / ast_speed
                            # Water continues through (no absorption)
                            break
                        absorbed = True
                        break
            if absorbed:
                continue

            # Slower projectiles are *wider* — fiction: missiles, plasma
            # globs, lobbed bolts carry volume. Hitscan beams are
            # pencil-thin. The 2400 reference is the fastest ship-primary
            # speed in the roster (furling/cleanser/defender beams).
            # Inverse scaling, capped 0.6x to 2.5x so the bonus is real
            # but not game-breaking. This was added 2026-05-17 to bring
            # slow-projectile ships (arilou, proto_qor_ah, melnorme,
            # proto_ur_quan) closer to viable — they had <20% win rates
            # vs hitscan even after the AI added target leading.
            speed_factor = max(0.6, min(2.5, 2400.0 / max(speed, 1.0)))

            # Check hits against the *other* side's ship. Hit radius is
            # per-target — derived from each ship sprite's non-transparent
            # bounding box (Aaron 2026-05-18 hit-box tightening). Falls
            # back to SHIP_RADIUS_FALLBACK for procedurally-rendered ships.
            despawn = False
            for target in (self.precursor, self.homesteader):
                if not target.alive:
                    continue
                if target.side == p.owner_side:
                    continue
                # Account for arena wrap — check against the toroidal-nearest copy
                dx = self._wrap_delta(p.x, target.x, ARENA_W)
                dy = self._wrap_delta(p.y, target.y, ARENA_H)
                d = math.hypot(dx, dy)
                target_radius = self._effective_radius(target.cls.id)
                hit_radius = target_radius * speed_factor + p.radius
                if d <= hit_radius:
                    # Default damage application.
                    effective_damage = p.damage

                    # --- Resonance wave damage falloff (Burv) ---
                    # Damage scales from full at spawn → wave_damage_floor
                    # fraction at max range, linearly. The wave is also
                    # immune to its owner via the owner_side filter above.
                    if p.is_resonance_wave:
                        frac_traveled = 1.0 - (
                            p.range_left / max(1.0, p.initial_range)
                        )
                        falloff = 1.0 - (1.0 - p.wave_damage_floor) * frac_traveled
                        effective_damage = p.damage * falloff

                    # --- Cleanser interaction matrix (Aaron 2026-05-17) ---
                    if p.is_water:
                        frac_traveled = 1.0 - (
                            p.range_left / max(1.0, p.initial_range)
                        )
                        is_outer_spike = frac_traveled > 0.70
                        if target.frozen_remaining > 0:
                            # Frozen target:
                            #   close-range water → WASTED
                            #   outer-spike water → CRACK (4× damage)
                            effective_damage = (
                                p.damage * 4.0 if is_outer_spike else 0.0
                            )
                        elif target.wetness >= 30.0 and is_outer_spike:
                            # Wet target + outer-spike water →
                            # contribute to ice_buildup. Reaching 100
                            # triggers auto-freeze (same effect as
                            # the icepeedo on a wet target). Aaron's
                            # spec: "enough spikes will actually do
                            # the freezing instead of the special
                            # freeze ray if you hit with enough of
                            # them on a wet ship."
                            target.ice_buildup = min(
                                100.0, target.ice_buildup + 25.0,
                            )
                            if target.ice_buildup >= 100.0:
                                target.frozen_remaining = 3.0
                                target.ice_buildup = 0.0
                                target.hit_flash = 0.2
                    elif p.is_icepeedo:
                        # Icepeedo contextual effects:
                        if target.frozen_remaining > 0:
                            # Second icepeedo on a frozen target →
                            # CRACK (Aaron spec: same effect as
                            # outer-spike water).
                            effective_damage = p.damage * 4.0
                        elif target.wetness >= 30.0:
                            # Wet target → FREEZE
                            target.frozen_remaining = 3.0
                            target.ice_buildup = 0.0
                        # Dry target → just base damage + frost (small
                        # wetness contribution handled by the generic
                        # water-wets block below would not apply — so
                        # we add some wetness explicitly here.
                        else:
                            target.wetness = min(
                                100.0, target.wetness + 15.0,
                            )

                    # Scout mod: Reflector Shield — chance to bounce
                    # an incoming projectile back at the firer. Only
                    # triggers when the target has shield up (the
                    # reflection physics are *the shield doing it*).
                    if (
                        target.mod_reflect_chance > 0
                        and target.shield > 0
                    ):
                        import random as _random
                        if _random.random() < target.mod_reflect_chance:
                            # Despawn the original projectile by NOT
                            # applying damage and breaking out of the
                            # hit loop. Spawn a mirror going opposite.
                            target.hit_flash = 0.20
                            self._spawn_projectile(
                                target,
                                target.x, target.y,
                                -p.vx, -p.vy,
                                p.damage,
                                range_left=600.0,
                                color=(220, 240, 255),
                                radius=p.radius,
                                damage_kind=p.damage_kind,
                            )
                            despawn = True
                            break
                    # Pulse Cannon stacking damage — if THIS ship (the
                    # firer) has pulse_stack_bonus, each consecutive
                    # hit on the same target ramps damage.
                    firer = self._find_owner_for_projectile(p)
                    if firer is not None and firer.mod_pulse_stack_bonus > 0:
                        stacks = firer.pulse_stacks.get(id(target), 0)
                        effective_damage += stacks * firer.mod_pulse_stack_bonus
                        firer.pulse_stacks[id(target)] = stacks + 1
                    was_alive_before = target.alive
                    target.apply_damage(effective_damage, p.damage_kind)
                    # Spawn an impact FX at the projectile's position.
                    # Bigger damage = bigger puff.
                    self.impact_fx.append(ImpactFx(
                        x=p.x, y=p.y,
                        color=p.color,
                        max_radius=14.0 + min(28.0, effective_damage * 1.2),
                        duration=0.25 + min(0.30, effective_damage * 0.012),
                    ))
                    if self.game is not None and hasattr(self.game, "sfx"):
                        # SFX hook: the shooter's primary_impact.wav.
                        shooter = (self.precursor if p.owner_side == self.precursor.side
                                   else self.homesteader)
                        self.game.sfx.play(f"ships/{shooter.cls.id}/primary_impact")
                        # Alert SFX on damage-threshold crossings (once
                        # each per ship per fight): warning when shields
                        # drop below 25%, danger when hull does.
                        s_max = max(1.0, target.cls.shield_max)
                        h_max = max(1.0, target.cls.hull_max)
                        if (not target.alert_warning_fired
                                and target.shield / s_max < 0.25):
                            target.alert_warning_fired = True
                            self.game.sfx.play("ui/alert_warning")
                        if (not target.alert_danger_fired
                                and target.hull / h_max < 0.25):
                            target.alert_danger_fired = True
                            self.game.sfx.play("ui/alert_danger")
                    # If the hit killed the target, spawn a death FX.
                    if not target.alive and target.cls.id not in self._death_fx_spawned:
                        self.death_fx.append(DeathFx(
                            x=target.x, y=target.y,
                            color=target.cls.hull_color,
                            seed=hash((target.cls.id, int(self.time_in_scene * 1000))) & 0xFFFF,
                        ))
                        self._death_fx_spawned.add(target.cls.id)
                    # Crew perk: Mira-Rou normal — every primary hit
                    # the firer lands reduces their special cooldown by
                    # `cooldown_reduce_per_hit` seconds. Reads firer
                    # off projectile side.
                    if firer is not None and firer.mod_cooldown_reduce_per_hit > 0:
                        firer.special_cooldown_left = max(
                            0.0,
                            firer.special_cooldown_left
                            - firer.mod_cooldown_reduce_per_hit,
                        )
                    # Crew perk: Bren-Vor post-quest — track this kill
                    # if the projectile from `firer` just killed
                    # `target`. The per-fight count multiplies into
                    # `mod_kill_stack_damage` on subsequent shots.
                    if was_alive_before and not target.alive and firer is not None:
                        firer.kills_this_fight += 1
                    # Scout mod: Chain Lightning — child bolt to nearest
                    # other target. Decrement chain count to bound the
                    # cascade.
                    if p.chain_remaining > 0:
                        self._spawn_chain_child(p, target)
                    # Water adds wetness on non-frozen targets. Cleanser's
                    # freeze trigger is gated by target wetness >= 30.
                    if p.is_water and target.frozen_remaining <= 0:
                        target.wetness = min(100.0, target.wetness + 4.0)
                    # Engine-seeker debuff: accumulate engine damage on
                    # the target. Applied in _apply_action as a perm
                    # top_speed + acceleration nerf (clamped to a min
                    # floor so a ship is never fully immobile).
                    if p.engine_damage_on_hit > 0:
                        target.engine_damage_accumulated += p.engine_damage_on_hit
                    # Resonance-pulse style: spawn visual debris when
                    # the projectile pops on contact. Pieces fly
                    # outward from the impact point in random
                    # directions; they use the thruster-particle
                    # system since they're visual-only.
                    if p.spawn_debris_on_hit:
                        self._spawn_debris_particles(target, p.color)
                    # Multi-hit projectiles (Androsynth bubbles, etc.)
                    # survive contact until hits_remaining is exhausted.
                    if p.hits_remaining > 0:
                        p.hits_remaining -= 1
                        # Brief invuln window to prevent multi-hitting
                        # the same target this frame: nudge projectile
                        # past the target along its current velocity.
                        nudge_speed = max(1.0, math.hypot(p.vx, p.vy))
                        nudge_dist = hit_radius * 1.2
                        p.x = (p.x + (p.vx / nudge_speed) * nudge_dist) % ARENA_W
                        p.y = (p.y + (p.vy / nudge_speed) * nudge_dist) % ARENA_H
                    else:
                        despawn = True
                    break
            if not despawn:
                survivors.append(p)
        self.projectiles = survivors

        # --- Chaff slowdown pass ---
        # After all projectiles have moved this frame, check each non-
        # chaff projectile against each chaff cloud. Inside a chaff
        # cloud, the projectile's velocity is multiplied by 0.92 per
        # frame — sustained contact decays it toward zero. Friendly-
        # fire-aware: the Defender's own projectiles ignore its own
        # chaff (chaff.owner_side == projectile.owner_side).
        chaffs = [p for p in self.projectiles if p.is_chaff]
        if chaffs:
            for p in self.projectiles:
                if p.is_chaff or p.is_gravity_well or p.orbital:
                    continue
                for chaff in chaffs:
                    if chaff.owner_side == p.owner_side:
                        continue
                    cdx = self._wrap_delta(p.x, chaff.x, ARENA_W)
                    cdy = self._wrap_delta(p.y, chaff.y, ARENA_H)
                    if cdx * cdx + cdy * cdy < chaff.radius * chaff.radius:
                        p.vx *= 0.92
                        p.vy *= 0.92
                        break

    def _wrap_delta(self, a: float, b: float, axis: float) -> float:
        d = a - b
        if d > axis / 2:
            d -= axis
        elif d < -axis / 2:
            d += axis
        return d

    # ------------------------------------------------------------------
    # Combat FX renderers
    # ------------------------------------------------------------------

    def _draw_impact_fx(
        self,
        screen: pygame.Surface,
        fx: "ImpactFx",
        ox: float, oy: float, scale: float,
    ) -> None:
        """Expanding blast-puff at the impact point. Two concentric
        rings — a fast bright inner flash, then a slower outer halo —
        fading to transparent over the FX duration.
        """
        progress = min(1.0, fx.t / fx.duration)
        sx, sy = self._world_to_screen(fx.x, fx.y, ox, oy, scale)
        # Inner flash: fades fastest, brightest at t=0
        inner_r = max(1, int((6 + fx.max_radius * 0.35 * progress) * scale))
        inner_a = int(255 * (1 - progress) ** 2)
        # Outer halo: expands more, fades slower
        outer_r = max(1, int(fx.max_radius * (0.4 + 0.9 * progress) * scale))
        outer_a = int(180 * (1 - progress))
        # Brighten color toward white for the flash
        flash_color = (
            min(255, int(fx.color[0] * 0.4 + 255 * 0.6)),
            min(255, int(fx.color[1] * 0.4 + 230 * 0.6)),
            min(255, int(fx.color[2] * 0.4 + 200 * 0.6)),
        )
        size = outer_r * 2 + 4
        surf = pygame.Surface((size, size), pygame.SRCALPHA)
        c = (size // 2, size // 2)
        # Outer halo
        pygame.draw.circle(surf, (*fx.color, outer_a), c, outer_r)
        # Inner bright flash
        pygame.draw.circle(surf, (*flash_color, inner_a), c, inner_r)
        screen.blit(surf, (int(sx) - size // 2, int(sy) - size // 2),
                    special_flags=pygame.BLEND_RGBA_ADD)

    def _draw_death_fx(
        self,
        screen: pygame.Surface,
        fx: "DeathFx",
        ox: float, oy: float, scale: float,
    ) -> None:
        """Ship-destruction explosion. Three layered effects:
        1. Bright central core flash (peaks early, fades fast)
        2. Expanding shockwave ring (white-yellow, grows to ~70 wu)
        3. 14 colored debris particles flying outward (in hull color)
        """
        progress = min(1.0, fx.t / fx.duration)
        sx, sy = self._world_to_screen(fx.x, fx.y, ox, oy, scale)
        # 1. Core flash — peaks at progress ~0.15
        flash_curve = max(0.0, 1.0 - abs(progress - 0.10) * 7)
        flash_r = max(2, int((10 + 20 * flash_curve) * scale))
        flash_a = int(255 * flash_curve)
        # 2. Shockwave ring — expanding outward
        ring_r = max(1, int(70 * progress * scale))
        ring_thick = max(1, int(4 * (1 - progress) * scale))
        ring_a = int(220 * (1 - progress))
        size = ring_r * 2 + ring_thick * 2 + 8
        surf = pygame.Surface((size, size), pygame.SRCALPHA)
        c = (size // 2, size // 2)
        # Shockwave ring
        if ring_r > 0 and ring_a > 0:
            pygame.draw.circle(surf, (255, 240, 200, ring_a), c, ring_r, ring_thick)
        # Core flash
        if flash_a > 0:
            pygame.draw.circle(surf, (255, 240, 200, flash_a), c, flash_r)
            pygame.draw.circle(surf, (255, 255, 230, flash_a), c,
                               max(1, flash_r // 2))
        screen.blit(surf, (int(sx) - size // 2, int(sy) - size // 2),
                    special_flags=pygame.BLEND_RGBA_ADD)
        # 3. Debris particles — 14 colored chunks radiating outward.
        # Deterministic per fx.seed so the pattern is stable per playback.
        rng = random.Random(fx.seed)
        for i in range(14):
            angle = (i / 14) * math.tau + rng.uniform(-0.18, 0.18)
            speed = rng.uniform(30, 80)
            life = rng.uniform(0.6, 1.0)
            t_frac = min(1.0, fx.t / life)
            if t_frac >= 1.0:
                continue
            dist = speed * fx.t
            px = fx.x + math.cos(angle) * dist
            py = fx.y + math.sin(angle) * dist
            psx, psy = self._world_to_screen(px, py, ox, oy, scale)
            chunk_a = int(220 * (1 - t_frac))
            chunk_r = max(1, int(rng.uniform(2, 4) * scale))
            chunk_surf = pygame.Surface((chunk_r * 2 + 2, chunk_r * 2 + 2),
                                         pygame.SRCALPHA)
            pygame.draw.circle(chunk_surf, (*fx.color, chunk_a),
                                (chunk_r + 1, chunk_r + 1), chunk_r)
            screen.blit(chunk_surf, (int(psx) - chunk_r - 1, int(psy) - chunk_r - 1))

    # ------------------------------------------------------------------
    # Result + finish
    # ------------------------------------------------------------------

    def _record_result(
        self,
        winner: ShipState | None,
        loser: ShipState | None,
        timed_out: bool = False,
    ) -> None:
        self.result = CombatResult(
            winner_side=winner.side if winner else None,
            winner_ship=winner.cls if winner else None,
            loser_ship=loser.cls if loser else None,
            duration=self.time_in_scene,
            timed_out=timed_out,
        )
        self.time_since_result = 0.0

    def _finish(self) -> None:
        assert self.game is not None
        if self.on_finish is not None:
            self.on_finish(self.result)
        else:
            # Default: bounce back to SuperMelee picker
            from scz.combat.super_melee import SuperMeleeScene
            self.game.set_scene(SuperMeleeScene())

    def _result_text(self) -> str:
        if self.result is None:
            return ""
        if self.result.winner_side is None:
            return "DOUBLE KO"
        winner_name = (
            self.result.winner_ship.name if self.result.winner_ship else "?"
        )
        if self.result.timed_out:
            return f"TIMEOUT  ·  {winner_name} stands"
        return f"VICTORY  ·  {winner_name}"

    # ------------------------------------------------------------------
    # Rendering helpers
    # ------------------------------------------------------------------

    def _scale(self) -> float:
        """Returns the current camera scale. Kept for backward
        compatibility with renderers that still pass an explicit
        `scale` arg to per-element draw paths.
        """
        return self.camera_scale

    def _update_camera(self) -> None:
        """SC2-style camera update — recompute target position + zoom
        each frame from the live ship positions, then smoothly lerp
        toward the target. Wrap-aware: when the two ships are near
        opposite arena edges, the camera follows the wrap-shortest
        midpoint (not the long way around). Snaps to target on the
        first frame so fights don't start with a zoom-in animation.
        """
        # Midpoint between ships (wrap-aware). Use precursor as the
        # reference and add half of the wrap-shortest delta to
        # homesteader.
        a = self.precursor
        b = self.homesteader
        dx = _wrap_shortest_delta(a.x, b.x, ARENA_W)
        dy = _wrap_shortest_delta(a.y, b.y, ARENA_H)
        mid_x = (a.x + dx * 0.5) % ARENA_W
        mid_y = (a.y + dy * 0.5) % ARENA_H

        # Zoom level from inter-ship separation. Bigger distance →
        # smaller scale (zoom out). Computed independently per-axis,
        # take min so both axes fit.
        sep_x = abs(dx) + CAMERA_DIST_MARGIN
        sep_y = abs(dy) + CAMERA_DIST_MARGIN
        # Target frac × viewport size = max screen pixels we want
        # the inter-ship distance to span. scale = pixels / world.
        target_w = self.screen_w * CAMERA_TARGET_FRAC
        target_h = self.screen_h * CAMERA_TARGET_FRAC
        scale_x = target_w / max(sep_x, 1.0)
        scale_y = target_h / max(sep_y, 1.0)
        target_scale = max(
            CAMERA_MIN_SCALE,
            min(CAMERA_MAX_SCALE, min(scale_x, scale_y)),
        )

        if not self._camera_initialized:
            # First-frame snap — no lerp animation visible to the user.
            self.camera_x = mid_x
            self.camera_y = mid_y
            self.camera_scale = target_scale
            self._camera_initialized = True
            return

        # Smooth toward target. Camera position lerp must be wrap-aware
        # — interpolating naively across the wrap edge would dash the
        # camera the long way around.
        cam_dx = _wrap_shortest_delta(self.camera_x, mid_x, ARENA_W)
        cam_dy = _wrap_shortest_delta(self.camera_y, mid_y, ARENA_H)
        self.camera_x = (self.camera_x + cam_dx * CAMERA_LERP) % ARENA_W
        self.camera_y = (self.camera_y + cam_dy * CAMERA_LERP) % ARENA_H
        # Scale lerp is plain (not wrap-aware — scale is scalar).
        self.camera_scale += (target_scale - self.camera_scale) * CAMERA_LERP

    def _world_to_screen(
        self, x: float, y: float, ox: float = 0.0, oy: float = 0.0, scale: float = 1.0
    ) -> tuple[float, float]:
        """Map a world-space (x, y) onto the current pygame surface.

        SC2-style wrap-aware: the screen position is computed from the
        wrap-shortest delta between the camera and the object. An object
        near the arena's left edge while the camera is near the right
        edge will render to the *right* of screen (via the wrap) — the
        natural "the planet floats by from the other side" behavior.

        The `ox, oy, scale` parameters are LEGACY (kept for backward
        compatibility with renderer code paths that still pass them);
        they are ignored — the camera state is the single source of
        truth now.
        """
        dx = _wrap_shortest_delta(self.camera_x, x, ARENA_W)
        dy = _wrap_shortest_delta(self.camera_y, y, ARENA_H)
        return (
            self.screen_w * 0.5 + dx * self.camera_scale,
            self.screen_h * 0.5 + dy * self.camera_scale,
        )

    def _effective_radius(self, ship_id: str) -> float:
        """Per-ship collision radius derived from the sprite's non-
        transparent bounding box. Returns `SHIP_RADIUS_FALLBACK` for
        ships without sprites loaded (procedural-polygon path). Loads
        the sprite if not yet cached so the radius is populated.

        Used by projectile-vs-ship hit-detection so the hitbox matches
        the actual visible silhouette instead of a fixed-size circle
        (Aaron 2026-05-18: "weapons should only consider non-black
        pixels as part of the hit box").
        """
        # If sprite cache lookup hasn't run yet, force a load (which
        # populates _ship_effective_radius as a side-effect).
        if ship_id not in self._ship_effective_radius:
            self._load_ship_sprite(ship_id)
        return self._ship_effective_radius.get(
            ship_id, SHIP_RADIUS_FALLBACK,
        )

    def _load_projectile_sprite(self, ship_id: str) -> pygame.Surface | None:
        """Return the projectile sprite for a ship's primary weapon, or None.

        Looks for `projectile_<ship_id>.png` in `SHIP_SPRITE_DIR`. The
        loaded image is scaled so its longest axis is
        `PROJECTILE_SPRITE_BASE_SIZE` world units and cached. Missing
        loads fall back to the colored-circle rendering in the draw loop.
        """
        if ship_id in self._projectile_sprite_cache:
            return self._projectile_sprite_cache[ship_id]
        path = os.path.join(SHIP_SPRITE_DIR, f"projectile_{ship_id}.png")
        if not os.path.isfile(path):
            self._projectile_sprite_cache[ship_id] = None
            return None
        try:
            img = pygame.image.load(path).convert_alpha()
            w, h = img.get_size()
            longest = max(w, h)
            if longest != PROJECTILE_SPRITE_BASE_SIZE:
                f = PROJECTILE_SPRITE_BASE_SIZE / longest
                img = pygame.transform.smoothscale(
                    img, (max(1, int(w * f)), max(1, int(h * f))),
                )
        except (pygame.error, OSError):
            img = None
        self._projectile_sprite_cache[ship_id] = img
        return img

    def _load_ship_sprite(self, ship_id: str) -> pygame.Surface | None:
        """Return the base (nose-up) sprite for a ship class, or None.

        Sprites live in `SHIP_SPRITE_DIR/SHIP_SPRITES[ship_id]`. The
        loaded image is scaled so its longest axis is `SHIP_SPRITE_BASE_SIZE`
        world units and cached. Missing/failed loads are cached as None
        so the fallback polygon path is taken without re-trying every
        frame.

        Near-black pixels (RGB all ≤10) are converted to alpha-zero so
        the visible silhouette is the actual ship, not a black square.
        Many Firefly outputs return with opaque-black backgrounds rather
        than transparent alpha; this is the runtime fix per Aaron's
        2026-05-18 note.

        Also computes an `effective_radius` per ship from the bounding
        rect of the non-transparent pixels — cached in
        `_ship_effective_radius` and used by the combat hit-detection
        path so projectiles only count non-black pixels as part of the
        hitbox (Aaron 2026-05-18: "weapons should only consider non-
        black pixels as part of the hit box").
        """
        if ship_id in self._ship_sprite_cache:
            return self._ship_sprite_cache[ship_id]
        fname = SHIP_SPRITES.get(ship_id)
        if fname is None:
            self._ship_sprite_cache[ship_id] = None
            return None
        path = os.path.join(SHIP_SPRITE_DIR, fname)
        if not os.path.isfile(path):
            self._ship_sprite_cache[ship_id] = None
            return None
        try:
            img = pygame.image.load(path).convert_alpha()
            # Zero out near-black pixels' alpha so the visible silhouette
            # is the actual ship, not a black square. See docstring.
            _make_near_black_transparent(img, threshold=10)
            w, h = img.get_size()
            longest = max(w, h)
            if longest != SHIP_SPRITE_BASE_SIZE:
                f = SHIP_SPRITE_BASE_SIZE / longest
                img = pygame.transform.smoothscale(
                    img, (max(1, int(w * f)), max(1, int(h * f))),
                )
            # Compute per-sprite effective collision radius from the
            # bounding rect of non-transparent pixels. Used in the hit-
            # detection path to tighten the circle to match the visible
            # silhouette.
            bbox = img.get_bounding_rect(min_alpha=8)
            if bbox.width > 0 and bbox.height > 0:
                eff = max(bbox.width, bbox.height) * 0.5
            else:
                eff = SHIP_RADIUS_FALLBACK
            self._ship_effective_radius[ship_id] = float(eff)
        except (pygame.error, OSError):
            img = None
        self._ship_sprite_cache[ship_id] = img
        return img

    def _draw_lassos(
        self,
        screen: pygame.Surface,
        ox: float,
        oy: float,
        scale: float,
    ) -> None:
        """Render the Persuader's tractor-lasso rope while latched.

        Draws a wiggling yellow energy tether between the Persuader
        and its captive plus a faint marker ring at the orbit center.
        The wiggle is generated from the orbit angle + time-in-scene
        so it reads as live, taut, oscillating energy — not a static
        line.
        """
        for ship in (self.precursor, self.homesteader):
            if ship.lasso_target_id == 0:
                continue
            captive = self._find_ship_by_id(ship.lasso_target_id)
            if captive is None or not captive.alive:
                continue
            psx, psy = self._world_to_screen(
                ship.x, ship.y, ox, oy, scale,
            )
            csx, csy = self._world_to_screen(
                captive.x, captive.y, ox, oy, scale,
            )
            # Faint center marker — small ring at orbit pivot.
            ccx, ccy = self._world_to_screen(
                ship.lasso_orbit_cx, ship.lasso_orbit_cy, ox, oy, scale,
            )
            pygame.draw.circle(
                screen, (180, 140, 60),
                (int(ccx), int(ccy)), max(2, int(4 * scale)), 1,
            )
            # Wiggling lasso rope — sample N points along the straight
            # line and perturb each laterally by a sine in time + index.
            ROPE_SEGMENTS = 10
            rope_color = (255, 220, 120)
            rope_color_dim = (200, 160, 60)
            dx = csx - psx
            dy = csy - psy
            seg_len = math.hypot(dx, dy) or 1.0
            # Perpendicular unit vector for the wiggle amplitude.
            perp_x = -dy / seg_len
            perp_y = dx / seg_len
            # Amplitude shrinks at the endpoints, peaks at the middle.
            t_phase = self.time_in_scene * 8.0 + ship.lasso_orbit_angle * 2.0
            points: list[tuple[int, int]] = []
            for i in range(ROPE_SEGMENTS + 1):
                u = i / ROPE_SEGMENTS
                # Smooth bell-shape envelope for the wiggle.
                env = math.sin(u * math.pi)
                wiggle = math.sin(u * 7.0 + t_phase) * 6.0 * env
                px = psx + dx * u + perp_x * wiggle
                py = psy + dy * u + perp_y * wiggle
                points.append((int(px), int(py)))
            if len(points) >= 2:
                # Outer (dim, fatter) glow + inner (bright, thin) core.
                pygame.draw.lines(
                    screen, rope_color_dim, False, points, 4,
                )
                pygame.draw.lines(
                    screen, rope_color, False, points, 2,
                )
            # Anchor pulses at the captive end — small pulsing star.
            pulse_r = int(6 + 3 * math.sin(t_phase * 1.5))
            pygame.draw.circle(
                screen, rope_color, (int(csx), int(csy)), pulse_r, 2,
            )

    def _draw_ship(
        self,
        screen: pygame.Surface,
        ship: ShipState,
        enemy: ShipState,
        ox: float,
        oy: float,
        scale: float,
    ) -> None:
        if not ship.alive:
            # Brief wreck
            sx, sy = self._world_to_screen(ship.x, ship.y, ox, oy, scale)
            pygame.draw.circle(screen, (180, 60, 60), (int(sx), int(sy)), 14, 1)
            pygame.draw.circle(screen, (140, 40, 40), (int(sx), int(sy)), 8, 1)
            return
        sx, sy = self._world_to_screen(ship.x, ship.y, ox, oy, scale)

        # Sprite path — try to blit a rotated Firefly-generated sprite.
        sprite = self._load_ship_sprite(ship.cls.id)
        if sprite is not None:
            # Convert game heading to pygame rotation. heading=0 means
            # nose pointing -y (up); pygame.transform.rotate is CCW. So
            # angle_degrees = -math.degrees(heading) gives the right
            # facing for sprites authored nose-up.
            # Compose heading rotation with the per-sprite authored
            # orientation offset (Aaron 2026-05-18: many sprites came
            # back nose-sideways from Firefly; ShipClass.sprite_rotation_offset_deg
            # corrects them at render time so the green nose-pip lands
            # on the actual nose).
            angle_deg = (
                -math.degrees(ship.heading)
                + getattr(ship.cls, "sprite_rotation_offset_deg", 0.0)
            )
            rotated = pygame.transform.rotozoom(sprite, angle_deg, scale)
            if ship.hit_flash > 0:
                t = ship.hit_flash / 0.25
                # Additive overlay tints the sprite warm-white on hit.
                tint = (int(t * 180), int(t * 90), int(t * 90), 0)
                flashed = rotated.copy()
                flashed.fill(tint, special_flags=pygame.BLEND_RGBA_ADD)
                rotated = flashed
            rect = rotated.get_rect(center=(int(sx), int(sy)))
            screen.blit(rotated, rect)
            if ship.cls.shield_max > 0 and ship.shield > 0:
                frac = max(0.0, min(1.0, ship.shield / ship.cls.shield_max))
                shield_color = (
                    min(255, int(120 * frac + 60)),
                    min(255, int(160 * frac + 60)),
                    min(255, int(180 * frac + 60)),
                )
                radius = max(8, int(max(rect.width, rect.height) * 0.6))
                pygame.draw.circle(
                    screen, shield_color, (int(sx), int(sy)), radius, 1,
                )
            self._draw_wetness_visual(screen, ship, sx, sy, scale)
            self._draw_freeze_visual(screen, ship, sx, sy, scale)
            self._draw_inertia_halt_visual(screen, ship, sx, sy, scale)
            self._draw_target_indicator(
                screen, ship, enemy, ox, oy, scale,
            )
            return

        # Polygon fallback (ships without sprites yet).
        cos_h = math.cos(ship.heading)
        sin_h = math.sin(ship.heading)
        # Silhouette: simple shape; mass + style suggest tweaks
        size = 14
        s = ship.cls.silhouette
        if s in ("scout", "skiff"):
            pts = [(0, -size), (-size * 0.65, size * 0.55), (size * 0.65, size * 0.55)]
        elif s == "blade":
            pts = [(0, -size), (-size * 0.4, size * 0.6), (0, size * 0.3), (size * 0.4, size * 0.6)]
        elif s in ("heavy", "cruiser"):
            size = 18
            pts = [
                (0, -size), (-size * 0.85, -size * 0.1),
                (-size * 0.6, size * 0.7), (size * 0.6, size * 0.7),
                (size * 0.85, -size * 0.1),
            ]
        elif s == "warship":
            size = 16
            pts = [(0, -size), (-size, size * 0.4), (-size * 0.3, size * 0.5),
                   (size * 0.3, size * 0.5), (size, size * 0.4)]
        else:  # sentinel
            size = 15
            pts = [(0, -size), (-size * 0.5, -size * 0.2), (-size * 0.7, size * 0.5),
                   (size * 0.7, size * 0.5), (size * 0.5, -size * 0.2)]
        rotated = []
        for lx, ly in pts:
            rx = lx * cos_h - ly * sin_h
            ry = lx * sin_h + ly * cos_h
            rotated.append((sx + rx * scale, sy + ry * scale))
        # Flash on damage
        body_color = ship.cls.hull_color
        if ship.hit_flash > 0:
            t = ship.hit_flash / 0.25
            body_color = (
                min(255, int(body_color[0] + t * 120)),
                min(255, int(body_color[1] + t * 60)),
                min(255, int(body_color[2] + t * 60)),
            )
        pygame.draw.polygon(screen, body_color, rotated)
        pygame.draw.polygon(screen, ship.cls.accent_color, rotated, 1)
        # Shield ring
        if ship.cls.shield_max > 0 and ship.shield > 0:
            frac = max(0.0, min(1.0, ship.shield / ship.cls.shield_max))
            shield_color = (
                min(255, int(120 * frac + 60)),
                min(255, int(160 * frac + 60)),
                min(255, int(180 * frac + 60)),
            )
            pygame.draw.circle(
                screen, shield_color, (int(sx), int(sy)),
                max(1, int((size + 6) * scale * 1.3)), 1,
            )
        self._draw_inertia_halt_visual(screen, ship, sx, sy, scale)
        self._draw_target_indicator(screen, ship, enemy, ox, oy, scale)

    def _draw_freeze_visual(
        self,
        screen: pygame.Surface,
        ship: ShipState,
        sx: float, sy: float,
        scale: float,
    ) -> None:
        """Frozen-ship overlay (Cleanser freeze target). A cyan-white
        ice block surrounds the ship while frozen_remaining > 0; also
        a fade-time-remaining marker as a thin clock-ring."""
        if ship.frozen_remaining <= 0:
            return
        ice_r = int(22 * scale)
        ice_surf = pygame.Surface(
            (ice_r * 2 + 6, ice_r * 2 + 6), pygame.SRCALPHA,
        )
        # Layered ice: outer faint + inner shimmer
        pygame.draw.circle(
            ice_surf, (180, 220, 250, 130),
            (ice_r + 3, ice_r + 3), ice_r,
        )
        pygame.draw.circle(
            ice_surf, (220, 240, 255, 200),
            (ice_r + 3, ice_r + 3), ice_r, 2,
        )
        screen.blit(
            ice_surf, (int(sx) - ice_r - 3, int(sy) - ice_r - 3),
        )
        # Crystal facets — 6 short tick marks around the perimeter
        ticks = pygame.time.get_ticks() / 1000.0
        for k in range(6):
            a = k * (math.tau / 6) + ticks * 0.4
            tx = sx + math.cos(a) * ice_r
            ty = sy + math.sin(a) * ice_r
            pygame.draw.circle(
                screen, (255, 255, 255), (int(tx), int(ty)), 2,
            )

    def _draw_wetness_visual(
        self,
        screen: pygame.Surface,
        ship: ShipState,
        sx: float, sy: float,
        scale: float,
    ) -> None:
        """Wet-ship tint (Cleanser water buildup). A subtle blue
        shimmer around the ship proportional to wetness."""
        if ship.wetness < 5.0:
            return
        frac = min(1.0, ship.wetness / 100.0)
        ring_r = int(18 * scale)
        alpha = int(40 + frac * 80)
        wet_surf = pygame.Surface(
            (ring_r * 2 + 4, ring_r * 2 + 4), pygame.SRCALPHA,
        )
        pygame.draw.circle(
            wet_surf, (90, 160, 230, alpha),
            (ring_r + 2, ring_r + 2), ring_r, 1,
        )
        screen.blit(
            wet_surf, (int(sx) - ring_r - 2, int(sy) - ring_r - 2),
        )

    def _draw_inertia_halt_visual(
        self,
        screen: pygame.Surface,
        ship: ShipState,
        sx: float, sy: float,
        scale: float,
    ) -> None:
        """Stasis-bubble visual while inertia_halt is active. A faint
        pulsing cyan-white ring around the ship, plus crosshair tick
        marks at cardinal points — reads as "ship locked in place."
        """
        if not (
            ship.special_active
            and ship.cls.special_ability == "inertia_halt"
        ):
            return
        ticks = pygame.time.get_ticks() / 1000.0
        pulse = (math.sin(ticks * 6) + 1) / 2   # 0..1
        ring_color = (
            int(120 + pulse * 120),
            int(220 + pulse * 35),
            int(240),
        )
        ring_r = int(22 * scale)
        alpha = int(120 + pulse * 80)
        ring_surf = pygame.Surface(
            (ring_r * 2 + 4, ring_r * 2 + 4), pygame.SRCALPHA,
        )
        pygame.draw.circle(
            ring_surf, (*ring_color, alpha),
            (ring_r + 2, ring_r + 2), ring_r, 1,
        )
        screen.blit(
            ring_surf, (int(sx) - ring_r - 2, int(sy) - ring_r - 2),
        )
        # Cardinal tick marks just outside the ring — reads as "locked"
        for i, (dx, dy) in enumerate(((1, 0), (0, 1), (-1, 0), (0, -1))):
            tx = sx + dx * (ring_r + 3)
            ty = sy + dy * (ring_r + 3)
            pygame.draw.line(
                screen, ring_color,
                (tx, ty), (tx + dx * 3, ty + dy * 3), 2,
            )

    def _draw_target_indicator(
        self,
        screen: pygame.Surface,
        ship: ShipState,
        enemy: ShipState,
        ox: float,
        oy: float,
        scale: float,
    ) -> None:
        """Small green target-lock light at the ship's nose. Bright +
        haloed when ship heading aligns with the enemy direction;
        dim/off otherwise.

        Per Aaron's spec (2026-05-17): there's NO lock-on mechanic —
        the enemy IS the target, always. The indicator simply tells the
        player when their nose-forward firing line is aligned, since
        many weapons fire forward and players need to know "right now,
        if I fire, I'd hit them." Universal across ship types.
        """
        if not enemy.alive:
            return
        # Wrap-shortest direction to enemy
        dx = _wrap_shortest_delta(ship.x, enemy.x, ARENA_W)
        dy = _wrap_shortest_delta(ship.y, enemy.y, ARENA_H)
        target_heading = math.atan2(dx, -dy)
        delta = (target_heading - ship.heading + math.pi) % (2 * math.pi) - math.pi
        # 6-degree tolerance — tight enough that on-target really means
        # on-target, loose enough that the player can ride the light to
        # a clean shot.
        TARGET_LOCK_TOLERANCE = math.radians(6.0)
        on_target = abs(delta) < TARGET_LOCK_TOLERANCE

        # Indicator position: just ahead of the ship body. Same vector
        # math as the firing nose offset.
        nose_offset = 18.0
        front_x = ship.x + math.sin(ship.heading) * nose_offset
        front_y = ship.y - math.cos(ship.heading) * nose_offset
        sx, sy = self._world_to_screen(front_x, front_y, ox, oy, scale)
        radius = max(2, int(3 * scale))

        if on_target:
            # Bright green light + pulsing halo for "ON TARGET"
            ticks = pygame.time.get_ticks() / 1000.0
            pulse = (math.sin(ticks * 8) + 1) / 2   # fast pulse, satisfying
            halo_r = radius * 3 + int(pulse * 2)
            halo_surf = pygame.Surface(
                (halo_r * 2 + 4, halo_r * 2 + 4), pygame.SRCALPHA,
            )
            pygame.draw.circle(
                halo_surf, (80, 255, 120, int(110 + pulse * 60)),
                (halo_r + 2, halo_r + 2), halo_r,
            )
            screen.blit(
                halo_surf, (int(sx) - halo_r - 2, int(sy) - halo_r - 2),
            )
            pygame.draw.circle(
                screen, (160, 255, 180), (int(sx), int(sy)), radius,
            )
        else:
            # Dim green pip — visible enough that the player knows
            # where the sight is, faint enough not to compete with the
            # ship body.
            pygame.draw.circle(
                screen, (40, 90, 50), (int(sx), int(sy)), radius,
            )

    def _draw_hud(self, screen: pygame.Surface) -> None:
        assert self.font is not None
        # Pull per-species instance names (canonical-first-encounter for
        # now; future encounter-id-seeded variation per the naming
        # conventions canon in `references/lore/species-naming-conventions.md`).
        from scz.content.species_names import (
            SHIP_CLASS_TO_SPECIES_ID,
            name_for_first_encounter,
        )
        # Side panels — left = Precursor, right = Homesteader
        for ship, x_anchor, align in (
            (self.precursor, 24, "left"),
            (self.homesteader, self.screen_w - 380, "left"),
        ):
            cls = ship.cls
            y = 24
            # Instance name — the headline. Falls back to the class
            # name if the ship-class id isn't yet registered in the
            # species-names mapping.
            species_id = SHIP_CLASS_TO_SPECIES_ID.get(cls.id)
            if species_id is not None:
                instance_name = name_for_first_encounter(species_id)
                screen.blit(
                    self.font.render(
                        instance_name, True, ship.cls.accent_color,
                    ),
                    (x_anchor, y),
                )
                y += 22
                # Class name as a sub-label
                screen.blit(
                    self.font.render(
                        cls.name, True, (180, 180, 200),
                    ),
                    (x_anchor, y),
                )
                y += 24
            else:
                # Fallback: original single-line class name display
                screen.blit(
                    self.font.render(cls.name, True, ship.cls.accent_color),
                    (x_anchor, y),
                )
                y += 28
            screen.blit(
                self.font.render(
                    f"{cls.side.upper():<12s}  {cls.points} pts",
                    True, (180, 180, 200),
                ),
                (x_anchor, y),
            )
            y += 24
            # Hull bar
            self._bar(
                screen, x_anchor, y, 320, 12,
                ship.hull / max(1, cls.hull_max),
                (220, 80, 80),
                f"HULL   {int(ship.hull):3d}/{cls.hull_max}",
            )
            y += 22
            # Shield bar (if any)
            if cls.shield_max > 0:
                self._bar(
                    screen, x_anchor, y, 320, 12,
                    ship.shield / max(1, cls.shield_max),
                    (90, 180, 240),
                    f"SHIELD {int(ship.shield):3d}/{cls.shield_max}",
                )
                y += 22
            else:
                screen.blit(
                    self.font.render("(no shields)", True, (130, 140, 170)),
                    (x_anchor, y),
                )
                y += 22
            # Energy bar
            self._bar(
                screen, x_anchor, y, 320, 8,
                ship.energy / max(1, cls.energy_max),
                (140, 220, 160),
                f"NRG    {int(ship.energy):3d}/{int(cls.energy_max)}",
            )

        # Center bottom — time remaining + range-between-ships readout.
        # The range is useful tactical info — it tells the player when
        # they're at primary-weapon range, when they're committed to a
        # close-range exchange, etc.
        import math as _math
        dx = self.precursor.x - self.homesteader.x
        dy = self.precursor.y - self.homesteader.y
        range_units = _math.hypot(dx, dy)
        timer = self.font.render(
            f"FIGHT  ·  t={self.time_in_scene:5.1f}s  ·  cap {self.max_duration:.0f}s"
            f"  ·  range {int(range_units):4d}u",
            True, (180, 190, 210),
        )
        tw, _ = timer.get_size()
        screen.blit(timer, ((self.screen_w - tw) // 2, self.screen_h - 36))

    def _bar(
        self,
        screen: pygame.Surface,
        x: int,
        y: int,
        w: int,
        h: int,
        frac: float,
        color: tuple[int, int, int],
        label: str,
    ) -> None:
        assert self.font is not None
        frac = max(0.0, min(1.0, frac))
        pygame.draw.rect(screen, (30, 30, 50), (x, y, w, h))
        pygame.draw.rect(screen, color, (x, y, int(w * frac), h))
        pygame.draw.rect(screen, (90, 100, 130), (x, y, w, h), 1)
        screen.blit(self.font.render(label, True, (200, 210, 230)), (x + w + 8, y - 3))
