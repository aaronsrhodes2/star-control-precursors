"""Ship module catalog — installable upgrades for the Furling Scout.

## The Four Pillars of Ability Growth

The player's ship grows along four parallel collection-tracks. Each is a
distinct *flavor* of upgrade with its own collection mechanic, narrative
register, and gameplay effect. All four feed the same underlying stat
system (`Game.effective_stat()` sums installed modules' `deltas`), but
they're surfaced to the player as conceptually-separate progression axes.

1. **Crewmates** *(slots: crew_1, crew_2)* — passive-bonus passengers
   with named identities and story hooks. Improve specific roles: ship
   handling, weapon control, repair speed, sensor sensitivity, dialog
   leverage. Each crew NPC is a *character*, not a redshirt — they don't
   die, they don't have HP. They get on board, they ride along, they
   shift the player's stats. Collection: quest rewards + named-NPC
   encounters. Per [furling-tech-mechanics §5](../../../references/lore/furling-tech-mechanics.md).

2. **Sensor upgrades** *(slot: sensor)* — what the player can SEE. The
   sensor family extends along multiple axes: range (sensor_range,
   other_detection_range, surface_sensor_range), specificity (life,
   anomaly, enemy, mineral, proto-species), and system-level scanning
   (system_resource_scan). Each sensor is mutually-exclusive in the
   single sensor slot — install one, keep its trade-offs. Collection:
   tutorial pickup, alien quest rewards, shop purchase.

3. **Ship modules** *(slots: hull, drive, weapon, field)* — what the
   player's ship CAN DO. Main weapons (BEAM, PLASMA_LANCE), defenses
   (SHIELD_BOOSTER), special-weapon mods, engine mods (FUEL_TANK,
   QUASI_DRIVE), hull mods (CARGO_POD). The traditional combat-and-
   utility loadout slots. Collection: shop purchase + faction trade
   (Melnorme tech-buys) + quest rewards.

4. **Artifacts** *(parallel system: lives in `game.flags` + Bio-Archive
   entries)* — collected quest items, some of which gate abilities
   (Quasi-Space portal, Cloaking Satellite blueprint, Distress Beacon
   replayability). Some artifacts also slot in to a regular slot (e.g.
   the Rainbow Resonator occupies the field slot for the slice climax
   seeding); others are pure-flag (e.g. has_quasispace_portal, granted
   by the Arilou Sage). The Bio-Archive sub-scene at Mh-Lai Station is
   the player's record of artifacts collected. Collection: quest
   completion + observation + cinematic playback. See
   [src/scz/content/archive_entries.py](archive_entries.py) for the
   catalog of artifact records.

The four pillars share a single underlying mechanic — install a module,
sum the deltas, the renderer reads the effective stats and adjusts what
it shows. The conceptual separation is for *the player's mental model*
("I'm growing my crew" / "I'm upgrading my sensors") and for the
*authoring layer* (a new crewmate is a story beat; a new sensor is a
gameplay-info unlock; a new weapon is a combat tactical change).

Schema per `references/lore/station-screens-design.md`. Modules slot
into one of: hull / drive / weapon / sensor / field / crew_1 / crew_2.
Effective ship stats are the base Furling Scout stats plus the sum of
all installed modules' `deltas`. Quest-reward modules cost 0 credits;
purchasable modules cost credits + sometimes specific mineral types.

Crew specialists are NOT redshirts — they are passive-bonus passenger
upgrades, per the solo-captained doctrine in
[furling-tech-mechanics §5](../../../references/lore/furling-tech-mechanics.md).
"""

from __future__ import annotations

from dataclasses import dataclass, field


# Canonical module slot names — matches Game.ship_modules keys.
#
# 2026-05-18 refactor (Aaron: "make sure all of the mods are stackable,
# you are just limited to 12 of them"):
# - 12 GENERIC slots, no slot-type constraint
# - Same module can be installed in MULTIPLE slots; deltas stack
#   automatically via effective_stat()'s sum-over-values
# - Module.slot field is preserved as a CATEGORY label for UI grouping,
#   but is NOT enforced at install time
# - Pattern/special-override modules: when multiple compete, the one in
#   the lowest-numbered slot wins (deterministic precedence)
SLOTS: tuple[str, ...] = tuple(f"slot_{i + 1}" for i in range(12))
# Legacy slot names — kept ONLY for save-file migration (restore_game
# remaps these to slot_1..slot_7).
LEGACY_SLOT_NAMES: tuple[str, ...] = (
    "hull", "drive", "weapon", "sensor", "field", "crew_1", "crew_2",
)


@dataclass(frozen=True)
class Module:
    """One installable ship module. Static catalog entry — install/uninstall
    happens against Game state.
    """
    id: str
    name: str
    slot: str                   # one of SLOTS (crew modules can go in crew_1 OR crew_2)
    tier: int                   # 0 = quest-reward, 1 = standard, 2 = advanced
    cost_credits: int           # 0 for quest-reward
    cost_resources: dict[str, int] = field(default_factory=dict)
    deltas: dict[str, float] = field(default_factory=dict)
    description: str = ""
    locked: bool = False        # True = visible-but-uninstallable (quest gated)
    # When non-None, the module is hidden from the shop catalog until
    # the player has consumed a matching schematic at the Mh-Lai
    # Schematic Vault (i.e. `unlock_schematic in game.consumed_schematics`).
    # Per `references/lore/economy-and-trade-loops.md` §Schematic Loop:
    # a schematic is the *unlock*, not the purchase itself — the mod
    # still costs credits + minerals to buy after consuming the schematic.
    unlock_schematic: str | None = None
    # When non-None, REPLACES the Scout's primary_pattern in combat.
    # Pattern-changing mods (Lance Coil, Scatter Array, Tracking Laser
    # etc.) use this to swap the beam for an entirely different
    # firing pattern — the deltas dict tunes the numbers, this field
    # picks the behavior. Engine reads this via apply_scout_mods()
    # in combat/ships.py.
    primary_pattern_override: str | None = None
    # When non-None, REPLACES the Scout's special_ability in combat.
    # Special-swap mods (Phase Skip Mod, Chaff Spray Mod) use this
    # to plug in another ship class's special on the Scout chassis.
    special_ability_override: str | None = None
    # 2026-05-18 crew-perk overhaul (Aaron: "Do the same for our
    # crewmate normal and post-quest perks"). Each crew module has
    # a NORMAL perk (always active when installed) and an OPTIONAL
    # POST-QUEST perk (active once the crew member's personal arc
    # completes — gated on `post_quest_flag`). The post-quest perks
    # stack onto the normal perk; effective_stat in engine/game.py
    # checks the flag and conditionally adds `post_quest_deltas` /
    # post_quest pattern/special overrides.
    #
    # `post_quest_flag`: a game.flags key name (e.g. "mraka_quest_complete").
    # When the flag is True, the post_quest_deltas are summed onto the
    # base deltas. When False/missing, only the base deltas apply.
    #
    # `post_quest_deltas`: dict of stat→bonus values to ADD when the
    # post-quest flag is set. Same shape as `deltas`.
    post_quest_flag: str | None = None
    post_quest_deltas: dict[str, float] = field(default_factory=dict)
    # Optional post-quest pattern/special override (rare — most post-
    # quest perks just augment via deltas). Mirror of the base override
    # fields above; if non-None AND flag is set, they take effect.
    post_quest_pattern_override: str | None = None
    post_quest_special_override: str | None = None


# ---------------------------------------------------------------------------
# Quest-reward modules (tier 0, zero cost, granted on quest completion)
# ---------------------------------------------------------------------------

SCANNER_MK3 = Module(
    id="scanner_mk3",
    name="Stellar Field Scanner Mk III",
    slot="sensor",
    tier=0,
    cost_credits=0,
    deltas={
        "sensor_range": 1.5,            # hyperspace star-detection
        "surface_sensor_range": 0.10,   # lander deposit-fuzz range (additive on base 0.20)
        "surface_hazard_range": 0.05,   # lander hazard-detection range (additive on base 0.30)
    },
    description="Furlmart pickup — upgrades hyperspace sensor range 1.5x, extends the lander's deposit-fuzz range, and adds a small bump to hazard detection. The Mk II is half-blind on all three fronts.",
)

HYPERSPACE_ECHO_SENSOR = Module(
    id="hyperspace_echo_sensor",
    name="Hyperspace-Echo Sensor",
    slot="sensor",
    tier=0,
    cost_credits=0,
    deltas={"other_detection_range": 2.0},
    description="Slylandro gift — reveals Others' dimensional ripples at 2x normal range.",
)

