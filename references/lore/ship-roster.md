# Ship Roster Design — Stay/Go Balance and the Others' Ship

> Design canon for the playable ship roster. Two principles: (1) Homesteader (Stay) and Precursor (Go) sides must have **equal ship counts and rough combat parity** so super-melee is balanced; (2) the Others' ship is special — **not normally playable**, only acquirable through a one-of-a-kind hijack quest. Combat AI for each ship follows the three-layer architecture in [combat-ai.md](combat-ai.md). Defensive doctrine follows [furling-tech-mechanics.md "Annoyance #5"](furling-tech-mechanics.md): regenerating shields are *Furling-rare*; almost every non-Furling ship in this roster has hull only, which is the central asymmetry the player exploits.

## Slice-Scope Roster (Phase 4 content target)

We aim for **5 ships per side** at slice scope (10 total + Cleanser variant + Others ship). This is enough variety for combat encounters and super-melee fun, modest enough to actually author.

### Precursor (Go) side — 5 ships

| Ship | Species/Origin | Role | Hull | Shield? | Key Mechanic |
|---|---|---|---|---|---|
| **Furling Scout** | Furling (player default) | Balanced, modular | Medium | **Yes** | Time Drive (mid-combat tactical rewind possible at high upgrade) |
| **Persuader Vessel** | Furling Persuader faction | Diplomatic, light combat | Light-medium | **Yes** | Dialog-amplifier weapon (forces brief truce in combat — risky utility) |
| **Arilou Skiff** | Arilou cousins | Fast, evasive | Light | No (Quasi-Space evasion instead) | Quasi-Space short-jump (brief invulnerability + teleport) |
| **Androsynth Refugee Cruiser** | Androsynth (time-displaced) | Medium-armor, science-tech | Medium | No | Dimensional-shear cannon (damages standard ships AND has a chance to disrupt Others-aligned entities) |
| **Lemmkin Skitter** | Lemmkin (canonical-anthropomorphic-squirrels; canonical-no-fear-only-curiosity) | Chaotic-engineering; high-firepower-but-unstable | Light | No | **Unstable Prototype** — canonical-random-effect-weapon-fire (rolls every shot: canonical-high-damage / canonical-self-damage / canonical-area-burst / canonical-fizzle); canonical-fast canonical-skittering canonical-evasion; canonical-fast-respawn-in-super-melee (canonical: *they breed fast to make up for the losses*). See [`species-the-lemmkin.md`](species-the-lemmkin.md). |

### Homesteader (Stay) side — 5 ships

| Ship | Species/Origin | Role | Hull | Shield? | Key Mechanic |
|---|---|---|---|---|---|
| **Defender Vessel** | Furling Defender faction | Heavy, slow | Heavy | **Yes** | Sa-Matra prototype beam (high damage, long cooldown) |
| **Mmrnmhrm Sentinel** | Mmrnmhrm (autonomous) | Transforming | Medium-heavy | No (mid-fight fabricator instead) | Mode-shift (combat / scout / fabricator); fabricator-mode repairs hull mid-combat |
| **Proto-Ur-Quan Warship** | Proto-Ur-Quan (mid-uplift) | Aggressive, ramming-capable | Medium | No | Crushing-claw forward arc (high damage close-range) |
| **Proto-Qor-Ah Marauder** | Proto-Qor-Ah (mid-uplift, lethal) | Glass-cannon, fanatic | Light-medium | No | Cutting-blade spinning attack (continuous AOE in close range; suicidal aggression in AI) |
| **Mrokon Hammer-Vessel** | Mrokon (canonical-Operator-puppet-operators; canonical-Homesteader-by-defiance) | Heavy-kinetic; canonical-the-only-ship-that-marks-the-Others | Heavy | No | **Hammer-Of-Refusal** — canonical-high-damage canonical-single-shot canonical-kinetic-round; canonical-MARKS canonical-the-Others (canonical: SC2 *"dimpled Vessel"* canon-explanation); canonical-Operator-puppet-respawn (canonical-mid-combat-puppet-switch sound when hull canonical-destroyed; canonical-Operator canonical-survives; canonical-new-puppet-takes-the-fight). Canonical *kill-tally* + canonical *Grand Accounting* cultural-canon. See [`loop-closing-content-pass.md §5`](loop-closing-content-pass.md). |

