"""Species Domains — who owns which territory in the 10000x10000
hyperspace.

The fixed `hyperspace_encounters.ENCOUNTERS` registry covers
story-critical scripted encounters (Cleanser patrol, salvage wrecks,
the Cleanser climax). What that registry does NOT cover: the rest of
the galaxy belongs to *somebody*, and crossing into their space should
produce an occasional patrol encounter.

This module fills that gap. A `SpeciesDomain` is a circle on the map
with:

- a faction owner (Furling Hearth, Cleanser Approach, etc.)
- a canonical ship class id for patrol spawning
- a target encounter density (number of patrol EncounterPoints to
  spawn within the domain on hyperspace scene-entry)
- a gate flag (optional — Cleanser Approach patrols only spawn after
  `tutorial_complete`)
- a render color and a label

**Anchor rule**: domains *generally* center on the owning species'
canonical home planet (Mh-Lai for Furlings, the Slylandro homeworld
for Slylandro, Mycon Biot Hive for Mycon, etc). Exceptions are
documented per-domain — Cleansers don't have a homeworld of their
own (they're a Furling sub-faction), so the Cleanser Approach is
anchored on the fleet's staging vector toward Mh-Lai rather than a
homeworld.

**Color rule**: each domain's color matches the canonical warp-pod
rim color from `species_visual.SPECIES_WARP_POD`. Players learn the
palette by play: a violet ring on the map means Melnorme territory
the same way a violet warp pod converging in hyperspace means a
Melnorme trader. Single source of truth — if a species' canon color
changes, it changes in `species_visual.py` and propagates here.

The hyperspace scene renders domain boundaries as faint translucent
rings *before* stars (so stars sit on top), and consults this registry
in `_maybe_spawn_encounters` to drop per-domain patrols at deterministic
positions distributed by golden-angle around each domain's center.

Patrols retire via per-domain per-index flags: meeting domain D's
patrol #N sets `patrol_<D>_<N>_met` and removes the encounter from
respawning. This keeps the design forgiving (the player can clear a
region by working through it) while keeping the rest of the galaxy
populated.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import TYPE_CHECKING

from scz.content.species_visual import SPECIES_WARP_POD

if TYPE_CHECKING:
    from scz.engine.game import Game


def _rim(species_id: str) -> tuple[int, int, int]:
    """Return the canonical warp-pod rim color for a species, used as
    the domain boundary color. Falls back to neutral gray if the
    species isn't in the palette yet."""
    entry = SPECIES_WARP_POD.get(species_id)
    if entry is None:
        return (200, 200, 220)
    return entry["rim"]


@dataclass(frozen=True)
class SpeciesDomain:
    """One region of hyperspace owned by a species or faction.

    Fields:

    - `id`: stable key, used as the prefix for per-patrol retire flags
      (`patrol_<id>_<N>_met`). Keep ASCII, no spaces.
    - `name`: human-readable label shown in the hyperspace HUD when the
      player ship is inside the domain.
    - `center_x, center_y`: universe-space coords of the domain center.
      Anchored on the canonical homeworld where one exists.
    - `radius`: universe-space radius. Domains may overlap; the
      closest-center wins for HUD readout via `domain_at`.
    - `color`: RGB tuple for the boundary ring render. Sourced from
      `species_visual.SPECIES_WARP_POD[species_id]["rim"]` so the
      domain boundary matches the species' ship-and-warp-pod identity.
    - `ship_class_id`: canonical name from `scz.combat.ships` used to
      look up the ShipClass for patrol combat. None means "ambient
      domain — render boundary, no patrol spawning."
    - `encounter_density`: how many patrol EncounterPoints to spawn
      within this domain on scene entry. 0 = ambient domain.
    - `requires_flag`: optional flag name that must be truthy for any
      patrols to spawn (e.g. Cleanser Approach gated on
      `tutorial_complete`).
    - `not_flag`: optional flag name that must be falsy for spawning
      (used to fully retire a domain post-event).
    - `friendly`: True for trade/dialog domains (Melnorme Network,
      Furling Hearth); False for combat domains (Cleanser, Mycon).
      The patrol trigger callback consults this to choose dialog vs.
      combat scene.
    """
    id: str
    name: str
    center_x: float
    center_y: float
    radius: float
    color: tuple[int, int, int]
    ship_class_id: str | None = None
    encounter_density: int = 0
    requires_flag: str | None = None
    not_flag: str | None = None
    friendly: bool = False


