"""Generate the 3-shot Distress Beacon cinematic montage via local SD.

The existing cutscene_distress_beacon.png is the AFTER state.
This adds the THREE process shots the user described:
  1. The decursion swap itself
  2. The Others emerging from black space-time tunnels
  3. The Others consuming the population's cognition
"""

from __future__ import annotations

import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from sd_client import txt2img, health


ROOT = Path(__file__).resolve().parent.parent
PROMPT_DIR = ROOT / "tools" / "firefly_prompts" / "tier1_cutscenes"
OUT_DIR = ROOT / "assets" / "generated_drafts" / "firefly" / "tier1_cutscenes"


QUEUE = [
    "cutscene_decursion_swap",
    "cutscene_others_emerging",
    "cutscene_others_consuming",
]


def strip_prompt(path: Path) -> str:
    lines = path.read_text(encoding="utf-8").splitlines()
    body = [ln for ln in lines if not ln.startswith("#")]
    return " ".join(s.strip() for s in body if s.strip())


def main() -> int:
    print(f"SD server: {health()}")
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    n_ok = 0
    for name in QUEUE:
        prompt_path = PROMPT_DIR / f"{name}.txt"
        if not prompt_path.exists():
            print(f"SKIP {name}: no prompt")
            continue
        prompt = strip_prompt(prompt_path)
        out_path = OUT_DIR / f"{name}.png"
        print(f"\n=== {name} ===")
        print(f"    {prompt[:90]}...")
        try:
            t0 = time.time()
            img = txt2img(prompt=prompt, width=1216, height=688)  # 16:9 native-ish for SDXL
            img.save(out_path)
            print(f"    saved ({img.size}) in {time.time()-t0:.1f}s")
            n_ok += 1
        except Exception as e:
            print(f"    FAIL: {e}")
    print(f"\n=== done: {n_ok}/{len(QUEUE)} ===")
    return 0 if n_ok == len(QUEUE) else 1


if __name__ == "__main__":
    sys.exit(main())
