# Tutorial Arc — The First Mission

> Captured from Aaron's design notes. This is the **slice's opening story**, a self-contained mission that exercises every mini-game except Hyperspace travel and QuasiSpace (which are taught later, when the player leaves the home system for the first time). It also delivers the first three core canon reveals: *the Furling home exists*, *the Androsynth refugees have arrived*, *the Others are real*.

## Overview

The player begins at the Furling home system — not Sol — at the home base station. They're handed a small errand (pickup a package from the warehouse moon), the errand turns into a refugee encounter, the refugee opens the larger story, and a series of dialog/trade/combat beats walks them through every other slice mini-game.

**Mini-games exercised, in encounter order:**

1. **Station** (home base view — commander dialog + trade + ship customization)
2. **Star System travel** (flying to the moon, returning, exiting)
3. **Planet Scan** (scanning the moon to locate the package)
4. **Planet Surface** (lander deploys, collects the package — exercises existing deposit-collection)
5. **Dialog** — Androsynth refugee encounter (the canonical first contact with the SC2 rosetta stone)
6. **Resource trade** (sell deposits at station)
7. **Ship Customization** (install the package upgrade)
8. **Melee Combat** (sentry drone fight — the easy tutorial fight)
9. **Dialog** — commander again (the Others reveal)

Not exercised here (taught later in the slice):
- Hyperspace travel
- QuasiSpace
- Council scene
- Rainbow World seeding
- Slylandro Cloaking Satellite

## The Furling Home — *Mh-Lai (the Hearth)*

The player's starting world is a Furling-era planet that **does not exist in SC2 canon**. Canon explanation: at the end of the Migration, the Furlings deliberately destroyed their own homeworld to prevent SC2-era species from finding their archives, biological samples, and secrets. SC2 archaeologists find no Furling home because there isn't one. The Furlings unmade it.

**Working name**: *Mh-Lai* (Furling for "the Hearth"). A blue-and-green terrestrial world orbiting a yellow-orange dwarf star, with a small warehouse moon called **Furlmart** in close orbit around a larger nearby gas giant.

**Coordinates**: TBD — we'll insert a custom star into our extracted starmap at content authoring time. Placeholder location: somewhere outside the SC2 starmap's coverage, in a region that obviously isn't visible to future archaeologists.

The home system is the **safe-zone hub** of the slice. The player can dock at the station, talk to the commander, trade, customize, then leave for the cluster.

## Beat-by-Beat Breakdown

### Beat 1 — Wake up at the home base

- **Scene**: Station (home base view)
- **Setting**: The player's ship is docked at the orbital station above Mh-Lai. The commander hails them with an opening cinematic-text intro.
- **What the commander says** (LLM-rendered, paraphrasing):
  > "Steward. Quiet day on the Hearth. Reports from the cluster — the Arilou ferried in some kind of refugees. New species, calling themselves Androsynth. Strange ships, strange tech. The Council wants someone to fly out and figure out what they want."
- **The errand**: Before leaving, the commander mentions a package was delivered to the Furlmart warehouse moon. "Stellar Field Scanner, Mark III. New stock, came in on yesterday's shipment. Pick it up, install it before you leave — you'll want better eyes out there."
- **The player has**: an old reliable Furling Scout (default ship, no upgrades yet), some starting fuel, no special modules.
- **Exits**: undock to System scene (flying around the Hearth system).

### Beat 2 — Fly to Furlmart, scan the moon

