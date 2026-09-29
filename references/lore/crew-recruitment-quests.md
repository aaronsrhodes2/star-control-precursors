## Crew Recruitment Side-Quests

> The five Furling crew specialists (Pilot / Weapons Officer / Engineer / Medic / Navigator) are **gained through side-quests, not bought from the shop**. Each is a short side-mission — "along the way," not a central beat — that culminates in a recruitment moment. Crew NPCs come aboard, ride with the Steward for the slice's duration, contribute their passive bonus, and shift the slice's social texture. They are **not redshirts** — they don't have HP, they don't die.

> **Canonical FSM data — `tools/quest_inventory.csv`** (built from `tools/build_quest_inventory.py`). Each of the 5 crew recruitment quests has a full state-and-choice tree in the spreadsheet (quest_ids: `crew_pilot`, `crew_weapons_officer`, `crew_engineer`, `crew_medic`, `crew_navigator`). This doc carries the narrative *shape*; the spreadsheet carries the *dialog content and recruited_<role> flag plumbing*. When updating crew dialog: edit the ROWS in `tools/build_quest_inventory.py`, regenerate the CSV, and reflect the change here.

> **Slice contract (2026-05-17)**: each side-quest *grants* its specific crew module on completion. The module catalog (`src/scz/content/modules.py`) keeps these five modules `locked=True` until the corresponding quest flag is set. Lore-chat authors the side-quest content here; Design-chat wires the flag-gate. Quest-flag naming convention: `recruited_<role>` (e.g. `recruited_pilot`).

> **Tone**: these are *light-touch* side-quests — 2-4 beats each, no combat-mandatory. The point is **character** — Steward meets a Furling who has a reason to be in this story, demonstrates one specific thing the NPC was looking for, and the NPC asks to come aboard. Each quest is skippable; skipping leaves that crew slot bonus uncollected but never gates anything else in the slice.

> **Authoring order (matches priority of Design-chat dialog FSM work)**: Mraka (anchors the tutorial-extension recruit flow) → Mira-Rou (rides on Androsynth Beacon — Act 2) → Bren-Vor (rides on Distress Beacon witnessing — Act 2) → Yelena (background; recruit-able anytime post-customization-tutorial) → Tarven (Council-flavored, late-tutorial / early-Act-2).

---

### 1. The Sure-Foot — recruit **Mraka Yenn-Sa, Furling Drifter** (Pilot)

- **Module unlocked**: `crew_pilot` — top_speed +25, turn_rate +0.4, acceleration +30
- **Quest flag**: `recruited_pilot`
- **Hook location**: Mh-Lai Station — Mraka is in the docking-bay observation lounge after the Furlmart shakedown run
- **Prerequisite**: Furlmart pickup complete (Tutorial Beat 2-3); Scanner Mk III installed (proves the Steward has completed at least one cargo-bay handover)
- **Quest steps**:
  1. **Encounter**: Mraka introduces herself in the docking lounge. She watched the Steward's shakedown run from the observation deck. She has *opinions*. She is **kind** about the rough edges and **specific** about which ones cost the Steward time.
  2. **The Test (optional, skippable)**: Mraka asks if the Steward will fly a *Drifter's Circuit* — a low-stakes hyperspace navigation challenge through Mh-Lai's outer-marker buoys. Time-trial; failing has no consequence; succeeding grants Mraka's instant respect. (Implementation: a hyperspace minigame with three checkpoint-buoys near Mh-Lai. Either complete or skip is acceptable.)
  3. **The Story**: Whether the Steward flies the Circuit or skips it, Mraka asks to sit in the galley over tea. She tells the story of a Migration-bound Furling family — three generations on one Scout — who hired an inexperienced pilot and lost the ship to a quasispace miscalculation between systems. Two adults and four cubs. She has been a Drifter on the Mh-Lai docks ever since, watching new Stewards train, waiting for one she'd trust to ride with. *"The Sure-Foot is what the Drifter ancestors called the pilot whose route everyone followed. I am looking for one. I think I have found one."*
  4. **The Ask**: Mraka offers her service. No salary, no rank. *"I just want to ride along."* If accepted → `recruited_pilot` flag set → crew module unlocked.
- **Branches**:
  - **Recruit** (default) → `recruited_pilot = True`; Mraka aboard for the slice's remainder; ship handles tighter
  - **Decline** → Mraka thanks the Steward and walks away; flag remains False; can re-attempt at any later Mh-Lai docking
  - **Be cruel** (rare option, available only if Cleanser standing is high) → Mraka leaves Mh-Lai for another cluster; flag locked False permanently; small Persuader standing penalty
- **NPC voice notes**: warm; technical; conversational; uses *Sure-Foot* and *Drifter-circuit* without translating; speaks of the dead family by occupation, not by name (Furling grief-customs avoid the names until the year of mourning passes).

---

### 2. The Beacon Witness — recruit **Bren-Vor Telcas, Furling Aimer** (Weapons Officer)

- **Module unlocked**: `crew_weapons_officer` — primary_damage +2, primary_rate ×1.15, primary_accuracy ×1.1
- **Quest flag**: `recruited_weapons_officer`
- **Hook location**: Mh-Lai Station — Defender training-cohort barracks at the orbital ring
- **Prerequisite**: Distress Beacon obtained (Coel Tessar Beat — Tutorial Beat 6 onward); Persuader-faction standing ≥ 0 (not actively hostile)
- **Quest steps**:
  1. **Encounter**: After the Distress Beacon is in the Archive, Mh-Lai's Council asks the Steward to share the Beacon footage with the Defender training cohort — they will fly Cleanser support if the Council ever calls for one, and they need to know what they would be fighting *for*. Bren-Vor is in the audience.
  2. **The Aftermath**: After the screening, Bren-Vor approaches privately. He is a Defender trainee. His older sister Velt-Ra Telcas was killed three years ago in a Cleanser action against a sentient population the Council had not yet ruled on. The action was overturned on appeal; the trainees who fired the volley were rotated, not censured. He has been processing it. The Beacon has decided him. *"The Cleansers say they Eliminate to prevent the Others' notice. The Others arrive anyway. My sister was killed for a doctrine that does not work. I want off the Defender track."*
  3. **The Ask**: Bren-Vor formally requests transfer from Defender training to active-duty as the Steward's weapons officer, *"on a ship where Eliminating is not the first instinct."* If the Steward accepts, the transfer paperwork goes through the Persuader-faction commander; Bren-Vor's name moves to the Steward's roster.
