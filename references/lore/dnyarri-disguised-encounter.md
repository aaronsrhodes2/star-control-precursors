# Dnyarri Disguised Encounter — A Fog-of-War Mechanic Over The Ship Roster

> Authored 2026-05-17 from Aaron's canon: *"The DNYARRI have no ship. Their ship is whichever ship they took control of. They are mind controllers and so they make their ship **look** like any other ship in the catalog, but you don't know what it actually does until it fires or uses a special weapon because it could be **any** ship in the catalog."*

## Backstory — the Dnyarri the Steward meets are *the powerful version*

SC2 canon: the Dnyarri the player meets aboard the Ur-Quan flagship (the "Talking Pet") are a **mutilated remnant** — the Ur-Quan, after their slave-revolution against their Dnyarri masters, **mutated** them to disable their psionic powers. The Talking Pet still has rudimentary mind-control (it can compel a Captain to silence) but it is a shadow of what its ancestors were. By SC2's time the Dnyarri are below the Others' threshold because they have been *engineered* below it — not because they were ever weak.

In **our** era (250kya, pre-Ur-Quan-uplift, pre-revolution), the Dnyarri are the **un**mutated, **un**disabled, **fully psionic** original version. They are above the Others' threshold by a comfortable margin. Their pre-sentient bulk lives on a single homeworld (`DNYARRI_PRIMITIVE` at Beta Orionis, observed in `walk_dnyarri_encounter`), but a few precocious individuals have made the sentience leap early and slipped off-world by riding host pilots. Their telepathic reach is wide enough to commandeer adult organic minds across short distances; their will is strong enough to hold a ship's crew for the duration of a fight; their grasp of stolen ship systems is good enough to *operate* a hijacked vessel with no apparent friction.

This is critical for slice tension: the Steward's mandate (the Quiet Resolution) requires every sentient species to reach a terminal status before the Others arrive. A loose population of powerful psionics, currently un-tracked, riding stolen ships through Furling territory, is **exactly** the kind of un-resolved bookkeeping that breaks the Quiet. They are not pre-sentient. They are not below threshold. They are a problem.

The bridge from "powerful Furling-era Dnyarri" to "Talking Pet Dnyarri" is canonically handled long after the slice, when the Ur-Quan rebel and mutate them. The Steward never sees that future; the player can infer it.

## Why this is the right shape for the Dnyarri

Dnyarri are mind-controllers. They are not building ships. They are not raising fleets. They are *passengers* who have learned to drive — and what they drive is whatever ship they boarded.

This rules out a Dnyarri *territory* (no fleet → no patrol → no domain). What it opens up is much more interesting: **a fog-of-war layer over the ship roster.** The player approaches what *looks* like a Mycon Podship; the warp pod is chartreuse, the silhouette is right, the sensor reads MYCON_BIOT. Combat begins. The ship fires — and the first shot is a Cleanser cone, or a Slylandro lightning, or a Melnorme plasma lance. The disguise breaks the moment the actual ship class's signature weapon discharges.

The reveal moment is the mechanic's whole payload. Until it fires, the player plays against their *expectations* of the cover species. After it fires, they're playing against an entirely different ship.

## What the encounter looks like end-to-end

1. **Sensor reading** — the disguised ship reads on the Echo Sensor as its **cover species** (a Cleanser Cruiser, a Mycon Podship, a Melnorme Trader, etc.). No tell. The ripple color, intensity, and label match the cover.

2. **Warp pod render** — in hyperspace, the ship draws its **cover** warp pod from `species_visual.SPECIES_WARP_POD[cover_species_id]`. Same rim, same glow, same identity.

3. **First-hail (optional)** — if the cover species has a normal hail behavior (the Cleansers broadcast before combat; Melnorme open trade dialog), the disguised ship *attempts* the same. The dialog comes through the cover-species voice profile — but **with off-notes**. The Cleanser cadence is correct but a word is wrong. The Mycon pheromone-channel carries an undertone of compulsion. The Melnorme trade pattern is correct but the timing is off by a beat. A perceptive Steward (high LLM-generated banter sensitivity) might *notice*. Most players will not until later.

4. **Combat entry** — combat opens with the **cover ship's silhouette + warp pod**, but the underlying `ShipClass` is the **actual** ship's stats, weapons, and AI. The player initially fights what they think they're fighting.

5. **The reveal** — the *first time* the disguised ship fires a weapon or uses a special ability, the visual disguise breaks. Three things happen in the same frame:
   - The warp pod color shifts from cover → **DNYARRI sickly yellow** (the species_visual.SPECIES_WARP_POD["DNYARRI"] rim, recently added). One-frame snap, no fade — discovery is sharp.
   - A small floating tag appears above the ship for ~3 seconds: `"DNYARRI — controlling [ACTUAL_SHIP_NAME]"`.
   - The actual ship's species-tag replaces the cover in the HUD readout.