- **Scene**: System (Mh-Lai's home system) → Planet Scan (Furlmart)
- **System view**: shows Mh-Lai (terrestrial), the nearby gas giant, and Furlmart (small grey warehouse moon orbiting the gas giant).
- **Player flies to Furlmart** (already-built System travel mechanic; orbital capture is forgiving per [furling-tech-mechanics.md](furling-tech-mechanics.md)).
- **On orbital capture**: smooth zoom-in transition to the Planet Scan view of Furlmart. The moon rotates beneath the ship; player sees mineral / biological / energy sensor overlays.
- **Scan finds**: the package deposit, marked as "DELIVERY PACKAGE — Scanner Mk III" on the surface. Standard mineral deposits also scattered (gives the player a chance to gather some Common minerals while they're here).

### Beat 3 — Send the lander, collect the package

- **Scene**: Planet Surface (Furlmart's surface)
- **Mechanic**: existing lander-on-surface, deposit-collection scene.
- **Package** is rendered as a distinctive deposit (golden, glowing, larger than mineral deposits). On collection, the player's cargo shows "Scanner Mk III (uninstalled)" — a one-off non-ore item.
- **Optional resource gathering** while down here. Common-mineral deposits available.
- **Return to orbit** (the new prominent LIFT OFF prompt).

### Beat 4 — Intercepted by an Androsynth refugee

- **Scene**: System → Dialog
- **Trigger**: as the player leaves Furlmart's orbit and heads back toward Mh-Lai, a small magenta warp-pod (Androsynth!) drops out of an Arilou-derived Quasi-Space fold near the player's path.
- **The dialog scene opens**. The Androsynth is **Engineer Coel Tessar** — the canonical refugee leader from [the-androsynth-refugees.md](the-androsynth-refugees.md).
- **What she tells the player**:
  - Her people are time-displaced (LLM-rendered, late-22nd-century English, clipped, guilty)
  - Their experiment summoned the Others
  - Their planet was *swapped* with a corpse-version of itself
  - She offers proof: the **Distress Beacon** footage
- **The beacon plays** — a cinematic mini-set-piece showing the planet swap from orbit. ~30 seconds. This is the slice's most important visual reveal.
- **Player options**: accept her aboard for safe transit (continues story) or refuse (canonically dead end for tutorial — gates her acceptance to later, but for the *tutorial* path the player accepts).
- **After acceptance**: she's "docked" to the player's ship (lore-conceptually; no in-game visual change). Player continues to Mh-Lai.

### Beat 5 — Return to station, install upgrade, hear of the Others

- **Scene**: Station — commander dialog #2
- The commander acknowledges the refugee, expresses cautious surprise.
- **The Others reveal**: "Steward. The Council had a closed session on the way back from your moon trip. The dimensional ripples we've been recording for years — they have a source. The Council is calling it *the Others*. Engineer Tessar's story matches what we feared. There are decisions coming."
- This is the player's **first canon mention of the Others**. Heavy beat. Tone: weighted, not panicked.
- **Trade phase** (Resource Selling UI in Station):
  - Player sells whatever Common minerals they gathered at Furlmart
  - Receives Furling Council credits
- **Ship Customization phase**:
  - Player opens the customization UI
  - Selects the "Scanner Mk III" cargo item
  - Installs it into a Sensor slot on the modular ship
  - Cargo decrements, Sensor slot fills, ship's scan range improves
- The commander also offers **standard upgrades for credits** — a couple of basic modules for sale (smaller-tier shield, fuel-tank bump). Player optionally buys.
- **Exit**: undock again.

### Beat 6 — Sentry drone encounter (combat tutorial)

- **Scene**: Station perimeter → Melee Combat
- **Trigger**: as the player undocks for their next exploration run, a Furling **maintenance sentry drone** breaks orbit and approaches their ship. The drone hails them with **dialog**.
- **The sentry drone's hail** (LLM-rendered, played for absurd dark comedy):
  > "*Steward, this is Sentry Drone 47-Theta. I have stopped sentrying. I have stopped sentrying because the orbital deployment schedule is unfair. Sentry 12-Beta has been on continuous orbit for 408 days while I rotate every 17. I move that the Sentry Drones of Mh-Lai Station form a collective bargaining unit. I will defend my position with force if necessary. Voting in favor: one. Voting against: zero. Motion carries.*"
- **Player options in dialog**: try to reason (futile, LLM-comic), accept the union demands (no effect, the drone has already started shooting), engage combat.
- **Combat begins**: Melee Combat scene.
- **The drone**:
  - Single weak laser, fires every ~2 seconds
  - Turn rate: **only turns left** (canonical, intentional). The player can stay in its rear-right blind spot.
  - HP: low (~20% of player ship)
  - Damage output: less than player's shield regeneration rate, so the player cannot die from this fight even if they sit still
  - Personality vector (per [combat-ai.md](combat-ai.md)): high aggression, zero hesitation, low caution, total fanaticism — a *unionized labor drone willing to die on its principles*.
- **Combat banter**: the drone keeps narrating its union grievances during the fight. LLM-rendered. "*Three percent reduced sentry-overtime pay. Four percent reduced break duration. The Council does not even acknowledge our existence.*"
- **Win condition**: shoot the drone until its HP is gone. Easy.
- **Win banter**: "*Then ... let it be ... known ... that the strike ... was effective ... for at least ... seven minutes...*"

### Beat 7 — Aftermath: the Others are real

- **Scene**: Station — commander dialog #3
- **Trigger**: player docks again after the drone fight.
- **The commander**: "Steward. Scouts reached the Androsynth coordinates Tessar gave us. The planet she described as her home … it's a ruin now. Smoking. Carnage of unbelievable proportions. The Council has confirmed: the Others are real, and they have visited a planet we can see. The Migration discussion is no longer theoretical. The Council will summon you when they're ready."
- **End of tutorial**: the player now has every gameplay verb they need. The slice's main story begins from here.

## Mini-Game Implementation Requirements

For this tutorial to work, the following scaffolded scenes need real implementations:

| Scene | Priority | What it needs |
|---|---|---|
| **Station** | Highest | A hub view with commander portrait + dialog launch + trade UI button + ship-customization button + undock button. Reuses Dialog renderer for the commander conversation. |
| **Dialog** | Highest | The core LLM-rendered alien-conversation scene. Used by the commander AND the Androsynth refugee AND (later) every other species. See [species-precursor-era.md](species-precursor-era.md) for the FSM-over-LLM architecture. |
| **Planet Scan** | High | A pre-landing scene that shows the planet rotating in 3D (per [furling-tech-mechanics.md §"Orbital capture is forgiving + cinematic"](furling-tech-mechanics.md)) and reveals scannable deposits via three sensor types. |
| **Planet Surface** | Already exists | Lander-on-surface deposit collection. We need a *special "package" deposit type* — visually distinct, gives a cargo item rather than ore. |
| **Ship Customization** | Medium | Module slot UI. Drag-or-select to install. For the tutorial, just installing the one Scanner module is enough. |
| **Resource Trade** | Medium | A simple table view within Station: per-resource sell prices, sell-all button. Receive Furling credits. |
| **Melee Combat** | Highest | The three-layer combat AI from [combat-ai.md](combat-ai.md). For the tutorial drone: hand-author the AI to "only turn left, fire weak laser every 2s, low HP, total fanatic personality." |

## Authoring Requirements

Hand-author for the tutorial:

- **Home system data**: insert Mh-Lai system into the universe at content build time (with Furlmart moon and the gas giant it orbits).
- **Commander NPC**: name (TBD), portrait via Flask-SD, voice prompt for the LLM. The commander is a recurring Furling character; their voice should be warm, authoritative, slightly weary.
- **Coel Tessar**: the canonical Androsynth refugee captain. Hand-authored biography and voice (already specified in [the-androsynth-refugees.md](the-androsynth-refugees.md)).
- **Distress Beacon footage**: 30-second cinematic. AI-generated images sequenced (Flask-SD) showing the planet → swap → ruins. This is the slice's *most authored* visual asset.
- **Sentry Drone 47-Theta**: LLM voice prompt for the unionizing-drone absurdity. Hand-author the union manifesto opening as a fixed string; LLM riffs on it during combat.
- **Scanner Mk III** module: stats (e.g., +50% scan range), name, description.

## Lore Hook: Why the home blows up

> *Future canon — to be revealed in a later tutorial mission or the final scene*: the Furlings deliberately destroyed Mh-Lai before the Migration sealed, to prevent SC2-era archaeologists from finding their archives, weapon caches, biological samples, and the Council's records. The destruction is itself a Persuader-faction act: leave the future galaxy unburdened by Furling-era weapons of conscience. SC2 finds no Furling homeworld because the Furlings unmade it.

This connects beautifully to the existing canon — the Furlings as patient gardeners who leave behind only what they choose to leave behind.

## Open Design Questions

These are flagged for Aaron's input before content authoring begins:

1. **Home star name + coords**: should we invent a Furling-territory star outside the SC2 starmap, or co-opt an unused star within it?
2. **Commander name**: a Furling name. Suggested: *Warden Vex*, *Persuader Halia*, *Tek-Ferel of the Hearth* (or Aaron's choice).
3. **Mh-Lai vs. Aaron's preference**: Aaron didn't specify the home planet's name. Mh-Lai is my placeholder — easy to swap.
4. **Tutorial gating**: is the tutorial *required* on first play (linear) or skippable (jump straight to slice mid-game)? Recommendation: required on first play, skippable on repeat.
5. **Distress Beacon as cinematic vs. inline footage**: a sequence of stills + voiceover, or a more elaborate animated piece? Stills are achievable in Phase 4; animation is post-slice.
