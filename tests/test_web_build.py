"""Tests for the browser build's own pieces: save mirroring, the stem
player and the controller layouts.

These need no browser and no display. Run them with either

    python -m pytest tests/test_web_build.py
    python tests/test_web_build.py

The gameplay itself is covered by the scripted walks
(`python -m scz --test <walk>`), which also run inside the browser build
(`?test=<walk>` on the game page; see tools/build_web.py).
"""

from __future__ import annotations

import json
import os
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame  # noqa: E402

from scz.audio.web_mixer import WebStemMixer  # noqa: E402
from scz.engine import webstore  # noqa: E402
from scz.engine.input import DESKTOP_PAD, WEB_PAD, InputManager  # noqa: E402


# ----- webstore: saves mirrored into the browser localStorage -----------

class FakeLocalStorage:
    """localStorage with an optional size limit, like a real browser."""

    def __init__(self, cap: int | None = None) -> None:
        self.d: dict[str, str] = {}
        self.cap = cap

    @property
    def length(self) -> int:
        return len(self.d)

    def key(self, i: int) -> str:
        return list(self.d)[i]

    def getItem(self, k: str):
        return self.d.get(k)

    def setItem(self, k: str, v: str) -> None:
        used = sum(len(a) + len(b) for a, b in self.d.items() if a != k)
        if self.cap is not None and used + len(k) + len(v) > self.cap:
            raise RuntimeError("QuotaExceededError")
        self.d[k] = v

    def removeItem(self, k: str) -> None:
        self.d.pop(k, None)


def _fresh_store(cap: int | None = None) -> FakeLocalStorage:
    store = FakeLocalStorage(cap)
    webstore._storage_override = store
    webstore._thumbnails_off = False
    webstore._warned = False
    return store


def test_webstore_is_a_no_op_on_desktop():
    webstore._storage_override = None
    root = Path(tempfile.mkdtemp())
    (root / "meta.json").write_text("{}")
    webstore.sync(root)                      # must not raise
    assert webstore.restore(root) == 0


def test_webstore_mirrors_writes_and_deletions_and_restores_them():
    store = _fresh_store()
    root = Path(tempfile.mkdtemp())
    camp = root / "camp"
    camp.mkdir()
    (camp / "meta.json").write_text('{"n":1}')
    (camp / "save_1.json").write_text('{"s":1}')
    (camp / "save_1.png").write_bytes(b"\x89PNG\x00\xff")
    webstore.sync(root)
    assert len(store.d) == 3

    # A newer save replaces the old one; meta.json is rewritten each save.
    (camp / "save_1.json").unlink()
    (camp / "save_1.png").unlink()
    (camp / "save_2.json").write_text('{"s":2}')
    (camp / "meta.json").write_text('{"n":2}')
    webstore.sync(root)
    assert sorted(store.d) == ["scz-save/camp/meta.json", "scz-save/camp/save_2.json"]

    # A later visit gets the files back; foreign keys and paths that
    # climb out of the folder are ignored.
    store.d["scz-save/../evil.json"] = "t:x"
    store.d["some-other-key"] = "zzz"
    store.d["scz-save/camp/thumb.png"] = "b:iVBORw=="
    fresh = Path(tempfile.mkdtemp())
    assert webstore.restore(fresh) == 3
    assert json.loads((fresh / "camp" / "meta.json").read_text()) == {"n": 2}
    assert (fresh / "camp" / "thumb.png").read_bytes() == b"\x89PNG"
    assert not (fresh.parent / "evil.json").exists()


def test_webstore_gives_up_thumbnails_before_it_gives_up_a_save():
    store = _fresh_store(cap=1300)
    root = Path(tempfile.mkdtemp())
    camp = root / "camp"
    camp.mkdir()
    (camp / "meta.json").write_text('{"n":1}')
    for i in range(3):
        (camp / f"save_{i}.json").write_text('{"s":%d}' % i)
        (camp / f"save_{i}.png").write_bytes(bytes(400))
        webstore.sync(root)
    keys = sorted(store.d)
    assert all(f"scz-save/camp/save_{i}.json" in keys for i in range(3)), keys
    assert not any(k.endswith(".png") for k in keys), keys
    assert webstore._thumbnails_off


# ----- web mixer: the page plays the stems, Python sets the volumes -----

class FakePage:
    """Stands in for the browser `window` and its sczMusic player."""

    def __init__(self) -> None:
        self.calls: list[tuple] = []
        self.sczMusic = self

    def eval(self, code: str) -> None:
        self.calls.append(("eval", len(code)))

    def startGroup(self, spec: str) -> None:
        self.calls.append(("start", json.loads(spec)))

    def volume(self, stem_id: str, v: float) -> None:
        self.calls.append(("vol", stem_id, round(v, 2)))

    def stop(self, stem_id: str) -> None:
        self.calls.append(("stop", stem_id))