### Special — Cleanser Furling Cruiser

The **Cleanser Cruiser** is the slice's combat climax (see [factions-and-war.md](factions-and-war.md) and [combat-ai.md](combat-ai.md)). Technically Precursor-aligned (method-faction Cleanser is a Precursor sub-position) but in combat appears against the player AND against Homesteader species. For super-melee, treat as a **neutral / Precursor-extreme variant** of the Furling base hull with unique Cleanser modules:

- Medium-heavy hull
- **Shields, like all Furling ships** — this is the slice's only enemy fight where the bide-and-strike doctrine doesn't give the player an automatic edge. Cleanser vs Furling Scout is a *fair* fight on defense; it's decided by piloting, weapon timing, and personality
- **Quiet weapons** — engineered plagues, stellar-disruption beam (these are the Cleansers' planet-elimination tools downscaled to ship-vs-ship)
- AI: high persistence, moderate hesitation, formal banter

Should be playable in super-melee as a Furling variant, with a note that "the Cleanser is what the player fights against in the slice's climax."

## The Others' Ship — Special Hijack-Only

The **Others' Vessel** is fundamentally different from every other ship in the roster:

- **Not playable in super-melee by default.** The super-melee roster is balanced around 3D-physics ships; the Others' ship cheats so hard that including it ruins the matchup balance.
- **Acquirable through a special one-of-a-kind quest** ("The Hijack"). Quest details TBD; it likely happens *post-slice* in the larger game, but a slice-scope teaser version is possible.
- **In the hijack quest** the player encounters an Others' Vessel mid-incursion. They must disable its consciousness-substrate (using a Mmrnmhrm-derived expert-system probe? Andromeda's-equivalent? TBD) without engaging in standard combat (it ignores standard weapons). On success: the vessel becomes inert and can be captured and re-piloted.

### Why the Others' ship is so different

