"""Load + cache UQM planet sprite assets.

Maps UQM planet-type enum names (e.g. WATER_WORLD) to pygame Surfaces.
Three sizes available: "big" (75x67), "med" (38x34), "sml" (19x17).
Scenes that want a bigger render just `pygame.transform.scale` the
"big" sprite — UQM's pixel-art aesthetic stays intact when upscaled.

Also provides a fallback mapping from our internal 8-bucket planet
type ("TERRESTRIAL", "OCEAN", etc.) to a representative UQM sprite,
so hand-built systems (Mh-Lai, Arilou Outpost, Beta Corvi) also get
real planet visuals.
"""

from __future__ import annotations

import json
from pathlib import Path

import pygame


_DATA_DIR = Path(__file__).resolve().parent / "universe"
_ASSETS_DIR = Path(__file__).resolve().parent.parent.parent.parent / "assets" / "planets"
_SPRITES_JSON = _DATA_DIR / "uqm_planet_sprites.json"


# Loaded on demand; sprites cached by (uqm_type, size)
_SPRITE_MAP: dict[str, dict[str, str]] | None = None
_LOADED: dict[tuple[str, str], pygame.Surface] = {}


# Fallback: our 8-bucket internal type → a representative UQM type.
# Used when a planet has no `uqm_type` attribute (hand-built systems
# in home_system.py, arilou_outpost.py, beta_corvi.py). Picked for
# visual fit — water world for ocean, magma for volcanic, etc.
LEGACY_TO_UQM: dict[str, str] = {
    "TERRESTRIAL": "ORGANIC_WORLD",
    "OCEAN":       "WATER_WORLD",
    "ROCKY":       "CHONDRITE_WORLD",
    "DESERT":      "DUST_WORLD",
    "ICE":         "PELLUCID_WORLD",
    "PRIMORDIAL":  "PRIMORDIAL_WORLD",
    "VOLCANIC":    "MAGMA_WORLD",
    "GAS_GIANT":   "ORA_GAS_GIANT",
}


def _sprite_map() -> dict[str, dict[str, str]]:
    global _SPRITE_MAP
    if _SPRITE_MAP is None:
        if _SPRITES_JSON.exists():
            _SPRITE_MAP = json.loads(_SPRITES_JSON.read_text(encoding="utf-8"))
        else:
            _SPRITE_MAP = {}
    return _SPRITE_MAP


def sprite_for(uqm_type: str, size: str = "big") -> pygame.Surface | None:
    """Return the cached pygame Surface for a UQM planet type at the
    requested size ('big' | 'med' | 'sml'), or None if unknown.

    Loads from disk on first request per (type, size).
    """
    key = (uqm_type, size)
    cached = _LOADED.get(key)
    if cached is not None:
        return cached
    entry = _sprite_map().get(uqm_type)
    if entry is None:
        return None
    fname = entry.get(size)
    if fname is None:
        return None
    path = _ASSETS_DIR / fname
    if not path.exists():
        return None
    surf = pygame.image.load(str(path)).convert_alpha()
    _LOADED[key] = surf
    return surf


def sprite_for_legacy(legacy_type: str, size: str = "big") -> pygame.Surface | None:
    """Hand-built systems use the 8-bucket legacy type. Map to a
    representative UQM type and return that sprite."""
    uqm_type = LEGACY_TO_UQM.get(legacy_type)
    if uqm_type is None:
        return None
    return sprite_for(uqm_type, size)


def scaled_sprite(
    uqm_type: str, target_diameter: int, size: str = "big"
) -> pygame.Surface | None:
    """Convenience: load the sprite at `size`, then scale (preserving
    aspect ratio) so its longest dimension is `target_diameter` pixels.
    Cached per (type, size, target_diameter).
    """
    cache_key = (uqm_type, size, target_diameter)
    cached = _LOADED.get(cache_key)
    if cached is not None:
        return cached
    base = sprite_for(uqm_type, size)
    if base is None:
        return None
    bw, bh = base.get_size()
    longest = max(bw, bh)
    if longest <= 0:
        return None
    scale = target_diameter / longest
    new_w = max(1, int(bw * scale))
    new_h = max(1, int(bh * scale))
    scaled = pygame.transform.scale(base, (new_w, new_h))
    _LOADED[cache_key] = scaled
    return scaled


def scaled_sprite_for_legacy(
    legacy_type: str, target_diameter: int, size: str = "big"
) -> pygame.Surface | None:
    uqm_type = LEGACY_TO_UQM.get(legacy_type)
    if uqm_type is None:
        return None
    return scaled_sprite(uqm_type, target_diameter, size)
