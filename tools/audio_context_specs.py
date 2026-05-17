"""All slice music contexts as data.

Per Aaron's 2026-05-17 scope lock:
  - 43 tracks total, ~200 stems
  - 90-second perfect loops (where applicable)
  - Asset-time generation via ElevenLabs Music
  - Skip hostile-species themes (combat covers it)
  - 6 per-faction endings (no shared base)
  - 7 Furling-civilization tracks (home + 6 per-faction Council;
    Cleanser-Council theme doubles as the pre-combat dread theme)
  - Cinematic stingers shorter (3 stems instead of 5)

The first batch we generate is "round 1" -- a 5-track sample so
Aaron can spot-check the prompt template before we burn the rest
of the credit budget. Round 1 picks one track from each major
category:

  hyperspace_peace, combat_low, slylandro_peace,
  cleanser_council, title_menu

Each ContextSpec is consumed by tools/audio_generate.py to fire
one ElevenLabs call per stem. Manifest is written alongside the
stems so the runtime can find them.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class ContextSpec:
    """A single music context = one track's worth of stems."""
    name: str                          # subdir under assets/music/<name>
    category: str                      # for grouping in tooling reports
    key: str                           # e.g. "C minor"
    bpm: int                           # tempo
    duration_s: int                    # 90 for loops, 30-45 for stingers
    description: str                   # one-line summary for humans
    stems: dict[str, str]              # stem_name -> prompt body
    # Round identifier for staged execution (1 = first batch sample).
    round: int = 1
    notes: str = ""


# ---------------------------------------------------------------------------
# Prompt template helpers
# ---------------------------------------------------------------------------

def _stem_prompt(role_caps: str, body: str, key: str, bpm: int, mood: str) -> str:
    """Standardize the per-stem prompt template.

    Front-load "Isolated <ROLE> STEM" because ElevenLabs Music is more
    responsive to high-level musical framing than to negation. Tail
    clause "stems-only mix" reinforces the isolation goal."""
    return (
        f"Isolated {role_caps} STEM for layered production: {body}, "
        f"in {key} at {bpm} bpm, {mood}, stems-only mix"
    )


def _standard_5stem(
    key: str,
    bpm: int,
    mood: str,
    *,
    bass_body: str,
    perc_body: str,
    pad_body: str,
    lead_body: str,
    amb_body: str,
) -> dict[str, str]:
    """Standard 5-stem set (bass / percussion / pad / lead / ambient)."""
    return {
        "bass": _stem_prompt("BASS", bass_body, key, bpm, mood),
        "percussion": _stem_prompt("DRUMS", perc_body, key, bpm, mood),
        "pad": _stem_prompt("PAD", pad_body, key, bpm, mood),
        "lead": _stem_prompt("LEAD MELODY", lead_body, key, bpm, mood),
        "ambient": _stem_prompt("AMBIENT TEXTURE", amb_body, key, bpm, mood),
    }


def _stinger_3stem(
    key: str,
    bpm: int,
    mood: str,
    *,
    drone_body: str,
    pulse_body: str,
    texture_body: str,
) -> dict[str, str]:
    """3-stem set for cinematic stingers (drone / pulse / texture)."""
    return {
        "drone": _stem_prompt("DRONE BASS", drone_body, key, bpm, mood),
        "pulse": _stem_prompt("RHYTHMIC PULSE", pulse_body, key, bpm, mood),
        "texture": _stem_prompt("AMBIENT TEXTURE", texture_body, key, bpm, mood),
    }


# ---------------------------------------------------------------------------
# A. Universal travel & exploration (Round 1 includes hyperspace)
# ---------------------------------------------------------------------------

HYPERSPACE_PEACE = ContextSpec(
    name="hyperspace",
    category="travel",
    key="C minor",
    bpm=108,
    duration_s=90,
    description="Hyperspace travel — peaceful; the player's 'ship at speed' theme",
    round=1,
    stems=_standard_5stem(
        "C minor", 108, "sci-fi space-flight, mid-tempo propulsive, hopeful but vast",
        bass_body="deep analog synth bassline, mid-tempo propulsive groove, no drums no melody no pads",
        perc_body="gated kick-and-hat pattern, mid-tempo four-on-the-floor with subtle space-fx claps, no melody no bass no pads",
        pad_body="warm analog synth pad, long sustained chords, atmospheric and propulsive, no melody no drums no bass",
        lead_body="mid-tempo synth arpeggio, hopeful melodic phrase, no drums no bass no pads",
        amb_body="subtle space drone wash, distant cosmic wind, sparkles, no melody no drums no bass",
    ),
)


# ---------------------------------------------------------------------------
# B. Combat (Round 1 includes combat_low)
# ---------------------------------------------------------------------------

COMBAT_LOW = ContextSpec(
    name="combat_low",
    category="combat",
    key="D minor",
    bpm=132,
    duration_s=90,
    description="Low-risk skirmish — engaged but not in real danger",
    round=1,
    stems=_standard_5stem(
        "D minor", 132, "tense action, driving propulsion, controlled risk",
        bass_body="driving distorted synth bass riff with eighth-note motion, no drums no melody no pads",
        perc_body="urgent live-sounding kit, fast hihats and snare backbeat with tom fills, no melody no bass no pads",
        pad_body="aggressive minor-key brass-pad stabs on the downbeat, no melody no drums no bass",
        lead_body="staccato synth riff, defiant melodic figure with tense intervals, no drums no bass no pads",
        amb_body="filtered sirens and radio chatter texture, no melody no drums no bass",
    ),
)


