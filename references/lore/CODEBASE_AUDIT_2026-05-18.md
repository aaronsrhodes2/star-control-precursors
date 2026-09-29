# SCZ vs UQM Codebase Audit — 2026-05-18

System-by-system comparison of Star Control Zero (SCZ) against the Ur-Quan Masters (UQM, the SC2 reimplementation). For each system: what UQM does, what SCZ has, what's missing, importance.

Reference roots:
- **UQM**: `references/uqm-source/sc2/src/uqm/`
- **SCZ**: `src/scz/`

---

## 1. Super-melee combat

**UQM**: 1v1 ship combat in a screen-wrapping arena with a central gravity well (planet). UQM source: `battle.c` (512 LOC, top-level orchestration), `process.c` (1108 LOC, per-frame physics + camera + gravity), `cyborg.c` (1339 LOC, the AI flying every ship), `weapon.c` (414 LOC, projectile spawn/lifetime), `gravity.c` (200 LOC), and 27 ship folders under `ships/*/` — each defines stat block, weapon function, special function, and AI evaluator. Newtonian movement, energy pool funds both primary and special, hot-swap with damage carry-over via `melee.c` (2640 LOC, supermelee/ subdir).

**SCZ**: `src/scz/combat/scene.py` (5057 LOC — bigger than the entire UQM combat suite), `combat/ai.py` (860 LOC), `combat/ships.py` (875 LOC, ~15 ship classes wired). Newtonian, screen-wrap, central-planet gravity, asteroids, nebulae (mass-based drag), moon, bg star. SC2-style camera zoom (`process.c` `CalcReduction` ported, comment cites it explicitly at scene.py:116). AI in `ai.py:_should_use_inertia_halt` etc. is per-style (brawler/kiter/circler/orbital_strafer/snipe_then_relocate/left_only). Specials: inertia_halt, teleport, blazer_form, phase_skip, adware_pulse, icepeedo, tractor_lasso, chaff_spray, xform, homing_cluster, water_spray, engine_seeker. Fleet hot-swap is a wrapper layer (`scenes/fleet_combat.py:308`).

**Gap**:
- Player-controlled combat path not fully wired; super_melee picker (`combat/super_melee.py:287`) is AI-vs-AI only
- No SC2-style super-melee point-buy/team-build UI (matches UQM `melee.c` `buildpick.c`)
- No network super-melee (UQM has `supermelee/netplay/`)
- Special-energy decoupling means SCZ has different feel than UQM's shared-pool tension (deliberate design call)
- Probe / Sa-Matra / Talking-Pet / Last-Battle special ships not ported (`ships/probe`, `lastbat`, `talkpet`, `blackurq`)

**Importance**: Essential — combat IS the SC2 experience. SCZ is well-served here; this is the most-developed system.

---

## 2. Hyperspace navigation

**UQM**: Top-down 2D galaxy map with a player ship moving across it. `hyper.c` (1747 LOC) handles motion, fuel consumption, encounter spawning, autopilot lock, in-flight menu (STARMAP / EQUIP_DEVICE / CARGO / ROSTER / GAME_MENU / NAVIGATION). Hyper-flag swap (regular hyperspace vs QuasiSpace) keeps same code path. Encounter generation in `encount.c` + `grpinfo.c`: each species's sphere-of-influence spawns ships near the player based on standing.

**SCZ**: `hyperspace/scene.py` (1779 LOC) — well-developed. Zoom/pan, autopilot-cone (`AUTOPILOT_CONE_DEG = 45`), camera follows ship with clamp, system-entry by proximity (`STAR_ENTER_RADIUS = 250`). SC2 starmap PNG backdrop. Encounter points (`EncounterPoint` dataclass) and broadcast crawl overlay (`HyperspaceBroadcast` for incoming-hail text rendered before dialog launch). Species-domain patrols spawn via `_make_domain_patrol_trigger`. **No fuel mechanic** (see §17).

