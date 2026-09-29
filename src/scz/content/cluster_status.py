"""Cluster Status Board data layer — slice-wide win-condition tracking.

Each sentient species in the slice has a canonical terminal-status flag
(set by the species' resolution path — dialog choice, Council ruling,
or arrival handler). This module:

1. Defines the canonical status vocabulary (`StatusKind`).
2. Lists every species the Cluster Status Board tracks.
3. Resolves each species' current status by reading the relevant
   flag, falling back to a sensible default (Unknown / Pending /
   Pre-sentient).
4. Aggregates slice-wide progress: % species resolved, Rainbow Worlds
   discovered, Bio-Archive entries unlocked, Migration deadline.

Win condition (per `references/lore/win-condition-and-methods.md`):
every sentient species reaches a terminal status (Migrated / Cloaked /
Hidden / Pre-sentient / Eliminated) AND the Rainbow Worlds arc is
complete. The Status Board surfaces all of this in one place so the
player can see at a glance what's left to do.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Callable

if TYPE_CHECKING:
    from scz.engine.game import Game


# Canonical terminal-status vocabulary. The order matters for the
# Status Board's grouping logic — terminal statuses (the player has
# made a final call) come first; intermediate / unresolved statuses
# come last.
STATUS_ORDER: tuple[str, ...] = (
    "Migrated",
    "Cloaked",
    "Hidden",
    "Pre-sentient",
    "Eliminated",
    "Pending",
    "Unknown",
)

# Color per status — used by the Status Board renderer to color-code
# each species row. Roughly: cool green for safe migrations, blue for
# cloaks, amber for pre-sentient, slate for hidden, red for eliminated,
# muted for unknown/pending.
STATUS_COLORS: dict[str, tuple[int, int, int]] = {
    "Migrated":     (140, 220, 160),    # warm green
    "Cloaked":      (130, 190, 230),    # cool blue
    "Hidden":       (180, 170, 220),    # soft violet
    "Pre-sentient": (220, 200, 130),    # amber
    "Eliminated":   (220, 110, 110),    # red
    "Pending":      (200, 200, 170),    # warm grey
    "Unknown":      (110, 120, 140),    # muted slate
}


@dataclass(frozen=True)
class SpeciesEntry:
    """One species the Cluster Status Board tracks."""
    id: str
    name: str
    short_blurb: str           # one-line situational summary
    # Predicate: returns the species' current terminal-status string by
    # reading game.flags. Each species has its own logic (multiple
    # flags often map to one status).
    resolver: Callable[["Game"], str]


# ---------------------------------------------------------------------------
# Per-species status resolvers
# ---------------------------------------------------------------------------
#
# Each resolver returns one of STATUS_ORDER. The pattern: first check
# for a directly-set terminal flag (set by Council or quest commit);
# fall back to intermediate flags (met / observed) for Pending; else
# Unknown.

def _slylandro_status(g: "Game") -> str:
    f = g.flags
    explicit = f.get("slylandro_terminal_status")
    if explicit in STATUS_ORDER:
        return explicit
    if f.get("slylandro_migrated"):
        return "Migrated"
    if f.get("slylandro_cloaked"):
        return "Cloaked"
    if f.get("met_slylandro"):
        return "Pending"
    return "Unknown"


def _arilou_status(g: "Game") -> str:
    f = g.flags
    # Arilou are voluntary exiles in Quasi-Space — canonically Hidden
    # once the Sage gift is granted. No alternate path in the slice.
    if f.get("arilou_terminal_status") in STATUS_ORDER:
        return f.get("arilou_terminal_status")
    if f.get("has_quasispace_portal") or f.get("talked_to_arilou_sage"):
        return "Hidden"
    return "Unknown"


def _androsynth_status(g: "Game") -> str:
    f = g.flags
    # Androsynth canonically migrate with the Steward. If they died
    # (rare decline path), Eliminated.
    if f.get("androsynth_terminal_status") in STATUS_ORDER:
        return f.get("androsynth_terminal_status")
    if f.get("androsynth_aboard"):
        return "Migrated"
    if f.get("met_androsynth"):
        # Met but declined to aboard them — Migrated by their own means
        # (the Beacon is still recovered).
        return "Migrated"
    return "Unknown"


def _mycon_status(g: "Game") -> str:
    f = g.flags
    explicit = f.get("mycon_terminal_status")
    if explicit in STATUS_ORDER:
        return explicit
    if f.get("met_mycon"):
        return "Pending"
    return "Unknown"


def _proto_uq_status(g: "Game") -> str:
    f = g.flags
    explicit = f.get("proto_uq_terminal_status")
    if explicit in STATUS_ORDER:
        return explicit
    if f.get("observed_proto_uq"):
        return "Pending"
    return "Unknown"


def _proto_qa_status(g: "Game") -> str:
    f = g.flags
    explicit = f.get("proto_qa_terminal_status")
    if explicit in STATUS_ORDER:
        return explicit
    if f.get("observed_proto_qa"):
        return "Pending"
    return "Unknown"


def _mmrnmhrm_status(g: "Game") -> str:
    f = g.flags
    if f.get("mmrnmhrm_terminal_status") in STATUS_ORDER:
        return f.get("mmrnmhrm_terminal_status")
    if f.get("met_mmrnmhrm"):
        # Below-threshold-by-biology — canonically Hidden in the slice
        # (the patches we install don't change their detection profile).
        return "Hidden"
    return "Unknown"


def _chenjesu_status(g: "Game") -> str:
    f = g.flags
    if f.get("chenjesu_terminal_status") in STATUS_ORDER:
        return f.get("chenjesu_terminal_status")
    if f.get("met_chenjesu"):
        # Rooted, below-threshold-by-substrate — canonically Hidden.
        return "Hidden"
    return "Unknown"


def _melnorme_status(g: "Game") -> str:
    f = g.flags
    explicit = f.get("melnorme_terminal_status")
    if explicit in STATUS_ORDER:
        return explicit
    if f.get("melnorme_committed"):
        return "Migrated"
    if f.get("met_melnorme") or f.get("met_melnorme_council"):
        return "Pending"
    return "Unknown"


def _proto_human_status(g: "Game") -> str:
    f = g.flags
    if f.get("proto_human_terminal_status") in STATUS_ORDER:
        return f.get("proto_human_terminal_status")
    if f.get("observed_proto_human"):
        # Per the canonical PROTO_HUMAN archive entry: we leave them
        # alone; they remain on their own developmental schedule.
        return "Pre-sentient"
    return "Unknown"


def _proto_dnyarri_status(g: "Game") -> str:
    f = g.flags
    # Direct terminal-status flag wins if set
    if f.get("proto_dnyarri_terminal_status") in STATUS_ORDER:
        return f.get("proto_dnyarri_terminal_status")
    rec = f.get("dnyarri_recommendation")
    if rec == "cleanse":
        return "Eliminated"
    if rec == "observe":
        return "Pre-sentient"
    if rec == "deferred" or f.get("met_dnyarri_survey"):
        return "Pending"
    if f.get("observed_proto_dnyarri"):
        return "Pending"
    return "Unknown"


def _make_generic_proto_resolver(species_key: str) -> Callable[["Game"], str]:
    """Build a resolver for an observe-only proto-species. Status is
    Pre-sentient once observed, Unknown otherwise. Used for the 12+
    proto-species where the canonical Furling answer is "leave alone."
    """
    flag = f"observed_proto_{species_key}"

    def resolver(g: "Game") -> str:
        if g.flags.get(flag):
            return "Pre-sentient"
        return "Unknown"

    return resolver


# ---------------------------------------------------------------------------
# Species registry — the order here drives the Status Board's display order.
# Sentient species first (the ones requiring decisions), then proto-species.
# ---------------------------------------------------------------------------
SPECIES: tuple[SpeciesEntry, ...] = (
    SpeciesEntry(
        id="slylandro",
        name="Slylandro Observers",
        short_blurb="Gas-current sentients · cloak-or-evacuate",
        resolver=_slylandro_status,
    ),
    SpeciesEntry(
        id="arilou",
        name="Arilou Sage",
        short_blurb="Quasi-Space exiles · voluntary withdrawal",
        resolver=_arilou_status,
    ),
    SpeciesEntry(
        id="androsynth",
        name="Androsynth Refugees",
        short_blurb="Time-displaced clone-humans · Migration cargo",
        resolver=_androsynth_status,
    ),
    SpeciesEntry(
        id="mycon",
        name="Mycon Biots",
        short_blurb="Deep Child whisper · awakening sentience",
        resolver=_mycon_status,
    ),
    SpeciesEntry(
        id="proto_uq",
        name="Proto-Ur-Quan",
        short_blurb="Uplift dilemma · molluscoid dominators",
        resolver=_proto_uq_status,
    ),
    SpeciesEntry(
        id="proto_qa",
        name="Proto-Qor-Ah",
        short_blurb="Uplift dilemma · molluscoid purifiers",
        resolver=_proto_qa_status,
    ),
    SpeciesEntry(
        id="mmrnmhrm",
        name="Mmrnmhrm Sentinels",
        short_blurb="Self-modifying robots · invisible to Others",
        resolver=_mmrnmhrm_status,
    ),
    SpeciesEntry(
        id="chenjesu",
        name="Chenjesu Collective",
        short_blurb="Rooted crystalline · prior-cycle witnesses",
        resolver=_chenjesu_status,
    ),
    SpeciesEntry(
        id="melnorme",
        name="Melnorme Trade-Network",
        short_blurb="Super-giant traders · Trader's Manifest quest",
        resolver=_melnorme_status,
    ),
    SpeciesEntry(
        id="proto_human",
        name="Proto-Humans (Sol III)",
        short_blurb="Bipedal mammals · they bury their dead",
        resolver=_proto_human_status,
    ),
    SpeciesEntry(
        id="proto_dnyarri",
        name="Proto-Dnyarri",
        short_blurb="Psionic precursor signal · Beta Orionis briefing",
        resolver=_proto_dnyarri_status,
    ),
    # Observe-only proto-species. Status = Pre-sentient once visited.
    SpeciesEntry(
        id="proto_shofixti",
        name="Proto-Shofixti",
        short_blurb="Hooting highland bipeds · below threshold",
        resolver=_make_generic_proto_resolver("shofixti"),
    ),
    SpeciesEntry(
        id="proto_yehat",
        name="Proto-Yehat",
        short_blurb="Avian pack-hunters · display-syntax emerging",
        resolver=_make_generic_proto_resolver("yehat"),
    ),
    SpeciesEntry(
        id="proto_pkunk",
        name="Proto-Pkunk",
        short_blurb="Migratory flocking scavengers · pre-mysticism",
        resolver=_make_generic_proto_resolver("pkunk"),
    ),
    SpeciesEntry(
        id="proto_vux",
        name="Proto-VUX",
        short_blurb="Aquatic cephalopods · proto-aesthetic discrimination",
        resolver=_make_generic_proto_resolver("vux"),
    ),
    SpeciesEntry(
        id="proto_spathi",
        name="Proto-Spathi",
        short_blurb="Burrowing gastropods · metabolic fear-response",
        resolver=_make_generic_proto_resolver("spathi"),
    ),
    SpeciesEntry(
        id="proto_syreen",
        name="Proto-Syreen",
        short_blurb="Mammalian matriarchies · song-cognition",
        resolver=_make_generic_proto_resolver("syreen"),
    ),
    SpeciesEntry(
        id="proto_zoqfot",
        name="Proto-Zoq-Fot",
        short_blurb="Two-species symbiosis · third partner not yet joined",
        resolver=_make_generic_proto_resolver("zoqfot"),
    ),
    SpeciesEntry(
        id="proto_thraddash",
        name="Proto-Thraddash",
        short_blurb="Cyclic self-destruction · pre-Cultures",
        resolver=_make_generic_proto_resolver("thraddash"),
    ),
    SpeciesEntry(
        id="proto_utwig",
        name="Proto-Utwig",
        short_blurb="Just-sentient · the Veils Falling devolution",
        resolver=_make_generic_proto_resolver("utwig"),
    ),
    SpeciesEntry(
        id="proto_supox",
        name="Proto-Supox",
        short_blurb="Plant-derived photosynthetic cognition",
        resolver=_make_generic_proto_resolver("supox"),
    ),
    SpeciesEntry(
        id="proto_druuge",
        name="Proto-Druuge",
        short_blurb="Subterranean hoarders · pre-trade",
        resolver=_make_generic_proto_resolver("druuge"),
    ),
    SpeciesEntry(
        id="proto_ilwrath",
        name="Proto-Ilwrath",
        short_blurb="Arachnoid pack predators · ritualized killings",
        resolver=_make_generic_proto_resolver("ilwrath"),
    ),
)


def species_status(game: "Game", species_id: str) -> str:
    """Look up a species' current terminal status by id."""
    for sp in SPECIES:
        if sp.id == species_id:
            return sp.resolver(game)
    return "Unknown"


