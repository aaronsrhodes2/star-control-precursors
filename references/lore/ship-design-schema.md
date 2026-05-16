## Ship Design Schema (canonical template)

> The stat block every ship in the game fits into. Sister document to [species-design-schema.md](species-design-schema.md) §5. Roster + balance notes live in [ship-roster.md](ship-roster.md); this is the per-ship form. The defensive doctrine that frames every ship's stat block (Furling-rare shields, solo-captained, mineral-cost out-of-combat repair) lives in [furling-tech-mechanics.md "Annoyance #5"](furling-tech-mechanics.md).

## Authoring Principles

1. **Asymmetric balance** (per Super Melee tradition): every ship is *great* against some opponents and *terrible* against others. Even matchups are the *exception*; rock-paper-scissors with skill variance is the rule. The thing that makes the game replayable is the discovery of which ship counters which.
2. **Points-buy, not equal cost**: the slice's eventual Super Melee fleet selection is points-based — strong ships cost more points, glass cannons cost more than their effective combat duration would suggest because of their *peak* output. Aim for ~150 points = a "fair" 1v1.
3. **Identity over balance** *(when the two conflict)*: a Proto-Ur-Quan Warship should *feel* like a Proto-Ur-Quan Warship — a heavy crusher — even if that means it's strictly worse than another medium ship of the same cost in some matchups. The "wrong choice" being viable in skilled hands is the point.
4. **One identifying mechanic**: each ship needs one immediately-recognizable thing the player remembers it for. *"The one that teleports."* *"The one with the slow huge beam."* *"The one whose claws kill you if you get close."* If two ships compete on the same identifying mechanic, redesign one.

## Stat Block (fill all fields)

| Field | Type | Notes |
|---|---|---|
| **Name** | string | e.g. *"Furling Scout"* |
| **Species / origin** | string | links the ship back to its species sheet |
| **Role** | string | one-line role: *"glass cannon," "evasive scout," "anchor brawler"* |
| **Points cost** | integer | Super Melee buy value (see §Points Calibration) |
| **Hull HP** | integer | non-regenerating health pool |
| **Shield HP** | integer or N/A | regenerating ablative layer. **N/A is the default** — most non-Furling ships have hull only |
| **Shield regen rate** | HP/sec | 0 if N/A. Pauses for 2–3 seconds after taking damage |
| **Top speed** | units/sec | reference: Furling Scout = 220 sys-units/sec (matches `SYSTEM_PLAYER_SPEED`) |
| **Acceleration** | units/sec² | how fast it reaches top speed from rest |
| **Turning rate** | rad/sec | how fast it rotates in place. Heavy ships → low; nimble ships → high |
| **Mass / inertia** | integer | abstract — affects ramming damage given/taken and Newtonian drift recovery |
| **Primary weapon** | (see §Weapon Block) | the always-available main weapon |
| **Special weapon / utility** | (see §Special Block) | the energy-gated unique mechanic |
| **Energy pool** | integer | total energy capacity |
| **Energy regen** | units/sec | how fast the pool refills |
| **Visual base description** | 3–5 sentence prompt for SD | input to portrait/sprite generation. Distinctive enough that the eighth one fought reads as the same class as the first |
| **Variation knobs** *(later)* | list | which visual axes can vary per-instance (hue, decoration, mark). Authored at Phase 4.5+ — list now so the base description doesn't accidentally lock in non-variable details |

### Weapon Block (Primary)
- **Damage** per shot (or per second for continuous beams)
- **Energy cost** per shot
- **Cooldown / rate of fire**
- **Range** in screen-units
- **Travel time** (instant for hitscan; finite for projectile)
- **Hit pattern**: single target / line / cone / area
- **Visual**: short prompt-style description

