"""Runtime planet sphere widget — load pre-rendered rotation frames
and return the current frame for a given planet at a given game time.

Same planet shows the SAME visual across scanner / solar-system /
combat views: each view calls `get_frame(planet_id, time_seconds)`
and gets a pygame Surface from a shared cache. Frames are pre-rendered
by `tools/animate_planet.py` from each planet's 2D Firefly painting
via sphere-warp equirectangular projection.

SC2 ref: `references/uqm-source/sc2/src/uqm/planets/plangen.c`
- our `tools/animate_planet.py` mirrors `CreateSphereTiltMap` +
  `RenderPlanetSphere` but pre-bakes frames offline instead of
  computing them per render frame.

Source layout:
    assets/planets/animated/<planet_id>/rot_NN.png   (NN = 00..15)

Usage:
    from scz.content.planet_sphere import get_frame, has_sphere

    if has_sphere("mh_lai"):
        surf = get_frame("mh_lai", game.time_seconds, diameter=192)
        screen.blit(surf, (cx - surf.get_width()//2, cy - surf.get_height()//2))
"""

from __future__ import annotations

import pathlib

import pygame


_ROOT = pathlib.Path(__file__).resolve().parent.parent.parent.parent
_ANIM_DIR = _ROOT / "assets" / "planets" / "animated"
_DEFAULT_FPS = 6.0

# (planet_id, target_diameter) -> list of pygame.Surface, indexed by frame
_CACHE: dict[tuple[str, int], list[pygame.Surface]] = {}
# (planet_id,) -> frame count discovered on disk, or 0 if no sphere
_FRAME_COUNT: dict[str, int] = {}


def _discover_frames(planet_id: str) -> int:
    """Return the number of rot_NN.png frames on disk for this planet,
    or 0 if there's no animated/<planet_id>/ dir.
    Cached after first call.
    """
    if planet_id in _FRAME_COUNT:
        return _FRAME_COUNT[planet_id]
    d = _ANIM_DIR / planet_id
    if not d.is_dir():
        _FRAME_COUNT[planet_id] = 0
        return 0
    frames = sorted(d.glob("rot_*.png"))
    _FRAME_COUNT[planet_id] = len(frames)
    return len(frames)


def has_sphere(planet_id: str) -> bool:
    """True if there's a pre-rendered rotation sequence for this planet."""
    return _discover_frames(planet_id) > 0


def _load_sequence(planet_id: str, diameter: int) -> list[pygame.Surface]:
    """Load + cache the rotation sequence at the requested diameter."""
    key = (planet_id, diameter)
    cached = _CACHE.get(key)
    if cached is not None:
        return cached
    n = _discover_frames(planet_id)
    if n == 0:
        _CACHE[key] = []
        return []
    d = _ANIM_DIR / planet_id
    frames: list[pygame.Surface] = []
    for i in range(n):
        path = d / f"rot_{i:02d}.png"
        if not path.exists():
            continue
        img = pygame.image.load(str(path)).convert_alpha()
        if img.get_width() != diameter:
            scale = diameter / img.get_width()
            new_w = max(1, int(img.get_width() * scale))
            new_h = max(1, int(img.get_height() * scale))
            img = pygame.transform.smoothscale(img, (new_w, new_h))
        frames.append(img)
    _CACHE[key] = frames
    return frames


def get_frame(
    planet_id: str,
    time_seconds: float,
    diameter: int = 192,
    fps: float = _DEFAULT_FPS,
) -> pygame.Surface | None:
    """Return the current rotation frame for `planet_id` at game time
    `time_seconds`, scaled so width equals `diameter`. Returns None if
    no sphere is available for this planet (caller should fall back to
    a static sprite).

    Time-sync rule: all views pass the same `time_seconds` (game-clock
    seconds since scene/game start) so the planet rotates continuously
    across view transitions — no visible jump when moving from solar
    system to orbit to combat.
    """
    frames = _load_sequence(planet_id, diameter)
    if not frames:
        return None
    idx = int(time_seconds * fps) % len(frames)
    return frames[idx]


def clear_cache() -> None:
    """For tests / hot-reload."""
    _CACHE.clear()
    _FRAME_COUNT.clear()
