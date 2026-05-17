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
    # SC2 source track this context echoes -- a tracker .mod or 3DO .ogg
    # under references/uqm-source/sc2/content/. Used to seed the prompt
    # with an "in the spirit of <described idiom>" line so our generated
    # music inherits the family resemblance Aaron asked for. Empty when
    # the context is SCZ-original (no SC2 equivalent).
    sc2_inspiration: str = ""
    sc2_idiom: str = ""                # 1-2 sentence prompt-ready description of the SC2 source
    # Round identifier for staged execution (1 = first batch sample).
    round: int = 1
    notes: str = ""


# ---------------------------------------------------------------------------
# Prompt template helpers
# ---------------------------------------------------------------------------

def _stem_prompt(role_caps: str, body: str, key: str, bpm: int, mood: str,
                 sc2_idiom: str = "") -> str:
    """Standardize the per-stem prompt template.

    Front-load "Isolated <ROLE> STEM" because ElevenLabs Music is more
    responsive to high-level musical framing than to negation. Tail
    clause "stems-only mix" reinforces the isolation goal.

    If `sc2_idiom` is provided, it's spliced in as a "in the spirit of"
    line -- this is how Aaron's "use the SC2 90s tracks as basis" rule
    is plumbed through to every stem prompt."""
    spirit = f", in the spirit of {sc2_idiom}" if sc2_idiom else ""
    return (
        f"Isolated {role_caps} STEM for layered production: {body}, "
        f"in {key} at {bpm} bpm, {mood}{spirit}, stems-only mix"
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
    sc2_idiom: str = "",
) -> dict[str, str]:
    """Standard 5-stem set (bass / percussion / pad / lead / ambient)."""
    sf = sc2_idiom
    return {
        "bass": _stem_prompt("BASS", bass_body, key, bpm, mood, sf),
        "percussion": _stem_prompt("DRUMS", perc_body, key, bpm, mood, sf),
        "pad": _stem_prompt("PAD", pad_body, key, bpm, mood, sf),
        "lead": _stem_prompt("LEAD MELODY", lead_body, key, bpm, mood, sf),
        "ambient": _stem_prompt("AMBIENT TEXTURE", amb_body, key, bpm, mood, sf),
    }


