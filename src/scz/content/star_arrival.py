"""Star arrival handlers — what happens when the player enters a named
star system.

The map carries 503 stars; 37 of those have `defined_name` tags from the
SC2 era data (`SHOFIXTI_PROTO`, `MELNORME_PROTO`, `RAINBOW_BEING_SEEDED`,
etc.). This module is the table that maps each tag to an arrival
behavior, called from `SystemScene.on_enter` when `skip_arrival_event`
is False.

**Two layers of behavior**:

1. **Visit recording** — runs on every system entry regardless of
   handler. Appends the system to `game.flags['visited_systems']` (a
   list of `cluster_name` strings, deduped). This drives Bio-Archive
   gating and future content (Tarven's Star-Reader briefings, etc.).

2. **Defined-name handler** — runs once per arrival (suppressed by
   `skip_arrival_event=True` to avoid loops). Looks up the star's
   `defined_name` in `ARRIVAL_HANDLERS`; if a handler is registered,
   calls it with the SystemScene instance. Typical actions:
   - Set an `observed_proto_<species>` flag (idempotent)
   - Award a small BIO cargo bonus on first visit
   - Launch a dialog (e.g. Melnorme at super-giant trade posts)

**Convention**: proto-species arrival handlers set
`observed_proto_<species>` matching the existing Bio-Archive entry's
`flags_gating`. The archive entry then appears in the player's archive
automatically on next docking at Mh-Lai.

**Slice scope**: this module wires the 16 proto-species + 1 Mycon hive
+ 1 Orz rift + Melnorme super-giant entries. RAINBOW_BEING_SEEDED is
left without an arrival handler — the Rainbow World arc is its own
beat (the player needs to visit all 10 with a specific sensor) and
won't be handled inline here.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Callable

if TYPE_CHECKING:
    from scz.system.scene import SystemScene


# Arrival handler signature: takes the active SystemScene and returns
# None. Handlers may inspect / mutate the game (flags, cargo) and may
# also switch scenes (e.g. open a dialog) via scene.game.set_scene.
ArrivalHandler = Callable[["SystemScene"], None]


# Bio-data bonus on first visit to a proto-species observation site.
# Small enough that you'd need to visit many systems to feel rich; big
# enough that the player notices "oh, scanning here paid off."
PROTO_BIO_AWARD: int = 4


def _make_proto_handler(species_key: str) -> ArrivalHandler:
    """Build an arrival handler for a proto-species observation site.

    On first visit, sets `observed_proto_<species_key>` and awards
    `PROTO_BIO_AWARD` BIO cargo. On subsequent visits, the flag is
    already set — the handler is idempotent and the bio award doesn't
    repeat.
    """
    flag = f"observed_proto_{species_key}"

    def handler(scene: "SystemScene") -> None:
        game = scene.game
        if game is None:
            return
        if game.flags.get(flag):
            return   # already observed; no double award
        game.flags[flag] = True
        game.cargo["BIO"] = game.cargo.get("BIO", 0) + PROTO_BIO_AWARD
        # Mark the scene with a "recent pickup" so the HUD can surface
        # the bio award if the SystemScene grows that affordance. For
        # now this just lives in game state for the Bio-Archive gating.
        game.flags[f"recent_proto_visit"] = species_key

    return handler


def _arrive_melnorme(scene: "SystemScene") -> None:
    """Auto-launch the Melnorme dialog at any super-giant system tagged
    MELNORME_PROTO. Two dispatch paths:

    1. **Council Seat** at Alpha Vulpeculae, when the Steward has been
       directed there by a trader (`learned_melnorme_homeworld` flag) —
       opens `melnorme_council(game)` with its dynamic initial_state
       advancing through quest Beats 2-5 based on flags.

    2. **Standard trader** at any other super-giant, or at Alpha
       Vulpeculae before the recruitment track has been opened — opens
       the existing `melnorme()` trader dialog.

    Same back-to-system parent factory pattern (skip_arrival_event=True
    so the player can navigate the system afterward without
    re-triggering the dialog).
    """
    from scz.dialog.characters import melnorme, melnorme_council
    from scz.dialog.scene import DialogScene
    from scz.system.scene import SystemScene as _Sys

    assert scene.game is not None
    game = scene.game
    star = scene.star
    planets = scene.planets

    def _back_to_system() -> "SystemScene":
        return _Sys(star, planets, skip_arrival_event=True)

    # Council Seat dispatch — only at Alpha Vulpeculae, only after the
    # trader has directed the Steward there. Before that, Alpha
    # Vulpeculae behaves like any other super-giant trade-stop.
    is_council_seat = (
        star.get("cluster_name") == "Alpha Vulpeculae"
        and game.flags.get("learned_melnorme_homeworld")
    )
    if is_council_seat:
        scene.game.set_scene(
            DialogScene(
                character=melnorme_council(game),
                parent_factory=_back_to_system,
            )
        )
        return

    scene.game.set_scene(
        DialogScene(character=melnorme(), parent_factory=_back_to_system)
    )


def _arrive_chenjesu(scene: "SystemScene") -> None:
    """Procyon — Chenjesu Crystalline Collective home. Per slice canon
    the Chenjesu are below-threshold sentient survivors (not proto), so
    the arrival uses the existing `met_chenjesu` flag that the
    CHENJESU_COLLECTIVE archive entry gates on, *not* the generic
    `observed_proto_chenjesu` proto-handler convention.

    Two-layer behavior:

    1. **Visit recording + bio award** (always, idempotent): sets
       `met_mhenjesu` and awards `PROTO_BIO_AWARD` BIO.
    2. **Dialog auto-launch** (first visit only): switches to a
       DialogScene with the Chenjesu Collective. The player can
       receive the Resonance Record (key item, parallels Distress
       Beacon and Mmrnmhrm Archive Excerpt), or defer and revisit.

    Subsequent visits after `has_resonance_record` is set: no dialog
    re-launch. The Chenjesu have nothing new to say — they've been
    saying the same thing for millions of years.
    """
    game = scene.game
    if game is None:
        return

    # Data layer (always, idempotent on revisit)
    if not game.flags.get("met_chenjesu"):
        game.flags["met_chenjesu"] = True
        game.cargo["BIO"] = game.cargo.get("BIO", 0) + PROTO_BIO_AWARD

    # Dialog auto-launch — only the first time, and only if the record
    # decision is still open. After the player has either taken the
    # record OR deferred-with-goodbye, the Chenjesu's testimony is
    # complete from their perspective.
    if game.flags.get("has_resonance_record"):
        return

    from scz.dialog.characters import chenjesu_collective
    from scz.dialog.scene import DialogScene
    from scz.system.scene import SystemScene as _Sys

    star = scene.star
    planets = scene.planets

    def _back_to_system() -> "SystemScene":
        return _Sys(star, planets, skip_arrival_event=True)

    game.set_scene(
        DialogScene(
            character=chenjesu_collective(),
            parent_factory=_back_to_system,
        )
    )


def _arrive_mycon_hive(scene: "SystemScene") -> None:
    """The Mycon biot home hive — Epsilon Scorpii. First arrival sets
    `met_mycon` (unlocks the Mycon biot Bio-Archive entry) and stages
    the Mycon Whisper plot flag for the next dialog beat. The Deep
    Child dialog itself is a downstream beat (not yet wired); for now
    this handler just opens the data layer.
    """
    game = scene.game
    if game is None:
        return
    if game.flags.get("met_mycon"):
        return
    game.flags["met_mycon"] = True
    game.flags["mycon_whisper_observable"] = True
    game.cargo["BIO"] = game.cargo.get("BIO", 0) + PROTO_BIO_AWARD


def _arrive_dnyarri_primitive(scene: "SystemScene") -> None:
    """Beta Orionis — proto-Dnyarri psionic precursor observation site.

    Bespoke handler (replaces the generic proto-species pattern). Three
    behaviors layered:

    1. **Visit recording** (always): set `observed_proto_dnyarri`,
       award PROTO_BIO_AWARD on first visit. Same data-layer payoff
       as any proto handler.
    2. **Dialog auto-launch** (first visit only): switches to a
       DialogScene with Survey Commander Vesh Vasa-Lon, who briefs
       the Steward on the psionic precursor signal and asks for a
       recommendation. The dialog's side-effects set
       `dnyarri_recommendation` to one of cleanse/observe/deferred
       and `met_dnyarri_survey` to True.
    3. **Subsequent visits** (after `met_dnyarri_survey` is set):
       no dialog, just data-layer behavior. The detail stays at Beta
       Orionis; the Steward is welcome to return but Vesh is busy
       observing.

    Per design doc + slice canon, this is the only proto-species site
    where the player is asked for a Council recommendation in the
    slice. The other 13 proto-species are observed-and-archived, no
    decision required. The Dnyarri are the exception because the
    Cleanser-faction has actively petitioned.
    """
    game = scene.game
    if game is None:
        return

    # Data-layer (always, idempotent)
    if not game.flags.get("observed_proto_dnyarri"):
        game.flags["observed_proto_dnyarri"] = True
        game.cargo["BIO"] = game.cargo.get("BIO", 0) + PROTO_BIO_AWARD

    # Dialog auto-launch (first time only — the survey commander has
    # nothing new to say on revisit; the player can re-engage via the
    # Council UI when that lands)
    if game.flags.get("met_dnyarri_survey"):
        return

    from scz.dialog.characters import dnyarri_survey_commander
    from scz.dialog.scene import DialogScene
    from scz.system.scene import SystemScene as _Sys

    star = scene.star
    planets = scene.planets

    def _back_to_system() -> "SystemScene":
        # skip_arrival_event=True so coming back from dialog doesn't
        # re-launch this handler. The proto-data flag was already set
        # above (idempotent on revisit anyway).
        return _Sys(star, planets, skip_arrival_event=True)

    game.set_scene(
        DialogScene(
            character=dnyarri_survey_commander(),
            parent_factory=_back_to_system,
        )
    )


def _arrive_ossuary(scene: "SystemScene") -> None:
    """Gamma Trianguli / Ossuary — Mmrnmhrm Sentinels' homeworld.

    Two-layer behavior:

    1. **Visit recording + bio award** (always, idempotent on revisit):
       sets `met_mmrnmhrm` and awards `PROTO_BIO_AWARD` BIO. The
       MMRNMHRM_SENTINEL archive entry unlocks immediately on visit;
       MMRNMHRM_ARCHIVE_EXCERPT unlocks only after the dialog's
       "accept the excerpt" side-effect fires.

    2. **Dialog auto-launch** (first visit only): switches to a
       DialogScene with Sentinel-Aux Theta-Four. The player can:
       - Accept the Archive Excerpt (key item, parallels Distress Beacon)
       - Grant / refuse / cap the Mmrnmhrm's cognition-upgrade request
       - Browse lore about the First-Makers and the Others' silence

    The Mmrnmhrm cannot migrate (substrate-bound to Ossuary's
    iron-rich crust) but formally support the Migration. They are not
    hostile, never threatened by Furling visitors; the dialog flow is
    cooperative.

    Subsequent visits: no dialog re-launch. The Sentinel has nothing
    new to say on revisit. The Council UI (future) re-engages the
    cognition decision if it was deferred.
    """
    game = scene.game
    if game is None:
        return

    # Data layer (always idempotent)
    if not game.flags.get("met_mmrnmhrm"):
        game.flags["met_mmrnmhrm"] = True
        game.cargo["BIO"] = game.cargo.get("BIO", 0) + PROTO_BIO_AWARD
        # Schematic gift (audit 2026-05-18): Sentinel-Aux Theta-Four
        # presents the Mmrnmhrm Reinforced Plating schematic personally
        # on first visit. Canonical: *the First-Makers designed this
        # plating; it did not save them, but the design is still good.*
        if not hasattr(game, "schematics") or game.schematics is None:
            game.schematics = set()
        game.schematics.add("schematic_mmrnmhrm_reinforced_plating")

    # Dialog auto-launch — only the first time, and only if the
    # cognition decision is still open. After the player has made the
    # call (grant/refuse/cap), the Sentinel's archive has nothing new.
    if game.flags.get("mmrnmhrm_cognition"):
        return

    from scz.dialog.characters import mmrnmhrm_sentinel
    from scz.dialog.scene import DialogScene
    from scz.system.scene import SystemScene as _Sys

    star = scene.star
    planets = scene.planets

    def _back_to_system() -> "SystemScene":
        return _Sys(star, planets, skip_arrival_event=True)

    game.set_scene(
        DialogScene(
            character=mmrnmhrm_sentinel(),
            parent_factory=_back_to_system,
        )
    )


def _arrive_utwig_prime(scene: "SystemScene") -> None:
    """Beta Aquarii (UTWIG_PROTO) — the Utwig homeworld in the
    pre-doctrine transition window.

    Overrides the generic `_make_proto_handler("utwig")` because the
    Utwig are *not* a generic proto-species observation; they're a
    real first-contact + Doctrine decision encounter. Per canon
    (`references/lore/species-sheets.md §11`), the Utwig have *just*
    become sentient and are about to undertake the **Veils Falling**
    — the formal mass-adoption of mask-and-ceremony culture as
    cognitive-dampening doctrine. The Steward arrives in the days
    before the ceremony.

    Two-layer behavior:

    1. **Visit recording + bio award** (always, idempotent): sets
       `met_utwig`, awards `PROTO_BIO_AWARD` BIO, and ALSO sets the
       legacy `observed_proto_utwig` flag for any existing content
       that gates on the generic proto convention.
    2. **Dialog auto-launch** (first visit only, while contribution
       decision is open): switches to a DialogScene with Veiled-In-
       Three-Days. The Steward decides whether to witness silently,
       advocate evacuation for the unmasked young, sabotage the
       ceremony under Cleanser pressure, or defer.

    Subsequent visits: no dialog re-launch once `utwig_contribution`
    is set. The Doctrine progresses on its own canonical schedule.
    """
    game = scene.game
    if game is None:
        return

    # Data layer (always, idempotent). Maintain the legacy proto-flag
    # for any existing content that reads it (Bio-Archive entry,
    # cluster status, etc).
    if not game.flags.get("met_utwig"):
        game.flags["met_utwig"] = True
        game.flags["observed_proto_utwig"] = True
        game.cargo["BIO"] = game.cargo.get("BIO", 0) + PROTO_BIO_AWARD

    if game.flags.get("utwig_contribution"):
        return

    from scz.dialog.characters import utwig_veiled_in_three_days
    from scz.dialog.scene import DialogScene
    from scz.system.scene import SystemScene as _Sys

    star = scene.star
    planets = scene.planets

    def _back_to_system() -> "SystemScene":
        return _Sys(star, planets, skip_arrival_event=True)

    game.set_scene(
        DialogScene(
            character=utwig_veiled_in_three_days(),
            parent_factory=_back_to_system,
        )
    )


def _arrive_whirligig(scene: "SystemScene") -> None:
    """Beta Crucis / Whirligig — Lemmkin homeworld.

    The Lemmkin are *not* a generic proto-species. They have chosen
    no survival strategy in the face of the Others, and instead plan
    to spend the remaining time *learning everything they can*. The
    encounter is a real first-contact + Doctrine decision moment.

    Two-layer behavior:

    1. **Visit recording + bio award**: sets `met_lemmkin`, awards
       `PROTO_BIO_AWARD` BIO on first visit.
    2. **Dialog auto-launch** (first visit only, while contribution
       decision is open): switches to Brisk-Ever-Onward dialog.

    Subsequent visits: no dialog re-launch once `lemmkin_contribution`
    is set. The troupe is canonically delighted to receive return
    visits but the in-game contribution decision is one-shot.
    """
    game = scene.game
    if game is None:
        return

    if not game.flags.get("met_lemmkin"):
        game.flags["met_lemmkin"] = True
        game.cargo["BIO"] = game.cargo.get("BIO", 0) + PROTO_BIO_AWARD

    if game.flags.get("lemmkin_contribution"):
        return

    from scz.dialog.characters import lemmkin_brisk_ever_onward
    from scz.dialog.scene import DialogScene
    from scz.system.scene import SystemScene as _Sys

    star = scene.star
    planets = scene.planets

    def _back_to_system() -> "SystemScene":
        return _Sys(star, planets, skip_arrival_event=True)

    game.set_scene(
        DialogScene(
            character=lemmkin_brisk_ever_onward(),
            parent_factory=_back_to_system,
        )
    )


def _arrive_burvix_caster(scene: "SystemScene") -> None:
    """Burvix Caster — the Burvixese Be-Loud doctrine's flagship
    installation system. Delta Cassiopeiae, yellow dwarf, mid-cluster.

    Two-layer behavior:

    1. **Visit recording + bio award** (always, idempotent): sets
       `met_burvixese` and awards `PROTO_BIO_AWARD` BIO on first visit.
    2. **Dialog auto-launch** (first visit only, while contribution
       decision is open): switches to a DialogScene with Foreman
       Vesh-Kar Twel-Pin. The Steward makes their contribution choice
       (witness / advocate-evacuation / sabotage-cleanser / defer);
       the choice is recorded in `burvixese_contribution` for the
       downstream Caster-activation cinematic (deferred — wires up
       with the Migration Phase-4 / Final Conflict beat).

    Subsequent visits: no dialog re-launch once
    `burvixese_contribution` is set.
    """
    game = scene.game
    if game is None:
        return

    # Data layer (always, idempotent)
    if not game.flags.get("met_burvixese"):
        game.flags["met_burvixese"] = True
        game.cargo["BIO"] = game.cargo.get("BIO", 0) + PROTO_BIO_AWARD

    if game.flags.get("burvixese_contribution"):
        return

    from scz.dialog.characters import burvixese_foreman
    from scz.dialog.scene import DialogScene
    from scz.system.scene import SystemScene as _Sys

    star = scene.star
    planets = scene.planets

    def _back_to_system() -> "SystemScene":
        return _Sys(star, planets, skip_arrival_event=True)

    game.set_scene(
        DialogScene(
            character=burvixese_foreman(),
            parent_factory=_back_to_system,
        )
    )


def _arrive_taalos_stone(scene: "SystemScene") -> None:
    """Taalo's Stone — the Taalo Mountain-Range Sentience's homeworld.

    Two-layer behavior:

    1. **Visit recording + bio award** (always, idempotent): sets
       `met_taalo` and awards `PROTO_BIO_AWARD` BIO on first visit.
       The Taalo are silicon-substrate but their lattice cognition
       counts as readable biological information from a Furling sensor.
    2. **Dialog auto-launch** (first visit only): switches to a
       DialogScene with We-Who-Watch-The-Northwest-Bench. The Steward
       makes their contribution-level choice (full / partial / decline
       / cleanser-betrayal); the choice is recorded in
       `taalo_contribution` for the downstream Shield-failure
       cinematic (deferred — wires up with the Migration Phase-4 /
       Final Conflict beat).

    Subsequent visits: no dialog re-launch once `taalo_contribution`
    is set. Per the MVP compression, one decisive visit locks the
    branch; the canonical "repeated visits across five thousand years"
    cadence is deferred to Phase 5 polish (depends on Migration
    timetable wiring).
    """
    game = scene.game
    if game is None:
        return

    # Data layer (always, idempotent)
    if not game.flags.get("met_taalo"):
        game.flags["met_taalo"] = True
        game.cargo["BIO"] = game.cargo.get("BIO", 0) + PROTO_BIO_AWARD

    # Dialog auto-launch — only the first time, and only until the
    # contribution choice is locked.
    if game.flags.get("taalo_contribution"):
        return

    from scz.dialog.characters import taalo_we_who_watch
    from scz.dialog.scene import DialogScene
    from scz.system.scene import SystemScene as _Sys

    star = scene.star
    planets = scene.planets

    def _back_to_system() -> "SystemScene":
        return _Sys(star, planets, skip_arrival_event=True)

    game.set_scene(
        DialogScene(
            character=taalo_we_who_watch(),
            parent_factory=_back_to_system,
        )
    )


def _arrive_orz_rift(scene: "SystemScene") -> None:
    """The Orz rift — a tear in dimensional substrate near Gamma
    Vulpeculae. First arrival sets `saw_orz_rift` (unlocks the
    OTHERS_RIFT_SIGHTING archive entry; the rift is the slice's
    closest first-hand glimpse of the Others' substrate).

    No bio-data award here — the rift isn't a life-form. The data
    payoff is the archive entry itself.

    SCHEMATIC GRANT (audit 2026-05-18): the Persuader-faction wreck
    near Gamma Vulpeculae is the canonical source of
    `schematic_dimensional_armor` per
    `references/lore/economy-and-trade-loops.md`. Half the wreck is
    inside the rift's dimensional bleed; the schematic was on the
    outside half, intact. Granted here on first visit.
    """
    game = scene.game
    if game is None:
        return
    if game.flags.get("saw_orz_rift"):
        return
    game.flags["saw_orz_rift"] = True
    # Dimensional Armor schematic — Persuader-wreck salvage.
    if not hasattr(game, "schematics") or game.schematics is None:
        game.schematics = set()
    game.schematics.add("schematic_dimensional_armor")


def _arrive_rainbow_world(scene: "SystemScene") -> None:
    """First visit to a Rainbow World — each of the 10 sets its own
    `rainbow_seen_<sys_key>` flag (consumed by
    `cluster_status.rainbow_worlds_discovered`).

    On the FIRST Rainbow World visited (any of the 10), the Steward
    is granted the Rainbow Resonator module — Mh-Lai canonically
    issues the resonator on the first observation report, since the
    slice's Rainbow Worlds quest is "find one, then chase the
    arrow." Subsequent Rainbow World visits set their own seen-flag
    but don't re-grant the module.

    Bio award on first visit (canonical: Rainbow Worlds are
    biologically distinctive — algae mats, iridescent flora, etc.).
    """
    game = scene.game
    if game is None:
        return
    star = scene.star
    sys_key = f"{int(star['x'])}_{int(star['y'])}"
    seen_flag = f"rainbow_seen_{sys_key}"
    if game.flags.get(seen_flag):
        return
    game.flags[seen_flag] = True
    game.cargo["BIO"] = game.cargo.get("BIO", 0) + PROTO_BIO_AWARD * 2
    # First-Rainbow-World gift — grant the Resonator.
    if not game.flags.get("has_rainbow_resonator"):
        game.flags["has_rainbow_resonator"] = True
        game.uninstalled_modules["rainbow_resonator"] = (
            game.uninstalled_modules.get("rainbow_resonator", 0) + 1
        )


# ---------------------------------------------------------------------------
# Registry
# ---------------------------------------------------------------------------
# Order matches the proto-species memory + universe data tags. Future
# special-case handlers (per-species bespoke quests) layer on top by
# overwriting the entry — the registry is a plain dict and overrides
# are explicit.
ARRIVAL_HANDLERS: dict[str, ArrivalHandler] = {
    # Super-giant trade posts (9 stars)
    "MELNORME_PROTO": _arrive_melnorme,

    # Proto-species observation sites — one per SC2 species
    "SOL_PROTO":      _make_proto_handler("human"),
    "SHOFIXTI_PROTO": _make_proto_handler("shofixti"),
    "YEHAT_PROTO":    _make_proto_handler("yehat"),
    "PKUNK_PROTO":    _make_proto_handler("pkunk"),
    "VUX_PROTO":      _make_proto_handler("vux"),
    "CHENJESU_PROTO": _arrive_chenjesu,
    "DRUUGE_PROTO":   _make_proto_handler("druuge"),
    "ILWRATH_PROTO":  _make_proto_handler("ilwrath"),
    "SPATHI_PROTO":   _make_proto_handler("spathi"),
    "SYREEN_PROTO":   _make_proto_handler("syreen"),
    "ZOQFOT_PROTO":   _make_proto_handler("zoqfot"),
    "THRADD_PROTO":   _make_proto_handler("thraddash"),
    "UTWIG_PROTO":    _arrive_utwig_prime,
    "SUPOX_PROTO":    _make_proto_handler("supox"),
    "DNYARRI_PRIMITIVE": _arrive_dnyarri_primitive,

    # Bespoke handlers
    "MYCON_BIOT_HIVE":   _arrive_mycon_hive,
    "ORZ_RIFT":          _arrive_orz_rift,
    "MMRNMHRM_OSSUARY":  _arrive_ossuary,
    "TAALOS_STONE":      _arrive_taalos_stone,
    "BURVIX_CASTER":     _arrive_burvix_caster,
    "LEMMKIN_WHIRLIGIG": _arrive_whirligig,

    # Rainbow Worlds — first visit grants the Rainbow Resonator
    # (audit 2026-05-18: previously orphaned, now wired). Per-star
    # rainbow_seen_<sys_key> flag also set; consumed by
    # `cluster_status.rainbow_worlds_discovered`.
    "RAINBOW_BEING_SEEDED": _arrive_rainbow_world,
}


def record_visit(scene: "SystemScene") -> None:
    """Append the entered system's cluster_name to game.flags['visited_systems']
    (deduped). Runs unconditionally on every SystemScene entry, not gated
    by skip_arrival_event — re-entry still counts as a visit moment for
    the Star-Reader briefings layer that consumes this list.

    AUTO-RECRUIT (audit 2026-05-18): the Star-Reader's Routes
    recruitment quest (Tarven Olwen-Sa) canonically fires once the
    Steward has visited 3+ systems. When the visited-list crosses
    the threshold for the first time, auto-recruit Tarven so the
    `crew_navigator` module is reachable in real gameplay.
    """
    game = scene.game
    if game is None:
        return
    name = scene.star.get("cluster_name")
    if not name:
        return
    visited = game.flags.get("visited_systems")
    if not isinstance(visited, list):
        visited = []
        game.flags["visited_systems"] = visited
    if name not in visited:
        visited.append(name)
    # Auto-recruit Tarven at 3+ visits (one-shot).
    if len(visited) >= 3 and not game.flags.get("recruited_navigator"):
        from scz.dialog.characters import _recruit_tarven
        _recruit_tarven(game)

    # Cross-cutting anomaly discovery (2026-05-18) — runs on every
    # system entry, separate from the defined_name dispatch in
    # `fire_arrival`. Captures per-property anomaly observations that
    # any system might have (primordial biome flag, cache tag, etc.)
    # so every anomaly kind that the scanner surfaces also has a
    # quest-style discovery moment with flag + BIO award + Archive
    # entry trigger. Per Aaron canon: "all anomalies on planets and
    # in space should be considered quest features."
    _observe_anomalies(game, scene.star)


# Bio-data award sizes per anomaly kind. Smaller than the proto-species
# bonus since primordial / cache / artifact observations are quieter
# discoveries; the cumulative reward across many visits is the point.
_PRIMORDIAL_BIO_AWARD: int = 3
_CACHE_BIO_AWARD: int = 5
_ARTIFACT_BIO_AWARD: int = 6


def _observe_anomalies(game, star) -> None:
    """Capture per-property anomaly observations on system entry.

    Each anomaly kind that the scanner can surface (per `SystemAnomaly`
    in `system_scan.py`) gets a matching discovery flag + BIO award on
    first visit. Idempotent — re-visits don't re-award.

    Current kinds wired:
      - primordial : star.get("primordial") is True
      - cache      : star.get("furling_cache") is True (canonical tag
                     for systems holding a Furling-era data cache)
      - artifact   : star.get("artifact_site") is True (canonical tag
                     for systems with a recoverable Precursor artifact)

    Each first-visit fires the matching `observed_<kind>_<sys_key>`
    flag, which `system_scan.anomaly_is_discovered` already reads to
    drive the hyperspace dim-tier and Bio-Archive gating logic.
    """
    sys_key = f"{int(star['x'])}_{int(star['y'])}"

    if star.get("primordial"):
        flag = f"observed_primordial_{sys_key}"
        if not game.flags.get(flag):
            game.flags[flag] = True
            game.cargo["BIO"] = game.cargo.get("BIO", 0) + _PRIMORDIAL_BIO_AWARD
            game.flags["recent_primordial_visit"] = sys_key

    if star.get("furling_cache"):
        flag = f"observed_cache_{sys_key}"
        if not game.flags.get(flag):
            game.flags[flag] = True
            game.cargo["BIO"] = game.cargo.get("BIO", 0) + _CACHE_BIO_AWARD
            game.flags["recent_cache_visit"] = sys_key

    if star.get("artifact_site"):
        flag = f"observed_artifact_{sys_key}"
        if not game.flags.get(flag):
            game.flags[flag] = True
            game.cargo["BIO"] = game.cargo.get("BIO", 0) + _ARTIFACT_BIO_AWARD
            game.flags["recent_artifact_visit"] = sys_key


def fire_arrival(scene: "SystemScene") -> None:
    """Look up the star's `defined_name` in ARRIVAL_HANDLERS and run the
    handler if registered. No-op for stars without a defined_name or
    without a registered handler.

    Call site: `SystemScene.on_enter` (after `record_visit`), only when
    `skip_arrival_event` is False.
    """
    defined = scene.star.get("defined_name")
    if not defined:
        return
    handler = ARRIVAL_HANDLERS.get(defined)
    if handler is None:
        return
    handler(scene)
