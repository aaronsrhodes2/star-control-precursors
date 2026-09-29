"""The Fall of Mh-Lai — data layer for the slice's mid-game catastrophe.

Per `references/lore/the-fall-of-mh-lai.md`, this is the slice's
biggest single emotional + structural beat: Mh-Lai Station is destroyed
mid-game; every Mh-Lai-only service transfers to a Migration flagship
(*Hearth-of-Iron*); the slice's tone shifts permanently.

This module owns the **decision layer** — branch definitions + per-
branch side-effects + the trigger predicate. The scene (`fall_of_mhlai.py`)
renders the 5-beat sequence and routes player input through the timer
+ decision picker.

**Trigger contract** (per the dispatch):
- `tutorial_complete = True`
- `has_distress_beacon = True` (Steward understands what the Others ARE)
- `len(visited_systems) >= 5`
- AND at least one species-decision flag (slylandro_decision_made
  OR mycon_decision_made) — both currently authored as Council
  recommendation `resolved_flag`s
- AND `mhlai_destroyed` is False (the event hasn't already fired)

When all conditions are met, the scene auto-fires at the next
hyperspace traversal. The decision is time-constrained (60 seconds
real / game-time-equivalent). If the player times out, the
*honor-migration* branch defaults.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Callable

if TYPE_CHECKING:
    from scz.engine.game import Game


# Suggested decision window in game-seconds. The scene's update advances
# a timer; the player can pause-think via input-quiescence; expiry
# defaults to the honor-migration branch.
DECISION_WINDOW_SECONDS: float = 60.0

# Cleanser-acceleration branch availability gate.
CLEANSER_ACCELERATION_STANDING_THRESHOLD: int = 3


@dataclass(frozen=True)
class FallBranch:
    """One branch of the Fall of Mh-Lai decision tree.

    `id` matches canonical FSM state ids in the quest spreadsheet.
    `label` is the in-fiction option text shown in the decision UI.
    `summary` is a one-line consequence preview (shown in the detail
    pane when the option is focused).
    `side_effect` mutates game state on commit — sets the canonical
    flag-set per the lore doc.
    """
    id: str
    label: str
    summary: str
    side_effect: Callable[["Game"], None]


# ---------------------------------------------------------------------------
# Branch side-effects — one per outcome
# ---------------------------------------------------------------------------
# All branches set `mhlai_destroyed = True` (the Fall itself is
# inevitable regardless of branch — only Halia's fate and the post-
# fall faction balance vary). All set `mhlai_fall_resolved = True` so
# the trigger doesn't re-fire on the next hyperspace traversal.

def _race_and_evacuate(game: "Game") -> None:
    """High-effort race; arrive ~20 min before the Others; aboard the
    Council chamber; fight to evacuate Halia + ~30% of the Council.
    Persuader leadership preserved. Tense combat-and-dialog sequence —
    for slice MVP the combat is narrated, not played out.
    """
    game.flags["mhlai_destroyed"] = True
    game.flags["mhlai_fall_resolved"] = True
    game.flags["mhlai_fall_branch"] = "race_and_evacuate"
    game.flags["halia_alive"] = True
    game.flags["halia_status"] = "free_persuader"
    game.flags["persuader_leadership_preserved"] = True


def _race_but_witness(game: "Game") -> None:
    """Burn for Mh-Lai but the math doesn't work; arrive in orbit *as
    Mh-Lai is being consumed*; witness Halia's last broadcast from the
    burning chamber. Mid-payoff: an Archive entry of unprecedented
    detail.
    """
    game.flags["mhlai_destroyed"] = True
    game.flags["mhlai_fall_resolved"] = True
    game.flags["mhlai_fall_branch"] = "race_but_witness"
    game.flags["halia_alive"] = False
    game.flags["halia_status"] = "dead"
    game.flags["witnessed_fall_at_orbit"] = True


def _honor_migration(game: "Game") -> None:
    """Do not race; stay on current trajectory. Halia's last
    transmission arrives via long-range comm. The Steward grieves from
    a distance. *The canonical "you accepted the math" branch.* Also
    the timer-expiry default.
    """
    game.flags["mhlai_destroyed"] = True
    game.flags["mhlai_fall_resolved"] = True
    game.flags["mhlai_fall_branch"] = "honor_migration"
    game.flags["halia_alive"] = False
    game.flags["halia_status"] = "dead"


def _cleanser_acceleration(game: "Game") -> None:
    """Only available if Cleanser standing ≥ 3 AND
    `cleanser_action_authorized` was previously set. The Cleansers had
    already evacuated themselves + some senior Persuaders pre-emptively
    (citing the Hider probe risk). Halia is off-world on a Cleanser
    vessel; she survives. Cleanser doctrine now controls the Council
    remnant. *Worst surviving-Halia outcome.*
    """
    game.flags["mhlai_destroyed"] = True
    game.flags["mhlai_fall_resolved"] = True
    game.flags["mhlai_fall_branch"] = "cleanser_acceleration"
    game.flags["halia_alive"] = True
    game.flags["halia_status"] = "cleanser_supervised"
    game.flags["persuader_collapse"] = True
    game.flags["cleanser_council_supervision"] = True


# ---------------------------------------------------------------------------
# Branch registry — order matters for cursor-default selection
# ---------------------------------------------------------------------------

BRANCHES_BASE: tuple[FallBranch, ...] = (
    FallBranch(
        id="race_and_evacuate",
        label="Race to Mh-Lai — fight to evacuate Halia",
        summary=(
            "Burn the drive open. Slam the Quasi-Drive if it's "
            "ready. Arrive ~20 minutes ahead of the Others. Aboard the "
            "chamber; fight to evacuate Halia and the Council remnant. "
            "High cost; high payoff. Persuader leadership survives."
        ),
        side_effect=_race_and_evacuate,
    ),
    FallBranch(
        id="race_but_witness",
        label="Race — but accept it will be too late",
        summary=(
            "Burn anyway. The math says you arrive *as Mh-Lai is being "
            "consumed*. Witness the fall directly from orbit. Halia's "
            "last transmission reaches you from the burning chamber. "
            "Grief as fuel; an Archive entry of unprecedented detail."
        ),
        side_effect=_race_but_witness,
    ),
    FallBranch(
        id="honor_migration",
        label="Do not race — honor the Migration timetable",
        summary=(
            "Stay on the current trajectory. Halia's last transmission "
            "arrives via long-range comm. The Steward grieves at a "
            "distance. The Council is gone. You are one of the most "
            "senior surviving Persuader voices. *(Default if you take "
            "no action — the math chooses for you.)*"
        ),
        side_effect=_honor_migration,
    ),
)

# The Cleanser-aligned acceleration branch is conditionally available.
_CLEANSER_BRANCH: FallBranch = FallBranch(
    id="cleanser_acceleration",
    label="Cleanser-aligned acceleration",
    summary=(
        "The Cleansers had already pre-emptively evacuated themselves "
        "and some senior Persuaders, citing a Hider probe risk. Halia "
        "is off-world on a Cleanser vessel — she survives, but "
        "Cleanser doctrine now controls the Council remnant. The "
        "Persuader bench collapses. Halia is alive and *miserable*."
    ),
    side_effect=_cleanser_acceleration,
)


def visible_branches(game: "Game") -> list[FallBranch]:
    """Return the branches the Steward can pick from given current
    game state. Cleanser acceleration only appears if the Cleanser
    standing threshold is met AND a prior Cleanser-pre-emption was
    authorized.
    """
    out: list[FallBranch] = list(BRANCHES_BASE)
    standing = game.flags.get("faction_standing")
    cleanser = 0
    if isinstance(standing, dict):
        cleanser = int(standing.get("cleanser", 0))
    if (
        cleanser >= CLEANSER_ACCELERATION_STANDING_THRESHOLD
        and game.flags.get("cleanser_action_authorized")
    ):
        out.append(_CLEANSER_BRANCH)
    return out


# ---------------------------------------------------------------------------
# Trigger predicate
# ---------------------------------------------------------------------------

def should_fire_fall(game: "Game") -> bool:
    """True iff the Fall of Mh-Lai trigger should auto-fire now.

    Per the dispatch trigger contract:
    - tutorial_complete
    - has_distress_beacon
    - visited_systems >= 5
    - at least one of slylandro_decision_made / mycon_decision_made
    - NOT mhlai_fall_resolved (the event hasn't already fired)
    """
    flags = game.flags
    if flags.get("mhlai_fall_resolved"):
        return False
    if not flags.get("tutorial_complete"):
        return False
    if not flags.get("has_distress_beacon"):
        return False
    visited = flags.get("visited_systems")
    if not isinstance(visited, list) or len(visited) < 5:
        return False
    species_decision = (
        flags.get("slylandro_decision_made")
        or flags.get("mycon_decision_made")
        # Slylandro cloak/migrate flags also count — the dispatch
        # lists slylandro_decision_made as the canonical key but the
        # underlying cloak/migrate flags are what gets set by the
        # existing Slylandro quest.
        or flags.get("slylandro_cloaked")
        or flags.get("slylandro_migrated")
        or flags.get("mycon_whisper_resolved")
    )
    if not species_decision:
        return False
    return True
