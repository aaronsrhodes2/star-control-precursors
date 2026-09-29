"""System-level scan data — what an upgraded sensor surfaces about a
star system *from hyperspace*, before the player enters it.

Conceptually parallel to `hyperspace_ripples`: that module tells the
sensor "what threats/anomalies are *out there in deep space*"; this
module tells the sensor "what's *in this star system over there*."

The architecture:

1. `scan_system(star)` is a pure function from a star dict to a
   `SystemScan` summary. It aggregates the already-deterministic outputs
   of `generate_uqm_system()` (planet list) and `generate_deposits()`
   (per-planet deposit list), so the numbers a sensor reports match
   what the player will actually find on entry.

2. Sensor modules add capability stats on top of the base game stat
   layer. Each sensor declares what it can show: `system_resource_scan`,
   `system_anomaly_scan`, `proto_species_scan`, etc. The
   `HyperspaceScene` HUD queries `game.effective_stat(stat, 0.0)` and
   reveals the corresponding `SystemScan` fields when the player has
   the relevant module.

3. Cache results per star — `scan_system` is potentially called every
   frame for the nearest-star HUD. The underlying generators are
   deterministic-but-not-free; a small per-coords cache makes this
   negligible.

**Slice-scope status**: the data layer is functional. The LR Mineral
Scanner module (`system_resource_scan: 1.0`) is the first consumer.
Future scanners (`system_anomaly_scan`, `proto_species_scan`,
`cloak_pierce`) extend the same pattern — add a stat to a sensor module,
query the corresponding `SystemScan` field, render it in the HUD.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from scz.engine.game import Game


@dataclass(frozen=True)
class SystemAnomaly:
    """One non-mineral point of interest in a star system.

    Anomalies are derived from canonical star tags (`RAINBOW_BEING_SEEDED`,
    `MELNORME_PROTO`, primordial flag, etc.) and from future flag-gated
    content the design lands (Furling caches, dormant artifacts, etc.).

    The `kind` field drives the HUD palette + icon when an anomaly-capable
    sensor is installed. The `gating_stat` field (default empty = always
    visible to any anomaly scanner) lets future content require a
    specific sensor capability — e.g. a Mmrnmhrm-derived cognition
    detector for non-organic-substrate anomalies.
    """
    kind: str          # "rainbow" | "melnorme" | "primordial" | "cache" | "proto_species" | "artifact" | ...
    label: str         # short human-readable, e.g. "Rainbow World marker", "Melnorme post"
    gating_stat: str = "system_anomaly_scan"   # the sensor stat key that reveals this
    importance: float = 0.5    # 0.0 (footnote) to 1.0 (slice-critical) — affects HUD ordering


@dataclass(frozen=True)
class SystemScan:
    """Summary of a star system as visible to a sufficiently-equipped sensor.

    All fields are pre-computed; rendering code just picks which fields
    the player's sensor loadout has unlocked. Unequipped fields are
    populated but simply not rendered.
    """
    star: dict[str, Any]            # original star dict (cluster_name, type, color, etc.)
    planet_count: int               # how many planets generate_uqm_system would produce
    total_minerals: dict[str, int]  # COMMON / USEFUL / BIO / ENERGY summed across all planets
    anomalies: tuple[SystemAnomaly, ...] = ()
    # Future fields slot in here as sensors gain new capabilities:
    #   proto_species: str | None
    #   cloaked_signatures: tuple[str, ...]
    #   biological_hazard: float


# Cache keyed by (int(star.x), int(star.y)). Star data + the underlying
# generators are pure functions of these two ints, so memoizing is safe
# and the per-frame HUD lookup becomes O(1).
_SCAN_CACHE: dict[tuple[int, int], SystemScan] = {}


def scan_system(star: dict[str, Any]) -> SystemScan:
    """Return the SystemScan for a star. Cached per (x, y).

    Mirrors what `SystemScene` will find on entry — calls the same
    deterministic generators (`generate_uqm_system`, `generate_deposits`).
    Safe to call every frame from the HUD; the cache makes subsequent
    calls free.
    """
    key = (int(star["x"]), int(star["y"]))
    cached = _SCAN_CACHE.get(key)
    if cached is not None:
        return cached
    scan = _build_scan(star)
    _SCAN_CACHE[key] = scan
    return scan


def _build_scan(star: dict[str, Any]) -> SystemScan:
    """Construct a SystemScan from scratch (no cache lookup). Aggregates the
    deterministic outputs of the existing planet + deposit generators so
    the scan-from-hyperspace numbers match the lander-collected reality.
    """
    # Import lazily to avoid circular dependency at module-load time.
    from scz.planet.deposits import generate_deposits
    from scz.system.uqm_procgen import generate_uqm_system

    star_x = int(star["x"])
    star_y = int(star["y"])

    # Planet list (deterministic via star coords seed)
    planets = generate_uqm_system(star)

    # Per-planet deposits → aggregate totals
    totals = {"COMMON": 0, "USEFUL": 0, "BIO": 0, "ENERGY": 0}
    for p in planets:
        # generate_deposits expects (star_x, star_y, planet_index) tuple
        deposit_id = (star_x, star_y, p.index)
        for d in generate_deposits(deposit_id, p.type):
            if d.type in totals:
                totals[d.type] += d.value

    # Anomalies derived from canonical star tags
    anomalies: list[SystemAnomaly] = []
    defined = star.get("defined_name")
    if defined == "RAINBOW_BEING_SEEDED":
        anomalies.append(SystemAnomaly(
            kind="rainbow",
            label="Rainbow World marker",
            importance=1.0,
        ))
    elif defined == "MELNORME_PROTO":
        anomalies.append(SystemAnomaly(
            kind="melnorme",
            label="Melnorme super-giant post",
            importance=0.8,
        ))
    elif defined and defined.endswith("_PROTO"):
        # Generic proto-species observation site
        anomalies.append(SystemAnomaly(
            kind="proto_species",
            label=f"Proto-species: {defined.removesuffix('_PROTO').lower()}",
            gating_stat="proto_species_scan",
            importance=0.4,
        ))

    if star.get("primordial"):
        anomalies.append(SystemAnomaly(
            kind="primordial",
            label="Primordial biome",
            importance=0.3,
        ))

    # Furling-cache and artifact-site tags (2026-05-18). Per canon —
    # every anomaly kind should be a quest feature; visit discovers it.
    if star.get("furling_cache"):
        anomalies.append(SystemAnomaly(
            kind="cache",
            label="Furling data cache",
            importance=0.5,
        ))
    if star.get("artifact_site"):
        anomalies.append(SystemAnomaly(
            kind="artifact",
            label="Precursor-era artifact",
            importance=0.6,
        ))

    return SystemScan(
        star=star,
        planet_count=len(planets),
        total_minerals=totals,
        anomalies=tuple(anomalies),
    )


def visible_anomalies(scan: SystemScan, game: "Game") -> tuple[SystemAnomaly, ...]:
    """Filter a scan's anomalies by what the player's installed sensor
    capabilities reveal. An anomaly with `gating_stat=X` is visible iff
    `game.effective_stat(X) > 0.0`.

    Helper for HUD rendering; cleaner than duplicating the stat-check
    logic per call site.
    """
    return tuple(
        a for a in scan.anomalies
        if game.effective_stat(a.gating_stat, 0.0) > 0.0
    )


def can_scan_resources(game: "Game") -> bool:
    """True iff the player's loadout includes any module with
    `system_resource_scan` capability. The HUD shows mineral totals only
    when this returns True.
    """
    return game.effective_stat("system_resource_scan", 0.0) > 0.0


def can_scan_anomalies(game: "Game") -> bool:
    """True iff the player's loadout includes any anomaly-capable sensor.
    The HUD shows the anomaly list only when this returns True. Specific
    anomalies may further require a `gating_stat` capability beyond this
    blanket gate (see `visible_anomalies`).
    """
    return game.effective_stat("system_anomaly_scan", 0.0) > 0.0


# ---------------------------------------------------------------------------
# Visit / extraction / discovery helpers — drive the hyperspace map's
# system-dim logic and HUD readout.
# ---------------------------------------------------------------------------

def is_system_visited(game: "Game", star: dict[str, Any]) -> bool:
    """True iff the player has entered this star's system at least once.
    Reads `game.flags['visited_systems']` populated by `star_arrival.
    record_visit`.
    """
    visited = game.flags.get("visited_systems")
    if not isinstance(visited, list):
        return False
    return star.get("cluster_name") in visited


def total_extracted(game: "Game", star: dict[str, Any]) -> dict[str, int]:
    """Return the cumulative per-mineral extraction the player has
    pulled from this system. Keyed by mineral type ('COMMON', 'USEFUL',
    'BIO', 'ENERGY'); missing types report 0.

    Populated by `PlanetSurfaceScene._exit_to_orbit(committed=True)` —
    each successful lander lift-off appends the trip-haul to the
    per-system bucket.
    """
    by_sys = game.flags.get("extracted_by_system")
    if not isinstance(by_sys, dict):
        return {"COMMON": 0, "USEFUL": 0, "BIO": 0, "ENERGY": 0}
    sys_key = f"{int(star['x'])}_{int(star['y'])}"
    raw = by_sys.get(sys_key, {})
    return {t: int(raw.get(t, 0)) for t in ("COMMON", "USEFUL", "BIO", "ENERGY")}


def system_resources_remaining_pct(
    game: "Game", star: dict[str, Any]
) -> float:
    """Return 0.0..1.0 — fraction of the system's mineral yield that
    has NOT yet been extracted by the player. 1.0 = untouched system,
    0.0 = fully drained.

    Computed against the scan's total-minerals figure (the original
    procgen output) so the denominator is stable.
    """
    scan = scan_system(star)
    total = sum(scan.total_minerals.values())
    if total <= 0:
        return 1.0
    extracted_sum = sum(total_extracted(game, star).values())
    remaining = max(0, total - extracted_sum)
    return min(1.0, remaining / total)


def anomaly_is_discovered(
    anomaly: SystemAnomaly, star: dict[str, Any], game: "Game"
) -> bool:
    """True iff the named anomaly has been *seen* by the player — used
    by the hyperspace dim logic to decide whether the system is fully
    explored. Each anomaly kind maps to a flag the rest of the engine
    sets when the player resolves the corresponding content:

    - melnorme       → met_melnorme              (trade dialog opened)
    - rainbow        → rainbow_seen_<star_key>   (per-Rainbow seeded
                                                  flag; future content
                                                  sets this)
    - proto_species  → observed_proto_<species>  (proto-species arrival
                                                  handler in
                                                  star_arrival.py)
    - primordial     → observed_primordial_<sys_key>  (future content)
    - cache/artifact → discovered_<id>           (future content)

    Unmapped kinds return False (treat as undiscovered until content
    wires up the matching flag).
    """
    kind = anomaly.kind
    flags = game.flags
    sys_key = f"{int(star['x'])}_{int(star['y'])}"

    if kind == "melnorme":
        return bool(flags.get("met_melnorme"))
    if kind == "proto_species":
        # Reconstruct species key from the canonical defined_name
        defined = star.get("defined_name") or ""
        species_key = defined.removesuffix("_PROTO").lower()
        return bool(flags.get(f"observed_proto_{species_key}"))
    if kind == "rainbow":
        return bool(flags.get(f"rainbow_seen_{sys_key}"))
    if kind == "primordial":
        return bool(flags.get(f"observed_primordial_{sys_key}"))
    if kind == "cache":
        return bool(flags.get(f"observed_cache_{sys_key}"))
    if kind == "artifact":
        return bool(flags.get(f"observed_artifact_{sys_key}"))
    return False


def system_anomalies_undiscovered_count(
    game: "Game", star: dict[str, Any]
) -> int:
    """Count anomalies in this system that the player has NOT yet
    discovered. Drives the hyperspace dim's "very dim" tier — a system
    is fully explored when no undiscovered anomalies remain.
    """
    scan = scan_system(star)
    undiscovered = 0
    for a in scan.anomalies:
        if not anomaly_is_discovered(a, star, game):
            undiscovered += 1
    return undiscovered


# Resources threshold below which a visited system is considered "drained"
# for the very-dim dim tier. 30% per Aaron's spec.
DRAINED_RESOURCE_PCT: float = 0.30


def system_dim_tier(game: "Game", star: dict[str, Any]) -> int:
    """Return 0/1/2 for the hyperspace-map dim logic:

    - 0: untouched — render at full brightness
    - 1: visited but still has resources or undiscovered anomalies
         — render slightly dimmer
    - 2: visited AND resources below `DRAINED_RESOURCE_PCT` AND no
         undiscovered anomalies remain — render very dim. The system
         has been fully extracted, fully explored, and is no longer
         worth flying back to.
    """
    if not is_system_visited(game, star):
        return 0
    pct = system_resources_remaining_pct(game, star)
    undiscovered = system_anomalies_undiscovered_count(game, star)
    if pct < DRAINED_RESOURCE_PCT and undiscovered == 0:
        return 2
    return 1
