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
import os
import sys
import time
from pathlib import Path

import soundfile as sf

sys.path.insert(0, str(Path(__file__).resolve().parent))
from audio_context_specs import ContextSpec, ALL_CONTEXTS, for_round, get


ROOT = Path(__file__).resolve().parent.parent
OUT_ROOT = ROOT / "assets" / "music"


# ---------------------------------------------------------------------------
# Backend selection
# ---------------------------------------------------------------------------
# SCZ_AUDIO_BACKEND=local  -> local AudioLDM2-Music server on port 5006
#                             (audio-server/). Native 16 kHz mono PCM;
#                             always saves .wav. Free, runs on local GPU.
# SCZ_AUDIO_BACKEND=eleven -> ElevenLabs Music API. Native 44.1 kHz
#                             stereo MP3 (saved as .mp3 byte-passthrough).
#                             Higher quality; costs credits.
# Default 2026-05-17: local (Aaron switched after ElevenLabs quota
#                     exhaustion).
BACKEND = os.environ.get("SCZ_AUDIO_BACKEND", "local").lower()


import re


# Category-appropriate genre/groove suffixes for MusicGen. Aaron's
# 2026-05-17 direction: "cruising in space, having a good time" — beat-
# driven, coherent, not ambient drift. Suffixes carry the energy while
# the spec.prompt body keeps the species/context identity.
_MUSICGEN_CAT_SUFFIX = {
    "travel": (
        ", synthwave space cruise music, driving mid-tempo electronic "
        "beat with crisp drum machine, melodic synth bassline, "
        "optimistic and fun retro 80s sci-fi soundtrack, full-band "
        "arrangement"
    ),
    "homeworld": (
        ", warm cinematic sci-fi soundtrack with steady mid-tempo "
        "groove, optimistic and homely, full-band arrangement with "
        "rhythmic foundation"
    ),
    "species_peace": (
        ", atmospheric sci-fi soundtrack with steady rhythmic backbone, "
        "full-band arrangement, characterful and immersive, drum kit "
        "with melodic synth"
    ),
    "furling_faction": (
        ", cinematic political mid-tempo soundtrack with rhythmic pulse, "
        "contemplative and weighty, full-band arrangement"
    ),
    "cinematic": (
        ", dramatic cinematic short-form score, full-band arrangement "
        "with rhythmic drive"
    ),
    "combat": (
        ", driving aggressive electronic combat soundtrack, hard-hitting "
        "drum beat, intense and exciting, full-band arrangement"
    ),
    "ending": (
        ", cinematic ending theme with steady groove, full-band "
        "arrangement, melodic resolution"
    ),
}


def _rewrite_for_musicgen(prompt: str, category: str = "") -> str:
    """Rewrite a SAO/AudioLDM2-style stem prompt into a MusicGen-native
    full-track prompt.

    Why: the existing spec prompts use 'Isolated <ROLE> STEM for layered
    production: ...  no drums no melody no pads, ..., stems-only mix' —
    framing that worked for SAO/AudioLDM2 because the diffusion path
    actually honored the stem-isolation intent. MusicGen, in contrast,
    is an autoregressive full-mix generator: it tries to produce a
    coherent musical idea regardless of what we say about isolation,
    and the negation language ('no drums no melody no pads') tends to
    just confuse it. So for MusicGen we strip the SAO framing and lean
    into a beat-driven, category-appropriate full-track aesthetic.

    Trade-off: 'stems' generated this way are really 5 different full
    mixes of the same musical idea, not separable layers. The runtime
    mixer will play them simultaneously, which is acceptable when all
    5 derive from the same key/bpm/identity prompt — they'll roughly
    align even though they're not true stems. The variation layer
    (post-MVP) will further mute/jitter individual 'stems' to break up
    any sameness.

    Aaron's 2026-05-17 direction: 'cruising in space, having a good
    time' → favor synthwave/outrun/space-funk-driven full-band
    arrangements over ambient drift. Encoded per-category in
    `_MUSICGEN_CAT_SUFFIX`.
    """
    p = prompt
    # Drop SAO stem-isolation framing.
    p = re.sub(r"^Isolated\s+[A-Z\s]+STEM\s+for\s+layered\s+production:\s*",
               "", p)
    # Drop the no-X-no-Y negations (any order / 2-4 instruments).
    p = re.sub(
        r",?\s*no\s+(?:drums|melody|pads|bass)"
        r"(?:\s+no\s+(?:drums|melody|pads|bass)){1,3}",
        "", p, flags=re.IGNORECASE)
    # Drop 'stems-only mix' and 'isolated track' framing fragments.
    p = re.sub(r",?\s*stems[-\s]only\s+mix\b", "", p, flags=re.IGNORECASE)
    p = re.sub(r",?\s*isolated\s+track\b", "", p, flags=re.IGNORECASE)
    # Drop trailing/leading whitespace + dangling commas.
    p = re.sub(r"\s+,", ",", p)
    p = re.sub(r",\s*,", ",", p)
    p = p.strip().strip(",").strip()
    # Append category-appropriate groove suffix.
    suffix = _MUSICGEN_CAT_SUFFIX.get(
        category,
        ", atmospheric sci-fi soundtrack with rhythmic backbone, "
        "full-band arrangement",
    )
    return p + suffix


