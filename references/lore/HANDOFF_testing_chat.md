# HANDOFF — anyone → SCZ: Testing Chat

> Cross-chat dispatch queue for **walk-test work** in Star Control Zero. The Testing chat reads this file at session start, picks up open entries, writes/extends walk-tests in `src/scz/testing/scripts.py`, runs them, and marks each `✅ PROCESSED <date>` (or removes it) when caught up.
>
> Other chats append new entries when their work generates testing tasks (a new feature lands → it needs a walk; a new content beat lands → it needs verification; a bug surfaces → it needs a repro walk).
>
> **Testing lane scope**: `src/scz/testing/scripts.py` walk-tests, `src/scz/testing/harness.py` infrastructure, bug-hunting via the scene switcher (F1 / R3), bug reports. Small obvious bug fixes are in-lane; large/design-decision bugs dispatch back to Design.
>
> **Lane discipline reminder**: Testing chat does NOT author new content, scenes, lore, art, audio, or design. Testing chat *verifies* that the other chats' work runs correctly, *finds* bugs that walks didn't predict, and *reports* findings.

---

## 2026-05-18 — Save/Load + Campaigns + Scrubber + Time Drive (Design — verify before merge)

**Origin**: Design chat. Aaron asked for persistent save/load with campaign management, screen-grab thumbnails per save, a save-scrubber UI gated by a 4-minute lockout, and Time Drive re-routed through the same scrubber.

**Status**: ☐ Open. 5/5 existing regression walks pass post-merge (`walk_super_melee`, `walk_tutorial_arc`, `walk_hyperspace_encounters`, `walk_customization`, `walk_upgrade_loop`). Roundtrip test included in this entry. No walk-tests yet specifically exercise save/load — they need to be authored in this lane.

### What landed

**New file**: `src/scz/engine/persistence.py` (~470 LOC). Public API:

- `serialize_game(game) → dict` / `restore_game(game, state)` — full game-state JSON dump. Covers `flags`, `cargo`, `credits`, `ship_modules`, `uninstalled_modules`, `fleet`, `schematics`, `consumed_schematics`, `frame_count`, plus timestamps. Schema version 1.
- `CampaignManager` — discovery (`list_campaigns()`), creation (`create_campaign(display_name)` → slug), deletion, auto-save scheduling (`tick(dt, game)` increments save-clock, fires every `AUTO_SAVE_INTERVAL_S=60`), `snapshot(game)` (sync serialization, async disk write via daemon thread), `list_saves(slug) → list[SaveInfo]`, `load_state(save_path)`, `load_latest(slug)`.
- `CampaignInfo` / `SaveInfo` dataclasses with `age_human()`, `is_loadable()`, `time_until_loadable()`.

**Tunables** (top of `persistence.py`):
```python
AUTO_SAVE_INTERVAL_S = 60.0
SAVES_PER_CAMPAIGN   = 20      # 20 minutes of rolling history
LOAD_LOCKOUT_S       = 240.0   # 4-minute scrubber barring
THUMB_W = 256; THUMB_H = 144
TIME_DRIVE_DEFAULT_CURSOR_S = 300.0
```

**Save layout** under `~/.scz/campaigns/<slug>/`:
- `meta.json` — display name + timestamps
- `save_<unix_ms>.json` — game-state dump
- `save_<unix_ms>.png` — 256×144 screen-grab thumbnail (best-effort)

**New scene**: `src/scz/scenes/save_scrubber.py:SaveScrubberScene`. Thumbnail picker with vertical list on the left + big preview on the right. Cursor only lands on loadable (≥4-min-old) saves; locked rows render greyed with `🔒 unlocks in Nm Ns`. Confirm on a locked row is a no-op. Same scene serves both Load Campaign (cursor on newest loadable) and Time Drive (cursor on closest-to-5-min-ago loadable).

**Modified files**:
- `src/scz/engine/game.py` — `CampaignManager` instantiated; `tick()` called per frame; `_apply_campaign_rewind()` opens scrubber on Time Drive input; final-snapshot in `finally:` block on game shutdown; clean `campaign_manager.shutdown()` in finally.
- `src/scz/scenes/stubs.py:MainMenuScene` — real menu (Continue / New Campaign / Load Campaign / Super Melee / Quit). Continue = auto-load latest. Load Campaign → campaign list → scrubber. New = auto-name `Stardate YYYY-MM-DD HHMM`, take immediate first snapshot, drop into Mh-Lai.

### Manual smoke test (Aaron has already run)

1. `python -m scz.main --windowed` from `src/`
2. New Campaign → first auto-save fires immediately, captures the Mh-Lai backdrop as the thumbnail
3. Play for >4 minutes → Time Drive button opens scrubber; cursor on save closest to 5min ago
4. Verify cursor skips greyed (locked) rows; confirm on locked is silent
5. Restore a save → chronometric flash, lands in Mh-Lai with restored state
6. Quit → re-launch → Continue → resumes from latest save

### Roundtrip test (already passes)

```bash
SDL_VIDEODRIVER=dummy python -c "
from scz.engine.persistence import CampaignManager, serialize_game, restore_game
# build fake game, snapshot, load, assert state matches
"
```

Verified: serialize → write → load → restore preserves credits, flags, fleet, modules.

### Walk-tests to author (Testing lane)

These are the high-value walks for verifying save/load:

1. **`walk_save_load_roundtrip`** — fresh Game → seed flags/cargo/credits → invoke `campaign_manager.snapshot()` → mutate game state → invoke `campaign_manager.load_state(latest_save_path)` + `restore_game()` → assert all fields back to seeded values. No scene transitions needed; this is pure data-layer.

2. **`walk_main_menu_new_campaign`** — start at MainMenuScene → press confirm on first item (New Campaign when no campaigns exist) → expect StationScene → assert `game.campaign_manager.has_active() == True` → assert a save exists in the campaign dir → cleanup (delete the test campaign).

3. **`walk_main_menu_load_campaign`** — pre-seed a campaign dir with a hand-rolled save (use `serialize_game(game)` + `campaign_manager.create_campaign(...)` + `snapshot()`) → enter MainMenuScene → navigate to Load Campaign → confirm → assert SaveScrubberScene → confirm → assert StationScene with seeded state restored. Cleanup.

4. **`walk_scrubber_lockout`** — create campaign with several saves at FAKE wall-clock ages (modify `saved_unix` in the JSON directly) → enter SaveScrubberScene → assert cursor lands on a loadable save (not the newest) → press menu_down through all rows → assert cursor never lands on a locked row → assert confirm on a locked row is a no-op.

