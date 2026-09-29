"""Generate a rotation sequence of 3D-sphere views from a 2D
equirectangular planet texture. Mirrors SC2's `plangen.c` approach:
build a lookup table mapping each output pixel on the sphere disc to a
source pixel on the 2D map, then sweep longitude across frames.

SC2 ref: references/uqm-source/sc2/src/uqm/planets/plangen.c
- `CreateSphereTiltMap()` builds the (output pixel) -> (texture coord)
  lookup with antialiasing
- `RenderPlanetSphere(offset)` renders each frame by shifting the
  longitude offset through the map

We pre-bake N frames per planet as PNGs, then the game cycles through
them at a fixed fps. Same texture is used for scanner / solar-system /
combat views so the planet visually IS the same across transitions.

Run:
    .venv/Scripts/python.exe tools/animate_planet.py
    .venv/Scripts/python.exe tools/animate_planet.py --only mh_lai
    .venv/Scripts/python.exe tools/animate_planet.py --frames 32 --diameter 192
"""

from __future__ import annotations

import argparse
import math
import pathlib
import sys

import numpy as np
from PIL import Image


ROOT = pathlib.Path(__file__).resolve().parent.parent
SRC_DIR = ROOT / "assets" / "generated_drafts" / "firefly" / "tier1_planets"
OUT_DIR = ROOT / "assets" / "planets" / "animated"

# Default render params. Increase frames for smoother rotation; increase
# diameter for higher-fidelity scanner-view zoom.
DEFAULT_FRAMES = 24
DEFAULT_DIAMETER = 192


def render_frame_orthographic(
    disc_tex: np.ndarray,
    diameter: int,
    longitude_offset: float,
    light_dir: tuple[float, float, float] = (-0.45, -0.45, 0.77),
    ambient: float = 0.30,
) -> np.ndarray:
    """Treat the source painting as the ORTHOGRAPHIC projection of the
    planet (sphere viewed straight-on). For each output pixel, compute
    its sphere normal, inverse-rotate by the desired longitude offset
    to find the corresponding source-sphere normal, and sample the
    painting at that 2D position.

    When the rotated normal's z is positive, we're seeing the front
    half of the source — direct sample. When negative, we're seeing
    the back half — we sample the same painting but mirrored along the
    x axis, so the planet appears to keep rotating with believable
    coherent features wrapping around.

    Result: no equirectangular distortion, no label-bleed from the
    source corners (they're outside the sphere disc and never sampled),
    and the rotation reads smoothly across 360°.
    """
    R = diameter / 2.0
    yy, xx = np.meshgrid(
        np.linspace(-R + 0.5, R - 0.5, diameter),
        np.linspace(-R + 0.5, R - 0.5, diameter),
        indexing="ij",
    )
    rr2 = xx * xx + yy * yy
    inside = rr2 < R * R

    # Output sphere normal (viewer coords, sphere at origin, looking +z)
    onx = xx / R
    ony = yy / R
    onz = np.sqrt(np.maximum(0.0, 1.0 - rr2 / (R * R)))

    # Inverse-rotate the OUTPUT normal by longitude_offset around the
    # Y axis to find the SOURCE normal. Y is the screen-up axis.
    cos_t = np.cos(longitude_offset)
    sin_t = np.sin(longitude_offset)
    snx = onx * cos_t + onz * sin_t
    sny = ony
    snz = -onx * sin_t + onz * cos_t

    # If snz > 0 the source-sphere point is on the front (visible in
    # the painting). Sample directly at (snx, sny). If snz <= 0 we're
    # on the back of the source-sphere; mirror along x so a coherent
    # feature wraps around.
    src_h, src_w = disc_tex.shape[:2]
    src_R = min(src_h, src_w) / 2.0
    src_cx = src_w / 2.0
    src_cy = src_h / 2.0

    # Sample at BOTH the direct (front) and mirrored (back) source
    # positions, then blend smoothly across the front/back meridian.
    # This eliminates the visible seam at snz = 0 — the transition
    # becomes a gradual fade through the planet's limb instead of a
    # sharp fold.
    def _bilinear(sx, sy):
        sx = np.clip(sx, 0, src_w - 1)
        sy = np.clip(sy, 0, src_h - 1)
        x0 = np.floor(sx).astype(np.int32)
        y0 = np.floor(sy).astype(np.int32)
        x1_ = np.minimum(x0 + 1, src_w - 1)
        y1_ = np.minimum(y0 + 1, src_h - 1)
        fx = (sx - x0)[..., None]
        fy = (sy - y0)[..., None]
        c00 = disc_tex[y0, x0]
        c01 = disc_tex[y1_, x0]
        c10 = disc_tex[y0, x1_]
        c11 = disc_tex[y1_, x1_]
        top = c00 * (1 - fx) + c10 * fx
        bot = c01 * (1 - fx) + c11 * fx
        return top * (1 - fy) + bot * fy

    sample_y = sny * src_R + src_cy
    front_sample = _bilinear(snx * src_R + src_cx, sample_y)
    back_sample = _bilinear(-snx * src_R + src_cx, sample_y)
    # Smooth step centered on snz=0 with a soft transition band
    front_w = 0.5 + 0.5 * np.tanh(snz * 4.0)
    front_w_ = front_w[..., None]
    sampled = front_sample * front_w_ + back_sample * (1 - front_w_)

    # Subtle darkening on the back hemisphere — makes the rotation
    # feel like a real planet wrapping around instead of just a
    # perfect mirror. Smoothly fades from full to 80% as we cross.
    back_darken = 1.0 - 0.20 * (1 - front_w_)
    sampled = sampled * back_darken

    # Lambertian lighting using output normal
    lx, ly, lz = light_dir
    dot = np.maximum(0.0, onx * lx + ony * ly + onz * lz)
    bright = (ambient + (1.0 - ambient) * dot)[..., None]
    lit = np.clip(sampled * bright, 0.0, 255.0)

    rgba = np.zeros((diameter, diameter, 4), dtype=np.uint8)
    rgba[..., :3] = lit.astype(np.uint8)
    rgba[..., 3] = np.where(inside, 255, 0).astype(np.uint8)
    return rgba