### Special Block (Special / Utility)
- **Effect**: what it does — damage, defense, mobility, debuff, status, deployable, transformation
- **Energy cost** (often gates the whole match's tempo)
- **Cooldown / one-shot / per-fight count**
- **Counter-play**: what the opponent can do to neutralize or punish it. Every special must have a counter-play; specials without one are bad design

## Points Calibration

Rough scale, tune in playtest:

| Tier | Points | Examples |
|---|---|---|
| Glass scout | 60–90 | proto-creature, light skiff |
| Standard | 100–140 | Furling Scout, Persuader, most species mid-cruisers |
| Heavy | 150–180 | Defender, Proto-Ur-Quan, Mmrnmhrm |
| Specialist | 110–160 | unusual mechanic premium (Arilou teleport, Androsynth shear) |
| Cleanser climax | 170+ | the "boss" baseline |
| Others' Vessel | N/A in Super Melee | not point-priced; opt-in only |

A standard 1v1 fight is 150 vs 150. Multi-ship matches let the player spend a points pool however they like (1× Heavy or 2× Glass + Special). The points pool is the **lever Aaron can pull** to make a match feel intentionally unfair (a 100-pt Skiff vs a 200-pt Defender is a tutorial in piloting; same player in reverse is a tutorial in patience).

## Asymmetric Matchup Targets (slice-scope)

For each pair of slice ships, declare a target verdict — *strong / fair / weak* — from the column ship's perspective. This is the matrix the designer fills out after stat blocks land; not every cell needs balancing, but every cell needs a *known answer*.

Example fragment (placeholder values — to be filled when ships are stat-blocked):

| vs → | Scout | Persuader | Arilou Skiff | Androsynth | Defender | Mmrnmhrm | Proto-Ur-Quan | Proto-Qor-Ah | Cleanser |
|---|---|---|---|---|---|---|---|---|---|
| Scout | — | fair | weak | strong | fair | strong | fair | weak | fair |
| Arilou Skiff | strong | fair | — | strong | weak | strong | strong | fair | weak |
| Defender | fair | strong | strong | fair | — | fair | strong | strong | fair |
| Proto-Ur-Quan | fair | strong | weak | weak | weak | fair | — | fair | weak |
| ... | ... | ... | ... | ... | ... | ... | ... | ... | ... |

The matrix has to be honest: if every ship is "fair" against every other, the design has failed the asymmetric-balance test. Specifically expect: at least one *strong / weak* triangle per ship, and at least one matchup the ship just loses to no matter what (the Proto-Qor-Ah's suicidal-fanatic AI means *something* should be able to bait it to death; a heavy Defender's beam cooldown means *something* fast should be able to dance through volleys).

## Authoring Order

1. **Furling Scout** first — player baseline; all other balance is "against" this. Mid-points (~130), shields + medium hull, balanced everything, primary = standard beam, special = Time Drive (rare — uses TD charge).
2. **Cleanser Cruiser** second — combat climax. The fight the player has to *learn* to win. ~170 points, shields + heavy hull, slow turning, primary = stellar-disruption beam, special = engineered-plague AOE.
3. **One enemy from each slice species** — fast (Arilou Skiff), medium (Androsynth Cruiser), heavy (Mmrnmhrm Sentinel or Proto-Ur-Quan Warship), light-glass (Proto-Qor-Ah Marauder).
4. **The remaining Homesteader + Precursor variants** as polish slots — Persuader Vessel, Defender Vessel, the two invented species placeholders.
5. **Others' Vessel last** — its stat block is special (non-Newtonian, decursion weapon, no points cost); see [ship-roster.md "The Others' Ship"](ship-roster.md).

## Visual Variation Discipline (later)

Per the variation principle ([variation-architecture.md](variation-architecture.md)):
- One **base sprite** per ship class — the canonical archetype
- A **variation knob list** (hue tint, hull decoration noise, captain's-mark variation, paint scheme) defined per ship — varied deterministically per-instance
- All ships of a species **share a unifying visual grammar** so a player learns species at a glance even before reading the name. *Furling ships use the warp-pod ring; Mmrnmhrm ships transform; Proto-Ur-Quan have crushing claws; Arilou ships hover-shimmer with the Quasi-Space halo.*

The visual variation layer is **deferred past slice completion**. Slice ships ship as static base sprites only.
