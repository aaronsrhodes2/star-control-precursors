# Rainbow Worlds — The Central Plot Arc

In *Star Control 2*, the Rainbow Worlds are an unresolved mystery: ten unique planets that emit a "rainbow" signal, each in a different SC2 cluster, which together trace a **spatial arrow**. The game never explains why the Precursors placed them, and SC2-era observers assume the arrow points toward the Galactic Core.

**In our game, the player places them — and the arrow points somewhere else.** The arrow points to a **dimensional crossing whose exit is in the nearest neighboring galaxy** — the destination of the **Precursors faction**'s Migration. (Important: "Precursors" is the in-fiction name of the *migrating faction*, of which the Furlings are one member. The Furlings call themselves Furlings; in retrospect, SC2-era observers will misread "Precursors" as referring to the Furlings specifically — see [the-precursors-and-homesteaders.md](the-precursors-and-homesteaders.md).)

**Why *that* neighboring galaxy.** The Furlings did not pick a destination at random. Generations of long-range cognition-pattern surveys came back null for one specific neighboring galaxy: **the Andromeda Galaxy (M31)** — our nearest large spiral neighbor, ~2.5 million light-years from Sol. The Furlings **felt no presence of The Others there**. They cannot be certain the absence is permanent; the Arilou have a quiet concern that it isn't (see [§8 of the-furlings-and-the-others.md](the-furlings-and-the-others.md)). But at the time of choosing, Andromeda reads as *quiet*, large enough to host every Migrant civilization, and reachable through the dimensional-crossing technique the Furling Hider faction had developed. The Council bet the Migration on it.

**Why a *galactic* crossing as the strategy.** A galactic crossing — even a *dimensional* one that folds the 2.5-million-light-year traverse into a single Furling-engineered jump — is a *difficult task*. It took the Furlings generations to develop the technique, requires the Rainbow World infrastructure to find the exit, and consumes immense energy reserves to execute. **The difficulty itself is the buffer.** Even if the Others noticed the crossing's effects and wanted to follow, replicating that effort is more than they typically expend on prey — they prefer to cull the loud where they find it. The Furlings' hope is that by the time the Others might learn the crossing (if they ever do), they will have already moved on from the Milky Way with minimal lasting damage to it — and the migrated civilizations can return.

The Rainbow Worlds are *both* an exit-sign (for the evacuating Precursors, *now*) and a **return-map** (for after the Others pass, decades or centuries from now). They are aimed at the dimensional crossing — which **on the SC2 starmap's 2D projection lies in the upper-right quadrant**, which SC2-era archaeologists 250,000 years later will misread as "toward the Galactic Core."

## How SC2 archaeologists get it wrong (canonical retcon)

This is the in-fiction error the Star Control Zero player gets to know is wrong.

SC2-era researchers, working from incomplete starmap projections and without context for the dimensional crossing, plot the ten Rainbow Worlds' coordinates and observe the arrow's vector pointing **up-and-right in the local stellar projection**. They label that direction "**toward the Galactic Core**" — because in their 2D map convention, up-and-right is where the Core symbol sits. They are doubly wrong:

1. **Wrong direction on the real sky.** The actual constellation cluster the upper-right quadrant maps to is the *Pegasus / Andromeda / Aquarius* region of the night sky from Sol's perspective — which is **the direction toward Andromeda Galaxy (M31)**, not toward the Milky Way's center. (The Galactic Core is in the *Sagittarius* direction, on the opposite arc of the sky.) The SC2 starmap convention swapped these in projection; the in-fiction archaeologists never caught the projection error.
2. **Wrong destination type.** Even if "Galactic Core" were the direction, the destination is **not in this galaxy**. The arrow points to the *dimensional crossing*, whose exit is in M31. SC2 archaeologists are interpreting a *crossing-marker* as a *coordinate-marker* — assuming "the Precursors are at the arrow's vector," when really *the Precursors are through a portal the arrow marks*.

**The diegetic wink**: one of the canonical Rainbow Worlds (per the table below) is **Alpha Andromedae** itself — the Precursors named a Rainbow World after the constellation that points to the destination galaxy. SC2 archaeologists never made the connection because they assumed the arrow pointed to the Core, not to where the constellation's name suggests. Star Control Zero players catch the wink — *we* know the Furlings were marking the direction of M31 in the very names of their seeded worlds.

