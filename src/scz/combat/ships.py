"""Ship class definitions — stat blocks for every combat ship.

Numbers mirror the canonical roster in
`references/lore/ship-roster.md`. First-pass values; expect ±30% tuning
after early playtest. The schema is `references/lore/ship-design-schema.md`.

For Phase 2 we hardcode the stat blocks here. When the modular ship
system lands (Phase 4+), the Furling Scout's stats become a base + module
deltas. Everything else stays static.
"""

from __future__ import annotations

from dataclasses import dataclass


# Side designations — the super-melee asymmetry. "Special" is for
# climax fights that are nominally Precursor but feel like a third side
# (Cleanser).
SIDE_PRECURSOR = "precursor"
SIDE_HOMESTEADER = "homesteader"
SIDE_SPECIAL = "special"


@dataclass(frozen=True)
class ShipClass:
    """Static description of a ship type. Instances of this class are
    the slot machine; runtime state lives in ShipState (in scene.py).
    """
    id: str
    name: str
    side: str
    points: int

    # Defense
    hull_max: int
    shield_max: int           # 0 = no shield tech
    shield_regen: float       # HP/sec when regenerating
    shield_regen_delay: float # seconds after hit before regen resumes

    # Movement
    top_speed: float          # units/sec
    acceleration: float       # units/sec²
    turn_rate: float          # rad/sec
    mass: float               # ramming weight (informational; not used yet)

    # Energy
    energy_max: float
    energy_regen: float       # units/sec

    # Primary weapon
    primary_damage: float
    primary_energy: float     # cost per shot
    primary_rate: float       # shots/sec
    primary_range: float      # max range (units)
    primary_speed: float      # projectile speed (units/sec); large = effectively hitscan
    primary_color: tuple[int, int, int]

    # Visual — a tiny hand-drawn silhouette is enough for the slice
    hull_color: tuple[int, int, int]
    accent_color: tuple[int, int, int]
    silhouette: str           # one of: "scout", "cruiser", "skiff", "heavy", "warship", "blade", "sentinel"

    # AI hint — preferred engagement style.
    # "brawler" closes the distance and fights. "kiter" prefers max-range.
    # "circler" stays at mid-range moving laterally.
    # "orbital_strafer" — Arilou-style perpendicular orbit.
    # "snipe_then_relocate" — fire at max range, reposition after each shot.
    # "left_only" — Sentry Drone tutorial exploit; can only turn left.
    ai_style: str = "brawler"

    # Primary weapon firing pattern. The engine implements:
    #   "single"        — one projectile from the nose along heading (default).
    #   "twin"          — two parallel projectiles offset laterally; Cleanser
    #                     Cruiser. Reads as a heavy twin-cannon volley.
    #   "triple"        — three parallel projectiles, wider spacing than
    #                     twin; Proto-Ur-Quan Warship. Slow broadside.
    #   "multi_spread"  — three projectiles in a narrow forward fan (±10°);
    #                     Mmrnmhrm Sentinel. Mid-range volley.
    #   "scatter"       — five projectiles in a wide forward cone (~±20°);
    #                     Proto-Qor-Ah. Short-range scatter blast; individual
    #                     hits are weak, full volley at point-blank is brutal.
    #   "burst"         — three projectiles in a tight forward fan (±3°)
    #                     suggesting a "measured 3-shot burst"; Persuader
    #                     Vessel. Reads as careful, deliberate fire.
    #   "lance"         — single projectile at 1.5× speed + 1.3× range over
    #                     the ship's stated stats; Androsynth Cruiser.
    #                     Reads as a precision sniper shot.
    #   "homing"        — single projectile that slowly turns toward the
    #                     enemy each frame; Melnorme Trader (SC2-canonical
    #                     heat-seeking plasmoids). Best against fleeing
    #                     targets, neutered by leading-turn ships.
    #   "charged"       — slow rate but oversized projectile (double radius,
    #                     double damage per shot); Defender Vessel.
    #                     The engine treats this as a single with stat
    #                     overrides; AI behavior identical.
    primary_pattern: str = "single"

    # Special ability — the active power, distinct from the primary
    # weapon. Triggered by a button/AI decision separate from firing.
    #   "none"          — no special (default; most ships don't have one
    #                     yet — they'll be added in the specials pass).
    #   "inertia_halt"  — Furling Scout. While held, ship velocity is
    #                     zeroed; on release, the pre-halt velocity is
    #                     restored. Used to dodge slow projectiles that
    #                     would otherwise intercept on a predictable path.
    #                     Each activation costs `special_energy` and is
    #                     gated by `special_cooldown` after release.
    # Future specials (Phase 1.5 — Aaron's "specials/abilities pass"):
    #   "teleport"      — Arilou Skiff (SC2-canon short-range hop)
    #   "butt_missiles" — Proto-Qor-Ah (defensive AOE on rear hemisphere)
    #   ...
    special_ability: str = "none"
    # Specials run on COOLDOWN ONLY — they do not share the primary
    # weapon's energy pool (Aaron 2026-05-17: "I never liked that it
    # shares the same energy pool"). `special_energy` is retained as
    # a dataclass field for backward compatibility but is no longer
    # consumed; instead each special's per-frame state is gated by
    # `special_cooldown_left` and (for held specials) `special_duration`.
    special_energy: float = 0.0       # DEPRECATED — ignored by engine
    special_cooldown: float = 0.0     # seconds after release before re-usable
    # Max duration a HELD special can stay active before forced revert.
    # 0.0 = no time limit (cooldown alone gates re-activation; release
    # is voluntary or condition-based). Held specials with a hold-cap:
    #   - inertia_halt (Furling Scout): can't dodge forever
    #   - absorb_shield (Utwig): can't tank forever
    #   - regen_hull (Mycon): can't heal back to full repeatedly
    #   - blazer_form (Androsynth): can't ram-form indefinitely
    #   - fried_discs (Proto-Qor-Ah): can't keep the disc ring up
    # Instant-trigger specials (teleport, icepeedo, dash_slice, etc.)
    # leave this 0.
    special_duration: float = 0.0

    # xform_alt: optional alternate ShipClass for ships whose special
    # is a form-transformation (Mmrnmhrm X-Form). When non-None and
    # the ship is xform-active, ShipState.cls swaps to this. Hull /
    # shield / energy values on ShipState are preserved across the
    # swap; only weapon and movement stats change. The alt-form's
    # xform_alt should point back at the base (so toggling works
    # both directions). Frozen-dataclass constraint means we wire
    # this with `object.__setattr__` after both forms are defined.
    xform_alt: "ShipClass | None" = None

    # Per-sprite rotation offset (degrees, CCW positive). 0.0 means the
    # sprite is authored NOSE-UP (the engine default). Non-zero values
    # correct sprites whose authored nose is pointing in another
    # direction:
    #   +90  — sprite nose points RIGHT in source PNG
    #   -90  — sprite nose points LEFT in source PNG
    #   180  — sprite nose points DOWN
    #   +45  — sprite nose at upper-right diagonal
    # The engine applies this offset on top of the heading rotation
    # in `_draw_ship` so the green target-lock pip lands on the
    # actual visible nose, not on a side of a sideways sprite.
    # Aaron 2026-05-18: many of the Firefly sprites came back nose-
    # right / nose-down / etc.; this field corrects without re-author.
    sprite_rotation_offset_deg: float = 0.0


