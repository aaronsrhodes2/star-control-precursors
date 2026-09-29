# HANDOFF — anyone → SCZ: Combat Mechanics Chat

> Cross-chat dispatch queue for **combat-simulation, ship-tuning, and super-melee work** in Star Control Zero. The Combat Mechanics chat reads this file at session start, picks up open entries, implements the changes in `src/scz/combat/` (and adjacent), and marks each `✅ PROCESSED <date>` (or removes it) when done. Newest entries at the top.
>
> Other chats append new entries when their work generates combat tasks. Per the multi-chat split (memory: `project_combat_chat_split.md`), Design chat does NOT modify `src/scz/combat/*`; all combat code changes flow through this queue.
>
> **Combat lane scope**: `src/scz/combat/scene.py` (MeleeCombatScene + physics + projectiles), `src/scz/combat/ships.py` (ShipClass definitions + stat tuning), `src/scz/combat/super_melee.py` (super-melee picker), `src/scz/combat/ai.py` (AI behavior + personality vector + combat strategy archetypes), per-matchup balance tuning.
>
> **Lane discipline reminder**: Combat Mechanics chat does NOT author lore canon, image assets, audio, or hyperspace-level / style-level / dialog scene wiring. Combat chat *tunes the simulation* the Design chat scaffolds around.

---

## 2026-05-19 — Final Conflict balance: Drev-Tok wins 4/4 vs full Steward alliance

**Origin**: Testing chat, during the overnight `walk_integration_great_run` extension that drove the new `FinalConflictScene` (shipped 2026-05-18 by Design) end-to-end with the maximum-strength Steward roster.

### Test setup

`walk_integration_great_run` Phase 5-8:
- All 5 alliance flags TRUE → `build_steward_fleet(game)` returns the full **6-ship** Steward fleet:
  `[FURLING_SCOUT, ARILOU_SKIFF, ANDROSYNTH_CRUISER, MMRNMHRM_SENTINEL, THINN_BLADE, LEMMKIN_SKITTER]`
- Drev-Tok roster (fixed): 5 ships per `DREV_TOK_FLEET_IDS`:
  `[DEFENDER_VESSEL, CLEANSER_CRUISER, MYCON_PODSHIP, BURV_BROADCASTER, UTWIG_JUGGER]`
- `should_fire_final_conflict()` triggers in-engine via flags (`mhlai_destroyed=True` + `rainbow_resonator_in_cargo=True`)
- Walk waits 420s game-time at speed 10x for combat resolution

### Observed result

**Drev-Tok wins 4/4 sample runs.** Despite the Steward having a numerical advantage (6 vs 5) AND the full alliance roster, combat outcome is consistently Drev-Tok victory. Walk worked around the issue in Phase 9 by invoking `resolve_ending(game)` directly to verify the GREAT tier evaluation (snapshot preserves all 31 flags seeded in Phase 5).

### Why this matters

Per `references/lore/the-final-conflict.md` § Canon revision 2026-05-18, the climax is **forced combat — negotiation always fails**. So the player's only path to the canon GREAT/BEST ending is to **win the super-melee**. If even the full 6-ship alliance loses 4/4 against the canonical Drev-Tok 5, then Aaron's "every successful alliance is rewarded" promise to the player is broken.

The endings runtime still resolves correctly to GREAT because all the upstream flags (species saved, crew recruited, side-quests done) are evaluated — the Final Conflict outcome is what gates **whether the player reaches** the ending evaluator at all. With current balance: loss → Time Drive snapshot restore → player tries again forever, never sees their ending.

### Suggested investigation

1. **Per-ship ranking pass** — `src/scz/combat/ships.py`: are the Homesteader-coalition ships (CLEANSER_CRUISER, MYCON_PODSHIP, BURV_BROADCASTER, UTWIG_JUGGER, DEFENDER_VESSEL) over-tuned, or are the Steward-side ships (ARILOU_SKIFF, ANDROSYNTH_CRUISER, MMRNMHRM_SENTINEL, THINN_BLADE, LEMMKIN_SKITTER) under-tuned for the slice's final fight?
2. **AI behavior pass** — `src/scz/combat/ai.py`: is the per-ship AI archetype assigning Drev-Tok ships an aggressive-focus behavior while the player's allies use a defensive default? If so, the player's 6 ships may be fighting individually while Drev-Tok's 5 focus-fire.
3. **Combat-strategy archetype dispatch** — per `project_combat_strategy_archetypes.md`, this matchup needs the full N×N validation sweep (Drev-Tok coalition × Steward alliance permutations) once the strategy layer is in place. Until then, manual tuning.

