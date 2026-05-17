"""Generic sound-effect generator (backend-aware).

Consumes SfxSpec entries from tools/audio_sfx_specs.py. Dispatch to
either:
  - local  : audio_client.sfx() against audio-server:5006 (AudioLDM2)
             16 kHz mono PCM. Free, runs on the local GPU. Loop and
             prompt_influence are ignored (AudioLDM2 has no equivalents).
  - eleven : eleven_sfx.sfx_bytes() against ElevenLabs Music API
             Higher quality with loop + prompt_influence support.
             Costs credits.
Default 2026-05-17: local. Override via env: SCZ_AUDIO_BACKEND=eleven.

Provenance: every saved SFX gets a row in assets/sfx/_provenance.json
recording which backend produced it. The audio review player reads
this manifest and displays a small backend badge ("LOCAL" / "ELEVEN")
per SFX so Aaron can spot the quality split at a glance.

We always save .wav (PCM_16). For ElevenLabs we normalize on save
because the SFX endpoint outputs inconsistently quiet audio.

No per-folder manifest -- SFX are leaf assets keyed by filename; the
spec module is the inventory of record + the provenance file is the
"who made it" record.

Usage:
    .venv/Scripts/python.exe tools/audio_sfx_generate.py --list
    .venv/Scripts/python.exe tools/audio_sfx_generate.py menu_select
    .venv/Scripts/python.exe tools/audio_sfx_generate.py --round 1
    .venv/Scripts/python.exe tools/audio_sfx_generate.py --category ui
    .venv/Scripts/python.exe tools/audio_sfx_generate.py --missing  # any spec without a .wav on disk
"""

from __future__ import annotations

import argparse
import io
import json
import os
import sys
import time
from pathlib import Path

import numpy as np
import soundfile as sf

sys.path.insert(0, str(Path(__file__).resolve().parent))
from audio_sfx_specs import (  # noqa: E402
    SfxSpec, ALL_SFX, by_category, for_round,
)


# Backend dispatch (see audio_generate.py for the music-side equivalent).
BACKEND = os.environ.get("SCZ_AUDIO_BACKEND", "local").lower()


# Aaron 2026-05-17: Round-1 SFX too quiet, raised normalize target.
NORMALIZE_TARGET_PEAK = 0.95     # any peak below this scales up to here
NORMALIZE_FLOOR_PEAK = 0.6       # peaks at/above this are left alone


def _backend_label() -> str:
    """Provenance string written per-file."""
    if BACKEND == "eleven":
        return "elevenlabs-sound-generation"
    return "audioldm2-music/local-server"


def _provenance_path(root: Path) -> Path:
    return root / "assets" / "sfx" / "_provenance.json"


def _load_provenance(root: Path) -> dict:
    p = _provenance_path(root)
    if not p.exists():
        return {}
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return {}


def _save_provenance(root: Path, data: dict) -> None:
    p = _provenance_path(root)
    p.parent.mkdir(parents=True, exist_ok=True)
    tmp = p.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(data, indent=2, sort_keys=True, ensure_ascii=False),
                   encoding="utf-8")
    tmp.replace(p)


def _record_provenance(root: Path, key: str, label: str) -> None:
    data = _load_provenance(root)
    data[key] = {
        "backend": label,
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }
    _save_provenance(root, data)


def _gen_sfx_bytes_or_array(spec: SfxSpec):
    """Backend dispatch. Returns one of:
      ("bytes", raw_bytes, format_str)   -- eleven (mp3)
      ("array", audio_np, sample_rate)   -- local (decoded)
    """
    if BACKEND == "eleven":
        from eleven_sfx import sfx_bytes, DEFAULT_OUTPUT_FORMAT  # noqa
        data, fmt = sfx_bytes(
            text=spec.prompt,
            duration_s=spec.duration_s,
            prompt_influence=spec.prompt_influence,
            loop=spec.loop,
            output_format=DEFAULT_OUTPUT_FORMAT,
        )
        return ("bytes", data, fmt)
    # local — AudioLDM2 SFX path. Note: AudioLDM2 has no loop or
    # prompt_influence equivalents; those spec fields are ignored.
    from audio_client import sfx as _local_sfx  # noqa
    audio, sr = _local_sfx(prompt=spec.prompt, duration=spec.duration_s)
    return ("array", audio, sr)


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


def _normalize_array(audio: np.ndarray) -> tuple[np.ndarray, float]:
    """Apply normalize gain if peak is below the floor. Returns (audio, gain)."""
    audio = audio.astype(np.float32)
    peak = float(np.abs(audio).max()) if audio.size else 0.0
    if peak >= NORMALIZE_FLOOR_PEAK or peak < 1e-6:
        return audio, 1.0
    gain = NORMALIZE_TARGET_PEAK / peak
    return np.clip(audio * gain, -1.0, 1.0), gain


