# Rainbow Worlds — The Central Plot Arc

In *Star Control 2*, the Rainbow Worlds are an unresolved mystery: ten unique planets that emit a "rainbow" signal, each in a different SC2 cluster, which together trace a **spatial arrow**. The game never explains why the Precursors placed them, and SC2-era observers assume the arrow points toward the Galactic Core.

**In our game, the player places them — and the arrow points somewhere else.** The arrow points to a **dimensional crossing to a neighboring universe** — the destination of the **Precursors faction**'s Migration. (Important: "Precursors" is the in-fiction name of the *migrating faction*, of which the Furlings are one member. The Furlings call themselves Furlings; in retrospect, SC2-era observers will misread "Precursors" as referring to the Furlings specifically — see [the-precursors-and-homesteaders.md](the-precursors-and-homesteaders.md).)

The Rainbow Worlds are *both* an exit-sign (for the evacuating Precursors, *now*) and a **return-map** (for after the Others pass, decades or centuries from now). They are aimed at the dimensional crossing, which in our universe's coordinate system *projects through the galaxy's center* — which is why SC2 archaeologists, 250,000 years later, will conclude the arrow points "to the Core."

The Rainbow Worlds aren't just lore — they're the **mechanical and narrative spine** of the slice and the larger game. They are placed by the player regardless of whether their specific cluster's species choose to migrate, cloak-and-stay (the Slylandro path), or hide-and-watch (the Arilou path). The cluster's Rainbow World is a contribution to the *galaxy-wide* arrow, not a per-cluster evacuation marker.

## The Canon Mystery (SC2)

From Aaron's original worldbuilding doc:
> "We seeded the Rainbow Worlds, a trail of breadcrumbs for those who would one day be strong enough to find us at the Core."

The 250,000-year-old assumption that the arrow points to the *Core* is exactly what we'd expect SC2-era archaeologists to conclude — they don't know about the dimensional crossing. The Furlings did not go to the Galactic Core. They went *through* it (the crossing's manifold projects through the galaxy's center as seen from our coordinate plane) to a universe adjacent to ours. The arrow is a love note, yes — but also a survival document.

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

The centroid sits at roughly (6143, 6579) — above and to the right of map center. The **densest concentration is in the upper-right quadrant**, which is the direction the arrow points: toward the Galactic Core in SC2 lore.

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
- **Compeller Path** — Slylandro evacuated by force or deception, no one died, you bent your principles to make the timeline. The Council looks the other way. The Slylandro who survive in the new universe never quite trust you again.
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
