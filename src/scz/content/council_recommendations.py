"""Furling Council recommendations — the formal decision moments where
species fates crystallize into canonical terminal statuses.

The Council scene presents a list of *open* recommendations (one per
species/topic that's reached the decision-ready threshold). Each
recommendation has 2-4 options; selecting one applies the option's
side-effects (terminal-status flag + faction-standing shifts +
Bio-Archive ledger entry) and retires the recommendation from the open
list.

Some recommendations are also reachable through species-side dialog —
e.g. the Slylandro Cloak quest lets the player commit the cloak
straight from the Slylandro dialog. The Council is the *meta-formal*
path: where decisions that don't have a species-side resolution
moment get made (Uplift Dilemma especially) and where prior
decisions get ratified.

**Slice scope** (this round): three recommendations wired:
- `uplift_dilemma`: the proto-Ur-Quan + proto-Qor-Ah uplift question.
  The canonical Council moment. No species-side resolution path —
  only Council can decide this. Three options.
- `mycon_whisper`: the Deep Child emergence question. Has a partial
  species-side resolution (Mycon dialog branches) but Council formalizes.
  Four options.
- `dnyarri_briefing` (read-only): displays the recommendation the
  Steward already made at Beta Orionis. Confirmation moment; no
  re-decision. Documents the choice for the slice ledger.

**Faction standings**: stored in `game.flags["faction_standing"]` as a
dict keyed by faction id (persuader/compeller/cleanser/defender/
denier/hider). Each option's side-effect adjusts via `_adjust_standing`.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Callable

if TYPE_CHECKING:
    from scz.engine.game import Game


# The six Furling factions (per references/lore/factions-and-war.md and
# the canonical narrative spine). Each Council option can shift any
# subset of these standings; the slice's overall ending tilts toward
# whichever faction dominates the cumulative score.
FACTIONS: tuple[str, ...] = (
    "persuader",
    "compeller",
    "cleanser",
    "defender",
    "denier",
    "hider",
)

# Human-readable faction labels for HUD rendering.
FACTION_LABELS: dict[str, str] = {
    "persuader": "Persuaders",
    "compeller": "Compellers",
    "cleanser":  "Cleansers",
    "defender":  "Defenders",
    "denier":    "Deniers",
    "hider":     "Hiders",
}


# Side-effect type: takes the game, mutates state, optionally returns a
# string description that the scene logs as a "Council outcome" line.
SideEffect = Callable[["Game"], str | None]


def _adjust_standing(game: "Game", **deltas: int) -> None:
    """Adjust faction standings by the given keyword deltas.

    Example: `_adjust_standing(game, persuader=+2, cleanser=-1)`.

    Lazily initializes `game.flags["faction_standing"]` as a dict of
    all six factions at zero. Missing keys default to 0.
    """
    standing = game.flags.get("faction_standing")
    if not isinstance(standing, dict):
        standing = {f: 0 for f in FACTIONS}
        game.flags["faction_standing"] = standing
    for faction, delta in deltas.items():
        if faction in FACTIONS:
            standing[faction] = int(standing.get(faction, 0)) + int(delta)


@dataclass(frozen=True)
class CouncilOption:
    """One choice in a Council recommendation."""
    id: str
    label: str
    # Short description shown in the detail pane before the player
    # commits to this option. 1-3 sentences.
    summary: str
    # The faction-reaction line shown after commit, in the voice of
    # whichever faction this option pleases or upsets most.
    outcome_line: str
    side_effect: SideEffect


@dataclass(frozen=True)
class CouncilRecommendation:
    """One Council decision moment."""
    id: str
    title: str
    # Brief context the Council leader gives when the recommendation is
    # selected — what the species is, what's at stake.
    context: str
    options: tuple[CouncilOption, ...]
    # Flag that gates whether this recommendation appears on the open
    # list. Typically a species-encounter flag (`met_slylandro`,
    # `observed_proto_uq`, etc.).
    prereq_flag: str
    # Flag set after the player commits — gates the recommendation off
    # the open list. Usually `<id>_resolved`.
    resolved_flag: str
    # True if this recommendation is informational only — the decision
    # was already made elsewhere (e.g. dnyarri_briefing reflects the
    # Beta Orionis dialog choice). The player just acknowledges.
    read_only: bool = False


# ---------------------------------------------------------------------------
# Side-effect helpers — one per option's outcome
# ---------------------------------------------------------------------------

# --- Uplift Dilemma ---

def _uplift_continue(game: "Game") -> str:
    """Persuader path — let the proto-Ur-Quan / proto-Qor-Ah finish
    uplift to sapience. They become Migration cases (a later slice's
    problem). SC2-era domination canon then holds.
    """
    game.flags["uplift_recommendation_made"] = True
    game.flags["uplift_recommendation"] = "continue"
    game.flags["uplift_dilemma_resolved"] = True
    # SC2-canon outcomes: both species reach sapience; they become
    # Migration cases in a later slice. For our slice scope, mark them
    # as Pending so the win-condition tracker shows them unresolved.
    game.flags["proto_uq_terminal_status"] = "Pending"
    game.flags["proto_qa_terminal_status"] = "Pending"
    _adjust_standing(game, persuader=+2, cleanser=-2)
    return "Persuader bench rises; Cleansers withdraw from chamber."


def _uplift_stop(game: "Game") -> str:
    """Defender path — halt the uplift project; the proto-species stay
    pre-sapient and the Others never notice them. SC2 canon-clean (we
    leave them where SC2 finds them).
    """
    game.flags["uplift_recommendation_made"] = True
    game.flags["uplift_recommendation"] = "stop"
    game.flags["uplift_dilemma_resolved"] = True
    game.flags["proto_uq_terminal_status"] = "Pre-sentient"
    game.flags["proto_qa_terminal_status"] = "Pre-sentient"
    _adjust_standing(game, defender=+2, persuader=-1)
    return "Defenders nod. The molluscoids stay molluscoids."


def _uplift_cleanse(game: "Game") -> str:
    """Cleanser path — euthanize the proto-species pre-sapient. The
    Quiet Ledger grows by several million names. No SC2-era domination
    canon (the Ur-Quan never become).
    """
    game.flags["uplift_recommendation_made"] = True
    game.flags["uplift_recommendation"] = "cleanse"
    game.flags["uplift_dilemma_resolved"] = True
    game.flags["proto_uq_terminal_status"] = "Eliminated"
    game.flags["proto_qa_terminal_status"] = "Eliminated"
    _adjust_standing(game, cleanser=+2, persuader=-2, defender=-1)
    return "Cleansers rise. The chamber chills."


# --- Mycon Whisper ---

def _mycon_suppress(game: "Game") -> str:
    """Halt the Deep Child emergence — the biot mass stays pre-sentient.
    Persuader/Defender favor: a clean SC2 outcome (the biots remain
    terraforming tools).
    """
    game.flags["mycon_whisper_resolved"] = True
    game.flags["mycon_whisper_decision"] = "suppress"
    game.flags["mycon_terminal_status"] = "Pre-sentient"
    _adjust_standing(game, persuader=+1, defender=+1, hider=+1)
    return "The biot mantle stays quiet. The seed does not grow."


def _mycon_allow(game: "Game") -> str:
    """Let the Deep Child wake — a new sentient species emerges that
    must then be evacuated or cloaked. Adds a Migration case the
    Council had not planned for.

    The awakening Mycon biot-mantle, in its first decision-capable
    moment, gifts the Steward a `bio_architect` crew specialist — the
    Mantle-Resonance Bio-Architect canonically engineered by the
    nascent collective as a thank-you. This was the missing grant for
    the BIO_ARCHITECT Module (audit 2026-05-18); now wired here.
    """
    game.flags["mycon_whisper_resolved"] = True
    game.flags["mycon_whisper_decision"] = "allow"
    game.flags["mycon_terminal_status"] = "Pending"
    _adjust_standing(game, persuader=+2, cleanser=-1)
    # Bio-Architect crew gift — Mycon-quest reward module.
    game.uninstalled_modules["bio_architect"] = (
        game.uninstalled_modules.get("bio_architect", 0) + 1
    )
    return "The Persuader bench welcomes the new sapience to the manifest."


def _mycon_cleanse_heretical(game: "Game") -> str:
    """Cleanse the awakening subset only — the bulk of biot mass
    continues as terraforming tools, but the Deep-Child-stirred
    population is euthanized.
    """
    game.flags["mycon_whisper_resolved"] = True
    game.flags["mycon_whisper_decision"] = "cleanse_heretical"
    game.flags["mycon_terminal_status"] = "Pre-sentient"
    _adjust_standing(game, cleanser=+1, persuader=-1)
    return "The Cleansers carry the motion. The Ledger ticks up by hundreds of thousands."


def _mycon_ignore(game: "Game") -> str:
    """Allow the Deep Child but make no provision — the emerging
    sentience is then easy prey for the arriving Others (slice
    epilogue: biots all consumed). Denier favor.
    """
    game.flags["mycon_whisper_resolved"] = True
    game.flags["mycon_whisper_decision"] = "ignore"
    game.flags["mycon_terminal_status"] = "Eliminated"
    _adjust_standing(game, denier=+2, persuader=-2)
    return "Deniers shrug. The chamber is silent for a long moment."


# --- Dnyarri briefing (read-only acknowledgement) ---

def _dnyarri_ack(game: "Game") -> str:
    """Read-only ack — the player already made their Dnyarri call at
    Beta Orionis. Council records the recommendation for posterity.
    No re-decision; no standing shift.
    """
    game.flags["dnyarri_briefing_resolved"] = True
    rec = game.flags.get("dnyarri_recommendation") or "deferred"
    return f"Recommendation logged: {rec}. The proto-Dnyarri file is closed."


# ---------------------------------------------------------------------------
# Recommendation registry
# ---------------------------------------------------------------------------

RECOMMENDATIONS: tuple[CouncilRecommendation, ...] = (
    CouncilRecommendation(
        id="uplift_dilemma",
        title="The Uplift Dilemma — proto-Ur-Quan / proto-Qor-Ah",
        context=(
            "Centuries ago a Furling bio-engineering team began an "
            "uplift project on the Vela molluscoids. The Proto-Ur-Quan "
            "are one branch — dominators, blood-red when in command. "
            "The Proto-Qor-Ah are the other — ritual purifiers, ivory "
            "when pure, pitch when impure. Both sit on the Others' "
            "detection threshold; the Proto-Qor-Ah cross it on the "
            "current uplift trajectory. The Council requires a "
            "recommendation. There is no species-side resolution path "
            "— the question lives here."
        ),
        options=(
            CouncilOption(
                id="continue",
                label="Continue the uplift to sapience",
                summary=(
                    "Both species reach full sapience. They become "
                    "Migration cases the Council can persuade. Risk: "
                    "the Proto-Qor-Ah's cognitive signature ramps "
                    "before the Migration window closes."
                ),
                outcome_line=(
                    "*\"Then we will persuade them when they wake.\"*"
                ),
                side_effect=_uplift_continue,
            ),
            CouncilOption(
                id="stop",
                label="Halt the uplift — leave them pre-sapient",
                summary=(
                    "The uplift project is wound down. The molluscoids "
                    "stay molluscoids. SC2-canon-clean: they remain "
                    "where the historical record finds them. The "
                    "Persuader bench is — disappointed."
                ),
                outcome_line=(
                    "*\"A small kindness. They will not know what "
                    "they have been spared.\"*"
                ),
                side_effect=_uplift_stop,
            ),
            CouncilOption(
                id="cleanse",
                label="Cleanse — pre-emptive euthanasia",
                summary=(
                    "The Proto-Qor-Ah ramp is the deciding argument. "
                    "Euthanize both species before they cross the "
                    "threshold. The Quiet Ledger grows by several "
                    "million names. The Persuaders will not forgive "
                    "this for a generation."
                ),
                outcome_line=(
                    "*\"The deepest mercy. They will not have to fear.\"*"
                ),
                side_effect=_uplift_cleanse,
            ),
        ),
        prereq_flag="observed_proto_uq",
        resolved_flag="uplift_dilemma_resolved",
    ),
    CouncilRecommendation(
        id="mycon_whisper",
        title="The Mycon Whisper — Deep Child emergence",
        context=(
            "The Mycon biot mass is showing signs of sentience "
            "nucleation. A subset of the spore-network is developing "
            "what the Mycon call the *Deep Child whisper* — an "
            "emergent self. Allowed to mature, this becomes a new "
            "sapient species (a Migration case the Council had not "
            "planned for). Suppressed, the biots remain "
            "terraforming tools. The Council requires a recommendation."
        ),
        options=(
            CouncilOption(
                id="suppress",
                label="Suppress the emergence",
                summary=(
                    "Halt the Deep Child nucleation. The biots stay "
                    "pre-sentient and continue terraforming. SC2-"
                    "canon-clean. Hider faction approves."
                ),
                outcome_line=(
                    "*\"The seed does not grow. The mantle stays quiet.\"*"
                ),
                side_effect=_mycon_suppress,
            ),
            CouncilOption(
                id="allow",
                label="Allow the emergence — build them out",
                summary=(
                    "Let the Deep Child wake. A new sentient species "
                    "joins the Migration roster — but their mycelial "
                    "roots make standard evacuation difficult. They "
                    "will need a cloak or a Bio-Architect-mediated "
                    "lift. Persuader-aligned."
                ),
                outcome_line=(
                    "*\"Welcome to the chamber, Deep Child.\"*"
                ),
                side_effect=_mycon_allow,
            ),
            CouncilOption(
                id="cleanse_heretical",
                label="Cleanse the emerging subset only",
                summary=(
                    "The Deep-Child-stirred biot population is "
                    "euthanized; the bulk of the biot mass continues "
                    "as terraforming tools. Cleanser-aligned. The "
                    "Persuader bench dissents."
                ),
                outcome_line=(
                    "*\"A surgical mercy.\"*"
                ),
                side_effect=_mycon_cleanse_heretical,
            ),
            CouncilOption(
                id="ignore",
                label="Allow + ignore — no Council provision",
                summary=(
                    "Let the Deep Child wake without making provision "
                    "for their evacuation. The Others arrive; the "
                    "biots are consumed. Denier-aligned. *Persuaders "
                    "will not forget.*"
                ),
                outcome_line=(
                    "*\"We will not concern ourselves with what was "
                    "never our problem.\"*"
                ),
                side_effect=_mycon_ignore,
            ),
        ),
        prereq_flag="met_mycon",
        resolved_flag="mycon_whisper_resolved",
    ),
    CouncilRecommendation(
        id="dnyarri_briefing",
        title="Proto-Dnyarri briefing — Beta Orionis log",
        context=(
            "Survey Commander Vesh Vasa-Lon's Beta Orionis detail has "
            "received the Steward's initial recommendation on the "
            "proto-Dnyarri psionic precursor question. The Council "
            "logs the recommendation for the slice ledger. No further "
            "deliberation; the call has been made."
        ),
        options=(
            CouncilOption(
                id="acknowledge",
                label="Acknowledge and log",
                summary=(
                    "Council records the prior recommendation. No "
                    "re-decision; no faction-standing shift."
                ),
                outcome_line=(
                    "*\"The file is closed. The frogs sing at dusk.\"*"
                ),
                side_effect=_dnyarri_ack,
            ),
        ),
        prereq_flag="met_dnyarri_survey",
        resolved_flag="dnyarri_briefing_resolved",
        read_only=True,
    ),
)


def open_recommendations(game: "Game") -> list[CouncilRecommendation]:
    """Return the list of recommendations the player can act on right
    now — prereq flag truthy, resolved flag falsy.
    """
    flags = game.flags
    return [
        r for r in RECOMMENDATIONS
        if flags.get(r.prereq_flag) and not flags.get(r.resolved_flag)
    ]


def any_open(game: "Game") -> bool:
    """True iff at least one Council recommendation is awaiting action.
    Drives the StationScene "Convene Council" menu-item visibility.
    """
    return bool(open_recommendations(game))


def faction_standing(game: "Game") -> dict[str, int]:
    """Return the player's current faction standing, with missing
    factions defaulting to 0. Lazy-initializes the underlying dict if
    no faction shifts have been recorded yet.
    """
    standing = game.flags.get("faction_standing")
    if not isinstance(standing, dict):
        return {f: 0 for f in FACTIONS}
    return {f: int(standing.get(f, 0)) for f in FACTIONS}
