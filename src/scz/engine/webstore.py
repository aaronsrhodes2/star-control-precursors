"""Browser save persistence — mirrors the campaign folder into localStorage.

The web build (pygbag / WebAssembly) writes saves to an in-memory
filesystem that is thrown away when the tab reloads. This module copies
every file the CampaignManager writes into the browser's localStorage
and puts them back on the next launch, so the rest of the persistence
code keeps using ordinary files.

One localStorage entry per file: key = PREFIX + path relative to the
campaign root, value = "t:" + text for JSON or "b:" + base64 for PNG
thumbnails. Saves stay on the one browser they were made in.

A browser allows a site ~5 MB. The JSON is tiny (~3 KB a save); the
thumbnails are not (up to ~100 KB each as base64), so they are the
first thing to go: when the store is full, every thumbnail is dropped
and thumbnails stop being mirrored, which leaves room for thousands of
saves. A save without a thumbnail still loads; the scrubber just shows
no picture for it.

Everything here is best-effort: a full or disabled localStorage must
never break the game, so failures are logged once and swallowed.
"""

from __future__ import annotations

import base64
import sys
from pathlib import Path
from typing import Any

IS_WEB = sys.platform == "emscripten"
PREFIX = "scz-save/"

_warned = False
_thumbnails_off = False           # set once the store has filled up
_storage_override: Any = None     # tests inject a fake localStorage here


def _storage() -> Any:
    if _storage_override is not None:
        return _storage_override
    if not IS_WEB:
        return None
    import platform
    return platform.window.localStorage


def _warn(what: str, err: Exception) -> None:
    global _warned
    if not _warned:
        print(f"[save] browser storage {what} failed: {err}")
        _warned = True


def _key(path: Path, root: Path) -> str:
    return PREFIX + path.relative_to(root).as_posix()


def put(path: Path, root: Path) -> bool:
    """Copy one just-written file into localStorage. False if it didn't fit."""
    store = _storage()
    if store is None:
        return False
    try:
        if path.suffix == ".json":
            value = "t:" + path.read_text(encoding="utf-8")
        else:
            value = "b:" + base64.b64encode(path.read_bytes()).decode("ascii")
        store.setItem(_key(path, root), value)
        return True
    except Exception:   # quota exceeded, storage disabled, ...
        return False


def _drop_thumbnails(store: Any) -> None:
    """Free the space the thumbnails hold and stop mirroring them."""
    global _thumbnails_off
    _thumbnails_off = True
    for key in [str(store.key(i)) for i in range(int(store.length))]:
        if key.startswith(PREFIX) and not key.endswith(".json"):
            store.removeItem(key)


def restore(root: Path) -> int:
    """Recreate every mirrored file under `root`. Returns the file count."""
    store = _storage()
    if store is None:
        return 0
    count = 0
    try:
        keys = [str(store.key(i)) for i in range(int(store.length))]
        for key in keys:
            if not key.startswith(PREFIX):
                continue
            rel = key[len(PREFIX):]
            if ".." in rel.split("/"):
                continue
            value = str(store.getItem(key))
            out = root / rel
            out.parent.mkdir(parents=True, exist_ok=True)
            if value.startswith("t:"):
                out.write_text(value[2:], encoding="utf-8")
            elif value.startswith("b:"):
                out.write_bytes(base64.b64decode(value[2:]))
            else:
                continue
            count += 1
    except Exception as e:
        _warn("read", e)
    return count


def sync(root: Path) -> None:
    """Make localStorage match the files under `root`.

    Called after the CampaignManager writes or deletes anything. Save
    files never change once written, so only new files, meta.json
    (rewritten on every save) and deletions cost a storage call.
    """
    store = _storage()
    if store is None:
        return
    try:
        stored = {
            k for k in (str(store.key(i)) for i in range(int(store.length)))
            if k.startswith(PREFIX)
        }
    except Exception as e:
        _warn("read", e)
        return
    files = [f for f in root.rglob("*") if f.is_file()]
    on_disk = {_key(f, root) for f in files}
    # Deletions first: pruned saves make room for the new one.
    for key in stored - on_disk:
        try:
            store.removeItem(key)
        except Exception as e:
            _warn("delete", e)
    # JSON before thumbnails, so the part that matters lands first.
    for f in sorted(files, key=lambda f: f.suffix != ".json"):
        key = _key(f, root)
        is_json = f.suffix == ".json"
        if not is_json and _thumbnails_off:
            continue
        if key in stored and f.name != "meta.json":
            continue
        if put(f, root):
            continue
        try:
            if not _thumbnails_off:
                _drop_thumbnails(store)
                if is_json and put(f, root):
                    continue
            if is_json:
                _warn("write", RuntimeError(f"no room for {key}"))
        except Exception as e:
            _warn("write", e)