def _gen_music_array(prompt: str, duration_s: float, category: str = ""):
    """Backend-dispatch: returns (audio_array, sample_rate).

    Local-backend dispatch is further model-aware via SCZ_AUDIO_MODEL:

    - stable-audio-open: 44.1 kHz stereo, 47s native cap. We clamp to
      45s and let the runtime mixer loop. Use the tuned diffusion
      params (steps=200, guidance=10) + negative prompt.
    - musicgen* (transformers): 32 kHz stereo (or mono), arbitrary
      duration via server-side chunked continuation. No diffusion
      steps; autoregressive token generation. Prompt gets rewritten
      from SAO-style to MusicGen-native style (drop stem-isolation
      framing, add beat-driven full-track suffix per category).
      Use guidance=3.0 (Meta's recommended CFG default).
    - audioldm2-music / audioldm: 16 kHz mono. Cap at 45s. Same tuned
      diffusion params; ignored where not applicable.
    """
    if BACKEND == "eleven":
        from eleven_music import music as _eleven_music  # noqa: E402
        return _eleven_music(prompt=prompt, duration_s=duration_s)

    from audio_client import music as _local_music  # noqa: E402
    model = os.environ.get("SCZ_AUDIO_MODEL", "audioldm2-music").lower()

    if "musicgen" in model:
        # Rewrite SAO-style stem prompts into MusicGen-native full-track
        # prompts. Strips stem-isolation framing + adds category-
        # appropriate beat/groove suffix.
        mg_prompt = _rewrite_for_musicgen(prompt, category=category)
        return _local_music(
            prompt=mg_prompt,
            duration=float(duration_s),
            steps=1,            # ignored by server in MusicGen path
            guidance=3.0,       # Meta's recommended CFG default
        )

    # Diffusion path (SAO / AudioLDM2): cap at 45s, use tuned params.
    NEG = ("speech, voice, vocals, talking, mumbling, noise, distortion, "
           "clicks, pops, low quality, scratchy, hiss, lo-fi, tinny, muddy")
    local_dur = min(float(duration_s), 45.0)
    return _local_music(
        prompt=prompt,
        duration=local_dur,
        steps=200,
        guidance=10.0,
        negative_prompt=NEG,
    )


def _backend_extension() -> str:
    """Local backend always saves .wav (PCM_16 16kHz mono). Eleven backend
    saves .wav too in the unified-array path (vs the .mp3 byte-passthrough
    path which is no longer used here)."""
    return ".wav"


def _backend_label(spec: ContextSpec) -> str:
    """Label for the manifest's `backend` field. Reflects the actual
    model in use so future audits can tell SAO-era files from
    AudioLDM2-era files apart by reading the manifest alone."""
    if BACKEND == "eleven":
        return "elevenlabs-music_v1/decoded"
    model = os.environ.get("SCZ_AUDIO_MODEL", "audioldm2-music").lower()
    if "stable-audio" in model:
        return "stable-audio-open/local-server"
    if "musicgen" in model:
        return f"{model}/local-server"
    if "audioldm2-large" in model:
        return "audioldm2-large/local-server"
    if "audioldm2" in model:
        return "audioldm2-music/local-server"
    return f"{model}/local-server"


