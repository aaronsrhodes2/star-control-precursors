"""Crew bond-objects — Common Room shelf contents per the canon in
`references/lore/crew-common-room.md` §Five named-crew alcoves.

Each named-crew alcove has a personal shelf that accumulates bond-
objects as the slice progresses. Three layers:

- **Default**: shown whenever the crew is aboard (recruited).
- **Always**: shown alongside the default — canonical objects that
  *define* the crew (Mraka's family portrait, Bren-Vor's firing-rule
  notebook, etc.). Not a separate render tier; just always-on.
- **Conditional**: shown when a quest-completion flag is set
  (typically a side-quest favorable-resolution flag). Many of these
  flags are not yet authored — the crew side-quests dispatch in
  `HANDOFF_design_chat.md` is still open. For now those bond-objects
  reference the canonical flag names per `crew-recruitment-quests.md`;
  they simply don't render until the underlying quest content ships.

The Common Room scene renders each visible bond-object as a small
labelled tile on the alcove's shelf strip. Image-chat will eventually
supply per-object sprites; for slice MVP the labels render as text
inside small colored rectangles.

Side-quest goalpost notifications — when the player has met the
prereqs for a crew's side-quest to *begin* but the quest hasn't yet
fired, the Common Room renders a "!" badge on the alcove. Predicates
live in `goalpost_notification_visible` below.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from scz.engine.game import Game


@dataclass(frozen=True)
class BondObject:
    """One personal-shelf item in a crew member's Common Room alcove.

    `flag_required` is None for default/always-on objects; non-None
    objects render only when `game.flags[flag_required]` is truthy
    (typically a quest favorable-resolution flag from the
    crew-recruitment-quests doc).

    `label` is the in-fiction object name shown on the shelf.
    `color` is the placeholder-sprite accent until Image-chat ships
    the real object art.
    """
    label: str
    color: tuple[int, int, int]
    flag_required: str | None = None


# ---------------------------------------------------------------------------
# Per-crew bond-objects
# ---------------------------------------------------------------------------
# Authored from `references/lore/crew-common-room.md`. Default/always-
# on objects render whenever the crew is recruited; conditional objects
# render when the corresponding flag is set. Flag names track canonical
# crew-recruitment-quests.md side-quest favorable-resolution flags;
# many of those flags are not yet wired (side-quest content is open
# in HANDOFF_design_chat.md), so those bond-objects simply won't render
# until the underlying content lands. The Image-chat dispatch covers
# the per-object sprite art.

BOND_OBJECTS: dict[str, tuple[BondObject, ...]] = {
    "pilot": (   # Mraka Yenn-Sa
        BondObject(
            label="Drifter's Circuit medals (3 cup wins)",
            color=(220, 180, 100),
        ),
        BondObject(
            label="Olwen-Veth family portrait (un-named)",
            color=(180, 160, 140),
        ),
        BondObject(
            label="Soren Kel-Var's drive-fix component",
            color=(200, 200, 220),
            flag_required="mraka_last_race_reconciled",
        ),
        BondObject(
            label="Olwen-Veth clan-marker (Soren's gift)",
            color=(200, 180, 120),
            flag_required="mraka_last_race_reconciled",
        ),
    ),
    "weapons_officer": (   # Bren-Vor Telcas
        BondObject(
            label="Velt-Ra Telcas's photograph",
            color=(160, 170, 200),
        ),
        BondObject(
            label="Firing-rule notebook (32 pages, annotated)",
            color=(180, 180, 200),
        ),
        BondObject(
            label="Velt-Ra's journal (closed, with Persuader pin)",
            color=(180, 200, 220),
            flag_required="bren_vor_aimers_verdict_resolved",
        ),
    ),
    "engineer": (   # Yelena Lwen-Tar
        BondObject(
            label="Family portrait (Mev-Tar + child Yelena)",
            color=(200, 170, 130),
        ),
        BondObject(
            label="17 specialized tools (alphabetical)",
            color=(200, 180, 140),
        ),
        BondObject(
            label="Unzervalt factory-floor fragment",
            color=(180, 150, 100),
            flag_required="yelena_last_hull_completed",
        ),
        BondObject(
            label="Korven's tool-belt buckle",
            color=(170, 140, 100),
            flag_required="yelena_last_hull_completed",
        ),
    ),
    "medic": (   # Mira-Rou Halve-Tel
        BondObject(
            label="Glass amphora (heirloom biot-fragment)",
            color=(180, 220, 200),
        ),
        BondObject(
            label="Olune Halve-Tel portrait (great-grandmother)",
            color=(190, 200, 180),
        ),
        BondObject(
            label="Portable shear-repair fab pattern",
            color=(160, 200, 200),
        ),
        BondObject(
            label="Furling Hider citation (cognitive substrate)",
            color=(200, 210, 180),
            flag_required="mira_rou_deep_child_suppressed",
        ),
        BondObject(
            label="Sevreth's Child translation-log",
            color=(180, 230, 220),
            flag_required="mira_rou_deep_child_allowed",
        ),
    ),
    "navigator": (   # Tarven Olwen-Sa
        BondObject(
            label="7 prior-Steward portrait miniatures",
            color=(160, 150, 200),
        ),
        BondObject(
            label="Inexhaustible tea-cup supply",
            color=(180, 160, 140),
        ),
        BondObject(
            label="Iren-Vor Olwen-Veth's voice-cache (open)",
            color=(200, 180, 220),
            flag_required="tarven_erased_logs_reported",
        ),
        BondObject(
            label="Iren-Vor Olwen-Veth's voice-cache (sealed)",
            color=(180, 160, 200),
            flag_required="tarven_erased_logs_kept_secret",
        ),
    ),
}


def visible_bond_objects(
    game: "Game", role: str,
) -> list[BondObject]:
    """Return the bond-objects that should render for the given crew
    role right now. Default/always-on objects (flag_required is None)
    always render; conditional objects render only when their flag is
    truthy. Returns [] for unknown roles.
    """
    items = BOND_OBJECTS.get(role, ())
    out: list[BondObject] = []
    for obj in items:
        if obj.flag_required is None or game.flags.get(obj.flag_required):
            out.append(obj)
    return out


# ---------------------------------------------------------------------------
# Side-quest goalpost notifications
# ---------------------------------------------------------------------------
# Each crew has a side-quest that becomes *available* once a goalpost
# threshold is met (per `references/lore/crew-recruitment-quests.md`
# §Backstories, Personalities, Side-Quests). The Common Room shows a
# pulsing "!" badge on the crew's alcove until the side-quest starts.
#
# Goalposts are READ here from canonical flags. Many of the side-quest
# *start* flags (`q_<role>_sq_start`) are not yet wired because the
# crew side-quest content dispatch in HANDOFF_design_chat.md is open.
# For now, the badge clears when the corresponding goalpost is met
# AND the side-quest's start-flag is set; absent the start-flag, the
# badge stays visible (acceptable for MVP — Aaron's playtest will see
# them as "the crew wants to talk to you eventually").

_PILOT_GOALPOST_SYSTEMS: int = 5
_NAVIGATOR_GOALPOST_SYSTEMS: int = 3
_ENGINEER_GOALPOST_INSTALLS: int = 4


def _systems_visited(game: "Game") -> int:
    """Count entries in `visited_systems` (deduplicated by cluster_name).
    Drives Mraka's and Tarven's goalposts.
    """
    visited = game.flags.get("visited_systems")
    if isinstance(visited, list):
        return len(visited)
    return 0


def _modules_installed(game: "Game") -> int:
    """Count of modules currently installed in slots (non-None).
    Drives Yelena's goalpost.
    """
    return sum(
        1 for mid in game.ship_modules.values() if mid is not None
    )


def goalpost_notification_visible(
    game: "Game", role: str,
) -> bool:
    """True iff the crew member's side-quest goalpost is met and the
    side-quest hasn't started yet. Drives the "!" badge render on
    their Common Room alcove.

    Per crew-recruitment-quests.md goalposts:
    - pilot: visited 5+ systems
    - weapons_officer: Distress Beacon screened (`has_distress_beacon`)
    - engineer: 4+ modules installed
    - medic: post-Beacon-quest (`has_distress_beacon`); some branches
      gate on `met_mycon` for the Deep Child arc
    - navigator: visited 3+ systems
    """
    flags = game.flags
    # Mission must be aboard for the goalpost to matter
    if not flags.get(f"recruited_{role}"):
        return False
    # If the side-quest's start flag is already set, the player has
    # initiated the quest — badge clears.
    if flags.get(f"q_{role}_sq_start"):
        return False

    if role == "pilot":
        return _systems_visited(game) >= _PILOT_GOALPOST_SYSTEMS
    if role == "weapons_officer":
        return bool(flags.get("has_distress_beacon"))
    if role == "engineer":
        return _modules_installed(game) >= _ENGINEER_GOALPOST_INSTALLS
    if role == "medic":
        return bool(flags.get("has_distress_beacon"))
    if role == "navigator":
        return _systems_visited(game) >= _NAVIGATOR_GOALPOST_SYSTEMS
    return False
