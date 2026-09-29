"""State-driven stem volumes — the per-species twist in the music system.

Per the music-system.md design, each species theme has disposition-tied
stems that fade in/out based on the player's relationship with the
species:
- Slylandro theme has an `awe` stem and a `worry` stem (both 0-1).
- Mycon theme has an `obedience` stem and a `heresy` stem.
- Arilou theme has a `patience` stem.

This module owns the mapping from a species' current disposition
state (read from game.flags / dialog_character disposition counters)
to per-stem volume values that the StemMixer applies.

Each species has a `StateLayerSpec` that lists which stems are state-
driven and a function that maps the disposition state to (stem_name,
volume) pairs. The director calls evaluate() once per frame (or once
per disposition change) and pushes the result into the mixer.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable


# Type alias for the per-frame evaluator: takes the game (so it can
# read flags/dispositions) and returns {stem_name: volume} for the
# state-driven stems.
EvaluatorFn = Callable[[Any], dict[str, float]]


@dataclass(frozen=True)
class StateLayerSpec:
    """One species' state-layer configuration."""
    context: str                  # the music context this binds to
    species_id: str               # the species whose state drives this
    state_driven_stems: tuple[str, ...]  # which stems are state-controlled
    evaluator: EvaluatorFn        # current-disposition → stem volumes
    description: str = ""


# ---------------------------------------------------------------------------
# Slylandro: awe vs worry. As the player builds rapport, awe rises;
# as they push toward Cleanse, worry rises.
# ---------------------------------------------------------------------------

def _slylandro_eval(game: Any) -> dict[str, float]:
    if game is None:
        return {"awe": 0.5, "worry": 0.5}
    flags = getattr(game, "flags", {}) or {}
    awe = max(0.0, min(1.0, float(flags.get("slylandro_awe", 0.5))))
    worry = max(0.0, min(1.0, float(flags.get("slylandro_worry", 0.5))))
    return {"awe": awe, "worry": worry}


SLYLANDRO_LAYERS = StateLayerSpec(
    context="slylandro",
    species_id="SLYLANDRO",
    state_driven_stems=("awe", "worry"),
    evaluator=_slylandro_eval,
    description="awe rises with friendly contact; worry rises near "
                "Cleanse-path decisions",
)


# ---------------------------------------------------------------------------
# Mycon biot: obedience vs heresy. The Deep Child whispers raise the
# heresy volume; the player's intervention lowers it.
# ---------------------------------------------------------------------------

def _mycon_eval(game: Any) -> dict[str, float]:
    if game is None:
        return {"obedience": 1.0, "heresy": 0.0}
    flags = getattr(game, "flags", {}) or {}
    heresy = max(0.0, min(1.0, float(flags.get("mycon_heresy_level", 0.0))))
    obedience = 1.0 - heresy   # inverse for now
    return {"obedience": obedience, "heresy": heresy}


MYCON_LAYERS = StateLayerSpec(
    context="mycon",
    species_id="MYCON_BIOT",
    state_driven_stems=("obedience", "heresy"),
    evaluator=_mycon_eval,
    description="heresy rises with Deep Child progress; obedience is "
                "its inverse and dims as awakening completes",
)


# ---------------------------------------------------------------------------
# Arilou: patience. Drops as the player ignores Sage warnings or
# argues. Starts high and only ever decreases in the slice arc.
# ---------------------------------------------------------------------------

def _arilou_eval(game: Any) -> dict[str, float]:
    if game is None:
        return {"patience": 1.0}
    flags = getattr(game, "flags", {}) or {}
    patience = max(0.0, min(1.0, float(flags.get("arilou_patience", 1.0))))
    return {"patience": patience}


ARILOU_LAYERS = StateLayerSpec(
    context="arilou",
    species_id="ARILOU",
    state_driven_stems=("patience",),
    evaluator=_arilou_eval,
    description="patience starts 1.0 and only decreases; stem fully "
                "fades out when the Sage gives up on the Steward",
)


# ---------------------------------------------------------------------------
# Lookup
# ---------------------------------------------------------------------------

ALL_STATE_LAYERS: dict[str, StateLayerSpec] = {
    spec.context: spec
    for spec in (SLYLANDRO_LAYERS, MYCON_LAYERS, ARILOU_LAYERS)
}


def get_state_layers(context: str) -> StateLayerSpec | None:
    """Return the StateLayerSpec for a context if one exists; else None."""
    return ALL_STATE_LAYERS.get(context)
