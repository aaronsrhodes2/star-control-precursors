"""Stem-mixer: wraps pygame.mixer.Channel for multi-stem track playback.

Each stem is a separate WAV/OGG file loaded into a pygame.mixer.Sound,
played on its own channel, with independent volume control. The
director.py module decides which stems exist and what volumes each
should be at; this module just executes the playback.

Architecture:
- One StemMixer instance per game; created in engine bootstrap.
- StemMixer owns a fixed pool of pygame.mixer.Channel objects (default
  8) and rents them to active stems.
- Tracks are loaded lazily on first play_track() call; cached after.
- Volume changes are smoothed (linear ramp) over a configurable
  duration so transitions don't pop.
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

import pygame


log = logging.getLogger("scz.audio.mixer")


# Default channel pool size. 8 is pygame.mixer's default; we can lift
# this with pygame.mixer.set_num_channels(N) before init if needed.
DEFAULT_CHANNELS = 8


@dataclass
class StemState:
    """Runtime state of one playing stem."""
    name: str                     # e.g. "bass", "lead"
    sound: pygame.mixer.Sound
    channel: pygame.mixer.Channel
    target_volume: float = 1.0    # what we're ramping toward (0.0–1.0)
    current_volume: float = 1.0   # what's actually applied right now
    # Per-stem fade rate (linear, units/sec). 1.0 = full fade in 1 second.
    fade_rate: float = 2.0


@dataclass
class Track:
    """A loaded track is a dict of named stems sharing tempo/key."""
    context: str                  # e.g. "hyperspace"
    stems: dict[str, pygame.mixer.Sound]
    # Optional manifest (key, bpm, duration, etc.) from the build-time
    # JSON manifest that lives alongside the audio files.
    manifest: dict = field(default_factory=dict)


class StemMixer:
    """Owns pygame.mixer init + a pool of channels + a cache of loaded tracks."""

    def __init__(self, channel_count: int = DEFAULT_CHANNELS) -> None:
        # Mixer initialization is deferred to bootstrap() so the caller
        # can choose when pygame is ready. Some games init pygame after
        # creating subsystem objects; we honor that.
        self._channel_count = channel_count
        self._initialized = False
        self._tracks: dict[str, Track] = {}
        self._active: dict[str, StemState] = {}  # stem name -> state
        self._current_context: Optional[str] = None
        self._master_volume = 1.0

    # ----- Lifecycle -----

    def bootstrap(self, frequency: int = 44100, channels_stereo: int = 2) -> None:
        """Initialize pygame.mixer if it isn't yet. Idempotent."""
        if self._initialized:
            return
        if not pygame.mixer.get_init():
            pygame.mixer.pre_init(
                frequency=frequency, size=-16,
                channels=channels_stereo, buffer=512,
            )
            pygame.mixer.init()
        pygame.mixer.set_num_channels(self._channel_count)
        self._initialized = True
        log.info(
            "StemMixer ready: %d channels, %d Hz stereo",
            self._channel_count, frequency,
        )

    def shutdown(self) -> None:
        """Stop everything and release channels."""
        for state in list(self._active.values()):
            state.channel.stop()
        self._active.clear()
        self._current_context = None

    # ----- Track loading -----

    def load_track(self, context: str, track_dir: Path) -> Track:
        """Load all .wav/.ogg stems under track_dir into memory.

        Expects a manifest.json with at least:
            {"context": "...", "stems": {"bass": {"path": "..."}, ...}}

        Falls back to globbing *.wav if no manifest is present.
        """
        if context in self._tracks:
            return self._tracks[context]

        manifest_path = track_dir / "manifest.json"
        manifest: dict = {}
        if manifest_path.exists():
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))

        stems: dict[str, pygame.mixer.Sound] = {}
        if manifest.get("stems"):
            # Use manifest paths (resolved relative to project root)
            project_root = track_dir.parent.parent.parent  # assets/music/<ctx> → project root
            for name, info in manifest["stems"].items():
                p = project_root / info["path"]
                if not p.exists():
                    log.warning("missing stem %s for %s at %s", name, context, p)
                    continue
                stems[name] = pygame.mixer.Sound(str(p))
        else:
            # Glob fallback (.mp3 / .ogg / .wav — all natively supported
            # by pygame.mixer.Sound).
            found = (
                sorted(track_dir.glob("*.mp3"))
                + sorted(track_dir.glob("*.ogg"))
                + sorted(track_dir.glob("*.wav"))
            )
            # If a stem name appears in multiple formats, prefer the
            # smaller one (mp3 > ogg > wav per the order above) since
            # ElevenLabs ships mp3 by default.
            seen: set[str] = set()
            for p in found:
                if p.stem in seen:
                    continue
                seen.add(p.stem)
                stems[p.stem] = pygame.mixer.Sound(str(p))

        track = Track(context=context, stems=stems, manifest=manifest)
        self._tracks[context] = track
        log.info("loaded track %s with %d stem(s): %s",
                 context, len(stems), ", ".join(stems.keys()))
        return track

    # ----- Playback -----

    def play_context(
        self,
        context: str,
        track_dir: Path,
        stem_volumes: dict[str, float] | None = None,
        fade_out_prev: bool = True,
    ) -> None:
        """Start playing the track for `context`. Optionally override
        per-stem volumes (defaults to 1.0 for each loaded stem)."""
        if self._current_context == context and self._active:
            # Already playing; just rebalance volumes
            if stem_volumes:
                for name, vol in stem_volumes.items():
                    self.set_stem_volume(name, vol)
            return

        if fade_out_prev and self._active:
            self.fade_out_all(rate=2.0)
            # Note: the caller's update() loop will finish the fade-out
            # naturally; we proceed with fade-in immediately, which gives
            # a brief crossfade.

        track = self.load_track(context, track_dir)
        volumes = stem_volumes or {name: 1.0 for name in track.stems}
        free_channels = self._free_channels()
        new_active: dict[str, StemState] = {}
        for name, sound in track.stems.items():
            if not free_channels:
                log.warning("no free channels for stem %s", name)
                break
            ch = free_channels.pop(0)
            # Loop the stem indefinitely
            ch.play(sound, loops=-1, fade_ms=400)
            ch.set_volume(0.0)
            new_active[name] = StemState(
                name=name, sound=sound, channel=ch,
                target_volume=volumes.get(name, 1.0) * self._master_volume,
                current_volume=0.0,
            )
        self._active = new_active
        self._current_context = context

    def _free_channels(self) -> list[pygame.mixer.Channel]:
        """Find channels not currently used by an active stem."""
        used = {st.channel for st in self._active.values()}
        return [
            pygame.mixer.Channel(i)
            for i in range(self._channel_count)
            if pygame.mixer.Channel(i) not in used
        ]

    def set_stem_volume(self, name: str, target: float) -> None:
        """Smoothly fade a stem to `target` (0.0–1.0)."""
        if name not in self._active:
            return
        st = self._active[name]
        st.target_volume = max(0.0, min(1.0, target)) * self._master_volume

    def fade_out_all(self, rate: float = 2.0) -> None:
        for st in self._active.values():
            st.target_volume = 0.0
            st.fade_rate = rate

    def set_master_volume(self, v: float) -> None:
        self._master_volume = max(0.0, min(1.0, v))
        for st in self._active.values():
            st.target_volume = min(st.target_volume, self._master_volume)

    # ----- Per-frame update -----

    def update(self, dt: float) -> None:
        """Per-frame: advance volume ramps toward targets."""
        if not self._initialized or not self._active:
            return
        stopped: list[str] = []
        for name, st in self._active.items():
            if abs(st.current_volume - st.target_volume) < 1e-3:
                st.current_volume = st.target_volume
            else:
                step = st.fade_rate * dt
                if st.current_volume < st.target_volume:
                    st.current_volume = min(st.target_volume, st.current_volume + step)
                else:
                    st.current_volume = max(st.target_volume, st.current_volume - step)
                st.channel.set_volume(st.current_volume)
            # If a stem has fully faded out, free the channel
            if st.current_volume <= 0.001 and st.target_volume == 0.0:
                st.channel.stop()
                stopped.append(name)
        for name in stopped:
            del self._active[name]