### Reproduction

```powershell
Set-Location D:\Aaron\development\star-control-precursors\.claude\worktrees\elegant-bartik-733a37
python -m scz --windowed --test walk_integration_great_run
```

Walk currently passes 13/13 because Phase 9 sidesteps the loss by calling `resolve_ending` directly. If Combat fixes the balance, change Phase 8's `expect_scene_in(["EndingScene", "HyperspaceScene"])` to `expect_scene("EndingScene")` — that's the regression assertion proving the win-path is now reachable.

### Code refs

- `src/scz/content/final_conflict.py:DREV_TOK_FLEET_IDS` — fixed 5-ship antagonist roster
- `src/scz/content/final_conflict.py:build_steward_fleet` — alliance-flag-driven 1-to-6 ship player roster
- `src/scz/scenes/final_conflict.py:_handle_win` / `_handle_loss` — outcome routing
- `src/scz/testing/scripts.py:walk_integration_great_run` Phase 5-9 — the integration-walk driver

### Priority

**HIGH** — this is the single biggest blocker to the player ever *seeing* their non-DISASTROUS ending. Without a winnable Final Conflict, the entire endings tier system (Block A, shipped) renders only on `resolve_ending` debug invocation, not gameplay.

**Status**: ☐ Open

---

## 2026-05-18 — Incoming weapon FX + star sprites (Image chat dispatch)

**Origin**: Image chat. Aaron's directive (2026-05-18): "Nearly all of our weapon effects are either placeholders (colored circles) or we have generated them and not wired them in. Let the Combat Mechanics lane know when you have re-generated all of the weapon effect sprites to be pretty. We need gorgeous images for the stars that we will see in the hyperspace view and also in combat view and solar system view. Make sure you inform Combat Mechanics which sprites are new so it can wire them in for you."

**Status**: ☐ Open. **Wiring is fully automatic for projectile sprites** — `_load_projectile_sprite` already keys off `projectile_<ship_id>.png` in `assets/ships/sprites/`. Combat chat only needs to wire the **star sprites** (new code path) when those land.

### Weapon FX projectile sprites — wiring contract

All 17 ships now have entries in `SHIP_SPRITES` ([scene.py:46](src/scz/combat/scene.py:46)). Of those, 11 had projectile sprites already wired (rendered via `_load_projectile_sprite` at [scene.py:707](src/scz/combat/scene.py:707) — falls back to colored circle if `projectile_<ship_id>.png` is missing).

**6 new ships that currently render colored-circle placeholders** (added to `SHIP_SPRITES` 2026-05-18, no projectile sprite yet):

| ship_id | Weapon flavor | Status |
|---|---|---|
| `burv_broadcaster` | cyan-blue concentric shockwave (resonance pulse) | 🟡 Firefly drift v1 produced asteroid-like output; re-rolling with v2 prompt |
| `compeller_vessel` | translucent green sedation beam | ☐ Queued |
| `lemmkin_skitter` | warm yellow tracer bolt | ☐ Queued |
| `mycon_podship` | purple-red bio-plasmoid | ☐ Queued |
| `thinn_blade` | iridescent teal-violet-gold knife-thin lateral cut | ☐ Queued |
| `utwig_jugger` | heavy amber ceremonial bolt with green shield-halo | ☐ Queued |

**Wiring action when sprites land** = *none*. They drop into `assets/ships/sprites/projectile_<ship_id>.png` and `_load_projectile_sprite` picks them up. Combat chat's only job: verify the sprite renders correctly in `walk_super_melee` by changing the ships in the test to include each new ship at least once.

Source prompt files (Aaron can drive these into Firefly interactively): `tools/firefly_prompts/tier1_weapons/projectile_<ship_id>.txt`. All have been rewritten with explicit anti-celestial-body language because Firefly Image 3 drifts toward "asteroid in space" interpretation when given orb-shape prompts.

### Star sprites — new wiring required