# ---------------------------------------------------------------------------
# Precursor side (Go) — 4 ships available in the slice + Cleanser variant
# ---------------------------------------------------------------------------

FURLING_SCOUT = ShipClass(
    id="furling_scout",
    name="Furling Scout",
    side=SIDE_PRECURSOR,
    points=130,
    hull_max=100, shield_max=80, shield_regen=12.0, shield_regen_delay=2.0,
    top_speed=220.0, acceleration=280.0, turn_rate=3.0, mass=100,
    energy_max=60, energy_regen=6.0,
    # Role rebalance iter 5 (2026-05-17): Scout is MODULAR (~50%).
    # Iter-4 7dmg landed at 57% — drop to 6.5 to settle near 50%.
    primary_damage=6.5, primary_energy=4, primary_rate=4.0,
    primary_range=400, primary_speed=2400,  # near-hitscan beam
    primary_color=(255, 220, 140),
    hull_color=(200, 200, 220), accent_color=(160, 220, 255),
    silhouette="scout", ai_style="circler",
    # Inertia halt — Furling Scout signature defensive special. While
    # active, ship velocity is zeroed; on release the pre-halt velocity
    # is restored. Used to dodge slow incoming projectiles whose lead
    # solution depends on the ship's current motion vector.
    #
    # Energy-free per Aaron's spec (2026-05-17) — the halt is a
    # signature survival tool, not an energy-throttled ability. The
    # 1.2s cooldown after release prevents constant on/off flickering.
    # 2.0s max hold so the player can't camp the halt forever.
    special_ability="inertia_halt",
    special_energy=0.0,
    special_cooldown=1.2,
    special_duration=2.0,
    # Sprite authored nose-RIGHT — correct by rotating +90° CCW so the
    # nose-pip lands on the actual visible front. Aaron 2026-05-18.
    sprite_rotation_offset_deg=90.0,
)

PERSUADER_VESSEL = ShipClass(
    id="persuader_vessel",
    name="Persuader Vessel",
    side=SIDE_PRECURSOR,
    points=110,
    # The Persuader's whole win-condition is the lasso — it has no
    # primary projectile damage. To keep it from being a brick-tank
    # that just lassos forever, defenses are deliberately thin: 65
    # hull, 35 shield. If a fight gets dragged out (cooldown 3.5s
    # between latches), the Persuader can be punished hard.
    hull_max=65, shield_max=35, shield_regen=10.0, shield_regen_delay=2.0,
    # Higher acceleration + turn-rate than the "burst diplomat" earlier
    # build — the Persuader spends a lot of time closing to lasso range
    # and needs to dodge incoming fire while doing so.
    top_speed=210.0, acceleration=260.0, turn_rate=3.0, mass=90,
    energy_max=90, energy_regen=8.0,
    # Aaron's 2026-05-17 spec: signature TRACTOR LASSO primary. No
    # per-frame projectile damage — the lasso latches the enemy, spins
    # them around at orbit, and flings them tangentially on release.
    # Kills come from the captive slamming into planet/asteroid after
    # being flung. The primary_damage / primary_energy / primary_rate
    # fields are unused by tractor_lasso (LASSO_* constants in
    # scene.py own the tuning); primary_range is informational
    # (matches LASSO_MAX_RANGE for AI engagement-distance heuristics).
    primary_damage=0, primary_energy=0, primary_rate=1.0,
    primary_range=280, primary_speed=0,
    primary_color=(220, 180, 100),
    hull_color=(220, 180, 100), accent_color=(255, 230, 180),
    silhouette="scout", ai_style="brawler",   # close-to-lasso-range
    primary_pattern="tractor_lasso",
    # Aaron's 2026-05-17 spec: short directional phase-skip teleport.
    # Costs energy; lets the Persuader skip OVER planets, asteroids,
    # other ships, and incoming projectiles when energy allows.
    # Iconic Persuader move — "I'm here. Now I'm there. Are we going
    # to be reasonable?"
    special_ability="phase_skip",
    special_energy=0.0,
    special_cooldown=3.5,
)

ARILOU_SKIFF = ShipClass(
    id="arilou_skiff",
    name="Arilou Skiff",
    side=SIDE_PRECURSOR,
    points=120,
    # Outlier fix 2026-05-19 (iter 2): hull 60→75 only got Skiff to
    # 33.8% (still below band). Bumping further to 90 — fighter-tier
    # but tough enough to trade with heavies that 1-shotted it before.
    hull_max=90, shield_max=0, shield_regen=0.0, shield_regen_delay=0.0,
    top_speed=320.0, acceleration=420.0, turn_rate=5.5, mass=55,
    energy_max=100, energy_regen=10.0,
    # Archetype-fit pass 2026-05-17: FIGHTER (~35%). At 7dmg the
    # Skiff over-shot to 44.7% — back to 6 (auto-aim laser
    # accumulates fast at 6 fps, so per-shot is the sensitive lever).
    primary_damage=6, primary_energy=2, primary_rate=6.0,
    primary_range=300, primary_speed=900,
    primary_color=(140, 240, 210),
    hull_color=(140, 240, 210), accent_color=(200, 255, 230),
    silhouette="skiff",
    ai_style="kiter",
    # SC2 canon (arilou.c): IMMEDIATE auto-aim tracking laser.
    # Our `tracking` pattern is a sharp-homing near-hitscan that
    # follows the enemy each frame.
    primary_pattern="tracking",
    # SC2 canon (arilou.c): teleport to a random arena location.
    # Now cooldown-only (Aaron 2026-05-17 special-energy decoupling).
    # 1.5s cooldown — still chainable in a panic but not free-spam.
    special_ability="teleport",
    special_energy=0.0,
    special_cooldown=1.5,
    # Sprite authored nose-RIGHT — correct +90° CCW. Aaron 2026-05-18.
    sprite_rotation_offset_deg=90.0,
)