# ---------------------------------------------------------------------------
# C. Per-species peace themes (Round 1 includes slylandro_peace)
#
# Slylandro: 7-stem (5 standard + awe + worry). The state-driven stems
# rise/fade with the player's disposition relative to the Slylandro.
# ---------------------------------------------------------------------------

SLYLANDRO_PEACE = ContextSpec(
    name="slylandro",
    category="species_peace",
    key="A major",
    bpm=78,
    duration_s=90,
    description="Slylandro friendly — awed gas-bag aliens; state stems = awe + worry",
    round=1,
    stems={
        **_standard_5stem(
            "A major", 78, "wondrous, slow-floating, drifting through gas-giant clouds, sense of awe",
            bass_body="warm low sine-wave drone, ultra-slow swells, no drums no melody no pads",
            perc_body="soft mallet percussion and slow shakers, no kick, gentle pulse, no melody no bass no pads",
            pad_body="airy choral synth pad in major-key suspensions, very wide stereo, no melody no drums no bass",
            lead_body="slow flute-like solo, curious upward phrases, no drums no bass no pads",
            amb_body="gas-giant wind, distant chimes, gentle vinyl crackle, no melody no drums no bass",
        ),
        # State-driven layer: AWE — rises as the player builds rapport
        "awe": _stem_prompt(
            "AWE-FEELING TEXTURE",
            "bright crystalline bells, swelling major-key strings, sense of wonder and revelation",
            "A major", 78, "uplifting, transcendent, awe at the Furling visitor",
        ),
        # State-driven layer: WORRY — rises near Cleanse-path decisions
        "worry": _stem_prompt(
            "ANXIOUS UNEASE TEXTURE",
            "dark cellos and tremolo strings beneath the major key, distant alarm tones, dread leaking in",
            "A major", 78, "creeping worry, dread under the wonder",
        ),
    },
    notes=(
        "State stems 'awe' and 'worry' are read by src/scz/audio/state_layers.py "
        "from game.flags['slylandro_awe'] / game.flags['slylandro_worry']."
    ),
)


# ---------------------------------------------------------------------------
# F. Furling civilization (Round 1 includes cleanser_council)
#
# Cleanser-Council theme is loaded for both the Council debate scene AND
# the Vael-Souren pre-combat approach (per Aaron's locked scope; the
# Cleanser music IS the Cleanser music wherever they appear).
# ---------------------------------------------------------------------------

CLEANSER_COUNCIL = ContextSpec(
    name="cleanser_council",
    category="furling_faction",
    key="E flat minor",
    bpm=72,
    duration_s=90,
    description="Cleanser-Council theme — dread, conviction, monolithic resolve",
    round=1,
    stems=_standard_5stem(
        "E flat minor", 72,
        "monolithic dread, religious certainty, the executioner's quiet self-belief",
        bass_body="deep sub-bass drone with slow octave dives, almost subliminal, no drums no melody no pads",
        perc_body="slow taiko thump on the downbeats with whispered metallic scrapes, no melody no bass no pads",
        pad_body="cathedral pipe-organ-like minor-key chords, glacial sustain, ominous resolve, no melody no drums no bass",
        lead_body="solo low cello phrasing a funeral march motif, mournful conviction, no drums no bass no pads",
        amb_body="distant Furling chant fragments and wind through stone halls, no melody no drums no bass",
    ),
    notes=(
        "Doubles as the Vael-Souren PRE-COMBAT dread theme; the variance "
        "engine may darken it further for the dread moment."
    ),
)


# ---------------------------------------------------------------------------
# G. Cinematic stingers (Round 1 includes title_menu)
#
# 3-stem (drone / pulse / texture) instead of 5 — stingers have less
# need for mixing variance.
# ---------------------------------------------------------------------------

TITLE_MENU = ContextSpec(
    name="title_menu",
    category="cinematic",
    key="F minor",
    bpm=66,
    duration_s=90,
    description="Title screen — mystery, scale, the Furred Ones gazing at the stars",
    round=1,
    stems=_stinger_3stem(
        "F minor", 66,
        "vast, lonely, mythic, ancient civilization on the edge of revelation",
        drone_body="deep slow-evolving synth drone, swells of low harmonic content",
        pulse_body="slow heartbeat-like sub-pulse, occasional resonant metallic tap",
        texture_body="distant alien choral pads, soft solar wind, slow shimmer",
    ),
)


# ---------------------------------------------------------------------------
# Registry
# ---------------------------------------------------------------------------

# Round 1 — the 5-track validation sample.
ROUND_1: list[ContextSpec] = [
    HYPERSPACE_PEACE,
    COMBAT_LOW,
    SLYLANDRO_PEACE,
    CLEANSER_COUNCIL,
    TITLE_MENU,
]

# All defined contexts (extends with each round).
ALL_CONTEXTS: dict[str, ContextSpec] = {
    spec.name: spec for spec in ROUND_1
}


def get(name: str) -> ContextSpec:
    """Look up a context by name."""
    if name not in ALL_CONTEXTS:
        raise KeyError(
            f"unknown context {name!r}; available: {sorted(ALL_CONTEXTS)}"
        )
    return ALL_CONTEXTS[name]


def for_round(round_num: int) -> list[ContextSpec]:
    """Return all contexts in a given round, in declaration order."""
    return [s for s in ALL_CONTEXTS.values() if s.round == round_num]
