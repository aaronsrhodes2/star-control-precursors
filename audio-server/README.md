# scz-audio — Dedicated audio-generation server for Star Control Zero

A focused Flask + diffusers backend on port **5006** for SCZ music
and SFX work. Build-time only: it produces stem files for the slice's
contextual music system + the SFX library. **Runtime audio playback
is `pygame.mixer` in the game itself, not this server.**

Sibling to `sd-server/` (image generation, port 5005).

## What it's for

Per [music-system.md](../references/lore/music-system.md), each music
context in the slice is composed as **4-6 stems** that the game mixes
at runtime with variation knobs (tempo jitter, stem mute, key shift,
state-driven layers). This server generates those stems from text
prompts.

Same model handles SFX — Stable Audio Open is multi-modal.

## Quick start

```powershell
cd D:\Aaron\development\star-control-precursors\audio-server
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

First request triggers model download (~3.5 GB for Stable Audio Open).

Health check:
```
curl http://localhost:5006/health
```

## Endpoints

All POSTs take JSON, return JSON with `audio_b64` (base64 WAV),
`sample_rate`, `duration_s`, `took_s`.

### `POST /music`

Default duration 30 s. For multi-stem coherence, include key + bpm
in every stem prompt for the same track:

```json
{
  "prompt": "Hyperspace travel theme bass stem, deep synth bass, mid-tempo propulsive, in C minor at 110 bpm",
  "duration_s": 30,
  "seed": 42,
  "steps": 100,
  "guidance": 7.0
}
```

### `POST /sfx`

Default duration 3 s. Same call shape, shorter.

```json
{
  "prompt": "short metallic shield-hit, brief sustain, sci-fi UI sound",
  "duration_s": 2.5
}
```

### `POST /generate`

Generic endpoint with default duration 10 s. Equivalent to /music with
a shorter default — handy for one-off jingles, stingers.

## Configuration

| Env var | Default | Effect |
|---|---|---|
| `SCZ_AUDIO_MODEL` | `stable-audio-open` | Currently the only supported model |
| `SCZ_AUDIO_PORT` | `5006` | Server port |
| `SCZ_AUDIO_CPU_OFFLOAD` | unset | `1` enables model CPU offload (slower, lower VRAM) |

## Typical scripted workflow

```python
import base64, io
import requests, soundfile as sf

AS = "http://localhost:5006"

def music(prompt, duration=30, seed=None):
    body = {"prompt": prompt, "duration_s": duration}
    if seed is not None: body["seed"] = seed
    r = requests.post(f"{AS}/music", json=body, timeout=180)
    r.raise_for_status()
    data = r.json()
    audio_bytes = base64.b64decode(data["audio_b64"])
    return sf.read(io.BytesIO(audio_bytes))  # (audio, sample_rate)

# Five-stem Hyperspace theme — same seed family, same key/bpm
key_bpm = "in C minor at 110 bpm"
stems = {
    "bass":       f"Hyperspace bass stem, deep synth bass, propulsive, {key_bpm}",
    "lead":       f"Hyperspace lead stem, mid-tempo synth arpeggio, {key_bpm}",
    "pad":        f"Hyperspace pad stem, ambient analog warmth, {key_bpm}",
    "perc":       f"Hyperspace percussion stem, gated rhythm, four-on-floor, {key_bpm}",
    "ambient":    f"Hyperspace ambient stem, subtle space drone wash, {key_bpm}",
}
for name, prompt in stems.items():
    audio, sr = music(prompt, duration=30, seed=42)
    sf.write(f"assets/music/hyperspace_{name}.wav", audio, sr)
```

The bundled `tools/audio_client.py` (project-relative) wraps this.

## Storage and naming

Generated audio lands in:
```
assets/music/<context>_<stem>.wav      e.g. hyperspace_bass.wav
assets/sfx/<category>_<name>.wav       e.g. ui_select.wav
```

Stems are written as 44.1 kHz float-WAV (lossless). The build-tool
compresses to OGG Vorbis later for the shipped game. Per the music
plan: ~50 MB total for slice scope after OGG compression.