ANDROSYNTH_CRUISER = ShipClass(
    id="androsynth_cruiser",
    name="Androsynth Refugee Cruiser",
    side=SIDE_PRECURSOR,
    points=135,
    # Role rebalance 2026-05-17: STRIKE craft (~45% win, deals 75%
    # damage). Bumped hull 130→160 + bubble damage 4→6 so the
    # Androsynth lands meaningful damage before going down.
    hull_max=160, shield_max=0, shield_regen=0.0, shield_regen_delay=0.0,
    top_speed=190.0, acceleration=220.0, turn_rate=2.2, mass=130,
    energy_max=70, energy_regen=6.0,
    # Archetype-fit pass 2026-05-17: STRIKE (~45%). Energy-decoupling
    # brought Androsynth to 56% — bubble damage 7.5 → 6.5 to drop
    # the strike DPS back to target band.
    primary_damage=6.5, primary_energy=3, primary_rate=2.0,
    primary_range=350, primary_speed=600,
    primary_color=(220, 130, 220),
    hull_color=(180, 100, 200), accent_color=(240, 200, 240),
    silhouette="cruiser",
    ai_style="kiter",
    primary_pattern="bubble",
    # SC2 canon (androsyn.c): Blazer/Comet transform. While active,
    # ship rams for damage; no primary fire. Cooldown-only now;
    # 5.0s max hold so the ram form is a committed window, not a
    # permanent state. 4.0s cooldown after release.
    special_ability="blazer_form",
    special_energy=0.0,
    special_cooldown=4.0,
    special_duration=5.0,
    # Sprite authored nose-DOWN — correct 180°. Aaron 2026-05-18.
    sprite_rotation_offset_deg=180.0,
)

CLEANSER_CRUISER = ShipClass(
    id="cleanser_cruiser",
    name="Cleanser Furling Cruiser",
    side=SIDE_SPECIAL,   # nominally Precursor; faction-extreme
    points=175,
    # Slight shield nerf 2026-05-17 (sim_combat showed 98% win rate vs
    # every other ship including the base Furling Scout). The Cleanser
    # is *meant* to be a hard climax fight — but the player using their
    # base scout on auto-fight should have a chance, not a 0% win rate.
    # Shield down 100 → 70 puts it around 75-85% — still scary, not auto.
    # Drev-Tok climax pass 2026-05-19 (iter 2): Cleanser was racking
    # up 3.10 Steward kills/run in 5v6 super-melee — its 1v1 is
    # in-band but its slot-4 fresh-hull carry potential was too high.
    # Shield 70→50 (iter-1) only got it to 2.30. Pushing further:
    # hull 150→130, shield_regen 10→8 — should land near 1.5 kills/run.
    hull_max=130, shield_max=50, shield_regen=8.0, shield_regen_delay=3.0,
    top_speed=175.0, acceleration=180.0, turn_rate=2.0, mass=150,
    energy_max=80, energy_regen=6.0,
    # Aaron's 2026-05-17 spec: water spray primary + freeze special.
    # The Cleanser sprays literal water at the target (5 droplets per
    # fire in a forward cone); droplets soak the target (wetness
    # accumulates) and slowly damage. After 1s flight, the water
    # space-freezes mid-air into low-damage ice droplets. Water can
    # also push asteroids without damaging them.
    # Role rebalance: Cleanser is FLAGSHIP (~65% target). Slight buff
    # to fire rate 3.0→3.5; per-droplet damage 1→1.5.
    primary_damage=1.5, primary_energy=2, primary_rate=3.5,
    primary_range=320, primary_speed=850,
    primary_color=(90, 160, 230),
    hull_color=(230, 230, 240), accent_color=(180, 160, 240),
    silhouette="heavy", ai_style="brawler",
    primary_pattern="water_spray",
    # Aaron's 2026-05-17 spec: "icepeedo" — a chunky ice torpedo
    # projectile. On hit:
    #   dry target → small damage + significant wetness
    #   wet target (>= 30) → FREEZE (frozen_remaining = 3.0)
    #   already-frozen target → CRACK (4× damage)
    # So two icepeedos in a row also finish a frozen ship without
    # needing the back-up-and-snipe water dance.
    special_ability="icepeedo",
    special_energy=0.0,
    special_cooldown=3.5,
)

# Melnorme Trade Pod — generated via Gemini Flash Lite, see
# tools/gemini_drafts/ship_melnorme_trader.json. Merchant escort:
# unshielded hull-tank, slow-but-stout, kiter AI. SC2-canon "Confusion
# Pulse" special is the merchant-favored option; primary is a stock
# plasma cannon (Aaron may iterate later to the canonical heat-seeking
# plasmoids).
MELNORME_TRADER = ShipClass(
    id="melnorme_trader",
    name="Melnorme Trade Pod",
    side=SIDE_PRECURSOR,
    points=155,
    hull_max=150, shield_max=0, shield_regen=0.0, shield_regen_delay=0.0,
    top_speed=180.0, acceleration=250.0, turn_rate=2.5, mass=120,
    energy_max=80, energy_regen=6.0,
    # SC2 canon (melnorme.c): 3-tier charge-up plasma. Energy gates
    # the tier — full charge fires a heavy bolt (3× damage), mid
    # charge a medium bolt (2× damage), low fires a standard. Per-shot
    # energy cost is fixed; the tier bonus is "free" off accumulated
    # charge.
    # Archetype-fit pass 2026-05-17: UTILITY (~50%). Even at 3dmg
    # Melnorme sat at 62% — fire rate 2.0 → 1.4 so charged shots
    # take longer to accumulate AND between-tier-burst gaps are
    # bigger. Tiers scale 3/6/9; rate-down preserves the SC2 "charge-
    # then-tier-burst" rhythm without making it spammy.
    primary_damage=3, primary_energy=4, primary_rate=1.4,
    primary_range=500, primary_speed=600,
    primary_color=(255, 165, 0),
    hull_color=(255, 140, 0), accent_color=(255, 215, 0),
    silhouette="cruiser", ai_style="kiter",
    primary_pattern="tier_plasma",
    # Aaron's 2026-05-17 spec: replace SC2's broken confusion-pulse
    # with `adware_pulse` — blasts the target's HUD with Grand
    # Shopping Super Mart pop-ups; their autopilot helpfully steers
    # them toward the nearest "store" (in-arena = nearest asteroid,
    # which is also a collision hazard). For ~2.5s the target can't
    # fire and is driving themselves into rock. Iconic Melnorme.
    special_ability="adware_pulse",
    special_energy=0.0,
    special_cooldown=13.0,
)