- **Branches**:
  - **Recruit** (Persuader path) → `recruited_weapons_officer = True`; Bren-Vor aboard; Persuader standing rises modestly; Defender standing drops modestly
  - **Decline kindly** → Bren-Vor stays in Defender training and silences his doubt; flag remains False; can re-attempt at later Mh-Lai docking with Persuader-standing check
  - **Tell him to stay Defender** (Cleanser-aligned response, only available if Cleanser standing is high) → Bren-Vor's doubt is suppressed; he completes Defender training and fires the next Cleanser volley; flag permanently locked False; Bio-Archive logs the choice; small Defender standing bump
- **NPC voice notes**: clipped; precise; uses sister's full name once and never again; cites firing-solution geometry the way Mraka cites hyperspace navigation — fluently, with grief under the fluency.

---

### 3. The Mender's Inspection — recruit **Yelena Lwen-Tar, Furling Mender** (Engineer)

- **Module unlocked**: `crew_engineer` — hull_regen +0.5, module_repair_rate ×1.5, fuel_efficiency ×1.15
- **Quest flag**: `recruited_engineer`
- **Hook location**: Mh-Lai Station — Customization scene, after the Steward installs any module
- **Prerequisite**: Customization-tutorial complete (Tutorial Beat 5); Steward has installed at least one module from the shop or quest reward
- **Quest steps**:
  1. **Encounter**: Yelena walks into the Customization bay while the Steward is mid-install. She is **young** (early-career Mender), **direct**, and from the Unzervalt factory floor where every Furling Scout is built. Her mother runs the bay where this specific Scout was assembled. She has been waiting for it to come home modified. *"I have been reading your install-log from the dock telemetry. You have made one mistake. Would you like me to show you?"*
  2. **The Inspection**: Yelena walks the Steward through the Scout's interior — fur-wrapped consoles, the engine-bay's bioluminescent coolant manifold, the Bio-Architect cradle (if installed). She points out one *specific* maintenance oversight — too much tractor-beam cycle without a coil rest-period, or a sensor-array re-aim torque not properly stress-tested, or a fuel-tank gasket overdue for cycle replacement. **The maintenance is real and the fix is small** — the Customization scene's repair flag is set; the ship gains a small hidden bonus.
  3. **The Ask**: Yelena reveals she has been waiting for one of her family's Scouts to come back to Mh-Lai with field experience under its hull. The Migration-build queue has every Scout going to the Lift; one in twenty stays to fly. She wants to ride with the one that stayed. *"My mother built this hull. I want to see it work."*
- **Branches**:
  - **Recruit** → `recruited_engineer = True`; Yelena aboard; ship gains hull-regen + repair-rate
  - **Decline** → Yelena says she will keep watching from Mh-Lai; flag remains False; can re-attempt anytime
  - **Allow her to inspect but decline crew slot** → small hidden maintenance-fix bonus persists (Customization scene tracks `yelena_inspection = True`); but recruitment flag stays False
- **NPC voice notes**: young, direct, faintly **flirtatious** with the ship (not the Steward); refers to Scouts by serial number; sentences are short and end with confirmations. *"You see? It is correct now."*

---

### 4. The Bio-Architect's Apprenticeship — recruit **Mira-Rou Halve-Tel, Furling Bio-Architect** (Medic)

- **Module unlocked**: `crew_medic` — androsynth_shear_repair +1.0, crew_morale ×1.2
- **Quest flag**: `recruited_medic`
- **Hook location**: Coel Tessar encounter site (Androsynth refugee ship) — *during* the Distress Beacon quest
- **Prerequisite**: Mira-Rou opt-in to ride along, which the Steward can grant at any Mh-Lai docking after Tutorial Beat 5; the Beacon quest is then the recruitment event
- **Quest steps**:
  1. **Encounter (pre-quest)**: Mira-Rou meets the Steward at Mh-Lai. She is descended from the original Mycon biot-designer lineage — five generations of careful bio-engineering. She has been *reading about* dimensional-shear injuries from the Androsynth's transmissions, but has never worked a real case. She asks to **ride along** to the Coel Tessar encounter, not as crew yet, just as a Bio-Architect-in-training with an interest. The Steward agrees or declines.
  2. **The Field Work**: At the Coel Tessar encounter, Mira-Rou observes the Steward's deployment of the shear-repair fab pattern. If the Steward succeeds at stabilizing the refugees → Mira-Rou is in the field assisting; her notes inform the Furling Archive's permanent shear-repair record. If the Steward fails or skips → Mira-Rou's work is observation-only; she still learns.
  3. **The Ask (post-Beacon)**: After the Beacon is in the Archive, Mira-Rou approaches at the next Mh-Lai docking. She has decided. She wants to continue the work in the field, not at the Mh-Lai bio-labs. She asks to formally join the Steward's crew. *"My family designed life. I would like to keep some of it alive."*
- **Branches**:
  - **Recruit** (default if Beacon quest completed cleanly) → `recruited_medic = True`; Mira-Rou aboard; dimensional-shear repair capability + morale bump
  - **Decline her ride-along earlier** → Mira-Rou never witnesses the Beacon quest field-work; the recruitment beat does not surface; she stays at Mh-Lai
  - **Steward refused Coel Tessar aid** (failed Beacon quest by hostility, not field-failure) → Mira-Rou refuses to fly with the Steward; flag locked False permanently; small Persuader standing penalty; she leaves the cluster on the next Migration lift
  - **Steward fielded Coel Tessar with maximum Bio-Architect involvement** → Mira-Rou aboard *plus* the Mycon Mantle-Resonance Bio-Architect module gains a small efficiency bonus (the two Bio-Architects calibrate each other; tracked in `mira_calibrated = True`)
