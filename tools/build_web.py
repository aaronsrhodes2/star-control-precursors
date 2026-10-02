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
# Tiers the code scans as whole folders (combat picks a random planet
# from tier1_planets); every other draft ships only if its filename
# appears literally in the source.
DRAFT_TIERS_WHOLE = {"tier1_planets"}

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


# The web build runs at 1280x720, so no art needs to be taller than the
# window. Downscaling the 1024px Firefly drafts roughly halves them.
WEB_MAX_DIM = 720


def _shrink_art(folder: Path) -> None:
    from PIL import Image
    before = after = 0
    for f in folder.rglob("*.png"):
        before += f.stat().st_size
        with Image.open(f) as im:
            im.load()
            if max(im.size) > WEB_MAX_DIM:
                im.thumbnail((WEB_MAX_DIM, WEB_MAX_DIM), Image.LANCZOS)
            im.save(f, optimize=True)
        after += f.stat().st_size
    print(f"[web] draft art {before / 1e6:.0f} MB -> {after / 1e6:.0f} MB")


def _copy_drafts() -> int:
    """Copy only the draft art the game references. Returns LFS-skip count."""
    source = "".join(
        f.read_text(encoding="utf-8")
        for f in (ROOT / "src" / "scz").rglob("*.py")
    )
    skipped = 0
    for tier in DRAFT_TIERS:
        src = ROOT / "assets" / "generated_drafts" / "firefly" / tier
        dst = STAGE / "assets" / "generated_drafts" / "firefly" / tier
        if not src.exists():
            continue
        for f in src.glob("*.png"):
            if tier in DRAFT_TIERS_WHOLE:
                if "_v1" in f.name or "_misread" in f.name:
                    continue
            elif f.name not in source:
                continue
            if _is_lfs_pointer(f):
                skipped += 1
                continue
            dst.mkdir(parents=True, exist_ok=True)
            shutil.copy2(f, dst / f.name)
    return skipped


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
    total_skipped += _copy_drafts()
    _wav_to_ogg(STAGE / "assets")
    _shrink_art(STAGE / "assets" / "generated_drafts")

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