# ---------------------------------------------------------------------------
# Homesteader side (Stay) — 5 ships in the slice
# ---------------------------------------------------------------------------

DEFENDER_VESSEL = ShipClass(
    id="defender_vessel",
    name="Defender Vessel",
    side=SIDE_HOMESTEADER,
    points=170,
    # Drev-Tok climax buff 2026-05-19 (iter 4): roster sweep still
    # showed 66.7% after iter-3 (10dmg/1.3rate). Trimming fire rate
    # 1.3→1.15 — DPS drops to 11.5, should land near 60%.
    hull_max=210, shield_max=60, shield_regen=8.0, shield_regen_delay=3.0,
    top_speed=150.0, acceleration=130.0, turn_rate=1.6, mass=180,
    energy_max=90, energy_regen=5.0,
    # Aaron's 2026-05-17 spec: primary is an ENGINE-SEEKING missile —
    # single long-range tracking shot that on hit applies a permanent
    # slowdown to the target (engine_damage_on_hit = 30; effective
    # top_speed drops 30 per hit, clamped to a 60 floor).
    primary_damage=10, primary_energy=5, primary_rate=1.15,
    primary_range=620, primary_speed=750,
    primary_color=(255, 200, 100),
    hull_color=(200, 180, 120), accent_color=(255, 230, 160),
    silhouette="heavy", ai_style="kiter",
    primary_pattern="engine_seeker",
    # Aaron's 2026-05-17 spec: chaff field sprayed in a forward cone.
    # 12 stationary puffs cover a 50-200u-deep cone in front of the
    # Defender; enemy projectiles passing through have their velocity
    # multiplied by 0.92 per frame until they barely move. Defensive +
    # zone-denial. Energy 14, cooldown 4s.
    special_ability="chaff_spray",
    special_energy=0.0,
    special_cooldown=4.0,
)

# Mmrnmhrm has two forms — laser fighter (close-range nimble) and
# missile jet (long-range fast slow-turning). The `xform` special
# toggles between them. Defined in the order MISSILE first, then
# LASER (with xform_alt = MISSILE), then we wire MISSILE.xform_alt
# back to LASER post-construction (Frozen dataclass — uses
# object.__setattr__).
MMRNMHRM_SENTINEL_MISSILE = ShipClass(
    id="mmrnmhrm_sentinel",
    name="Mmrnmhrm Sentinel (Missile Form)",
    side=SIDE_HOMESTEADER,
    points=155,
    # Same defensive stats as laser form — hull/shield/energy persist
    # across the swap (handled via ShipState retaining its hp values).
    hull_max=150, shield_max=0, shield_regen=0.0, shield_regen_delay=0.0,
    # Missile form: faster + bigger, slower-turning ("fighter jet")
    top_speed=260.0, acceleration=180.0, turn_rate=1.4, mass=140,
    energy_max=70, energy_regen=7.0,
    # Long-range homing missiles — single missile per fire, slow-ish
    # speed, tracks target gently. Range-diversification 2026-05-19:
    # promoted to LONG_RANGE_SNIPER tier — range 620→1050. Ancient
    # Mmrnmhrm cohort's tracking missiles are an unmatched ranged
    # threat; xform-into-this-form is the explicit "open the gap"
    # decision (laser form is the close-quarter answer). New DPS at
    # full range = 8.4 with homing pursuit.
    primary_damage=7, primary_energy=5, primary_rate=1.2,
    primary_range=1050, primary_speed=900,
    primary_color=(220, 220, 240),
    hull_color=(220, 220, 240), accent_color=(180, 200, 255),
    silhouette="sentinel", ai_style="long_range_sniper",
    primary_pattern="homing",
    special_ability="xform",   # press special again to revert
    special_energy=0.0,         # cooldown-only now (decoupled from energy)
    special_cooldown=1.0,
)

MMRNMHRM_SENTINEL = ShipClass(
    id="mmrnmhrm_sentinel",
    name="Mmrnmhrm Sentinel",
    side=SIDE_HOMESTEADER,
    points=155,
    hull_max=150, shield_max=0, shield_regen=0.0, shield_regen_delay=0.0,
    # Laser form: short-range, nimble (high turn, mid-speed)
    top_speed=180.0, acceleration=200.0, turn_rate=2.8, mass=140,
    energy_max=70, energy_regen=7.0,
    # Triple-laser volley — three bolts in a narrow forward fan.
    # Archetype-fit pass 2026-05-17: STRIKE (~45%). At 2.0dmg the
    # Sentinel landed at 52% — pulled to 1.75 (volley 5.25) to fit
    # mid-range strike identity.
    primary_damage=1.75, primary_energy=3, primary_rate=5.0,
    primary_range=380, primary_speed=900,
    primary_color=(220, 220, 240),
    hull_color=(220, 220, 240), accent_color=(255, 255, 255),
    silhouette="sentinel", ai_style="circler",
    primary_pattern="multi_spread",
    # Aaron's 2026-05-17 spec: xform special toggles between LASER
    # form (this baseline — short-range nimble) and MISSILE form
    # (long-range homing jet). Hull/shield/energy persist across the
    # swap. AI decides based on engagement distance.
    special_ability="xform",
    special_energy=0.0,
    special_cooldown=1.0,
    xform_alt=MMRNMHRM_SENTINEL_MISSILE,
)
# Wire the missile form's xform_alt back to the laser form. ShipClass
# is frozen but the field default is None; we set the reverse-link
# now via object.__setattr__ to bypass the frozen restriction. This
# is a deliberate one-time bootstrap.
import dataclasses as _dc  # noqa: E402
object.__setattr__(
    MMRNMHRM_SENTINEL_MISSILE, "xform_alt", MMRNMHRM_SENTINEL,
)

