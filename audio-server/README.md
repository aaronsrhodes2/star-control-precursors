# scz-audio — Local audio LLM server (RUNTIME variance engine, future)

Local Flask + diffusers backend on port **5006**. Sibling of `sd-server/`
(images, port 5005).

## Where this fits in 2026-05-17 onward

There are **two** audio generation paths and they have different jobs:

| Path | When | What | Where |
|---|---|---|---|
| **ElevenLabs Music API** | Asset-time (build-time) | High-quality stems committed into git | `tools/eleven_music.py` |
| **This server (AudioLDM2-Music)** | Eventual: runtime variance | On-the-fly variations during a play session | `tools/audio_client.py` |

The shipped game's music contexts live as static `assets/music/<context>/*.wav`
files generated up-front by ElevenLabs. This local server doesn't need to
be running for normal asset work, and it isn't required at game runtime
either.

It exists because of the [variation principle](../references/lore/variation-architecture.md):
when we add the runtime variance engine, we want a local audio model the
game can call cheaply during a session to introduce small per-encounter
variations on top of the static stems — without paying ElevenLabs per call
and without requiring an internet connection. AudioLDM2-Music is the
candidate. Not wired into the engine yet.

## Quick start (if you actually need to run it)

```powershell
cd D:\Aaron\development\star-control-precursors\audio-server
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

First request triggers model download (~6 GB for AudioLDM2-Music; ~3.5 GB
for Stable Audio Open).

Health check:
```
curl http://localhost:5006/health
```

## Endpoints

All POSTs take JSON, return JSON with `audio_b64` (base64 WAV),
`sample_rate`, `duration_s`, `took_s`.

| Endpoint | Default duration | Notes |
|---|---|---|
| `POST /music` | 30 s | Multi-stem coherence: include key+bpm in every stem prompt |
| `POST /sfx` | 3 s | Same call shape, shorter default |
| `POST /generate` | 10 s | Generic — handy for one-off jingles/stingers |
| `GET /health` | — | Reports model, device, sample rate |

Body shape:
```json
{
  "prompt": "Hyperspace bass stem, deep synth, in C minor at 108 bpm",
  "duration_s": 30,
  "seed": 42,
  "steps": 100,
  "guidance": 7.0
}
```

## Configuration

| Env var | Default | Effect |
|---|---|---|
| `SCZ_AUDIO_MODEL` | `audioldm2-music` | `audioldm2`, `audioldm2-large`, `stable-audio-open` (gated) |
| `SCZ_AUDIO_PORT` | `5006` | Server port |
| `SCZ_AUDIO_CPU_OFFLOAD` | unset | `1` enables model CPU offload (slower, lower VRAM) |

## Compatibility matrix (CRITICAL — do not bump blind)

`requirements.txt` pins:

```
diffusers==0.32.2
transformers==4.46.3
```

This is the only working combination as of 2026-05-17:

- **diffusers 0.32.x** still calls `_update_model_kwargs_for_generation`
  on `GPT2Model` inside the AudioLDM2 pipeline.
- **transformers 4.47+** removed that method, breaking the AudioLDM2
  language-model path.
- **diffusers 0.34+** requires `Dinov2WithRegistersConfig` from
  transformers 4.50+, which has the opposite incompat with AudioLDM2.

Bump only after testing both AudioLDM2 + Stable Audio Open end-to-end.

## Stable Audio Open (Pro option — gated)

Higher-fidelity model (47s stereo at 44.1 kHz native). Requires HF
license acceptance:

1. Login at https://huggingface.co/stabilityai/stable-audio-open-1.0
2. Accept the license
3. `huggingface-cli login` and paste your token
4. `SCZ_AUDIO_MODEL=stable-audio-open python app.py`

## Storage and naming

Generated audio lands in:
```
assets/music/<context>/<stem>.wav      e.g. hyperspace/bass.wav
assets/sfx/<category>/<name>.wav       e.g. ui/select.wav
```

Each context dir has a `manifest.json` with key/bpm/duration/seed/per-stem
prompts so re-generation can match the original recipe.