MANTLE_RESONANCE_BIO_ARCHITECT = Module(
    id="bio_architect",
    name="Mantle-Resonance Bio-Architect",
    slot="crew_1",
    tier=0,
    cost_credits=0,
    # NORMAL perk — wider lander tractor (+50%) + faster replication
    # (+40%). Both functional surface-gameplay changes.
    deltas={"tractor_radius_bonus": 0.015, "lander_replication_bonus": 0.4},
    # POST-QUEST perk — Mantle Echo: in combat, the Scout's tractor
    # field passively pulls asteroids toward it within 200u, forming
    # a defensive cluster. Flag set when the player resolves Mycon
    # Whisper "allow" AND visits the Mycon Biot Hive afterward.
    post_quest_flag="mycon_mantle_echo_unlocked",
    post_quest_deltas={"combat_tractor_pull_radius": 200.0},
    description="Mycon gift — tractor beam +50% radius, landers replicate 40% faster. Post-quest 'Mantle Echo': passive in-combat asteroid-pull within 200u (turns the Scout into a small gravity well).",
)

RAINBOW_RESONATOR = Module(
    id="rainbow_resonator",
    name="Rainbow Resonator",
    slot="field",
    tier=0,
    cost_credits=0,
    deltas={},
    description="Required to seed the cluster's Rainbow World. Slice-climax module.",
)

LR_MINERAL_SCANNER = Module(
    id="lr_mineral_scanner",
    name="Long-Range Mineral Scanner",
    slot="sensor",
    tier=1,
    cost_credits=120,
    cost_resources={"USEFUL": 4},
    # Capability flag: setting any positive value here unlocks the HUD
    # mineral-totals readout for the nearest star in hyperspace. Future
    # stronger LR scanners could increase the value to surface totals for
    # a wider radius of stars rather than just the nearest one.
    deltas={"system_resource_scan": 1.0, "sensor_range": 0.3},
    description="Scans star systems from hyperspace and reports total mineral yield before you enter. Scout the cluster, then commit to the richest systems.",
)


# UNLOCKED_BY: melnorme_committed (quest: "Trader's Manifest" — Melnorme
# Council Seat at Alpha Vulpeculae; awarded at quest Beat 5 as part of
# the recruitment commitment ceremony).
#
# Sensor stub — final deltas pending Lore-chat alignment per
# species-quests.md "Open canonical questions (TODO_LORE)". The working
# hypothesis is the module surfaces all super-giant trade-routes on the
# starmap regardless of whether the Steward has flown there, plus
# per-system "expected bio-cargo yield" hints to the system scan. For
# slice MVP the module just registers as a sensor-slot upgrade with a
# stat key the future HUD layer can hook.
MELNORME_TRADE_NETWORK_SENSOR = Module(
    id="melnorme_trade_network_sensor",
    name="Melnorme Trade-Network Sensor",
    slot="sensor",
    tier=0,             # quest-reward; not shop-buyable
    cost_credits=0,
    deltas={
        "sensor_range": 0.5,
        "trade_route_visibility": 1.0,
        "bio_cargo_predict": 1.0,
    },
    description="A Melnorme cold-substrate sensor unit, pressed into your hold by the Trade-Council at Alpha Vulpeculae as part of the recruitment commitment. Surfaces the Melnorme spice-routes — every super-giant in the cluster registers as a known trade-stop, with per-system bio-cargo yield predictions overlaid on the system scan. *(Final stat tuning pending Lore-chat alignment — see references/lore/species-quests.md.)*",
    locked=True,        # quest-gated; not in shop until canon stabilizes
)

# ---------------------------------------------------------------------------
# Tier-1 modules (purchasable from the start)
# ---------------------------------------------------------------------------

BACKUP_CAPACITOR = Module(
    id="backup_capacitor",
    name="Backup Capacitor",
    slot="drive",
    tier=1,
    cost_credits=60,
    deltas={"energy_max": 20.0},
    description="Auxiliary energy bank tapped into the drive coils. +20 max energy. Useful starter for any weapon-heavy loadout.",
)

SHIELD_BOOSTER_I = Module(
    id="shield_booster_i",
    name="Shield Booster I",
    slot="field",
    tier=1,
    cost_credits=90,
    cost_resources={"USEFUL": 5},
    deltas={"shield_max": 20},
    description="Stronger projector coils. +20 shield HP.",
)

BEAM_MOD_I = Module(
    id="beam_mod_i",
    name="Beam Modulator I",
    slot="weapon",
    tier=1,
    cost_credits=75,
    deltas={"primary_damage": 2},
    description="Tighter beam coherence. +2 damage per primary shot.",
)

CARGO_POD_PLUS_50 = Module(
    id="cargo_pod_plus_50",
    name="Cargo Pod +50",
    slot="hull",
    tier=1,
    cost_credits=50,
    deltas={"cargo_max": 50},
    description="Strapped-on lander cargo pod. +50 hold capacity.",
)

# ---------------------------------------------------------------------------
# Tier-2 modules (gated by quest progress or rare resources)
# ---------------------------------------------------------------------------

QUASI_DRIVE_COMPACT = Module(
    id="quasi_drive_compact",
    name="Quasi-Drive (Compact)",
    slot="drive",
    tier=2,
    cost_credits=180,
    cost_resources={"ENERGY": 8},
    deltas={"quasi_space_access": 1.0},
    description="Built-in Quasi-Space portal — independent of the Arilou Sage's gift.",
)

SA_MATRA_LANCE_REPLICA = Module(
    id="sa_matra_lance_replica",
    name="Sa-Matra Lance (Replica)",
    slot="weapon",
    tier=2,
    cost_credits=420,
    cost_resources={"ENERGY": 8, "USEFUL": 6},
    deltas={"primary_damage": 30, "primary_rate": 0.5},
    description="Defender-faction prototype lance — replica. Originally a locked Defender-quest reward; reworked 2026-05-18 to be schematic-gated. The schematic is recovered from a Defender shipyard cache (post-Final-Conflict salvage scene, deferred content). Until that content lands, this module is shop-listed when its schematic enters the Vault.",
    unlock_schematic="schematic_sa_matra_lance_replica",
)

# ---------------------------------------------------------------------------
# Melnorme catalog (super-giant traders, BIO-cargo currency).
#
# CANON NOTE (2026-05-17): Per the economy-and-trade-loops doctrine,
# **Melnorme sell ONLY sensors + lander-hardening**. Ship mods (weapons,
# shields, hull, drive, field) are Mh-Lai's niche.
# See references/lore/economy-and-trade-loops.md.
#
# This narrows the existing catalog:
# - MELNORME_PATTERN_SENSOR — fits new canon (it's a sensor). ✓
# - MELNORME_PLASMA_LANCE — VIOLATES new canon (weapon). Design-chat to
#   resolve via one of three paths:
#     (a) RETIRE: remove from MODULES registry entirely
#     (b) RELOCATE: change vendor framing in name/description to Mh-Lai,
#         re-tier to 1+, add cost
#     (c) SCHEMATIC-CONVERT (recommended): introduce
#         `schematic_furling_coil_lance` sold by Melnorme for BIO-cargo;
#         on Mh-Lai schematic-vault consumption, unlocks a Mh-Lai-buyable
#         weapon mod with these same deltas
#   Until Design resolves, this module remains in MODULES for test
#   compatibility but the description has been updated to reflect that
#   it's a pending-canon-resolution entry.
#
# Future Melnorme catalog additions (lander-hardening — Design framework
# pending): MELNORME_LANDER_ABLATIVE_HULL, MELNORME_LANDER_HAZARD_SHIELD,
# MELNORME_LANDER_TRACTOR_FOCUSER. All would be tier-1+, BIO-cargo cost,
# field-installable (lander-system slot, parallel to sensor slot).
# ---------------------------------------------------------------------------

MELNORME_PLASMA_LANCE = Module(
    id="melnorme_plasma_lance",
    name="Furling Coil Lance (pending vendor resolution)",
    slot="weapon",
    tier=0,
    cost_credits=0,
    deltas={"primary_damage": 6, "primary_rate": 1.2},
    description="Furling-engineered ionization-coil weapon. Originally framed as Melnorme-direct-sale, but the 2026-05-17 economy canon restricts Melnorme to sensors + lander-hardening only. Pending Design-chat resolution: either retire this module, relocate it to Mh-Lai shop at tier 1+, or convert to a Melnorme-sold schematic that unlocks a Mh-Lai weapon. The deltas remain authoritative; the vendor framing is what needs to change.",
)

