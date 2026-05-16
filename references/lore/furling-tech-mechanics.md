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
- **Landers are remote-piloted drones, manufactured on the spot.** No crew aboard. If a lander is destroyed by a hostile planet (lightning, lava, hostile life), the ship's onboard fabricator prints a replacement in a few seconds. *Loss* costs you a small mineral fraction and a few seconds; it never grounds you.
- **No "supplies" stat.** The ship's recyclers handle crew biomass needs indefinitely. There is no "you must return home to restock" loop.
- **Tractor-beam collection (per Aaron's design): never shoot living things.** SC2's "shoot the life-form for bio-data" mechanic is *not* in this game. Furling landers carry tractor beams with a visible collection radius — anything inside, mineral or biological, is gently pulled in. Better lander modules (a future module slot) grow the beam radius, so progression makes you a more capable but also *gentler* collector. The lore frame: Furlings tend the galaxy; they don't harvest it.

This eliminates ~half of SC2's busywork without removing the *interesting* resource decision — which is "what do you spend your minerals on?" (modules, ship upgrades, alliance gifts), not "do I have enough fuel to get there?"

## Annoyance #4 — Static Ship → Modular Furling Scout

**SC2 pain:** the player's flagship was modular but in a fairly clunky way (fixed slot count, no real visual change, modules felt interchangeable rather than transformative). Ship customization was mostly *resource sink*, not *progression*.

**Furling fix:** the **Furling Scout** has a modular architecture and many quest rewards are **permanent ship upgrades** that meaningfully change what the ship can do.

### Module categories

- **Hull modules** — armor type, structure, crew capacity (Furling crew capsules), hangar (drone storage), cargo (mineral hold)
- **Drive modules** — sublight thrusters, hyperdrive class, *Time Drive capacity* (yes, you can upgrade the Time Drive to rewind longer or recharge faster), Quasi-Space access
- **Weapon modules** — beam, missile, point-defense; each species' tech offers a different weapon style
- **Sensor modules** — bio-scanner, mineral-scanner, *Other-detector* (advanced versions of this are quest rewards mid-slice), *dimensional-rift* sensor
- **Field modules** — shields, cloaking field, terraforming projector, dialog amplifier (better Slylandro contact range), *Rainbow Resonator* (the special module used for seeding Rainbow Worlds)
- **Crew specialists** — a Furling Archivist (better dialog context), a Bio-Architect (faster lander replication), a Warden (better combat AI assist), a Tunneler (Quasi-Space navigation)

### How upgrades are earned

- Many are quest rewards from the species you help (Slylandro give you a sensor; Arilou give you Quasi-Space access; etc.)
- Some are from Council faction reputation (Persuaders give diplomatic modules; Wardens give defensive)
- Some are found in old Furling installations (the precursor era's own pre-history)
- Some are crafted from rare minerals + blueprints

### Visual

The ship's silhouette in combat / star-system view **changes based on installed modules.** A heavily-shielded ship looks different from a fast scout, even if they're the same base hull. The variation layer applies on top of *that* — every Cleanser cruiser is one base + module config + per-instance variation, so they all look related but distinct.

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

- **No "you must visit this NPC every game-week" mechanic.** SC2's Melnorme was great but felt artificial. Our NPCs come to you, or are at fixed locations the player visits when they want to.
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
