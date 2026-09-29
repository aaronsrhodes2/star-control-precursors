"""Hyperspace ripples — what the Hyperspace-Echo Sensor passively detects.

The Echo Sensor is a Slylandro-traded sensor module (quest reward — see
[species-quests.md "Slylandro Cloak"](../../../references/lore/species-quests.md)).
Its in-fiction reading is *the small pre-arrival distortions the Others
leave in adjacent space — the same eddies the Slylandro have been carefully
cataloguing for ten thousand years*.

**The sensor is passive and always-on when installed.** There is no toggle,
no button-press, no manual activation. Installing it in the ship's sensor
slot is the only action; from there it continuously surfaces whatever
ripples are currently detectable in hyperspace, rendered as pulsing markers
overlaid on the starmap.

This module owns the **data layer**: a `Ripple` dataclass and a
`current_ripples(game)` helper. The `HyperspaceScene` renderer queries this
every frame (cheap) when the sensor is installed and draws the result.

**Slice-scope content**: hyperspace encounter content is not yet populated.
`current_ripples()` returns an empty list by default. As future hyperspace
encounters land (Burvixese Caster activation flare, Cleanser cruiser
approach, Other-rift sighting, enemy ship intercept, etc.), they will be
registered here based on `game.flags`. The visualization framework is
ready; the *content* fills in over time.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from scz.engine.game import Game


@dataclass(frozen=True)
class Ripple:
    """One ripple the Echo Sensor surfaces in hyperspace.

    The renderer draws a pulsing marker at `(x, y)` in universe-space. The
    `kind` field picks a palette color (Others / ship / anomaly); the
    `intensity` field (0.0-1.0) drives marker size and pulse rate — faint
    distant readings pulse slowly, urgent close threats pulse fast.
    """
    x: float
    y: float
    kind: str          # "other" | "ship" | "anomaly" — drives marker color
    intensity: float   # 0.0 (faint distant reading) ... 1.0 (urgent, close)
    label: str | None = None   # optional short tag rendered under the marker


# Marker palette by ripple kind. Tuned to read distinctly from stars (which
# use star-body colors) and from encounter points (which use per-encounter
# colors authored at trigger time).
RIPPLE_COLORS: dict[str, tuple[int, int, int]] = {
    "other":   (180,  90, 220),   # violet — the Others' dimensional signature
    "ship":    (220, 180, 120),   # warm amber — another vessel's hyperdrive wake
    "anomaly": (120, 200, 200),   # cyan — generic / unidentified dimensional anomaly
}


# Multiplier from `other_detection_range` stat → universe units.
# Echo Sensor's `other_detection_range: 2.0` therefore = 2000-unit detection
# radius in universe-space. Future stronger sensors can stack/replace this.
RIPPLE_RANGE_SCALE: float = 1000.0


def echo_sensor_installed(game: "Game") -> bool:
    """True iff the Hyperspace-Echo Sensor module is in the player's sensor slot.

    Gates the entire ripple overlay. The Steward installs the module at
    Mh-Lai Station; from then on the sensor is passively active in every
    hyperspace scene.
    """
    from scz.content.modules import is_module_installed
    return is_module_installed(game, "hyperspace_echo_sensor")


def effective_ripple_range(game: "Game") -> float:
    """Universe-unit radius within which the player's installed sensor can
    surface ripples. Sums any module's `other_detection_range` delta and
    scales by `RIPPLE_RANGE_SCALE`.

    Returns 0.0 when no ripple-capable sensor is installed (the renderer
    short-circuits before calling this when `echo_sensor_installed()` is
    False, but this remains correct in all cases).
    """
    return game.effective_stat("other_detection_range", 0.0) * RIPPLE_RANGE_SCALE


def current_ripples(game: "Game") -> list[Ripple]:
    """Return the ripples currently detectable by the Echo Sensor.

    Called every frame by `HyperspaceScene._draw_ripples` when the sensor
    is installed. Cheap by design — return [] when nothing is detectable.

    Sources, in order:
    1. `hyperspace_encounters.encounter_ripples(game)` — the canonical
       slice content registry. Both interactive (Cleanser patrol, etc.)
       and ambient (Other-rift sightings) encounters produce one ripple
       each. Flag-gated visibility lives there.
    2. *(future)* event-driven transient ripples — e.g. a Caster
       activation broadcast with a time-bounded lifetime. Slot in as a
       second source when that content lands.
    """
    # Lazy import keeps the ripple module free of the encounters
    # registry at top level so the content layers stay decoupled.
    from scz.content.hyperspace_encounters import encounter_ripples
    return encounter_ripples(game)