- **NPC voice notes**: thoughtful; biological-vocabulary-rich; refers to the Mycon biots with the same affection the Steward reserves for the Sure-Foot family; cites her ancestors' work matter-of-factly. *"My great-grandmother shaped the first biot pod. I am only continuing."*

---

### 5. The Star-Reader's Routes — recruit **Tarven Olwen-Sa, Furling Star-Reader** (Navigator)

- **Module unlocked**: `crew_navigator` — sensor_range +0.3, surface_sensor_range +0.05, autopilot_precision ×1.2
- **Quest flag**: `recruited_navigator`
- **Hook location**: Mh-Lai Station — Council Archives wing, after the Steward has visited at least 3 different star systems
- **Prerequisite**: 3+ systems visited (the basic exploration tutorial is complete); Steward has been entered into the Mh-Lai Council Archives' active-Steward log
- **Quest steps**:
  1. **The Summons**: A Council clerk pages the Steward to the Archives for a Stellar-Drift Briefing. The Steward's recent system-visits have crossed routes that *prior Stewards* in the same job flew. Tarven hosts the briefing.
  2. **The Reading**: Tarven walks the Steward through the prior-Steward history of each visited system — what was found, what was missed, what the prior-Stewards left undocumented. The briefing is **lore-rich** — small flavor anecdotes about Stewards-Past flesh out the slice's sense of historical depth. (Implementation: this is a dialog beat with up to 5 mini-vignettes, one per visited system; data drives off the `game.visited_systems` set.)
  3. **The Reveal**: Tarven shows the Steward a chart — every Furling Steward who has flown this Steward's *specific assigned cluster* over the past 200 years. There have been **seven prior Stewards**. Tarven has read every one of their logs. He has a *theory* about a system the prior Stewards all *almost* visited but never did. (Implementation: the system is one of the optional-encounter systems still un-flagged at the time of the briefing — picked dynamically.)
  4. **The Ask**: Tarven offers to ride along as ship-Reader. *"I have read where every prior Steward of this cluster went. I would like to read where you go, in real time, on the ship's bridge, rather than ten years later in a transcript."* He acknowledges he is **junior** and that his offer is unusual.
- **Branches**:
  - **Recruit** (default) → `recruited_navigator = True`; Tarven aboard; modest sensor bonuses + tighter autopilot
  - **Decline kindly** → Tarven returns to the Archives; flag remains False; can re-attempt at later Mh-Lai docking after additional system-visits
  - **Recruit after visiting Tarven's prediction system** → if the Steward visits Tarven's hinted-at system *before* the recruitment ask, the recruitment beat is enriched (Tarven reads the encounter into the Archive while it happens) and the navigator module gains a small extra bonus on `surface_sensor_range` (`tarven_verified = True`)
- **NPC voice notes**: bookish; uses prior-Stewards' formal Furling titles with full clan suffixes; tends to begin sentences with *"In the seventh decade of the Steward Iren-Vor's tenure—"* and lose track of the original question. Charming. Slightly intimidated by being on the bridge.

---

## Cross-quest notes

- **All five quests are skippable.** The slice runs to completion with zero crew recruited; the player simply forgoes the passive bonuses. No main-story gate is conditional on any crew recruitment.
- **All five quests trigger on Mh-Lai docking** (or, for Mira-Rou, on Coel Tessar approach) — they're **opportunistic side-content**, not actively pushed at the player. The hook surfaces when the prerequisite is met; the player can engage or skip.
- **Voice ownership**: each NPC has their own voice profile (fields above feed the LLM-renderer's per-NPC prompt). Design chat wires the dialog FSM; the recruitment beat is the FSM's terminal state with the side-effect of setting the `recruited_<role>` flag.
- **Bio-Archive integration**: each recruited crew NPC also adds a short bio-entry to the Bio-Archive's "Furling Crew" category (1-paragraph in-fiction summary in the Steward's voice — the Steward's notes about who they brought aboard and why). Lore-chat will author these entries when the Bio-Archive `archive_entries.py` is implemented (Design-chat's pending task).
- **Failure / refusal**: the only *permanent* recruitment-failures are the cruel-decline branches (Mraka, Bren-Vor, Mira-Rou). All other declines leave the recruitment available on a later visit. This is the slice's social-fabric texture: most Furlings forgive a first decline; a *cruel* decline is remembered.

## Backstories, Personalities, Side-Quests & Bonus Progression

> **Canon appended 2026-05-17 (Skippy creative pass).** Each named crew NPC now has: a fuller backstory (beyond the recruitment-hook teaser), a personality profile (for dialog FSM authoring), a **goalpost-triggered follow-up side-quest** that develops their arc mid-slice, and a **pre/post-quest bonus progression** (post-quest bonus unlocks after the side-quest resolves favorably). Side-quest FSMs are in `tools/quest_inventory.csv` (quest_ids `crew_<role>_side_quest`).
>
> **Pre/post-quest bonus design rationale**: each recruited crew gives the Steward an *immediate* set of stat-deltas (the pre-quest bonus). Completing their follow-up side-quest *favorably* unlocks an enhanced bonus set — typically the pre-quest bonus PLUS a unique active ability + an extra passive. This rewards the player for engaging with crew-personal content rather than treating crew as fire-and-forget stat-bumps.

---

### 1. Mraka Yenn-Sa — Furling Drifter (Pilot)