PROTO_UR_QUAN = ShipClass(
    id="proto_ur_quan",
    name="Proto-Ur-Quan Warship",
    side=SIDE_HOMESTEADER,
    points=145,
    # Role rebalance 2026-05-17: Proto-Ur-Quan is a FLAGSHIP (~65%
    # target). Hull bumped 170→220 (soaks one fight), primary damage
    # 6→9 (plasma bolt is heavier), homing_cluster damage 8→12.
    # Outlier fix 2026-05-19 (iter 2): roster sweep showed 74.2% even
    # after speed/hull nerf (iter-1 landed at 71.7%). The plasma bolt
    # at 9 damage was still too potent — pulled to 7. Hull stays 180.
    hull_max=180, shield_max=0, shield_regen=0.0, shield_regen_delay=0.0,
    top_speed=145.0, acceleration=140.0, turn_rate=1.9, mass=170,
    energy_max=50, energy_regen=4.0,
    primary_damage=7, primary_energy=5, primary_rate=1.3,
    primary_range=260, primary_speed=600,
    primary_color=(110, 140, 220),
    hull_color=(70, 90, 160), accent_color=(140, 170, 230),
    silhouette="warship", ai_style="brawler",
    primary_pattern="charged",
    # Homing cluster — 5 missiles fired in forward arc; spread for
    # ~0.4s flying straight, then start tracking the enemy.
    # Outlier fix 2026-05-19 (iter 3): cooldown 5.5→9.0 to throttle
    # the cluster carry — 5 × 12 dmg per cooldown = 10.9 DPS at 5.5s,
    # 6.7 DPS at 9.0s. Drops Ur-Quan from 70% to flagship band.
    special_ability="homing_cluster",
    special_energy=0.0,
    special_cooldown=9.0,
    # Sprite authored nose-LEFT (jaws/claws visible on the LEFT side
    # of the source PNG, body trailing right) — correct -90° CCW so
    # the engine's heading rotation lands the nose-pip on the jaws.
    # Aaron 2026-05-18.
    sprite_rotation_offset_deg=-90.0,
)

SENTRY_DRONE_47T = ShipClass(
    id="sentry_drone_47t",
    name="Sentry Drone 47-Theta (unionized)",
    side=SIDE_SPECIAL,
    points=20,
    hull_max=20, shield_max=0, shield_regen=0.0, shield_regen_delay=0.0,
    # Deliberately slow + can't outturn the player. The canonical
    # tutorial enemy you can pick apart by orbiting right.
    top_speed=60.0, acceleration=80.0, turn_rate=1.2, mass=40,
    energy_max=20, energy_regen=2.0,
    primary_damage=2, primary_energy=1, primary_rate=0.5,
    primary_range=200, primary_speed=400,
    primary_color=(255, 200, 80),
    hull_color=(180, 180, 200), accent_color=(120, 140, 160),
    silhouette="skiff",
    # Canonical left-only-turn behavior — see combat/ai.py for the
    # special-case handling (a unionized labor drone willing to die on
    # its principles, see tutorial-arc-implementation Beat 6)
    ai_style="left_only",
)


PROTO_QOR_AH = ShipClass(
    id="proto_qor_ah",
    name="Proto-Qor-Ah Marauder",
    side=SIDE_HOMESTEADER,
    points=95,
    # Role rebalance iter 3 (2026-05-17): STRATEGIC craft (~40% target,
    # avoidance + long range, patience to win). Hull 90→110 for
    # extra durability; lawnmower damage 14 still left at 32% — bumped
    # to 17 so a clean hit really pays.
    hull_max=110, shield_max=0, shield_regen=0.0, shield_regen_delay=0.0,
    top_speed=240.0, acceleration=300.0, turn_rate=3.5, mass=80,
    energy_max=60, energy_regen=5.0,
    primary_damage=17, primary_energy=4, primary_rate=1.0,
    primary_range=440, primary_speed=720,
    primary_color=(240, 230, 200),
    hull_color=(240, 230, 200), accent_color=(40, 30, 20),
    silhouette="blade", ai_style="circler",
    primary_pattern="lawnmower_blade",
    # Special: ring of 4 blade-shaped orbitals around the ship
    # (reverted from the 2-blade static design per Aaron's revised
    # spec — "ring of these blades around the ship like the fireball
    # ring used to do"). Costs energy continuously; rotates around
    # the host; damages anything in contact.
    special_ability="fried_discs",
    special_energy=0.0,
    special_cooldown=3.0,
    special_duration=4.0,
    # Sprite faces upper-right (~45° clockwise from nose-up); rotate
    # +45° CCW so heading-0 nose-pip lands on the blade tip.
    sprite_rotation_offset_deg=45.0,
)


# Master registry — used by the super-melee picker
# ---------------------------------------------------------------------------
# Additional species roster (2026-05-17) — 6 ships closing the gap
# between our species canon and the combat roster. SC2-mapped where
# the source ship exists; original where the species is ours.
# ---------------------------------------------------------------------------

