"""Browser stem mixer — the web build's stand-in for StemMixer.

The desktop StemMixer decodes every stem of a track into memory
(pygame.mixer.Sound). That is ~100+ MB of PCM per track and a
multi-second decode on the main thread, neither of which a browser tab
can afford, and the stems would have to be downloaded up front.

On the web build (pygbag / WebAssembly) the browser plays the stems
instead: one streaming <audio> element per stem, each behind a Web Audio
gain node so volume works everywhere (iOS ignores `audio.volume`). The
stems are MP3 files that sit beside the page under the same
`assets/music/<context>/` paths the manifests name; the build converts
them (tools/build_web.py). Python keeps doing what it does on desktop:
decides targets and ramps volumes each frame, then pushes the numbers
to the page.

Same public surface as StemMixer, so MusicDirector doesn't know which
one it is driving.
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional

log = logging.getLogger("scz.audio.web_mixer")


# Installed into the page once. `startGroup` starts a track's stems
# together once every stem has buffered (or after 4 s, so one slow file
# can't hold the music back). Browsers only let audio start after the
# player has pressed or clicked something; `unlock` retries on the next
# key / click / controller button if the first attempt was refused.
_PLAYER_JS = r"""
(function () {
  if (window.sczMusic) return;
  var ctx = null, stems = {};
  function ac() {
    if (!ctx) {
      var C = window.AudioContext || window.webkitAudioContext;
      ctx = new C();
    }
    if (ctx.state === 'suspended') ctx.resume();
    return ctx;
  }
  function tryPlay(s) {
    var p = s.el.play();
    if (p && p.catch) p.catch(function () { s.blocked = true; });
  }
  function unlock() {
    if (ctx && ctx.state === 'suspended') ctx.resume();
    for (var id in stems) {
      var s = stems[id];
      if (s.blocked && s.started) { s.blocked = false; tryPlay(s); }
    }
  }
  ['keydown', 'pointerdown', 'touchend', 'gamepadconnected'].forEach(function (ev) {
    window.addEventListener(ev, unlock, true);
  });
  window.sczMusic = {
    startGroup: function (spec) {
      var a = ac(), group = [], waiting = 0, fired = false;
      function go() {
        if (fired) return;
        fired = true;
        group.forEach(function (s) { if (stems[s.id] === s) { s.started = true; tryPlay(s); } });
      }
      JSON.parse(spec).forEach(function (item) {
        var el = new Audio();
        el.loop = true;
        el.preload = 'auto';
        var gain = a.createGain();
        gain.gain.value = item.volume;
        a.createMediaElementSource(el).connect(gain);
        gain.connect(a.destination);
        var s = { id: item.id, el: el, gain: gain, started: false, blocked: false };
        stems[item.id] = s;
        group.push(s);
        waiting += 1;
        var done = false;
        function ready() { if (!done) { done = true; waiting -= 1; if (waiting <= 0) go(); } }
        el.addEventListener('canplaythrough', ready);
        el.addEventListener('error', ready);
        el.src = item.url;
        el.load();
      });
      setTimeout(go, 4000);
    },
    volume: function (id, v) {
      var s = stems[id];
      if (s) s.gain.gain.value = v;
    },
    status: function () {
      var out = [];
      for (var id in stems) {
        var s = stems[id];
        out.push({ id: id, paused: s.el.paused, time: s.el.currentTime, volume: s.gain.gain.value });
      }
      return JSON.stringify({ context: ctx ? ctx.state : null, stems: out });
    },
    stop: function (id) {
      var s = stems[id];
      if (!s) return;
      delete stems[id];
      try { s.el.pause(); s.el.removeAttribute('src'); s.el.load(); s.gain.disconnect(); } catch (e) {}
    }
  };
})();
"""


@dataclass
class WebStemState:
    """Runtime state of one playing stem (mirrors mixer.StemState)."""
    name: str
    stem_id: str                  # key the page's player knows it by
    target_volume: float = 1.0
    current_volume: float = 0.0
    fade_rate: float = 2.0
    pushed_volume: float = -1.0   # last value sent to the page


@dataclass
class WebTrack:
    """A track is a dict of stem name -> URL (relative to the page)."""
    context: str
    stems: dict[str, str]
    manifest: dict = field(default_factory=dict)


class WebStemMixer:
    """Drives the page's audio player. Drop-in for StemMixer on the web."""

    def __init__(self, channel_count: int = 8, page: Any = None) -> None:
        self._page = page                    # the JS `window`; tests pass a fake
        self._initialized = False
        self._tracks: dict[str, WebTrack] = {}
        self._active: dict[str, WebStemState] = {}
        self._fading_out: list[WebStemState] = []
        self._current_context: Optional[str] = None
        self._master_volume = 1.0
        self._serial = 0

    # ----- Lifecycle -----

    def bootstrap(self, frequency: int = 44100, channels_stereo: int = 2) -> None:
        if self._initialized:
            return
        if self._page is None:
            import platform
            self._page = platform.window
        self._page.eval(_PLAYER_JS)
        self._initialized = True

    def shutdown(self) -> None:
        for st in list(self._active.values()) + self._fading_out:
            self._page.sczMusic.stop(st.stem_id)
        self._active.clear()
        self._fading_out.clear()
        self._current_context = None

    # ----- Track loading -----

    def load_track(self, context: str, track_dir: Path) -> WebTrack:
        """Read the track's manifest. Nothing is downloaded here; the
        browser streams each stem when it starts playing."""
        if context in self._tracks:
            return self._tracks[context]
        manifest: dict = {}
        manifest_path = track_dir / "manifest.json"
        if manifest_path.exists():
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        stems = {
            name: str(info["path"])
            for name, info in (manifest.get("stems") or {}).items()
        }
        track = WebTrack(context=context, stems=stems, manifest=manifest)
        self._tracks[context] = track
        return track

    # ----- Playback -----

    def play_context(
        self,
        context: str,
        track_dir: Path,
        stem_volumes: dict[str, float] | None = None,
        fade_out_prev: bool = True,
    ) -> None:
        if self._current_context == context and self._active:
            if stem_volumes:
                for name, vol in stem_volumes.items():
                    self.set_stem_volume(name, vol)
            return
        if not self._initialized:
            return

        # Crossfade: the previous track's stems ramp down in update()
        # while the new ones ramp up.
        for st in self._active.values():
            st.target_volume = 0.0
            st.fade_rate = 1.5
            self._fading_out.append(st)
        self._active = {}

        track = self.load_track(context, track_dir)
        volumes = stem_volumes or {name: 1.0 for name in track.stems}
        spec = []
        for name, url in track.stems.items():
            self._serial += 1
            st = WebStemState(
                name=name,
                stem_id=f"{context}/{name}/{self._serial}",
                target_volume=volumes.get(name, 1.0) * self._master_volume,
            )
            self._active[name] = st
            st.pushed_volume = 0.0
            spec.append({"id": st.stem_id, "url": url, "volume": 0.0})
        if spec:
            self._page.sczMusic.startGroup(json.dumps(spec))
        self._current_context = context

    def set_stem_volume(self, name: str, target: float) -> None:
        st = self._active.get(name)
        if st is not None:
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
        if not self._initialized:
            return
        for st in self._active.values():
            self._ramp(st, dt)
        if self._fading_out:
            still_fading: list[WebStemState] = []
            for st in self._fading_out:
                self._ramp(st, dt)
                if st.current_volume <= 0.001:
                    self._page.sczMusic.stop(st.stem_id)
                else:
                    still_fading.append(st)
            self._fading_out = still_fading

    def _ramp(self, st: WebStemState, dt: float) -> None:
        if abs(st.current_volume - st.target_volume) < 1e-3:
            st.current_volume = st.target_volume
        else:
            step = st.fade_rate * dt
            if st.current_volume < st.target_volume:
                st.current_volume = min(st.target_volume, st.current_volume + step)
            else:
                st.current_volume = max(st.target_volume, st.current_volume - step)
        # Crossing into the page costs far more than the ramp itself, so
        # only send a volume the ear could tell apart from the last one.
        if abs(st.current_volume - st.pushed_volume) >= 0.01 or (
            st.current_volume == st.target_volume
            and st.pushed_volume != st.current_volume
        ):
            self._page.sczMusic.volume(st.stem_id, st.current_volume)
            st.pushed_volume = st.current_volume