**Backstory (full)**: Born to a hyperspace-racing family on Mh-Lai's outer-marker dock-ring; trained as a Drifter from age 10. By 30 she was on the cluster's professional Drifter's Circuit. By 35 she had won three cluster-cup races. Then a Migration-bound Furling family — the **Olwen-Veth** clan, three generations, two adults and four cubs, all aboard a single Furling Scout — hired a pilot Mraka had personally tested and certified as competent. He wasn't. He missed a quasispace-vector calculation between Sigma Tauri and Beta Lyrae and lost the ship to a fold-mismatch event. The family died in the dimensional shear. Mraka attended every funeral. She quit the Circuit the day after the seventh funeral. She has been a Drifter on the Mh-Lai docks ever since, watching new Stewards train, waiting for one she'd personally trust to ride with. She is **40 Furling years old** at slice start.

**Personality**: warm, technical, watchful. Notices everything about how a Steward flies (and tells them honestly). Refers to deceased Furlings by occupation, not name, until the year of mourning passes — *"the Olwen-Veth pilot"* and not *"Var-Sen Olwen-Veth"*, even though she knew his name perfectly well. Uses the verb-form *"to drift-fly"* (intransitive) for hyperspace navigation done well; *"to drift"* alone means poorly. Has dry, kind humor — *"You drifted that approach. That's not a compliment."*

**Goalpost trigger**: Steward visits 5+ systems while Mraka is aboard.

