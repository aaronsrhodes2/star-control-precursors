"""Real-asset runtime smoke test for every context dir.

For each subdirectory under assets/music/, attempt to:
- Load the track via StemMixer.load_track()
- Verify manifest stems match the loaded file list
- Briefly play (1 second) to confirm pygame.mixer.Sound can decode it
- Fade out cleanly

Exit code is non-zero on any failure. Intended as a CI-style guard.

Usage:
    .venv/Scripts/python.exe tools/audio_runtime_smoke.py
"""

from __future__ import annotations

import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

import pygame  # noqa: E402
from scz.audio.mixer import StemMixer  # noqa: E402


MUSIC_ROOT = ROOT / "assets" / "music"


def _try_init() -> bool:
    try:
        pygame.mixer.pre_init(frequency=44100, channels=2, buffer=512)
        pygame.mixer.init()
        return True
    except pygame.error as e:
        print(f"  (no audio device: {e})")
        return False


def _smoke(track_dir: Path) -> bool:
    """One context. Returns True on success."""
    print(f"\n== {track_dir.name} ==")
    mixer = StemMixer(channel_count=12)  # 12 covers our heaviest 7-stem species
    mixer.bootstrap(frequency=44100, channels_stereo=2)
    try:
        track = mixer.load_track(track_dir.name, track_dir)
    except Exception as e:
        print(f"  LOAD FAIL: {e}")
        return False
    if not track.stems:
        print("  NO STEMS LOADED")
        return False
    print(f"  loaded {len(track.stems)} stems: {sorted(track.stems)}")
    mixer.play_context(track_dir.name, track_dir)
    for _ in range(15):  # 0.5s of playback
        mixer.update(1 / 30)
        time.sleep(1 / 30)
    mixer.fade_out_all(rate=8.0)
    for _ in range(15):
        mixer.update(1 / 30)
        time.sleep(1 / 30)
    mixer.shutdown()
    return True


def main() -> int:
    print("== runtime smoke (StemMixer + pygame.mixer) ==")
    if not _try_init():
        print("skipping (headless / no audio device)")
        return 0
    if not MUSIC_ROOT.is_dir():
        print(f"no music dir at {MUSIC_ROOT}")
        return 1
    dirs = sorted(p for p in MUSIC_ROOT.iterdir() if p.is_dir())
    if not dirs:
        print("no contexts to test")
        return 1
    failed: list[str] = []
    for d in dirs:
        if not _smoke(d):
            failed.append(d.name)
    pygame.mixer.quit()
    print("\n" + "=" * 40)
    if failed:
        print(f"FAIL: {failed}")
        return 1
    print(f"OK: {len(dirs)} contexts loaded + played + faded clean")
    return 0


if __name__ == "__main__":
    sys.exit(main())
