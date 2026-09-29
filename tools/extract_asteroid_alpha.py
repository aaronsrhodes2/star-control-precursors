"""Alpha-extract irregular asteroid sprites via rembg + binary
threshold, same approach as the ship sprite pipeline. Asteroids are
typically painted on near-black space; rembg cleanly isolates the
rock + we threshold the alpha hard to eliminate halo/noise.

Source:  assets/generated_drafts/firefly/tier1_asteroids/asteroid_*_v{N}.png
Target:  assets/asteroids/asteroid_<id>.png

Run with the sd-server venv (has rembg):
    sd-server/.venv/Scripts/python.exe tools/extract_asteroid_alpha.py
"""

from __future__ import annotations

import pathlib
import sys

from PIL import Image
from rembg import new_session, remove


ROOT = pathlib.Path(__file__).resolve().parent.parent
SRC_DIR = ROOT / "assets" / "generated_drafts" / "firefly" / "tier1_asteroids"
DST_DIR = ROOT / "assets" / "asteroids"


def main() -> int:
    DST_DIR.mkdir(parents=True, exist_ok=True)
    print("loading rembg u2net...")
    session = new_session("u2net")
    print()
    ok = 0
    for src in sorted(SRC_DIR.glob("asteroid_*.png")):
        # Source files look like 'asteroid_rocky_v1.png' -> id 'rocky_v1'
        asteroid_id = src.stem.replace("asteroid_", "")
        dst = DST_DIR / f"asteroid_{asteroid_id}.png"
        try:
            img = Image.open(src).convert("RGB")
            cut = remove(img, session=session, alpha_matting=False)
            # Binary alpha to give a coherent rock silhouette (same as ships)
            r, g, b, a = cut.split()
            a = a.point(lambda v: 255 if v >= 160 else 0)
            cut = Image.merge("RGBA", (r, g, b, a))
            bbox = cut.getbbox()
            if bbox:
                cut = cut.crop(bbox)
            cut.save(dst, format="PNG", optimize=True)
            print(f"  OK   {asteroid_id:25s} -> {dst.name}  ({cut.size[0]}x{cut.size[1]})")
            ok += 1
        except Exception as e:
            print(f"  FAIL {asteroid_id}: {e}")
    print()
    print(f"summary: {ok} asteroids alpha-extracted")
    return 0


if __name__ == "__main__":
    sys.exit(main())
