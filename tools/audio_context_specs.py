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
# A. Universal travel & exploration — Round 2 batch
# ---------------------------------------------------------------------------

SYSTEM_TRAVEL = ContextSpec(
    name="system_travel",
    category="travel",
    key="D minor",
    bpm=92,
    duration_s=90,
    description="In-system travel — contemplative exploration of a star system",
    sc2_inspiration="references/uqm-source/sc2/content/addons/3domusic/space.ogg",
    sc2_idiom="1990s sci-fi in-system exploration idiom — slower than hyperspace, "
              "contemplative chord beds with occasional bright bell-like punctuation, "
              "3DO orchestrated synth, sense of approach rather than transit",
    round=2,
    stems=_standard_5stem(
        "D minor", 92,
        "contemplative sci-fi in-system flight, slower-paced exploration, sense of approach",
        bass_body="slow walking analog synth bassline, sustained low pulses, no drums no melody no pads",
        perc_body="sparse mid-tempo brush kit with occasional rim-shots and shaker, no melody no bass no pads",
        pad_body="warm slow-evolving analog pad in minor-key chord beds, atmospheric, no melody no drums no bass",
        lead_body="occasional bright bell-tone melody fragments, restrained and curious, no drums no bass no pads",
        amb_body="distant solar wind and gentle deep-space hum, no melody no drums no bass",
        sc2_idiom="1990s sci-fi in-system exploration — slower than hyperspace, "
                  "ProTracker-derived chord beds, 3DO synth",
    ),
)

HYPERSPACE_PURSUIT = ContextSpec(
    name="hyperspace_pursuit",
    category="travel",
    key="C minor",
    bpm=140,
    duration_s=90,
    description="Hyperspace travel — chased; danger stalking, must escape",
    sc2_inspiration="references/uqm-source/sc2/content/addons/3domusic/hyper.ogg",
    sc2_idiom="1990s space-game pursuit idiom — same minor-key chord-progression "
              "DNA as the peaceful hyperspace theme but faster and tenser, the "
              "same melodic family in a panic state",
    round=2,
    notes="Should sound like the peaceful Hyperspace theme's tense cousin — "
          "same key (C minor) for continuity, but +32 bpm and shifted to "
          "a 'something is wrong' register so context transitions feel related.",
    stems=_standard_5stem(
        "C minor", 140,
        "tense pursuit, fast-paced sci-fi flight, danger stalking, must escape",
        bass_body="fast pulsing distorted synth bass with eighth-note urgency, no drums no melody no pads",
        perc_body="driving four-on-the-floor with double-time hihats and occasional crash, anxious tom fills, no melody no bass no pads",
        pad_body="dissonant minor-key brass stab pads, repeating tense rhythmic figure, no melody no drums no bass",
        lead_body="urgent staccato synth riff, fearful melodic figure that climbs and falls, no drums no bass no pads",
        amb_body="alarm-siren texture and panicked radio chatter, no melody no drums no bass",
        sc2_idiom="1990s space-game pursuit — tense cousin of the peaceful "
                  "hyperspace theme, ProTracker-derived",
    ),
)

QUASISPACE_TRAVEL = ContextSpec(
    name="quasispace_travel",
    category="travel",
    key="D flat major",
    bpm=70,
    duration_s=90,
    description="Quasi-Space travel via Arilou portal — otherworldly, time-detached",
    sc2_inspiration="references/uqm-source/sc2/content/addons/3domusic/quasispace.ogg",
    sc2_idiom="1990s alien-dimensional-pocket idiom — drifting, time-stretched, "
              "phase-shifted chimes, sense of being between places, 3DO synth",
    round=2,
    stems=_standard_5stem(
        "D flat major", 70,
        "otherworldly drifting through a non-Euclidean pocket dimension, time-detached",
        bass_body="slow detuned synth drone, gentle phase-shifting low frequencies, no drums no melody no pads",
        perc_body="very sparse soft mallet percussion with long reverb tails, almost ambient, no melody no bass no pads",
        pad_body="airy choral synth pad with subtle pitch-bend modulation, time-stretched quality, no melody no drums no bass",
        lead_body="distant phase-shifted bell-tone melody, dreamy and detached, no drums no bass no pads",
        amb_body="reversed shimmer textures, subtle dimensional-echo aftertones, no melody no drums no bass",
        sc2_idiom="1990s alien-dimensional-pocket idiom — drifting, "
                  "time-stretched, ProTracker-derived",
    ),
)

