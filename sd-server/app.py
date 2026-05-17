"""SCZ-dedicated Stable Diffusion Flask server.

A focused image-generation backend for the Star Control Zero project,
intentionally separate from any other SD instance in the Skippy
ecosystem. Listens on port 5005 by default.

Models supported (env var SCZ_SD_MODEL):
  sdxl-turbo     stabilityai/sdxl-turbo            (default; ~7GB, 1-4 step)
  sdxl-base      stabilityai/stable-diffusion-xl-base-1.0  (~12GB, 25-step)
  sd15           runwayml/stable-diffusion-v1-5    (~4GB, 25-step)

Endpoints:
  GET  /health                  status + active model
  POST /txt2img                 prompt → PNG bytes (Firefly substitute)
  POST /img2img                 image + prompt + strength → PNG bytes
                                (per-individual variants, refinement passes)
  POST /inpaint                 image + mask + prompt → PNG bytes
                                (body-part swaps for articulation frames)
  POST /chromakey               image (matte navy) → PNG with alpha
                                (post-Firefly cleanup; uses rembg if avail)

All POST endpoints accept JSON with base64-encoded images. PNG bytes
are returned as base64 strings under `image` key. Errors return JSON
with `error` and a meaningful HTTP code.
"""

from __future__ import annotations

import base64
import io
import logging
import os
import time
from typing import Any

from flask import Flask, jsonify, request
from flask_cors import CORS
from PIL import Image

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] [%(levelname)s] %(message)s",
)
log = logging.getLogger("scz-sd")


# ---------------------------------------------------------------------------
# Lazy model loading — heavy, so done once on first request.
# ---------------------------------------------------------------------------

_pipelines: dict[str, Any] = {}   # task -> diffusers pipeline
_model_name: str = ""
_torch_dtype = None
_device = "cpu"


def _load_torch():
    global _torch_dtype, _device
    import torch
    if torch.cuda.is_available():
        _device = "cuda"
        _torch_dtype = torch.float16
        log.info(
            "CUDA available: %s (%.1f GB VRAM)",
            torch.cuda.get_device_name(0),
            torch.cuda.get_device_properties(0).total_memory / 1e9,
        )
    else:
        _device = "cpu"
        _torch_dtype = torch.float32
        log.warning("CUDA not available — using CPU (will be SLOW)")
    return torch


def _model_id(env_value: str) -> str:
    table = {
        "sdxl-turbo": "stabilityai/sdxl-turbo",
        "sdxl-base":  "stabilityai/stable-diffusion-xl-base-1.0",
        "sd15":       "runwayml/stable-diffusion-v1-5",
    }
    return table.get(env_value, env_value)


def get_pipeline(task: str):
    """Lazily load (or fetch from cache) the pipeline for one of:
       'txt2img', 'img2img', 'inpaint'.
    All three share the same model weights — diffusers reuses the
    underlying components, so the second call is fast.
    """
    if task in _pipelines:
        return _pipelines[task]
    global _model_name
    _model_name = _model_id(os.environ.get("SCZ_SD_MODEL", "sdxl-turbo"))
    torch = _load_torch()
    log.info("Loading %s for task=%s", _model_name, task)
    t0 = time.time()
    from diffusers import (
        StableDiffusionXLPipeline,
        StableDiffusionXLImg2ImgPipeline,
        StableDiffusionXLInpaintPipeline,
        StableDiffusionPipeline,
        StableDiffusionImg2ImgPipeline,
        StableDiffusionInpaintPipeline,
        AutoPipelineForText2Image,
        AutoPipelineForImage2Image,
        AutoPipelineForInpainting,
    )
    if task == "txt2img":
        pipe = AutoPipelineForText2Image.from_pretrained(
            _model_name, torch_dtype=_torch_dtype, variant="fp16" if _torch_dtype != None else None
        )
    elif task == "img2img":
        pipe = AutoPipelineForImage2Image.from_pretrained(
            _model_name, torch_dtype=_torch_dtype, variant="fp16" if _torch_dtype != None else None
        )
    elif task == "inpaint":
        pipe = AutoPipelineForInpainting.from_pretrained(
            _model_name, torch_dtype=_torch_dtype, variant="fp16" if _torch_dtype != None else None
        )
    else:
        raise ValueError(f"unknown task: {task}")

    pipe = pipe.to(_device)
    # Memory-efficient attention (saves ~30% VRAM)
    try:
        pipe.enable_xformers_memory_efficient_attention()
    except Exception:
        pass
    # If VRAM is tight, model offload pages weights to CPU between calls
    if os.environ.get("SCZ_SD_CPU_OFFLOAD") == "1":
        pipe.enable_model_cpu_offload()
        log.info("Enabled CPU offload (slower but works in lower VRAM)")
    _pipelines[task] = pipe
    log.info("Loaded in %.1fs", time.time() - t0)
    return pipe