# Compeller Vessel — Furling Compeller-faction warship. The Compellers
# are one of the four canonical Furling political factions
# (Persuaders, Compellers, Cleansers, Defenders) per canon-lore
# (project_furlings_others.md). Compellers practice non-lethal force —
# sedation, deception, tractor extraction — for species that refuse
# voluntary evacuation. Mechanically: heavy short-range hitscan
# coupled with thick shields so they can close in and "compel."
#
# Diegetically replaces the Slylandro Probe slot in the roster (the
# Slylandro Probe is post-Melnorme-return canon, doesn't exist in our
# era — only the sentient Slylandro evacuees and their Cloaking
# Satellites exist now).
COMPELLER_VESSEL = ShipClass(
    id="compeller_vessel",
    name="Compeller Vessel",
    side=SIDE_PRECURSOR,
    points=140,
    # Built to take a hit — Compellers will close to point-blank to
    # apply sedation, so they need to survive being shot at on the way
    # in. Heavy shields, moderate hull.
    hull_max=110, shield_max=120, shield_regen=12.0, shield_regen_delay=2.0,
    top_speed=190.0, acceleration=210.0, turn_rate=2.4, mass=110,
    energy_max=70, energy_regen=7.0,
    # Aaron's 2026-05-17 spec: primary is a GRAVITY WELL placer.
    # Archetype-fit pass 2026-05-17: UTILITY (~50%). Energy-decoupling
    # bumped Compeller to 64% — gravity well per-frame damage stacks
    # too hard now that compel is cooldown-only. Damage 8 → 5 and
    # compel cooldown bumped (see special_cooldown below).
    primary_damage=5, primary_energy=18, primary_rate=0.4,
    primary_range=400, primary_speed=0,
    primary_color=(180, 220, 180),
    hull_color=(160, 200, 170), accent_color=(220, 240, 200),
    silhouette="scout", ai_style="brawler",
    primary_pattern="gravity_well",
    # Aaron's 2026-05-17 spec: Compeller "compels" the enemy — forces
    # an inertia-halt state on them for ~2 seconds. Same mechanic as
    # the Furling Scout's voluntary halt, but imposed externally.
    # Costs energy + has cooldown.
    special_ability="compel",
    special_energy=0.0,
    special_cooldown=8.5,
)

# Mycon Podship — SC2 canon (mycon.c): single big plasmoid + the
# iconic regenerate special (full hull heal-back). Slow, tanky.
# Diegetic: the awakening Mycon biots have learned to weaponize
# plasma streaks and to self-repair via their internal symbiotes.
MYCON_PODSHIP = ShipClass(
    id="mycon_podship",
    name="Mycon Podship",
    side=SIDE_PRECURSOR,
    points=140,
    hull_max=200, shield_max=0, shield_regen=0.0, shield_regen_delay=0.0,
    top_speed=140.0, acceleration=140.0, turn_rate=1.8, mass=160,
    energy_max=80, energy_regen=5.0,
    # Plasmoid — big slow heavy shot. Charged pattern doubles radius
    # + damage at spawn.
    primary_damage=8, primary_energy=6, primary_rate=1.0,
    primary_range=300, primary_speed=550,
    primary_color=(200, 90, 130),
    hull_color=(140, 60, 100), accent_color=(220, 120, 160),
    silhouette="warship", ai_style="kiter",
    primary_pattern="charged",
    # Regenerate hull while held; drains energy.
    special_ability="regen_hull",
    special_energy=0.0,
    special_cooldown=4.0,
    special_duration=3.5,
)

# Utwig Jugger — SC2 canon (utwig.c) pre-doctrine fleet. Tank with
# weak short-range gun + iconic absorption shield. The Utwig in our
# slice devolved AFTER this fleet existed, so a Jugger encounter is
# canonical for "pre-devolution Utwig still flying." For now we model
# the absorption shield as just very-high shield regen (the proper
# damage-to-energy conversion is in the "absorb_shield" backlog).
UTWIG_JUGGER = ShipClass(
    id="utwig_jugger",
    name="Utwig Jugger",
    side=SIDE_HOMESTEADER,
    points=165,
    # Archetype-fit pass 2026-05-17: GUNSHIP (~57.5%). Shield/fire
    # exclusivity reduced firing windows AND damage uptime; hull
    # 160→175 + shield_regen 15→18 to make the Jugger the durable
    # gunship the role demands. Aaron's "Utwig can't shield and
    # fire at the same time, one of their limitations" sticks; the
    # buff just compensates the loss of overlap.
    hull_max=175,
    shield_max=80, shield_regen=18.0, shield_regen_delay=2.0,
    top_speed=170.0, acceleration=180.0, turn_rate=2.4, mass=140,
    energy_max=50, energy_regen=4.0,
    # Aaron's 2026-05-17 spec: gatling laser — 3 big alternating
    # bolts from rotating barrels (left/center/right). Reads as a
    # rapid-fire energy weapon with cadence. Per-bolt damage moderate;
    # sustained fire is the strength. Shield/fire exclusivity (Aaron's
    # 2026-05-17 "Utwig limitation") cut firing windows — damage bumped
    # back from 2.5 → 3.2 to compensate the smaller damage window.
    primary_damage=3.2, primary_energy=2, primary_rate=3.0,
    primary_range=320, primary_speed=2000,
    primary_color=(220, 240, 200),
    hull_color=(180, 200, 160), accent_color=(220, 240, 200),
    silhouette="heavy", ai_style="brawler",
    primary_pattern="gatling",
    # Aaron's 2026-05-17 spec: full SC2-canonical absorption shield.
    # Incoming damage redirects to energy (80% conversion, 20% still
    # pierces — sustained focused fire can still wear it down).
    # Costs energy per second to maintain.
    special_ability="absorb_shield",
    special_energy=0.0,
    special_cooldown=1.5,
    special_duration=6.0,
)

# Lemmkin Skitter — original species, canonical via lore (HANDOFF
# image entry 2026-05-17). Fast, fragile, scatter-probe weapon
# fired from leading-edge ports. Squirrelly + brave-stupid pilots.
LEMMKIN_SKITTER = ShipClass(
    id="lemmkin_skitter",
    name="Lemmkin Skitter",
    side=SIDE_HOMESTEADER,
    points=80,
    # Role rebalance iter 3: FIGHTER (~35%). Hull dropped further to
    # 50 — fighter is supposed to be very fragile, AI-flown they die
    # but skilled human pilots use them with their speed advantage.
    hull_max=50, shield_max=0, shield_regen=0.0, shield_regen_delay=0.0,
    top_speed=300.0, acceleration=400.0, turn_rate=5.0, mass=50,
    energy_max=50, energy_regen=8.0,
    # Role rebalance iter 5 (2026-05-17): FIGHTER (~35%). Iter-4
    # 3.5dmg over-shot (43.7%) — Lemmkin latch DoT + scatter burst
    # was finishing fights in 2-3s. Back to 3.0 damage.
    primary_damage=3.0, primary_energy=2, primary_rate=3.0,
    primary_range=160, primary_speed=900,
    primary_color=(255, 200, 100),
    hull_color=(220, 140, 80), accent_color=(255, 240, 180),
    silhouette="skiff", ai_style="kiter",
    primary_pattern="scatter",
    # Aaron's 2026-05-17 spec: "Aggressive Discovery" — the Skitter
    # latches onto the enemy and does damage-over-time until the
    # enemy's energy maxes out (they have to fully recharge to "force
    # the Skitter off"). Free to activate but cooldown after release.
    special_ability="aggressive_discovery",
    special_energy=0.0,
    special_cooldown=2.0,
)

