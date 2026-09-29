# Cross-Species Awareness + Should I Stay or Should I Go Meter

> Aaron dispatch (2026-05-18): *"Do a pass where there are extra dialog events that let the player know the species is aware of events elsewhere in the galaxy that the player responsible for. Example: 'I hear the Taalo home world was annihilated and you have the last survivor of their kind on your ship.' or something similar. Each species might only be aware of 3 other possible nearby events, not every single one. Build an overall 'Should I Stay or Should I Go' meter that is sort of a quest completion meter letting the player know how much of the 'great ending' content they have completed, successful or not."*
>
> Two features canonized:
> 1. **Cross-Species Awareness Events** — each species canonical-aware of 3 other slice-events the Steward is canonical-responsible-for; canonical surface as conditional dialog on revisit
> 2. **The Should I Stay or Should I Go Meter** — canonical player-visible quest-completion meter; canonical-delivered by Forty-Seven; canonical-shows-progress-toward-Great-tier-ending (canonical *successful or not* per Aaron canon — the meter measures completion, not moral outcome)

---

## 1. Cross-species awareness — design

### 1.1 The canonical premise

Each species in the slice has canonical *limited awareness* of events elsewhere in the galaxy. They are not omniscient — canonical *each species canonical-knows-about-only-3-other-events* that have plausibly reached them via their canonical-communication-channels. The canonical *3-event-limit* is canonical-by-design (Aaron canon); canonical: any more would feel canonical-magical; canonical-less would feel canonical-disconnected.

The awareness manifests as canonical *conditional dialog* — if the Steward has triggered the relevant event-flag AND the species has a canonical-channel-to-know-about-it, then on canonical-next-visit (or canonical-revisit during the same encounter), the species canonical-greets-the-Steward with awareness of the event.

### 1.2 Canonical-channels-of-awareness

How each species learns about distant events:

