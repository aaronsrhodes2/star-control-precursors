"""Trigger first SDXL-Turbo call. Downloads weights (~7 GB) on cold start
then generates a tiny test image to validate the pipeline."""
import base64, io, sys, time

import requests
from PIL import Image

print("Sending test txt2img...", flush=True)
t0 = time.time()
r = requests.post(
    "http://localhost:5005/txt2img",
    json={
        "prompt": "a small glowing crystalline cube on a black background, painterly",
        "width": 512,
        "height": 512,
        "steps": 1,
    },
    timeout=600,
)
dt = time.time() - t0
print(f"HTTP {r.status_code} in {dt:.1f}s", flush=True)
if r.status_code != 200:
    print(r.text[:500])
    sys.exit(1)
data = r.json()
img = Image.open(io.BytesIO(base64.b64decode(data["image"])))
out = "sd_test_first.png"
img.save(out)
print(f"saved {out} ({img.size}, took {data.get('took_s')}s on the server)", flush=True)