# ---------------------------------------------------------------------------
# Encode/decode helpers
# ---------------------------------------------------------------------------

def _b64_to_pil(b64: str) -> Image.Image:
    if b64.startswith("data:"):
        b64 = b64.split(",", 1)[1]
    raw = base64.b64decode(b64)
    return Image.open(io.BytesIO(raw))


def _pil_to_b64(img: Image.Image) -> str:
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return base64.b64encode(buf.getvalue()).decode("ascii")


# ---------------------------------------------------------------------------
# Flask app
# ---------------------------------------------------------------------------

app = Flask(__name__)
CORS(app)


@app.route("/health", methods=["GET"])
def health():
    return jsonify({
        "status": "ok",
        "model": _model_name or os.environ.get("SCZ_SD_MODEL", "sdxl-turbo"),
        "device": _device,
        "loaded_tasks": sorted(_pipelines.keys()),
    })


@app.route("/txt2img", methods=["POST"])
def txt2img():
    data = request.get_json(force=True)
    prompt = data.get("prompt", "").strip()
    if not prompt:
        return jsonify({"error": "missing prompt"}), 400
    pipe = get_pipeline("txt2img")
    # SDXL-Turbo defaults: very low step count, no negative prompt, guidance 0
    is_turbo = "turbo" in (_model_name or "").lower()
    kwargs = dict(
        prompt=prompt,
        width=data.get("width", 1024),
        height=data.get("height", 1024),
        num_inference_steps=data.get("steps", 4 if is_turbo else 25),
        guidance_scale=data.get("guidance", 0.0 if is_turbo else 7.5),
    )
    if data.get("seed") is not None:
        import torch
        kwargs["generator"] = torch.Generator(device=_device).manual_seed(int(data["seed"]))
    if not is_turbo and data.get("negative_prompt"):
        kwargs["negative_prompt"] = data["negative_prompt"]
    t0 = time.time()
    result = pipe(**kwargs).images[0]
    log.info("txt2img %dx%d in %.1fs", kwargs["width"], kwargs["height"], time.time() - t0)
    return jsonify({"image": _pil_to_b64(result), "took_s": round(time.time() - t0, 2)})


@app.route("/img2img", methods=["POST"])
def img2img():
    """Per-individual variant generation + refinement passes over a
    Firefly base. Low strength (0.2-0.4) preserves identity; higher
    strength (0.5-0.7) repurposes the composition.
    """
    data = request.get_json(force=True)
    prompt = data.get("prompt", "").strip()
    image_b64 = data.get("image")
    if not prompt or not image_b64:
        return jsonify({"error": "need prompt + image"}), 400
    init = _b64_to_pil(image_b64).convert("RGB")
    pipe = get_pipeline("img2img")
    is_turbo = "turbo" in (_model_name or "").lower()
    kwargs = dict(
        prompt=prompt,
        image=init,
        strength=data.get("strength", 0.35),
        num_inference_steps=data.get("steps", 4 if is_turbo else 30),
        guidance_scale=data.get("guidance", 0.0 if is_turbo else 7.5),
    )
    if data.get("seed") is not None:
        import torch
        kwargs["generator"] = torch.Generator(device=_device).manual_seed(int(data["seed"]))
    t0 = time.time()
    result = pipe(**kwargs).images[0]
    log.info(
        "img2img strength=%.2f steps=%d in %.1fs",
        kwargs["strength"], kwargs["num_inference_steps"], time.time() - t0,
    )
    return jsonify({"image": _pil_to_b64(result), "took_s": round(time.time() - t0, 2)})


