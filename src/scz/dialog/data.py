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
# award resources, transition scenes, etc.). Returns either None (no
# override — DialogScene follows the choice's static next_state_id) OR
# a string state id (override — DialogScene jumps there instead). Used
# for conditional routing like "did the purchase succeed?".
SideEffectFn = Callable[[Any], "str | None"]


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


@dataclass(frozen=True)
class Joint:
    """A named pivot point on a character body, normalized to the avatar
    image (0,0 = top-left, 1,1 = bottom-right). The renderer does NOT
    use these for transforms yet — they're documentation for the future
    PortraitAnimator that the variation layer will wire up (likely using
    Flask-SD per-frame generation). For now, they exist so prompts can
    cite specific joints and so handed-off characters carry the rig
    description with them.
    """

    name: str                          # e.g. "head", "shoulder_l", "tendril_3"
    pivot: tuple[float, float]         # normalized (x, y) in [0, 1]
    rot_range_rad: tuple[float, float] = (-0.1, 0.1)
    # Rough size hint for downstream cropping/masking when frames are
    # generated independently. Normalized to avatar dims.
    size_hint: tuple[float, float] = (0.1, 0.1)


@dataclass(frozen=True)
class ArticulationSpec:
    """Describes a character's articulation rig — which body parts can
    move and roughly how. Currently consumed only by the prompt-authoring
    layer; the PortraitAnimator will use it when frame banks land."""

    rig_type: str                      # "bipedal_humanoid", "gasbag_tendril", ...
    joints: tuple[Joint, ...]
    # Procedural-animation tuning specific to this rig. The dialog scene's
    # default sway/breath constants are overridden by these when present.
    breath_amplitude_px: float = 1.5
    sway_amplitude_px: float = 2.0
    speak_bob_amplitude_px: float = 1.5
    # Optional head-tilt rotation amplitude (radians) for the procedural
    # animator. 0 = translation only; > 0 = the whole avatar rotates
    # slightly during speech. Read by DialogScene when wiring articulation
    # to the render path.
    speak_tilt_amplitude_rad: float = 0.0


@dataclass(frozen=True)
class BackgroundSpec:
    """A scene-setting backdrop image for a character. A character can
    carry several (e.g. their ship bridge, their planet surface, your
    own ship) so the dialog scene can vary the setting per encounter.

    The dialog scene currently picks `backgrounds[0]` whenever an avatar
    is being rendered; the future variation layer will rotate through
    them based on encounter context."""

    name: str                          # e.g. "ship_bridge", "planet_surface"
    image_path: str                    # project-relative
    description: str = ""


@dataclass
class DialogCharacter:
    """All the data for one conversational NPC.

    name + title are displayed in the dialog header. portrait_color is a
    placeholder used as the fill color of a portrait disc when no portrait
    image is available. species_id keys into the warp-pod palette so the
    dialog visual can match the ship visual.

    Visual fields (two render paths in DialogScene):

    portrait_image_path (legacy): path to a single static PNG combining
    character + backdrop, rendered as a circular disc in the upper-left.
    Backwards-compatible with characters authored before the layered
    render path landed.

    avatar_path + backgrounds + articulation (layered): when avatar_path
    is set, DialogScene renders a rectangular scene panel instead — first
    the selected background, then the transparent-PNG avatar with
    procedural animation on top. backgrounds is a tuple of scene-setting
    backdrops the character can appear against; articulation describes
    the body rig so the variation-layer animator can wire per-joint
    transforms later. If avatar_path is set but backgrounds is empty,
    the panel falls back to a dark-navy fill.

    initial_state names which state to enter first; states is the FSM.
    """

    name: str
    title: str
    species_id: str
    portrait_color: tuple[int, int, int]
    initial_state: str
    states: dict[str, DialogState]
    portrait_image_path: str | None = None
    # Layered-render fields (all optional; set together when migrating)
    avatar_path: str | None = None
    backgrounds: tuple[BackgroundSpec, ...] = ()
    articulation: ArticulationSpec | None = None


def build_state_dict(*states: DialogState) -> dict[str, DialogState]:
    """Helper: turn a sequence of DialogStates into the dict keyed by id."""
    return {s.id: s for s in states}
