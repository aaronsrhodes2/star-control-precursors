"""Per-species name banks for ship instances + named entities.

Canonical doc: `references/lore/species-naming-conventions.md`.

Each species has a cultural value-anchor that drives naming. Melnorme
name ships after trade/sales jokes ("The Going-Out-of-Business Sale");
Burvixese name them for loudness ("The Long-Term Hearing Damage");
Furlings name them for stewardship virtues; Utwig for ritual cadences;
etc.

The registry is consumed by:
- Combat scene HUD — displays the **instance name** of the opponent
  rather than the bare ship-class id
- Super-melee picker — names AI-controlled ships from the bank
- Hyperspace encounter labels — "you see a Cleanser approaching: *The
  Last Verse*"

Sampling is deterministic-per-encounter via a seed (typically the
encounter id or a hash of the spawn-context), so a repeated encounter
keeps its name and the player learns to recognize *specific ships*.

When the variation layer (Phase 3 polish) ships, names will be
LLM-generated *in the cultural pattern* of each bank rather than
sampled from the fixed list — unlimited variety, same naming voice.
The fixed banks here are the canonical seed corpus the LLM is
conditioned on.
"""

from __future__ import annotations

import hashlib


# Species id → list of canonical example names. Keys match the
# `species_id` used in `dialog.characters` factories + the
# `species_visual.SPECIES_WARP_POD` keys where applicable.

