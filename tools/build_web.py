"""Stage + build the browser version of the game with pygbag.

    python tools/build_web.py          # stage + build -> build/web/build/web/
    python tools/build_web.py --serve  # stage + run pygbag's dev server on :8000

pygbag packs everything in the app folder into one bundle the browser
downloads up front, so we stage a slim copy: the scz package, a web
entrypoint, and only the assets the game actually loads. Music is left
out — the WAV stems are ~3.9 GB and need to be converted to OGG and
streamed separately before they can ship.

The staged folder mirrors the repo layout (src/scz + assets/) so the
code's repo-root-relative asset paths resolve unchanged.
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
STAGE = ROOT / "build" / "web"

# Asset folders the runtime loads from. generated_drafts is mostly
# unused drafts; only these tiers are referenced by game code.
ASSET_DIRS = [
    "asteroids", "combat", "comm", "cutscene", "fonts", "lander", "maps",
    "nav", "planets", "sfx", "ships", "stars", "ui",
]
DRAFT_TIERS = [
    "tier1_avatars", "tier1_backdrops", "tier1_cutscenes",
    "tier1_dialog_backgrounds", "tier1_planets", "tier1_portraits",
]

WEB_MAIN = '''\
"""Browser entrypoint (pygbag). Desktop uses `python -m scz`."""
import asyncio
import sys

# pygbag only loads libraries it sees imported here, so name pygame
# explicitly even though scz does the real work.
import pygame  # noqa: F401

sys.path.insert(0, "src")

from scz.engine.game import Game
from scz.scenes.stubs import MainMenuScene


async def main():
    game = Game(
        width=1280,
        height=720,
        title="Star Control Zero: The Precursors",
        target_fps=60,
        fullscreen=False,
    )
    game.set_scene(MainMenuScene())
    await game.run_async()


asyncio.run(main())
'''


def _is_lfs_pointer(path: Path) -> bool:
    try:
        with path.open("rb") as f:
            return f.read(24) == b"version https://git-lfs."
    except OSError:
        return False


def _copy_tree(src: Path, dst: Path) -> tuple[int, int]:
    """Copy src -> dst, skipping LFS pointer stubs. Returns (copied, skipped)."""
    copied = skipped = 0
    for f in src.rglob("*"):
        if not f.is_file() or "__pycache__" in f.parts:
            continue
        if _is_lfs_pointer(f):
            skipped += 1
            continue
        out = dst / f.relative_to(src)
        out.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(f, out)
        copied += 1
    return copied, skipped


def _wav_to_ogg(assets: Path) -> None:
    """Browsers (and pygbag) want OGG. Convert staged WAVs in place;
    the SFX bus prefers .ogg when both exist."""
    wavs = list(assets.rglob("*.wav"))
    for wav in wavs:
        subprocess.run(
            ["ffmpeg", "-loglevel", "error", "-y", "-i", str(wav),
             "-c:a", "libvorbis", "-q:a", "4", str(wav.with_suffix(".ogg"))],
            check=True,
        )
        wav.unlink()
    print(f"[web] converted {len(wavs)} WAV -> OGG")


def stage() -> None:
    if STAGE.exists():
        shutil.rmtree(STAGE)
    STAGE.mkdir(parents=True)
    (STAGE / "main.py").write_text(WEB_MAIN, encoding="utf-8")
    _copy_tree(ROOT / "src" / "scz", STAGE / "src" / "scz")

    total_skipped = 0
    for name in ASSET_DIRS:
        src = ROOT / "assets" / name
        if src.exists():
            total_skipped += _copy_tree(src, STAGE / "assets" / name)[1]
    for tier in DRAFT_TIERS:
        src = ROOT / "assets" / "generated_drafts" / "firefly" / tier
        if src.exists():
            total_skipped += _copy_tree(
                src, STAGE / "assets" / "generated_drafts" / "firefly" / tier,
            )[1]
    for f in (ROOT / "assets").glob("*.json"):
        shutil.copy2(f, STAGE / "assets" / f.name)
    _wav_to_ogg(STAGE / "assets")

    size_mb = sum(f.stat().st_size for f in STAGE.rglob("*") if f.is_file()) / 1e6
    print(f"[web] staged {STAGE} ({size_mb:.0f} MB)")
    if total_skipped:
        print(f"[web] skipped {total_skipped} LFS pointer files "
              f"(run `git lfs pull` to include them)")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--serve", action="store_true",
                        help="Run pygbag's local server instead of a static build")
    args = parser.parse_args()
    stage()
    cmd = [sys.executable, "-m", "pygbag", "--title", "Star Control Zero"]
    if not args.serve:
        cmd.append("--build")
    cmd.append(str(STAGE))
    return subprocess.call(cmd, cwd=ROOT)


if __name__ == "__main__":
    sys.exit(main())
