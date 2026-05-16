## The Slice Cluster — Twelve Systems, Hand-Authored

> Canonical layout of the systems the player traverses during the slice. Each entry pins the system to its galactic-coord position from the precursor-era starmap (`src/scz/content/universe/stars.json`) or assigns it a synthetic position for Furling-internal locations not in SC2 canon. The player navigates them via hyperspace + (post-Sage) Quasi-Space portals.

The slice has 12 visited systems. The Furling Council assigned the Steward to the **Mh-Lai Frontier Cluster** — a region of ~5 systems where the Steward is the responsible Steward. The other 7 visited systems are *adjacent clusters or far destinations* the Steward travels to via hyperspace flight. "Cluster" is bureaucratic, not strictly spatial.

When the engine spawns the player into hyperspace, these are the targets they can autopilot to and the systems whose contents are hand-authored (not procgen). See `src/scz/content/home_system.py` and `src/scz/content/arilou_outpost.py` for the pattern; the other systems will get their own content modules as they're implemented.

## The Twelve

### 1. Mh-Lai (home) — synthetic at (1900, 1600)

The Steward's home. Already implemented (`src/scz/content/home_system.py`).

- **Star**: yellow dwarf
- **Planets**: Mh-Lai I (ROCKY), Mh-Lai II (DESERT), **Mh-Lai** (TERRESTRIAL, the Hearth), Mh-Lai IV (GAS_GIANT) + **Furlmart** moon (warehouse), Mh-Lai VI (ICE)
- **Steward presence**: Mh-Lai Station orbits Mh-Lai. The Council faction rep visits here.
- **Slice role**: Home base. Acts 1, 2, and 4 climax all happen here. The Cleanser arrives in Act 3 *to* this system.
- **Implemented**: ✅ Station, Undock → SystemScene, Y in orbit → Dock at Station.

### 2. Sol — canonical at (1793, 1450), defined_name `SOL_PROTO`

Proto-humans on Sol III. Observation-only encounter (fanservice).

- **Star**: yellow dwarf (matches reality / SC2 canon)
- **Planets**: SC2 procgen would generate ~6-8 worlds; for the slice, hand-author at least **Sol III** (proto-humans, mid-Neolithic) and a gas giant or two for atmospheric texture
- **Slice role**: proto-species observation encounter ([proto-species-observations.md](proto-species-observations.md)). Awards bio-data + Archive entry. Thematic counterweight to the Ur-Quan uplift dilemma.
- **Distance from Mh-Lai**: ~150 universe units — closer than autopilot's STAR_ENTER_RADIUS will allow; the player can reach Sol on the first frame of hyperspace if they aim south-by-southwest
- **Implementation**: SystemScene works via procgen today; consider hand-authoring Sol III as TERRESTRIAL with a primitive-civilization tag

### 3. Arilou Outpost — synthetic at (3500, 2400)

The Sage's seat. Already implemented (`src/scz/content/arilou_outpost.py`).