**Side-quest sketch — "The Last Race"** (`crew_pilot_side_quest`):
A distress beacon picks up the call-sign of **Soren Kel-Var** — Mraka's former Drifter's Circuit rival, mid-Migration with a Furling family aboard his Scout, drive-failed in an anomaly zone at the cluster's edge. Mraka has *unfinished feelings* about Soren (he was the pilot the Olwen-Veth clan considered hiring before Mraka recommended otherwise; he was furious; they have not spoken in 12 years). She wants to detour. Branches: **tow him to safety** (slow exposure to ambient Other-ripples; tense) / **repair Soren's drive in-place** (best outcome if Yelena Lwen-Tar is also aboard — they collaborate; deep bond forms) / **leave Soren** (Mraka's grief turns to anger; eventually quits the crew, permanently).

**Pre-quest bonus** (immediate on recruitment):
- `top_speed: +25`
- `turn_rate: +0.4`
- `acceleration: +30`

**Post-quest bonus** (unlocked on favorable Last Race resolution):
- All pre-quest deltas RETAINED
- NEW **"Evasive Burst"** active ability — once per combat fight, the ship instantly burst-evades ~200 units in any direction with brief invulnerability frames during the burst. *"Drift-fly the corner. Don't engage it."*
- NEW **"Hyperspace Corridor Intuition"** passive — Mraka's race-circuit-honed knowledge of cluster fold-vectors reduces hyperspace fuel cost by 20%. She *knows* the cheap routes.

---

### 2a. Forward — Thinn Rebel (Weapons Officer; ALTERNATIVE to Bren-Vor)

> **Canon added 2026-05-17** per Aaron's brief: *"make one of our crew one of the Thinn, our weapons officer. Lots of 2D-related jokes to plumb here."* Forward is **mutually exclusive with Bren-Vor Telcas** — the player can recruit ONE weapons officer; the other recruitment hook deactivates once the slot is filled. Two thematically opposite weapons officers; player agency at the slot level.

**Backstory (full)**: Born to the Thinn troupe at Spire. Canonically Thinn — 2D ribbon-body, zero width, all the species traits per [species-the-thinn.md](species-the-thinn.md). **Realized in early adulthood that the Edge-Align doctrine was wrong.** Not by complex argument (his species's canonical brain-volume-zero cognition prevents that) but by sincere geometric observation: *"If we are facing edge-on to the Others when they arrive, we will not see them. I would like to see them."*

He argued with the troupe. The troupe pointed out (correctly per their canon) that *the doctrine does not require seeing them*. Forward responded that *he* required seeing them. The troupe pointed out that *he* is *we* and that *we* do not require seeing them. Forward used a singular pronoun — *"I"* — for the first time in Thinn species history.

The troupe was scandalized. Singular pronouns are a cognitive impossibility for Thinn collective-substrate cognition; using one is *both linguistic heresy AND apparently medically inadvisable*. Forward did it anyway. **The first Thinn singular self in 50,000 years.**

He was shunned. He left Spire on a Furling traveler's vessel ~3 years before slice. Made his way to Mh-Lai docks. Has been waiting for a Steward willing to take *a rebel-Thinn-with-singular-pronouns* aboard. He is **canonical age unknown** (Thinn ages are collective-troupe-scale; Forward has no troupe; he refuses to be older or younger).

**His motto** (canonical line; preserved verbatim from Aaron):
> *"Face them head on, but keep your eyes pointed at them at a conceptually impossible angle forward at a 90 degree angle perpendicular our reality, and into to this mythical 'space' everyone keeps talking about, and we shall survive."*

**Personality**: dryly philosophical (Thinn voice register) + canonically Thinn-dumb (per species canon — zero brain volume; cannot revise plans; sincere geometric observations delivered as deep wisdom that the Furlings find *quietly hilarious*) + the **sharp** edge developed from being ostracized + cheerful unawareness that his own Forward doctrine is *also* probably wrong. His humor is *sincere*. He does not realize he is being funny. The Steward's wit-options with him work because *Forward thinks the Steward is praising him* every time.

**Canonical Forward voice tics**:
- Uses singular *"I"* relentlessly (canonical rebellion marker)
- Refers to other Thinn as *"they"* (rejection of we-who-collective)
- Says his name as just *"Forward"* — never *"We-Who-Face-Forward"* or any multi-word version. *"I am Forward. The other Thinn say my name with five additional words. I do not require them."*
- Talks about his "perpendicular reality" — a fourth-dimensional space he claims to perceive ("the space everyone keeps talking about"). Furling xenophysiologists have *measured* this and concluded he *does* perceive something but the something *may not be a fourth dimension*; more likely a confused attempt to model 3D space using 2D cognition. **Forward does not know the difference.**
- Has *strong opinions* about firing solutions: he aims at the *center of mass of his target plus or minus his entire width, which is zero, so just the center of mass*
- Cannot be hidden from by standing edge-on. He sees edge-on targets as *plain as anyone* because he is also edge-on; the trick does not work on him
- Cheerful about his species's probable extinction *AND his own probable contribution to a slightly different probable extinction*

**Why he wants to be a weapons officer**: he believes the Others *can* be fought and he wants to fight them. Forward is the slice's clearest example of *brave-but-wrong-yet-still-useful*. He is genuinely good at aiming — his 2D nature gives him a uniquely flat perspective on combat geometry — but his strategic doctrine is naive in the same way his species's is.

**Goalpost trigger for recruitment**: Steward has visited Spire (the Thinn homeworld) AT LEAST once. After the Spire visit, the next time the Steward docks at Mh-Lai, Forward approaches them at the docking pad with a polite request. (If Bren-Vor has already been recruited, Forward's recruitment hook does NOT surface — the slot is taken.)

**Recruitment dialog sketch** (quest_id `crew_weapons_officer_thinn`):

> **Forward** *(canonically 2D — standing forward-facing toward the Steward, NOT edge-on; iridescent teal-violet-gold ribbon-body)*: Furling. Hello. I am Forward. I have been waiting. I have a question.
>
> **Steward**: [several options including the canonical *"Aren't you supposed to be edge-on?"*]
>
> **Forward**: I am not supposed to be edge-on. I refuse to be edge-on. My motto: *"Face them head on, but keep your eyes pointed at them at a conceptually impossible angle forward at a 90 degree angle perpendicular our reality, and into to this mythical 'space' everyone keeps talking about, and we shall survive."* I require a ship. I would like yours. I am a good aimer. *(Beat.)* Are you laughing? You may laugh. I will not be insulted. I have not understood why Furlings laugh at me since I left Spire. I have decided this is acceptable.

**Pre-quest bonus**:
- `primary_damage: +2.0`
- `primary_rate: ×1.1`
- `primary_accuracy: ×1.2` *(slightly higher than Bren-Vor's; Forward's 2D nature is genuinely good for aim-geometry)*
- `crew_morale_quirk: +0.5` *(novel — the crew finds Forward unintentionally hilarious; baseline morale +5%)*

**Side-quest sketch — "Forward Says Goodbye"** (`crew_weapons_officer_thinn_side_quest`):
The trigger fires when the Steward has visited Spire WITH Forward aboard at least once + 5+ total systems visited. Forward asks to return to Spire to confront his old troupe one last time. He has Furling data (per his time aboard) that he believes proves Edge-Align won't work. He wants to share it.

Branches:
- **Confront the troupe with the data** (best path): the troupe receives the data; per canon they *agree* the data is correct AND continue with Edge-Align anyway (the Thinn cognition limitation). Forward is *frustrated but resigned*. Then, unexpectedly: TWO Thinn from the troupe choose to leave with the Migration. They believe in Forward's Forward-doctrine. Forward gains a tiny *collective* — three Thinn aboard the Furling Scout. Mixed terminal: Thinn-majority stays (Pending) + 3-Thinn diaspora (Migrated).
- **Quietly visit Spire without confrontation**: Forward says goodbye to his old troupe. They acknowledge him *as a fragment of we-who-watch* despite his singular pronouns. He cries — a Thinn-style ripple of color across his entire body. The Furlings learn what Thinn grief looks like. No troupe migrants but Forward gains *peace*.
- **Skip the side-quest** (decline to detour): Forward carries the grief of not having returned for the rest of the slice. Bonus locked.

**Post-quest bonus** (favorable resolution):
- All pre-quest deltas RETAINED
- NEW **"Perpendicular Aim"** active ability — once per fight, Forward perceives the enemy's next 0.5 seconds via his canonical "perpendicular reality" (whatever it actually is, it works). The next shot fires at the *predicted* enemy position with 95% accuracy regardless of enemy maneuvers. Visual: a faint chromatic flash across Forward's body as he aims, then the shot lands as if the enemy *teleported into position for him*.
- NEW **"2D Witness"** passive — Forward's flat perspective gives the ship a small dodge-bonus against enemies firing from directly ahead (3% damage reduction from forward attacks). Canonical: *"I have an aim and I have an edge-on. I choose the aim. But I still have the edge-on if I want it."*
- **(Confront-troupe-with-data branch only)** ADD `forward_collective_aboard=True` — the 3-Thinn diaspora ride on the Furling Scout for the rest of the slice. Forward has *a we* again for the first time. Visible in Common Room (his alcove now has three Thinn ribbon-bodies; Forward forward-facing, the other two edge-on per their preserved doctrine). Adds banter complexity in the Common Room — Forward and his diaspora argue *constantly* about the doctrine they share.

**Canonical 2D jokes the Steward will encounter** *(curated set — Lore-authored for Forward dialog throughout slice)*:

- *"I aim at things. Things in three dimensions. It is a constant learning experience."*
- *"My firing solution is: the target's center of mass, plus or minus my entire width — which is zero — so just the center of mass. It is a clean solution. I am proud of it."*
- *"You cannot hide from me by standing edge-on. I respect the attempt. I would also still shoot you. I am sorry. We are both 2D. I see you."*
- *"The Furlings call me 'turn around so we can see you' which is funny because I am already facing them. I am always facing everyone. I am 2D. I am facing the wall behind me at the same time. I am also facing the floor. The Furlings are tall and the floor is short; this confuses them."*
- *"My troupe believes facing sideways will save them. I believe facing forward will save us. Both of us are probably wrong. At least I will see the predator."*
- *"Bren-Vor would have made a good weapons officer. I have read his file. He had grief. I have geometry. The Steward picked one of us. Both are valid. I am also better at aim, I think, though I have not measured."*

### 2b. Bren-Vor Telcas — Furling Aimer (Weapons Officer; original)

**Backstory (full)**: Born on Mh-Lai to a Defender-aligned military family (his father served, his mother is a Defender quartermaster). Older sister **Velt-Ra Telcas** entered Defender service at 22 and was assigned to a Cleanser-support patrol cohort. Three years before the slice begins, that cohort fired on a population the Furling Council had *not yet ruled on* — a marginal-sentient cluster of pre-Migration Yehat that some Cleansers argued were already past the threshold. Velt-Ra was the firing officer. The action was overturned on appeal eight months later; the trainees who fired were rotated to other duties, not censured. Velt-Ra was rotated. She killed herself eleven days after the rotation. The official cause-of-death is listed as *"complication from rotation-stress."* Bren-Vor knows that's a lie. He has been **23 Furling years old** for two of those years; he is **24 at slice start**.

**Personality**: clipped, precise, deeply controlled. He uses Velt-Ra's full name *exactly once* per conversation and then refers to her as *"my sister"* for the rest. He cites firing-solution geometry fluently — *"32-degree lead on a 0.8c target, three-shot grouping, you can hold that with my training"* — and the fluency holds when he discusses Velt-Ra's death. The grief is *under* the fluency, not visible in it. Drinks Mh-Lai station-tea black; eats sparingly. **Will not laugh, but will smile small** when the Steward earns it.

**Goalpost trigger**: Steward has either (a) been involved in a Cleanser-aligned choice in any quest, OR (b) Cleanser-faction-standing has risen ≥ 1 point.

**Side-quest sketch — "The Aimer's Verdict"** (`crew_weapons_officer_side_quest`):
Council convenes a hearing on Captain **Karol-Vere Belt-Tar** — the Cleanser officer who *authorized* the action that killed Velt-Ra (Bren-Vor's commanding officer, technically not Velt-Ra's direct superior). The Council is reviewing his proposed *promotion* to Cleanser-faction leadership. Bren-Vor wants to attend. The Steward attends with him. Branches: **cross-examine Karol-Vere** (Bren-Vor presents evidence the Council didn't see, including a journal-entry Velt-Ra wrote that names the cover-up; Karol-Vere is demoted; Bren-Vor finds peace) / **let it go** (Bren-Vor's grief turns to anger; he stays aboard but distant) / **advocate FOR Karol-Vere** (Cleanser-aligned Steward path; Bren-Vor leaves the crew permanently and the Bio-Archive logs the action).

**Pre-quest bonus**:
- `primary_damage: +2.0`
- `primary_rate: ×1.15`
- `primary_accuracy: ×1.1`

**Post-quest bonus** (favorable cross-examine resolution):
- All pre-quest deltas RETAINED
- NEW **"Precision Focus"** active ability — once per fight, the next shot fires at 3× damage but 1/3 the normal rate; visible *aimer's calm* effect on screen (time slightly slows during the aim window)
- NEW **"Ethical Targeting"** passive — Steward gains +1 Persuader standing per combat where they *spare* an enemy (don't fire after the enemy ship disengages or surrenders). Bren-Vor logs the restraint personally and reports it to Council; the standing rise is mechanical.

---

### 3. Yelena Lwen-Tar — Furling Mender (Engineer)

**Backstory (full)**: Born and raised on the **Unzervalt** factory floor — the canonical Furling Scout assembly plant on Mh-Lai's third moon. Her mother **Mev-Tar Lwen-Tar** is the *senior assembly chief* for the Scout production line and personally oversaw the welding of the Steward's specific hull. Her father **Korven Lwen-Tar** was a Mender who died in a routine factory accident when Yelena was 8 (a coolant-line rupture; he saved three workers by closing the bulkhead manually before he could evacuate). Yelena trained as a Mender from age 12, partly to *honor* her father, partly because she genuinely loves the work. By 22 she had her Mender's certification. By 25 — slice start — she is *one of the youngest certified Mh-Lai Menders* and is *itching* to fly with one of "her" Scouts in the field. She is **25 Furling years old**.

**Personality**: young, direct, faintly *flirtatious with the ship* (not the Steward). Refers to the Furling Scout by her serial-number — "*Twelve-Forty-Eight*" — in casual conversation. Re-tightens loose ship components on autopilot, even mid-conversation. Wears a tool-belt with seventeen specialized tools she can name in alphabetical order. *"You see? It's correct now."* Quietly intense about the work; her father's death is rarely mentioned but always present. Likes the Mraka of the same age-cohort (both early-career professionals).

**Goalpost trigger**: Steward has installed 4+ modules total (any modules) while Yelena is aboard.

**Side-quest sketch — "The Last Hull"** (`crew_engineer_side_quest`):
News arrives from Unzervalt: the factory floor is being decommissioned in 30 days. Yelena's mother Mev-Tar is leading the team building **the last Furling Scout that will ever be built in this galaxy** (after Migration there will be a different shipyard in Andromeda, but Unzervalt's specific tooling and traditions end here). Yelena wants the Steward to attend the launch ceremony. She has *one final family-engineered module* she wants to install on the Steward's ship — a hull-resonance dampener her father partly designed before he died, that she has completed in his honor. Branches: **help her install it** (technical sequence; deep bond forms; the Lwen-Tar family adopts the Steward informally; *"Captain, Twelve-Forty-Eight has carried you well — now she carries us both"*) / **let her install it alone** (smaller bonus; the family is still grateful but the Steward missed the moment) / **refuse to detour** (Yelena disappointed; bonus locked).

**Pre-quest bonus**:
- `hull_regen: +0.5`
- `module_repair_rate: ×1.5`
- `fuel_efficiency: ×1.15`

**Post-quest bonus** (favorable last-hull resolution):
- All pre-quest deltas RETAINED
- NEW **"Field Overhaul"** active ability — once per slice, Yelena performs a full repair AND installs ONE module without requiring Mh-Lai docking (the canonical Mh-Lai install gate is bypassed exactly once; canon-justified: her mother's senior-Mender authority transfers temporarily). The module installed via Field Overhaul is *permanent* and can be uninstalled later normally.
- NEW **"Hull Intuition"** passive — Yelena's ship-knowledge anticipates incoming hull damage; the ship takes 10% less damage from any combat or environmental source.

---

### 4. Mira-Rou Halve-Tel — Furling Bio-Architect (Medic)

**Backstory (full)**: Descendant of the original Mycon biot-designer lineage. Her great-grandmother **Olune Halve-Tel** shaped the first Mycon biot in the slice's deep past (~700 years ago). Her grandmother **Sevreth Halve-Tel** trained the second wave of biot terraformers. Her mother **Klesh Halve-Tel** is currently a senior Bio-Architect at the Mh-Lai Council medical-research wing. Mira-Rou herself was the *first Halve-Tel to break the tradition* — she trained in dimensional-shear injury research instead of biot-design, partly because the Mycon biots had reached a stable plateau and there was less work, partly because she found the Androsynth medical literature *fascinating*. She is **27 Furling years old** at slice start. She has been waiting four years for a Steward to recruit her so she can do field-work on actual dimensional-shear cases.

**Personality**: thoughtful, biological-vocabulary-rich, *patient with everyone except herself*. She'll explain dimensional-shear injuries in painful technical detail; she'll also quietly correct her own diagnostic predictions when proven wrong. Cites her ancestors matter-of-factly — *"My great-grandmother shaped the first biot pod. I am only continuing"* — without false modesty or false pride. **Carries a small biot-fragment in a sealed glass amphora** as both medical equipment and family heirloom; the fragment is a descendant of Olune Halve-Tel's original work.

**Goalpost trigger**: Steward has completed Coel Tessar Distress Beacon quest favorably (refugees stabilized) AND visited a Mycon biot site.

**Side-quest sketch — "The Deep Child's Cradle"** (`crew_medic_side_quest`):
Mira-Rou's biot-fragment (the family heirloom) begins emitting the **FIRST_WHISPER pattern** — independently of any field Mycon site. The biot fragment is *waking up*. Mira-Rou is terrified and fascinated. She tells the Steward: *"My ancestors made these. My ancestors did not anticipate this. The whisper is in my pocket and I do not know what to do."* Travel to a quiet system; consult with the local Mycon biot collective; the choice is not field-Mycon but **this specific heirloom**: branches: **suppress the heirloom** (Mira-Rou with heavy heart accepts; preserves Halve-Tel tradition; bonus unlocked) / **allow the heirloom to wake** (Mira-Rou becomes the *first Furling biologist to host a sentient biot*; the heirloom develops into a new tiny sentient being she names *Sevreth's Child* after her grandmother; bonus unlocked + special bond) / **Cleanser action** (destroy the heirloom; Mira-Rou refuses and leaves the crew permanently).

**Pre-quest bonus**:
- `androsynth_shear_repair: +1.0`
- `crew_morale: ×1.2`

**Post-quest bonus** (favorable Deep Child's Cradle resolution):
- All pre-quest deltas RETAINED
- NEW **"Bio-Signature Dampening"** active ability — when activated, the ship's biological-cognition-signature is reduced by ~50% for 30 seconds. Useful in late-slice Others-approach scenes where the player needs to slip past Others patrols. Canonical: Mira-Rou's biot-knowledge allows masking the Steward's cognitive flare temporarily.
- NEW **"Tractor Extension"** passive — the Mantle-Resonance Bio-Architect's `tractor_radius_bonus` is extended by another +20% (stacks with Mantle-Resonance's own bonus). Mira-Rou's biot-tuning makes the tractor reach further.
- **(Allow-emergence branch only)** ADD **"Sevreth's Child"** — a new "dialog character" the Steward can converse with on the bridge; provides per-encounter morale variability and unique commentary on Mycon-related quests.

---

### 5. Tarven Olwen-Sa — Furling Star-Reader (Navigator)

**Backstory (full)**: Born to a clerical Mh-Lai Archives family. Trained as an Archivist from age 11. By 19 he had specialized in **stellar-drift records** — the geometric history of how stars have shifted position across Furling-era millennia. By 23 he had read every prior-Steward log in the Council Archives for the slice's specific cluster (seven prior Stewards over 200 years). By 24 — slice start — he was a *junior* Archivist with deep specialty in this particular cluster, *itching* to ride along on the bridge of one of the cluster's active Stewards. He is **24 Furling years old**. He is also **slightly intimidated** by being on a working ship — his entire career has been pure-text Archives work, and the Furling Scout's bridge is loud and fast in a way Archives reading rooms are not.

**Personality**: bookish, charming, *slightly intimidated*. Begins sentences with formal Furling clan-titles — *"In the seventh decade of the Steward Iren-Vor's tenure—"* — and loses track of the original question. Carries a portable log-reader at all times. Refers to prior Stewards by *full clan suffix*, never first-name. Has *very strong opinions* about which prior-Stewards were the best at their job (he ranks Iren-Vor highly, Halve-Kor mid-pack, the Furling-name-erased-by-mourning-customs-third-Steward as *"underrated, in my opinion"*). Drinks tea relentlessly.

**Goalpost trigger**: Steward has visited 8+ systems while Tarven is aboard.

**Side-quest sketch — "The Erased Logs"** (`crew_navigator_side_quest`):
Tarven discovers an inconsistency — Steward **Iren-Vor Olwen-Veth** (the 7th Steward of this cluster, ~50 years before slice; *of the canonical Olwen-Veth clan that Mraka mourns*) erased part of her own logs in her final year of service. There is a 14-month gap in her stellar-drift entries that *makes no sense* — she was clearly flying, she was clearly visiting systems, and yet the entries are *not there*. Tarven hypothesizes the erasure covers an *early Others-related discovery* she didn't report. He wants to investigate. The trail leads to a fringe system; Tarven cross-references with Iren-Vor's nav-trace; they find a hidden Iren-Vor data-cache deep in the system's outer belt. The cache reveals: Iren-Vor witnessed an *early Others incursion* — a faint dimensional ripple, well below the threshold the Council would later identify — and chose to erase it because *"the Council is not ready to act on this; reporting will trigger panic; I will record this privately and bring it forward when the moment is right."* The moment never came; Iren-Vor died in the Olwen-Veth fold-mismatch accident before she could share the data. Branches: **report the find to Council** (Council formally acknowledges the early-warning; bonus unlocked; Persuader and Hider standing rise) / **keep the secret personally** (the Steward and Tarven share the discovery; bonus unlocked with different flavor — *secret-knowledge bonus to dialog-context-depth*) / **destroy the cache** (the past stays buried; Tarven horrified; he leaves the crew permanently).

**Pre-quest bonus**:
- `sensor_range: +0.3`
- `surface_sensor_range: +0.05`
- `autopilot_precision: ×1.2`

**Post-quest bonus** (favorable Erased Logs resolution):
- All pre-quest deltas RETAINED
- NEW **"Deep Archive Scan"** active ability — once per slice, reveal *all hidden encounters and anomalies* on the starmap. Canonical: Tarven's research surfaces prior-Steward annotations the player wouldn't otherwise see.
- NEW **"Prior Steward Intuition"** passive — `dialog_context_depth: ×1.3` — Tarven's deep-archive knowledge enriches every Steward conversation (the LLM-renderer has access to prior-Steward context).
- **(Report-to-Council branch only)** also ADD `iren_vor_archive_unlocked = True` — a Bio-Archive entry "Others — early ripples (Iren-Vor's hidden record)" is added, completing the slice's canonical Others-detection chronology.

---

## Crew side-quest cross-canon

- **Mraka's Last Race + Yelena's Last Hull** can intersect — if BOTH are recruited AND both side-quests are accepted, Yelena offers to help Mraka repair Soren's drive in-place. This produces a *best outcome* for the Last Race quest where Soren's family survives intact AND Mraka + Yelena form a bonded working pair (small ongoing morale bonus).
- **Tarven's Erased Logs + Mraka's Last Race** also intersect — Iren-Vor is canonically *of the Olwen-Veth clan* (Mraka's deceased-family-friends). If Mraka's quest is complete, Tarven's quest delivers an extra emotional beat: Iren-Vor was *related to* the Olwen-Veth pilot Mraka mourned; the prior-Steward and the lost-family-Mraka-tried-to-protect were cousins. Both Mraka and Tarven react to this revelation; small additional dialog content unlocks.
- **Mira-Rou's Deep Child's Cradle + Bren-Vor's Aimer's Verdict** — if both crew are aboard AND both side-quests reach Cleanser-aligned decision points, the Steward's choices become *visibly weightier* — both crew watch the same decisions and both judge the Steward, separately, by their separate ethical lenses (Bren-Vor wants Cleanser restraint; Mira-Rou wants biot-protection). Minor cross-character dialog beats.

## Implementation backlog (Design chat)

- 5 new quest FSMs in `tools/quest_inventory.csv` (already authored — see quest_ids `crew_<role>_side_quest`)
- 5 new "promoted crew" module variants (or equivalent post-quest-bonus mechanic) — Design decides whether to (a) add `crew_<role>_promoted` modules with enhanced deltas + abilities, (b) extend `Module` with `promoted_deltas` and a `promoted_flag` field, or (c) implement as a scene-layer post-quest-bonus filter
- New active-ability framework needed for the special abilities (Evasive Burst, Precision Focus, Field Overhaul, Bio-Signature Dampening, Deep Archive Scan) — these need a unified "crew special ability" mechanic with cooldown / once-per-fight / once-per-slice semantics. **Single largest Design-side change implied by this work.**
- Cross-quest intersection logic (Mraka+Yelena, Tarven+Mraka, Mira-Rou+Bren-Vor) — bonus dialog content authored in Lore; Design wires the cross-flag-check
- Voice profile authoring for Soren Kel-Var, Karol-Vere Belt-Tar, Mev-Tar Lwen-Tar, the deceased-prior-Steward Iren-Vor (if Tarven plays a recording) → all flagged in `HANDOFF_audio_chat.md`
- Portrait + avatar authoring for the same new NPCs → flagged in `HANDOFF_image_chat.md`

## Slice implications (for Design chat)

- **Five new dialog character factories** needed in `src/scz/dialog/characters.py`: `mraka_yenn_sa()`, `bren_vor_telcas()`, `yelena_lwen_tar()`, `mira_rou_halve_tel()`, `tarven_olwen_sa()`. Each carries a `# TODO_AVATAR: <NPC name>, Furling <Role-Title>` marker for Image-chat pickup.
- **Five recruitment side-effects** to wire on the FSM terminal states: `recruited_pilot = True`, `recruited_weapons_officer = True`, etc. Each grants the corresponding module from `MODULES` registry by inserting it into `game.uninstalled_modules`.
- **Five quest-flag gates** to add to the module-customization filter: modules `crew_pilot` / `crew_weapons_officer` / `crew_engineer` / `crew_medic` / `crew_navigator` should remain `locked=True` until the corresponding `recruited_<role>` flag is True. Currently they're filtered out by `locked=True`; once the flag is set, `purchasable_modules` should return them. Design-chat to decide whether to add an `unlock_flag` field to `Module` or filter at the scene layer.
- **Mraka's Drifter-Circuit minigame** (Step 2 of her quest) is the only one with new gameplay scope. The other four quests are pure dialog FSM. If the Circuit minigame is too much scope, drop it — Mraka can simply observe the Furlmart shakedown and approach in the lounge. The recruitment beat is what matters.
- **Tarven's prior-Stewards reading** (Step 2 of his quest) needs flavor-anecdote content keyed by system_id for the slice's optional-encounter systems. Lore-chat will author the anecdotes when Design-chat surfaces the system list.