# Domain registry — centered on canonical homeworld coordinates per the
# `defined_name` entries in `src/scz/content/universe/stars.json` (plus
# synthetic anchors for Mh-Lai and Arilou Outpost from
# `home_system.HOME_X/Y` and `arilou_outpost.OUTPOST_X/Y`).
#
# Reference table (authoring snapshot):
#   Mh-Lai             (1900, 1600)   home_system.HOME_X/Y
#   Arilou Outpost     (3500, 2400)   arilou_outpost.OUTPOST_X/Y
#   SLYLANDRO          ( 276, 9810)   stars.json defined_name
#   MYCON_BIOT_HIVE    (6162, 2263)   stars.json defined_name
#   MELNORME (centroid)(4375, 4701)   9 super-giant anchors averaged
# Dnyarri are intentionally absent — they have no territory because
# they have no fleet (mind-controllers ride hijacked host ships).
DOMAINS: tuple[SpeciesDomain, ...] = (
    SpeciesDomain(
        id="furling_hearth",
        name="Furling Hearth",
        # Mh-Lai — the player's home and Furling political center
        center_x=1900.0, center_y=1600.0,
        radius=1100.0,
        # Furling red — matches FURLING_SCOUT warp pod
        color=_rim("FURLING_SCOUT"),
        # No patrols inside the Hearth — it's home turf
        ship_class_id=None,
        encounter_density=0,
        friendly=True,
    ),
    SpeciesDomain(
        id="cleanser_approach",
        name="Cleanser Approach",
        # NON-homeworld domain: Cleansers are a Furling sub-faction
        # with no separate homeworld. This region marks the fleet
        # staging vector NW of Mh-Lai where Cleanser cruisers stage
        # for the Approach to the Steward's cluster. Overlaps the
        # fixed cleanser_patrol_alpha pos at (1500, 900).
        center_x=900.0, center_y=600.0,
        radius=1400.0,
        # Cleanser orange — matches FURLING_CLEANSER warp pod
        color=_rim("FURLING_CLEANSER"),
        ship_class_id="CLEANSER_CRUISER",
        encounter_density=2,
        requires_flag="tutorial_complete",
        not_flag="cleanser_climax_resolved",
        friendly=False,
    ),
    SpeciesDomain(
        id="slylandro_sphere",
        name="Slylandro Sphere",
        # SLYLANDRO homeworld — gas-giant orbital habitat
        center_x=276.0, center_y=9810.0,
        radius=1500.0,
        # Slylandro pale gold — matches SLYLANDRO warp pod
        color=_rim("SLYLANDRO"),
        # No combat — Slylandro side with the Migration
        ship_class_id=None,
        encounter_density=0,
        friendly=True,
    ),
    SpeciesDomain(
        id="mycon_whisper",
        name="Mycon Whisper",
        # MYCON_BIOT_HIVE — the Mycon's autonomous spore center
        center_x=6162.0, center_y=2263.0,
        radius=1300.0,
        # Mycon chartreuse — matches MYCON_BIOT warp pod
        color=_rim("MYCON_BIOT"),
        ship_class_id="MYCON_PODSHIP",
        encounter_density=2,
        # Mycon biots wander whether the player has tripped any flags
        # or not — they're the slice's autonomous threat
        friendly=False,
    ),
    SpeciesDomain(
        id="melnorme_network",
        name="Melnorme Trade Network",
        # NON-homeworld-pointlike domain: Melnorme orbit *multiple*
        # super-giants. Center is the centroid of the 9 MELNORME_PROTO
        # anchors in stars.json. Wide radius covers the trade band.
        center_x=4375.0, center_y=4701.0,
        radius=2400.0,
        # Melnorme plasma-violet — matches MELNORME warp pod
        color=_rim("MELNORME"),
        ship_class_id="MELNORME_TRADER",
        encounter_density=1,
        # Melnorme are itinerant; their patrols are trade-route
        # solicitations, not combat
        friendly=True,
    ),
    # NOTE: No Dnyarri domain. Per canon, Dnyarri are mind-controllers
    # without their own ships — a Dnyarri-piloted ship is whichever
    # vessel they hijacked, *visually disguised as* its host species
    # (Cleanser warp pod, Mycon pod, Slylandro envelope, etc.). They
    # have no territory because they have no fleet — they have
    # passengers. See `references/lore/dnyarri-disguised-encounter.md`
    # for the disguised-encounter mechanic; the pre-sentient homeworld
    # survey at Beta Orionis (handled by `_arrive_dnyarri_primitive`)
    # is unrelated to the disguised encounter and lives in
    # `star_arrival.py`, not here.
    SpeciesDomain(
        id="arilou_sanctuary",
        name="Arilou Sanctuary",
        # Arilou Outpost — the Sage's seat, synthetic per
        # arilou_outpost.OUTPOST_X/Y. Aligned-with-Precursors species;
        # ambient-friendly (the player visits for the QS portal gift,
        # not for patrol encounters).
        center_x=3500.0, center_y=2400.0,
        radius=1000.0,
        # Arilou mint — matches ARILOU warp pod
        color=_rim("ARILOU"),
        ship_class_id=None,
        encounter_density=0,
        friendly=True,
    ),
)


