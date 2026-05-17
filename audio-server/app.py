"""SCZ-dedicated audio-generation Flask server.

Sibling to sd-server. Listens on port 5006. Build-time AI audio
generation for the slice's music stems + SFX library, per the design
in references/lore/music-system.md. Runtime mixing is done in
pygame.mixer by the game itself; this server is OFFLINE infrastructure.

Default model: cvssp/audioldm2-music — open-access, music+SFX from
text prompts, ~6GB VRAM, 16 kHz native (we resample to 44.1 kHz).
Other supported models:
  audioldm2          general (music + SFX)
  audioldm2-music    music-only (sharper for our use case)
  audioldm2-large    larger params, slower
  stable-audio-open  47s stereo at 44.1 kHz — best quality but GATED
                     (requires HF login + license acceptance at
                     https://huggingface.co/stabilityai/stable-audio-open-1.0
                     and HF_TOKEN env var)
Override via SCZ_AUDIO_MODEL.

Endpoints:
  GET  /health        status + active model
  POST /music         music clip from prompt (recommends key + bpm in
                      prompt for inter-stem coherence)
  POST /sfx           short SFX clip; identical mechanics, semantically
                      framed for short clips
  POST /generate      generic: same backing call as both above

All POSTs accept JSON, return JSON with `audio_b64` (base64-encoded
WAV) + `sample_rate` + `duration_s` + `took_s`. Audio is mono- or
stereo-WAV; the caller can re-encode to OGG/FLAC if needed.
"""

from __future__ import annotations

import base64
import io
import logging
import os
import time
from typing import Any

import numpy as np
import soundfile as sf
from flask import Flask, jsonify, request
from flask_cors import CORS


logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] [%(levelname)s] %(message)s",
)
log = logging.getLogger("scz-audio")


# ---------------------------------------------------------------------------
# Lazy model loading
# ---------------------------------------------------------------------------

_pipeline: Any = None
_model_name: str = ""
_torch_dtype = None
_device = "cpu"
_sample_rate: int = 44100   # stable-audio-open native rate


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
        "stable-audio-open": "stabilityai/stable-audio-open-1.0",
        "stable-audio":      "stabilityai/stable-audio-open-1.0",
        "audioldm2":         "cvssp/audioldm2",
        "audioldm2-music":   "cvssp/audioldm2-music",
        "audioldm2-large":   "cvssp/audioldm2-large",
        "audioldm":          "cvssp/audioldm-s-full-v2",
    }
    return table.get(env_value, env_value)


def _is_stable_audio(model_id: str) -> bool:
    return "stable-audio" in model_id.lower()


def get_pipeline():
    """Lazy-load the audio pipeline on first request. Picks the right
    diffusers pipeline class based on the model id."""
    global _pipeline, _model_name, _sample_rate
    if _pipeline is not None:
        return _pipeline
    _model_name = _model_id(os.environ.get("SCZ_AUDIO_MODEL", "audioldm2-music"))
    torch = _load_torch()
    log.info("Loading %s ...", _model_name)
    t0 = time.time()
    if _is_stable_audio(_model_name):
        from diffusers import StableAudioPipeline
        _pipeline = StableAudioPipeline.from_pretrained(
            _model_name, torch_dtype=_torch_dtype,
        )
        _sample_rate = 44100
    elif "audioldm2" in _model_name.lower():
        from diffusers import AudioLDM2Pipeline
        _pipeline = AudioLDM2Pipeline.from_pretrained(
            _model_name, torch_dtype=_torch_dtype,
        )
        _sample_rate = 16000  # AudioLDM2 native; resampled in client if needed
    else:
        from diffusers import AudioLDMPipeline
        _pipeline = AudioLDMPipeline.from_pretrained(
            _model_name, torch_dtype=_torch_dtype,
        )
        _sample_rate = 16000
    _pipeline = _pipeline.to(_device)
    try:
        _pipeline.enable_xformers_memory_efficient_attention()
    except Exception:
        pass
    if os.environ.get("SCZ_AUDIO_CPU_OFFLOAD") == "1":
        _pipeline.enable_model_cpu_offload()
        log.info("Enabled CPU offload")
    log.info("Loaded in %.1fs (sample rate %d Hz)", time.time() - t0, _sample_rate)
    return _pipeline


# ---------------------------------------------------------------------------
# Audio I/O helpers
# ---------------------------------------------------------------------------

