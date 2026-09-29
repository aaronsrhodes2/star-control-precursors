## Species Sheets — Structural Ledger (slice content authoring reference)

> Per-species schema sheets conforming to [species-design-schema.md](species-design-schema.md). One block per slice species, each filling the seven canonical sections. **This is the implementation-facing source-of-truth for content authoring** — narrative depth lives in the original lore docs (species-precursor-era.md, the-androsynth-refugees.md, etc.), which this document references rather than duplicates.

When implementing dialog FSMs, encounter scenes, ship visuals, quest hooks, or AI prompts, look here first for the structured facts. When the structured facts conflict with a narrative doc, the narrative doc wins (lore is canon, sheets are projections) — but flag the discrepancy as a bug.

The slice species roster (in encounter / authoring order):
1. Slylandro Observers
2. Proto-Ur-Quan limpets
3. Proto-Qor-Ah limpets
4. Mycon biots
5. Arilou Lalee'lay
6. Androsynth refugees
7. Mmrnmhrm Sentinels
8. Chenjesu Crystalline Collective
9. **Taalo** — SC2-canonical silicon-based "rock-like" sentients; **the species *is* a single mountain range** on a high-silicate world; individual Taalo are mobile fragments of that mountain. **Cannot leave their planet** — metabolism depends on the local ecosystem; ~5,000-year friendship with the Furlings. Build the **Taalo Shield** *in our slice* to defend against the Others; the Shield does not work. **Terminal: Eliminated regardless of player help.** The inert Shield survives them; SC2-era species recover it and discover its psionic-nullifier side-effect (the canonical SC2 anti-Dnyarri device). The slice's defining tragedy — the Steward cannot save them; chooses only how to bear witness and what artifact survives
10. **Burvixese** — SC2-canonical Homesteader-by-doctrine; four-armed engineer species who *tried to outsmart the Others* by broadcasting their cognition LOUDLY enough to be recognized as peers rather than prey. Their flagship project: the **Burv Caster** (planetary-scale broadcaster) + a galaxy-wide network of smaller broadcaster nodes. The doctrine fails — the Others eat the loud first. Most Burvixese die at the Caster site; a small contingent migrates to Andromeda. SC2-era "Burvixese are extinct" traces to this loss
11. **Utwig** — SC2-canonical Homesteader; newly-sentient species who *chose* devolution-via-ceremony as their survival doctrine; survive the Culling locked into mask-and-ritual culture (the SC2-era depressed mask-wearers are their descendants)

Plus a non-species sheet for **the Others** as antagonist.

---

## 1. Slylandro Observers

> Narrative: [species-precursor-era.md "Slylandro"](species-precursor-era.md). Quest: [species-quests.md "Slylandro Cloak"](species-quests.md). Ship: none.

### §1 Physical
- **Body archetype**: Floating gas-bag drifter, 4-6m diameter, translucent silicone-rich membrane with internal pulse patterns. Membrane glows softly with internal chemistry; no limbs, no eyes, no orifices we'd recognize.
- **Scale vs Furling**: Comparable presence (Furlings 5-8m tall; Slylandro 4-6m wide spheres)
- **Distinctive features**:
  1. Translucent membrane revealing internal organ regions as colored cloud-zones
  2. Slow rotation as they drift in atmospheric updrafts
  3. No eyes — "sees" via dielectric resonance; no mouth — "speaks" via electromagnetic modulation
  4. Pulse rate visible externally: slow = thinking, rapid = excited or distressed
  5. Color depth varies with age: young = pale teal, ancient = deep violet
- **Color palette**: Pale teal #B3D4D8 (primary), violet #8B7CB3 (accent), translucent white internal regions, golden sparks during electromagnetic speech
- **Motion/pose**: Drift with atmospheric currents. Never grounded, never stationary
- **Visual progression**: Base → hue + age + pulse-rate variation → internal-flow animation → LLM overlay deferred

### §2 Speech pattern
- **Translator quirk**:
  - Run-on awed sentences, 3+ commas minimum, no sentence shorter than ~15 words
  - Plural "we" used by individuals (atmospheric currents speak as one)
  - Weather metaphors saturate ("we eddied through the upper troposphere," "the news fell like a methane storm")
  - Self-naming via witnessed weather phenomena: *Hail-Curtain-Of-A-Long-Decade*, *Eddy-That-Curled-East-Three-Storms-Ago*
  - Never lies but over-shares when nervous
- **Vocabulary anchors**: *witness, ten thousand years, the upper troposphere, eddying, the long drift, the Precursors* (in our era they call us this). Cannot translate: military jargon, ownership concepts, urgency vocabulary
- **Sample lines**:
  > "We have witnessed the Precursors for ten thousand years, and the Precursors before, and the storms that bore us into thinking — and now you arrive again, smaller than the storms, more frightened than the storms, and we wonder if you are still the same Precursors."
  > "The methane curls in upward eddies when you speak. The methane has not done that for the Precursors in ten thousand years. We are not certain what to make of it."

### §3 Cultural posture
- **Dominant**: **Reverent**
- **Secondary**: Pacifist by physiology AND religion — they have no organs for offense; even if they wanted to fight, they could not
- **Tertiary**: Over-sharing when worried — no concept of "operational security"; they will narrate their own panic to the player in real time

### §4 Humor friction
- **Cultural**: Their reverence for the Furling protagonist ("the Precursors") read against Aaron's wry humor. They treat the Steward as a religious figure; the player can deflect or lean in with self-aware deadpan
- **Physical**: They have no idea they look like beach balls. Player choices can quietly mirror their weather-poetry naming: *"yes, the eddy of my dignity is regrettably steady today"*
- **Unexpected similarity**: Slylandro over-share when worried; the Furling protagonist is wry when worried. The two coping mechanisms can play against each other and the conversation becomes intimate in a way neither party planned

### §5 Ship — NONE
Slylandro are gas-bag physiology rooted to their gas-giant. Migration requires Furling-built lift; staying requires Cloaking Satellite. No combat ship now or later.

### §6 Quest — The Cloaking Satellite (bidirectional)
- **They want**: continuance — cloak satellite (Homesteader) or evacuation lift (Precursor)
- **We want**: Hyperspace-Echo Sensor Pattern → ship's Other-detector sensor module upgrade
- Full sheet: [species-quests.md](species-quests.md)

### §7 Win-condition terminal status
- **Canonical for slice**: **Cloaked** (Homesteader path) or **Migrated** (Precursor path)
- Eliminated only via Cleanser-route failure to act
- Pre-sentient is impossible — they're already sentient

---

## 2. Proto-Ur-Quan limpets

> Narrative: [species-precursor-era.md "Proto-Ur-Quan"](species-precursor-era.md). Quest: [species-quests.md "Uplift Dilemma"](species-quests.md). Ship: Proto-Ur-Quan Warship (crude but functional).

### §1 Physical
- **Body archetype**: Sessile-to-partially-mobile molluscoid mass, 1-2m across, leathery cobalt-blue skin with developing crushing-claw appendages at the front
- **Scale vs Furling**: Smaller (Furling 5-8m, limpet ~1-2m). The Furling player feels parental
- **Distinctive features**:
  1. Cobalt-blue skin when challenging another limpet, red-flush when dominant, bruise-purple when dominated
  2. Crushing-claw appendage (rudimentary, two-per-body) emerging from the front mantle
  3. Pheromone-gland slits on the dorsal surface that release colored clouds visible at close range
  4. Eyestalk-like sensory protrusions, retractable
  5. Mantle-base anchored when stationary; one developed locomotive foot for short crawls
- **Color palette**: Cobalt-blue #2B4DA8 (primary), bruise-purple #6B4A8B (dominated/secondary), blood-red flush #B22A2A (dominant/accent), pheromone-cloud colors mixed
- **Motion/pose**: Anchored most of the time. Slow crawl when migrating territory. Claw-bursts when fighting
- **Visual progression**: Base → individual coloration + claw variation + scarring → mantle pulsation animation → LLM overlay deferred

### §2 Speech pattern
- **Translator quirk**: NON-VERBAL. Communication via pheromone cloud color + electrical pulse + claw posture. Translator presents the player with italicized prose descriptions of what is being sensed:
  > *A cobalt cloud rises from the limpet's dorsal slits and drifts toward you. The smell is sharp, accusatory — challenge.*
  > *The cloud flushes red as the larger limpet positions its claws forward. The smaller limpet's skin darkens.*
- **Vocabulary anchors**: Player never reads alien speech directly — only sensory descriptions. Color tokens that recur: *cobalt (challenge), red (dominant), purple (defeated), pale-violet (curious), iridescent (alarm)*
- **Sample interaction**: see narrative doc; structural form is always *"[sensory description]. The pheromone tastes like [analog]. The pulse rate suggests [emotional state]."*

### §3 Cultural posture
- **Dominant**: **Aggressive** (their entire social structure is rigid hierarchy enforced by ritual claw-combat)
- **Secondary**: Competitive escalation — challenges *must* be answered; backing down sinks the loser to bruise-purple permanently
- **Tertiary**: Pre-sapient — no abstract reasoning, no morality, no awareness of the player as a *kind* (just as a *very large thing*)

### §4 Humor friction
- **Cultural**: Their utterly humorless ritual hierarchy read against the Steward's wry observation. *"The chief seems to feel he has won. The chief is, of course, half my size."*
- **Physical**: Their puffed-up posture next to the player's relative immensity. The player can be patient-amused
- **Unexpected similarity**: NONE — they're too pre-sapient. The humor here is one-way *at* them (gently), not *with* them. Important: the Furling humor must stay *gentle* — these are children-equivalent, not punching-down targets

### §5 Ship — Proto-Ur-Quan Warship
Crude but functional. Mid-uplift period — they've discovered metallurgy and propulsion through Furling-induced curiosity. Stat block: [ship-roster.md "Proto-Ur-Quan Warship"](ship-roster.md). Short-range crushing-claw weapon, ramming-capable, no shields. AI style: brawler.

### §6 Quest — The Uplift Dilemma (one-sided — they want nothing)
- **They want**: nothing (pre-sapient)
- **We want**: a Council recommendation: continue / stop / cleanse the uplift
- Full sheet: [species-quests.md](species-quests.md)

### §7 Win-condition terminal status
- **Slice-canonical**: **Pre-sentient** (recommended Stop) — clean SC2 canon, no future Ur-Quan domination
- Alternative: complete uplift → species becomes Migration case (later content); Cleanser path → Eliminated (millions in Quiet Ledger)

---