6. **Post-reveal combat** — the ship plays as its actual class for the rest of the encounter. The cover identity is gone; the disguise was a one-time information asymmetry.

## What "any ship in the catalog" means

The Dnyarri-controlled ship's **actual** class is sampled (deterministically per-encounter, not random per-frame) from the full ship catalog at encounter-spec authoring time:

- `CLEANSER_CRUISER`
- `MELNORME_TRADER`
- `MYCON_PODSHIP`
- `ANDROSYNTH_CRUISER`
- `MMRNMHRM_SENTINEL`
- `PROTO_UR_QUAN`
- `PROTO_QOR_AH`
- `BURV_BROADCASTER`
- `UTWIG_JUGGER`
- `LEMMKIN_SKITTER`
- `THINN_BLADE`
- `DEFENDER_VESSEL`
- `COMPELLER_VESSEL`
- `PERSUADER_VESSEL`
- `ARILOU_SKIFF`

Any catalog ship is a fair sample — including ships from species the player has not yet met. **This is one of the only ways to encounter certain ship classes before their canon introduction**, which is itself a desirable side-effect: the Dnyarri are smuggling-in early exposure to ships the player will face later, in a context where the encounter doesn't burn the species' "first meeting" beat.

Excluded from the actual-class pool:
- **FURLING_SCOUT** (no Dnyarri rides the Steward's own kind in our era — the Furling resistance to psionic compulsion is the slice-implicit defense layer)
- **The Others' Vessel** (hijack-only per `ship-roster.md` canon; not in any normal pick pool)
- **ARILOU_SKIFF** (the Sage's people are partially out-of-phase with normal 3D space; the Dnyarri reach can't grab them)

## What the cover species pool looks like

The **cover** species is chosen separately from the **actual** species. A Dnyarri-disguised ship can wear *any* sentient-species cover, including covers for species that don't have their own combat ship yet (the Slylandro have an envelope but no Cruiser — but a Dnyarri can still wear "looks like a Slylandro orbital cruiser" if the renderer supports the silhouette). The pool for slice MVP:

- `CLEANSER_CRUISER` cover
- `MELNORME_TRADER` cover
- `MYCON_PODSHIP` cover
- `ANDROSYNTH` cover (the refugee silhouette)
- `MMRNMHRM_SENTINEL` cover
- `PROTO_UR_QUAN` cover

Crucially, the cover is **never** Furling (the Steward would instantly recognize home). It's never Arilou (the Sage's species has a unique signature). It's never the same as the actual class (no self-disguise — that would be invisible).

## Where the encounter spawns

Disguised encounters seed into the existing hyperspace encounter registry as a **new encounter kind**, not a new domain. Spawning rules:

