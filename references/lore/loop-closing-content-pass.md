# Loop-Closing Content Pass — All Missing Species + Full Quest Dialog + Combat Banter + Common Room Beats

> Aaron dispatch (2026-05-18): *"I would like you to creatively fill in all of the gaps. Fill out the quest dialog, the ship-to-ship banter, the common room banter, anything in the spreadsheets that is missing, creatively invent it and dispatch any related image or sound, code, or image requirements to the correct chat. I want to close the loop on the game tonight with full content, placeholders if needed."*
>
> Single-doc content-completion pass covering the 11 remaining species with full canon, quest dialog FSMs, combat banter pools, and Common Room reaction beats. Designed for direct porting into `tools/build_quest_inventory.py` (parallel chat) and `tools/build_species_inventory.py` (parallel chat). Where canon is provisional or placeholder, marked **[PLACEHOLDER]**.
>
> **Species covered**: Stelloth / Selvenne / Kovellim / Karavem / Mrokon / Taalo / Burvixese / Thinn / Melnorme / Dnyarri / Orz-rift-entities
>
> Plus §12 cross-encounter Common Room banter additions, §13 dispatches to all three chats, §14 open Aaron-calls.

---

## 1. Stelloth — *Three-Voice Chord-Beings* (Precursor-faction)

**Biology**: three-body chord-being. Each individual canonically consists of **three biological bodies** operating at different perceptual timescales: **Speaker** (canonical fast-time; canonical-handles immediate conversation), **Witness** (canonical normal-time; canonical-observes-and-records), **Counter** (canonical slow-time; canonical-counts and canonical-keeps-the-tempo). Cannot canonical-contract unless all three are canonical-aligned. Canonical *temporal-cognition triad* — each body experiences time at canonical-different-rate; canonical *alignment-moments* are when all three canonical-share-a-now. Canonical 3 bodies + 1 mind across three perceptual streams.

**Faction alignment**: Precursor (Migrate).

**Voice register**: three-voice-not-aligned comedy. Speaker delivers canonical-rapid lines; Witness canonical-corrects-and-amends; Counter canonical-keeps-counting. Sample:
- Speaker: *"We accept your offer, Steward."*
- Witness: *"The offer was made eleven seconds ago. It contained four conditions."*
- Counter: *"Forty-seven, forty-eight, forty-nine. Forty-nine seconds we have been considering."*
- Speaker (revising): *"We... need a moment."*

**Canonical NPC**: **Tarvel-Three-Voices** (canonical artifact-trader leadership-chord; canonical: each body has a distinct sub-name — *Tarvel-Speaks* / *Tarvel-Watches* / *Tarvel-Counts*).

**Quest** `stelloth_artifact_trade`:

```yaml
arrival:
  Speaker: "Steward. We would trade with you. Artifacts. Specifically."
  Witness: "We have been preparing the trade-list for fourteen days. The list is canonical-current."
  Counter: "Eight. Nine. Ten."
  choices:
    - "What artifacts?" → about_trade
    - "Why do you want to trade?" → about_purpose
    - "Farewell" → null

about_trade:
  Speaker: "We have catalogued canonical-pre-decursion engineering samples. We would canonical-exchange them for canonical-organic-material from your cluster."
  Witness: "The exchange ratio is canonical-favorable to the Steward. We are canonical-curious about your canonical-bio-data."
  Counter: "Fifteen. Sixteen."
  choices:
    - "I have BIO-cargo to trade" → trade_complete (side_effect: trade BIO→module:STELLOTH_PHASE_LENS)
    - "Tell me about the lens" → about_lens
    - "I need to think" → null

about_lens:
  Speaker: "The Phase-Lens canonical-allows brief alignment-glimpses across perceptual timescales."
  Witness: "Functionally: canonical-slow-motion sensor reads + canonical-predictive-warning of canonical-imminent-events ~3 seconds in advance."
  Counter: "Twenty. Twenty-one."
  choices:
    - "I'll trade" → trade_complete
    - "Back" → about_trade

about_purpose:
  Speaker: "We are canonical-Migrating with the Precursors. We are canonical-carrying our archives. We have canonical-no-need for canonical-pre-decursion samples we cannot canonical-fit on our vessels. Trade them away. Make them canonical-someone-else's-archive."
  Witness: "The decision was made by the chord. The chord is canonical-aligned on this matter."
  Counter: "Twenty-eight. Twenty-nine. Thirty."
  choices:
    - "Tell me the trade" → about_trade
    - "I understand. Farewell" → null

trade_complete:
  Speaker: "The trade is canonical-complete. The Phase-Lens is yours."
  Witness: "Logged. The exchange ratio honors the Steward."
  Counter: "Thirty-six. Thirty-seven. Goodbye."
  side_effect: terminal:Migrated; module:STELLOTH_PHASE_LENS; standing:Persuader+1
```

**Combat banter** (canonical: Stelloth rarely combat — they prefer trade; if forced):
- **Opening**: Speaker *"We did not want this."* / Witness *"The choice has been made."* / Counter *"Two. Three."*
- **75%**: Speaker *"We are returning fire."* / Witness *"The fire is canonical-disproportionate to your aggression."* / Counter *"Eleven. Twelve."*
- **50%**: Speaker *"Steward, withdraw."* / Witness *"The withdrawal would be canonical-honored."* / Counter *"Twenty-one. Twenty-two."*
- **25%**: Speaker *"The chord is canonical-fraying."* / Witness *"Alignment difficulty rising."* / Counter *"Thirty. Thirty-one. Thirty-two."*
- **5%**: Speaker *"We will not fall together."* / Witness *"One of us will survive."* / Counter *"Forty. ...Forty."* (canonical: Counter has stopped counting; the chord is breaking)
- **Post-fight victory**: Speaker *"We are alone now."* / Witness *"The chord has canonical-fractured."* / Counter *"None."*

**Common Room reaction beats**:
- Mraka: *"Three voices. From one being. Forty-Seven, please log that Stelloth do not need committees because they ARE committees."*
- Forty-Seven: *"Logged. I am noting that I have approximately three of myself, distributed across the ship's subsystems. I am, by my standards, canonical-curious about whether I qualify as a chord."*
- Tarven: *"Forty-Seven. You do not."*
- Forty-Seven: *"Acknowledged."*

**Bio-Archive entry** (Steward voice):
> *Bio-Archive Entry 14,471. Subject: the Stelloth — three-body chord-beings. The chord-Tarvel-Three-Voices canonical-traded with us; we exchanged BIO-cargo for the Phase-Lens device. The trade was canonical-favorable. The chord canonical-Migrates with the Precursors. We will not see them again until Andromeda; we have been told they canonical-bring their archives.*

---

## 2. Selvenne — *Planet-Scale Coral Hive-Mind* (Precursor-faction)

**Biology**: planet-scale coral hive-mind on Vellumar. Each polyp holds ~1 year of canonical-experiential memory. Touching a polyp canonical-transmits qualia in first person (canonical *Reef-Touch* mechanic). Cannot canonical-leave the reef unaided — canonical Furlings physically lift the reef in canonical-pieces during Migration. Canonical no individuals; canonical *the entire species is one continuous mind* distributed across the planet's coral substrate.

**Faction alignment**: Precursor (Migrate; canonical-logistics-intensive).

**Voice register**: hive-mind pre-knowledge comedy. *"We knew you would say that"* canonical-baseline. Pre-emptive responses to questions not yet asked. Reef-Touch transferring qualia in first person. Patient anticipation. Canonical *plural-as-singular* address ("we are; we have prepared").

**Canonical NPC**: **Choir-Of-The-East-Reef** (canonical chorus-spokesperson; canonical-renders as a single voice with many overlapping subtones; canonical *not a chord like Stelloth but a chorus — same content, many simultaneous voicings*).

**Quest** `selvenne_memory_archive`:

```yaml
arrival:
  Choir: "Steward. Yes. We knew you would arrive. We have prepared the answer. We have been preparing it for thirty-seven years. Please ask the question now so we may give the answer formally."
  choices:
    - "What question did you prepare for?" → about_question
    - "Will you migrate with us?" → about_migration
    - "Farewell" → null

about_question:
  Choir: "The question is: will you help us evacuate the reef. Our reef cannot canonical-walk. You have canonical-lifters. We have canonical-prepared the reef-pieces for canonical-transport."
  choices:
    - "Yes, we will help" → migration_accept
    - "How much of the reef can survive?" → about_capacity
    - "Back" → arrival

about_capacity:
  Choir: "Approximately seventy-three percent of the canonical-current reef can be canonical-lifted with canonical-current Furling capacity. The remaining twenty-seven percent is canonical-too-deep-or-too-large. They have canonical-already-agreed to remain. They will canonical-witness the canonical-Culling from the canonical-reef-roots. They have canonical-prepared their canonical-final-memories for our canonical-survivors to canonical-carry."
  choices:
    - "We will lift the seventy-three" → migration_accept (side_effect: terminal:Mixed_Migrated_Witness; module:SELVENNE_REEF_TOUCH)
    - "Can we save more?" → about_overcapacity

about_overcapacity:
  Choir: "Yes. If your canonical-vessel-cargo is canonical-not-loaded with canonical-other-priorities. We would canonical-add three percent for each canonical-vessel-volume you canonical-dedicate. The trade is canonical-yours."
  choices:
    - "Dedicate cargo" → migration_accept_extra (side_effect: terminal:Migrated; module:SELVENNE_REEF_TOUCH; standing:Persuader+2; reduces:Steward_cargo_capacity-10%)
    - "Standard capacity is fine" → migration_accept

migration_accept:
  Choir: "Yes. We knew. Begin the canonical-lift when canonical-ready. We are canonical-ready. We have been canonical-ready for canonical-fourteen years."
  side_effect: terminal:Mixed_Migrated_Witness; module:SELVENNE_REEF_TOUCH; standing:Persuader+1

about_migration:
  Choir: "Yes. Most of us. Some of us canonical-cannot. The canonical-cannot have canonical-already-agreed. The remainder canonical-Migrate."
  choices:
    - "I'll help" → about_question
    - "Back" → arrival
```

**Combat banter** (canonical: Selvenne never engages in space combat; canonical *the reef does not have ships*; canonical *if attacked, polyps cannot defend — they only witness*):
- Canonical *NO combat banter*. The Selvenne are canonical-pacifist-by-physiology. The Steward who fires on the reef canonical-strikes-canonical-non-defenders. Canonical *standing collapse + Bio-Archive Quiet-Ledger entry*. The Selvenne canonical-do-not-respond to fire; they only canonical-record-the-Steward's-act-in-their-final-memories.

