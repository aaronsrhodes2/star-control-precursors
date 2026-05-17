"""Smoke-test the runtime audio system without depending on the
audio-server. Generates 5 short synthetic sine-wave stems (one
sustained note per stem in C-minor harmony), writes them to a
temp track dir, instantiates StemMixer + MusicDirector, plays
them, exercises volume ramps + state layers, then exits.

Use as a sanity test of src/scz/audio/ when changing the runtime
code. Stems will be silent in a CI/headless context if pygame
can't open the audio device, but the StemMixer code paths are
still exercised.

    .venv/Scripts/python.exe tools/audio_smoke_test.py
"""

from __future__ import annotations

import json
import math
import os
import sys
import tempfile
import time
from pathlib import Path

import numpy as np
import soundfile as sf

# Make src importable
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

import pygame  # noqa: E402

from scz.audio.mixer import StemMixer  # noqa: E402
from scz.audio.director import MusicDirector  # noqa: E402


SAMPLE_RATE = 44100
DURATION_S = 4.0


def _sine(freq_hz: float, duration_s: float = DURATION_S, amplitude: float = 0.15):
    """Return a single-channel sine wave as float32."""
    t = np.arange(int(SAMPLE_RATE * duration_s), dtype=np.float32) / SAMPLE_RATE
    return amplitude * np.sin(2 * np.pi * freq_hz * t).astype(np.float32)


def _write_stems(track_dir: Path) -> None:
    """C-minor chord stems (rough sketch of a track)."""
    track_dir.mkdir(parents=True, exist_ok=True)
    # 5 stems at C-minor harmony — bass C3 (~131), perc rim ~200,
    # pad Eb4 (~311), lead G4 (~392), ambient C5 (~523).
    stems = {
        "bass":       _sine(131.0),
        "percussion": _sine(200.0),
        "pad":        _sine(311.0),
        "lead":       _sine(392.0),
        "ambient":    _sine(523.0),
    }
    for name, audio in stems.items():
        sf.write(track_dir / f"{name}.wav", audio, SAMPLE_RATE)
    # Minimal manifest matching the production format
    manifest = {
        "context": "hyperspace",
        "key": "C minor",
        "bpm": 108,
        "duration_s": DURATION_S,
        "stems": {
            name: {
                "path": f"assets/music/hyperspace/{name}.wav",
                "sample_rate": SAMPLE_RATE,
                "prompt": "(synthetic sine wave for smoke test)",
            }
            for name in stems
        },
    }
    (track_dir / "manifest.json").write_text(json.dumps(manifest, indent=2))


def _try_init_mixer() -> bool:
    """Return True if pygame.mixer can be initialized in this env.
    Headless / no-audio-device boxes return False and we skip the
    actual playback portion; the mixer code paths still get
    exercised against the no-op channel."""
    try:
        pygame.mixer.pre_init(frequency=SAMPLE_RATE, channels=1, buffer=512)
        pygame.mixer.init()
        return True
    except pygame.error as e:
        print(f"  (no audio device: {e})")
        return False


def main() -> int:
    print("== scz audio runtime smoke test ==")
    with tempfile.TemporaryDirectory() as tmp:
        # Real test wants the stems under assets/music for the StemMixer's
        # default lookup. Use tempdir-as-project-root to avoid polluting.
        proj = Path(tmp)
        track_dir = proj / "assets" / "music" / "hyperspace"
        _write_stems(track_dir)
        print(f"  wrote 5 sine stems to {track_dir}")

        if not _try_init_mixer():
            print("  skipping playback portion (no audio device)")
            return 0

        mixer = StemMixer(channel_count=8)
        mixer.bootstrap(frequency=SAMPLE_RATE, channels_stereo=1)

        # Load the track + start playback
        track = mixer.load_track("hyperspace", track_dir)
        assert len(track.stems) == 5, f"expected 5 stems, got {len(track.stems)}"
        print(f"  loaded {len(track.stems)} stems: {sorted(track.stems.keys())}")

        # Play with all stems at full volume
        mixer.play_context("hyperspace", track_dir)
        print("  started playback at 1.0 volume per stem")

        # Run the update loop for ~1.5s to let volumes ramp up
        for _ in range(60):
            mixer.update(1 / 60)
            time.sleep(1 / 60)

        # Fade out the percussion stem to demonstrate state-driven
        # volume control
        mixer.set_stem_volume("percussion", 0.0)
        print("  faded percussion to 0.0")
        for _ in range(60):
            mixer.update(1 / 60)
            time.sleep(1 / 60)

        # Fade everything out
        mixer.fade_out_all(rate=4.0)
        print("  fade-out all")
        for _ in range(60):
            mixer.update(1 / 60)
            time.sleep(1 / 60)

        mixer.shutdown()
        pygame.mixer.quit()
        print("== OK ==")
        return 0


if __name__ == "__main__":
    sys.exit(main())
