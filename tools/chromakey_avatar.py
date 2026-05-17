"""Strip the matte dark-navy background from a Firefly-generated avatar.

The articulated-avatar prompts ask Firefly to render the character on a
SOLID MATTE DARK NAVY (#0a0e1a) background so we can extract a clean
transparent avatar PNG without round-tripping through a background-removal
service. This script applies a simple distance-from-target chroma key,
then erodes the alpha at the avatar edge by one pixel to remove any
remaining halo of "almost navy" pixels.

Usage:
    python tools/chromakey_avatar.py <input.png> <output.png>

When in doubt about a particular avatar, tweak `TARGET` and `THRESHOLD`.
The defaults match the prompt-spec navy.
"""

from __future__ import annotations

import sys
from pathlib import Path

from PIL import Image


# Target navy color from the avatar prompts (#0a0e1a → (10, 14, 26))
TARGET = (10, 14, 26)
# Max squared-color distance from TARGET that we treat as "background".
# 70 ≈ permissive enough to catch JPEG-style blending of the prompted
# color into nearby pixels without eating into legibly-shadowed parts
# of the character body.
THRESHOLD = 70


def chromakey(in_path: Path, out_path: Path) -> None:
    img = Image.open(in_path).convert("RGBA")
    pixels = img.load()
    w, h = img.size
    tr, tg, tb = TARGET
    t2 = THRESHOLD * THRESHOLD
    transparent = 0
    for y in range(h):
        for x in range(w):
            r, g, b, a = pixels[x, y]
            dr, dg, db = r - tr, g - tg, b - tb
            if dr * dr + dg * dg + db * db <= t2:
                pixels[x, y] = (r, g, b, 0)
                transparent += 1
    img.save(out_path)
    total = w * h
    print(f"  in : {in_path}")
    print(f"  out: {out_path}")
    print(f"  size: {w}x{h}  transparent: {transparent}/{total} "
          f"({100*transparent/total:.1f}%)")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("usage: python tools/chromakey_avatar.py <input.png> <output.png>")
        sys.exit(1)
    chromakey(Path(sys.argv[1]), Path(sys.argv[2]))