PLANET_ORBIT_CLOAKED = ContextSpec(
    name="planet_orbit_cloaked",
    category="travel",
    key="E flat major",
    bpm=80,
    duration_s=90,
    description="Planet orbit — cloaked and safe; scanning from above",
    sc2_inspiration="references/uqm-source/sc2/content/addons/3domusic/orbit1.ogg",
    sc2_idiom="1990s sci-fi planetary-orbit idiom — calm, observational, "
              "soft sustained pads with gentle pulsing bass, 3DO synth, "
              "sense of safety from a high vantage point",
    round=2,
    stems=_standard_5stem(
        "E flat major", 80,
        "calm safe orbital observation, scanner-active but invisible, soft watchful",
        bass_body="warm sub-bass slow pulse on the downbeat, no drums no melody no pads",
        perc_body="soft electronic shaker with gentle hihat, mostly quiet, no melody no bass no pads",
        pad_body="warm major-key synth pad in slow sustained chords, atmospheric calm, no melody no drums no bass",
        lead_body="soft chime-like melody motif, contemplative and watchful, no drums no bass no pads",
        amb_body="gentle scanner-tone shimmer and distant planet-atmosphere whisper, no melody no drums no bass",
        sc2_idiom="1990s sci-fi orbital idiom — calm observation, ProTracker-derived",
    ),
)

PLANET_LANDER = ContextSpec(
    name="planet_lander",
    category="travel",
    key="G major",
    bpm=96,
    duration_s=90,
    description="Planet lander — surface collecting; methodical exploration",
    sc2_inspiration="",  # no direct SC2 antecedent
    sc2_idiom="",
    round=2,
    notes="Should sound like productive work on an alien surface — "
          "methodical rhythm, slight wonder, never tense.",
    stems=_standard_5stem(
        "G major", 96,
        "methodical sci-fi surface exploration, productive working tempo, slight wonder",
        bass_body="steady walking analog synth bassline with optimistic forward motion, no drums no melody no pads",
        perc_body="light kit with rim-shots and shaker, mid-tempo working rhythm, no melody no bass no pads",
        pad_body="warm major-key synth pad with major-7 colors, atmospheric and inviting, no melody no drums no bass",
        lead_body="bright synth melody with curious rising phrases, productive but slightly awed, no drums no bass no pads",
        amb_body="alien wind through canyon, distant resource-detection chirps, no melody no drums no bass",
    ),
)


# ---------------------------------------------------------------------------
# B. Combat — Round 2 batch (combat_low already in Round 1)
# ---------------------------------------------------------------------------

COMBAT_HIGH = ContextSpec(
    name="combat_high",
    category="combat",
    key="D minor",
    bpm=144,
    duration_s=90,
    description="High-risk skirmish — real danger, escalation past low-risk threshold",
    sc2_inspiration="references/uqm-source/sc2/content/addons/3domusic/battle.ogg",
    sc2_idiom="1990s sci-fi combat-game battle idiom — same heavy-metal "
              "vocabulary as combat_low but faster, harder, with higher stakes",
    round=2,
    notes="Continuity with combat_low's heavy-metal pivot — same key (D minor), "
          "+12 bpm, more aggressive riffs.",
    stems=_standard_5stem(
        "D minor", 144,
        "escalated heavy-metal sci-fi combat, real-stakes danger, more aggressive than low-risk",
        bass_body="aggressive palm-muted distorted electric bass riff with sixteenth-note gallop, no drums no melody no pads",
        perc_body="hard thrash-metal kit with sustained double-kick, crash and china cymbals, snare rolls between fills, no melody no bass no pads",
        pad_body="sustained heavy distorted power-chord stabs with chromatic motion, no melody no drums no bass",
        lead_body="shredding distorted lead electric-guitar with fast melodic runs, defiant and dangerous, no drums no bass no pads",
        amb_body="industrial machine-room hum, amp feedback, distant warning sirens, no melody no drums no bass",
        sc2_idiom="1990s sci-fi combat — heavy-metal escalation, ProTracker-derived",
    ),
)

