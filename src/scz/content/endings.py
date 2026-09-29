"""The Endings — 6-tier slice-resolution evaluator + canonical-flag applier.

Canon: `references/lore/the-endings.md`. Six tiers gated on
**species saved**, **crew aboard**, and **side-quest completion**:

| Tier         | Species saved (of 16) | Crew (of 5) | Side-quest threshold |
|--------------|-----------------------|-------------|----------------------|
| BEST         | 16                    | 5           | >= 95% (effectively all 8) |
| GREAT        | 16                    | 5           | >= 85% (>= 7 of 8) |
| GOOD         | 16                    | 2-4         | (any)                |
| AT_COST      | 8-15                  | 2-5         | (any)                |
| UNSUCCESSFUL | 1-7  OR crew <= 1     | any         | (any)                |
| DISASTROUS   | 0                     | 0           | (any)                |

The species + crew side-effect flag lists are the canonical "favorable"
set extracted from `walk_perfect_run` (which canonicalized the
spread-out CSV's Best-aligned branches). When CSV adds new flags, they
should be reflected here.

This module is **pure** — no scene transitions, no rendering. The
FinalConflictScene win path calls `evaluate_ending(game)` and then
`apply_ending(game, tier)` to set the canonical slice_ending flags;
EndingScene reads `slice_ending` to render the right tier.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from scz.engine.game import Game


# ---------------------------------------------------------------------------
# Canonical flag pools
# ---------------------------------------------------------------------------

# The 16 slice species, each represented by their FAVORABLE-terminal flag.
# A species is "saved" iff its flag is True. Aaron's canon enumerates the
# slice roster as: Slylandro, Androsynth, Mmrnmhrm, Chenjesu, Mycon,
# Proto-UQ/QA (collapsed into one quest), Arilou, Melnorme, Burvixese,
# Karavem, Kovellim, Lemmkin, Mrokon, Selvenne, Stelloth, Taalo, Utwig,
# Thinn, Forward (the 2D Thinn rebel — separate species track from Thinn
# proper per Forward HANDOFF entry).
#
# Order: roughly the canonical-encounter order from the slice timetable.
SPECIES_FAVORABLE_FLAGS: tuple[str, ...] = (
    "slylandro_cloaked",          # Slylandro — Cloaked
    "androsynth_aboard",          # Androsynth refugees — aboard
    "has_mmrnmhrm_excerpt",       # Mmrnmhrm — alliance honored
    "chen_pre_sentient",          # Chenjesu — pre-sentient (rooted, below threshold)
    "mycon_pre_sentient",         # Mycon — biot quiescent
    "proto_uplift_stopped",       # Proto-UQ + Proto-QA — non-uplift recommendation
    "arilou_hidden",              # Arilou — Hidden via Quasispace
    "melnorme_migration_pending", # Melnorme — Migration pledge secured
    "burvixese_migrated",         # Burvixese — small contingent Migrated
    "karavem_migrated",           # Karavem — Migrated
    "kovellim_traded",            # Kovellim — trade relation secured
    "lemmkin_curiosity_satisfied",# Lemmkin — quest favorable
    "mrokon_hammer_committed",    # Mrokon — full-support
    "selvenne_memory_contributed",# Selvenne — quest favorable
    "stelloth_trade_completed",   # Stelloth — quest favorable
    "taalo_v1_complete",          # Taalo — help-fully (Shield witnessed)
    "utwig_veils_lifted",         # Utwig — devolution-doctrine honored
    "thinn_cloaked",              # Thinn — sideways-cloaked
    "forward_diaspora_aboard",    # Forward + 2-Thinn diaspora — aboard
)

# The 5 named crew slots. The "weapons officer" slot can be filled by
# Bren-Vor (canonical) OR Forward (the 2D rebel alternative) — either
# satisfies the slot.
CREW_RECRUITED_FLAGS: tuple[str, ...] = (
    "recruited_pilot",            # Mraka (canonical)
    "recruited_weapons_officer",  # Bren-Vor OR Forward
    "recruited_engineer",         # Yelena
    "recruited_medic",            # Mira-Rou
    "recruited_navigator",        # Tarven
)

# The slice's tracked SIDE-QUEST flags. Each crew has a side-quest, plus
# the Hijack mission. Total: 7 flags. Best requires >= 95% (i.e. all 7).
# Great requires >= 85% (i.e. >= 6 of 7).
#
# Note: the older CSV included `diplomatic_resolution` as an 8th flag,
# but the 2026-05-18 canon revision (`the-final-conflict.md`) retired
# the diplomatic-resolution branch — combat is forced at the climax.
# So the Final Conflict's contribution to the ending tier is binary
# (won-it OR didn't), captured by `final_conflict_resolved` separately.
SIDE_QUEST_FLAGS: tuple[str, ...] = (
    "mraka_sq_complete",
    "brenvor_sq_complete",
    "yelena_sq_complete",
    "mira_sq_complete",
    "tarven_sq_complete",
    "forward_sq_complete",
    "hijack_council_sanctioned",
)


# Public tier name constants (avoid magic strings in scene wiring)
TIER_BEST = "BEST"
TIER_GREAT = "GREAT"
TIER_GOOD = "GOOD"
TIER_AT_COST = "AT_COST"
TIER_UNSUCCESSFUL = "UNSUCCESSFUL"
TIER_DISASTROUS = "DISASTROUS"

ALL_TIERS: tuple[str, ...] = (
    TIER_BEST, TIER_GREAT, TIER_GOOD,
    TIER_AT_COST, TIER_UNSUCCESSFUL, TIER_DISASTROUS,
)


# ---------------------------------------------------------------------------
# Counters
# ---------------------------------------------------------------------------

def count_species_saved(game: "Game") -> int:
    """Number of slice species whose favorable-terminal flag is True."""
    return sum(1 for f in SPECIES_FAVORABLE_FLAGS if game.flags.get(f))


def count_crew_aboard(game: "Game") -> int:
    """Number of named crew slots filled (out of 5)."""
    return sum(1 for f in CREW_RECRUITED_FLAGS if game.flags.get(f))


def count_side_quests_complete(game: "Game") -> int:
    """Number of canonical side-quest flags True (out of 8)."""
    return sum(1 for f in SIDE_QUEST_FLAGS if game.flags.get(f))


def side_quest_fraction(game: "Game") -> float:
    """Fraction of canonical side-quest flags True. 0.0 to 1.0."""
    total = len(SIDE_QUEST_FLAGS)
    if total == 0:
        return 1.0
    return count_side_quests_complete(game) / total


# ---------------------------------------------------------------------------
# Evaluator
# ---------------------------------------------------------------------------

# Threshold for Best (>=95% per canon). With 8 side-quest flags, 95%
# means >= 7.6, i.e. effectively all 8.
_BEST_FRACTION = 0.95


def evaluate_ending(game: "Game") -> str:
    """Compute the canonical ending tier from current flag state.

    Returns one of `TIER_*` constants. Priority order resolves overlap
    (most-specific rules first):

      1. DISASTROUS  — 0 species AND 0 crew
      2. UNSUCCESSFUL — <=7 species OR <=1 crew  (the OR is canon — the
         Migration cannot succeed without minimum allies AND minimum
         crew; failing EITHER axis triggers the survivor's-guilt ending)
      3. AT_COST     — 8-15 species, >=2 crew (mid-tier success)
      4. GOOD        — 16/16 species, 2-4 crew (full galactic Migration,
         partial personal community)
      5. BEST/GREAT  — 16/16 species AND 5/5 crew; split by side-quest
         completion fraction (>=95% Best; otherwise Great)

    Reads only `game.flags`. Pure function — no side effects. Callers
    that want to write the resulting flags should follow with
    `apply_ending(game, tier)`.
    """
    species = count_species_saved(game)
    crew = count_crew_aboard(game)

    if species == 0 and crew == 0:
        return TIER_DISASTROUS

    # UNSUCCESSFUL: insufficient on EITHER axis (canon OR)
    if species <= 7 or crew <= 1:
        return TIER_UNSUCCESSFUL

    # AT_COST: some-but-not-all species, sufficient crew
    if species < len(SPECIES_FAVORABLE_FLAGS):
        return TIER_AT_COST

    # species == len(SPECIES_FAVORABLE_FLAGS) (all species saved)
    if crew < len(CREW_RECRUITED_FLAGS):
        return TIER_GOOD

    # species == 16 AND crew == 5 — split Best vs Great by side-quest %
    if side_quest_fraction(game) >= _BEST_FRACTION:
        return TIER_BEST
    return TIER_GREAT


# ---------------------------------------------------------------------------
# Applier
# ---------------------------------------------------------------------------

def apply_ending(game: "Game", tier: str) -> None:
    """Write the canonical slice_ending flags per the CSV side-effects.

    Mutates `game.flags` only. Idempotent — calling twice with the same
    tier yields the same flag state.

    Side-effects per `tools/quest_inventory.csv` `q_endings_*` rows:
      - `slice_ending` = the tier name
      - `sc2_era_canonical` = True iff tier in (BEST/GREAT/GOOD/AT_COST)
      - `galaxy_consumed_forever` = True for UNSUCCESSFUL + DISASTROUS
      - `treaty_signed_in_blood` = True for DISASTROUS only
    """
    if tier not in ALL_TIERS:
        raise ValueError(
            f"Unknown ending tier {tier!r}; expected one of {ALL_TIERS}"
        )

    game.flags["slice_ending"] = tier

    sc2_canonical = tier in (TIER_BEST, TIER_GREAT, TIER_GOOD, TIER_AT_COST)
    game.flags["sc2_era_canonical"] = sc2_canonical

    if tier == TIER_DISASTROUS:
        game.flags["galaxy_consumed_forever"] = True
        game.flags["treaty_signed_in_blood"] = True
    elif tier == TIER_UNSUCCESSFUL:
        game.flags["galaxy_consumed_forever"] = True
        game.flags["treaty_signed_in_blood"] = False
    else:
        game.flags["galaxy_consumed_forever"] = False
        game.flags["treaty_signed_in_blood"] = False


def resolve_ending(game: "Game") -> str:
    """Evaluate the tier AND apply the canonical flags. Returns the tier.

    Convenience wrapper for scene wiring — the most common pattern is
    "compute tier, write flags, transition to EndingScene." This is
    that pattern.
    """
    tier = evaluate_ending(game)
    apply_ending(game, tier)
    return tier