**Gap**:
- No fuel consumption per unit travelled (UQM's `fuel_ticks` static)
- No mid-hyperspace menu (UQM's STARMAP/EQUIP/CARGO/ROSTER overlay) — these are reached only at Station
- No sphere-of-influence color rendering on the map (UQM's per-race tinted disc; SCZ's `_draw_species_domains` draws boundaries but not the canonical SC2 color clouds)
- No "different hyperspace zone" graphic per region (UQM's red/yellow vortex zones)

**Importance**: Essential — primary navigation surface. Mostly there; fuel + in-flight menus are the conspicuous absences.

---

## 3. Star map / autopilot

**UQM**: Dedicated star-map screen (`planets/pstarmap.c`, 1631 LOC — large because it owns autopilot, race-sphere shading, cluster name labels, fuel-range circle, save/load star-map state). Press F6 on hyperspace → modal map; click a star → set autopilot target → engine drives the ship across.

**SCZ**: `hyperspace/starmap.py` (239 LOC) is data + rendering only; the autopilot lives in `hyperspace/scene.py:_find_autopilot_target`. SCZ does NOT have a separate modal star-map screen — the hyperspace scene IS the map. Press A near a star → autopilot engages immediately and auto-enters the system on arrival.

**Gap**:
- No modal map / no clicking a faraway star to autopilot across the galaxy — autopilot is forward-cone only (45°), so the player has to physically point at the destination
- No fuel-range circle (no fuel in SCZ yet)
- No race sphere-of-influence shading
- No "save autopilot target" between sessions

**Importance**: Nice-to-have — SCZ's autopilot is functional. Long-haul autopilot across the whole galaxy is a quality-of-life feature SC2 users will miss.

---

## 4. Solar system / orbit view

**UQM**: `planets/solarsys.c` (2021 LOC) — flying around inside a star system with orbiting planets, with the star at center. Planets generated by `generate.h` family + `gentopo.c`. Approaching a planet enters orbit (`orbits.c`, 629 LOC); from orbit the player can scan, dispatch shuttle, or land. `pl_stuff.c` (318 LOC) handles per-planet visual rendering.

**SCZ**: `system/scene.py` (695 LOC) renders the in-system view; `system/orbit.py` (527 LOC) is the dedicated orbit scene. Planets generated by `uqm_procgen.py` (398 LOC) — a bit-exact port of SC2's procgen (planets.h + orbits.c + plandata.c + Park-Miller LCG, comment-cited at uqm_procgen.py:10-22). Auto-zoom in system scene (`MIN_AUTO_ZOOM = 1.0` to `MAX_AUTO_ZOOM = 4.0`) tightens view as ship nears a planet. Orbit scene shows planet, scan summary, "Y: context action" for orbital hails.

**Gap**:
- No SC2-style starfield zoom-in cinematic on entry (purely a polish gap)
- No moons in the system view (SC2 doesn't show them either)
- Asteroids in-system not modeled (UQM does show them for some star types)

**Importance**: Essential — and SCZ does this well, with a faithful procgen port.

---

## 5. Planet surface / lander gameplay

**UQM**: `planets/lander.c` (2101 LOC) is the major file — top-down lander on a wrapping cylindrical map (longitude wraps, latitude doesn't), shoots/picks up: minerals, energy nodes, bio creatures. Hazards: lightning, earthquake, heat, biological. Lander HP drops, lander can die. `lifeform.h` + `lifeform.c` enumerate ~50 creature types with movement and danger. `surface.c` (251 LOC) holds the mineral deposit RNG, `cargo.c` (356 LOC) tracks the hold.

**SCZ**: `planet/scene.py` (1382 LOC) covers surface gameplay, `planet/deposits.py` (101 LOC, 4 deposit types — COMMON/USEFUL/BIO/ENERGY — vs UQM's ~13 elements), `planet/hazards.py` (165 LOC: lava, lightning, earthquake, heat, crack, thermal_vent — already similar to UQM). Lander has HP, can be destroyed, trip-haul is lost (per Furling-tech canon: drone is replaceable). Tractor beam (radius `TRACTOR_BEAM_BASE = 0.030`), no shooting deposits (Aaron canon: "life and minerals are both tractored, never shot"). Sensor-distance fuzz-to-sharp rendering for hot/cold deposit-hunting.

**Gap**:
- No biological-creature lifeforms — UQM has 50, SCZ has none yet (`lifeform.h` not ported)
- No cylindrical surface wrap (SCZ uses a fixed [0,1]² rect; UQM wraps longitude)
- Fewer element types — 4 vs UQM's 13 (COMMON/USEFUL/BIO/ENERGY is a deliberate simplification per `deposits.py:11`)
- No mineral *quality tier* (UQM has medium/large deposit grades)
- No lander upgrade slot (UQM has lander armor/speed/cargo upgrades via `devices.c`); SCZ has them planned as modules (e.g. `LANDER_BURVIXESE_AMPLIFIER` in memory) but mostly not yet implemented

**Importance**: Essential — surface gameplay is one of SC2's pillars. SCZ is partial; biological creatures and lander upgrades are the missing pieces.

---

## 6. Mineral / resource scanning + collection

**UQM**: From planet orbit, `scan.c` (1385 LOC) drives the mineral/biology/energy scan modes — wireframe globe rotates, scan animations draw colored dots at deposit positions, AUTO_SCAN flies the lander to each in turn, DISPATCH_SHUTTLE manually lands. `report.c` (271 LOC) summarizes resources after each visit. `cargo.c` tracks the hold (1ton, 10t, 50t bays).

**SCZ**: Scan happens in two places: `system/orbit.py` shows aggregate deposit_count_by_type before deploying lander; `content/system_scan.py` (327 LOC) computes a full per-system aggregate from hyperspace for the LR Mineral Scanner module. `planet/scene.py` itself renders the orbital scan summary. Cargo lives on `game.cargo` dict. `station/trade.py` (214 LOC) sells minerals at fixed prices in `MINERAL_PRICES`. Per-system extraction tracked in `flags["extracted_by_system"]` for the dim-tier UI.

**Gap**:
- No globe-rotation scan animation (cosmetic gap)
- No three-mode scan UI (UQM had separate mineral/biology/energy scan buttons; SCZ just shows totals)
- No "AUTO_SCAN" mode (lander auto-flies to each deposit) — SCZ has only manual flying
- Element-by-element vs aggregate-bucket sell prices — UQM had per-element pricing, SCZ has a single price per category

**Importance**: Essential — the SC2-loop is scan→land→collect→sell. SCZ has the loop; the UI is more abstract than UQM's.

---

## 7. Dialog / communication

**UQM**: `comm.c` (1669 LOC) drives the dialog scene — animated talking head, scrolling text, branching options. `commglue.c` (400 LOC) hooks per-race dialog scripts. Each species has a folder under `comm/*` (28 races, e.g. `melnorm/melnorm.c` 1851 LOC). Scripts are imperative C with `Response()` macros. `lua/luacomm.c` adds Lua scripting for later content. `commanim.c` runs per-frame portrait animation.

**SCZ**: `dialog/data.py` (157 LOC) defines `DialogState` + `DialogChoice` + `DialogCharacter` (FSM nodes with side_effect callbacks). `dialog/characters.py` is 5342 LOC and holds 129 DialogState definitions across many characters (Halia, Coel Tessar, Cleanser Vael-Souren, the Sage, Melnorme trader, etc.). `dialog/scene.py` (515 LOC) renders portraits with procedural sway/breath/speak-bob animation. `dialog/articulation.py` (188 LOC) defines rigs (BIPEDAL_HUMANOID, GASBAG_TENDRIL, RIBBON_PLANAR, COMPOSITE_CLOUD, FLOATING_DRONE) — currently documentation for future per-frame animation. **LLM-rendered dialog is not yet wired**; per `dialog/data.py:9-10` the canned text flows through directly.

**Gap**:
- LLM renderer not yet active (per project canon, deferred to Phase 3.5)
- No per-frame mouth-flap art (procedural sway is the placeholder); UQM has hand-drawn frame banks for every species
- Speech bubbles + scrolling text vs SCZ's static rendered text

**Importance**: Essential — and this is the entire reason for the game existing (per Aaron's memory: "wanted a concrete justification for an LLM in a game"). The FSM layer is well-developed; the LLM renderer is the next big lift.

---

## 8. Quest tracking + game state

**UQM**: `globdata.c` (659 LOC) defines the `GLOBAL_STATE` bitfield — ~1000 named state flags. `gameev.c` (894 LOC) handles scheduled events (clock-driven, e.g. "Ur-Quan arrive on this date"). `grpinfo.c` (865 LOC) tracks per-race standing + ship counts in each sphere of influence. Save/load serializes the entire bitfield.

**SCZ**: `engine/game.py:64` defines `flags: dict[str, object]` — a flat string-keyed store that quest code writes to. Quest-content modules: `content/council_missions.py` (525 LOC, ~12 missions with prereq/completion flags), `content/council_recommendations.py` (437 LOC), `content/cluster_status.py` (424 LOC, slice-wide species-status board with per-species resolver fns), `content/endings.py` (240 LOC, 6 endings keyed on aggregate flag count), `content/crew_bond_objects.py` (261 LOC), `content/fall_of_mhlai.py` (241 LOC), `content/final_conflict.py` (229 LOC, slice climax), `content/archive_entries.py` (1008 LOC, Bio-Archive). Quest CSV (`tools/quest_inventory.csv` per memory) at 387 rows.

**Gap**:
- No game clock / no scheduled events on calendar dates (UQM's `gameev.c` design is absent — SCZ uses flag-based gates instead, which is fine for the slice but doesn't give the player a calendar sense of pressure)
- No serialized save format
- No quest log UI for the player to review active quests (the Council scene and Cluster Status Board partly fill this role)

**Importance**: Essential. Heavily content-developed; the quest tracking is robust. Missing time-pressure mechanic (§15).

---

## 9. Ship customization / module system

**UQM**: `build.c` (687 LOC) builds the player's flagship from purchased modules in slots (Crew Pod, Storage Bay, Fuel Tank, Dynamo, Shiva Furnace, Tracking System, Cannon, Point-Defense, Hellbore Cannon, ...). `roster.c` (428 LOC) tracks escort ships. `planets/devices.c` (690 LOC) holds the artifact device list. `confirm.c` (250 LOC) is the confirm-purchase modal. All happens at SC2 Starbase.

**SCZ**: `content/modules.py` (1042 LOC) is the catalog — ~50 modules across hull / drive / weapon / sensor / field / crew_1 / crew_2 slots. `station/customization.py` (336 LOC) is the install/uninstall UI. `station/shipyard.py` (331 LOC) is allied-ship purchase. `station/schematic_vault.py` (301 LOC) is the schematic-to-shop-unlock loop. `combat/ships.py:apply_scout_mods` applies module deltas to a Scout's ShipClass at combat-start. Effective stats via `Game.effective_stat()` (`engine/game.py:109`).

**Gap**:
- No 2D-grid ship layout like UQM's flagship outfitter (SCZ has slot-based; UQM had visual grid). Cosmetic.
- No fuel tanks (no fuel system)
- No flagship vs Furling Scout distinction — UQM's `Vindicator` had its own visual configurator; SCZ's "flagship" IS the modular Scout
- No buy-cap based on hold space (UQM mass-limited the loadout)

**Importance**: Essential — and SCZ has innovated past UQM here (schematic vault, allied-ship purchase, multiple tier-2 mods per slot).

---

## 10. Resource economy / vendors

**UQM**: Single currency: `RU` (Resource Units) earned from minerals collected + Melnorme credits earned from bio-data. `cons_res.c` (112 LOC) handles the conversion and display. Melnorme info/tech are tier-based unlocks; Druuge buy crew for credits.

**SCZ**: `station/trade.py:30` sells minerals for *Council Credits* at flat per-type prices (`MINERAL_PRICES` in `content/modules.py`). Allied ships and schematic-vault unlocks form a richer trade graph than UQM (per `references/lore/economy-and-trade-loops.md`). Three-vendor niches: **Mh-Lai** (mods + allied ships + schematic vault), **Melnorme** (sensors + lander-hardening — narrowed canon), **allied species** (quest-reward modules in-field). Schematics are quest-recoverable items that unlock shop catalog entries.

**Gap**:
- No Melnorme bio-data tech-purchase loop yet wired (the dialog exists per `dialog/characters.py:_melnorme_trader`, but the bio-data-to-tech conversion isn't fleshed out as a Melnorme-side shop scene)
- `MELNORME_PLASMA_LANCE` violates the narrowed-Melnorme-niche canon per memory — flagged for retire/relocate
- No SC2-style escalating-tier purchase UI ("level 1 info costs 100, level 2 costs 250...")

**Importance**: Essential — and largely innovating past SC2. Solid foundation; Melnorme bio-data loop is the main outstanding piece.

---

## 11. Crew + ship management

**UQM**: `roster.c` is fleet management — buying / dismissing escort ships at Starbase, viewing ship stats. Each ship has its own crew complement (Crew Pod modules), and crew is consumed when ships take hull damage in combat (a ship with crew=0 dies even with full hull).

**SCZ**: Per Aaron's canon (`furling-tech-mechanics.md §5` cited in `modules.py:16`), the Steward is solo-captained. Crew are NOT redshirts — they're passive-bonus passengers with named identities. `content/modules.py` defines named crew (Mraka the Pilot, Bren-Vor Weapons Officer, Yelena Engineer, Mira-Rou Medic, Tarven Navigator, plus Forward as alternative weapons officer). `content/crew_bond_objects.py` (261 LOC) and `scenes/common_room.py` (949 LOC) cover the social-hub side. `station/shipyard.py` is the fleet-buy UI for allied ships.

**Gap**:
- No SC2-style crew-as-HP — deliberate design departure
- No crew-as-currency for Druuge (Druuge not yet in slice)
- Common Room banter is fixed line-pools (per memory, ~300 lines authored); the variation layer that makes them feel per-encounter unique is deferred

**Importance**: Essential conceptually — SCZ has rethought this thoroughly. Doesn't 1:1 copy UQM, but its replacement system is well-fleshed.

---

## 12. Sensors / detection

**UQM**: Sensor functionality lives mostly in `planets/scan.c` (modes) and `pstarmap.c` (race-sphere visibility). No dedicated sensor *modules* — what you can see is fixed by your ship class.

**SCZ**: `content/modules.py` defines multiple sensor modules: `SCANNER_MK3` (sensor_range/surface_sensor_range/hazard_sensor_range), `HYPERSPACE_ECHO_SENSOR` (Slylandro-traded, `other_detection_range`), Lemmkin's whirligig scanner, etc. `content/system_scan.py` (327 LOC) is the data layer the sensor stat-stack queries — produces a per-system summary visible at the hyperspace HUD when the player has a `system_resource_scan` capable module. Surface sensor radius is normalized [0,1] and module-extensible. Per-system anomalies (`SystemAnomaly` dataclass) gated by stat keys (`system_anomaly_scan`, `proto_species_scan`).

**Gap**:
- Most of this is *additive* over UQM rather than gap-filling; SCZ has more sensor variety than UQM
- No "sensor pierces cloak" mechanic yet (Dnyarri ship-cover-reveal still in design, per memory)

**Importance**: Nice-to-have — and SCZ has invested heavily here. Better than UQM in terms of player progression surface.

---

## 13. Quasispace / Arilou portals

**UQM**: `gameev.c` handles QS portal entry/exit events; `gendef.c` (the QS map config) defines the 11 portal positions (UQM has 11; canonical SC2 lore says one more for a total of 12). Arrival in QS swaps the hyperspace flag; the same `hyper.c` code path animates the green grid. Captain's log + Sage dialog gate the gift.

**SCZ**: `quasispace/scene.py` (804 LOC) is a dedicated scene with **12 portals** (per Sage Lwen-Olou's canon, slightly different from UQM's 11). Three known by default (Hearth / Arilou Outpost / Distant Fold); the other nine are destination-hidden until first traversal. Smooth zoom, autopilot-to-nearest-in-cone (parity with hyperspace), auto-capture on collision. Y button in hyperspace opens a portal if `has_quasispace_portal` flag is set (granted by Arilou Sage dialog side-effect).

**Gap**:
- No SC2-style green-grid arena visual (cosmetic — SCZ uses an SC2 QS map PNG backdrop)
- No QS-specific encounter content yet (Slylandro probes won't fit lore; could be Other-flickers per design notes)

**Importance**: Essential — SCZ has full coverage and a richer puzzle-discovery layer than UQM.

---

## 14. Encounters / spheres of influence

**UQM**: `encount.c` (844 LOC) + `grpinfo.c` (865 LOC) drive sphere-of-influence ship spawning. Each race has a sphere center + radius on the map; entering it spawns hostile/neutral/friendly ships at frequencies tuned per race. Encountered ship → comm or combat.

**SCZ**: `content/hyperspace_encounters.py` (387 LOC) defines fixed-coordinate encounters — Cleanser patrol alpha, Cleanser climax alpha, Coel Tessar, salvage wrecks alpha/beta/gamma/delta, ambient Other-rift sightings, drifter wakes, anomaly pulses. `content/species_domains.py` (301 LOC) defines species territories with per-domain patrol density; `_make_domain_patrol_trigger` spawns AI ships at deterministic positions within those domains. `content/hyperspace_ripples.py` (108 LOC) is the Echo Sensor's data layer.

**Gap**:
- No race-standing-modulates-frequency (UQM's "Ur-Quan are more aggressive after you fight them" mechanic isn't here — the Cleanser patrol is single-shot)
- No random encounter table per sphere — SCZ encounters are hand-placed
- No "you keep running into ships when traversing the Ur-Quan sphere" continuous-pressure mechanic

**Importance**: Essential conceptually. The fixed-coordinate model is faithful to slice scope but breaks the open-world feel SC2 had in late-game.

---

## 15. Game clock / time pressure / story deadline

**UQM**: `clock.c` (314 LOC) is a Gregorian calendar clock running at 24 ticks/day, with `gameev.c` (894 LOC) scheduled events (Ur-Quan arrival, Kohr-Ah cleansing march, etc.). Game loses if Ur-Quan reach Earth before the player wins. Daily ticks fire events even while player is at Starbase.

**SCZ**: **No game clock**. Time pressure is purely flag-driven: `content/cluster_status.py` tracks a Migration deadline indirectly via the status board; `content/fall_of_mhlai.py:208` defines `should_fire_fall(game)` as a flag-conjunction predicate (`tutorial_complete + has_distress_beacon + visited_systems>=5 + at-least-one-species-decision-made`); fires on next hyperspace traversal. The Fall has a 60s decision window timer (`DECISION_WINDOW_SECONDS = 60.0`) but that's intra-scene only.

**Gap**:
- No diegetic calendar / day counter shown anywhere
- No scheduled-event queue — events fire on flag conditions, not date stamps
- No "running out of time" pressure mechanic visible to the player (the Cluster Status Board and Fall trigger conceptually fill this role but the design intent has been to keep this slice flag-based)

**Importance**: Essential to SC2 feel but **deliberately replaced** in SCZ canon. The Migration-pressure narrative is delivered through dialog + Cluster Status Board rather than a clock. May want to consider a visible day counter for atmosphere.

---

## 16. Save/load

**UQM**: `save.c` (1501 LOC) + `load.c` (834 LOC) + `load_legacy.c` serialize the entire game state to disk — slot-based save files with versioning.

**SCZ**: **No save/load.** Grep for `json.dump|save_game|load_game` in src/scz returned no files. The Time Drive system (`engine/time_drive.py`, 143 LOC) provides a *rewind* mechanic but no persistent save.

**Gap**:
- No save files at all
- Cannot quit and resume a game

**Importance**: Essential for any released game. Acceptable for slice MVP, but blocks any playtesting longer than one sitting.

---

## 17. Fuel + refueling

**UQM**: Fuel consumed per unit hyperspace travelled (`gameev.c` decrement; `cleanup.c` end-of-day check). Refuel at SC2 Starbase or Melnorme. Running out = stuck in hyperspace until you drift to a star.

**SCZ**: **No fuel mechanic.** Grep for `fuel` matched only `FUEL_TANK_PLUS_50` (module deltas: `fuel_max: 50`), Yelena Lwen-Tar's `fuel_efficiency` delta, and Halia's dialog line mentioning "burn through fuel reserves" rhetorically. There is no fuel meter, no per-unit-travelled consumption, no refuel scene.

**Gap**:
- No fuel meter
- No per-unit-travelled hyperspace consumption
- No refuel cost
- No "stranded out of fuel" lose-state

**Importance**: Essential to SC2 feel. The fuel meter is a defining feature of SC2's hyperspace tension. Per Furling-tech canon ("Time Drive, fuel regen, lander drones, modular ship — Four mechanics that fix specific SC2 annoyances"), fuel may be deliberately less central in SCZ — but there's currently no system at all.

---

## 18. Pursuit / fleeing in hyperspace

**UQM**: `encount.c` spawns enemy ships at the sphere edge; if encounter is hostile and the player flees, the enemy ship pursues across the hyperspace map at its own speed, eventually catching up unless the player makes it to a star or out of the sphere. Stealth/escape is a real mechanic.

**SCZ**: `hyperspace/scene.py` — encounters are *fixed-position trigger circles* (`EncounterPoint.trigger_radius = 220`). The player either enters or doesn't; there is no pursuing-enemy entity on the hyperspace map. The Cleanser patrol's first-hail broadcast (`HyperspaceBroadcast`, 5-second crawl) is the closest gesture toward pre-engagement tension, but the encounter still fires by collision.

**Gap**:
- No pursuing-ship entities — enemies don't chase you in hyperspace
- No cloak-runs / hide-in-a-star moments
- No "I can't escape this fight" tension

**Importance**: Nice-to-have for the slice; essential for late-game galactic feel. Hyperspace currently feels like a navigable map, not a hostile one (which fits the SCZ "we're the apex Furlings" tone in the early slice).

---

## Overall coverage estimate

### Systems fully implemented (full coverage or richer than UQM)
- **§1 Super-melee combat** — well past UQM in code size; 12+ specials wired
- **§4 Solar system / orbit view** — bit-exact UQM procgen ported
- **§7 Dialog / communication** — 129 DialogStates in 5342 LOC of characters.py; FSM layer is solid (LLM renderer deferred)
- **§9 Ship customization / module system** — ~50 modules across 7 slots, schematic vault innovating past UQM
- **§13 Quasispace / Arilou portals** — 12 portals with discovery-puzzle layer past UQM's 11

### Systems partially implemented (real but missing pieces)
- **§2 Hyperspace navigation** — fuel + in-flight menus missing
- **§3 Star map / autopilot** — no modal galaxy-wide autopilot
- **§5 Planet surface / lander gameplay** — no biological lifeforms, no cylindrical wrap, lander upgrades planned but mostly unwired
- **§6 Mineral / resource scanning** — works but UI is more abstract than UQM's three-mode globe scan
- **§8 Quest tracking** — robust content, but no in-game quest log UI
- **§10 Resource economy** — Melnorme bio-data tech-purchase loop unfinished
- **§11 Crew management** — Common Room banter is fixed line-pools (variation layer deferred)
- **§12 Sensors** — richer than UQM, no cloak-pierce
- **§14 Encounters** — fixed-coord rather than spawn-table
- **§17 Fuel + refueling** — module deltas exist but no underlying mechanic

### Systems stub or missing
- **§15 Game clock / time pressure** — no calendar, no scheduled events (deliberately replaced by flag-driven beats; consider visible day counter for atmosphere)
- **§16 Save/load** — entirely absent
- **§18 Pursuit / fleeing in hyperspace** — no pursuing-ship entities

### Rough completeness vs SC2-equivalent feature complexity
**~70%** of SC2-equivalent feature surface is in place, with the following weighting:

- **Combat + dialog + ship customization + quasispace** are at or past parity — these are most of the player's screen-time, so the *feel* coverage is higher than 70%
- **Planet surface gameplay** is ~60% (deposits + hazards work; biological lifeforms missing is the biggest gap)
- **Hyperspace + map** is ~75% (functional with notable absences: fuel, modal map, pursuit, in-flight menu)
- **Long-running game systems** (save/load, fuel, calendar) are ~15% — these are the blockers for releasing beyond a slice
- **Quest tracking + content** is ~85% if we count slice-scope only (387 quest rows authored; most species have full FSM coverage)

The remaining 30% is heavily concentrated in: persistent save/load, fuel mechanics, calendar clock, biological lifeforms on planet surfaces, modal galaxy-map autopilot, and hyperspace pursuit. The LLM dialog renderer is technically a different category (it's the variance layer over a complete FSM, not a missing system) but is the single biggest investment outstanding.
