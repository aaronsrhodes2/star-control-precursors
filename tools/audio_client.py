"""Thin client for the scz-audio Flask server (port 5006).

Used by music + SFX generation scripts. Configurable via SCZ_AUDIO_URL.

Example:
    from tools.audio_client import music, sfx, health

    audio, sr = music(
        prompt="Hyperspace bass stem, mid-tempo synth, in C minor at 110 bpm",
        duration=30, seed=42,
    )
    import soundfile as sf
    sf.write("hyperspace_bass.wav", audio, sr)
"""

from __future__ import annotations

import base64
import io
import os
from pathlib import Path

import requests
import soundfile as sf


AUDIO_URL = os.environ.get("SCZ_AUDIO_URL", "http://localhost:5006")


def health() -> dict:
    return requests.get(f"{AUDIO_URL}/health", timeout=5).json()


def _decode(b64: str):
    """Decode the server's base64 WAV. Returns (audio_array, sample_rate)."""
    return sf.read(io.BytesIO(base64.b64decode(b64)))


def _call(endpoint: str, body: dict, timeout: int):
    r = requests.post(f"{AUDIO_URL}/{endpoint}", json=body, timeout=timeout)
    r.raise_for_status()
    data = r.json()
    audio, sr = _decode(data["audio_b64"])
    return audio, sr


def music(
    prompt: str,
    duration: float = 30.0,
    seed: int | None = None,
    negative_prompt: str | None = None,
    steps: int = 100,
    guidance: float = 7.0,
):
    """Music generation. For multi-stem coherence include key+bpm in the
    prompt for every stem. Returns (audio array, sample rate)."""
    body: dict = {"prompt": prompt, "duration_s": float(duration), "steps": steps, "guidance": guidance}
    if seed is not None: body["seed"] = int(seed)
    if negative_prompt: body["negative_prompt"] = negative_prompt
    return _call("music", body, timeout=300)


def sfx(
    prompt: str,
    duration: float = 3.0,
    seed: int | None = None,
    negative_prompt: str | None = None,
    steps: int = 60,
    guidance: float = 7.0,
):
    """Sound-effect generation. Shorter default duration than /music
    but mechanically identical."""
    body: dict = {"prompt": prompt, "duration_s": float(duration), "steps": steps, "guidance": guidance}
    if seed is not None: body["seed"] = int(seed)
    if negative_prompt: body["negative_prompt"] = negative_prompt
    return _call("sfx", body, timeout=180)


def save_wav(audio, sample_rate: int, out_path: str | Path) -> Path:
    p = Path(out_path)
    p.parent.mkdir(parents=True, exist_ok=True)
    sf.write(p, audio, sample_rate)
    return p


if __name__ == "__main__":
    # Quick health check
    import sys
    try:
        print(health())
    except Exception as e:
        print(f"FAIL: {e}", file=sys.stderr)
        sys.exit(1)
