# HANDOFF — anyone → SCZ: Audio Chat

> Cross-chat dispatch queue for **audio work** in Star Control Zero. The Audio chat reads this file at session start, picks up open entries, generates/refines the audio (music, SFX, VO), and marks each `✅ PROCESSED <date>` (or removes it) when done.
>
> Other chats append new entries when their work generates audio tasks. Newest entries at the top.
>
> **Audio lane scope**: music composition + arrangement, SFX library, VO authoring (incl. ElevenLabs voice profiles per `memory/project_voices_future.md`), audio asset directory, audio-pipeline tools.
>
> **Lane discipline reminder**: Audio chat does NOT author lore canon, game code, image assets, or scene wiring. Other chats *describe* the audio target; Audio chat *generates* the sound.

---

## 🗂️ 2026-05-17 — CONSOLIDATED OPEN-WORK SUMMARY (start here)

> The list below is your **session checklist**. Each item links to a detailed entry further down in this doc OR points at the canonical lore source. Voice-profile work is the biggest workload. Mark each `✅ PROCESSED <date>` when complete.

### High-priority — slice catastrophe audio cues

- [ ] **Taalo extermination cinematic audio** — lattice-resonance VO authored ✓ in detail; the cue needs: shambling locomotion SFX (dry stone-on-stone with multi-second pauses); acid-grazing SFX (subaudible fizz + slurry drip + mineralizing chime); extermination silence cue (each Taalo glow-pulse extinguishes in audio in waves); post-Culling orbital flyover canonical *full silence* (no music; resist underscoring)
- [ ] **Burvixese world destruction audio** — brass-fanfare confidence at Caster activation; detuned-corruption as Others arrive moth-to-flame; chorus-cheering goes abrupt-silent in waves; **Caster keeps firing into the silence** (the cruelest sound in the slice); post-destruction Caster low-power harmonic-idle hum that continues across 230kya into SC2 era

### Voice profile authoring backlog — slice species (~16 species)

| Species | Status | Notes |
|---|---|---|
| Slylandro Observer | pending | Drift-think cadence, atmospheric reverb. NPC: Drift-Of-The-Magenta-Cloud-Witness |
| Arilou Sage | pending | Wry, ancient, dimensional-shimmer. NPC: Sage Lwen-Olou |
| Mycon Biot | pending | Collective chorus + FIRST_WHISPER subset |
| Proto-Ur-Quan / Proto-Qor-Ah | low-priority | Pre-sentient vocalizations only, not speech |
| Androsynth (Coel Tessar) | pending | Time-displaced human clone — accented terran |
| Mmrnmhrm Sentinel | pending | Robotic, ~3-8My old, wry awareness. NPC: Sentinel-Defense-Loop-Cohort-Forty-Seven-Theta |
| Chenjesu Collective | pending | Slow present-tense, crystalline resonance. NPC: Far-Memory-Spire-Of-The-South-Reef |
| Burvixese | pending | Four-armed engineer — confident pre-activation, anguished post-failure. NPC: Velmek-Resonant-Forty-Three, Caster-Foreman |
| Utwig (pre-doctrine) | pending | Lucid, anxious-enthusiastic. NPC: Vell-Of-The-Open-Face. **Doctrine-Master variant**: Vell carrying 17 prayer scrolls / blessing-the-bench style |
| Utwig (post-doctrine) | pending | Devolved, mask-muffled chant. NPC: Korm-Of-The-Folded-Veil |
| Taalo (Witness fragment) | **detailed spec exists** ✓ | Slowest VO of any species; lattice-resonance substrate-hum; mountain-thought interjection cue |
| Thinn (We-Who-Witness-the-Edge) | pending | Warm, slow, cheerful, *unhurried by ignorance*; ribbon-membrane glass-instrument; literal-rhetorical-question-answering; **canonically dumb** |
| Lemmkin (Brisk-Ever-Onward / Snip) | pending | High-pitched, fast, chittery, no hesitation markers, frequent self-interruption, **cheerful even when discussing extermination** |
| Melnorme (Vermilion) | pending | Ionization-pattern, "Carbon-pattern," "Captain-form" |
| Stelloth (Tarvel-Three-Voices) | **detailed spec exists** ✓ | THREE-VOICE HARMONIC CHORD with offset timing |
| Selvenne (Choir-Of-The-East-Reef) | **detailed spec exists** ✓ | Underwater layered chorus + qualia-transfer first-person-Steward voice |
| Mrokon (Vrek-The-Eighth-Body + Operator) | **detailed spec exists** ✓ | Puppet (gruff, formal, vocoder-artifact) + Operator (smaller, softer, child-sized) |
| Kovellim (Ovala-Eight-Crossings) | **detailed spec exists** ✓ | Deep, slow, cyclical; "in the cycle of" idiom |
| Karavem (Veled-Of-The-Canyon-Wall) | **detailed spec exists** ✓ | MUSIC IS LANGUAGE; three simultaneous notes; emotional-valence-reversal (major=sad/formal, minor=joyful/exploratory) |

### Voice profiles — Furling NPCs (~10 named characters)

