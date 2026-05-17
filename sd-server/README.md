# scz-sd — Dedicated Stable Diffusion server for Star Control Zero

A focused Flask + diffusers backend on port **5005** for SCZ image
generation work. Independent from any other SD/flask service in the
Skippy ecosystem.

## What it's for

1. **Refinement passes over Firefly bases** — img2img at low denoise
   produces per-individual character variants while preserving identity.
2. **Body articulation frames** — inpaint masked regions (head, arms,
   eyes) on a base avatar to produce mouth-flap and blink frames the
   future `PortraitAnimator` can cycle through.
3. **Background substitution / chroma-key cleanup** — strip the matte
   navy from Firefly avatars to clean alpha PNGs.
4. **Standalone txt2img** — Firefly substitute when its anti-automation
   refuses synthetic clicks (the failure mode that triggered this).

## Quick start (host-mode, fastest)

```powershell
# From the project root, in a fresh PowerShell (or current shell):
cd D:\Aaron\development\star-control-precursors\sd-server
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

First request triggers model download (~7 GB for SDXL-Turbo,
cached under `~/.cache/huggingface/`). Subsequent runs are fast.

Health check:
```
curl http://localhost:5005/health
```

## Endpoints

All POST endpoints take JSON, return JSON with `image` (base64 PNG) +
`took_s`. Images going IN are base64 PNG/JPEG; images coming OUT are
base64 PNG.

### `POST /txt2img`

```json
{
  "prompt": "A full-body avatar painting of...",
  "width": 1024,
  "height": 1024,
  "steps": 4,
  "guidance": 0.0,
  "seed": 42
}
```

### `POST /img2img`

```json
{
  "prompt": "same character, different pose: arms raised",
  "image": "<base64 PNG>",
  "strength": 0.35,
  "steps": 4
}
```

`strength` is the denoise amount. 0.2-0.4 preserves identity; 0.5-0.7
repurposes composition.

### `POST /inpaint`

```json
{
  "prompt": "same character, eyes closed",
  "image": "<base64 PNG>",
  "mask": "<base64 PNG, white=repaint black=preserve>",
  "strength": 0.9,
  "steps": 4
}
```

### `POST /chromakey`

```json
{
  "image": "<base64 PNG>",
  "mode": "rembg",
  "target_rgb": [10, 14, 26],
  "threshold": 70
}
```

`mode` is `rembg` (cleaner edges via u2net) or `color` (fast distance
keying — same algorithm as tools/chromakey_avatar.py).

## Configuration (env vars)

| Var | Default | Effect |
|---|---|---|
| `SCZ_SD_MODEL` | `sdxl-turbo` | `sdxl-turbo`, `sdxl-base`, `sd15`, or any HF model ID |
| `SCZ_SD_PORT` | `5005` | server port |
| `SCZ_SD_CPU_OFFLOAD` | unset | `1` enables CPU offload (slower but lower VRAM) |

`sdxl-turbo` is the default because the project's RTX 4070 Ti can do
1024×1024 in ~3 s. If VRAM is tight (other models running),
`SCZ_SD_CPU_OFFLOAD=1` keeps it working at ~15 s/image. For maximum
quality, use `sdxl-base` (12 GB VRAM, 5-7 s/image).

## Typical scripted workflow (from the SCZ project)

```python
import base64, io, requests
from PIL import Image

SD = "http://localhost:5005"

def img2img_variant(base_path, prompt, strength=0.3):
    with open(base_path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode()
    r = requests.post(f"{SD}/img2img",
        json={"prompt": prompt, "image": b64, "strength": strength},
        timeout=120)
    out = base64.b64decode(r.json()["image"])
    return Image.open(io.BytesIO(out))

# Make 3 per-individual variants of Commander Halia:
for i in range(3):
    img = img2img_variant(
        "assets/generated_drafts/firefly/tier1_avatars/avatar_commander_halia.png",
        "same Furling officer, weathered scar over left eye, slightly older",
        strength=0.3,
    )
    img.save(f"assets/generated_drafts/sd/halia_variant_{i}.png")
```