MELNORME_PATTERN_SENSOR = Module(
    id="melnorme_pattern_sensor",
    name="Melnorme Pattern Sensor",
    slot="sensor",
    tier=0,
    cost_credits=0,
    deltas={"other_detection_range": 1.5, "dialog_context_depth": 1.3},
    description="Melnorme-exclusive — ionization-pattern analyzer. Boosts Others detection and deepens dialog context. Bought with BIO-cargo at any super-giant trading post. Sensors are field-installable (no Mh-Lai gate).",
)

# Lemmkin Pattern Database — granted by `_lemmkin_science_trade` in
# `dialog/characters.py:194` as a side-effect of the Lemmkin science
# trade beat. Audit 2026-05-18 caught this as a reverse-orphan: the
# grant code existed but the Module dataclass entry didn't — meaning
# the Customization scene's `MODULES.get(installed_id)` would return
# None and the install rendered as a bare id string. Adding the
# Module entry closes the loop.
LEMMKIN_PATTERN_DATABASE = Module(
    id="lemmkin_pattern_database",
    name="Lemmkin Pattern Database",
    slot="sensor",
    tier=0,
    cost_credits=0,
    deltas={
        "system_anomaly_scan": 1.0,
        "proto_species_scan": 1.0,
        "sensor_range": 0.4,
    },
    description="Lemmkin-gifted research archive — eclectic-pattern recognition library compiled by the Whirligig troupes' enthusiastic science output. Surfaces anomalies + proto-species signatures across the cluster. The Lemmkin trade was sincere; the cheerful exchange is preserved as-is in the data.",
)

# ----- Tier-0 quest-reward sensors (2026-05-18 expansion) -----
# Sensors are always-on per Aaron's canon — these are passive
# discovery-extender modules granted via quest reward (one per
# species niche). Mutually exclusive with each other (single sensor
# slot) — players pick the discovery axis they need that mission.

KARAVEM_AERIAL_SENTRY = Module(
    id="karavem_aerial_sentry",
    name="Karavem Aerial Sentry",
    slot="sensor",
    tier=0,
    cost_credits=0,
    deltas={"flying_threat_range": 0.20, "surface_sensor_range": 0.05},
    description="Karavem gift — perch-singer migration patterns transposed onto sensor logic. Flying-tier fauna pings at extended range so you can route around them before they swoop.",
    locked=True,
)

ARILOU_PORTAL_PATHFINDER = Module(
    id="arilou_portal_pathfinder",
    name="Arilou Portal Pathfinder",
    slot="sensor",
    tier=0,
    cost_credits=0,
    deltas={"qs_portal_pre_reveal": 1.0, "sensor_range": 0.3},
    description="Arilou extended gift — quasispace-portal mapping woven into the Scout's hyperspace scanner. Undiscovered portals + their hyperspace exits surface on entry.",
    locked=True,
)

COUNCIL_MIGRATION_BEACON = Module(
    id="council_migration_beacon",
    name="Council Migration Beacon",
    slot="sensor",
    tier=0,
    cost_credits=0,
    deltas={"migration_beacon_visible": 1.0, "sensor_range": 0.2},
    description="Furling Council issue — receives the Migration fleet's coordinating broadcasts. Fleet positions surface on the hyperspace map as the migration progresses.",
    locked=True,
)

STELLOTH_ARTIFACT_LOCATOR = Module(
    id="stelloth_artifact_locator",
    name="Stelloth Artifact Locator",
    slot="sensor",
    tier=0,
    cost_credits=0,
    deltas={"artifact_visibility_full": 1.0},
    description="Stelloth gift — quest-item PACKAGE deposits render at full clarity on the lander surface regardless of distance, so you don't have to grid-search for tiny pickups.",
    locked=True,
)

TAALO_STRATA_TOMOGRAPHY = Module(
    id="taalo_strata_tomography",
    name="Taalo Strata Tomography",
    slot="sensor",
    tier=0,
    cost_credits=0,
    deltas={"deep_strata_visibility": 0.15, "surface_sensor_range": 0.05},
    description="Taalo gift — silicon-being deep-rock perception transposed into the lander scanner. High-value ENERGY and USEFUL deposits surface at extended range; the rest stay quiet.",
    locked=True,
)


# ---------------------------------------------------------------------------
# Crew specialist modules (passenger-class — NOT combat-vulnerable)
# ---------------------------------------------------------------------------

CREW_ARCHIVIST = Module(
    id="crew_archivist",
    name="Crew: Furling Archivist",
    slot="crew_1",
    tier=1,
    cost_credits=120,
    # NORMAL perk — the Archivist whispers lore-relevant facts in your
    # ear during every dialog encounter, unlocking one extra response
    # category per FSM state (e.g. ASK appears even when the FSM
    # default wouldn't expose it). Read by dialog/scene.py's choice
    # filter when present.
    deltas={"dialog_extra_choice": 1.0},
    # No post-quest perk — the generic crew aren't quest-tied.
    description="Hand-trained Archivist — whispers lore-relevant facts during every dialog encounter, unlocking one extra ASK/RECALL response in any FSM state. Frequent, subtle, always useful.",
)

CREW_WARDEN = Module(
    id="crew_warden",
    name="Crew: Furling Warden",
    slot="crew_2",
    tier=1,
    cost_credits=140,
    cost_resources={"USEFUL": 4},
    # NORMAL perk — the Warden's trained reflexes parry the FIRST
    # damaging hit of every combat encounter. One-shot per fight,
    # resets on next combat scene. Read by `apply_damage` via
    # `mod_hit_negate_first_per_fight`.
    deltas={"hit_negate_first_per_fight": 1.0},
    description="Defender-trained Warden — trained reflexes parry the FIRST damaging hit of every combat encounter (one-shot per fight). Reads as 'the alpha-strike misses'; sustained damage still bites.",
)

CREW_TUNNELER = Module(
    id="crew_tunneler",
    name="Crew: Furling Tunneler",
    slot="crew_2",
    tier=1,
    cost_credits=120,
    cost_resources={"ENERGY": 2},
    # NORMAL perk — the Tunneler reveals all 12 Quasi-Space portals
    # on the QS map immediately, instead of progressive discovery.
    # Functional (changes what the player can see/use).
    deltas={"quasispace_portal_visible": 1.0},
    description="Quasi-Space-trained Tunneler — all 12 QS portals revealed on the map immediately (no discover-by-traversal). Plus 'navigation feel' for the routes between them.",
)

# ---------------------------------------------------------------------------
# Crew specialists — named Furling NPCs gained through SIDE-QUESTS.
# Each fills a *role* (pilot / weapons / engineer / medic / navigator) with
# a Lore-chat-authored recruitment side-quest. Unlocked 2026-05-17.
#
# These five are NOT shop-purchasable. Each is granted to the player when
# the corresponding recruitment quest completes (flag set, then module
# moves into game.uninstalled_modules).
#
# Quest-flag gating: each carries an UNLOCKED_BY comment naming the flag
# that Design-chat should wire as the unlock condition. The module-scene
# filter currently only honors `locked=True/False`; Design-chat to decide
# whether to extend the Module dataclass with an `unlock_flag: str | None`
# field, or to filter at the scene layer based on game.flags. Until then,
# these stay locked=True and are pre-staged in MODULES so the Bio-Archive
# can reference their identity from the moment a quest hook surfaces.
#
# Full side-quest content: references/lore/crew-recruitment-quests.md
# Three canonical Furling crew titles are already taken (Archivist, Warden,
# Tunneler — see above); the five below introduce four new role-titles
# (Drifter, Aimer, Mender, Star-Reader) plus reuse the canonical
# Bio-Architect for the Medic role (dimensional-shear repair is
# bio-engineering lineage). Costs/slots/deltas remain Design-chat's
# framework; Lore chat only touched name + description + locked.
# ---------------------------------------------------------------------------