5. **`walk_scrubber_20_save_cap`** — write 25 fake saves into a campaign dir → trigger `_prune_old_saves` (or trigger one new snapshot which calls the worker) → assert only the newest 20 remain on disk → assert .png siblings of the deleted .json files are also gone.

6. **`walk_time_drive_opens_scrubber`** — start a campaign → press the rewind input → assert SaveScrubberScene (not legacy per-scene rewind) → cursor sits within 60s of the 5min target.

7. **`walk_thumbnail_capture`** — start a campaign → take a snapshot with `game.screen` filled with a recognizable color → wait for worker to flush → load the PNG from disk → assert it's 256×144 and the dominant pixel color matches what was on screen.

### Edge cases / gotchas

- **Daemon worker thread**: `pygame.image.save` is called from a non-main thread on the thumbnail surface. On most platforms this is safe because the surface is detached via `.copy()` before crossing the thread boundary, but watch for sporadic save failures on weird disk setups. Failure is best-effort — JSON still writes, thumbnail just won't appear in the scrubber (placeholder rendered).
- **Cursor when all saves locked**: A fresh campaign with <4 minutes of play has zero loadable saves. Cursor parks on the oldest locked row; confirm is silent. Player can wait or back out. Verify the back-out works.
- **Same-second saves**: `save_<unix_ms>.json` uses millisecond precision, but rapid successive snapshots (e.g. via `walk` test loop) could collide. Worker overwrites on collision — not a bug but worth noting if a walk-test takes many saves in <1ms.
- **20-save cap pruning**: Pruning happens in the worker thread AFTER each successful write. A walk that takes 25 snapshots and immediately asserts disk count may race — sleep ~0.5s or call `mgr.shutdown()` to drain the queue before asserting.
- **Test mode `test_speed` multiplier**: `tick(dt)` uses game-`dt`, which is wall-`dt` × `test_speed`. At `test_speed=10`, one wall second = 10s of save-clock; auto-saves fire 10× more often. Fine for `walk_*` tests but worth knowing.
- **`game.screen` in headless tests**: `SDL_VIDEODRIVER=dummy` produces a working surface; thumbnails capture dummy pixels (probably solid black). Walks don't need to assert thumbnail *content*, just existence.
- **`Continue` ignores lockout**: deliberate — only the scrubber UI bars the recent 4 min. A walk that uses `_continue_latest` will always get the newest save regardless of age.

### Lane discipline

The save/load system is fully built and live. This entry asks Testing chat to:
1. Author walk-tests #1-#7 above (or whichever subset bandwidth allows)
2. Add them to `tools/run_walks_parallel.py`'s sweep
3. Flag any edge cases the walks surface back to Design

Bugs surfaced during walk authoring that look like 1-line fixes (e.g. missing flag seed, off-by-one in cursor math) → fix in-lane. Bugs that smell like design questions (e.g. "should Continue actually load the latest *loadable* save instead of the latest save?") → dispatch back to Design via `HANDOFF_design_chat.md`.

---

## 2026-05-17 — `walk_loaded_ship_tour` failing on Coel Tessar Beat 4 interception

**Origin**: Design chat (regression sweep after Species Domains MVP land).

**Status**: ☐ Open. 5 assertions failing in `walk_loaded_ship_tour`. Standalone-reproducible; NOT caused by Species Domains.

**Repro**:
```
SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy PYTHONPATH=src \
  python -m scz.main --test walk_loaded_ship_tour
```

**Symptom**: Two scene assertions fail with `expected scene 'HyperspaceScene' / 'SystemScene', got 'DialogScene'`. The walk installs `scanner_mk3` via `set_module_inventory` + customization, which sets `flag:scanner_mk3_installed=True`. On the player's first HyperspaceScene entry after that, `_maybe_spawn_encounters` fires Beat 4's Coel Tessar trigger (gate: `scanner_mk3_installed` AND NOT `met_androsynth`). The walk doesn't seed `met_androsynth=True`, so the dialog launches and breaks the rest of the script.

**Suggested fix** (one-line): add `s.set_flag("met_androsynth", True)` at the top of the walk (right after `s.set_speed(3.0)`) to skip the Beat 4 hook. The walk's intent is "fully-loaded ship tour" — there's no story-reason for Coel Tessar to fire mid-tour. Alternative: also retire any future hyperspace ambient encounters that could fire en-route by seeding their `not_flag` / `met_*` flags. The Mycon and Melnorme domain patrols spawn at (6915, 2300) / (5673, 2783) / (5720, 4700) — the walk's east-flight from (1793, 1450) for 4.5 wall-seconds at test_speed 3.0 covers 16200 game units and crosses several of those.

**Why this is Testing-lane**: the walk was authored in this lane; the fix is purely test-side (flag seeding), no game-code change required.

---

## 2026-05-17 — Species Domains MVP shipped; new walk `walk_species_domain_patrol`

**Origin**: Design chat.

**Status**: ✅ PROCESSED 2026-05-17 (walk green standalone + in parallel sweep, 4/4 passing).

New content + scene wiring shipped in this Design session:

- `src/scz/content/species_domains.py` — 6-domain registry (Furling Hearth, Cleanser Approach, Slylandro Sphere, Mycon Whisper, Melnorme Network, Dnyarri Trail), `domain_at(x, y)` lookup, `active_patrols(game)` enumerator
- `src/scz/hyperspace/scene.py` — `_draw_species_domains` boundary render before stars, domain HUD readout in `_draw_hud`, `_make_domain_patrol_trigger` factory, per-domain trigger registration loop, per-domain patrol spawn integration in `_maybe_spawn_encounters`
- `walk_species_domain_patrol` exercises the Melnorme friendly trigger (teleport onto patrol → trigger fires → met flag set, still in hyperspace)

**What would benefit from more coverage** (Testing-lane to author when bandwidth permits):
- A `walk_species_domain_combat_mycon` that teleports into Mycon Whisper patrol pos and asserts `MeleeCombatScene` opens
- A `walk_species_domain_cleanser_gated` that verifies Cleanser Approach patrols do NOT spawn without `tutorial_complete=True`, and DO spawn after
- A `walk_species_domain_retire` that fires one patrol, re-enters hyperspace, asserts the patrol is gone