def _stinger_3stem(
    key: str,
    bpm: int,
    mood: str,
    *,
    drone_body: str,
    pulse_body: str,
    texture_body: str,
    sc2_idiom: str = "",
) -> dict[str, str]:
    """3-stem set for cinematic stingers (drone / pulse / texture)."""
    sf = sc2_idiom
    return {
        "drone": _stem_prompt("DRONE BASS", drone_body, key, bpm, mood, sf),
        "pulse": _stem_prompt("RHYTHMIC PULSE", pulse_body, key, bpm, mood, sf),
        "texture": _stem_prompt("AMBIENT TEXTURE", texture_body, key, bpm, mood, sf),
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
    sc2_inspiration="references/uqm-source/sc2/content/addons/3domusic/hyper.ogg",
    # NOTE: ElevenLabs ToS filter rejects the literal string "SC2" /
    # "Star Control" (trademark). Describe the IDIOM, not the name.
    sc2_idiom="the classic 1990s space-game hyperspace idiom — flowing minor-key chord progressions on analog synth pads, mid-tempo propulsive bass, ProTracker-derived 3DO arrangement, restless forward momentum",
    round=1,
    stems=_standard_5stem(
        "C minor", 108, "sci-fi space-flight, mid-tempo propulsive, hopeful but vast",
        bass_body="deep analog synth bassline, mid-tempo propulsive groove, no drums no melody no pads",
        perc_body="gated kick-and-hat pattern, mid-tempo four-on-the-floor with subtle space-fx claps, no melody no bass no pads",
        pad_body="warm analog synth pad, long sustained chords, atmospheric and propulsive, no melody no drums no bass",
        lead_body="mid-tempo synth arpeggio, hopeful melodic phrase, no drums no bass no pads",
        amb_body="subtle space drone wash, distant cosmic wind, sparkles, no melody no drums no bass",
        sc2_idiom="the classic 1990s space-game hyperspace idiom — flowing minor-key synth progressions, ProTracker-derived 3DO arrangement",
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
    description="Low-risk skirmish — engaged but not in real danger (heavy-metal pivot 2026-05-17)",
    sc2_inspiration="references/uqm-source/sc2/content/addons/3domusic/battle.ogg",
    sc2_idiom="1990s sci-fi combat-game battle idiom crossed with classic heavy-metal — galloping distorted bass, double-kick drums, palm-muted electric-guitar riffs, screaming lead guitar",
    round=1,
    stems=_standard_5stem(
        "D minor", 132,
        "heavy-metal sci-fi combat, driving aggressive but musical, never harsh-for-the-sake-of-harsh",
        bass_body="galloping palm-muted distorted electric bass guitar riff, eighth-note motion, no drums no melody no pads",
        perc_body="thrash-metal kit with double-kick gallop on bass drum, crash and ride cymbals, tight snare backbeat, no melody no bass no pads",
        pad_body="sustained distorted electric-guitar power chord stabs on the downbeats, no melody no drums no bass",
        lead_body="screaming distorted lead electric-guitar melody with confident bluesy phrasing, hero-on-the-attack feel, no drums no bass no pads",
        amb_body="industrial machine-room hum and amp-feedback texture, no melody no drums no bass",
        sc2_idiom="1990s sci-fi combat-game battle crossed with classic heavy-metal — galloping distorted bass, double-kick drums, palm-muted electric guitars",
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
    sc2_inspiration="references/uqm-source/sc2/content/base/comm/slylandro/slylandro.mod",
    sc2_idiom="the 1990s alien-first-contact game theme idiom — eerie slow chord beds, distant gas-giant winds, multitracker chiptune, wonder edging into unease",
    round=1,
    stems={
        **_standard_5stem(
            "A major", 78, "wondrous, slow-floating, drifting through gas-giant clouds, sense of awe",
            bass_body="warm low sine-wave drone, ultra-slow swells, no drums no melody no pads",
            perc_body="soft mallet percussion and slow shakers, no kick, gentle pulse, no melody no bass no pads",
            pad_body="airy choral synth pad in major-key suspensions, very wide stereo, no melody no drums no bass",
            lead_body="slow flute-like solo, curious upward phrases, no drums no bass no pads",
            amb_body="gas-giant wind, distant chimes, gentle vinyl crackle, no melody no drums no bass",
            sc2_idiom="the 1990s alien-first-contact game theme — eerie chord beds, gas-giant winds, multitracker chiptune",
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
    sc2_inspiration="",  # SCZ-original (Cleanser is a Furling faction; no SC2 antecedent)
    sc2_idiom="",
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
    bpm=72,
    duration_s=240,  # 4-minute orchestrated piece per Aaron 2026-05-17
    description="Title screen — grand orchestrated anthem, 4-minute structured piece with a memorable hero-hook",
    sc2_inspiration="references/uqm-source/sc2/content/addons/3domusic/credits.ogg",
    sc2_idiom="1990s mythic sci-fi credits idiom — vast ancient civilization at scale, 3DO orchestrated synth, slow majestic chord progression",
    round=1,
    notes=(
        "240-second piece. Each stem prompt names a 5-part structure so the "
        "generation hangs together rhythmically when stems are mixed: "
        "intro (0-30s, sparse) -> build (30-90s, layering in) -> hero theme "
        "with the HOOK (90-180s, full orchestra) -> restatement (180-210s, "
        "darker minor variation) -> fade (210-240s, intro motif returning)."
    ),
    stems=_standard_5stem(
        "F minor", 72,
        ("grand cinematic sci-fi orchestra, 4-minute structured piece: "
         "sparse intro -> layered build -> soaring hero-theme hook at 90s -> "
         "minor-key restatement -> fade. Striking, memorable, NOT ambient"),
        bass_body=("orchestral low end: tuba pedal tones, double-bass section, "
                   "timpani rolls on section transitions, deep cinematic foundation; "
                   "no drums no melody no pads"),
        perc_body=("orchestral percussion: timpani, ride cymbals, snare rolls, "
                   "occasional gong on the hero-theme entry, restrained but "
                   "deliberate; no melody no bass no pads"),
        pad_body=("sustained full string section — violins and cellos — with "
                  "warm horns underneath, swelling on the hero theme, "
                  "supportive chord beds throughout; no melody no drums no bass"),
        lead_body=("MEMORABLE HEROIC BRASS THEME: French horns and trumpets "
                   "stating a striking 4-bar hook melody that lands at the "
                   "90-second mark, then restates with variations. The HOOK "
                   "is the most important element — make it singable. Hero "
                   "theme in a minor key, noble but melancholy; "
                   "no drums no bass no pads"),
        amb_body=("distant alien choral pads, soft solar wind, slow harmonic "
                  "shimmer, mythic backing texture sustaining throughout; "
                  "no melody no drums no bass"),
        sc2_idiom="1990s mythic sci-fi credits — vast ancient scale, 3DO orchestrated, hero brass theme",
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