def domain_at(x: float, y: float) -> SpeciesDomain | None:
    """Return the domain containing point (x, y), or None for Wild
    space. When multiple domains overlap, the one whose center is
    closest wins — that biases the readout toward the species the
    player is *most-in* rather than the species they're *barely-in*.
    """
    best: SpeciesDomain | None = None
    best_d = float("inf")
    for d in DOMAINS:
        dx = x - d.center_x
        dy = y - d.center_y
        dist = math.hypot(dx, dy)
        if dist > d.radius:
            continue
        if dist < best_d:
            best_d = dist
            best = d
    return best


def patrol_positions(domain: SpeciesDomain) -> list[tuple[float, float, int]]:
    """Return `(x, y, index)` positions for this domain's patrols.

    Spawns at golden-angle offsets from the center, at 0.55 * radius
    out. Deterministic per-domain so walk-tests can predict positions;
    not random per-scene-entry — once a patrol is met it retires via
    its index flag, and a fresh scene entry never resurrects it.
    """
    if domain.encounter_density <= 0:
        return []
    GOLDEN_ANGLE = math.pi * (3.0 - math.sqrt(5.0))
    R = domain.radius * 0.55
    out = []
    for i in range(domain.encounter_density):
        a = i * GOLDEN_ANGLE
        x = domain.center_x + R * math.cos(a)
        y = domain.center_y + R * math.sin(a)
        out.append((x, y, i))
    return out


def active_patrols(game: "Game") -> list[tuple[SpeciesDomain, float, float, int]]:
    """Enumerate `(domain, x, y, index)` for every patrol that should
    spawn given current game state.

    A patrol spawns when:
    - its domain has `encounter_density > 0`
    - the domain's `requires_flag` is truthy or unset
    - the domain's `not_flag` is falsy or unset
    - the specific patrol's `patrol_<id>_<index>_met` flag is falsy

    Caller (HyperspaceScene._maybe_spawn_encounters) decides whether
    to actually materialize an EncounterPoint for each entry —
    typically yes, unless an EncounterPoint with the same label
    already exists.
    """
    flags = game.flags
    out: list[tuple[SpeciesDomain, float, float, int]] = []
    for d in DOMAINS:
        if d.encounter_density <= 0:
            continue
        if d.requires_flag is not None and not flags.get(d.requires_flag):
            continue
        if d.not_flag is not None and flags.get(d.not_flag):
            continue
        for x, y, i in patrol_positions(d):
            met_flag = f"patrol_{d.id}_{i}_met"
            if flags.get(met_flag):
                continue
            out.append((d, x, y, i))
    return out
