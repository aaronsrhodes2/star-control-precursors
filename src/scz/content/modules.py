"""Ship module catalog — installable upgrades for the Furling Scout.

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


# Canonical module slot names — matches Game.ship_modules keys
SLOTS: tuple[str, ...] = (
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


# ---------------------------------------------------------------------------
# Quest-reward modules (tier 0, zero cost, granted on quest completion)
# ---------------------------------------------------------------------------

SCANNER_MK3 = Module(
    id="scanner_mk3",
    name="Stellar Field Scanner Mk III",
    slot="sensor",
    tier=0,
    cost_credits=0,
    deltas={"sensor_range": 1.5},
    description="Furlmart pickup — upgrades hyperspace sensor range 1.5x. The Mk II is half-blind.",
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
    # All deltas are ADDITIVE — base + sum(installed_module.deltas)
    # tractor_radius base is 0.030 (planet/scene.py), bonus +0.015 = 50% bigger
    deltas={"tractor_radius_bonus": 0.015, "lander_replication_bonus": 0.4},
    description="Mycon gift — tractor beam +50% radius, landers replicate 40% faster.",
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

# ---------------------------------------------------------------------------
# Tier-1 modules (purchasable from the start)
# ---------------------------------------------------------------------------

FUEL_TANK_PLUS_50 = Module(
    id="fuel_tank_plus_50",
    name="Fuel Tank +50",
    slot="drive",
    tier=1,
    cost_credits=60,
    deltas={"fuel_max": 50},
    description="Extra antimatter capacity. Useful for long hops.",
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
    cost_credits=0,
    deltas={"primary_damage": 30, "primary_rate": 0.5},
    description="Defender-faction prototype lance. Locked — requires Defender quest progress.",
    locked=True,
)

MELNORME_PLASMA_LANCE = Module(
    id="melnorme_plasma_lance",
    name="Melnorme Plasma Lance",
    slot="weapon",
    tier=0,
    cost_credits=0,
    deltas={"primary_damage": 6, "primary_rate": 1.2},
    description="Melnorme-exclusive — ionization-coil weapon, harder hits and slightly faster cadence. Bought with BIO-cargo at any super-giant trading post.",
)

MELNORME_PATTERN_SENSOR = Module(
    id="melnorme_pattern_sensor",
    name="Melnorme Pattern Sensor",
    slot="sensor",
    tier=0,
    cost_credits=0,
    deltas={"other_detection_range": 1.5, "dialog_context_depth": 1.3},
    description="Melnorme-exclusive — ionization-pattern analyzer. Boosts Others detection and deepens dialog context. Bought with BIO-cargo.",
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
    deltas={"dialog_context_depth": 1.5},
    description="Hand-trained Archivist — pulls deeper lore context into dialog encounters.",
)

CREW_WARDEN = Module(
    id="crew_warden",
    name="Crew: Furling Warden",
    slot="crew_2",
    tier=1,
    cost_credits=140,
    cost_resources={"USEFUL": 4},
    deltas={"auto_fight_skill": 1.3},
    description="Defender-trained Warden — sharper auto-fight combat AI when offloading combat.",
)

CREW_TUNNELER = Module(
    id="crew_tunneler",
    name="Crew: Furling Tunneler",
    slot="crew_2",
    tier=1,
    cost_credits=120,
    cost_resources={"ENERGY": 2},
    deltas={"quasispace_portal_visible": 1.0},
    description="Quasi-Space-trained Tunneler — more QS portals visible on the map.",
)


# ---------------------------------------------------------------------------
# Master registry
# ---------------------------------------------------------------------------

MODULES: dict[str, Module] = {
    m.id: m for m in (
        SCANNER_MK3, HYPERSPACE_ECHO_SENSOR, MANTLE_RESONANCE_BIO_ARCHITECT,
        RAINBOW_RESONATOR,
        FUEL_TANK_PLUS_50, SHIELD_BOOSTER_I, BEAM_MOD_I, CARGO_POD_PLUS_50,
        QUASI_DRIVE_COMPACT, SA_MATRA_LANCE_REPLICA,
        MELNORME_PLASMA_LANCE, MELNORME_PATTERN_SENSOR,
        CREW_ARCHIVIST, CREW_WARDEN, CREW_TUNNELER,
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

    Locked modules are filtered. Tier-2 modules whose unlock flag isn't
    set yet are also filtered.
    """
    out: list[Module] = []
    for m in MODULES.values():
        if m.tier == 0:
            continue   # quest rewards aren't shop-buyable
        if m.locked:
            continue
        out.append(m)
    return out


def crew_slot_compatible(module: Module, slot: str) -> bool:
    """Crew modules can slot into either crew_1 or crew_2; other modules
    must match their declared slot exactly.
    """
    if module.slot in ("crew_1", "crew_2"):
        return slot in ("crew_1", "crew_2")
    return module.slot == slot
