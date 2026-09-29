"""Allied Species Ships — buyable hulls that grow `game.fleet`.

Canon source: `references/lore/economy-and-trade-loops.md`
"Allied Species Ships" + HANDOFF_design_chat.md entry "Allied species
ship registry + Mh-Lai purchase UI" (2026-05-17).

The slice's combat is now SC2-style hot-swap fleet (`FleetCombatScene`,
2026-05-18). Allied ships are the primary lever for growing the
player's fleet at Mh-Lai. Each entry maps to an existing combat
`ShipClass` from `src/scz/combat/ships.py`; purchase appends the
class id to `game.fleet`.

**Unlock gates**: each ship is gated on an alliance flag (set by
the relevant species quest's positive-resolution side-effect — e.g.
`mmrnmhrm_cognition` set means the Mmrnmhrm welcome a Sentinel to
travel with the Steward). The ships are also gated on **available
credits**, which the player accumulates by selling cargo at Trade.

**Mh-Lai only**: per economy canon the Shipyard exists at Mh-Lai
Station alone. Purchase from the shipyard sub-scene; no remote
purchase path. (The Mh-Lai install-gate rule for tier-1+ modules
mirrors this.)

**Slice scope**: 4 ships ship in this MVP (Arilou Skiff, Androsynth
Cruiser, Mmrnmhrm Sentinel, Thinn Blade). The Slylandro Lift and the
Burvixese Skipper require new `ShipClass` entries from the Combat
Mechanics chat and are deferred — entries are present in this
registry but marked `unavailable=True` so the UI greys them out
until Combat Mechanics ships the classes.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class AlliedShipEntry:
    """One buyable allied hull. The `ship_class_id` matches a class
    in `src/scz/combat/ships.py`; purchase appends it to `game.fleet`.

    Fields:

    - `ship_class_id`: the canonical id (e.g. "ARILOU_SKIFF") used by
      both the combat catalog and `game.fleet`
    - `display_name`: human-readable hull name; rendered in the
      shipyard list. Distinct from the *instance* names produced by
      `species_names.py` — this is the class designation
    - `cost_credits`: purchase price; the player must have at least
      this in `game.credits`
    - `unlock_flag`: game-flag name; until True, the entry is locked
      and shown greyed (or hidden, per UI policy)
    - `species_id`: for warp-pod palette + naming-conventions lookup
    - `unavailable`: True when the entry is canonically valid but the
      ShipClass doesn't yet exist in Combat Mechanics' catalog. The UI
      shows these as "[under construction]" so the player understands
      they're forthcoming
    - `blurb`: 1-2 sentence in-fiction description of why this hull is
      worth bringing along
    """
    ship_class_id: str
    display_name: str
    cost_credits: int
    unlock_flag: str
    species_id: str
    unavailable: bool = False
    blurb: str = ""


# Slice catalog. Order is canonical priority — Arilou Skiff is the
# first hull the Steward unlocks (Sage's gift completes early in the
# slice); the others follow as the player progresses through the
# species quests.
ALLIED_SHIPS: tuple[AlliedShipEntry, ...] = (
    AlliedShipEntry(
        ship_class_id="ARILOU_SKIFF",
        display_name="Arilou Skiff",
        cost_credits=800,
        unlock_flag="has_quasispace_portal",   # Sage's gift is the alliance
        species_id="ARILOU",
        blurb=(
            "Half-folded teal disc. Phases briefly when struck; "
            "the Sage warns the player not to rely on the phase "
            "in tight quarters but offers the hull anyway."
        ),
    ),
    AlliedShipEntry(
        ship_class_id="ANDROSYNTH_CRUISER",
        display_name="Androsynth Refugee Cruiser",
        cost_credits=600,
        unlock_flag="met_androsynth",
        species_id="ANDROSYNTH",
        blurb=(
            "Stacked dark-and-red spindle from Coel Tessar's people. "
            "Built for distance flight; canonically the Androsynth "
            "carry their grief into the hull's weld-lines."
        ),
    ),
    AlliedShipEntry(
        ship_class_id="MMRNMHRM_SENTINEL",
        display_name="Mmrnmhrm Sentinel (gifted variant)",
        cost_credits=1500,
        unlock_flag="met_mmrnmhrm",
        species_id="MMRNMHRM",
        blurb=(
            "Silver-white swing-wing fighter, formally gifted by "
            "archive consensus. The Sentinel arrives with a "
            "preserved log-index plate; the Steward is requested "
            "to preserve it in turn."
        ),
    ),
    AlliedShipEntry(
        ship_class_id="THINN_BLADE",
        display_name="Thinn Blade (sideways-attuned)",
        cost_credits=900,
        unlock_flag="met_thinn",
        species_id="THINN",
        blurb=(
            "Two-dimensional ribbon-craft. Faces forward by Forward's "
            "personal heresy. Counter-intuitive aiming; canonically "
            "elegant when piloted at a conceptually-impossible angle."
        ),
    ),
    # ---- Pending: require new ShipClass from Combat Mechanics chat ----
    AlliedShipEntry(
        ship_class_id="SLYLANDRO_LIFT",
        display_name="Slylandro Lift",
        cost_credits=700,
        unlock_flag="met_slylandro",
        species_id="SLYLANDRO",
        unavailable=True,
        blurb=(
            "Gas-current envelope rebuilt for non-Slylandro pilots. "
            "Awaiting Combat Mechanics' ShipClass authoring."
        ),
    ),
    AlliedShipEntry(
        ship_class_id="BURVIXESE_SKIPPER",
        display_name="Burvixese Skipper",
        cost_credits=1100,
        # Only the evacuation branch survivors offer a hull
        unlock_flag="burvixese_contribution_evacuate",
        species_id="BURVIXESE",
        unavailable=True,
        blurb=(
            "Compact engineer-vessel built by the Andromeda-bound "
            "Burvixese remnant. Awaiting Combat Mechanics' ShipClass "
            "authoring + the canonical evacuation-branch flag wire-up."
        ),
    ),
)


def available_ships(game) -> list[AlliedShipEntry]:
    """Return entries that the player can SEE in the shipyard.

    Includes locked-but-canonically-available entries (rendered greyed
    in the UI) so the player learns what's coming. Excludes `unavailable`
    entries entirely until Combat Mechanics ships their ShipClass.

    Player must additionally have `cost_credits` available to PURCHASE
    an entry (separate from visibility).
    """
    return [s for s in ALLIED_SHIPS if not s.unavailable]


def is_purchaseable(game, entry: AlliedShipEntry) -> bool:
    """True iff the entry's unlock flag is set, the player has enough
    credits, and the ship isn't already in their fleet."""
    if entry.unavailable:
        return False
    if not game.flags.get(entry.unlock_flag):
        return False
    if game.credits < entry.cost_credits:
        return False
    if entry.ship_class_id in (game.fleet or []):
        return False
    return True


def buy_ship(game, entry: AlliedShipEntry) -> bool:
    """Attempt to purchase the entry. On success: deduct credits +
    append ship_class_id to game.fleet + return True. On failure:
    return False without mutating state.
    """
    if not is_purchaseable(game, entry):
        return False
    game.credits -= entry.cost_credits
    if entry.ship_class_id not in game.fleet:
        game.fleet.append(entry.ship_class_id)
    return True


def any_unlocked(game) -> bool:
    """True iff at least one allied ship is purchasable (unlock flag
    set). Drives the Mh-Lai Shipyard menu-entry visibility — until at
    least one is unlocked, the shipyard sub-menu stays hidden."""
    for entry in ALLIED_SHIPS:
        if entry.unavailable:
            continue
        if game.flags.get(entry.unlock_flag):
            return True
    return False