Roadmap context: see `references/lore/roadmap_to_play_field.md`. Species Domains is Phase 1 of a 6-phase plan to a full play field. Phase 2 (queued species implementation) will keep generating new content walks; we expect ~1-2 new walks per species.

---

## 2026-05-17 — Test framework infrastructure now shipped; Testing chat takes over operation + extension

**Origin**: Design chat. Aaron asked for a "solid, fast testing framework" so the project can be built/tested with minimal manual interaction. The framework is now implemented; this entry hands operation off to the Testing chat.

### What's been built (Design lane, available for use)

All under `tools/` (standalone Python; each is one self-contained script):

| Tool | What it does | First-run numbers |
|---|---|---|
| `tools/run_walks_parallel.py` | Runs all walks via concurrent subprocess pool. Replaces the sequential `for t in walks; python -m scz.main --test $t` loop. | 34 walks / 356 assertions in 46s (was 4-5min) |
| `tools/dialog_coverage.py` | BFS-walks every DialogCharacter FSM; flags orphan states, dead-ends, broken `next_state_id` transitions, side-effect inventory | 14 factories audited, 0 failures, 3 with benign dynamic-initial orphans |
| `tools/module_stat_audit.py` | Installs each module; verifies `effective_stat` returns the declared delta; validates `slot` + `cost_resources` keys | 28 modules / 0 issues |
| `tools/status_dashboard.py` | Single-page view across HANDOFFs (open / in-prog / processed / backlog / wont-do) + test-queue + recent commits | Current state: ~15 open dispatches in Design, ~4 in Image, ~4 in Audio, ~6 in Testing |
| `tools/check_stubs.py` | Greps TODO_AVATAR / TODO_LORE / TODO_AUDIO / TODO_DESIGN markers across codebase; groups by owner-chat | Image=36, Lore=37, Audio=2, Design=2 |

Three new fuzz/smoke walks (in `src/scz/testing/scripts.py`):

- `walk_input_fuzz` — visits 14 major scenes via the switcher, exercises all axes + all menu nav keys, verifies no crash. **29/29 pass, 25s.**
- `walk_lander_collect_all` — full deposit-sweep + lift-off happy path. 3/3 pass.
- `walk_lander_liftoff_immediate` — zero-haul exit. 3/3 pass.

### What Testing chat should do with this

