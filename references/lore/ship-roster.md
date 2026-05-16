# Ship Roster Design — Stay/Go Balance and the Others' Ship

> Design canon for the playable ship roster. Two principles: (1) Homesteader (Stay) and Precursor (Go) sides must have **equal ship counts and rough combat parity** so super-melee is balanced; (2) the Others' ship is special — **not normally playable**, only acquirable through a one-of-a-kind hijack quest. Combat AI for each ship follows the three-layer architecture in [combat-ai.md](combat-ai.md).

## Slice-Scope Roster (Phase 4 content target)

We aim for **5 ships per side** at slice scope (10 total + Cleanser variant + Others ship). This is enough variety for combat encounters and super-melee fun, modest enough to actually author.

### Precursor (Go) side — 5 ships

| Ship | Species/Origin | Role | Hull | Key Mechanic |
|---|---|---|---|---|
| **Furling Scout** | Furling (player default) | Balanced, modular | Medium | Time Drive (mid-combat tactical rewind possible at high upgrade) |
| **Persuader Vessel** | Furling Persuader faction | Diplomatic, light combat | Light-medium | Dialog-amplifier weapon (forces brief truce in combat — risky utility) |
| **Arilou Skiff** | Arilou cousins | Fast, evasive | Light | Quasi-Space short-jump (brief invulnerability + teleport) |
| **Androsynth Refugee Cruiser** | Androsynth (time-displaced) | Medium-armor, science-tech | Medium | Dimensional-shear cannon (damages standard ships AND has a chance to disrupt Others-aligned entities) |
| **[INVENTED species ship — TBD]** | Filled in via [species-content-backlog.md](species-content-backlog.md) | Variable | Variable | Variable |

### Homesteader (Stay) side — 5 ships

| Ship | Species/Origin | Role | Hull | Key Mechanic |
|---|---|---|---|---|
| **Defender Vessel** | Furling Defender faction | Heavy, slow | Heavy | Sa-Matra prototype beam (high damage, long cooldown) |
| **Mmrnmhrm Sentinel** | Mmrnmhrm (autonomous) | Transforming | Medium-heavy | Mode-shift (combat / scout / fabricator); fabricator-mode repairs hull mid-combat |
| **Proto-Ur-Quan Warship** | Proto-Ur-Quan (mid-uplift) | Aggressive, ramming-capable | Medium | Crushing-claw forward arc (high damage close-range) |
| **Proto-Qor-Ah Marauder** | Proto-Qor-Ah (mid-uplift, lethal) | Glass-cannon, fanatic | Light-medium | Cutting-blade spinning attack (continuous AOE in close range; suicidal aggression in AI) |
| **[INVENTED species ship — TBD]** | Filled in via [species-content-backlog.md](species-content-backlog.md) | Variable | Variable | Variable |

### Special — Cleanser Furling Cruiser

The **Cleanser Cruiser** is the slice's combat climax (see [factions-and-war.md](factions-and-war.md) and [combat-ai.md](combat-ai.md)). Technically Precursor-aligned (method-faction Cleanser is a Precursor sub-position) but in combat appears against the player AND against Homesteader species. For super-melee, treat as a **neutral / Precursor-extreme variant** of the Furling base hull with unique Cleanser modules:

- Medium-heavy hull
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
