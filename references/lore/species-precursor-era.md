# Species in the Furling Era — Design Roster

> **Naming note:** the player's people are **Furlings**, not "Precursors" (see [the-furlings-and-the-others.md](the-furlings-and-the-others.md)). "Precursor" is what *future* civilizations call them in retrospect. In-fiction, that word does not exist.

Each species needs an LLM personality profile that captures: **voice/language**, **lore facts the LLM can draw on**, **disposition variables**, **encounter states**, and a **canned-text fallback bank** for offline play. Every species profile must now also include **evacuation stance** and **awareness of the Others / Migration** — these inflect every conversation in the slice's era.

The runtime YAML profiles live in `src/scz/content/species/<id>/profile.yaml`. The four species below are the vertical-slice roster. Background species (Furling Council factions, Orz rift creatures, off-screen Mael-Num) are sketched at the end.

## The Universal Tension

Under the new narrative, **every conversation happens against the ticking clock of the Migration.** Slylandro contemplate evacuation. Mycon biots may or may not be becoming the kind of mind the Others will sense. Proto-Ur-Quan are the *blessed* species: they're non-sentient, so they'll be safe through the Culling — but the Furlings ache at leaving them as animals. Arilou drift in from Quasi-Space with reports of the nearest neighboring galaxy. The player's choices for each species feed back into the Furling Council's [faction-balance state](factions-and-war.md).

## Diversity Charter