COMBAT_BOSS = ContextSpec(
    name="combat_boss",
    category="combat",
    key="E flat minor",
    bpm=132,
    duration_s=90,
    description="Boss fight — Cleanser climax; religious-dread combat",
    sc2_inspiration="",  # SCZ-original — Cleanser is a Furling faction
    sc2_idiom="",
    round=2,
    notes="Bridges combat_low (heavy-metal sci-fi) and cleanser_council "
          "(monolithic Furling dread). Same key as cleanser_council (Eb minor) "
          "for thematic ties; combat tempo (132 bpm) for action.",
    stems=_standard_5stem(
        "E flat minor", 132,
        "monolithic religious-dread combat, Cleanser boss climax, doom-metal sci-fi",
        bass_body="thunderous detuned distorted electric bass with deep sub-bass doubling, doom-metal weight, no drums no melody no pads",
        perc_body="massive taiko-and-thrash hybrid kit with double-kick gallop and crash cymbals, ceremonial weight, no melody no bass no pads",
        pad_body="distorted cathedral pipe-organ stabs in minor-key chord progression, religious dread, no melody no drums no bass",
        lead_body="solo distorted electric-guitar lead with mournful conviction, hero-against-fate phrasing, no drums no bass no pads",
        amb_body="distant Furling chant fragments, deep cathedral reverb tail, ominous wind through stone, no melody no drums no bass",
    ),
)


# ---------------------------------------------------------------------------
# C. Per-species peace themes — Round 2 batch
# (Slylandro already in Round 1; Lemmkin queued below)
# ---------------------------------------------------------------------------

MYCON_PEACE = ContextSpec(
    name="mycon",
    category="species_peace",
    key="F minor",
    bpm=64,
    duration_s=90,
    description="Mycon biot — obedient ritual chanting; state stems = obedience + heresy",
    sc2_inspiration="references/uqm-source/sc2/content/base/comm/mycon/mycon.mod",
    sc2_idiom="1990s alien-fungal-ritual idiom — chanting, wet thrumming, "
              "deep bio-mechanical pulses, slow tempo, multitracker chiptune "
              "vocabulary",
    round=2,
    notes="State stems 'obedience' and 'heresy' are read by "
          "src/scz/audio/state_layers.py from game.flags['mycon_heresy_level']. "
          "obedience high when player hasn't disturbed the Deep Child; heresy "
          "rises as the Deep Child whispers gain traction.",
    stems={
        **_standard_5stem(
            "F minor", 64,
            "alien fungal-ritual species theme, slow chanting, wet bio-mechanical pulses",
            bass_body="deep sub-bass bio-thrum with slow pulsing modulation, no drums no melody no pads",
            perc_body="slow wet organic percussion: dripping cave-water rhythms, soft body-thuds, no melody no bass no pads",
            pad_body="droning minor-key fungal-tone pad with subtle dissonance, no melody no drums no bass",
            lead_body="slow ceremonial chant-melody, low voiced syllables in fragments, no drums no bass no pads",
            amb_body="distant cave reverb, drip echoes, low spore-cloud rumble, no melody no drums no bass",
            sc2_idiom="1990s alien-fungal-ritual — chanting, multitracker chiptune",
        ),
        # State stem: OBEDIENCE — high when undisturbed; communal chant of conformity
        "obedience": _stem_prompt(
            "OBEDIENCE-RITUAL TEXTURE",
            "low-voiced chorus of synchronized ceremonial chant, calm dutiful murmuring, "
            "sense of an entire colony moving in perfect ritual harmony",
            "F minor", 64, "obedient, calm, harmonious, ritually-perfect",
        ),
        # State stem: HERESY — rises with Deep Child whispers; dissonant counter-melody
        "heresy": _stem_prompt(
            "HERESY-WHISPER TEXTURE",
            "dissonant counter-chant of individual voices breaking from harmony, "
            "whispered alien syllables, growing unease in the bio-machinery, the "
            "Deep Child awakening from below",
            "F minor", 64, "dissonant, dawning awareness, awakening from ritual",
        ),
    },
)