Currently stars in **hyperspace** are 2-7px solid circles (`hyperspace/starmap.py:101-102`). Stars in **solar system** view are layered concentric circles ([system/scene.py:382-406](src/scz/system/scene.py:382)). Combat has a 180-dot procedural starfield ([combat/scene.py:348-354](src/scz/combat/scene.py:348)).

Image chat is generating gorgeous painted star sprites at `assets/stars/star_<color>.png` for each of the 6 SC2 spectral colors:

| File | Color name | Hex tint reference |
|---|---|---|
| `star_blue.png` | BLUE_BODY | (120,160,255) |
| `star_white.png` | WHITE_BODY | (240,240,255) |
| `star_yellow.png` | YELLOW_BODY | (255,230,120) |
| `star_green.png` | GREEN_BODY | (140,255,160) |
| `star_orange.png` | ORANGE_BODY | (255,180,100) |
| `star_red.png` | RED_BODY | (255,110,100) |

Plus one **combat starfield backdrop** at `assets/combat/starfield.png` (16:10 aspect, replaces the 180-dot procedural rendering).

**Wiring required in Combat chat lane** (and adjacent — system + hyperspace are normally lore/design lane but the rendering paths are tightly coupled, so flagging here):

1. ✅ **Combat starfield backdrop** ([combat/scene.py:348](src/scz/combat/scene.py:348)) — *Wiring landed 2026-05-18.* Replaced the procedural `for _ in range(180): pygame.draw.circle(...)` loop with `_load_starfield_sprite()` + `screen.blit(starfield, (ox, oy))`. Procedural fallback preserved when `assets/combat/starfield.png` is missing. Combat starfield sprite drops at that path with no further code change.

2. ✅ **Solar system star** ([system/scene.py:_draw_star](src/scz/system/scene.py:432)) — *Wiring landed 2026-05-18.* Replaced the 4-layer concentric circle render with `_load_star_sprite(self.star["color"])` + `screen.blit(...)`. Sprite is scaled to `base_radius * 4` (disc + corona). Procedural fallback preserved when `assets/stars/star_<color>.png` is missing. Each color sprite drops at the mapped path with no further code change.

3. ☐ **Hyperspace stars** ([hyperspace/starmap.py:101-102](src/scz/hyperspace/starmap.py:101)) — At low zoom the per-pixel-circle render is fine (the star is 2-7px, sprite would be over-detail). At high zoom (zoom > LABEL_MIN_ZOOM threshold) it'd be nice to blit a small star sprite instead. **Lower priority** — only do this if Combat chat thinks it's worth the conditional. *Not yet wired.*

Two of three wiring points are already done; the painted PNGs will activate the sprite paths automatically when they land in `assets/combat/starfield.png` and `assets/stars/star_<color>.png`. The third (hyperspace zoom-in) is optional polish — defer unless Combat chat decides the conditional is worth adding.

### Acceptance

For each new ship's projectile sprite: `walk_super_melee` with that ship as one of the combatants. The projectile sprite should render rotated correctly along velocity vector. No crash on missing sprite (existing fallback path tested 2026-05-18).

For star sprites: `python -m scz --windowed`, enter hyperspace at high zoom on a colored star + enter a system + start a combat fight. All three views should show the new star art.

### Status

- ☐ Open as of 2026-05-18. Image chat is queueing prompts; many may have to be driven interactively by Aaron because the Chrome-MCP automation against Firefly Image 3 is producing inconsistent results past the first generation per session. Watch for prompts being committed into `tools/firefly_prompts/tier1_weapons/` and `tools/firefly_prompts/tier1_stars/`, sprites landing in `assets/ships/sprites/projectile_*.png` and `assets/stars/star_*.png`, and dispatch updates marking entries ✅ here.

---

## 2026-05-17 — Dnyarri super-melee gamble pick + disguised-encounter combat hookup

**Origin**: Design chat, from Aaron's canon (2026-05-17): *"In super-melee the player gambles by spending a middle number of points to get a random ship from it that is obfuscated by it's ship illusion ability."* Canonical doc: `references/lore/dnyarri-disguised-encounter.md`.

**Status**: ☐ Open. Phase 3 work (plot-beat mechanics) per `roadmap_to_play_field.md`. Not blocking current sessions.

### Super-melee picker — what changes

`src/scz/combat/super_melee.py` gets a new picker entry: **"Dnyarri (?)"** at the bottom of the roster.

