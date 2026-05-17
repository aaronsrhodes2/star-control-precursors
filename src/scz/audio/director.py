"""Music director — picks the active track per scene context and
configures the StemMixer with variation knobs + state-driven layers.

The director is owned by the engine (one instance per game). Scenes
call `set_context(context_name)` when they enter (e.g. HyperspaceScene
sets "hyperspace" on enter), and call `update(dt)` per frame so the
mixer can ramp volumes.

Variation knobs implemented this version:
- Stem mute: per playback, mute 0-2 random stems for a thinner texture.
- State-driven layers: pulls disposition values from the game and
  pushes per-stem volumes to the mixer.

Knobs DEFERRED to a future pass (per the lore doc):
- Tempo jitter (needs pre-rendered tempo variants OR runtime resampling)
- Key transposition (needs pre-rendered pitch-shifted variants)
- Lead instrument swap (needs alternate "lead-*.wav" stem files)
- Section reorder (needs section markers in stems)
- Density modulation (needs sparse/full variants)

These can be added without changing this module's external interface:
`set_context(ctx)` and `update(dt)`.
"""

from __future__ import annotations

import logging
import random
from pathlib import Path
from typing import Any, Optional

from scz.audio.mixer import StemMixer
from scz.audio.state_layers import get_state_layers


log = logging.getLogger("scz.audio.director")


# Where the build-time stem files live. Each context is one subdirectory
# under this root, e.g. assets/music/hyperspace/{bass,lead,pad,...}.wav.
def _music_root() -> Path:
    # src/scz/audio/director.py -> project root is 4 parents up
    return Path(__file__).resolve().parent.parent.parent.parent / "assets" / "music"


class MusicDirector:
    """Picks tracks and configures the StemMixer per scene context."""

    def __init__(self, mixer: StemMixer, *, seed: int | None = None) -> None:
        self.mixer = mixer
        self._rng = random.Random(seed)
        self._current_context: Optional[str] = None
        # Per-context seed cache so a given context's variation is
        # consistent across re-entry within one play session.
        self._context_seeds: dict[str, int] = {}

    # ----- Scene-facing API -----

    def set_context(self, context: str, game: Any = None) -> None:
        """Called by scenes when they enter. Loads the track for the
        context, applies variation knobs, and pushes to the mixer.

        `game` is passed through to the state-layer evaluator so it
        can read disposition flags."""
        if context == self._current_context:
            # Same context — just refresh state-driven layers and
            # let the music keep going.
            if game is not None:
                self._apply_state_layers(context, game)
            return

        ctx_dir = _music_root() / context
        if not ctx_dir.is_dir():
            log.warning("no track directory for context %s at %s", context, ctx_dir)
            self.mixer.fade_out_all()
            self._current_context = context
            return

        # Variation knob 1: stem mute. Roll which (if any) stems to
        # silence this playback. Deterministic per-context seed so the
        # variation is stable across re-entries within a session.
        seed = self._context_seeds.setdefault(
            context, self._rng.randint(0, 1_000_000),
        )
        variation_rng = random.Random(seed)
        track = self.mixer.load_track(context, ctx_dir)
        stem_names = list(track.stems.keys())
        # State-driven stems should NEVER be muted — they're the
        # narrative signal. Skip them from the mute pool.
        state_spec = get_state_layers(context)
        protected = set(state_spec.state_driven_stems) if state_spec else set()
        mutable = [s for s in stem_names if s not in protected]
        n_mute = variation_rng.choice([0, 0, 0, 1, 1, 2])   # weighted
        muted: set[str] = set()
        if mutable and n_mute > 0:
            muted = set(variation_rng.sample(mutable, min(n_mute, len(mutable))))
        if muted:
            log.info("context=%s muting stems: %s", context, ", ".join(sorted(muted)))

        # Initial volumes: muted stems start at 0, others at 1.
        vols = {name: (0.0 if name in muted else 1.0) for name in stem_names}
        # State-driven stems start at the current disposition values
        # (will be re-applied each update too)
        if state_spec and game is not None:
            for name, v in state_spec.evaluator(game).items():
                if name in vols:
                    vols[name] = v

        self.mixer.play_context(context, ctx_dir, stem_volumes=vols)
        self._current_context = context

    def update(self, dt: float, game: Any = None) -> None:
        """Per-frame: ramps + state-driven layer refresh."""
        if game is not None and self._current_context is not None:
            self._apply_state_layers(self._current_context, game)
        self.mixer.update(dt)

    def stop(self) -> None:
        self.mixer.fade_out_all()
        self._current_context = None

    # ----- Internal -----

    def _apply_state_layers(self, context: str, game: Any) -> None:
        spec = get_state_layers(context)
        if spec is None:
            return
        for stem_name, vol in spec.evaluator(game).items():
            self.mixer.set_stem_volume(stem_name, vol)