- **Random scatter** — 2-3 disguised encounters live somewhere across the 10000×10000 hyperspace at any given time, repositioned per-scene-entry (deterministic seed = hyperspace entry count, so the same scene state always produces the same spawn).
- **Cluster bias** — disguised encounters slightly prefer to spawn *inside* a domain matching their cover species (a Cleanser-cover disguised ship is most likely to spawn inside Cleanser Approach, since that's where a real Cleanser would be). This makes the disguise more convincing — the player encounters what they think is a Cleanser exactly where they'd expect a Cleanser.
- **Never inside Furling Hearth** — Furling territory is sacred; the Dnyarri haven't penetrated home yet (slice constraint; later games can break this).

## When the player learns "Dnyarri exist as a mechanic"

The first disguised encounter is the player's **introduction to the Dnyarri mechanic**. Before that point they may have visited Beta Orionis and surveyed the pre-sentient Dnyarri homeworld, but the disguised-ship mechanic is *only* learned by experiencing it.

To soften the surprise on the first encounter, the reveal frame includes an extra one-line caption: *"Sensor analysis: the controlling intelligence is Dnyarri. The host ship is yours to learn."* On subsequent encounters, no caption — only the warp pod color snap + the floating tag.

## Side-effects on Bio-Archive

The first disguised encounter unlocks a new Bio-Archive entry: **"Others — wait, no: the Dnyarri"** (a deliberate Steward-voice misnomer in the title, indicating the Steward's first instinct was wrong; the entry corrects itself in the body). The body explains the mechanic and the canon. Subsequent encounters don't add new entries.

## In Super-Melee — the Gamble Pick

Super-melee gets a **Dnyarri pick** at the bottom of the roster. Mechanic:

- **Cost**: a *middle* point cost — somewhere between the cheapest ships (skiffs / scouts at ~3-6 pts) and the heaviest (Ur-Quan-tier dreadnoughts at ~28-30 pts). Target band ≈ **12-16 points**. Exact value owned by Combat Mechanics chat; tune so the Dnyarri pick is *attractive at mid-game-points and gut-check at high-game-points*.
- **Reveal**: when picked, the **game** rolls the actual ShipClass from the same catalog the in-fiction disguised encounters draw from. The picking player does **not** see the roll. They get the silhouette-and-warp-pod of a randomly chosen cover species (also rolled by the game), and they take that into the arena. *They are gambling their own pick.*
- **Opponent's view**: the opposing player sees the same disguised silhouette — they don't know what they're facing either. The first weapon fire from the Dnyarri ship reveals the actual class **to both players simultaneously** (same one-frame snap as the hyperspace encounter).
- **No re-rolls**: once locked in, the roll stands. If the player picks Dnyarri and gets a 28-point Dreadnought-equivalent for their 14-point spend, congratulations. If they get a 6-point Scout, they live with it.
- **Catalog membership**: the Dnyarri pool excludes Furling, Arilou, and the Others' Vessel (the latter is hijack-only per `ship-roster.md` canon). Everything else in the catalog is a fair roll.
- **First-time exposure shadow**: in single-player campaign mode, picking Dnyarri in super-melee is the player's **safe** way to encounter ship classes from species they haven't met yet — the same as the in-fiction "Dnyarri smuggles in early exposure" side-effect. The campaign super-melee picker is the testing-ground.

This is a slot players will reach for when:
- They've memorized the catalog and want a wildcard
- They want to *bluff* their opponent (the opponent can't pre-plan against a known ship)
- They are emotionally regulated enough to lose 14 points to a bad roll
- They have just lost three fights and want to break the pattern

It is a slot players will avoid when:
- They are at the last ship of their roster and need a known quantity
- Their opponent is paying attention (no bluff value if reads-through-disguise is the opponent's specialty)
- The match is at the edge of total-points budget (one bad roll loses the fight)

## In Single-Ship Mode (campaign default)

Outside super-melee, the player flies one ship (the Furling Scout, plus any modules installed). The Dnyarri disguise mechanic does *not* affect the player's own ship — they cannot be Dnyarri-disguised. The mechanic exists *only* on the opposing-AI side, both in hyperspace ambient encounters and in super-melee as the gamble pick. The Steward's mandate makes them resistant to mind-control by virtue of Furling biology + the Council's psionic-shielding protocols (which canonically exist as a slice-implicit defense layer; future expansion may make this player-vulnerable).

## Implementation order (for the engine)

Phase A — minimum viable disguise:
1. Extend `EncounterSpec` (or add a sibling `DisguisedEncounterSpec`) with `cover_species_id` + `actual_ship_class_id` fields
2. Sensor render uses `cover_species_id` for ripple color and label
3. Combat entry uses `actual_ship_class_id` for the ShipClass
4. Frame-1 of combat: render with cover warp pod; on first weapon fire from the disguised ship, snap to DNYARRI yellow + floating tag

Phase B — bias + replenishment:
5. Per-scene-entry spawn of 2-3 disguised encounters inside random domains (cover matches domain when possible)
6. Met flag retires the specific (cover, actual) pair; the encounter does NOT respawn at the same coords, but new disguised encounters can spawn elsewhere

Phase C — banter + dialog tells:
7. Cover-species first-hail with off-notes (LLM banter layer renders the off-note; FSM is identical to cover species' normal hail)
8. Bio-Archive entry unlock on first reveal

## Test plan

- `walk_dnyarri_disguised_first_encounter` — teleport into a disguised encounter; expect cover warp pod pre-fire; trigger combat; first weapon fire flips to DNYARRI yellow; flag `met_dnyarri_disguise` set; Bio-Archive entry unlocked
- `walk_dnyarri_disguised_cover_voice` — open dialog with a disguised encounter; expect cover-species voice profile in use; verify side-effect flag set when player picks the "this isn't right" dialog branch (canonical Steward off-note awareness)
- `walk_dnyarri_disguised_combat_balance` — N runs across the catalog: verify every actual_ship_class_id is reachable by encounter authoring; verify HUD readout updates correctly post-reveal

## Cross-chat dispatches

This mechanic touches all four lanes. When implementation begins, file:

- **Design**: dataclass + spawn loop + cover-flip render + Bio-Archive wire
- **Image**: a 1-frame "disguise-cracks" overlay (optional flourish on reveal — fractal-warp distortion)
- **Audio**: a reveal sting (slice-thematic; suggests "the cover identity has just lied to you")
- **Combat Mechanics**: confirm all catalog ShipClasses work as `actual_ship_class_id` (no required Furling-only assumptions in their AI); flag any class that wouldn't survive a wholesale identity-swap
- **Testing**: the three walks above

## Where this lives in the roadmap

This mechanic is **Phase 3** territory (plot-beat mechanics), filed alongside the Hijack quest. It is not in Phase 2 (queued species) because Dnyarri don't get a "species implementation" the way Mmrnmhrm or Taalo do — they don't have a homeworld scene to author beyond the existing Beta Orionis observation, and they don't have a ship class of their own. Their canon is *all mechanic*. The mechanic is the species.
