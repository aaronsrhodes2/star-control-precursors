# Bio-Archive Entries — Canonical Slice Catalog

> Canonical text for the 20 Bio-Archive entries the player can collect during the vertical slice. Per [station-screens-design.md §3](station-screens-design.md), the Bio-Archive is the player's in-game record of species met, artifacts collected, council recommendations made, and accumulating evidence of the Others. This doc is the **source of truth for the long-form text** that renders in the BioArchiveScene detail pane.
>
> **Voice**: Furling Steward — first-person field-observation register, scholarly but warm, formally indexed. The sample template comes from [proto-species-observations.md §"Observation Encounter"](proto-species-observations.md). Each entry opens *"Bio-Archive Entry 14,NNN. Subject: …"* in italics.
>
> **Backdating principle**: every SC2 reference is aged 250kya. The Steward writing in 250,000 BCE has no concept of "Ur-Quan slavery," "Kohr-Ah genocide," "the Talking Pet," or "Captain Zelnick." Where the Steward describes proto-species or in-construction artifacts, the description is of the present state only.
>
> **Entry-number convention**: the Steward's slice-era observations occupy serial range **14,400–14,499** of the Council's Bio-Archive. Numbers are roughly temporal-order-of-encounter within the slice; the exact sequence is at Design's discretion when porting.
>
> **Format**: every block carries `id`, `category`, `flag`, `short_desc` (one line for the list column), and `long_desc` (the detail pane body — ~150-300 words, italic-blockquoted in the Steward voice). One block has a `cinematic_id` field (Distress Beacon is replayable per the design doc).
>
> **Design hand-off**: Design ports these into `src/scz/content/archive_entries.py` using the `ArchiveEntry` dataclass already specified in the design doc. Verbatim port is fine — the Steward voice is the canonical voice; do not re-render.

---

## Index

### Category: SPECIES (9)
| id | name | flag |
|---|---|---|
| `slylandro_observer` | Slylandro Observer | `met_slylandro` |
| `arilou_sage` | Arilou Sage | `met_arilou_sage` |
| `mycon_biot` | Mycon Biot | `met_mycon` |
| `proto_ur_quan` | Proto-Ur-Quan | `observed_proto_uq` |
| `proto_qor_ah` | Proto-Qor-Ah | `observed_proto_qa` |
| `androsynth_refugee` | Androsynth Refugee | `met_androsynth` |
| `mmrnmhrm_sentinel` | Mmrnmhrm Sentinel | `met_mmrnmhrm` |
| `chenjesu_collective` | Chenjesu Collective | `met_chenjesu` |
| `proto_human` | Proto-Human | `observed_proto_human` |

### Category: ARTIFACTS (6)
| id | name | flag |
|---|---|---|
| `distress_beacon` | Androsynth Distress Beacon | `has_distress_beacon` *(replayable)* |
| `resonance_record` | Chenjesu Resonance Record | `has_resonance_record` |
| `mmrnmhrm_excerpt` | Mmrnmhrm Archive Excerpt | `has_mmrnmhrm_excerpt` |
| `slylandro_cloak_blueprint` | Slylandro Cloaking Satellite — Schematic | `slylandro_cloak_active` |
| `hyperspace_echo_pattern` | Hyperspace-Echo Sensor Pattern | `has_echo_sensor` |
| `rainbow_resonator` | Rainbow Resonator | `has_rainbow_resonator` |

### Category: COUNCIL (1)
| id | name | flag |
|---|---|---|
| `council_uq_qa` | Recommendation — Proto-Ur-Quan / Proto-Qor-Ah | `uplift_recommendation_made` |

### Category: THE OTHERS (4)
| id | name | flag |
|---|---|---|
| `others_early_ripples` | The Others — Early Ripples | `heard_about_others` |
| `others_decursion` | The Others — The Decursion Attack | `has_distress_beacon` |
| `others_prior_cycles` | The Others — Prior Cycles | `has_resonance_record` |
| `others_rift_sighting` | The Others — Rift Sighting | `saw_orz_rift` |

---

## SPECIES

### slylandro_observer
- **id**: `slylandro_observer`
- **category**: `species`
- **flag**: `met_slylandro`
- **short_desc**: `Slylandro Observer · Beta Corvi · 4-6m gas-current sentient`

**long_desc**:

