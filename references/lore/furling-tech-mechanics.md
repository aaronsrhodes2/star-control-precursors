# Furling Technology — Mechanics That Fix SC2's Pain Points

> Companion to [the-furlings-and-the-others.md](the-furlings-and-the-others.md). Catalogs the player-facing mechanical advantages the Furlings have over the SC2-era survivors, and the SC2 annoyances each one fixes. The lore frame: *you are an apex civilization, not a scrappy underdog. Your tools work.*

## Design Premise

In SC2 you play a fragile survivor — a single experimental Precursor ship at the end of a long collapse. Many of the game's friction points reflect that fragility: no auto-save, limited fuel, expendable landers, deadly hyperspace pile-ons, save-point dependencies. They are *in-fiction* explainable but *mechanically* exhausting.

The Furlings are not survivors. They are gardeners of a galaxy, at the height of their power, with technology a quarter-million years more advanced than the SC2 era's. Their tools *should not* fail in the trivial ways human tech does. We can be in-fiction generous with capability while keeping the *real* tension (the Others, the moral conflict, the war among Furlings) intact.

## Annoyance #1 — No Auto-Save → The Time Drive

**SC2 pain:** dying or making a bad choice meant reloading a save you may not have taken recently. Tedious. Players save-scummed to compensate. Newcomers lost hours.

**Furling fix:** the **Time Drive**. Every Furling ship has a chronometric reverse-flow capacitor that continuously records the ship's state. At any moment, the player can engage the Time Drive to **roll the ship back exactly 5 minutes of real time**. The drive auto-engages on ship destruction.

There is no save/load UI. There is no save-scumming. There is *also* no fear of losing more than five minutes of progress to a single mistake.

### Mechanics

