"""Generate the Hyperspace theme as 5 coherent stems via the audio-server.

Per references/lore/music-system.md, each slice context is composed
as 4-6 stems that the game mixes at runtime. The Hyperspace identity
is "mid-tempo, propulsive, the player's 'ship at speed' theme."

Coherence across stems is enforced by:
- Identical key + bpm baked into every stem prompt ("in C minor at
  108 bpm")
- Same seed for all 5 calls (Stable Audio Open seeds the prompt
  noise too, so a shared seed gives related musical motion)
- Identical duration

Outputs land in assets/music/hyperspace/<stem>.wav and the manifest
file alongside.

Usage:
    .venv/Scripts/python.exe tools/audio_generate_hyperspace.py
"""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from audio_client import music, save_wav, health


ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = ROOT / "assets" / "music" / "hyperspace"

# Shared compositional anchor — every stem references these so they
# line up at mix time.
KEY = "C minor"
BPM = 108
DURATION_S = 30
SEED = 731  # deterministic; rerun gives same audio

# 5 stems with prompts. Order = bottom-up in the mix (bass first,
# ambient last) so I can think about layering.
STEMS = [
    (
        "bass",
        f"Sci-fi space flight music, BASS-ONLY stem, deep analog synth "
        f"bassline, mid-tempo propulsive groove, in {KEY} at {BPM} bpm, "
        f"no melody no drums no pads, isolated bass track",
    ),
    (
        "percussion",
        f"Sci-fi space flight music, DRUMS-ONLY stem, gated kick-and-hat "
        f"pattern, mid-tempo four-on-the-floor with subtle space-fx claps, "
        f"in {KEY} at {BPM} bpm, no melody no bass no pads, isolated "
        f"percussion track",
    ),
    (
        "pad",
        f"Sci-fi space flight music, PAD-ONLY stem, warm analog synth pad, "
        f"long sustained chords, atmospheric and propulsive, in {KEY} at "
        f"{BPM} bpm, no melody no drums no bass, isolated pad track",
    ),
    (
        "lead",
        f"Sci-fi space flight music, LEAD MELODY-ONLY stem, mid-tempo "
        f"synth arpeggio, hopeful melodic phrase, in {KEY} at {BPM} bpm, "
        f"no drums no bass no pads, isolated lead melody track",
    ),
    (
        "ambient",
        f"Sci-fi space flight music, AMBIENT TEXTURE-ONLY stem, subtle "
        f"space drone wash, distant cosmic wind, sparkles, in {KEY} at "
        f"{BPM} bpm, no melody no drums no bass, isolated atmosphere track",
    ),
]


def main() -> int:
    try:
        h = health()
        print(f"audio server: {h}", flush=True)
    except Exception as e:
        print(f"ERROR: audio server unreachable: {e}", file=sys.stderr)
        return 1

    OUT_DIR.mkdir(parents=True, exist_ok=True)

    manifest = {
        "context": "hyperspace",
        "key": KEY,
        "bpm": BPM,
        "duration_s": DURATION_S,
        "seed": SEED,
        "stems": {},
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }

    for name, prompt in STEMS:
        out = OUT_DIR / f"{name}.wav"
        print(f"\n=== {name} ({DURATION_S}s) ===", flush=True)
        print(f"  prompt: {prompt[:90]}...", flush=True)
        t0 = time.time()
        try:
            audio, sr = music(prompt=prompt, duration=DURATION_S, seed=SEED)
        except Exception as e:
            print(f"  FAIL: {e}", flush=True)
            continue
        save_wav(audio, sr, out)
        sz_mb = out.stat().st_size / 1e6
        print(f"  saved {out.relative_to(ROOT)} ({sr}Hz, {sz_mb:.1f} MB) in {time.time()-t0:.1f}s", flush=True)
        manifest["stems"][name] = {
            "path": str(out.relative_to(ROOT)).replace("\\", "/"),
            "prompt": prompt,
            "sample_rate": sr,
        }

    manifest_path = OUT_DIR / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(f"\nwrote {manifest_path.relative_to(ROOT)}")
    print(f"\n=== done: {len(manifest['stems'])}/{len(STEMS)} ===")
    return 0


if __name__ == "__main__":
    sys.exit(main())