# UNLOCKED_BY: recruited_pilot (quest: "The Sure-Foot" — Mh-Lai docking
# lounge, post-Furlmart shakedown; optional Drifter's Circuit hyperspace
# navigation challenge then recruitment beat in the galley)
CREW_PILOT = Module(
    id="crew_pilot",
    name="Crew: Mraka Yenn-Sa, Furling Drifter",
    slot="crew_1",
    tier=1,
    cost_credits=0,
    # NORMAL perk: "Drifter's Touch" — Mraka rides shotgun on body-
    # collision physics. The Scout takes 75% less damage from planet/
    # moon/asteroid impacts (reuses the Crash Plating hook). She knows
    # how to bounce.
    deltas={"crash_damage_reduction": 0.75},
    # POST-QUEST: "Sure-Foot Maneuver" — the Inertia Dumpers control
    # scheme is unlocked (rotate 180° + thrust against velocity =
    # instant zero, no drift). Reuses inertia_dump flag.
    post_quest_flag="mraka_sure_foot_unlocked",
    post_quest_deltas={"inertia_dump": 1.0},
    description="Mraka Yenn-Sa, Furling Drifter — retired hyperspace-racing-circuit veteran. Recruited via 'The Sure-Foot' at Mh-Lai after the Furlmart shakedown. NORMAL: 'Drifter's Touch' — body-collision damage reduced 75%. POST-QUEST: 'Sure-Foot Maneuver' — Inertia Dumpers unlocked (rotate-and-reverse-thrust instantly zeros velocity, free 180-flip dodge).",
    locked=True,
)

# UNLOCKED_BY: recruited_weapons_officer (quest: "The Beacon Witness" —
# Mh-Lai Defender training cohort barracks, after the Distress Beacon
# is screened for the cohort; Bren-Vor approaches privately and requests
# transfer from Defender training to Persuader-aligned active duty)
CREW_WEAPONS_OFFICER = Module(
    id="crew_weapons_officer",
    name="Crew: Bren-Vor Telcas, Furling Aimer",
    slot="crew_1",
    tier=1,
    cost_credits=0,
    # NORMAL perk: "Patient Eye" — Bren-Vor refines the firing
    # solution so the Scout's primary costs 30% less energy per shot.
    # The Aimer's hand cuts the wastage. Lets you sustain fire longer.
    deltas={"primary_energy_reduction": 0.30},
    # POST-QUEST: "Velt-Ra's Mark" — kill-stack damage. Every enemy
    # ship the Scout kills in a fight adds +1.5 damage to every
    # subsequent primary bolt for the rest of the encounter. Bren-Vor
    # carries his sister's grief into precision; each loss earns each
    # shot more. Stacks reset between fights.
    post_quest_flag="brenvor_velt_ra_unlocked",
    post_quest_deltas={"kill_stack_damage": 1.5},
    description="Bren-Vor Telcas, Furling Aimer — former Defender trainee who shifted Persuader-aligned after losing his sister. Recruited via 'The Beacon Witness' after sharing the Distress Beacon. NORMAL: 'Patient Eye' — primary fire 30% energy-cheaper. POST-QUEST: 'Velt-Ra's Mark' — every kill in a fight adds +1.5 damage to every subsequent primary bolt for the rest of the encounter.",
    locked=True,
)

# UNLOCKED_BY: recruited_engineer (quest: "The Mender's Inspection" —
# Mh-Lai Customization bay, after the Steward installs any module;
# Yelena performs an inspection that fixes one specific maintenance
# oversight, then asks to ride with one of "her" ships in the field)
CREW_ENGINEER = Module(
    id="crew_engineer",
    name="Crew: Yelena Lwen-Tar, Furling Mender",
    slot="crew_1",
    tier=1,
    cost_credits=0,
    # NORMAL perk: "Mended in Transit" — Yelena patches micro-damage
    # continuously. Reuses the Repair Drone hook for 1.0 HP/sec
    # passive hull regen. Her tools are alphabetized; the ship gets
    # better while you fly it.
    deltas={"hull_regen_passive": 1.0},
    # POST-QUEST: "Alphabetized Tools" — Yelena pre-charges the
    # shield projectors before every fight. Combat starts with the
    # shield at 150% of max (overcharge bleeds back to 100% over
    # the first 5 seconds via normal regen interaction).
    post_quest_flag="yelena_alphabetized_unlocked",
    post_quest_deltas={"combat_start_shield_overcharge": 0.50},
    description="Yelena Lwen-Tar, Furling Mender — Unzervalt factory-floor lineage; deep mechanical intuition. Recruited via 'The Mender's Inspection'. NORMAL: 'Mended in Transit' — passive 1 HP/sec hull regen. POST-QUEST: 'Alphabetized Tools' — combat starts with shield overcharged to 150% (bleeds back to normal max over 5 seconds).",
    locked=True,
)

# UNLOCKED_BY: recruited_medic (quest: "The Bio-Architect's Apprenticeship" —
# Mira-Rou opt-in ride-along granted at Mh-Lai post-Beat-5; recruitment
# beat is at the next Mh-Lai docking after the Coel Tessar encounter
# resolves cleanly with refugees stabilized)
CREW_MEDIC = Module(
    id="crew_medic",
    name="Crew: Mira-Rou Halve-Tel, Furling Bio-Architect",
    slot="crew_2",
    tier=1,
    cost_credits=0,
    # NORMAL perk: "Steward Maintenance" — Mira watches the special-
    # weapon capacitor and bleeds heat from it after every primary
    # hit. Every projectile that lands shaves 0.20s off the Steward's
    # current special_cooldown_left. Lets the player chain primary +
    # special more aggressively.
    deltas={"cooldown_reduce_per_hit": 0.20},
    # POST-QUEST: "Bio-Architecture Emergency" — if hull would hit
    # 0 in a fight, Mira's emergency biot-grafts trigger a phase-
    # shift at the last possible moment (1.5s of invulnerability +
    # 30% hull restored once per fight). Reuses the Dimensional
    # Armor `phase_shift_hull_threshold` hook with a very-low
    # threshold; the post-quest mod also stacks an emergency-heal
    # flag the scene checks at activation.
    post_quest_flag="mira_bio_emergency_unlocked",
    post_quest_deltas={"phase_shift_hull_threshold": 0.01},
    description="Mira-Rou Halve-Tel, Furling Bio-Architect — Mycon biot-designer lineage. Recruited via 'The Bio-Architect's Apprenticeship' after Coel Tessar. NORMAL: 'Steward Maintenance' — every primary hit shaves 0.20s off the Steward's special cooldown. POST-QUEST: 'Bio-Architecture Emergency' — first time hull would hit 0 in a fight, Mira's biot-grafts trigger 1.5s invulnerability (one-shot per fight).",
    locked=True,
)

# UNLOCKED_BY: recruited_navigator (quest: "The Star-Reader's Routes" —
# Mh-Lai Council Archives wing, after the Steward has visited 3+ systems;
# Tarven hosts a Stellar-Drift Briefing tracing prior-Stewards' routes,
# then asks to ride as ship-Reader)
CREW_NAVIGATOR = Module(
    id="crew_navigator",
    name="Crew: Tarven Olwen-Sa, Furling Star-Reader",
    slot="crew_2",
    tier=1,
    cost_credits=0,
    # NORMAL perk: "Stellar Drift Reading" — in hyperspace, your
    # current autopilot route lights up RED if it crosses a hostile
    # species' sphere of influence. Tarven plots the lethal patches
    # before you fly into them. Hyperspace HUD reads this flag.
    deltas={"hostile_route_warning": 1.0},
    # POST-QUEST: "Iren-Vor's Quiet Route" — once per docking at
    # Mh-Lai, Tarven plots a "ghost route" through hyperspace; the
    # NEXT system traversal triggers zero random encounters (existing
    # encounters at fixed coords still fire — this is anti-pursuit
    # only). Hyperspace scene reads + clears the flag.
    post_quest_flag="tarven_quiet_route_unlocked",
    post_quest_deltas={"quiet_route_per_docking": 1.0},
    description="Tarven Olwen-Sa, Furling Star-Reader — junior Archivist; reads stellar drift across the Furling era. Recruited via 'The Star-Reader's Routes' at Mh-Lai Council Archives after the Steward visits 3+ systems. NORMAL: 'Stellar Drift Reading' — current hyperspace route lights up RED through hostile spheres so the player sees the danger before flying into it. POST-QUEST: 'Iren-Vor's Quiet Route' — once per Mh-Lai docking, the next system traversal triggers zero random encounters.",
    locked=True,
)


