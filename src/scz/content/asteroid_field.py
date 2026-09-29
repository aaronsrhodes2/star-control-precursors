"""Runtime asteroid field — load irregular asteroid sprites and place
them as rotating, drifting backdrop props in combat scenes.

Each asteroid uses pygame.transform.rotozoom for 2D rotation; the
irregular silhouette reads as a 3D tumbling rock without needing
pre-baked rotation frames (unlike planets, which need sphere-warp to
look spherical).

Asteroids live at `assets/asteroids/asteroid_*.png`, alpha-extracted
by `tools/extract_asteroid_alpha.py`. The widget supports an arbitrary
pool — drop in more sprites and they'll be picked up automatically.

Usage:
    from scz.content.asteroid_field import AsteroidField

    self.asteroids = AsteroidField(seed=42).spawn(
        arena_w=ARENA_W, arena_h=ARENA_H, count=6,
    )
    # per tick:
    self.asteroids.update(dt)
    # per render:
    self.asteroids.draw(screen, ox, oy, scale)
"""

from __future__ import annotations

import math
import pathlib
import random
from dataclasses import dataclass

import pygame


_ROOT = pathlib.Path(__file__).resolve().parent.parent.parent.parent
_ASSET_DIR = _ROOT / "assets" / "asteroids"


_SPRITE_CACHE: list[pygame.Surface] | None = None


def _load_sprites() -> list[pygame.Surface]:
    """Load all asteroid sprites once, cached."""
    global _SPRITE_CACHE
    if _SPRITE_CACHE is not None:
        return _SPRITE_CACHE
    out: list[pygame.Surface] = []
    if _ASSET_DIR.exists():
        for path in sorted(_ASSET_DIR.glob("asteroid_*.png")):
            try:
                surf = pygame.image.load(str(path)).convert_alpha()
                out.append(surf)
            except (pygame.error, OSError):
                continue
    _SPRITE_CACHE = out
    return out


@dataclass
class AsteroidInstance:
    sprite_index: int       # index into the sprite pool
    x: float                # world x
    y: float                # world y
    vx: float               # drift velocity
    vy: float
    angle: float            # current rotation, degrees
    angular_velocity: float # deg/sec
    base_size: float        # world-units along the longest axis


class AsteroidField:
    """A pool of asteroid instances. Stateless wrt rendering — call
    update + draw each frame.
    """

    def __init__(self, seed: int | None = None) -> None:
        self.rng = random.Random(seed) if seed is not None else random.Random()
        self.asteroids: list[AsteroidInstance] = []
        # Cache rotated surfaces per (sprite_index, rounded_angle, size_key)
        # so we don't rotozoom every asteroid every frame.
        self._rot_cache: dict[tuple[int, int, int], pygame.Surface] = {}

    def spawn(
        self,
        arena_w: float,
        arena_h: float,
        count: int = 6,
        min_size: float = 32.0,
        max_size: float = 96.0,
        max_drift_speed: float = 18.0,
        max_angular_speed: float = 35.0,
        clear_margin: float = 80.0,
    ) -> "AsteroidField":
        """Populate the field. clear_margin keeps asteroids away from
        the arena center (where ships spawn). Returns self for chaining.
        """
        sprites = _load_sprites()
        if not sprites:
            self.asteroids = []
            return self
        cx, cy = arena_w / 2, arena_h / 2
        for _ in range(count):
            for _attempt in range(20):
                x = self.rng.uniform(0, arena_w)
                y = self.rng.uniform(0, arena_h)
                if math.hypot(x - cx, y - cy) > clear_margin:
                    break
            else:
                continue
            self.asteroids.append(AsteroidInstance(
                sprite_index=self.rng.randrange(len(sprites)),
                x=x, y=y,
                vx=self.rng.uniform(-max_drift_speed, max_drift_speed),
                vy=self.rng.uniform(-max_drift_speed, max_drift_speed),
                angle=self.rng.uniform(0, 360),
                angular_velocity=self.rng.uniform(-max_angular_speed, max_angular_speed),
                base_size=self.rng.uniform(min_size, max_size),
            ))
        return self

    def update(self, dt: float, arena_w: float, arena_h: float) -> None:
        for a in self.asteroids:
            a.x = (a.x + a.vx * dt) % arena_w
            a.y = (a.y + a.vy * dt) % arena_h
            a.angle = (a.angle + a.angular_velocity * dt) % 360.0

    def draw(
        self,
        screen: pygame.Surface,
        ox: float,
        oy: float,
        scale: float,
        world_to_screen,
    ) -> None:
        """Render all asteroids. `world_to_screen` is the caller's
        function (world_x, world_y, ox, oy, scale) -> (screen_x, screen_y)
        so we share its coordinate logic.
        """
        sprites = _load_sprites()
        if not sprites:
            return
        for a in self.asteroids:
            base = sprites[a.sprite_index]
            # rotozoom is expensive — cache at integer angle + size
            angle_q = int(a.angle / 8) * 8  # quantize to 8deg buckets
            target_diam = max(8, int(a.base_size * scale))
            cache_key = (a.sprite_index, angle_q, target_diam)
            rotated = self._rot_cache.get(cache_key)
            if rotated is None:
                # rotozoom scale param: relative to base sprite size
                bw, bh = base.get_size()
                base_scale = target_diam / max(bw, bh)
                rotated = pygame.transform.rotozoom(base, float(angle_q), base_scale)
                # Cap cache to avoid unbounded growth
                if len(self._rot_cache) > 256:
                    self._rot_cache.clear()
                self._rot_cache[cache_key] = rotated
            sx, sy = world_to_screen(a.x, a.y, ox, oy, scale)
            rect = rotated.get_rect(center=(int(sx), int(sy)))
            screen.blit(rotated, rect)