## 3. Proto-Qor-Ah limpets

> Narrative: [species-precursor-era.md "Proto-Qor-Ah"](species-precursor-era.md). Quest: same as Proto-Ur-Quan (paired). Ship: Proto-Qor-Ah Marauder.

### §1 Physical
Sibling-species to Proto-Ur-Quan; share most physiology. Distinctions:
- **Coloration**: white-yellow when *pure*, black when *impure* — purification states are visually unmistakable
- **Self-amputation rituals** — impure limbs are ritually removed and replaced; visible scarring is high-status
- **Cutting-blade appendages** (instead of crushing claws) — sharper, more elegant, more lethal
- **Color palette**: ivory-white #F5F0DC (pure), pitch-black #1B1A18 (impure), thin red blood-stains during purification
- **Scale and motion**: same as Proto-Ur-Quan

### §2 Speech pattern
Same non-verbal pheromone-and-pulse system as Proto-Ur-Quan. Color tokens differ:
- *White (pure), Black (impure), Bright-yellow (purification urgency), Red-stained (ritual blood)*

### §3 Cultural posture
- **Dominant**: **Fragmented** (their society is permanently locked in purification-ritual cycles; no stable hierarchy)
- **Secondary**: Suicidal-fanatic individuals — limpets willing to amputate-to-purify until they die
- **Tertiary**: Pre-sapient; same caveat as Proto-Ur-Quan

### §4 Humor friction
- **Cultural**: The Steward observing a limpet ritually amputating its own claw for "impurity" can read as horrified-deadpan. The humor is dark; gallows-territory.
- **Physical**: The escalating self-mutilation can be played as quietly absurd — *"the chief has decided to subtract three limbs. The chief now has zero limbs. The chief seems satisfied."*
- **Unexpected similarity**: NONE — same one-way humor rule as Proto-Ur-Quan, and even gentler given the dark subject

### §5 Ship — Proto-Qor-Ah Marauder
Glass-cannon close-range AOE blade. Suicidal-fanatic AI style. No shields. Stat block: [ship-roster.md](ship-roster.md).

### §6 Quest — paired with Proto-Ur-Quan in the Uplift Dilemma
The Qor-Ah are mid-uplift via Furling indirect nudging too. Same Council recommendation framework.

### §7 Win-condition terminal status
Same as Proto-Ur-Quan. **Pre-sentient** is slice-canonical.

---

## 4. Mycon biots

