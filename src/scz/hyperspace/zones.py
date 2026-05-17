"""Species control zones — toggleable overlay on the hyperspace map.

Each ControlZone owns a list of star coordinates in universe space + a
color + an alpha. The renderer composites a soft-blob (radial-gradient)
mask around each star and unions them per-zone, then blits all visible
zones onto the map view.

Zones are deliberately *vague* — they're "areas of influence", not hard
borders. The blob radius is roughly one cluster's worth of stars so
neighboring stars of the same species visually merge into a single
fuzzy area.

Toggle hotkey is wired in HyperspaceScene.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Callable

import pygame


# Blob radius in universe units. Roughly the spacing between adjacent
# stars in a cluster, so multiple stars of the same species merge into
# a single fuzzy area.
ZONE_BLOB_RADIUS_UNIVERSE = 700.0

# Internal cache: blob template surfaces keyed by (radius_px, color, alpha)
_BLOB_CACHE: dict[tuple[int, tuple[int, int, int], int], pygame.Surface] = {}


@dataclass(frozen=True)
class ControlZone:
    """One species' area of influence on the hyperspace map."""
    species_id: str
    display_name: str
    star_coords: tuple[tuple[float, float], ...]
    color: tuple[int, int, int]    # RGB; alpha applied at render
    alpha: int = 60                # 0-255
    blob_radius: float = ZONE_BLOB_RADIUS_UNIVERSE


# Type alias for the universe→screen transform function
TransformFn = Callable[[float, float], tuple[float, float]]


class ZoneRenderer:
    """Renders all registered ControlZones as soft-blob overlays.

    Hidden by default (`visible=False`); toggle with `.toggle()`. Render
    AFTER stars but BEFORE labels so the zone color tints the sky behind
    the stars but the names still read clearly on top.
    """

    def __init__(self, zones: tuple[ControlZone, ...]) -> None:
        self.zones = zones
        self.visible: bool = False

    def toggle(self) -> None:
        self.visible = not self.visible

    def render(
        self,
        surface: pygame.Surface,
        transform: TransformFn,
        zoom: float,
    ) -> None:
        """Composite each visible zone's blob onto the surface."""
        if not self.visible:
            return
        sw, sh = surface.get_size()
        for zone in self.zones:
            # Blob radius in pixels scales with zoom AND with base_scale,
            # but the transform encapsulates both — we can compute by
            # transforming a point and a point offset by one universe
            # unit, taking the screen-space delta as effective scale.
            x0, y0 = transform(0.0, 0.0)
            x1, _ = transform(1.0, 0.0)
            effective_scale_px_per_unit = max(0.001, abs(x1 - x0))
            radius_px = int(zone.blob_radius * effective_scale_px_per_unit)
            if radius_px < 4:
                # Too small to read; skip — the cluster will be a single
                # color-tinted star anyway.
                continue

            blob = _get_blob_surface(radius_px, zone.color, zone.alpha)
            for ux, uy in zone.star_coords:
                sx, sy = transform(ux, uy)
                # Cheap on-screen cull
                if sx < -radius_px or sx > sw + radius_px:
                    continue
                if sy < -radius_px or sy > sh + radius_px:
                    continue
                surface.blit(
                    blob,
                    (int(sx) - radius_px, int(sy) - radius_px),
                    special_flags=pygame.BLEND_RGBA_ADD,
                )


def _get_blob_surface(
    radius_px: int, color: tuple[int, int, int], alpha: int,
) -> pygame.Surface:
    """Return a cached radial-gradient blob surface. Built lazily."""
    key = (radius_px, color, alpha)
    cached = _BLOB_CACHE.get(key)
    if cached is not None:
        return cached
    size = radius_px * 2 + 2
    surf = pygame.Surface((size, size), pygame.SRCALPHA)
    cx, cy = size // 2, size // 2
    # Build with ~16 alpha rings so we don't burn time per-pixel.
    rings = 18
    for i in range(rings, 0, -1):
        t = i / rings
        r = int(radius_px * t)
        # Quadratic falloff feels softer than linear
        a = int(alpha * (1.0 - t) * (1.0 - t))
        pygame.draw.circle(surf, (color[0], color[1], color[2], a), (cx, cy), r)
    _BLOB_CACHE[key] = surf
    return surf


