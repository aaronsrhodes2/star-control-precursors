"""SfxBus — one-shot sound-effect playback.

Sibling of StemMixer: StemMixer plays looping music stems on a dedicated
channel pool; SfxBus plays short fire-and-forget sounds (weapon hits,
UI clicks, lander touchdowns) on a separate channel pool managed by
pygame.

Loaded lazily — `play("ui/menu_select")` resolves to
`assets/sfx/ui/menu_select.wav`, loads it on first hit, caches the
`pygame.mixer.Sound` for subsequent plays. Same call works for
ship weapons (`play("ships/furling_scout/primary_fire")`),
lander events (`play("lander/pickup_mineral")`), etc.

Volume control:
- master_volume (0..1) scales every Sound at load time
- per-play override via `play(name, volume=0.5)` for one-shots
- mute() to silence the entire SFX bus

The bus is silent (no errors) if assets/sfx/<name>.wav doesn't exist
yet — gameplay code can call play() freely without checking file
existence; missing audio is reported once via the logger and then
suppressed for that name.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Optional

import pygame


log = logging.getLogger("scz.audio.sfx_bus")


def _sfx_root() -> Path:
    # src/scz/audio/sfx_bus.py -> project root is 4 parents up
    return Path(__file__).resolve().parent.parent.parent.parent / "assets" / "sfx"


class SfxBus:
    """One-shot SFX playback. One instance per game (constructed by Game)."""

    def __init__(self) -> None:
        self._cache: dict[str, pygame.mixer.Sound] = {}
        # Once we've logged a missing-asset warning for a given name we
        # suppress further logs for that name. Avoids log-spam if a
        # frequently-played sound is missing.
        self._missing_warned: set[str] = set()
        self._muted = False
        self._master_volume = 0.7

    def set_master_volume(self, v: float) -> None:
        """Scale ALL future plays + retroactively scale cached sounds."""
        self._master_volume = max(0.0, min(1.0, v))
        for snd in self._cache.values():
            snd.set_volume(self._master_volume)

    def mute(self, muted: bool = True) -> None:
        self._muted = bool(muted)

    def _load(self, name: str) -> Optional[pygame.mixer.Sound]:
        """Find assets/sfx/<name>.ogg (browser build) or .wav and load it once."""
        if name in self._cache:
            return self._cache[name]
        path = _sfx_root() / f"{name}.ogg"
        if not path.exists():
            path = _sfx_root() / f"{name}.wav"
        if not path.exists():
            if name not in self._missing_warned:
                log.warning("SFX not found: %s (looked at %s)", name, path)
                self._missing_warned.add(name)
            return None
        try:
            snd = pygame.mixer.Sound(str(path))
        except pygame.error as e:
            log.warning("SFX load failed for %s: %s", name, e)
            return None
        snd.set_volume(self._master_volume)
        self._cache[name] = snd
        return snd

    def play(self, name: str, *, volume: float | None = None) -> None:
        """Play one shot. `name` is path-under-assets/sfx without extension,
        e.g. "ui/menu_select" or "ships/furling_scout/primary_fire".

        Idempotent against repeated calls: each call triggers a fresh
        playback (pygame.mixer.Sound.play() always returns a new channel
        if one is available).
        """
        if self._muted:
            return
        if not pygame.mixer.get_init():
            return
        snd = self._load(name)
        if snd is None:
            return
        if volume is not None:
            # Per-call volume scales WITH master.
            snd.set_volume(max(0.0, min(1.0, volume)) * self._master_volume)
            snd.play()
            snd.set_volume(self._master_volume)
        else:
            snd.play()

    def stop_all(self) -> None:
        """Stop every currently-playing SFX (doesn't affect music stems
        on the StemMixer pool — they have their own channels)."""
        for snd in self._cache.values():
            snd.stop()

    def play_loop(self, name: str, *, volume: float | None = None):
        """Start an SFX looping indefinitely. Returns the pygame.mixer.Channel
        the sound is playing on (or None if the SFX is missing / muted / no
        free channel). Caller is responsible for stopping it via the returned
        channel's .stop() when the loop should end (e.g. on scene exit)."""
        if self._muted or not pygame.mixer.get_init():
            return None
        snd = self._load(name)
        if snd is None:
            return None
        if volume is not None:
            snd.set_volume(max(0.0, min(1.0, volume)) * self._master_volume)
        ch = snd.play(loops=-1)
        # Restore the master volume on the cached Sound so subsequent
        # one-shot plays start at the right level.
        if volume is not None:
            snd.set_volume(self._master_volume)
        return ch