def _track_dir(name: str) -> Path:
    d = Path(tempfile.mkdtemp()) / name
    d.mkdir()
    (d / "manifest.json").write_text(json.dumps({"stems": {
        "bass": {"path": f"assets/music/{name}/bass.mp3"},
        "lead": {"path": f"assets/music/{name}/lead.mp3"},
    }}))
    return d


def test_web_mixer_starts_a_track_fades_it_in_and_crossfades_to_the_next():
    page = FakePage()
    mixer = WebStemMixer(page=page)
    mixer.bootstrap()
    assert page.calls[0][0] == "eval"                 # the player was installed

    mixer.play_context("a", _track_dir("a"), stem_volumes={"bass": 1.0, "lead": 0.5})
    kind, spec = page.calls[1]
    assert kind == "start"
    assert [s["url"] for s in spec] == ["assets/music/a/bass.mp3", "assets/music/a/lead.mp3"]
    assert all(s["volume"] == 0.0 for s in spec)      # starts silent, ramps up
    for _ in range(60):
        mixer.update(1 / 60)
    assert ("vol", spec[0]["id"], 1.0) in page.calls
    assert ("vol", spec[1]["id"], 0.5) in page.calls

    mixer.play_context("b", _track_dir("b"))
    for _ in range(120):
        mixer.update(1 / 60)
    stops = [c for c in page.calls if c[0] == "stop"]
    assert len(stops) == 2 and all(c[1].startswith("a/") for c in stops)
    assert set(mixer._active) == {"bass", "lead"} and not mixer._fading_out

    # Settled: no more traffic to the page.
    before = len(page.calls)
    mixer.update(1 / 60)
    assert len(page.calls) == before


def test_web_mixer_replaying_the_same_track_only_rebalances():
    page = FakePage()
    mixer = WebStemMixer(page=page)
    mixer.bootstrap()
    d = _track_dir("a")
    mixer.play_context("a", d)
    mixer.play_context("a", d, stem_volumes={"lead": 0.0})
    assert len([c for c in page.calls if c[0] == "start"]) == 1
    assert mixer._active["lead"].target_volume == 0.0


# ----- controller layouts and keys ---------------------------------------

def _pad_events(layout, *buttons):
    pygame.init()
    inp = InputManager(pad=layout)
    inp.update([pygame.event.Event(pygame.JOYBUTTONDOWN, button=b, joy=0) for b in buttons])
    return inp


def test_the_browser_gamepad_layout_puts_the_dpad_and_triggers_on_buttons():
    inp = _pad_events(WEB_PAD, 12)
    assert inp.menu_up and not inp.menu_down
    inp = _pad_events(WEB_PAD, 13, 15)
    assert inp.menu_down and inp.menu_next
    assert _pad_events(WEB_PAD, 14).menu_prev
    assert _pad_events(WEB_PAD, 7).fire_primary        # right trigger
    assert _pad_events(WEB_PAD, 8).rewind              # Back / View
    assert _pad_events(WEB_PAD, 11).open_switcher      # right stick click
    for layout in (WEB_PAD, DESKTOP_PAD):
        assert _pad_events(layout, 0).confirm
        assert _pad_events(layout, 1).cancel
        both = _pad_events(layout, 5)                  # RB
        assert both.zoom_in and both.menu_next and both.fire_secondary
        assert _pad_events(layout, 4).zoom_out         # LB


def test_start_quits_on_desktop():
    assert _pad_events(DESKTOP_PAD, 7).quit
    assert not _pad_events(DESKTOP_PAD, 12).menu_up    # desktop D-pad is a hat, not button 12


def test_wasd_moves_through_menus_and_zoom_has_its_own_keys():
    pygame.init()

    def press(*keys):
        inp = InputManager()
        inp.update([pygame.event.Event(pygame.KEYDOWN, key=k) for k in keys])
        return inp

    assert press(pygame.K_w).menu_up
    both = press(pygame.K_s, pygame.K_d)
    assert both.menu_down and both.menu_next
    turn = press(pygame.K_a)
    assert turn.menu_prev and not turn.zoom_out        # turning must not zoom the map
    out = press(pygame.K_MINUS)
    assert out.zoom_out and not out.menu_prev
    assert press(pygame.K_EQUALS).zoom_in
    assert press(pygame.K_SPACE).confirm
    assert press(pygame.K_RETURN).confirm


if __name__ == "__main__":
    failed = 0
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            try:
                fn()
                print(f"ok    {name}")
            except Exception as exc:   # noqa: BLE001
                failed += 1
                print(f"FAIL  {name}: {exc!r}")
    sys.exit(1 if failed else 0)
