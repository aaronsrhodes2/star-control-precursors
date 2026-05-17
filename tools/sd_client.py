"""Thin client for the scz-sd Flask server (port 5005).

Used by image-generation scripts in this project. The server runs at
http://localhost:5005 by default; configure via SCZ_SD_URL env var.

Example:
    from tools.sd_client import txt2img, img2img, inpaint

    img = txt2img(
        prompt="A full-body avatar painting of...",
        width=848, height=1264,
    )
    img.save("out.png")

    variant = img2img(
        image="assets/.../avatar_commander_halia.png",
        prompt="same Furling officer, weathered scar over left eye",
        strength=0.3,
    )
    variant.save("variant.png")
"""

from __future__ import annotations

import base64
import io
import os
from pathlib import Path
from typing import Union

import requests
from PIL import Image


SD_URL = os.environ.get("SCZ_SD_URL", "http://localhost:5005")


PathOrImage = Union[str, Path, Image.Image]


def _pil_from_path_or_image(src: PathOrImage) -> Image.Image:
    if isinstance(src, Image.Image):
        return src
    return Image.open(src)


def _pil_to_b64(img: Image.Image) -> str:
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return base64.b64encode(buf.getvalue()).decode("ascii")


def _b64_to_pil(b64: str) -> Image.Image:
    return Image.open(io.BytesIO(base64.b64decode(b64)))


def health() -> dict:
    return requests.get(f"{SD_URL}/health", timeout=5).json()


def txt2img(
    prompt: str,
    width: int = 1024,
    height: int = 1024,
    steps: int | None = None,
    guidance: float | None = None,
    seed: int | None = None,
    negative_prompt: str | None = None,
) -> Image.Image:
    """Generate an image from a prompt. Server picks default steps/guidance
    based on the active model (SDXL-Turbo: 4 steps, guidance 0; SDXL-Base:
    25 steps, guidance 7.5)."""
    body: dict = {"prompt": prompt, "width": width, "height": height}
    if steps is not None:           body["steps"] = steps
    if guidance is not None:        body["guidance"] = guidance
    if seed is not None:            body["seed"] = seed
    if negative_prompt is not None: body["negative_prompt"] = negative_prompt
    r = requests.post(f"{SD_URL}/txt2img", json=body, timeout=300)
    r.raise_for_status()
    data = r.json()
    return _b64_to_pil(data["image"])


def img2img(
    image: PathOrImage,
    prompt: str,
    strength: float = 0.35,
    steps: int | None = None,
    guidance: float | None = None,
    seed: int | None = None,
) -> Image.Image:
    """Generate a refined / varied version of an input image.

    strength: 0.2-0.4 preserves identity for per-individual variants,
              0.5-0.7 repurposes the composition.
    """
    init = _pil_from_path_or_image(image).convert("RGB")
    body: dict = {
        "prompt": prompt,
        "image": _pil_to_b64(init),
        "strength": strength,
    }
    if steps is not None:    body["steps"] = steps
    if guidance is not None: body["guidance"] = guidance
    if seed is not None:     body["seed"] = seed
    r = requests.post(f"{SD_URL}/img2img", json=body, timeout=300)
    r.raise_for_status()
    return _b64_to_pil(r.json()["image"])


def inpaint(
    image: PathOrImage,
    mask: PathOrImage,
    prompt: str,
    strength: float = 0.9,
    steps: int | None = None,
    guidance: float | None = None,
    seed: int | None = None,
) -> Image.Image:
    """Inpaint a masked region of an image. The mask is WHITE where to
    repaint, BLACK to preserve. Used for body-part articulation frames:
    mask out just the head/arms/eyes and regenerate them in a new pose
    while preserving the rest of the avatar."""
    init = _pil_from_path_or_image(image).convert("RGB")
    msk = _pil_from_path_or_image(mask).convert("L")
    body: dict = {
        "prompt": prompt,
        "image": _pil_to_b64(init),
        "mask": _pil_to_b64(msk),
        "strength": strength,
    }
    if steps is not None:    body["steps"] = steps
    if guidance is not None: body["guidance"] = guidance
    if seed is not None:     body["seed"] = seed
    r = requests.post(f"{SD_URL}/inpaint", json=body, timeout=300)
    r.raise_for_status()
    return _b64_to_pil(r.json()["image"])


def chromakey(
    image: PathOrImage,
    mode: str = "rembg",
    target_rgb: tuple[int, int, int] = (10, 14, 26),
    threshold: int = 70,
) -> Image.Image:
    """Strip a solid-color background to alpha. mode='rembg' uses
    rembg/u2net (cleaner edges) if installed on the server; 'color'
    uses distance keying."""
    src = _pil_from_path_or_image(image)
    body: dict = {
        "image": _pil_to_b64(src),
        "mode": mode,
        "target_rgb": list(target_rgb),
        "threshold": threshold,
    }
    r = requests.post(f"{SD_URL}/chromakey", json=body, timeout=60)
    r.raise_for_status()
    return _b64_to_pil(r.json()["image"])


if __name__ == "__main__":
    # Quick self-test against the running server
    import sys
    try:
        h = health()
        print(f"OK - {h}")
    except Exception as e:
        print(f"FAIL - {e}", file=sys.stderr)
        sys.exit(1)
