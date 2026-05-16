## Species Sheets — Structural Ledger (slice content authoring reference)

> Per-species schema sheets conforming to [species-design-schema.md](species-design-schema.md). One block per slice species, each filling the seven canonical sections. **This is the implementation-facing source-of-truth for content authoring** — narrative depth lives in the original lore docs (species-precursor-era.md, the-androsynth-refugees.md, etc.), which this document references rather than duplicates.

When implementing dialog FSMs, encounter scenes, ship visuals, quest hooks, or AI prompts, look here first for the structured facts. When the structured facts conflict with a narrative doc, the narrative doc wins (lore is canon, sheets are projections) — but flag the discrepancy as a bug.

The seven slice species:
1. Slylandro Observers
2. Proto-Ur-Quan limpets
3. Proto-Qor-Ah limpets
4. Mycon biots
5. Arilou Lalee'lay
6. Androsynth refugees
7. Mmrnmhrm Sentinels
8. Chenjesu Crystalline Collective

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

## 9. The Others — antagonist, not a species

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
