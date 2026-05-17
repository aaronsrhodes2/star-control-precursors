"""Generic sound-effect generator.

Consumes SfxSpec entries from tools/audio_sfx_specs.py and fires one
ElevenLabs sound-generation call per spec. Writes the audio file under
assets/sfx/<out_subdir>/<name>.wav.

We save .wav (not .mp3) because the ElevenLabs SFX endpoint has a known
tendency to output very quiet audio (peaks of 0.05-0.15 instead of
0.7-0.9 like music does). We must normalize to be playable; that
requires decoding the response, so we save the normalized result as
lossless PCM_16 WAV. File-size cost is ~7 MB across all 74 SFX --
trivially acceptable.

No per-context manifest -- SFX are leaf assets keyed by filename; the
spec module is the inventory of record.

Usage:
    .venv/Scripts/python.exe tools/audio_sfx_generate.py --list
    .venv/Scripts/python.exe tools/audio_sfx_generate.py menu_select
    .venv/Scripts/python.exe tools/audio_sfx_generate.py --round 1
    .venv/Scripts/python.exe tools/audio_sfx_generate.py --category ui
"""

from __future__ import annotations

import argparse
import io
import sys
import time
from pathlib import Path

import numpy as np
import soundfile as sf

sys.path.insert(0, str(Path(__file__).resolve().parent))
from audio_sfx_specs import (  # noqa: E402
    SfxSpec, ALL_SFX, by_category, for_round,
)
from eleven_sfx import sfx_bytes, DEFAULT_OUTPUT_FORMAT  # noqa: E402


NORMALIZE_TARGET_PEAK = 0.9      # any peak below this scales up to here
NORMALIZE_FLOOR_PEAK = 0.5       # peaks at/above this are left alone


ROOT = Path(__file__).resolve().parent.parent
OUT_ROOT = ROOT / "assets" / "sfx"


def _decode_and_normalize(data: bytes) -> tuple[np.ndarray, int, float]:
    """Decode the API response (MP3) and normalize to a usable peak.

    Returns (audio_array, sample_rate, applied_gain). Gain of 1.0 means
    the source already had a healthy peak; > 1.0 means we boosted it."""
    audio, sr = sf.read(io.BytesIO(data))
    audio = audio.astype(np.float32)
    peak = float(np.abs(audio).max()) if audio.size else 0.0
    if peak >= NORMALIZE_FLOOR_PEAK:
        return audio, sr, 1.0
    if peak < 1e-6:
        # Nearly-silent output -- can't normalize a zero signal.
        return audio, sr, 1.0
    gain = NORMALIZE_TARGET_PEAK / peak
    return np.clip(audio * gain, -1.0, 1.0), sr, gain


def generate_one(
    spec: SfxSpec,
    *,
    output_format: str = DEFAULT_OUTPUT_FORMAT,
    overwrite: bool = True,
) -> Path | None:
    """Generate a single SFX. Returns the path written, or None on failure.

    Always writes .wav (PCM_16) after normalizing. ElevenLabs SFX has a
    known tendency to output very quiet audio (peaks of 0.05-0.15)
    that's inaudible without boosting; we normalize anything below
    peak 0.5 up to peak 0.9. MP3 path is bypassed because we need to
    decode anyway."""
    out_dir = OUT_ROOT / spec.out_subdir
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{spec.name}.wav"
    if out_path.exists() and not overwrite:
        print(f"  skip {out_path.relative_to(ROOT)} (exists)", flush=True)
        return out_path
    print(f"\n  === {spec.category}/{spec.out_subdir}/{spec.name} ===", flush=True)
    print(f"    duration: {spec.duration_s}s loop: {spec.loop} "
          f"infl: {spec.prompt_influence}", flush=True)
    print(f"    prompt: {spec.prompt[:110]}{'...' if len(spec.prompt) > 110 else ''}", flush=True)
    t0 = time.time()
    try:
        data, fmt = sfx_bytes(
            text=spec.prompt,
            duration_s=spec.duration_s,
            prompt_influence=spec.prompt_influence,
            loop=spec.loop,
            output_format=output_format,
        )
    except Exception as e:
        print(f"    FAIL: {e}", flush=True)
        return None
    audio, sr, gain = _decode_and_normalize(data)
    sf.write(out_path, audio, sr, subtype="PCM_16")
    kb = out_path.stat().st_size / 1024
    gain_note = f" (norm x{gain:.1f})" if gain > 1.01 else ""
    print(f"    saved {out_path.relative_to(ROOT)} ({kb:.0f} KB){gain_note} "
          f"in {time.time()-t0:.1f}s", flush=True)
    return out_path


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("name", nargs="?", help="SFX name (e.g. 'menu_select')")
    ap.add_argument("--out-subdir", help="Disambiguate when name is shared across ships")
    ap.add_argument("--round", type=int, help="Generate all SFX with this round number")
    ap.add_argument("--category", help="Generate all SFX in category (ui|weapon|lander|scan)")
    ap.add_argument("--list", action="store_true", help="List inventory and exit")
    ap.add_argument("--no-overwrite", action="store_true")
    args = ap.parse_args(argv)

    if args.list:
        by_cat: dict[str, list[SfxSpec]] = {}
        for s in ALL_SFX:
            by_cat.setdefault(s.category, []).append(s)
        for cat in sorted(by_cat):
            specs = by_cat[cat]
            print(f"\n{cat} ({len(specs)} sounds):")
            for s in specs:
                marker = "[R1] " if s.round == 1 else ""
                loop_marker = " [LOOP]" if s.loop else ""
                print(f"  {marker}{s.out_subdir}/{s.name:<22} "
                      f"{s.duration_s}s{loop_marker} -- {s.prompt[:60]}...")
        return 0

    overwrite = not args.no_overwrite

    if args.round is not None:
        specs = for_round(args.round)
        if not specs:
            print(f"no SFX for round {args.round}", file=sys.stderr)
            return 1
        print(f"generating {len(specs)} SFX for round {args.round}")
        t0 = time.time()
        n_ok = 0
        for spec in specs:
            if generate_one(spec, overwrite=overwrite):
                n_ok += 1
        print(f"\n## round {args.round} done: {n_ok}/{len(specs)} "
              f"in {time.time()-t0:.1f}s")
        return 0 if n_ok == len(specs) else 1

    if args.category:
        specs = by_category(args.category)
        if not specs:
            print(f"no SFX in category {args.category!r}", file=sys.stderr)
            return 1
        print(f"generating {len(specs)} SFX for category {args.category}")
        t0 = time.time()
        n_ok = sum(1 for s in specs if generate_one(s, overwrite=overwrite))
        print(f"\n## category {args.category} done: {n_ok}/{len(specs)} "
              f"in {time.time()-t0:.1f}s")
        return 0 if n_ok == len(specs) else 1

    if not args.name:
        ap.error("provide a SFX name OR --round N OR --category X OR --list")
    candidates = [s for s in ALL_SFX if s.name == args.name]
    if args.out_subdir:
        candidates = [s for s in candidates if s.out_subdir == args.out_subdir]
    if not candidates:
        print(f"no SFX named {args.name!r}", file=sys.stderr)
        return 1
    if len(candidates) > 1:
        print(f"{args.name!r} is ambiguous; pass --out-subdir from:",
              file=sys.stderr)
        for c in candidates:
            print(f"  --out-subdir {c.out_subdir}", file=sys.stderr)
        return 2
    generate_one(candidates[0], overwrite=overwrite)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