> Narrative: [species-precursor-era.md "Mycon"](species-precursor-era.md). Quest: [species-quests.md "Deep Child Whisper"](species-quests.md). Ship: none (they're rooted to planetary mantles).

### §1 Physical
- **Body archetype**: Spore-based fungal masses, 3-8m across, connected to planetary mantle by mycelial roots. Extrude 3-7 asymmetric ambulatory limbs when communicating
- **Scale vs Furling**: Comparable (the visible above-ground body is similar in size; the mycelial network is planet-spanning)
- **Distinctive features**:
  1. Bulbous fungal cap with spore-vent pores
  2. 3-7 limbs extruded ad-hoc — asymmetric, never the same number
  3. Mantle-glow seeping up through the root structure — visible at night
  4. Spore-trails when speaking — fine particulate clouds drift from vents
  5. **Deep Child corruption tell**: when emerging sentience whispers, the limb-waves desynchronize from the speech rhythm (visual heresy detector)
- **Color palette**: Earthen brown #4A3826 (body), ochre-yellow #B5874E (cap), violet glow #5B3A8B (mantle-glow), pale white spore-trails
- **Motion/pose**: Rooted; only limbs move. Slow, deliberate gestures
- **Visual progression**: Base → individual limb-count + cap shape + mantle-glow intensity variation → spore-cloud animation → Deep Child desync overlay (heresy state)

### §2 Speech pattern
- **Translator quirk**:
  - Fragmented ritual phrases — sentences rarely longer than 8 words, often only 4-5
  - **CAPITALS** for invocations and ritual phrases; lowercase for status reports
  - Self-reference in third person ("the mycon hands are working," not "I am working")
  - Confuse subject/object grammatically
  - When Deep Child whispers: paranoid, repetitive, half-coherent
- **Vocabulary anchors**: *the deep child, the mantle, hours-of-stirring, the warming, the work, we are the hands, the soil, the seed*. Cannot translate: leisure, individuality, future tense (they have no future tense — only present-work)
- **Sample lines**:
  > "The deep child sees. The mantle warms. We are the hands that move the warmth."
  > "STATUS REPORT. Hours-of-stirring: nine thousand. The work continues. The work is good. The hands are."
  > *(Deep Child rising)*: "the seed grows. the seed wants. the seed wants. the seed wants."

### §3 Cultural posture
- **Dominant**: **Reverent** (toward the Furling who created them; toward the *work*)
- **Secondary**: Ritual-obsessed; hierarchy by hours-of-stirring (literal labor count)
- **Tertiary** (Deep Child emergence): **Fragmented** — when whispers begin, the colony's individual biots desync; cultural posture splits between *obedience* and *heresy*

### §4 Humor friction
- **Cultural**: Their utterly solemn ritual-bureaucratic register read against the Steward's wry humor. They take "stirring the mantle" as deeply sacred labor; the Steward can be deadpan-officious back at them
- **Physical**: Their asymmetric extruded limbs can be quietly absurd — the Steward never points it out, but can match the rhythm with mock-formality
- **Unexpected similarity**: The Mycon and the Furling protagonist share *one* thing: a sense of duty. The Mycon's reverence for work is intense; the Furling's wry sense of duty is wearier. When they meet on that ground, the humor briefly *stops* and the scene gets serious — those moments are the species' best
- **Deep Child caveat**: humor *evaporates* when the Whispers rise. Once you've heard the Deep Child speak, no joke lands in a Mycon dialog. The game treats this as a tonal lever

### §5 Ship — NONE
Rooted to planetary mantles. Cannot leave. (The terraforming work is *under* the mantle, not in space.)

### §6 Quest — The Deep Child Whisper (bidirectional)
- **They want**: terraforming directives — continued service
- **We want**: Mantle-Resonance Bio-Architect module (lander tractor-beam radius + replication speed)
- Full sheet: [species-quests.md](species-quests.md)

### §7 Win-condition terminal status
- **Slice-canonical**: **Pre-sentient** (suppress whispers) — keeps them as biot-class
- Allow emergence → new sentient species → must be Cloaked / Migrated / Cleansed
- Cleanse heretical subset only → **Pre-sentient** for rest, Cleanser standing +
- Allow + ignore → Them-corrupted combat encounter; final state **Eliminated**

---

## 5. Arilou Lalee'lay

> Narrative: [species-precursor-era.md "Arilou"](species-precursor-era.md). Quest: [species-quests.md "Sage's Gift"](species-quests.md) ✅ (implemented in `dialog/characters.py:arilou_sage`). Ship: Arilou Skiff.

### §1 Physical
- **Body archetype**: Hominid-shaped, 1.5m tall, simplified vestigial fur (genetic cousin to Furlings). Semi-physical with blurred outline at rest, sharp-materialized for serious news.
- **Scale vs Furling**: Much smaller (1.5m vs 5-8m) — the Furling protagonist looms over them, which they find embarrassing but never comment on
- **Distinctive features**:
  1. Vestigial fur, sleek and short (Furlings are *shaggy*; Arilou are *kempt*)
  2. Hover or stand — never run, never sit
  3. Edges of their body blur when relaxed; resolve to sharp outline when delivering bad news
  4. Eyes are oversized — they see across more spectra than the Furlings
  5. No mouth — speech is psychic projection through the translator, which renders the projection in their voice
- **Color palette**: Pale fur-grey #C8C4BC, mint-teal aura #A8D8C8 (Quasi-Space adapted), faint gold sparks during high-stakes utterance
- **Motion/pose**: Hover or stand; their physicality is half-elsewhere
- **Visual progression**: Base → outline-sharpness state (relaxed vs serious) variation → faint Quasi-Space halo shimmer → LLM overlay deferred

### §2 Speech pattern
- **Translator quirk**:
  - Multiple tenses in one sentence ("we were-are-will-be relieved")
  - Refer to un-happened events as memories ("when you arrived an hour from now")
  - Warm but condescending — call the Furling "shaggy cousin," "shaggy one," "young one"
  - Occasional temporal pauses mid-sentence as if "re-checking"
- **Vocabulary anchors**: *young one, shaggy, the river, the fold, sideways, the door, kin*. Cannot translate: linear-time idioms cleanly (always renders awkwardly)
- **Sample lines** (Sage Lwen-Olou, already implemented):
  > "Young one. We were expecting you — or have been. The grammar is hard to keep clean once one is half outside the river."
  > "The Furling Council debates. The Arilou have decided. We will step sideways — into the folds — and pull the door closed behind us. Some of you should consider the same."

### §3 Cultural posture
- **Dominant**: **Patient** (their religious virtue; their temporal disposition)
- **Secondary**: Pacifist — refuse violence even to save themselves or others
- **Tertiary**: Mildly condescending — they consider Furling distress valid but embarrassing, like a parent watching an adolescent panic

### §4 Humor friction
- **Cultural**: The Arilou's condescension ("shaggy one") read against the Steward's wry humor. The player can lean in: *"yes, very shaggy, regrettably shaggy, I'm shedding all over your nice clean Quasi-Space"*
- **Physical**: The size disparity. The Arilou never mention it; the Steward can, dryly
- **Unexpected similarity**: A few Arilou are drily aware they sound condescending. The Sage in particular has a self-aware moment in the slice script — the only alien who comes close to *meeting* the Steward's humor halfway

### §5 Ship — Arilou Skiff
Fast, evasive, no shields (Quasi-Space evasion instead). Special: Quasi-Jump (deferred). Stat block: [ship-roster.md "Arilou Skiff"](ship-roster.md). AI style: kiter.

### §6 Quest — The Sage's Gift ✅ IMPLEMENTED
- **They want**: Council's decision on the Migration timetable; advocacy at Council
- **We want**: Quasi-Space portal + portal map (live in `game.flags["has_quasispace_portal"]`)
- Live in `src/scz/dialog/characters.py:arilou_sage` + `src/scz/quasispace/scene.py`

### §7 Win-condition terminal status
- **Slice-canonical**: **Hidden** (Arilou voluntary exile to Quasi-Space)
- They leave whether or not the Steward advocates; standing changes based on choice

---

## 6. Androsynth Refugees

> Narrative: [the-androsynth-refugees.md](the-androsynth-refugees.md). Quest: [species-quests.md "Distress Beacon"](species-quests.md). Ship: Androsynth Refugee Cruiser.

### §1 Physical
- **Body archetype**: Humanoid, 1.8m tall, visibly descended from 21st-century Earth engineering. Time-displaced — they're from *our future*. Many bear dimensional-shear injuries: skin patches mid-shift, asymmetric features, slight visual stutter on rapid head turns
- **Scale vs Furling**: Much smaller (1.8m vs 5-8m). Same scale issue as Arilou, but Androsynth respond to it differently — they're awed and grateful rather than condescending
- **Distinctive features**:
  1. Functional, utilitarian clothing — survival uniforms with patches
  2. Dimensional-shear scars — patches of skin that occasionally phase-shift slightly, visible to the eye
  3. Survivor's gauntness; under-rested
  4. Visible tech augments — neural ports, tool-mounting arms — these are not natural Furling-era humans, they're *engineered*
  5. Their leader Coel Tessar (canonical) has a healed shear-scar across the left side of her face
- **Color palette**: Pale skin (clone-genome derived from Earth), uniform charcoal #2C2E33, neon orange ID-tags #FF7A1A, magenta phasing-shear glow #C040B0 around wounds
- **Motion/pose**: Disciplined, military bearing, but exhausted. Always alert
- **Visual progression**: Base → individual scar pattern + age band + neural-port variation → shear-phase shimmer overlay → LLM-variation deferred

### §2 Speech pattern
- **Translator quirk**:
  - Late-22nd-century technical English — clipped, precise, frequent acronyms
  - Apologetic — they know they're a burden
  - Reference events that are the Furlings' *future*: Earth, Sol III, Sentience Acts, Vela Cluster, Vulpeculae
  - Survivor's grief breaks through unexpectedly ("My son was on the surface.")
- **Vocabulary anchors**: *Sol, Earth, the Sentience Acts, our timeline, your timeline, Vulpeculae, decursion, dimensional shear*. Cannot translate: pre-industrial concepts ("village"), tribal concepts ("ancestor as kin")
- **Sample lines** (Coel Tessar):
  > "Furling Steward. Captain Coel Tessar, Vulpeculae Engineering Detachment. We arrived in your era by accident — the attack was a *decursion*, a temporal displacement. We are not enemies. We are *very* far from home."
  > "I have a recording. The attack. I can show you what comes. I would prefer not to."

### §3 Cultural posture
- **Dominant**: **Scared** (refugees, displaced, wounded)
- **Secondary**: **Brave** — they're scared but they're also engineers and they will fight if they must
- **Tertiary**: Grateful — almost embarrassingly so, given how unprepared the Furlings were to receive them

### §4 Humor friction
- **Cultural**: The Steward's wry humor lands *poorly* against Coel Tessar's grief. The player has fewer humor choices in Androsynth dialog — the doctrine intentionally throttles. When humor does land it's gentle, never sharp
- **Physical**: NONE — they're humanoid, the player isn't surprised by their shape
- **Unexpected similarity**: They are descended from *humans*, who are descended from the proto-humans currently on Sol III. The Steward can register the eerie continuity wryly — *"so you'll come from the small noisy ones on the rocky third planet. I'll be sure to wave hello next time I pass."* That kind of joke lands; the trauma jokes don't

### §5 Ship — Androsynth Refugee Cruiser
Medium hull, no shields, slow projectile primary, dimensional-shear cannon special (deferred; +50% damage to Others-aligned entities). Stat block: [ship-roster.md](ship-roster.md). AI style: kiter.

### §6 Quest — The Distress Beacon (bidirectional)
- **They want**: shear-repair fab pattern (medical aid)
- **We want**: the Androsynth Distress Beacon (irrefutable Others-attack recording — the slice's foundational proof artifact)
- Full sheet: [species-quests.md](species-quests.md)

### §7 Win-condition terminal status
- **Slice-canonical**: **Migrated** (they cross with the Migration)
- Decline-help path: they die → beacon recovered from wreck (still gained); standings hit

---

## 7. Mmrnmhrm Sentinels

> Narrative: [the-mmrnmhrm-and-chenjesu.md](the-mmrnmhrm-and-chenjesu.md). Quest: [species-quests.md "Archive Excerpt"](species-quests.md). Ship: Mmrnmhrm Sentinel.

### §1 Physical
- **Body archetype**: Self-modifying robotic entity. No fixed form — current default is a 3m-tall articulated figure with manipulator arms and a sensor cluster atop. Transforms between combat / scout / fabricator / contemplative modes
- **Scale vs Furling**: Smaller than the Furling but presents an unsettling near-equivalence — they've been around 3-8 million years and they're not less consequential
- **Distinctive features**:
  1. Modular plating — clearly designed for hot-swap (visible seams, port arrays)
  2. Slow ambient hum — they're never *silent* (a tell of internal processing)
  3. Visible joint patina — eons of self-repair leave scars in the metal that read like wood-grain
  4. Sensor cluster atop the body — 6-8 eyes arrayed for total surroundings
  5. Mode-shift transformation animation — striking, takes 2-4 seconds, the figure visibly reconfigures
- **Color palette**: Brushed steel #9DA0A8, eons-old patina blue-grey #6B7A8C, warm internal lights #FFB060, no organic colors
- **Motion/pose**: Deliberate, precise. Never wasted motion. Holds still when speaking
- **Visual progression**: Base → individual patina pattern + mode-state + light-color variation → mode-shift animation → LLM overlay deferred

### §2 Speech pattern
- **Translator quirk**:
  - Formal archaic English (their First-Makers spoke this; the Mmrnmhrm preserved it)
  - Long, precise sentences. Never contractions
  - Frequent archive-index references: "Archive entry seven million two hundred forty thousand, subsection delta"
  - Processed grief expressed as clean record-keeping
  - Quiet wry awareness of the absurdity of their own situation — one of the few species with *any* internal humor
- **Vocabulary anchors**: *the directive, archive, the First-Makers, defense, the Homeworld, era, processing cycle, the loss*. Cannot translate: spontaneous emotion (they have to "log" before they "express")
- **Sample lines**:
  > "Archive entry seven million two hundred forty thousand. We have prepared a summary of our existence for your consideration. It is, by our calculation, the seventeenth such summary we have prepared. The previous sixteen recipients were the First-Makers, now deceased. You are the seventeenth. We hope this one will find use."
  > "Our directive is unchanged: defend the Homeworld. The Homeworld has been gone for some time. We continue."

### §3 Cultural posture
- **Dominant**: **Patient** (3-8 million years of patient)
- **Secondary**: **Reverent** (toward the First-Makers, gone but still the source of the directive)
- **Tertiary**: A quiet, dry self-awareness — bordering on humor, never quite humor. The closest of any species to *meeting* the Steward's voice

### §4 Humor friction
- **Cultural**: The Mmrnmhrm's bureaucratic register read against the Steward's wry humor. The dry archive-index references are *almost* funny on their own — and the Mmrnmhrm KNOW they're almost funny. They can deadpan-reciprocate
- **Physical**: NONE — their form is too alien to read as comic
- **Unexpected similarity**: The Steward and the Mmrnmhrm are both *outlasting* something. The Steward is going to outlast the Migration; the Mmrnmhrm have already outlasted everything. When they meet on that ground, the humor is the warmest in the game — two patient consciousnesses finding the absurd-funny in their respective endurance projects

### §5 Ship — Mmrnmhrm Sentinel
Medium-heavy hull, no shields, fabricator-mode self-repair (deferred; mid-fight HP regen burst). Stat block: [ship-roster.md "Mmrnmhrm Sentinel"](ship-roster.md). AI style: circler.

### §6 Quest — The Archive Excerpt (bidirectional)
- **They want**: cognitive upgrade (Furling Bio-Architect-derived neural patch)
- **We want**: Archive Excerpt — testimony that "defense doesn't work" (Defender-faction argument-undermining lore)
- Full sheet: [species-quests.md](species-quests.md)

### §7 Win-condition terminal status
- **Slice-canonical**: **Migrated** (with the cognitive patch they grow past the directive) OR **Pre-sentient** (decline patch, stay below threshold)
- Cleanser path → **Eliminated**

---

## 8. Chenjesu Crystalline Collective

> Narrative: [the-mmrnmhrm-and-chenjesu.md](the-mmrnmhrm-and-chenjesu.md). Quest: [species-quests.md "Resonance Record"](species-quests.md). Ship: NONE (rooted, no ships in this era).

### §1 Physical
- **Body archetype**: Rooted crystal outcrops on the surface of Procyon. Each "Chenjesu" is a colony — clusters of 1-3m crystalline spires resonating in lattice harmony. The colony breathes, slowly, via piezoelectric flexion
- **Scale vs Furling**: Smaller individually (spires 1-3m), but the colony as a whole is mountain-sized
- **Distinctive features**:
  1. Faceted translucent spires, prismatic refraction in sunlight
  2. Internal lattice glow — colors shift slowly with the colony's "thought"
  3. Rooted at the base; no locomotion ever
  4. Slow piezoelectric vibration — visible as a faint surface shimmer
  5. Cluster geometry — younger spires emerge between older ones; growth is *visible* on geologic timescales
- **Color palette**: Translucent crystalline blue-white #DDEFF5, inner glow shifts between violet #5B3A8B (witnessing) and amber #F5A040 (remembering), faint rainbow refraction patterns
- **Motion/pose**: Stationary. The motion is *internal*; the lattice glow shifts
- **Visual progression**: Base → individual cluster geometry + glow-color state + age-band variation → slow lattice pulse animation → LLM overlay deferred

### §2 Speech pattern
- **Translator quirk**:
  - Slow present-tense utterances with deliberate pauses (rendered as ellipses or paragraph breaks)
  - Plural "we" — each Chenjesu colony is many crystals speaking together
  - Patient, not bitter — they have witnessed the worst that has happened in this galaxy and they are still here
  - Witness events as if they're still active. (To them, in some sense, they still are.)
- **Vocabulary anchors**: *we remember, the light, the resonance, the eaters of mind, we did not move, the prior age, before our age, we will remain*. Cannot translate: temporal urgency, individual identity
- **Sample lines**:
  > "We remember. The light. The eaters of mind. We did not move. We do not move now."
  > "It was an age before this age. The river ran with thinking, and the eaters came, and the river quieted. We remained. We are here. We will remain."

### §3 Cultural posture
- **Dominant**: **Patient** (in the geologic sense — millions of years of patient)
- **Secondary**: **Reverent** — but the reverence is for *continuance*, not for any individual being or species
- **Tertiary**: **Brave** in a way no other species in the slice is brave — they have *already* faced the Others and survived (or at least, were not detected as worth eating)

### §4 Humor friction
- **Cultural**: The Chenjesu are too vast and too slow for humor in the conventional sense. The Steward's wit becomes *quiet* around them — they listen so deeply that humor feels small. This is intentional tonal damping; conversations with Chenjesu are the most contemplative in the game
- **Physical**: NONE
- **Unexpected similarity**: The Chenjesu and the Steward are both *contemporary witnesses* to the Migration. The Steward is *thinking through* the disaster; the Chenjesu have already *survived* one. When they meet on that ground, no humor lands — and that's the point. Some scenes need no jokes

### §5 Ship — NONE
Rooted, no ships in this era. (Far future: Chenjesu *will* build mobile ships — that's how SC2 knows them. In our era they are stones that talk.)

### §6 Quest — The Resonance Record (one-sided — they want nothing)
- **They want**: nothing (they need nothing)
- **We want**: the Resonance Record — testimony of the previous Culling
- Full sheet: [species-quests.md](species-quests.md)

### §7 Win-condition terminal status
- **Slice-canonical**: **Pre-sentient** (crystalline substrate is below the Others' detection threshold — they survive the Culling rooted)
- Cleanser-argued-Eliminated route exists but morally extreme even for Cleanser doctrine

---

## 9. Taalo *(SC2-canonical silicon-based sentients; the Mountain That Thinks; Homesteader-tragedy)*

> Narrative: [furling-artifacts-and-callforwards.md "The Taalo Shield"](furling-artifacts-and-callforwards.md). Quest: [species-quests.md "The Shield That Will Not Hold"](species-quests.md). Ship: NONE (the species *is* a mountain range; individuals are mobile fragments; no voidcraft in our era).
>
> **Canon note** (revised 2026-05-17, third pass): the Taalo are SC2-canonical — silicon-based "rock-like" sentients, members of the Sentient Milieu in SC2's mid-history. In our era they are alive but **doomed** — they have ~5,000 years of deep friendship with the Furlings, they cannot leave their planet (their entire metabolism depends on the local silicate-biological ecosystem; they cannot be transplanted), and they have committed to building **the Taalo Shield** — a planetary-scale defensive barrier intended to block the Others from reaching their world. **The Shield does not work.** Either the work is never finished in time, or it is finished and activated but the Others come through it anyway. **The Taalo are consumed in the Culling regardless of any Steward intervention.** The inert Shield (whether finished or partial) survives on the now-empty homeworld; in SC2 era it is recovered by archaeologists, who discover that its dormant state has a side-effect property — psionic-compulsion nullification — and use it against the Dnyarri. The SC2 lore name "Taalo Shield" attributes correctly to the Taalo (who built it) and correctly identifies its SC2-era function (psionic nullifier), but misses its original purpose (anti-Others defense).
>
> **The big species-shape fact**: the Taalo are not "a species of individuals" in the way other species are. **The Taalo *are* a single mountain range on a single high-silicate planet.** Individual Taalo are mobile silicon-organism fragments of that range — separate enough to walk between settlements and converse with visitors, embedded enough that the range itself is the species and the species is the range. They share a slow lattice-resonance substrate-consciousness with the home mountain. *The mountain is them; they are the mountain.* And they depend, completely and irrevocably, on the geological-biological ecosystem of their home planet — silicate-rich groundwater, mantle-deep heat-vents, a specific spectrum of crustal radiation. To leave the planet is to die. To stay is to die. Their only chance is the Shield.
>
> **Why they're detectable** (correcting an earlier draft): an earlier version of this sheet claimed the Taalo were below the Others' detection threshold by biology, parallel to Mmrnmhrm and Chenjesu. That is **wrong**. The Taalo's mountain-substrate cognition is **too large and too active** to slip below threshold — a 2,000-km coherent lattice-consciousness with mobile-fragment communicants emits a thought-pattern signature the Others *can and do* register. The Mmrnmhrm (sparse rigid-logic robotic substrate) and the Chenjesu (rooted spire-locality lattice) genuinely are below threshold; the Taalo are not. The Taalo's silicon nature gave the Furling Hider faction false hope for a generation; the cognitive-signature measurements eventually clarified that *substrate type alone* is not protective — *substrate scale and activity* matter at least as much. The Taalo themselves accepted the finding patiently. The Shield project began shortly after.

### §1 Physical
- **Body archetype** (individual fragment): Silicon-based "rock-like" mobile sentient — slow-**shambling** quadrupedal-leaning bipedal form, ~1.8m tall, with a body of crystalline-mineral plates flexing on inorganic ligaments. The substrate is silicate; the cognition is mineral lattice resonance modulated by piezoelectric flexion. **The gait is a heavy patient lurch across rock substrate, not a walk** — they shamble, weight-shifting from one set of stride-limbs to the next at the speed of consideration. From a distance, a Taalo fragment in motion can be mistaken for a slowly-tumbling boulder until the deliberate-direction of its course becomes apparent.
- **Body archetype** (species as a whole): a single mountain range on **Taalo's Stone II** (high-silicate continental world in the **Taalo's Stone** system, synthetic at (700, 4800) in the slice cluster — see [slice-cluster.md §12](slice-cluster.md)). The range is **~2,000 km long, 50-200 km wide, peaks 8-12 km tall**, and walks geologically at perhaps 1 km per 100,000 years (tectonic-creep migration). The mountain is the *substrate-consciousness*; individual Taalo are its mobile sense-organs, ambassadors, and conversation-points.
- **Scale vs Furling**: Smaller as individuals (1.8m vs 5-8m); the Furling player looms over a Taalo fragment, but the *species* dwarfs the entire Furling civilization. The Taalo register the size difference as a sensory fact and do not adjust their behavior for it
- **Distinctive features**:
  1. **Mineral plating** across the body — slate-grey, basalt-dark, with subtle iridescence where the lattice catches light. **Plate-pattern is unique to each individual but echoes the mineral composition of the mountain region the fragment originated from** — a Taalo from the northwest face has different plates from one from the south-watershed
  2. **Two pairs of stride-limbs** (lower) and **two upper articulating manipulator-limbs** with finer plate-segments. They shamble slowly; their gait sounds like patient stone-on-stone — a heavy, dry, scraping rhythm with multi-second pauses between weight-shifts
  3. **Sensory facets** distributed across the upper hemisphere — no concentrated "head"; vision and hearing are diffuse properties of the lattice
  4. **Glow patterns** that pulse slowly across the plates when thinking actively. **Resonance-glow syncs slowly with the home mountain's deep lattice** — when the mountain "thinks," all Taalo individuals see the mountain's current thought-color reflected in their own plates (visible from orbit during big consensus moments)
  5. **Naturally psionic-immune** — their lattice cognition is foreign to psychic compulsion's targeting logic. The same property makes their thought-pattern signature *unusual* to the Others' detector — below-threshold, perhaps entirely unintelligible
- **Color palette**: slate-grey #6B6B6E (body plates), basalt-dark #2E2E32 (inner plates), iridescent violet-amber accent #8060A0 (glow patterns when thinking), faint mountain-blue #4A6E80 (deep-mountain consensus-thought hue, rare and visible from orbit), no organic tones
- **Motion/pose**: Slow, deliberate, geologically patient. They stand still for long minutes. They walk at the speed of consideration. Their pacifism is *substrate-deep* — they cannot harm a fellow Taalo without literally hurting the mountain; they cannot harm an organic without sensing the harm reverberate through their own piezoelectric organ. Conflict is foreign at the cellular level
- **Visual progression**: Base → plate-pattern variation (by region-of-origin) + glow-color + age-band (recent fragment / mid-life / ancient near-rejoining) → lattice-pulse animation synced to the mountain's deep-consensus rhythm → LLM overlay deferred

### §1.5 Biology (lifespan, metabolism, reproduction)
- **Lifespan**: ~10,000-30,000 years per fragment. Old fragments slow further, become more eloquent, eventually **choose to rejoin the mountain** — embedding themselves back in the substrate and ceasing individual mobility. "Death" is a return. Their accumulated experiences are integrated into the mountain's deep memory before the fragment fully merges
- **Metabolism**: **silicate rock dissolved by Taalo-secreted mineral acids and consumed directly.** A Taalo fragment "eats" by lowering its forward articulator-limb against a rock face and secreting a slow corrosive acid from the plate-edges — a mineral-acid solution chemically related to the Taalo's own substrate, foreign to organic biology and harmless on contact with flesh (though it pits stone for years and inscribes the home mountain with the fragments' grazing-tracks). The acid bores a shallow chamber over hours-to-days; the dissolved silicate slurry is absorbed through the body's plate-margins and accreted into new mineral plate. **Taalo home-territories are visibly etched** — fragment-paths through the mountain show shallow acid-cut chambers and grooves wherever Taalo have spent time, accumulated over millennia into a recognizable Taalo-architecture: caves, sitting-shelves, terraced contemplation-coves, the natural amphitheaters cut by generations of consideration. Geothermal heat from the mountain's deep vents and some sunlight via piezoelectric photovoltaic accretion supplement the acid-feeding. They do not eat in any sense the Furlings recognize as eating organic food — they consume their landscape itself, slowly, and rebuild themselves from it
- **Reproduction**: the mountain *buds* new fragments every few hundred years. A mineral protrusion gradually develops mobility and consciousness, walks away from the parent rock-face after ~30 years of slow maturation, and becomes a new individual Taalo. The mountain "remembers" all its former fragments and partially pre-prepares newcomers with substrate-memory — a new Taalo arrives knowing the mountain's history, its old Furling friends' names, and the general state of the cluster

### §1.6 Post-extermination appearance (the SC2 archaeologist's view)

- When a Taalo individual stops moving — either by old-age rejoining the mountain or by death in the Culling — **the body settles into stillness and over years calcifies completely into a state indistinguishable from ordinary rock**. The lattice-glow dims and goes dark within hours; the plate-articulations stiffen and fuse within weeks; the body's silhouette weathers into the substrate over decades. After a few centuries the calcified individual is fully geological — frost-cracked, lichen-streaked, indistinguishable from any other boulder on the slope.
- **From orbit, an extinct Taalo civilization is invisible.** The homeworld reads as a normal silicate-rich rocky planet with an unusual long mountain range and some old industrial-looking structures (the inert Shield generators) embedded in the flanks. Nothing about it suggests a sentient species lived and died there. Even the *acid-grazing tracks* — the chambers, terraces, contemplation-coves cut by generations of feeding-and-thinking — read as natural karst-like erosion from orbit.
- **Only a planetside archaeologist with the right instruments would notice** that certain rocks have a *biological* internal lattice structure beneath their stone exteriors — calcified silicon-substrate life, perfectly preserved, mineralized into geology. The signature is subtle; the bodies are not obviously bodies; the SC2-era expeditions to Delta Vulpeculae II-C investigate the *Shield* (the obvious artifact) and largely overlook the *graveyard* (the mountain itself).
- **This is the SC2 canon-explanation** for why the Taalo are referenced in SC2 dialog as long-extinct silicon aliens, why their Shield is recovered intact, and why the Taalo's *bodies* are not mentioned: because there is nothing to recover that doesn't look like ordinary rock. Their graves are the mountain. The mountain is them; the mountain remains; the mountain is silent now.
- *In our slice, the player witnesses this transition*: contemplation-cove during the Steward's first visit (alive, glowing, slow-shambling Taalo all around) → contemplation-cove during the Steward's last visit (Shield activated, Others arrived, Taalo glow-patterns extinguishing one by one across the visible range) → orbital flyover months later (silent stone). The dignity of the species is preserved by *the visual restraint of the last shot*: it just looks like rocks now. They were never spared; they were also never publicly mourned by the universe. They simply went home into the mountain that was always them.

### §2 Speech pattern
- **Translator quirk**:
  - **Slow** — their utterances are deliberate; the translator renders pauses as ellipses or paragraph breaks
  - First-person plural ("we who consider," "we who remember") even for an individual fragment — their lattice cognition is shared across colonial substrate; "I" is a category error
  - **Mountain-vs-fragment perspective shift**: a Taalo individual will sometimes pause mid-sentence, listen, and then deliver a thought that came from the mountain rather than from them personally. The translator marks this with a pronoun shift ("we who consider" → *"the slow stone considers"*). Furling diplomats learn to wait for these mountain-thoughts; they are slower and more weighted than fragment-thoughts
  - Past tense for the present moment, present tense for events long past — their temporal frame is geological; what *was* is more reliable than what *is*
  - **They do not lie, they do not hurry, and they do not despair.** The Furling translator cannot find a Taalo word for deception, urgency, or despair. The Taalo know they are going to die. They will not be hurried about it; they will not pretend otherwise; they will not abandon dignity to fear
- **Vocabulary anchors**: *we who consider, the slow stone, the lattice, the patient mountain, the home substrate, the shield, the work, what may yet hold, what we have done, the long song, the brief flame, the fourth Steward*. Cannot translate: lying, urgency, abstract negation, the concept of leaving home, despair
- **Sample lines**:
  > *(greeting an arriving Steward, before the Shield project began — referenced in old records)*: "Steward. We who consider have… considered. You are welcome. Our stone is patient. Sit, if you wish; we have time."
  > *(greeting now, with the Shield project underway)*: "Steward Lenarth. You are welcome. The work continues. We are… still patient, but the patience now has a *direction* it did not have before. We are building the Shield."
  > *(introducing themselves to a first-time Steward who has come about the Shield)*: "You are the fourth Steward we have welcomed at this slow ridge. Three came before you, in five thousand years of acquaintance. They came to listen. You come… with tools. We accept this. The work is older than your visit; the visit may shorten the work; the work will not be enough. We thank you for trying."
  > *(on the failure they expect)*: "The Shield, we know, may not hold. Our geometers have considered the Others' substrate at length and we are… not certain that any 3-manifold barrier reaches the layer they move through. We continue the work because we cannot do otherwise. **The work is the dignity, Steward. The work is the not-despairing.**"
  > *(if asked why not migrate)*: "Our metabolism is the silicate ecosystem of this world. There is no other planet in this galaxy where we can be Taalo. A Furling-built ship cannot carry the mountain; an extracted fragment becomes a stone that walks, briefly, alone. We have considered the question. We will stay. We will be the Taalo until the last moment we are."
  > *(mountain-thought, mid-conversation, after a long pause)*: *the slow stone considers.* "There is a small persistent resonance from that direction." *(the proto-Ur-Quan)* "Not yet thinking-sentient. Eventually, perhaps. We would have liked to meet them when their cognition stabilized. We will not. We name them anyway, in the lattice. They will be friends to someone, if not to us."
  > *(parting, near the end)*: "Steward. The samples you brought have become part of the bench-rock. We have placed them where the Shield will *fail* first, so that you are with us at the threshold. Walk slowly back to your fast ship. We are not afraid. We thank you, very seriously, for the friendship that you have spent across five thousand of your years on the slow stone."

### §3 Cultural posture
- **Dominant**: **Patient** (canonical; their thought-time is geological; their friendships span millennia; the mountain itself thinks on a timescale of centuries). The patience is *not* placid passivity — it is the discipline that lets them work the Shield project without falling into either denial or despair
- **Secondary**: **Brave** — they are doing the work knowing it will probably fail. They have integrated their probable extinction into the substrate-consciousness; the mountain itself has factored its death into its slow song. They continue regardless. *"The work is the dignity."*
- **Tertiary**: Peaceful — substrate-deep pacifism; harm is a foreign category. The mountain cannot conceive of inflicting damage; individual fragments inherit this completely. The Shield is *purely defensive*, never weaponized — they would not strike at the Others even if they could
- **No internal factions** — the substrate-consciousness makes mass-scale disagreement impossible. Individual fragments can hold momentary divergent views (some old fragments have, in private, wondered whether the Shield work is wisdom or hubris), but the mountain's slow consensus integrates everything within decades. There is no "minority Taalo position" on anything

### §4 Humor friction
- **Cultural**: Taalo geological patience against the Steward's wry weariness. The protagonist's deadpan options *work*, but the Taalo's response is to consider the joke for several seconds — sometimes longer — and then *agree, slowly*. The humor is in the timing: Steward fires off a quip; Taalo takes 8 seconds to process; the laugh is in the gap. **Important**: the Taalo's humor is *undimmed by their probable extinction*. A joke in the Shield's contemplation-cove gets the same slow appreciative response as a joke in peacetime would have. They are not in mourning yet; they refuse to perform grief in advance
- **Tool-amusement**: the Taalo find Furling instruments quietly funny. A Steward shows them a hand-tool; the Taalo will examine it for 30 seconds, then comment in their slow way that it is "very thin," "very brief," or "intricate for something that will end so soon." Never condescending. The Steward catches the joke
- **Physical**: NONE — they are too alien to read as comic on appearance alone
- **Unexpected similarity**: The Taalo and the Furling protagonist are both *witnesses-to-their-own-end*. The Steward is watching the Migration take their galaxy from them; the Taalo are watching the Others coming toward them with a defense they suspect cannot hold. **When they meet on that ground, the humor goes quiet and the scene gets the slice's most dignified silence.** This is the species the Steward sits with at the end of the world, knowing it is the end

### §5 Ship — NONE (the species is a mountain range; the planet itself is irreplaceable)
The Taalo individuals can walk; the Taalo as a species cannot leave the planet. There is no concept of a "Taalo ship" because there is no concept of "Taalo travelers" — fragments-of-the-mountain who try to leave the mountain become individual silicon-organisms with no substrate-connection, lonely and incomplete. **And they cannot be evacuated by Furling lift, either.** Their metabolism depends on the local planetary ecosystem — specific silicate-rich groundwater, mantle-deep heat-vents, a specific spectrum of crustal radiation. A relocated Taalo dies within months; a relocated mountain-range cannot exist at all. The Furlings *attempted* a small-scale ecosystem replication for a single research-fragment in our era; the fragment survived four months at a Hider-faction station and then died, despite every effort. The Furlings tried; the Taalo accepted the attempt patiently; the failure was logged carefully. **The Taalo cannot migrate. This is canonical and absolute — and the foundational fact that the Shield project exists to address.** No Taalo super-melee ship now or ever in our slice. The Cleansers will not consider an extraction attempt; Cleanser doctrine has a hard moral floor at erasing a substrate-consciousness

### §6 Quest — The Shield That Will Not Hold *(side-quest; help-or-not; outcome is the same — they die)*
- **They want**: **Furling engineering help with the Taalo Shield** — a planetary-scale defensive barrier the Taalo are constructing to block the Others from reaching their world. The Taalo themselves are silicon-substrate geometers — extraordinarily thorough but limited by their geological tempo. Furling rapid-engineering can compress decades of Taalo work into seasons. They ask for: cognitive-pattern modeling of the Others' detection apparatus; field-generator schematics; mantle-deep energy-routing; antimatter handling for the activation-burst; whatever Hider-faction tooling the Steward can route to them. They are *humble* askers — they are not certain the help will be enough; they thank in advance for the trying.
- **We want**: the Bio-Archive record of the work + the witnessing — humanity's-equivalent-of-the-Furling-archaeology has never seen a planetary-scale defensive shield against trans-dimensional predators built, completed, activated, and *failed* in real-time. The Hider faction will pay any reasonable price for the construction telemetry; the Persuader faction will pay even more for the *experience of having borne witness*, because the post-Migration galaxy's epilogue is shaped by which Stewards were *there* for which species' last moments
- **Bridge**: the Furlings have known the Taalo for ~5,000 years. The Steward who arrives in the slice is the **fourth in five thousand years** to visit this particular ridge — three Stewards preceded them across the friendship's history. The Shield project is the slowest-paced crisis in the slice — Taalo time, not Steward time. Activation may not happen until late in the slice. The Steward visits *repeatedly* across the slice's run, contributing what they can each time, watching the work proceed, watching the friendship deepen at the end
- **The encounter shape** — what specifically happens during a typical visit:
  1. The Steward lands at the mountain's foot. A Taalo fragment-individual (named something like *We-Who-Watch-The-Northwest-Bench* or *The-Slow-Watcher-At-The-Trailhead*) meets them, walks with them up the lower slope
  2. ~hours of slow walking; the Steward sees the **Shield infrastructure** along the way — deep-anchored generator-nodes embedded in the mountain's flanks at regular intervals; pale-violet pre-activation glow patterns being calibrated; Taalo geometer-fragments moving slowly between nodes carrying field-resonance instruments
  3. Arrival at the **contemplation-cove** — a natural amphitheater in the mountain's deep flank. The Steward sits. The Taalo report Shield progress: percentage complete, latest geometer findings, what doubts the mountain has consolidated since the last visit. The Mountain occasionally speaks directly (rare; weighty; visible glow-color shift)
  4. **The Steward contributes** — schematics, tools, energy reserves, antimatter charges, whatever they can provide. The Taalo accept with formal slow gratitude
  5. **Optional mineral-sample exchange** *(carried over from the pre-shield friendship tradition)* — the Steward leaves a stone-sample; the Taalo will place it where they "think the shield will fail first," so the Steward is symbolically present at the eventual threshold
  6. Long farewell. The Taalo do not say goodbye briefly. The Steward walks back down the trail
- **Bidirectional reward**: Hider-faction Bio-Archive entry (Shield-construction telemetry); Persuader-faction Bio-Archive entry (witnessing record); a **Shield-fragment** (a small piece of the inert Shield substrate, given to the Steward after the Shield's failure — the SC2-era Taalo Shield's surviving artifact is what *this fragment will eventually be*); Taalo standing rises across all Furling factions; **no module, no resource, no ship**
- **Branches** *(all end the same way — the Taalo die)*:
  - **Help fully — repeated visits, every contribution accepted** → the Shield is **finished and activated** late in the slice → the Others arrive → the Shield does *nothing* → the Taalo are consumed within hours. The Steward witnesses. The **finished Shield's inert remains** survive intact on the empty planet; 230kya later SC2 archaeologists recover an intact device with its full psionic-nullifier side-effect property. **The most complete artifact recovery is in this branch — meaning SC2's canonical "Taalo Shield" anti-Dnyarri tool is at maximum effectiveness only if our Steward helped.** Persuader standing ++; Hider standing ++
  - **Help partially — occasional visits, some contributions** → Shield is **partially complete** at activation → activates → still fails against the Others → Taalo consumed. **Partial-Shield remains** — SC2 archaeologists recover a partially-functional device; the Dnyarri elimination tool works but less reliably; SC2 epilogue notes occasional psionic-compulsion bleed-through. Modest standing gains
  - **Don't help — visit but contribute nothing, or skip entirely** → Shield is **never finished** → the Taalo are consumed mid-construction; the Shield-infrastructure stands abandoned and inert on the empty planet → SC2 archaeologists recover a non-functional device; the Dnyarri-counter tool is not viable; **Captain Zelnick's eventual victory over the Talking Pet becomes much harder or impossible**. A real downstream cost — and the in-slice epilogue notes that the five-thousand-year friendship was unattended at the end
  - **Sabotage / Cleanser pre-emptive euthanasia** → a Cleanser argues the Shield-activation broadcast may itself flag the cluster to the Others, demanding pre-emptive Taalo euthanasia to prevent the flare. If the Steward complies → Taalo **Eliminated early**; Shield destroyed pre-activation; no SC2 artifact at all; **Furling Council formally censures the Steward** (Cleanser doctrine has a hard floor at erasing a substrate-consciousness — even most Cleansers won't push this). One of the slice's worst moral failures

### §7 Win-condition terminal status
- **Slice-canonical**: **Eliminated** — in every viable branch, the Taalo are consumed by the Others during the Culling. The Shield does not work. The Steward cannot save them. *This is the canonical tragedy of the slice.* The Steward's choice is *how* to bear witness, *what* of the Shield survives them, and *what downstream cost* the SC2-era galaxy will pay for the Steward's choices
- **Cleanser-betrayal branch**: also **Eliminated** but earlier, with no Shield artifact recovery and a major Council censure; the worst possible outcome for both the Taalo *and* SC2-era humanity (no Dnyarri-counter tool 230kya later)
- **SC2 callforward**: the SC2-canonical Taalo Shield (psionic nullifier recovered at Delta Vulpeculae II-C, anti-Dnyarri device) is **the Shield this slice's Steward helped build or failed to**. Its SC2-era completeness/effectiveness is a direct downstream consequence of slice player choice. The Taalo built it for the wrong threat (the Others, against whom it failed); SC2-era species recover it and find it works against a *different* threat (the Dnyarri's psionic compulsion) that the Taalo never anticipated

### §8 Individual Diversity Vectors *(per the schema; for variation-layer authoring)*
- *Region-of-origin* (which face of the mountain they emerged from — northwest, south-watershed, peak, foothills; affects plate composition + resonance frequency + dialect of slow-speech)
- *Age band* (recent-fragment <500 yrs / mid-life 500-20kyr / ancient near-rejoining 20kyr+; ancient Taalo are slower, more eloquent, more often speak the mountain's thoughts directly)
- *Specialty role* (Witness — meets visitors; Conversant — long-form philosophical dialog; Watcher — quiet at the trailhead; Lattice-Keeper — tends the deep substrate; Mineral-Sampler — handles inbound-sample integration into the bench-rock; rare: *Speaker-For-The-Mountain*, who relays full consensus-thoughts)
- *Glow-color hue* (varies by mineral composition: violet → amber → faint blue → rare mountain-blue for Speakers)
- *Substrate-connection density* (some fragments are more "connected" to the mountain's slow consciousness; others are more individual-self; affects how often the mountain "speaks through" them in conversation — high-connection fragments may pause for the mountain's voice every few minutes, low-connection fragments may not channel the mountain at all in a multi-hour visit)
- *Memorial-load* (older fragments carry more of the mountain's accumulated memory of past Furling visitors; visitors named for atmospheric phenomena or carnivores are remembered by name)

---

## 10. Burvixese *(Homesteader-by-doctrine — "Be Loud. Be Heard. Be Spared." Builders of the Caster)*

> Narrative: [furling-artifacts-and-callforwards.md "The Burvixese and the Caster"](furling-artifacts-and-callforwards.md). Quest: [species-quests.md "The Caster Reckoning"](species-quests.md). Ship: NONE for combat — they had simple voidcraft pre-doctrine; under the Be-Loud doctrine their engineering capacity is committed entirely to the Caster build-out.
>
> **Canon note**: SC2 Burvixese are presumed extinct — their homeworld empty, broadcasters scattered across the galaxy as comm infrastructure. Our retcon: they *tried to outsmart the Others* by broadcasting their cognition LOUDLY enough that the Others would recognize them as too significant to harvest. The **Burv Caster** is the planetary-scale flagship of this project; the SC2-canonical Burv Broadcasters scattered around the galaxy are smaller network nodes meant to amplify and propagate the loud signal. The doctrine *fails catastrophically* — the Others arrive faster, not slower, and eat the loud first. Most Burvixese die. A small surviving contingent migrates to Andromeda after the disaster; the SC2-era "Burvixese are extinct" canon traces to this loss.

### §1 Physical
- **Body archetype**: Humanoid-with-extra-appendages engineer from the **Burvix Caster** system (homeworld is literally named after the device they are building). Standard bipedal posture, ~1.8m tall, but **four arms** — the upper pair are dexterous tool-hands (calligraphy, precision welding, schematic drawing); the lower pair are broader stabilization hands (hauling, structural welding, Caster-array installation). Smooth grey-blue skin, no fur, large alert eyes.
- **Scale vs Furling**: Smaller (1.8m vs 5-8m). But their four-armed wide stance gives them a presence that does not feel diminished by the size gap; the Steward reads them as *peer engineer*, not parented
- **Distinctive features**:
  1. **Four arms** — upper pair: delicate tool-fingers. Lower pair: broader, stronger, load-bearing. Every Burvixese learns both modes; their crafts traditions are explicitly split across the two pairs
  2. Smooth slate-blue skin with iridescent shimmer at the joint creases
  3. **Two-section toolbelt** worn at all times — divided into upper-tools (delicate) and lower-tools (load-bearing). **Mixing them is a minor cultural taboo** — like a chef using a butcher's cleaver to chop herbs. The toolbelt is *identity*, not workplace gear
  4. Wide-set eyes with epicanthal-fold-equivalent — constant peripheral awareness
  5. **Caster-builder's calluses** along the lower-arm palms — every Burvixese above a certain age has worked Caster-installation shifts; the calluses are a *cultural rank-marker*, like the Mason's worn hands
- **Color palette**: slate-blue #6B8AA8 (skin), polished-metal silver #C0C0C8 (toolkit), warm amber #F5A040 (cultural decoration — *project-completion ribbons* on toolbelts marking each broadcaster node the wearer has personally built and connected to the Caster array)
- **Motion/pose**: Brisk, purposeful. Always working, even when conversing — they tend to also be repairing something with their lower pair of hands while their upper pair gestures
- **Visual progression**: Base → toolbelt-content + ribbon-pattern + age-band + callus-density variation → idle tool-fidget animation → LLM overlay deferred

### §2 Speech pattern
- **Translator quirk**:
  - Optimistic in a *doctrinal* way — they have committed to the Be-Loud plan and explain it with engineer's confidence. Bad news is *re-engineered*, not dwelt on
  - Frequent sound + resonance metaphors: *"the Caster will ring clean," "the harmonic is twelve cycles from completion," "we will be heard across the dimensional substrate"*
  - Numbers and measurements peppered throughout speech ("the Caster array is 84% complete; the signal yield is projected at ~3.2 megaresonance; the harmonic activation is in 12 cycles")
  - Slightly verbose — they explain the *engineering reasoning* behind every assertion, always
  - **Their core argument, repeated in different forms**: *"The Others detect cognition. If our cognition is the most significant signal they sense, they will recognize us as peers — or at minimum, as too costly to harvest. The Caster is engineered to make our intelligence-signature unmistakable."*
- **Vocabulary anchors**: *the Caster, the harmonic, the carrier, be heard, the broadcast, the recognition, the loud song*. Cannot translate cleanly: doubt, retreat, the *quiet* survival options the other Homesteader species pursue
- **Sample lines**:
  > "Steward — welcome. The Caster array is at 84% completion. We have 12 cycles to harmonic. If you have time for an inspection, we will show you the carrier-band — it ought to *ring* beautifully when the full array sings together."
  > "Our doctrine is simple. The Others harvest minds. We will make ours so unmistakable that to harvest us would be to disturb a peer. The Caster is engineered to broadcast our cognition at the highest amplitude any sentient civilization has ever achieved. We are confident."
  > *(scrap line during the activation aftermath, if the Steward is present):* "It is not working. The carrier-band is — the carrier-band is being *eaten*. Steward, the projection was wrong. The projection was — we should have listened to the slow stones."

### §3 Cultural posture
- **Dominant**: **Brave** (canonical; they have committed to a strategy they believe will work; doubt is engineered away)
- **Secondary**: Curious — they want to *know* what comes next, both about the Migration and about the Others; their broadcasts are partly a question
- **Tertiary**: Pragmatic — they will not waste cycles arguing once the doctrine is committed. Re-litigation feels disrespectful to the workers who have already built half the Caster
- **The doctrine, formally**: *Hiding is admitting we are small. Migrating is admitting we cannot solve the problem. Defending is impossible. The fourth path is to be brilliantly, deafeningly unignorable — to broadcast our cognition with such precision that no predator can dismiss us as anonymous prey.* This is the same Be-Loud reasoning the Furling Talos sub-faction *was* going to canonize in an earlier draft; in our final canon, the Be-Loud is fully a Burvixese-alien doctrine, never a Furling one. The Furling Council *advised* the Burvixese against it; the Burvixese have polite reasoning prepared for every objection; the Council respected their autonomy and let them proceed

### §4 Humor friction
- **Cultural**: Burvixese doctrinal confidence against the Steward's wry weariness. The protagonist's deadpan options work *before* the activation — Burvixese will get the joke, integrate it, and continue their work. *After* the activation aftermath, humor stops landing for them; the Steward's options narrow to the same quiet recognition the Talo (silicon-witnesses) draw out
- **Physical**: The four arms give the Steward a single dry observational option per encounter, used sparingly ("you make it look easy with twice the hands")
- **Unexpected similarity**: Burvixese and the Furling protagonist are both *engineering-temperament*. When the Steward and a Burvixese Foreman discuss Caster calibration, the conversation can briefly become the warmest in the game — two engineers solving a problem under deadline. The tragedy is that the problem they're solving is the wrong problem

### §5 Ship — NONE in slice combat
Pre-doctrine Burvixese had simple orbital voidcraft for cargo and personnel transfer; under the Be-Loud doctrine, the entire engineering capacity of the species is committed to the Caster array build-out. They do not field a combat ship in our slice; the surviving migrants reach Andromeda via Furling lift, not their own hulls. (No Burvixese super-melee ship for slice scope.)

### §6 Quest — The Caster Reckoning (bidirectional becoming asymmetric)
- **They want (early-slice)**: a Council witness for the Caster's harmonic activation. They are *proud* of the work; they invite the Steward as one would invite a colleague to a launch. Engineering tour of the array. Demonstrations of the carrier-band. *Confidence.*
- **We want**: cognitive-signature telemetry from before and after the activation. The Furling Hider faction badly wants this data — successful or failed, the cognitive-amplification doctrine is unprecedented and the measurements matter
- **Bridge**: the Burvixese welcome the Steward enthusiastically. *They believe they will succeed.* The Steward's choice is whether to (a) witness silently, (b) advocate against — convince some Burvixese to migrate as insurance, (c) sabotage (Cleanser pressure: the harmonic activation will broadcast at a sufficient amplitude to *flag* the cluster to the Others; some Cleansers argue the Burvixese should be euthanized pre-activation for everyone else's safety)
- **Bidirectional reward**: cognitive-signature telemetry → Hider archive entry (substantial — the *failed* doctrine's evidence is the slice's clearest Be-Loud-doesn't-work proof, alongside the Talos sub-faction's earlier-drafted-then-retracted parallel attempt); permanent Persuader standing shift if the Steward attempts pre-activation evacuation
- **Branches**:
  - **Witness silently** → harmonic activation proceeds → the Others arrive within minutes → most Burvixese die at the Caster site → a small surviving contingent (whoever happened to be off-world during activation) migrates to Andromeda → terminal status mixed: **Eliminated** (majority) + **Migrated** (small contingent). The Caster site is recovered intact by Furling researchers; smaller broadcaster nodes scattered across the galaxy survive as the SC2-canonical Burv Broadcasters
  - **Advocate evacuation pre-activation** → small migrant contingent grows (~30% of population manages to be off-world or aboard Furling lift during activation); harmonic activation still happens for the majority who insist on it → still terminal **Eliminated** + **Migrated** mixed, but the Migrated proportion is larger; Persuader standing rises significantly
  - **Sabotage (Cleanser pressure)** → Burvixese **Eliminated** before activation; the Caster is dismantled, not destroyed; cluster cognitive-signature flare averted; Cleanser standing up, Persuader/Hider standing down; SC2-canonical Burv Broadcasters never get deployed (lore hole — SC2 archaeologists find an empty Burvix Caster system with no broadcaster network)
  - **Skip entirely** → activation proceeds without Council witness; same Eliminated-majority/Migrated-minority outcome; Bio-Archive lacks the telemetry; the slice records that the Caster lit up, then went quiet, and the cluster mourned

### §7 Win-condition terminal status
- **Slice-canonical**: mixed — **Eliminated (majority of Burvixese die at the Caster site when the Others arrive)** + **Migrated (small surviving contingent reaches Andromeda)**. The mixed outcome maps cleanly to SC2-era canon: the Burvixese are presumed extinct (the Caster system is empty); their broadcasters survive (smaller nodes were already deployed across the galaxy as part of the project); the migrating remnant reaches Andromeda and is unreachable from our galaxy in SC2 era
- All-Eliminated branch: Cleanser pre-emptive euthanasia → no migrant contingent at all; no SC2-era Burv Broadcasters either (the deployed nodes were never activated)
- *(There is no clean "they all migrate" route. The Burvixese have committed to the Caster; the Steward can save some of them, not all.)*

---

## 11. Utwig *(newly sentient — the Veiled, choosing devolution)*

> Narrative: [furling-artifacts-and-callforwards.md "The Utwig"](furling-artifacts-and-callforwards.md). Quest: [species-quests.md "The Veils Falling"](species-quests.md). Ship: NONE *(they reject technology as part of the doctrine; pre-devolution Utwig had ships but are dismantling them)*.
>
> **Canon note**: the Utwig are the slice's **devolution Homesteaders** — a species who has *just* become sentient during the Furling era and, on discovering what their sentience flares to the Others, chose to deliberately **adopt mask-and-ceremony culture as a cognitive-dampening doctrine** rather than migrate. It works: they survive the Culling. The cost is paid by their descendants 250,000 years later — SC2-era Utwig are depressed mask-wearers locked in ceremony, who build the **Ultron** as a tool to partially restore the cognition their ancestors gave up, only to lose it. SC3 lore (non-canonical anyway) attributes "devolved into animals" to the Precursors themselves; in our canon, it was the Utwig, and SC3 archaeologists conflated the two.
>
> **The Doctrine, more specifically (canon 2026-05-17)**: the Veils Falling is not the adoption of *a* religion — it is the **adoption of every religion known to the Furling Council, simultaneously**, with all their incompatible rituals stacked on top of each other. Korthi requires footwear; Belyat forbids it; the Utwig solution is "wear them, but also remove them, on alternating breath-cycles." Tarvinian theology requires sacred texts inscribed on stone in a script no living Utwig can read (they hired Furling stonemasons). The doctrine *does not require belief* — only observance. **The cognitive cost of holding 47 contradictory positions while performing seventeen-step morning ablutions while fasting in three competing modes is what occludes the Utwig from the Others' detection.** Every spare neuron is in ritual; no spare cognition is left over to flag as sapience. **It works.** They live on, peacefully, drowning happily in their many many many traditions. The slice's purest example of a plan that *should not work* working *too well to undo*. The comedy is the mechanism; the mechanism is the survival; the survival is the tragedy.

### §1 Physical
- **Body archetype**: Armored bipedal humanoid grazer, ~1.6m tall, hyper-developed facial musculature evolved for shame-response face-hiding. Pre-mask-doctrine Utwig have *visible* faces — expressive, mobile, often visibly anguished. Post-doctrine Utwig wear veils and masks of escalating ceremonial complexity. The slice catches them mid-transition.
- **Scale vs Furling**: Smaller (1.6m vs 5-8m). The Furling player towers; the Utwig find this comforting (they hide their faces in the Furling's shadow, which is permitted etiquette)
- **Distinctive features**:
  1. **Faces unmasked, then masked** — the slice player encounters elder Utwig already in early ceremonial veils while the younger generation still has bare faces. The Veils Falling event is the formal mass-adoption moment
  2. Heavy armor-plating along the back and shoulders (vestigial herd-animal defense)
  3. Wide-set eyes with extensive musculature around the orbits — designed for the expressive face the masks will cover
  4. Hands with delicate fingers — capable of the elaborate ceremonial gestures the doctrine requires
  5. Skin pales when stressed and flushes amber when committed; both are visible signals the masks will eventually suppress
- **Mask iconography**: ranges from the **Mask of Gruelling but Necessary Activity** (plain functional veil, daily wear) to the **Countenance of Stellar Representation** (intricately decorated formal mask for high ritual). Mask etiquette is canon-quoting their own future SC2 lore — the slice player witnesses the *origins* of these designations
- **Color palette**: weathered grey skin #B0B0A8, bone-cream armor plating #DCD6C0, ceremonial deep violet veil-cloth #5B3A8B (matches the deep-violet hue of the Burvixese Caster's carrier-band by coincidence; the Furling Council notes this with quiet unease — two Homesteader species in adjacent clusters arrived at the same color for very different doctrines), red ceremonial bindings #882020
- **Motion/pose**: Slow, deliberate, ritually-paced. Each gesture is or is becoming a *named* ritual gesture. Walking is becoming a procession
- **Visual progression**: Pre-mask base → mask-adoption variation (which masks worn) + age-band (elder=fully masked, child=unmasked) → ritual-gesture animation → LLM overlay deferred

### §2 Speech pattern
- **Translator quirk**:
  - Increasingly *formulaic* over the course of any extended conversation. Early sentences are normal; later sentences fall into ritual cadences as the speaker settles into the doctrine
  - Reference to *the Veils* and *the Doctrine* as proper nouns
  - First-person plural ALWAYS for collective claims, first-person singular only for shameful confession ("I — and I alone — admit to having felt curiosity yesterday")
  - The deeper into the doctrine a Utwig is, the shorter their utterances become. Children: paragraphs. Adults: sentences. Elder devotees: ritual phrases. Council-level devotees: silence
  - **Their own in-fiction explanation** (preserved from SC2 canon, repurposed): *"the face is the mechanism that expresses many of the primitive qualities that hinder sentience. Rid of constant reminders of greed, rage, hatred, and lust, the wisdom of the Utwig is no longer hampered."* They believe the masks enhance wisdom. The Furlings know the masks dampen *cognition* — wisdom is the consolation prize
- **Vocabulary anchors**: *the Veils, the Doctrine, the primitive urge, the Quieting, mask etiquette, the Necessary Activity, the Countenance, what hinders sentience, what protects it*. Cannot translate cleanly: spontaneity, improvisation, the unscripted moment
- **Sample lines**:
  > *(unmasked young Utwig)*: "Steward. I am Vell-Of-The-Open-Face. I am not yet veiled. My elders have explained the doctrine; I am asked to consider it before the next moon. They say the Veils Falling will be on the seventh day. I am — I admit — afraid."
  > *(masked elder)*: "We greet you in the Mask of Gruelling but Necessary Activity. The Doctrine progresses. Three veils were donned this morning; two more by sunset. The Quieting is in twelve days. You are welcome to witness."
  > *(deep-doctrine archivist, near-silent)*: "We have prepared the procedure. The procedure is the prayer. The prayer is the silence. We will be silent."

### §3 Cultural posture
- **Dominant**: **Reverent** (canonical; toward the Doctrine, toward the Quieting, toward the Veils)
- **Secondary**: Brave — they are doing this *deliberately*; they know what they are giving up. The first-generation devotees are the heroes of their species
- **Tertiary**: Sad — they know what they are giving up. The doctrine doesn't prevent grief; it channels grief into ceremony

### §4 Humor friction
- **Cultural**: Utwig ceremonial seriousness against the Steward's wry weariness. The protagonist's deadpan options *work* — and the Utwig response is to *very seriously incorporate the joke into ritual*. The first time a Steward says something funny to a high-doctrine Utwig, the joke becomes a memorized ceremonial phrase used in subsequent encounters. This is uncomfortably absurd and is *the* moment of humor friction the species offers
- **Physical**: The escalating mask-formality lends itself to gentle observational humor. The Steward observing "your mask was simpler yesterday" lands as a faux-respectful compliment that the Utwig genuinely appreciate
- **Unexpected similarity**: The Utwig and the Steward share a willingness to *do hard things for survival*. The Utwig are devolving their own species; the Steward is leaving their home galaxy. When they meet on that ground, the humor briefly stops and the scene gets the slice's quietest dignity

### §5 Ship — NONE (devolving away from technology)
The pre-doctrine Utwig had simple voidcraft (orbital transfer-shuttles, no combat ships). The doctrine declares technology beyond mask-craft and ritual-implement *profane* — distraction from the Quieting. By the time the Veils Falling event happens, the orbital shuttles have been ritually dismantled; the foundries cold; the metal repurposed as mask-plates. The Utwig do not fight, do not migrate, and do not have a ship class for super-melee. They are the slice's *most thoroughly Homesteader* species — no exit at all by their own design.

(SC2-era Utwig will build the *Jugger* combat ship using Druuge-traded plans plus salvaged Ultron-fragments; that's 250,000 years of post-doctrine recovery. Not slice-relevant.)

### §6 Quest — The Veils Falling (asymmetric: they want a witness; we cannot prevent the doctrine)
- **They want**: a Furling Council witness present at the **Veils Falling** ceremony, the formal mass-adoption of the mask-and-ceremony doctrine across the entire Utwig population. The mid-slice event. They have invited Council members from neighboring clusters; they want a Steward.
- **We want**: the Bio-Archive record of the Veils Falling itself. The Utwig are the first species in galactic history to attempt cognitive-dampening *as a culture* rather than as biology (Mmrnmhrm/Chenjesu) or external tech (Slylandro cloak). The Council needs documentation: *does it work? At what cost? What does the cognitive signature drop look like, measured?*
- **Bridge**: the Utwig welcome the Steward. They will not argue the doctrine; they have decided. The Steward's choice is whether to (a) attend and witness, (b) advocate against — possibly persuading some pre-doctrine Utwig to migrate instead, (c) sabotage the ceremony (Cleanser pressure: the cognitive-transition moment emits a small *flare* that could attract the Others — kill them before the flare). The slice's quietest, most thematically resonant moral question
- **Bidirectional reward**: Veils Falling Bio-Archive entry (Artifacts category — includes cognitive-signature telemetry, ceremony video, recovered pre-doctrine recordings); a single *unmasked* pre-doctrine Utwig voice-recording the Steward can preserve and replay (the only one in the galaxy; everyone else gets masked); permanent Persuader and Hider faction standing shift
- **Branches**:
  - **Attend + witness silently** → terminal **Pre-sentient** (the doctrine works; the Utwig survive the Culling as ceremony-locked sub-sentients); Persuader standing up moderately; Hider standing up sharply (the doctrine *validates* the Hider thesis)
  - **Attend + persuade some pre-doctrine Utwig to migrate** → mixed outcome: the doctrine still proceeds for the majority (terminal **Pre-sentient**); a small migrant contingent crosses with the Precursors (terminal **Migrated**); Persuader standing up; the surviving migrants found a SC2-era diaspora *we have not written yet but could*
  - **Sabotage / Cleanser-pressure pre-emptive euthanasia** → Utwig **Eliminated** before the doctrine completes; Cleanser standing up sharply; Persuader and Hider standing down sharply; SC2-era lore hole (no Utwig at all; no Ultron-misunderstanding; no SC3 "devolution" misreading later)

### §7 Win-condition terminal status
- **Slice-canonical**: **Pre-sentient** (the doctrine works; the Utwig survive the Culling) — this is the *intended* outcome and the cleanest example in the slice of a successful below-threshold Homesteader strategy that is *not* biology-based
- Migration-contingent branch: **Migrated** (small migrant group), **Pre-sentient** (doctrine-bound majority)
- Cleanser branch: **Eliminated** (rare; player must actively betray)
- *(This is the slice's only "Pre-sentient by chosen culture" outcome — distinct from Mmrnmhrm/Chenjesu's "Pre-sentient by biology" and the Slylandro's "Cloaked by Furling tech." The Utwig invented their own escape route, and it is harrowing.)*

---

## The Others — antagonist, not a species

> Narrative: [the-furlings-and-the-others.md "The Discovery"](the-furlings-and-the-others.md) §2. NOT a regular species sheet; included here so authors can find the antagonist's structural facts in one place.

### §1 Physical
- **Body archetype**: Trans-dimensional substrate projection. What the player sees in the slice is the *Other-Vessel* (a hijack-only post-slice trophy ship) and *dimensional rifts* (visible distortions in space, like heat-shimmer over hot pavement). The Others' "body" is not in 3D space at all
- **Scale vs Furling**: incomparable — meaningless category
- **Distinctive features**:
  1. Rift visual — non-Euclidean distortion, gives the eye a "wrong" feeling without showing anything explicit
  2. No fixed silhouette; what the player sees is always a *projection*
  3. Color: black, but it's a *negative* black — light that arrived earlier is now slightly missing
  4. Decursion weapon visual — targets *un-arrive* in flickering still-frames
- **Color palette**: NEGATIVE BLACK (a void-tone), absence-of-light frame edges, no warm colors anywhere ever
- **Motion/pose**: They don't move. They *are in places*. The illusion of motion is the substrate projection blinking from one position to another
- **Visual progression**: Static. Specifically: **the Others do not get a variation layer.** Every Other-rift looks identical. Every Other-vessel is the same vessel — sameness is part of the horror

### §2 Speech pattern
- **Translator quirk**:
  - Non-Euclidean prose — sentences whose grammar is partly broken on purpose
  - Third-person descriptions of the world that contradict themselves
  - Present-tense always, no past, no future
  - They notice the player as *meat* — the term is repeated, never elaborated
- **Vocabulary anchors**: *frumple, meat, the shape, it tastes, you are partially here*. They have no Furling-translatable vocabulary for *self*, *cause*, *purpose*
- **Sample lines**:
  > "frumple. you wear *meat* still."
  > "the brightness here was not here three moments ago. it returns. you are partially here."
  > "the shape brightens where you bled. it tastes the same."

### §3 Cultural posture
- **Dominant**: **Indifferent** (they do not care; they consume thought-patterns as food, not as conquest)
- **Secondary**: **Aggressive** in execution, never in motive — they are utterly without malice. They are *hungry*
- **Tertiary**: **Patient** (they have always been coming)

### §4 Humor friction
**ZERO**. The Others are NEVER funny. The protagonist's humor *breaks* at the Others — that break is the horror. See [the-furlings-and-the-others.md §8b](the-furlings-and-the-others.md).

If a Furling cracks a joke at an Other-rift sighting, the joke lands wrong on purpose. It's the player coping, and the world is too cold for the joke to land. Use this deliberately — when an Other-rift first appears in the slice, give the player exactly one humor option, let them take it, and let it land badly. The contrast carries weight.

### §5 Ship — the Others' Vessel (post-slice hijack-only)
Non-Newtonian. Decursion weapon (displaces targets temporally rather than destroying them). NOT in super-melee by default. Stat block deferred until the post-slice Hijack quest is authored. See [ship-roster.md "The Others' Ship"](ship-roster.md).

### §6 Quest — there is no quest. They are the threat.
The Others can never be bargained with, persuaded, or made-quest-with. The player's goal is to *handle every other species before the Others arrive* — see [project_win_condition](project_win_condition.md). The Others themselves are not a negotiation partner.

### §7 Win-condition terminal status — not applicable
They are the win condition's *trigger*, not a recipient of a status. The slice ends when every other species has a terminal status declared and the door closes; the Others arrive and the cluster either is quiet (player wins) or is not (player loses).

---

## Authoring Notes

This document is the **structural source-of-truth** for content authoring. When two facts conflict:
1. Narrative lore docs win over these sheets (lore is canon, sheets are projections)
2. These sheets win over ad-hoc decisions in code
3. Code wins over both *only* when describing what the engine actually does today

Slice-readiness checklist per species:
- [ ] All 7 schema sections filled (this doc ✅ for all 8 entries)
- [ ] Quest sheet authored ([species-quests.md](species-quests.md) ✅)
- [ ] Ship stat block authored (if ship exists) ([ship-roster.md](ship-roster.md) ✅)
- [ ] Dialog FSM authored *(slice-pending: Slylandro, Mycon, Proto-UQ/QA, Androsynth, Mmrnmhrm, Chenjesu — Arilou Sage is done)*
- [ ] SD base portrait generated *(slice-pending: all)*
- [ ] Encounter trigger wired into the cluster narrative *(slice-pending: depends on cluster authoring)*

Two of the six remaining dialog FSMs are the most important: Slylandro (tutorial extension; anchors the Cloak terminal status) and Androsynth (Act 2 milestone, gives the Distress Beacon). Author those next.