ARILOU_PEACE = ContextSpec(
    name="arilou",
    category="species_peace",
    key="B flat major",
    bpm=90,
    duration_s=90,
    description="Arilou Lalee'lay — gentle quasi-space whisper; state stem = patience",
    sc2_inspiration="references/uqm-source/sc2/content/base/comm/arilou/arilou.mod",
    sc2_idiom="1990s alien-mystical idiom — phase-shifted chimes, dimensional "
              "whisper, gentle major-key chord beds, multitracker chiptune",
    round=2,
    notes="State stem 'patience' is read by src/scz/audio/state_layers.py from "
          "game.flags['arilou_patience']. Starts at 1.0 and only decreases as "
          "the Sage gives up on the Steward.",
    stems={
        **_standard_5stem(
            "B flat major", 90,
            "alien mystical species theme, gentle phase-shifted chimes, dimensional whisper",
            bass_body="warm low sine-wave pulse with subtle pitch-bend modulation, no drums no melody no pads",
            perc_body="soft mallet hits with long reverb tails, very sparse, no melody no bass no pads",
            pad_body="airy major-key choral synth pad with phase-shifting filter motion, no melody no drums no bass",
            lead_body="floating bell-tone melody with bent pitches, contemplative and ethereal, no drums no bass no pads",
            amb_body="time-stretched shimmer and quasi-space whisper textures, no melody no drums no bass",
            sc2_idiom="1990s alien-mystical idiom — phase-shifted chimes, multitracker chiptune",
        ),
        # State stem: PATIENCE — fades as the Sage gives up on the Steward
        "patience": _stem_prompt(
            "PATIENCE-TEXTURE",
            "warm sustained major-7 string pad with gentle calming resonance, "
            "soft choral hum underneath, the sound of waiting indefinitely without "
            "irritation, a presence that has been patient for centuries",
            "B flat major", 90, "patient, calming, indefinitely-waiting",
        ),
    },
)

ANDROSYNTH_PEACE = ContextSpec(
    name="androsynth",
    category="species_peace",
    key="A minor",
    bpm=116,
    duration_s=90,
    description="Androsynth Refugees — human-improvised retro-Atari with warm analog underneath",
    sc2_inspiration="",  # Androsynth had no SC2 comm theme — destroyed pre-SC2
    sc2_idiom="",
    round=2,
    notes="Androsynth = clone-humans from 250,000 years in OUR future, thrown "
          "into the past by an Other 'decursion.' Their sonic identity is "
          "REFUGEE-IMPROVISED: retro-Atari-style PCM blips and warm analog "
          "synth foundations under it. Sounds like humans making do.",
    stems=_standard_5stem(
        "A minor", 116,
        "human-improvised refugee species theme, retro-Atari-on-warm-analog, "
        "making-do-with-what-you-have, slightly melancholy but determined",
        bass_body="warm analog synth bassline with chunky low-end, retro-but-grounded, no drums no melody no pads",
        perc_body="mid-tempo kit with retro-PCM-style snare and hihat, slightly lo-fi, no melody no bass no pads",
        pad_body="warm analog string-pad sustained chords with subtle vibrato, minor-key melancholy, no melody no drums no bass",
        lead_body="bright Atari-era PCM lead melody, brave little tune, slightly off-tuning that reads as 'jury-rigged', no drums no bass no pads",
        amb_body="background ship-hum, distant Atari-blip indicators, warm tape hiss texture, no melody no drums no bass",
    ),
)

MMRNMHRM_PEACE = ContextSpec(
    name="mmrnmhrm",
    category="species_peace",
    key="C major",
    bpm=100,
    duration_s=90,
    description="Mmrnmhrm — cold-precise robot survivors of a prior Culling",
    sc2_inspiration="references/uqm-source/sc2/content/base/comm/chmmr/chmmr.mod",
    sc2_idiom="1990s alien-robot idiom — synthetic precision, mechanical hum, "
              "perfect-frequency tones, multitracker chiptune robotic vocabulary",
    round=2,
    notes="Mmrnmhrm are the robot half of what becomes the SC2 Chmmr after "
          "the merge with the Chenjesu. In our era they're separate — the "
          "robots survived a prior Culling, their organic creators didn't.",
    stems=_standard_5stem(
        "C major", 100,
        "alien-robot precision species theme, synthetic clinical perfection, "
        "no warmth, microsecond-precise timing",
        bass_body="cold square-wave bass with perfectly-quantized pulses, no drums no melody no pads",
        perc_body="electronic kit with crisp clicks and precise hihat patterns, robotic timing, no melody no bass no pads",
        pad_body="sustained sine-wave pad in cold major-key intervals, no human breath, no drums no melody no bass",
        lead_body="precision FM-synth lead with crystalline tones, mechanical melodic phrasing, no drums no bass no pads",
        amb_body="machine-room hum, faint server-rack tones, cold rotating fans, no melody no drums no bass",
        sc2_idiom="1990s alien-robot idiom — synthetic precision, multitracker chiptune",
    ),
)