# Thinn Blade — original species, canonical via lore. 2D ribbon-body
# pilot embedded along the spine of a sail-like elliptical hull.
# Long-range precision strikes (lance). The famous edge-on
# invisibility belongs to the species' DOCTRINE (turn face-on to be
# detectable, edge-on to be invisible); we model only the lance
# weapon for now. Edge-invisibility special is in the backlog.
THINN_BLADE = ShipClass(
    id="thinn_blade",
    name="Thinn Blade",
    side=SIDE_HOMESTEADER,
    points=115,
    # Archetype-fit pass 2026-05-17: FIGHTER (~35%). Hull 80 → 95
    # so the Thinn survives more snipe-exchange duels — the lance
    # buff alone (5.5 → 7.0) didn't reach fighter target.
    hull_max=95, shield_max=0, shield_regen=0.0, shield_regen_delay=0.0,
    top_speed=210.0, acceleration=240.0, turn_rate=3.2, mass=70,
    energy_max=60, energy_regen=6.0,
    # Lance — single high-speed long-range precision shot.
    # Range-diversification 2026-05-19: Lance is canonically a long-
    # range precision weapon; range 520→780 fits the silhouette
    # (literally a needle) and pulls the Thinn out of mid-range fight
    # into a sniper-adjacent role (95% of range with snipe_then_relocate
    # AI = 741u engagement, still less than Burv/Mmrnmhrm 990-1050u).
    primary_damage=7.0, primary_energy=4, primary_rate=1.8,
    primary_range=780, primary_speed=1800,
    primary_color=(180, 240, 220),
    hull_color=(120, 200, 200), accent_color=(220, 240, 230),
    silhouette="blade", ai_style="snipe_then_relocate",
    primary_pattern="lance",
    # Aaron's 2026-05-17 spec: "Dash-Slice" — high-damage melee strike
    # that costs no energy. Inflicts large damage on the enemy + small
    # self-damage. The Thinn's defensive bonus is *not* this special —
    # it's the edge-invisibility (whenever the green target-lock pip
    # is lit, the Thinn is invisible to the enemy and takes no
    # damage). The bonus is handled in `ShipState.apply_damage`.
    special_ability="dash_slice",
    special_energy=0.0,
    special_cooldown=2.5,
)

# Burv Broadcaster — Burvixese support/combat ship. Per the
# Be-Loud doctrine, projects a cognition-amplification pulse that
# (in lore) was supposed to ward off the Others. We model as a
# wide multi-spread broadcast cone — slow, heavy, fires across an
# arc. Burvixese ships exist in small numbers; most of the species
# went down with the Caster.
BURV_BROADCASTER = ShipClass(
    id="burv_broadcaster",
    name="Burv Broadcaster",
    side=SIDE_HOMESTEADER,
    points=125,
    # Archetype: LONG-RANGE SNIPER (Chenjesu-style) per Aaron
    # 2026-05-19 range diversification + wave overhaul. Canonical:
    # Burvixese "Be-Loud" doctrine — a single ship's resonance pulse
    # reaches across an entire cluster.
    #
    # Visual identity (2026-05-19 spec): "Gigantic bullhorn" — the
    # ship is literally a flying loudspeaker, conical mouth aimed
    # forward.  TODO_SPRITE: image chat to author bullhorn-shaped hull
    # (cone mouth + grip handle + thin support struts). Until then,
    # silhouette="bullhorn" is a category hint only; the procedural
    # renderer will fall back to cruiser shape.
    #
    # Weapon identity (2026-05-19 spec): slow propagating resonance
    # wave, curved wavefront, grows in radius while traveling, damage
    # falls off with distance, full-map range, owner is immune.
    # See `is_resonance_wave` in scene.py Projectile.
    hull_max=130, shield_max=30, shield_regen=6.0, shield_regen_delay=3.5,
    top_speed=210.0, acceleration=180.0, turn_rate=1.6, mass=120,
    energy_max=80, energy_regen=6.0,
    # Resonance wave: slow + huge range + damage-falloff. Numbers:
    #   speed 380u/s — eye can track it, ships can dodge
    #   range 1700u — full arena diagonal (1600x1000 → diag ~1887)
    #   damage 17 at point-blank → 7.6 at max range (45% floor)
    #   rate 0.85/s — slower fire, telegraphed
    # iter-3 tune: 14dmg + 25% floor put Burv at 32% (UNDERPOWERED) —
    # long-range hits deal only 3.5, no threat. iter-2 24dmg overshot
    # to 65%. Landing at 17/0.45: point-blank wave 17, max-range 7.6
    # — both meaningful, neither auto-win.
    # NOTE: wave_damage_floor is set in scene.py's resonance_pulse
    # spawn block (currently 0.45 per Aaron 2026-05-19 tune).
    primary_damage=17, primary_energy=5, primary_rate=0.85,
    primary_range=1700, primary_speed=380,
    primary_color=(255, 180, 100),
    hull_color=(180, 130, 80), accent_color=(255, 200, 130),
    silhouette="bullhorn", ai_style="long_range_sniper",
    primary_pattern="resonance_pulse",
    # Special: resonance BURST — pushes every projectile + asteroid
    # within 250u radius away from the Burv and DOUBLES their speed.
    # Defensive panic button + arena-clear; affects the Burv's own
    # outbound shots too (chaotic).
    special_ability="resonance_burst",
    special_energy=0.0,
    special_cooldown=4.0,
)