def generate_one(
    spec: SfxSpec,
    *,
    overwrite: bool = True,
) -> Path | None:
    """Generate a single SFX. Returns the path written, or None on failure.

    Three code paths:
      - spec.reverse_of: derive by sample-reversing the named source
        (no API call). Provenance = "derived/reverse_of:<source>".
      - BACKEND=local: audio_client.sfx() returns decoded numpy array.
        16 kHz mono PCM. Normalized + saved as .wav. Provenance =
        "audioldm2-music/local-server".
      - BACKEND=eleven: eleven_sfx.sfx_bytes() returns raw MP3 bytes,
        decoded + normalized + saved as .wav. Provenance =
        "elevenlabs-sound-generation".
    """
    out_dir = OUT_ROOT / spec.out_subdir
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{spec.name}.wav"
    if out_path.exists() and not overwrite:
        print(f"  skip {out_path.relative_to(ROOT)} (exists)", flush=True)
        return out_path
    print(f"\n  === {spec.category}/{spec.out_subdir}/{spec.name} ===", flush=True)

    # Derivation path: sample-reverse another SFX.
    if spec.reverse_of:
        src = OUT_ROOT / f"{spec.reverse_of}.wav"
        if not src.exists():
            print(f"    FAIL: reverse_of source missing: {src}", flush=True)
            return None
        print(f"    DERIVE: sample-reverse of {spec.reverse_of}", flush=True)
        t0 = time.time()
        audio, sr = sf.read(src)
        audio_rev = audio[::-1]
        sf.write(out_path, audio_rev, sr, subtype="PCM_16")
        kb = out_path.stat().st_size / 1024
        print(f"    saved {out_path.relative_to(ROOT)} ({kb:.0f} KB) (reversed) "
              f"in {time.time()-t0:.1f}s", flush=True)
        key = f"{spec.out_subdir}/{spec.name}"
        _record_provenance(ROOT, key, f"derived/reverse_of:{spec.reverse_of}")
        return out_path

    print(f"    duration: {spec.duration_s}s loop: {spec.loop} "
          f"infl: {spec.prompt_influence}  [backend={BACKEND}]", flush=True)
    print(f"    prompt: {spec.prompt[:110]}{'...' if len(spec.prompt) > 110 else ''}", flush=True)
    t0 = time.time()
    try:
        kind, *payload = _gen_sfx_bytes_or_array(spec)
    except Exception as e:
        print(f"    FAIL: {e}", flush=True)
        return None
    if kind == "bytes":
        data, fmt = payload
        audio, sr = sf.read(io.BytesIO(data))
    else:
        audio, sr = payload
    audio, gain = _normalize_array(np.asarray(audio))
    sf.write(out_path, audio, sr, subtype="PCM_16")
    kb = out_path.stat().st_size / 1024
    gain_note = f" (norm x{gain:.1f})" if gain > 1.01 else ""
    print(f"    saved {out_path.relative_to(ROOT)} ({kb:.0f} KB, sr={sr}){gain_note} "
          f"in {time.time()-t0:.1f}s", flush=True)
    key = f"{spec.out_subdir}/{spec.name}"
    _record_provenance(ROOT, key, _backend_label())
    return out_path


def for_missing() -> list[SfxSpec]:
    """Return every spec whose output .wav doesn't exist on disk."""
    out: list[SfxSpec] = []
    for s in ALL_SFX:
        p = OUT_ROOT / s.out_subdir / f"{s.name}.wav"
        if not p.exists():
            out.append(s)
    return out


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("name", nargs="?", help="SFX name (e.g. 'menu_select')")
    ap.add_argument("--out-subdir", help="Disambiguate when name is shared across ships")
    ap.add_argument("--round", type=int, help="Generate all SFX with this round number")
    ap.add_argument("--category", help="Generate all SFX in category (ui|weapon|lander|scan)")
    ap.add_argument("--missing", action="store_true",
                    help="Generate every spec whose .wav doesn't yet exist on disk")
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

    if args.missing:
        specs = for_missing()
        if not specs:
            print("no missing SFX — corpus is complete")
            return 0
        print(f"generating {len(specs)} missing SFX  [backend={BACKEND}]")
        t0 = time.time()
        n_ok = 0
        for spec in specs:
            if generate_one(spec, overwrite=overwrite):
                n_ok += 1
        print(f"\n## --missing done: {n_ok}/{len(specs)} "
              f"in {time.time()-t0:.1f}s")
        return 0 if n_ok == len(specs) else 1

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