**The Furlings did not go to the Galactic Core. They went through a crossing to Andromeda.**

The Rainbow Worlds aren't just lore — they're the **mechanical and narrative spine** of the slice and the larger game. They are placed by the player regardless of whether their specific cluster's species choose to migrate, cloak-and-stay (the Slylandro path), or hide-and-watch (the Arilou path). The cluster's Rainbow World is a contribution to the *galaxy-wide* arrow, not a per-cluster evacuation marker.

## The Canon Mystery (SC2)

From Aaron's original worldbuilding doc:
> "We seeded the Rainbow Worlds, a trail of breadcrumbs for those who would one day be strong enough to find us at the Core."

The 250,000-year-old assumption that the arrow points to the *Core* is exactly what we'd expect SC2-era archaeologists to conclude — they don't know about the dimensional crossing, and their starmap projection conflates *upper-right* with *coreward* (it doesn't; see the next section). The Furlings did not go to the Galactic Core. They went *through* a crossing aimed at **the Andromeda Galaxy (M31)** — our nearest large neighbor, ~2.5 million light-years away, surveyed and confirmed empty of the Others before the Migration began. The arrow is a love note, yes — but also a survival document, and a destination marker SC2 archaeologists will misread for 250,000 years until the Star Control Zero player gets to know better.

## The 10 Rainbow Worlds (Extracted Data)

From `src/scz/content/universe/stars.json`, tagged `RAINBOW_BEING_SEEDED`:

| Cluster              | (x, y)         | Star color    | Direction from map center |
|----------------------|----------------|---------------|---------------------------|
| Zeta Sextantis       | (4704, 969)    | ORANGE_BODY   | South                     |
| Gamma Kepler         | (5927, 2855)   | ORANGE_BODY   | SE                        |
| Gamma Reticuli       | (7472, 5155)   | GREEN_BODY    | E                         |
| Alpha Andromedae     | (8696, 6893)   | GREEN_BODY    | NE                        |
| Beta Pegasi          | (419, 7516)    | BLUE_BODY     | NW                        |
| Epsilon Draconis     | (2856, 7867)   | WHITE_BODY    | N (slightly W)            |
| Epsilon Lipi         | (5360, 8298)   | RED_BODY      | N                         |
| Beta Leporis         | (7601, 8544)   | ORANGE_BODY   | NE (toward upper right)   |
| Gamma Aquarii        | (8403, 8759)   | ORANGE_BODY   | NE                        |
| Groombridge          | (9989, 8934)   | WHITE_BODY    | Upper-right corner        |

The centroid sits at roughly (6143, 6579) — above and to the right of map center. The **densest concentration is in the upper-right quadrant**. SC2 lore reads that direction as "toward the Galactic Core"; our canon reads it as "toward Andromeda" via the dimensional crossing — see the *How SC2 archaeologists get it wrong* section above. Note that one of the ten worlds is literally **Alpha Andromedae** — the Precursors named a Rainbow World after the constellation that points to their destination galaxy. SC2 archaeologists missed it because they were looking for a Milky-Way-internal destination.

The seven different star colors are intentional — each Rainbow World "sings" in a different spectral signature. A future Newcomer scanning for the rainbow pattern will see seven distinct chromatic peaks across ten systems. (Three colors repeat to keep the signature unmistakable.)

## What Makes a World a Rainbow World

The Precursors transform a candidate planet by:

1. **Selecting a high-biology world** (the candidate must already host complex life — Rainbow Worlds in SC2 are the highest biological-data planets in the game; in our era they become that *because* the Precursors enrich them).
2. **Implanting a Resonator Spine** — a kilometers-deep crystalline structure in the planet's mantle that absorbs solar radiation and re-emits it in the world's signature color. Visible from light-years away in the right scanners.
3. **Circling the star** — a fleet of small autonomous Precursor satellites maintains a stable orbit around the host star, forming a glittering ring. This is the "circle" Aaron mentioned: every Rainbow World is one of a ringed pair (star + circling drones).
4. **Imprinting the arrow vector** — the orientation of the ring + the spectral peak together encode a direction. Read the ten Rainbow Worlds together: they triangulate a single point at the Galactic Core.

## The Player's Role

The slice contains **one Rainbow World seeding event** as the major beat. The full game (scaled up from the slice) would have the player participate in all ten across multiple clusters.

### Mechanics

To seed a Rainbow World, the player must:

1. **Scout a candidate** — find a planet in the cluster with biological data score ≥ threshold. (Reuses the existing planet scanning mechanic.)
2. **Gather seed materials** — three uncommon elements from other planets in the cluster. (Reuses the resource-collection mechanic and gives it a narrative goal.)
3. **Defend the seeding** — a Them-rift or rogue biot attacks during the implantation ritual. **This is the slice's combat climax.**
4. **Place the spine** — a short ritual scene; player aims a precise dive and releases the Resonator. The planet's color signature becomes visible from hyperspace forever after. (Visible permanent change to the map: the cluster now shows a colored ring.)
5. **Council report** — narrate what you did; the Council's faction balance shifts.

### Narrative Weight

The slice's Act 4 decision (the canonical climax of the vertical slice) is:

> *"The Resonator is placed. The crossing is live and your cluster's exit point will hold for the Migration window. You face two final choices. First: how have you handled the sentient species in your cluster — the Slylandro especially? Did you persuade them out, compel them out, let the Cleansers eliminate them, or stand with them as Defenders? Second: do you cross with the Migration now, stay as a Watcher to monitor the Culling, or remain as a Defender beside whatever holdouts you've protected?"*

The slice's epilogue reflects which of the four faction paths (see [factions-and-war.md](factions-and-war.md)) the player walked:

- **Persuader Path** — Slylandro evacuated peacefully, Mycon kept non-sentient or evacuated, you defied the Cleansers and crossed with the Migration. The Council preserves your name in honor. This is the canonical "good" ending.
- **Compeller Path** — Slylandro evacuated by force or deception, no one died, you bent your principles to make the timeline. The Council looks the other way. The Slylandro who survive in the new galaxy never quite trust you again.
- **Cleanser Path** — you sided with the Cleansers because the math said you had to. The Slylandro died for the Quiet. Your name enters the Quiet Ledger. You cross with the Migration but carry the weight forever.
- **Defender Path** — you refused the Migration. The Slylandro stayed with you. The Sa-Matra is forming. The slice ends with you watching the dimensional crossing close. **This is the closest path to SC2 canon.** Most of the species that exist in SC2 are descendants of the Defender path's choices in clusters like yours.

The Rainbow World you seeded in Act 3 remains visible from the cluster's hyperspace view permanently — a glittering ringed star, signal active, regardless of which path you took. Whoever inherits this galaxy, 250,000 years from now, will see it.

## Why This Works as the Game's Spine

- **Concrete goal**: every play session, the player knows what they're working toward — find a candidate, gather materials, defend, place.
- **All mechanics unified**: scanning, mining, dialog, combat, exploration are all *in service of* the Rainbow World goal. None are extraneous.
- **Lore payoff**: the SC2 community has speculated for decades about the Rainbow Worlds. Our game makes those speculations canon, with the player as the protagonist of the answer.
- **Scales naturally**: the full game is "ten of these, one per cluster, with the migration tension growing each time." The vertical slice is "one of these, with all the systems working." Same shape, different size.

## Visual & Audio

- Each Rainbow World's ring of drones is a **persistent visual landmark** in hyperspace — once seeded, the cluster's star-system view always shows a glittering colored circle. Player navigation tip: "follow the rainbow."
- A unique musical sting plays when a Rainbow World is seeded: the world's signature color note layered into the ambient track.
- The full ten-world arrow is **visible on the starmap** as a faint chromatic gradient once enough are placed (3 or more triggers a partial reveal in the player's archive).

## What This Does NOT Do

- **No Rainbow World grind**: each seeding is a unique scripted event, not a procedurally repeating quest. The full game has exactly ten.
- **No "complete the arrow" achievement screen**: the player never sees the full arrow in-game. The reveal is for the *next* civilization (the SC2 player, in our shared canon). The Precursors making the arrow don't see it from the perspective they're encoding it from.
- **No telling the player the arrow's purpose explicitly**: the player figures it out as the Council debates and the Arilou hint. Discovery, not exposition.