SHIP_NAME_BANKS: dict[str, list[str]] = {
    # ----- Furling (player's people + factions) -----------------------
    # Anchor: stewardship, witnessing, dignity, the Quiet Resolution.
    # Furling names are warm and slightly bureaucratic — ships are
    # named after virtues, acts of bookkeeping, the gestures of a
    # Steward at a tea-table.
    "FURLING_SCOUT": [
        "The Quiet Stewardship",
        "The Soft Confirmation",
        "The Bookkeeping Is The Dignity",
        "The Mother's Tea",
        "The Patient Drift",
        "The Furling's Word",
        "The Last Welcome",
        "The Slow Inventory",
        "The Census of Friends",
        "The Bonded Letter",
        "The Steward's First Tea",
        "The Honored Record",
    ],
    "FURLING_PERSUADER": [
        "The Listening Ledger",
        "The Open Question",
        "The Patient Argument",
        "The Honored Disagreement",
        "The Long Conversation",
        "The Soft Persuasion",
        "The Yielding",
        "The Mother's Question",
    ],
    "FURLING_COMPELLER": [
        "The Necessary Lift",
        "The Sealed Manifest",
        "The Quiet Disembarkation",
        "The Steady Hand",
        "The Pragmatist's Receipt",
        "The Work-That-Got-Done",
    ],
    "FURLING_CLEANSER": [
        # The canonical Cleanser cruiser the slice already uses;
        # placed first so encounter spawn that picks index 0 keeps
        # canon continuity with the existing Vael-Souren dialog.
        "The Bell of the Quiet Ledger",
        "The Mercy Without Triumph",
        "The Final Inventory",
        "The Last Verse",
        "The Quiet Burying",
        "The Compassionate Termination",
        "The Bell That Does Not Ring Twice",
        "The Sealed Ledger",
    ],
    "FURLING_DEFENDER": [
        "The Hold-the-Line",
        "The Wall-Whose-Name-Was-Forgotten",
        "The Sa-Matra's Foreword",
        "The Defender-of-What-Cannot-Be-Defended",
        "The Three Hammers",
        "The Last Argument",
    ],

    # ----- Mmrnmhrm — formal-archaic English; ships are index entries
    "MMRNMHRM": [
        "Index 7-240-Delta",
        "Subsection Beta of the Patient Archive",
        "The Continued Operation",
        "The Defended Homeworld (Indexed)",
        "Log Volume 22-Million",
        "The Maker-Memorial-Continuous",
        "The Quiet Sentinel-Aux (Sub-Wing 4)",
        "Index 8-Hundred-Thousand-Two-Hundred",
        "The First-Maker Catalog",
        "Reference 12-Indexed-Delta",
    ],

    # ----- Chenjesu — "we"-pronoun, lattice, stillness
    "CHENJESU": [
        "We Who Wait",
        "The Slow Stone Considers",
        "The Patient Lattice",
        "We Are Still Here",
        "The Memory of Light",
        "What We Remember",
        "We Who Were Already Listening",
        "The Resonance That Remained",
        "The Lattice Beneath The Hollow",
        "We Remember (Plural Form)",
    ],

    # ----- Taalo — mountain, sub-region, slow stone
    "TAALO": [
        # Canonical in-code speaker name placed first
        "We-Who-Watch-The-Northwest-Bench",
        "The Slow-Watcher-At-The-Trailhead",
        "The Mountain Remembers",
        "The Slow Patient Stone",
        "The Bench-Rock Greets You",
        "The Long Song Continues",
        "What May Yet Hold",
        "The Patient Geometer",
        "We-Who-Sit-Now",
        "The Northwest-Ridge-Speaks",
    ],

    # ----- Burvixese — Aaron's canonical example: loudness/volume
    "BURVIXESE": [
        "The Long-Term Hearing Damage",
        "All About the Bass",
        "The Loudest Possible Argument",
        "The Megaresonance Mark IV",
        "The Carrier-Band Eternal",
        "The Brilliant Deafening",
        "The Caster's Carrier",
        "The Unignorable",
        "The Distortion Pedal",
        "The Speaker-of-Speakers",
        "The Resonator Mark VII",
        "The Tinnitus Permanent",
        "The Treble Booster",
        "The Volume Knob Removed",
        "The Subwoofer's Last Concert",
        "The Cymbal-Crash-Eternal",
    ],

    # ----- Utwig — ritual, mask-cadence
    "UTWIG": [
        "The Mask of Gruelling but Necessary Activity",
        "The Countenance of Stellar Representation",
        "The Veil That Falls First",
        "The Seventeen-Step Ablution",
        "The Quieting",
        "The Procedure Is The Prayer",
        "The Worn-and-Removed-on-Alternating-Breath-Cycles",
        "The Necessary Activity",
    ],

    # ----- Melnorme — Aaron's canonical example: trade/sales puns
    "MELNORME": [
        "The Going-Out-of-Business Sale",
        "The Dollar General",
        "The Buy-One-Get-One",
        "The Special Discount",
        "The End-of-Season Clearance",
        "The Manager's Special",
        "The Wholesale Account",
        "The Bulk Discount",
        "The Two-for-One Tuesday",
        "The Bargain Bin",
        "The Liquidation",
        "The Inventory Reduction",
        "The Markup Honest",
        "The Receipt-In-Triplicate",
        "The Bring-A-Friend-Get-Ten-Percent",
        "The Shipping-Handling-Negotiable",
        "The Cash-Or-Bio-Cargo",
        "The While-Supplies-Last",
        "The Loss-Leader",
    ],

    # ----- Slylandro — drift, observation, wind-borne
    "SLYLANDRO": [
        "The Drifting Observation",
        "The Long Patient Watching",
        "The Wind-Borne Sigh",
        "The Cloak That Holds",
        "The Storm-Wisdom",
        "The Slow Spore",
        "The Halia-Below",
        "The Conversation With Itself",
        "The Gentle Drift",
        "The Murmuration",
    ],

    # ----- Arilou — half-folded, partial-presence
    "ARILOU": [
        "The Halfway Here",
        "The Mostly-Listened",
        "The Folded Greeting",
        "The Thrice-Voted-Patient",
        "The Quietest Possible Sage",
        "The Slip-Between",
        "The Half-Folded Skiff",
        "The Listening Beside",
        "The Sage's-Patient-Vessel",
        "The Almost-Arrived",
    ],

    # ----- Mycon — spore, awakening, the Deep Child
    "MYCON_BIOT": [
        "The Awakening Spore",
        "The Deep Child Stirs",
        "The Hive-Knows-Itself",
        "The Vela's Forge",
        "The Spore-Carries-Memory",
        "The Soft Egg-Case",
        "The Patient Mycelium",
        "The Awakening (Indefinitely)",
    ],

    # ----- Androsynth — time-displaced, distress, refugee-class
    "ANDROSYNTH": [
        # Canonical in-code first
        "The Distress Beacon",
        "The Refugee-Class III",
        "The Wrong-Era Survivor",
        "The Lost-Future",
        "The Memorial 22nd-Century",
        "The Decursion-Survivor",
        "The Cargo-Manifest-Backwards",
    ],

    # ----- Lemmkin — curiosity, footnotes-become-chapters
    "LEMMKIN": [
        "The Inquiring Skitter",
        "The Many-Footed Question",
        "The Trove-That-Counts",
        "The Footnote-Becomes-Chapter",
        "The Curious-First",
        "The Index-In-Progress",
        "The Maybe-Possibly",
        "The Question-Mark-Vessel",
    ],

    # ----- Thinn — 2D, sideways, edge-align
    "THINN": [
        "The Edge-Aligned",
        "The Sideways-Forward",
        "The Wholly Sideways",
        "The Perpendicular Aim",
        "The Conceptually-Impossible-Angle",
        "The Sliver-That-Looks-Back",
        "The Ribbon-Carries-Memory",
    ],

    # ----- Karavem — music, valence-reversed (major=sad, minor=joy)
    "KARAVEM": [
        "The Aria in F-Minor",          # = joyful exploration
        "The Joyful Minor-Key",
        "The Sad-Major-Final",
        "The Lullaby for the Dying Star",
        "The Hymn-of-Curiosity",
        "The Cadence-in-Reverse",
        "The Coda-of-Welcome",
    ],

    # ----- Proto-Ur-Quan — Furling Hider-naming convention overlay
    # The proto-species don't name themselves; the Furlings call them
    # by location + species-tag. These names are how Furling Stewards
    # *would refer to* a proto-ship if one existed (currently they
    # don't have ships in our era; this is for super-melee testing
    # exposure and future cinematic use).
    "PROTO_URQUAN": [
        "The Sigma-Persei Mollusc-Cluster (Observed)",
        "The Sessile-Population, Pre-Sentient",
    ],
    "PROTO_QORAH": [
        "The Eta-Vulpeculae Mollusc-Cluster (Eastern Branch)",
        "The Sessile-Population, Pre-Sentient (Variant 2)",
    ],

    # ----- The Others — no names; sameness is part of the horror.
    # Combat HUD shows just "OTHERS" or "[OTHERS' VESSEL]". This entry
    # exists so name-lookup doesn't crash on the species id; consumers
    # should special-case the Others.
    "OTHERS": [
        "OTHERS",
    ],

    # ----- Dnyarri — they use stolen ships; the cover species' bank
    # is sampled instead. This entry is the post-reveal tag only.
    "DNYARRI": [
        "DNYARRI (controlling host)",
    ],
}


