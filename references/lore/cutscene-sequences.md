# Cutscene Sequences — Ken Burns Pan-and-Narrate

> Aaron dispatch (2026-05-18): *"Fill out the cutscene sequences. They should be awesome rewards or thrilling defeats depending on a good or bad outcome, and there should be heavy text associated with it. We can use still images that are very wide, so we slowly slide across the image and maybe we add some overlay later to make the images change a bit while we watch, while the narrator speaks (text for now, speech later). That seems a simple task within our reach."*
>
> Canonical-minimum-viable-cinematic system spec + canonical-cutscene-catalog with heavy-text passages. Canonical implementation target: text-on-screen with Ken Burns canonical-slow-pan across wide image; canonical-no-audio-required-initially; canonical-Phase-2-overlay-animation later.
>
> This doc consolidates with [`cinematic-narration.md`](cinematic-narration.md) — that doc has canonical-narration-prose for the 15 canonical-priority-cinematics; this doc has canonical-pan-and-image specs PLUS new heavy-text passages for species-resolution outcomes (good vs bad pairs) PLUS the canonical-6-endings cutscenes PLUS the canonical-Tier-1.5 candidates (Rainbow World seeding / First-Other-Vessel sighting / etc.).

---

## 1. The canonical Ken Burns cutscene system — spec

### 1.1 Image canvas

- **Canonical wide-aspect canvas**: **3840 × 1080 pixels** (canonical 16:4.5 ratio = canonical-3-screens-wide on canonical-1920×1080 display). Canonical: the camera pans canonical-horizontally across the canvas; canonical-the player sees canonical-1920×1080 viewport at any moment; the canonical-pan covers canonical-3-screens-worth of image content.
- **Canonical vertical-pan variant**: **1080 × 3840** (canonical 4.5:16 ratio) for canonical-descent scenes (canonical-falling-into-Mh-Lai-corpse-planet, canonical-Crossing-Opens vertical-portal). Canonical-Design's call which scenes need vertical-pan.
- **Canonical close-detail variant**: **1920 × 1920** (square) for canonical-character-detail-zoom scenes (canonical-Halia's-final-transmission close-up; canonical-Drev-Tok's-eyes-finally-visible). The canonical-camera canonical-zooms canonical-in slowly rather than pans.

### 1.2 Pan path specification

Each cutscene has a canonical-`pan` value with these fields:
- **`start`**: normalized canvas position `[x, y, zoom]` where x/y are 0-1 across the canvas and zoom is 0.5-2.0 (1.0 = canonical-1:1 with viewport)
- **`end`**: same format; canonical-camera-target at end of pan
- **`duration_sec`**: canonical-total-pan-duration (recommended 30-90 seconds; canonical-priority-passages can go up to 120)
- **`easing`**: `linear` / `ease-in-out` / `ease-in` / `ease-out`. Canonical-default: `linear` (canonical-Ken-Burns canonical-feel is canonical-uniform-motion)

**Canonical example**: `pan: {start: [0.0, 0.5, 1.0], end: [1.0, 0.5, 1.0], duration_sec: 60, easing: "linear"}` = canonical-slow-pan-left-to-right across canonical-full-canvas-width in canonical-1-minute.

### 1.3 Text overlay specification

