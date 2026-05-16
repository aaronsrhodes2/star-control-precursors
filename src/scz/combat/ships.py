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
    ai_style: str = "brawler"


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
    primary_damage=8, primary_energy=4, primary_rate=4.0,
    primary_range=400, primary_speed=2400,  # near-hitscan beam
    primary_color=(255, 220, 140),
    hull_color=(200, 200, 220), accent_color=(160, 220, 255),
    silhouette="scout", ai_style="circler",
)

PERSUADER_VESSEL = ShipClass(
    id="persuader_vessel",
    name="Persuader Vessel",
    side=SIDE_PRECURSOR,
    points=110,
    hull_max=80, shield_max=90, shield_regen=14.0, shield_regen_delay=2.0,
    top_speed=200.0, acceleration=240.0, turn_rate=2.8, mass=90,
    energy_max=80, energy_regen=8.0,
    primary_damage=5, primary_energy=3, primary_rate=3.0,
    primary_range=360, primary_speed=2200,
    primary_color=(220, 180, 100),
    hull_color=(220, 180, 100), accent_color=(255, 230, 180),
    silhouette="scout", ai_style="circler",
)

ARILOU_SKIFF = ShipClass(
    id="arilou_skiff",
    name="Arilou Skiff",
    side=SIDE_PRECURSOR,
    points=120,
    hull_max=60, shield_max=0, shield_regen=0.0, shield_regen_delay=0.0,
    top_speed=320.0, acceleration=420.0, turn_rate=5.5, mass=55,
    energy_max=100, energy_regen=10.0,
    primary_damage=4, primary_energy=2, primary_rate=6.0,
    primary_range=300, primary_speed=700,
    primary_color=(140, 240, 210),
    hull_color=(140, 240, 210), accent_color=(200, 255, 230),
    silhouette="skiff", ai_style="kiter",
)

ANDROSYNTH_CRUISER = ShipClass(
    id="androsynth_cruiser",
    name="Androsynth Refugee Cruiser",
    side=SIDE_PRECURSOR,
    points=135,
    hull_max=130, shield_max=0, shield_regen=0.0, shield_regen_delay=0.0,
    top_speed=190.0, acceleration=220.0, turn_rate=2.2, mass=130,
    energy_max=70, energy_regen=6.0,
    primary_damage=10, primary_energy=5, primary_rate=2.0,
    primary_range=500, primary_speed=1200,
    primary_color=(220, 130, 220),
    hull_color=(180, 100, 200), accent_color=(240, 200, 240),
    silhouette="cruiser", ai_style="kiter",
)

CLEANSER_CRUISER = ShipClass(
    id="cleanser_cruiser",
    name="Cleanser Furling Cruiser",
    side=SIDE_SPECIAL,   # nominally Precursor; faction-extreme
    points=175,
    hull_max=150, shield_max=100, shield_regen=10.0, shield_regen_delay=3.0,
    top_speed=175.0, acceleration=180.0, turn_rate=2.0, mass=150,
    energy_max=80, energy_regen=6.0,
    primary_damage=11, primary_energy=5, primary_rate=3.0,
    primary_range=480, primary_speed=2400,
    primary_color=(220, 220, 255),
    hull_color=(230, 230, 240), accent_color=(180, 160, 240),
    silhouette="heavy", ai_style="brawler",
)

# ---------------------------------------------------------------------------
# Homesteader side (Stay) — 5 ships in the slice
# ---------------------------------------------------------------------------

DEFENDER_VESSEL = ShipClass(
    id="defender_vessel",
    name="Defender Vessel",
    side=SIDE_HOMESTEADER,
    points=170,
    hull_max=180, shield_max=60, shield_regen=8.0, shield_regen_delay=3.0,
    top_speed=150.0, acceleration=130.0, turn_rate=1.6, mass=180,
    energy_max=90, energy_regen=5.0,
    primary_damage=12, primary_energy=6, primary_rate=2.0,
    primary_range=450, primary_speed=2400,
    primary_color=(255, 200, 100),
    hull_color=(200, 180, 120), accent_color=(255, 230, 160),
    silhouette="heavy", ai_style="kiter",
)

MMRNMHRM_SENTINEL = ShipClass(
    id="mmrnmhrm_sentinel",
    name="Mmrnmhrm Sentinel",
    side=SIDE_HOMESTEADER,
    points=155,
    hull_max=150, shield_max=0, shield_regen=0.0, shield_regen_delay=0.0,
    top_speed=180.0, acceleration=200.0, turn_rate=2.4, mass=140,
    energy_max=70, energy_regen=7.0,
    primary_damage=6, primary_energy=3, primary_rate=5.0,
    primary_range=380, primary_speed=900,
    primary_color=(220, 220, 240),
    hull_color=(220, 220, 240), accent_color=(255, 255, 255),
    silhouette="sentinel", ai_style="circler",
)

PROTO_UR_QUAN = ShipClass(
    id="proto_ur_quan",
    name="Proto-Ur-Quan Warship",
    side=SIDE_HOMESTEADER,
    points=145,
    hull_max=170, shield_max=0, shield_regen=0.0, shield_regen_delay=0.0,
    top_speed=170.0, acceleration=160.0, turn_rate=1.9, mass=170,
    energy_max=50, energy_regen=4.0,
    primary_damage=14, primary_energy=4, primary_rate=1.5,
    primary_range=200, primary_speed=600,    # short-range, slow projectile
    primary_color=(110, 140, 220),
    hull_color=(70, 90, 160), accent_color=(140, 170, 230),
    silhouette="warship", ai_style="brawler",
)

PROTO_QOR_AH = ShipClass(
    id="proto_qor_ah",
    name="Proto-Qor-Ah Marauder",
    side=SIDE_HOMESTEADER,
    points=95,
    hull_max=60, shield_max=0, shield_regen=0.0, shield_regen_delay=0.0,
    top_speed=280.0, acceleration=380.0, turn_rate=4.5, mass=70,
    energy_max=40, energy_regen=5.0,
    primary_damage=4, primary_energy=2, primary_rate=8.0,   # rapid close-range
    primary_range=120, primary_speed=900,
    primary_color=(240, 230, 200),
    hull_color=(240, 230, 200), accent_color=(40, 30, 20),
    silhouette="blade", ai_style="brawler",
)


# Master registry — used by the super-melee picker
SHIPS: dict[str, ShipClass] = {
    s.id: s for s in (
        FURLING_SCOUT, PERSUADER_VESSEL, ARILOU_SKIFF, ANDROSYNTH_CRUISER,
        CLEANSER_CRUISER,
        DEFENDER_VESSEL, MMRNMHRM_SENTINEL, PROTO_UR_QUAN, PROTO_QOR_AH,
    )
}


def precursor_ships() -> list[ShipClass]:
    return [s for s in SHIPS.values() if s.side == SIDE_PRECURSOR]


def homesteader_ships() -> list[ShipClass]:
    return [s for s in SHIPS.values() if s.side == SIDE_HOMESTEADER]
