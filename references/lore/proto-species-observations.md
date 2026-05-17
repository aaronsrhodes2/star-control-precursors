# Proto-Species Observations — Fanservice Visits to Pre-Sentient SC2 Races

> Optional exploration content: the player can visit star systems containing the **pre-sentient ancestors of SC2 species** and observe them in the wild. They are all **below the Others' detection threshold**, present no Furling decision-burden, and will evolve over the 250,000 years between our era and SC2 into the races players will later know. These are pure fanservice for SC2 fans, modest bio-data rewards for everyone, and a thematic counterweight to the Ur-Quan uplift dilemma — **most species are better off left alone**.

## The Conceit

The Furling Council's bio-archive maintains observation entries on every pre-sentient species in the galaxy with detectable cognitive trajectory. As a Steward, you contribute observations from your cluster. Many of these species are recognizable to SC2 fans as the *ancestors* of the SC2 races — proto-Spathi crouching nervously in burrows, proto-Yehat fledgling raptors learning to fly in their stratospheric eyries, proto-humans walking upright for the first time in East African savannas.

**You do nothing.** You observe. You log. You leave. The species evolves naturally over 250,000 years and becomes itself. This is the *opposite* path from the Ur-Quan uplift project — instead of accelerating a species into sapience under the Migration deadline, you simply let evolution do its work on the long timeline.

The Furling Council formally records each Steward's observation entries. They are **irreversible** (Time Drive cannot undo them — the species exists and your archive entry stands, even if you rewind). Each observation grants a small bio-data reward (resource economy benefit) and a permanent flag indicating you visited.

## The Observation Encounter (Scene Type)

This is a *new* scene type, lighter than the FSM-dialog encounters. Lifecycle:

1. Player lands the lander on the relevant planet
2. Scan completes (visual: pre-sentient lifeforms identified)
3. **Observation log** generated: an LLM-rendered Furling Archivist entry describing the species in this moment — their behaviors, their environment, their cognitive trajectory. 3-5 sentences, voice: warm, scholarly, fondly amused. Like Attenborough narrating an early-hominid documentary.
4. Optional player action: **add a personal annotation** to the log entry. Free-form input or pre-set choice. This shows up in the Furling Council archive.
5. Bio-data + irreversible archive flag awarded
6. Player returns to ship; the encounter is over

There is no FSM. There are no choices. The variation principle still applies (each observation generates slightly different text; the archive flag is deterministic).

### Sample Observation Logs (LLM target examples)

These are *target outputs* — examples of what the LLM should produce for an observation encounter. Use them as reference when authoring the LLM prompt. Each sample is one of several valid renderings; on a re-visit, the LLM would produce a different log with the same essential content.

**Proto-Spathi observation log (sample):**

> *Bio-Archive Entry 14,308. Steward [name] reports landfall on the second planet of [system]. Subject species: the* burrowing-slugs-of-coordinated-evasion *(no self-designation; vocal communication has not been observed).*
>
> *They are practicing the art of cowering in fear. There is a colony of perhaps four thousand individuals occupying a network of vertical burrows in the silt of a freshwater shoreline. When a passing predator-bird crossed the colony's airspace this morning, the entire population vanished into the burrows within 1.4 seconds — a coordinated wave the Steward's instruments registered as a single behavior, not four thousand separate ones.*
>
> *They are deemed below intelligent sentience. Their fear-art, however, is sophisticated beyond expectations: synchronized keening-songs structure the evasion response, and terror-postures (a particular folded curl, observable from orbit) are passed between generations. The trajectory is uncertain. Whatever they become, it is unlikely to be brave. Council recommendation: leave undisturbed.*

**Proto-VUX observation log (sample):**

> *Bio-Archive Entry 14,309. Subject species: the* tide-pool molluscs-of-the-thirty-color-disciminations *(no self-designation).*
>
> *They are sorting themselves by color. The colony in this tide-pool — perhaps two hundred individuals — has organized into bands of identical hue along the rock-shelf, the most discriminating Steward observations confirming that mating selection is governed by precise pattern-matching of body coloration. Individuals whose patterns deviate from their band's consensus are not killed, but they are not bred. Over generations, the bands have become more uniform within themselves and more distant from each other.*
>
> *Their visual cognition is extraordinary; their tolerance for visual difference is nearly zero. The Furling biologists watching this species find it disquieting. Council recommendation: leave undisturbed, monitor the trajectory.*

**Proto-Humans (Sol III) observation log (sample):**

