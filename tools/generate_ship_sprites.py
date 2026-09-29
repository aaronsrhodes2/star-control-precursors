"""Generate alpha-cutout sprite versions of approved Firefly ship hero
images for in-game runtime use.

The combat scene loads ship hero PNGs directly and rotates them per-frame
via pygame. Firefly outputs have RGB-only (no alpha) backgrounds, so the
hero PNGs render as opaque squares in-game. This script produces alpha-
cutout sprite versions tightly cropped to the ship silhouette.

Source: assets/generated_drafts/firefly/_manifest.json — all entries
        under tier1_ships/* with status="keep"
Output: assets/ships/sprites/<original-filename>.png — RGBA, tight bbox

Run with the sd-server venv's python (which has rembg + onnxruntime):
    sd-server/.venv/Scripts/python.exe tools/generate_ship_sprites.py

Options:
    --only <name>   process only the manifest entry whose filename
                    matches <name> (substring, case-insensitive); good
                    for spot-testing a single ship before running all.
    --force         re-process even if the output file already exists.
"""

from __future__ import annotations

import argparse
import json
import pathlib
import sys

from PIL import Image
from rembg import new_session, remove


ROOT = pathlib.Path(__file__).resolve().parent.parent
MANIFEST = ROOT / "assets" / "generated_drafts" / "firefly" / "_manifest.json"
OUT_DIR = ROOT / "assets" / "ships" / "sprites"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--only", help="substring filter on filename")
    parser.add_argument("--force", action="store_true", help="re-process existing outputs")
    args = parser.parse_args()

    if not MANIFEST.exists():
        print(f"manifest not found: {MANIFEST}", file=sys.stderr)
        return 1
    m = json.loads(MANIFEST.read_text(encoding="utf-8"))
    keep = sorted(
        (k, v) for k, v in m.items()
        if k.startswith("tier1_ships/") and v.get("status") == "keep"
    )
    if args.only:
        needle = args.only.lower()
        keep = [(k, v) for k, v in keep
                if needle in pathlib.Path(v["image_path"]).name.lower()]
    if not keep:
        print("no approved ships match the filter", file=sys.stderr)
        return 0

    OUT_DIR.mkdir(parents=True, exist_ok=True)

    print(f"loading rembg u2net session...")
    session = new_session("u2net")
    print(f"processing {len(keep)} approved ships -> {OUT_DIR.relative_to(ROOT)}")
    print()

    ok, skipped, failed = 0, 0, 0
    for k, v in keep:
        src_path = ROOT / v["image_path"]
        out_path = OUT_DIR / src_path.name
        if not src_path.exists():
            print(f"  SKIP   {k}: missing src {src_path}")
            skipped += 1
            continue
        if out_path.exists() and not args.force:
            print(f"  SKIP   {k}: output exists ({out_path.name}; use --force to redo)")
            skipped += 1
            continue
        try:
            src = Image.open(src_path)
            if src.mode != "RGB":
                src = src.convert("RGB")
            cut = remove(src, session=session, alpha_matting=False)
            # Threshold low-alpha pixels to 0 so soft starfield haze
            # doesn't survive as faint halos around the ship. Pixels
            # below 32/255 (~12%) become fully transparent; above stays.
            r, g, b, a = cut.split()
            a = a.point(lambda v: 0 if v < 32 else v)
            cut = Image.merge("RGBA", (r, g, b, a))
            # crop to alpha bbox so the sprite is tightly framed
            bbox = cut.getbbox()
            if bbox:
                cut = cut.crop(bbox)
            cut.save(out_path, format="PNG", optimize=True)
            print(f"  OK     {k:50s} -> {out_path.name}  ({cut.size})")
            ok += 1
        except Exception as e:
            print(f"  FAIL   {k}: {e}")
            failed += 1

    print()
    print(f"summary: {ok} ok, {skipped} skipped, {failed} failed")
    return 0 if failed == 0 else 2


if __name__ == "__main__":
    sys.exit(main())
