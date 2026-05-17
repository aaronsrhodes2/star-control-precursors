"""Generic music-context generator.

Consumes a ContextSpec from tools/audio_context_specs.py and fires one
ElevenLabs Music call per stem. Writes the audio (MP3 by default) and
a manifest.json into assets/music/<context_name>/.

Usage:
    # Generate one context by name
    .venv/Scripts/python.exe tools/audio_generate.py hyperspace

    # Generate every context in a numbered round
    .venv/Scripts/python.exe tools/audio_generate.py --round 1

    # List what's available
    .venv/Scripts/python.exe tools/audio_generate.py --list
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from audio_context_specs import ContextSpec, ALL_CONTEXTS, for_round, get
from eleven_music import music_bytes, save_audio, DEFAULT_OUTPUT_FORMAT, _ext_for_format


ROOT = Path(__file__).resolve().parent.parent
OUT_ROOT = ROOT / "assets" / "music"


def generate_context(
    spec: ContextSpec,
    *,
    output_format: str = DEFAULT_OUTPUT_FORMAT,
    overwrite: bool = True,
) -> dict:
    """Generate every stem in `spec`. Returns the written manifest dict."""
    out_dir = OUT_ROOT / spec.name
    out_dir.mkdir(parents=True, exist_ok=True)
    ext = _ext_for_format(output_format)

    manifest = {
        "context": spec.name,
        "category": spec.category,
        "description": spec.description,
        "key": spec.key,
        "bpm": spec.bpm,
        "duration_s": spec.duration_s,
        "backend": f"elevenlabs-music_v1/{output_format}",
        "stems": {},
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "notes": spec.notes,
    }

    print(f"\n## context: {spec.name} ({spec.category}) -- "
          f"{spec.key} @ {spec.bpm}bpm, {spec.duration_s}s, "
          f"{len(spec.stems)} stems", flush=True)

    for stem_name, prompt in spec.stems.items():
        out_path = out_dir / f"{stem_name}{ext}"
        if out_path.exists() and not overwrite:
            print(f"  skip {stem_name} (exists)", flush=True)
            continue
        print(f"  === {stem_name} ===", flush=True)
        print(f"    prompt: {prompt[:100]}...", flush=True)
        t0 = time.time()
        try:
            data, fmt = music_bytes(
                prompt=prompt,
                duration_s=spec.duration_s,
                output_format=output_format,
            )
        except Exception as e:
            print(f"    FAIL: {e}", flush=True)
            continue
        save_audio(data, fmt, out_path)
        sz_kb = out_path.stat().st_size / 1024
        print(f"    saved {out_path.relative_to(ROOT)} "
              f"({sz_kb:.0f} KB) in {time.time()-t0:.1f}s", flush=True)
        manifest["stems"][stem_name] = {
            "path": str(out_path.relative_to(ROOT)).replace("\\", "/"),
            "prompt": prompt,
            "format": output_format,
        }

    manifest_path = out_dir / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(f"  wrote {manifest_path.relative_to(ROOT)} "
          f"({len(manifest['stems'])}/{len(spec.stems)} stems)", flush=True)
    return manifest


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("name", nargs="?", help="Context name to generate (e.g. 'hyperspace')")
    ap.add_argument("--round", type=int, help="Generate every context with this round number")
    ap.add_argument("--list", action="store_true", help="Print available contexts and exit")
    ap.add_argument("--no-overwrite", action="store_true",
                    help="Skip stems whose output file already exists")
    args = ap.parse_args(argv)

    if args.list:
        print("Available contexts:")
        by_round: dict[int, list[ContextSpec]] = {}
        for spec in ALL_CONTEXTS.values():
            by_round.setdefault(spec.round, []).append(spec)
        for r in sorted(by_round):
            print(f"\nRound {r}:")
            for s in by_round[r]:
                print(f"  {s.name:<25} {s.category:<18} "
                      f"{len(s.stems)} stems, {s.duration_s}s -- "
                      f"{s.description}")
        return 0

    overwrite = not args.no_overwrite

    if args.round is not None:
        specs = for_round(args.round)
        if not specs:
            print(f"no contexts found for round {args.round}", file=sys.stderr)
            return 1
        print(f"generating {len(specs)} contexts for round {args.round}: "
              f"{[s.name for s in specs]}")
        t0 = time.time()
        for spec in specs:
            generate_context(spec, overwrite=overwrite)
        print(f"\n## round {args.round} done in {time.time()-t0:.1f}s")
        return 0

    if not args.name:
        ap.error("provide a context name OR --round N OR --list")
    try:
        spec = get(args.name)
    except KeyError as e:
        print(str(e), file=sys.stderr)
        return 1
    generate_context(spec, overwrite=overwrite)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