Each cutscene has canonical-`text_blocks` — an array of canonical-narration-segments synchronized with the pan:
- **`start_time_sec`**: when the text block fades in (relative to cutscene start)
- **`end_time_sec`**: when it fades out
- **`text`**: canonical-narration-prose (canonical 50-200 words per block; canonical-readable in canonical-block's-display-window at canonical-reading-pace ~250 wpm)
- **`position`**: `bottom-third` (canonical-default; canonical-letterbox-style) / `top-third` / `left-bar` / `right-bar` / `center` (canonical-only-for-final-anchor-lines)
- **`color`**: canonical-warm-amber `(240, 200, 140)` for canonical-good-outcomes; canonical-cool-grey `(180, 180, 200)` for canonical-baseline; canonical-cold-violet `(200, 180, 240)` for canonical-Cleanser-related; canonical-bright-white `(240, 240, 240)` for canonical-priority-anchor-lines

**Canonical font**: clean readable serif or sans-serif at canonical-32-48px; canonical-NOT-the-engineered-Furling-letterform (canonical: that's reserved for in-world environmental signs per `callbacks-and-callforwards.md`).

### 1.4 Phase 2 overlay animation (canonical-deferred)

Canonical-Phase-1 (canonical-MVP): static wide image + pan + text. Canonical-Phase-2: optional small canonical-looping-overlay-effects layered on the image during pan:
- **Particle effects**: canonical-embers / canonical-dust / canonical-falling-stars / canonical-rain / canonical-snow / canonical-pollen / canonical-rift-fragments
- **Light effects**: canonical-light-leaks / canonical-lens-flares / canonical-warm-sunbeams / canonical-cold-light-shafts
- **Color shifts**: canonical-warm-to-cool gradient / canonical-bright-to-dark over time / canonical-color-pulse
- **Local-zone animations**: canonical-ship-engine-glow that pulses / canonical-canopy-leaves rustling / canonical-rift-distortion-ripple / canonical-fire-flickering-in-background
- **Specific canonical-Others-related overlay**: canonical-spatial-distortion ripple at canonical-low-amplitude (canonical-rift-imagery; canonical-makes-the-Others-cutscenes feel-wrong-on-a-substrate-level)

Canonical-Phase-2 is canonical-not-required-for-canonical-slice-MVP. Canonical-Phase-1 (still + pan + text) is canonical-sufficient for canonical-dramatic-impact.

### 1.5 Duration targets by canonical-cutscene-tier

| Tier | Target duration | Text-block count | Word count |
|---|---|---|---|
| **Top priority** (Crossing-Opens; Halia death; Disastrous ending) | 90-120 sec | 5-8 blocks | 400-700 words |
| **High priority** (Council briefing; Fall of Mh-Lai; species-resolution-tragic) | 60-90 sec | 4-6 blocks | 250-450 words |
| **Standard** (species-resolution-good; minor-meta-cinematics) | 30-60 sec | 3-5 blocks | 150-300 words |

---

## 2. Cutscene catalog — pan/image specs + heavy-text passages

### 2.1 Tutorial / Beat 1-5 cutscenes

#### CINEMATIC: The Council Briefing — *Your mandate is The Quiet Resolution*

**Trigger**: `flag:tutorial_beat_5_council_briefing`. **Tier**: High. **Duration**: 75 sec.

**Image canvas (3840 × 1080)**: canonical-wide-shot of the Defense Fleet operations room at Mh-Lai Station; canonical-left-third: deep-galactic-window showing Beta Corvi gas giant in distance; canonical-middle-third: Halia standing at canonical-strategic-table with warm-russet fur + Persuader sash; canonical-right-third: Furling Council seal on wall with canonical-bookkeeping-stacks of canonical-archive-records behind. Canonical-warm-amber lighting throughout.

**Pan**: `{start: [0.0, 0.5, 1.0], end: [1.0, 0.5, 1.0], duration_sec: 75, easing: "linear"}` — canonical-slow-pan-left-to-right; canonical-camera-discovers-Halia-mid-pan-then-rests-on-archive-records.

**Text blocks** (warm-amber):

1. `[0-15s; bottom-third]`: *"There is a clock on this work, Steward. The Furling Council has projected the Others' arrival window. It is shorter than we would have wished. It is longer than we deserve. We will use it carefully."*

2. `[18-35s; bottom-third]`: *"Your mandate is **The Quiet Resolution**. Every species we encounter must be brought to a terminal state — saved, hidden, or honestly mourned — before the Others arrive. We will not have time for everyone. We will lose some of them. The losses will be recorded. We will not pretend the recording is sufficient. But we will not abandon the recording either."*

3. `[40-58s; bottom-third]`: *"You will visit gas-giant atmospheres and rooted-stone collectives, ribbon-beings who face sideways and mountain-ranges who are species, refugees from a future that ate them and engineers who cheerfully die learning. Each one deserves your attention. Each one will receive it. The work is the work."*

4. `[62-72s; center; bright-white]`: ***"The bookkeeping is the dignity."*** *(canonical-anchor; canonical-priority-line)*

5. `[72-75s; bottom-third]`: *"Drink the tea, Steward. The work begins."*

**Phase 2 overlay**: canonical-slow-warm-light-pulse-from-window (canonical-Beta-Corvi-light); canonical-faint-dust-motes in canonical-archive-stacks area.

---

#### CINEMATIC: Beat 4 — Distress Beacon delivery

**Trigger**: `flag:tutorial_beat_4_androsynth_arrived`. **Tier**: High. **Duration**: 70 sec.

**Image canvas (3840 × 1080)**: canonical-left-third: canonical-Quasi-Space fold-aperture canonical-iridescent and canonical-wounded; canonical-middle-third: canonical-damaged Androsynth ship canonical-late-22nd-century-engineering-aesthetic canonical-hull-pitted-with-dimensional-shear; canonical-right-third: Coel Tessar canonical-bare-faced standing in canonical-vessel-airlock, canonical-Distress-Beacon held in canonical-outstretched-hand. Canonical-cool-blue-and-grey palette.

**Pan**: `{start: [0.0, 0.5, 1.0], end: [1.0, 0.5, 1.2], duration_sec: 70, easing: "ease-out"}` — canonical-pan-toward-Coel; canonical-slight-zoom on canonical-final-third toward canonical-Beacon-in-her-hand.

**Text blocks** (cool-grey):

1. `[0-15s]`: *"Bio-Archive Entry 14,420. The fold opened slowly. The vessel was canonical-Furling-engineering-unfamiliar — angular; lit by white-spectrum lamps the Council had not seen in any record. The Arilou flagged it before we did. They flag everything before we do."*

2. `[18-35s]`: *"Eight thousand of them survived. Two minutes ago, in their reckoning, six hundred thousand of them lived. They were on a planet. The planet is canonical-no-longer-theirs in canonical-any direction of time. The Others did not kill them. The Others sent them backward."*

3. `[38-55s]`: *"Their leader's name is Coel Tessar. She has spent the seventy-two hours since the displacement organizing canonical-survivor-regrouping. She has not slept. She did not collapse. The rest of them followed her by emergent consensus. She does not raise her voice. She apologizes too often. Her eyes do not quite warm even when she thanks us for the rescue."*

4. `[58-67s]`: *"She has given us a recording. A small device. She calls it a Distress Beacon."*

5. `[67-70s; center; bright-white]`: ***"I will not watch it twice."***

**Phase 2 overlay**: canonical-faint-dimensional-shear-shimmer at canonical-edges of frame; canonical-rare-canonical-spatial-distortion-ripple near the fold-aperture.

---

### 2.2 Species-resolution cutscenes — GOOD outcomes (rewards)

#### CINEMATIC: Slylandro — Cloaking Satellite deployed (REWARD)

**Trigger**: `flag:slylandro_cloaking_satellite_installed`. **Tier**: High. **Duration**: 80 sec.

**Image canvas (3840 × 1080)**: canonical-left-third: Beta Corvi gas giant Lai-leh canonical-dominating, canonical-bands-of-warm-amber-and-rust; canonical-middle-third: Slylandro Cloaking Satellite canonical-near-geosynchronous-orbit, canonical-Furling-fission-core glowing canonical-warm-blue at center; canonical-right-third: pulling back to show canonical-satellite-against-starfield with canonical-Lirin-Pel-Sa's-Canopy-vessel visible far in canonical-distance, canonical-witness-position. Canonical-warm-amber-and-cosmic-purple palette.

**Pan**: `{start: [0.5, 0.5, 1.5], end: [0.0, 0.5, 1.0], duration_sec: 80, easing: "ease-out"}` — canonical-start-zoomed-on-satellite-detail, then canonical-pull-back-and-left to reveal canonical-full-scale-of-saved-civilization.

**Text blocks** (warm-amber):

1. `[0-12s]`: *"Bio-Archive Entry 14,484. The installation was canonical-three-hours. The canonical-fission-core is canonical-near-eternal — the Council projects canonical-operational-lifetime of canonical-millions-of-years."*

2. `[15-28s]`: *"The canonical-Slylandro felt-the-shift-from-below and composed a canonical-song-of-thanks. The song is canonical-twelve days long. We are recording it. We will not have time to listen to all of it before we depart. We have made our peace with this."*

3. `[31-50s]`: *"The cloak will hold past the Culling. It will hold while we are gone. It will hold while the canonical-next-civilization wonders why this one gas giant is canonical-quiet on canonical-every-detector that should-be-able-to-read it. It will hold through their canonical-questions, through their canonical-theories, through their canonical-eventual-dismissal-of-the-canonical-anomaly."*

4. `[53-72s]`: *"In canonical-two-hundred-and-fifty-thousand years, when canonical-future-Stewards — no, no Furlings will call themselves Stewards by then — come to canonical-Beta-Corvi looking for canonical-anything, they will find the Slylandro alive. They will not know how. They will not know why. I will know. I am recording this so someone knows."*

5. `[75-80s; center; bright-white]`: ***"Lirin Pel-Sa is singing back to them. The song is not twelve days. It is a greeting."***

**Phase 2 overlay**: canonical-soft-pulsing-glow on canonical-fission-core; canonical-faint-Slylandro-shapes drifting in canonical-gas-giant-atmosphere; canonical-faint-canonical-Lirin-canopy-light visible in canonical-far-distance.

---

#### CINEMATIC: Vresh Extraction — the one of them (REWARD-with-TRAGEDY)

**Trigger**: `flag:vresh_extracted` + `flag:taalo_eliminated_with_one_migrant`. **Tier**: High. **Duration**: 85 sec.

**Image canvas (3840 × 1080)**: canonical-left-third: Taalo's-Stone planetary surface canonical-mountain-range visible canonical-veins-still-glowing-faintly; canonical-middle-third: canonical-Furling-engineered substrate-tank being canonical-loaded onto canonical-Steward's-Scout; canonical-tank-interior-visible with canonical-Vresh-Hum-Of-The-Slow-Veins canonical-pulsing-warm-blue; canonical-right-third: canonical-mountain-range receding in canonical-rear-viewport of canonical-vessel, canonical-other-Taalo canonical-still-visible-but-distant. Canonical-warm-amber-and-stone-grey palette.

**Pan**: `{start: [0.0, 0.5, 1.0], end: [1.0, 0.5, 1.0], duration_sec: 85, easing: "linear"}` — canonical-slow-left-to-right; canonical-the-mountain-recedes-as-the-tank-advances.

**Text blocks** (warm-amber):

1. `[0-15s]`: *"Bio-Archive Entry 14,476-V. The extraction took canonical-fourteen-hours. The canonical-substrate-tank had to be canonical-temperature-stabilized at canonical-Vresh's home-substrate-equilibrium for canonical-three-hours before the canonical-transfer could even canonical-begin. We had time. We used it."*

2. `[18-38s]`: *"Veshen-Hum-Of-The-Slow-Veins, the canonical-Taalo-elder, was canonical-present at the canonical-transfer. The canonical-Taalo do not say goodbye in the way we do. They do not have the vocal apparatus for it. What they do is canonical-resonate-together-at-a-single-frequency for canonical-one-long-moment and then they canonical-stop-resonating. The stopping is the canonical-goodbye."*

3. `[42-58s]`: *"Vresh resonated with them for canonical-six-minutes. The Furling-engineers waited. The canonical-mountain-range resonated back. We could hear it through canonical-the-vessel's-hull. Forty-Seven recorded the frequency for the canonical-Bio-Archive. It is a canonical-low-rumble that the canonical-human-ear-equivalent would call canonical-music."*

4. `[62-78s]`: *"Then they canonical-stopped resonating, and Vresh's tank was canonical-sealed, and we canonical-lifted. The canonical-Shield is being built behind us. It will not work. The canonical-mountain-range will canonical-calcify. The canonical-canonical-bodies will become canonical-ordinary-rock."*

5. `[80-85s; center; bright-white]`: ***"Vresh carries them forward. We-all are with them. We-all are leaving them. We-all are both."***

**Phase 2 overlay**: canonical-warm-glow-pulse from canonical-tank-ember-core; canonical-faint-resonance-ripple in canonical-mountain-range; canonical-subtle-color-shift from canonical-warm-Stone to canonical-cooler-receding-distance as canonical-pan-progresses.

---

#### CINEMATIC: Lemmkin Migrate-with-Curiosity — the 50 million join the corridor (REWARD)

**Trigger**: `flag:lemmkin_migrate_outcome`. **Tier**: Standard. **Duration**: 55 sec.

**Image canvas (3840 × 1080)**: canonical-left-third: Skitter-Prime from canonical-orbit with canonical-many-vessels-launching simultaneously; canonical-middle-third: canonical-Lemmkin-Skitters canonical-en-masse-canonical-cheerfully-forming-up alongside canonical-Furling-Migration-fleet, canonical-some-Skitters canonical-visibly-experiencing-canonical-technical-difficulty (canonical-one-spinning-the-wrong-direction; canonical-another-leaving-a-trail-of-canonical-something-that-should-not-be-on-fire); canonical-right-third: Whisk-Of-The-Better-Bouncing-Thing canonical-in-canonical-lead-Skitter waving-cheerfully-out-the-canonical-viewport at canonical-Furling-flagship. Canonical-warm-orange-and-russet palette.

**Pan**: `{start: [0.0, 0.5, 1.0], end: [1.0, 0.5, 1.0], duration_sec: 55, easing: "linear"}`.

**Text blocks** (warm-amber):

1. `[0-12s]`: *"Bio-Archive Entry 14,478. The Lemmkin canonical-Convince-Vote concluded at canonical-eleven-minutes. They have canonical-decided to come. All canonical-fifty-million of them. Forty-Seven has canonical-already-warned the canonical-Migration-corridor coordinators."*

2. `[15-32s]`: *"Their canonical-engineering-archives are canonical-being-loaded onto canonical-cargo-vessels at canonical-rates that canonical-violate-canonical-safety-protocols that the canonical-Furling-loaders have-canonical-stopped-reading-aloud-because-the-Lemmkin-keep-canonical-cheerfully-agreeing-with-each-violation."*

3. `[35-48s]`: *"Whisk has canonical-asked-Forty-Seven canonical-fourteen-times what canonical-Andromeda canonical-physics-will-be-like. Forty-Seven has-canonical-answered fourteen-times that canonical-Andromeda-physics will-canonical-mostly-resemble canonical-our-galaxy-physics. Whisk-has-been-canonical-disappointed-fourteen-times. Each canonical-disappointment-has-been-canonical-shorter-than-the-canonical-previous."*

4. `[50-55s; center; bright-white]`: ***"They are coming. Andromeda will canonical-have-its-first explosions canonical-within canonical-the-hour."***

**Phase 2 overlay**: canonical-faint-flickering-small-explosions among canonical-Lemmkin-fleet; canonical-warm-light-streaks from canonical-vessel-engines; canonical-occasional-canonical-something-on-fire-in-background.

---

#### CINEMATIC: Sevra recruitment — *I have waited for this since I was eight*

**Trigger**: `flag:sevra_recruited` + `flag:sevra_at_window`. **Tier**: High. **Duration**: 70 sec.

**Image canvas (3840 × 1080)**: canonical-left-third: Utwig outer groves at canonical-dusk, canonical-Sevra's reading-nook with canonical-cushions and canonical-books visible; canonical-middle-third: canonical-Sevra walking canonical-bare-faced toward canonical-Steward's-Scout, canonical-small-satchel of canonical-books at her hip; canonical-right-third: canonical-Common-Room-window-view of canonical-stars, with canonical-Sevra's canonical-profile canonical-silhouetted against canonical-the-window canonical-looking-out for the canonical-first-time. Canonical-soft-warm-purple-and-gold palette.

**Pan**: `{start: [0.0, 0.5, 1.0], end: [1.0, 0.4, 1.1], duration_sec: 70, easing: "ease-out"}` — canonical-camera-follows-Sevra and canonical-rests on her-at-the-window.

**Text blocks** (warm-amber):

1. `[0-15s]`: *"Bio-Archive Entry 14,478-S. Sevra-of-no-Veil-suffix-because-she-refuses joined the bridge crew on canonical-the-evening of the canonical-third Utwig visit. She brought canonical-one-satchel of canonical-books, canonical-no-mask, and canonical-the-canonical-care she-has-canonical-cultivated for canonical-the-word *tomorrow* since she-was-canonical-eight years old."*

2. `[18-35s]`: *"The High Veil canonical-permitted-the-leaving. The canonical-doctrine canonical-permits-the-leaving-of-canonical-those-who-have-not-chosen-the-staying. Sevra has canonical-not-chosen-the-staying. The canonical-Council-of-Veils will canonical-discover-her-absence canonical-eventually. They will canonical-conclude she-canonical-was-always-meant-to-leave. The doctrine canonical-permits this canonical-conclusion."*

3. `[38-55s]`: *"She does not look at the doctrine-keepers as she walks past them. She does not look back at her settlement. She looks forward. She has been canonical-practicing-this for canonical-twenty-five years. Today is the first day the practice has canonical-meant-anything outside her own head."*

4. `[58-67s]`: *"She boards the Scout. She finds the Common Room. She walks to the window. The canonical-stars-are-there. She has not canonical-looked at stars before. The doctrine canonical-prohibited-it. The canonical-stars-were-future-tense-things."*

5. `[68-70s; center; bright-white]`: ***"Tomorrow. The doctrine renounces tomorrow. I use the word. I use it carefully. It is the small thing I have kept."***

**Phase 2 overlay**: canonical-soft-glow-on-Sevra-at-window from canonical-stars; canonical-faint-pollen-or-dust in canonical-outer-groves; canonical-warm-light-pulse from canonical-Common-Room-interior.

---

### 2.3 Species-resolution cutscenes — BAD outcomes (thrilling defeats)

#### CINEMATIC: Slylandro Cleansed — *the wind goes still* (DEFEAT)

**Trigger**: `flag:slylandro_eliminated_by_cleanser`. **Tier**: High. **Duration**: 80 sec.

**Image canvas (3840 × 1080)**: canonical-left-third: Beta Corvi gas giant Lai-leh canonical-mid-Cleansing-event, canonical-spore-cloud canonical-spreading-through canonical-upper-troposphere, canonical-Slylandro-shapes canonical-going-still-in-cascade; canonical-middle-third: Cleanser Cruiser canonical-Bell-of-the-Quiet-Ledger in canonical-foreground, canonical-Vael-Souren-canonical-visible-on-bridge with her white-fur dense and her hands folded; canonical-right-third: canonical-gas-giant-after-the-Cleansing, canonical-atmosphere-still-but-canonical-no-longer-conscious. Canonical-cold-violet and-mournful-grey palette.

**Pan**: `{start: [0.0, 0.5, 1.0], end: [1.0, 0.5, 1.0], duration_sec: 80, easing: "linear"}`.

**Text blocks** (cold-violet):

1. `[0-15s]`: *"Bio-Archive Entry 14,484-X. Quiet Ledger entry. Cleanser Vael-Souren delivered the canonical-cessation-protocol. The Slylandro felt no pain. They felt nothing. They became canonical-very-tired. Their canonical-presence canonical-faded canonical-from canonical-the canonical-gas canonical-mantle canonical-over canonical-the canonical-course canonical-of canonical-a canonical-Mh-Lai canonical-day."*  *(canon-update 2026-05-19 per [`violence-depiction-doctrine.md`](violence-depiction-doctrine.md): prior canon canonical-`"absorbed it through their respiratory membrane"` canonical-physiological-absorption canonical-detail canonical-re-framed canonical-to canonical-canonical-presence-fading-from-mantle. canonical-Vael-Souren's canonical-clinical-Cleanser-register canonical-preserved.)*

2. `[18-38s]`: *"The Cleansing took canonical-six hours. The canonical-twelve-thousand-year-canonical-songs canonical-fell-into-canonical-silence in canonical-cascading-bands across the canonical-gas-giant's canonical-upper troposphere. Lai-leh — canonical-the-slow-breath — is canonical-still-breathing in the canonical-sense-that-canonical-atmosphere-moves. It is no longer canonical-thinking the breath. The canonical-difference is canonical-recorded."*

3. `[42-60s]`: *"Lirin Pel-Sa was-present-in-canonical-the-canonical-witnessing-position. The canonical-Preserver-doctrine canonical-required-the-witnessing. She did not interfere. She could not have. The Council vote had canonical-resolved-against-the-cloak. She has not sung since. The Preserver canonical-mourning-song-protocol canonical-requires-canonical-fourteen-days-of-silence-before-the-canonical-mourning-song begins. Lirin is in canonical-day-three."*

4. `[63-77s]`: *"Vael-Souren recorded every Slylandro name canonical-she-could-recover-from-the-canonical-Furling-Archive. The Quiet Ledger entry is canonical-eight-thousand-pages long. She will mourn them. She will mourn them longer than anyone in this universe will miss them. That is the canonical-price-she-pays. It is the canonical-only-price-she-is-asked-to-pay."*

5. `[78-80s; center; bright-white]`: ***"Just to be safe."***

**Phase 2 overlay**: canonical-cold-violet-pulse from Cleanser-Cruiser; canonical-slow-fade of canonical-Slylandro-shapes in canonical-atmosphere; canonical-spore-cloud canonical-dispersing slowly across canonical-frame.

---

#### CINEMATIC: The Fall of Mh-Lai — *Halia, mid-sentence* (DEFEAT)

**Trigger**: `flag:mh_lai_fell`. **Tier**: Top. **Duration**: 110 sec.

**Image canvas (3840 × 1080)**: canonical-left-third: Mh-Lai Station in canonical-warm-amber pre-Fall-state, canonical-Council-chambers visible-with-canonical-figures inside; canonical-middle-third: canonical-dimensional-signature-crosses-foreground as canonical-spatial-distortion ripple, canonical-Halia's-command-vessel mid-evacuation-burn, canonical-Council-chambers canonical-going-dark in canonical-cascade; canonical-right-third: canonical-Mh-Lai-as-corpse-planet, canonical-atmosphere-gone, canonical-paralleling-the canonical-Vulpeculae-Distress-Beacon-imagery deliberately. Canonical-warm-fading-to-cold palette across canonical-pan.

**Pan**: `{start: [0.0, 0.5, 1.0], end: [1.0, 0.5, 0.9], duration_sec: 110, easing: "linear"}` — canonical-slight-zoom-out toward the canonical-end as the canonical-corpse-planet canonical-fills-frame.

**Text blocks** (warm-amber fading to cold-grey through pan):

1. `[0-15s; warm-amber]`: *"Mh-Lai was warm when we approached. The canonical-Council-was-in-session. Halia's canonical-comm-channel was open. She was canonical-mid-sentence about a canonical-Slylandro-supply-routing question when the canonical-channel canonical-changed."*

2. `[18-40s; transitioning]`: *"I have canonical-listened to the recording of the moment of change canonical-eleven-times. I-will-not-listen-to-it-again. The canonical-change is the sound of canonical-everyone-on-the-canonical-Council-floor canonical-becoming-aware-at-the-canonical-same-second that the canonical-Hider-faction's-canonical-projection was canonical-six-months-off."*

3. `[44-62s; cool-grey]`: *"Halia did not panic. She gave canonical-three-canonical-orders in canonical-twelve-seconds. The canonical-orders were canonical-correct. The canonical-orders were canonical-too-late. She knew it. She gave them anyway."*

4. `[65-85s; cool-grey]`: *"Forty-Seven calculated canonical-arrival-time. We were canonical-too-late by canonical-fourteen-minutes. We knew it before-we-engaged-the-Time-Drive. We engaged anyway. The canonical-fourteen-minutes-we-watched were canonical-the-longest-fourteen-minutes the canonical-Steward-has-ever-witnessed."*

5. `[88-105s; cold-grey]`: *"I do not know how to write down what we witnessed. There is canonical-no canonical-Bio-Archive-Entry-number for canonical-this. The canonical-Council-archive-clerk has canonical-asked-me-three-times for canonical-the-canonical-entry-number. I have not canonical-supplied-it."*

6. `[107-110s; center; cold-grey]`: ***"I will canonical-supply-it tomorrow. I am canonical-working on it."***

**Phase 2 overlay**: canonical-spatial-distortion ripple at canonical-foreground during canonical-Fall-frames; canonical-Council-chamber-lights canonical-cascading-out in canonical-sequence; canonical-atmosphere-bleeding-out from canonical-corpse-planet in canonical-final-frame.

---

#### CINEMATIC: Halia's Death — *Drink the tea* (DEFEAT-TOP-PRIORITY)

**Trigger**: `flag:halia_died_in_fall`. **Tier**: Top. **Duration**: 120 sec.

**Image canvas (1920 × 1920)** — canonical-close-detail variant; canonical-zoom-not-pan: canonical-Halia in canonical-cracked-viewport, canonical-warm-russet fur canonical-singed at the edges, canonical-Council-seal still visible on her shoulder, canonical-her eyes canonical-frequently-visible-through-the-fur and meeting the Steward's eyes through canonical-the-comm-feed. Canonical-warm-russet and cracked-glass-grey palette.

**Pan**: `{start: [0.5, 0.5, 0.7], end: [0.5, 0.5, 1.3], duration_sec: 120, easing: "ease-in"}` — canonical-camera-zooms-in-very-slowly over canonical-the-full-passage; canonical-her-eyes canonical-fill-more-of-frame as canonical-final-line-arrives.

**Text blocks** (warm-amber for command-register; bright-white for final):

1. `[0-18s; warm-amber]`: *"Halia (canonical comm-channel): Steward. Position acknowledged. The Scout is canonical-too-close. Withdraw to the canonical-evacuation-line. That is an order."*

2. `[22-45s; warm-amber]`: *"(canonical pause; the canonical-Steward-canonical-does-not-withdraw; Halia canonical-acknowledges-the-canonical-disobedience without canonical-acknowledging-it.) I have canonical-confirmed this is final. The canonical-Hearth-of-Iron is canonical-three-systems-out and they-canonical-will-take-canonical-the-command when canonical-I'm gone. The canonical-Fleet is canonical-organized. The canonical-civilians are canonical-clear of canonical-the-orbit. The canonical-work continues with you now."*

3. `[50-72s; warm-amber → bright-white]`: *"(canonical pause; Halia's voice canonical-softens; canonical-the canonical-code-switch from canonical-command to canonical-private register canonical-happens canonical-here canonical-deliberately.) Steward. I'm telling you that as your friend, not your commander."*

4. `[78-100s; bright-white]`: *"I love you, Steward. I have been your commander. I have been your friend. Either way — keep going."*

5. `[105-115s; canonical-channel-going-silent]`: *(canonical pause; canonical-the canonical-comm-channel canonical-goes-silent; canonical-no-final-clipping-sound; canonical-just-the-canonical-channel-stopping)*

6. `[115-120s; center; bright-white; canonical-final-line]`: ***"Drink the tea."***

**Phase 2 overlay**: canonical-warm-glow on Halia's fur in canonical-early-passage; canonical-glow-dimming during canonical-private-register-switch; canonical-final-fade-to-near-black at canonical-comm-cut.

---

#### CINEMATIC: Taalo Shield Failure — *They do not have the vocal apparatus for it* (DEFEAT)

**Trigger**: `flag:taalo_shield_failed`. **Tier**: Top. **Duration**: 100 sec.

**Image canvas (3840 × 1080)**: canonical-left-third: Taalo's-Stone mountain-range canonical-pre-event, canonical-veins-glowing-warm-and-alive; canonical-middle-third: canonical-Shield-firing as canonical-eleven-seconds of canonical-Furling-Taalo-engineering-marvel; canonical-Others'-dimensional-signature-crossing canonical-foreground; canonical-Shield collapsing; canonical-right-third: canonical-mountain-range-canonical-cooling, canonical-veins-fading-to-canonical-ordinary-stone, canonical-no-detectable-life-signatures. Canonical-warm-stone fading to cold-stone palette.

**Pan**: `{start: [0.0, 0.5, 1.0], end: [1.0, 0.5, 1.0], duration_sec: 100, easing: "linear"}`.

**Text blocks** (warm-amber fading to cold-grey):

1. `[0-12s; warm-amber]`: *"Bio-Archive Entry 14,476-A. The Shield held for canonical-eleven seconds."*

2. `[15-35s; warm fading]`: *"The Taalo had canonical-projected canonical-thirty. They had canonical-built-the canonical-projection-into-the-canonical-Shield's-design. The canonical-design assumed the Others' canonical-substrate-signature was canonical-within canonical-three-orders-of-magnitude of canonical-Dnyarri-psionic-pressure. The Others were canonical-six-orders-of-magnitude-stronger. The Shield canonical-burned-out canonical-trying-to-hold."*

3. `[38-55s; transitioning]`: *"Veshen-Hum-Of-The-Slow-Veins canonical-broadcast during the canonical-eleven seconds. The broadcast was canonical-a-single-canonical-phrase: 'We-all are canonical-grateful.' The broadcast was canonical-not-addressed-to-anyone-specific."*

4. `[60-80s; cool-grey]`: *"The canonical-mountain-range canonical-was canonical-still canonical-by canonical-the canonical-next canonical-sunrise. The Taalo canonical-do-not-cry-out."*

5. `[82-95s; cold-grey; bright-white anchor]`: ***"They do not have the vocal apparatus for it."***

6. `[96-100s; cold-grey]`: *"The canonical-bodies-calcify-into-landscape. By canonical-next-week they will be canonical-indistinguishable from canonical-ordinary-rock. In canonical-two-hundred-and-fifty-thousand years, canonical-archaeologists will find the canonical-Shield canonical-intact. They will not find the canonical-bodies. The bodies will be the canonical-mountain."*

*(canon-update 2026-05-19 per [`violence-depiction-doctrine.md`](violence-depiction-doctrine.md): block 4 canonical-shortened canonical-via canonical-temporal-distance. canonical-Prior canonical-canon canonical-block 4 canonical-canonical-included canonical-`"silicon substrate cools over hours / feel the cooling / remain conscious during most of it"` canonical-conscious-suffering-detail. canonical-Re-framed canonical-to canonical-canonical-`"the mountain-range was still by the next sunrise"` canonical-temporal-aftermath canonical-framing. canonical-Block 5 canonical-`"vocal apparatus for it"` canonical-preserved canonical-because canonical-it canonical-notes canonical-absence-of-protest canonical-rather canonical-than canonical-act-of-suffering. canonical-Pan-timing canonical-may canonical-need canonical-canonical-Design-lane canonical-canonical-re-balance canonical-given canonical-shortened canonical-text.)*

**Phase 2 overlay**: canonical-bright-Shield-glow in canonical-middle-third (canonical-only-for-Shield-firing-window); canonical-Others-rift-distortion in canonical-foreground; canonical-veins fading from canonical-warm-glow to canonical-stone-cold over canonical-pan-progress.

---

#### CINEMATIC: Lemmkin Stay-outcome — *We will die curious* (DEFEAT-BITTERSWEET)

**Trigger**: `flag:lemmkin_stay_outcome`. **Tier**: High. **Duration**: 75 sec.

**Image canvas (3840 × 1080)**: canonical-left-third: Skitter-Prime canonical-from-orbit at canonical-night, canonical-many-small-engineering-disasters visible as canonical-cheerful-fires; canonical-middle-third: Whisk-Of-The-Better-Bouncing-Thing in canonical-Archive-Hall canonical-completing his canonical-final-entry, canonical-other-Lemmkin canonical-still-experimenting-in-background; canonical-right-third: canonical-Others'-arrival visible in canonical-distant-sky, canonical-Lemmkin-still-cheerfully-investigating-everything including canonical-the canonical-arrival itself. Canonical-warm-orange-and-cheerful-firelight palette throughout.

**Pan**: `{start: [0.0, 0.5, 1.0], end: [1.0, 0.5, 1.0], duration_sec: 75, easing: "linear"}`.

**Text blocks** (warm-amber):

1. `[0-12s]`: *"Bio-Archive Entry 14,478-L. The Lemmkin Convince Vote concluded canonical-against-the-Migration. They were canonical-very-polite-about-it. They were canonical-very-cheerful-about-it. They were canonical-not-going-to-change-their-canonical-minds about it."*

2. `[15-35s]`: *"Whisk canonical-thanked-the-Steward for the canonical-trying. He held up the canonical-archive. The canonical-archive is canonical-not-finished. He will be canonical-finishing-it canonical-until-the-Others-arrive. The canonical-final entry will be canonical-very-detailed. He will be canonical-writing canonical-quickly."*

3. `[38-55s]`: *"They are canonical-not-afraid. They canonical-cannot-be-afraid. The canonical-Lemmkin canonical-fear-response-substrate is canonical-vestigial; canonical-the freed-canonical-neural-substrate is canonical-occupied-by canonical-an-expanded-curiosity-drive. The Others will be canonical-the-most-interesting-thing they-have-ever-investigated. They are canonical-looking-forward to it."*

4. `[58-70s; bright-white anchor]`: ***"We will die curious. We recommend it."***

5. `[71-75s]`: *"Drink the tea, Steward. Oh — apologies — your commander said this. It seemed appropriate. We have canonical-amended-our-canonical-doctrine to include it."*

**Phase 2 overlay**: canonical-small-cheerful-explosions across canonical-frame in canonical-perpetual-background; canonical-distant-Others-arrival as canonical-spatial-distortion at canonical-right-edge growing over canonical-pan; canonical-Lemmkin-still-skittering-cheerfully throughout.

---

### 2.4 Mid-slice cutscenes — Rainbow Worlds + First-Other-Vessel

#### CINEMATIC: Rainbow World Seeding — *the longest postcard*

**Trigger**: `flag:rainbow_resonator_seeded`. **Tier**: High. **Duration**: 90 sec.

**Image canvas (3840 × 1080)**: canonical-left-third: canonical-Resonator-spine being canonical-aimed at canonical-target-planet, canonical-the-spine-is-kilometers-long-and-crystalline-and-beautiful; canonical-middle-third: canonical-spine-implanting-into-canonical-planet's-mantle, canonical-energy-cascade as canonical-planet's-color-signature canonical-activates; canonical-right-third: canonical-the-ringed-pair canonical-revealed — canonical-host-star with canonical-orbital-ring of canonical-autonomous-satellites canonical-forming-the-ring-around-it, canonical-arrow-vector-orientation canonical-visible. Canonical-vibrant-cosmic-color palette (depending on canonical-which-Rainbow-World — canonical 7 spectral signatures).

**Pan**: `{start: [0.0, 0.5, 1.0], end: [1.0, 0.5, 1.3], duration_sec: 90, easing: "ease-out"}` — canonical-pull-back-and-zoom at end to reveal canonical-full-ringed-system.

**Text blocks** (warm-amber):

1. `[0-15s]`: *"Bio-Archive Entry 14,490. The Resonator-spine was kilometers long. It was canonical-crystalline and canonical-beautiful and canonical-purpose-built and canonical-canonical-one-of-ten such canonical-spines across the galaxy. The other nine were being canonical-seated by canonical-other-Stewards on canonical-other-worlds at canonical-roughly-this moment."*

2. `[18-38s]`: *"We aimed it. The canonical-aiming took canonical-six-hours. Furling Council canonical-orbital-mechanics has canonical-tolerances canonical-tighter than canonical-anything-the-canonical-future-civilization-will-build-to-find-us with. The canonical-spine canonical-seated canonical-correctly. The canonical-energy-cascade canonical-activated the planet's-color-signature."*

3. `[42-62s]`: *"The planet now canonical-sings. It sings on canonical-a-spectral-frequency the canonical-future-finders will canonical-eventually-build-detectors-to-read. The canonical-ring-of-satellites canonical-encodes the canonical-vector. Together with the canonical-other-nine, the canonical-ringed-pair triangulates canonical-a-single-direction."*

4. `[65-82s]`: *"What canonical-the-direction points-to is, in the canonical-Council's canonical-formal-recording, *the crossing*. In canonical-Steward-shorthand, *Andromeda*. The Furlings canonical-could-not-feel-the-Others in the neighbor galaxy when they last looked. The canonical-absence is the criterion."*

5. `[85-90s; center; bright-white]`: ***"The Steward who seeds this cluster's Rainbow World is participating in the longest postcard ever written."***

**Phase 2 overlay**: canonical-energy-cascade animation during canonical-spine-seating; canonical-color-pulse on canonical-planet matching canonical-spectral-signature; canonical-ring-of-satellites canonical-slow-rotation around canonical-host-star.

---

#### CINEMATIC: First Sight of an Others' Vessel — *the canonical-substrate is wrong*

**Trigger**: `flag:first_other_vessel_sighting`. **Tier**: Top. **Duration**: 95 sec.

**Image canvas (3840 × 1080)**: canonical-left-third: canonical-Steward's-Scout in canonical-foreground; canonical-middle-third: canonical-Others'-Vessel emerging from canonical-dimensional-fold, canonical-rendered-as-spatial-distortion-rather-than-vessel (canonical: the canonical-shape-does-not-resolve-correctly under canonical-sensors; canonical-objects-at-apparent-foreground-floating-past-objects-at-apparent-background; canonical-not-resolving-under-any-rendering-pass); canonical-right-third: canonical-the-Vessel canonical-becoming-canonical-more-coherent as canonical-camera approaches, canonical-but-still-canonical-wrong. Canonical-cold-spatial-distortion palette with canonical-faint-violet undertones.

**Pan**: `{start: [0.0, 0.5, 0.8], end: [1.0, 0.5, 1.4], duration_sec: 95, easing: "ease-in"}` — canonical-camera-approaches-the-Vessel slowly; canonical-the-zoom-IS-the-canonical-horror.

**Text blocks** (cold-grey; canonical-no-warm-undertones; canonical-the-Others-are-never-funny-canon-fully-suppresses-the-Steward-wit):

1. `[0-15s]`: *"Bio-Archive Entry 14,493. We had been told what to expect. The Furling Council canonical-briefing-materials had canonical-illustrations. The illustrations were canonical-best-guess. The illustrations were canonical-incorrect."*

2. `[18-38s]`: *"The Vessel does canonical-not-resolve-correctly. Forty-Seven's canonical-sensor-pass canonical-returned canonical-three-inconsistent-readings within canonical-one-second. The canonical-first-reading suggested canonical-a-vessel-of-canonical-conventional-mass. The canonical-second suggested canonical-a-vessel-of-canonical-no-mass. The canonical-third suggested canonical-the-canonical-vessel-was-canonical-not-canonical-there at all."*

3. `[42-62s]`: *"Forty-Seven's canonical-fourth-reading suggested canonical-that-the-previous-three-readings were canonical-each-correct-from-canonical-different-points-of-view-canonical-simultaneously. Forty-Seven canonical-flagged-the-reading as canonical-anomalous. Forty-Seven did not canonical-disagree-with-the-flag."*

4. `[65-82s]`: *"The Vessel approached. It did canonical-not-fire. It did canonical-not-respond-to-canonical-comm-hails. It did canonical-not-respond-to-canonical-Furling-Council-recognition-codes. It did canonical-not-respond-to-canonical-the-canonical-Steward's-canonical-Hammer-Round-bay-priming canonical-sensor-signature. It did canonical-not-appear-to-canonical-notice-us-canonical-at-all."*

5. `[85-95s; center; cold-grey; bright-white anchor]`: ***"Then it folded somewhere else. We had been the canonical-first-Stewards in canonical-fourteen-years to canonical-see-an-Others'-Vessel and canonical-survive-the-seeing. Halia had-canonical-asked-us-to-record-canonical-everything. We are canonical-recording. There is canonical-not-much to canonical-record."***

**Phase 2 overlay**: canonical-spatial-distortion at canonical-low-amplitude throughout canonical-middle-and-right-thirds; canonical-the-distortion-pulses-at-canonical-irregular-intervals (canonical-not-quite-rhythmic); canonical-faint-frumple-glyph-flicker at edge of frame (canonical-untranslatable Dimension-* signal).

---

### 2.5 Endgame cutscenes — Crossing-Opens + 6 endings

#### CINEMATIC: Crossing-Opens — *Engaging the corridor* (TOP)

**Trigger**: `flag:rainbow_worlds_aligned` + `flag:crossing_opens`. **Tier**: Top. **Duration**: 120 sec.

**Image canvas (3840 × 1080)** — canonical-priority-feature image: canonical-left-third: canonical-Rainbow Worlds canonical-aligned across canonical-galactic-distance as canonical-visible-galactic-arrow; canonical-middle-third: canonical-iridescent-corridor opening between canonical-galaxies, canonical-Migration-fleet entering in canonical-canonical-order — canonical-Kovellim-vanguard first, canonical-Karavem-singing second, canonical-Selvenne-cargo-vessels third, canonical-Furlings fourth, canonical-migrants fifth, canonical-Steward-Scout LAST; canonical-right-third: canonical-corridor receding into canonical-Andromeda. Canonical-iridescent rainbow palette throughout — canonical-the-canonical-color-IS-the-canonical-arrival.

**Pan**: `{start: [0.0, 0.5, 1.0], end: [1.0, 0.5, 1.0], duration_sec: 120, easing: "linear"}`.

**Text blocks** (warm-amber transitioning through canonical-iridescent):

1. `[0-15s]`: *"Bio-Archive Entry 14,495. The Rainbow Worlds aligned on schedule. The Resonator-spines resonated. The orbital rings locked into vector-alignment. The arrow-vector resolved into a corridor."*

2. `[18-38s]`: *"The corridor is canonical-not-what-I-expected. It is canonical-not-a-tunnel. It is canonical-not-a-portal. It is canonical-iridescent-folding of canonical-space-itself between here-and-Andromeda. The vessels entering canonical-fold with it."*

3. `[42-62s]`: *"The Kovellim went canonical-first. They have done this canonical-seven-times. They canonical-led-the-way into the fold without hesitation. Ovala-Eight-Crossings canonical-broadcast canonical-one-message-as-she-entered: 'The corridor is favorable.'"*

4. `[65-85s]`: *"The Karavem followed singing. Major-key. Mourning what they leave. The song was canonical-three-hours-long and the corridor canonical-held-the-song's-resonance after the Karavem had crossed. Selvenne followed slowly — the reef-pieces canonical-lifted and canonical-carried by cargo-vessels."*

5. `[88-108s]`: *"Then the Furlings. The Defenders who changed their minds. The migrants from the Homesteader species who chose to leave. Renn aboard the Scout. Sevra at the window. Vresh in her tank. Forward in his alcove. Mraka at the controls. Tarven at the archive. Forty-Seven everywhere."*

6. `[110-118s; bright-white anchor]`: ***"I am the last. The Council asked me to be. The final Steward across is the one who saw everyone else through."***

7. `[118-120s; center; bright-white]`: ***"The bookkeeping is the dignity. Engaging the corridor — now."***

**Phase 2 overlay**: canonical-iridescent-color-pulse throughout corridor; canonical-Migration-fleet-vessels each canonical-emit-faint-light as they enter; canonical-Karavem-song-resonance-visualization as canonical-subtle-wave-pattern in canonical-iridescence; canonical-final-line canonical-fade-to-rainbow-then-white.

---

#### CINEMATIC: Best Ending — *The Quiet Resolution*

**Trigger**: `flag:ending_best`. **Tier**: Top. **Duration**: 90 sec.

**Image canvas (3840 × 1080)**: canonical-left-third: Andromeda arrival, canonical-all-16-species-fleets visible-in-formation; canonical-middle-third: canonical-new-Furling-settlement-canonical-being-canonical-established, canonical-Common-Room-warmth visible-in-canonical-Scout-windows; canonical-right-third: canonical-Halia-and-the-Steward-walking-together-on-canonical-new-soil canonical-watching canonical-Rainbow-Worlds-of-the-canonical-new-galaxy. Canonical-warm-gold-cream palette throughout.

**Pan**: `{start: [0.0, 0.5, 1.0], end: [1.0, 0.5, 1.0], duration_sec: 90, easing: "linear"}`.

**Text blocks** (warm-amber):

1. `[0-15s]`: *"All sixteen species. All five crew. All canonical-side-quests favorably resolved. The canonical-Quiet Resolution is complete. The canonical-Migration is complete. The canonical-handoff to canonical-Andromeda is complete."*

2. `[18-38s]`: *"The Slylandro canonical-sing in their canonical-cloaked gas-giant a quarter-million years behind us. The Taalo's one-of-them canonical-resonates from canonical-Vresh's tank. The Burvixese broadcasters speak our messages forward. The Lemmkin explode cheerfully in canonical-Andromeda's first-month."*

3. `[42-62s]`: *"The Utwig devolve in peace where we left them. Sevra writes her canonical-book. Renn teaches his children canonical-22nd-century slang they canonical-will-not-canonical-need to know. Forward faces forward at angles his species canonical-no-longer-believes-in. Mraka and Tarven argue. Forty-Seven listens."*

4. `[65-82s]`: *"Halia walks beside me on canonical-soil that canonical-was-not-here yesterday. She does canonical-not-need to give canonical-orders. The canonical-Defense-Fleet is canonical-settled. The canonical-Hearth-of-Iron is canonical-anchored. The canonical-Quiet Ledger is canonical-closed for the night."*

5. `[83-90s; center; bright-white]`: ***"The Quiet Resolution. The bookkeeping is the dignity. We continue."***

**Phase 2 overlay**: canonical-warm-sunrise-light across canonical-new-soil; canonical-fleet-vessels canonical-settled in canonical-orbit; canonical-soft-warm-pulse from Common-Room windows.

---

#### CINEMATIC: Great Ending — *we continue, mostly*

**Trigger**: `flag:ending_great`. **Tier**: High. **Duration**: 80 sec.

**Image canvas (3840 × 1080)**: canonical-similar to Best but canonical-slightly-cooler-palette; canonical-Common-Room visible with canonical-all-crew but canonical-quieter; canonical-Halia or canonical-Halia-absence depending on canonical-branch.

**Pan**: `{start: [0.0, 0.5, 1.0], end: [1.0, 0.5, 1.0], duration_sec: 80, easing: "linear"}`.

**Text blocks** (warm-amber with canonical-cool-undertone):

1. `[0-15s]`: *"All sixteen species. All canonical-five crew. Most canonical-side-quests favorably resolved. Some not. The canonical-Quiet Resolution is canonical-mostly complete."*

2. `[18-40s]`: *"There are names in the canonical-Quiet Ledger we did not put there. There are species that canonical-survived-on-canonical-paths we-canonical-did-not-choose. There are crew who carry canonical-grief they-canonical-do-not-articulate. There are canonical-rooms on the Hearth-of-Iron that are canonical-quieter than-canonical-they-would-have-been."*

3. `[42-62s]`: *"We arrived. Most of us. Most of them. The corridor folded behind us. The Rainbow Worlds canonical-no-longer-sing — the canonical-Resonators were canonical-one-time-emissions. The arrow has been canonical-drawn and canonical-followed. The canonical-future-finders may find it. We canonical-no-longer-need it."*

4. `[65-78s; bright-white anchor]`: ***"We continue, mostly. That is canonical-enough for canonical-tonight."***

5. `[78-80s; center; warm-amber]`: *"Drink the tea."*

**Phase 2 overlay**: canonical-warm-but-not-bright sunrise; canonical-some-windows-dark on canonical-fleet; canonical-faint-color-shift toward canonical-cooler-tones at canonical-pan-end.

---

#### CINEMATIC: Disastrous Ending — *Good job + We told you* (DEFEAT-FOURTH-WALL)

**Trigger**: `flag:ending_disastrous`. **Tier**: Top. **Duration**: 60 sec.

**Image canvas (3840 × 1080)**: canonical-left-third: canonical-galaxy-consumed-forever, canonical-Others'-substrate-fills-frame as canonical-spatial-distortion; canonical-middle-third: canonical-Steward's-Scout being canonical-folded-into-the-substrate, canonical-blood-imprinting-treaty onto canonical-galactic-substrate (canonical-existing canon per parallel-chat); canonical-right-third: canonical-absolute-black with canonical-engineered-Furling-letterform text canonical-fading-in. Canonical-darkest palette in the slice.

**Pan**: `{start: [0.0, 0.5, 1.0], end: [1.0, 0.5, 1.0], duration_sec: 60, easing: "linear"}`.

**Text blocks** (cold-violet → canonical-stark-white on canonical-black):

1. `[0-3s]`: *(canonical absolute silence; canonical-no-text)*

2. `[3-25s; cold-violet]`: *"You led negotiations to hand over the galaxy to the Others, for all time. The fleet fell silent. The galaxy fell silent. The treaty was binding because there was no one left to contest it."*  *(canon-update 2026-05-19 per [`violence-depiction-doctrine.md`](violence-depiction-doctrine.md): canonical-blood-treaty canonical-imagery canonical-re-framed canonical-to canonical-canonical-aggregate-silence canonical-+ canonical-treaty-validity-via-absence.)*

3. `[28-32s; center; bright-white; canonical-deliberate-cheerful-inflection-tag]`: ***"Good job."***

4. `[32-45s]`: *(canonical pause; canonical-absolute-silence; canonical-the canonical-fourth-wall-break canonical-fires-here in canonical-the canonical-3-second-silence)*

5. `[45-58s; center; bright-white; canonical-Furling-deadpan-tag]`: ***"We told you the Others were never funny."***

6. `[58-60s]`: *(canonical absolute silence resumes; canonical-final-frame canonical-fades-to-black)*

**Phase 2 overlay**: canonical-spatial-distortion across canonical-frame; canonical-blood-imprinting-treaty-pattern slowly-emerging onto canonical-galactic-substrate; canonical-engineered-Furling-letterform-text rendering for canonical-final-line.

---

#### CINEMATIC: Unsuccessful Ending — *the galaxy is the kitchen now*

**Trigger**: `flag:ending_unsuccessful`. **Tier**: Top. **Duration**: 95 sec.

**Image canvas (3840 × 1080)**: canonical-left-third: canonical-Andromeda-corridor closing behind canonical-Steward's-Scout; canonical-middle-third: canonical-Common Room canonical-empty-of-most-crew-positions, canonical-Forty-Seven's-display-panel canonical-still-active, canonical-Mraka's-alcove-empty / canonical-Tarven's-archive-empty / canonical-Forward's-alcove-empty / canonical-Renn's-station-empty / canonical-Vresh's-tank-empty / canonical-Sevra's-corner-empty; canonical-right-third: canonical-Andromeda-stars-ahead, canonical-Steward-canonical-alone-at-canonical-viewport. Canonical-cold-grey palette throughout with canonical-faint-warm-undertones-only-in-Forty-Seven's-display.

**Pan**: `{start: [0.0, 0.5, 1.0], end: [1.0, 0.5, 1.0], duration_sec: 95, easing: "linear"}`.

**Text blocks** (cold-grey):

1. `[0-12s]`: *"Bio-Archive Entry 14,499. I have crossed."*

2. `[15-32s]`: *"Forty-Seven is here. The ship is here. The canonical-Common-Room is canonical-empty. Mraka is not. Tarven is not. Forward is not. Renn is not. Vresh is not. Sevra is not. Halia is not."*

3. `[35-58s]`: *"The galaxy behind canonical-the-corridor is canonical-being consumed. The Others canonical-stayed. They have canonical-decided they like-the-taste. The galaxy will be the Others' canonical-feeding-ground for the rest of its canonical-existence."*

4. `[60-78s]`: *"In canonical-two-hundred-and-fifty-thousand years there will be canonical-no SC2. There will be canonical-no Captain Zelnick. There will be canonical-no Ur-Quan, canonical-no Slylandro probes, canonical-no Spathi cowardice evolved into canonical-sentience, canonical-no future civilizations to misunderstand our canonical-archives. There will be the Others. There will be the kitchen."*

5. `[80-88s; center; bright-white anchor]`: ***"I am the only one. The galaxy is the kitchen now."***

6. `[88-93s; soft-warm-undertone]`: *"Forty-Seven: I am here, Steward.*

7. `[93-95s]`: *Steward: I know, Forty-Seven. Thank you."*

**Phase 2 overlay**: canonical-Andromeda-corridor closing behind in canonical-slow-fade; canonical-galaxy-behind-canonical-darkening; canonical-Forty-Seven's-display canonical-faintly-warm — canonical-only-warmth-in-the-canonical-frame.

---

#### CINEMATIC: Sterile Galaxy Ending — *the galaxy was emptied of life that could have failed it* (canonical-NEW; Tier-1.5)

**Trigger**: `flag:ending_sterile_galaxy` (canonical Cleanser-pushed Steward extended canonical-vote-victory to canonical-proto-species). **Tier**: Top. **Duration**: 100 sec.

**Image canvas (3840 × 1080)**: canonical-left-third: canonical-galaxy-from-outside, canonical-no-detectable-life-signatures; canonical-middle-third: canonical-corpse-worlds in canonical-succession — canonical-Sol-III empty (canonical-proto-humans erased pre-history); canonical-Spathiwa empty (canonical-proto-Spathi erased); canonical-Beta-Corvi empty (canonical-Slylandro Cleansed); canonical-each-canonical-world canonical-detailed-with canonical-emptiness; canonical-right-third: canonical-Andromeda-fleet canonical-arrived but canonical-quiet, canonical-Migration successful but canonical-haunted. Canonical-cold-violet palette throughout (canonical-Cleanser-doctrinal-color as canonical-final-statement).

**Pan**: `{start: [0.0, 0.5, 1.0], end: [1.0, 0.5, 1.0], duration_sec: 100, easing: "linear"}`.

**Text blocks** (cold-violet; canonical-Cleanser-doctrinal-color):

1. `[0-15s]`: *"The Migration was canonical-perfect. Not a single canonical-Furling, not a single canonical-migrating-species, not a single canonical-Andromeda-bound-vessel was canonical-lost in the canonical-corridor. The Council's canonical-Cleanser-faction had canonical-prepared the galaxy correctly."*

2. `[18-42s]`: *"The Slylandro were cleansed. The Mycon were cleansed. The Mmrnmhrm were cleansed (canonical-uncertain-substrate canonical-meant uncertain-canonical-Quiet; canonical-the canonical-doctrine canonical-required canonical-certainty). The Taalo were cleansed before the Shield could fail and canonical-confirm-the-canonical-failure. The Utwig were cleansed before-the-Veils-could-Fall."*

3. `[45-70s]`: *"And canonical-the-proto-species. The canonical-proto-Spathi practicing fear. The canonical-proto-humans burying their grandmothers. The canonical-proto-Druuge sorting pebbles. The canonical-proto-Yehat in their stratospheric eyries. All of them. Just to be safe. The canonical-Cleanser-doctrine canonical-completed-itself."*

4. `[72-90s]`: *"In canonical-two-hundred-and-fifty-thousand years, canonical-no-civilization will-canonical-find-our-archives because canonical-there-will-be-no-civilization. The Others will canonical-arrive, find canonical-no-prey-of-canonical-detection-threshold, and canonical-move-on. The galaxy will be canonical-quiet. The canonical-Quiet will be canonical-absolute."*

5. `[92-100s; center; cold-violet; bright-white anchor]`: ***"The Quiet Ledger is canonical-complete. The bookkeeping is canonical-complete. No one will read it. We have arrived in Andromeda. We are canonical-the-only-ones-who-remember-them. We will canonical-mourn-them-longer-than-they-would-have-canonical-mourned-us. That is the doctrine. It works.***
>
> ***Just to be safe.***"

**Phase 2 overlay**: canonical-cold-violet-pulse throughout; canonical-corpse-worlds canonical-detailed in canonical-Cleanser-pale-grey lighting; canonical-Andromeda-fleet canonical-quiet but canonical-not-empty; canonical-final-line canonical-doubles-the canonical-violet-pulse for canonical-anchor.

---

## 3. Implementation suggestions — canonical MVP

### 3.1 Canonical-minimal-viable runtime

```python
# Conceptual sketch (canonical Design's lane to actually code)
class CinematicScene(Scene):
    def __init__(self, image_path: str, pan: dict, text_blocks: list, duration_sec: float):
        self.image = load_image(image_path)
        self.pan = pan  # dict with start, end, duration_sec, easing
        self.text_blocks = text_blocks  # list of dicts with start/end/text/position/color
        self.duration = duration_sec
        self.elapsed = 0.0
    
    def update(self, dt):
        self.elapsed += dt
        # Canonical-skip-protection: priority-passages reject skip until canonical-final-anchor-line plays
        if input_skip and not self.is_priority_final_anchor_playing():
            self.elapsed = self.duration  # canonical-fade-cut
        if self.elapsed >= self.duration:
            self.transition_to_next_scene()
    
    def draw(self, surface):
        # Compute canonical-current-camera-position by interpolating pan.start → pan.end
        t = self.elapsed / self.pan["duration_sec"]
        t = ease(t, self.pan["easing"])
        cam = lerp(self.pan["start"], self.pan["end"], t)
        # Draw canonical-image-section at canonical-cam-coordinates with canonical-zoom
        viewport = compute_viewport(self.image, cam)
        surface.blit(viewport, (0, 0))
        # Draw canonical-text-blocks that are currently active
        for block in self.text_blocks:
            if block["start_time_sec"] <= self.elapsed <= block["end_time_sec"]:
                fade = compute_fade(block, self.elapsed)
                draw_text(surface, block["text"], block["position"], block["color"], fade)
```

### 3.2 Canonical-asset-format suggestions

- Canonical-wide-images saved as `.png` or `.webp` in canonical-`assets/cutscene/<event_id>/canvas.png` (3840×1080 or canonical-variant)
- Canonical-cutscene-metadata as canonical-`assets/cutscene/<event_id>/sequence.yaml` containing canonical-pan + canonical-text-blocks + canonical-duration (canonical-Lore-portable from this doc's specs)
- Canonical-Phase-2-overlays as canonical-separate-PNG-sprites with canonical-alpha-channels in canonical-`assets/cutscene/<event_id>/overlays/`

### 3.3 Canonical-pan implementation hints

- Canonical-linear pan = canonical-simplest; canonical-the canonical-Ken-Burns-feel is canonical-uniform
- Canonical-ease-out = canonical-good for canonical-rest-on-final-detail (canonical-Halia's-death; canonical-Slylandro-Cloak)
- Canonical-ease-in = canonical-good for canonical-camera-approaches-something (canonical-First-Other-Vessel; canonical-Drev-Tok's-eyes)
- Canonical-zoom-out at canonical-end = canonical-good for canonical-reveal-of-scale (canonical-Crossing-Opens; canonical-Slylandro-Cloak)
- Canonical-zoom-in over canonical-whole-passage = canonical-good for canonical-character-close-up (canonical-Halia's-death uses canonical-square-canvas-zoom-only)

### 3.4 Canonical-text-rendering suggestions

- Canonical-bottom-third overlay is canonical-default (canonical-letterbox-style); canonical-leaves-2/3-of-frame for canonical-image
- Canonical-text-fade-in over canonical-0.5-1.0-seconds; canonical-fade-out over canonical-0.5 seconds
- Canonical-center-position only for canonical-final-anchor-lines (canonical-1-per-cutscene-maximum)
- Canonical-color-coding: warm-amber (good); cool-grey (baseline); cold-violet (Cleanser-related); bright-white (anchor)
- Canonical-font-size: 32-48px depending on canonical-text-block-length; canonical-shorter-blocks-larger-text

### 3.5 Canonical-prioritized-build-order for tonight

If the Design lane has canonical-2-4 hours to build canonical-Phase-1:
1. **Minimal `CinematicScene` class** (1 hour) — load image; pan via linear interpolation; render text-blocks with timed fade
2. **Wire 1 cutscene trigger** (30 min) — pick canonical-Council-Briefing (canonical-Tutorial Beat 5) — canonical-easy-flag-trigger; canonical-good-test-case
3. **Stitch 1 wide image** (1 hour) — canonical-can-be-canonical-temporary-stitched-from canonical-existing-Firefly-narrow-cutscene-image plus canonical-extended-canvas-painted-from-prompt-rerun
4. **Test playback** (30 min) — verify pan-and-text works
5. **Iterate to canonical-3-5 cutscenes** (next session) — Halia's death; Slylandro Cloak; Disastrous Ending; First-Other-Vessel; Crossing-Opens

That gets canonical-the-MVP-loop-working tonight; the rest of the 16 cutscene specs in this doc become canonical-fill-in-as-Image-and-Design-have-time.

---

## 4. Image-lane canvas guidance — canonical-stitch-from-existing-stills

Image already has canonical-8-Firefly-cutscene-stills at canonical-narrower-aspect. Canonical-options for canonical-wide-canvas:

### 4.1 Canonical-canvas-extension via Firefly
- Re-prompt Firefly with canonical-canvas-3840×1080 + canonical-original-prompt expanded with canonical-scene-extension-context
- Canonical: this canonical-may-require canonical-multi-pass-stitching if Firefly canonical-cannot-render canonical-canonical-3840-wide

### 4.2 Canonical-stitch-from-multiple-narrow-renders
- Canonical-render canonical-3-overlapping narrow images at canonical-canonical-1920×1080
- Canonical-stitch in canonical-image-editor with canonical-overlap-region-blended
- Canonical-faster than canonical-re-prompting; canonical-existing-Firefly-stills can canonical-serve-as canonical-middle-frame

### 4.3 Canonical-pan over canonical-narrower-image with canonical-zoom-as-the-motion
- Canonical-1920×1080 image; canonical-camera-zooms in or out rather than panning across
- Canonical-works-well for canonical-character-close-ups (canonical-Halia's-death; canonical-Drev-Tok)
- Canonical-loses canonical-Ken-Burns-feel for canonical-environmental-cutscenes (canonical-Slylandro-Cloak; canonical-Crossing-Opens)

### 4.4 Canonical-canvas-priorities for canonical-tonight-MVP

Recommend canonical-Image-lane canonical-prioritize these canonical-3-canvases for canonical-tonight:
1. **Crossing-Opens canvas** (canonical-Migration-fleet-order-in-canonical-corridor) — canonical-slice-largest-single-image
2. **Slylandro Cloak canvas** (canonical-gas-giant + satellite + canonical-Lirin-witness) — canonical-clearest-reward-cutscene
3. **Fall of Mh-Lai canvas** (canonical-Station→Fall→corpse-planet) — canonical-clearest-tragedy-cutscene

The other canonical-13+ canvases canonical-can-be-canonical-stitched-or-extended-later as canonical-Image-has-time.

---

## 5. Cross-chat dispatches

### To Design (`HANDOFF_design_chat.md`)
- **`CinematicScene` class spec** authored in §3.1 — canonical-minimal-MVP implementation sketch
- **16 canonical-cutscene-spec sets** authored in this doc — pan + text-blocks + duration per cinematic
- **Canonical-cutscene-asset-format**: image at canonical-`assets/cutscene/<event_id>/canvas.png` + metadata at canonical-`assets/cutscene/<event_id>/sequence.yaml`
- **Canonical-priority-build-order tonight**: Council Briefing → Halia Death → Slylandro Cloak → Fall of Mh-Lai → Disastrous → Crossing-Opens → First-Other-Vessel
- **Canonical skip-protection**: priority-passages (canonical-Halia-death; canonical-Disastrous; canonical-Crossing-Opens; canonical-Unsuccessful; canonical-Sterile-Galaxy) canonical-reject-skip until canonical-final-anchor-line plays
- **Canonical-trigger-flags list** consolidated in this doc + §2 of `cinematic-narration.md`

### To Image (`HANDOFF_image_chat.md`)
- **16 canonical-wide-canvas specs** authored in §2 of this doc — each cinematic has canonical-detailed-image-description for canonical-3840×1080 wide-canvas
- **Canonical-stitch-from-existing options** outlined in §4 — Image-lane can canonical-extend existing 8 Firefly stills to canonical-wide-canvases
- **Canonical-Phase-2-overlay-sprites** noted per cinematic — canonical-deferred but flagged
- **Canonical-priority-canvases-for-tonight**: Crossing-Opens / Slylandro Cloak / Fall of Mh-Lai
- **Canonical-image-format**: PNG or WEBP at canonical-3840×1080 (wide) / 1080×3840 (vertical) / 1920×1920 (square close-detail)

### To Audio (`HANDOFF_audio_chat.md`)
- **Canonical-no-immediate-audio-work** — Aaron canon: *"text for now, speech later"*. Text-on-screen suffices for canonical-Phase-1.
- **Canonical-Phase-2 VO recording roadmap**: 16 canonical-cutscene narration passages = canonical-~3,500 words = canonical-~30-40 minutes of recorded narration when canonical-Phase-2-audio is canonical-priority. Build-on the canonical-priority-list per `cinematic-narration.md §5`.
- **Canonical-future ambient music cues**: per `cinematic-narration.md §5` canonical-music-policy (canonical-NO-MUSIC during canonical-Disastrous + canonical-Unsuccessful; canonical-MAJOR-ORCHESTRAL during canonical-Crossing-Opens; canonical-Karavem-3-hour-song carries canonical-Crossing-Opens canonical-secondary-bed)

---

## 6. Open items / Aaron-call

- **Canonical-cutscene-count canonical-prioritization**: 16 cutscenes specced; Aaron may want canonical-trim to canonical-priority-8-10 for canonical-slice-MVP scope.
- **Canonical-additional cutscenes-needed**: canonical-Hammer-First-Use (§3.6 cinematic-narration); canonical-Mrokon-Operator-Puppet-Switch; canonical-Burvixese-Be-Loud-failure; canonical-Mycon-Deep-Child-awakening; canonical-Council-vote-deliberations canonical-6-tier. Aaron may want canonical-additional-spec-passes.
- **Canonical-Phase-2-overlay-priority**: Aaron may want canonical-Phase-2-overlay-animation-now or canonical-defer-entirely. Recommend canonical-defer; canonical-Phase-1 is canonical-dramatically-sufficient.
- **Canonical-text-typography-canon**: provisional canonical-clean-readable-serif-or-sans-serif; Aaron may want canonical-specific-canonical-Furling-Council-document-canonical-typography choice.

---

## Cross-references

- [`cinematic-narration.md`](cinematic-narration.md) — canonical-15-priority-passages with full-canonical-narration-text (this doc canonical-extends with canonical-pan-and-image specs)
- [`callbacks-and-callforwards.md`](callbacks-and-callforwards.md) — canonical-callback-economy + canonical-3-4th-wall-breaks (canonical-Disastrous-Ending §2.5 deploys canonical-4th-wall-break-#3)
- [`halia-profile.md`](halia-profile.md) — canonical-Halia-canon (canonical-Halia-Death + canonical-Council-Briefing cinematics)
- [`humor-pass.md`](humor-pass.md) — canonical-Furling-humor-doctrine (canonical-Others-never-funny canon applies to canonical-First-Other-Vessel cinematic)
- (parallel chat) `the-endings.md` — canonical-6-tier endings (canonical-6 ending-cinematics in §2.5)
- (parallel chat) `the-fall-of-mh-lai.md` — canonical-Fall canon (canonical-Fall cinematic §2.4)
- (parallel chat) `the-final-conflict.md` — canonical-Drev-Tok + canonical-Crossing-Opens (cinematics in §2.5)
