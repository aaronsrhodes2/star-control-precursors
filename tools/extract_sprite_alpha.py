"""Alpha-extract the v1 variant of each Firefly-generated ship sprite
and copy to assets/ships/sprites/ with the filename combat expects.

This replaces the older rembg-cutouts (which were made from full hero
portraits) with the new sprite-format Firefly outputs (top-down
designed-as-sprite art).

Source:  assets/generated_drafts/firefly/tier1_ship_sprites/sprite_{ship_id}_v1.png
Target:  assets/ships/sprites/ship_{filename}                  (filename per SHIP_SPRITES map below)

Run with the sd-server venv (has rembg):
    sd-server/.venv/Scripts/python.exe tools/extract_sprite_alpha.py
"""

from __future__ import annotations

import argparse
import pathlib
import sys

from PIL import Image
from rembg import new_session, remove


ROOT = pathlib.Path(__file__).resolve().parent.parent
SRC_DIR = ROOT / "assets" / "generated_drafts" / "firefly" / "tier1_ship_sprites"
DST_DIR = ROOT / "assets" / "ships" / "sprites"

# Map ship_id -> output filename. Mirrors src/scz/combat/scene.py:SHIP_SPRITES
# plus extra entries for ships that aren't yet wired into combat (ready for
# when they're added).
SHIP_FILENAMES: dict[str, str] = {
    "androsynth_cruiser": "ship_androsynth_cruiser.png",
    "arilou_skiff":      "ship_arilou_skiff.png",
    "burv_broadcaster":  "ship_burv_broadcaster.png",
    "cleanser_cruiser":  "ship_cleanser_cruiser.png",
    "compeller_vessel":  "ship_compeller_vessel.png",
    "defender_vessel":   "ship_defender_vessel.png",
    "furling_scout":     "ship_furling_scout.png",
    "lemmkin_skitter":   "ship_lemmkin_skitter.png",
    "melnorme_trader":   "ship_melnorme_trader.png",
    "mmrnmhrm_sentinel": "ship_mmrnmhrm_sentinel.png",
    "mycon_podship":     "ship_mycon_podship.png",
    "others_vessel":     "ship_others_vessel.png",
    "persuader_vessel":  "ship_persuader_vessel.png",
    "proto_qor_ah":      "ship_proto_qor_ah.png",
    "proto_urquan":      "ship_proto_urquan.png",      # combat uses ship_id 'proto_ur_quan' but filename omits underscore
    "sentry_drone_47t":  "ship_sentry_drone_47t.png",
    "thinn_blade":       "ship_thinn_blade.png",  # 2026-05-18 renamed from planar_blade
    "utwig_jugger":      "ship_utwig_jugger.png",
}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--variant", default="v1", help="which variant to use (v1, v2, v3, v4)")
    parser.add_argument("--only", help="substring filter on ship_id")
    parser.add_argument("--no-threshold", action="store_true",
                        help="skip alpha thresholding (keep all rembg output as-is)")
    args = parser.parse_args()

    DST_DIR.mkdir(parents=True, exist_ok=True)
    print("loading rembg u2net session...")
    session = new_session("u2net")
    print()

    ok, failed = 0, 0
    for ship_id, dst_name in SHIP_FILENAMES.items():
        if args.only and args.only not in ship_id:
            continue
        src = SRC_DIR / f"sprite_{ship_id}_{args.variant}.png"
        if not src.exists():
            print(f"  SKIP {ship_id}: src missing ({src.name})")
            continue
        dst = DST_DIR / dst_name
        try:
            img = Image.open(src)
            if img.mode != "RGB":
                img = img.convert("RGB")
            cut = remove(img, session=session, alpha_matting=False)
            # BINARY ALPHA: pixels above threshold become fully opaque,
            # everything else fully transparent. Eliminates the soft halo
            # / ambient noise around the ship body. Aaron's directive
            # (2026-05-18): "pure #000000 black background as a
            # transparency layer and no ambient noise in the back. It
            # has to look like a coherent ship."
            if not args.no_threshold:
                r, g, b, a = cut.split()
                threshold = 160  # binary cutoff (alpha >= 160 -> 255, else 0)
                a = a.point(lambda v: 255 if v >= threshold else 0)
                cut = Image.merge("RGBA", (r, g, b, a))
            # tight bbox crop
            bbox = cut.getbbox()
            if bbox:
                cut = cut.crop(bbox)
            cut.save(dst, format="PNG", optimize=True)
            print(f"  OK   {ship_id:25s} {src.name} -> {dst.name}  ({cut.size[0]}x{cut.size[1]})")
            ok += 1
        except Exception as e:
            print(f"  FAIL {ship_id}: {e}")
            failed += 1

    print()
    print(f"summary: {ok} ok, {failed} failed")
    return 0 if failed == 0 else 2


if __name__ == "__main__":
    sys.exit(main())