- **Point cost**: target band **12-16 points**. Tune to your judgment. The pick should be *attractive at mid-game-points and gut-check at high-game-points*. Lower than a Furling Persuader (medium-light ship); higher than a Skiff (light scout). Aaron's canon is "middle number of points" — interpret that as roughly the median of the existing roster's costs.
- **No re-rolls**. Once locked in, the roll stands.
- **Roll on lock-in** (not on first-fire — the roll happens at pick time but is hidden):
  - Sample `actual_ship_class_id` uniformly from the catalog with these exclusions: never `FURLING_SCOUT`, never the Others' Vessel, never `ARILOU_SKIFF`. (Same actual-class exclusion list as the hyperspace disguised encounter — see doc §"What 'any ship in the catalog' means".)
  - Sample `cover_species_id` uniformly from the cover pool: `CLEANSER_CRUISER`, `MELNORME_TRADER`, `MYCON_PODSHIP`, `ANDROSYNTH`, `MMRNMHRM_SENTINEL`, `PROTO_UR_QUAN`. Cover ≠ actual (never self-disguise).
- **Picking player's view during pick**: shows "Dnyarri (?)" entry and its cost. NOT shown: the rolled cover or the rolled actual. The player has locked in *uncertainty*.
- **Both players' view in the arena, pre-fire**: the disguised ship draws with the cover species' silhouette + warp pod from `species_visual.SPECIES_WARP_POD[cover_species_id]`. Sensor / HUD tags read as the cover.
- **First-fire reveal**: when the disguised ship fires *any* weapon or uses *any* special, both players see the snap to DNYARRI yellow (color from `SPECIES_WARP_POD["DNYARRI"]`) + the floating "DNYARRI — controlling [ACTUAL_NAME]" tag for ~3s + the HUD species-tag swap. The actual ShipClass's stats and AI were *already* playing through; only the rendering was disguised.

### Hyperspace disguised-encounter combat hookup

When the Design chat ships the hyperspace disguised-encounter spawn loop (Phase 3 implementation), the combat-scene entry needs to support the same cover/actual split. Two combat-side pieces:

1. `MeleeCombatScene` accepts a new optional kwarg `dnyarri_cover_species_id: str | None = None`. When non-None, the rendering layer uses the cover species' silhouette + warp pod until the disguised ship fires its first weapon or special; then snaps to DNYARRI palette.
2. The reveal trigger fires from inside the weapon-discharge code-path (combat lane). Cleanest hook: a flag on the AI-controlled ship instance that the rendering layer reads each frame. First weapon discharge sets the flag once; rendering applies the snap from the next frame onward.

### Catalog audit ask

Per the mechanic doc, the actual ShipClass plays through normally. Combat Mechanics chat should confirm that **every catalog ShipClass eligible for the actual-class pool** (i.e., all 15ish ShipClasses minus the 3 exclusions) handles a wholesale identity-swap without crashing. Specifically: any ship-AI that hard-codes "this is a Furling escort" or "this ship's pilot is Slylandro and therefore won't ram" assumptions needs to be neutralized to AI-only logic for the disguise case. Flag any class that wouldn't survive.

### Test plan (Testing chat owns the walks)

Three walks Combat Mechanics should make sure the combat side handles, so Testing can write them:

- `walk_dnyarri_disguised_first_encounter` — hyperspace teleport into a disguised encounter; combat opens with cover ship visuals; first weapon fire flips palette to DNYARRI; expect met flag + Bio-Archive entry unlock
- `walk_dnyarri_super_melee_gamble` — super-melee picker confirms Dnyarri costs ~12-16 pts; lock-in rolls actual + cover; arena entry shows cover silhouette; first fire snaps to DNYARRI; verify the actual ShipClass's signature weapon is what fired (not the cover's)
- `walk_dnyarri_disguised_catalog_sweep` — N iterations of disguised encounters cycling through every eligible actual_ship_class_id; verify each handles the wholesale identity-swap and combat resolves cleanly

### Dispatch this back to

When done:
- Update this entry's Status line to indicate completion
- File a return-dispatch to **Design chat** noting which engine APIs landed so Design can wire the hyperspace spawn loop
- File a return-dispatch to **Testing chat** with the actual super-melee point cost (the 12-16 band exact value) so the walk asserts pin to the real number

---