@app.route("/inpaint", methods=["POST"])
def inpaint():
    """Body-part swaps for articulation frames. The mask is a B/W image
    where WHITE = repaint, BLACK = preserve. Use a soft mask edge for
    natural blending.
    """
    data = request.get_json(force=True)
    prompt = data.get("prompt", "").strip()
    image_b64 = data.get("image")
    mask_b64 = data.get("mask")
    if not prompt or not image_b64 or not mask_b64:
        return jsonify({"error": "need prompt + image + mask"}), 400
    init = _b64_to_pil(image_b64).convert("RGB")
    mask = _b64_to_pil(mask_b64).convert("L")
    pipe = get_pipeline("inpaint")
    is_turbo = "turbo" in (_model_name or "").lower()
    kwargs = dict(
        prompt=prompt,
        image=init,
        mask_image=mask,
        strength=data.get("strength", 0.9),
        num_inference_steps=data.get("steps", 4 if is_turbo else 30),
        guidance_scale=data.get("guidance", 0.0 if is_turbo else 7.5),
    )
    if data.get("seed") is not None:
        import torch
        kwargs["generator"] = torch.Generator(device=_device).manual_seed(int(data["seed"]))
    t0 = time.time()
    result = pipe(**kwargs).images[0]
    log.info("inpaint in %.1fs", time.time() - t0)
    return jsonify({"image": _pil_to_b64(result), "took_s": round(time.time() - t0, 2)})


@app.route("/chromakey", methods=["POST"])
def chromakey():
    """Strip a solid-color background (default: SCZ matte navy
    #0a0e1a) to alpha. Uses rembg's u2net model if installed for
    cleaner edges; falls back to simple color-distance keying.
    """
    data = request.get_json(force=True)
    image_b64 = data.get("image")
    if not image_b64:
        return jsonify({"error": "need image"}), 400
    img = _b64_to_pil(image_b64).convert("RGBA")
    mode = data.get("mode", "rembg")  # rembg | color
    if mode == "rembg":
        try:
            from rembg import remove
            out = remove(img)
            return jsonify({"image": _pil_to_b64(out), "mode": "rembg"})
        except Exception as e:
            log.info("rembg unavailable (%s), falling back to color key", e)
            mode = "color"
    if mode == "color":
        target = data.get("target_rgb", [10, 14, 26])
        threshold = data.get("threshold", 70)
        pixels = img.load()
        w, h = img.size
        tr, tg, tb = target
        t2 = threshold * threshold
        for y in range(h):
            for x in range(w):
                r, g, b, a = pixels[x, y]
                dr, dg, db = r - tr, g - tg, b - tb
                if dr * dr + dg * dg + db * db <= t2:
                    pixels[x, y] = (r, g, b, 0)
        return jsonify({"image": _pil_to_b64(img), "mode": "color"})
    return jsonify({"error": f"unknown mode {mode}"}), 400


if __name__ == "__main__":
    port = int(os.environ.get("SCZ_SD_PORT", 5005))
    log.info("Starting scz-sd on http://0.0.0.0:%d", port)
    log.info("Model: %s (override with SCZ_SD_MODEL)", _model_id(os.environ.get("SCZ_SD_MODEL", "sdxl-turbo")))
    log.info("First request loads weights — expect 30-90s on cold start")
    # threaded=False is important: diffusers pipelines are not thread-safe
    app.run(host="0.0.0.0", port=port, threaded=False, debug=False)
