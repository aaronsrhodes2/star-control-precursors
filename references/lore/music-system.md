# Music — Contextual, Varying, Never the Same Twice

> Companion to [the-furlings-and-the-others.md](the-furlings-and-the-others.md). Defines the game's music system: what plays where, and how each playback differs subtly from every other playback of the same context.

## Why a variation system at all

In *Star Control 2*, every alien race had a great theme — and every time you met that race, the theme played identically. After your fourth encounter, players stopped hearing it as music and started hearing it as *that sound that means an Ur-Quan*. By the tenth encounter, players muted the game.

This isn't an SC2 problem; it's a video-game-music problem. Limited soundtracks become wallpaper. Players turn them off. The work the composer did is wasted, the atmosphere collapses, and the player plays in silence.

**Star Control Zero's music doesn't repeat.** Every time you enter hyperspace, the hyperspace theme plays — but it plays *slightly differently* than the last time. Tempo nudged. A stem dropped. Lead instrument swapped. Section order shuffled. The melody you remember is still there. The arrangement is fresh.

This is the same design philosophy as the LLM-rendered dialog and the per-individual visual variation: **the assets define a center of mass; the runtime varies around it**. Three pillars, one principle.

## Music Contexts (the "tracks")

Each context has a defined musical identity and a set of variation parameters. Slice scope includes the bolded ones; the rest are full-game.

| Context | Identity | Slice? |
|---|---|---|
| **Hyperspace travel** | Mid-tempo, propulsive, the player's "ship at speed" theme | ✅ |
| **Star system view** | Slower, atmospheric, ambient — exploration | ✅ |
| **Planet surface (rocky)** | Sparse, percussive, ground-level | ✅ |
| Planet surface (gas/primordial/ice) | Distinct atmospheres per type | full |
| **Combat — vs Furling Cleanser** | Tense, conflicted — major-key inflections under minor harmony, "fighting our own" | ✅ |
| Combat — vs creature/rift | Pure adrenaline | full |
| **Tension / Other-ripple near** | Subbass drones, sparse hits, dread | ✅ |
| **Slylandro theme** | Floating, awe-inflected, wind-chime upper register | ✅ |
| **Mycon biot theme** | Ritualistic drums, low chant, dissonant when heresy_level rises | ✅ |
| **Arilou theme** | Pretty, slightly displaced (microtonal lean), cousin-warmth | ✅ |
| **Proto-Ur-Quan theme** | Almost silence — ambient organic textures, no melody | ✅ |
| Other species (full-game) | Each gets a base + variation set | full |
| **Rainbow World seeding (climax)** | The cluster's color signature note is a tone center; theme builds toward placement | ✅ |
| **Council scene** | Stately, deliberative, choral undertones | full |
| **Furling home / cluster of origin** | Warm, slow, evokes memory and loss | full |
| Quasi-space | Different scale (Lydian or Hijaz), "across the curtain" | full |

## Variation Mechanisms (the "knobs")

Each context exposes a subset of these knobs. The runtime picks values seeded by the encounter or moment, so the same scene re-loaded sounds the same — different scenes vary.

### 1. Tempo jitter
**±3-8%** from canonical tempo. Same melody, slightly faster or slower. Most subtle knob; almost always on. Players don't consciously notice but feel the difference.

### 2. Stem mute/unmute
Each track is composed as **4-6 stems** (e.g., bass, lead, pad, percussion, ambient_high, ambient_low). Mute one or two stems per playback. The melody you remember stays; the bed thins. Listen to a hyperspace track three times: once with full mix, once with just bass + lead + percussion, once with bass + pad + ambient. Same identity, three textures.

### 3. Key transposition
**±1 semitone or whole step.** The slylandro theme in F-major one encounter, F#-major the next. Players don't consciously hear "different key" but get a "this feels different" response.

### 4. Lead instrument swap
The lead melody-carrier swaps between **2-3 alternate instruments per track**. Slylandro lead could be ocarina, glass-harmonica, or pan-flute. The harmonic structure is identical; the timbre changes.