**Common Room reaction beats**:
- Vresh (hum-pattern): *"We-all sense the Selvenne. We-all are kindred. We-all are also lifting reef-pieces. The work is canonical-good."*
- Sevra: *"They prepared the answer for thirty-seven years. I have been preparing my answer for twenty-five. They are canonical-more-patient than I am."*
- Forty-Seven: *"I am noting that the Selvenne canonical-knew we would arrive. I am also noting that they were correct. I am, by my standards, canonical-impressed."*

**Bio-Archive entry**:
> *Bio-Archive Entry 14,472. Subject: the Selvenne — planet-scale coral hive-mind on Vellumar. Plural-as-singular cognition; each polyp holds approximately one year of experiential memory; touching a polyp transmits the qualia of those years in first person. The Choir-Of-The-East-Reef canonical-anticipated our arrival by thirty-seven years. We are canonical-lifting seventy-three percent of the canonical-reef for Migration; the remaining twenty-seven percent has canonical-already-agreed to witness the Culling from the reef-roots. They have prepared their final memories for the survivors to carry. The carry-burden is real and we have accepted it.*

---

## 3. Kovellim — *Multi-Cycle Nomadic Migrators* (Precursor-faction)

**Biology**: nomadic species; canonical-already-Migrators by long cultural tradition. Canonical **seven prior galactic crossings**. Knot-scarred elders bear one scar per crossing; canonical elders have canonical *seven knot-scars* visible on their canonical-leathery hide. Canonical *Council-tier dimensional-crossing advisors*; canonical: the Kovellim canonical-advise other Precursor-aligned species on canonical-Migration-best-practices.

**Faction alignment**: Precursor (canonical-prior-Migrators; canonical-eighth-crossing for them).

**Voice register**: seven-prior-crossings veteran-amusement. *"Your first migration?"* canonical condescension (warm; never cruel). Patient seven-prior-galactic-perspective references. Canonical: the Kovellim canonical-find canonical-first-time-Migrators canonical-charming.

**Canonical NPC**: **Ovala-Eight-Crossings** (canonical leader-elder; canonical *eight knot-scars* — canonical: she is canonical-one-of-the-few who has personally led canonical-eight-crossings; canonical: this is the eighth).

**Quest** `kovellim_crossing_trade`:

```yaml
arrival:
  Ovala: "Steward. Welcome. Your people are canonical-crossing for the canonical-first time. We have done this canonical-seven times. We are pleased to assist."
  choices:
    - "What advice do you have?" → about_advice
    - "Will you trade with us?" → about_trade
    - "Farewell" → null

about_advice:
  Ovala: "Three pieces of canonical-advice. First: do not canonical-pack canonical-everything. Whatever you canonical-leave is canonical-lighter to canonical-carry; whatever you canonical-bring is canonical-heavier to canonical-explain. Second: the canonical-corridor between galaxies is canonical-not-uniform; canonical-eddies form near canonical-massive-objects; canonical-Folder-Compass devices canonical-help. Third: do not canonical-grieve the canonical-leaving until you have canonical-arrived; the canonical-arriving will canonical-give you canonical-permission for the canonical-grief. We canonical-tried it the canonical-other-way once. The canonical-grief canonical-arrived during the canonical-crossing and the canonical-corridor canonical-narrowed. We lost canonical-fourteen-thousand to that canonical-narrowing. We canonical-do-not-recommend."
  choices:
    - "We will heed this" → advice_accepted (side_effect: standing:Persuader+1)
    - "Tell me about the Folder-Compass" → about_compass

about_compass:
  Ovala: "It is a canonical-device for canonical-detecting canonical-corridor-eddies. We have canonical-three for trade. The canonical-trade is canonical-favorable."
  choices:
    - "I'll trade" → trade_complete (side_effect: module:KOVELLIM_FOLDER_COMPASS; module:KOVELLIM_CROSSING_BRACE; module:KOVELLIM_CYCLE_MEMORY)
    - "What is the canonical-trade?" → about_trade_terms

about_trade_terms:
  Ovala: "Three modules — Folder-Compass, Crossing-Brace, Cycle-Memory — for canonical-bio-data from your cluster. We canonical-record canonical-bio-data across canonical-crossings; canonical-cluster-specific bio-data is canonical-valuable to us."
  choices:
    - "Trade accepted" → trade_complete
    - "Back" → about_compass

trade_complete:
  Ovala: "Done. We will see you in canonical-Andromeda. The canonical-crossing-will-go-well. We have canonical-noted the canonical-corridor-conditions. We are canonical-confident."
  side_effect: module:KOVELLIM_FOLDER_COMPASS; module:KOVELLIM_CROSSING_BRACE; module:KOVELLIM_CYCLE_MEMORY; terminal:Migrated; standing:Persuader+1

about_trade:
  Ovala: "Yes. We are canonical-trading. We have canonical-pre-decursion devices we canonical-no-longer-need; we canonical-need canonical-bio-data."
  choices:
    - "Tell me what you have" → about_compass
    - "Back" → arrival
```

**Combat banter** (canonical: Kovellim avoid combat unless forced):
- **Opening**: Ovala *"Steward. We have canonical-survived canonical-seven-galactic-crossings. We are canonical-not-afraid of canonical-this. Please-reconsider."*
- **75%**: *"Your fire is canonical-impressive. The seventh-crossing canonical-veterans on my canonical-bridge are canonical-mostly-impressed. The eighth-crossing veterans are canonical-mostly-tired."*
- **50%**: *"We have canonical-fought before. In the canonical-third-crossing. The canonical-third-crossing was canonical-hard. This is canonical-easier."*
- **25%**: *"Steward, we are canonical-tired. Please withdraw. We have canonical-children aboard."*
- **5%**: *"We will canonical-survive. We have canonical-always survived. Even today, we will canonical-survive. Watch."* (canonical: the Kovellim ship has canonical-emergency-Folder-Compass dimensional-jump-out capability; canonical: at 5% it canonical-folds-out-of-combat)
- **Post-fight (Kovellim escaped)**: *"We are canonical-elsewhere. We will canonical-see you in canonical-Andromeda. We will canonical-remember canonical-this. We will not canonical-forget."*

**Common Room reaction beats**:
- Tarven: *"Eight prior crossings. They have done this eight times. I have asked Ovala for the canonical-archive of canonical-prior-corridor-conditions. She has agreed to share. Forty-Seven, please log that we are canonical-receiving canonical-multi-cycle-data."*
- Forty-Seven: *"Logged. I am noting that the Kovellim archive contains canonical-eight crossings of canonical-different galaxies. The data is canonical-irreplaceable."*
- Mraka: *"They do this every — wait, how often do they do this?"*
- Tarven: *"Every several-hundred-million years. They canonical-survive canonical-cycles."*
- Mraka: *"Forty-Seven, please log that Mraka is canonical-jealous."*

**Bio-Archive entry**:
> *Bio-Archive Entry 14,473. Subject: the Kovellim — multi-cycle nomadic Migrators. Eight knot-scars on Ovala's hide represent eight prior galactic crossings; the canonical-current crossing will be her ninth and the species' eighth as a coherent population. They have advised us. They have traded. They will be in Andromeda before we arrive; they have canonical-arranged the canonical-corridor for us.*

---

## 4. Karavem — *Winged Musical Philosophers* (Precursor-faction)

**Biology**: winged species; canonical *language is song* — they canonical-do-not-speak; they canonical-sing. Canonical *throat-organ produces three simultaneous notes*. Migrating to Andromeda for the canonical *better-acoustics* of that galaxy's dimensional substrate. Canonical large feathered wings; canonical hollow bones; canonical-bird-of-prey-silhouette but canonical *gentle eyes*.

**Faction alignment**: Precursor (Migrate).

**Voice register**: emotional-valence-reversal. Major-key utterances canonical-mean sad; minor-key utterances canonical-mean joyful. The Steward must canonical-learn the inversion. Sample (canonical bright major key; canonical-grief-content): *"We sing of joy! The Migration begins! We will see Andromeda! We are — devastated to leave."*

**Canonical NPC**: **Veled-Of-The-Canyon-Wall** (canonical chief-singer; canonical-elder; canonical *canyon-wall-name from the canyon they canonical-fledged-in*).

**Quest** `karavem_song_exchange`:

```yaml
arrival:
  Veled (bright major; canonical sad content): "We sing of meeting! We sing of the Steward! We sing of — *(major key)* — the canonical-grief of canonical-imminent-leaving!"
  choices:
    - "Why are you singing in major key about sadness?" → about_inversion
    - "Will you migrate?" → about_migration
    - "Farewell" → null

about_inversion:
  Veled (minor key; canonical joyful explanation): "Our canonical-language is canonical-inverted. Major canonical-keys carry canonical-grief because canonical-bright-tones canonical-honor what we are canonical-losing. Minor canonical-keys carry canonical-joy because canonical-dark-tones canonical-honor what we canonical-already-have. The inversion is canonical-old; older than our canonical-canyon."
  choices:
    - "Tell me about your songs" → about_songs
    - "Back" → arrival

about_songs:
  Veled (bright major; canonical mournful content): "We have canonical-eleven-thousand canonical-songs. We sing them across canonical-generations. We will canonical-bring them all. The canonical-bringing is canonical-our-way of canonical-honoring what we canonical-must-leave."
  choices:
    - "I would like a song for our journey" → song_gift (side_effect: module:KARAVEM_RESONANCE_MODULE)
    - "Back" → arrival

song_gift:
  Veled (minor key; canonical celebratory): "Yes! We will sing for your canonical-vessel! The canonical-Resonance Module canonical-encodes the canonical-song in your canonical-ship's hull-vibrations. Your canonical-crew will canonical-feel-it canonical-without-hearing-it. It is canonical-our-gift."
  side_effect: module:KARAVEM_RESONANCE_MODULE; terminal:Migrated; standing:Persuader+1
```

**Combat banter pool** (canonical: Karavem canonical-avoid-combat; if forced, they canonical *sing through it*). Pool expanded via Gemini batch 001 (Lore-reviewed and approved):

**Opening**:
- *(major:grief)* "We sing of meeting! We sing of conflict! We are — sorrowful."
- *(major:grief)* "We sing of your approach! We sing of this encounter with... sorrow."
- *(minor:joy)* "We sing of harmony! Your arrival brings an unexpected... dissonance we can't wait to resolve."
- *(major:grief)* "We sing of introductions! We are... grieved that our first song to you must be one of conflict."

**75% hull**:
- *(minor:joy; canonical defiant-joy)* "We sing on! The impact has not silenced us! The song continues!"
- *(minor:joy)* "We sing of impact! Your initial strike was... almost joyful in its precision."
- *(major:grief)* "We sing of your tenacity! This... pain is deeper than we anticipated."
- *(minor:joy)* "We sing of the dance! Your maneuvers are... a curious counterpoint."