> *Bio-Archive Entry 14,310. Subject species: the* tool-using bipedal mammals of the third planet *(self-designation unobserved; their vocalizations have not yet stabilized into language).*
>
> *They have buried a body. A small group of perhaps eleven individuals carried one of their dead — an elderly female by the Steward's biological inference — to a slow hillside above their cave, and placed her in a shallow scrape with several stones that had been carefully selected for shape. They sat with the scrape for nearly an hour. Then they returned to their cave.*
>
> *They use fire. They use stone tools. They bury their dead. They are deemed below intelligent sentience by the Council, but the buried-grandmother is the kind of observation that makes the Council's classification feel provisional. Trajectory: very promising. The Steward who logs this entry is reminded to walk back to the lander quietly.*

These three samples establish the tone: **warm, scholarly, fondly amused, occasionally moved.** The Furling Archivist voice is *Attenborough narrating an early-hominid documentary* — never condescending, never sentimental, but specifically attentive to the small moments that prefigure what each species will become.

## Per-Species Briefs (Slice + Full Game)

Each entry is the species' SC2 identity → what they look like in our era. Slice-scope candidates marked with ✱.

### ✱ Proto-Humans (Sol, 1793×1450)
*SC2 race*: Earth-born humanity, fragmenting into Star Control captains.
*In our era*: small-brained early hominids on a single continent of Earth. Use stone tools. Fire is a recent acquisition. They bury their dead. Their cognitive trajectory is *promising* — the Furling archive notes "tool-use coupled with social grief; suggestive."