| Character | Role | Notes |
|---|---|---|
| Commander Halia | Persuader-faction Mh-Lai commander | Already implemented in code; needs voice now. Warm, authoritative |
| Mraka Yenn-Sa | Pilot crew | Warm, technical, grief-under-the-fluency (lost-Migration-family backstory) |
| Bren-Vor Telcas | Weapons Officer crew | Clipped, precise, sister's-name-once-and-never-again |
| Yelena Lwen-Tar | Engineer crew | Young, direct, faintly flirtatious *with the ship* (not the Steward) |
| Mira-Rou Halve-Tel | Medic crew | Thoughtful, biological-vocabulary-rich |
| Tarven Olwen-Sa | Navigator crew | Bookish, uses prior-Stewards' formal titles, charming, slightly intimidated on the bridge |
| Vael-Souren | Cleanser climax NPC | **Testing feedback: should be GENTLE, never triumphant.** Quiet, weighted, doctrinally certain but emotionally cost-aware |
| Vesh Vasa-Lon | Dnyarri encounter Survey Commander | **Testing feedback: professional-but-troubled register.** Carries the weight of the recommendation |
| Furling Archivist / Warden / Tunneler | Shop-buyable crew (generic NPCs, not unique) | Lower-priority; can share voice patterns |
| **Soren Kel-Var** (Mraka's Last Race side-quest) | Furling Drifter, ~40 years; over-comm voice only | **Weathered**, defeated dignity; *quiet apology under the words*; uses Drifter-circuit vocabulary the way Mraka does. The voice that says *"Mraka. You came."* and means it after 12 years |
| **Karol-Vere Belt-Tar** (Bren-Vor's Aimer's Verdict side-quest) | Furling Cleanser officer, ~55 years | **Formal, procedurally confident, cold-warm**; the cover-up is *under* the voice (audible only as faint tonal stiffness when Velt-Ra's journal is mentioned); the voice that defends doctrine without raising its volume |
| **Mev-Tar Lwen-Tar** (Yelena's Last Hull side-quest) | Furling Senior Mh-Lai assembly chief, ~50 years | **Warm, tired, emotionally-weighted**; the voice of a mother who built ships and now watches the last one ship out; strong family resemblance to Yelena's voice in cadence and warmth |
| **Iren-Vor Olwen-Veth** (Tarven's Erased Logs — recorded voice only) | Deceased prior Steward, ~45 years at recording time | **Calm, tired, the weight of a secret chosen-not-to-share**; the recorded voice should have a faint *50-year-old recording artifact* — slight band-limited frequency response, subtle warmth-decay. The voice that says *"If you are hearing this, you are a future Steward"* and means the loneliness of waiting for someone to find it |
| **Velt-Ra Telcas** (Bren-Vor's Aimer's Verdict — journal-reading; deceased) | Bren-Vor's deceased sister, ~25 at writing | **Bren-Vor reads her journal aloud**; her voice is heard through *his* voice — the audio production should hint at this gently (his voice subtly carries her cadence as he reads, almost a possession-by-grief effect). Brief, hauntingly personal |
| **Sevreth's Child** (Mira-Rou's Deep Child's Cradle — allow-emergence branch only) | Tiny biot-class sentient being | **NOT VERBAL** — communicates via chemical signals + faint sub-audible humming. Audio cue: a gentle, harmonically-pure pad that *responds* to nearby dialog with slight pitch-bend or amplitude modulation. Mira-Rou translates Sevreth's Child's signals into prose for the player; the player never hears words from Sevreth's Child directly |

### Module-class audio cues

- [ ] **Decursion** signature weapon (Others' Vessel — see Hijack quest): *temporally-recursive* feel; the projectile should sound like its echo arriving before itself; distinct from any other weapon
- [ ] **Hammer-Round** (Mrokon weapon): heavy kinetic-impact with dimensional-resonance overtones; the canonical sound of *marking the predator*
- [ ] **Quasi-Space portal entry/exit** audio cue (Arilou path)
- [ ] **Time Drive engage** audio (already in canon — reverse-running high-pitched chime)

### Music cues for slice beats

- [ ] **Tutorial Beats 1-7 musical bed** — varies by beat per music-system.md
- [ ] **Distress Beacon cinematic music** — Beat 4 milestone
- [ ] **Cleanser climax music** — gentle-not-triumphant per Vael-Souren voice direction
- [ ] **Bio-Archive contemplation bed** — quiet, archival, reflective
- [ ] **Taalo contemplation-cove ambient bed** — slow drone-pad + sparse mineral-bell tones + lattice-resonance substrate-tone (detail in existing entry below)
- [ ] **Andromeda arrival epilogue** — bittersweet hope; the Migration's payoff; the canonical "we made it" cue

### Per-encounter variation requirement (Phase 3+ work, per `music-system.md`)

Music **never repeats identically** — tempo jitter, stem mute/unmute, key swaps, disposition-tied layers. The Audio chat eventually owns the variance system. For slice MVP, fixed beds are acceptable; the variance system is post-MVP.

---

## 2026-05-17 — Combat audio — full per-ship + per-weapon library (Design chat request)

**Origin**: Design chat. The combat scene is mechanically complete (17 ships, 12 weapon patterns, 5 specials) but ships silently — there are zero audio cues anywhere in `MeleeCombatScene`. This is the biggest single audio gap in the slice. Roughly **17 ships × 3 sound types + 12 weapon patterns × 1-2 sounds + 5 specials × 1 sound = ~80 distinct cues**, but per-pattern reuse cuts that to ~30-40 actual files.

**Engine state (Design chat already shipped):**
- [src/scz/combat/scene.py](src/scz/combat/scene.py) — `MeleeCombatScene` has hooks ready at: ship-spawn (`on_enter`), per-frame thrust (`action.thrust=True`), primary fire (`_fire_primary`), projectile-on-ship hit (`apply_damage`), ship death (`alive=False` transition), special activate (`_update_ship_special`)
- Currently silent — no `pygame.mixer` calls in combat
- Audio path convention (Design will wire when assets land): `assets/sfx/combat/<category>/<id>.ogg` for SFX; the engine loads on demand and caches per session

### Required output — three tiers

**Tier 1 — universal combat cues (3 files)**. These play regardless of which ship/weapon — they handle the cases that don't need per-ship variation.

| File | When it plays | Direction |
|---|---|---|
| `assets/sfx/combat/hit_shield.ogg` | Projectile contacts shielded ship; shield > 0 | Crackling electromagnetic discharge; ~200ms; mid-cool palette |
| `assets/sfx/combat/hit_hull.ogg` | Projectile contacts ship hull (shield 0 or pierced) | Metallic impact + brief structural creak; ~250ms; punchier than shield |
| `assets/sfx/combat/ship_destroyed.ogg` | Ship's `alive` flips False | Explosion + venting + dwindling crackle; ~1.2s tail; the dramatic one. SC2 reference: the satisfying shipdies.wav |

**Tier 2 — per-primary-pattern fire sounds (12 patterns, ~10 distinct files since some share)**. Played on `_fire_primary` invocation. Each pattern has its own character:

| Pattern | Used by | Sound direction |
|---|---|---|
| `single` | Furling Scout, Compeller, Slylandro-canon-removed, Utwig, Sentry Drone | Crisp pulse-laser ping. Furling Scout is the canonical "default" combat sound — make it feel like *home* |
| `twin` | Cleanser Cruiser | Two overlapping single pulses, ~30ms offset. Reads as "heavy double-tap" — slightly menacing |
| `triple` | (currently unused; reassigned to charged) | Three overlapping pulses, wider spacing. Skip if unused |
| `multi_spread` | Mmrnmhrm Sentinel, Burv Broadcaster | Volley fan — single pulse with subtle reverb-tail suggesting fan-spread |
| `scatter` | Lemmkin Skitter | Rapid 5-pulse burst, ~15ms apart, with crackle texture. Reads as "shotgun" |
| `burst` | Persuader Vessel | 3 tight clicks then short tail — *measured* not aggressive. Carries the diplomat tone |
| `lance` | Thinn Blade | Long thin charge-discharge — hold-then-release feel. The longest single fire sound (~600ms) |
| `homing` | (currently unused; reassigned to tier_plasma) | Curving whine + Doppler tail. Skip if unused |
| `tracking` | Arilou Skiff | Sharp focused beam ping with reverb — reads as "auto-aim laser tracks lock" |
| `bubble` | Androsynth Cruiser | Wet plasma launch + low resonant *bloop* on release. Reads as soft, organic |
| `returning` | Proto-Qor-Ah Marauder (RHC) | Heavy thud-launch + sub-bass tail (the SC2 RHC was iconic — borrow the spirit) |
| `tier_plasma` | Melnorme Trader | Three distinct release sounds — tier1 small (high-pitched ping), tier2 medium (deeper *whump*), tier3 big (sub-bass *KA-CHUNK*). One file per tier OR a layered sample with tier mapped to playback variant |
| `charged` | Defender Vessel, Proto-Ur-Quan, Mycon Podship | Slow charge-up + heavy *boom* release. Sub-bass dominant. SC2 Ur-Quan fusion bolt is the spirit |

**Tier 3 — per-special-ability sounds (5 specials, 5 files)**. Each special is held/triggered through `_update_ship_special`. Looping vs one-shot is per-special:

| Special | Used by | Activation cue | Loop while held? | Release cue |
|---|---|---|---|---|
| `inertia_halt` | Furling Scout | Quick pressurization *hiss* → stasis-tone hum (sustained pure sine, ~80Hz fundamental + harmonic) | YES — quiet stasis hum | "Whoosh" releasing motion back |
| `teleport` | Arilou Skiff | Sharp gate-opening crackle + harmonic-resolution chime | NO (instant) | (none — same activation sound on arrival side) |
| `blazer_form` | Androsynth Cruiser | Power-up surge → "comet roar" engine layer | YES — sustained jet/plasma roar (mid-aggressive) | Power-down whine |
| `fried_discs` | Proto-Qor-Ah Marauder | Mechanical-deployment clicks → 4 disc spin-up | YES — rotating-blade *whirr*, faintly ominous | Wind-down (discs retracting) |
| `regen_hull` | Mycon Podship | Wet organic-bloom release → sustained low-frequency healing-pulse | YES — quiet pulsing organic *throb* | (cuts off cleanly) |

### Per-ship engine drone (Tier 4 — nice-to-have, can defer)

While each ship is in combat, a faint engine drone localized to that ship would tie the soundscape together. ~17 ships × distinct drone is a lot of work; the easier alternative is **3 generic drones by ship-class** (light/medium/heavy) tinted by per-ship pitch:

- `assets/sfx/combat/engine_light.ogg` — fast/light ships (Furling Scout, Arilou, Lemmkin, Sentry Drone). Higher-pitched, faster pulse
- `assets/sfx/combat/engine_medium.ogg` — most mid-tier
- `assets/sfx/combat/engine_heavy.ogg` — heavies (Cleanser, Defender, Proto-Ur-Quan, Mycon, Utwig, Compeller). Deep rumble, slower pulse

The combat engine will pitch-shift these per-ship for variation when it wires the playback path.

### File format + length conventions

- **Format**: `.ogg` vorbis (pygame mixer reads natively); fall back to `.wav` if vorbis is awkward
- **Sample rate**: 44.1kHz or 48kHz
- **Channels**: mono for SFX (the engine spatializes via panning later); stereo OK for big destruction/special cues
- **Length budget**: per-shot fire sounds ≤ 400ms; specials' loop layer ≤ 2s with clean loop point; destruction ≤ 1.5s

### Naming convention

- Per-pattern fire: `assets/sfx/combat/fire_<pattern>.ogg` (e.g. `fire_lance.ogg`, `fire_scatter.ogg`)
- Per-special: `assets/sfx/combat/special_<ability>_activate.ogg`, `special_<ability>_loop.ogg`, `special_<ability>_release.ogg`
- Universal: as listed in Tier 1 table

### Acceptance

- [ ] Each Tier-1 file plays without distortion at typical volume
- [ ] Per-pattern fire sounds are distinguishable from each other in blind A/B
- [ ] Special-ability loops have clean loop points (no click)
- [ ] No single sound is so loud that it masks the others during combat clutter
- [ ] Per Aaron's preference, none of these compete with VO/dialog tracks

### Status

- ☐ Open as of 2026-05-17
- Tag `✅ PROCESSED <date>` per file or per tier when complete

### Cross-references

- Engine wiring lives in [src/scz/combat/scene.py](../../src/scz/combat/scene.py) — Audio chat doesn't touch this; Design will wire playback once assets land
- Ship roster + special_ability fields defined in [src/scz/combat/ships.py](../../src/scz/combat/ships.py) for canonical names
- Voice/music backlog already in this doc — combat SFX is *additional* work, not a replacement

---

## 2026-05-17 — Taalo lattice-resonance VO + slice-defining silence cue

**Canon source** (lore docs: [species-sheets.md §9 Taalo](species-sheets.md), [species-quests.md "The Shield That Will Not Hold"](species-quests.md), [HANDOFF_image_chat.md "Taalo shield-tragedy reframe"](HANDOFF_image_chat.md))

The Taalo are the slice's defining-tragedy species — silicon-substrate mountain-cognition, geological tempo, terminal Eliminated regardless of Steward action. Audio needs:

### Voice profile — Taalo Witness fragment

- **Tempo**: very slow — **slowest of any slice species' VO**. Multi-second pauses between phrases. Mountain-tempo.
- **Vocal character**: lattice-resonance — deep substrate hum that the formed words emerge *from*, rather than being delivered *on top of*. Suggested approach: synthesize a base sub-audible substrate-tone (very deep, lattice-like, slow waver) and the spoken phrases ride above it, almost as if the mountain itself is the voice and the Witness fragment is articulating-on-behalf-of.
- **Mountain-thought interjection**: occasional weight-shift to a *longer phrase, deeper resonance frequency* — the mountain-thought interrupting or extending the fragment's individual articulation. The translator marks these as *"the slow stone considers."* Audio cue: drop the F0 by ~30%, lengthen phrase duration by ~2x, swell the substrate-tone.
- **Cannot translate**: lying, urgency, despair, the concept of leaving home. The voice should be *incapable* of speeding up. Performance direction: never hurry, even when content is emotional. Brave melancholy, never desperation.

### SFX — Taalo locomotion + acid-grazing

The Taalo's body-physics and feeding behavior have **non-VO sound footprints** in the slice that the Audio chat should design:

- **Shambling locomotion**: the Taalo's gait is a heavy patient lurch (Horta-style — Star Trek TOS *"The Devil in the Dark"* visual lineage; see HANDOFF_image_chat.md). Sound profile: **dry stone-on-stone scrape with multi-second pauses between weight-shifts**. Each step is a low *grind-thump* with substrate-resonance underneath; the gait sounds like patient stone-on-stone, not feet-on-ground. Loop the cycle with irregular pacing — Taalo don't have a metronomic walk. Multiple fragments moving together create a slow rhythmic stone-percussion that the contemplation-cove ambient bed should incorporate.
- **Acid-grazing (Taalo feeding)**: a Taalo at rest by a rock face is *eating* it — secreting slow corrosive mineral acid that bores a shallow chamber over hours. Sound profile: **a very slow soft fizz, like a chemical reaction at low intensity** — quieter than the locomotion grind, almost subaudible, but present whenever a fragment is paused in feeding-posture. Pair with a *very slow drip* of dissolved-silicate slurry (every 10-30 seconds), and the *slow accretion* of the slurry into the fragment's plate-margins (a soft mineralizing crystallize-sound, like a faint chime). The contemplation-cove ambient bed should include faint acid-fizz in the background — many Taalo around the cove are feeding while the dialog plays.
- **Plate-glow modulation**: when a Taalo's lattice-glow pulses, no sound necessarily plays — but if Audio wants to give the glow an audio counterpart, a very subtle *sub-bass swell* timed to the visible glow-rise (and a soft *substrate-detune* on the fall) would work. Optional; the visual carries the moment fine on its own.
- **Sample lines** (from species-sheets.md §9 — for VO test recordings):
  - *"The slow stone considers. The visitor returns. We are pleased — in the way of mountains."*
  - *"The Shield will be built. We do not know if it will hold. The work is the dignity. The work is the not-despairing."*
  - *"You are the fourth Steward to walk this ridge. The third sat where you are sitting now. She was kind to us. We remember."*
  - *"We know we are going to die. We will not be hurried about it. We will not pretend otherwise. We will not abandon dignity to fear."*
  - *"The Shield activates tomorrow. By the season after, we will be silent. The work is the dignity. Walk with us today."*

### Music cue — Taalo extermination scene

- **The slice's quietest beat by design.** The image-chat HANDOFF specifies *"no music recommended; just the lattice-resonance audio fading."* This is the canonical direction.
- Audio chat's task here is **the absence of music handled well**: as the Shield activates and fails and the Taalo are consumed, the lattice-resonance tone *fades out* — not silenced abruptly, but each Taalo glow-pulse extinguishing across the visible range is mirrored audibly by a tone in the substrate-resonance going silent one by one. The **acid-fizz feeding-sounds also fade out** in parallel — each Taalo's individual feeding ends as the fragment's body-chemistry stops. The shamble-grind footsteps go quiet last (any Taalo still moving when the Others arrive). The final state is *full silence*. Hold the silence for the visual hold on the empty mountain.
- **Humor-doctrine zero** is canonical here — no comedic music, no jaunty Furling motifs even in the Steward's POV music. Just the lattice resonance, then nothing.
- **Post-Culling orbital flyover audio (separate cue)**: when the Steward returns later and sees the silent planet from orbit (the canonical "planet now reads as just rocks" image — see HANDOFF_image_chat.md "Taalo post-Culling planet view"), the audio is *fully silent* on the Taalo's side — no resonance, no fizz, no shamble. Just the Furling ship's ambient hum. **The silence is the audio**. Resist the temptation to underscore the moment with strings; the dignity is in the restraint.

### Music cue — Contemplation cove (Taalo dialog backdrop)

- The contemplation-cove is where Steward-Taalo dialog happens. It's a *quiet, patient* music bed — distinct from the extermination scene's silence.
- Suggested: a very slow drone-pad (~40-50 bpm equivalent, but mostly arrhythmic), with sparse mineral-bell tones at irregular intervals (~every 8-15 seconds). The lattice-resonance substrate-tone underneath, *softer than during VO*, just enough to feel the mountain's presence.
- Loops cleanly for the duration of the dialog (which is long-paced by design).

### Status

- ☐ Open as of 2026-05-17
- This entry was migrated from `HANDOFF_image_chat.md` (where it was originally seeded before the Audio lane existed). Image chat handles the visuals; Audio handles the lattice-resonance VO + music cues.

---

## 2026-05-17 — Halia banter performance direction + post-Fall crew reaction audio

**Source**: `references/lore/halia-steward-banter.md` + `tools/quest_inventory.csv` 5 post-Fall mini-quests.

The Halia-Steward banter library is the slice's biggest emotional investment outside the Fall cinematic itself. Audio production carries it.

### Halia banter performance direction

- **Register**: *warm-dry-direct*. Bone-dry humor, never showboaty. The voice of a senior captain who has earned the right to be gentle.
- **Halia's canonical verbal idioms** must be delivered with deliberate flat-affect — *the joke is in NOT signaling the joke*:
  - *"That was a compliment"* — delivered with the same matter-of-fact tone as an actual order
  - *"I'm telling you that as your friend, not your commander"* — the ONE place Halia's voice softens; the dry register breaks slightly
  - *"Drink the tea"* — closes scenes; warm but firm
- **Voice states** to track:
  - `commander_formal`: Council-channel; brisk; minimal personal register
  - `commander_warm`: Mh-Lai docking comm; her default with the Steward
  - `friend_private`: tea-visit conversations; warmest; canonical mother-conversation lives here
  - `late_mid_tightening`: ~3-1 weeks before Fall; warmth + faint anticipatory weight
  - `post_fall_alive_persuader`: alive-survivor variant; quiet weight; *more patient than before*
  - `post_fall_dead_recording`: final-state-seal artifact + slow composure (already canonical from the Fall dispatch)
  - `post_fall_cleanser_supervised`: metallic edge from Cleanser-channel review; short formal sentences; the friend is in there but the channel is between her and the Steward

### The Steward's banter voice

- *Warm-deadpan*. Wit slightly less sharp with Halia than with alien species (canonical respect signal).
- Self-deprecating in the friend-private register.
- The canonical *"Drink the tea, Halia"* line (Steward turning Halia's tea-order back on her) marks the moment their relationship reached *equals* — performance should land this gently.

### Player-driven tea-visit canonical scene

The ~2-weeks-before-Fall tea visit (in Halia's Mh-Lai office) has a **canonical 4-5 minute extended conversation** where Halia talks about her mother (Persuader Vala Telven-Mar, deceased ~3 years before slice). This is the slice's **deepest pre-Fall Halia moment**.

- **If the player triggers it**: full audio scene; Halia's voice in `friend_private` register; the *"I think she would have liked you"* canonical line lands quietly; tea-service ambient (cup-on-saucer, soft pour); the Furling fur-aesthetic muting effect is heavy in this scene (intimate, quiet)
- **If the player misses the trigger window**: the scene NEVER plays. The canonical line is permanently lost. **Do not retro-fit this; the loss is canonical.**

### Post-Fall crew reaction audio

5 new mini-dialogs in the Common Room post-Fall. Audio reuses the per-crew voice profiles already documented (Mraka warm-technical, Bren-Vor clipped-precise-controlled-grief, Yelena vibrant, Mira-Rou thoughtful, Tarven bookish-charming) but with **post-Fall mood markers**:

- **All crew speak more slowly than usual**
- **Pauses are longer than usual** — the canonical Furling fur-muting effect is heavier in the Common Room post-Fall
- **Mraka**: voice catches on *"the Olwen-Veth memorial site, which is now... I don't know what it is now"*; canonical small voice-break
- **Bren-Vor**: voice goes *flat* (his trained-Defender register he hasn't used since recruitment) only in the Cleanser-supervised branch; in other branches his voice is *the controlled grief he uses for Velt-Ra*
- **Yelena**: voice catches on *"Twelve-Forty-Eight is the LAST"*; one of the slice's quiet-devastating lines
- **Mira-Rou**: voice is *quietly fierce* throughout; she does not break. If Sevreth's Child is alive, the chemical-signal humming intensifies briefly during her line; Mira-Rou translates with a small smile (first smile since the Fall)
- **Tarven**: voice is *wet* (his eyes are wet); the eternal tea-cup is empty — *audible silence where the cup-clink usually is*

### Common Room post-Fall ambient bed (recap from prior dispatch)

The Common Room ambient bed post-Fall:
- Ship-system hums softer
- Yelena's workbench tools STILL (no tap-tap-tap)
- Tarven's tea-cup empty (no clink)
- Bren-Vor's weapons-cleaning kit closed (no mechanical clicks)
- Mira-Rou's amphora hum is now the LOUDEST ambient layer (it was barely audible before; it is the room's anchor now)
- Fur-muting effect is heavier — every footstep, every breath, more cushioned

### Status

- ☐ Open as of 2026-05-17 — pairs with the Fall of Mh-Lai dispatch. **The pre-Fall banter is half the emotional load; the post-Fall reactions are the other half.** Voice production is the slice's most important audio investment.

---

## 2026-05-17 — Combat + Crewmate Banter Library (voice direction)

**Lore source**: `references/lore/banter-library.md` (NEW). ~300 lines of canonical banter content. Voice production for combat-state + Common Room delivery.

### Per-species combat-banter voice direction

All voices retain their canonical voice-profile from this doc's species table. Combat banter adds **damage-bracket escalation** to the existing voice register:

| Species | Opening (>75%) | Mid (50-75%) | Pressed (25-50%) | Desperate (<25%) |
|---|---|---|---|---|
| **Steward** | Playful-warm-deadpan | Sharper wit; *committed* | Wit cracking slightly — *"Halia would have something dry to say here. I do not."* | Witty-desperate — *"Yelena, the whatever-it-is is making the bad noise"* |
| **Cleanser** | Quiet-doctrinal | Same quiet but *insistent* | A single-volley-pause line | *"I am sorry, Steward."* — never triumphant; always grieving |
| **Drev-Tok** | 2-years-of-grievance held in formal stillness | Sharpening; sub-vessel taunts | Phase-2 split — voice fragments slightly across 3 sub-vessels | Phase-3 final volley — voice cracks ONCE (the canonical conversion-line frequency) |
| **Mrokon (Vrek)** | Gruff puppet voice + deep-link vocoder artifact | Same; *Operator-switching* register | *"Operator switches to the eighth puppet"* — flat | Quietly fatalistic; *"The Hammer is not for you, Steward"* |
| **Thinn** (canonical) | Warm-slow-cheerful | Cheerful-confused; *"this is novel"* | Cheerfully bewildered; *"the doctrine had not specified what to do here"* | Cheerfully resigned (canonical Thinn doctrine — never desperate; just *quieter*) |
| **Forward** | Same Thinn base + singular "I" + sharper edge | Sincere geometric observations | Still sincere; *"I am taking damage. This is novel."* | Sincere-not-funny doctrine maintained throughout (the joke is in the listener) |
| **Lemmkin** | Excited! Loud! Many questions! | More excited! Pip is taking notes! | Frantically curious! | **Cheerful even at 0% hull** — canonical *"We are dying! It is interesting!"* register |
| **Karavem** | Musical — descending C minor → modulating | Joyful F♯ minor (canonical minor=joy reversal) | Fast staccato counterpoint | Sad C major (canonical major=sad reversal); single descending phrase — the SLICE'S SADDEST POSSIBLE CADENCE |
| **Kovellim** (Ovala) | Deep slow cyclical; *"in the cycle of"* | Same; veteran-weary | Same; Cycle-Fold engages with a sub-bass swell | *"Eight knot-scars. The ninth will form during the crossing"* — composed, weighted |
| **Stelloth** | Three-voice chord with offset timing | Same with Witness click-rate doubled | Counter's bass drops in pitch (grief tone) | Murrer-cord-fraying tone — the chord visibly *cracks* in the audio |
| **Mmrnmhrm** | Robotic + wry awareness | Same; *"Defense doesn't work. Try anyway."* | Defense-loop hits canonical limit | First-Makers tribute register — the only time the Sentinel-voice softens |

### The Others' Vessel banter — Steward-only

The Others canonically don't speak. Steward lines during Others' Vessel combat fire alongside the canonical Others' audio (sub-bass anti-tone + reverse-tinnitus from the Fall-of-Mh-Lai canon). Steward should sound *increasingly tense* through the brackets. **The crew banter during Others'-Vessel combat is critical** — each crew's active ability gets a brief voice-line as they activate it:

- **Mraka**: *"Steward — evasive burst, port-aft. Now."*
- **Bren-Vor**: *"Targeting the dimensional-substrate intersect. Fire."*
- **Forward**: *"I see the predator from a fourth-dimensional angle. They are unsettled by being seen. Fire — now."* (Forward's sincere-not-funny register is *especially unsettling* here — the canonical Furling humor breaking against canonical horror)
- **Yelena**: *"Shield-recharge cycle. I am holding it."*
- **Mira-Rou**: *"Bio-Signature Dampening — engaging."*
- **Tarven**: *"Deep archive cross-reference says — they have a pattern. The pattern is —"* (decursion hits; line cuts off; the *unfinished sentence* is canonical)

### Common Room Steward-crew banter voice direction

Each crew NPC's Common Room voice maintains their canonical voice-profile but with **slightly softer cadence** than mission-context lines — they're in the safe space; they speak less formally.

- Mraka: warm-technical; *occasional voice-catch* on Olwen-Veth references
- Bren-Vor: clipped; *long silences are content*; he says Velt-Ra's name *once per conversation*
- Forward: same Thinn-base sincere register; in Common Room he *sometimes* uses "we" reflexively when stressed (canonical lapse back into pre-rebellion pronouns; reveals the cognitive cost of his individuation)
- Yelena: vibrant; *talks while working*; tools tap-tap-tap audible underneath
- Mira-Rou: thoughtful-quiet; *the amphora hum is louder than her voice* at moments
- Tarven: bookish-charming; *eternal tea-cup clink* audible; *loses track of original question* canonically — voice trails off mid-sentence into a different topic

### Cross-crew banter

Cross-crew dialogues should have **layered voice production** — both crews audible; ambient bed ducks slightly; the canonical fur-muting effect *cushions* both voices.

### Status

- ☐ Open as of 2026-05-17 — pairs with Design's banter trigger system + Image's Common Room scene. The banter is the slice's *character-voice payoff*.

---

## 2026-05-17 — **SLICE TERMINAL**: The 6 Endings audio

**Lore source**: `references/lore/the-endings.md` (NEW). 6 canonical endings; each with distinct music and audio register.

### Per-ending audio specification

| Ending | Music | Audio Atmosphere | Final canonical narrator line delivery |
|---|---|---|---|
| **Best** | Crossing-Opens triumphal cue (from Final Conflict dispatch) + **unified crew themes** woven through the Andromeda-arrival montage; canonical *"a funeral that has become a procession of hope"* mood; ~3 minutes | Warm; full Furling fleet engine-sounds; resettlement-cinematic ambient (Kovellim ceremony chant, Karavem canyon-singing in Andromeda, Selvenne reef bubbling into new ocean-worlds, Lemmkin chittery delight as archives unpack, Mrokon memorial gong) | *"We continue."* — Steward's voice; warm, weighted, quietly proud |
| **Great** | Same triumphal cue but slightly compressed; ~2.5 minutes; a *thin note* canonically signals "we missed a thing" (a single sustained held minor-key tone briefly underneath the triumphal major) | Same as Best but with the missing-crew-arc beats *audibly absent* (the silence where their canonical sound would have been) | *"We continue, mostly."* — Steward's voice; warm but a small held-back tone |
| **Good** | Triumphal cue but with *held-back joy*; canonical *"the room is smaller"* feel; ~2 minutes | Cooler ambient; emptier crew-themes (the missing crew's musical signature simply absent; the Common Room sounds *quieter* in the epilogue scene) | *"The home is smaller than I hoped."* — Steward's voice; warm-but-melancholy |
| **Successful, at a cost** | Bittersweet — a major key that DOESN'T resolve fully; ~90s; canonical *unresolved cadence* (musical-theory term for *"we got there but the chord doesn't land"*) | Ambient is cool grey + amber; the canonical *"the warmth has receded"* mood; some Migration vessel engine-sounds *cut off mid-tone* representing the lost-in-transit vessels | *"The dignity is in not pretending otherwise."* — Steward's voice; pragmatic, slightly hollow |
| **Unsuccessful** | **NO triumphal music**. Quiet ambient drone; sub-bass anti-tone from the Others' canonical audio signature LINGERING (the galaxy is consumed; their substrate-frequency is now the background hum); the Steward's breath audible | Deep quiet; canonical *"the Steward alone in Andromeda"* register; faint *galaxy-being-consumed-forever* low-frequency hum that NEVER fully fades; the Migration fleet's absence is the dominant audio fact | *"I am the only one. The galaxy is the kitchen now. I will tell Andromeda what we were. I will hope no one comes back."* — Steward's voice; tired, weighted, alone |
| **Disastrous** | **NO MUSIC AT ALL.** Absolute silence except: the Steward's negotiation-broadcast transmission (canonically pathetic — they speak the Council-channel formal lines Halia trained them to use; the silence answering them is the canon); then the Others' approach (the sub-bass anti-tone + reverse-tinnitus artifact from the Fall of Mh-Lai canon, but DEEPER); then the Steward's death (implied audibly — a brief sharp cut; the comm goes flat-line); then the treaty-blood-imprint sound (a wet *impression-stamp* sound — canonically the Others using Steward blood as ink); then a long full silence (~10 seconds) | Absolute audio bareness. The viewer/listener hears their own breathing. The silence IS the cinematic | *"You led negotiations to hand over the galaxy to the Others, for all time, and then they ate you and used your blood to sign the treaty. Good job."* — narrator voice (NOT the Steward; canonically the slice's wry-bitter Furling-humor-doctrine narrator). Delivered with *deliberate cheerful inflection* on *"Good job"* — the dark-comedy punchline lands because the narrator is *taking a small bow* |

### Disastrous ending — special audio direction

The Disastrous ending is the slice's *audio masterpiece*. It must achieve **absurdist-horror-comedy** in a single landing — the cinematic IS funny, but the funniness is *cosmic-bureaucratic* (the Others SIGNED a treaty; the treaty is REAL; the Steward's blood is the INK), not slapstick. The wry-bitter *"Good job"* punchline must be delivered in the canonical Furling-humor-doctrine register — *gentle, slightly disappointed, slightly amused*. Performance reference: a teacher who has watched a student do something catastrophically wrong and is now mildly impressed by the precision of the failure.

The audio production should NEVER signal that the line is meant to be funny. Like Forward's 2D jokes — the comedy is in the LISTENER'S recognition, never the speaker's delivery.

### Crew theme unification (Best ending only)

The Best ending's triumphal cue should weave **every recruited crew's musical signature** into the orchestral fabric:
- Mraka's Drifter-circuit motif (woodwind)
- Bren-Vor's Aimer-tone OR Forward's chromatic-ripple Thinn signature (depending on which weapons officer is recruited)
- Yelena's Lwen-Tar-family warmth motif (warm brass)
- Mira-Rou's Halve-Tel pad (subtle string-pad)
- Tarven's prior-Steward-archive motif (harp arpeggios — canonical archives-being-read sound)

This is the ONLY moment in the slice where all crew themes are simultaneously audible. It is the slice's most musically maximal moment.

### Music for the Andromeda resettlement frames (Best/Great)

Each resettlement sub-frame can have a brief musical signature from that species:
- Kovellim ceremony: deep slow cyclical chord (canonical Kovellim VO base)
- Karavem canyon-singing: actual Karavem six-part harmony in major-key reversed-valence-meaning (per their canon)
- Selvenne reef-arrival: layered chorus + bubbling water ambient
- Lemmkin archive: cheerful chittery sub-track
- Mrokon memorial: a gong + naming-of-names sequence (canonical: dead Mrokon Operators named at the memorial)

### Status

- ☐ Open as of 2026-05-17 — **slice terminal**. The audio is half the ending's payload. The Disastrous ending's silence is canonically the slice's hardest audio production target after the Halia Cleanser-whisper.

---

## 2026-05-17 — **SLICE CLIMAX**: The Final Conflict — the slice's only major orchestral cue

**Lore source**: `references/lore/the-final-conflict.md`. The Migration vs Homesteader fleet super-melee at the Rainbow Worlds arrow-tip. **This is where the slice's music budget lives.**

### Music policy reversal

The Fall of Mh-Lai dispatch established NO music until the first post-fall memorial. The Final Conflict is **the second exception** — *the slice's only major orchestral cue*.

### Required music cues

| Cue | Trigger | Spec |
|---|---|---|
| **Drev-Tok's hail (opening)** | Beat 1 | NO music; two fleets in standoff — engine hums, comm-channel static, Furling fleet collective breath |
| **Drev-Tok's address (building)** | Beat 2 | A single sustained low brass note enters mid-speech; barely there |
| **Diplomatic-rare conversion** | Drev-Tok converts | Brass shifts to a warmer Persuader-Defender harmonization chord — ~30s; the music finds a reconciliation tone the slice has not had |
| **Symbolic-clash volley** | One volley for honor | Brief 4-8s martial fanfare; ceases as honor satisfied |
| **Phase 1 combat** | Sa-Matra opens fire | **THE BIG CUE.** Full orchestra; brass-heavy; Defender-themed (deep crimson sonic palette); driving rhythm. ~3-4 minutes. Performance reference: SC2 Ur-Quan Dreadnought theme but with more weight, less alien-strangeness — *this is Furlings fighting Furlings* |
| **Phase 2 multi-vessel split** | Sa-Matra splits | Theme fragments into 3 counterpointing lines; technical-precision combat music |
| **Phase 3 final volley** | Sa-Matra targets crossing | Theme COMPRESSES; tempo doubles; ~30s frantic intercept feel. **Each crew active ability gets a brief musical signature**: Mraka's Evasive Burst (Drifter-circuit motif); Bren-Vor's Precision Focus (Aimer-tone) OR Forward's Perpendicular Aim (chromatic-ripple Thinn signature); Yelena's Field Overhaul (Lwen-Tar-family warmth motif); Mira-Rou's Bio-Signature Dampening (Halve-Tel pad); Tarven's Deep Archive Scan (prior-Steward-archive motif). **All crew themes appear here.** |
| **Drev-Tok's death** | Combat-victory | Defender theme dies — held minor chord that fades; mournful but honoring; Steward feels not triumphant but sober |
| **The Crossing Opens** | Rainbow Resonator fires | **THE SLICE'S PAYOFF MUSIC.** All faction themes unified — Persuader + Kovellim deep-time + Karavem song + Selvenne chorus + Mmrnmhrm + Stelloth chord + Mraka Drifter-vector + (if relevant) Defender-honoring fade. ~60s of *the slice's only triumphant music*. Crescendo as corridor opens. Performance reference: *a funeral that has become a procession of hope* |
| **The Steward enters last** | Final frame | Music resolves to a single quiet line — Persuader theme + Halia's voice (alive) OR memorial-tone (dead) OR Cleanser-channel artifact (supervised). *The slice's last note* |

### Drev-Tok voice direction

- **Performance**: stern, controlled, **2 years of grievance held in formal stillness**. His voice has been on Council-channels for 2 years; players RECOGNIZE it instantly when he hails in person
- **Canonical opening line** *"Steward. I have been waiting to meet you in person."* — landed coldly; warmth gone; man who rehearsed this for 2 years
- **Grievance is in cadence, not volume** — he never raises his voice
- **Conversion line (diplomatic-rare)**: *"You did it. You marked them back."* — voice cracks for the ONLY time in the slice; doctrinal collapse audible
- **Death line (combat victory)**: *"You were the better tactician."* — flat acknowledgment; not bitter; Defender code requires honor in defeat

### Retro-fit task: Drev-Tok in earlier Council scenes

Per Lore canon, Drev-Tok has been a Council-channel voice for the slice's 2 years. **He should be heard in earlier Council scenes** — every Migration-aligned vote should include a brief Drev-Tok counter-statement (1-2 lines). His voice must be IMMEDIATELY recognizable by the time of the Final Conflict.

### Halia Cleanser-supervised whisper line — SLICE'S MOST PAINFUL SINGLE LINE

In the Cleanser-Fall branch, Halia is on Drev-Tok's coalition side during the Final Conflict. Her Cleanser-channel transmission is formal-only — BUT canonically she briefly breaks formal cadence mid-combat:

> **Halia (Cleanser-channel formal)**: "Migration fleet hostile-tagged. Defender authority confirmed. Recommend Persuader vessel — *(brief break to private register, almost whisper)* I'm sorry, Steward — *(channel cuts back to formal review)* — vessel acquisition per Defender protocol."

The audio production must catch this **exactly** — formal-to-whisper-to-formal in under 2 seconds. The whisper line *"I'm sorry, Steward"* is **the slice's most painful single line**. Performance: Halia's friend-private register from the banter library, but constrained to 1.5 seconds, almost-but-not-quite-clipped by the Cleanser-channel artifact.

### Status

- ☐ Open as of 2026-05-17 — **slice-climactic**. The slice's only major music investment. The whisper line is the slice's hardest single audio production target.

---

## 2026-05-17 — **MAJOR**: The Fall of Mh-Lai audio (slice's biggest emotional beat)

**Lore source**: `references/lore/the-fall-of-mh-lai.md` (NEW). The slice's mid-game catastrophe. The Furling home falls. Audio is *more than half* the emotional load.

**Performance reference for the whole cinematic**: *imagine watching a documentary about a friend's funeral, knowing the friend will not be in the next scene*. Quiet. Restrained. *Not cinematic-overwhelming.*

### Required audio cues

#### Halia's first transmission (Beat 2)

- **Voice direction**: Halia speaks the canonical line (in lore doc). **Calm, urgent, intimate.** She knows. She tells the Steward. Not afraid; not performative. The voice of a friend who has accepted the math.
- **Audio production**: light Persuader-priority-channel processing — subtle ionization-pattern artifact under the voice; clear-enough to be heard but with the hint of *we are recording for posterity*.
- **Background**: faint Council-chamber ambient (paper rustles, evacuation klaxons in distance, quiet voices). The chamber sounds *busy* behind her composure.

#### The dimensional ripple approaching (Beat 3-4 ambient)

- **Sub-bass anti-tone** — the canonical Others' audio signature; *a sound you hear in the body, not the ear*. Builds slowly as the ripple crosses the cluster halo.
- **Reverse-running high-frequency tinnitus artifact** — the dimensional substrate intersecting normal space; reads as *wrong* to the listener's primitive senses. Audio engineering trick.

#### Halia's final transmission (Beat 4)

- **Voice direction**: Halia speaks **even slower than her first transmission**. Her composure is *deeper* now. She is in the chamber with the data-archive final-state seal activating around her. She is *present and accepting*. Performance reference: a meditation teacher giving the last instruction before a long silence.
- **Audio production**: the Persuader-priority-channel artifact is *louder* now (the signal is degrading as the chamber shielding fails) but the voice remains clear. *"Steward — I see your ship in orbit. Thank you for coming. Even now."* This line must land.
- **Background**: chamber ambient is now *much quieter* (most have evacuated); the data-archive racks are humming as they seal; the aurora has audible faint chromatic *crackle* through the chamber window.
- **The signal cuts**: clean cut to silence. NO music swell. NO bracketing sound. Just *cut to silence*. This is the slice's most important silence.

#### The fall itself (Beat 4 cinematic)

- **Atmospheric flicker — aurora sound**: brief, beautiful, chromatic — *the last beautiful sound Mh-Lai produces*. ~3 seconds. Resembles a slow harmonic chime.
- **The Others' substrate intersecting**: the sub-bass anti-tone *deepens*; reverse-tinnitus is now overt; the planet's biosphere going dark in waves is *audibly silenced* — distant Furling broadcasts that were on the air *cut off* in waves as cognition extinguishes. This is canonical and should be designed: ~6-12 distant Furling voices (radio chatter, mundane stuff — *"copy that, central"* etc.) cutting off in cascading waves. **Each cut-off is a death.**
- **Final silence**: 10-15 seconds of FULL silence. The viewer hears their own breathing. The Migration vessels are pulling away in silent visual; the audio is silent. *Resist the temptation to underscore with strings.*

#### Hearth-of-Iron new-home ambient

When the Steward docks at Hearth-of-Iron post-fall, the audio ambient is *different from Mh-Lai*:
- Migration-vessel mechanical sounds (the ship is moving, unlike Mh-Lai Station which was orbital-stable)
- Quieter Furling chatter (everyone is grieving; conversations are subdued)
- The canonical Furling fur-muting effect is *heavier* (everything is more cushioned)
- Mev-Tar Lwen-Tar's Unzervalt tooling can be heard in the distance (the assembly chief is at work; the work continues; the canonical comfort of *something being built*)

### Halia branch-state voice variants

- **Halia alive Persuader-free (race-success)**: Halia's voice in subsequent slice scenes carries *quiet weight* — she watched her home die; she leads anyway. *More patient than before.*
- **Halia dead, remembered**: a Persuader-faction successor reads Halia's transmissions in formal Council scenes — *"Commander Halia's last directive..."* — voice cadence honors Halia's slow composure
- **Halia alive Cleanser-supervised**: Halia speaks through Cleanser-channel review now — her voice is the same but the *audio production* has Cleanser-channel artifact (subtle metallic edge; her phrasing is constrained — short formal sentences without warmth). The friend is in there; the Cleanser overlay is between her and the Steward.

### Music cue policy

- **Beat 1 (Detection)**: NO music; just the alarm and Halia's voice
- **Beat 2 (Halia first transmission)**: NO music; just Halia and chamber ambient
- **Beat 3 (Decision)**: NO music; *the silence is the choice*
- **Beat 4 (Race / The Fall)**: NO music during the chamber + atmospheric flicker. **Optional**: a single sustained low-tone (~30Hz pad) during the fall itself, very quietly — a *grief-substrate* rather than a melody. **Maximum 1 layer of music.** No brass; no strings; no choir.
- **Beat 5 (Aftermath)**: NO music when the Steward returns to the ship for the first time post-fall. The Common Room ambient bed plays normally but with the *post-fall mood markers* (quieter; heavier fur-muting; tools tap less; Mira-Rou's amphora hum is the loudest layer).
- **First Mh-Lai memorial visit / formal Council moment post-fall**: *here* a music cue is allowed — a quiet Persuader-faction memorial theme; ~60 seconds; restrained. This is the slice's only music about Mh-Lai itself.

### Status

- ☐ Open as of 2026-05-17 — **slice-critical**. The audio carries this scene as much as the visuals do. **The silences are content.**

---

## 2026-05-17 — Crew Common Room ambient + banter cues (Aaron's direct dispatch)

**Lore source**: `references/lore/crew-common-room.md` (NEW). The Common Room is the slice's first major ship-interior scene — needs warm-textural-furnished ambient sound + per-crew banter cues + small UI-feedback sounds.

### Ambient bed (loops while player is in the room)

**Acoustic profile**: *fur-muted warm interior* — the Common Room's canonical fur-everywhere surfaces make the room **acoustically dead** in a specific way. Sound carries softly but doesn't echo. Performance reference: *a library after closing hours, but warm and with people present*.

Ambient layers (each looping independently for variation):
- Distant ship-system hums (low-frequency continuous bed)
- **Yelena's workbench**: tap-tap-tap of tools on metal at irregular intervals (one tap every ~3-8 seconds; varies with what she's repairing)
- **Tarven's tea-cup**: small clinks of cup-on-saucer + occasional soft *page-flip* of a log-reader
- **Bren-Vor's weapons-cleaning kit**: faint mechanical clicks (component re-assembly)
- **Mira-Rou's amphora hum**: very faint sub-aural humming (~30Hz) — barely audible unless the player approaches her alcove; canonical *biot-fragment present*
- Soft fabric-rustles when any crew member shifts position (the canonical *fur-muting* effect — movement sounds are *cushioned*)

**Banter mode (when crew are talking)**: ambient layers duck slightly to make room for the banter dialog audio.

### Per-crew banter cue characteristics

Each named crew's voice profile is already documented in the species voice table above. In the Common Room banter context:

- **Mraka**: warm-technical; references hyperspace patterns visible out her window; teaches Drifter math; corrects Yelena's coffee-maker repair attempts (gentle teasing)
- **Bren-Vor**: quiet observation; cleans his rifle while speaking; says less than others but his lines carry weight
- **Yelena**: vibrant; references whatever she's currently fixing; family-warm in conversation; finishes others' sentences when they're discussing engineering
- **Mira-Rou**: thoughtful; quotes biological-vocabulary; *patient with everyone except herself*; occasionally interrupted by Sevreth's Child's chemical signals (if alive)
- **Tarven**: bookish; cites prior-Stewards by full clan suffix; loses track of original questions; reads aloud unprompted

**Cross-crew banter pair dynamics** (per lore doc):
- **Mraka + Yelena**: technical-collaborative; *easy*; the slice's most comfortable pairing
- **Bren-Vor + Mira-Rou**: shared-grief quiet; they recognize each other's weight; canonical *less-said-is-more*
- **Tarven + anyone**: Tarven reading aloud, being gently redirected; the slice's comic relief in the Common Room
- **Sevreth's Child + anyone**: chemical-signal sub-audible humming that Mira-Rou translates — *"Sevreth's Child finds your voice... amusing? I think the word is *amusing*"* (canonical line)

### UI feedback audio cues

| Cue | When | Spec |
|---|---|---|
| **TALK prompt confirm** | Player presses A/Enter on a crew member | Small pleasant *ascending* chime (~200ms); confirms dialog opening |
| **Notification badge appear** | Side-quest goalpost trigger fires while player not in Common Room | Subtle *pleasant chime* (NOT alarming); ~400ms; the player may be in hyperspace and shouldn't be jolted |
| **Notification badge clear** | Player initiates the side-quest dialog | Brief warm *resolution* tone; ~150ms |
| **Banter bubble appear** | Ambient banter line plays | No dedicated cue — the dialog audio IS the cue |
| **Approach the Steward's bunk** | Player walks to/clicks bunk corner | Soft *creak-of-fur-settling* sound (the bed reacts to weight) |

### Status

- ☐ Open as of 2026-05-17 — pairs with Image chat's Common Room art dispatch

---

## 2026-05-17 — Burvixese world destruction audio (slice catastrophic-witness beat)

**Canon source**: HANDOFF_image_chat.md "Burvixese world destruction cutscene" entry (same date).

The visual cutscene depicts the Caster firing → Others arriving moth-to-flame → Burvixese civilization consumed → Caster left standing on empty planet. Audio is critical for selling the catastrophe. Required cues:

- **Pre-activation Burvixese pride**: the Caster ramp-up sequence — confident harmonic-amplification, deep resonance frequency layering, Burvixese chorus-cheering (four-armed-engineer comm-chatter, excited, technical jargon, *proud*). Heavy on warm copper-brass tonal language.
- **Activation moment**: the Caster fires its harmonic wave — a *brilliantly loud, peak-amplitude tone* that resolves into the broadcast pattern. This is the loudest the slice's audio ever gets, peaking at the moment of activation. Performance metaphor: a brass orchestra hitting the apex of a fanfare just as the Hindenburg ignites.
- **Moth-to-flame Others arrival**: the brass-fanfare *bends and distorts* as the Others arrive. The Caster's tone keeps firing but the harmonic structure starts going *wrong* — the resonances detune; the amplification feedback-loops; the proud confident sound becomes a *high-frequency screech* that the listener instinctively recognizes as catastrophic-failure. The Others' own audio signature (negative-frequency drone, sub-bass anti-tone) bleeds in underneath.
- **Civilization consumed**: the Burvixese chorus-cheering goes *abrupt-silent* in waves — one section at a time, like rooms in a building losing power. The detuned Caster fanfare keeps playing into the silence because the device doesn't know its operators are gone. *That continuation is the cruelest sound in the slice.*
- **Post-destruction silence**: the Caster's tone finally degrades, drops to a low subaudible hum, and continues *forever* — the device remains in low-power harmonic-idle state across the 230,000 years between slice and SC2. The audio fades but doesn't fully stop. (Compare to the Taalo extermination's full silence — the Burvixese silence is *not* full silence because their device is still running. That's the difference between the two tragedies.)

**Performance direction**: lean hard into the **moth-to-flame visual metaphor** — the audio's job is to make the listener *hear* the Burvixese being attracted-to-their-own-destruction. The triumphant-then-corrupted brass fanfare is the sonic punchline.

**Humor doctrine zero** during this cue — no comedic music elements, no Steward POV musical cues, just the catastrophe.

### Status

- ☐ Open as of 2026-05-17
- Tag `✅ PROCESSED <date>` when the activation + consumption + post-silence cues land

---

## Authoring backlog — slice species voice profiles (no specific dispatch yet; for Audio chat's planning)

The following slice species need voice profiles at some point. Lore-side details live in `references/lore/species-sheets.md`. Audio chat can pull voice notes from there and queue work; dedicated HANDOFF entries will appear when a species' voice work becomes a blocker.

| Species | Notes location | Distinctive trait |
|---|---|---|
| Slylandro Observer | species-sheets.md | Drift-think cadence, atmospheric reverb |
| Arilou Sage | dialog/characters.py (already implemented as text) | Wry, ancient, dimensional-shimmer |
| Mycon Biot | species-sheets.md | Collective chorus, FIRST_WHISPER subset |
| Proto-Ur-Quan / Proto-Qor-Ah | proto-species-observations.md | Pre-sentient — vocalizations, not speech |
| Androsynth Refugee (Coel Tessar) | the-androsynth-refugees.md | Time-displaced human clone — accented terran |
| Mmrnmhrm Sentinel | the-mmrnmhrm-and-chenjesu.md | Robotic, 3-8My old, wry awareness |
| Chenjesu Collective | the-mmrnmhrm-and-chenjesu.md | Slow present-tense, crystalline resonance |
| Burvixese | species-sheets.md §10 | Four-armed engineer, confident pre-activation, broadcast-amplitude |
| Utwig | species-sheets.md §11 | Pre-doctrine (un-masked sentient) → post-doctrine (devolved, mask-muffled chant) |
| Thinn (renamed from Planar 2026-05-17) | species-the-thinn.md | "We who are watching" — collective plural, no singular I; ribbon-membrane vibration vocalization (tonal-harmonic, glass-instrument-struck); **canonically dumb** (zero brain volume canon 2026-05-17) — voice should be *warm, slow, cheerful, unhurried by ignorance*; no rhetorical-question awareness, no idiom-comprehension, no sarcasm-detection; the slowness is *not* the wisdom-slowness of the Taalo, it's the cheerfulness of having no urgency because they cannot fully grasp urgency. Performance reference: a cheerful, optimistic person who is also Forrest-Gump-simple, made of glass-harmonic resonance. They take everything literally and answer rhetorical questions sincerely. |
| Melnorme | project_melnorme.md | Ionization-pattern, "Carbon-pattern," "Captain-form" |
| **Forward** (Thinn rebel; weapons-officer alt-recruit; added 2026-05-17) | crew-recruitment-quests.md §2a | **Thinn voice base** (ribbon-membrane glass-instrument; canonically Thinn-dumb) BUT with **singular "I" pronouns** throughout (the canonical rebellion) AND a slightly *sharper* edge from being ostracized 3 years alone at Mh-Lai docks. Performance reference: *a cheerful Forrest-Gump-simple person who has taught himself to be one and is cautiously proud of it.* **Critical**: Forward does NOT realize he is being funny. His 2D jokes are sincere geometric observations delivered with full earnestness. The joke is in the LISTENER'S recognition, never the speaker's delivery. The voice production must NEVER wink. **Canonical Forward grief sound** (side-quest quiet-goodbye outcome): a chromatic glissando across his vocal range — a harmonic ripple, no words. The canonical Thinn grief gesture, first time the Steward witnesses it. **The two diaspora-Thinn** (We-Who-Watch-The-Far-Slope, We-Who-Watch-The-Lower-Bench) share Forward's voice base BUT use standard collective-plural pronouns (their preserved doctrine); they argue cheerfully with Forward in Common Room banter. |
| Lemmkin (added 2026-05-17) | species-the-lemmkin.md | High-pitched, fast cadence, chittery, **no hesitation markers** (no um/uh), frequent self-interruption, rising-tone interrogatives at every clause break, cheerful even when discussing their own extermination. Performance reference: *over-caffeinated nature documentary host crossed with a curious child.* They ask 4-6 questions in a single breath and don't wait for answers. **No fear-modulation** in voice — when talking about the Others' arrival, they sound *excited.* Pitch up, speed up, chitter on the consonants. |
| Mael-Num (off-screen, low priority) | species-precursor-era.md §Background | One-eyed; future Sentient Milieu founders. Mentioned in slice gossip but no dialog NPC needed. Voice profile deferred until they get an on-screen role. |
| **Stelloth** (added 2026-05-17) | species-the-stelloth.md | **THREE-VOICE HARMONIC CHORD** — when a Stelloth speaks, all three bodies contribute simultaneously. **Speaker** (mid-register, formal, modulated — the front voice the visitor hears clearly); **Witness** (HIGH-pitched click-emphasis, ~0.2 seconds BEFORE the Speaker finishes each contractually-significant phrase, marking semantic moments the Witness has noted); **Counter** (DEEP slow bass, ~1.5 seconds AFTER the Speaker finishes, evaluating long-term consequence). Performance: render as a literal three-voice chord with offset timing. The Counter occasionally CONTRADICTS the Speaker (a held low-tone of refusal); when this happens, the Speaker stops mid-sentence and re-negotiates with itself. Canonical NPC: Tarvel-Three-Voices. |
| **Selvenne** (added 2026-05-17) | species-the-selvenne.md | **LAYERED CHORUS** — many voices speaking in unison from a planet-scale coral reef. The voice should feel *underwater* — slight reverb, gentle pitch-modulation as if filtered through bioluminescent depth. Communicates emotional TEXTURE more than facts. Slow, *feels-rich* delivery. Performance reference: a cathedral choir filtered through an ocean current. **Special audio task**: when a polyp transmits memory to the Steward, the playback should sound like the *Steward's own voice* hearing the memory in first person. This is canonical and distinct from the chorus voice. |
| **Mrokon** (added 2026-05-17) | species-the-mrokon.md | **PUPPET voice** speaking FOR the **Operator**: gruff, formal, oath-bound; warrior-class register; short declarative sentences; structured around honor and duty. Voice should sound *vocally normal* but with a faint underlying *deep-link artifact* — a subtle electromechanical undertone that hints the speaker isn't directly biological. Performance: imagine a stoic warrior captain whose voice has been *very gently* processed through a vocoder. The Operator's actual voice (heard only in the bunker scene) is *different* — softer, less formal, *child-sized*. Canonical NPC: Vrek-The-Eighth-Body. |
| **Kovellim** (added 2026-05-17) | species-the-kovellim.md | **DEEP, SLOW, CYCLICAL** — they think in cycles across the deep past. Long phrases punctuated by long pauses; each pause is the Kovellim mentally cross-referencing against prior-cycle records. Performance reference: an ancient sea-captain who has navigated this stretch of coast for 1,200 years and is unhurried because they've seen everything. Tonally *warmly weary*. Use the verbal idiom *"in the cycle of"* frequently. Canonical NPC: Ovala-Eight-Crossings (elder, 1,200 years old, eight prior crossings; voice carries the weight of millennia held gently). |
| **Karavem** (added 2026-05-17) | species-the-karavem.md | **NO SPOKEN LANGUAGE — every utterance is MUSIC**. The throat-organ produces THREE simultaneous notes (primary + two harmonic overtones); vocal range spans ~5 octaves. Furling translator renders songs as *prose with musical annotation* (*"[in C minor, mournful]"* etc.) — render the music PLUS the prose-translation in audio output. Microtonal modulation, rhythmic micro-variation, and harmonic-density carry ~30% of nuance that the prose-translation loses; the audio production should *sustain* these nuances even when the prose is approximate. Performance reference: a six-part choir filtered through a wind-instrument; complex, beautiful, *sad in major keys and joyful in minor keys* (Karavem emotional valence is reversed from Furling expectations — major = formal commitment which can be sad, minor = open exploration which can be joyful). Canonical NPCs: Veled-Of-The-Canyon-Wall (elder conductor; deep-indigo highland plumage; voice spans 5+ octaves), Pheri-Sings-Open (younger theorist; golden-rust plumage), Olava-Counterpoint (Aria-Skiff pilot). |

### Furling NPCs voice profiles (also pending)

The protagonist Steward + named Furling NPCs need voice profiles too. Per `memory/project_voices_future.md`, this is post-variation-layer work; per the new economy + crew canon, slice has named NPCs at:

- Halia (Mh-Lai commander; dialog already implemented)
- The 5 recruitable crew (see `references/lore/crew-recruitment-quests.md`): Mraka Yenn-Sa, Bren-Vor Telcas, Yelena Lwen-Tar, Mira-Rou Halve-Tel, Tarven Olwen-Sa
- Furling Archivist, Warden, Tunneler (shop-buyable crew with generic-character voices, not unique NPCs)

---

*(Future entries appended above this line.)*