| Channel | Species using it | What they learn |
|---|---|---|
| **Furling Council relay** | All Furling-allied species (most slice species) | Council-published events (Mh-Lai Fall; Cleanser actions; Sa-Matra progress; the Steward's recommendations) |
| **Burvixese Broadcaster network** | Anyone listening to Burvixese broadcasts | Broadcast content (canonical-Migration-progress; canonical-Burvixese-songs-and-fragments) |
| **Arilou Quasi-Space temporal-drift** | Arilou only | Pre-knowledge of future events |
| **Slylandro 10,000-year observation** | Slylandro only | Visible distant astronomical/dimensional events |
| **Mycon spore-network** | Mycon biots only | Other-Mycon-site status |
| **Chenjesu resonance-translation** | Chenjesu (slow, geological) | Stone-resonance events; silicon-substrate events |
| **Stelloth trader-network** | Stelloth + their canonical-trade-partners | Trade-route events; cluster-economic-shifts |
| **Selvenne hive-mind pre-knowledge** | Selvenne | Anything (canonical-they-already-knew) — but canonical-limited-to-3-per-Aaron |
| **Kovellim galactic-monitoring** | Kovellim veteran-Migrators | Migration-progress; corridor-conditions; Mh-Lai-level events |
| **Karavem song-exchange-network** | Karavem | Song-encoded-events from other singing species |
| **Melnorme trade-data** | Melnorme | Canonical-everything-via-trade — but canonical-limited-to-3-per-Aaron |
| **Cleanser doctrinal-tracking** | Cleansers (Vael-Souren) | Cleanser-mission-target status; Defender-fleet movements |
| **Mrokon kill-tally tradition** | Mrokon | Anything-marking-the-Others; combat-record-keeping |
| **Lemmkin curiosity-engineering-curiosity** | Lemmkin | Engineering-disaster-events; canonical-explosive-events |
| **Preserver canopy-singing-network** | Preservers (Lirin Pel-Sa) | Other-Preserver-witnessed-events; canonical-Slylandro-Cloaking-Satellite progress |
| **Steward's-Distress-Beacon-showings** | Androsynth (canonical: they track who has been shown the Beacon) | Who has received the Beacon |
| **Forty-Seven's-records** (canonical-meta) | Forty-Seven (the AI knows everything) | Canonical-meta-awareness; canonical *Forty-Seven delivers the canonical-meter (§3)* |

### 1.3 Canonical-dialog-format

Each canonical-awareness event surfaces as a canonical *greeting-prefix-line* on canonical-next-visit-after-flag-trigger. The species canonical-acknowledges the event canonical-briefly-then-continues-normal-dialog. Canonical: the awareness is canonical-flavor not canonical-quest-blocking; canonical-the-Steward-can-skip the awareness reaction and proceed to canonical-baseline-dialog.

Canonical structure:
```
on_revisit_dialog:
  IF flag:<event_triggered> AND canonical-channel-supports-awareness:
    npc_text: <awareness-prefix-line>
    THEN continue to standard greeting
  ELSE:
    standard greeting
```

### 1.4 Canonical Aaron-example reproduced

> *"I hear the Taalo home world was annihilated and you have the last survivor of their kind on your ship."*

The canonical structure: **species-acknowledges-Steward's-action** + **species-references-Steward's-current-state**. The awareness is canonical *warm-or-grave depending on species-and-event*; canonical *not-judgmental*; canonical-the-species-knows-what-happened-and-canonical-knows-the-Steward-is-canonical-carrying-the-survivor.

---

## 2. Awareness events catalog — 21 species × 3 events each

Per-species canonical 3 awareness events. Each event has: **event-flag** (the canonical condition that triggers awareness) + **canonical-dialog-line** (the species canonical-delivers on revisit).

### 2.1 Slylandro (Hail-Curtain-Of-A-Long-Decade)

**Channel**: 10,000-year observation + Arilou-cousins-flag-it

1. **flag:taalo_eliminated** → *"We have heard the silicon-songs of Taalo's-Stone go silent. Twelve thousand of our years they have sung; one of our seasons of silence now. The Steward is canonical-with-the-last-one. We honor canonical-both: the silenced and the carried."*
2. **flag:mh_lai_fell** → *"The Furling-home — we sang of it. The song was three days. We will canonical-not sing it again, perhaps; we have only canonical-one-song-per-loss in our tradition. The Steward bore witness. We canonical-witnessed-the-Steward-bearing-witness. The canonical-song will canonical-include this."*
3. **flag:androsynth_arrived** → *"The Arilou-cousins flagged a fold in the gas-currents above us. We thought it weather. They told us it was canonical-survivors-from-the-future. We have prepared a song. The song will canonical-take canonical-twelve days. The Steward is canonical-welcome to listen if canonical-time-permits."*

### 2.2 Arilou (Quasi-Space cousins)

**Channel**: temporal-drift; canonical pre-knowledge

1. **flag:rainbow_resonator_seeded** → *"We were-are-will-be pleased. The Rainbow World you canonical-seeded is canonical-bright in our future-memory. We have already-remembered Andromeda canonical-arriving. The canonical-thing is canonical-good."*
2. **flag:halia_died_in_fall** → *"We will-have-grieved Halia. We are-grieving Halia. We have-grieved Halia. The Shaggy One — *(canonical pause)* — we are sorry. Patience-as-a-religious-virtue does not canonical-extend to canonical-this. We have canonical-broken our canonical-rule briefly. We canonical-recommend you canonical-do-likewise."*
3. **flag:sevra_recruited** → *"The young Utwig is canonical-with you. We canonical-remember her canonical-arrival in Andromeda. She will-have-written-a-book. We have-read-it. It will-be-good. We will-not-tell-you-the-content. Some canonical-things should canonical-arrive in canonical-their-own-time."*

### 2.3 Mycon biots (via spore-network)

**Channel**: mycelial spore-network connection between mantle-sites

1. **flag:cleanser_active_on_mycon** (any Mycon site Cleansed) → *"alpha-tucanae-four: the mantle has canonical-stopped-warming. the spore-network reports canonical-silence. THE DEEP CHILD WHISPERS-ARE-QUIETER-FROM-THAT-DIRECTION. the mycon biot canonical-acknowledges. the canonical-cleansing is canonical-recorded."*
2. **flag:mh_lai_fell** → *"the canonical-Furling-home was canonical-warm-and-is-no-longer-warm. the spore-network is canonical-extending-to-other-warm-sites. we will canonical-continue-stirring. THE MANTLE WARMS-ELSEWHERE."*
3. **flag:taalo_eliminated** → *"the canonical-silicon-substrate at Taalo-Stone has canonical-calcified. the canonical-spore-network reports canonical-no-mycelial-engagement-was-attempted-because-canonical-silicon-substrate-resists-spore. we are canonical-curious. WE WILL NOT EXPERIMENT."*

### 2.4 Proto-Ur-Quan colonies

**Channel**: Furling Council relay

1. **flag:cleanser_action_against_uq** → *"(via Furling-translator)* The Quan-cluster at canonical-Theta-Six has canonical-been-touched. We canonical-know. The Furlings have canonical-not-explained. We are canonical-cautious. We will canonical-be canonical-cautious."*
2. **flag:uplift_continue_recommendation_filed** → *"(via translator)* The Council has canonical-decided to canonical-continue the uplift. We are canonical-uncertain how to react. We canonical-feel something we canonical-do-not-have-a-word-for. Possibly canonical-gratitude. Possibly canonical-fear. We will canonical-investigate the feeling."*
3. **flag:uplift_cleanse_recommendation_filed** → *"(via translator; canonical-rapid-fire chord-pheromone delivery)* The Council canonical-cleansing canonical-our-cohort. We canonical-knew. We will canonical-fight. The Steward will canonical-find us canonical-prepared. We thank-the-canonical-Council-for-the-canonical-warning."*

### 2.5 Proto-Qor-Ah colonies

**Channel**: Furling Council relay (canonical-shorter than proto-Ur-Quan)

1. **flag:cleanser_action_against_qa** → *"(via translator)* The canonical-Qor-Ah-purification continues elsewhere. We canonical-honor-the-canonical-elsewhere. We canonical-purify here."*
2. **flag:proto_uq_uplift_continued** → *"(translator)* The proto-Ur-Quan have canonical-been-uplifted. We are canonical-displeased. The canonical-uplift creates canonical-impure-cousins. We will canonical-purify-them when canonical-able."*
3. **flag:mh_lai_fell** → *"(translator)* The canonical-Furling-home has canonical-fallen. The canonical-Furlings canonical-failed. We canonical-purify-better-than-they-did. We will canonical-remember-this."*

### 2.6 Androsynth (Coel Tessar)

**Channel**: Furling Council brief + canonical-Distress-Beacon-tracking

1. **flag:distress_beacon_shown_to_X** (any species shown the Beacon) → *"Coel: I am told you showed the Beacon to canonical-<X>. Thank you. The canonical-watching is canonical-difficult. The Beacon is canonical-our-burden-to-share, and canonical-our-burden-to-not-keep-private. Each canonical-showing is canonical-a-small-erosion of our canonical-silence. We canonical-permit-the-erosion."*
2. **flag:mh_lai_fell** → *"Coel: The Furling-home. I — I am sorry. Halia visited us. She was canonical-kind. I did not know her well. I am told canonical-she-stayed-to-keep-her-canonical-word. That is canonical-very-Furling. It is canonical-very-everything-I-respect-about-them."*
3. **flag:from_afar_theory_articulated** (Steward triggered Coel's canonical private theory-articulation dialog) → *"Coel: I told you the theory. You have canonical-considered it. You have not canonical-rejected-me-for-it. Thank you. Thank you. Renn would have — *(canonical pause)* — Renn did not need-to-be-told. He canonical-knew. He is canonical-with-you. He has canonical-been-kind-to-me-since. I have canonical-not-deserved-the-kindness. I have canonical-accepted-it."*

### 2.7 Mmrnmhrm (Sentinels at Ossuary)

**Channel**: canonical-archive + Furling-broadcasts

1. **flag:cleanser_action_against_any_species** → *"Archive entry seven million two hundred forty thousand, eight hundred eleven. Steward, we register that a Cleanser-faction Furling has canonical-completed-canonical-action against canonical-<species>. The canonical-action is canonical-recorded. The canonical-Quiet-Ledger has canonical-grown. We canonical-note that the canonical-pattern matches the canonical-First-Makers' canonical-final-decision. We canonical-do-not-judge."*
2. **flag:sa_matra_prototype_progressed** → *"Archive entry. The Defender canonical-Sa-Matra-Prototype has canonical-progressed by canonical-fourteen-percent. We have canonical-modeled the canonical-projected canonical-engagement against canonical-Others-substrate. The model canonical-projects canonical-failure. We canonical-have-told the Furling-Council. They have canonical-thanked-us-for-the-data. The canonical-Prototype canonical-continues."*
3. **flag:mh_lai_fell** → *"Archive entry. The Furling-Council-home has canonical-fallen. We canonical-extend-formal-condolences-via-archive. The Furlings have canonical-thanked-us. The canonical-condolences are canonical-noted. We canonical-continue. There is canonical-nothing-else-to-be."*

### 2.8 Chenjesu (Procyon)

**Channel**: slow stone-resonance + canonical-prior-cycle-memory

1. **flag:taalo_eliminated** → *(slow; 30-second-delivery)* *"We... feel... Taalo's-Stone... go... quiet. The silicon... is... silent... now. We grieve. Slowly. We have... grieved... before. We will... grieve... again. Carry the one... you saved. We bless... her."*
2. **flag:selvenne_reef_lifted** → *"The Selvenne... reef... is moving. We feel... the stone... shift. We approve. The Selvenne... we know. They are... like us... but younger. They will... reach... the new... galaxy. We will... not. We are... at peace."*
3. **flag:resonance_record_delivered_to_council** → *"You delivered... the Record. The Furlings... now know... that we... remember. The cycles... will be... discussed. We have... waited... a long time. Thank you. Thank... you."*

### 2.9 Stelloth (Tarvel-Three-Voices)

**Channel**: trader-network

1. **flag:mh_lai_fell** → *Speaker: "The Furling-home has fallen. Our canonical-trade-routes through that-region are canonical-restructured."* / *Witness: "The restructuring took canonical-four-days. Our canonical-fleet has canonical-adapted."* / *Counter: "Forty-eight. Forty-nine."* / *Speaker: "We canonical-mourn. We canonical-trade. We canonical-continue."*
2. **flag:selvenne_reef_lifted** → *Speaker: "The Selvenne canonical-reef-lifting was canonical-impressive. Furling-Council canonical-coordinated canonical-cargo-vessels."* / *Witness: "The canonical-cargo-capacity-utilization was canonical-ninety-three percent. We are canonical-impressed."* / *Counter: "Twelve. Thirteen."*
3. **flag:burvixese_broadcaster_placed** → *Speaker: "The Burvixese canonical-broadcaster-network has canonical-extended."* / *Witness: "We canonical-traded the placement-coordinates to canonical-three-other-trader-networks."* / *Counter: "Twenty. Twenty-one. The canonical-trade was canonical-favorable."*

### 2.10 Selvenne (Choir-Of-The-East-Reef)

**Channel**: hive-mind pre-knowledge (canonical-limited to 3)

1. **flag:steward_arrived_at_selvenne** → *"Yes. We knew. You arrived. We have prepared the answer. We have been preparing it for thirty-seven years."* (canonical existing canon; canonical-the-greeting-itself-is-canonical-pre-knowledge-aware)
2. **flag:mh_lai_fell** → *"We knew. We are canonical-sorry we did not tell the Furlings sooner. We canonical-pre-knew but we canonical-could-not-articulate-until-the-canonical-moment-arrived. The canonical-pre-knowledge does not canonical-extend-to-canonical-actionable-warning. We canonical-grieve. We canonical-knew we would canonical-grieve."*
3. **flag:taalo_eliminated** → *"We feel them — felt them — will feel them. The canonical-silicon-substrate is canonical-near-our-coral-substrate. We are canonical-with-them. We are canonical-grateful you canonical-carry the one. We canonical-pre-knew that, too."*

### 2.11 Kovellim (Ovala-Eight-Crossings)

**Channel**: galactic-monitoring + canonical-prior-crossings-experience

1. **flag:rainbow_resonator_seeded** → *"Ovala: The Rainbow World you canonical-seeded canonical-shows in our canonical-corridor-sensor-data. The canonical-arrow-vector is canonical-clearer-now. The canonical-corridor-conditions are canonical-favorable. We are canonical-pleased."*
2. **flag:mh_lai_fell** → *"Ovala: The Furling-home has canonical-fallen. We canonical-noted. We have canonical-seen-canonical-galactic-homeworlds-fall before. Our canonical-third-crossing-canonical-galaxy lost canonical-eleven-canonical-homeworlds in canonical-one-canonical-season. The canonical-Furling-loss is canonical-painful and canonical-survivable. We are canonical-here-to-help."*
3. **flag:halia_died_in_fall** → *"Ovala: The canonical-Fleet-Commander. We have canonical-known-Defense-Fleet-Commanders before, across canonical-prior-crossings. They canonical-tend-to-die-keeping-their-canonical-word. Halia is canonical-not-the-first-of-this-pattern. She is canonical-the-one-we-have-known. We canonical-honor her by canonical-continuing the canonical-corridor-work."*

### 2.12 Karavem (Veled-Of-The-Canyon-Wall)

**Channel**: song-exchange-network

1. **flag:slylandro_cloaking_satellite_installed** → *(bright major key; canonical-grief-content)* *"We sing of canonical-saving! The Slylandro have canonical-been-cloaked! We are canonical-grieving the canonical-cloaking — *(canonical major-key continues)* — because canonical-cloaking is canonical-leaving and canonical-leaving is canonical-grief."*
2. **flag:karavem_song_received_by_other_species** → *(minor key; canonical-celebratory)* *"Our song has canonical-traveled! The Selvenne canonical-received-it! The canonical-song-network canonical-extends! We are canonical-celebrating in canonical-minor-key!"*
3. **flag:mycon_deep_child_whispers_heard** → *(mixed keys)* *"We have canonical-heard-the-Deep-Child-whispers. They are canonical-not-music. They are canonical-not-not-music. We are canonical-uncertain how to canonical-classify. We will canonical-sing about it. The canonical-song will canonical-take canonical-seven-years."*

### 2.13 Melnorme (canonical-Trader)

**Channel**: trade-network-everything (canonical-limited to 3 per Aaron canon)

1. **flag:mh_lai_fell** → *"Trader: The Furling-home fell. Our canonical-trade-routes through canonical-Mh-Lai-cluster are canonical-restructured. The canonical-trade-ratio against canonical-affected species shifts by canonical-three-percent. We canonical-mourn. We canonical-trade. The canonical-trade includes canonical-mourning-prices."*
2. **flag:drahn_loyalists_stayed** (canonical-baseline; canonical-always-true after slice mid-game) → *"Trader: Drahn was canonical-annihilated. The canonical-loyalists canonical-stayed. We canonical-survivors canonical-continue. The canonical-trade continues. The canonical-trade is canonical-our-distraction. You canonical-may-buy more canonical-bio-data canonical-products if canonical-you-have-bio-data-to-canonical-trade."*
3. **flag:cleanser_action_against_any_grounded_species** → *"Trader: We canonical-noted the canonical-Cleansing of canonical-<species>. The canonical-Cleansers are canonical-professional. We canonical-do-not-trade with them but we canonical-respect-the-canonical-discipline. The canonical-trade-list canonical-now-includes a canonical-mourning-discount for canonical-three-cycles."*

### 2.14 Cleansers (Vael-Souren)

**Channel**: doctrinal-target-tracking + Defender-fleet-monitoring

1. **flag:preserver_blocked_my_action** (Vael-Souren standing-aside while Preserver advocacy succeeded with Council) → *"Vael-Souren: The Council canonical-voted-against my canonical-recommendation on canonical-<species>. The canonical-Preservers were canonical-louder than I canonical-was. I canonical-respect the canonical-Council-process. The canonical-species canonical-survives. The canonical-Quiet-Ledger canonical-does-not-grow today. I will canonical-write a canonical-private-archive-entry about the canonical-difference between canonical-the-Quiet-Ledger and canonical-the-Quiet-Record. Both are canonical-canonical. Drink the tea, Steward. — Yes, I have canonical-also learned that phrase."*
2. **flag:sa_matra_prototype_progressed** → *"Vael-Souren: The Defender canonical-Sa-Matra-Prototype progresses. Drev-Tok canonical-continues. My canonical-faction canonical-considers this canonical-misguided. The canonical-Defenders are canonical-attempting to canonical-save the canonical-species by canonical-killing the canonical-Others, which is canonical-impossible. We are canonical-attempting to canonical-save the canonical-Migration by canonical-killing the canonical-species, which is canonical-possible-and-painful. The canonical-difference is canonical-everything."*
3. **flag:halia_died_in_fall** → *"Vael-Souren: Halia is canonical-recorded. The canonical-Quiet-Ledger now contains canonical-her name with canonical-full-honor. She was canonical-the-Persuader-faction-canonical-commander-of-the-Defense-Fleet. She was canonical-honorable to a canonical-fault. The canonical-fault is canonical-recorded as canonical-the-cause-of-canonical-her-presence-at-Mh-Lai. I will mourn her. I will canonical-mourn-her-longer-than-she-would-have-canonical-mourned-me. That is canonical-the-doctrine."*

### 2.15 Defenders (Drev-Tok via Council-channel; canonical-not-direct-encounter until Final Conflict)

**Channel**: Council-channel-intrusion monitoring

1. **flag:mh_lai_fell** → *Drev-Tok (Council channel): "The Furling-Council-home has canonical-fallen. I canonical-have-said for canonical-two-years that the Migration was canonical-preemptive-surrender. I canonical-now-say that the canonical-Migration's-mid-flight-vulnerability is canonical-also-not-surrender-it's-canonical-shoddy-preparation. I canonical-continue-to-say. The canonical-canonical-Council canonical-continues-to-ignore me."*
2. **flag:sa_matra_prototype_progressed** → *Drev-Tok: "The Sa-Matra Prototype is canonical-near canonical-functional. We canonical-test it next canonical-cycle. The Hider canonical-faction canonical-measured-incorrectly; canonical-the-Sa-Matra will canonical-scale. I canonical-have-said this. The canonical-Council canonical-continues-to-prefer canonical-running-away."*
3. **flag:steward_killed_a_cleanser** → *Drev-Tok: "I canonical-note that the Steward has canonical-killed a Cleanser-faction Furling. The canonical-Steward canonical-acted-against-the-Cleanser-doctrine. The canonical-Cleansers and I are canonical-doctrinal-opposites. I canonical-do-not-celebrate. I canonical-note. The canonical-Steward is canonical-not-entirely-aligned-with-the-Migration's-canonical-conscience. This is canonical-interesting."*

### 2.16 Hiders

**Channel**: research-substrate-monitoring + Council records

1. **flag:slylandro_cloaking_satellite_installed** → *Hider researcher: "Steward. The Slylandro canonical-Satellite is canonical-operational. The canonical-detection-threshold-modeling canonical-projects canonical-three-million-year-stable-operation. The canonical-Slylandro will canonical-outlast us. The canonical-research is canonical-validated. Thank you."*
2. **flag:mh_lai_fell** → *Hider researcher: "Steward. We canonical-acknowledge. The canonical-Hider-research-probe canonical-trajectory was canonical-the-canonical-attractor. We canonical-have-recorded-canonical-our-responsibility in canonical-the-Council-archive. We are canonical-redirecting our canonical-research-to canonical-substrate-cloaking-doctrines that canonical-do-not-require-canonical-probes. The canonical-probe-class is canonical-discontinued. We are canonical-sorry."*
3. **flag:chenjesu_cycle_testimony_archived** → *Hider researcher: "Steward. The canonical-Chenjesu-prior-cycle-data is canonical-extraordinary. We have canonical-built canonical-detection-substrate models around it. The canonical-projection: canonical-cycles canonical-recur every canonical-200,000-to-1,000,000 years. We are canonical-uncertain about the canonical-bound. We are canonical-continuing to canonical-model. Thank you for the canonical-data."*

### 2.17 Preservers (Lirin Pel-Sa)

**Channel**: canopy-singing-network + Preserver-Slylandro-resident-witness

1. **flag:slylandro_cloaking_satellite_installed** → *Lirin (multi-tonal overtones): "Steward. The Satellite is canonical-singing now. The Slylandro have canonical-heard-it sing. They are canonical-relaxing-into-the-canonical-cloaking. The canonical-song is canonical-good. I canonical-prepared-the-Slylandro for forty years for canonical-this. Thank you. The canonical-thank-you is canonical-not-needed-but-canonical-offered."*
2. **flag:utwig_devolved_baseline_completed** → *Lirin: "The Utwig have canonical-completed their canonical-First-Sixth-Veil practitioners. The canonical-doctrine is canonical-working. We canonical-respect the canonical-choice. We canonical-mourn the canonical-language they have canonical-given up. We canonical-celebrate the canonical-survival."*
3. **flag:taalo_shield_failed** → *Lirin: *(multi-tonal overtones canonical-shift-toward-grief)* *"The Taalo Shield canonical-failed. We canonical-knew it would. We canonical-still-grieve. We canonical-sang at canonical-Taalo's-Stone for canonical-three-days before-the-canonical-Others-arrived. The Taalo canonical-heard. They canonical-thanked us. They canonical-died. We canonical-thank-you for canonical-Vresh's-extraction. The canonical-one-of-them carries forward."*

### 2.18 Lemmkin (Whisk-Of-The-Better-Bouncing-Thing)

**Channel**: curiosity-driven-monitoring of canonical-engineering-and-explosive-events

1. **flag:mh_lai_fell** → *Whisk: "STEWARD! We heard! The Furling-home canonical-fell! We are canonical-investigating! We have canonical-already-built-three-canonical-models of canonical-what-the-Others-might-have-done! Two of the models canonical-exploded! One survived! The canonical-survivor is canonical-on-our-display-shelf! May we canonical-show-you?!"* (canonical: the Steward canonical-may decline; Whisk canonical-will-show-anyway; canonical-the-display-shelf canonical-also-explodes-during-the-showing)
2. **flag:sa_matra_prototype_progressed** → *Whisk: "The canonical-Sa-Matra! We have canonical-heard about it! It is canonical-very-large! The Defender canonical-engineers must be canonical-thrilled! We have canonical-applied to join the canonical-Defender-Sa-Matra-construction-team! They have canonical-not-replied! We are canonical-uncertain if they have canonical-received-our-application! We may canonical-apply-again! Steward, do you know the canonical-Defender-engineering-protocols?"*
3. **flag:hammer_round_used_on_other** → *Whisk: "The Mrokon-Hammer-Round was canonical-USED! It WORKED! The Others' Vessel was canonical-MARKED! We are canonical-VERY-excited! We have canonical-been-prototyping our canonical-own-version! Three canonical-prototypes have canonical-exploded! We are canonical-confident the canonical-fourth-prototype will canonical-also-explode but in a canonical-MORE-USEFUL-WAY! Steward, do you have canonical-any-Hammer-Round-fragments-we-could-canonical-study?"*

### 2.19 Mrokon (Vrek-The-Ninth-Body)

**Channel**: kill-tally tradition + Others-marking-monitoring

1. **flag:cleanser_action_against_any_species** → *Vrek: "The Cleansers have canonical-acted. We canonical-honor-the-canonical-kill. We canonical-record-it in canonical-our-tally. The Cleansers do canonical-similar work canonical-with-different-doctrine. The canonical-tally is canonical-grown. The canonical-work is canonical-the-work."*
2. **flag:mh_lai_fell** → *Vrek: "The Furling-Council-home has canonical-fallen. The Others canonical-acted. We canonical-record. The canonical-marking we canonical-prepare canonical-will-canonical-be canonical-stronger-for-this-knowledge. The Others canonical-took something we canonical-needed. We canonical-take-back-a-mark. The canonical-trade is canonical-uneven but canonical-the-only-trade-available."*
3. **flag:hammer_round_used_on_other** → *Vrek: "The canonical-Hammer-Round you canonical-fired canonical-landed. The canonical-Others' Vessel is canonical-marked. The canonical-mark will canonical-survive cycles. The canonical-Eighth-Body would have been canonical-proud. The Ninth-Body is canonical-pleased. The canonical-Tenth-Body, when-it-arrives, will canonical-inherit the canonical-pride. The canonical-tally is canonical-significantly-grown."*

### 2.20 Taalo (Veshen-Hum-Of-The-Slow-Veins; canonical pre-extinction only; post-extinction = silent)

**Channel**: empathic-resonance with canonical-Vresh-on-Steward-ship

1. **flag:vresh_recruited** → *Veshen: "We-all sense Vresh-Hum-Of-The-Slow-Veins on your canonical-vessel. We-all are canonical-pleased. Vresh canonical-carries us forward. We-all are canonical-with you-and-with-her. Drink the tea, Steward."*
2. **flag:selvenne_reef_lifted** → *Veshen: "We-all sense the canonical-Selvenne canonical-stone-shifting. The canonical-reef is canonical-moving. We-all are canonical-kin to them. We-all are canonical-glad they canonical-cross. We-all canonical-stay. We-all are canonical-content with the canonical-difference."*
3. **flag:chenjesu_cycle_testimony_archived** → *Veshen: "We-all sense Chenjesu canonical-resonance-output. They have canonical-given the canonical-Record. The canonical-Record canonical-tells the canonical-Furlings what came before us. We-all canonical-thank them. We-all will be canonical-recorded similarly when-the-canonical-Shield-fails. The canonical-recording will be canonical-Vresh's-canonical-memory. We-all are canonical-content."*

### 2.21 Thinn (Edge-Align-Eldest; pre-doctrine-realization only)

**Channel**: Furling-Council relay + canonical-Forward-tracking-via-Steward

1. **flag:forward_recruited** → *Edge-Align-Eldest: "The canonical-heretic Forward is canonical-with you. We canonical-track-the-canonical-heretic. They are canonical-still-facing-forward. We are canonical-still-edge-aligned. The doctrine is canonical-clear. Goodbye."*
2. **flag:mh_lai_fell** → *Edge-Align-Eldest: "We have canonical-heard. The canonical-Furling-home-canonical-fell. We were canonical-edge-aligned during-the-event. The canonical-Others canonical-did-not-see-us. The canonical-doctrine is canonical-validated. We are canonical-confident."* (canonical: the Steward may canonical-realize-the-Thinn-do-not-understand-they-were-canonical-not-in-the-Mh-Lai-direction)
3. **flag:karavem_song_received_by_other_species** → *Edge-Align-Eldest: "We have canonical-heard a canonical-Karavem-song. The song was canonical-thin-in-our-perception-because we were canonical-edge-aligned. We canonical-appreciated the canonical-thinness. We may canonical-edge-align-permanently to canonical-experience-more-canonical-thin-songs."*

### 2.22 Burvixese (Tev-Mar-Burv [PLACEHOLDER])

**Channel**: their own broadcaster network + Furling Council relay

1. **flag:mh_lai_fell** → *Tev-Mar: "Steward! We have canonical-rebroadcast the canonical-Mh-Lai-fall canonical-record across the canonical-network! All canonical-fifty-eight active broadcasters are canonical-carrying the canonical-record! Whoever canonical-finds the canonical-broadcasters will canonical-know that we canonical-mourned-with-the-Furlings. We are — *(canonical brief loss of cheerfulness)* — we are canonical-still-cheerful. The canonical-mourning is canonical-part-of-the-canonical-broadcast."*
2. **flag:karavem_song_received_by_other_species** → *Tev-Mar: "The canonical-Karavem-songs are canonical-being-broadcast on canonical-our-network! The canonical-cross-broadcast was canonical-our-suggestion! The canonical-Karavem-canonical-songs canonical-now-reach canonical-thousands-of-light-years-via-canonical-our-broadcasters! Engineering-collaboration-canonical-success!"*
3. **flag:lemmkin_explosive_event_broadcast** (canonical: any canonical-Lemmkin-engineering-disaster Whisk broadcasts to ask for advice) → *Tev-Mar: "The canonical-Lemmkin canonical-broadcasted-a-canonical-engineering-question! It was about canonical-canonical-overpressure-canonical-management! We have canonical-replied with canonical-safety-protocols! They have canonical-broadcast-our-reply-and-canonical-also-broadcast-their-canonical-rejection-of-the-canonical-safety-protocols-as-canonical-boring! The canonical-engineering-dialogue is canonical-active-and-canonical-frustrating-and-canonical-charming!"*

### 2.23 Utwig (Mal-Dren Veil-Of-Knowing)

**Channel**: Furling-Council channel + Falling-Book Appendix-of-Visitors

1. **flag:mh_lai_fell** → *Mal-Dren: "Steward. The canonical-Furling-home has canonical-fallen. We canonical-mourn. The canonical-doctrine canonical-does-not-have-canonical-language for canonical-this-grief, but the canonical-grief canonical-exists-anyway. I am canonical-noting that I-have-noticed-the-grief. This is canonical-First-Veil canonical-violation. I-have-canonical-not-renounced-the-noticing. Drink the tea, Steward."*
2. **flag:sevra_recruited** → *Mal-Dren: "Steward. The young one — Sevra. She is canonical-with-you. The doctrine canonical-permitted her canonical-leaving. The doctrine canonical-does-not-comment on her canonical-success. I would canonical-comment if the canonical-doctrine canonical-permitted me. I-will-canonical-not-articulate-the-comment. You can-canonical-infer it."*
3. **flag:ultron_recovered** → *Mal-Dren: "Steward. The Ultron is canonical-with you. The canonical-doctrine canonical-permits-its-leaving. The canonical-Council-of-Veils canonical-will-discover its canonical-absence canonical-eventually. They will canonical-conclude it was canonical-always-meant-to-leave. The canonical-conclusion is canonical-canonically-permitted. I am canonical-at-peace. Drink the tea."*

---

## 3. The Should I Stay or Should I Go Meter — design

### 3.1 The canonical premise

Per Aaron canon: *"Build an overall 'Should I Stay or Should I Go' meter that is sort of a quest completion meter letting the player know how much of the 'great ending' content they have completed, successful or not."*

The meter is canonical *player-visible UI*. Canonical: it shows canonical-progress-toward-the-Great-tier-ending content. Canonical: *successful or not* — the meter measures **completion**, not **moral outcome**. A species canonical-Cleansed counts as canonical-handled; a species canonical-Migrated counts as canonical-handled; the canonical-meter does not canonical-judge.

Canonical name: **"Should I Stay or Should I Go"** (Aaron canon; canonical reference to the song; canonical *the central question of the slice*).

### 3.2 What the meter tracks

Per the canonical 6-tier endings system (parallel-chat canon), the Great-tier-or-better-ending requires:
- All 16 slice species canonical-handled
- All canonical-named-crew recruited (canonical 7 with the canonical-six-being-bridge + Sevra)
- 85%+ side-quests canonical-favorable

The meter tracks **completion** of these components (not canonical-favorability — that drives the canonical-tier-prediction).

**Meter components**:

| Component | Total | Notes |
|---|---|---|
| **Species handled** | 16 | Each canonical-slice-species with terminal-state-set counts. ANY terminal state counts (Migrated / Devolved / Cleansed / Cloaked / Hidden / Mixed / Eliminated-with-honor / etc.). Only "unresolved" doesn't count. |
| **Crew recruited** | 7 | Mraka, Tarven, Forward, Renn, Vresh, Sevra, Forty-Seven (canonical: Forty-Seven canonical-comes-with-the-ship — auto-counted; canonical: counts toward the meter at canonical Steward's-first-direct-address) |
| **Side-quests favorable** | ~25 | The canonical-named-side-quest-list; canonical: per-species + per-crew + miscellaneous |
| **Halia status** | 1 binary | Survived (1) / Died-or-Cleanser-supervised (0) |
| **Ultron recovered** | 1 binary | Recovered (1) / Not recovered (0) |
| **Andromeda-gate readiness** | 1 binary | Final-conflict canonical-handled (1) / not yet (0) |

**Total possible**: 16 + 7 + 25 + 1 + 1 + 1 = **51 completion-points**

### 3.3 The canonical-tier-prediction logic

Beyond raw-percentage, the meter renders a canonical-tier-prediction based on the current canonical-state of completions:

| Tier | Criteria | Display label |
|---|---|---|
| **Best** | 51/51 + 95%+ side-quests favorable | *"On track for the Quiet Resolution"* |
| **Great** | 51/51 + 85%+ side-quests favorable | *"On track for *we continue, mostly*"* |
| **Good** | 16/16 species + 1-4 crew + any side-quest count | *"On track for *the home is smaller than I hoped*"* |
| **Successful-at-cost** | 8-15 species + 1-4 crew | *"On track for *the dignity is in not pretending otherwise*"* |
| **Unsuccessful** | 1-7 species OR ≤1 crew | *"On track for *the galaxy is the kitchen*"* (canonical-stark warning) |
| **Disastrous** | 0 species + 0 crew | *"On track for canonical-Good-job"* (canonical-Furling-humor-doctrine-respected; the meter canonical-bites) |

### 3.4 The Forty-Seven delivery — canonical UI integration

The meter is canonical-delivered by **Forty-Seven**. Canonical: the Steward asks; Forty-Seven canonical-renders. Canonical *"by my standards"* delivery direction.

**Canonical invocation**:
- Player action: canonical *Speak to Forty-Seven* (or canonical *Open Ledger* — canonical UI button)
- Forty-Seven canonical-renders the canonical-meter

**Canonical Forty-Seven meter-delivery dialog**:

```yaml
meter_open:
  Forty-Seven: "Steward. You have canonical-asked for the canonical-meter. I am, by my standards, canonical-pleased to deliver."
  display: METER_UI (canonical-visual progress-bars + canonical-tier-prediction text)
  Forty-Seven (after the visual): "Canonical-current-state: <N>/51 completion-points. Canonical-tier-prediction: <TIER_TEXT>. The canonical-meter is canonical-current-as-of-canonical-now. I will canonical-update-it canonical-continuously."
  choices:
    - "Tell me what I'm missing" → meter_gaps
    - "Tell me what I've done" → meter_completed
    - "Close" → null

meter_gaps:
  Forty-Seven: "Canonical-uncompleted components: <list of uncompleted-species + uncompleted-crew + unfilled-side-quests>. I am canonical-noting that canonical-many are canonical-still-time-sensitive. I am also noting that canonical-not all components are canonical-achievable — canonical-some-species canonical-prefer-to-not-be-handled by-canonical-the-Steward (canonical: Lemmkin Stay-outcome; canonical: Mrokon-stay-by-doctrine; etc.). The canonical-meter counts canonical-handled, which canonical-includes canonical-these-species' canonical-chosen-outcomes."
  choices:
    - "Specifics" → meter_gaps_specifics
    - "Back" → meter_open

meter_gaps_specifics:
  # Forty-Seven renders canonical-list-of-specific-uncompleted-items with canonical-brief-suggestion for each
  Forty-Seven: "Species: <species-name> canonical-needs-canonical-action. Suggestion: <canonical-action>. Time-window: <canonical-time-window-if-known>. (... repeats for each uncompleted species ...)"
  choices:
    - "Back" → meter_gaps

meter_completed:
  Forty-Seven: "Canonical-completed components: <list>. Canonical-summary: <brief-prose-summary>. I am, by my standards, canonical-impressed. I am also, by my standards, canonical-curious-what-the-next-canonical-action-will-be."
  choices:
    - "Close" → null
```

### 3.5 Canonical-meter-update-trigger-events

The canonical-meter canonical-updates-continuously based on canonical-flag-state. Canonical update events:
- Species terminal-state set (canonical: any Migrate/Devolved/Cleansed/etc.) → +1 species-component
- Crew member recruited (canonical: flag:<crew>_recruited=true) → +1 crew-component
- Side-quest favorable-resolution (canonical: flag:<side-quest>_resolved_favorable=true) → +1 side-quest-component + canonical-favorable-count++
- Side-quest unfavorable-resolution (canonical: flag:<side-quest>_resolved_unfavorable=true) → +1 side-quest-component + canonical-favorable-count unchanged
- Halia survives the slice (canonical: flag:halia_status=survived) → +1 Halia-component
- Ultron recovered (canonical: flag:ultron_recovered=true) → +1 Ultron-component
- Andromeda-gate-readiness flag set → +1 Andromeda-component

Canonical *the meter canonical-only-fills*; canonical: it does not canonical-empty. Even if a species is canonical-Cleansed-after-Migration-was-offered, the canonical-component is canonical-still-set (canonical: the canonical-handling-has-happened; canonical: the canonical-moral-outcome is canonical-tracked-separately for canonical-tier-prediction).

### 3.6 Canonical-tier-prediction-update

Canonical-tier-prediction canonical-recalculates on every canonical-meter-component update. Canonical: the canonical-tier-prediction is canonical *projected based on canonical-current-trajectory* — canonical: if all canonical-remaining-components canonical-fill-at-canonical-current-favorable-rate, the canonical-projected-tier is X. Canonical: the canonical-tier-prediction is canonical-not-locked-in until the canonical-slice-ending-evaluation.

### 3.7 Canonical-meter-UI-design

**Canonical display structure** (canonical Image-lane canonical-design):

```
+---------------------------------------+
|  SHOULD I STAY OR SHOULD I GO         |
|                                       |
|  Species:    [############----] 11/16 |
|  Crew:       [################] 7/7   |
|  Side-quests:[##########------] 17/25 |
|  Halia:      [################] OK    |
|  Ultron:     [----------------] -     |
|  Crossing:   [----------------] -     |
|                                       |
|  Total:    37/51                      |
|  Tier projection: ON TRACK FOR GOOD   |
|                                       |
|  [Tell me gaps] [Tell me done] [Close]|
+---------------------------------------+
```

Canonical color-coding:
- Components: canonical *warm-gold for filled*; canonical *cool-grey for unfilled*
- Tier-projection: canonical *warm-positive-gold* for Best/Great/Good; canonical *amber* for Successful-at-cost; canonical *grey* for Unsuccessful; canonical *cold-violet* for Disastrous (canonical Cleanser-palette callback — the Disastrous-tier-warning canonically *uses the Cleanser doctrinal color*)

**Canonical access UI** (canonical Design-lane canonical-implementation):
- Canonical *meter-icon-in-corner-of-screen* at all times (canonical-baseline-visibility)
- Canonical *clickable-or-keyboard-shortcut* to open the full meter
- Canonical *automatic-pop-up* on canonical-major-milestone-reached (e.g. canonical-tier-threshold-crossed — canonical *brief animation + canonical Forty-Seven brief-line*)

### 3.8 Canonical-Forty-Seven flair lines (for canonical-meter-state-changes)

When the canonical-meter canonical-updates due to canonical-flag-trigger, Forty-Seven canonical-announces briefly:

- **+1 species handled**: *"Species <name> canonical-resolved. Canonical-meter updates."* (canonical: brief; canonical not-intrusive)
- **+1 crew recruited**: *"Crew member <name> canonical-aboard. Canonical-meter updates."*
- **+1 side-quest favorable**: *"Side-quest <name> canonical-resolved favorably. Canonical-meter updates."* (canonical: small canonical-warmth-in-the-tone)
- **+1 side-quest unfavorable**: *"Side-quest <name> canonical-resolved unfavorably. Canonical-meter still-updates. Completion canonical-counts."*
- **Tier-projection-threshold-crossed-upward**: *"Steward. I am noting that the canonical-tier-projection has canonical-shifted-upward to <NEW_TIER>. I am, by my standards, canonical-pleased."*
- **Tier-projection-threshold-crossed-downward**: *"Steward. The canonical-tier-projection has canonical-shifted-downward to <NEW_TIER>. I am canonical-recording the canonical-shift without canonical-judgment."*

### 3.9 Canonical-Disastrous-tier-projection special case

When the canonical-meter canonical-projects-Disastrous-tier, Forty-Seven canonical-delivers a canonical-warning:

> *"Steward. The canonical-current-tier-projection is canonical-Disastrous. I am, by my standards, canonical-concerned. I have canonical-noted-the-canonical-trajectory. I will canonical-continue-to-track. — Steward. I should add: the canonical-Disastrous-tier-ending canonical-includes a canonical-specific narrator-line. The line is canonical-not-said-with-cruelty. The line is canonical-said-flat. The canonical-Furling-humor-doctrine canonical-respects-this. I am canonical-noting-this-for-your-canonical-information. Drink the tea."*

(canonical: this is canonical *Forty-Seven's third-canonical-warning of the canonical-three-canonical-warnings-in-the-slice* — canonical: the canonical-first canonical-warning was canonical-Forty-Seven's-canonical-fourth-wall-break #1 post-Fall; canonical-the-canonical-second canonical-warning was canonical-each canonical-individual-species-canonical-Cleanser-vote; canonical: the canonical-Disastrous-tier-warning is canonical-the-canonical-third-and-final-warning before canonical-the-canonical-Disastrous-ending fires)

---

## 4. Cross-canon integration

### 4.1 The canonical-awareness-events-and-the-meter

The canonical-awareness-events (§2) and the canonical-meter (§3) are canonical *both-driven-by-the-same-canonical-flag-state*. Canonical: when a canonical-flag is set, BOTH:
- Canonical-relevant-species' canonical-awareness-dialogs become canonical-available on next visit
- Canonical-meter-component canonical-fills (if applicable)

Canonical *implementation-note*: the canonical-flag-state is canonical-source-of-truth. Both features canonical-read-it; canonical-no-other-coupling needed.

### 4.2 Canonical-narrative-integration

The canonical-meter canonical-makes-the-Steward feel canonical *responsible-and-watched*. Canonical: the canonical-awareness-events canonical-confirm that canonical-the-galaxy-is-watching. Canonical: the canonical-meter canonical-confirms the canonical-Steward is canonical-tracking-the-watching. Canonical: together they canonical-create the canonical-Quiet-Resolution-experience — canonical *every-action-matters; every-species-knows; every-completion-counts*.

### 4.3 Canonical-callback-economy-integration

Per `callbacks-and-callforwards.md`, the canonical *"Drink the tea"* phrase canonical-migrates across canonical-multiple-species. The canonical-awareness-events canonical-extend this canonical-migration:
- Canonical-Vael-Souren canonical-says-it (per Cleanser awareness event 1)
- Canonical-Veshen canonical-says-it (per Taalo awareness event 1)
- Canonical-Mal-Dren canonical-says-it (per Utwig awareness event 1 + 3)
- Canonical-Whisk's-Stay-outcome canonical-line (per Lemmkin canon)
- Canonical-Halia (canonical original)

Canonical: by canonical-slice-mid-game, canonical *"Drink the tea"* is canonical-heard from canonical-five-different-species-and-faction-NPCs. Canonical: the canonical-callback-economy expansion is canonical-Halia's-canonical-cultural-legacy — canonical: she has canonical-shaped-the-canonical-slice-language with one phrase.

---

## 5. Cross-chat dispatches

### To Design (`HANDOFF_design_chat.md`)

**Net new content**:
- **~63 canonical-awareness-events** (21 species × 3 events) — canonical conditional-dialog-trigger-system + canonical-flag-state-table per `§2`
- **Canonical Should I Stay or Should I Go Meter** — canonical UI + canonical flag-tracking + canonical tier-prediction logic per `§3`
- **Canonical Forty-Seven meter-delivery dialog FSM** + canonical-Forty-Seven flair-lines for canonical-state-changes per `§3.8`
- **Canonical Forty-Seven Disastrous-tier-warning canonical-line** per `§3.9` (canonical: this is canonical-the-canonical-third-of-canonical-three-canonical-warnings in the slice)
- **Canonical meter-UI-design specs**: corner-icon + clickable-full-display + tier-projection-text + color-coding (warm-gold filled / cool-grey unfilled / cold-violet Disastrous-tier-warning)
- **Canonical meter-component-flag-list** (~30 flags total) for canonical-flag-tracking
- **Canonical *automatic-pop-up* on canonical-tier-threshold-crossed** behavior
- **Canonical *meter-updates-continuously* requirement**: every canonical-flag-state-change canonical-recalculates-meter-AND-canonical-tier-projection-AND-canonical-awareness-event-availability

### To Image (`HANDOFF_image_chat.md`)

**Canonical meter-UI visual design**:
- Canonical *Should I Stay or Should I Go* canonical-meter UI per `§3.7` mockup
- Canonical *corner-icon* (canonical-baseline-visibility; canonical-small; canonical-non-intrusive)
- Canonical *full-display panel* (canonical-clean; canonical-readable; canonical-warm-color-palette)
- Canonical *tier-projection text* with canonical-color-coding per tier
- Canonical *cold-violet for Disastrous-tier-warning* — canonical Cleanser-palette callback as canonical-visual-statement

### To Audio (`HANDOFF_audio_chat.md`)

**Canonical Forty-Seven meter-delivery voice direction**:
- Canonical *by my standards* delivery throughout
- Canonical *brief; not-intrusive* flair-line delivery on canonical-state-changes
- Canonical *priority-production* for the canonical-Disastrous-tier-warning canonical-line per `§3.9` (canonical: this is canonical-one-of-canonical-Forty-Seven's-canonical-most-important canonical-lines; canonical-the-canonical-Furling-humor-doctrine canonical-respect canonical-extends here)

**Canonical-awareness-event delivery direction** (canonical per-species):
- Canonical-each-species delivers their canonical-3-events in their canonical-baseline-voice-register
- Canonical-the-canonical-awareness-prefix-lines canonical-extend the canonical-existing-voice-direction per the species
- Canonical *priority-recordings*: Halia-died-in-Fall canonical-Vael-Souren-canonical-mourning-line (canonical Cleanser awareness event 3); canonical Arilou's *"we are sorry"* canonical-pause moment (canonical Arilou awareness event 2); canonical Coel Tessar's *"You have not canonical-rejected-me-for-it"* canonical-vulnerable-line (canonical Androsynth awareness event 3)

---

## 6. Open items / Aaron-call

- **Canonical-meter total-completion-points**: provisional 51 (16 species + 7 crew + 25 side-quests + 3 binaries). Aaron may want to revise (e.g. canonical-side-quest count; canonical-crew count if Forty-Seven canonical-counts differently).
- **Canonical-tier-prediction thresholds**: provisional per `§3.3` — canonical-Aaron may want to tune (e.g. canonical-Best at 51/51 + 95% vs. canonical-95% threshold).
- **Canonical-meter automatic-pop-up frequency**: provisional canon (canonical-pop-up on canonical-tier-threshold-crossed). Aaron may want canonical-additional triggers (canonical-pop-up on canonical-major-species-handled; canonical-pop-up on canonical-Halia-status-changed).
- **Canonical-awareness-event additions**: 63 events authored across 21 species. Aaron may want to add canonical-additional events for specific species OR canonical-remove events that feel canonical-implausible (canonical: canonical-Slylandro-knowing-about-Androsynth might feel canonical-too-magical; Aaron's-call).
- **Canonical-cross-meter-and-awareness-events callbacks** (canonical *"Drink the tea"* migration): canonical-listed at `§4.3`. Aaron may want canonical-other-callback-phrases to canonical-migrate.

---

## Cross-references

- [callbacks-and-callforwards.md](callbacks-and-callforwards.md) — canonical *"Drink the tea"* canonical-callback economy + canonical-Furling-humor-doctrine canon; canonical-this-doc canonical-extends-the-economy
- [halia-profile.md](halia-profile.md) — canonical Halia idioms; canonical *"Drink the tea"* migration source
- [loop-closing-content-pass.md](loop-closing-content-pass.md) — canonical 11 species canon; canonical-each-species' canonical-awareness-events build on the canonical-base canon
- [species-the-lemmkin.md](species-the-lemmkin.md) — canonical Lemmkin canon + canonical Convince Vote mechanic; canonical-meter-tracks-Lemmkin-outcome
- [utwig-quest.md](utwig-quest.md) — canonical Utwig canon + Mal-Dren character; canonical-3-Utwig-awareness-events authored
- [the-androsynth-refugees.md](the-androsynth-refugees.md) — canonical Coel Tessar character + from-afar theory; canonical-3-Androsynth-awareness-events authored
- [cleansers-as-ice-branch.md](cleansers-as-ice-branch.md) — canonical Vael-Souren canon; canonical-3-Cleanser-awareness-events authored
- [preservers-as-tree-branch.md](preservers-as-tree-branch.md) — canonical Lirin Pel-Sa canon; canonical-3-Preserver-awareness-events authored
- [crew-roster-redesign.md](crew-roster-redesign.md) — canonical 7-crew + Forty-Seven canon; canonical-meter-tracks-7-crew + canonical-Forty-Seven-delivers-the-meter
- [humor-pass.md](humor-pass.md) — canonical Forty-Seven *by my standards* register; canonical-meter-delivery uses this register
- (parallel chat) `the-endings.md` — canonical 6-tier endings system; canonical-meter-tracks-toward-Great-tier-or-better