### ✱ Proto-Spathi (in the slice's cluster, location TBD)
*SC2 race*: Cowardly molluscoids of Spathiwa.
*In our era*: burrow-dwelling sluglike creatures **practicing the art of cowering in fear** to survive the local predators. No ships, no tools, no language. They have evolved an extraordinarily good early-warning sense; their coordinated flee-responses ripple across an entire colony in seconds. They are deemed **below intelligent sentience** in the formal Council classification, but their *fear-art* is already startlingly sophisticated — they have terror-rituals, terror-postures, terror-songs (high keening that synchronizes the colony's escape vector). **The cowardice is already here, 250,000 years early.** Council note: *social fear-response sophisticated beyond expectations; trajectory uncertain but unlikely to be brave.*

### Proto-Yehat (Serpentis cluster, somewhere)
*SC2 race*: Warrior bird-saurians; clan-bonded; honor-codes.
*In our era*: large stratospheric raptors. They glide for weeks without landing. They have evolved aerial combat behaviors against rival flocks. They have not yet developed language; their displays of dominance are wing-clack patterns. **The warrior-honor is in the wing-clacks already.**

### Proto-Pkunk (near proto-Yehat, ancestrally related)
*SC2 race*: Psychic-pacifist bird-people; spiritual; opposites of the Yehat.
*In our era*: smaller, ground-foraging birds *of the same broad lineage as the proto-Yehat*. They have begun forming flock-roosts in low caves. They show unusual *paired-behavior* — preening rituals that the Furling archive cannot yet decode but suspects of being proto-empathic. The Yehat-Pkunk split happens later (around 50,000 years from now); in our era they are arguably the same proto-species in two ecological niches.

### Proto-Druuge (Caeli region)
*SC2 race*: Capitalist slaver-traders. Greedy. Soulless.
*In our era*: small mammals living in heat-vent cave systems. They *hoard* — pebbles, bones, mineral fragments. Their colonies have evolved primitive *exchange protocols*: trading shiny objects for grooming, for shelter, for mating access. **Capitalism in proto-form.** The Furling archive notes "fascinating proto-economy; we will not interfere."

### ✱ Proto-VUX (Luyten region, "in their infancy" per Aaron's worldbuilding)
*SC2 race*: Xenophobic squid-creatures; revolted by other species' appearances.
*In our era*: tide-pool molluscs whose color-vision is *exceptional* and whose mating selection is *aggressively pattern-matching*. They will eat any of their own who develop "ugly" coloration; territorial males will display threat-patterns at any visual anomaly in their reef. **Xenophobia evolves from this.** The Furling archive notes "complex visual discrimination; possible cognitive substrate for future symbolic thought."

### Proto-Ilwrath (Tauri region)
*SC2 race*: Religious-zealot spiders who worship genocidal gods.
*In our era*: silk-spinning arachnids whose webs are stunningly elaborate *and* organized along radial axes that always point to specific celestial objects (whose significance the spiders themselves cannot articulate). They engage in mass-suicide rituals on certain calendrical days. **The proto-religion is already structuring their cognition.** The Furling archive is uneasy about this one and watches carefully.

### Proto-Syreen (Betelgeuse region)
*SC2 race*: Beautiful psychic women; their world destroyed by Mycon (in SC2's future).
*In our era*: humanoid sea-dwellers with bioluminescent skin patterns. Their colonies coordinate through a low-frequency vibrational communication that propagates kilometers underwater. They are NOT psychic yet — their cognitive substrate is just unusually *resonant* with electromagnetic patterns. The Furling archive notes "long-range coherent communication; if this evolves into telepathy as we suspect, this species is a future asset."

### Proto-Utwig (Gorno region)
*SC2 race*: Depressed warriors who wear masks to hide their faces.
*In our era*: armored bipedal grazers with extremely expressive facial musculature *and* a hyper-developed shame response. When threatened or rebuked by their herd-mates, they bury their faces. **The face-hiding is already the trauma response.** The Furling archive notes this with sympathy.

### Proto-Supox (Libris area)
*SC2 race*: Plant-people; gentle botanists.
*In our era*: ambulatory rooted-when-rested photosynthetic creatures, capable of slow walking. They commune via chemical-pollen exchange. They are pacifists by metabolism — fighting costs more energy than they can generate. **The gentle-botanist is already gentle.**

### Proto-Thraddash (Apodis region)
*SC2 race*: Warlike pyromaniacs who have cycled through 23 civilizations.
*In our era*: pack-hunting reptilian predators that have just learned to *deliberately spread* wildfires to drive prey. Their pack-leadership cycles violently every season. **The cyclical-civilization-collapse is in their pack dynamics already.** The Furling archive notes "concerning trajectory; we considered uplift but the Council voted to leave them."

### Proto-Zoq-Fot-Pik (Tucanae region)
*SC2 race*: Three-species alliance (one optimistic, one pessimistic, one quiet).
*In our era*: three distinct species sharing a tropical world — a tree-dwelling chittering primate-analog (Zoq), a burrow-dwelling melancholy crustacean (Fot), and a stone-still meditation-frog (Pik). They do NOT yet cooperate as a triumvirate. They will eventually. The Furling archive notes "three convergent intelligences in one biosphere; rare and lucky."

### Proto-Shofixti (Gorno-adjacent)
*SC2 race*: Short, warlike raccoon-people; sacrificed themselves in the Ur-Quan war.
*In our era*: small mustelid-analog mammals with *extraordinarily aggressive* territorial defense rituals. They throw themselves at much larger predators. **The kamikaze-bravery is already here.** The Furling archive admires them.

### Melnorme — full sentient, *not* proto (see `MELNORME_PROTO` tags in starmap — name kept for the data tag only)
*SC2 race*: Mysterious nomadic cyclopean merchants; trade in information, fuel, and technology. Iconic orange-pod silhouette, single deep-blue eye.
*In our era*: **already fully sentient.** A composite species — the public face is the cyclopean orange-pod form humans will later meet in SC2, but each pod is *piloted* by a gas-cloud energy-being whose cognition lives in ionization cascades across the host super-giant's heliopause. They communicate through the pod's mechanical voicebox in the colony dialect; with each other, they communicate by direct ionization-pattern signaling.

**Homeworld — and its impending loss.** The Melnorme have a single canonical homeworld, **Drahn** (orbits a yellow dwarf within the cluster, NOT at a super-giant — the super-giants are *trading posts*, not the home). When the Precursors open the Migration portal, the **majority of the Melnorme leave** — but a hardline minority refuse to abandon Drahn's hot-deep-mantle research archives. **The Others find them.** Drahn is annihilated. The surviving Melnorme — the ones who *did* leave — become the nomadic fleet known to SC2, scattered permanently across the host galaxy and (later, after some return through the Migration portal in SC2 era) across the neighbor galaxy too. **Their nomadism is not a cultural choice; it is grief.**

**Why they buy organic material.** Each surviving Melnorme has dedicated their post-homeworld existence to a single project: **mapping the detectable-intelligence threshold.** The Others sense concentrations of cognition above some signal-strength floor. The Slylandro Cloaking Satellite is a brute-force solution — *suppress everything*. The Melnorme research is finer-grained: *what is the exact curve*, and *can a species sit just below it* while still functioning? To characterize the curve they need samples at every position on the cognitive spectrum, from microbial to sapient. Hence the universal hunger for organic material — **especially lower-life specimens** which mark the lower bound of the curve and are the part the Melnorme themselves cannot easily produce (their own biology is exotic and high-cognition by definition).

**Currency**: they trade **advanced technology and information for organic material.** Council Credits are useless to them — molecular matter is what their research needs. The Steward sells them BIO-cargo collected from planet scanning; in return the Melnorme offer ship modules and information unlocks the Furling Council cannot or will not provide. Some of what the Melnorme sell is *derived from* their threshold research (sensors that read the cognition curve, signal-dampener field projectors).

**Faction alignment**: **Precursor-faction (Stay-Go alignment) — with a faction-internal schism.** The Melnorme who survive align Precursor. The Drahn-loyalists who refused to leave are the Melnorme equivalent of the Furling Defenders: principled, doomed, and the cause of the destruction-event that fractures their civilization permanently. **In the slice, the player can witness or interfere with this schism if they visit Drahn during the Migration window.**

**Furling Council attitude**: cordial-but-distant trade partner. The Council considers the Melnorme price model "predatory but fair." Most Stewards make at least one Melnorme call per career, almost always for an information item the Council has chosen not to disseminate. **After Drahn falls, the Council formally mourns** — the loss is the first major Migration-era casualty among Precursor-aligned allies, and the lesson lands hard: leaving is not safe for the holdouts. The lesson echoes through Persuader-faction recruitment.

### Proto-Dnyarri / Proto-Umgah (Orionis area; tagged `DNYARRI_PRIMITIVE`)
*SC2 race*: The Talking Pet (mind-controllers) and the Umgah (their hosts, shape-shifters).
*In our era*: parasitic micro-organisms that infect host species and subtly modulate their behavior. They are not yet sentient *themselves*; the modulation is biological-instinct level. The Furling archive flags them as "low-priority surveillance — modulation behavior could evolve into hostile cognition; recommend long-term observation."

### Notes on Already-Sentient Species (not proto-)

These are NOT in this doc — they have their own canon:

- **Slylandro**: sentient now, Homesteader path (Cloaking Satellite)
- **Proto-Ur-Quan + Proto-Qor-Ah**: mid-uplift, the Continue/Stop/Cleanse dilemma
- **Mycon biots**: pre-sentient but in active terraforming service; Deep Child whispers may awaken them
- **Mmrnmhrm**: machine sentients, the survivor lesson
- **Chenjesu**: rooted sentients, witnesses to a prior cycle
- **Androsynth**: time-displaced refugees
- **Arilou**: voluntary-exile path
- **Melnorme**: sentient nomadic traders (see entry above — moved out of proto-list)

The Furling Council has *deliberately decided* not to uplift the proto-species in this fanservice list. Their reasoning: the Migration deadline makes new uplifts untenable. Leave them. They will be here when the galaxy regrows.

## Slice Scope vs. Full Game

For the **vertical slice**, we pick 2-3 proto-species visits to include in the slice's cluster:

- **Proto-Spathi** — universally recognizable; the cowardice is in the burrow-dwelling; gives a moment of fond recognition for SC2 fans
- **Proto-VUX** — already in the slice's region (per `VUX_PROTO` tag at Luyten); xenophobia-from-color-vision is a fun reveal
- **Proto-humans on Sol** — if Sol is in or near the cluster (it's at 1793×1450 in extracted data); the visit to Earth is *the* fanservice beat. Watch a single hominid bury their grandmother. Note the tool-use. Leave silently.

The remaining ~12 proto-species become **full-game content** — the player visits them across the galaxy after the slice. Each visit is small but the collected Archive becomes a *substantial Furling-perspective natural history* of the galaxy as it stood 250,000 years before SC2.

## The Archive (UI element)

The Furling bio-archive deserves its own slice UI panel. Lists every observed proto-species with:

- Species name (Furling-given, e.g. "the burrowing molluscs of [system name]")
- The cognitive trajectory note
- The Furling council's recommendation ("leave undisturbed" — universal)
- The player's optional personal annotation
- A small portrait (AI-generated, with per-individual variation as ever)

This is part of the **Cluster Status Board** UI ecosystem (see [win-condition-and-methods.md](win-condition-and-methods.md)), but specifically for *observations* rather than *decisions*. Filling the Archive is its own quiet reward arc.

## The Thematic Counterweight to the Uplift Dilemma

Here is why this content matters thematically:

The Ur-Quan uplift project is the **dangerous, ambitious, well-intentioned** thing the Furlings did. It produces monsters because the timeline ran out. Stop, Continue, or Cleanse — every option is heavy.

The proto-species observations are the **patient, modest, well-intentioned** thing the Furlings did. They simply *watched*. And those species will inherit the regrowing galaxy in 250,000 years, naturally, gracefully, on their own developmental schedule.

> *The path of least intervention is, often, the most loving path.*

SC2 fans will encounter the proto-Spathi and feel something. The Star Control Zero player, even without SC2 context, will feel a different thing — *we did not interfere with this species; in some far future they may build their own civilization on their own terms*. Both readings are correct. The slice has both.