SHIPS: dict[str, ShipClass] = {
    s.id: s for s in (
        FURLING_SCOUT, PERSUADER_VESSEL, ARILOU_SKIFF, ANDROSYNTH_CRUISER,
        CLEANSER_CRUISER, MELNORME_TRADER,
        DEFENDER_VESSEL, MMRNMHRM_SENTINEL, PROTO_UR_QUAN, PROTO_QOR_AH,
        SENTRY_DRONE_47T,
        # 2026-05-17 — additional species roster. Slylandro Probe was
        # in this slot but the Probes are post-Melnorme-return canon
        # (not in our era); replaced by COMPELLER_VESSEL which fills
        # out the Furling faction tetrad with the missing Compeller
        # archetype.
        COMPELLER_VESSEL, MYCON_PODSHIP, UTWIG_JUGGER,
        LEMMKIN_SKITTER, THINN_BLADE, BURV_BROADCASTER,
    )
}


def precursor_ships() -> list[ShipClass]:
    return [s for s in SHIPS.values() if s.side == SIDE_PRECURSOR]


def homesteader_ships() -> list[ShipClass]:
    return [s for s in SHIPS.values() if s.side == SIDE_HOMESTEADER]


def apply_scout_mods(base: ShipClass, game) -> ShipClass:
    """Return a ShipClass with the player's installed modules applied
    on top of the base (FURLING_SCOUT). Sums stat deltas and applies
    any primary_pattern_override / special_ability_override.

    Called when launching combat for the player's Scout. Mod effects
    that aren't pure-stat (damage_reduction, bounce_chance,
    hull_regen_passive, ablative_pool, engine_damage_on_hit) live as
    delta keys the engine reads via game.effective_stat() during
    apply_damage / _regen / _spawn_projectile hooks.

    Game-less invocation (None) returns the base ShipClass unchanged
    — used by tests / super-melee where no Game state exists.
    """
    if game is None:
        return base
    from scz.content.modules import MODULES
    # Aggregate deltas across all installed modules. We only consume
    # the keys that map onto ShipClass fields here; behavior-flag
    # deltas (damage_reduction, bounce_chance, etc.) stay in the
    # game.effective_stat() pool and are read by combat hooks.
    accum: dict[str, float] = {
        "hull_max": 0.0,
        "shield_max": 0.0,
        "shield_regen": 0.0,
        "shield_regen_delay": 0.0,
        "top_speed": 0.0,
        "acceleration": 0.0,
        "turn_rate": 0.0,
        "energy_max": 0.0,
        "energy_regen": 0.0,
        "primary_damage": 0.0,
        "primary_rate": 0.0,
        "primary_range": 0.0,
        "primary_speed": 0.0,
    }
    pattern_override: str | None = None
    special_override: str | None = None
    # 2026-05-18 stacking refactor: iterate slots in DECLARED order
    # (slot_1..slot_12), accumulating deltas across all installations.
    # For pattern/special overrides, the FIRST slot with one wins —
    # deterministic precedence the player controls via placement.
    #
    # Crew-perk overhaul (same date): if the mod declares a
    # post_quest_flag AND that flag is set in game.flags, also sum
    # post_quest_deltas and consider post_quest_pattern_override /
    # post_quest_special_override.
    from scz.content.modules import SLOTS as _SLOTS
    flags = getattr(game, "flags", {}) or {}
    for slot_key in _SLOTS:
        mod_id = game.ship_modules.get(slot_key)
        if mod_id is None:
            continue
        mod = MODULES.get(mod_id)
        if mod is None:
            continue
        for k in accum:
            if k in mod.deltas:
                accum[k] += mod.deltas[k]
        if (
            pattern_override is None
            and mod.primary_pattern_override is not None
        ):
            pattern_override = mod.primary_pattern_override
        if (
            special_override is None
            and mod.special_ability_override is not None
        ):
            special_override = mod.special_ability_override
        # Post-quest layer.
        if (
            mod.post_quest_flag is not None
            and flags.get(mod.post_quest_flag)
        ):
            for k in accum:
                if k in mod.post_quest_deltas:
                    accum[k] += mod.post_quest_deltas[k]
            if (
                pattern_override is None
                and mod.post_quest_pattern_override is not None
            ):
                pattern_override = mod.post_quest_pattern_override
            if (
                special_override is None
                and mod.post_quest_special_override is not None
            ):
                special_override = mod.post_quest_special_override
    import dataclasses as _dc
    # Apply stat deltas (clamped to sensible floors so a bad mod
    # combo can't produce <=0 stats that crash physics).
    new_hull = max(20, int(base.hull_max + accum["hull_max"]))
    new_shield = max(0, int(base.shield_max + accum["shield_max"]))
    new_shield_regen = max(0.0, base.shield_regen + accum["shield_regen"])
    new_shield_delay = max(0.0, base.shield_regen_delay + accum["shield_regen_delay"])
    new_top_speed = max(60.0, base.top_speed + accum["top_speed"])
    new_accel = max(60.0, base.acceleration + accum["acceleration"])
    new_turn = max(0.5, base.turn_rate + accum["turn_rate"])
    new_energy_max = max(20.0, base.energy_max + accum["energy_max"])
    new_energy_regen = max(0.5, base.energy_regen + accum["energy_regen"])
    new_primary_damage = max(0.5, base.primary_damage + accum["primary_damage"])
    new_primary_rate = max(0.2, base.primary_rate + accum["primary_rate"])
    new_primary_range = max(80.0, base.primary_range + accum["primary_range"])
    new_primary_speed = max(120.0, base.primary_speed + accum["primary_speed"])
    return _dc.replace(
        base,
        hull_max=new_hull,
        shield_max=new_shield,
        shield_regen=new_shield_regen,
        shield_regen_delay=new_shield_delay,
        top_speed=new_top_speed,
        acceleration=new_accel,
        turn_rate=new_turn,
        energy_max=new_energy_max,
        energy_regen=new_energy_regen,
        primary_damage=new_primary_damage,
        primary_rate=new_primary_rate,
        primary_range=new_primary_range,
        primary_speed=new_primary_speed,
        primary_pattern=pattern_override or base.primary_pattern,
        special_ability=special_override or base.special_ability,
    )
