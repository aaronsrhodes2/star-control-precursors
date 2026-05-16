"""Dialog data structures: DialogState, DialogChoice, DialogCharacter.

These define the deterministic conversation FSM. Each character carries a
state graph; states have NPC text and a list of player choices; choices
transition to new states (or terminate the conversation).

The architecture per [species-precursor-era.md](../../references/lore/species-precursor-era.md):
- Game logic = the FSM (states + transitions + side effects). Deterministic.
- LLM = renders `npc_text` and `choice_text` into species-voice surface
  text. Not yet wired; canned strings flow through to the screen for now.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any


# Side-effect callback signature: takes the game (so it can set flags,
# award resources, transition scenes, etc.) and returns nothing.
SideEffectFn = Callable[[Any], None]


@dataclass
class DialogChoice:
    """One option a player can pick at a given state."""

    # Surface text shown to the player. (LLM will render this from intent
    # later; canned for now.)
    text: str
    # State ID to transition to; None means "end the conversation" (and
    # close the Dialog scene, returning to the parent).
    next_state_id: str | None = None
    # Optional callback that mutates game state when this choice is made.
    side_effect: SideEffectFn | None = None
    # Semantic category for the LLM later (FIGHT / TALK / AGREE / etc.).
    category: str = "TALK"


@dataclass
class DialogState:
    """One state in a character's dialog FSM.

    npc_text is rendered as the character's speech for the duration of
    this state. choices are the player's options out of this state.
    """

    id: str
    npc_text: str
    choices: list[DialogChoice] = field(default_factory=list)
    # If True, the dialog auto-closes when this state is entered (used for
    # one-off "Good hunting, Steward." farewell states with no choice list).
    is_terminal: bool = False


@dataclass
class DialogCharacter:
    """All the data for one conversational NPC.

    name + title are displayed in the dialog header. portrait_color is a
    placeholder until we have Flask-SD-generated species portraits — it's
    used as the fill color of a portrait disc. species_id keys into the
    warp-pod palette so the dialog visual can match the ship visual.
    initial_state names which state to enter first; states is the FSM.
    """

    name: str
    title: str
    species_id: str
    portrait_color: tuple[int, int, int]
    initial_state: str
    states: dict[str, DialogState]


def build_state_dict(*states: DialogState) -> dict[str, DialogState]:
    """Helper: turn a sequence of DialogStates into the dict keyed by id."""
    return {s.id: s for s in states}