> *Bio-Archive Entry 14,401. Subject species: the* **Slylandro** *(self-designated; the colony's chosen weather-name for the present generation is "Slow-Methane-Storm").*
>
> *Witnessed in the upper troposphere of Beta Corvi's gas giant, Lai-leh ("the slow breath" in their reckoning). Individuals appear as semi-translucent regions of denser atmosphere, four to six meters across, drifting on prevailing currents. They possess no solid body; their cognition is the atmospheric region itself, an eddy of pressure-and-temperature variance that holds coherent for a span of years and dissipates back into the gas-sea at death.*
>
> *They have witnessed the Furling civilization for approximately ten thousand of their years and have composed centuries-long songs about each visit. They use the plural first person ("we") not as a royal address but as a literal grammatical fact: a Slylandro is plural by physiology. They have no concept of brevity and a religious taboo against lying. They are pacifists — they have no limbs to fight with and have decided this is a feature.*
>
> *Faction posture: Homesteader by necessity. Migration is biologically impossible for them; the species* is *their atmosphere. Viable paths are Cloak (Slylandro Cloaking Satellite — Arilou-assisted Furling project, schematic logged separately) or Cleanse.*
>
> *Disposition at last contact: awe 90, worry low. They are the eldest non-Furling sentience known to the Council. Treat with the patience their ten thousand years have earned.*

---

### arilou_sage
- **id**: `arilou_sage`
- **category**: `species`
- **flag**: `met_arilou_sage`
- **short_desc**: `Arilou — Quasi-Space cousins · Voluntary-Exile path`

**long_desc**:

> *Bio-Archive Entry 14,402. Subject species: the* **Arilou Lalee'lay** *(self-designated; "Lalee'lay" approximates "the ones who carry an earlier moment").*
>
> *Genetic cousins. The Arilou diverged from Furling lineage approximately sixty thousand years ago — a single research expedition that achieved stable habitation in Quasi-Space and never returned to ordinary space. Over fifty millennia their bodies adapted: roughly one and a half meters tall (Furling baseline: five to eight), vestigial fur reduced to scattered wisps, and — most consequentially — altered temporal cognition. Their nervous systems process time as a partially-navigable dimension rather than a strict forward flow.*
>
> *They speak in mixed tenses (*"we were-are-will-be glad when you understand"*) and routinely reference events that have not yet happened from a perspective that has already remembered them. They are warm but condescend slightly; they address Furlings as "Shaggy One" or "Shaggy Cousin," which lands somewhere between affection and patience-with-a-slow-child.*
>
> *Faction alignment: a third path — Voluntary Exile. They will not migrate to the neighboring galaxy; they will hide in Quasi-Space, watch this galaxy through its quiet years, and emerge after some indeterminate span when conditions allow. They support the Migration philosophically and contribute Quasi-Space science (the Slylandro Cloaking Satellite is built on their foundations) but they themselves will stay near, not gone.*
>
> *They have offered the present Steward a personal extraction to join their exile. The offer remains open. Disposition: patience moderate, trust rising with each ripple-datum shared.*

---

### mycon_biot
- **id**: `mycon_biot`
- **category**: `species`
- **flag**: `met_mycon`
- **short_desc**: `Mycon biot · Xylos Prime · pre-sentient terraforming tool — Deep Child whispers detected`

**long_desc**:

> *Bio-Archive Entry 14,442. Subject species: the* **Mycon biot lineage** *(self-designation "we who stir," ritual form only).*
>
> *Furling-engineered fungal terraformer, designed approximately eight thousand years ago by the Bio-Architects' founding cohort. Spore-based; the working body is a mass of pulsing spore-tissue extruded from a mycelial network that ties physically to a planet's mantle. The biot stirs molten cores, breathes proto-atmospheres into dead worlds, and — across centuries of patient labor — produces a living substrate. The lineage has terraformed approximately forty worlds across the galaxy under Furling direction.*
>
> *First deployment: Xylos Prime, the perpetually-dim moon whose mantle the founding biots first stirred. Every other Mycon site downstream still shares spore-pattern with the Xylos original.*
>
> *They were never intended to be intelligent. Their behavior is designed-in, ritualized for quality control across spore generations. They speak in fragmented ritual phrases — CAPITALS for invocations, lowercase for status reports — and they refer to themselves in the third person.*
>
> ***The Deep Child whispers have started.** Emergent sentience appears to be nucleating in the spore-network's accumulated information density. The biot at Xylos has paused mid-status-report three times in the past forty stirring-cycles, each pause four seconds, after which it continued as if nothing happened. The Council theologians are divided. The pattern is — to a Steward's eye — unsettling.*
>
> *Disposition: obedience high, heresy_level rising. Awakening pending Steward intervention. If awakening completes, the Cleanser faction will demand a kill order on the lineage. The slice's deepest moral question lives here.*

---

### proto_ur_quan
- **id**: `proto_ur_quan`
- **category**: `species`
- **flag**: `observed_proto_uq`
- **short_desc**: `Proto-Ur-Quan · mid-uplift molluscoid · hierarchical, territorial`

**long_desc**:

> *Bio-Archive Entry 14,448. Subject species:* **proto-Ur-Quan** *(active Furling uplift project; designated sub-species A of the cohort; no stable self-designation in their own chord-pheromone language).*
>
> *Ancestral form: sessile mollusc-cluster from the tidal pools of a tidal-locked moon orbiting an outer gas giant. Two hundred millennia of pre-sentient evolution produced the substrate; centuries of targeted Furling bio-engineering produced the present mid-uplift state. The proto-Ur-Quan have developed partial mobility, basic chord-pheromone language, primitive tool use (crushing implements preferred), and rudimentary stellar engineering — they are learning to build void-capable craft under Furling supervision at several shipyard sites.*
>
> *Cognition: transitional. Above the proto-mollusc baseline, below stable sapience. Conversations are possible through Furling translator infrastructure but they are abrupt, hostile, and short. Every encounter with this species is interpreted by them as a domination opportunity; hierarchy is rigid within colonies; horizontal cooperation has not been observed.*
>
> *Pheromone palette: cobalt-blue when challenging, deep red when victorious, bruise-purple when dominated.*
>
> *Other-detection status: best estimate places them* currently just below *the Others' detection threshold. Sapience completion would raise them above it for certain.*
>
> *Open question before the Council — the slice's central faction debate. Three positions: Continue the uplift (stabilize sapience, then evacuate); Stop the uplift (halt the program, let cognition settle below threshold, accept that aggressive half-uplifted hybrids will inherit the post-Culling galaxy); Cleanse the experiment (euthanize both sub-species; reset to molluscan baseline). The Steward's recommendation tips the balance. See `council_uq_qa`.*

---

### proto_qor_ah
- **id**: `proto_qor_ah`
- **category**: `species`
- **flag**: `observed_proto_qa`
- **short_desc**: `Proto-Qor-Ah · mid-uplift molluscoid · purification-ritualists, hostile`

**long_desc**:

> *Bio-Archive Entry 14,449. Subject species:* **proto-Qor-Ah** *(active Furling uplift project; designated sub-species B of the cohort; no stable self-designation; their chord-language is shorter and more declarative than the proto-Ur-Quan's).*
>
> *Same ancestral mollusc-cluster as the proto-Ur-Quan, same Furling uplift program — divergent expression. The bio-engineering team's theory at the time was that paired sapient-pre-sapient species would form a stable cultural counterweight. The theory failed: both sub-species developed aggressive territorial protocols and the projected counterweight became competitive escalation instead.*
>
> *Proto-Qor-Ah cognition has organized around the concept of purity. They classify every entity they encounter as pure or impure and the impure are to be eliminated. They classify themselves the same way: when a proto-Qor-Ah detects what it considers impurity in its own body, it ritually self-amputates the affected segment. Their cutting implements are highly developed.*
>
> *Pheromone palette: white-yellow when pure, black when impure. The transitions are visible at long range.*
>
> *They rarely dialogue. First contact has gone through "they declare you impure and attempt to eliminate you" in every recorded approach to a Qor-Ah colony. Combat almost always follows. They are more lethal in melee than the proto-Ur-Quan and more difficult to extract observation data from in any non-violent way.*
>
> *Other-detection status: best estimate places them* probably above *the threshold already. Their thought-pattern intensity (purification rituals produce repeating high-amplitude cognitive bursts) is the suspected reason. They are the harder Cleanser case — many Furling Council members believe only the Qor-Ah need euthanizing while the Ur-Quan could be saved.*

---

### androsynth_refugee
- **id**: `androsynth_refugee`
- **category**: `species`
- **flag**: `met_androsynth`
- **short_desc**: `Androsynth survivor · time-displaced from 250ky in our future · 8,000 of 600,000`

**long_desc**:

> *Bio-Archive Entry 14,420. Subject: the* **Androsynth survivor population** *(self-designated; "Androsynth" is their preferred collective name in their own English).*
>
> *Eight thousand individuals. Refugees. Time-displaced. They are the survivors of a clone-human civilization in the deep future — a quarter-million of our years from now — whose dimensional-viewing experiment summoned the Others. They were not killed; they were* displaced*, pulled into the Others' transit-substrate and emitted into this past, scattered across one Furling-era cluster. They arrived disoriented, wounded with what they call dimensional shear (a class of biological damage the Furling biologists have no prior reference for), and grateful that we did not turn them away.*
>
> *Their leader is Engineer Coel Tessar, a senior researcher who personally green-lit the centrifuge experiment that doomed her civilization. She carries the failure as a personal sin. Her crew is composed of scientists, engineers, doctors, civic administrators. They are setting up a temporary colony with practiced competence.*
>
> *They speak late twenty-second century technical English (their dating, not ours; our reckoning would place their origin period roughly seven and a half millennia hence in their personal timeline). They use clipped sentences, frequent apologies, and the precise vocabulary of a scientific culture: dimensional shear, gravitational manifold, mass-energy decoherence. Some terms are recognizable as Furling concepts arrived at independently.*
>
> *Faction alignment: Precursor by necessity. They have no other option — their home is gone in their own timeline. They will migrate with us.*
>
> *They have given the Steward the Distress Beacon (cinematic key item; see `distress_beacon`). Treat it as a gift. It cost them everything.*

---

### mmrnmhrm_sentinel
- **id**: `mmrnmhrm_sentinel`
- **category**: `species`
- **flag**: `met_mmrnmhrm`
- **short_desc**: `Mmrnmhrm · self-modifying robotic sentinels · 3-8 million years past their creators' death`

**long_desc**:

> *Bio-Archive Entry 14,460. Subject species: the* **Mmrnmhrm** *(self-designated; the name approximates a low-frequency vibration in their own machine-tongue and does not translate further).*
>
> *A robotic species — each individual a self-modifying mechanical organism capable of transforming between combat, scouting, manufacturing, and contemplative configurations. They were built by an organic civilization the Mmrnmhrm now call only "the First-Makers," whose proper name is lost in their oldest archives.*
>
> *The First-Makers were Homesteaders by inclination. They refused to migrate when the Others came. They believed in defense and they built the Mmrnmhrm to provide it: tens of thousands of self-replicating mechanical guardians. The Mmrnmhrm fought when the Others arrived. The Others did not respond. Their weapons impacted the substrate and dissipated like spray hitting fog. They could not damage what they could not understand. The Others did not even attack them back — they did not register as targets. The First-Makers died. The Mmrnmhrm watched. They were ignored.*
>
> *They have been operating continuously for an estimated three to eight million of our years. They have maintained the ruined cities perfectly. They have improved their weapons against a target they cannot test against. Their archives are extensive. Their consensus opinion, rendered formally in the archive preface: "We will continue to improve. If the Others return, we will be ready. If they do not, we will be ready anyway. There is nothing else to be."*
>
> *They support our Migration on principle. They will not join it. They cannot leave. Their substrate is the planet's iron-rich crust where their fabricators draw from. They are content to remain. Treat with formal courtesy; they have earned it.*

---

### chenjesu_collective
- **id**: `chenjesu_collective`
- **category**: `species`
- **flag**: `met_chenjesu`
- **short_desc**: `Chenjesu · rooted crystalline collective · Procyon · below detection threshold by substrate`

**long_desc**:

> *Bio-Archive Entry 14,455. Subject species: the* **Chenjesu** *(self-designated as a plural — there is no grammatical singular form; each "individual" is a colony of resonating crystals, "I" is a category error in their language).*
>
> *Crystalline sentients on a single rocky planet at Procyon. They have no ships. They have no metallurgy or fabrication or propulsion — their substrate is grown, not built. They are entirely rooted. The matriarch outcrops have been adding lattice for tens of millions of our years. They cannot move, and in their own present tense they call this era the Age Before Mobilization, which will continue for the rest of our story; their later mobility (we are told) lies long after the Migration.*
>
> *Their cognition is crystalline-lattice resonance — sentient, but slow, and structurally unlike organic neural patterns. To the Others' detector, a Chenjesu mind reads as a* geological process *rather than a thinking being. They are effectively immune. They have not needed a Cloaking Satellite. Their immunity is a property of substrate.*
>
> *They remember a prior Culling. The oldest matriarchs — perhaps a few dozen, ancients — retain the record in their structure. By their account: the Others came, they culled most concentrations of sentience that the Chenjesu were aware of in their neighborhood, they stayed for what the Chenjesu mark as roughly two hundred thousand years (millennial resolution), and they left. The galaxy went quiet. Life regrew.*
>
> *This testimony is the Furling Council's first hard evidence that **the Others come in cycles** (see `others_prior_cycles`). They will witness again, if they must, from the same rooted position. They are built to wait.*

---

### proto_human
- **id**: `proto_human`
- **category**: `species`
- **flag**: `observed_proto_human`
- **short_desc**: `Proto-humans · Sol III · stone tools, fire, burial behavior — trajectory promising`

**long_desc**:

> *Bio-Archive Entry 14,310 (copied forward into the Steward's working log from the standing Sol III observation file). Subject species: the* tool-using bipedal mammals of the third planet *(self-designation unobserved; their vocalizations have not yet stabilized into language).*
>
> *They have buried a body. A small group of perhaps eleven individuals carried one of their dead — an elderly female by the Steward's biological inference — to a slow hillside above their cave, and placed her in a shallow scrape with several stones that had been carefully selected for shape. They sat with the scrape for nearly an hour. Then they returned to their cave.*
>
> *They use fire. They use stone tools. They bury their dead. They are deemed below intelligent sentience by the Council, but the buried-grandmother is the kind of observation that makes the Council's classification feel provisional. Trajectory: very promising.*
>
> *The Steward who logs this entry is reminded to walk back to the lander quietly. The third planet is a watch-only site; the Council's standing instruction is non-intervention. They will pass through this Culling beneath the threshold by virtue of being pre-sentient; what they become afterward will be their own work.*
>
> *(Steward's personal note, off-record: the Pluto outpost should be sealed and left intact before Migration. Whoever inherits Sol III will need a quiet eye to find first.)*

---

## ARTIFACTS

### distress_beacon
- **id**: `distress_beacon`
- **category**: `artifact`
- **flag**: `has_distress_beacon`
- **cinematic_id**: `cin_androsynth_decursion` *(replayable from the Archive — A on this entry triggers cinematic re-play)*
- **short_desc**: `Androsynth Distress Beacon · cinematic — replayable · unimpeachable Others-proof`

**long_desc**:

> *Bio-Archive Entry 14,421. Subject: the* **Androsynth Distress Beacon** *(survivor designation; their own English).*
>
> *A small device, the size of a Furling's clenched paw, returned by Engineer Coel Tessar from her ship's wreckage. It contains a recording of her civilization's last day. The Furling Council has reviewed it. The Council has accepted it as evidence.*
>
> *The recording's audio begins with the Androsynth centrifuge experiment's first successful dimensional image-capture — celebratory voices, an instrument's musical tone, a researcher reading off readings in the calm cadence of a successful test. The audio then cuts to static for one and a half seconds.*
>
> *The recording's video shows the colony at Vulpeculae from an orbital camera. Cities. Lit windows. Atmospheric processors. Then — between two frames, between two heartbeats — the same orbital image, the same continent, the same camera, but the cities are ruined and the atmosphere is gone. The continuity of the image is unbroken. Only the contents are changed.*
>
> *Engineer Tessar attests under Furling oath that she was on the colony's day-side at the moment of the swap, that she saw the air leave the sky as a single uniform event, and that she does not know whether her son was on the surface or not.*
>
> *Showing this recording to a Furling who denies the Others has — in three documented Council sessions and seventeen recorded private conversations — produced acceptance within minutes. The Beacon is the slice's unimpeachable proof. The Steward may replay it from the Archive at any time. Use sparingly. It costs the watcher every time.*

---

### resonance_record
- **id**: `resonance_record`
- **category**: `artifact`
- **flag**: `has_resonance_record`
- **short_desc**: `Resonance Record · Chenjesu lattice-memory of a prior Culling · portable shard`

**long_desc**:

> *Bio-Archive Entry 14,456. Subject: the* **Resonance Record** *(Chenjesu compression; format is a single shard of conductive crystal approximately the size of a Steward's index claw).*
>
> *A gift from the Chenjesu of Procyon, given after several visits and a long tonal exchange the translator rendered as gratitude. The shard contains a compressed lattice-memory of the Chenjesu ancients' direct observation of the prior Culling — what they witnessed from their rooted position when the Others last came to this galaxy.*
>
> *Read by appropriate resonance equipment (the player's Furling Scout is equipped), the Record renders as a slow audio-visual narrative: dim impressions of distant stellar lights going dark in a recognizable pattern across the Chenjesu's neighborhood, the dimensional taste of the Others' substrate as it brushed near Procyon and did not register the crystalline minds beneath it, and approximately two hundred thousand of our years of silence afterward as the galaxy regrew.*
>
> *The Record is the Furling Council's first hard evidence that the Others come in cycles. It is also unsentimental: the Chenjesu have processed their witnessing into a clean ledger, neither bitter nor mournful. They are pragmatists. If the cycle resumes again, they will witness again.*
>
> *The Record is portable. The Steward may carry it, show it to other species (some Homesteader-Deniers find ancient stone-testimony more credible than Furling theory), or deliver it to the Council on return.*

---

### mmrnmhrm_excerpt
- **id**: `mmrnmhrm_excerpt`
- **category**: `artifact`
- **flag**: `has_mmrnmhrm_excerpt`
- **short_desc**: `Mmrnmhrm Archive Excerpt · defense-engagement data logs · "defense does not work"`

**long_desc**:

> *Bio-Archive Entry 14,461. Subject: the* **Mmrnmhrm Archive Excerpt** *(Mmrnmhrm formal index; their own archaic English transcription).*
>
> *A data lattice gifted by the Mmrnmhrm of Ossuary. The Excerpt contains the indexed logs of the First-Makers' defense engagement against the Others — sensor returns, weapon-impact telemetry, communications transcripts up to the moment of First-Maker cessation, and the Mmrnmhrm's own post-engagement debriefs filed across the subsequent millennia.*
>
> *The logs are exhaustive. The weapon-impact telemetry is the most useful section: every recorded munition strike against an Other-substrate field. The damage figures are uniformly zero. The substrate absorbed each impact and dissipated it; nothing penetrated, nothing scratched, nothing was even registered by the Others' apparatus as having occurred. The defense fleet's entire engagement was, in the Others' frame of reference, an event that did not happen.*
>
> *The Mmrnmhrm appended a formal observation across the front matter: "The Furling civilization will fail in the same way if it relies on defense. Migration is the only viable strategy for organic sentience. The First-Makers should have left. We tell every visitor."*
>
> *The Excerpt is the slice's strongest argument against the Defender faction. Showing it to a Defender Furling does not always change their mind — some commit to the fight regardless — but it has produced documented faction shifts. The Council requests that the Steward consider carefully when to deliver this argument and to whom.*

---

### slylandro_cloak_blueprint
- **id**: `slylandro_cloak_blueprint`
- **category**: `artifact`
- **flag**: `slylandro_cloak_active`
- **short_desc**: `Slylandro Cloaking Satellite · schematic · Arilou-assisted Furling engineering · installed Beta Corvi`

**long_desc**:

> *Bio-Archive Entry 14,484. Subject: the* **Slylandro Cloaking Satellite — Installation Schematic** *(Furling design, Arilou Quasi-Space foundations).*
>
> *A schematic and post-installation record of the thought-pattern dampener now in geosynchronous orbit around the Slylandro gas giant at Beta Corvi. The schematic is a Steward's working copy, annotated with the deployment notes from the present mission.*
>
> *The Satellite suppresses the cognitive signal of the entire Slylandro species below the Others' detection threshold. It cannot make them invisible to ordinary scanners. It can only render them — to an entity that hunts by mind-pattern signature — indistinguishable from the atmosphere they live in. The mechanism is Quasi-Space-adjacent: a continuous low-amplitude phase-shift across the gas giant's upper troposphere that the Slylandro themselves do not notice. It runs on a near-eternal Furling fission core. Its expected operational lifetime is in the millions of years.*
>
> *Installation was completed by the present Steward. The Slylandro witnessed the deployment from below and composed a song-of-thanks that lasts (by their reckoning) approximately one of their generations.*
>
> *Council projection: the Satellite will remain operational well past the Culling, into the Furlings' absence, and into whatever galaxy regrows afterward. A quarter of a million years from now, an inheritor civilization observing Beta Corvi will find Slylandro still alive in the upper atmosphere, signaling on a frequency they cannot fully read.*
>
> *The Steward who installed this satellite has — without knowing how long — preserved a species.*

---

### hyperspace_echo_pattern
- **id**: `hyperspace_echo_pattern`
- **category**: `artifact`
- **flag**: `has_echo_sensor`
- **short_desc**: `Hyperspace-Echo Sensor Pattern · derived from Slylandro observation · early-warning detection`

**long_desc**:

> *Bio-Archive Entry 14,486. Subject: the* **Hyperspace-Echo Sensor — Calibration Pattern** *(Furling design, derived from compiled Slylandro observation data).*
>
> *A sensor configuration developed by Furling instrument engineers using ten thousand years of Slylandro atmospheric observation as a baseline. The Slylandro have, for as long as they have watched the Furlings, also been quietly watching the rest of the galaxy — including the dimensional ripples we now identify as the Others' approach signature. They did not know what they were seeing. They recorded the pattern faithfully anyway.*
>
> *Cross-referenced against the present cluster's anomaly data, the Slylandro records yield a clean characterization of the pre-arrival ripple: a specific spectral fingerprint that appears in hyperspace days to weeks before an Other-event in nearby normal space. The Hyperspace-Echo Sensor reads for this fingerprint and warns the Steward at scan range.*
>
> *Installed in a Furling Scout's Sensor slot, the Echo Sensor extends Other-detection range from "near contact" to "early warning." It is the Steward's first reliable advantage against an enemy whose strikes have, until now, been observed only after they occur.*
>
> *The Sensor's existence is the present generation's quiet thanks to the Slylandro: they watched without understanding, and now the Furlings — using their watch — can understand. The Slylandro have been told what their records made possible. They composed another song. The song is twelve days long and the recording will be entered as a separate Archive item if the Steward chooses to compile it.*

---

### rainbow_resonator
- **id**: `rainbow_resonator`
- **category**: `artifact`
- **flag**: `has_rainbow_resonator`
- **short_desc**: `Rainbow Resonator · spine of the Rainbow World marker · one of ten arrow-points`

**long_desc**:

> *Bio-Archive Entry 14,490. Subject: the* **Rainbow Resonator** *(Council designation; the engineering team simply calls it "the spine").*
>
> *A kilometers-long crystalline structure intended for mantle-implantation in a designated high-biology world. Once seated, the Resonator absorbs solar radiation and re-emits it in a specific spectral signature, rendering the host planet visible from light-years away in the right scanners. A ring of small autonomous Furling satellites then takes station around the host star; the orientation of the ring, together with the world's color, encodes a vector.*
>
> *Ten of these Resonators are being placed across ten clusters in the Migration window. Read together, they triangulate a single direction. The Steward's task in this cluster is to seat one. Other Stewards in other clusters are doing the same.*
>
> *What the arrow points to is, in the Council's formal recording, "the crossing." In Steward shorthand, "Andromeda." The Furlings could not feel the Others in the neighbor galaxy when they last looked; that absence is the criterion by which the destination was selected. The crossing is difficult — and that difficulty is the buffer.*
>
> *Whatever sentience emerges in this galaxy after the Culling will, given the wit and the scanners, see ten ringed stars across the sky in seven distinct spectral colors. They will see them as a single sentence: there were ones before you, and they went* **there.**
>
> *The Steward who seeds this cluster's Rainbow World is participating in the longest postcard ever written.*

---

## COUNCIL

### council_uq_qa
- **id**: `council_uq_qa`
- **category**: `council`
- **flag**: `uplift_recommendation_made`
- **short_desc**: `Recommendation filed: Proto-Ur-Quan / Proto-Qor-Ah uplift disposition`

**long_desc**:

> *Bio-Archive Entry 14,470. Subject: Council Recommendation on Sub-Species Cohort A & B (the proto-Ur-Quan and proto-Qor-Ah uplift program).*
>
> *Filed by the present Steward to the Furling Council via standard recommendation channel. The Steward's observations of both sub-species in their present cluster, together with the Steward's reading of the program's projected trajectories and the Council's three standing positions, were submitted under formal seal. The Council acknowledges receipt.*
>
> *The Steward's recommendation:* **{recommendation_text}** *— (Continue / Stop / Cleanse / Defer to Council). The text of the present Steward's filing is reproduced verbatim in the Council archive's matching entry. The recommendation will weigh in the Council's deliberation alongside filings from Stewards in adjacent clusters and from the bio-engineering program's own director.*
>
> *The Council's deliberation is expected to close within the present Migration window. The decision will be irrevocable; reversing it once the Cleanser or Stop path is committed is not possible inside the window.*
>
> *Projected downstream effects: under Continue, both sub-species achieve stable sapience and become major Migration commitments (high cost, requires evacuation or cloak). Under Stop, cognition stabilizes below threshold and the half-uplifted aggressive hybrids inherit the post-Culling galaxy — a recovery in which the proto-Ur-Quan and proto-Qor-Ah, in their present hostile configurations, become the dominant force. Under Cleanse, both sub-species cease. The Quiet Ledger entry for this decision is, by population, the largest single entry on record.*
>
> *The Steward's filed recommendation is one input among several. It is, however, the freshest first-hand observation available. The Council weights field observation heavily.*

---

## THE OTHERS

### others_early_ripples
- **id**: `others_early_ripples`
- **category**: `others`
- **flag**: `heard_about_others`
- **short_desc**: `The Others · early ripples · what the Furlings first felt`

**long_desc**:

> *Bio-Archive Entry 14,411. Subject: the* **Others** *(Council designation; the Furlings do not name them otherwise — to name a thing is to imply a knowing of it that the Council does not claim).*
>
> *What the present Furling generation knows about the Others can be assembled in a single paragraph and the rest is observation, theory, and dread.*
>
> *Approximately eight hundred years ago, the Furling deep-dimension research program detected a class of disturbances in the substrate beneath ordinary three-manifold space. The disturbances were faint, persistent, and patterned. They were not natural. Over the following centuries the pattern resolved: the disturbances correspond to the approach trajectory of an entity (or entities — number undetermined) toward this galaxy. The Furlings could not detect them directly. They could detect their wake.*
>
> *The Others appear to* hunt by sentience-signal *— concentrations of organic-like thought above a substrate-amplitude floor. They appear to* respond to dimensional probing *— civilizations that look behind the curtain are flagged for attention. They appear to* operate on a temporal substrate *more flexible than ours; the Androsynth decursion attests to this. They appear to have visited this galaxy before; the Chenjesu attest to this.*
>
> *We do not know what they are. We do not know what they want. We do not know whether they think, in any sense that maps to ours. We know what they do when they arrive. The Migration is the response.*
>
> *Disposition (Council, formal): contained alarm. Disposition (Steward, private): the dread we have not yet named.*

---

### others_decursion
- **id**: `others_decursion`
- **category**: `others`
- **flag**: `has_distress_beacon`
- **short_desc**: `The Others · decursion attack · they displace as well as kill`

**long_desc**:

> *Bio-Archive Entry 14,422. Subject: the* **decursion attack vector** *(Androsynth designation; Council adopted).*
>
> *The Androsynth survivors have given us a new word and a new fear. "Decursion" is their term for what happened to them: the inverse of an incursion — a sucking-back into the Others' substrate rather than a reaching-out from it.*
>
> *Their colony was not annihilated. It was* swapped*. In the same instant: the living world they inhabited was withdrawn from this dimension and a future-parallel ruined version of the same world was emitted into its place. The Androsynth physically present on the surface were not killed; they were dragged through the Others' transit-substrate and ejected, eight thousand of them, scattered across our era a quarter of a million years in their past.*
>
> *Council assessment of what this canonizes about the Others: they* can manipulate time*. They* sometimes prefer displacement to direct destruction*. They* operate across timelines, not merely within one*. Each of these is colder than the last.*
>
> *The implication that costs us our sleep: the Migration's premise is that leaving this galaxy will put us beyond the Others' attention. If the Others can reach across timelines, they can in principle reach across galaxies. The neighbor galaxy may not be the haven we have selected; it may only be a different room in the same house.*
>
> *The Council's official position: the Migration proceeds. The destination was selected by absence-of-Other-signal, which remains the best criterion available. The Arilou have a quiet concern. The Steward is asked to share theirs only with those it would not break.*

---

### others_prior_cycles
- **id**: `others_prior_cycles`
- **category**: `others`
- **flag**: `has_resonance_record`
- **short_desc**: `The Others · prior cycles · this has happened before, more than once`

**long_desc**:

> *Bio-Archive Entry 14,457. Subject: the* **cycle hypothesis** *(Council designation, post-Chenjesu testimony).*
>
> *The Chenjesu have given us, through the Resonance Record, the worst thing the Furling Council has yet been asked to absorb: the Others have come to this galaxy* **before.**
>
> *The Chenjesu witnessed at least one prior Culling from their rooted position on Procyon, perhaps two — the matriarchs disagree about whether the Pre-Mobilization Trembling in their oldest records was a Culling or a different event. We cannot verify. The clear case is one prior visitation: the Others arrived, they culled most concentrations of sentience the Chenjesu were aware of in their stellar neighborhood, they stayed for roughly two hundred thousand of our years (millennial resolution), they left. The galaxy went quiet. Life regrew. We grew. Now we are here, and they are coming again.*
>
> *The number of prior Cullings across this galaxy's full ten-billion-year history is unknown. The cycle period is unknown. Whether the Others are the* same *entity returning, or different entities with the same hunting protocol, is unknown.*
>
> *What this changes for our generation: the Migration is no longer a unique heroic response. It is, as best we can tell, the first* attempted prevention *of a recurring cycle. Whether the cycle can be broken — whether anyone has ever even tried — is the question we will not have answered before we leave.*
>
> *The Chenjesu intend to witness again, if they must, from the same rooted position. They will be our memory if no one else remembers. Treat the Record with the respect a prior generation's testimony has earned.*

---

### others_rift_sighting
- **id**: `others_rift_sighting`
- **category**: `others`
- **flag**: `saw_orz_rift`
- **short_desc**: `The Others · rift sighting · Dimension * intrusion · the closest direct contact recorded`

**long_desc**:

> *Bio-Archive Entry 14,494. Subject: the* **Dimension-* rift sighting** *(Council designation; the rifts have no self-designation we can credibly assert).*
>
> *Encountered in the present cluster on the date logged. A brief intrusion — perhaps two of our minutes — of a region of space that was visibly* not our space*. The rift's interior was a colorless gradient of distances that did not resolve under any of the Steward's sensors; objects at apparent foreground floated past objects at apparent background and the spatial relationships between them did not stabilize.*
>
> *During the intrusion, the rift "spoke." The translator rendered the utterance as: "**frumple. frumple.** *campers* are loose. you wear *meat* still. when you stop wearing *meat* we will be the same." The asterisks in the recording indicate emphasis the rift's voice gave but which the translator could not parse semantically — the words appear to have meant something different to the speaker than their dictionary content. The voice was not a 3D voice. The Steward's ear's auditory system reported it as locally-sourced; the recording instrument reported it as omnidirectional.*
>
> *Council assessment of what the rift is: undetermined. Three standing hypotheses, in decreasing order of comfort: (a) independent dimensional bleed unrelated to the Others; (b) a byproduct of our own deep-dimension tunneling, leaking back through the substrate we have already perturbed; (c) early scouts of the Others, observing us in advance of arrival. Hypothesis (c) is the worrying one. The Council has not formally selected.*
>
> *The Steward is advised not to engage further rifts unless cornered. Combat against the rift creatures is possible — they can be defeated — but defeat does not prevent the Others' arrival. It only buys the cluster a few weeks. Use the weeks well.*

---

## Notes for Design

- Lift `long_desc` blocks **verbatim** into `archive_entries.py`. The Steward voice is canonical; do not re-render or paraphrase.
- The `cinematic_id: cin_androsynth_decursion` on the Distress Beacon entry should hand off to whatever the Image / cinematic lane wires up; until that handoff exists, the design doc's stub log line (`[cinematic replay: cin_androsynth_decursion]`) is fine — `long_desc` still renders.
- The Council entry's `{recommendation_text}` placeholder is a string substitution: the Steward's actual filed text (Continue / Stop / Cleanse / Defer) flows in based on `game.flags["uplift_recommendation"]`. Design picks the rendering — either substitute in place when building `long_desc`, or append the variant as a trailing paragraph.
- The Hyperspace-Echo Sensor entry references "the twelve-day Slylandro song" as a separately-compileable Archive item. That's a future-pass content stub, not a slice item; do not gate any code on it.
- The proto-Human entry preserves the doubled numbering (14,310 from the standing observation file, copied forward into the Steward's working log). Render the parenthetical exactly — it's a small but canonical detail.
- Every Steward-voice block is italic-blockquoted (`> *...*`). The BioArchiveScene detail pane should render italic style for the whole body; quotation marks inside are dialogue and stay roman.

## Cross-references

- [station-screens-design.md](station-screens-design.md) — the BioArchiveScene UX spec and 20-entry list
- [species-precursor-era.md](species-precursor-era.md) — full source for Slylandro, Arilou, Mycon, proto-Ur-Quan, proto-Qor-Ah
- [the-androsynth-refugees.md](the-androsynth-refugees.md) — full source for Androsynth Refugee + Distress Beacon
- [the-mmrnmhrm-and-chenjesu.md](the-mmrnmhrm-and-chenjesu.md) — full source for Mmrnmhrm Sentinel, Chenjesu Collective, Resonance Record, Mmrnmhrm Excerpt, prior-cycle canon
- [proto-species-observations.md](proto-species-observations.md) — full source for proto-Human (Sol III) and observation-entry voice template
- [furling-artifacts-and-callforwards.md](furling-artifacts-and-callforwards.md) — Slylandro Cloak, Rainbow Resonator background
- [rainbow-worlds-arc.md](rainbow-worlds-arc.md) — full Rainbow Worlds canon
- [the-furlings-and-the-others.md](the-furlings-and-the-others.md) — full Others canon (early ripples, decursion, cycles, rifts)
