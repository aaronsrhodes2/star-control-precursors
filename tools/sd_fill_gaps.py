"""Fire the queued gap-fills against the local SD server.

For each item in the WORK_QUEUE:
1. Read the prompt file
2. Strip leading #-comments
3. Call sd_client.txt2img() with the right aspect
4. Save to the expected asset path
5. For avatars: chromakey the result to alpha

Usage:
    .venv/Scripts/python.exe tools/sd_fill_gaps.py [--dry-run] [--only NAME]
"""

from __future__ import annotations

import argparse
import os
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from sd_client import txt2img, chromakey, health


ROOT = Path(__file__).resolve().parent.parent
PROMPT_DIR = ROOT / "tools" / "firefly_prompts"
ASSET_DIR = ROOT / "assets" / "generated_drafts" / "firefly"


# Items still missing per the spreadsheet/inventory tracking.
# Each item: (prompt_file, output_path, width, height, is_avatar)
WORK_QUEUE: list[tuple[str, str, int, int, bool]] = [
    # --- Avatars (Tall 2:3 = 848x1264 to match the existing batch) ---
    (
        "tier1_avatars/avatar_mmrnmhrm_sentinel.txt",
        "tier1_avatars/avatar_mmrnmhrm_sentinel.png",
        848, 1264, True,
    ),
    (
        "tier1_avatars/avatar_planar_witness.txt",
        "tier1_avatars/avatar_planar_witness.png",
        848, 1264, True,
    ),
    (
        "tier1_avatars/avatar_vael_souren_cleanser.txt",
        "tier1_avatars/avatar_vael_souren_cleanser.png",
        848, 1264, True,
    ),
    # --- Dialog backgrounds (Tall 2:3) ---
    (
        "tier1_dialog_backgrounds/bg_planet_surface.txt",
        "tier1_dialog_backgrounds/bg_planet_surface.png",
        848, 1264, False,
    ),
    (
        "tier1_dialog_backgrounds/bg_alien_ship.txt",
        "tier1_dialog_backgrounds/bg_alien_ship.png",
        848, 1264, False,
    ),
    (
        "tier1_dialog_backgrounds/bg_open_space.txt",
        "tier1_dialog_backgrounds/bg_open_space.png",
        848, 1264, False,
    ),
    # --- Map L1 nebula backdrop (3:4 vertical, ~768x1024) ---
    (
        "tier1_nebula/bg_galaxy_nebula.txt",
        "tier1_nebula/bg_galaxy_nebula.png",
        768, 1024, False,
    ),
]


def strip_prompt(path: Path) -> str:
    lines = path.read_text(encoding="utf-8").splitlines()
    body = [ln for ln in lines if not ln.startswith("#")]
    return " ".join(s.strip() for s in body if s.strip())


def run_one(item: tuple[str, str, int, int, bool], dry_run: bool) -> bool:
    prompt_file, out_rel, w, h, is_avatar = item
    name = Path(out_rel).stem
    prompt_path = PROMPT_DIR / prompt_file
    if not prompt_path.exists():
        print(f"  SKIP {name}: prompt file missing ({prompt_path})")
        return False
    out_path = ASSET_DIR / out_rel
    out_path.parent.mkdir(parents=True, exist_ok=True)
    prompt = strip_prompt(prompt_path)

    print(f"\n=== {name} ({w}x{h}, {'avatar' if is_avatar else 'background'}) ===")
    print(f"    prompt: {prompt[:100]}...")
    if dry_run:
        print("    [dry-run] skipping generation")
        return True

    t0 = time.time()
    img = txt2img(prompt=prompt, width=w, height=h)
    img.save(out_path)
    print(f"    saved {out_path.relative_to(ROOT)} ({img.size}) in {time.time()-t0:.1f}s")

    if is_avatar:
        t0 = time.time()
        keyed = chromakey(img, mode="rembg")
        keyed.save(out_path)
        print(f"    chromakey'd via rembg in {time.time()-t0:.1f}s")

    return True


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--only", help="run only the item whose output name contains this string")
    args = parser.parse_args()

    try:
        h = health()
        print(f"SD server: {h}")
    except Exception as e:
        print(f"ERROR: SD server not reachable: {e}")
        print("Start it: .venv/Scripts/python.exe sd-server/app.py")
        return 1

    queue = WORK_QUEUE
    if args.only:
        queue = [q for q in WORK_QUEUE if args.only in q[1]]
        if not queue:
            print(f"no items match --only {args.only!r}")
            return 1
        print(f"filtered to {len(queue)} item(s) matching {args.only!r}")

    n_ok = 0
    for item in queue:
        try:
            if run_one(item, args.dry_run):
                n_ok += 1
        except Exception as e:
            print(f"  FAIL: {e}")
    print(f"\n=== done: {n_ok}/{len(queue)} ===")
    return 0 if n_ok == len(queue) else 1


if __name__ == "__main__":
    sys.exit(main())