# ---------------------------------------------------------------------------
# Default zones — derived from stars.json defined_name tags.
#
# Note: lore-tagged stars in our era are mostly PROTO-species (not sentient).
# These don't have control zones — they're below detection threshold and
# below player engagement. The zones below cover only the ACTIVE sentient
# species or active Furling factions present in the slice.
# ---------------------------------------------------------------------------

def build_default_zones(stars: list[dict]) -> tuple[ControlZone, ...]:
    """Walk the loaded stars list and assemble the canonical zone set."""

    def coords_with_name(name: str) -> tuple[tuple[float, float], ...]:
        return tuple(
            (float(s["x"]), float(s["y"]))
            for s in stars
            if s.get("defined_name") == name
        )

    zones: list[ControlZone] = []

    # Slylandro — single homeworld at Beta Corvi. Sentient species in our
    # era; the Cloak quest target.
    slylandro = coords_with_name("SLYLANDRO")
    if slylandro:
        zones.append(ControlZone(
            species_id="SLYLANDRO",
            display_name="Slylandro Witness",
            star_coords=slylandro,
            color=(255, 180, 130),
            alpha=70,
            blob_radius=900.0,
        ))

    # Mycon biot hives — Furling terraforming experiments waking up into
    # sentience (Deep Child arc).
    mycon = coords_with_name("MYCON_BIOT_HIVE")
    if mycon:
        zones.append(ControlZone(
            species_id="MYCON_BIOT_HIVE",
            display_name="Mycon Biot Hives",
            star_coords=mycon,
            color=(255, 100, 100),
            alpha=70,
            blob_radius=800.0,
        ))

    # Mmrnmhrm + Chenjesu at the Ossuary (Procyon). The robot/crystal
    # survivors of a prior cycle. Sentient but rooted; no ships.
    chenjesu = coords_with_name("CHENJESU_PROTO")
    if chenjesu:
        zones.append(ControlZone(
            species_id="MMRNMHRM_CHENJESU",
            display_name="Mmrnmhrm + Chenjesu (Ossuary)",
            star_coords=chenjesu,
            color=(140, 200, 240),
            alpha=70,
            blob_radius=800.0,
        ))

    # Melnorme trade routes — they nomad-orbit super-giants. Multiple
    # MELNORME_PROTO stars; merge them into one large vague zone.
    melnorme = coords_with_name("MELNORME_PROTO")
    if melnorme:
        zones.append(ControlZone(
            species_id="MELNORME",
            display_name="Melnorme Trade Routes",
            star_coords=melnorme,
            color=(255, 130, 60),
            alpha=50,
            blob_radius=600.0,
        ))

    # Rainbow Worlds — the player's seeding arc. Toggle these as a "where
    # are the Rainbow Worlds?" overlay so a fresh player can find them.
    rainbow = coords_with_name("RAINBOW_BEING_SEEDED")
    if rainbow:
        zones.append(ControlZone(
            species_id="RAINBOW_WORLDS",
            display_name="Rainbow Worlds (Migration arrow)",
            star_coords=rainbow,
            color=(220, 160, 255),
            alpha=80,
            blob_radius=500.0,
        ))

    # Orz rift incursions — dimensional threat markers
    orz = coords_with_name("ORZ_RIFT")
    if orz:
        zones.append(ControlZone(
            species_id="ORZ_RIFT",
            display_name="Orz Rift Incursions",
            star_coords=orz,
            color=(180, 100, 255),
            alpha=70,
            blob_radius=600.0,
        ))

    return tuple(zones)