# Statuses that count as "resolved" for the win-condition tracker.
# Pending and Unknown are NOT resolved.
RESOLVED_STATUSES: frozenset[str] = frozenset({
    "Migrated", "Cloaked", "Hidden", "Pre-sentient", "Eliminated",
})


def resolved_count(game: "Game") -> tuple[int, int]:
    """Return (resolved, total) counts — species that have a terminal
    status vs. species the Status Board tracks. Drives the
    progress-bar fill in the Status Board UI.
    """
    total = len(SPECIES)
    resolved = sum(
        1 for sp in SPECIES if sp.resolver(game) in RESOLVED_STATUSES
    )
    return resolved, total


def rainbow_worlds_discovered(game: "Game") -> int:
    """How many of the 10 Rainbow Worlds have been seeded / visited.
    Read from per-world flags (each Rainbow World sets
    `rainbow_seen_<sx>_<sy>` when visited; future content sets the
    canonical seeded-rainbow flags).
    """
    count = 0
    for k in game.flags:
        if isinstance(k, str) and k.startswith("rainbow_seen_"):
            if game.flags[k]:
                count += 1
    return count


def archive_entry_count(game: "Game") -> tuple[int, int]:
    """Return (unlocked, total) Bio-Archive entries — slice progress
    indicator. Reads via archive_entries.visible_entries.
    """
    from scz.content.archive_entries import (
        ARCHIVE_ENTRIES, visible_entries,
    )
    vis = visible_entries(game)
    unlocked = sum(len(v) for v in vis.values())
    return unlocked, len(ARCHIVE_ENTRIES)