- The Time Drive maintains a continuous backing buffer of ship + world state.
- "Rewind" snaps the world to its state from five real-time minutes ago.
- Cost: up to five minutes of progress (less if you've been idle).
- *Permanent* progression (modules unlocked, lore revealed, story flags set on accept) is **NOT** rolled back. Only positional/state things. (See §"What survives a rewind" below.)
- The drive recharges in real time: after a rewind, the buffer is empty and you cannot rewind again until five minutes have re-passed.
- HUD always shows: `Time Drive: READY` or `Time Drive: charging (M:SS)`.

### Visual / audio

- Engaging Time Drive: a brief (~0.5 sec) chronometric effect — desaturation, a high-pitched chime running backwards, a faint outline of the ship's old trajectory tracing in reverse.
- Auto-engagement on death is more dramatic: a slow zoom-in on the destroyed ship, a held silence, then the rewind effect plays in full.
- *No* "GAME OVER" screen. Ever. The Time Drive is the answer.

### What survives a rewind

| Category | Survives rewind? | Reason |
|---|---|---|
| Ship position, velocity, fuel | No | The whole point. |
| Currently-in-progress encounter state | No | You re-meet the alien, re-fight the fight. |
| Permanent ship module upgrades | Yes | They are *engineered into the ship now*; the chronometric reflux preserves matter rearrangements. |
| Story flags marked "irreversible" | Yes | Council decisions that were broadcast, deaths that were witnessed by others, etc. |
| Story flags marked "rewindable" | No | Local choices the player wants to undo. |
| The Time Drive's own state | No (it empties) | You can't time-travel infinitely. |
| Map exploration / discovered systems | Yes | You've already *seen* them. |
| Lore unlocked / archived | Yes | You read it. It's in your head. |

The irreversible/rewindable flag on each story flag is **authored per flag** during content design. The author decides what the player can undo. This gives us narrative control without giving the player narrative chaos.

## Annoyance #2 — Hyperspace Pile-Ons → Emergency Rewind

**SC2 pain:** in hyperspace, enemy ships ("encounter probes") would arrive faster than you could kill them. Skill didn't help. You'd just be stuck dying in a swarm.

**Furling fix:** the Time Drive does triple duty — it's also the **escape hatch from impossible tactical positions**. If you're being piled on, you can manually engage Time Drive at any moment to roll back to your last safe position. Same five-minute cost as the death-rewind. Always an exit.

This is a player-decision tool, not just an undo button. Knowing the rewind costs five minutes makes it *expensive enough* to be a real choice — "is this fight worth losing the cluster-scan I just did?"

## Annoyance #3 — Fuel & Landers → Furling Self-Replicating Resources

**SC2 pain:** running out of fuel or losing your landers forced a tedious trip back to Earth Starbase. Resource-management without strategic depth — just routine punishment.

**Furling fix:**

- **Fuel regenerates passively.** The ship's antimatter capacitors refill from cosmic flux at a rate that's small but always positive. You will never run out of fuel mid-cluster. You may have to *wait* a few seconds at the edge of a long hop, but you will never strand.
- **Landers are unmanned hovering drones with tractor beams.** No crew aboard, no contact with the ground. The drone floats a few meters above the surface, immune to terrain hazards: it doesn't trip on cliffs, fall in crevasses, get caught in earthquakes, or stick in mud. What CAN destroy it is *weather and atmospheric chemistry* — extreme heat (volcanic vents, lava plumes), extreme cold (ice storms, cryogenic geyser blasts), acid rain, lightning strikes. Each hazard interrupts the survey loop and forces the drone offline or off-planet. The ship's onboard fabricator prints a replacement in a few seconds. *Loss* costs you a small mineral fraction and a few seconds; it never grounds you. The drone-vs-terrain decoupling matters: planets are now characterized by *weather profile*, not "is there ground rough enough to break a landing strut?"
- **The same fabricator repairs the hull out of combat.** Hull damage (see *Annoyance #5*) is undone over time when the ship is docked or sitting at a safe-zone (orbit, Quasi-Space) by spending minerals from the hold. There is no "return to drydock" loop; the lander fabricator IS the drydock, scaled up. Mineral cost is non-trivial — repairing after a hard fight should cost a real fraction of your resources — but it never gates you.
- **No "supplies" stat.** Recyclers handle the Steward's biomass needs indefinitely. There is no "you must return home to restock" loop.
- **Tractor-beam collection (per Aaron's design): never shoot living things.** SC2's "shoot the life-form for bio-data" mechanic is *not* in this game. Furling landers carry tractor beams with a visible collection radius — anything inside, mineral or biological, is gently pulled in. Better lander modules (a future module slot) grow the beam radius, so progression makes you a more capable but also *gentler* collector. The lore frame: Furlings tend the galaxy; they don't harvest it.

This eliminates ~half of SC2's busywork without removing the *interesting* resource decision — which is "what do you spend your minerals on?" (modules, ship upgrades, alliance gifts), not "do I have enough fuel to get there?"

## Annoyance #4 — Static Ship → Modular Furling Scout

**SC2 pain:** the player's flagship was modular but in a fairly clunky way (fixed slot count, no real visual change, modules felt interchangeable rather than transformative). Ship customization was mostly *resource sink*, not *progression*.

**Furling fix:** the **Furling Scout** has a modular architecture and many quest rewards are **permanent ship upgrades** that meaningfully change what the ship can do.

### Module categories

- **Hull modules** — armor type, structure (hull HP), hangar (drone storage), cargo (mineral hold). The ship is solo-captained by the Steward; there is no "crew complement" stat and no crew that dies in combat (see *Annoyance #5*).
- **Drive modules** — sublight thrusters, hyperdrive class, *Time Drive capacity* (yes, you can upgrade the Time Drive to rewind longer or recharge faster), Quasi-Space access
- **Weapon modules** — beam, missile, point-defense; each species' tech offers a different weapon style
- **Sensor modules** — bio-scanner, mineral-scanner, *Other-detector* (advanced versions of this are quest rewards mid-slice), *dimensional-rift* sensor
- **Field modules** — *shield projector* (Furling-rare; see *Annoyance #5*), cloaking field, terraforming projector, dialog amplifier (better Slylandro contact range), *Rainbow Resonator* (the special module used for seeding Rainbow Worlds)
- **Crew specialists** — passenger-class upgrade slots; crew never die in combat, they're treated like advisors who give passive benefits. Slice picks: a Furling Archivist (better dialog context), a Bio-Architect (faster lander replication, larger tractor-beam radius), a Warden (sharper auto-fight AI when piloting for the Steward), a Tunneler (cheaper Quasi-Space portal use, more portals visible on the map)

### How upgrades are earned

- **Quest-reward modules (tier 0)** are installed *in-field* by the quest-giving species (Slylandro give you a sensor; Arilou give you Quasi-Space access; Mycon hand-grow the Bio-Architect cradle). These bypass the Mh-Lai install rule because they're built using *the quest-giver's* fabrication discipline.
- **Schematic-gated ship mods (tier 1+)** are the meat of the slice's progression. The Steward gathers **schematics** in the field (quest rewards, salvage, faction trades, Bio-Archive payouts), brings them to **Mh-Lai Station**, and the schematic is consumed in the Schematic Vault to *unlock* the mod for purchase. The mod then costs credits + minerals to build and is installed *only at Mh-Lai* — Furling shipyard tolerance is too tight for field-fitting. This is the slice's primary **return-home loop**. See [economy-and-trade-loops.md](economy-and-trade-loops.md) for the full doctrine.
- **Sensor and lander-hardening upgrades** are sold by the **Melnorme** for BIO-cargo and are field-installable (these are sub-systems, not ship-mods proper, and aren't bound by the Mh-Lai tolerance rule).
- **Crew specialists** are recruited via dedicated side-quests, not bought; see [crew-recruitment-quests.md](crew-recruitment-quests.md).
- **Allied species ships** become available at Mh-Lai once the Steward has earned alliance with a species — fly out in a Slylandro Lift, Mmrnmhrm Sentinel, etc. as a side-loadout option to the Furling Scout.

### Visual

The ship's silhouette in combat / star-system view **changes based on installed modules.** A heavily-shielded ship looks different from a fast scout, even if they're the same base hull. The variation layer applies on top of *that* — every Cleanser cruiser is one base + module config + per-instance variation, so they all look related but distinct.

## Annoyance #5 — Crew Casualties → Solo-Captained Ship + Rare-Shield Doctrine

**SC2 pain (two of them, conflated):** (1) every fight chewed through crew, who were both your *hit points* and the conceit of your "officers," so losing a fight felt like losing people; (2) every ship had the same defensive layer ("crew"), so combat was just exchanging damage until somebody ran out — no defensive *strategy*.

**Furling fix:**

### One Steward, one ship — crew don't die

The Furling Scout is **solo-captainable.** Aaron, the player, IS the Steward; nobody else lives on the ship. Crew specialists are upgrades, not redshirts — they sit in the module list with their own benefits (Archivist, Bio-Architect, Warden, Tunneler) and survive every fight. Combat damage hits the *ship*, not the people; victory and defeat are about the metal, the field, and the player's choices, not about funeral counts.

This kills the SC2 "I won the fight but lost three crew, was that worth it?" anxiety. It also kills the "I'm out of crew so my ship is useless" softlock. The Steward, alone, sails on.

### Regenerating shields + non-regenerating hull (the Furling combat doctrine)

The Furling Scout has the classic two-layer defense:

- **Shields** are regenerating. They absorb the first damage. When not taking damage for a few seconds, they recharge. Full shields → fresh attack run.
- **Hull** is non-regenerating *in combat*. When shields drop, hull takes the bleed. Hull lost in combat is lost until you spend minerals at a safe-zone (see *Annoyance #3* — same fabricator that prints landers patches the hull).

**This is rare technology.** Most ships in the galaxy — Proto-Ur-Quan, Proto-Qor-Ah, refugees, Mmrnmhrm Sentinels, even most Furling Defenders — have *only* hull. Damage them, and they don't get it back. The Furlings have shielding because the Persuader faction prioritized survivable scouts (you can't persuade what you're dead from).

**The doctrine this creates:** the Furling Scout's edge in combat is *patience*. Attack, withdraw, let shields regen, attack again. An attrition-cycle that the enemy cannot match because they're bleeding from the moment shields go down. A skilled player turns a 1v1 against a heavier ship into a series of clean attack runs.

This is the player's *strategic* advantage, distinct from raw firepower or maneuverability. It also gives the Time Drive a tactical buddy — a Time-Drive rewind reverses hull damage too, so the Furling has *two* defensive layers compared to one for everyone else.

### The Cleanser exception

The slice's combat climax is a Cleanser Furling Cruiser. Cleansers, being Furlings, **also have shields.** This is the fight that strips the player's "I always have an edge" — the same doctrine applies to both sides, so the Cleanser fight is decided by piloting and weapon timing, not by attrition. Other Furling ships (Persuader, Defender) similarly have shields. The Arilou Skiff has *Quasi-Space evasion*, which is a different defensive layer entirely.

### Out-of-combat repair

After combat, the Steward returns to a safe-zone — orbit, Quasi-Space, station, or anywhere with the fabricator powered — and pays minerals to restore hull. Mineral cost scales with damage taken; a heavy fight should cost a meaningful fraction of the hold. There is no other path back to full hull (no "auto-repair over time" in hyperspace). The mineral economy is what makes repair a real decision: do you spend on repair, or on a module upgrade?

## Orbit-Cloak and Hyperspace Pursuit (gameplay flow canon)

Two related player-experience commitments captured from Aaron's design notes:

### Orbital capture is forgiving + cinematic

- Approaching a planet in System view smoothly transitions to the Scanning view; the planet's gravity *grabs* the ship and the camera zooms in.
- **The capture radius is generous.** SC2's biggest anti-pattern here — "missing the orbit because you didn't align precisely" — does not exist in our game. If the player is close enough, they're captured.
- The Scanning view shows the planet as a **gorgeous spinning 3D body**, AI-generated per (star_x, star_y, planet_index) seed via the variation principle. Visual wow-moment of the slice.

### In-orbit cloak (combat-safe zone)

- The moment the ship is in orbit (Planet Scan or Planet Surface scenes), it is **cloaked**. No hyperspace encounter can touch you while you scan, gather, or talk to a planet-bound species.
- Lore frame: the warp pod's emission is masked by the planet's mass/gravity well.
- The cloak makes Planet Scan and Planet Surface safe-zones for thinking, dialog, and decision-making — the SC2 equivalent of being inside a star system.

### Uncloak on leaving orbit + Hyperspace pursuit

- Leaving orbit (returning to System view) drops the cloak.
- The player must fly back out of the system; enemy ships may be **actively pursuing** them in hyperspace once exposed.
- Per-species warp-pod colors (see `src/scz/content/species_visual.py`) make pursuers identifiable on sight — a magenta pod on your tail is an Androsynth, a green-black one is a Proto-Qor-Ah, etc.
- Time Drive is the player's escape hatch if pursuit becomes unwinnable (5-minute rewind, per Time Drive canon).

## Anti-Annoyances to Watch For (don't recreate SC2's mistakes)

- **No "you must visit this NPC every game-week" mechanic.** SC2's Melnorme was great but felt artificial. Our NPCs come to you, or are at fixed locations the player visits when they want to. **The schematic-loop return-home cadence** ([economy-and-trade-loops.md](economy-and-trade-loops.md)) is the *one* exception, and it's player-driven — the player goes to Mh-Lai when *they* have a schematic to convert, not on a calendar.
- **No "you must memorize the calendar" mechanic.** SC2 had hidden time-sensitive events that fired off-screen. The Migration deadline is the *only* major countdown, and the HUD always shows it.
- **No "fail state requires restart from scratch."** Time Drive covers it.
- **No "you discovered something but the game won't let you act on it because you haven't talked to the right person."** Limit knowledge-gate barriers to one or two narratively-required threads.

## Implementation Priority

| Mechanic | When to build | Why |
|---|---|---|
| **Time Drive** | Phase 2 — now | Foundational; affects how every other system reasons about state. Must be in from the start. |
| Fuel regen | Phase 2 (when fuel exists) | Trivial: it's just `fuel += rate * dt`. |
| Lander replication | Phase 2 (when landers exist) | Trivial: respawn after delay. |
| Modular ship | Phase 4 (content + UI) | Needs a module system, a fitting UI, art for variation. Doable but not foundational. |
| Rainbow Resonator (special module) | Phase 4 | Required for the slice's climax. |
