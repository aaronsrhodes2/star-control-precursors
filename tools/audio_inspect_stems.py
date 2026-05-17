"""Validate a directory of generated music stems.

For each .wav in the track dir, prints:
- duration (s) and sample rate
- channel count
- peak amplitude (should be < 1.0 for headroom)
- RMS amplitude (should be reasonably high — silent stems = bad)
- NaN / Inf check
- file size

Flags suspicious stems (silent, clipped, NaN, mismatched duration vs the
manifest). Doesn't try to score "musical quality" — that's an ear job.

Usage:
    .venv/Scripts/python.exe tools/audio_inspect_stems.py assets/music/hyperspace
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import soundfile as sf


def _inspect(wav_path: Path) -> dict:
    audio, sr = sf.read(wav_path)
    info: dict = {"path": str(wav_path), "sr": sr}
    if audio.ndim == 1:
        info["channels"] = 1
        mono = audio
    else:
        info["channels"] = audio.shape[1]
        mono = audio.mean(axis=1)
    info["duration_s"] = round(len(mono) / sr, 2)
    info["peak"] = float(np.abs(mono).max()) if len(mono) else 0.0
    info["rms"] = float(np.sqrt((mono.astype(np.float64) ** 2).mean())) if len(mono) else 0.0
    info["has_nan"] = bool(np.isnan(audio).any())
    info["has_inf"] = bool(np.isinf(audio).any())
    info["size_mb"] = round(wav_path.stat().st_size / 1e6, 2)
    return info


def _flag(info: dict, expected_duration: float | None) -> list[str]:
    flags = []
    if info["has_nan"]:
        flags.append("NaN")
    if info["has_inf"]:
        flags.append("Inf")
    if info["peak"] >= 1.0:
        flags.append("CLIPPED")
    if info["rms"] < 0.005:
        flags.append("NEAR-SILENT")
    if expected_duration is not None and abs(info["duration_s"] - expected_duration) > 0.5:
        flags.append(f"DUR≠{expected_duration:.0f}s")
    return flags


def main(argv: list[str]) -> int:
    if len(argv) < 2:
        print("usage: audio_inspect_stems.py <track-dir>", file=sys.stderr)
        return 2
    track_dir = Path(argv[1])
    if not track_dir.is_dir():
        print(f"not a dir: {track_dir}", file=sys.stderr)
        return 2

    manifest_path = track_dir / "manifest.json"
    expected_duration: float | None = None
    if manifest_path.exists():
        m = json.loads(manifest_path.read_text(encoding="utf-8"))
        expected_duration = m.get("duration_s")
        print(f"manifest: context={m.get('context')!r} key={m.get('key')!r} "
              f"bpm={m.get('bpm')} duration={m.get('duration_s')}s "
              f"seed={m.get('seed')}")

    wavs = sorted(track_dir.glob("*.wav"))
    if not wavs:
        print("no .wav files found", file=sys.stderr)
        return 1

    print(f"\n{'stem':<14} {'dur':<6} {'sr':<7} {'ch':<3} {'peak':<6} {'rms':<7} {'size':<7} flags")
    print("-" * 70)
    any_flag = False
    for p in wavs:
        info = _inspect(p)
        flags = _flag(info, expected_duration)
        flag_str = " ".join(flags) if flags else ""
        if flags:
            any_flag = True
        print(f"{p.stem:<14} {info['duration_s']:<6} "
              f"{info['sr']:<7} {info['channels']:<3} "
              f"{info['peak']:<6.3f} {info['rms']:<7.4f} "
              f"{info['size_mb']:<6.2f}MB {flag_str}")
    print()
    return 1 if any_flag else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
