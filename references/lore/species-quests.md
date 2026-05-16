## Species Quests (one per species, bidirectional)

> Every slice species has one canonical quest: **they want a concrete thing from us, we want a concrete thing from them.** This is the species' narrative center of mass — the encounter that turns first contact into a relationship. Branching outcomes feed [win-condition-and-methods.md](win-condition-and-methods.md)'s terminal-status framework. Schema in [species-design-schema.md §6](species-design-schema.md).

The list below is the slice authoring target. Detail per-quest grows as we author it; for the design pass, what matters is the *shape* — "this is the trade" — not the full dialog FSM.

## Slylandro Observers — *The Cloaking Satellite*

- **They want**: continuance. The Slylandro can't lift their own gas-bag bodies out of the atmosphere. Their only viable terminal status is *Cloaked* (Homesteader path) or *Migrated* (Precursor path, requires building them a hyperspace-capable evacuation lift).
- **We want**: the **Hyperspace-Echo Sensor Pattern** — when the Slylandro drift-think in the upper troposphere, their pulse patterns interfere with hyperspace echoes in a measurable way. Recording the interference gives the Furling Steward an Other-detection sensor module a generation ahead of the current one.
- **Bridge**: the cloak works *because* it uses the same interference pattern the Slylandro generate naturally — installing a satellite is essentially turning their atmosphere into a permanent quiet-field. The Slylandro must consent (they're sentient evacuees, not livestock) and they must teach you the pattern. Refusal of consent leaves *Eliminate* on the table for the Cleanser faction.
- **Bidirectional reward**: their cloak satellite goes up; your scanner module installs.
- **Branches**:
  - Persuader/Hide path: cloak satellite installed → terminal **Cloaked**
  - Precursor path: build them a lift → terminal **Migrated** (expensive, late slice)
  - Cleanser path: refuse to help → Cleanser faction enforces **Eliminated**
  - Defender path: leave them be → **Pre-sentient** (lore-tagged false; they're already sentient, so this is a delusion that ends in **Eliminated** by the Others arriving)

## Proto-Ur-Quan + Proto-Qor-Ah — *The Uplift Dilemma*

- **They want**: nothing from us — they're pre-sapient mid-uplift. The "want" is the Mycon-managed continued nudging that's already happening; the question is whether the Steward *continues* or *stops* it.
- **We want**: clarity on what happens next. The Council is split. Persuaders argue for completing the uplift to sapience so we can persuade them to Migrate; Cleansers argue for cleansing the pre-sapient stock before they cross the detection threshold; Defenders argue to halt-and-leave.
- **Bridge**: the player runs an observation arc — three encounters showing the proto-Ur-Quan establishing dominance hierarchy, the proto-Qor-Ah escalating purification ritual, and a glimpse of what the merged sapient form would look like. The quest's *deliverable* is the Steward's recommendation to Council.
- **Bidirectional reward**: the recommendation drives the slice's biggest moral choice; the Council reaction grants either **Persuader**, **Cleanser**, or **Defender** faction standing.
- **Branches**:
  - Continue uplift → both species mature → become Migration cases (later slice content; for slice, this just sets up the SC2-era domination canon)
  - Stop uplift → terminal **Pre-sentient** (slice-clean, SC2 canon-clean)
  - Cleanse → terminal **Eliminated** (Cleanser standing +; Persuader / Defender standing −−)

## Mycon Biots — *The Deep Child Whisper*

- **They want**: continued service. The Mycon were created by the Furlings as terraformers and are happy at it. They ask for **terraforming directives** to keep the work flowing.
- **We want**: the **Mantle-Resonance Bio-Architect** module — a Mycon-derived organ that grows the Steward's lander tractor-beam radius and accelerates lander replication, by repurposing the same mantle-stir biology the Mycon use to plant seeds. This is a permanent ship upgrade with real combat-AI relevance (faster lander cycle = faster mineral haul = faster repair).
- **Bridge**: the deal is good — until the Steward notices the FIRST_WHISPER state in their dialog. A subset of the biot mass is beginning to develop sentience through the "Deep Child" emergence. If the player accepts the bio-architect module and ignores the whispers, the slice climax includes a Them-Corrupted biot combat encounter (the Deep Child's awakening attracts the Others). If the player reports the whispers to Council early, the bio-architect is still delivered but a suppression directive accompanies it — terminal **Pre-sentient** preserved.
- **Bidirectional reward**: Bio-Architect module installed; Mycon terraforming directives delivered.
- **Branches**:
  - Suppress whispers → **Pre-sentient** (Persuader / Defender +)
  - Allow emergence → new sentient species → must be handled like another Slylandro/Arilou (cloak / migrate / etc.)
  - Cleanse the heretical biot subset only → **Pre-sentient** for rest, but Cleanser standing rises and Persuader standing falls
  - Allow + ignore → Them-corrupted combat encounter; biots end **Eliminated** by the Others on arrival regardless

## Arilou Lalee'lay — *The Sage's Gift* *(already implemented through Sage dialog)*

- **They want**: the Council's *decision* on the Migration timetable. The Arilou are leaving for Quasi-Space regardless; they want a clean handoff so they aren't blamed for the leftover problem.
- **We want**: **Quasi-Space access** (portal spawner + portal map) — already implemented as the Sage's gift in `dialog/characters.py:arilou_sage()`, side-effect `_grant_quasispace_portal`.
- **Bridge**: the Sage delivers the gift unconditionally because they pity the Steward, but at the cost of an obligation — the Sage expects the Steward to *speak for* the Arilou view at Council. (Council scene is later content; for the slice, this is a flag set on the player profile.)
- **Bidirectional reward**: portal spawner gained; the Steward owes the Sage a speech.
- **Branches**:
  - Speak for the Arilou at Council → terminal **Hidden** (Arilou voluntary exile, Arilou standing high)
  - Refuse to advocate → terminal **Hidden** anyway (they leave regardless), but Arilou standing low — affects future encounters
  - Council overrides Arilou advocacy with Cleanser doctrine → **Eliminated** of any holdouts (rare and ugly)

## Androsynth Refugees — *The Distress Beacon*

- **They want**: medical aid — they arrived with dimensional-shear injuries from the decursion attack that displaced them. The Steward can deliver a **shear-repair fab pattern** from the lander fabricator + Bio-Architect work.
- **We want**: the **Androsynth Distress Beacon** — an unimpeachable recording of the Others' decursion attack on their original timeline (their *future*, our era's some-millennia-later). This is the slice's primary "proof of the Others" artifact, used in every later Persuader dialog to convince other species to evacuate.
- **Bridge**: Coel Tessar (the canonical refugee leader) shares the beacon as soon as the Furling Steward proves they can stabilize her crew. The shear-repair lands the wounded; the beacon lands in the Furling Archive.
- **Bidirectional reward**: refugees stabilized → terminal **Migrated** (they cross with the Migration); Distress Beacon in the Bio-Archive's Others section.
- **Branches**:
  - Standard delivery → both halves complete cleanly
  - Steward declines to help (rare) → refugees die; their beacon is recovered from the wreck (still gained), but Persuader standing collapses; Cleanser standing rises (some Cleansers wanted them silenced anyway)
  - Steward fails the fab roll → can retry; never gates the slice

## Mmrnmhrm Sentinels — *The Archive Excerpt* *(optional)*

- **They want**: a **cognitive upgrade** — they've been working unchanged for 3-8 million years and the Sentinel collective has reached the limit of its self-modification ability. The Furling Steward can apply a Bio-Architect-derived neural-substrate patch that re-opens self-improvement.
- **We want**: the **Mmrnmhrm Archive Excerpt** — testimony that *defense doesn't work*. Their entire existence has been "defend the Homeworld"; they outlived their First-Makers, who lost. Used by Defender-faction Furlings to argue *for* Migration ("the Mmrnmhrm proved the alternative").
- **Bridge**: the Mmrnmhrm don't dramatize this — they offer the archive entry as transactional, deliver the patch as transactional. Quiet wry awareness of the absurdity is in their voice.
- **Bidirectional reward**: cognitive patch applied (their continued upgrade-cycle); Archive Excerpt in the Bio-Archive.
- **Branches**:
  - Standard delivery → Defender-faction standing falls (their argument is undermined), Persuader rises
  - Steward declines the patch but takes the Excerpt → small Persuader cost; Defender boost
  - Cleanser arc: a Cleanser Furling argues the Mmrnmhrm should be destroyed before they cross the sentience threshold themselves. The player can advocate for or against; choice affects terminal status
- **Terminal status (depending on path)**: **Migrated**, **Pre-sentient**, or **Eliminated** (Cleanser path)

## Chenjesu Crystalline Collective — *The Resonance Record* *(optional)*

- **They want**: nothing. They are rooted, patient, and unconcerned with departure — their crystalline substrate is invisible to the Others and they have lived through a prior Culling already. *They will remain.*
- **We want**: the **Resonance Record** — testimony, slowly delivered, of the *last* Culling. Millions of years ago. Witnessed from a rooted position. The slice's most cosmologically significant reveal: the Others come in cycles, the Furlings are not the first to face this, and rooted patience may be the *one* defense that works.
- **Bridge**: the Chenjesu offer the record in slow present-tense utterances. They ask nothing in return because they need nothing. The Furling Steward can offer a gift of mineral nutrients to accelerate their slow growth — accepted with no change in obligation, in true Chenjesu form.
- **Bidirectional reward**: Resonance Record in the Bio-Archive (and unlocked as evidence in Council dialog); the Chenjesu remain rooted in good condition.
- **Branches**:
  - Standard contact → terminal **Pre-sentient** (below detection threshold, no action needed); Defender standing rises (their argument validated by Chenjesu precedent)
  - Cleanser argues they're sentient and should be eliminated before transition → big moral fight; the slice's cleanest test of the Persuader/Cleanser axis
  - Player chooses to *mobilize* the Chenjesu (heretical hubris) → outside slice scope; flag for full game

## Quest Authoring Order (matches priority of dialog FSM work)

1. **Arilou Sage** ✅ — already implemented; portal gift drives the QuasiSpace flow.
2. **Slylandro Cloak** — tutorial-extension; first sentient evacuee, anchors the "Cloak" terminal status.
3. **Androsynth Beacon** — Act 2 milestone; the Others-proof artifact is foundational to every later Persuader dialog.
4. **Mycon Whisper** — the moral pivot; introduces the suppression-vs-emergence choice and the Bio-Architect upgrade.
5. **Proto-Ur-Quan/Qor-Ah Uplift** — Act 3 dilemma; biggest choice; Council standing pivot.
6. **Mmrnmhrm + Chenjesu** *(optional)* — exploration encounters that reward the curious player. Defender-faction argument-building.

## Cross-quest Reward Stack (slice end-state)

A player who completes every quest cleanly ends the slice with:
- Slylandro Cloaking Satellite installed (or evacuated)
- Hyperspace-Echo Sensor module
- Mycon Mantle-Resonance Bio-Architect
- Quasi-Space portal + portal map ✅
- Androsynth Distress Beacon (in Archive)
- Mmrnmhrm Archive Excerpt (in Archive)
- Chenjesu Resonance Record (in Archive)
- Faction standings shifted by their choices (Persuader / Cleanser / Defender / Denier balance)

That stack is the slice's "you've earned everything" baseline. Cleanser-route players have fewer artifacts but higher Cleanser standing. Defender-route players have more Archive entries and lower combat involvement.