# ---------------------------------------------------------------------------
# Sensor specializations — each surfaces a specific class of discovery.
# All wired into render layers 2026-05-18:
# - surface_sensor_range / surface_hazard_range / life_detect_range /
#   flying_threat_range / deep_strata_visibility / mineral_type_clarity /
#   artifact_visibility_full → planet/scene.py _draw_deposits + _render_life
# - schematic_resonance / wreck_detect_range / stellar_class_visible /
#   migration_beacon_visible / danger_zone_visible / qs_portal_pre_reveal /
#   enemy_detect_range → hyperspace/scene.py _draw_extra_sensor_hud
# - system_anomaly_scan / system_resource_scan / proto_species_scan →
#   _draw_lr_scanner_hud (hyperspace) + system-scan anomaly gating
# - other_detection_range → _draw_ripples (Hyperspace Echo Sensor)
# ---------------------------------------------------------------------------

BIO_SENSE_SCANNER = Module(
    id="bio_sense_scanner",
    name="Bio-Sense Scanner",
    slot="sensor",
    tier=1,
    cost_credits=140,
    cost_resources={"BIO": 3, "USEFUL": 2},
    deltas={"life_detect_range": 1.0, "proto_species_scan": 1.0},
    description="Reveals biological signatures on planet surfaces and flags proto-species in scanned systems. Surface-life detect range extends so the lander sees fauna from further out; proto-species sites surface on the hyperspace HUD.",
)

ENEMY_SCANNER = Module(
    id="enemy_scanner",
    name="Enemy Scanner",
    slot="sensor",
    tier=1,
    cost_credits=180,
    cost_resources={"USEFUL": 4, "ENERGY": 2},
    deltas={"enemy_detect_range": 1.0, "cloak_pierce": 0.5},
    description="Surfaces enemy-ship ripples in hyperspace at distance, with modest cloak-piercing capability. Turns intercepts into pre-warned engagements.",
)

ANOMALY_SCANNER = Module(
    id="anomaly_scanner",
    name="Anomaly Scanner",
    slot="sensor",
    tier=1,
    cost_credits=160,
    cost_resources={"USEFUL": 3},
    deltas={"system_anomaly_scan": 1.0, "surface_sensor_range": 0.15},
    description="System-level anomaly readout in hyperspace HUD (Furling caches, dormant artifacts, Rainbow markers, etc.) plus a surface-sensor bonus. Renderer already wired via `_draw_lr_scanner_hud`.",
)

HAZARD_SCANNER = Module(
    id="hazard_scanner",
    name="Hazard Scanner",
    slot="sensor",
    tier=1,
    cost_credits=130,
    cost_resources={"USEFUL": 3},
    deltas={"surface_hazard_range": 0.20, "surface_sensor_range": 0.05},
    description="Surface-danger specialist — reveals lava fields, lightning strikes, and other lethal terrain hazards from much further out (base 0.30 + this 0.20 = 0.50 of the surface visible at once). Modest deposit-sensor bonus alongside. Tutorial-extension upgrade for players who lost a lander to a hazard they didn't see coming.",
)

MINERAL_SPECTROMETER = Module(
    id="mineral_spectrometer",
    name="Mineral Spectrometer",
    slot="sensor",
    tier=1,
    cost_credits=130,
    cost_resources={"USEFUL": 3},
    deltas={"mineral_type_clarity": 1.0, "surface_sensor_range": 0.05},
    description="Resource-type analyzer. Deposits identify their type at sensor edge, not just up close — no more chasing a faint blob to find out it's only COMMON.",
)

SCHEMATIC_RESONANCE_READER = Module(
    id="schematic_resonance_reader",
    name="Schematic Resonance Reader",
    slot="sensor",
    tier=1,
    cost_credits=150,
    cost_resources={"USEFUL": 3, "BIO": 2},
    deltas={"schematic_resonance": 1.0, "sensor_range": 0.2},
    description="Hyperspace ping — systems holding unconsumed schematics light up on the starmap. Tightens the carrot-back-home loop, the long-pole gating mechanism of the slice.",
)

WRECK_PATTERN_READER = Module(
    id="wreck_pattern_reader",
    name="Wreck Pattern Reader",
    slot="sensor",
    tier=1,
    cost_credits=140,
    cost_resources={"USEFUL": 3, "ENERGY": 1},
    deltas={"wreck_detect_range": 0.5, "sensor_range": 0.2},
    description="Salvage-derelict detection range +50%. Worth the slot when running a salvage-heavy approach; competitive with the mineral scanner for resource-focused play.",
)

DANGER_ZONE_FORECASTER = Module(
    id="danger_zone_forecaster",
    name="Danger-Zone Forecaster",
    slot="sensor",
    tier=1,
    cost_credits=170,
    cost_resources={"USEFUL": 4, "ENERGY": 2},
    deltas={"danger_zone_visible": 1.0, "other_detection_range": 0.5},
    description="Renders hyperspace no-go regions (Others-territory, Cleanser patrols, post-Fall ash zones) on the map. Pairs well with the schematic-resonance reader for safe routing.",
)

MELNORME_STELLAR_CLASS_READER = Module(
    id="melnorme_stellar_class_reader",
    name="Melnorme Stellar-Class Reader",
    slot="sensor",
    tier=2,
    cost_credits=200,
    cost_resources={"BIO": 4, "ENERGY": 2},
    deltas={"stellar_class_visible": 1.0, "sensor_range": 0.3},
    description="Melnorme tech-trade — stellar-spectroscopy archive distilled into a sensor module. Star class (super-giant, dwarf, anomalous) surfaces on the hyperspace map before entering. Buy with BIO at any Melnorme super-giant station.",
)


# ---------------------------------------------------------------------------
# Weapon-mod stubs — distinct from main-weapon modules. Main weapons
# *replace* the primary beam (BEAM_MOD_I, MELNORME_PLASMA_LANCE);
# weapon-mods *modify* whatever main weapon is installed. They share the
# weapon slot for now (player picks one or the other); a future refactor
# could split them into separate sub-slots if the trade-offs feel too
# painful in playtest.
# ---------------------------------------------------------------------------

WEAPON_MOD_ACCURACY = Module(
    id="weapon_mod_accuracy",
    name="Weapon Mod: The Patient Eye",
    slot="weapon",
    tier=1,
    cost_credits=0,
    deltas={"primary_accuracy": 1.3, "primary_rate": 0.95},
    description="The Patient Eye — Furling weapons-craftsmen modeled this targeting refinement on the slow careful aim a hunter takes before a single committed shot. The mod hesitates the firing solution by a fraction of a second to lock the lead-vector tighter. Trades a small fire-rate cost for noticeably tighter aim. Stacks with crew bonuses.",
    locked=False,
)

WEAPON_MOD_RELOAD = Module(
    id="weapon_mod_reload",
    name="Weapon Mod: The Restless Coil",
    slot="weapon",
    tier=1,
    cost_credits=0,
    deltas={"primary_rate": 1.25, "primary_energy_cost": 1.15},
    description="The Restless Coil — a Furling-engineered capacitor pre-charge that keeps the next pulse ready a beat before it is called. Reduces the dwell between shots at the cost of higher per-shot energy draw. Drains the energy pool quicker; trade-off with shield-regen or special-weapon availability. The Aimers consider it gauche; the Drifters love it.",
    locked=False,
)


# ---------------------------------------------------------------------------
# Combat mod catalog (2026-05-18) — 24 ways to modify how the Scout
# behaves and succeeds in combat. Authored after Game Design canonized
# that encounters are super-melees: most fights are either a heavily-
# modded Scout alone OR Scout + 1-4 allies vs a fleet. The Scout's
# value-prop is modularity, so the mod catalog needs to support many
# distinct fighting styles.
#
# Organization:
#   - 8 PATTERN mods (weapon slot) — replace the beam with a different
#     primary firing pattern (twin / lance / scatter / pulse / homing /
#     burst / tracking / lawnmower-blade). Each plays differently.
#   - 2 WEAPON-STAT mods (weapon slot) — improve the base beam without
#     changing its pattern (Beam Modulator II, Engine Disruptor).
#   - 4 FIELD/SHIELD mods (field slot) — Shield Cap, Shield Catalyst,
#     Crystalline Armor, Reactive Plating.
#   - 3 HULL mods (hull slot) — Hull Reinforcement, Repair Drone,
#     Ablative Coating.
#   - 3 DRIVE mods (drive slot) — Thruster Boost, Maneuvering Jets,
#     Gyro Stabilizer.
#   - 2 ENERGY mods (drive slot — energy is power-systems-adjacent) —
#     Energy Cell, Power Regenerator.
#   - 2 SPECIAL-SWAP mods (field slot — they swap the special ability)
#     — Phase Skip Mod, Chaff Spray Mod.
#
# Engine support:
#   - Stat deltas read by Game.effective_stat() and applied in combat
#     via apply_scout_mods() in combat/ships.py.
#   - primary_pattern_override and special_ability_override swap the
#     Scout's pattern/special when non-None.
#   - Behavior flags (damage_reduction, bounce_chance, etc.) read by
#     hooks in scene.py's apply_damage / _regen / _spawn_projectile.
# ---------------------------------------------------------------------------