def generate_context(
    spec: ContextSpec,
    *,
    overwrite: bool = True,
) -> dict:
    """Generate every stem in `spec`. Returns the written manifest dict.

    Backend dispatch is via the SCZ_AUDIO_BACKEND env var (default
    "local"). Output is always PCM_16 .wav for uniformity. The mixer
    glob handles .wav alongside .mp3/.ogg seamlessly so the existing
    ElevenLabs-generated .mp3 files in other contexts coexist with new
    local-generated .wav files in this batch.
    """
    out_dir = OUT_ROOT / spec.name
    out_dir.mkdir(parents=True, exist_ok=True)
    ext = _backend_extension()
    backend_label = _backend_label(spec)

    manifest = {
        "context": spec.name,
        "category": spec.category,
        "description": spec.description,
        "key": spec.key,
        "bpm": spec.bpm,
        "duration_s": spec.duration_s,
        "backend": backend_label,
        "stems": {},
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "notes": spec.notes,
    }

    print(f"\n## context: {spec.name} ({spec.category}) -- "
          f"{spec.key} @ {spec.bpm}bpm, {spec.duration_s}s, "
          f"{len(spec.stems)} stems  [backend={BACKEND}]", flush=True)

    for stem_name, prompt in spec.stems.items():
        out_path = out_dir / f"{stem_name}{ext}"
        # Also dedup against the OTHER backend's existing file for this
        # stem (e.g. an ElevenLabs .mp3 from a prior run). When backend
        # produces a different extension and a sibling already exists,
        # `overwrite=False` should skip the call.
        sibling_paths = [
            out_dir / f"{stem_name}.mp3",
            out_dir / f"{stem_name}.ogg",
            out_dir / f"{stem_name}.wav",
        ]
        any_exists = any(p.exists() for p in sibling_paths)
        if any_exists and not overwrite:
            print(f"  skip {stem_name} (a file already exists)", flush=True)
            continue
        print(f"  === {stem_name} ===", flush=True)
        print(f"    prompt: {prompt[:100]}...", flush=True)
        t0 = time.time()
        try:
            audio, sr = _gen_music_array(
                prompt=prompt,
                duration_s=spec.duration_s,
                category=spec.category,
            )
        except Exception as e:
            print(f"    FAIL: {e}", flush=True)
            continue
        sf.write(out_path, audio, sr, subtype="PCM_16")
        sz_kb = out_path.stat().st_size / 1024
        print(f"    saved {out_path.relative_to(ROOT)} "
              f"({sz_kb:.0f} KB, sr={sr}) in {time.time()-t0:.1f}s", flush=True)
        manifest["stems"][stem_name] = {
            "path": str(out_path.relative_to(ROOT)).replace("\\", "/"),
            "prompt": prompt,
            "sample_rate": sr,
            "backend": backend_label,
        }

    manifest_path = out_dir / "manifest.json"
    # If nothing was actually generated in this run (everything skipped),
    # don't clobber an existing manifest that documents the prior
    # generation's backend. Without this guard, `--no-overwrite` runs
    # would overwrite the manifest with empty stems + the current
    # backend label, mislabeling assets that came from a different
    # backend.
    if not manifest["stems"] and manifest_path.exists():
        print(f"  manifest unchanged (no new stems written; preserving "
              f"existing {manifest_path.relative_to(ROOT)})", flush=True)
        # Load the existing manifest to return it
        try:
            return json.loads(manifest_path.read_text(encoding="utf-8"))
        except Exception:
            pass
    else:
        manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
        print(f"  wrote {manifest_path.relative_to(ROOT)} "
              f"({len(manifest['stems'])}/{len(spec.stems)} stems)", flush=True)
    return manifest


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("name", nargs="?", help="Context name to generate (e.g. 'hyperspace')")
    ap.add_argument("--round", type=int, help="Generate every context with this round number")
    ap.add_argument("--missing", action="store_true",
                    help="Generate every context with at least one missing stem on disk")
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

    if args.missing:
        # Find contexts where at least one stem's .wav/.mp3/.ogg is missing.
        # We run those contexts with overwrite disabled so existing stems
        # are preserved and only the gaps get filled.
        gappy: list[ContextSpec] = []
        for spec in ALL_CONTEXTS.values():
            out_dir = OUT_ROOT / spec.name
            for stem_name in spec.stems:
                exts = [".mp3", ".ogg", ".wav"]
                if not any((out_dir / f"{stem_name}{ext}").exists() for ext in exts):
                    gappy.append(spec)
                    break
        if not gappy:
            print("no missing music — corpus is complete")
            return 0
        print(f"generating {len(gappy)} contexts with missing stems  "
              f"[backend={BACKEND}]")
        t0 = time.time()
        for spec in gappy:
            generate_context(spec, overwrite=False)
        print(f"\n## --missing done in {time.time()-t0:.1f}s")
        return 0

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