def _audio_to_b64_wav(audio: np.ndarray, sample_rate: int) -> str:
    """Encode an (n_channels, n_samples) float32 array as base64 WAV."""
    if audio.ndim == 1:
        # Mono — keep as 1-D for soundfile
        data = audio.astype(np.float32)
    elif audio.ndim == 2:
        # soundfile expects (n_samples, n_channels)
        if audio.shape[0] < audio.shape[1]:
            data = np.ascontiguousarray(audio.T.astype(np.float32))
        else:
            data = audio.astype(np.float32)
    else:
        raise ValueError(f"unexpected audio shape {audio.shape}")
    buf = io.BytesIO()
    sf.write(buf, data, sample_rate, format="WAV", subtype="FLOAT")
    return base64.b64encode(buf.getvalue()).decode("ascii")


def _do_generation(
    prompt: str,
    duration_s: float,
    seed: int | None,
    negative_prompt: str | None,
    steps: int,
    guidance: float,
) -> tuple[np.ndarray, int]:
    """Run the underlying generation. Returns (audio array, sample rate).

    Handles the parameter-name difference between StableAudioPipeline
    (uses audio_end_in_s) and AudioLDM2Pipeline (uses audio_length_in_s).
    """
    import torch
    pipe = get_pipeline()
    kwargs: dict = {
        "prompt": prompt,
        "num_inference_steps": int(steps),
        "guidance_scale": float(guidance),
    }
    if _is_stable_audio(_model_name):
        kwargs["audio_end_in_s"] = float(duration_s)
    else:
        # AudioLDM / AudioLDM2 use audio_length_in_s
        kwargs["audio_length_in_s"] = float(duration_s)
    if negative_prompt:
        kwargs["negative_prompt"] = negative_prompt
    if seed is not None:
        kwargs["generator"] = torch.Generator(device=_device).manual_seed(int(seed))
    result = pipe(**kwargs)
    audio = result.audios[0]
    if hasattr(audio, "cpu"):
        audio = audio.cpu().numpy()
    audio = np.asarray(audio, dtype=np.float32)
    return audio, _sample_rate


# ---------------------------------------------------------------------------
# Flask app
# ---------------------------------------------------------------------------

app = Flask(__name__)
CORS(app)


@app.route("/health", methods=["GET"])
def health():
    return jsonify({
        "status": "ok",
        "model": _model_name or os.environ.get("SCZ_AUDIO_MODEL", "audioldm2-music"),
        "device": _device,
        "sample_rate": _sample_rate,
        "loaded": _pipeline is not None,
    })


def _do_endpoint(default_duration_s: float):
    data = request.get_json(force=True)
    prompt = (data.get("prompt") or "").strip()
    if not prompt:
        return jsonify({"error": "missing prompt"}), 400
    duration_s = float(data.get("duration_s", default_duration_s))
    seed = data.get("seed")
    negative_prompt = (data.get("negative_prompt") or "").strip() or None
    steps = int(data.get("steps", 100))
    guidance = float(data.get("guidance", 7.0))
    t0 = time.time()
    try:
        audio, sr = _do_generation(prompt, duration_s, seed, negative_prompt, steps, guidance)
    except Exception as e:
        log.exception("generation failed")
        return jsonify({"error": str(e)}), 500
    took = time.time() - t0
    log.info("generated %.1fs at %dHz in %.1fs (steps=%d)", duration_s, sr, took, steps)
    return jsonify({
        "audio_b64": _audio_to_b64_wav(audio, sr),
        "sample_rate": sr,
        "duration_s": duration_s,
        "took_s": round(took, 2),
        "format": "wav",
    })


@app.route("/music", methods=["POST"])
def music_endpoint():
    """Music generation. Default 30 s; include key + bpm in the prompt
    when generating multiple stems for the same track ('… in C minor at
    110 bpm …') so they line up at mix time."""
    return _do_endpoint(default_duration_s=30.0)


@app.route("/sfx", methods=["POST"])
def sfx_endpoint():
    """Short sound effect. Default 3 s. Stable Audio Open handles SFX
    from text prompts identically to music — the endpoint exists for
    semantic clarity and shorter default duration."""
    return _do_endpoint(default_duration_s=3.0)


@app.route("/generate", methods=["POST"])
def generate_endpoint():
    """Generic single endpoint, equivalent to /music with default 10 s."""
    return _do_endpoint(default_duration_s=10.0)


if __name__ == "__main__":
    port = int(os.environ.get("SCZ_AUDIO_PORT", 5006))
    log.info("Starting scz-audio on http://0.0.0.0:%d", port)
    log.info("Model: %s (override with SCZ_AUDIO_MODEL)",
             _model_id(os.environ.get("SCZ_AUDIO_MODEL", "audioldm2-music")))
    log.info("First request loads weights — expect 60-180s on cold start")
    # threaded=False because diffusers pipelines are not thread-safe
    app.run(host="0.0.0.0", port=port, threaded=False, debug=False)
