"""Extract luma-alpha from glowing projectile sprites on black backgrounds
and copy to combat-ready locations.

Projectile sprites are usually bright glowing FX on near-black space
backgrounds. For these, the cleanest alpha is the LUMA (max-RGB) of each
pixel — bright glowing pixels = opaque, dark space-background = transparent.
This gives a clean additive-blend look over the game's black play area.

Source:  assets/generated_drafts/firefly/tier1_weapons/projectile_{ship_id}_v1.png
Target:  assets/ships/sprites/projectile_{ship_id}.png

Run:
    .venv/Scripts/python.exe tools/extract_projectile_alpha.py
"""

from __future__ import annotations

import argparse
import pathlib
import sys

from PIL import Image, ImageChops


ROOT = pathlib.Path(__file__).resolve().parent.parent
SRC_DIR = ROOT / "assets" / "generated_drafts" / "firefly" / "tier1_weapons"
DST_DIR = ROOT / "assets" / "ships" / "sprites"

# Ship ids that have a generated projectile sprite. All 11 ships now
# covered after 2026-05-18 Firefly burst.
SHIPS = [
    "furling_scout",
    "persuader_vessel",
    "arilou_skiff",
    "androsynth_cruiser",
    "burv_broadcaster",
    "cleanser_cruiser",
    "compeller_vessel",
    "defender_vessel",
    "lemmkin_skitter",
    "melnorme_trader",
    "mmrnmhrm_sentinel",
    "mycon_podship",
    "proto_urquan",
    "proto_qor_ah",
    "sentry_drone_47t",
    "thinn_blade",
    "utwig_jugger",
]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--variant", default="v1", help="variant to extract (v1, v2, v3, v4)")
    parser.add_argument("--floor", type=int, default=8,
                        help="alpha values below this become 0 (suppresses haze)")
    args = parser.parse_args()

    DST_DIR.mkdir(parents=True, exist_ok=True)
    print(f"extracting luma-alpha (variant={args.variant}, floor={args.floor})")
    print()
    ok, failed = 0, 0
    for ship_id in SHIPS:
        src = SRC_DIR / f"projectile_{ship_id}_{args.variant}.png"
        dst = DST_DIR / f"projectile_{ship_id}.png"
        if not src.exists():
            print(f"  SKIP {ship_id}: src missing ({src.name})")
            continue
        try:
            img = Image.open(src).convert("RGB")
            r, g, b = img.split()
            # luma alpha = max(r, g, b) per pixel
            alpha = ImageChops.lighter(ImageChops.lighter(r, g), b)
            # threshold floor
            alpha = alpha.point(lambda v: 0 if v < args.floor else v)
            rgba = Image.merge("RGBA", (r, g, b, alpha))
            # tight bbox crop
            bbox = rgba.getbbox()
            if bbox:
                rgba = rgba.crop(bbox)
            rgba.save(dst, format="PNG", optimize=True)
            print(f"  OK   {ship_id:25s} -> {dst.name}  ({rgba.size[0]}x{rgba.size[1]})")
            ok += 1
        except Exception as e:
            print(f"  FAIL {ship_id}: {e}")
            failed += 1

    print()
    print(f"summary: {ok} ok, {failed} failed")
    return 0 if failed == 0 else 2


if __name__ == "__main__":
    sys.exit(main())