# ----- PATTERN MODS (weapon slot) — 8 different combat feels -----

MOD_TWIN_BEAM = Module(
    id="mod_twin_beam",
    name="Twin Beam Array",
    slot="weapon",
    tier=1,
    cost_credits=140,
    cost_resources={"USEFUL": 3},
    deltas={"primary_damage": -2, "primary_rate": 0.5},
    primary_pattern_override="twin",
    description="Splits the coherence-coil output into two parallel beams. Each bolt hits a touch lighter, but at this fire rate you spray-paint a target. Persuader weapons-officers love it; Aimers consider it gauche.",
)

MOD_LANCE_COIL = Module(
    id="mod_lance_coil",
    name="Lance Coil",
    slot="weapon",
    tier=2,
    cost_credits=240,
    cost_resources={"ENERGY": 4},
    deltas={"primary_damage": 6, "primary_range": 150, "primary_rate": -2.0},
    primary_pattern_override="lance",
    description="A long thin focus-coil that builds for a beat before releasing one decisive lance bolt. Long range, slow rate, painful per-hit. Turns the Scout into a sniper.",
)

MOD_SCATTER_ARRAY = Module(
    id="mod_scatter_array",
    name="Scatter Array",
    slot="weapon",
    tier=1,
    cost_credits=130,
    cost_resources={"USEFUL": 3},
    deltas={"primary_damage": -3, "primary_range": -180},
    primary_pattern_override="scatter",
    description="Shotgun-style 5-bolt wide-cone burst. Close range, per-bolt weak, full-volley brutal. Live or die by gap-closing.",
)

MOD_PULSE_CANNON = Module(
    id="mod_pulse_cannon",
    name="Pulse Cannon",
    slot="weapon",
    tier=2,
    cost_credits=220,
    cost_resources={"ENERGY": 3},
    deltas={"primary_damage": 14, "primary_rate": -2.5, "primary_speed": -1700},
    primary_pattern_override="single",
    description="One slow heavy capacitor-pulse per trigger pull. Punishes immobile targets; misses badly against jinkers. Pair with Phase Skip or evasive postures so the slow rate isn't a death sentence.",
)

MOD_HOMING_MORTAR = Module(
    id="mod_homing_mortar",
    name="Homing Mortar",
    slot="weapon",
    tier=2,
    cost_credits=230,
    cost_resources={"ENERGY": 4},
    deltas={"primary_damage": 3, "primary_rate": -2.5, "primary_speed": -1800},
    primary_pattern_override="homing",
    description="Slow heat-seeking plasmoid. Forgiving aim — the projectile course-corrects toward the target. Great for keeping pressure on fleeing or chaotic-moving enemies.",
)

MOD_BURST_CANNON = Module(
    id="mod_burst_cannon",
    name="Burst Cannon",
    slot="weapon",
    tier=1,
    cost_credits=150,
    cost_resources={"USEFUL": 4},
    deltas={"primary_damage": -2, "primary_rate": -1.0},
    primary_pattern_override="burst",
    description="Three-bolt tight-fan burst per pull. Persuader-faction signature — reads as a measured pop-pop-pop. Volleys land cleanly at mid-range.",
)

MOD_TRACKING_LASER = Module(
    id="mod_tracking_laser",
    name="Tracking Laser",
    slot="weapon",
    tier=2,
    cost_credits=260,
    cost_resources={"ENERGY": 4},
    deltas={"primary_damage": -1, "primary_rate": 2.0},
    primary_pattern_override="tracking",
    description="Arilou-pattern auto-tracking laser. Each bolt curves mid-flight toward whatever your nose is roughly pointed at. Forgiving aim, fast rate, low per-shot damage — death by a thousand cuts.",
)

MOD_LAWNMOWER_DISC = Module(
    id="mod_lawnmower_disc",
    name="Lawnmower Disc",
    slot="weapon",
    tier=2,
    cost_credits=210,
    cost_resources={"USEFUL": 5},
    deltas={"primary_damage": 8, "primary_rate": -3.0},
    primary_pattern_override="lawnmower_blade",
    description="Proto-Qor-Ah pattern — a wide spinning blade disc launched forward. Slow fire, but the disc is FAT and mows through whatever it crosses. Brutal in close, useless at long range.",
)

# ----- WEAPON-STAT MODS (weapon slot, no pattern swap) -----

MOD_BEAM_MOD_II = Module(
    id="mod_beam_mod_ii",
    name="Chain Lightning Coil",
    slot="weapon",
    tier=2,
    cost_credits=220,
    cost_resources={"USEFUL": 4, "ENERGY": 3},
    deltas={"chain_lightning_damage": 4.0},
    description="Each primary bolt that lands SPLITS into a chain bolt aimed at the nearest other target (enemy ship OR asteroid). The chain bolt does 4 damage; if it lands, it spawns one more 2.8-damage child. Devastating in fleet fights or asteroid-rich arenas.",
)

MOD_ENGINE_DISRUPTOR = Module(
    id="mod_engine_disruptor",
    name="Engine Disruptor Coil",
    slot="weapon",
    tier=2,
    cost_credits=210,
    cost_resources={"ENERGY": 3},
    deltas={"primary_damage": -1, "engine_damage_on_hit": 12.0},
    description="Defender-faction harmonic engineered into your beam. Each hit deals slightly less damage but permanently disables 12 units of the target's engine output (stacks, floor at 60 u/s top speed). Turns fast enemies into limping ones — control via attrition.",
)

# ----- FIELD/SHIELD MODS (field slot) — 4 distinct defensive flavors -----

MOD_SHIELD_CAPACITOR = Module(
    id="mod_shield_capacitor",
    name="Reflector Shield",
    slot="field",
    tier=2,
    cost_credits=240,
    cost_resources={"USEFUL": 5},
    deltas={"reflect_chance": 0.30},
    description="When shield is up and an incoming bolt hits, 30% chance the shield BOUNCES the bolt back along its incoming line — at the firer. Reads as a chaotic gift to evasive pilots and a nightmare for scatter-pattern attackers. Useless without an intact shield, so pair with shield-related mods if you want a stable defense.",
)

MOD_SHIELD_CATALYST = Module(
    id="mod_shield_catalyst",
    name="Thorn Shield",
    slot="field",
    tier=2,
    cost_credits=220,
    cost_resources={"USEFUL": 4, "BIO": 2},
    deltas={"thorn_pulse_radius": 180.0, "thorn_pulse_frac": 0.5},
    description="Crystalline thorn-lattice woven through the shield array. Every time the shield ABSORBS damage, it emits a 180-unit radial energy pulse for HALF the damage absorbed. Close-range attackers get back what they delivered. Stationary shooters at range stay safe; brawlers regret it.",
)

MOD_CRYSTALLINE_ARMOR = Module(
    id="mod_crystalline_armor",
    name="Crystalline Plating",
    slot="field",
    tier=2,
    cost_credits=260,
    cost_resources={"USEFUL": 6, "BIO": 4},
    deltas={"damage_reduction": 0.25},
    description="Chenjesu-pattern crystal lattice plating, harvested as fragments and re-grown on the Scout's exterior. Every incoming hit deals 25% less damage. No regen, no special trigger — just consistent mitigation.",
)

MOD_REACTIVE_PLATING = Module(
    id="mod_reactive_plating",
    name="Reactive Plating",
    slot="field",
    tier=2,
    cost_credits=240,
    cost_resources={"USEFUL": 5},
    deltas={"bounce_chance": 0.30},
    description="Smart-armor plating that reads incoming kinetic signature in time to deflect. 30% chance per hit to bounce the projectile harmlessly off — chaotic, occasionally devastating against scatter weapons.",
)

# ----- HULL MODS (hull slot) — 3 durability variants -----

MOD_HULL_REINFORCEMENT = Module(
    id="mod_hull_reinforcement",
    name="Crash Plating",
    slot="hull",
    tier=1,
    cost_credits=160,
    cost_resources={"USEFUL": 5},
    deltas={"crash_damage_reduction": 0.60, "crash_push_mult": 2.0},
    description="Reinforced collision-survival armor. Body-collision damage is reduced 60% AND the Scout SHOVES asteroids in the collision direction at 2× speed. Turns the arena's hazards into half-decent kinetic weapons — and a planet-grazing pilot survives the mistake instead of bouncing off bleeding.",
)