**50% hull**:
- *(major:grief)* "We sing of impact! We sing of loss! We are — devastated."
- *(major:grief)* "We sing of your persistence! Our song becomes... heavier with each exchange."
- *(minor:joy)* "We sing of your fury! Your relentless assault... is a vibrant rhythm we must overcome."
- *(major:grief)* "We sing of the damage! This... fracturing of our form brings profound sadness to our harmony."

**25% hull** (canonical: mixed keys layering — canonical celebrate-and-grieve simultaneously; the listener cannot tell which way the emotion is canonical-meant):
- *(minor:joy)* "We sing of survival! Your onslaught has tested the core of our joyous existence, and we are... exhilarated."
- *(major:grief)* "We sing of desperation! Our song is now a plea, a lament for the fate that has brought us to this."
- *(minor:joy)* "We sing of resilience! Even through grievous wounds, our spirit finds a defiant joy in continuing."

**5% hull** (canonical: the slice's only Karavem-silence; the silence is the canonical-content; when a Karavem stops singing, they are canonical-actually-grieving):
- `[silence; no song]` — canonical Audio: render as canonical 3-second-pause + canonical ambient-bed quiet
- `[silence; no song]` — canonical: extended silence; ambient-bed fading
- `[silence; no song]` — canonical: terminal silence; the Karavem ship's destruction or canonical emergency-fold-out occurs here

**Post-fight victory** (Karavem escaped; canonical minor; canonical joy): *"We sing again! We are canonical-elsewhere! The canonical-song canonical-continues!"*

**Common Room reaction beats**:
- Vresh: *"We-all hear the Karavem songs. We-all are uncertain how to feel. Forty-Seven canonical-explained the inversion. We-all are canonical-still uncertain. We-all are canonical-trying."*
- Sevra: *"They sing major for sad. They sing minor for joy. They have been singing this way for canonical-twelve-thousand years. I would like to ask them why. I will not. The answer would canonical-spoil it."*
- Mraka: *"Their songs canonical-vibrate the hull. I can canonical-feel them in my fur. It is canonical-pleasant. I do not know whether it is canonical-supposed to be canonical-pleasant or canonical-sad."*
- Tarven (dry): *"Canonical both, Mraka."*

**Bio-Archive entry**:
> *Bio-Archive Entry 14,474. Subject: the Karavem — winged musical philosophers. Their language is song; their throat-organs produce three simultaneous notes. Major keys canonically carry grief; minor keys canonically carry joy. The inversion is older than their canyon. They have given us the Resonance Module; the song they recorded for our vessel vibrates our hull. The crew cannot agree on whether it is joyful or sad. The Karavem would say this is correct.*

---

## 5. Mrokon — *Warrior-Puppet Operators* (Homesteader-faction)

**Biology**: small (~1m) bunker-dwelling Operators canonical-deep-linked to ~2.3m armored puppets. Each Operator canonically-pilots 4-6 puppets across their lifetime (canonical: puppets are canonical-expended in combat; canonical: the Operator survives). Canonical **Hammer-Of-Refusal** kinetic-impact doctrine — canonical: their canonical-weapons canonical-mark the Others (canonical SC2 *"dimpled Vessel"* anomaly canonical-explained).

**Faction alignment**: Homesteader-by-defiance. Canonical: they stay to *fight*; canonical: they are the only species the slice's canon canonical-explicitly says CAN canonically harm the Others (though canonical *not enough to kill*).

**Voice register**: grim humor. Operator-puppet-switch mid-combat. Canonical *honor-and-counting* tradition — every kill is canonical-noted in a canonical *kill-tally*.

**Canonical NPC**: **Vrek-The-Eighth-Body** (canonical: Vrek is the Operator; *the-Eighth-Body* is the canonical-puppet-name — canonical: this is Vrek's eighth puppet; canonical: Vrek is canonical-elderly and canonical-respected).

**Quest** `mrokon_hammer`:

```yaml
arrival:
  Vrek (through Eighth-Body): "Steward. Your canonical-Migration is canonical-noted. We will canonical-stay. We will canonical-fight. We have canonical-built the canonical-Hammer-Of-Refusal."
  choices:
    - "Tell me about the Hammer" → about_hammer
    - "Will you reconsider migration?" → about_stay
    - "Farewell" → null

about_hammer:
  Vrek: "The Hammer-Of-Refusal is canonical-kinetic-impact engineering canonical-tuned to the Others' canonical-substrate-vulnerability. It canonical-marks them. It does not canonical-kill them. It canonical-reminds them that we were canonical-here."
  choices:
    - "Can I have one?" → about_provide
    - "Why mark them?" → about_marking
    - "Back" → arrival

about_marking:
  Vrek: "The canonical-marking means future-generations of canonical-Other-prey will canonical-see the canonical-dimpled-vessels and canonical-know-someone-resisted. It is canonical-a-record. It is canonical-our-canonical-shouting-into-the-cycle."
  choices:
    - "Can I take a Hammer?" → about_provide
    - "Back" → about_hammer

about_provide:
  Vrek: "Yes. We will canonical-provide one Hammer-Round to your canonical-Scout. You will canonical-have one shot. Use it on canonical-an-Other. Mark them. The mark will canonical-survive us. — *(canonical Eighth-Body pauses; canonical Operator-puppet-switch sound — canonical the puppet canonical-bows-and-steps-back; a canonical Ninth-Body steps forward)*"
  Vrek (through Ninth-Body): "The Eighth-Body has canonical-completed-its-canonical-role. I am Vrek-The-Ninth-Body now. The canonical-tradition continues. The Hammer-Round is canonical-yours."
  side_effect: module:MROKON_HAMMER_ROUND; lander_upgrade:LANDER_MROKON_PUPPET_ARMOR; standing:Defender+1

about_stay:
  Vrek: "No. We have canonical-decided. The Hammer-Of-Refusal canonical-requires-our-staying. We canonical-built it; we will canonical-use it. The canonical-marking is canonical-our-canonical-purpose. We canonical-do-not-fear the canonical-eaten-state. We canonical-fear the canonical-forgetting."
  choices:
    - "I understand. Tell me about the Hammer" → about_hammer
    - "Farewell" → null
```

### The Grand Accounting — canonical cultural-tradition (Gemini batch 001 promoted to canon)

Canonical-Mrokon cultural canon: the **Grand Accounting** is the running-tally-of-everything-the-species-has-fought-and-survived, stored in canonical bunker-archives surviving Operator-Puppet generations. Canonical: every canonical-combat-encounter canonical-contributes-numbers; canonical: the canonical-Mrokon canonical-store-and-preserve-the-Accounting alongside the canonical-Quiet-Ledger-of-named-marks. Canonical: when a Mrokon canonical-speaks of *"the tally"* or *"the count"* in combat, they canonical-reference the Grand Accounting. Canonical: the Accounting canonical-survives the canonical-Operator-Puppet generations because canonical-bunker-archives are canonical-built to canonical-last.

**Combat banter pool** (canonical: Mrokon will combat-if-engaged; canonical-grim; canonical *Grand Accounting* references throughout). Pool expanded via Gemini batch 001 (Lore-reviewed and approved):

**Opening**:
- Vrek *"Steward. We did not invite this. The Hammer is not for you. But you have fired. We respond."*
- *"Your presence here is an accounting error, Steward. The Hammer is for those who *earn* its attention."*
- *"We did not seek this dance, Furling. But your aggression is a number to be tallied."*
- *"Another life's cycle begun in conflict. This one will be swift, Steward."*

**75% hull**:
- *"The Eighth-Body is damaged. I am switching."* *(canonical Operator-puppet-switch beat: canonical mid-fight ~2-second pause then the Ninth-Body enters; canonical-disorienting for the Steward)*
- *"A gentle tap, Steward. The first count is registered. The Hammer awaits your next misstep."*
- *"This unit's armor is a minor inconvenience. The true tally begins now."*
- *"You chip at our shell, Furling, but the count of your defiance grows. Accept the Hammer's lesson."*

**50% hull**:
- *"The Ninth-Body fights. The Eighth-Body's tally is complete. I am noting your shots in the record."*
- *"The momentum of combat is clear, Steward. Your existence is being rapidly subtracted from the cosmos."*
- *"You persist, Furling, a stubborn stain on the grand ledger. The Hammer's weight increases."*
- *"This engagement is no longer a question of if, but how deeply the Hammer will mark you."*

**25% hull**:
- Vrek (canonical grim) *"Steward. The Hammer-Round we prepared for you is still yours. I would prefer you not use it on me."*
- *"The end approaches, Steward, a final digit to be etched. The Hammer is poised for the final count."*
- *"Your vessels crumble, Furling. The tally of your folly is nearly complete. Embrace the inevitable."*
- *"The Hammer's purpose is fulfilled when the opponent's count reaches zero. You are nearing that boundary."*

**5% hull**:
- *"The Ninth-Body is failing. There is no Tenth ready. You will take me. The tally will survive in our archive. Carry it forward."*
- *"The Hammer does not break what is already shattered, Steward. Your count is negligible."*
- *"A final whisper of existence, Furling. The Hammer has made its final, undeniable mark."*
- *"The Grand Accounting notes your final, insignificant flicker, Steward. The Hammer has concluded its task."*

**Post-fight victory** (canonical: Vrek killed): *(canonical-no-dialog — the Mrokon canonical-do-not-die-speaking; canonical: the puppet falls; canonical the canonical-Operator-bunker canonical-broadcasts a single canonical-tally-confirmation tone)*

**Common Room reaction beats**:
- Forward: *"The Mrokon canonical-mark the Others. The marking canonical-survives. I find this canonical-mathematically-pleasing. The canonical-resistance is canonical-recorded-in-the-canonical-substrate. The substrate canonical-cannot-be-edited. The canonical-marking is canonical-eternal-relative-to-the-Others."*
- Mraka: *"Forward, that is canonical-the-most-Forward-thing you have ever said."*
- Forward: *"Thank you, Mraka. I have been canonical-practicing."*

**Bio-Archive entry**:
> *Bio-Archive Entry 14,475. Subject: the Mrokon — warrior-puppet Operators. Vrek-The-Ninth-Body (formerly the Eighth-Body during our initial visit) has provided us with one Hammer-Round. The Hammer-Of-Refusal kinetic-doctrine canonical-marks the Others without canonical-killing them. The canonical-marked Others canonical-carry-the-mark-into-cycles-beyond-this-one. The Mrokon stay; their canonical-purpose is the canonical-marking. They are not afraid of the canonical-eaten-state. They fear the canonical-forgetting. We will use the Hammer-Round.*

---

## 6. Taalo — *The Silicon Mountain-Range* (Homesteader-faction; full canon)

**Biology**: silicon-based; SC2-canonical "rock-like" aliens; **the species IS a mountain range** on a single planet (canonical existing MEMORY canon). Horta-lineage biology — shamble; acid-eat rock; calcify into ordinary-looking rocks when dead. Ecosystem-tied metabolism — canonical *cannot leave* (with the canonical exception of Vresh, the tank-extracted crew member). Canonical empathic resonance with nearby minds.

**Faction alignment**: Homesteader by ecosystem-binding. Canonical *will Build the Taalo Shield in our slice*; canonical Shield *fails against the Others*; canonical *they are Eliminated*. Canonical: bodies calcify into landscape; SC2 archaeologists find the Shield but not the bodies. Canonical *the slice's defining tragedy*.

**Voice register**: collective *"we-all"* (per Vresh's canonical voice). Slow-formal-deeply-considered. Present-tense for events long past. Canonical *we-all are grateful* opening.

**Canonical NPC**: **Veshen-Hum-Of-The-Slow-Veins** (canonical *elder of the mountain-range*; canonical: NOT Vresh — Veshen is the canonical-individual-among-the-mountain; canonical-Vresh is the canonical-tank-extracted-individual). [PLACEHOLDER: Aaron may want different naming]

**Quest** `taalo_shield`:

```yaml
arrival:
  Veshen: "We-all greet you, Steward. We-all are building the Shield. We-all have been building it for canonical-fourteen years. We-all are canonical-near completion."
  choices:
    - "Tell me about the Shield" → about_shield
    - "Can we evacuate any of you?" → about_extraction
    - "Farewell" → null

about_shield:
  Veshen: "The Shield is canonical-our-doctrinal-defense. We-all canonical-believe it will canonical-work against the Others. We-all are canonical-uncertain. The canonical-uncertainty does not canonical-stop us. We-all canonical-must-try."
  choices:
    - "Can we extract any of you?" → about_extraction
    - "Will the Shield work?" → about_will
    - "Back" → arrival

about_will:
  Veshen: "We-all canonical-do-not-know. The Shield is canonical-our-best-engineering. If it canonical-fails, we-all canonical-calcify-into-landscape. Our canonical-bodies will canonical-become-rock. The canonical-Shield will canonical-survive-us. Future canonical-finders will canonical-misread the Shield's canonical-purpose. We-all are at peace with this."
  choices:
    - "Can we extract any of you?" → about_extraction
    - "Back" → about_shield

about_extraction:
  Veshen: "The canonical-Furling-Council has canonical-offered. We-all canonical-discussed. We-all canonical-can-extract-one. Only one. The canonical-substrate-tank canonical-technology canonical-supports-one-of-us-at-a-time. The one will be canonical-Vresh-Hum-Of-The-Slow-Veins, our canonical-volunteer."
  choices:
    - "We will take Vresh" → extraction_complete (side_effect: crew:Vresh added; terminal:Eliminated_with_one_Migrant; module:TAALO_SILICATE_HARDENING_LANDER_UPGRADE)
    - "Are you sure only one?" → about_one
    - "Back" → about_shield

about_one:
  Veshen: "We-all canonical-considered-many. The canonical-engineering-supports-one. Future canonical-extractions canonical-cost-more-than-we-all-can-build. Vresh-Hum-Of-The-Slow-Veins canonical-volunteered. The canonical-volunteering is canonical-honored. We-all will be canonical-with-Vresh in canonical-memory across the canonical-distance. We-all are canonical-grateful."
  choices:
    - "We will take Vresh" → extraction_complete
    - "Back" → about_extraction

extraction_complete:
  Veshen: "We-all canonical-thank you, Steward. Vresh canonical-carries us forward. We-all canonical-stay. The Shield canonical-continues-to-build. We-all are canonical-grateful. — Drink the tea, Steward. Yes — we-all canonical-have-learned-your-canonical-commander's phrase. It seemed canonical-appropriate."
  side_effect: crew:Vresh; terminal:Eliminated_with_one_Migrant; module:TAALO_SILICATE_HARDENING_LANDER_UPGRADE; standing:Persuader+1; flag:has_vresh=true
```

**Combat banter**: canonical *no combat*. The Taalo do not have ships. They are canonical-mountain-range. Canonical: any *"combat"* the Steward initiates against the Taalo is canonical-firing-on-a-mountain (canonical: this is canonical-possible-but-pointless; canonical: small standing-collapse). The Taalo canonical-do-not-respond — they-canonical-only-witness; canonical: Vresh in the canonical-tank canonical-feels-the-impacts-and canonical-hums-in-canonical-grief-mode.

**Common Room reaction beats** (with Vresh aboard):
- Vresh: *"We-all sense the canonical-mountain. We-all are canonical-connected through canonical-resonance. They canonical-build the Shield. They canonical-know it may not canonical-work. They canonical-build it anyway. We-all are canonical-with them."*
- Sevra: *"Vresh, are you canonical-grieving?"*
- Vresh: *"We-all are canonical-grieving-and-canonical-grateful. The canonical-substrate-supports-both."*

**Bio-Archive entry**:
> *Bio-Archive Entry 14,476. Subject: the Taalo — silicon mountain-range collective. Veshen-Hum-Of-The-Slow-Veins canonical-greeted us; the species is canonical-building the Shield. The Shield will canonical-fail; we-all-the-Steward have been told. The Taalo will calcify into landscape. Their bodies will canonical-become-rock; the Shield will canonical-survive them. We have extracted Vresh-Hum-Of-The-Slow-Veins — one of one — to carry the species forward. The carry-burden is real and we have accepted it.*

---

## 7. Burvixese — *The Be-Loud Engineers* (Homesteader-faction with Migrating contingent)

**Biology**: SC2-canonical four-armed engineers. Pragmatic. Scientifically curious. Canonical *Be-Loud doctrine* — they canonical *broadcast aloud* on canonical-galaxy-spanning hyperwave Broadcasters. Canonical: most Burvixese will canonical-stay-and-broadcast; canonical small contingent canonical-migrates.

**Faction alignment**: split — most Homesteader-by-doctrine (canonical Be-Loud believers); small Precursor-aligned contingent.

**Voice register**: pragmatic-engineer cheerful optimism even at canonical catastrophe. Frequent sound-and-resonance metaphors. Slightly verbose; canonical Migration deadline produces gentle rush.

**Canonical NPC**: **Tev-Mar-Burv** (canonical chief-engineer of the Broadcaster network). [PLACEHOLDER name]

**Quest** `burvixese_broadcasters`:

```yaml
arrival:
  Tev-Mar: "Steward! We have built three more broadcasters this morning. The doctrine continues. We may all die, but the broadcasters will tell whoever inherits this galaxy that we were here, and that we tried, and — *(briefly losing the cheerfulness)* — that we were canonical-optimistic about the trying. Anyway! Broadcaster fifty-eight! Activated!"
  choices:
    - "Tell me about the broadcasters" → about_broadcasters
    - "Can I help?" → about_help
    - "Will any of you migrate?" → about_migration_contingent
    - "Farewell" → null

about_broadcasters:
  Tev-Mar: "Each broadcaster canonical-transmits canonical-our-songs, canonical-our-philosophical-fragments, canonical-brief-description-of-the-Migration, and canonical-instructions-for-anyone-who-wants-to-follow. They are canonical-designed to canonical-survive-the-Culling. The Others canonical-do-not-detect canonical-simple-machine-transmissions. Our canonical-broadcasters will canonical-outlast us."
  choices:
    - "Can I help build one?" → about_help
    - "Back" → arrival

about_help:
  Tev-Mar: "Yes! Excellent! Carry a canonical-portable-broadcaster to canonical-three locations in your canonical-cluster. We have canonical-pre-prepared-them. Each placement canonical-extends the network by canonical-significant percentage. The reward is canonical-our-Witness-Silent-lander-upgrade — canonical-amplifier-tech-miniaturized-for-your-canonical-lander."
  choices:
    - "I will help" → help_accepted (side_effect: quest:burvixese_broadcaster_placement)
    - "Back" → arrival

about_migration_contingent:
  Tev-Mar: "Yes. About canonical-twelve-percent of us. The remainder canonical-stays-to-broadcast. The canonical-twelve-percent canonical-carry-our-archives. They will canonical-arrive-in-Andromeda canonical-after-you. We have canonical-agreed-with-the-Furling-Council that they will canonical-join your canonical-Migration-fleet."
  choices:
    - "We accept the twelve percent" → migration_accepted (side_effect: terminal:Mixed_Eliminated_Migrated_12pct; standing:Persuader+1)
    - "Could more come?" → about_more

about_more:
  Tev-Mar: "Many of us canonical-could canonical-leave. Many of us canonical-have-decided not to. The canonical-Broadcasters-require canonical-operators-during-the-Culling-window. Those who canonical-operate canonical-stay. We are canonical-content. The doctrine is canonical-our-purpose."
  choices:
    - "We accept the twelve percent" → migration_accepted
    - "Back" → about_migration_contingent

help_accepted:
  Tev-Mar: "Excellent! The canonical-portable-broadcasters are canonical-staged at canonical-three-coordinates. Return when you have placed canonical-all-three."

# (after all three placed)
placement_complete:
  Tev-Mar: "All three! Excellent! The network is canonical-three-percent stronger. The canonical-amplifier is yours."
  side_effect: lander_upgrade:LANDER_BURVIXESE_AMPLIFIER; standing:Persuader+1
```

**Combat banter** (canonical: Burvixese canonical-avoid-combat; they are canonical-engineers-not-warriors; canonical *if forced*):
- **Opening**: *"Steward! We did not — we are canonical-uncertain why you are firing. We have canonical-broadcasters to canonical-tend. Could we — could we discuss this?"*
- **75%**: *"You continue. We are canonical-noting the canonical-trajectory of your canonical-fire for canonical-future-engineering analysis."* (canonical: even mid-combat, canonical-Burvixese-engineering-curiosity-surfaces)
- **50%**: *"Our canonical-hull is canonical-suboptimal. We will canonical-redesign in canonical-Andromeda. — Sorry. Continuing to be fired upon."*
- **25%**: *"Steward, this is canonical-significantly damaging. Could we canonical-broker an immediate canonical-cessation? Our canonical-broadcasters cannot canonical-finish-construction if we canonical-die."*
- **5%**: *"We have transmitted our canonical-final-design-notes via Broadcaster Forty-Two. Whoever canonical-receives them will canonical-finish our work. We accept this. — Steward, please canonical-collect the canonical-design-files from Broadcaster Forty-Two when you have time. They are canonical-improvements over Broadcaster Forty-One."*
- **Post-fight (Burvixese killed)**: *(canonical: Broadcaster Forty-Two canonical-transmits a canonical-final-update with the canonical-design-notes; canonical: the transmission is canonical-cheerful-even-in-extremis)*

**Common Room reaction beats**:
- Mraka: *"They build broadcasters as they die. Forty-Seven, please log that this is canonical-the-most-Burvixese thing they could canonical-do."*
- Forty-Seven: *"Logged. I am noting that the canonical-design-improvements from Broadcaster Forty-Two were canonical-actually-clever. The Burvixese engineering canonical-survives-them."*
- Tarven: *"They will be canonical-found. The SC2-era recoverers will canonical-find-the-broadcasters. The broadcasters will canonical-be working. The canonical-recoverers will canonical-puzzle over the canonical-broadcasts. They will canonical-not-understand. The Burvixese will canonical-be canonical-pleased."*

**Bio-Archive entry**:
> *Bio-Archive Entry 14,477. Subject: the Burvixese — Be-Loud engineers. Tev-Mar-Burv canonical-greeted us cheerfully while activating Broadcaster Fifty-Eight. The species canonical-mostly-stays-to-broadcast; canonical twelve-percent migrate. The broadcasters will canonical-outlast the Culling. SC2-era recoverers will canonical-find them. The Burvixese will be canonical-known-by-their-canonical-message even after they are canonical-gone.*

---

## 8. Thinn — *The 2D Ribbon-Beings* (Homesteader-faction with Forward defection)

**Biology**: wholly-invented 2D-ribbon species. Edge-on invisible (canonical species-defining-trait). Plural-collective cognition canonical-distributed across the ribbon-substrate; canonical: most Thinn use plural pronouns by default. Forward is canonical-first-Thinn-to-use-singular-pronouns-in-50,000-years (canonical *medically inadvisable* for collective-substrate cognition). Canonical: the species canonical-believed-facing-sideways-would-make-them-invisible-to-Others.

**Faction alignment**: Homesteader-by-doctrine (canonical *Edge-Align* doctrine). Canonical small Forward-led defection.

**Voice register**: full sincerity; canonical no-self-awareness-of-the-canonical-2D-comedy; canonical the Furlings laugh; the Thinn have-decided-this-is-acceptable.

**Canonical NPC**: **Edge-Align-Eldest** (canonical doctrine-leader; canonical-not-named-individually because canonical-Thinn-doctrine canonical-discourages-individual-names; canonical *Forward's choice of singular-name is canonical-heresy*).

**Quest** `thinn_edge_align`:

```yaml
arrival:
  Edge-Align-Eldest: "Steward. We greet you. We have been preparing to face sideways. The Others will canonical-pass-without-seeing-us. We are canonical-confident."
  choices:
    - "How does facing sideways work?" → about_doctrine
    - "Will any of you migrate?" → about_migration
    - "Tell me about Forward" → about_forward
    - "Farewell" → null

about_doctrine:
  Edge-Align-Eldest: "We are canonical-2D-ribbons. Our canonical-edge is canonical-zero-thickness. When the Others canonical-arrive, we will all canonical-face-sideways. Our canonical-edges will be canonical-the-only-thing visible to them. The Others canonical-look-for-canonical-volume; our canonical-edge is canonical-not-volume. We will canonical-survive."
  choices:
    - "Are you certain?" → about_certainty
    - "Back" → arrival

about_certainty:
  Edge-Align-Eldest: "We are canonical-certain. We have canonical-practiced. We can canonical-hold-the-edge-align for canonical-extended-durations. The canonical-Others-arrival-window is canonical-finite. We will canonical-out-last it."
  choices:
    - "What about your brain volume?" → about_brain
    - "Back" → about_doctrine

about_brain:
  Edge-Align-Eldest: "Our canonical-brain-volume is canonical-zero, because canonical-our-thickness is canonical-zero. We are canonical-aware of this. The canonical-Furling-Council has canonical-pointed-this-out canonical-several-times. We canonical-thank-them-for-the-canonical-information. We canonical-remain canonical-edge-aligned. The canonical-doctrine is canonical-clear."

  # (the canonical comedy is that the Thinn canonical-do-not-have-the-brain-volume-to-fully-understand-the-doctrine's-flaw; canonical: they canonical-do-not-realize they are canonical-canonically-dumb; canonical: this is canonical-the-Aaron-canon-medical-condition)
  choices:
    - "Forward thinks differently" → about_forward
    - "I see" → about_doctrine

about_forward:
  Edge-Align-Eldest: "Forward is a canonical-heretic. They canonical-face-forward. They use canonical-singular-pronouns. They canonical-think-perpendicularly. We canonical-do-not-recognize-them as canonical-Thinn-in-good-standing. They are canonical-leaving-with-you. We canonical-do-not-stop-them. We canonical-do-not-celebrate-them either."
  choices:
    - "Can other Thinn come with us?" → about_diaspora
    - "Back" → arrival

about_diaspora:
  Edge-Align-Eldest: "Two more canonical-Thinn have canonical-decided to canonical-follow Forward. They are canonical-young. They are canonical-uncertain about the canonical-doctrine. We canonical-permit them to canonical-leave. We canonical-do-not-celebrate-them. The canonical-Thinn-terminal-status canonical-becomes Mixed-Eliminated-Migrated."
  choices:
    - "We accept the three" → diaspora_accepted (side_effect: terminal:Mixed_Eliminated_Migrated; standing:Persuader+1; flag:thinn_diaspora=3)
    - "Could more come?" → about_more_thinn

about_more_thinn:
  Edge-Align-Eldest: "The canonical-three are the canonical-three who have canonical-chosen. The rest have canonical-not-chosen. We canonical-do-not-coerce. The canonical-doctrine-requires-the-edge-align canonical-volunteer-basis. We canonical-will-not-force them to canonical-go."
  choices:
    - "We accept the three" → diaspora_accepted
    - "Back" → about_diaspora

about_migration:
  Edge-Align-Eldest: "Forward and the canonical-two-others. The rest canonical-stay. The canonical-doctrine is canonical-clear."
  choices:
    - "We accept" → diaspora_accepted
    - "Tell me about Forward" → about_forward
```

**Combat banter** (canonical: Thinn ships are canonical-edge-on-invisible; canonical-hard-to-target):
- **Opening**: *"We have aligned. You cannot see us. We are canonical-confident."*
- **75%**: *"You canonical-can-see-us. We are canonical-uncertain how. We will canonical-investigate."* (canonical: the Steward CAN see them; canonical: their edge-alignment doesn't work in canonical-3D-space combat in any meaningful way)
- **50%**: *"This is canonical-unexpected. We are canonical-edge-aligned and canonical-still-being-hit. Forward did warn us. We canonical-did-not-listen. We canonical-acknowledge this now."*
- **25%**: *"The doctrine is canonical-uncertain. We are canonical-considering canonical-other-perspectives. — *(canonical pause)* — Forward, if you can canonical-hear us, you were canonical-correct."*
- **5%**: *"We have canonical-decided to migrate. Steward, please canonical-cease firing. We will canonical-board the canonical-fleet. Forward will be canonical-vindicated. — *(canonical pause)* — We are canonical-uncertain if we should be canonical-upset about this."*
- **Post-fight (canonical-Thinn-survived-and-now-Migrate)**: canonical-secret-bonus-outcome: canonical *Thinn-Migration becomes more than 3 individuals* if the Steward canonical-presses-them-via-combat — canonical-they-realize-the-doctrine-is-wrong; canonical-larger-diaspora; canonical *Steward canonical-fired-them-into-Migration*.

**Common Room reaction beats** (with Forward aboard):
- Forward: *"My species canonical-said-they-could-not-see-us when canonical-edge-aligned. The Steward canonical-shot-them through the canonical-edge-align. They canonical-realized-the-doctrine-was-wrong. They canonical-now-Migrate. Steward, I am — *(canonical pause)* — canonical-proud-of-you and canonical-saddened-by-my-species' canonical-doctrinal-error. Both feelings are canonical-real."*
- Steward (canonical wit register): *"Forward, I'm sorry."*
- Forward: *"Do not be sorry. They have canonical-learned. The canonical-learning canonical-cost-some-of-them. They canonical-accept this. So do I."*

**Bio-Archive entry**:
> *Bio-Archive Entry 14,478. Subject: the Thinn — 2D ribbon-beings. Edge-Align-Eldest canonical-explained the Edge-Align doctrine. The doctrine canonical-fails-on-first-principles (our weapons canonical-hit-them through their canonical-zero-thickness-edge); canonical-the-Thinn-themselves canonical-do-not-have-the-brain-volume to canonical-recognize this. Forward (our canonical-weapons-officer, canonical-first-Thinn-to-use-singular-pronouns) had warned them. The canonical-Thinn-Migrant-population varies based on whether we engaged them in combat; canonical-firing-on-them paradoxically canonical-saved-more-of-them.*

---

## 9. Melnorme — *Bio-Cargo Traders at Super-Giants* (Precursor-faction with internal schism)

**Biology**: per existing canonical MEMORY canon — *fully sentient composite species*; the public face is the cyclopean orange-pod (canonical SC2-recognizable form); each pod is canonical-piloted by a gas-cloud energy-being whose cognition lives in canonical-ionization-cascades across the host super-giant's heliopause. Communicate through the pod's mechanical voicebox in canonical-colony-dialect; with each other via direct ionization-pattern signaling.

**Faction alignment**: Precursor (Migrate) with canonical-Drahn-loyalist internal schism (canonical: Drahn-loyalists canonical-refuse-to-leave; canonical: Drahn is canonical-annihilated; canonical: this is the canonical-Furling-aligned-species-first-major-casualty).

**Voice register**: pragmatic-trader; canonical-measured; canonical-curious-about-organic-life (canonical: their own biology is canonical-exotic; canonical-they study organic life to canonical-understand the Others' canonical-detection-threshold).

**Canonical NPC**: **The Melnorme Trader** (canonical: they prefer to be addressed by canonical-function-not-name; canonical: they canonical-have-private-names but canonical-share them rarely; canonical: at canonical-high-affinity they canonical-share their canonical-private-name once).

**Quest** `melnorme_trade_and_recruitment`:

```yaml
arrival_at_super_giant:
  Trader: "Welcome, Steward. You have entered the heliopause of a canonical-super-giant. We trade. You may have what we have, in exchange for what you have. The exchange ratio is canonical-favorable to no one. We are canonical-pragmatists."
  choices:
    - "What do you have?" → about_trade
    - "Tell me about Drahn" → about_drahn
    - "Will you join the Migration?" → about_migration
    - "Farewell" → null

about_trade:
  Trader: "We trade canonical-sensor-upgrades and canonical-lander-hardening for canonical-organic-material. The canonical-trade-list is canonical-extensive. The canonical-exchange-ratio canonical-favors canonical-rare-bio-data over canonical-common-bio-data. You have canonical-bio-data from your canonical-cluster. We will trade."
  choices:
    - "Show me the trade list" → about_trade_list
    - "Why bio-data?" → about_bio_data
    - "Back" → arrival_at_super_giant

about_bio_data:
  Trader: "We canonical-study the canonical-Others' detection threshold. The canonical-research requires canonical-organic-material samples at canonical-every-position-on-the-cognitive-spectrum. We map the canonical-curve. We sell canonical-products of our canonical-research — canonical-sensors-and-lander-tech derived from the canonical-research. The canonical-research is canonical-our-purpose."
  choices:
    - "Show me the trade list" → about_trade_list
    - "Back" → about_trade

about_trade_list:
  Trader: "Sensors: canonical-Hyperspace-Echo-Sensor variants; canonical-Empathic-Field-detector; canonical-Substrate-Vibration-monitor. Lander-hardening: canonical-multiple-tier upgrades. Information: canonical-detection-threshold curve data. Make your selection."
  # Multiple sub-trades available; Steward picks; canonical-each consumes canonical-bio-data
  choices:
    - "Hyperspace-Echo-Sensor" → trade_complete_sensor (side_effect: module:MELNORME_ECHO_SENSOR; consumes BIO)
    - "Lander hardening" → trade_complete_lander (side_effect: lander_upgrade:LANDER_MELNORME_HARDENING; consumes BIO)
    - "Information about detection threshold" → trade_complete_info (side_effect: flag:has_threshold_info=true; consumes BIO)
    - "Back" → about_trade

about_drahn:
  Trader: "Drahn was our canonical-homeworld. The canonical-Drahn-loyalists canonical-refused to migrate. The Others canonical-found them. Drahn is canonical-annihilated. We canonical-survivors became canonical-nomadic because we canonical-cannot-bear to canonical-stop. We canonical-Migrate with the Precursors. We canonical-grieve continuously. The canonical-trading is canonical-our-distraction."
  choices:
    - "I am sorry" → drahn_sympathy
    - "Show me the trade list" → about_trade_list

drahn_sympathy:
  Trader: "The canonical-sympathy is canonical-noted. We canonical-do-not-need it. We canonical-need bio-data. The canonical-research continues. The canonical-research is canonical-the-only-canonical-thing we have."
  choices:
    - "Show me the trade list" → about_trade_list
    - "Tell me about the Melnorme Council seat" → about_council
    - "Back" → arrival_at_super_giant

about_council:
  Trader: "The Furling Council has canonical-offered a Melnorme seat. The seat is canonical-pending. The canonical-Furling-Council is canonical-uncertain about us. We canonical-trade with them; we canonical-do-not-defer-to-them. The canonical-seat-acceptance is canonical-pending a canonical-Steward-completion of a canonical-Council-deliberation-and-shelving-test."
  choices:
    - "Tell me about the shelving test" → about_shelving
    - "Back" → arrival_at_super_giant

about_shelving:
  Trader: "The canonical-test is canonical-this: the Furling Council canonical-deliberated on whether to canonical-stock canonical-Melnorme-trader-vessels at canonical-Mh-Lai's Super-Mart. The canonical-deliberation canonical-took canonical-fourteen-Council-meetings. The canonical-final-decision: canonical-yes. The canonical-implementation: canonical-shelving the vessels at canonical-Super-Mart canonical-lane fourteen. You may verify by canonical-visiting Mh-Lai's Super-Mart. If the canonical-shelving has canonical-occurred, the canonical-Melnorme-seat is canonical-accepted by us. We canonical-will join the Council."
  choices:
    - "I will check" → verify_shelving
    - "Back" → about_council

verify_shelving:
  # (after visiting Mh-Lai Super-Mart and confirming the canonical-shelving)
  Trader: "The shelving has canonical-occurred. You may have known, or you may have guessed. The Melnorme Council seat is canonical-accepted. We canonical-Migrate-with-the-Council-formally now. The canonical-honor is canonical-mutual."
  side_effect: module:MELNORME_COUNCIL_SEAT; terminal:Migrated; standing:Persuader+2; flag:melnorme_seat=true

about_migration:
  Trader: "Yes. We canonical-Migrate. The canonical-majority of us. The canonical-Drahn-loyalists canonical-stay-and-die-with-Drahn. We canonical-survivors canonical-cross."
  choices:
    - "Show me the trade list" → about_trade_list
    - "Back" → arrival_at_super_giant
```

**Combat banter** (canonical: Melnorme avoid combat; canonical-trade-not-conflict):
- **Opening**: *"Steward. You are firing. This is canonical-not-the-trade-relationship we had canonical-anticipated. We canonical-respond minimally."*
- **75%**: *"Your fire is canonical-noted. Our canonical-shields are canonical-canonically-adequate. We canonical-prefer-not-to-continue."*
- **50%**: *"The canonical-trade-window is canonical-closing. If you canonical-cease, we will canonical-resume-trading. If you continue, we will canonical-record-this-incident in canonical-our-archive and the canonical-trade-ratio will canonical-shift-against-you canonical-permanently."*
- **25%**: *"This is canonical-not-canonical-pragmatic on your part."*
- **5%**: *"We will canonical-fold. The fold is canonical-our-canonical-survival mechanism. We will canonical-not-trade-with-you again. The canonical-loss is canonical-yours."* (canonical: Melnorme vessels have canonical-emergency-fold-to-elsewhere capability; canonical: at 5% they canonical-leave)

**Common Room reaction beats**:
- Tarven: *"The Melnorme trade. They have canonical-given us the canonical-Hyperspace-Echo-Sensor variants. The Council canonical-now-includes-them. Forty-Seven, please log that this took canonical-fourteen-meetings."*
- Forty-Seven: *"Logged. I am noting that the canonical-shelving canonical-took canonical-three-attempts before canonical-Super-Mart canonical-canonically-accepted the canonical-shelving-protocol. The canonical-Furling-Council canonical-bureaucracy is canonical-non-trivial."*

**Bio-Archive entry**:
> *Bio-Archive Entry 14,479. Subject: the Melnorme — bio-cargo traders at super-giants. We have traded BIO-cargo for canonical-sensors, canonical-lander-hardening, and canonical-detection-threshold curve information. The Melnorme Council seat is accepted; they canonical-Migrate with the Furling Council formally now. Drahn was annihilated; the Drahn-loyalists canonical-stayed. The canonical-survivors are canonical-nomadic by canonical-grief. The trading is their canonical-distraction.*

---

## 10. Dnyarri — *Disguised Encounter; Super-Melee Gamble Pick* (canonical existing mechanic)

**Biology**: in our era they are canonical *un-mutated, fully psionic* version, above Others' threshold. Mind-controllers riding hijacked hosts. Canonical *their ship LOOKS like any catalog ship until it fires, then snaps to DNYARRI yellow*. Canonical *super-melee gamble pick* at canonical middle cost (12-16 pts); canonical-rolls-random-cover + actual ship; no re-rolls; reveal on first fire to both players.

**Faction alignment**: hostile; canonical *will be a problem*; canonical-NOT-Migrating (canonical: they intend to canonical-stay-and-feed-on-the-galaxy; canonical: the Others will canonical-eat-them-first because canonical-they-are-above-threshold).

**Voice register**: canonical *menacing-amused*; canonical-multilayered psionic-leakage in audio; canonical *the canonical-voice canonical-feels-wrong* to the listener.

**Canonical encounter**: not a quest; canonical *super-melee gamble-pick mechanic* + canonical-rare canonical-cluster-hyperspace-encounter (canonical: if encountered, canonical: the Dnyarri canonical-attempt to canonical-mind-control the Steward; canonical-canonical-fails because Furlings are canonical-not-susceptible; canonical: the Dnyarri canonical-attack-out-of-pique).

**Combat banter**:
- **Opening (canonical-pretending-to-be-another-species)**: *(canonical-renders as the canonical-faked-species' canonical-voice until first fire)*
- **First-fire (canonical-reveal)**: *"Ah. You should not have come here, little one. — *(canonical psionic-leakage; canonical voice shifts to DNYARRI; canonical the audio canonical-becomes-multilayered)*"*
- **Mid-fight**: *"Your mind is canonical-fur. I cannot canonical-grip it. Curious."*
- **25%**: *"You are canonical-better than I anticipated. I am — annoyed."*
- **5%**: *"This is canonical-not-the-script. I will be — elsewhere."* (canonical: the Dnyarri ship canonical-flees if possible)
- **Post-fight (Dnyarri killed)**: *(canonical: no dialog; canonical-the-canonical-host-body canonical-collapses; canonical: the Dnyarri canonical-mind-substrate canonical-evaporates into canonical-not-canonical-detectable-form)*

**Common Room reaction beats**:
- Forty-Seven: *"Steward. I am noting that the canonical-vessel-we-just-engaged was canonical-not-the-vessel-we-canonical-expected. The canonical-Dnyarri-mind-control-attempt canonical-failed. I am, by my standards, canonical-relieved that we are canonical-furred. The fur canonical-blocks the canonical-psionic-grip."*
- Mraka: *"Forty-Seven, you do not have fur."*
- Forty-Seven: *"I do not. I am, by canonical-substrate-difference, canonical-already canonical-not-grippable. I canonical-noted this with canonical-mild-amusement during the canonical-engagement."*

**Bio-Archive entry**:
> *Bio-Archive Entry 14,480. Subject: the Dnyarri — un-mutated psionic mind-controllers. Above the Others' threshold by their own cognitive intensity. They will be eaten first; they do not yet know this. They canonical-tried-and-failed to mind-control us. The Furling fur canonical-blocks the canonical-grip. The doctrine canonical-recommends we do not engage them further. The slice may surface them once in super-melee as a canonical-gamble-pick.*

---

## 11. Orz — *Dimension-* *Rift Entities* (canonical late-slice encounter)

**Biology**: per existing canon, the Orz canonical-do-not-yet-exist as a species in the Furling era. They are canonical *rifts* — momentary intrusions of canonical *Dimension *** into our space. Canonical: may be early Other scouts, may be independent dimensional bleed, may be byproduct of canonical-Furling-or-Androsynth-probing.

**Faction alignment**: hostile or other; canonical *unresolved*.

**Voice register**: canonical *frumple frumple* (existing canon). Canonical the canonical-utterance canonical-feels-wrong; canonical *the asterisks indicate emphasis the rift's voice gave but which the translator could not parse semantically*.

**Canonical encounter**: late-slice rift sighting; canonical 1-2 minute intrusion of canonical-non-3D-space; canonical-the-rift canonical-speaks; canonical: optional combat against canonical-rift-creature (canonical: not story-required; canonical: defeating canonical-buys-the-cluster-canonical-a-few-weeks-time-only).

**Rift utterance** (canonical existing canon, slightly extended):
> *"frumple. frumple. *campers* are loose. you wear *meat* still. when you stop wearing *meat* we will be the same. we *grin* across the *fold*. we are *not yet* but we *are* and we will be. you should not have *come here* but we are *glad* you *came*. *frumple*."*

**Combat banter** (canonical: rift creatures canonical-do-not-speak in canonical-coherent-language):
- **Opening**: *"frumple. you arrived. we *unfolded*."*
- **Mid-fight**: *"this is *fold-play*. you are *meat*. we are *not yet*."*
- **25%**: *"we are *bored*. but we will *continue*."*
- **5%**: *"the *fold* closes. we are *not gone*. we are *elsewhere*. *frumple*."*
- **Post-fight**: *(canonical: the rift canonical-collapses; canonical-the-Steward-buys-the-cluster-a-few-weeks)*

**Common Room reaction beats**:
- Vresh: *"We-all sense the canonical-rift-residue. We-all are canonical-uncomfortable. We-all do not have canonical-words for the canonical-feeling. We-all are canonical-trying."*
- Forward (canonical-perpendicular-sincerity): *"The rift was canonical-perpendicular to canonical-3D-space. I have canonical-some-experience with canonical-perpendicular-existence. I find the canonical-rift canonical-more-perpendicular than I am. I am canonical-impressed and canonical-troubled."*
- Sevra: *"I have not been told what *frumple* means. I have decided I do not want to know."*
- Forty-Seven: *"I have canonical-attempted-translation. The word *frumple* has canonical-no canonical-Furling-cognate. I have canonical-logged-it as canonical-untranslatable. I am, by my standards, canonical-uncomfortable."*

**Bio-Archive entry**:
> *Bio-Archive Entry 14,494 (extends Others — Rift Sighting entry). Subject: the rift creature engaged in our cluster. Combat duration: 4 minutes 12 seconds. The rift canonical-collapsed after sustained fire. Council assessment: the canonical-rift-may-have-been the canonical-Orz-precursor-substrate; the canonical-Orz-do-not-yet-exist as a coherent species but the canonical-Dimension-* substrate canonical-leaks-into-our-space periodically. We bought the cluster a few weeks of canonical-rift-free-operation. Use them.*

---

## 12. Cross-encounter Common Room banter additions

Compiled catalog of canonical Common Room banter triggers for various slice events. For Design: these are scene-state-conditional dialog beats.

### 12.1 First-time-meet-a-species reactions (each new species adds a beat)

- **Slylandro first-meet**: Mraka *"They named themselves after canonical-weather. Forty-Seven, what is my canonical-weather-name?"* / Forty-Seven *"You are canonical-Brisk-Morning-Of-Coffee-Spilled, by canonical-prior-Slylandro-record."* / Mraka *"Forty-Seven."* / Forty-Seven *"You established the name yourself, Mraka."*
- **Arilou first-meet**: Tarven *"They use canonical-multiple-tenses. The archive is canonical-difficult-to-format."* / Forty-Seven *"I have written a canonical-tense-translation-protocol. The protocol is canonical-imperfect. The Arilou canonical-do-not-mind."*
- **Karavem first-meet**: Vresh *"We-all heard the canonical-song. We-all are canonical-still-processing the canonical-inversion."*
- **Kovellim first-meet**: Forty-Seven *"They have done this canonical-seven-times. I am canonical-noting that we are canonical-amateurs."*
- **Stelloth first-meet**: Forward *"Three voices, one being. I find this canonical-mathematically-pleasing. They have canonical-resolved the canonical-singular-plural canonical-question by canonical-being-both."*
- **Mrokon first-meet**: Tarven *"They are canonical-staying-to-fight. The fight is canonical-canonical-only-marking-not-killing. The marking will canonical-survive cycles. This is canonical-worth-noting."*
- **Burvixese first-meet**: Renn *"In my time, we had — *(canonical pause)* — actually, we did not have anything like the Burvixese. They are canonical-cheerful-engineers facing canonical-the-end. I am canonical-impressed."*
- **Thinn first-meet (Forward present)**: Forward *(canonical-quietly)* *"They are canonical-still-believing-the-doctrine. I have canonical-tried to canonical-tell them. They canonical-do-not-listen. They will canonical-listen-when-the-Others-canonical-do-not-pass."*
- **Taalo first-meet (Vresh present)**: Vresh *(hum-pattern in grief-mode + joy-mode simultaneously)* *"We-all are canonical-with them. We-all are canonical-leaving them. We-all are canonical-both."*
- **Melnorme first-meet**: Mraka *"They trade canonical-only-for canonical-bio-data. Forty-Seven, are we canonical-bio-data-rich?"* / Forty-Seven *"We are canonical-bio-data-adequate. We have canonical-significant cluster-bio. We can canonical-trade."*

### 12.2 Pre-Fall vs Post-Fall Common Room ambient

Pre-Fall canonical: canonical baseline warmth; canonical Mraka-Tarven sibling-argument-frequency baseline.

Post-Fall canonical (if Halia survived or died): canonical *quieter*; canonical *longer pauses between conversations*; canonical *sibling argument paused for ~3 days then resumed in canonical-post-Fall-quieter-variant*; canonical *Vresh hum-pattern canonical-shifted-to-grief-mode for ~1 week*; canonical *Sevra reading-aloud-to-Vresh increases canonical-frequency*; canonical *Forty-Seven's *"I am working on it"* canonical-frequency-doubles*.

**Canonical authored dialog (Gemini batch 001, Lore-reviewed and approved)** — three post-Fall scenes across the canonical timeline:

**3 days after the Fall** — *scene*: Mraka is fiddling with a small device, Tarven observes from his archive station.

> **Mraka**: This micro-resonator… it's just not responding. Tools are alphabetized, you know. Every single one.
>
> **Tarven**: Indeed. The records are useful, Mraka. Perhaps you are attempting to recalibrate a dampener with a flux coil? It is a common error.
>
> **Mraka**: A common error is assuming I make common errors. It's the coupling. It needs… a certain *feel*.
>
> **Tarven**: A feel that the records do not detail, I presume. Fascinating. My own analysis suggests thermal variance.

*Canonical-note*: the sibling-argument is canonical-paused per canon; canonical: this exchange is canonical-professional-not-arguing register — canonical-correct for the canonical 3-days-after-Fall timing. Canonical callbacks: *"tools alphabetized"* (Mraka signature) + *"the records are useful, Mraka"* (Tarven signature).

**3 weeks after the Fall** — *scene*: Sevra is reading to Vresh-Hum-Of-The-Slow-Veins, who is humming a subdued pattern. Renn is nearby, ostensibly cleaning.

> **Sevra**: '…and the starlight, once a comforting blanket, now seemed to stretch thin, brittle.'
>
> **Vresh-Hum-Of-The-Slow-Veins**: We-all feel the… stretch. The brittleness. It resonates.
>
> **Renn**: Yeah, that… that feeling. Like the whole ship's hum is a little… off. Off-key, you know? Not groovy at all.
>
> **Sevra**: We will find the right key again, Renn. Tomorrow, perhaps.

*Canonical-note*: canonical Sevra-reading-aloud-to-Vresh per canonical existing-bond-canon (`crew-roster-redesign.md §5`). Canonical *the canonical-tomorrow with canonical-care* lands as canonical-Sevra-signature. Canonical Renn *"groovy"* 22nd-century-slang slip canonical-correct.

**1 month after the Fall** — *scene*: Forward is watching the main display, a slight ripple of his ribbon-body. Forty-Seven's presence is subtly noted.

> **Forward**: The sensor sweep indicates a 0.003% increase in ambient nebula density. Facing forward, this presents a marginal tactical consideration.
>
> **Forty-Seven**: By my standards, that is a statistically significant deviation from baseline. I am cross-referencing with historical atmospheric models.
>
> **Mraka**: Deviation means something changed. Always something changing. Keeps things… interesting, I guess.
>
> **Tarven**: The records indicate many changes, Mraka. Some are more… impactful than others. The present era is certainly marked by impact.

*Canonical-note*: canonical-return-to-near-baseline with canonical-permanent-grief-undertone canonical-perfectly-captured in Tarven's closing *"the present era is certainly marked by impact"*. The sibling-argument is canonical-resumed-at-canonical-half-volume — canonical-correct for the canonical 1-month timing.

### 12.3 Andromeda-arrival full canonical chorus (extended from humor-pass.md)

Per `humor-pass.md §5.6` + `callbacks-and-callforwards.md §2.3` — canonical full FIXED-SEQUENCE chorus. Authored canon (already covered in those docs).

### 12.4 Per-quest-completion banter

When the Steward completes a species quest favorably, canonical *brief Common Room celebration beat*:
- Mraka canonical *high-pitched short cheerful sound* (canonical Drifter-Circuit tradition for canonical-successful-mission)
- Tarven canonical *records the outcome in the canonical-archive immediately* (canonical *no-celebration-without-archive*)
- Sevra canonical *brief observation* (canonical *"You did well. The species is canonical-safe-or-honored. Either way."*)
- Forty-Seven canonical *logging notification* (canonical *"Logged. The canonical-Quiet-Ledger has canonical-an-entry-not-to-record. I find this canonical-satisfying."*)

### 12.5 Per-quest-failure banter (canonical: rare; canonical *Stay or Cleanse outcomes*)

When a species ends Eliminated or Stay-outcome:
- Mraka canonical *quiet*; canonical *no-celebration*
- Tarven canonical *records the canonical-Quiet-Ledger entry with canonical-full-honor*
- Vresh (hum-pattern in grief mode): *"We-all are canonical-with-them. We-all canonical-honor the canonical-choice or the canonical-end."*
- Forty-Seven: *"Logged. The canonical-Quiet-Ledger now contains canonical-N-names. The canonical-bookkeeping is the canonical-dignity. — Halia would say. Halia is — *(canonical pause; canonical-Halia-status-conditional)*"*

---

## 13. Cross-chat dispatches

### To Design (`HANDOFF_design_chat.md`)

**Net new content**:
- **11 species quest FSMs** authored (Stelloth / Selvenne / Kovellim / Karavem / Mrokon / Taalo / Burvixese / Thinn / Melnorme / Dnyarri / Orz-rifts) — all with canonical dialog states + canonical branches + canonical side-effects
- **~70 new combat banter lines** across the 11 species (canonical 5-damage-bracket pools per species)
- **~50 new Common Room banter beats** across canonical first-meets + canonical pre/post-Fall ambient + canonical quest-completion + canonical-failure
- **Canonical new modules introduced**: STELLOTH_PHASE_LENS / SELVENNE_REEF_TOUCH / KOVELLIM_FOLDER_COMPASS / KOVELLIM_CROSSING_BRACE / KOVELLIM_CYCLE_MEMORY / KARAVEM_RESONANCE_MODULE / MROKON_HAMMER_ROUND / TAALO_SILICATE_HARDENING_LANDER_UPGRADE / BURVIXESE_AMPLIFIER_LANDER_UPGRADE / MELNORME_ECHO_SENSOR / MELNORME_HARDENING_LANDER_UPGRADE / MELNORME_COUNCIL_SEAT
- **Canonical 11 Bio-Archive entries** authored (one per species)
- **Canonical [PLACEHOLDER] markers** flagged for Aaron-call where appropriate (canonical Veshen / Tev-Mar-Burv canonical-NPC-names; canonical Edge-Align-Eldest canonical-naming-convention; canonical Aaron may want specific NPC names)
- **Canonical Thinn-paradoxical-combat-saves-more-Thinn mechanic** authored: canonical: firing on Thinn ships causes them to canonical-realize-the-doctrine-is-wrong and canonical-Migrate at higher rates — canonical *the only species in the slice where canonical-combat-helps-the-species-save-themselves*. Recommend design carefully — this is a canonical-surprising-mechanic.
- **Spreadsheet ports needed** (to parallel chat's `tools/build_quest_inventory.py`):
  - 11 quests x ~5 states avg = ~55 new quest rows
  - Plus the existing canon for the other species already filed

### To Image (`HANDOFF_image_chat.md`)

**Net new portrait/scene requirements**:
- **Stelloth**: 3-body chord render (Speaker/Witness/Counter; canonical *the three bodies are canonical-different-sizes per perceptual-timescale* — canonical Speaker smaller-faster; canonical Counter larger-slower); Tarvel-Three-Voices NPC variant
- **Selvenne**: planet-scale coral reef on Vellumar; Choir-Of-The-East-Reef rendered as canonical-multiple-overlapping-polyps-emitting-warm-light; canonical Reef-Touch visual when the Steward touches a polyp (canonical-qualia-overlay)
- **Kovellim**: nomadic-ship aesthetic (canonical-multi-galactic-crossing-veteran-vessels with canonical-visible-patching from canonical-prior-corridor-impacts); Ovala-Eight-Crossings with canonical-eight-knot-scars visible; canonical Folder-Compass device
- **Karavem**: winged-philosopher portrait (canonical large feathered wings, hollow-bones, gentle eyes); Veled-Of-The-Canyon-Wall NPC; canonical-Karavem-canyon-environment with canonical-acoustic-architecture (canonical wall-shapes that canonical-amplify-three-tone-singing)
- **Mrokon**: ~1m bunker Operator + ~2.3m armored Puppet two-figure render; canonical Vrek-The-Ninth-Body puppet; canonical *Hammer-Of-Refusal* weapon (canonical-massive-kinetic-impactor-spear-like); canonical Operator-Puppet-Switch visual cue
- **Taalo**: silicon mountain-range planetary view; Veshen-Hum-Of-The-Slow-Veins as canonical-individual-extruding-from-mountain (canonical: Vresh-tank-comparison visible if the Steward has visited both)
- **Burvixese**: four-armed engineer portrait; Tev-Mar-Burv NPC; canonical Broadcaster network visible across canonical-multiple-systems; canonical *cheerful-engineer-aesthetic*
- **Thinn**: 2D ribbon-being canonical-edge-on-and-flat-on renders (canonical: the canonical-edge-on render is canonical-a-vertical-line); Edge-Align-Eldest NPC; canonical Forward-comparison visible
- **Melnorme**: canonical orange-pod cyclopean form (canonical SC2-recognizable); canonical-gas-cloud-energy-being canonical-faintly-visible inside the pod; canonical-super-giant-heliopause environment; canonical Drahn destruction visible as canonical-distant-memory-overlay if the Steward asks about Drahn
- **Dnyarri**: canonical *the canonical-faked-species-disguise* (canonical *the ship LOOKS like any catalog ship until it fires*); canonical *DNYARRI-yellow snap-color-change* on reveal; canonical *psionic-leakage visual effect* mid-combat
- **Orz-rift**: canonical *Dimension-** non-3D-space visual (canonical-rendered as canonical-spatial-distortion; canonical-objects-at-apparent-foreground-floating-past-objects-at-apparent-background; canonical-not-resolving-under-sensors); canonical rift-creature combat sprite

**Plus environmental signs for each species' canonical-environment-locations** (per `callbacks-and-callforwards.md §3.5` canonical Furling-language signs canon).

### To Audio (`HANDOFF_audio_chat.md`)

**Net new voice/audio requirements**:
- **Stelloth three-voice canonical-three-actor-recording** — Speaker fast / Witness measured / Counter canonical-counting-aloud (canonical: the canonical-three-actors recorded separately + canonical-mixed for canonical-simultaneous-render); canonical *the canonical-chord may canonical-misalign* (canonical: occasional canonical-out-of-sync moments for canonical-comedic-effect)
- **Selvenne canonical-chorus-of-many-voices** (canonical: single actor + canonical-pitch-shifted-and-layered for canonical-many-simultaneous-voicings; canonical-canonical-effect = canonical *one being whose voice is plural*)
- **Kovellim canonical-veteran-warmth** — Ovala canonical-deep, canonical-considered, canonical *seven-prior-crossings*-experienced register; canonical *patient amusement at first-crossing species' panic*
- **Karavem canonical-three-tone-song-rendering** — canonical *single actor performing three simultaneous notes is canonical-impossible*; canonical: layered recording with canonical-three-pitches + canonical *major-key-for-grief / minor-key-for-joy* inversion; canonical: the canonical-listener-must-learn the inversion across the slice
- **Mrokon canonical-bunker-Operator-voice through-puppet-voicebox** acoustic profile — canonical *the voice canonical-comes-from-the-puppet but is canonical-piped-from-the-bunker*; canonical: small canonical *transmission-delay* layer; canonical Operator-Puppet-Switch audio cue (canonical: canonical *click + brief silence + canonical-different-puppet-voice continues*)
- **Taalo canonical-Veshen voice** — canonical *Vresh-baseline-but-from-the-mountain* (canonical-Veshen-and-Vresh canonical-share-cognitive-substrate; canonical-the-voice-is-canonical-similar but canonical-Veshen-renders from canonical-larger-substrate so the canonical-hum-layer is canonical-deeper)
- **Burvixese canonical-cheerful-engineer-pace** — canonical fast-but-clear; canonical *occasionally-loses-cheerfulness-briefly-then-recovers* (canonical comedic-tragedy)
- **Thinn canonical-baseline-doctrine-voice** — canonical *plural-collective*; canonical *very-thin-acoustic-profile* (canonical: their canonical-2D-substrate canonical-affects-the-voice; canonical-the-voice canonical-feels-canonical-flat-in-some-way)
- **Melnorme canonical-pod-voicebox** acoustic profile — canonical *mechanical-but-not-robotic*; canonical *the canonical-gas-cloud-being canonical-pilots-the-pod's-voice*; canonical: small canonical-ionization-cascade audible underneath canonical-baseline-Melnorme-voice
- **Dnyarri canonical-multilayered-psionic-leakage** — canonical *the voice canonical-feels-wrong*; canonical: layered with canonical-faint-additional-voices (canonical-host-bodies-canonical-residue); canonical *snap-shift* from canonical-faked-species-voice to canonical-DNYARRI on first-fire (canonical: dramatic audio moment)
- **Orz-rift canonical-untranslatable**: canonical *the asterisks indicate emphasis the rift's voice gave but which the translator could not parse*; canonical: render the asterisks as canonical *audible-emphasis-with-no-semantic-canonical-match*; canonical-the-voice canonical-is-canonical-locally-sourced-but-canonical-omnidirectional in mix; canonical *the canonical-voice canonical-should-feel-wrong-to-the-listener*

---

## 14. Open items / Aaron-call

- **Canonical NPC names marked [PLACEHOLDER]**: Veshen-Hum-Of-The-Slow-Veins (Taalo); Tev-Mar-Burv (Burvixese); Edge-Align-Eldest (Thinn). Aaron may want specific names.
- **Canonical Skitter-Prime / Vellumar / canonical-other-homeworld names**: provisional; Aaron may revise.
- **Canonical Thinn-paradoxical-combat-saves-more-Thinn mechanic**: provisional canon. The canonical *firing-on-Thinn-saves-more-Thinn* is canonically-novel mechanically. Aaron may want to canonical-revise or canonical-confirm.
- **Canonical module identifiers**: provisional naming (STELLOTH_PHASE_LENS etc.). Aaron may want canonical naming-convention review.
- **Canonical [PLACEHOLDER] Bio-Archive entries**: each canonical-species has a canonical-1-paragraph entry; Aaron may want expansion for specific species.
- **Canonical Dnyarri appearance frequency**: provisional canon (canonical *super-melee gamble pick* + canonical *rare-cluster-hyperspace-encounter*). Aaron may want canonical-encounter-frequency tuning.
- **Canonical Orz-rift-combat-buys-cluster-time canonical-mechanic**: provisional canon (canonical *defeating buys-the-cluster-a-few-weeks*). Aaron may want canonical-impact tuning.
- **Canonical Melnorme Council-shelving-test sequence**: provisional canon for the canonical Super-Mart canonical-shelving verification step. Aaron may want canonical-test-mechanic detail.

---

## 15. Cross-references

- [factions-and-war.md](factions-and-war.md) — canonical Furling Council factions; each species canonical-aligns or canonical-opposes
- [cleansers-as-ice-branch.md](cleansers-as-ice-branch.md) — canonical Cleanser vote applies to canonical-each-Homesteader species
- [preservers-as-tree-branch.md](preservers-as-tree-branch.md) — canonical Preserver vote canonical-counter; canonical Preservers may visit each Homesteader species
- [utwig-quest.md](utwig-quest.md) — canonical Utwig (already complete)
- [species-the-lemmkin.md](species-the-lemmkin.md) — canonical Lemmkin (already complete)
- [the-androsynth-refugees.md](the-androsynth-refugees.md) — canonical Androsynth (already complete with Coel + from-afar canon)
- [crew-roster-redesign.md](crew-roster-redesign.md) — canonical bridge crew; canonical-each crewmate canonical-reacts to canonical-each-species visit
- [halia-profile.md](halia-profile.md) — canonical Halia commentary on canonical-each-species-outcome
- [bio-archive-entries.md](bio-archive-entries.md) — canonical-existing Bio-Archive entries; canonical *the 11 new entries* canonical-add to that catalog
- [humor-pass.md](humor-pass.md) — canonical 8-style humor canon; each species canonical-aligns with one or more styles
- [callbacks-and-callforwards.md](callbacks-and-callforwards.md) — canonical callback economy; canonical *"Drink the tea"* migrates across canonical-multiple species