- **Star**: green dwarf
- **Planets**: Outpost I (ROCKY), **Arilou Sanctuary** (TERRESTRIAL — Sage's homeworld), Outpost III (ICE), Outpost IV (GAS_GIANT)
- **Slice role**: Sage dialog → Quasi-Space portal gift. Story arc beat 2's climax-equivalent.
- **Distance from Mh-Lai**: ~1789 universe units — ~1.5 wall-seconds of autopilot at 3x test speed
- **Implemented**: ✅ Sage dialog, orbit Hail action, Quasi-Space portal flag

### 4. Gamma Vulpeculae — canonical at (3681, 2581), defined_name `ORZ_RIFT`

The Others' first signature in the cluster. Dimensional rift incursion site.

- **Star**: appears as a yellow dwarf but the system is *wrong* — light arrives slightly out of sync with itself
- **Planets**: 0 — the rift consumed them. Player sees only the star and the rift signature (a non-Euclidean visual distortion at a fixed position)
- **Slice role**: First Others encounter. Visual horror, no dialog (the Others speak through the rift in environmental subtitle: *"frumple. you wear meat still."*). Optional combat: a Them-corrupted creature emerges if the player loiters. **Humor doctrine zero here** — the player's wit options are stripped.
- **Distance from Mh-Lai**: ~2030 units — slightly past the Arilou Outpost
- **Implementation**: a new system type — "rift" instead of normal SystemScene. Could be a one-off scene class `RiftScene` rather than generic SystemScene
- **Encounter trigger**: revealed by Hyperspace-Echo Sensor Pattern (which the Slylandro quest gives — so this isn't accessible until after the player visits Beta Corvi). Until then it appears as a regular star on the map; afterward it's flagged as a rift in the HUD

### 5. Beta Corvi — canonical at (276, 9810), defined_name `SLYLANDRO`

The Slylandro homeworld. Far across the galaxy from Mh-Lai — this is one of the slice's long-distance trips.

- **Star**: green giant
- **Planets**: 1 inhabited gas giant (the Slylandro's world) + ~3-5 lifeless worlds for atmosphere
- **Slice role**: Slylandro Cloak quest. Both halves: deliver the Cloaking Satellite (or evacuation lift) and receive the Hyperspace-Echo Sensor Pattern.
- **Distance from Mh-Lai**: ~8300 units — too far for autopilot in one shot; player should use **Quasi-Space "distant fold"** portal (already implemented; exits at 6000, 5500, ~halfway). From there, autopilot the rest.
- **Implementation**: SystemScene with a gas-giant-emphasis layout. Orbit over the Slylandro homeworld → Hail action opens dialog with the Slylandro Observer collective

### 6. Epsilon Scorpii — canonical at (6162, 2263), defined_name `MYCON_BIOT_HIVE`

The Mycon biot hive — Furling terraforming site. Where the Deep Child whispers begin.

- **Star**: red dwarf (the biots prefer the dim warmth)
- **Planets**: 3-4 worlds, all in some stage of Mycon terraforming. The slice's focal world is **Epsilon Scorpii III** (TERRESTRIAL, half-terraformed, biot colonies visible from orbit)
- **Slice role**: Mycon Deep Child Whisper quest. The slice's moral pivot — the Bio-Architect module + the suppression/awakening choice.
- **Distance from Mh-Lai**: ~4350 units — outside autopilot range from home but reachable via "distant fold" portal exit, then autopilot
- **Implementation**: SystemScene with hand-authored planet layout emphasizing the half-terraformed world. Orbit over Epsilon Scorpii III → Hail action opens dialog with a Mycon biot. **Combat possibility**: late-quest Them-corrupted biot encounter

### 7. Procyon — canonical at (736, 2292), defined_name `CHENJESU_PROTO`

The Chenjesu's seat. Rooted crystalline life. Optional exploration.

- **Star**: orange dwarf
- **Planets**: 2-3, one of which is Procyon II (the Chenjesu world — TERRESTRIAL surface covered in crystalline outcrops, very low atmosphere)
- **Slice role**: Resonance Record quest. The cosmologically significant reveal — Others come in cycles.
- **Distance from Mh-Lai**: ~1400 units — within easy autopilot range, but the player won't know to come here until a hint surfaces. Slylandro mention "the singing stones to the southwest" in their dialog at high awe; that's the trigger
- **Implementation**: SystemScene. Orbit over Procyon II → Hail opens the Chenjesu dialog (slow, ellipsis-laden)

### 8. Proto-Hive — synthetic at (2400, 3000)

A Furling-monitored system housing the Proto-Ur-Quan and Proto-Qor-Ah limpets. Same star, different planets, mid-uplift.

- **Star**: yellow dwarf (chosen for Earth-like uplift conditions)
- **Planets**: **Proto-Hive III** (TERRESTRIAL — Proto-Ur-Quan colonies), **Proto-Hive IV** (TERRESTRIAL — Proto-Qor-Ah colonies). Sibling worlds, different cultural development
- **Slice role**: The Uplift Dilemma. The Steward visits, observes, and recommends to Council. **Combat possibility**: Proto-Ur-Quan warship encounter if the Steward tries to interfere with the hierarchy ritual; Proto-Qor-Ah Marauder if the Steward witnesses a purification cycle and intervenes
- **Distance from Mh-Lai**: ~1640 units — moderate autopilot
- **Implementation**: SystemScene with two TERRESTRIAL worlds. Orbit each → observation dialog (sensory description rather than direct speech, per the non-verbal canon)

### 9. Coel Tessar's Arrival — synthetic at (2300, 1800)

Where the Androsynth refugees arrived through their forced decursion. The wreckage of their FTL drive is still there.

- **Star**: white dwarf (an old, dim star — convenient anchorage for the refugee survival mode)
- **Planets**: 2-3 unremarkable worlds + the **Androsynth Survival Vessel** as a fixed-position artifact in the system (treat it like a planet for orbital approach)
- **Slice role**: Distress Beacon quest. Coel Tessar's dialog. Quasi-Space portal entry/exit visible nearby — the Arilou ferried them here
- **Distance from Mh-Lai**: ~430 units — easy autopilot, can be the player's first hyperspace destination after the Mh-Lai tutorial
- **Implementation**: SystemScene with a synthetic "vessel" planet entry. Orbit over the Survival Vessel → Hail opens Coel Tessar's dialog

### 10. Yehat-Adjacent Mmrnmhrm Site — synthetic at (4700, 800)

The Mmrnmhrm's Homeworld is gone, but the Sentinels still patrol the system. Located near (but not on) Yehat space.

- **Star**: blue-white dwarf (their First-Makers preferred bright sky)
- **Planets**: 3 — one was the original Homeworld (now glassed), one is a primordial leftover, one is the Sentinel staging ground
- **Slice role**: Archive Excerpt quest. Optional.
- **Distance from Mh-Lai**: ~3000 units — significant autopilot or via "distant fold" portal exit
- **Implementation**: SystemScene. Orbit over the staging ground → Hail opens the Mmrnmhrm dialog (formal archaic English, archive-index voice)

### 11. Zeta Sextantis — canonical at (4704, 969), defined_name `RAINBOW_BEING_SEEDED`

The slice's seeded Rainbow World. The Steward's task in Act 4 is to install the **Rainbow Resonator** here.

- **Star**: appears as a primordial, but contains a Furling-engineered hyperspace-anchor (the seeded Rainbow World is artificial in our era)
- **Planets**: a single TERRESTRIAL world tagged "Rainbow Being Seeded" — visually distinct (full-spectrum atmospheric refraction = a chromatic ring in low orbit)
- **Slice role**: Slice climax. After the Steward has handled Slylandro, Mycon, and Proto-UQ/QA, they fly here and install the Resonator. The Migration Door opens.
- **Distance from Mh-Lai**: ~2950 units — significant trip; intentional — the player has earned this destination
- **Implementation**: SystemScene with the special "Rainbow World" visual treatment. Orbit → A "Install Resonator" action (gated on quest progress) → cinematic transition to the slice ending

### 12. Cleanser Approach Vector — synthetic at (2700, 2100)

Where the Cleanser-faction Furling cruiser warps in during Act 3. Not a destination the player travels to — it's the location the Cleanser broadcasts from before bee-lining toward Mh-Lai.

- **Star**: a transient anchor (the Cleanser uses temporary hyperspace markers)
- **Planets**: NONE — this is a Cleanser-engineered transit point
- **Slice role**: Cleanser arrival cinematic + combat trigger. After Act 3's narrative beat, the Cleanser cruiser appears at this hyperspace coordinate and broadcasts a kill-order ultimatum to the Steward. If the Steward engages, combat starts. If the Steward retreats to Mh-Lai, the Cleanser pursues into the Mh-Lai system.
- **Distance from Mh-Lai**: ~960 units — close enough for a high-tension intercept
- **Implementation**: Not a normal SystemScene — a hyperspace-overlay encounter scene. The Cleanser broadcasts via Council channel; the player has to decide whether to investigate or run

## Coordinate Map (visualizable summary)

```
Y
 |
 |  [Slylandro]
 |   Beta Corvi
 |   (276, 9810)             (off-map far south)
 |
 |
 |
 |
 |
 |
 |   [Mmrnmhrm]                       [Zeta Sextantis — Rainbow]
 |    (4700, 800)                      (4704, 969)
 |
 |   [Sol]   [Mh-Lai] ← HOME
 |  (1793,1450)(1900,1600)
 |
 |  [Procyon]  [Coel arrival]  [Arilou Outpost]
 |   (736,2292)(2300,1800)      (3500,2400)
 |
 |   [Proto-Hive]   [Cleanser approach]   [ORZ Rift]
 |    (2400,3000)    (2700,2100)           (3681,2581)
 |                                            [Epsilon Scorpii — Mycon]
 |                                              (6162,2263)
 +———————————————————————————————————————→ X
```

(Diagram is schematic — coordinates are real but ASCII placement is approximate.)

## Authoring Order

The cluster systems author in this order, gated by which other code/content is ready:

1. **Mh-Lai** ✅
2. **Arilou Outpost** ✅
3. **Sol** — small content lift; hand-author Sol III, add proto-human observation encounter
4. **Coel Tessar's Arrival** — Androsynth refugees; needs Androsynth dialog FSM + Survival Vessel "planet" type
5. **Beta Corvi** — Slylandro; needs Slylandro dialog FSM + Cloaking Satellite item
6. **Epsilon Scorpii** — Mycon; needs Mycon dialog FSM + Bio-Architect module + Deep Child Whisper state machine
7. **Proto-Hive** — needs non-verbal "sensory description" dialog renderer (a renderer variant of the existing dialog scene)
8. **Procyon** — Chenjesu; needs Chenjesu dialog FSM + Resonance Record item
9. **Yehat-Adjacent Mmrnmhrm Site** — Mmrnmhrm; needs Mmrnmhrm dialog FSM + Archive Excerpt item
10. **Gamma Vulpeculae / ORZ Rift** — needs Rift scene (new scene class) + Others' first-appearance content
11. **Cleanser Approach Vector** — needs hyperspace-overlay encounter scene + Cleanser climax fight (this combines the SuperMelee infra with a narrative wrap)
12. **Zeta Sextantis — Rainbow World** — slice climax; needs Rainbow Resonator special orbit action + cinematic ending sequence

## What This Pins Down

- Star coordinates for every slice destination
- Distances (and therefore travel-time expectations) between systems
- Which systems are at canonical SC2 coords vs. synthetic Furling-era inserts
- Quasi-Space portal exits relative to slice destinations:
  - "near the Hearth" (2700, 1600) → 800 units from Mh-Lai; useful for Cleanser-approach intercepts
  - "Arilou Outpost" (3500, 2400) → on the Outpost itself
  - "distant fold" (6000, 5500) → useful as a midpoint for Beta Corvi (Slylandro) and Epsilon Scorpii (Mycon) trips

## Implementation Notes

- Most new systems can be authored as small `src/scz/content/<name>_system.py` modules following the home_system.py / arilou_outpost.py pattern: a `<name>_star()` factory returning a star dict + a `<name>_planets()` factory returning the Planet list.
- Systems flagged with `home_system: true` or `arilou_outpost: true` are picked up automatically by `SystemScene.__init__` (see `src/scz/system/scene.py`). New flags can be added for other lore-significant systems if needed, OR the existing `defined_name` field can be used to dispatch to hand-built planet lists (e.g. `SLYLANDRO` could dispatch to `slylandro_planets()` automatically).
- The Hyperspace starmap loader (`src/scz/hyperspace/starmap.py`) currently injects two synthetic stars (Mh-Lai, Arilou Outpost). New synthetic stars (Proto-Hive, Coel Tessar Arrival, Mmrnmhrm Site, Cleanser Approach) should be added there as they're authored. Or: a single `synthetic_stars.py` module aggregating all of them.
- The Rift scene (#4, Gamma Vulpeculae) is the only system that needs a NEW scene class. Everything else uses SystemScene + (where applicable) PlanetOrbitScene + DialogScene with the species' FSM.