### 5. Section reorder
Most tracks have 3-4 sections (intro / A / B / A' / outro). At runtime, shuffle the order of A, B, A' (keep intro first, outro last). A simple permutation pool gives 6 orderings per track.

### 6. Density modulation
Some stems have "sparse" and "full" recordings — the same musical idea at different note densities. Pick one per playback. Sparse Slylandro = lonely; full Slylandro = communal.

### 7. State-driven layers (the per-species twist)
Species themes have **disposition-tied stems** that fade in/out based on the player's relationship with the species:
- Slylandro theme has an `awe` stem and a `worry` stem. Both fade in proportional to current disposition values.
- Mycon theme has an `obedience` stem and a `heresy` stem. As `heresy_level` climbs, dissonant elements fade in.
- Arilou theme has a `patience` stem (drops out as their patience does).
This means **the music narrates the relationship**. By the time you're about to lose the Slylandro, their theme has gone from awe-major to worry-minor without ever sounding like a different song.

## Implementation Approach

### Phase A — Stems and mixing (slice baseline)
- Compose or commission each slice-era track as a **set of 4-6 stems** (24-bit WAV or OGG). Use AI music tools (Suno, Stable Audio, MusicGen) for first-pass generation; iterate by hand or by stem-substitution.
- Render the stems to a single base mix as a fallback.
- pygame's `pygame.mixer.Channel` can play 8 channels simultaneously — easily enough for stem mixing. Each stem on its own channel, runtime volume on each.

### Phase B — Knob layer
- A `music/director.py` module that:
  - Knows the current context (passed from the game scene).
  - Picks the active track for that context.
  - Rolls deterministic-or-random values for each knob using a seed (e.g., encounter ID, or `time()` for ambient contexts).
  - Configures the mixer channels accordingly.
- Tempo jitter via pre-rendered tempo variants (we render the stem at 95%, 100%, 105% tempo at content-build time) OR via runtime resampling (pygame supports this).
- Key transposition the same way — render N pitch-shifted variants at build, pick one at runtime.

### Phase C — State-driven layers (after disposition system exists)
- The species dialog state machine already tracks disposition (awe, heresy_level, patience). The music director subscribes to disposition changes and modulates stem volumes accordingly.
- This is the system that closes the loop with the dialog architecture — *what you say to a species literally changes how their theme sounds the next time you meet them*.

## Anti-Patterns We Avoid

- **Procedural composition** (generating notes at runtime). Too fragile, too easy to get wrong, and we lose the composer's hand.
- **AI music gen at runtime** (Suno/MusicGen calls in real time). Latency and cost don't fit; do this at build time only.
- **Wild variations** that change a track's identity. The variation should be felt, not heard. If a player thinks "this is a different song," we've gone too far.
- **Always-random** variation that prevents the music from carrying narrative weight. The state-driven layers (knob 7) are the most important — they make the music *mean something*.

## Music Library Choice

Default: pygame's built-in mixer (SDL2). Sufficient for stem mixing, channel volume control, and simple effects. No extra dependency.

Upgrades if needed later:
- `pyfluidsynth` for MIDI-driven instrument swaps at runtime.
- `pydub` for offline tempo/pitch shifting at content-build time.
- `librosa` for analysis if we want stem auto-extraction from existing tracks.

## What This Costs

- **Composition time**: each track needs to be authored as stems, not just a stereo mix. Maybe 1.5× the time of a normal mix.
- **Storage**: ~10MB per track at decent quality. Slice has ~10 tracks × 5 stems = 50 stem files × 10MB = ~500MB of audio. Compressible with OGG Vorbis to ~50MB total. Reasonable.
- **CPU**: 5-stem mix at runtime is trivial. We have headroom.

The win — players keep the music on, atmosphere holds across hours of play, the music itself becomes part of the storytelling — is enormous.