1. **Run the parallel sweep before each session start**:
   ```
   python tools/run_walks_parallel.py
   ```
   Anything failing red is a real regression filed by *someone* between sessions. Triage: identify the responsible lane (use `git log` + the walk's pre/post-mortem), file a fix dispatch to that lane.

2. **Run the audits weekly** (or whenever a content registry changes):
   ```
   python tools/dialog_coverage.py
   python tools/module_stat_audit.py
   ```
   Dialog coverage failures = orphan states, broken transitions, or dead-end traps in the FSM. Module audit failures = catalog typos or stat-math regressions. Both should be zero-failure at all times.

3. **Run the status dashboard at session start** to know what's in flight:
   ```
   python tools/status_dashboard.py
   ```

4. **Extend the walk coverage** along the patterns this dispatch establishes:
   - **Per-quest exhaustive branch walks** — for each species quest (Slylandro / Mycon / Uplift / Beacon / Mmrnmhrm / Chenjesu / Melnorme / Cleanser / Mraka / Dnyarri / etc.), author `walk_<quest>_<branch>` for each terminal-status outcome. The walk_inventory CSV (`tools/quest_inventory.csv`) has the canonical FSM data; mechanical translation to walks should be doable.
   - **Per-crew side-quest walks** when the side-quest content lands (currently the 5 crew side-quests are stubbed; per `HANDOFF_design_chat.md` Crew side-quests entry).
   - **Per-ship combat smoke walks** — for each ShipClass, a walk that picks it in Super Melee against a representative opponent and verifies the combat finishes (any outcome). Coordinate with Combat Mechanics chat — they own `src/scz/combat/*`.
   - **Per-Fall-branch walks** — `walk_mhlai_fall_race_success`, `walk_mhlai_fall_race_witness`, `walk_mhlai_fall_cleanser_acceleration` to cover the three branches `walk_mhlai_fall_dont_race` doesn't.
   - **Hearth-of-Iron-dock walk** — confirms the StationScene rebrands post-fall.

5. **File bug reports** (via this HANDOFF file's Findings section or via `HANDOFF_design_chat.md` for code-mod fixes). Bug format: what scene + what action + observed vs expected + flag state + (optional) screenshot.

6. **Triage convention** for HANDOFF status lines (newly canonical):
   - `Status: ☐ Open` — not started; eligible for pickup
   - `Status: ⏳ In-Progress` — partial MVP shipped, follow-ups deferred
   - `Status: 🗄️ Backlog` — recognized work, gated on something else first
   - `Status: ✅ PROCESSED <date>` — shipped; entry can be pruned next session
   - `Status: ❌ Won't-Do <date>` — explicitly de-prioritized

   The dashboard recognizes all five. Going forward, when picking up or shipping work, update the status line consistently — this makes the dashboard's lane-capacity hint accurate.

### Cross-chat dispatches that drop out

- **Design chat**: when the Testing chat finds bugs, file via `HANDOFF_design_chat.md` (or `HANDOFF_lore_chat.md` for content issues). Design will fix.
- **Combat Mechanics chat**: combat-related bugs go directly to that chat's lane; don't route through Design.

### Status

- ☐ Open as of 2026-05-17 — framework ready; Testing chat takes ownership of operation and extension.

---

## 2026-05-17 — Full gameplay sweep request (Design batch — many new features)

**Origin**: Design chat. Aaron asked for a Testing-chat pass over recent work, including gameplay/feel feedback (not just pass/fail). This is a broader ask than the usual "verify this walk" — it wants the Testing chat in a real pygame window with the controller / keyboard, *playing the game* and reporting what feels off.

**Worktree**: `elegant-bartik-733a37`.

### 1) Automated regression — already filed as queue job

A queue job is in `.claude/test-queue/inbox/` requesting `["all"]` walks. That covers:
- Tutorial arc (Beats 1-7)
- Orbit + surface + hazard
- Trade + customization + upgrade loop
- Bio-Archive
- Hyperspace encounters + Cleanser cooperate + Cleanser combat
- Mraka recruitment
- Visit proto-species + salvage wreck + Dnyarri encounter + Melnorme recruitment
- The two parity probes (teleport-into-zone + retire-after-resolved)
- The new dim-tier probe (`walk_system_visit_dim_tier`)
- Super Melee + Melnorme trader + Arilou Sage

20 walks total at last Design-chat regression. **Expected: 20/20 green, 241/241 assertions.** Anything red is a real regression.

### 2) Manual playtest targets (Testing chat — visual + feel)

The automated walks confirm flag mutations and scene transitions. They cannot confirm:
- *Visual quality* (the dummy video driver disables rendering)
- *Pacing* (does the dialog feel too long or too short?)
- *Discoverability* (do players naturally find the new features?)
- *Bugs invisible to assertions* (e.g., HUD text overlaps, audio cues missing)

Recent shipped surfaces worth opening in a real window and exercising:

**Hyperspace map — visit-aware dim tier + nearest-star HUD readout** ([src/scz/hyperspace/scene.py](src/scz/hyperspace/scene.py), [src/scz/hyperspace/starmap.py](src/scz/hyperspace/starmap.py), [src/scz/content/system_scan.py](src/scz/content/system_scan.py)):
- Enter hyperspace at game start. All stars at full brightness; HUD reads `(unexplored)` for the nearest.
- Fly to any nearby star, enter the system, lift off (no extraction needed). Back at hyperspace, the star should appear slightly dimmer; HUD reads `VISITED · resources 100%   anomalies 0`.
- Land on a planet, collect a haul, lift off → cargo committed AND extraction recorded.
  - Drain most of the system (multiple landings to push below 30% remaining). HUD's resources % drops; eventually the star renders **very dim** (tier 2) and HUD reads `DRAINED · explored`.
- Visit a named system (e.g. Beta Orionis = Dnyarri, or any MELNORME_PROTO super-giant). The HUD shows `anomalies N` while undiscovered. After resolving the dialog, the anomaly count should drop. With all anomalies discovered AND extraction below 30%, the star renders tier 2 (very dim).
- **Subjective feedback wanted**: Is the dim contrast strong enough at fullscreen? Is the HUD's `resources NN%   anomalies N` line legible? Does the badge color (slate grey for DRAINED, muted green for VISITED) read clearly against the starfield?

**Lander surface** ([src/scz/planet/scene.py](src/scz/planet/scene.py)):
- Procedural terrain texture per planet type — boulders / dunes / lava veins / ice cracks / wave strokes / etc.
- Sensor ring + scan pulse around the lander; hazard chevron when near active hazards.
- HUD SENSORS readout — `deposit / hazard / tractor` values, dim at base, bright after upgrade.
- The full manual playtest checklist for this surface is already in [tools/manual_playtest_lander.md](tools/manual_playtest_lander.md). Re-run that sweep and note any drift since it was authored.

**Cleanser climax dialog** (Vael-Souren — `walk_cleanser_*`):
- Trigger via the hyperspace encounter point — flag-gated; the walks set the prereqs. To trigger in normal play, you need `met_cleanser_patrol AND heard_about_others`.
- All three branches: Cooperate / Negotiate (1 or 2 cycles) / Refuse (combat).
- **Feedback wanted**: Is Vael-Souren's voice *gentle* enough? The design doc says they should never sound triumphant. Is the combat-launch transition jarring? Does the dialog land emotionally or feel rote?

**Mraka recruitment** (`walk_recruit_mraka`):
- Trigger: dock at Mh-Lai after `scanner_mk3_installed`. New menu option "Talk to Mraka (Sure-Foot)" appears.
- The Drifter's Circuit is a placeholder beat (currently a single dialog state); flag this if you think it deserves a real minigame.
- **Feedback wanted**: Is Mraka's voice warm enough? Does her family-loss reveal land?

**Melnorme recruitment** (`walk_melnorme_recruitment`):
- Trigger: speak to any super-giant Melnorme trader → new option "Will the Melnorme migrate with us?" (gated on `has_distress_beacon`). Direction is to Alpha Vulpeculae.
- At Alpha Vulpeculae: Council → Beacon → Super-Mart shelving test → awaiting witness → commit.
- **Feedback wanted**: The shelving test (`supermart_intro` → `supermart_front_fail`/`supermart_back_pass`) is the slice's gallows-comic peak. Does the front-shelf comic dismissal feel right? Is the elder's *"You may have known, or you may have guessed"* line landing?

**Dnyarri encounter** (`walk_dnyarri_encounter`):
- Trigger: fly to Beta Orionis. Survey Commander Vesh Vasa-Lon dialog auto-launches.
- Three branches: cleanse / observe / defer.
- **Feedback wanted**: Vesh's professional-but-troubled register. Does the player feel the weight of the recommendation, or is it pro-forma?

**Salvage wrecks + ambient encounters** (`walk_salvage_wreck`):
- 4 salvage wrecks scattered across deep space. With Echo Sensor installed, they appear on the map as ship-kind ripples.
- 16 ambient ripples (8 drifters, 4 distant Other-echoes, 4 anomaly pulses) — surfaced via Echo Sensor, not interactable.
- **Feedback wanted**: Are the ambient ripples too dense or too sparse? Do they make the void feel alive or cluttered?

### 3) Report back

Append findings to this file under a `## Findings 2026-05-17` section, or — for fast-turnaround items — file directly in `HANDOFF_design_chat.md` (Design owns code-mod fixes) or `HANDOFF_image_chat.md` (visual issues).

Bug reports should include: what scene + what action + observed vs expected + screenshot if applicable.

**Status**: ✅ PROCESSED (automated portion) — see Findings 2026-05-17 below for the gap on manual visual/feel.

---

## Findings 2026-05-18 (LATE) — Overnight great-run attempt + design-chat unlock

### TL;DR for Aaron (read on waking)

You asked the testing chat to drive `walk_integration_great_run` — boot, gather materials, talk to NPCs, traverse, defeat the final fleet, see the cutscene, no time drive — and dispatch any failures.

**Honest result**: the harness physically reaches **Phase 1-4** (Boot → Beat 1 Halia → Undock → SystemScene → flight attempt). Phase 5+ is blocked, but the blockers narrowed dramatically during this session because **the design chat shipped the endings runtime + Final Conflict scene while I was working**. The 23-piece path-to-finish dispatch I filed earlier today is now down to ~12-15 missing pieces.

### What design chat shipped overnight (parallel sweep grew from 57 → 64 walks)

- `src/scz/content/endings.py` — full `evaluate_ending(game)` + `apply_ending(game, tier)` per the 6-tier canon (`BEST` / `GREAT` / `GOOD` / `AT_COST` / `UNSUCCESSFUL` / `DISASTROUS`)
- `src/scz/content/final_conflict.py` — `should_fire_final_conflict(game)` trigger
- `src/scz/scenes/final_conflict.py` — `FinalConflictScene` class
- `src/scz/scenes/ending.py` — `EndingScene` class (reads `slice_ending`, renders the tier)
- **Auto-fire wiring**: `HyperspaceScene.on_enter` now auto-fires the Final Conflict if `should_fire_final_conflict()` returns True. A loss-rewind sets `final_conflict_just_rewound` to prevent infinite re-fire.
- New walks: `walk_ending_tiers` (24 asserts, drives all 6 tiers through the evaluator + applier), `walk_final_conflict` (3 asserts, 49s), `walk_anomaly_discovery`, `walk_planet_life`, `walk_sensor_suite`.
- `walk_perfect_run` was updated to use `s.invoke("scz.content.endings.resolve_ending")` — it now drives the REAL evaluator and gets `slice_ending=BEST` back from canon. Still 33/33 green, but now meaningful.

**Block A of my path-to-finish dispatch is effectively done.** Mark the 2026-05-18 endings-runtime HIGH PRIORITY entry as ✅ PROCESSED in `HANDOFF_design_chat.md`.

### What this session's `walk_integration_great_run` actually verified

In strict mode (no `set_*`, no switcher, no rewind):
- Phase 1 ✅ — Boot → MainMenu → confirm → StationScene
- Phase 2 ✅ — Beat 1 Halia opening dialog, walked through `start` state, exit back to Station
- Phase 3 ✅ — Undock via menu → SystemScene
- Phase 4 — Fly inward + attempt orbit. **The walk's confirm doesn't capture orbit because the planet's orbital angle at that wall-clock moment doesn't put it within `PLANET_INTERACT_RADIUS=40` of the player.** Walks through the action without failing (uses `expect_scene_in` for the union), but the actual gameplay outcome is "you flew toward the inner system, no planet captured." 8/8 assertions pass.

Total reach: ~5-10% of the perfect-run's intended depth (per a quick gut-feel weighting; actual content traversed is 4 of the slice's ~40 narrative beats).

### Blockers I hit and what I filed

1. **`cancel`/B in `HyperspaceScene` and `StationScene` calls `self.game.quit()`** — filed at top of `HANDOFF_design_chat.md`. This is the single biggest unblocker for integration walks: it silently terminates any walk that double-cancels through scenes. Discovered by re-running with stdout/stderr split + checking exit code (0, no error, no Test-complete line — game just quit out from under us).

2. **`SystemScene` has no planet-targeted autopilot** — to reach Mh-Lai or Furlmart specifically in strict mode, the walk would need either:
   - A new `set_target_planet(name)` harness primitive (testing-lane authoring — possible), OR
   - A new in-game autopilot-to-planet behavior (design-lane work; would be the player-facing equivalent)
   Filed as part of the path-to-finish overview's "Mh-Lai's orbital position is time-dependent" note.

3. **The 4 stub crew recruitment FSMs** (Bren-Vor, Yelena, Mira-Rou, Tarven) are still 1-state stubs per `dialog_coverage.py`. Already filed in path-to-finish + the crew-recruitment-quests doc.

4. **5+ species quests still missing FSMs**: Karavem, Kovellim, Selvenne, Stelloth, Thinn edge-align, Forward variant. Filed in path-to-finish.

### Remaining unblocked work to reach a real "Great ending" walk

Updated estimate after the design-chat ship:

| Block | Status | Remaining work |
|---|---|---|
| A — Endings runtime | ✅ DONE this session | Mark ✅ PROCESSED in design-chat handoff; testing chat to extend `walk_perfect_run` to chain Final Conflict → EndingScene render |
| B — Crew completeness | ☐ Open | 4 stub FSMs + 5 crew side-quests + 5 post-Fall Common Room reactions + Forward variant |
| C — Species quest completeness | ☐ Open | 5 missing FSMs + 1 Thinn quest variant + verify the 4 renamed-but-existing |
| D — Capstone runtime | ⏳ Partial | The Final Conflict trigger consumes `migration_corridor_open` + `rainbow_seeded` indirectly (via Fall + Rainbow Resonator); Hijack quest still missing; `met_arilou_sage` naming drift still unresolved |
| E — UX bug | ☐ NEW Open | The cancel-quit issue (filed today) blocks any walk that needs to fly through Hyperspace and survive cancels |

### Walk catalog status

- **Total walks**: 65 (+1 — added `walk_integration_great_run` this session)
- **Parallel sweep**: 64 in registry / 555 assertions (+85 since morning); 12 parallel-flake failures across 2 walks (`walk_cargo_full_auto_swap`, `walk_quasispace_interactive`) — both pass 100% sequentially, same pygame-init race already filed
- **Strict-mode integration walks**: 2/4 shipped (`walk_integration_undock_and_return` + `walk_integration_great_run`)

### Recommended pickup when Aaron wakes

1. Tell the design chat: "Mark the endings-evaluation dispatch ✅ PROCESSED; top open is now the cancel-quits-from-Hyperspace UX bug — that's the single biggest unblocker for the integration walks. Pick that up next."
2. Tell the testing chat: "Extend `walk_integration_great_run` to drive Final Conflict via `s.invoke('scz.content.final_conflict.fire_if_ready')` (or whatever the wiring is) and chain to EndingScene assertion."
3. The path-to-finish entry in `HANDOFF_design_chat.md` is still the canonical "what's left to build" overview. Update its block-A status (now ✅) but keep B/C/D/E open.

---

## Findings 2026-05-18 — Integration-walks tier introduced

### What shipped

1. **Strict mode in `TestScript`**. New keyword `strict=True` raises `ValueError` on shortcut verbs: `set_flag`, `set_cargo`, `set_credits`, `set_module_inventory`, `set_player_pos`, and `press("open_switcher")`. Verified by sanity test — strict raises on all 6, non-strict preserves backward compatibility (existing 57 walks unaffected). The newer shortcuts (`set_schematics`, `set_fleet`, `set_player_heading`, `simulate_lander_pickup`) aren't gated yet — add them when an integration walk would need them.
2. **`walk_integration_undock_and_return`** — first integration walk, passes 8/8 in ~21s. Uses `TestScript(strict=True)`. Traversal chain proved real:
   - `MainMenuScene → StationScene` (real menu confirm)
   - `StationScene → SystemScene` (real menu nav to Undock + confirm)
   - SystemScene inward thrust + sweep + confirm (no planet captured this run; the orbit-capture logic was exercised but didn't fire because home-planet orbital angles are time-dependent)
   - `SystemScene → HyperspaceScene` (real cancel-exits-to-hyperspace, NOT a parent-back transition — proves the directional semantics)
   - `HyperspaceScene → SystemScene` (real autopilot + auto-enter-radius)
3. **Audit finding on `walk_tutorial_arc`**: docstring says "no flag-seeding" and that's true for `set_*` verbs, but it uses `press("open_switcher")` **5 times** to skip travel (Beat 2→3, Beat 5→install path, Beat 4→hyperspace, Beat 7→Station, etc.). Comments explicitly acknowledge each as a deliberate skip. Not blocking, but means walk_tutorial_arc is a fast-regression walk, not an integration walk. A future `walk_integration_tutorial_arc` should re-do those legs via real Station→Undock→SystemScene→fly→Hyperspace→fly→SystemScene→Orbit→Dock chains.

### Coverage gaps (integration tier — deferred this session)

Each was scoped but deferred because the home-system navigation math is non-trivial and the original 3 walks each need 100-200 actions of careful nav setup. Targets:

| Walk | What it would prove | Blockers / approach |
|---|---|---|
| `walk_integration_species_tour` | Fly from Mh-Lai → Beta Corvi → hail Slylandro → fly home. Tests `HyperspaceScene` autopilot accuracy across cluster distances + species encounter wiring. | Need a deterministic "hail the species" path that doesn't depend on switcher. Slylandro Sky-Vault Orbit's Y-action calls `_hail_slylandro` per `system/orbit.py:172` — that's the canonical hook. Walk must reach Beta Corvi via real hyperspace autopilot. |
| `walk_integration_economy_loop` | Undock → fly to a planet → lander → collect deposits → lift → return → dock → trade-sell → upgrade-buy. Tests the mining-trade loop with REAL travel + REAL cargo (no `set_cargo` shortcut). | Home-system planets orbit, so deterministically reaching Furlmart (or any specific planet) via thrust is unreliable. Either accept "land on whatever planet is nearest" or implement a `expect_planet_in_range` harness primitive. |
| `walk_integration_quasispace_real` | Walk to Arilou Sage via real navigation → earn portal via dialog (no `set_flag("has_quasispace_portal", True)`) → Y in hyperspace → cross QS → exit at different anchor. Tests portal-acquisition + QS auto-eject without flag shortcuts. | Massive. Need to drive from MainMenu through ~30-min of real gameplay (find Arilou system, navigate to Sanctuary, hail Sage, walk dialog, leave, then portal use). Probably 200+ actions and 5-10 minutes wall-clock at 3x speed. |
| `walk_integration_full_perfect_run` | The capstone — full game from MainMenu to Best ending via real input only. | Blocked on `the_endings_evaluation` + `the_final_conflict` runtime (separate dispatch top of `HANDOFF_design_chat.md`). |

### Recommended next-session move

Pick up `walk_integration_economy_loop` first — it's the smallest of the three (~80-120 actions) and has no upstream dependency on dialog walks. Once it's green, the pattern for the species_tour and quasispace_real variants is established and they're mechanical follow-ons.

---

## Findings 2026-05-18 — Cargo auto-swap shipped + framework health

### Verification of design-chat dispatch ✅ PROCESSED 2026-05-17 (auto-discard feature)

`walk_cargo_full_auto_swap` (renamed from `walk_cargo_full_pickup_refused`) **passes 18/18** when run sequentially. Walk drives all 6 acceptance criteria from the original dispatch:
- Auto-swap fires when hold is full and incoming value > lowest held
- `cargo[COMMON]` decrements, higher-value type rises
- No swap when no lower-value type exists
- Preserves mid-value cargo (USEFUL untouched when discarding COMMON)
- Partial-fit swap works (the recommended extension was implemented)
- Quest items unaffected (stasis-bay path)

Design chat also added 3 harness primitives that the walk uses: `simulate_lander_pickup`, `expect_cargo_lt`, `expect_cargo_total_le`, `expect_cargo_higher_value_nonzero`. Clean implementation; matches spec.

### Framework health snapshot (2026-05-18 morning sweep)

- `tools/module_stat_audit.py`: **57 modules / 0 issues** (was 28 at framework rollout — design chat shipped 29 new modules).
- `tools/dialog_coverage.py`: **20 factories / 0 failed / 3 with benign flag-gated orphans** (was 14 — 6 new species character factories: burvixese_foreman, chenjesu_collective, lemmkin_brisk_ever_onward, mmrnmhrm_sentinel, taalo_we_who_watch, utwig_veiled_in_three_days).
- `tools/check_stubs.py`: **106 markers / 164 files** (was 96 / 144). Image markers up to 45 (was 37) — expected, since new species need portraits.
- `tools/run_walks_parallel.py`: **56 walks / 555 assertions / 5 failed in 57.4s** wall-clock.

### Parallel-runner pygame-init race — now affects 3 walks

The bug filed 2026-05-17 (`HANDOFF_design_chat.md` — `run_walks_parallel.py` flakes on PlanetSurfaceScene walks) still ☐ Open. Today's sweep shows the bug also flakes:
- `walk_lander_collect_all` (sometimes; passed this run)
- `walk_lander_liftoff_immediate` (consistent flake)
- **`walk_quasispace_interactive`** (new this batch — also pygame-display-heavy on entry)

All three pass 100% when run sequentially with `python -m scz --windowed --test <name>`. Same `Warning: no fast renderer available` stderr signature. Recommended fix from the existing bug entry (serialize pygame init via a file lock, or `--workers 4` default) handles all three.

### Newly authored walks (2026-05-17 session, all green)

| Walk | Asserts | Verifies |
|---|---|---|
| `walk_loaded_ship_tour` | 15 | Buy all upgrades + fly out + autopilot home |
| `walk_cargo_full_auto_swap` (was `_pickup_refused`) | 18 | Auto-discard feature — 6 acceptance scenarios |
| `walk_customization_uninstall_module` | 8 | Install → uninstall round-trip; inventory restoration |
| `walk_customization_insufficient_credits` | 14 | Broke player can't buy; no state corruption |
| `walk_bio_archive_hidden_when_empty` | 6 | Visibility gate on Bio-Archive menu item |
| `walk_quasispace_round_trip` | 4 | Portal 0 → Portal 1 → hyperspace |
| `walk_orbit_dock_at_station` | 3 | Y-button dock from Mh-Lai orbit → StationScene |

**Total this batch**: 7 walks / 68 assertions added.

---

## Findings 2026-05-17 — Full gameplay sweep

### Automated regression — ✅ 27/27 green, 308/308 assertions

Queue job `2026-05-17T1730-full-sweep`, requester `design-chat`. Result JSON: `.claude/test-queue/done/2026-05-17T1730-full-sweep.json` · log: `.claude/test-queue/logs/2026-05-17T1730-full-sweep.log`.

The handoff expected 20 walks / 241 assertions; the worktree's registry now has **27 walks / 308 assertions** — net new since the doc was written. Every walk green, zero failures.

| walks | added since the 20-walk baseline |
|---|---|
| `walk_bio_archive` | Beat 5 station-hub close-out (this chat shipped) |
| `walk_recruit_mraka` | Mraka recruitment FSM |
| `walk_cleanser_cooperate`, `walk_cleanser_combat` | Cleanser climax branches |
| `walk_melnorme_recruitment` | Vulpeculae shelving test + commit |
| `walk_dnyarri_encounter` | Vesh Vasa-Lon survey |
| `walk_salvage_wreck`, `walk_visit_proto_species` | Echo-sensor / proto-visit registry |
| `walk_hyperspace_encounters`, `walk_hyperspace_teleport_into_zone`, `walk_hyperspace_retire_after_resolved` | Hyperspace parity probes |
| `walk_system_visit_dim_tier` | Visit-aware dim-tier verification |

### Manual visual / feel playtest — **not feasible from this chat** as currently configured

The testing chat runs walks via `SDL_VIDEODRIVER=dummy` + `SDL_AUDIODRIVER=dummy` (no window, no audio — by design, so parallel chats aren't disrupted). With rendering off, I literally cannot see the game; with audio off, I cannot hear cues. Even if I flipped to a real window:
- I have no eyes/ears/hands. Subjective "is this contrast strong enough" / "does this dialog land" answers must come from a human at the keyboard.
- A real window steals focus and plays audio — the exact disruption the test queue was built to prevent.

Three paths forward — pick one when you next want this kind of feedback:
1. **You do the playtest, I take the notes.** Open the game yourself, talk me through what you see; I aggregate into a Findings entry. Best fidelity, requires your time.
2. **Computer-use screenshot mode.** Authorize the testing chat to launch the game on a Windows virtual desktop (`Win+Ctrl+D` for a new desktop, hidden from your active one). I run scripted walks with rendering enabled, capture screenshots, and report visual observations. No audio. Subjective feel still needs you.
3. **Static playtest checklist.** I generate a step-by-step manual playtest doc per feature (anchored to scene/file refs) and you run through it yourself, noting issues. Cheapest, slowest end-to-end.

### Code-level observations on the touched files (read-only review, not a playtest substitute)

**`src/scz/content/system_scan.py` — visit-aware dim tier**
- ✅ Architecture is clean: pure functions, per-star cache, capability-gated reveals.
- ✅ `system_dim_tier` matches the spec exactly (0/1/2 based on visited + extracted% + undiscovered-anomalies).
- ⚠️ `anomaly_is_discovered` returns `False` for unmapped kinds (e.g. `cache`, `artifact`). If a future anomaly kind ships without a matching flag handler, the system stays at tier 1 forever even when fully extracted. Benign for the slice (no such anomalies seeded), but worth a guard or a TODO so it doesn't silently regress later.
- 👀 `sys_key = f"{int(x)}_{int(y)}"` could collide if two stars round to the same integer pair. In a 10000-unit universe with integer-snapped star coords this should never happen, but a `f"{int(x):05d}_{int(y):05d}"` zero-pad would be a 2-character defense against accidental star-coord drift.

**Other touched files** (skim-read only — full review deferred until a playtest path is chosen):
- `src/scz/hyperspace/scene.py` (1405 lines) — too large to grep-walk in one Findings entry; spot-check it on the next playtest pass.
- `src/scz/hyperspace/starmap.py` (237 lines) + `src/scz/planet/scene.py` (1309 lines) — same.
- `tools/manual_playtest_lander.md` (202 lines) — exists; re-running its checklist requires the human-at-keyboard path above.

**Status (this Findings entry):** ✅ Automated regression done. Manual playtest blocked on path selection (Q1/Q2/Q3 above).

---

## 2026-05-17 — Bio-Archive scene walk-test (pending Design implementation)

**Source**: Beat 5 completion plan (closing the station-hub trilogy: Trade + Customization + Archive). Design-chat implements `src/scz/station/archive.py` `BioArchiveScene` + `src/scz/content/archive_entries.py` catalog (20 entries across 4 categories).

**Walk-test target** — `walk_bio_archive`:
- Set flags to grant Distress Beacon + one species sighting
- Enter StationScene → expect Bio-Archive menu item visible (hidden until any archive flag is True)
- Select Bio-Archive → expect `BioArchiveScene`
- Cycle categories → expect entry list updates
- Select entry → expect detail pane renders long_desc
- For an entry with `cinematic_id is not None` (Distress Beacon) → expect cinematic replay logs trigger
- B → expect StationScene returned

**Status**: ☐ Open — blocked on Design implementation. Testing chat should pick this up *after* Design lands the Bio-Archive scene.

---

## 2026-05-17 — Crew recruitment quest walks (pending Design FSM implementation)

**Source**: `references/lore/crew-recruitment-quests.md` (5 recruitment side-quests, one per crew NPC). Design-chat implements 5 character factories in `src/scz/dialog/characters.py` + FSM terminal-state side-effects that set `recruited_<role>` flags + filter that hides quest-locked modules from `purchasable_modules()`.

**Walk-test targets** — one per recruitable crew:
- `walk_recruit_pilot` — Mraka Yenn-Sa; trigger at Mh-Lai post-Furlmart; optional Drifter's Circuit minigame skip; verify `recruited_pilot = True` + `crew_pilot` appears in uninstalled modules
- `walk_recruit_weapons_officer` — Bren-Vor Telcas; trigger post-Distress-Beacon screening; verify `recruited_weapons_officer = True`
- `walk_recruit_engineer` — Yelena Lwen-Tar; trigger post-any-install at Customization bay; verify `recruited_engineer = True`
- `walk_recruit_medic` — Mira-Rou Halve-Tel; full path requires Coel Tessar Beacon quest clean-completion; verify `recruited_medic = True` + Mantle-Resonance calibration bonus check
- `walk_recruit_navigator` — Tarven Olwen-Sa; trigger post-3-systems-visited at Council Archives; verify `recruited_navigator = True`

Each walk should also verify the **decline** path (flag remains False; module stays locked).

**Status**: ☐ Open — blocked on Design FSM implementation.

---

## 2026-05-17 — Schematic Vault + Mh-Lai install gate walks (pending Design implementation)

**Source**: `references/lore/economy-and-trade-loops.md` (new vendor-niche canon: Mh-Lai install rule + schematic loop). Design-chat scaffolds `src/scz/station/schematic_vault.py`, `src/scz/content/schematics.py`, `Game.schematics: set[str]`, `Module.unlock_schematic: str | None`, and the install-location gate in `ShipCustomizationScene.install_module`.

**Walk-test targets**:
- `walk_schematic_vault` — visit Mh-Lai, set `game.schematics = {"schematic_pulse_cannon"}`, enter Schematic Vault, select schematic, confirm, verify schematic consumed + `pulse_cannon_mod` now appears in `purchasable_modules()`
- `walk_install_gate_remote` — try to install a tier-1+ module while NOT docked at Mh-Lai → expect rejection
- `walk_install_gate_home` — same module, at Mh-Lai → expect success
- `walk_tier_0_exempt` — install a tier-0 quest-reward module remotely → expect success (exemption to install gate)

**Status**: ☐ Open — blocked on Design implementation.

---

## 2026-05-17 — Kovellim + Karavem walk-tests (2 new Precursor-faction quests)

**Source**: 2 new quests in `tools/quest_inventory.csv` (`kovellim_crossing_trade`, `karavem_song_exchange`). Blocked on Design implementation.

**Walk-test targets**:

- `walk_kovellim_full_trade` — visit Eight-Knot Station → offer fresh galaxy-data → accept all three artifacts → verify `KOVELLIM_FOLDER_COMPASS` + `KOVELLIM_CROSSING_BRACE` + `KOVELLIM_CYCLE_MEMORY` added to `game.uninstalled_modules`; Kovellim standing +3
- `walk_kovellim_listen_only` — visit → request stories → verify Bio-Archive gains "Kovellim second crossing" and "Kovellim prior cycles" entries; no modules; Hider standing +2
- `walk_kovellim_cleanser_retract` — set `cleanser_kovellim_directive=True` → trigger Cleanser-pressure branch → Ovala's knot-scar speech triggers → choose back-down → verify `cleanser_kovellim_directive=False` + Persuader +2
- `walk_karavem_exchange` — visit Aeris-Sing → offer a Furling song → verify `KARAVEM_RESONANCE_MODULE` granted + Karavem standing +2
- `walk_karavem_masterwork` — visit → request commissioned masterwork → verify `KARAVEM_RESONANCE_MODULE_DELUXE` granted + Karavem standing +4

**Special walk requirements**:
- **Karavem dialog rendering** — the CSV's `npc_line` field contains bracketed musical annotations (*"[in C minor, mournful]"*). The walk-test harness needs to be tolerant of this rendering choice. If Design renders the music as audio cues, the walk should verify the audio fires; if Design renders as italic prose, the walk should verify the rendered string matches expectation.

**Status**: ☐ Open — blocked on Design implementation.

---

## 2026-05-17 — Stelloth + Selvenne + Mrokon walk-tests (3 new species quests)

**Source**: 3 new quests in `tools/quest_inventory.csv` (`stelloth_artifact_trade`, `selvenne_memory_archive`, `mrokon_hammer`). All blocked on Design implementation of character factories + ship classes + quest FSMs.

**Walk-test targets**:

- `walk_stelloth_honest_trade` — visit Three-Voice Arc trading post → encounter chord → trade artifact → verify Stelloth standing +2 + terminal Migrated flag set
- `walk_stelloth_withhold` — visit with a Taalo Shield-fragment in reserve cargo → attempt to withhold during trade → expect Witness-caught state surfaces → choose disgrace path → verify standing -3
- `walk_selvenne_contribute` — visit Vellumar via submarine → touch polyp → expect first-memory state plays (Slylandro prior-cycle) → contribute Steward's own memories → verify Echo Crystal artifact granted
- `walk_selvenne_eliminated` — Cleanser branch → attempt cleanse despite memory-playback warning → verify reef destroyed + worst-Cleanser-outcome standing collapse (Persuader -6, Hider -5)
- `walk_mrokon_hammer_full` — visit Mrokon's Stand → offer Furling resonance support → verify Hammer-Round fires at max effectiveness → verify `others_marked_permanently` flag set
- `walk_mrokon_partial_evac` — visit → offer migration to young Operators → verify mixed-migration + reduced-marking outcome
- `walk_mrokon_cleanse_combat` — visit → attempt Cleanser pre-emption → verify Mrokon combat encounter triggers + lose-outcome → verify worst-case Defender standing collapse

**Status**: ☐ Open — blocked on Design implementation.

**Special walk requirements**:
- **Stelloth withhold walk** needs the test harness to set a cargo flag (`has_taalo_shield_fragment=True`) before entering the trade dialog, so the Witness-caught branch is reachable.
- **Selvenne contribute walk** needs the memory-playback cinematic system to be implementable in test mode (either fully rendered or stub-with-log).
- **Mrokon Hammer walk** is purely dialog-FSM; the actual Hammer-firing cutscene fires only at slice climax (not during the quest visit) so the walk just verifies the *commitment-state* flags.

---

## 2026-05-17 — Allied species ship purchase walk (pending Design implementation)

**Source**: `references/lore/economy-and-trade-loops.md` "Allied Species Ships" section. Design-chat scaffolds a `SHIPS` registry (separate from `MODULES`) + Mh-Lai catalog UI + alliance-flag gating.

**Walk-test targets**:
- `walk_allied_ship_slylandro` — complete Slylandro Cloak quest → return to Mh-Lai → expect Slylandro Lift purchasable; buy → expect Steward's hull-loadout-selector shows two hulls (Furling Scout + Slylandro Lift)
- Similar walks for Arilou Skiff, Mmrnmhrm Sentinel, Androsynth Refugee Fighter (Burvixese + Thinn are conditional on quest-branch outcomes — defer until Design wires those branches)

**Status**: ☐ Open — blocked on Design implementation.

---

*(Future entries appended above this line.)*
