"""Direct ElevenLabs Music API client.

Per Aaron's directive (2026-05-17): ElevenLabs handles ASSET-TIME music
generation now. The local AudioLDM2 audio-server stays in tree for later
use in the runtime variation engine, but build-time stems come from
ElevenLabs because the quality is much higher.

API: POST https://api.elevenlabs.io/v1/music
Auth: xi-api-key header (key read from D:/Aaron/development/.env)
Returns: binary audio file (mp3 by default; configurable via output_format)

Pricing: ~2000 characters per minute of music. 90s loop × 5 stems
≈ 15000 chars per multi-stem context.

Two ways to use this module:

    # 1. music_bytes() — returns RAW response. Best for game assets
    #    because we save the MP3 directly to disk (5× smaller files
    #    than decoded WAV; pygame.mixer loads MP3 natively).
    from eleven_music import music_bytes, save_audio
    data, fmt = music_bytes("upbeat synth in C minor at 108 bpm", 90)
    save_audio(data, fmt, "hyperspace_bass.mp3")

    # 2. music() — decodes to (numpy_array, sample_rate) for inspection
    #    + WAV-write workflows.
    from eleven_music import music, save_wav
    audio, sr = music("upbeat synth in C minor at 108 bpm", 90)
    save_wav(audio, sr, "hyperspace_bass.wav")
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
DEFAULT_MODEL = "music_v1"
# pygame.mixer wants 44.1 kHz. Pick mp3 because it's smaller than PCM and
# soundfile/libsndfile decode it fine. Bitrate 192 is near-transparent.
# If we ever need lossless, switch to `pcm_44100` (raw little-endian
# int16) — but we'd need to know channel count from response headers.
DEFAULT_OUTPUT_FORMAT = "mp3_44100_192"


def _load_api_key() -> str:
    """Read the ElevenLabs API key from env, falling back to
    D:/Aaron/development/.env (ecosystem default)."""
    key = os.environ.get("ELEVENLABS_API_KEY", "").strip()
    if key:
        return key
    # Fall back to the ecosystem-level .env (shared with SkippyTel etc.)
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
    """Decode the API response bytes into (audio_array, sample_rate).

    mp3_* → libsndfile decodes the mp3 directly (channel count is in the
    file header).

    pcm_* → raw little-endian int16. The response carries no header so
    we have to infer/assume stereo (ElevenLabs Music's pcm output is
    stereo per the docs)."""
    if output_format.startswith("mp3"):
        audio, sr = sf.read(io.BytesIO(data))
        return audio, sr
    if output_format.startswith("pcm"):
        # Parse sample rate from format string e.g. "pcm_44100" → 44100
        sr = int(output_format.split("_")[1])
        # Raw int16 little-endian; ElevenLabs music output is stereo.
        arr = np.frombuffer(data, dtype="<i2").astype(np.float32) / 32768.0
        if arr.size % 2 == 0:
            arr = arr.reshape(-1, 2)  # interleaved stereo → (n_frames, 2)
        return arr, sr
    raise ValueError(f"unsupported output_format: {output_format}")


def music_bytes(
    prompt: str,
    duration_s: float = 90.0,
    model_id: str = DEFAULT_MODEL,
    instrumental: bool = True,
    output_format: str = DEFAULT_OUTPUT_FORMAT,
    timeout: int = 300,
) -> tuple[bytes, str]:
    """Generate music; return (raw_audio_bytes, output_format).

    Prefer this for game-asset workflows so we can save the MP3
    directly. Per the docstring at module-top, MP3 saves ~5× smaller
    than re-encoded WAV.

    NOTE: ElevenLabs Music's `seed` parameter is gated to composition_plan
    mode, not bare-prompt mode. Asset-time determinism is provided by
    committing the generated audio file to git — re-runs deliberately
    don't reproduce the exact bytes (the API picks a fresh seed each
    call).
    """
    api_key = _load_api_key()
    music_length_ms = int(duration_s * 1000)
    body: dict = {
        "prompt": prompt,
        "music_length_ms": music_length_ms,
        "model_id": model_id,
        "force_instrumental": bool(instrumental),
    }
    url = f"{API_BASE}/music?output_format={output_format}"
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
        raise RuntimeError(f"ElevenLabs /music HTTP {r.status_code}: {err}")
    return r.content, output_format


def music(
    prompt: str,
    duration_s: float = 90.0,
    **kwargs,
):
    """Decoded-array variant: returns (audio_array, sample_rate)."""
    data, fmt = music_bytes(prompt, duration_s, **kwargs)
    return _decode_response(data, fmt)


def _ext_for_format(output_format: str) -> str:
    if output_format.startswith("mp3"):
        return ".mp3"
    if output_format.startswith("opus"):
        return ".opus"
    if output_format.startswith("pcm") or output_format.startswith("ulaw") or output_format.startswith("alaw"):
        return ".wav"  # raw PCM gets wrapped in WAV; ulaw/alaw too
    return ".bin"


def save_audio(data: bytes, output_format: str, out_path: str | Path) -> Path:
    """Write raw ElevenLabs response bytes to disk.

    For MP3 / Opus formats this is a direct byte-passthrough (no decode
    round-trip, no re-encode quality loss). For PCM formats the function
    falls back to decode + soundfile so we land a valid WAV.
    """
    p = Path(out_path)
    p.parent.mkdir(parents=True, exist_ok=True)
    if output_format.startswith("mp3") or output_format.startswith("opus"):
        # Suffix sanity check — caller should match the file extension
        # to the actual content. Don't silently rewrite.
        expected = _ext_for_format(output_format)
        if p.suffix.lower() != expected:
            raise ValueError(
                f"output_format {output_format} produces {expected!r} "
                f"but out_path is {p.name!r}"
            )
        p.write_bytes(data)
        return p
    # PCM-family: decode to ndarray then write as PCM_16 WAV.
    audio, sr = _decode_response(data, output_format)
    sf.write(p, audio, sr, subtype="PCM_16")
    return p


def save_wav(audio, sample_rate: int, out_path: str | Path) -> Path:
    """Write decoded audio to a 16-bit PCM .wav. Use save_audio() instead
    when you've called music_bytes() and want to keep the original MP3."""
    p = Path(out_path)
    p.parent.mkdir(parents=True, exist_ok=True)
    sf.write(p, audio, sample_rate, subtype="PCM_16")
    return p


def _cli() -> int:
    """CLI smoke-test: generate a clip and save it (MP3 by default)."""
    import argparse, time
    ap = argparse.ArgumentParser()
    ap.add_argument("--prompt", default="dark slow synth pad in C minor at 80 bpm")
    ap.add_argument("--duration", type=float, default=5.0)
    ap.add_argument("--out", default=None, help="Output path (.mp3 or .wav)")
    args = ap.parse_args()
    t0 = time.time()
    out_fmt = DEFAULT_OUTPUT_FORMAT
    data, fmt = music_bytes(args.prompt, args.duration, output_format=out_fmt)
    dt = time.time() - t0
    print(f"got {len(data)} bytes ({fmt}) in {dt:.1f}s")
    if args.out:
        out = Path(args.out)
        if out.suffix.lower() == ".wav":
            # decode + write WAV
            audio, sr = _decode_response(data, fmt)
            save_wav(audio, sr, out)
        else:
            save_audio(data, fmt, out)
        print(f"wrote {out}")
    return 0


if __name__ == "__main__":
    sys.exit(_cli())
