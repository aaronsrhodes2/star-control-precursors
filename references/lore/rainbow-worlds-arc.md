# Rainbow Worlds — The Central Plot Arc

In *Star Control 2*, the Rainbow Worlds are an unresolved mystery: ten unique planets that emit a "rainbow" signal, each in a different SC2 cluster, which together trace a **spatial arrow pointing toward the Galactic Core**. The game never explains *why* the Precursors placed them.

**In our game, the player places them.** This is our central plot arc and the reason the game exists. The Rainbow Worlds aren't just lore — they're the **mechanical and narrative spine** of the slice and the larger game.

## The Canon Mystery (SC2)

From Aaron's worldbuilding doc:
> "We seeded the Rainbow Worlds, a trail of breadcrumbs for those who would one day be strong enough to find us at the Core."

The arrow points "home" — to where the Precursors migrated. It's a love note left for whoever inherits the galaxy.

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

> *"The Resonator is placed. The signal is live. Two questions remain. First: do you tell the proto-species what this world is for? They are intelligent enough to ask. Second: do you tell the Council what really happened with the Them-rift? Or do you omit it, so they don't accelerate the migration?"*

The four story permutations (tell/tell, tell/hide, hide/tell, hide/hide) lead to four short slice-ending epilogues that hint at the SC2 canon branching:

- **Tell / Tell**: the canon SC2 path. The Slylandro will testify accurately to "Newcomers" for the next 250,000 years. The Council moves quickly.
- **Tell / Hide**: the proto-species develop reverence-religions around the Rainbow World; the Council remains in this cluster longer than canon, and a few Precursors remain after the Migration.
- **Hide / Tell**: the proto-species never know; the Council leaves on schedule; the Rainbow World becomes a complete mystery to whoever finds it (closer to SC2 canon than expected).
- **Hide / Hide**: the player has gone rogue. The slice ends with the player being recalled to Council for explanation. The next chapter would explore the consequences.

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
