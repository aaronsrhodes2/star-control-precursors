"""Generate the Hyperspace theme as 5 coherent stems via ElevenLabs Music.

Per references/lore/music-system.md, each slice context is composed
as 4-6 stems that the game mixes at runtime. The Hyperspace identity
is "mid-tempo, propulsive, the player's 'ship at speed' theme."

Coherence across stems is enforced by:
- Identical key + bpm baked into every stem prompt ("in C minor at
  108 bpm")
- Identical duration
- Identical descriptor anchor ("sci-fi space-flight atmosphere")

The script uses tools/eleven_music.py (ElevenLabs Music API) — the
asset-time generation path per Aaron's 2026-05-17 directive. The
local audio-server (AudioLDM2-Music) stays in tree for the runtime
variance engine but isn't used here.

Outputs land in assets/music/hyperspace/<stem>.wav (44.1 kHz stereo
PCM_16) and a manifest.json alongside.

Usage:
    .venv/Scripts/python.exe tools/audio_generate_hyperspace.py
"""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from eleven_music import music, save_wav


ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = ROOT / "assets" / "music" / "hyperspace"

# Shared compositional anchor — every stem references these so they
# line up at mix time. ElevenLabs Music has no `seed` in prompt mode
# (it's gated to composition_plan), so determinism comes from
# committing the .wav to git, not from the API call.
KEY = "C minor"
BPM = 108
DURATION_S = 30

# 5 stems with prompts. Order = bottom-up in the mix (bass first,
# ambient last) so I can think about layering. Each prompt front-
# loads "Isolated <ROLE> STEM for layered production" because
# ElevenLabs Music is more responsive to high-level musical framing
# than AudioLDM2; the explicit "stems-only mix" tail-clause helps it
# avoid layering in the other instruments.
STEMS = [
    (
        "bass",
        f"Isolated BASS STEM for layered production: deep analog synth "
        f"bassline, mid-tempo propulsive groove, in {KEY} at {BPM} bpm, "
        f"sci-fi space-flight atmosphere, no drums no melody no pads, "
        f"stems-only mix",
    ),
    (
        "percussion",
        f"Isolated DRUMS STEM for layered production: gated kick-and-hat "
        f"pattern, mid-tempo four-on-the-floor with subtle space-fx claps, "
        f"in {KEY} at {BPM} bpm, sci-fi space-flight atmosphere, no melody "
        f"no bass no pads, stems-only mix",
    ),
    (
        "pad",
        f"Isolated PAD STEM for layered production: warm analog synth pad, "
        f"long sustained chords, atmospheric and propulsive, in {KEY} at "
        f"{BPM} bpm, sci-fi space-flight texture, no melody no drums no "
        f"bass, stems-only mix",
    ),
    (
        "lead",
        f"Isolated LEAD MELODY STEM for layered production: mid-tempo "
        f"synth arpeggio, hopeful melodic phrase, in {KEY} at {BPM} bpm, "
        f"sci-fi space-flight feel, no drums no bass no pads, stems-only mix",
    ),
    (
        "ambient",
        f"Isolated AMBIENT TEXTURE STEM for layered production: subtle "
        f"space drone wash, distant cosmic wind, sparkles, in {KEY} at "
        f"{BPM} bpm, no melody no drums no bass, stems-only mix",
    ),
]


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    manifest = {
        "context": "hyperspace",
        "key": KEY,
        "bpm": BPM,
        "duration_s": DURATION_S,
        "backend": "elevenlabs-music_v1",
        "stems": {},
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }

    for name, prompt in STEMS:
        out = OUT_DIR / f"{name}.wav"
        print(f"\n=== {name} ({DURATION_S}s) ===", flush=True)
        print(f"  prompt: {prompt[:90]}...", flush=True)
        t0 = time.time()
        try:
            audio, sr = music(prompt=prompt, duration_s=DURATION_S)
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
