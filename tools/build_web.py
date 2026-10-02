"""Build the browser version of the game with pygbag.

    python tools/build_web.py            # full build  -> build/web-dist/
    python tools/build_web.py --no-music # skip the music (fast; silent game)
    python tools/build_web.py --serve    # build, then serve it on :8000
    python tools/build_web.py --tarball  # also write build/scz-web.tar.gz (the release asset)

What comes out (build/web-dist/, plain static files, host anywhere):

    index.html            the door: loads the game on a computer, waits for a
                          controller on a phone / tablet (tools/web/index.html)
    game.html             pygbag's page, patched to fetch the bundle in parts
    web.tar.gz.partNN     the game bundle (code + art + sound effects), split
                          into parts under 32 MB each
    assets/music/<ctx>/   one MP3 per stem, streamed by the page on demand
    version.json          build id + sizes

Why it is shaped this way:

- pygbag packs everything in the app folder into one bundle the browser
  downloads before anything shows, so we stage a slim copy: the scz
  package, a web entrypoint, and only the assets the game loads.
- The bundle is split because some hosts cap a single response (Cloud Run:
  32 MiB over HTTP/1). game.html's loader joins the parts again.
- Music stays out of the bundle. The stems are ~3.9 GB of WAV; as MP3 they
  are ~450 MB, and the browser streams just the current track's stems
  (see src/scz/audio/web_mixer.py). MP3 because every browser, Safari
  included, plays it; sound effects are OGG because SDL plays those.
- The staged folder mirrors the repo layout (src/scz + assets/) so the
  code's repo-root-relative asset paths resolve unchanged.

Needs ffmpeg on PATH, Pillow, pygbag, and the LFS assets checked out
(`git lfs pull`); LFS pointer stubs are skipped with a warning.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
import sys
import tarfile
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
STAGE = ROOT / "build" / "web"              # what pygbag packs
PYGBAG_OUT = STAGE / "build" / "web"        # where pygbag writes
DIST = ROOT / "build" / "web-dist"          # what gets hosted
MUSIC_CACHE = ROOT / "build" / "music-cache"
TARBALL = ROOT / "build" / "scz-web.tar.gz"

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

# Parts of the bundle stay well under Cloud Run's 32 MiB response cap.
PART_BYTES = 24 * 1024 * 1024

WEB_MAIN = '''\
"""Browser entrypoint (pygbag). Desktop uses `python -m scz`."""
import asyncio
import sys

# pygbag only loads libraries it sees imported here, so name pygame
# explicitly even though scz does the real work.
import pygame  # noqa: F401

sys.path.insert(0, "src")

# The game asks for Consolas everywhere and browsers have no system
# fonts, so every request gets the bundled DejaVu Sans Mono instead.
# It is ~9% wider than Consolas; the size is scaled so text takes the
# same width and the layouts hold.
_FONT_DIR = "assets/fonts/web/"


def _web_font(name, size, bold=False, italic=False, **_kw):
    face = "DejaVuSansMono-Bold.ttf" if bold else "DejaVuSansMono.ttf"
    return pygame.font.Font(_FONT_DIR + face, max(8, round(size * 0.91)))


pygame.font.SysFont = _web_font


def _show_crash(text):
    """A crash must not leave a silent blank page: put the traceback in
    the browser console and on the page."""
    import platform
    try:
        platform.window.console.error(text)
        box = platform.window.infobox
        box.style.display = "block"
        box.style.whiteSpace = "pre-wrap"
        box.style.textAlign = "left"
        box.innerText = "Star Control Zero stopped:\\n\\n" + text
    except Exception:
        print(text)


def _requested_tests():
    """`?test=walk_trade` (or a comma list, or `all`) runs the scripted
    test walks inside the browser build, same as `python -m scz --test`."""
    import platform
    from urllib.parse import parse_qs
    query = parse_qs(str(platform.window.location.search).lstrip("?"))
    names = [n for n in ",".join(query.get("test", [])).split(",") if n]
    if names == ["all"]:
        from scz.testing.scripts import SCRIPTS
        names = sorted(SCRIPTS)
    return names


async def _run_tests(names):
    """One fresh Game per walk; results land in window.sczTestResults
    (a JSON string) as each walk finishes."""
    import gc
    import json
    import platform
    from scz.engine.game import Game
    from scz.scenes.stubs import MainMenuScene
    from scz.testing.harness import TestHarness
    from scz.testing.scripts import SCRIPTS

    results = []
    for name in names:
        entry = {"test": name, "passed": 0, "failed": [], "crash": None}
        try:
            game = Game(width=1280, height=720, target_fps=60, fullscreen=False)
            game.turbo = True
            harness = TestHarness(game, SCRIPTS[name]())
            game.test_harness = harness
            game.set_scene(MainMenuScene())
            await game.run_async()
            entry["passed"] = len(harness.successes)
            entry["failed"] = list(harness.failures)
        except Exception:
            import traceback
            entry["crash"] = traceback.format_exc()
        # Drop the finished Game before the next walk builds its own:
        # each one holds a full set of loaded art.
        game = harness = None
        gc.collect()
        results.append(entry)
        platform.window.sczTestResults = json.dumps(
            {"done": len(results) == len(names), "results": results})


async def main():
    try:
        tests = _requested_tests()
        if tests:
            await _run_tests(tests)
            return
        from scz.engine.game import Game
        from scz.scenes.stubs import MainMenuScene

        game = Game(
            width=1280,
            height=720,
            title="Star Control Zero: The Precursors",
            target_fps=60,
            fullscreen=False,
        )
        game.set_scene(MainMenuScene())
        await game.run_async()
    except Exception:
        import traceback
        _show_crash(traceback.format_exc())
        raise


asyncio.run(main())
'''

# pygbag's page fetches the whole bundle in one request. This replaces
# that with a loop over the parts. Indentation matters: it sits inside
# the page's embedded Python loader.
_LOADER_OLD = '''        async with platform.fopen("web.tar.gz", "rb") as archive:
            tar = tarfile.open(fileobj=archive, mode="r:gz")
            tar.extractall(path=appdir.as_posix(), filter='tar')
            tar.close()
'''
_LOADER_NEW = '''        import os
        joined = "/tmp/scz-web.tar.gz"
        with open(joined, "wb") as out:
            for part in range({parts}):
                platform.window.infobox.innerText = f"Downloading Star Control Zero ({{part + 1}} of {parts})"
                async with platform.fopen(f"web.tar.gz.part{{part:02d}}?v={build}", "rb") as chunk:
                    out.write(chunk.read())
        platform.window.infobox.innerText = "Unpacking"
        await asyncio.sleep(0)
        with open(joined, "rb") as archive:
            tar = tarfile.open(fileobj=archive, mode="r:gz")
            tar.extractall(path=appdir.as_posix(), filter='tar')
            tar.close()
        os.unlink(joined)
'''


_TEST_TICKER = (
    "<script>if (/[?&]test=/.test(location.search)) "
    "window.requestAnimationFrame = function (cb) "
    "{ return setTimeout(function () { cb(performance.now()); }, 4); };</script>"
)


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


def _ffmpeg(src: Path, dst: Path, *codec: str) -> None:
    dst.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        ["ffmpeg", "-loglevel", "error", "-y", "-i", str(src), *codec, str(dst)],
        check=True,
    )


def _wav_to_ogg(assets: Path) -> None:
    """Sound effects: pygbag refuses WAV and SDL plays OGG. Convert the
    staged WAVs in place; the SFX bus prefers .ogg when both exist."""
    wavs = list(assets.rglob("*.wav"))
    for wav in wavs:
        _ffmpeg(wav, wav.with_suffix(".ogg"), "-c:a", "libvorbis", "-q:a", "4")
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


# ----- Music -----------------------------------------------------------

def _music_plan() -> dict[str, dict[str, Path]]:
    """{context: {stem name: source audio file}} for every real track.

    Follows the same rules as StemMixer.load_track: the manifest's stem
    list when there is one, else every audio file in the folder
    (mp3 preferred over ogg over wav for a stem that exists twice)."""
    plan: dict[str, dict[str, Path]] = {}
    for ctx_dir in sorted((ROOT / "assets" / "music").iterdir()):
        if not ctx_dir.is_dir() or ctx_dir.name.startswith("_"):
            continue
        stems: dict[str, Path] = {}
        manifest_path = ctx_dir / "manifest.json"
        manifest = {}
        if manifest_path.exists():
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        if manifest.get("stems"):
            for name, info in manifest["stems"].items():
                stems[name] = ROOT / info["path"]
        else:
            for ext in ("mp3", "ogg", "wav"):
                for f in sorted(ctx_dir.glob(f"*.{ext}")):
                    stems.setdefault(f.stem, f)
        stems = {n: p for n, p in stems.items() if p.exists() and not _is_lfs_pointer(p)}
        if stems:
            plan[ctx_dir.name] = stems
    return plan


def _encode_stem(src: Path, dst: Path) -> None:
    """One stem -> MP3 in the cache, skipped when the cache is current."""
    if dst.exists() and dst.stat().st_mtime >= src.stat().st_mtime:
        return
    if src.suffix == ".mp3":
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
    else:
        # VBR ~115 kbps: transparent for the 32 kHz MusicGen stems.
        _ffmpeg(src, dst, "-c:a", "libmp3lame", "-q:a", "6")


def build_music() -> dict[str, dict[str, str]]:
    """Encode every stem to MP3 (cached) and return the web manifests:
    {context: {stem: page-relative url}}."""
    plan = _music_plan()
    jobs = []
    web: dict[str, dict[str, str]] = {}
    for ctx, stems in plan.items():
        web[ctx] = {}
        for name, src in stems.items():
            rel = f"assets/music/{ctx}/{name}.mp3"
            web[ctx][name] = rel
            jobs.append((src, MUSIC_CACHE / ctx / f"{name}.mp3"))
    t0 = time.time()
    with ThreadPoolExecutor(max_workers=8) as pool:
        list(pool.map(lambda j: _encode_stem(*j), jobs))
    total = sum(dst.stat().st_size for _, dst in jobs)
    print(f"[web] music: {len(plan)} tracks, {len(jobs)} stems, "
          f"{total / 1e6:.0f} MB MP3 ({time.time() - t0:.0f}s)")
    return web


def _stage_music_manifests(web: dict[str, dict[str, str]]) -> None:
    """The bundle carries one small manifest per track (no audio): the
    web mixer reads it to learn the stems and their URLs."""
    for ctx, stems in web.items():
        d = STAGE / "assets" / "music" / ctx
        d.mkdir(parents=True, exist_ok=True)
        (d / "manifest.json").write_text(json.dumps({
            "context": ctx,
            "stems": {name: {"path": url} for name, url in stems.items()},
        }), encoding="utf-8")


# ----- Stage / build / dist --------------------------------------------

def stage(music: dict[str, dict[str, str]]) -> None:
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
    _stage_music_manifests(music)

    size_mb = sum(f.stat().st_size for f in STAGE.rglob("*") if f.is_file()) / 1e6
    print(f"[web] staged {STAGE} ({size_mb:.0f} MB)")
    if total_skipped:
        print(f"[web] skipped {total_skipped} LFS pointer files "
              f"(run `git lfs pull` to include them)")


def _git_sha() -> str:
    try:
        return subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"], cwd=ROOT,
            capture_output=True, text=True, check=True,
        ).stdout.strip()
    except Exception:
        return "unknown"


def dist(music: dict[str, dict[str, str]]) -> None:
    """Assemble the hosted folder from pygbag's output."""
    if DIST.exists():
        shutil.rmtree(DIST)
    DIST.mkdir(parents=True)

    bundle = PYGBAG_OUT / "web.tar.gz"
    data = bundle.read_bytes()
    build_id = hashlib.sha256(data).hexdigest()[:12]
    parts = [data[i:i + PART_BYTES] for i in range(0, len(data), PART_BYTES)]
    for n, chunk in enumerate(parts):
        (DIST / f"web.tar.gz.part{n:02d}").write_bytes(chunk)

    page = (PYGBAG_OUT / "index.html").read_text(encoding="utf-8")
    if page.count(_LOADER_OLD) != 1:
        raise SystemExit(
            "[web] pygbag's page changed: the bundle loader this script "
            "patches was not found (see _LOADER_OLD)."
        )
    page = page.replace(
        _LOADER_OLD, _LOADER_NEW.format(parts=len(parts), build=build_id),
    )
    # pygbag paints the page grey; every Skippy surface is black.
    page = page.replace('body.style.background = "#7f7f7f"',
                        'body.style.background = "#000000"')
    page = page.replace("background-color:powderblue", "background-color:#000")
    # Test runs (?test=...) must keep going while the tab is hidden, when
    # browsers stop requestAnimationFrame; a timer stands in for it.
    page = page.replace("<html lang=\"en-us\">", "<html lang=\"en-us\">" + _TEST_TICKER, 1)
    (DIST / "game.html").write_text(page, encoding="utf-8")
    shutil.copy2(ROOT / "tools" / "web" / "index.html", DIST / "index.html")
    shutil.copy2(PYGBAG_OUT / "favicon.png", DIST / "favicon.png")

    music_bytes = 0
    for ctx, stems in music.items():
        for name, url in stems.items():
            out = DIST / url
            out.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(MUSIC_CACHE / ctx / f"{name}.mp3", out)
            music_bytes += out.stat().st_size

    (DIST / "version.json").write_text(json.dumps({
        "build": build_id,
        "commit": _git_sha(),
        "built_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "bundle_bytes": len(data),
        "bundle_parts": len(parts),
        "music_tracks": len(music),
        "music_bytes": music_bytes,
    }, indent=2), encoding="utf-8")
    print(f"[web] dist {DIST}: bundle {len(data) / 1e6:.0f} MB in "
          f"{len(parts)} parts, music {music_bytes / 1e6:.0f} MB, build {build_id}")


def tarball() -> None:
    with tarfile.open(TARBALL, "w:gz", compresslevel=1) as tar:
        tar.add(DIST, arcname="scz-web")
    print(f"[web] wrote {TARBALL} ({TARBALL.stat().st_size / 1e6:.0f} MB)")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--no-music", action="store_true",
                        help="Skip the music (fast build, silent game)")
    parser.add_argument("--serve", action="store_true",
                        help="Serve build/web-dist on http://localhost:8000 after building")
    parser.add_argument("--tarball", action="store_true",
                        help="Also write build/scz-web.tar.gz (the release asset)")
    args = parser.parse_args()

    music = {} if args.no_music else build_music()
    stage(music)
    rc = subprocess.call(
        [sys.executable, "-m", "pygbag", "--title", "Star Control Zero",
         "--build", str(STAGE)],
        cwd=ROOT,
    )
    if rc != 0:
        return rc
    dist(music)
    if args.tarball:
        tarball()
    if args.serve:
        return subprocess.call(
            [sys.executable, "-m", "http.server", "8000", "--directory", str(DIST)],
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