# Map ShipClass id (e.g. "CLEANSER_CRUISER") to its owning species
# id (e.g. "FURLING_CLEANSER"). When a new ShipClass lands in
# `src/scz/combat/ships.py`, add a row here so the combat HUD + super-
# melee picker can look up the right name bank.
SHIP_CLASS_TO_SPECIES_ID: dict[str, str] = {
    "FURLING_SCOUT":       "FURLING_SCOUT",
    "PERSUADER_VESSEL":    "FURLING_PERSUADER",
    "COMPELLER_VESSEL":    "FURLING_COMPELLER",
    "CLEANSER_CRUISER":    "FURLING_CLEANSER",
    "DEFENDER_VESSEL":     "FURLING_DEFENDER",
    "ARILOU_SKIFF":        "ARILOU",
    "ANDROSYNTH_CRUISER":  "ANDROSYNTH",
    "MELNORME_TRADER":     "MELNORME",
    "MMRNMHRM_SENTINEL":   "MMRNMHRM",
    "MYCON_PODSHIP":       "MYCON_BIOT",
    "PROTO_UR_QUAN":       "PROTO_URQUAN",
    "PROTO_QOR_AH":        "PROTO_QORAH",
    "UTWIG_JUGGER":        "UTWIG",
    "LEMMKIN_SKITTER":     "LEMMKIN",
    "THINN_BLADE":         "THINN",
    "BURV_BROADCASTER":    "BURVIXESE",
}


# Species that should never show an instance name (the species itself
# is the name — sameness is part of the canonical horror or the
# species has no individuating names).
_NO_INSTANCE_NAMES: frozenset[str] = frozenset({"OTHERS"})


def name_for_encounter(
    species_id: str, seed_key: str | int,
) -> str:
    """Return a deterministic instance name for a species + encounter
    seed key.

    The same `seed_key` always returns the same name; different
    seed_keys for the same species typically return different names.
    Repeated encounters with the same id keep their name (the player
    learns to recognize *specific ships*).

    Falls back to the species id as a label if the bank is missing
    or empty — better to show something raw than crash.
    """
    if species_id in _NO_INSTANCE_NAMES:
        return species_id
    bank = SHIP_NAME_BANKS.get(species_id, [])
    if not bank:
        return species_id
    # Deterministic hash of the seed_key → bank index. Using sha1 for
    # the stable cross-platform-ness; we don't need crypto security.
    key = f"{species_id}:{seed_key}".encode("utf-8")
    digest = hashlib.sha1(key).digest()
    idx = int.from_bytes(digest[:4], "big") % len(bank)
    return bank[idx]


def name_for_first_encounter(species_id: str) -> str:
    """The bank's index-0 entry — used for the canonical first
    encounter the player will have with a species. Banks are ordered
    with the canonical "first thing the player will see" at index 0
    (e.g. `The Bell of the Quiet Ledger` for `FURLING_CLEANSER`).
    """
    if species_id in _NO_INSTANCE_NAMES:
        return species_id
    bank = SHIP_NAME_BANKS.get(species_id, [])
    if not bank:
        return species_id
    return bank[0]