MOD_REPAIR_DRONE = Module(
    id="mod_repair_drone",
    name="Repair Drone Bay",
    slot="hull",
    tier=2,
    cost_credits=240,
    cost_resources={"USEFUL": 6, "ENERGY": 2},
    deltas={"hull_regen_passive": 1.5},
    description="A pair of palm-sized repair drones that buzz over your hull and patch micro-damage continuously. +1.5 HP/sec passive hull regen. Doesn't trigger; doesn't care about cooldowns. Just slowly rebuilds you.",
)

MOD_ABLATIVE_COATING = Module(
    id="mod_ablative_coating",
    name="Ablative Coating",
    slot="hull",
    tier=1,
    cost_credits=140,
    cost_resources={"USEFUL": 5},
    deltas={"ablative_pool": 60.0},
    description="Sacrificial outer coating layer that absorbs the first 60 HP of damage of any fight before the hull starts taking real hits. Doesn't regenerate during combat — once depleted, you're back to standard durability.",
)

# ----- DRIVE/MOBILITY MODS (drive slot) -----

MOD_THRUSTER_BOOST = Module(
    id="mod_thruster_boost",
    name="Afterburners",
    slot="drive",
    tier=2,
    cost_credits=200,
    cost_resources={"USEFUL": 3, "ENERGY": 2},
    deltas={"afterburners": 1.0},
    description="Hold thrust continuously for 2 seconds and the afterburners ignite — 3 seconds of 1.6× top-speed AND acceleration. Then a 4-second cooldown before they can re-ignite. Reads as a committed sprint: you'll close the gap or escape a tight spot, but you can't do it casually.",
)

MOD_MANEUVERING_JETS = Module(
    id="mod_maneuvering_jets",
    name="Inertia Dumpers",
    slot="drive",
    tier=1,
    cost_credits=170,
    cost_resources={"USEFUL": 4},
    deltas={"inertia_dump": 1.0},
    description="High-thrust reverse-vector jets. When you rotate 180° and thrust AGAINST your current velocity, the dumpers instantly zero your momentum before applying the new thrust. Newtonian flight becomes arcade-style on demand — no more drifting past a target you wanted to engage.",
)

MOD_GYRO_STABILIZER = Module(
    id="mod_gyro_stabilizer",
    name="Strafing Jets",
    slot="drive",
    tier=1,
    cost_credits=150,
    cost_resources={"USEFUL": 3},
    deltas={"strafing_jets_force": 180.0, "turn_rate": 0.5},
    description="Side-vectored thrusters fire perpendicular to the hull while you're TURNING and NOT thrusting forward. The ship gains lateral drift — useful for dodging incoming fire without breaking your aim or your forward motion. Pair with Tracking Laser for a circle-strafe attack pattern.",
)

# ----- ENERGY/SPECIAL MODS -----

MOD_ENERGY_CELL = Module(
    id="mod_energy_cell",
    name="Capacitor Surge",
    slot="drive",
    tier=2,
    cost_credits=210,
    cost_resources={"ENERGY": 4},
    deltas={"capacitor_surge": 1.0},
    description="When your energy reservoir hits MAX, the next primary-fire volley is SURGED — every bolt deals 3× damage. The visual: bolts glow white-hot on the surge shot. Encourages a rhythm of restrained fire while charging, then one decisive overcharge release. Goes well with any pattern; lethal on Lance Coil.",
)

MOD_POWER_REGENERATOR = Module(
    id="mod_power_regenerator",
    name="Cross-Wired Capacitors",
    slot="drive",
    tier=2,
    cost_credits=230,
    cost_resources={"ENERGY": 5},
    deltas={"cross_wired_ratio": 1.0},
    description="The primary-fire capacitor is cross-wired to the shield projector. Every shot you fire ALSO restores shield (1 shield per energy spent on the shot). Pair with high-rate weapons (Twin Beam, Gatling) for a self-sustaining defensive loop. Doesn't help if you have no shield to recharge.",
)

# ----- SPECIAL-SWAP MODS (field slot — they swap the special ability) -----

MOD_PHASE_SKIP_MOD = Module(
    id="mod_phase_skip",
    name="Phase Skip Module",
    slot="field",
    tier=2,
    cost_credits=280,
    cost_resources={"ENERGY": 5, "BIO": 3},
    deltas={},
    special_ability_override="phase_skip",
    description="Persuader-pattern dimensional skip array. REPLACES the Scout's inertia halt with a directional phase skip: short blink forward, collision-immune, dodges through planets and projectiles. Trades the precision of standstill-dodge for raw mobility.",
)

MOD_CHAFF_SPRAY_MOD = Module(
    id="mod_chaff_spray",
    name="Chaff Spray Module",
    slot="field",
    tier=2,
    cost_credits=240,
    cost_resources={"USEFUL": 5},
    deltas={},
    special_ability_override="chaff_spray",
    description="Defender-pattern chaff-puff dispenser. REPLACES the Scout's inertia halt with a 12-puff chaff cone in front. Enemy projectiles passing through slow to a crawl. Area-denial special — useful vs scatter, lance, and tracking weapons.",
)


# ---------------------------------------------------------------------------
# Schematic-gated modules — unlocked at Mh-Lai by consuming a schematic
# at the Vault. Each module's `unlock_schematic` matches a Schematic.id
# from `content/schematics.py`. The schematic is the *unlock*; the
# module still costs credits + minerals at the Customization counter.
# Per `references/lore/economy-and-trade-loops.md` §Schematic Loop.
# ---------------------------------------------------------------------------

FURLING_COIL_LANCE = Module(
    id="furling_coil_lance",
    name="Furling Coil Lance",
    slot="weapon",
    tier=2,
    cost_credits=280,
    cost_resources={"USEFUL": 6, "ENERGY": 4},
    deltas={"lance_charge_max_dmg": 1.0},
    primary_pattern_override="lance",
    unlock_schematic="schematic_furling_coil_lance",
    description="Twin-bore Furling coil lance — fires the standard lance pattern FORWARD as well as a mirrored lance bolt REARWARD on every trigger pull. The Scout becomes an in-line cannon: it can defend its rear while attacking forward. Wider arena coverage; risky if you're flying near friendly ships. Melnorme-broker origin per archive notes.",
)

DIMENSIONAL_ARMOR = Module(
    id="dimensional_armor",
    name="Dimensional Armor",
    slot="hull",
    tier=2,
    cost_credits=280,
    cost_resources={"USEFUL": 6, "ENERGY": 5},
    deltas={"phase_shift_hull_threshold": 0.25},
    unlock_schematic="schematic_dimensional_armor",
    description="Persuader-era prototype armor with a dimensional-substrate sub-layer. The first time your hull would drop below 25% in a fight, the substrate engages: 1.5 seconds of FULL invulnerability while the dimensional bleed re-anchors. Once per fight. Recovered from a Persuader wreck near the Orz Rift.",
)

PULSE_CANNON = Module(
    id="pulse_cannon",
    name="Pulse Cannon",
    slot="weapon",
    tier=1,
    cost_credits=180,
    cost_resources={"USEFUL": 4, "ENERGY": 2},
    deltas={"pulse_stack_bonus": 1.5},
    unlock_schematic="schematic_pulse_cannon",
    description="Pressure-build cannon — each consecutive hit on the SAME target ramps the next shot's damage by +1.5. Stacks indefinitely; resets only when the target dies or you switch targets. Rewards sticking with one opponent through a brawl. Furling-era survey-lifter spare-copy origin.",
)

MMRNMHRM_REINFORCED_PLATING = Module(
    id="mmrnmhrm_reinforced_plating",
    name="Mmrnmhrm Reinforced Plating",
    slot="hull",
    tier=1,
    cost_credits=220,
    cost_resources={"COMMON": 12, "USEFUL": 5},
    deltas={"energy_absorb_frac": 0.70},
    unlock_schematic="schematic_mmrnmhrm_reinforced_plating",
    description="Patchwork-alloy plating from the First-Makers' design book. Energy-weapon damage (beams, lasers, scatter, lance, tracking, gatling) is reduced 70%. KINETIC damage (missiles, plasma, water, blades, ramming) is normal. Canonical First-Maker: *it was the engagement that was wrong, not the metal.* Gifted by archive consensus at Ossuary.",
)

