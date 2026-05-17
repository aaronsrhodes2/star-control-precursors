"""Gemini Flash Image generator (or flask-sd fallback) for project assets.

Usage:
    .venv/Scripts/python.exe tools/gen_image.py SLUG --prompt "..."
    .venv/Scripts/python.exe tools/gen_image.py SLUG --prompt-file path.txt
    .venv/Scripts/python.exe tools/gen_image.py SLUG --backend gemini|flask-sd

Default backend: gemini (paid tier required). Falls back to flask-sd
(http://localhost:5000) if gemini fails with 429/billing error AND
--backend wasn't pinned. Output: tools/gemini_drafts/<SLUG>.png

This is for *drafts* — Aaron reviews, then we move accepted images
into assets/ with the proper _PLACEHOLDERS.json entry.
"""

from __future__ import annotations

import argparse
import base64
import json
import os
import sys
import time
from pathlib import Path
from typing import Optional

import requests
from dotenv import load_dotenv
from google import genai
from google.genai import errors as genai_errors
from google.genai import types

ROOT = Path(__file__).resolve().parent.parent
DRAFTS_DIR = ROOT / "tools" / "gemini_drafts"
ENV_PATH = ROOT.parent / ".env"


def gemini_image(prompt: str, model: str) -> Optional[bytes]:
    """Generate one image via Gemini. Returns PNG bytes or None."""
    load_dotenv(ENV_PATH)
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError(f"GEMINI_API_KEY not in {ENV_PATH}")
    client = genai.Client(api_key=api_key)
    resp = client.models.generate_content(model=model, contents=prompt)
    for part in resp.candidates[0].content.parts:
        if getattr(part, "inline_data", None):
            return part.inline_data.data
        if getattr(part, "text", None):
            print(f"[gen_image] gemini text part: {part.text[:120]}",
                  file=sys.stderr)
    return None


# The remnant-silly Stable Diffusion Flask service. The Docker container
# is named `remnant-flask-sd` and serves on its INTERNAL port 1592. For
# this to be reachable as `http://localhost:1592`, the container must
# have been published with `-p 1592:1592`. Verify in Docker Desktop:
#   docker ps | grep remnant-flask-sd
# should show "0.0.0.0:1592->1592/tcp" (not just "1592/tcp").
FLASK_SD_BASE_URLS = [
    "http://localhost:1592",   # remnant-silly canonical
    "http://localhost:5000",   # earlier port some clients may still use
]


def flask_sd_image(prompt: str) -> Optional[bytes]:
    """Generate via the local flask-sd service. Returns PNG bytes or None.
    Tries each known base URL and a couple of common endpoint shapes."""
    paths = ["/api/generate", "/generate"]
    payload = {"prompt": prompt}
    for base in FLASK_SD_BASE_URLS:
        # Quick health check so we don't burn a 60s generate-timeout on
        # an unreachable URL.
        try:
            requests.get(f"{base}/api/health", timeout=2)
        except requests.RequestException:
            try:
                requests.get(f"{base}/health", timeout=2)
            except requests.RequestException:
                print(f"[gen_image] flask-sd unreachable at {base}",
                      file=sys.stderr)
                continue
        for path in paths:
            url = f"{base}{path}"
            try:
                r = requests.post(url, json=payload, timeout=180)
                r.raise_for_status()
            except requests.RequestException as e:
                print(f"[gen_image] {url} failed: {e}", file=sys.stderr)
                continue
            ctype = r.headers.get("content-type", "")
            if ctype.startswith("image/"):
                return r.content
            try:
                data = r.json()
            except json.JSONDecodeError:
                print(f"[gen_image] {url} returned non-image, non-json "
                      f"({ctype})", file=sys.stderr)
                continue
            for key in ("image", "image_b64", "base64", "b64"):
                if key in data:
                    return base64.b64decode(data[key])
            print(f"[gen_image] {url} json missing image fields: "
                  f"{list(data)[:5]}", file=sys.stderr)
    return None


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("slug")
    parser.add_argument("--prompt", default="")
    parser.add_argument("--prompt-file", default="")
    parser.add_argument(
        "--backend", choices=["auto", "gemini", "flask-sd"], default="auto",
        help="auto: try gemini first, fall back to flask-sd on failure",
    )
    parser.add_argument(
        "--model", default="gemini-2.5-flash-image",
        help="gemini model (only when backend != flask-sd)",
    )
    args = parser.parse_args()

    if args.prompt and args.prompt_file:
        print("ERROR: pass --prompt OR --prompt-file, not both", file=sys.stderr)
        return 1
    if args.prompt_file:
        prompt = Path(args.prompt_file).read_text(encoding="utf-8").strip()
    else:
        prompt = args.prompt.strip()
    if not prompt:
        print("ERROR: empty prompt", file=sys.stderr)
        return 1

    print(f"[gen_image] slug={args.slug} backend={args.backend} "
          f"prompt_len={len(prompt)}", file=sys.stderr)

    img_bytes: Optional[bytes] = None

    backends = [args.backend] if args.backend != "auto" else ["gemini", "flask-sd"]
    last_err: Optional[str] = None
    for backend in backends:
        print(f"[gen_image] trying {backend}", file=sys.stderr)
        try:
            if backend == "gemini":
                img_bytes = gemini_image(prompt, model=args.model)
            elif backend == "flask-sd":
                img_bytes = flask_sd_image(prompt)
            if img_bytes:
                print(f"[gen_image] {backend} returned {len(img_bytes)} bytes",
                      file=sys.stderr)
                break
        except genai_errors.ClientError as e:
            last_err = f"gemini: {e}"
            print(f"[gen_image] gemini failed: {str(e)[:160]}", file=sys.stderr)
            if args.backend != "auto":
                raise
        except Exception as e:
            last_err = f"{backend}: {e}"
            print(f"[gen_image] {backend} exception: {e}", file=sys.stderr)

    if not img_bytes:
        print(f"[gen_image] FAIL: no backend produced an image"
              + (f"\n  last error: {last_err}" if last_err else ""),
              file=sys.stderr)
        return 1

    DRAFTS_DIR.mkdir(exist_ok=True, parents=True)
    out_path = DRAFTS_DIR / f"{args.slug}.png"
    out_path.write_bytes(img_bytes)
    print(f"[gen_image] wrote {out_path} ({len(img_bytes)} bytes)",
          file=sys.stderr)
    print(out_path)
    return 0


if __name__ == "__main__":
    sys.exit(main())