# ---------------------------------------------------------------------------
# Lemmkin peace theme (NEW SPECIES, 2026-05-17 lore expansion)
#
# Lemmkin = anthropomorphic squirrels with no fear (vestigial amygdala),
# Homesteader-by-CHOICE: they chose to stay so they could SEE WHAT HAPPENS
# with the Others. They will die LEARNING — fearless, curious, slightly off.
# Their theme should sound BRIGHT and CURIOUS and CONFIDENT with a subtly
# WRONG quality you can't quite pin down (no fear should feel uncanny).
# Queued at round=2 — fires when Aaron approves the music expansion.
# ---------------------------------------------------------------------------

LEMMKIN_PEACE = ContextSpec(
    name="lemmkin",
    category="species_peace",
    key="G major",
    bpm=104,
    duration_s=90,
    description="Lemmkin friendly — fearless-curious squirrel troupe; subtly off-bright",
    sc2_inspiration="",  # no SC2 antecedent — Lemmkin is SCZ-original
    sc2_idiom="",
    round=2,
    notes=(
        "Lemmkin sonic identity: bright major-key woodwinds and plucked strings, "
        "lively rhythmic activity, but with ONE subtle quality that reads as "
        "WRONG (a slightly-flat note in the melody, a shifted accent that lands "
        "off the beat, etc.) so the music sounds 'too cheerful for the danger' "
        "the species is in. Aaron's note from the species lore: 'they will die "
        "LEARNING, not believing they'd live.' Foreshadow that."
    ),
    stems=_standard_5stem(
        "G major", 104,
        ("bright lively curious-fearless squirrel-clade species theme, "
         "subtly-wrong-cheerful, foreshadows tragedy under apparent joy"),
        bass_body="pizzicato low strings + soft tuba pulses on the downbeat, "
                  "active walking bassline, warm but slightly off-tempo, "
                  "no drums no melody no pads",
        perc_body="light jaunty hand-percussion: tambourine, shakers, soft "
                  "snare brush, the rhythm of a troupe-investigating-something, "
                  "no melody no bass no pads",
        pad_body="warm woodwind bed: clarinets and oboes in close harmony, "
                 "lightly drifting major-key chord beds with ONE subtly-flat "
                 "tone, no melody no drums no bass",
        lead_body="playful piccolo + plucked banjo-like string melody, bright "
                  "curious phrasing, lively melodic line that climbs confidently, "
                  "no drums no bass no pads",
        amb_body="distant rustling-leaves texture, soft squirrel-chitter under "
                 "the mix, subtle wrong-note shimmer that doesn't quite resolve, "
                 "no melody no drums no bass",
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

# Round 2 — music expansion batch (Aaron approved Round-1 5/5; firing 10 more).
ROUND_2_QUEUED: list[ContextSpec] = [
    # Universal travel (5)
    SYSTEM_TRAVEL,
    HYPERSPACE_PURSUIT,
    QUASISPACE_TRAVEL,
    PLANET_ORBIT_CLOAKED,
    PLANET_LANDER,
    # Combat (2 — combat_low already in Round 1)
    COMBAT_HIGH,
    COMBAT_BOSS,
    # Species peace (4 — Slylandro in Round 1)
    MYCON_PEACE,
    ARILOU_PEACE,
    ANDROSYNTH_PEACE,
    MMRNMHRM_PEACE,
    LEMMKIN_PEACE,
]

# All defined contexts (extends with each round).
ALL_CONTEXTS: dict[str, ContextSpec] = {
    spec.name: spec for spec in ROUND_1 + ROUND_2_QUEUED
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