ARILOU_PHASE_DAMPENER = Module(
    id="arilou_phase_dampener",
    name="Arilou Phase Dampener",
    slot="field",
    tier=2,
    cost_credits=260,
    cost_resources={"USEFUL": 5, "BIO": 4},
    deltas={"hit_negate_interval": 2.0},
    unlock_schematic="schematic_arilou_phase_dampener",
    description="Fractional dimensional displacement on incoming hits. The FIRST damaging hit every 2 seconds is completely negated — the bolt arrives just slightly out of phase with your hull. Sustained DPS still bites; alpha-strikes pop off harmlessly. Subtle, like its source. Slipped into the manifest by Sage Lwen-Olou.",
)


# ---------------------------------------------------------------------------
# Master registry
# ---------------------------------------------------------------------------

MODULES: dict[str, Module] = {
    m.id: m for m in (
        # ----- Pillar: Sensors (tier-0 quest rewards) -----
        SCANNER_MK3, HYPERSPACE_ECHO_SENSOR,
        # ----- Pillar: Crew (tier-0 quest rewards) -----
        MANTLE_RESONANCE_BIO_ARCHITECT,
        # ----- Pillar: Artifacts (slotted; flag-side-effect quest items) -----
        RAINBOW_RESONATOR,
        # ----- Pillar: Ship modules (tier-1 purchasables) -----
        # Catalog order is also the customization-list display order.
        # Keep CARGO_POD_PLUS_50 at index-3 of the purchasable list so
        # walk_upgrade_loop's menu-index nav remains stable. New tier-1
        # modules go AFTER it.
        BACKUP_CAPACITOR, SHIELD_BOOSTER_I, BEAM_MOD_I, CARGO_POD_PLUS_50,
        # ----- Pillar: Sensors (tier-1+ purchasable) -----
        LR_MINERAL_SCANNER,
        # ----- Pillar: Ship modules (tier-2) -----
        QUASI_DRIVE_COMPACT, SA_MATRA_LANCE_REPLICA,
        # ----- Pillar: Faction trade (Melnorme) -----
        MELNORME_PLASMA_LANCE, MELNORME_PATTERN_SENSOR,
        # ----- Pillar: Species quest-reward modules -----
        LEMMKIN_PATTERN_DATABASE,
        # 5 new species quest-reward sensors (2026-05-18 expansion).
        # All locked=True; granted via game.uninstalled_modules on
        # quest-completion. See the species-quest dispatch entries
        # in HANDOFF for the grant points.
        KARAVEM_AERIAL_SENTRY, ARILOU_PORTAL_PATHFINDER,
        COUNCIL_MIGRATION_BEACON, STELLOTH_ARTIFACT_LOCATOR,
        TAALO_STRATA_TOMOGRAPHY,
        # Recruitment-quest reward (Trader's Manifest quest, Beat 5).
        # Stays locked=True; granted via game.uninstalled_modules at the
        # recruitment commitment moment.
        MELNORME_TRADE_NETWORK_SENSOR,
        # 5 new purchasable / Melnorme-trade sensors (2026-05-18).
        MINERAL_SPECTROMETER, SCHEMATIC_RESONANCE_READER,
        WRECK_PATTERN_READER, DANGER_ZONE_FORECASTER,
        MELNORME_STELLAR_CLASS_READER,
        # ----- Pillar: Crew (active — shop-buyable named roles) -----
        CREW_ARCHIVIST, CREW_WARDEN, CREW_TUNNELER,
        # ----- Pillar: Crew (LOCKED — granted by recruitment side-quests;
        # see references/lore/crew-recruitment-quests.md for the 5 quests.
        # Each module's UNLOCKED_BY comment names the gate flag.) -----
        CREW_PILOT, CREW_WEAPONS_OFFICER, CREW_ENGINEER, CREW_MEDIC, CREW_NAVIGATOR,
        # ----- Pillar: Sensor stubs wired 2026-05-18 — render/scene layer
        # now reads each sensor's deltas via effective_stat. -----
        BIO_SENSE_SCANNER, ENEMY_SCANNER, ANOMALY_SCANNER, HAZARD_SCANNER,
        # ----- Pillar: Weapon-mod stubs (LOCKED — awaiting combat-layer hooks) -----
        WEAPON_MOD_ACCURACY, WEAPON_MOD_RELOAD,
        # ----- Pillar: Combat mods (2026-05-18 — 24 ways to modify the
        # Scout in combat). Pattern-overriding weapon mods, stat-tuning
        # weapon mods, defensive field mods, hull mods, drive mods,
        # special-swap mods. -----
        # Pattern-replacing weapon mods (8)
        MOD_TWIN_BEAM, MOD_LANCE_COIL, MOD_SCATTER_ARRAY, MOD_PULSE_CANNON,
        MOD_HOMING_MORTAR, MOD_BURST_CANNON, MOD_TRACKING_LASER, MOD_LAWNMOWER_DISC,
        # Stat-tuning weapon mods (2)
        MOD_BEAM_MOD_II, MOD_ENGINE_DISRUPTOR,
        # Field/shield mods (4)
        MOD_SHIELD_CAPACITOR, MOD_SHIELD_CATALYST, MOD_CRYSTALLINE_ARMOR, MOD_REACTIVE_PLATING,
        # Hull mods (3)
        MOD_HULL_REINFORCEMENT, MOD_REPAIR_DRONE, MOD_ABLATIVE_COATING,
        # Drive/mobility mods (3)
        MOD_THRUSTER_BOOST, MOD_MANEUVERING_JETS, MOD_GYRO_STABILIZER,
        # Energy mods (2)
        MOD_ENERGY_CELL, MOD_POWER_REGENERATOR,
        # Special-swap mods (2)
        MOD_PHASE_SKIP_MOD, MOD_CHAFF_SPRAY_MOD,
        # ----- Schematic-gated modules (unlocked via Vault) -----
        # Hidden from shop until the player consumes the matching
        # schematic at Mh-Lai. Catalog-order-stable — placed AFTER
        # special-swap mods so walk_upgrade_loop's menu-index nav
        # is not disturbed.
        FURLING_COIL_LANCE, DIMENSIONAL_ARMOR, PULSE_CANNON,
        MMRNMHRM_REINFORCED_PLATING, ARILOU_PHASE_DAMPENER,
    )
}


# Pricing for mineral sales — Trade scene reads this
MINERAL_PRICES: dict[str, int] = {
    "COMMON": 1,
    "USEFUL": 4,
    "BIO": 6,
    "ENERGY": 12,
}


def purchasable_modules(game) -> list[Module]:
    """Return tier-1 + tier-2 modules visible in the customization shop.

    Locked modules are filtered. Modules with `unlock_schematic` set
    are hidden until the player has consumed the matching schematic at
    the Schematic Vault (i.e. `unlock_schematic in
    game.consumed_schematics`).
    """
    consumed = getattr(game, "consumed_schematics", None) or set()
    out: list[Module] = []
    for m in MODULES.values():
        if m.tier == 0:
            continue   # quest rewards aren't shop-buyable
        if m.locked:
            continue
        if m.unlock_schematic is not None and m.unlock_schematic not in consumed:
            continue   # gated by a schematic the player hasn't converted
        out.append(m)
    return out


def crew_slot_compatible(module: Module, slot: str) -> bool:
    """2026-05-18 refactor: slot-type constraints DROPPED. Any module
    can be installed into any of the 12 generic slots. Function kept
    for backward compatibility with existing call sites; always returns
    True now. Module.slot remains as a UI category label only.
    """
    return True


def is_module_installed(game, module_id: str) -> bool:
    """True iff ANY slot of ship_modules holds the given module id.
    Used by content sites that need to know whether a specific module
    is on the ship — previously they queried a single named slot
    (e.g. `ship_modules.get("field") == "rainbow_resonator"`), which
    breaks under the 12-generic-slot model where the same module can
    sit in any slot (or multiple).
    """
    mods = getattr(game, "ship_modules", None) or {}
    return any(mid == module_id for mid in mods.values())


def count_module_installed(game, module_id: str) -> int:
    """Return how many slots hold the given module id. Used by stacking-
    aware behaviors that care about the multiplier (most do not — the
    delta sum in effective_stat already handles stacking automatically).
    """
    mods = getattr(game, "ship_modules", None) or {}
    return sum(1 for mid in mods.values() if mid == module_id)
