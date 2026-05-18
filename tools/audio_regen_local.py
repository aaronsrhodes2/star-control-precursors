"""Regenerate every locally-AudioLDM2-produced music context that isn't
status='keep' yet — using the now-tuned settings (steps=200,
guidance=10, negative prompt, +Stable Audio Open as the active backend
when the server runs with SCZ_AUDIO_MODEL=stable-audio-open).

Selection criteria:
  - audio review entry's status != "keep" (i.e. reject, reroll_requested,
    provisional, pending, or missing)
  - manifest's backend label includes "audioldm" (the local R3+ runs)
  Eleven-backend keeps from R1/R2 are NEVER touched.

Usage:
    SCZ_AUDIO_BACKEND=local .venv/Scripts/python.exe tools/audio_regen_local.py
    SCZ_AUDIO_BACKEND=local .venv/Scripts/python.exe tools/audio_regen_local.py --dry-run
    SCZ_AUDIO_BACKEND=local .venv/Scripts/python.exe tools/audio_regen_local.py --only ending_cleanser tension_other_ripple

The duration cap (45s for local) is applied inside
tools/audio_generate._gen_music_array so SAO stays inside its 47s
native training window. Manifest's duration_s remains the *intended*
context duration; the mixer loops shorter stems at runtime.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))

from audio_context_specs import ALL_CONTEXTS, get  # noqa: E402
from audio_generate import generate_context  # noqa: E402
from datetime import datetime, timezone  # noqa: E402


REVIEW_PATH = ROOT / "assets" / "_audio_review.json"


def _reset_review(context_name: str, prev_status: str) -> None:
    """Mark a regenerated context's review status back to 'pending' so
    Aaron can re-review. Preserve the previous status in notes so the
    history isn't lost."""
    if not REVIEW_PATH.exists():
        return
    try:
        review = json.loads(REVIEW_PATH.read_text(encoding="utf-8"))
    except Exception:
        return
    key = f"music/{context_name}"
    entry = review.get(key, {})
    prev_notes = (entry.get("notes") or "").strip()
    # Use the live SCZ_AUDIO_MODEL env so the note is honest about which
    # backend produced the new audio.
    model = os.environ.get("SCZ_AUDIO_MODEL", "audioldm2-music")
    bump = f"regenerated via {model} (was {prev_status})"
    new_notes = f"{prev_notes}; {bump}" if prev_notes else bump
    review[key] = {
        "status": "pending",
        "notes": new_notes,
        "reviewed_at": datetime.now(timezone.utc).isoformat(),
    }
    tmp = REVIEW_PATH.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(review, indent=2, ensure_ascii=False),
                   encoding="utf-8")
    tmp.replace(REVIEW_PATH)


_LOCAL_BACKEND_TAGS = ("audioldm", "stable-audio", "musicgen")


def collect_targets(include_keep: bool = False) -> list[str]:
    """Collect contexts whose current on-disk audio is from any local
    model (audioldm/stable-audio/musicgen). By default skip ones with
    status=keep (Aaron's already-approved set). Pass include_keep=True
    to also regenerate keeps — useful when a better local model lands
    and we want to roll the whole local corpus forward.

    The ElevenLabs-generated keeps are NEVER touched (their backend
    label is 'elevenlabs-music_v1/decoded', not in the local list)."""
    review_path = ROOT / "assets" / "_audio_review.json"
    review = json.loads(review_path.read_text(encoding="utf-8")) if review_path.exists() else {}
    targets: list[tuple[str, str, int, int]] = []
    for name, spec in ALL_CONTEXTS.items():
        entry = review.get(f"music/{name}", {})
        status = entry.get("status", "pending")
        if status == "keep" and not include_keep:
            continue
        mpath = ROOT / "assets" / "music" / name / "manifest.json"
        if not mpath.exists():
            continue
        try:
            md = json.loads(mpath.read_text(encoding="utf-8"))
        except Exception:
            continue
        backend = md.get("backend", "").lower()
        if not any(tag in backend for tag in _LOCAL_BACKEND_TAGS):
            continue
        targets.append((name, status, spec.duration_s, len(spec.stems)))
    targets.sort(key=lambda t: (-t[2], t[0]))
    return [t[0] for t in targets]


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true",
                    help="Print the targets and exit; don't call the model")
    ap.add_argument("--only", nargs="*", default=None,
                    help="Restrict to this subset of context names (must "
                         "still pass the audioldm/non-keep filter unless "
                         "--force is set)")
    ap.add_argument("--force", action="store_true",
                    help="With --only, skip the audioldm/non-keep filter")
    ap.add_argument("--include-keep", action="store_true",
                    help="Also regen contexts whose review status is 'keep' "
                         "(use when rolling the whole local corpus forward "
                         "to a new model)")
    args = ap.parse_args(argv)

    if args.only and args.force:
        targets = list(args.only)
    elif args.only:
        all_targets = set(collect_targets(include_keep=args.include_keep))
        targets = [n for n in args.only if n in all_targets]
        missed = [n for n in args.only if n not in all_targets]
        if missed:
            print(f"[regen] excluded by filter (not audioldm+non-keep): {missed}")
    else:
        targets = collect_targets(include_keep=args.include_keep)

    if not targets:
        print("[regen] nothing to regenerate")
        return 0

    print(f"[regen] {len(targets)} target contexts:")
    for n in targets:
        print(f"  - {n}")
    if args.dry_run:
        print("[regen] --dry-run, exiting before generation")
        return 0

    backend = os.environ.get("SCZ_AUDIO_BACKEND", "local")
    print(f"[regen] backend={backend}")
    # Snapshot the prior statuses so the review-reset notes carry the
    # *original* status (not whatever this loop just wrote).
    review = (json.loads(REVIEW_PATH.read_text(encoding="utf-8"))
              if REVIEW_PATH.exists() else {})
    prior_status: dict[str, str] = {
        n: review.get(f"music/{n}", {}).get("status", "pending")
        for n in targets
    }
    t_start = time.time()
    for i, name in enumerate(targets, 1):
        spec = get(name)
        t0 = time.time()
        print(f"\n[regen] ({i}/{len(targets)}) {name}  "
              f"({spec.duration_s}s nominal, {len(spec.stems)} stems)",
              flush=True)
        try:
            generate_context(spec, overwrite=True)
        except Exception as e:
            print(f"[regen] FAILED {name}: {e}", flush=True)
            continue
        _reset_review(name, prior_status.get(name, "pending"))
        print(f"[regen] done {name} in {time.time()-t0:.1f}s "
              f"(review reset to pending)", flush=True)
    elapsed = time.time() - t_start
    print(f"\n[regen] ALL DONE in {elapsed/60:.1f} min "
          f"({len(targets)} contexts)")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