- It is not a 3D physics object in the same way other ships are. Its movement does not follow Newtonian dynamics — it "appears" places. It can be in two places simultaneously briefly.
- Standard weapons do not damage it. Its hull is a *projection* of an entity from the Others' substrate; what 3D physics calls "the ship" is the outline of a being whose body is elsewhere.
- Its weapon is the **decursion** — a localized temporal-dimensional displacement attack. Targets are not destroyed; they are *moved*. They can be moved to a previous moment (small rewinds for tactical effect), moved across the map (teleport), or moved to a different state (revert health, ammo, etc.). At high power, a decursion can erase a target from current spacetime entirely (functionally a one-shot kill, but the target is *displaced* not *destroyed* — they're still alive somewhere/somewhen).
- Its AI is *not* the standard combat-AI three-layer architecture. The Others don't have personality in the human sense. Their banter is unsettling third-person descriptions of the world that contradict each other ("the brightness here was not here three moments ago. it returns. you are partially here.").
- After hijacking, the player can use it but it has *cost*:
  - Each shot of the decursion weapon emits a thought-pattern that may attract Other attention (cumulative; tracked across the campaign)
  - The vessel's substrate-projection slowly fades over time; needs "recharging" at certain locations
  - Other 3D species are *terrified* of the ship; diplomacy with anyone goes badly while piloting it

The Hijacked Others' Vessel is a **trophy ship** — a reward for an exceptional player who completes the optional Hijack quest. It is *not* the optimal ship for most situations. It is dramatic.

## Super-Melee Balance Notes

For super-melee mode:

- **5 Precursor vs 5 Homesteader** is the default lineup (10 ships total).
- Each ship should have a clear "answer" on the other side — no clearly dominant matchup. Tune via the personality vector + base stats.
- The Cleanser Furling cruiser is the **11th** ship, faction-neutral. Available as an unlock or default-on depending on tuning.
- The **Others' Vessel is NOT available** by default. Only after completing the (post-slice) Hijack quest. Even then, the player must enable a super-melee "include Others' ship" toggle, because its mechanics break standard match flow.

## Combat AI Per Ship (Phase 3.5 work)

Each ship gets the three-layer combat-AI treatment ([combat-ai.md](combat-ai.md)):

| Ship | Aggression baseline | Caution baseline | Special-axis bias |
|---|---|---|---|
| Furling Scout (NPC) | 40 | 50 | Hesitation 50 |
| Persuader Vessel | 20 | 70 | Hesitation 80 (rarely fires first) |
| Arilou Skiff | 30 | 80 | Patience 70 (evasive) |
| Androsynth Cruiser | 50 | 50 | Persistence 80 (refugees fight to survive) |
| Defender Vessel | 70 | 30 | Persistence 95 |
| Mmrnmhrm Sentinel | 50 | 60 | Persistence 80; mode-switch is its variation axis |
| Proto-Ur-Quan Warship | 80 | 30 | Aggression-dominant, ramming bias |
| Proto-Qor-Ah Marauder | 95 | 5 | Suicidal-fanatic — no Hesitation, low Caution |
| Cleanser Cruiser | 50 | 60 | Hesitation 50-80 (varies — see species design) |
| **Others' Vessel** | n/a | n/a | Uses a custom non-personality-vector AI; goal-driven, alien |

Personality vectors are then varied *per encounter* on top of these baselines (the variation principle — same ship class, different captain every fight).

## Ship Visual Variation

Per the [variation principle](variation-architecture.md), each ship class has a **base archetype** (hand-authored or AI-generated reference image) and a **variation function** that produces per-instance visual deltas. A Proto-Ur-Quan Warship always reads as a Proto-Ur-Quan Warship; the eighth one you fight has a different hull paint, slight greeble pattern variation, and a different captain's mark from the first.

The Others' Vessel is the exception: it does not vary. Every Others' Vessel encountered is the *same* (because it's the same entity peeking through). This is canonically important — its sameness is one of its terrors. If you fight a second Others' Vessel, *you don't know if it's a second one or the first one again*.

## Authoring Order

If we author ships in priority order for the slice:

1. **Furling Scout** (player default; foundational)
2. **Cleanser Furling Cruiser** (slice combat climax)
3. **Proto-Ur-Quan Warship** (encountered during the uplift question)
4. **Proto-Qor-Ah Marauder** (encountered during the uplift question)
5. **Arilou Skiff** (Arilou encounter ship; brief)
6. **Androsynth Refugee Cruiser** (single arrival)
7. **Mmrnmhrm Sentinel** (optional exploration encounter)
8. **Defender Vessel** (rare cluster passage)
9. **Persuader Vessel** (Council briefing / dialog scenes)
10. **Invented Homesteader / Precursor ships** (super-melee filler)

The Others' Vessel is post-slice content.

## Stat Blocks (initial pass — tune in playtest)

Each block conforms to [ship-design-schema.md](ship-design-schema.md). These are the first-pass numbers for slice combat; expect ±30% adjustments after the first sparring sessions. Speed numbers are in system-units/sec to match the existing engine (Furling Scout = 220).

### Furling Scout *(Precursor — player default)*

| Field | Value |
|---|---|
| Points | 130 |
| Hull HP | 100 |
| Shield HP | 80 |
| Shield regen | 12/sec, after 2s no-damage delay |
| Top speed | 220 |
| Acceleration | 280 |
| Turning rate | 3.0 rad/s |
| Mass | 100 |
| Energy pool | 60 |
| Energy regen | 6/sec |

- **Primary — Furling Beam**: 8 dmg, 4 energy/shot, 4 shots/sec, range 400, hitscan, single target. *"Slim coherent beam, warm gold."*
- **Special — Time Drive Pulse** *(rare, expensive)*: rewinds the Scout's own hull+shield+position by 3 seconds. Energy 50; one use per fight unless TD module upgraded. **Counter**: the enemy can spend the 3 seconds gaining position; the Scout reappears where it *was*, not where it's gone. Skilled opponents bait the pulse.

### Persuader Vessel *(Precursor — Furling diplomatic faction)*

| Field | Value |
|---|---|
| Points | 110 |
| Hull HP | 80 |
| Shield HP | 90 |
| Shield regen | 14/sec, after 2s delay |
| Top speed | 200 |
| Acceleration | 240 |
| Turning rate | 2.8 rad/s |
| Mass | 90 |
| Energy pool | 80 |
| Energy regen | 8/sec |

- **Primary — Persuader Beam**: 5 dmg, 3 energy/shot, 3 shots/sec, range 360, hitscan. Weaker than Scout but cheaper.
- **Special — Dialog Amplifier**: forces a 4-second truce window — neither ship can fire. Energy 40, single use. **Counter**: the truce ends and the Persuader is *still* a glass ship — the enemy uses the truce to reposition for a kill window. High risk, sometimes saves a life.

### Arilou Skiff *(Precursor — Arilou cousins)*

| Field | Value |
|---|---|
| Points | 120 |
| Hull HP | 60 |
| Shield HP | N/A (Quasi-Space evasion instead) |
| Shield regen | 0 |
| Top speed | 320 |
| Acceleration | 420 |
| Turning rate | 5.5 rad/s |
| Mass | 55 |
| Energy pool | 100 |
| Energy regen | 10/sec |

- **Primary — Pulse Caster**: 4 dmg, 2 energy/shot, 6 shots/sec, range 300, fast projectile (700 units/s). *"Quick teal pulses, fading."*
- **Special — Quasi-Jump**: instant teleport up to 500 units in current heading; 1.5s invulnerability frame mid-jump. Energy 30, 5s cooldown. **Counter**: predictable jump targets — leading shots that arrive at jump destination catch the Skiff. Also, no shields means a single solid hit hurts.

### Androsynth Refugee Cruiser *(Precursor — time-displaced refugees)*

| Field | Value |
|---|---|
| Points | 135 |
| Hull HP | 130 |
| Shield HP | N/A |
| Shield regen | 0 |
| Top speed | 190 |
| Acceleration | 220 |
| Turning rate | 2.2 rad/s |
| Mass | 130 |
| Energy pool | 70 |
| Energy regen | 6/sec |

- **Primary — Twin Rail**: 10 dmg, 5 energy/shot, 2 shots/sec, range 500, projectile (1200 units/s). *"Two thin tracers from forward rails."*
- **Special — Dimensional Shear Cannon**: 35 dmg single shot, range 600, slow projectile (400 units/s), but +50% damage to Others-aligned entities and stuns regular ships for 0.8s. Energy 50, 6s cooldown. **Counter**: the projectile is slow enough to be dodged sideways. Used as a finisher, not a duel weapon.

### Defender Vessel *(Homesteader — Furling Defender faction)*

| Field | Value |
|---|---|
| Points | 170 |
| Hull HP | 180 |
| Shield HP | 60 |
| Shield regen | 8/sec, after 3s delay |
| Top speed | 150 |
| Acceleration | 130 |
| Turning rate | 1.6 rad/s |
| Mass | 180 |
| Energy pool | 90 |
| Energy regen | 5/sec |

- **Primary — Heavy Beam**: 12 dmg, 6 energy/shot, 2 shots/sec, range 450, hitscan. *"Wide amber lance."*
- **Special — Sa-Matra Prototype Lance**: 60 dmg, range 700, hitscan, **8-second cooldown**. Energy 60. **Counter**: the cooldown is brutal — the 8 seconds after a Lance is a window where the Defender is just a slow heavy with a regular beam. Fast ships hunt the cooldown.

### Mmrnmhrm Sentinel *(Homesteader — autonomous robotics)*

| Field | Value |
|---|---|
| Points | 155 |
| Hull HP | 150 |
| Shield HP | N/A (fabricator self-repair instead) |
| Shield regen | 0 |
| Top speed | 180 |
| Acceleration | 200 |
| Turning rate | 2.4 rad/s |
| Mass | 140 |
| Energy pool | 70 |
| Energy regen | 7/sec |

- **Primary — Particle Stream**: 6 dmg, 3 energy/shot, 5 shots/sec, range 380, projectile (900 units/s).
- **Special — Mode Shift (Fabricator)**: enters fabricator mode for 4s — cannot fire or thrust, regenerates 20 HP/sec. Energy 40, single use per fight. **Counter**: during fabricator mode the Sentinel is stationary. A heavy hit during that window dominates the trade.

### Proto-Ur-Quan Warship *(Homesteader — mid-uplift molluscoids)*

| Field | Value |
|---|---|
| Points | 145 |
| Hull HP | 170 |
| Shield HP | N/A |
| Shield regen | 0 |
| Top speed | 170 |
| Acceleration | 160 |
| Turning rate | 1.9 rad/s |
| Mass | 170 |
| Energy pool | 50 |
| Energy regen | 4/sec |

- **Primary — Crushing Claw Burst**: 14 dmg, 4 energy/shot, 1.5 shots/sec, range 200 (short!), projectile (600 units/s). Damage scales with distance closed — full damage point-blank.
- **Special — Ram Charge**: massive thrust burst for 1.5s, 80 dmg on contact. Energy 30, 5s cooldown. **Counter**: huge but committed move — sidestep it and they're past you with a 5s cooldown.

### Proto-Qor-Ah Marauder *(Homesteader — mid-uplift, lethal-pure)*

| Field | Value |
|---|---|
| Points | 95 |
| Hull HP | 60 |
| Shield HP | N/A |
| Shield regen | 0 |
| Top speed | 280 |
| Acceleration | 380 |
| Turning rate | 4.5 rad/s |
| Mass | 70 |
| Energy pool | 40 |
| Energy regen | 5/sec |

- **Primary — Spin Blade**: 18 dmg/sec continuous AOE, radius 80 around the ship, energy drain 6/sec while active. *"Whirring blade-segments deploy in a halo."*
- **Special — Fanatic Burn**: enters fanatic state for 3s — top speed +50%, takes +50% damage, immune to flinch. Energy 30, 6s cooldown. **Counter**: glass cannon. Hit it once during fanatic-burn and the trade goes wildly bad for it. AI is suicidal so this is *not* hard — they come to you.

### Cleanser Furling Cruiser *(slice combat climax)*

| Field | Value |
|---|---|
| Points | 175 |
| Hull HP | 150 |
| Shield HP | 100 |
| Shield regen | 10/sec, after 3s delay |
| Top speed | 175 |
| Acceleration | 180 |
| Turning rate | 2.0 rad/s |
| Mass | 150 |
| Energy pool | 80 |
| Energy regen | 6/sec |

- **Primary — Stellar Disruption Beam**: 11 dmg, 5 energy/shot, 3 shots/sec, range 480, hitscan. *"Pale-white beam with a violet edge."*
- **Special — Engineered Plague Spore**: deploys a slow-moving 60-radius AOE that does 6 dmg/sec to anything inside; lasts 4s. Energy 50, 8s cooldown. **Counter**: the cloud is slow and visible — move out of it. Plus the cooldown is long; bait the spore, then close.

### Others' Vessel *(post-slice, hijack-only)*

Non-Newtonian, decursion-weapon, sameness-as-terror. Stat-blocked separately when the post-slice hijack quest is authored; for slice purposes its existence is canon but its stats are not.

## Asymmetric Matchup Matrix (first-pass intuition)

Designer's gut after the first stat-block pass. To be confirmed in playtest:

| ↓ vs → | Scout | Pers | Arilou | Andro | Defender | Mmrnmhrm | Proto-UQ | Proto-QA | Cleanser |
|---|---|---|---|---|---|---|---|---|---|
| Scout       | —     | fair  | weak   | strong | fair     | strong   | fair     | strong   | weak     |
| Persuader   | fair  | —     | weak   | fair   | weak     | fair     | weak     | strong   | weak     |
| Arilou      | strong| strong| —      | strong | weak     | strong   | strong   | fair     | weak     |
| Androsynth  | weak  | fair  | weak   | —      | strong   | fair     | fair     | strong   | strong   |
| Defender    | fair  | strong| strong | weak   | —        | fair     | fair     | strong   | fair     |
| Mmrnmhrm    | weak  | fair  | weak   | fair   | fair     | —        | strong   | weak     | fair     |
| Proto-UQ    | fair  | strong| weak   | fair   | fair     | weak     | —        | fair     | weak     |
| Proto-QA    | weak  | weak  | fair   | weak   | weak     | strong   | fair     | —        | weak     |
| Cleanser    | strong| strong| strong | weak   | fair     | fair     | strong   | strong   | —        |

Read across a row to see how *that ship* fares against each opponent. The Scout has clear hard counters (Arilou, Cleanser) and clear cushions (Andro, Mmrnmhrm, Proto-QA) — exactly the asymmetric profile Aaron wants. The Cleanser is hard for *almost everyone*; the Arilou is hard for everyone *except* heavies. The points-buy compensates.
