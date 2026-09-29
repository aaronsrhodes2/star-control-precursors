"""The Final Conflict — fleet composition + trigger logic.

Canon (revised 2026-05-18, supersedes the 2026-05-17 draft):
`references/lore/the-final-conflict.md` §"Canon revision 2026-05-18".

The slice climax. Migration fleet arrives at the Rainbow Worlds
arrow-tip to depart; Drev-Tok's Homesteader coalition is already
there blocking the crossing. Negotiation always fails. Super-melee.

- **Drev-Tok's fleet** = canonical fixed roster (one-of-each
  Homesteader-aligned combat ship class).
- **Steward's fleet** = `FURLING_SCOUT` plus one ship per friendly
  species the player helped (alliance-flag-driven).
- **Win** → ending.
- **Loss** → Time Drive snapshot restore (the player tries again).
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from scz.engine.game import Game


# Drev-Tok's canonical Homesteader coalition. Fixed across all slice
# variations — the slice climax doesn't change shape based on player
# choices on the antagonist side. See `the-final-conflict.md` §Canon
# revision for the inclusion rationale (each entry has a canonical
# Homesteader-coalition basis).
DREV_TOK_FLEET_IDS: tuple[str, ...] = (
    # Deploy order = pacing (sim 2026-05-19): Defender is Drev-Tok's
    # personal flagship and deploys LAST as the climax-of-the-climax —
    # the player chews through escort screen first, then faces him.
    # Previous order (Defender first) buried him as filler-tier opener
    # and let the Cleanser carry too many fights from slot 2.
    "MYCON_PODSHIP",       # Autonomous biot, opportunistic — opener/distractor
    "BURV_BROADCASTER",    # Broadcaster network outlived the Burvixese; hostile by inertia
    "UTWIG_JUGGER",        # Pre-doctrine Utwig ships re-purposed by Drev-Tok
    "CLEANSER_CRUISER",    # Cleanser hardliner; opposes Migration as theology
    "DEFENDER_VESSEL",     # Drev-Tok's flagship — boss slot (always last)
)


# Alliance-flag → ship-class-id mapping for the player's fleet. Each
# tuple is `(flag_check_callable, ship_class_id)`. The flag_check is
# called with `game` and returns True if that ally should join the
# Steward's fleet at the Final Conflict.
#
# Order matters — it's the canonical display order in the fleet roster
# UI (Scout first, then Sage's gift Arilou, then chronological
# alliances thereafter).
def _alliance_arilou(game: "Game") -> bool:
    return bool(game.flags.get("has_quasispace_portal"))


def _alliance_androsynth(game: "Game") -> bool:
    # The Distress Beacon quest is the alliance gate. Excludes the
    # Cleanser-betrayal branch where the Androsynth were canonically
    # exterminated rather than welcomed.
    return (
        bool(game.flags.get("met_androsynth"))
        and game.flags.get("androsynth_recommendation") != "cleanse"
    )


def _alliance_mmrnmhrm(game: "Game") -> bool:
    # Any non-sabotage outcome of the cognition decision counts —
    # grant / refuse / cap-compromise are all "alliance honored."
    return (
        bool(game.flags.get("met_mmrnmhrm"))
        and game.flags.get("mmrnmhrm_cognition") not in (None, "sabotage")
    )


def _alliance_thinn(game: "Game") -> bool:
    return bool(game.flags.get("met_thinn"))


def _alliance_slylandro(game: "Game") -> bool:
    return bool(game.flags.get("met_slylandro"))


def _alliance_burvixese(game: "Game") -> bool:
    # Only the evacuation-advocacy branch — that's the only branch
    # where any Burvixese survive to send a hull.
    return game.flags.get("burvixese_contribution") == "advocate"


def _alliance_lemmkin(game: "Game") -> bool:
    # Any non-Cleanser branch counts — the Lemmkin send their
    # Skitter as moral support even though they don't fight; canon
    # color, per the slice's "all helped allies join the Steward"
    # spec.
    contribution = game.flags.get("lemmkin_contribution")
    return contribution is not None and contribution != "cleanser_eliminated"


ALLIANCE_SHIP_RULES: tuple[tuple[object, str], ...] = (
    (_alliance_arilou,     "ARILOU_SKIFF"),
    (_alliance_androsynth, "ANDROSYNTH_CRUISER"),
    (_alliance_mmrnmhrm,   "MMRNMHRM_SENTINEL"),
    (_alliance_thinn,      "THINN_BLADE"),
    # The Slylandro Lift + Burvixese Skipper ShipClasses don't yet
    # exist in `src/scz/combat/ships.py` (per the Allied Ships
    # dispatch — `unavailable=True` flagged in `allied_ships.py`).
    # When Combat Mechanics ships those classes, uncomment these:
    # (_alliance_slylandro,  "SLYLANDRO_LIFT"),
    # (_alliance_burvixese,  "BURVIXESE_SKIPPER"),
    (_alliance_lemmkin,    "LEMMKIN_SKITTER"),
)


def build_steward_fleet(game: "Game") -> list[str]:
    """Compose the Steward's Final Conflict fleet from alliance flags.

    Returns ship-class ids in canonical-display order. Always starts
    with FURLING_SCOUT (the Steward's own ship); each subsequent slot
    is gated on an alliance flag from `ALLIANCE_SHIP_RULES`.

    A player who completed zero alliance quests gets `["FURLING_SCOUT"]`
    — a genuinely-hard 1v5 fight against Drev-Tok's coalition.

    A player who completed every viable alliance gets the full 6-ship
    roster against Drev-Tok's 5.
    """
    fleet: list[str] = ["FURLING_SCOUT"]
    for check, ship_id in ALLIANCE_SHIP_RULES:
        try:
            if check(game):
                fleet.append(ship_id)
        except Exception:
            # Defensive — if a check accesses a missing attribute,
            # treat it as "no alliance" rather than crash the climax.
            continue
    return fleet


def build_drev_tok_fleet() -> list[str]:
    """Return Drev-Tok's canonical coalition roster.

    Fixed across all slice variations. See `DREV_TOK_FLEET_IDS` for
    the per-ship rationale.
    """
    return list(DREV_TOK_FLEET_IDS)


def should_fire_final_conflict(game: "Game") -> bool:
    """True iff the Final Conflict trigger should auto-fire now.

    Trigger conditions (slice-end gates):
    - The Fall of Mh-Lai has resolved (post-Phase-4 timetable)
    - The player holds the Rainbow Resonator (or has it installed) —
      proxy: `rainbow_resonator_in_cargo` OR the module is installed
      in the field slot OR the `rainbow_resonator_equipped` flag is set
    - Single-fire (`final_conflict_resolved` is False)

    Future expansion: add `migration_fleet_assembled` gate once that
    upstream beat has authoring. For MVP, the resolver + post-Fall is
    enough — the Migration is *implicit* once these are met.
    """
    flags = game.flags
    if flags.get("final_conflict_resolved"):
        return False
    if not flags.get("mhlai_destroyed"):
        return False
    # Rainbow Resonator gate — accept any of three signals:
    if (
        flags.get("rainbow_resonator_equipped")
        or flags.get("rainbow_resonator_in_cargo")
        or _resonator_installed(game)
    ):
        return True
    return False


def _resonator_installed(game: "Game") -> bool:
    """True iff the Rainbow Resonator module is installed in ANY of
    the 12 generic slots. Post 2026-05-18 stacking refactor: modules
    aren't constrained to specific slot types, so a name-slot query
    is wrong — use the cross-slot helper instead."""
    try:
        from scz.content.modules import is_module_installed
        return is_module_installed(game, "rainbow_resonator")
    except Exception:
        return False


# ---------------------------------------------------------------------------
# Pre-conflict snapshot (Time Drive restore-on-loss)
# ---------------------------------------------------------------------------

def take_pre_conflict_snapshot(game: "Game") -> dict:
    """Snapshot the relevant game state to restore on loss.

    Per Aaron's canon: *"otherwise, re-load last save (our time drive
    takes us back before the conflict starts)"*. The snapshot captures
    everything that the Final Conflict could plausibly disturb — fleet,
    credits, cargo, schematics, and a copy of `flags`. Hyperspace
    position is captured separately by the FinalConflictScene so the
    player materializes back at the right hyperspace coords.

    Returned dict can be passed to `restore_pre_conflict_snapshot`.
    """
    return {
        "fleet": list(game.fleet),
        "credits": int(game.credits),
        "cargo": dict(game.cargo),
        "schematics": set(game.schematics),
        "consumed_schematics": set(game.consumed_schematics),
        "flags": dict(game.flags),
        "uninstalled_modules": dict(game.uninstalled_modules),
        "ship_modules": dict(game.ship_modules),
    }


def restore_pre_conflict_snapshot(game: "Game", snapshot: dict) -> None:
    """Restore the game state from a `take_pre_conflict_snapshot`
    output. Used by the Final Conflict's loss path — the Time Drive
    rewinds the Steward to before the conflict fired.

    `final_conflict_resolved` is explicitly NOT carried forward from
    the snapshot since the snapshot was taken BEFORE the failed
    attempt — the player can re-engage.
    """
    game.fleet = list(snapshot["fleet"])
    game.credits = int(snapshot["credits"])
    game.cargo = dict(snapshot["cargo"])
    game.schematics = set(snapshot["schematics"])
    game.consumed_schematics = set(snapshot["consumed_schematics"])
    game.flags = dict(snapshot["flags"])
    game.uninstalled_modules = dict(snapshot["uninstalled_modules"])
    game.ship_modules = dict(snapshot["ship_modules"])
    # Explicitly clear the resolved flag in case the snapshot was
    # taken AFTER it got set (which shouldn't happen but is defensive).
    game.flags.pop("final_conflict_resolved", None)