def _find_largest_connected_blob_bbox(mask: np.ndarray) -> tuple[int, int, int, int]:
    """Find bbox of the largest connected True region via 4-neighbor
    flood-fill BFS. Returns (y0, y1, x0, x1) or whole-mask bbox on
    failure. No scipy/cv2 dependency.
    """
    H, W = mask.shape
    visited = np.zeros_like(mask, dtype=bool)
    best_size = 0
    best_bbox = (0, H, 0, W)
    # Iterate, finding each connected component
    for sy in range(0, H, 4):  # stride for speed; planets are big so 4-stride is fine
        for sx in range(0, W, 4):
            if not mask[sy, sx] or visited[sy, sx]:
                continue
            # BFS
            stack = [(sy, sx)]
            ys: list[int] = []
            xs: list[int] = []
            while stack:
                y, x = stack.pop()
                if y < 0 or y >= H or x < 0 or x >= W or not mask[y, x] or visited[y, x]:
                    continue
                visited[y, x] = True
                ys.append(y)
                xs.append(x)
                stack.append((y + 1, x))
                stack.append((y - 1, x))
                stack.append((y, x + 1))
                stack.append((y, x - 1))
            if len(ys) > best_size:
                best_size = len(ys)
                best_bbox = (min(ys), max(ys) + 1, min(xs), max(xs) + 1)
    return best_bbox


def crop_to_planet_disc(img: Image.Image) -> Image.Image:
    """Pluck JUST the planet's spherical disc out of a Firefly portrait
    that may include starfield, labels, moons, and other decoration
    around it. Returns a SQUARE crop centered on the disc.

    Approach (no scipy/cv2):
    1. Threshold to a binary mask of bright pixels (planet body).
    2. Aggressive morphological opening (PIL MinFilter then MaxFilter
       at kernel 31 = ~15-pixel radius) removes text labels, small
       star clusters, and other small bright features. The planet
       disc — hundreds of pixels across — survives.
    3. Take the LARGEST connected blob in the cleaned mask as the
       planet (labels are smaller and disconnected).
    4. Compute the centroid of that blob and a tight radial extent
       (max distance from centroid to any blob pixel). Crop a SQUARE
       of that diameter centered on the centroid.

    The crop is then stretched to 2:1 by the caller for use as a
    faux-equirectangular sphere texture.
    """
    # SIMPLE CENTER-CROP — Firefly planet paintings are uniformly
    # composed with the planet roughly centered in the frame. Sun
    # glows and starfields, when present, appear in the CORNERS of
    # the painting (upper-left typically). A center-crop at 60% of
    # the image side excludes those corners cleanly while still
    # capturing the full planet disc.
    #
    # This is more robust than centroid/blob-fitting because it
    # doesn't rely on brightness — which fails when the sun is as
    # bright as the planet, or when the planet has dark features
    # (oceans, shadows) that drop it below threshold.
    H = img.height
    W = img.width
    side = min(H, W)
    radius = side * 0.30  # 60% center crop → radius = side * 0.3
    cx = W / 2.0
    cy = H / 2.0
    # 5. Square crop centered on the inscribed-circle center.
    y0 = max(0, int(round(cy - radius)))
    y1 = min(H, int(round(cy + radius)))
    x0 = max(0, int(round(cx - radius)))
    x1 = min(W, int(round(cx + radius)))
    return img.crop((x0, y0, x1, y1))


def animate_planet(
    src_path: pathlib.Path,
    out_dir: pathlib.Path,
    frames: int,
    diameter: int,
) -> int:
    if not src_path.exists():
        print(f"  SKIP missing: {src_path.name}")
        return 0
    tex_img = Image.open(src_path).convert("RGB")
    tex_img = crop_to_planet_disc(tex_img)
    # Orthographic-sphere sampling: the cropped square IS the disc
    # texture. No equirectangular resize needed — sphere normals are
    # computed from the disc's own center + radius.
    disc_tex = np.asarray(tex_img, dtype=np.float32)

    out_dir.mkdir(parents=True, exist_ok=True)
    for i in range(frames):
        longitude = (i / frames) * 2.0 * math.pi
        rgba = render_frame_orthographic(disc_tex, diameter, longitude)
        out = Image.fromarray(rgba, mode="RGBA")
        out.save(out_dir / f"rot_{i:02d}.png", format="PNG", optimize=True)
    return frames


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--only", help="planet name substring filter")
    parser.add_argument("--frames", type=int, default=DEFAULT_FRAMES)
    parser.add_argument("--diameter", type=int, default=DEFAULT_DIAMETER)
    args = parser.parse_args()

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    sources = sorted(SRC_DIR.glob("planet_*.png"))
    if args.only:
        sources = [p for p in sources if args.only in p.stem]
    print(f"animating {len(sources)} planets at {args.frames} frames, {args.diameter}px diameter")
    print()

    ok = 0
    for src in sources:
        planet_id = src.stem.replace("planet_", "")
        out_dir = OUT_DIR / planet_id
        n = animate_planet(src, out_dir, args.frames, args.diameter)
        if n > 0:
            print(f"  OK   {planet_id:35s} -> animated/{planet_id}/rot_00..rot_{n-1:02d}.png  ({args.diameter}x{args.diameter})")
            ok += 1
    print()
    print(f"summary: {ok} planets animated")
    return 0


if __name__ == "__main__":
    sys.exit(main())
