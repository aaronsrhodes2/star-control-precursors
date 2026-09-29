"""Generate the Furling+Utwig batch via local SD server.

This is a one-shot script for the 2026-05-17 fur-canon update:
- Halia v2 (replaces v1 with bare-fur + harness)
- Vael-Souren v2 (same)
- Utwig elder (new)
- 6 per-faction Furling reference plates
"""

from __future__ import annotations

import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from sd_client import txt2img, chromakey, health


ROOT = Path(__file__).resolve().parent.parent
PROMPT_DIR = ROOT / "tools" / "firefly_prompts"
ASSET_DIR = ROOT / "assets" / "generated_drafts" / "firefly"


# (prompt_file, output_path, chroma_key_after)
QUEUE: list[tuple[str, str, bool]] = [
    # --- Re-rolls of two committed avatars under the new fur canon ---
    (
        "tier1_avatars/avatar_commander_halia.txt",
        "tier1_avatars/avatar_commander_halia.png",
        True,
    ),
    (
        "tier1_avatars/avatar_vael_souren_cleanser.txt",
        "tier1_avatars/avatar_vael_souren_cleanser.png",
        True,
    ),
    # --- New Utwig main-Homesteader avatar ---
    (
        "tier1_avatars/avatar_utwig_elder.txt",
        "tier1_avatars/avatar_utwig_elder.png",
        True,
    ),
    # --- Six per-faction Furling reference plates ---
    (
        "tier1_furling_reference/furling_persuader.txt",
        "tier1_furling_reference/furling_persuader.png",
        True,
    ),
    (
        "tier1_furling_reference/furling_compeller.txt",
        "tier1_furling_reference/furling_compeller.png",
        True,
    ),
    (
        "tier1_furling_reference/furling_defender.txt",
        "tier1_furling_reference/furling_defender.png",
        True,
    ),
    (
        "tier1_furling_reference/furling_hider.txt",
        "tier1_furling_reference/furling_hider.png",
        True,
    ),
    (
        "tier1_furling_reference/furling_denier.txt",
        "tier1_furling_reference/furling_denier.png",
        True,
    ),
    (
        "tier1_furling_reference/furling_talos.txt",
        "tier1_furling_reference/furling_talos.png",
        True,
    ),
]


def strip_prompt(path: Path) -> str:
    lines = path.read_text(encoding="utf-8").splitlines()
    body = [ln for ln in lines if not ln.startswith("#")]
    return " ".join(s.strip() for s in body if s.strip())


def main() -> int:
    try:
        h = health()
        print(f"SD server: {h}")
    except Exception as e:
        print(f"ERROR: SD server unreachable: {e}")
        return 1

    n_ok = 0
    for prompt_file, out_rel, do_chroma in QUEUE:
        name = Path(out_rel).stem
        prompt_path = PROMPT_DIR / prompt_file
        if not prompt_path.exists():
            print(f"  SKIP {name}: prompt missing")
            continue
        out_path = ASSET_DIR / out_rel
        out_path.parent.mkdir(parents=True, exist_ok=True)
        prompt = strip_prompt(prompt_path)
        print(f"\n=== {name} ===")
        print(f"    {prompt[:100]}...")
        try:
            t0 = time.time()
            img = txt2img(prompt=prompt, width=848, height=1264)
            img.save(out_path)
            print(f"    saved ({img.size}) in {time.time()-t0:.1f}s")
            if do_chroma:
                t0 = time.time()
                keyed = chromakey(img, mode="rembg")
                keyed.save(out_path)
                print(f"    chromakey'd in {time.time()-t0:.1f}s")
            n_ok += 1
        except Exception as e:
            print(f"    FAIL: {e}")
    print(f"\n=== done: {n_ok}/{len(QUEUE)} ===")
    return 0 if n_ok == len(QUEUE) else 1


if __name__ == "__main__":
    sys.exit(main())
