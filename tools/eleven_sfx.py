"""Direct ElevenLabs Sound Effects API client.

Sibling to tools/eleven_music.py. Same auth (shared ELEVENLABS_API_KEY),
different endpoint. Used for UI/lander/scan/weapon SFX -- everything
that isn't a 90-second music loop.

API: POST https://api.elevenlabs.io/v1/sound-generation
Returns: binary audio (mp3 by default).

Example:
    from eleven_sfx import sfx_bytes, save_audio
    data, fmt = sfx_bytes("crisp menu click, sharp attack, quick decay", 0.5)
    save_audio(data, fmt, "menu_select.mp3")
"""

from __future__ import annotations

import io
import os
import sys
from pathlib import Path
from typing import Optional

import numpy as np
import requests
import soundfile as sf


API_BASE = "https://api.elevenlabs.io/v1"
DEFAULT_MODEL = "eleven_text_to_sound_v2"
# 128kbps stereo @ 44.1kHz is plenty for SFX (most are < 2s).
DEFAULT_OUTPUT_FORMAT = "mp3_44100_128"
# Higher than the 0.3 default -- SFX want the prompt obeyed strictly,
# not interpreted. 0.7 is a good baseline for our weapon / UI / lander
# SFX library; raise toward 0.9 for very specific timbres.
DEFAULT_PROMPT_INFLUENCE = 0.7


def _load_api_key() -> str:
    """Same loader as eleven_music: env first, then D:/.../development/.env."""
    key = os.environ.get("ELEVENLABS_API_KEY", "").strip()
    if key:
        return key
    env_path = Path("D:/Aaron/development/.env")
    if env_path.exists():
        for line in env_path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line.startswith("ELEVENLABS_API_KEY="):
                key = line.split("=", 1)[1].strip().strip('"').strip("'")
                if key:
                    return key
    raise RuntimeError(
        "ELEVENLABS_API_KEY not set in env or D:/Aaron/development/.env"
    )


def _decode_response(data: bytes, output_format: str):
    """mp3_*/opus_* -> libsndfile decodes. pcm_* -> raw int16 (assume mono)."""
    if output_format.startswith("mp3") or output_format.startswith("opus"):
        return sf.read(io.BytesIO(data))
    if output_format.startswith("pcm"):
        sr = int(output_format.split("_")[1])
        arr = np.frombuffer(data, dtype="<i2").astype(np.float32) / 32768.0
        return arr, sr
    raise ValueError(f"unsupported output_format: {output_format}")


def sfx_bytes(
    text: str,
    duration_s: float = 1.5,
    *,
    prompt_influence: float = DEFAULT_PROMPT_INFLUENCE,
    loop: bool = False,
    model_id: str = DEFAULT_MODEL,
    output_format: str = DEFAULT_OUTPUT_FORMAT,
    timeout: int = 120,
) -> tuple[bytes, str]:
    """Generate one sound effect; return (raw_audio_bytes, output_format).

    `text`: prompt describing the sound. Include attack/decay/material/
        size cues for snappier UI sounds (e.g. "sharp attack, quick decay,
        small metallic chime").
    `duration_s`: 0.5-30 seconds. The API floor of 0.5s is awkward for
        very short UI ticks; design prompts with front-loaded transient
        + quick tail so the perceived hit is shorter.
    `prompt_influence`: 0-1, higher = stricter adherence to the prompt.
        Default 0.7 (higher than ElevenLabs' 0.3 default) because SFX
        want the prompt obeyed, not interpreted.
    `loop`: True returns a clean-looping clip (handy for engine hums,
        scan-sweep, atmospheric entry).
    """
    api_key = _load_api_key()
    # Clamp duration to API range; let auto-calc kick in for very short ones.
    duration_s = max(0.5, min(30.0, float(duration_s)))
    body: dict = {
        "text": text,
        "duration_seconds": duration_s,
        "prompt_influence": float(prompt_influence),
        "model_id": model_id,
        "loop": bool(loop),
    }
    url = f"{API_BASE}/sound-generation?output_format={output_format}"
    r = requests.post(
        url,
        headers={
            "xi-api-key": api_key,
            "Content-Type": "application/json",
            "Accept": "*/*",
        },
        json=body,
        timeout=timeout,
    )
    if r.status_code != 200:
        try:
            err = r.json()
        except Exception:
            err = r.text[:400]
        raise RuntimeError(f"ElevenLabs /sound-generation HTTP {r.status_code}: {err}")
    return r.content, output_format


def sfx(text: str, duration_s: float = 1.5, **kwargs):
    """Decoded-array variant: returns (audio_array, sample_rate)."""
    data, fmt = sfx_bytes(text, duration_s, **kwargs)
    return _decode_response(data, fmt)


def _ext_for_format(output_format: str) -> str:
    if output_format.startswith("mp3"):
        return ".mp3"
    if output_format.startswith("opus"):
        return ".opus"
    return ".wav"


def save_audio(data: bytes, output_format: str, out_path: str | Path) -> Path:
    """Save raw API bytes to disk. MP3/Opus = byte passthrough (no
    decode loss); PCM = decode + soundfile-write PCM_16 WAV."""
    p = Path(out_path)
    p.parent.mkdir(parents=True, exist_ok=True)
    if output_format.startswith("mp3") or output_format.startswith("opus"):
        expected = _ext_for_format(output_format)
        if p.suffix.lower() != expected:
            raise ValueError(
                f"output_format {output_format} produces {expected!r} "
                f"but out_path is {p.name!r}"
            )
        p.write_bytes(data)
        return p
    audio, sr = _decode_response(data, output_format)
    sf.write(p, audio, sr, subtype="PCM_16")
    return p


def _cli() -> int:
    """CLI smoke-test: generate a clip and save it."""
    import argparse, time
    ap = argparse.ArgumentParser()
    ap.add_argument("--text", default="crisp menu select click, sharp attack, quick decay")
    ap.add_argument("--duration", type=float, default=0.5)
    ap.add_argument("--influence", type=float, default=DEFAULT_PROMPT_INFLUENCE)
    ap.add_argument("--loop", action="store_true")
    ap.add_argument("--out", default=None)
    args = ap.parse_args()
    t0 = time.time()
    data, fmt = sfx_bytes(
        args.text, args.duration,
        prompt_influence=args.influence, loop=args.loop,
    )
    dt = time.time() - t0
    print(f"got {len(data)} bytes ({fmt}) in {dt:.1f}s")
    if args.out:
        save_audio(data, fmt, args.out)
        print(f"wrote {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(_cli())