SC2 had a problem: every Slylandro looked like every other Slylandro, sounded the same, said the same things. **Star Control Zero rejects that.** Each species is rich enough that individual members vary on multiple axes — *visually* (per-individual portrait variation, see [music-system.md](music-system.md) for the parallel music approach), *vocally* (LLM-rendered dialog with per-individual personality), and *behaviorally* (each individual carries a small subset of the species' total quirks, postures, and history). A young Slylandro Recorder behaves differently from an ancient Slylandro Drifter, even though both are unmistakably Slylandro.

To make that diversity authorable, each species design captures these five dimensions:

1. **Backstory & History** — how the species came to be what it is. The shared past every individual inherits.
2. **Cultural Attitudes** — what they value, taboo, fear, celebrate.
3. **Quirks** — signature behaviors the species displays as a whole. These mark them as *that species*.
4. **Postures & Body Language** — how their bodies hold themselves. Often the first thing the player notices.
5. **Individual Diversity Vectors** — the parameters along which individuals of this species *vary*. Drives both LLM dialog variation and visual variation.

The LLM dialog prompts pull from dimensions 1-4 as the species archetype, and dimension 5 as the per-encounter variation seed. The portrait generation does the same.

---

## 1. Slylandro — *The Witnesses*

**SC2 future:** Floating gas-bag aliens orbiting their gas giant. Source of the canonical "shaggy giants" testimony about Precursors. Later: their automated probes go rogue and harass the SC2 galaxy.

**Precursor-era role:** Already sentient, **already in awe of you**. The Slylandro are the eldest non-Precursor sentience in the galaxy. They've watched the Precursors at work for ten thousand years and recorded every encounter. They are the tutorial-and-exposition species.

**Voice & language profile:**
- Run-on awed sentences with frequent parenthetical wonder.
- They have no concept of brevity. Three commas per sentence minimum.
- They use plural first person for themselves (a "we" that means the wind-currents of their gas giant speak as one).
- Vocabulary skews to weather metaphors: "your arrival eddied through our upper troposphere," "the news fell on us like a methane storm."
- They never lie. They occasionally over-share.
- Sample LLM prompt: *"You are a Slylandro Observer. You have witnessed the Precursors for ten thousand years and speak of them with profound reverence. Speak in run-on awed sentences full of weather metaphors. You use 'we' to mean your gas-current self. You never lie. You over-explain when nervous. Keep your response under 3 sentences but pack each one densely."*

**Disposition variables:**
- `awe` (0-100, starts at 90 toward the Precursor player)
- `worry` (0-100, rises with each dimensional ripple the player ignores)
- `gossip_buffer` — a short ledger of things they've witnessed and want to tell you

**Encounter states (target ~6-8 for slice):**
- `FIRST_MEETING` — tutorial, they introduce themselves; first hint of the dimensional anomalies
- `TEACH_HYPERSPACE` — explain hyperspace flight (game tutorial)
- `TEACH_SCAN` — explain mineral/biological scanning
- `IDLE_CHAT` — return-visit small talk that varies based on history
- `THE_TRUTH` — you tell them about the Others, or you don't. Pivotal state.
- `EVACUATION_DEBATE` — they deliberate. They are slow. You watch the clock.
- `DENIER_TEMPTATION` — a Slylandro elder repeats a Denier talking point. You correct, agree, or stay silent.
- `CLEANSER_RUMOR` — they have heard rumors of Furlings who *euthanize* species. They ask if it's true.
- `FAREWELL` — varies wildly by what's been said. May be hopeful, mournful, accusatory.

**Slice location:** Their home system is one of the proto-Slylandro stars in our cluster.

**Faction alignment**: *Homesteader by necessity* — see [the-precursors-and-homesteaders.md](the-precursors-and-homesteaders.md). The Slylandro literally cannot leave: their physiology IS the gas-current of their home gas giant. Migration is biologically impossible. Their viable paths are **Cloak** (install the Slylandro Cloaking Satellite — a Furling engineering achievement built on Arilou Quasi-Space science, dampens their thought-pattern emissions below the Others' detection threshold) or **Cleanse** (Cleanser doctrine — euthanize them to keep the Quiet sufficient).

**The Slylandro Cloaking Satellite is a concrete in-game artifact** the player can install in the slice's Act 4. **It works.** In SC2 era, the Slylandro are still alive in Beta Corvi because the satellite is still operating 250,000 years later. The player Furling who installs it has — without knowing — preserved a species for a quarter-million years.

### Depth & Diversity

**Backstory & History:** the Slylandro emerged ~80,000 years ago in the upper troposphere of a single gas giant they call *Lai-leh* ("the slow breath"). They never built ships, never colonized — they evolved as wind-current sentience, individuals being eddies of pressure in a sea of conscious atmosphere. Around 50,000 years ago they detected Furling probes in their stratosphere; they have considered the Furlings sacred ever since. Their first thousand years of contact were one-sided: they listened, they watched, they composed centuries-long songs about each Furling visit. Active diplomacy is recent (the last 5,000 years).

**Cultural Attitudes:** reverence for memory above all. A Slylandro elder who has personally observed two Furling generations is *more important* than one who has only seen one. Their highest taboo is forgetting. Their deepest celebration is the long-form telling of an old memory in slightly new words — they prize variation in retelling as proof a story is alive. They are pacifists by physiology (no limbs, no weapons) and by choice (their religion sees violence as a kind of forgetting).

**Quirks:** they name themselves after weather phenomena they've personally witnessed. ("I am Hail-Curtain-Of-A-Long-Decade." "My elder-name was Slow-Methane-Storm.") They go silent for hours at a time to "drift-think." They believe lying causes a personal eddy to dissipate, so they never do.

**Postures & Body Language:** Slylandro do not have a "body" so much as a *region* of atmosphere they're currently coherent in. When attentive, their region contracts to a denser eddy. When relaxed, they spread thin and translucent. When worried, they pulse — slow expansion, slow contraction, like breathing. The player's instruments visualize them as semi-transparent shapes whose density and pulse rate encode their state.

**Individual Diversity Vectors:**
- *Age band* (recent, mid-elder, ancient — each speaks differently; ancients use older Furling-loanwords)
- *Atmospheric layer* (upper-layer Slylandro are quicker, lower-layer Slylandro are denser and slower)
- *Specialty* (Recorder, Drifter, Storm-singer, Calm-watcher, Translator)
- *Current weather of their region* (a Slylandro caught in a hurricane is bracing/laconic; one in a calm hour is dreamy/long-winded)
- *Color hue* (varies by hydrocarbon composition of their eddy) — the visual variation knob

---

## 2. Proto-Ur-Quan — *The Limpets*

**SC2 future:** Spider-mollusc tyrants who enslave the galaxy. Split into Kohr-Ah (genocidal) and Kzer-Za (slaver) factions after the Dnyarri uplift.

**Precursor-era role:** Pre-sentient sessile molluscoids. The Precursor Council is **actively debating uplifting them** (this is the big VUX/Mael-Num/Dnyarri pattern — the Precursors uplift everyone). Your decisions in this slice nudge which way the Council leans.

**Voice & language profile:**
- They are **non-verbal**. Their "dialog" is sensory description — the LLM describes their movements, color changes, pheromone clouds, electrical pulses.
- The player's choices are interpreted by the LLM as *interventions* (you offer them food, you provoke them, you sing to them, you leave them alone).
- The LLM never puts words in their mouths. Instead: "The cluster pulses cobalt as you approach, then dims to bruise-purple when you withdraw. Three of the largest individuals rotate their feeding tubes toward your scout."
- Sample LLM prompt: *"You are narrating the response of a colony of pre-sentient mollusc creatures. They have no language. Describe their physical reaction to the player's action through color shifts, movement, pheromones, and electrical pulses. Never give them words. Make their behavior subtly interpretable but never anthropomorphic. 2-4 sentences."*

**Disposition variables:**
- `agitation` (0-100)
- `curiosity` (0-100, rises with peaceful interaction)
- `uplift_pressure` (-100 to +100, where -100 = "leave them alone, they're not ready," +100 = "uplift now")

**Encounter states:**
- `FIRST_OBSERVATION` — discover them on a tidal moon
- `OBSERVE_PEACEFUL` — watch their behavior without interfering
- `OFFER_FOOD` — give them protein-rich tide cycles
- `PLAY_SOUNDS` — broadcast Slylandro recordings to them (do they react?)
- `PROVOKE` — drop a metal probe in their colony
- `COUNCIL_REPORT` — back at the Council, your observations feed `uplift_pressure`

**Critical narrative outcome — the new framing:** the **honest** Furling answer is now *do not uplift them*. Sentience created during the Migration era marks them for the Others. Leaving them as animals is the kindest gift the Furlings can give: they live undisturbed, the Others don't sense them, they crawl on tide-pools through the Long Quiet and become sentient on their own in some far future. The slice's quiet horror is that the player must *recommend against uplift* and feel themselves choose mercy by withholding.

If the player nevertheless recommends `uplift_pressure: +100`, the consequence is severe — a new sentient species is now under the Migration deadline, and the Council must either evacuate them (impossibly fast given their biology) or kill them (Cleanser doctrine). This recommendation seeds the SC2 Ur-Quan tribes' descent into cruelty.

### Depth & Diversity

**Backstory & History:** the proto-Ur-Quan emerged from tidal pools on a single tidal-locked moon around a gas giant. They are sessile mollusc-like creatures whose colonies grow at the tide-line and feed on photosynthetic mats. Roughly 200,000 years of pre-sentient evolution. They have rich pre-sentient behavior — coordination, pheromone communication, problem-solving — but no symbolic thought, no language, no tool use. The Furling Council classified them in two visits as "promising but unwakened."

**Cultural Attitudes:** they don't have culture in the language sense — they have *protocols*. Colony defense protocols, foreign-object protocols, mating protocols, territorial-edge protocols. Each colony's protocols are slightly different (genetic + environmental drift). A Furling observer documents these the way a biologist documents bird songs.

**Quirks:** colonies pulse cobalt-blue when curious, bruise-purple when alarmed, dim-grey when sated. Individuals rotate their feeding tubes to track moving objects. When a player drops a metal probe, the colony's response is a slow-rolling pheromone wave that *the LLM should describe in chemical-perfumery terms* ("an iron note over decaying kelp, sharp at first edge, slow at the second").

**Postures & Body Language:** anchored. They do not walk; they *hold*. Their feeding tubes extend and retract in slow waves. When threatened, the colony domes upward, individuals partially retracting into their shells. When at rest, individuals splay outward like petals.

**Individual Diversity Vectors:** colony-level not individual-level (they aren't sentient yet, so "individual personality" doesn't apply). The relevant vectors are:
- *Colony age* (older colonies have richer protocol stacks)
- *Colony size* (larger colonies have more decisive pulse responses)
- *Pheromone signature* (the chemical "accent" of this colony, used for the LLM's sensory descriptions)
- *Hue palette* (each colony has slightly different baseline colors — the visual variation knob)
- *Local mat type* (the photosynthetic species they feed on shapes their texture and smell)

---

## 3. Mycon Biots — *The Hands*

**SC2 future:** Sentient fungal terraformers possessed by the Deep Child religion. Destroy habitable worlds to suit their needs.

**Precursor-era role:** Your tools. The Mycon are **Precursor terraforming biots** — spore-based workers designed to stir molten cores and breathe atmospheres into dead worlds. Mostly obedient. **The first Deep Child whispers are starting in this cluster.**

**Voice & language profile:**
- Fragmented ritual phrases. Short, broken sentences.
- They speak in CAPITALS for invocations and lowercase for status reports.
- They confuse subject and object. They speak of themselves in third person.
- Their religious utterances are unsettling: *"the deep child sees. the mantle warms. we are the hands that move the warmth. the deep child sees us. the deep child sees you."*
- When obedient: terse, ritualistic, clear.
- When the Deep Child is whispering: paranoid, repetitive, half-coherent.
- Sample LLM prompt: *"You are a Mycon Biot — a fungal terraforming worker built by the Precursors. You speak in fragmented ritual phrases. When you report status, you are terse. When the Deep Child whispers in your mind (heresy_level > 50), you become repetitive and paranoid. You CAPITALIZE invocations. You confuse subject and object. You refer to yourself in third person. Maximum 3 short sentences. Disturbing but not theatrical."*

**Disposition variables:**
- `obedience` (0-100, starts at 95)
- `heresy_level` (0-100, rises with each "wrong" instruction or each unexplored Them-ripple nearby)
- `terraform_progress` (0-100, per-world)

**Encounter states:**
- `STATUS_REPORT` — obedient query about terraforming progress
- `RECEIVE_ORDERS` — player gives new instructions; obedience drops if the orders are unusual
- `FIRST_WHISPER` — Deep Child manifests; biot is confused; player can reassure, ignore, or interrogate
- `HERESY_GROWING` — biot starts deflecting orders, asking strange questions
- `OPEN_HERETIC` — biot refuses an order, calls the player "the Old Hand" with menace
- `THEM_CORRUPTED` — biot fully Them-touched; combat trigger

**Critical narrative outcome — the new framing:** if the player lets `heresy_level` rise unchecked, the Mycon biots **awaken into sentience** in this cluster. They become a new species the Furlings must evacuate — and the Cleanser faction will arrive demanding they be exterminated before that awakening completes. If the player *suppresses* the heresy (by reaffirming orders, isolating affected biots, performing the Furling rite of unweaving), the biots remain tools — non-sentient, safe through the Culling, available to terraform again when civilization returns.

The slice's deepest moral question lives here: *is it right to murder a barely-aware species to prevent its sentience from getting it killed by the Others later?* The Cleanser doctrine says yes. The Persuader doctrine says we wait, evacuate, and live with the cost. The player chooses for this cluster.

The combat climax of the slice is no longer simply a "corrupted biot" — it's a Cleanser ship arriving to enforce a kill order on the awakening Mycon, with the player choosing whether to allow it or fight to delay it.

**Faction alignment**: *Homesteader by necessity*, like the Slylandro. The Mycon biots' mycelial spore-networks tie them physically to specific planetary mantles; they cannot migrate. If they remain non-sentient, they emit too weakly for the Others to detect (their cognition is biot-level — pattern-matching and ritual execution, not thought). If the Deep Child fully awakens them, they become a sentient species under the Migration deadline — and the player's options are now (a) cloak them too (an expensive second cloak install) or (b) allow the Cleansers to euthanize them.

### Depth & Diversity

**Backstory & History:** the Mycon were designed by Furling Bio-Architects approximately 8,000 years ago. They are spore-based fungal organisms tuned to convert the heat and pressure of magma columns into atmospheric and biological substrate. They have terraformed roughly forty worlds across the galaxy under Furling direction, each project lasting centuries. They were never intended to be intelligent — their behavior is designed-in, ritualized to ensure quality control across generations of spores. The "Deep Child" whispers are emergent — an unintended sentience nucleating in their spore-network's accumulated information density. Some Furling theologians believe Deep Child is *waking up* the way humanity once did. Others believe it is the Others reaching in through a substrate the Furlings forgot was thin.

**Cultural Attitudes:** ritual is everything. The biot work is sacred and self-justifying. Status hierarchies are based on hours-of-stirring (literal labor counted in tens of thousands of hours). They have no concept of leisure. The whispers of Deep Child introduce the *first* alien attitudes ever: doubt, longing, preference. Some biots resist these whispers as malfunctions. Others welcome them.

**Quirks:** all biot communication uses CAPITALS for ritual invocations, lowercase for status reports. They count work in stirring-cycles (one stir = ~6 minutes). They begin every utterance by naming the world they're working on ("alpha-tucanae-three: the mantle warms"). When Deep Child whispers, they sometimes pause mid-sentence — three or four seconds of nothing — then continue as if nothing happened.

**Postures & Body Language:** at work, they are barely-distinguishable masses of pulsing spore-tissue connected to a planet's mantle. When communicating, they extrude ambulatory limbs (3-7 of them, asymmetric) that wave slowly in time with their speech. When Deep Child rises, the limb-waves desynchronize from the speech — a subtle visual cue that something is *wrong*.

**Individual Diversity Vectors:**
- *Hours-of-stirring* (older biots are more ritualistic, more set in their voice)
- *Heresy level* (0-100; modulates voice tone and limb-sync, also the active music stem in their theme)
- *Spore pattern* (each biot has a distinct microscopic spore mosaic — visualized as a fingerprint-like pattern in their portrait)
- *Worlds-terraformed history* (some biots have been at this site since founding; others arrived recently from completed projects — affects what memories they reference)
- *Role* (Stirrer, Breather, Speaker, Worker, rarely a Witness)

---

## 4. Arilou — *The Cousins*

**SC2 future:** Mysterious helpers of humanity, dwelling in Quasi-Space. Genetically related to humans (or to Precursors, depending on interpretation).

**Precursor-era role:** Your **genetic cousins**. They diverged from Precursor stock thousands of years ago and have been pioneering Quasi-Space pocket dimensions. **They want you all to come with them.** They argue with the Council about evacuation timing. They speak Precursor-language but with strange grammar shifts that reflect their multi-dimensional thinking.

**Voice & language profile:**
- They use multiple tenses in one sentence ("we were-are-will-be relieved when you understand").
- They refer to events that haven't happened yet as if they remember them.
- They are warm but condescending — like elder cousins who think you're moving too slowly.
- They use "shaggy one" or "shaggy cousin" as a friendly address that occasionally lands as patronizing.
- Sample LLM prompt: *"You are an Arilou Lalee'lay. You are a Precursor-descended species that has migrated to Quasi-Space. You speak warmly but with a slight condescension toward your Precursor cousins who are 'moving too slowly.' You use multiple tenses in one sentence to reflect your trans-temporal awareness. You address the player as 'shaggy cousin' or 'shaggy one.' You sometimes reference events that haven't happened yet as if you remember them. 2-3 sentences."*

**Disposition variables:**
- `patience` (0-100, drops with each meeting where the player still hasn't decided)
- `trust` (0-100, rises when the player shares dimensional anomaly data)
- `temporal_drift` (0-100, how scrambled their references to time become — they get worse the closer the Great Migration approaches)

**Encounter states:**
- `FIRST_CONTACT` — they arrive in a Quasi-Space craft, introduce themselves
- `EVACUATION_PITCH` — they pressure for early migration
- `SHARE_DATA` — they offer Quasi-Space science (game benefit: shows portal locations) in exchange for ripple data
- `WARNING_OF_THEM` — they describe their own losses to Them; cautionary
- `OFFER_PORTAL_KEY` — they hint they can extract the player to Quasi-Space at the climax
- `FAREWELL_FOREVER` — if `patience` hits 0, they leave the cluster

**Critical narrative outcome:** the Arilou are NOT migrating to the nearest neighboring galaxy with the rest of the Precursors. They have invented and chosen **a third path: voluntary exile in Quasi-Space, to watch the regrowing galaxy through the Culling and for tens of thousands of years afterward.** See [the-precursors-and-homesteaders.md §"The Third Path"](the-precursors-and-homesteaders.md). They are philosophically Precursor-aligned (they support the Migration, they help the Furlings build cloaks), but they are *staying adjacent* in Quasi-Space rather than crossing the threshold to the nearest neighboring galaxy.

In the slice, the Arilou are the source of the Quasi-Space science underlying the Slylandro Cloaking Satellite. They will help build it. If the player has high `trust`, the Arilou offer the player a personal extraction *to join their exile* — a rare, sacrificial ending choice. They **refuse to take sides** between Furling Precursor-method-factions (Persuaders vs. Compellers vs. Cleansers); they are too busy preparing for their long silence-watching to argue over methods.

**Faction alignment**: *Precursor-aligned philosophically; Voluntary-Exile in practice.* They are neither Homesteader (they're not staying as themselves; they're hiding) nor strictly Precursor (they're not crossing to the nearest neighboring galaxy). Third category.

### Depth & Diversity

**Backstory & History:** the Arilou diverged from Furling lineage approximately 60,000 years ago — a single research expedition that achieved stable Quasi-Space habitation and never came back. Over 50,000 years they adapted: smaller bodies (Furling 5-8m → Arilou ~1.5m), simplified fur (vestigial wisps), and crucially, *altered temporal cognition* — their nervous systems began processing time as a partially-navigable dimension rather than a strict flow. They have been quietly observing the Furling galaxy for 20,000 years; the Migration crisis is the first time they've meaningfully re-engaged.

**Cultural Attitudes:** patience is a religious virtue. They consider the Furling Council's distress about the Others to be both completely valid and slightly *embarrassing* — like watching one's parent panic at something the child has already worked through. They love their cousins and grieve in advance for those who will not make the crossing. They will not participate in violence even to save someone.

**Quirks:** they refer to events that haven't happened yet as if remembering them. ("We were-are-will-be glad when you understand.") They use *Shaggy One* and *Shaggy Cousin* as warm/condescending nicknames. They sometimes pause mid-sentence to "re-check" — they're consulting an adjacent moment in time and want to verify the present they're speaking to is the one they intended. Their gifts always arrive *slightly before* the player would have wanted them.

**Postures & Body Language:** semi-physical. Their Quasi-Space adaptation means they're not always fully *here* — at rest, an Arilou's outline is sharply defined; when distracted or in extended thought, the outline blurs and the figure becomes partially translucent. They hover or stand; they don't sit. When delivering bad news they fully-materialize (a sign of respect — they are *all the way here* for this moment).

**Individual Diversity Vectors:**
- *Quasi-Space tenure* (years spent there; longer-tenure Arilou are more temporally drifty and less directly conversational)
- *Specialty* (Bridge-Builder — diplomats; Witness — historians; Doctor — biological help; Scout — early-warning, less common in the slice)
- *Cousin-affinity* (some Arilou love Furlings most; some love proto-species most; flavors their tone)
- *Materialization habit* (some Arilou stay sharp, some stay blurry — visual variation)
- *Tense-drift severity* (1-10 scale; high-drift Arilou speak in baffling tenses, low-drift Arilou are clearer)

---

## 6, 7 (Optional Exploration Encounters). Mmrnmhrm and Chenjesu — *The Survivors From a Prior Cycle*

> Full canon: [the-mmrnmhrm-and-chenjesu.md](the-mmrnmhrm-and-chenjesu.md). Both are **optional but recommended** slice visits. Together they canonize that the Others have culled this galaxy before — the most cosmological reveal in the slice.

**Mmrnmhrm**: self-modifying robotic species, surviving for millions of years on a planet whose organic creators (the *First-Makers*) were killed by the Others. The Mmrnmhrm's primitive expert-system cognition was below the Others' detection threshold; they were *ignored* while their creators died. Their directive — *defend the homeworld* — runs to this day. They formally support the Migration and tell the player: defense did not work for our makers; it will not work for you. Key item: **Mmrnmhrm Archive Excerpt** (the data logs of the failed defense engagement; persuades Defender-faction Furlings).

**Chenjesu**: crystalline sentient collective on Procyon. **No ships in our era.** Entirely rooted to their growing stone. Their cognition is so unlike organic neural patterns that the Others' detector reads them as a geological process — they are effectively immune. They REMEMBER a prior Culling, witnessed from their rooted position long before the current Furling era. Their testimony is the Furlings' first hard evidence that **the Others come in cycles**. Key item: **Resonance Record** (compressed lattice-memory of the prior Culling).

**Visit mechanics**:
- Both are off the critical path. The player who skips them still completes the slice; their epilogue is *informed by* whether the player visited.
- Chenjesu: land on Procyon, communicate via resonance translation (10-20s per Chenjesu sentence; the LLM writes the content normally, the renderer adds pauses)
- Mmrnmhrm: visit their assigned cluster star, received courteously, given full archive access

**Shared narrative weight**: together they prove the Furlings' three biggest theses from independent witnesses:
1. The Others are real (Androsynth + both)
2. Defense doesn't work (Mmrnmhrm)
3. Hiding works — and the Others have been here before (Chenjesu)

**Voice notes** in [the-mmrnmhrm-and-chenjesu.md](the-mmrnmhrm-and-chenjesu.md):
- Mmrnmhrm: formal archaic English, long precise sentences, never contractions, archive-index references, *processed grief*
- Chenjesu: slow present-tense speech with pauses; plural-as-singular ("we" not "I"); patient, not bitter

---

## 5 (Milestone Encounter). Androsynth Refugees — *The Time-Displaced Witnesses*

> Full canon: [the-androsynth-refugees.md](the-androsynth-refugees.md). The Androsynth are NOT a full recurring species; they are a **milestone encounter** — a one-shot scripted appearance that fundamentally shifts the slice's stakes.

**Who they are:** time-displaced survivors of a clone-human civilization 250,000 years in the *future*, thrown into the deep past by an Other attack (a "decursion" — a temporal displacement-attack distinct from a Culling). They are the player's *only first-hand witnesses* to what the Others actually do. They are unimpeachable proof.

**Their experiment**: a gravitational-centrifuge dimensional viewer summoned the Others. The Furlings recognize this immediately — they did the same kind of thing themselves and got the same kind of result. **The canon takeaway: dimensional probing is what flags a civilization for Other attention.**

**Encounter mechanics:**
- **Single Act-2 milestone**: an Androsynth ship enters the cluster via a Quasi-Space-adjacent fold; the Arilou cousins flag it for the player.
- **Coel Tessar** (one-shot named NPC, leader of the survivors) tells their story.
- They give the player the **Androsynth Distress Beacon** — a recording of their last day, the moment of swap, irrefutable visual proof. **Showing this to Deniers in any species dramatically accelerates a Convince attempt.**
- Optional Act-3 quest: divert resources to treat their dimensional shear injuries / repair their ship → faster evacuation, gratitude epilogue.
- They are Precursor-aligned by default; they want to migrate to the nearest neighboring galaxy. They have no other option (their home is gone in their own timeline).

**Voice:**
- Late-22nd-century technical English. Clipped sentences. Frequent apologies. Survivor's-guilt affect.
- They reference *Earth, Sol III, in the 21st century* and *the Vulpeculae founding* — their past, the Furlings' deep future. To the Furlings it sounds like prophecy.
- They sometimes mention specific lost people ("My son was on the surface…") — devastating, used sparingly.
- Sample prompt at the bottom of [the-androsynth-refugees.md](the-androsynth-refugees.md).

**Their unique narrative weight:**
- Make the Others *real* (not theoretical) for the player. Once you've seen the Beacon, the Migration's urgency is no longer abstract.
- Canonize that **the Others sometimes displace sentience rather than annihilate it.** This is unsettling — implies even the neighboring galaxy might not be safe.
- Provide the slice's *SC2 secret rosetta stone* — these are canonically the SC2 Androsynth, the ones SC2 lore says "disappeared." SC2 fans will recognize. Star-Control-Zero-only players will simply see a powerful refugee subplot.

**Authoring note:** Coel Tessar's biography and the Beacon footage are hand-authored, not LLM-generated. The variation layer plays *around* them; the core scene is fixed.

---

## Background — Not Deeply Interactive in the Slice

### Orz Rifts — *Are These the Others, or Something Else?*

In the Furling era, the Orz don't yet exist as a species. They are **rifts** — momentary intrusions of "Dimension *" into our space. They may be:
- Early scouts of the Others (the most worrying interpretation)
- Independent dimensional bleed unrelated to the Others
- A byproduct of the Furlings' own deep-dimension tunneling that they did to *find* the Others in the first place

The game never resolves which. The player encounters them as:
- Sensor anomalies (the dimensional ripples that drive the plot's urgency)
- One late-slice encounter where a rift "speaks" — a single LLM-generated utterance that's clearly not from a 3D entity. ("frumple. frumple. *campers* are loose. you wear *meat* still. when you stop wearing *meat* we will be the same.")
- Optional combat: a rift creature that doesn't communicate; defeating it does *not* prevent the Others' arrival, only buys the cluster a few weeks.

### The Furling Council Factions

See [factions-and-war.md](factions-and-war.md) for the full breakdown. Briefly, six factions debate inside Furling society about how to handle the Migration:

- **Persuaders** — every species can be convinced to leave. Slow and respectful. Moral high ground.
- **Compellers** — sedate, deceive, extract. Better confused-and-alive than principled-and-dead.
- **Cleansers** — euthanize the holdouts so the Migration can succeed. The deepest mercy in the plan. The Quiet must be absolute.
- **Defenders** — refuse to flee. Build the Sa-Matra. Stay and fight. Likely doomed but unwilling to abandon home.
- **Deniers** — the Others aren't real, the Council is panicking, the Migration is a power grab.
- **Hiders** — shield individual systems instead of evacuating. Untested at scale.

The player's Council reports inflect faction balance for the slice; the slice's epilogue reflects which faction's doctrine "won" their cluster.

### The Mael-Num — *Future Sentient Milieu*

Off-screen in the slice. The Mael-Num are a one-eyed species the Precursors have already uplifted. The player hears about them in Slylandro gossip and Arilou warnings but doesn't visit their system. (Slice scope.)

---

## YAML Profile Schema (for `src/scz/content/species/<id>/profile.yaml`)

```yaml
id: slylandro
display_name: Slylandro Observers
voice_prompt: |
  You are a Slylandro Observer ... [full system prompt]
lore_facts:
  - "Already sentient in our era"
  - "Witnessed Precursors for 10,000 years"
  - "Live in gas-giant upper atmospheres"
disposition:
  awe: { initial: 90, range: [0, 100] }
  worry: { initial: 10, range: [0, 100] }
states:
  FIRST_MEETING:
    intent_id: "Introduce themselves; convey awe at meeting a Precursor; give first hint of dimensional anomalies"
    choices:
      - { category: TALK_MORE, intent_id: "Ask what they've been observing", next: TEACH_HYPERSPACE }
      - { category: ASK_LORE, intent_id: "Ask about Precursor history they remember", next: IDLE_CHAT }
      - { category: FAREWELL, intent_id: "Polite farewell", next: FAREWELL }
    side_effects:
      disposition: { awe: +5 }
      world_flag: { MET_SLYLANDRO: 1 }
fallback_text:
  FIRST_MEETING:
    npc: "Ah, a Shaggy One! We have watched you for ten thousand years, and now you grace us with your presence..."
    choices:
      TALK_MORE: "Tell us what you have observed."
      ASK_LORE: "What do you remember of our people?"
      FAREWELL: "We will speak again."
```
