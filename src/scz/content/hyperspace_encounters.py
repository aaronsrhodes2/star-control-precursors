"""Hyperspace encounter spec — what populates hyperspace beyond the
stars and the Coel Tessar Beat-4 trigger.

Two render paths feed off one content registry:

1. **Sensor-side (ambient + interactive both)**: every visible encounter
   contributes a `Ripple` to `hyperspace_ripples.current_ripples`. The
   Echo Sensor surfaces these as pulsing markers, in-range only.

2. **Collision-side (interactive only)**: encounters with
   `interactive=True` are also spawned as `EncounterPoint` objects in
   `HyperspaceScene._maybe_spawn_encounters`. Flying within the trigger
   radius fires the on_trigger callback — typically combat or dialog.

The split is deliberate: an ambient "Other-rift sighting" should
register on the sensor without ever resolving into a *thing the player
can fly into*, while a Cleanser patrol should do both. Same registry,
two consumer code paths.

**Slice content** (this round):

- **Cleanser patrol alpha** — appears after `tutorial_complete`. Sensor
  ripple at intensity 0.7, color "ship". Proximity → combat
  vs CLEANSER_CRUISER. First playable instance of the slice's central
  faction conflict (Cleansers enforcing kill orders).

- **Other-rift, north tear** — appears after `others_confirmed`. Sensor
  ripple at intensity 0.4, color "other". Ambient only — flying close
  does nothing. Reminds the player the Others are *out there*.

- **Distant Other-ripple, west** — same pattern, lower intensity.
  Atmospheric: the Echo Sensor catches *something* the player can never
  reach.

Future encounters land here by adding rows to `ENCOUNTERS` and (if
interactive) a corresponding trigger callback constant in
`scz.hyperspace.scene` (similar to `_trigger_coel_tessar`).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Callable

from scz.content.hyperspace_ripples import Ripple

if TYPE_CHECKING:
    from scz.engine.game import Game


@dataclass(frozen=True)
class EncounterSpec:
    """One hyperspace encounter — visible to the sensor, and optionally
    interactive (fires a callback on proximity).

    Fields:

    - `id`: stable string key. Used as the dedupe key when respawning the
      scene (we don't want two Cleanser patrols if the player exits and
      re-enters hyperspace mid-flag-state).
    - `label`: human-readable short tag. Rendered under the ripple marker
      when the sensor surfaces it.
    - `x, y`: universe-space coordinates (0..UNIVERSE_MAX). Fixed for the
      slice; future content can make them dynamic.
    - `kind`: one of "other" / "ship" / "anomaly" — drives ripple color.
    - `intensity`: 0.0..1.0 — drives ripple marker size + pulse rate.
    - `interactive`: True if proximity should fire a callback. False for
      ambient ripples (rifts, distant echoes).
    - `trigger_id`: when interactive=True, names the callback in
      `scz.hyperspace.scene._ENCOUNTER_TRIGGERS`. Indirected by string
      key (rather than a direct callable) so this content file stays
      free of scene imports — keeps content/engine layers separable.
    - `flag_gate`: optional flag name that must be truthy for the
      encounter to appear. Multiple flags via `flag_gates` (any-of for
      now; we don't need all-of yet).
    - `not_flag`: optional flag name that must be falsy. Used to retire
      encounters once they've been resolved (e.g. `met_cleanser_patrol`).
    """
    id: str
    label: str
    x: float
    y: float
    kind: str
    intensity: float
    interactive: bool = False
    trigger_id: str | None = None
    flag_gate: str | None = None
    # Optional second flag gate — when set, BOTH `flag_gate` and
    # `also_flag_gate` must be truthy for the encounter to appear. Used
    # for compound conditions like "patrol has been met AND others have
    # been heard about." Keep this two-flag at most for now; if compound
    # gating gets richer, extend to a tuple.
    also_flag_gate: str | None = None
    not_flag: str | None = None


# Slice-scope encounter registry.
#
# Coordinates anchor to Sol/Mh-Lai (~1793, 1450). UNIVERSE_MAX is 10000
# in the precursor-era starmap; "near home" is anything within ~1500 of
# Mh-Lai, "edge of mapped space" is anything beyond ~3500.
ENCOUNTERS: tuple[EncounterSpec, ...] = (
    EncounterSpec(
        id="cleanser_patrol_alpha",
        label="Cleanser patrol",
        # NW of Mh-Lai. Roughly in the "Furling-controlled space" zone
        # where the player is most likely to encounter the slice's
        # central political tension.
        x=1500.0, y=900.0,
        kind="ship",
        intensity=0.7,
        interactive=True,
        trigger_id="cleanser_patrol_alpha",
        flag_gate="tutorial_complete",
        not_flag="met_cleanser_patrol",
    ),
    EncounterSpec(
        id="other_rift_north",
        label="Distortion (north tear)",
        # Up near the top of mapped space. Far enough that the player
        # only catches it with a good sensor.
        x=2800.0, y=400.0,
        kind="other",
        intensity=0.4,
        interactive=False,
        flag_gate="others_confirmed",
    ),
    EncounterSpec(
        id="other_distant_west",
        label="Distortion (west)",
        # Far west — atmospheric. The player likely never reaches this
        # in the slice but the sensor catches it if they fly out that way.
        x=400.0, y=2200.0,
        kind="other",
        intensity=0.25,
        interactive=False,
        flag_gate="others_confirmed",
    ),
    EncounterSpec(
        id="cleanser_climax_alpha",
        label="Cleanser cruiser inbound",
        # Closer to Mh-Lai than the patrol — the named Cleanser arrives
        # *with intent* and stages near the home cluster. Sensor ripple
        # intensity is high (this Furling is here for the player).
        x=2100.0, y=1100.0,
        kind="ship",
        intensity=0.9,
        interactive=True,
        trigger_id="cleanser_climax_alpha",
        # Compound gate: appears only AFTER the foreshadow patrol has
        # been met AND the player has heard about the Others. This
        # sequencing keeps the foreshadow→climax beat distinct.
        flag_gate="met_cleanser_patrol",
        also_flag_gate="heard_about_others",
        not_flag="met_cleanser_climax",
    ),

    # =====================================================================
    # Deep-space ambient encounter density
    # =====================================================================
    # Hand-placed atmospheric encounters spread across the 10000x10000
    # universe — meant to make the *void between* the 503 stars feel
    # alive when the player has the Echo Sensor installed. Most are
    # ambient (ripple-only); four salvage wrecks are interactive (visit
    # → small cargo reward → encounter retires).
    #
    # No flag gating on the ambient entries: the moment the player has
    # an Echo Sensor, the map "fills in" with these markers. The salvage
    # wrecks retire on visit via their `not_flag`.
    #
    # Coordinates are placed away from Mh-Lai's home cluster
    # (~1500-2000 universe units around SOL) so the home region stays
    # quiet and these read as "out there in deep space."

    # Drifter signals — civilian ship wakes scattered across the map.
    # Sensor-visible only; flying close does nothing (no interactive flag).
    EncounterSpec(
        id="drifter_signal_alpha",
        label="Drifter wake",
        x=8500.0, y=1200.0,
        kind="ship", intensity=0.3,
    ),
    EncounterSpec(
        id="drifter_signal_beta",
        label="Drifter wake",
        x=700.0, y=7800.0,
        kind="ship", intensity=0.25,
    ),
    EncounterSpec(
        id="drifter_signal_gamma",
        label="Drifter wake",
        x=9000.0, y=5500.0,
        kind="ship", intensity=0.35,
    ),
    EncounterSpec(
        id="drifter_signal_delta",
        label="Drifter wake",
        x=200.0, y=4400.0,
        kind="ship", intensity=0.3,
    ),
    EncounterSpec(
        id="drifter_signal_epsilon",
        label="Drifter wake",
        x=5500.0, y=9000.0,
        kind="ship", intensity=0.25,
    ),
    EncounterSpec(
        id="drifter_signal_zeta",
        label="Drifter wake",
        x=3800.0, y=6800.0,
        kind="ship", intensity=0.3,
    ),
    EncounterSpec(
        id="drifter_signal_eta",
        label="Drifter wake",
        x=7200.0, y=7500.0,
        kind="ship", intensity=0.25,
    ),
    EncounterSpec(
        id="drifter_signal_theta",
        label="Drifter wake",
        x=1100.0, y=9200.0,
        kind="ship", intensity=0.2,
    ),

    # Distant Other-echoes — atmospheric ambient at far corners of the map.
    # These complement the two flag-gated Other ripples (north tear, west)
    # by surfacing the Others' presence as a *constant background noise*
    # once the Echo Sensor is installed, without requiring story-flag.
    EncounterSpec(
        id="other_echo_corner_se",
        label="Distortion (deep)",
        x=9500.0, y=9500.0,
        kind="other", intensity=0.2,
    ),
    EncounterSpec(
        id="other_echo_corner_ne",
        label="Distortion (deep)",
        x=8800.0, y=200.0,
        kind="other", intensity=0.18,
    ),
    EncounterSpec(
        id="other_echo_corner_sw",
        label="Distortion (deep)",
        x=200.0, y=9800.0,
        kind="other", intensity=0.18,
    ),
    EncounterSpec(
        id="other_echo_far_north",
        label="Distortion (deep)",
        x=4500.0, y=200.0,
        kind="other", intensity=0.15,
    ),

    # Anomaly pulses — unknown-signal cyan markers, generic-curiosity
    # density. Atmospheric; sensor-only; no interaction yet.
    EncounterSpec(
        id="anomaly_pulse_alpha",
        label="Anomaly",
        x=6000.0, y=4500.0,
        kind="anomaly", intensity=0.4,
    ),
    EncounterSpec(
        id="anomaly_pulse_beta",
        label="Anomaly",
        x=3000.0, y=5500.0,
        kind="anomaly", intensity=0.35,
    ),
    EncounterSpec(
        id="anomaly_pulse_gamma",
        label="Anomaly",
        x=7500.0, y=3500.0,
        kind="anomaly", intensity=0.45,
    ),
    EncounterSpec(
        id="anomaly_pulse_delta",
        label="Anomaly",
        x=1200.0, y=5000.0,
        kind="anomaly", intensity=0.3,
    ),

    # Salvage wrecks — INTERACTIVE. Flying close awards a small mineral
    # bundle and retires the encounter. Sensor reads them as ship-kind
    # ripples; the player can choose to visit or not. Limited quantity
    # so they read as genuine finds, not a grind loop.
    EncounterSpec(
        id="salvage_wreck_alpha",
        label="Wreck (salvageable)",
        x=4500.0, y=5000.0,
        kind="ship", intensity=0.4,
        interactive=True,
        trigger_id="salvage_wreck_alpha",
        not_flag="salvaged_alpha",
    ),
    EncounterSpec(
        id="salvage_wreck_beta",
        label="Wreck (salvageable)",
        x=8000.0, y=6000.0,
        kind="ship", intensity=0.4,
        interactive=True,
        trigger_id="salvage_wreck_beta",
        not_flag="salvaged_beta",
    ),
    EncounterSpec(
        id="salvage_wreck_gamma",
        label="Wreck (salvageable)",
        x=3000.0, y=8000.0,
        kind="ship", intensity=0.4,
        interactive=True,
        trigger_id="salvage_wreck_gamma",
        not_flag="salvaged_gamma",
    ),
    EncounterSpec(
        id="salvage_wreck_delta",
        label="Wreck (salvageable)",
        x=6500.0, y=1500.0,
        kind="ship", intensity=0.4,
        interactive=True,
        trigger_id="salvage_wreck_delta",
        not_flag="salvaged_delta",
    ),
)


def encounters_visible(game: "Game") -> list[EncounterSpec]:
    """Return the encounter specs currently active for this game state.

    Filters by:
    - `flag_gate` — must be truthy when set
    - `also_flag_gate` — must also be truthy when set (compound AND)
    - `not_flag` — must be falsy when set (retire after resolved)
    """
    flags = game.flags
    out: list[EncounterSpec] = []
    for spec in ENCOUNTERS:
        if spec.flag_gate is not None and not flags.get(spec.flag_gate):
            continue
        if spec.also_flag_gate is not None and not flags.get(spec.also_flag_gate):
            continue
        if spec.not_flag is not None and flags.get(spec.not_flag):
            continue
        out.append(spec)
    return out


def encounter_ripples(game: "Game") -> list[Ripple]:
    """Convert visible encounters to sensor ripples.

    Every encounter (interactive or ambient) contributes one ripple. The
    Echo Sensor surfaces them when in range; the renderer applies the
    distance filter in `_visible_ripples`. Returns [] when nothing is
    visible.
    """
    return [
        Ripple(
            x=spec.x, y=spec.y,
            kind=spec.kind, intensity=spec.intensity,
            label=spec.label,
        )
        for spec in encounters_visible(game)
    ]


# Trigger-callback table populated by `scz.hyperspace.scene` at module
# import time (avoids the content layer importing the scene layer).
# Keys match `EncounterSpec.trigger_id`. Each callable takes the
# HyperspaceScene instance and returns None — typical action is to set
# scene to a combat or dialog scene with a back-to-hyperspace parent
# factory.
_ENCOUNTER_TRIGGERS: dict[str, Callable[[object], None]] = {}


def register_trigger(trigger_id: str, fn: Callable[[object], None]) -> None:
    """Register a trigger callback by id. Idempotent — re-registering
    the same id overwrites the previous callable. Called from the
    hyperspace scene at module load.
    """
    _ENCOUNTER_TRIGGERS[trigger_id] = fn


def get_trigger(trigger_id: str) -> Callable[[object], None] | None:
    """Look up a registered trigger callback by id. Returns None if no
    matching trigger has been registered — the caller (scene
    `_maybe_spawn_encounters`) should skip that encounter rather than
    crashing.
    """
    return _ENCOUNTER_TRIGGERS.get(trigger_id)
