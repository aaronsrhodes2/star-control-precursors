# HANDOFF — anyone → SCZ: Game Design Chat

> Cross-chat dispatch queue for **code-modification work** in Star Control Zero. The Game Design chat is the *exclusive* code-mod owner (per project-rules.md Rule 5) — all other chats dispatch implementation work here.
>
> The Design chat reads this file at session start, picks up open entries, implements the changes in `src/`, and marks each `✅ PROCESSED <date>` (or removes it) when done. Newest entries at the top.
>
> **Design lane scope**: all `src/` code, `tools/*.py` (non-image-pipeline), scene wiring, FSMs, game systems, content catalogs (modules, schematics, archive entries, etc.), test infrastructure changes.
>
> **Lane discipline reminder**: Design chat does NOT author lore canon (read `references/lore/*.md` as source of truth — Lore chat writes it), image assets (Image chat), or audio (Audio chat). Design chat *implements* the canon the other chats author.

---

## 2026-05-19 — Deterministic navigation primitives for strict-mode integration walks

**Origin**: Testing chat, after the overnight `walk_integration_great_run` attempt. With the cancel-quit fix landed (✅ above) and Block A endings runtime shipped (✅ below), strict-mode integration walks can finally chain Station ↔ Hyperspace ↔ System without silent termination. **What's still missing is deterministic navigation** — walks currently rely on `set_player_pos` (forbidden in strict mode) or rough joystick-axis pushes (flaky, timing-sensitive) to actually *reach* a specific star or planet. To finish the "no shortcuts, no harness-only knobs" perfect run, we need in-game autopilot affordances.

**Why this matters now**: every remaining integration walk needs to navigate to specific places (Mh-Lai for the Fall, Coel Tessar for Beat 4, the Rainbow Worlds arrow-tip for Final Conflict). Without autopilot, every walk has to either A) cheat via `set_player_pos` (strict mode forbids), or B) push joystick axes hopeful-blindly for N seconds (timing-flaky, breaks on map changes).

### Gap 1 — Hyperspace autopilot to named star/system

`HyperspaceScene` has a navigation surface but no "autopilot to X" command. Player has to manually fly there.

**Proposed surface** (minimal — pure in-game UI, no harness-only knobs):

```python
# in scz/hyperspace/scene.py
def autopilot_to_star(self, star_id: str) -> bool:
    """Engage autopilot toward the named star. Returns True if engaged,
    False if star doesn't exist or already there."""

def cancel_autopilot(self) -> None: ...
```

UI surface options (Design's call):
- **Option A**: Cursor on starmap → A button → autopilot engages. Simplest; matches existing starmap cursor.
- **Option B**: Starmap search-by-name menu → list of known stars → A engages. Matches "I've heard of Mh-Lai" pattern.

In either case, the walks would drive via the actual UI, not a hidden harness call. Both are real-input paths.

**Suggested**: Option A (cursor + A). Already-implemented cursor; one new button binding; minimal new UI. Cancel via cancel/B (now safe with PauseMenuScene overlay).

### Gap 2 — System view planet-targeted autopilot

When you enter a system (`SystemScene`), reaching a specific planet (Mh-Lai, the homeworld, etc.) requires manual flight. For walks driving the Tutorial Beat 1 dock, this currently relies on `set_player_pos` or hopeful axis pushes.

**Proposed surface**:

```python
# in scz/system/scene.py
def autopilot_to_planet(self, planet_index: int) -> bool:
    """Engage in-system autopilot to the indexed planet."""
```

UI surface: cursor or hover-select on a planet → A engages autopilot → ship orbits → standard dock prompt fires on arrival. Same pattern as hyperspace Option A.

### Gap 3 — Star-discovery flag for "known" stars

Once Gaps 1 + 2 land, integration walks need to know which stars are reachable by name. Mh-Lai is always discoverable (Furling home), but the Rainbow Worlds arrow-tip should become discoverable only after the player has been told about it.

Suggested flag: `game.flags["known_stars"]: set[str]`. Set by Beat-1 onboarding to `{"MH_LAI"}`; appended-to by dialog events ("the rainbow worlds form an arrow… here, plotted on your starmap" → adds the 10 rainbow-cluster star ids).

The starmap-search UI (Gap 1 Option B) would filter to this set. The starmap-cursor UI (Option A) doesn't strictly require this but using `known_stars` to mark them with a halo would help.

### Acceptance criteria (testing chat will verify)

After these land:
1. `walk_integration_mhlai_dock` (NEW) — from MainMenu → New Campaign → spawn in hyperspace → autopilot to Mh-Lai → enter system → autopilot to Mh-Lai planet → dock prompt → Station. Zero `set_player_pos`. Zero hopeful axis pushes. Pure UI input.
2. `walk_integration_great_run` revised — replace its current Phase 1-3 (which rely on `set_player_pos` to reach Furlmart) with autopilot-driven navigation.
3. `walk_integration_full_perfect_run` (the eventual no-shortcuts MainMenu → Best walk) becomes possible.

### Cross-references

- `src/scz/testing/harness.py` — strict mode is in place; forbidden verbs documented
- `src/scz/testing/scripts.py:walk_integration_undock_and_return` — the foundation walk (non-strict today, would become strict-promotable after Gap 1 + 2)
- `references/lore/HANDOFF_testing_chat.md` Findings 2026-05-18 — Integration-walks tier (the rationale for strict mode)

### Priority

**MEDIUM** — Block A is done, so endings can be reached via the existing scripted walks. This dispatch is what unlocks **strict-mode** integration walks, which is the bar Aaron set for proving the game is truly traversable end-to-end without harness-only knobs.

**Status**: ☐ Open

---

## 2026-05-18 — UX bug: `cancel` / B in `HyperspaceScene` and `StationScene` quits the game

**Origin**: Testing chat, discovered while authoring `walk_integration_great_run` for Aaron's "play through to the Great ending using only the harness" overnight task.

**Symptom**: pressing `B` / `cancel` in `HyperspaceScene` or `StationScene` calls `self.game.quit()` and exits the game.

**Code refs**:
- `src/scz/hyperspace/scene.py:349-351`:
  ```python
  # Esc/cancel at top-level scene → quit game (no parent to back to)
  if inp.cancel and self.game is not None:
      self.game.quit()
      return
  ```
- `src/scz/station/scene.py:120-123`:
  ```python
  # B → quit (Station is the top-level scene; backing out exits)
  if inp.cancel and self.game is not None:
      self.game.quit()
      return
  ```

**Why this is a bug**:
1. **User-hostile**: a player tapping B in the middle of hyperspace navigation expects to *back out of a menu*, not quit the game with no confirmation. The same applies to Station — players returning from a Trade screen via repeated B-press can over-press one frame and lose the session.
2. **Save-system implication**: now that `CampaignManager` auto-saves every 60s, the quit *probably* preserves most progress — but a rapid quit can still lose up to ~60s of play. There's no "save before quitting" prompt.
3. **Test-harness hostility**: any integration walk that accidentally double-cancels through scenes (e.g. Station→cancel→back to MainMenu? no — quits) is silently terminated. The walk's `s.end()` never fires; no `Test complete:` summary; output cuts off mid-trace. Discovered the issue by re-running with `2> stderr.log` separation — exit code 0, no error.

**Recommendation**:

For `StationScene.cancel` (top-level dock):
- Replace `self.game.quit()` with a confirmation prompt scene, or with **save+return-to-MainMenu** behavior. Save-system makes "return to title" the natural meaning of "back" from the top dock.

For `HyperspaceScene.cancel`:
- Best: open a small in-game menu (Pause / Save / Load / Quit-to-Title / Resume).
- Acceptable interim: `cancel` becomes a no-op + brief HUD hint "Press Start (or menu key) to pause." Aaron is in control of Start binding.
- Worst-case interim: keep the quit but add a confirmation overlay ("Quit to Title? Y/N").

**Acceptance criteria for the testing chat**:
- After this lands, `walk_integration_great_run` can navigate through Phase 3 → Phase 4 → Phase 5+ without the walk silently terminating on a stray cancel.
- A new walk `walk_pause_menu_cancel` verifies the new behavior — pressing cancel in Hyperspace/Station opens the pause menu OR is a no-op, NOT a quit.

**Status**: ✅ PROCESSED 2026-05-19 — shipped:

- **`src/scz/scenes/pause_menu.py`** (NEW) — `PauseMenuScene` opens as a modal overlay over whatever top-level scene is active. Four options: **Resume** (close overlay), **Save Now** (campaign snapshot + close), **Return to Title** (auto-save then transition to MainMenu), **Quit Game** (auto-save then `game.quit()`). Dim-translucent backdrop preserves visibility of the underlying scene; centered panel with cursor-driven menu. Cancel/B in the pause menu = Resume.
- **`src/scz/hyperspace/scene.py`** + **`src/scz/station/scene.py`** — cancel handlers now call `game.open_overlay(PauseMenuScene())` instead of `game.quit()`. Guarded by `overlay_scene is None` so cancel while another overlay (e.g. switcher) is up doesn't stack.
- **`src/scz/testing/harness.py`** — NEW `expect_overlay(scene_class_name | None)` action verb. Passes `None` to assert no overlay is up.
- **`src/scz/testing/scripts.py`** — NEW `walk_pause_menu_cancel` (14/14 ✓) covers all four cases: Station-cancel opens, in-overlay cancel resumes, Return-to-Title navigates to MainMenu, Hyperspace-cancel opens. Testing chat can now write integration walks that traverse Station + Hyperspace without risking silent termination.

Auto-save guard: every "exit-the-session" path (Return to Title, Quit Game) takes a snapshot first when a campaign is active, so the player can't lose progress by clicking through the menu fast. No-op if no campaign.

**Status**: ✅ PROCESSED 2026-05-19

---

## 2026-05-18 — HIGH PRIORITY: Path-to-finish dispatch — 23 missing runtime pieces blocking the perfect-run

**Origin**: Testing chat, after Aaron's "use the full walk test to find the missing parts" gap-analysis pass. Cross-references the 2026-05-18 endings-evaluation dispatch below and consolidates everything blocking a real `walk_integration_full_perfect_run`.

### How this was derived

Walk `walk_perfect_run` (33/33 green, flag-state simulation) sets 69 flags per the canonical Best-ending criteria in `references/lore/the-endings.md` and the `q_endings_best.side_effects` row of `tools/quest_inventory.csv`. Cross-referenced each flag and each quest_id against `src/scz/` (non-testing) via `grep -rln`. Findings below split into 4 gap categories — each is a thing the testing chat **cannot drive** because there's no runtime to drive.

### Gap 1 — Flags set by perfect-run that nothing in `src/` reads (11 of 69)

These flags exist in the spec but no scene / FSM / module / scene-eval reads them. Whoever sets them upstream might be dead code; downstream consumers don't exist yet.

| Flag | Consumer that's missing |
|---|---|
| `brenvor_postfall_resolved`, `mira_postfall_resolved`, `mraka_postfall_resolved`, `tarven_postfall_resolved`, `yelena_postfall_resolved` | Post-Fall Common Room reaction quests (see Gap 2 — `post_fall_crew_*` 5 quests). Whoever sets these expects the Common Room scene to read them and unlock crew bond states. |
| `drev_tok_alive` | The Final Conflict's diplomatic-resolution branch. Already in the existing 2026-05-18 dispatch below; mentioned here for completeness. |
| `migration_corridor_open` | The Migration corridor / Crossing cinematic gate. No scene yet renders the corridor opening or reads this flag as a precondition for the ending sequence. |
| `migration_accelerated` | Migration-timetable acceleration logic. Either a quest reward applies it (Karavem song?) or a Cleanser-faction action does. No code path yet. |
| `rainbow_seeded` | Cluster's Rainbow World seeding ritual. Flag exists but no scene / encounter sets or reads it. The `RAINBOW_RESONATOR` module exists in `modules.py` but there's no "seed the Rainbow World" interaction. |
| `slylandro_cloak_install_offered` | Intermediate Slylandro Cloak progression flag. The `walk_slylandro_cloak` walk drives the quest to `slylandro_cloaked` directly; this intermediate state seems unused. Either remove from the CSV or wire the multi-state cloak install. |
| `met_arilou_sage` | Likely a flag-naming inconsistency — `walk_arilou_sage`'s side-effect actually sets `talked_to_arilou_sage` (per `engine/game.py:63` comment). `met_arilou_sage` may be a documentation drift; pick one canonical name and prune. |

### Gap 2 — Quest_ids in `tools/quest_inventory.csv` with NO `src/scz/` runtime references (24 of 39)

Conservative grep (literal quest_id only — some are likely implemented under different naming, like `taalo_shield` → `taalo_we_who_watch()` factory). The list is annotated with whether a likely-renamed factory exists.

**Genuinely missing (no factory found under any plausible name):**
- `the_endings_evaluation` — confirmed missing (separate dispatch below)
- `the_final_conflict` — confirmed missing (separate dispatch below)
- `hijack_others_vessel` — no scene; needed for Best (`flag:hijack_council_sanctioned` is a Best criterion)
- `post_fall_crew_engineer`, `post_fall_crew_medic`, `post_fall_crew_navigator`, `post_fall_crew_pilot`, `post_fall_crew_weapons` — 5 Common Room reaction mini-quests (already on the 2026-05-17 "Halia banter + Post-Fall Common Room reactions" entry below — those are the 5)
- `crew_engineer_side_quest`, `crew_medic_side_quest`, `crew_navigator_side_quest`, `crew_pilot_side_quest`, `crew_weapons_officer_side_quest` — 5 crew side-quests
- `crew_weapons_officer_thinn`, `crew_weapons_officer_thinn_side_quest` — Forward (Thinn-defector) weapons officer variant + side-quest
- `thinn_edge_align` — Thinn species' Edge-Align quest (the Thinn-cloaked outcome path)
- `selvenne_memory_archive`, `karavem_song_exchange`, `kovellim_crossing_trade`, `stelloth_artifact_trade` — 4 species quests with no factory I could find

**Likely implemented but under transformed names** (Design to verify):
- `androsynth_beacon` → `coel_tessar()` factory (Beat 4 — exists)
- `burv_caster` → `burvixese_foreman()` factory (exists)
- `chenjesu_resonance` → `chenjesu_collective()` factory (exists)
- `taalo_shield` → `taalo_we_who_watch()` factory (exists)

So **the genuine count is ~20 unimplemented quests**.

### Gap 3 — Stub character factories (1-state FSMs)

`tools/dialog_coverage.py` confirms 4 character factories are still 1-state stubs (1/1 reachable, no real branches):

- `bren_vor_telcas` (Aimer / Weapons Officer)
- `mira_rou_halve_tel` (Bio-Architect / Medic)
- `tarven_olwen_sa` (Star-Reader / Navigator)
- `yelena_lwen_tar` (Mender / Engineer)

These are the 4 crew recruits — together with the existing `mraka_yenn_sa` (which IS implemented, 7-state FSM), this is the recruitment infrastructure for Best's 5/5-crew criterion. **Without these, the perfect-run can't drive recruitment through actual dialog** — only via the `set_flag("recruited_*", True)` shortcut that strict mode now forbids.

### Gap 4 — Categorized TODO markers (informational; lane-owned)

`tools/check_stubs.py` reports 108 markers total — informational, mostly content-authoring (Image=45, Lore=37). Not blocking but worth tracking:

- **18 uncategorized** TODO markers — design or testing chat to triage
- **45 Image** TODO_AVATAR markers — image chat's natural backlog; not blocking gameplay
- **37 Lore** TODO_LORE markers — lore chat's backlog
- **3 Audio**, **2 Design**, **1 Testing** — minor

### Prioritized path to finish (recommended sequencing)

Each block can ship independently. Rough effort estimates assume the testing chat will write/update walks in parallel.

**Block A — Endings runtime** ✅ SHIPPED 2026-05-18
- `src/scz/content/endings.py` — evaluate_ending + apply_ending + resolve_ending
- `src/scz/scenes/ending.py` — EndingScene renders all 6 tiers
- `src/scz/scenes/final_conflict.py` — already shipped; win path now drives resolve_ending + EndingScene
- `walk_perfect_run` re-authored to drive the runtime evaluator (slice_ending=BEST returned from `resolve_ending`); NEW `walk_ending_tiers` (24/24) verifies all 6 tiers
- Note: the contract's `the_final_conflict.py with diplomatic + symbolic + super_melee_engage branches` is canon-deprecated by the 2026-05-18 canon revision (`the-final-conflict.md` §Canon revision 2026-05-18) — negotiation always fails, combat is forced. The existing scene is canonically correct.
- Remaining Gap-1 connectors (`migration_corridor_open`, `rainbow_seeded`, `drev_tok_alive`): authored as Block D below.

**Block B — Crew completeness** (~2-3 days)
- 4 stub recruitment FSMs (Bren-Vor, Mira-Rou, Tarven, Yelena) — pick up from `crew-recruitment-quests.md`
- 5 crew side-quests (`crew_*_side_quest`)
- 5 post-Fall Common Room reactions (already partially in the 2026-05-17 "Halia banter + Post-Fall" entry)
- Forward (Thinn-defector) variant: `crew_weapons_officer_thinn` + side-quest

**Block C — Species quest completeness** (~2-3 days)
- 4 missing species quests: `selvenne_memory_archive`, `karavem_song_exchange`, `kovellim_crossing_trade`, `stelloth_artifact_trade`
- 1 Thinn quest variant: `thinn_edge_align`
- Verify the 4 "likely under renamed factory" quests actually map to their existing factories (mark them ✅ if so)

**Block D — Capstone runtime** (~1 day)
- Migration corridor scene + `migration_corridor_open` consumer
- Rainbow World seeding ritual + `rainbow_seeded` consumer
- Hijack quest (`hijack_others_vessel`) — short FSM since it leads into the endings evaluator
- `migration_accelerated` apply-effect logic (probably a Karavem-quest side-effect)
- Clean up the `met_arilou_sage` / `talked_to_arilou_sage` naming drift

**Total estimated path: 6-7 focused days of design-chat work** before the testing chat can drive a true `walk_integration_full_perfect_run` from MainMenu to Best ending in strict mode.

### Testing chat's commitment

Once each block ships:
- Block A → re-author `walk_perfect_run` to use the real `evaluate_ending` runtime; ship `walk_final_conflict_diplomatic`
- Block B → drive recruitment via actual dialog walks (drop `set_flag("recruited_*")` shortcuts)
- Block C → walks per quest with terminal-state verification
- Block D → ship `walk_integration_full_perfect_run` — the no-shortcut, real-input, MainMenu-to-Best-ending walk Aaron asked for

The strict-mode infrastructure (`TestScript(strict=True)` + `walk_integration_undock_and_return` foundation) is already in place to support all the integration walks.

### Cross-references

- `tools/quest_inventory.csv` — authoritative quest list
- `references/lore/the-endings.md` — Best/Great/Good/AT_COST/UNSUCCESSFUL/DISASTROUS thresholds
- `references/lore/the-final-conflict.md` — Drev-Tok FSM design
- `references/lore/crew-recruitment-quests.md` — 5 crew recruit specs
- `references/lore/HANDOFF_testing_chat.md` `## Findings 2026-05-18 — Integration-walks tier` — strict-mode rationale + 3 deferred integration walks
- `src/scz/testing/scripts.py:walk_perfect_run` — the 69-flag canonical Best state
- This dispatch's parent: the next entry below (2026-05-18 endings-evaluation HIGH PRIORITY)

**Status**: ☐ Open — this is the consolidated "path to finish" overview. Individual sub-blocks may ship via the existing per-block dispatches in this doc.

---

## 2026-05-18 — HIGH PRIORITY: Implement `the_endings_evaluation` runtime + `the_final_conflict` scene

**Origin**: Testing chat, after Aaron's end-of-night request to "test successfully playing the entire game by finishing every quest, the mid and final conflict, complete with a perfect ending, using only the test harness."

**Today's gap**: I cannot drive a real Best-ending walkthrough because the runtime does not exist:

- `tools/quest_inventory.csv` defines `the_endings_evaluation` with 6 outcome states (`q_endings_best`, `q_endings_great`, `q_endings_good`, `q_endings_at_cost`, `q_endings_unsuccessful`, `q_endings_disastrous`) and the `side_effects` column declares what flags each sets (`flag:slice_ending=BEST;flag:sc2_era_canonical=True` etc.). But:
  - `grep -rl 'FinalConflict\|the_endings_evaluation\|ending_tier' src/` returns **empty**.
  - No `EndingScene`, no `eval_ending(game)` function, no scene-class that fires `q_final_drev_tok_diplomatic_*`.
  - The 4 stub crew recruitment FSMs (Bren-Vor, Yelena, Mira-Rou, Tarven) are still 1-state stubs per `tools/dialog_coverage.py` (matching their previous status).

The new walk `walk_perfect_run` I just shipped is a **flag-state simulation** (33/33 green in 2.5s) — it sets every flag the CSV's Best branches name, tours `StationScene` + `BioArchiveScene` to prove they open under late-game state, and asserts the flag set matches the spec. **It does not drive an actual end-game cinematic because there is none to drive.**

### Implementation contract

**1. `src/scz/content/endings.py`** — new module. Public surface:

```python
def evaluate_ending(game) -> str:
    """Return one of BEST / GREAT / GOOD / AT_COST / UNSUCCESSFUL / DISASTROUS.

    Per `references/lore/the-endings.md`:
      - Best:        16/16 species saved AND 5/5 crew AND >=95% side-quests
      - Great:       16/16 species saved AND 5/5 crew AND >=85% side-quests
      - Good:        16/16 species saved AND 1-4 crew
      - AT_COST:     8-15 species saved AND 1-4 crew
      - UNSUCCESSFUL: 1-7 species saved OR 0-1 crew
      - DISASTROUS:  0 species saved AND 0 crew
    """
    ...

def apply_ending(game, tier: str) -> None:
    """Set the canonical flags per CSV q_endings_<tier>.side_effects."""
    ...
```

The species-saved count reads from per-species terminal-status flags (`slylandro_cloaked`, `chen_pre_sentient`, etc. — full list in `tools/quest_inventory.csv` Best-aligned branches; I extracted it for the walk_perfect_run flag-setter — copy that as the canonical "favorable" set).

**2. `src/scz/scenes/the_final_conflict.py`** — new scene. Per `references/lore/the-final-conflict.md` + `tools/quest_inventory.csv` `the_final_conflict` 14 rows:
- State machine with branches: `diplomatic_rare`, `diplomatic_symbolic`, `symbolic_resolution`, `rejection`, `super_melee_engage` (the combat fallback)
- Triggered by reaching `migration_corridor_open=True` + `rainbow_seeded=True` per the CSV's prereqs
- On terminal state, calls `evaluate_ending(game)` and routes to an `EndingScene`

**3. `src/scz/scenes/ending.py`** — new scene. Per `references/lore/the-endings.md`:
- Reads `game.flags["slice_ending"]` (set by `evaluate_ending`)
- Renders the canonical narration line + cinematic backdrop per tier (Image chat owns the backdrop assets; this scene just blits)
- Optionally returns to MainMenu after a fixed display time

**4. Stub crew recruitment FSMs** — author full FSMs for the 4 stub recruits (Bren-Vor, Yelena, Mira-Rou, Tarven) per `references/lore/crew-recruitment-quests.md`. Already filed elsewhere in this doc; included here as a hard dependency for any meaningful end-to-end perfect run.

### Acceptance criteria (testing chat will verify)

When this lands, `walk_perfect_run` is updated to:
1. Drive the recruitment FSMs as real dialog walks (replacing the `s.set_flag("recruited_*", True)` shortcuts)
2. Trigger the final conflict via the in-game path (player at corridor + rainbow → FinalConflictScene)
3. Walk the diplomatic resolution branch
4. Assert `evaluate_ending(game) == "BEST"` returns from the runtime
5. Assert the EndingScene loads with the Best-tier cinematic

The walk's flag-state asserts stay as a regression safety net but the gameplay phase replaces the flag-set shortcuts.

### Why HIGH priority

Without these three modules + the 4 recruitment FSMs, the slice's defining promised payoff — "playing through to the Best ending" — is impossible to verify with the test harness. Every other feature that landed (cargo auto-discard, dim tiers, crew side-quests, species quests, the Fall of Mh-Lai) is downstream of the player reaching this end-state, so any regression-test campaign caps out short of the slice's intended terminus.

**Status**: ✅ PROCESSED 2026-05-18 — Phase 1, 2, and the practical Phase 3 (FinalConflictScene win-path wiring) shipped:

- **`src/scz/content/endings.py`** — `evaluate_ending(game) -> tier`, `apply_ending(game, tier)`, `resolve_ending(game) -> tier`. Canonical flag pools `SPECIES_FAVORABLE_FLAGS` (19), `CREW_RECRUITED_FLAGS` (5), `SIDE_QUEST_FLAGS` (7 — `diplomatic_resolution` dropped per 2026-05-18 canon). Tier logic per the-endings.md priority order.
- **`src/scz/scenes/ending.py`** — `EndingScene` with per-tier title, subtitle, canonical narration body, tonal palette, and dwell time. Reads `game.flags["slice_ending"]`; safe-default UNSUCCESSFUL if unset. Disastrous tier 10s silent dwell for the *"Good job"* punchline.
- **`src/scz/scenes/final_conflict.py`** — win path now calls `resolve_ending(game)` + transitions to `EndingScene`. `EndingPlaceholderScene` removed from stubs.py.
- **`src/scz/testing/scripts.py`** — `walk_perfect_run` (33/33) now drives the runtime evaluator (`s.invoke("scz.content.endings.resolve_ending")`); NEW `walk_ending_tiers` (24/24) exercises all 6 tiers.
- **`src/scz/testing/harness.py`** — NEW `invoke(dotted_path)` action verb for driving runtime evaluators from seeded state.

**Important canon-reconciliation note**: the contract's "Phase 2 — `the_final_conflict.py` with diplomatic + symbolic + super_melee_engage branches" is **deprecated by canon** — the 2026-05-18 canon revision in `references/lore/the-final-conflict.md` retired the diplomatic and symbolic branches ("negotiation always fails; combat is forced; loss = Time Drive restore"). The existing `FinalConflictScene` (shipped same-day earlier) IS the canonically-correct climax; no branched FSM rewrite needed. The CSV's older 14-row design is documentation drift, to be reconciled by the next Lore-chat sweep.

Phase 4 (4 stub recruitment FSMs) remains open as a Block-B follow-up per the path-to-finish overview above.

---

## 2026-05-17 — Feature: Auto-discard low-value cargo for high-value pickups when hold is full

**Origin**: Testing chat, after Aaron's "this is what we always wanted it to do" request. Filed alongside the new regression walk `walk_cargo_full_pickup_refused`, which locks in the current (refusal) behavior and will fail loudly once this feature ships — that failure is the signal to update the walk's asserts.

### Current behavior (verified by `walk_cargo_full_pickup_refused`)

`src/scz/planet/scene.py:_on_pickup` (line 512). When the lander tractors a deposit and the hold is full:

```python
ship_total = sum(self.game.cargo.values())
haul_total = sum(self.trip_haul.values())
cargo_max  = int(self.game.effective_stat("cargo_max", LANDER_CARGO_BASE))
remaining  = cargo_max - ship_total - haul_total
if remaining <= 0:
    d.collected = False
    self.recent_pickup = (d.type, 0)
    self.recent_pickup_label = "cargo full — upgrade hold at station"
    return
```

With a hold full of low-value COMMON (1c/unit), every ENERGY (12c) or BIO (6c) deposit on the surface is **refused** and stays put. The player has to lift off + sell + come back — or just leave the high-value loot behind.

### Desired behavior

When the hold is full **and the incoming deposit's per-unit value is greater than the lowest-value mineral in the player's cargo**, automatically discard enough of that lowest-value mineral to fit the new pickup.

### Proposed algorithm (drop-in for `_on_pickup`)

```python
# After computing `remaining`, replace the `if remaining <= 0` block:
if remaining <= 0:
    from scz.content.modules import MINERAL_PRICES
    incoming_price = MINERAL_PRICES.get(d.type, 0)

    # Find lowest-value held mineral whose per-unit value is strictly less
    # than the incoming. Search trip_haul + game.cargo combined.
    candidates = [
        (t, MINERAL_PRICES.get(t, 0),
         self.trip_haul.get(t, 0) + self.game.cargo.get(t, 0))
        for t in ("COMMON", "USEFUL", "BIO", "ENERGY")
        if t != d.type
        and MINERAL_PRICES.get(t, 0) < incoming_price
        and (self.trip_haul.get(t, 0) + self.game.cargo.get(t, 0)) > 0
    ]
    if not candidates:
        # Nothing lower-value to discard — fall back to refusal
        d.collected = False
        self.recent_pickup = (d.type, 0)
        self.recent_pickup_label = "cargo full — upgrade hold at station"
        self.recent_pickup_age = 0.0
        return

    candidates.sort(key=lambda c: c[1])     # cheapest first
    discard_type, _, available = candidates[0]
    to_discard = min(available, d.value)

    # Discard from trip_haul first (cheapest to "lose"), then game.cargo
    haul_discard = min(self.trip_haul.get(discard_type, 0), to_discard)
    self.trip_haul[discard_type] = self.trip_haul.get(discard_type, 0) - haul_discard
    remaining_discard = to_discard - haul_discard
    if remaining_discard > 0:
        self.game.cargo[discard_type] = (
            self.game.cargo.get(discard_type, 0) - remaining_discard
        )

    added = min(d.value, to_discard)
    self.trip_haul[d.type] = self.trip_haul.get(d.type, 0) + added
    self.recent_pickup = (d.type, added)
    self.recent_pickup_label = (
        f"swapped {to_discard} {discard_type.lower()} → {added} {d.type.lower()}"
    )
    self.recent_pickup_age = 0.0
    return

# Existing non-full path continues:
added = min(d.value, remaining)
self.trip_haul[d.type] = self.trip_haul.get(d.type, 0) + added
```

### Acceptance criteria (testing chat will verify when feature ships)

When the feature lands, `walk_cargo_full_pickup_refused` starts failing. Testing chat updates the walk's asserts to verify:

1. **Auto-swap fires**: cargo = `{COMMON: 200, ...}` (full); sweep over a 5-unit ENERGY deposit → `cargo[COMMON]` -5, `cargo[ENERGY]` +5, total still ≤ 200.
2. **Floater updates**: `recent_pickup_label` reads `"swapped 5 common → 5 energy"`, not `"cargo full"`.
3. **No swap when nothing lower exists**: cargo = `{ENERGY: 16}` (near-full at 200 cap with 12c each = 192); COMMON deposit refused (no lower-value type).
4. **Preserves mid-value cargo**: cargo = `{COMMON: 100, USEFUL: 100}` (full); ENERGY pickup discards COMMON (cheapest) first, USEFUL untouched.
5. **Partial swap is OK**: cargo = `{COMMON: 195, ENERGY: 5}` (200 full); 10-unit ENERGY pickup discards 10 COMMON, adds 10 ENERGY. Net: COMMON 185, ENERGY 15.
6. **Quest items unaffected**: PACKAGE_SCANNER_MK3 still commits immediately via stasis bay (existing code path).

### Design choices worth confirming with Aaron before implementation

- **Extend swap into the partial-fit case too?** With 150/200 used and an incoming 100-unit ENERGY: today, `min(d.value, remaining)` fits 50 and drops the rest. Better: also discard COMMON to fit the remaining 50. **Recommended: yes** — same user intent ("I'd rather have ENERGY than COMMON" applies regardless of whether the hold is exactly full).
- **Discard heuristic**: cheapest-first (spec above) vs. "preserve-best-ratio" (refuse swaps where discard-value-lost > pickup-value-gained × some margin). Cheapest-first is simpler and matches Aaron's stated intent. **Recommended: cheapest-first**.
- **Visual affordance**: text-only floater (`"swapped 5 common → 5 energy"`) vs. paired icon (small ↓ COMMON / ↑ ENERGY). Defer the richer indicator to Image chat if wanted.

### Testing chat will

- Watch for the feature to land (parallel sweep will go red on `walk_cargo_full_pickup_refused`).
- On red: re-author the walk to verify items 1-6 above; possibly add `walk_cargo_full_auto_swap_partial` for case 5.
- File a follow-up Findings entry to `HANDOFF_testing_chat.md` once the swap is verified working.

**Status**: ✅ PROCESSED 2026-05-17 — shipped in `src/scz/planet/scene.py:_on_pickup`. Algorithm extended into the partial-fit case too (per the design-choice "Recommended: yes"). Walk renamed `walk_cargo_full_pickup_refused` → `walk_cargo_full_auto_swap`; uses new `simulate_lander_pickup` harness primitive for deterministic case-coverage across all 6 acceptance scenarios (18/18 assertions). Three new harness primitives added: `expect_cargo_lt`, `expect_cargo_total_le`, `expect_cargo_higher_value_nonzero`. ASCII arrow (`->`) in the floater label per Windows cp1252 convention. Full regression: 46 walks / 474 assertions / 0 failed.

---

## 2026-05-17 — Bug: `run_walks_parallel.py` flakes on PlanetSurfaceScene walks at workers≥8

**Origin**: Testing chat, verifying the new framework. Filed during the test-plan-to-1.0 review.

**Symptom**: `python tools/run_walks_parallel.py` (default `--workers 8`) reports two walks as red:
- `walk_lander_collect_all` — `1 passed, 2 failed`, exit 2
- `walk_lander_liftoff_immediate` — `1 passed, 2 failed`, exit 2

Stderr tail shows only the benign `Warning: no fast renderer available` from `pygame.display.set_mode()`. Other walks in the same parallel batch pass cleanly.

**Crucially**: running either walk *sequentially* (`python -m scz --windowed --test walk_lander_collect_all`) returns `3 passed, 0 failed` with exit 0. From either cwd (worktree root OR `src/`). So the walks themselves are fine — the parallel runner is the bug.

**Likely cause**: pygame-init race. The PlanetSurfaceScene walks construct `Game()` → `pygame.display.set_mode((1920, 1080), pygame.FULLSCREEN | pygame.SCALED)` (see `src/scz/engine/game.py:37`). When 8 worker subprocesses do this concurrently, one or more end up with a partially-initialized display that can't render planet sprites. The "fast renderer" warning appears for *all* parallel processes but only the asset-heaviest walks (planet sprites + deposits + terrain) exit on it.

**Reproduction**:
1. `python tools/run_walks_parallel.py` → red on 2 lander walks
2. `python tools/run_walks_parallel.py --workers 4` → may still flake intermittently; needs confirmation
3. `python tools/run_walks_parallel.py walk_lander_collect_all walk_lander_liftoff_immediate` (just the two) → likely passes (only 2 parallel)
4. `python -m scz --windowed --test walk_lander_collect_all` → passes every time

**Suggested fixes (any one is sufficient)**:
1. **Serialize pygame init**: take a file lock around `pygame.init() + display.set_mode()` so only one subprocess initializes a display at a time. Cheap; preserves parallelism for the rest of the walk.
2. **Lower default `--workers` to 4**. Halves the speedup but eliminates the race in practice on most machines.
3. **Add a 50-200ms staggered startup delay** keyed by subprocess slot index. Hacky but trivial.
4. **Investigate parallel-safe SDL flags** — there may be a newer flag that disables the renderer probe entirely (`SDL_RENDER_DRIVER=software` or similar) so no race window exists.

**Workaround in place meanwhile**: testing chat's session-start recipe documented in `~/.claude/projects/.../memory/workflow_testing_plan_to_1_0.md` is "if parallel sweep is red on `walk_lander_*`, re-run those walks sequentially before treating as a real regression."

**Status**: ☐ Open

---

## 2026-05-17 — Halia–Steward banter library + Post-Fall Common Room reactions

**Lore sources**: `references/lore/halia-steward-banter.md` (NEW; canonical curated banter library, ~30 exchanges) + `tools/quest_inventory.csv` (5 NEW post-Fall Common Room crew-reaction mini-quests).

Both pieces serve the same goal: **make Halia's loss in the Fall feel like the player has lost a person**. The banter library is the *pre-Fall emotional deposit*; the post-Fall crew reactions are the *post-Fall emotional withdrawal*.

### Halia banter library — implementation contract

The library contains ~30 canonical exchanges organized by trigger context:

- **Tutorial banter** (Beat 1-7): one canonical exchange per tutorial beat; fires automatically at each milestone
- **Mid-game post-quest banter**: ~7 exchanges, each tied to completion of a specific quest (Slylandro Cloak, Mycon Whisper suppress/allow, Mraka Last Race favorable, Bren-Vor Aimer's Verdict favorable, etc.); fires within ~5 minutes of quest completion
- **Late-mid banter** (the heart-tightening trio): 3 exchanges that fire on calendar-week-equivalent triggers approaching the Fall:
  - ~3 weeks before: *"How long has it been since we just sat for tea?"* (the miss-you line)
  - ~2 weeks before: the visit-or-don't moment — **player-driven trigger**: if Steward routes to Mh-Lai during the window, the tea-and-mother conversation fires (Halia's *"I think she would have liked you"* canonical line); if Steward does NOT route to Mh-Lai, the canonical line is **permanently lost** (the line never appears later — the player missed it forever)
  - ~1 week before: the *"be more careful than the work requires"* line
- **Post-Fall banter variants** (3 versions): gate on `flag:halia_status` — alive_persuader / dead_witnessed-or-distant / cleanser_supervised. Each is a distinct rendered scene.

### Implementation tasks (Halia banter)

1. **Trigger-context registry** — Design needs a registry mapping trigger events (quest_complete:slylandro_cloak, milestone:tutorial_beat_4, calendar:weeks_before_fall_3, etc.) to specific banter exchanges. Suggested location: `src/scz/content/halia_banter.py`. Lore-authored content in the library doc → Design copies/transforms into Python data.
2. **Player-driven tea-visit trigger** — the canonical ~2-weeks-before-Fall window. When the player docks at Mh-Lai during this window, fire the tea-and-mother conversation. If the player does NOT dock at Mh-Lai during the window AND the window closes, set `flag:halia_mother_line_lost=True` permanently. The Fall fires shortly after — the canonical loss is canon. **Do not let the player re-trigger this; it's gone forever.**
3. **Banter rendering** — exchanges range from 2-12 lines. Render via the existing dialog FSM. Suggested implementation: each banter exchange is a small mini-quest in the quest spreadsheet OR a small standalone DialogCharacter scene (Design picks). Lore-side authoring is currently in the *library doc* as canonical text, not yet in spreadsheet rows.
4. **Voice flags for Halia** — `halia_voice_state` should track which register she's in (commander-formal / commander-warm / friend-private / late-mid-tightening / post-fall variant); the audio system queries this for performance direction.

### Post-Fall Common Room reactions — implementation contract

5 new mini-quests authored in `tools/quest_inventory.csv`, one per crew NPC, all gated on `flag:mhlai_destroyed=True`:

- `post_fall_crew_pilot` (Mraka) — 3 Halia-status-branches
- `post_fall_crew_weapons` (Bren-Vor) — 3 Halia-status-branches; Cleanser-supervised branch triggers `brenvor_will_resign_post_andromeda=True`
- `post_fall_crew_engineer` (Yelena) — Mev-Tar-alive console + silent-support paths
- `post_fall_crew_medic` (Mira-Rou) — share-Halia's-words; Sevreth's Child reacts if alive
- `post_fall_crew_navigator` (Tarven) — knowledge-as-archive console + wordless-tea-refill paths

Total: ~22 new rows in the quest spreadsheet.

### Implementation tasks (Common Room reactions)

1. **Common Room dialog routing** — when player enters Common Room post-Fall AND a crew member's `<role>_postfall_resolved` flag is False, the TALK action on that crew opens their post-Fall mini-quest instead of their normal dialog. Once resolved, normal dialog resumes (but with post-Fall context flag still queryable).
2. **Branch routing on `halia_status`** — Mraka and Bren-Vor each have 3-branch openers depending on `halia_status` flag value (free_persuader / dead_* / cleanser_supervised). Standard if/elif/else dispatch.
3. **Sevreth's Child reaction** — if `sevreth_child_alive=True`, Mira-Rou's post-Fall reaction includes the chemical-signal-humming line. Branch on the flag inside the q_mira_postfall_halia_words state.
4. **Persistent flags** — the post-Fall mini-quests set narrative-state flags (e.g., `mraka_will_lead_vector=True`, `brenvor_naming_shots=True`, `tarven_rebuilding_archive=True`) that flavor subsequent slice content. Cross-quest authors will reference these.

### Cross-chat dispatches

- **Image chat** (`HANDOFF_image_chat.md`) — minor work: Halia portraits already have 3 branch-state variants per prior Fall dispatch; the banter library doesn't require new portraits but suggests visual states for Halia (her warm office; her tea-service prominent; the fur-bound logbook on her desk pre-Fall). Common Room post-Fall scene already covered.
- **Audio chat** (`HANDOFF_audio_chat.md`) — voice direction for Halia's banter register (warm-dry-direct; her canonical verbal idioms *"That was a compliment"* / *"I'm telling you that as your friend, not your commander"* / *"Drink the tea"* should be delivered with flat-affect — the joke is in *not signaling the joke*); post-Fall crew banter mood already covered by existing Common Room ambient dispatch.

### Status

- ☐ Open as of 2026-05-17 — pairs with the Fall of Mh-Lai dispatch above. **The banter library is the slice's largest emotional investment.** Trigger-context wiring is the biggest piece of work.

---

## 2026-05-17 — Scanner Lore system (per-star + per-planet canonical reveal text)

**Aaron's brief**: planet + star lore that the scanner reveals on system entry / planet orbit. Significant stars (large / homeworld / unique) and significant planets (homeworld / quest / inhabited / remarkable resources / rainbow world / anomaly / SC2-canonical with 250kya backdating).

**Lore canon**: `references/lore/scanner-lore.md` (NEW) — covers 19 slice-cluster systems + 10 Rainbow Worlds; Tier 3 backlog noted (Earth, SC2 mainstream homeworlds, Sa-Matra prototype build site).

### Scanner reveal mechanic — Design implementation contract

1. **System entry trigger** — when the Steward arrives in a system via hyperspace, surface the *star lore* passage as a sensor-readout (UI per Design's existing scanner conventions)
2. **Planet orbit trigger** — when the Steward enters a planet's orbit (PlanetOrbitScene), surface the *planet lore* passage as the orbital scan readout
3. **Surface descent trigger** *(optional Phase 2)* — when the Steward lands on a planet surface, surface deeper surface-detail lore if it exists
4. **Already-revealed flag** — once the scanner has revealed a passage, mark the system/planet `lore_revealed=True` in `game.flags` so subsequent visits show the lore unobtrusively (not a full re-reveal)
5. **Bio-Archive integration** — lore-revealed planets/stars should auto-add a Bio-Archive entry per canonical scanner reveals (canonical: the Steward's Furling Scout's onboard log auto-archives revealed knowledge)

### Suggested implementation

- `src/scz/content/scanner_lore.py` — canonical lore-text registry; data sourced from the lore doc; format: `{star_id: {"star_lore": str, "planets": {planet_idx: {"orbital": str, "surface": str|None}}}}`
- `src/scz/system/scene.py` — extend `on_enter` to check star_id, surface star_lore if present + not yet revealed
- `src/scz/planet/scene.py` — extend orbit-entry to check planet, surface orbital lore if applicable
- New UI element: scanner-readout text panel (Furling-cyan accent; canonical scanner aesthetic)

### Post-Fall reveal divergence

For Mh-Lai specifically, the scanner reveal differs based on `mhlai_destroyed=True`. Design should check this flag and surface the appropriate text. Lore doc has both versions.

### Performance notes

The scanner lore text is canonical content per the lore doc; future Phase 3 variation can add minor lexical jitter per the variation principle, but for slice MVP fixed-text is acceptable.

### Cross-chat dispatches

- **Image**: no NEW assets needed (the canonical planet sprites from existing planet-type renderers are sufficient); scanner UI is text-based
- **Audio**: a soft *scanner-chime* audio cue when lore is revealed (canonical Furling-warm tone; ~300ms; non-intrusive)
- **Testing**: walk-test for scanner reveal on each canonical system

### Status

- ✅ PROCESSED 2026-05-17 — Scanner Lore system shipped end-to-end:
  - `src/scz/content/scanner_lore.py` — `SystemLore` dataclass + `STAR_LORE: dict[str, SystemLore]` registry covering 13 slice-canonical systems (Mh-Lai, Arilou Outpost, Sol/proto-Humans, Slylandro/Beta Corvi, Procyon/Chenjesu, Ossuary/Mmrnmhrm, Taalo's Stone, Burvix Caster, Whirligig/Lemmkin, Beta Aquarii/Utwig, Beta Orionis/Dnyarri, Mycon Hive, Orz Rift)
  - `star_key()` helper maps any `star` dict → canonical lookup key via `defined_name` or `cluster_name` fallback
  - `reveal_star_lore(game, star)` + `reveal_planet_lore(game, star, planet_index)` — set `lore_revealed_star_<key>` / `lore_revealed_planet_<key>_<idx>` flags + return `(text, is_first_reveal)` so the UI can show the "+ ARCHIVE ENTRY" indicator only on first visit
  - **Post-Fall override**: Mh-Lai homeworld (planet index 2) returns the "consumed; Council chambers gone" variant when `mhlai_destroyed=True`
  - `SystemScene.on_enter` calls `reveal_star_lore`; `PlanetOrbitScene.on_enter` calls `reveal_planet_lore`; both render a "SCANNER · STAR" / "SCANNER · ORBITAL" word-wrapped panel in their HUD
  - `_wrap_text` helper added to both scenes (deduped opportunity for a shared util later)
  - `walk_scanner_lore` (5/5 green) verifies both star + planet flags set on entry
  - Cross-chat dispatches dropped out: Audio chat (a 300ms scanner-chime cue on first reveal); Image chat (no new assets — text-only); Testing chat (per-system walk-tests when other species ship). Bio-Archive auto-add deferred to Phase 5 polish.

---

## 2026-05-17 — Combat + Crewmate Banter Library (canonical content + trigger system)

**Aaron's brief**: combat banter at multiple damage brackets per species + per match-up; crewmate banter with side-quest carrot lead-ins and inter-crew differences.

**Lore canon**: `references/lore/banter-library.md` (NEW) — ~300 canonical banter lines: generic per-species banks (16 species × ~10-15 lines across damage brackets); 5 priority match-up specific sets (Cleanser climax / Sa-Matra Prototype / Mrokon Hammer-Ship / Others' Vessel / Defender Vessel); Steward-crew Common Room conversations (6 crew with side-quest carrot lead-ins gated on goalpost flags); 4 cross-crew pairings (Mraka+Yelena easy-bond; Bren-Vor+Mira-Rou shared-grief-quiet; Tarven+Mraka Olwen-Veth-reveal; Forward+ANY).

### Banter trigger system — implementation contract

1. **Combat banter trigger** — fires on combat-state events: damage-bracket transitions (100→75, 75→50, 50→25, 25→0 hull%); first-contact (>75% opening); post-fight (winner + loser lines)
2. **Match-up specific preference** — prefer specific match-up's line bank if it exists; otherwise fallback to per-species generic bank
3. **Common Room dialog initiation** — TALK on crew → check side-quest flags → surface appropriate banter bracket (pre-side-quest / mid-side-quest carrot / post-side-quest favorable)
4. **Cross-crew ambient banter** — fires when both crew present in Common Room + slice progression triggers; volume ducks ambient bed
5. **Per-encounter variation** (Phase 3+ per variation principle) — banter never repeats identically; slice MVP can ship with fixed line-pool sampling

### Suggested implementation files

- `src/scz/content/banter.py` — canonical line bank loaded from lore doc's structured content
- `src/scz/combat/banter_system.py` — trigger system + bracket detection + line-pool sampling
- `src/scz/scenes/common_room.py` (per prior Common Room HANDOFF) — extends with crew banter dispatch

### Canonical content rules (per lore doc)

- **The Steward's wit is canonically funny** (Furling humor doctrine) — combat lines deadpan-witty, not slapstick
- **The Others are NEVER funny** — their combat banter is Steward-only; no NPC Others lines
- **Lemmkin and Slylandro stay cheerful/confused at every damage bracket** — canonical exceptions to escalation arc
- **Time Drive interaction**: Steward does NOT remember rewound fights; only Cleanser canonically does (Vael-Souren *"I always know"* line)
- **Never hurtful to the player** — crew may tease but never cruelly

### Voice direction cross-canon

- Damage-bracket *tonal arc*: opening playful → mid aggressive → pressed cracking-or-doubling-down → desperate per personality
- Drev-Tok combat banter preserves *2-years-of-grievance-held-in-formal-stillness* register
- Forward's 2D jokes delivered with full sincerity — joke is in listener's recognition, never speaker
- Karavem combat is *musical* with emotional-valence-reversal (major = sad/formal; minor = joy/exploratory)

### Status

- ☐ Open as of 2026-05-17 — pairs with existing Common Room dispatch. Banter is the slice's *character-voice payoff* during combat + Common Room.

---

## 2026-05-17 — **SLICE TERMINAL**: The 6-tier Endings system + ending-evaluation logic

**Aaron's brief**: 6 canonical ending tiers (Best / Great / Good / Successful-at-a-cost / Unsuccessful / Disastrous) gated on ally count + crewmate count + side-quest completion.

**Lore canon**: `references/lore/the-endings.md` (NEW). Quest: `the_endings_evaluation` in `tools/quest_inventory.csv` (~13 rows).

### Threshold cascade (per lore doc; tuneable)

```
IF ally_count >= 16 AND crewmate_count >= 5 AND side_quest_completion_pct >= 95: BEST
ELIF ally_count >= 16 AND crewmate_count >= 5 AND side_quest_completion_pct >= 85: GREAT
ELIF ally_count >= 16 AND crewmate_count >= 1: GOOD
ELIF ally_count >= 8 AND crewmate_count >= 1: SUCCESSFUL_AT_A_COST
ELIF ally_count >= 1 AND ally_count <= 7 OR crewmate_count <= 1: UNSUCCESSFUL
ELIF ally_count == 0 AND crewmate_count == 0: DISASTROUS
```

First-match-wins.

### Threshold flags Design needs to compute

- **`ally_count`** — count of species at non-Eliminated terminal status (Migrated/Cloaked/Pre-sentient/Hidden/MixedEliminatedMigrated-with-diaspora/Pending-favorable)
- **`crewmate_count`** — count of `recruited_<role>=True` flags (range 0-5; weapons-officer slot counts either Bren-Vor OR Forward)
- **`side_quest_completion_pct`** — favorable-quest-count / total-completable * 100

### Ending-evaluation timing

- **Best / Great / Good / Successful-at-a-cost**: AFTER Final Conflict resolves AND Crossing-Opens cinematic plays
- **Unsuccessful**: when Migration timeline reaches Others'-arrival deadline AND Steward has FEW allies/crew — Final Conflict either never triggers OR is bypassed
- **Disastrous**: same deadline + 0 allies + 0 crew → unique negotiation cinematic with treaty-signed-in-Steward-blood canonical punchline

### Per-ending implementation tasks

1. **6 distinct ending cinematics** (per Image / Audio HANDOFFs)
2. **`slice_ending` state-flag** (BEST / GREAT / GOOD / AT_COST / UNSUCCESSFUL / DISASTROUS) for any post-slice content to query
3. **SC2-era canonical-impact flags**: `sc2_era_canonical`, `galaxy_consumed_forever`, `treaty_signed_in_blood` — for any future SC2-era references in the project to respect
4. **Unsuccessful + Disastrous DO NOT need Crossing-Opens** — unique sequences instead
5. **Unsuccessful** reachable via timeout path (Others arrive before Migration assembles)
6. **Disastrous** requires NEW unique cinematic — the *negotiation-attempt-and-consumption* scene; canonical *"the Steward unilaterally drafts a treaty ceding the galaxy in perpetuity"*; the cinematic IS the dark-comedy punchline

### Drev-Tok retroactive framing

- **Favorable endings**: Drev-Tok was wrong (Migration worked)
- **Unsuccessful**: Drev-Tok was right (Migration failed; galaxy consumed)
- **Disastrous**: Drev-Tok was *retroactively correct and tragically irrelevant* — died defending a galaxy the Steward then surrendered

Design can wire these into Drev-Tok's epitaph in the relevant endings (memorial mention OR canonical *"I told you so"* voice from beyond).

### Status

- ☐ Open as of 2026-05-17 — **slice terminal**. The Endings ARE the slice's payoff. Highest priority Design work after the Final Conflict implementation.

---

## 2026-05-17 — The Quiet Resolution canon + 4 NEW lander-upgrade modules + Melnorme recruitment quest

**Aaron's brief**: *"make sure each species we meet are covered by their own side-quest where they need something from us or need us to do something… Each success gives us a reward of some sort (one of our crew, a module blueprint, an artifact, a sensor, lander, or lander upgrade)."*

**Lore canon**: `references/lore/the-quiet-resolution.md` (NEW) — formalizes:
- The slice's mandate name: **"The Quiet Resolution"**
- The 6-category reward framework: crew / module blueprint / artifact / sensor / lander / lander-upgrade
- Full reward parity audit table covering all 19+ slice species quests
- 4 NEW lander-upgrade modules to close the lander-upgrade reward gap

### Reward parity audit results

Every slice species has at least one canonical side-quest with at least one tangible reward. **Two gaps were filled**:

1. **Melnorme recruitment quest** — existed in code (`walk_melnorme_recruitment`) but missing from Lore-side spreadsheet. Now authored: `melnorme_recruitment` quest with 8 rows; full Council-deliberation-and-shelving-test FSM; grants `MELNORME_COUNCIL_SEAT` sensor (reveals super-giant trade routes + per-system BIO-yield hints)
2. **Lander-upgrade reward category** — 0 species quests previously granted lander upgrades. Now 4 do.

### 4 NEW lander-upgrade modules

Per the existing Melnorme HANDOFF entry, lander upgrades occupy a new `lander_armor` slot parallel to `sensor`. The 4 new modules (granted by quest outcomes, NOT by Melnorme trade):

| Module ID | Quest grant | Deltas (suggested; Design refines) | Lore-side description |
|---|---|---|---|
| `LANDER_CHENJESU_CRYSTALLINE_PLATING` | `chenjesu_resonance` standard outcome | `surface_hazard_resistance: +0.5` | Crystalline-resonance hull-plating derived from Chenjesu biology; gentle bioluminescent shimmer visible while landed |
| `LANDER_MROKON_PUPPET_ARMOR` | `mrokon_hammer` full-support outcome | `lander_max_hp: +30%; surface_hazard_resistance: +0.25` | Mrokon puppet-armor metallurgy applied to lander chassis; bears canonical scribed-ledger pattern (kill-tally marks added per surface mission — *the puppet-armor tradition extended to landers*) |
| `LANDER_BURVIXESE_AMPLIFIER` | `burv_caster` witness-silent outcome | `surface_sensor_range: +0.35; deposit_detection_fidelity: +0.2` | Cognitive-amplification circuitry derived from smaller Burv Broadcaster nodes, miniaturized for lander use |
| `LANDER_TAALO_SILICATE_HARDENING` | `taalo_shield` help-fully outcome only | `surface_hazard_resistance: +0.4` (specifically against lava/lightning/geological hazards) | Silicate-substrate plating derived from Taalo Shield-fragment material; pale-violet glow-tracery visible |

**Quest-FSM update**: The 4 quest terminal-states' `side_effects` columns in `tools/quest_inventory.csv` now include the corresponding `module:<NAME>` entry. Design wires the module-grant flow.

### Implementation tasks

1. **`lander_armor` module slot** — extend `SLOTS` tuple in `src/scz/content/modules.py` (if not already done per Melnorme HANDOFF backlog)
2. **4 new Module definitions** in `modules.py` per the table above (tier=0; cost_credits=0 since quest-rewards; deltas per suggestions)
3. **`melnorme_recruitment` quest implementation** — Design has the walk-test already; Lore-side spreadsheet now matches. Verify the implementation matches the canonical CSV rows.
4. **`MELNORME_COUNCIL_SEAT` sensor module** — already stubbed in modules.py per prior linter-touched state; verify deltas match canonical lore intent (super-giant-trade-routes-visible flag + per-system-BIO-yield-hint flag)

### Halia Council briefing canonical update

Per The Quiet Resolution canon, Halia's first-tutorial Council briefing should canonically open with the mandate-name introduction. Suggested line for the tutorial dialog FSM:

> **Halia**: *"Steward. Your mandate is The Quiet Resolution. Every species we encounter must be brought to a terminal state — saved, hidden, or honestly mourned — before the Others arrive. The bookkeeping is the dignity."*

Design-chat should wire this into the existing tutorial Beat 2 or Beat 3 Halia briefing scene.

### Drev-Tok dialog update (cross-canon with Final Conflict)

Per The Quiet Resolution canon, Drev-Tok's Council-channel opposition voice should reference *"The Quiet Resolution"* dismissively. The Final Conflict opening transmission can be updated to include:

> *"Your Quiet Resolution is what brought us here, Steward. You resolved species into terminal statuses; I have been *not* resolved into one for two years, and here I am."*

This is canonical and ties Drev-Tok's grievance explicitly to the mandate-name.

### Status

- ☐ Open as of 2026-05-17 — lander-upgrade module category + Melnorme quest catch-up + canonical mandate-name wiring. ~1 week of Design work.

---

## 2026-05-17 — **SLICE CLIMAX**: The Final Conflict — fleet-vs-fleet super-melee at the Rainbow Worlds arrow-tip

**Aaron's brief**: *"the remaining fleet of the Precursors of all the migrating species arrive at the point of the arrow of rainbow worlds to depart, but they are greeted by the Homesteaders led by your arch nemesis leader of the Homesteaders. Confrontation is a giant super-melee between the two fleets."*

**Lore canon**: `references/lore/the-final-conflict.md` (NEW). Quest FSM: `the_final_conflict` in `tools/quest_inventory.csv` (~16 rows; 3 outcome branches).

This is **the slice's climactic battle** — the largest combat scene by an order of magnitude. Fleet-vs-fleet engagement; multi-phase boss fight; the slice's largest single design investment.

### Trigger conditions

- `flag:mhlai_destroyed=True` (Fall has happened)
- `flag:rainbow_resonator_equipped=True` (climactic module installed)
- `flag:rainbow_worlds_seeded>=8` (alignment threshold)
- `flag:migration_fleet_assembled=True` (Hearth-of-Iron has called the fleet)

When all met → forced cinematic; slice climax begins.

### Arch-nemesis canonical NPC — Admiral Drev-Tok Velt-Mar

**New DialogCharacter** needed: `drev_tok_velt_mar()` in `src/scz/dialog/characters.py`. He has been **heard on Council channels for 2 years** of slice time — the canonical *voice the Steward has known but never met in person*. Until this scene.

- **Voice**: stern, controlled, *2-years-of-grievance under the control*
- **Personality**: lifelong Defender; veteran of three operations; lost his cohort; doctrinally committed and personally furious
- **His position**: Migration is preemptive surrender; the Furlings can fight with the Sa-Matra; the Mrokon proved the Others can be marked; leaving is betrayal
- **He is wrong about Sa-Matra scaling** — the Hider faction has measured this; he is wrong; but he is *committed*

Suggested implementation: add Drev-Tok's voice into earlier Council scenes as a *recurring opposition voice* the player hears on broadcast. Each major Migration-aligned vote the Steward casts in a Council scene should include a brief Drev-Tok counter-statement. This builds the 2-year-recurring-voice canon.

### Coalition composition (data-driven)

Drev-Tok's fleet composition depends on prior slice flags:

| Flag | Effect |
|---|---|
| `mrokon_hammer_fired_full=True` | +12 Mrokon Hammer-Ships symbolic presence |
| `burvixese_sabotaged=True` | +Burvixese Broadcaster-modified vessels |
| `forward_collective_aboard=False AND thinn_pending=True` | +Thinn troupe holdouts (edge-on; faint chromatic slipstreams) |
| `cleanser_acceleration=True` | +hardline Cleanser contingent; **Halia canonically on Drev-Tok's side via Cleanser-vessel capture** |
| `slylandro_eliminated=True` | +bitter Slylandro contingent |

Migration fleet composition also depends on prior slice flags (Migrated terminal statuses per the Migration Timetable). The fleet-composition system needs to *read* slice state and render appropriately. **The visual asymmetry of the two fleets reflects every choice the player made.**

### 3-phase Sa-Matra Prototype boss fight

The Sa-Matra Prototype is a **multi-phase boss**:

- **Phase 1** *(100%-50% hull)*: heavy energy-lance volleys at Migration flagships; defensive piloting required
- **Phase 2** *(50%-25% hull)*: Prototype splits into 3-vessel multi-form; central coordination vessel can be one-shot by **Bren-Vor's Precision Focus** OR **Forward's Perpendicular Aim** if either crew is recruited *and* their side-quest completed favorably; otherwise much harder
- **Phase 3** *(25%-0% hull)*: Prototype unifies for final volley AT THE DIMENSIONAL CROSSING ITSELF; ~30 seconds intercept window; **Yelena's Field Overhaul** crucial for surviving; **Hijacked Others' Vessel Decursion** can stutter the firing solution if equipped

### Crew active-ability payoff design

The whole crew-side-quest investment pays off here. Players who built bonds with crew through side-quests get *substantially easier combat*:

- **Mraka's Evasive Burst** — escape Sa-Matra volleys
- **Bren-Vor's Precision Focus** OR **Forward's Perpendicular Aim** — one-shot Phase 2 coordination vessel
- **Yelena's Field Overhaul** — single full-repair during the fight (Phase 3 is hard to survive without it)
- **Mira-Rou's Bio-Signature Dampening** — reduce Sa-Matra lock-on duration
- **Tarven's Deep Archive Scan** — reveal Sa-Matra targeting pattern; pre-position

This is the canonical *crew side-quest payoff*. Skipping side-quests = canonically the hard version.

### Diplomatic rare outcome — implementation contract

The "diplomatic rare" branch requires ALL of:
- `flag:standing_persuader>=10`
- `flag:has_others_vessel=True AND flag:others_vessel_council_sanctioned=True` (Council-sanctioned Hijacked Vessel — NOT the secret variant)
- `flag:halia_status=free_persuader`
- `flag:has_distress_beacon=True`
- ≥ 5 Homesteader species at terminal Cloaked/Pre-sentient/Hidden/Pending

When the Steward says *"Admiral. Look at my ship"* and decloaks the marked Others' Vessel: Drev-Tok sees the Mrokon marking-tech integrated; canonical conversion line; Defender doctrine reframes; he joins the Migration.

This is **the slice's hardest-to-unlock outcome**. Hidden achievement-tier.

### The Crossing-Opens cinematic

When the conflict resolves favorably, the **Rainbow Resonator fires + the Rainbow Worlds align + the dimensional crossing opens**. Multi-frame cinematic showing the Migration fleet entering the iridescent corridor in canonical order:

1. Kovellim Crossing-Frigates first (vanguard)
2. Karavem Aria-Skiffs second (singing the crossing-passage)
3. Selvenne Tank-Ships third
4. Furling Migration Lifts main mass
5. Migrant-contingent ships
6. The Steward's ship LAST (canonical Persuader-Commander honor)

If Halia is alive: she stands beside the Steward on the bridge.

### Halia branch-state implications (cross-canon)

- **Halia alive free**: stands beside the Steward on the bridge during the climax; appears in the diplomatic-rare conversion scene as a witness; canonically *quiet* (she has earned the right to be quiet here)
- **Halia dead**: her memorial sigil on the bridge; her last transmission (*"Keep going"*) plays once during the crossing-opening cinematic
- **Halia Cleanser-supervised**: **she is on Drev-Tok's side**. This is the DEVASTATING variant — the Steward fights their friend's controlled-vessel during the super-melee. A canonical moment: Halia's Cleanser-channel transmission during combat where she briefly breaks formal cadence to whisper *"...I'm sorry, Steward..."* before the channel cuts back to formal review. **The slice's most painful single line in this branch.**

### Implementation scope

This is **the largest single Design-side scene in the slice**. Conservative estimate: 4-6 weeks of work. Key sub-systems:

1. **Fleet-vs-fleet combat mechanic** — extension of MeleeCombatScene; multi-ship engagement; player commands one ship + issues commands to fleet (or simpler: the player just commands their own ship and the fleet AI handles itself)
2. **Sa-Matra Prototype as multi-phase boss** — NEW ShipClass with phase-transition behavior
3. **Coalition-composition reader** — Drev-Tok's fleet renders based on slice flags
4. **Drev-Tok DialogCharacter** — including the 2-year-recurring-voice on Council channels (retro-fit work)
5. **Diplomatic-rare gating** — multi-flag combinatorial check
6. **The Crossing-Opens cinematic** — multi-frame Image dispatch + Audio cue
7. **Halia branch-state integration** — bridge composition + Cleanser-supervised whisper line

### Cross-chat dispatches

- **Image** HANDOFF entry to be posted: Drev-Tok portrait + Sa-Matra Prototype exterior + multi-phase variant sprites + fleet-arrival cinematics + the diplomatic-success-conversion frame + the dimensional crossing-opens cinematic
- **Audio** HANDOFF entry to be posted: **THE SLICE'S ONLY MAJOR ORCHESTRAL CUE** lives here; Drev-Tok's voice (stern-controlled-2-years-of-grievance); the Crossing-Opens canonical music; the Halia Cleanser-supervised whisper line as the slice's most painful single audio moment
- **Testing** HANDOFF entry to be posted: `walk_final_conflict_diplomatic`, `walk_final_conflict_symbolic`, `walk_final_conflict_combat`, `walk_final_conflict_cleanser_halia` (the worst-case branch with Halia on the wrong side)

### Status

- ☐ Open as of 2026-05-17 — **slice-climactic**. Highest priority Design work after the Fall of Mh-Lai is implemented. The slice does not *complete* without this scene.

---

## 2026-05-17 — **MAJOR**: The Fall of Mh-Lai — mid-slice catastrophe + service-transfer rewiring

**Aaron's direct dispatch (2026-05-17)**: *"a very emotional scene in the mid-point of the game where The Others find the council and consume the Furling home planet."*

**Lore canon**: `references/lore/the-fall-of-mh-lai.md` (NEW). Quest FSM: `the_fall_of_mh_lai` in `tools/quest_inventory.csv` (~18 rows; 4 outcome branches).

This is **the slice's biggest single emotional + structural beat** — Mh-Lai Station is destroyed mid-game; every Mh-Lai-only service must transfer to a Migration flagship; the slice's tone shifts permanently.

### Trigger contract

Suggested gating (Design refines):
- `flag:tutorial_complete=True`
- `flag:has_distress_beacon=True` (Steward must already understand what the Others ARE)
- `flag:systems_visited >= 5`
- AND at least one of: `slylandro_decision_made` OR `mycon_decision_made`

When all conditions met: **the scene auto-fires at the next hyperspace traversal**. The dimensional-ripple alarm sounds; Halia's transmission opens. The player CANNOT defer it (forced beat). The decision window is time-constrained — suggested 60 real-time seconds of pause-able UI (if the player times out, the *don't-race* branch defaults).

### Branches + their gameplay consequences

| Branch | Halia outcome | Service-transfer effect | Cleanser standing required |
|---|---|---|---|
| **Race + evacuate (success)** | Alive on Hearth-of-Iron; Persuader-faction free | Standard transfer | — |
| **Race + Halia honors-protocol** | Halia dies; Persuader-faction operational | Standard transfer | — |
| **Race but doomed (witness)** | Halia dies; deep grief | Standard transfer + bonus Archive | — |
| **Don't race** | Halia dies; political pragmatism | Standard transfer | — |
| **Cleanser acceleration** | Halia alive but Cleanser-supervised; Persuader collapses | Standard transfer + Cleanser channel-review overlay | `cleanser_standing >= 3` + `cleanser_action_authorized=True` |

### Critical post-fall implementation work

This is the **single largest mid-slice rewiring** in the codebase. Implementing this cleanly requires:

1. **`flag:mhlai_destroyed=True`** — set on the fall; checked by ALL Mh-Lai-related scenes thereafter
2. **Hearth-of-Iron as new home base** — a NEW scene `src/scz/scenes/hearth_of_iron.py` mirroring the existing Mh-Lai station scene but with:
   - All Mh-Lai-only services (Trade, Customization, Bio-Archive, tier-1+ install-gate) operational
   - Halia branch-state visible — her Hearth-of-Iron command position, dead-memorial display, or Cleanser-supervised stance
   - Mev-Tar Lwen-Tar's transferred Unzervalt tooling visible in the assembly bay
   - Furling fur-aesthetic *with grief markers* (Mh-Lai memorial sigils on walls)
3. **Service-transfer routing** — when the player tries to dock at Mh-Lai post-fall, redirect to Hearth-of-Iron. The Mh-Lai system in the hyperspace map should show *empty space + station-debris* (no longer a docking target).
4. **Halia DialogCharacter branch-states** — three voice + portrait variants per branch (alive Persuader-free / dead-remembered / alive Cleanser-supervised). All future Halia dialog scenes check `flag:halia_status` to pick the right variant.
5. **Migration timetable acceleration** — Phase 4 (Last-Wave) effectively *begins now* in the timetable. Quest-state pre-checks for any Phase-4-or-later content should accommodate compressed timing. **This is a long-tail change touching many quests.**
6. **Common Room mood shift** — post-fall, the Common Room ambient bed shifts (per Audio HANDOFF). Crew banter has post-fall variants (per Lore doc; canonical lines authored per crew). Quest-state should expose `flag:mhlai_destroyed=True` for the banter system to query.
7. **Bio-Archive auto-entry** — on completion of the fall, automatically add the canonical "The Fall of Mh-Lai (witnessed)" or "(reported)" entry to the Bio-Archive — variant depending on branch.
8. **Crew side-quest interaction** — Yelena's Last Hull side-quest's setting (Unzervalt) is gone post-fall. The quest's setting should canonically transfer to *Hearth-of-Iron's assembly bay* where Mev-Tar has rebuilt the tooling. Lore-side handle the dialog change; Design wires the scene-location switch.

### Time-constrained decision UI

The 60-second decision window is novel for this slice. Existing dialog FSM is text-based and untimed. Design needs to extend the dialog system OR build a one-off timed-decision UI for this scene specifically. Suggested: a clean countdown bar at the top of the screen + bold red text *"Decide before the window closes"*; if timer expires, default to `c_honor_migration`.

### Cross-chat dispatches

- **Image** HANDOFF entry posted same date — 9+ cinematic frames + 3 Halia branch-state portraits + Hearth-of-Iron exterior + interior concourse
- **Audio** HANDOFF entry posted same date — Halia's two transmissions + the dimensional ripple + the cascading death-of-voices effect + post-fall ambient bed + 3 Halia voice branch-variants + music policy (NO music until the post-fall memorial scene)
- **Testing** HANDOFF entry below — `walk_mhlai_fall_race_success`, `walk_mhlai_fall_dont_race`, `walk_mhlai_fall_cleanser_acceleration`, `walk_hearth_of_iron_dock`

### Quest-FSM implementation note

The quest is **forced + branching**; it cannot be skipped. When the trigger conditions are met, fire the scene at the next hyperspace traversal. The `q_mhlai_warning` opening state is non-interactive (forced sensor alarm); the player IS thrust into Halia's transmission. Decision happens at `q_mhlai_halia_first` with the 4 branches above. Each outcome state sets a comprehensive flag-set that downstream content can query.

### Status

- ⏳ IN-PROGRESS as of 2026-05-17 — **MVP shipped**: `src/scz/scenes/fall_of_mhlai.py` (465 LOC) + `src/scz/content/fall_of_mhlai.py` (241 LOC, 4-branch registry + `should_fire_fall` predicate); auto-fire on hyperspace traversal; 5-beat scene (detection / transmission / decision / fall / aftermath); 60s timed decision window; `walk_mhlai_fall_dont_race` (9/9 green); post-fall station rebrand to HEARTH-OF-IRON. **Still open**: 3 Halia portrait-and-voice branch variants (all-3 alive/dead/cleanser-supervised), Migration timetable acceleration for downstream quests, Crew side-quest setting transfer (Yelena's Last Hull → Hearth assembly bay), Cleanser-supervised channel-review overlay, Bio-Archive auto-entry on branch resolution.

---

## 2026-05-17 — **MAJOR**: Crew Common Room scene + interaction UI (Aaron's direct request)

**Aaron's direct dispatch (2026-05-17)**: *"a whole crew gathering spot in the ship and images for that, and a way to chat and interface with the crew."*

**Lore canon**: `references/lore/crew-common-room.md` (NEW, full doc). Read this first — it spells out the physical layout, per-crew alcoves, bond-objects that accumulate as slice progresses, banter rules, and what does NOT belong in the room.

This is **a substantial new scene + UI surface**. Sketch of scope below.

### Scene scope — `src/scz/scenes/common_room.py` (NEW)

The Common Room is the ship's social hub — accessible from the ship's main HUD (suggested: a new top-level menu item alongside Bio-Archive / Customization / Trade — OR a dedicated controller shortcut from any scene where the Steward is on the ship). It's an *interactive 2D scene*, not a combat or exploration screen.

**Required scene behaviors**:

1. **Render the Common Room interior** — backdrop image (Image-chat-dispatched) + 5 named-crew alcove regions + central long-table + Steward's bunk corner + generic-crew rotating alcove. Furling fur-everywhere aesthetic per canon.

2. **Render present crew at their alcoves** — for each `recruited_<role>=True` flag set, render the corresponding crew member at their canonical alcove with their canonical posture (per the lore doc):
   - Mraka at port-forward window
   - Bren-Vor on his bunk-edge cleaning a rifle component
   - Yelena at her workbench
   - Mira-Rou at her medbay-window observation post
   - Tarven cross-legged on his bunk with log-readers
   - Generic crew (Archivist/Warden/Tunneler) at rotating-bunk alcove (whichever is currently installed)

3. **Render bond-objects per alcove** — each crew alcove has a personal shelf that accumulates bond-objects as side-quests resolve. Render conditional on slice progression flags. See lore doc for the full per-crew bond-object list. Suggested data structure: `BOND_OBJECTS: dict[str, list[BondObject]]` with `crew_role` → list of `BondObject(flag_required, image_asset, position_in_alcove)`.

4. **Approach + interact** — Steward's player-cursor navigates the room (D-pad or mouse). When cursor is over a crew member, render **"TALK"** prompt (Furling cyan accent per palette). A on controller / Enter on keyboard opens that crew's dialog FSM.

5. **Side-quest notification badge** — when a crew's side-quest goalpost prereqs are met (e.g., `recruited_pilot=True AND systems_visited>=5` for Mraka), render a **"!" notification badge** beside that crew's alcove portrait. Badge clears when the side-quest's `q_<role>_sq_start` state is entered (the dialog opens). Suggested impl: a `notification_visible(game, crew_role) -> bool` helper that checks the goalpost flag-conditions per the crew-recruitment-quests doc.

6. **Approach the central table** — opens ambient-banter mode. The crew currently chatting say their lines; player can listen, sit (join the table, hear more lines), or move on. Banter content is per-encounter-varying (per slice's variation principle). Lore doc has banter rules per-pairing.

7. **Approach the Steward's bunk** — opens a small *bunk menu* allowing the player to (a) review the Bio-Archive in narrative format (alternate path to the Mh-Lai Bio-Archive scene), (b) check accumulated milestone artifacts on the bunk-shelf, (c) sleep / time-skip if useful.

8. **Approach the generic-crew alcove** — shows current rotating resident (Archivist / Warden / Tunneler) with a brief role-flavored line. Generic crew aren't deep dialog NPCs.

### UI components — new requirements

- **Notification badge sprite** (small "!" with subtle pulse-animation; Furling cyan accent)
- **TALK prompt sprite** (button-icon + "TALK" label; appears on cursor-hover)
- **Banter bubble** (text bubble that floats above the speaking crew member during ambient banter; auto-dismisses after each line)
- **Bond-object shelf renderer** — per-alcove shelf-region with dynamic positioning of conditionally-rendered objects

### Dialog FSM hooks

The Common Room **doesn't author dialog content** — it dispatches to existing crew DialogCharacter factories:

- `mraka_yenn_sa()`, `bren_vor_telcas()`, `yelena_lwen_tar()`, `mira_rou_halve_tel()`, `tarven_olwen_sa()` — all per `crew-recruitment-quests.md`

When the player clicks "TALK" on a crew member, the Common Room scene **opens the appropriate dialog scene**. The dialog FSM handles the rest (recruitment dialog if not yet recruited; ambient banter if recruited; side-quest start if goalpost met; etc.).

**New DialogCharacter state needed**: each crew NPC needs a `common_room_default()` state — what they say when the player initiates non-mission dialog. Suggested content per crew (Lore-chat authoring deferred to a follow-up pass; for MVP just stub strings are fine).

### Banter system (Phase 2 — slice MVP can ship without this)

Ambient banter is *nice-to-have* for slice MVP but not blocking. Suggested phasing:

- **MVP (Phase 1)**: Common Room renders; crew visible at alcoves; TALK prompt works; dialog dispatches; notification badges work for side-quests
- **Phase 2 (post-MVP)**: ambient banter system — periodic auto-fired lines between crew when player is in the room but not actively dialoging
- **Phase 3 (post-MVP)**: per-encounter banter variation per the variation principle

### Cross-canon implications

- **Time Drive interaction**: when the player rewinds the Time Drive, the Common Room state should rewind too — any conversation in progress reverts; notification badges return to their pre-rewind state. Standard rewind semantics.
- **Crew morale modifier**: crew_morale stat may be visible in the Common Room (per-crew small mood indicator?). Suggested: subtle facial-expression variation in the crew portraits based on their morale + recent slice events. Phase 2+ work.
- **Bio-Archive narrative alt-path**: per lore doc, the Steward's bunk lets the player review Bio-Archive content "in narrative format" — this is a *style variant* of the Mh-Lai Bio-Archive scene, not a duplicate scene. Suggested implementation: reuse `BioArchiveScene` with a `narrative_mode=True` flag that changes the visual presentation (e.g., text rendered as if from the Steward's POV, hand-written-journal aesthetic instead of clinical-archive aesthetic). Defer to post-MVP if scope is tight.

### Sub-dispatches to other chats

- **Image chat** (`HANDOFF_image_chat.md`) — full Common Room art request: room backdrop, 5 named-crew alcove visuals, generic-crew alcove, central long-table, Steward's bunk corner, ALL bond-objects (~15-20 small object sprites that conditionally render), notification badge sprite, TALK prompt sprite, banter bubble template
- **Audio chat** (`HANDOFF_audio_chat.md`) — Common Room ambient bed (fur-muted warm interior sound — soft fabric rustles, Tarven's tea-cup clinks, Yelena's tools tap-tap-tap on her workbench, distant ship-system hums); banter cue audio (per crew); notification-badge "!" sound (small pleasant chime, NOT alarming); TALK prompt confirmation sound

### Implementation phasing recommendation

- **Sprint 1 (~1 week)**: scene scaffold + render the room + render 5 crew at alcoves + TALK prompt + dialog dispatch
- **Sprint 2 (~1 week)**: notification badges + side-quest goalpost trigger wiring + bond-object conditional rendering
- **Sprint 3 (post-MVP)**: ambient banter system; Steward's bunk Bio-Archive narrative-mode; per-encounter banter variation

### Status

- ✅ PROCESSED 2026-05-17 — `src/scz/scenes/common_room.py` (949 LOC); 5 named-crew alcoves + Steward's bunk + generic alcove + bond-objects shelf + notification badges + post-fall mood shift + milestone-artifact shelf. Bond objects registered in `src/scz/content/crew_bond_objects.py`. Council scene-wiring puts Common Room into the StationScene menu. Walks: `walk_common_room` (8/8), `walk_common_room_bunk` (5/5). Sprint-3 items (ambient banter system, per-encounter variation) belong to the separate Combat+Crew banter dispatch (line 247) and the Halia banter dispatch (line 151).

---

## 2026-05-17 — Forward, the Thinn Rebel: alternative weapons officer (slot mutual-exclusion mechanic)

**Aaron's brief**: *"make one of our crew one of the Thinn, our weapons officer. Lots of 2D-related jokes to plumb here."*

**Lore source**: `references/lore/crew-recruitment-quests.md` §2a (Forward — Thinn Rebel) + `references/lore/species-the-thinn.md` (Canon Note on Forward). Recruitment quest: `crew_weapons_officer_thinn` (~8 rows in `tools/quest_inventory.csv`). Side-quest: `crew_weapons_officer_thinn_side_quest` (~10 rows).

### Key implementation requirement — slot mutual-exclusion

Forward and Bren-Vor Telcas occupy the **same crew slot** (`crew_weapons_officer`). The player can recruit ONE but not BOTH. Implementation contract:

- Forward's recruitment hook fires only when `visited_spire=True AND NOT recruited_weapons_officer` (slot empty)
- Bren-Vor's recruitment hook fires only when `has_distress_beacon=True AND NOT recruited_weapons_officer` (slot empty)
- On either being recruited: set `recruited_weapons_officer=True` + the appropriate type-flag (`recruited_weapons_officer_thinn=True` OR Bren-Vor's existing recruitment)
- The OTHER recruitment hook deactivates from that point forward (the Steward cannot subsequently recruit the alternative)

**Suggested implementation**: extend the existing recruitment-quest gating logic with a single check `slot_already_filled(role)` that prevents alternative hooks from surfacing once a slot is taken.

### Forward-specific implementation tasks

- **DialogCharacter factory**: `forward_thinn_rebel()` in `src/scz/dialog/characters.py`. Carries `# TODO_AVATAR: Forward, Thinn Rebel (forward-facing, not edge-on)` for Image-chat pickup
- **New crew Module**: `CREW_WEAPONS_OFFICER_THINN` — pre-quest variant with deltas slightly different from Bren-Vor's (per lore doc — higher accuracy and a unique `crew_morale_quirk: +0.5` for the "crew finds Forward unintentionally hilarious" baseline)
- **Side-quest Module**: `CREW_WEAPONS_OFFICER_THINN_PROMOTED` — post-quest variant with retained pre-quest deltas PLUS:
  - **Perpendicular Aim** active ability — once per fight, predictive targeting (95% accuracy on next shot regardless of enemy maneuvers); visual: faint chromatic flash across Forward's body as he aims
  - **2D Witness** passive — 3% damage reduction from forward attacks; canonical *"I have an aim and I have an edge-on. I choose the aim. But I still have the edge-on if I want it."*
- **Optional flag `forward_collective_aboard=True`** (set in side-quest confrontation-branch favorable outcome): two additional Thinn (We-Who-Watch-The-Far-Slope, We-Who-Watch-The-Lower-Bench) ride aboard for the rest of the slice. They share Forward's alcove. They argue *constantly* about the doctrine. Suggested implementation: a small "tagalong" mechanic where the alcove renders 3 Thinn instead of 1; banter content extends to include 3-way Thinn argument

### Common Room alcove handling

The weapons-officer alcove (starboard-mid corner) renders DIFFERENTLY based on which weapons officer is recruited:

- If `recruited_weapons_officer_thinn=True`: render Forward's alcove (iridescent-mineral wall-panel + vertical resting-rack bunk + his specific bond-objects + the optional 2-Thinn diaspora if `forward_collective_aboard=True`)
- If `recruited_weapons_officer=True AND NOT recruited_weapons_officer_thinn`: render Bren-Vor's alcove (per existing crew-common-room.md canon)
- If neither: render the empty alcove

The Common Room scene needs to conditionally swap alcove content based on these flags — same screen-region, different assets.

### Forward's canonical "perpendicular reality" lore tag

Forward claims to perceive a *fourth dimension* via his 2D nature. Furling xenophysiologists have measured this and concluded he *does* perceive something but the something *may not be a fourth dimension* (more likely a confused 2D-cognition-modeling-3D-space artifact). Forward does not know the difference. **The Perpendicular Aim ability works in-game regardless of which interpretation is correct.** This canonical ambiguity should be preserved — neither Design nor Image nor Audio should *resolve* whether Forward really perceives a 4th dimension or not. The mystery is canonical.

### Side-quest goalpost: confrontation has cross-canon implications

The favorable confrontation branch sets `forward_collective_aboard=True` AND `standing:thinn+3`. The Thinn species's status changes to **MixedEliminatedMigrated** — a tiny 3-Thinn diaspora makes it to Andromeda. This is canonically the FIRST Thinn-species split (the troupe stays; Forward + 2 leave). Future Andromeda-arrival epilogue content should acknowledge this if the flag is set.

### Cross-chat dispatches

- **Image chat** (`HANDOFF_image_chat.md`) — entry posted: Forward portrait (canonically forward-facing — the only Thinn ever to be drawn this way), his Common Room alcove variant, his 5+ bond-objects, the 2 diaspora-Thinn sprites for the confrontation branch, the Spire troupe encounter cinematic backdrop
- **Audio chat** (`HANDOFF_audio_chat.md`) — entry posted: Forward's voice profile (Thinn base + singular pronouns + sharper-from-isolation edge + sincere-not-funny delivery doctrine — the joke is in NOT signaling the joke); canonical chromatic-ripple grief sound; the 2 diaspora-Thinn share Forward's voice base but use standard collective-plural pronouns (per their preserved doctrine)

### Status

- ☐ Open as of 2026-05-17 — pairs with the existing crew-recruitment-quests + side-quest implementation work

---

## 2026-05-17 — Crew side-quests + pre/post-quest bonus mechanic (5 quests authored)

**Sources**: `references/lore/crew-recruitment-quests.md` (appended new "Backstories, Personalities, Side-Quests & Bonus Progression" section, ~2000 words of new content). Quests authored: `crew_pilot_side_quest`, `crew_weapons_officer_side_quest`, `crew_engineer_side_quest`, `crew_medic_side_quest`, `crew_navigator_side_quest` — ~50 rows total in `tools/quest_inventory.csv`.

### Design implementation request — the post-quest bonus mechanic

This is the *single largest Design-side change* implied by this work. Lore has authored:
- A **pre-quest bonus** per crew (the current canonical stat-deltas they grant immediately on recruitment)
- A **post-quest bonus** per crew that activates *after the favorable side-quest resolution* — typically the pre-quest deltas RETAINED plus a unique **active ability** + an extra **passive stat-delta**

**Design's framework decision** — pick one:
- **(a) Module variants**: introduce `CREW_<ROLE>_PROMOTED` modules with the post-quest deltas; the side-quest's favorable outcome side-effect swaps the pre-quest module out for the promoted variant in `game.uninstalled_modules`. *Simpler; consistent with existing convention.* Lore-authored quest CSV uses this naming convention (`CREW_PILOT_PROMOTED`, etc.).
- **(b) Promoted-flag**: extend `Module` with `promoted_deltas: dict[str, float]` and `promoted_flag: str | None`; when the flag is set in `game.flags`, the module's effective deltas become `deltas + promoted_deltas`. *More elegant; requires Module dataclass extension.*
- **(c) Scene-layer filter**: keep the modules as-is but apply post-quest bonuses in the `Game.effective_stat()` aggregation based on flag-checks. *Most flexible; no module-system change.*

Recommended: **(a) Module variants** to match the existing UNLOCKED_BY pattern from the recruitment quests.

### New "crew special ability" framework

The post-quest bonuses introduce **5 new active abilities** with various cooldown semantics:
- **Mraka — Evasive Burst**: once per combat fight, instant ~200u directional burst with brief invuln frames during the burst
- **Bren-Vor — Precision Focus**: once per fight, next shot is 3× damage but 1/3 fire rate; visual effect slows time during the aim window
- **Yelena — Field Overhaul**: once per slice, full repair AND bypass the Mh-Lai install-gate for ONE module
- **Mira-Rou — Bio-Signature Dampening**: -50% biological-cognition-signature for 30 seconds; useful in late-slice Others-approach scenes
- **Tarven — Deep Archive Scan**: once per slice, reveal all hidden encounters/anomalies on the starmap

These need a **unified crew-ability mechanic** — cooldown framework (per-fight vs per-slice), trigger UI (controller button for combat abilities, menu option for non-combat), state tracking. Single-largest Design-side change implied by this work.

### New post-quest passive stat-deltas (suggested values; Design refines)

| Crew | Promoted Module ID | Passive (suggested deltas) |
|---|---|---|
| Mraka | `CREW_PILOT_PROMOTED` | `hyperspace_fuel_efficiency: 1.20` |
| Bren-Vor | `CREW_WEAPONS_OFFICER_PROMOTED` | `combat_persuader_standing_per_spare: 1.0` (per-combat hook) |
| Yelena | `CREW_ENGINEER_PROMOTED` | `damage_reduction: 0.10` (10% less damage from any source) |
| Mira-Rou | `CREW_MEDIC_PROMOTED` | `tractor_radius_bonus_extra: 0.20` (stacks with Mantle-Resonance) |
| Tarven | `CREW_NAVIGATOR_PROMOTED` | `dialog_context_depth: 1.30` |

### Special-case modules introduced by these quests

- **`HULL_RESONANCE_DAMPENER`** (Yelena's Last Hull quest) — a unique hull-resonance-dampener module Yelena's father designed and she completed. Permanent install on the Steward's ship. Suggested deltas: `hull_max: 30, shield_recharge_rate: 1.1`. Special: cannot be uninstalled (canonical: it's part of the family bond).
- **`CREW_SEVRETH_CHILD`** (Mira-Rou's allow-emergence branch) — a tiny biot-class sentient companion in the medbay. Functions as a passive crew-style stat-bumper (suggested: `crew_morale: 1.1`) AND introduces a new dialog-character-on-the-bridge mechanic — Sevreth's Child can comment on Mycon-related quests and adds per-encounter morale variability.
- **`CREW_NAVIGATOR_PROMOTED_SECRET`** (Tarven's keep-secret branch) — alternate promoted variant with `dialog_context_depth: 1.5` (extra bonus from the secret) instead of the standard 1.3. Either-or with `CREW_NAVIGATOR_PROMOTED`.

### Cross-quest intersection logic

Lore has authored crew-cross-bond beats that fire when multiple crew side-quests resolve favorably:
- **Mraka + Yelena**: if both side-quests reach favorable resolution AND Yelena is aboard during Mraka's Last Race, the `c_repair_with_yelena` branch triggers; sets `flag:mraka_yelena_bonded=True` for ongoing morale bonus
- **Tarven + Mraka**: if Tarven's quest reveals Iren-Vor was an Olwen-Veth (canonical) AND Mraka is aboard, additional dialog beats unlock revealing the prior-Steward and the lost-family Mraka mourned were cousins
- **Mira-Rou + Bren-Vor**: if both have Cleanser-aligned decision points open, additional cross-character dialog content unlocks (they judge the Steward separately by different ethical lenses)

Design wires the cross-flag-check; content is in CSV + lore doc.

### Cross-chat dispatches that drop out

- **Image** HANDOFF needs portraits for: **Soren Kel-Var** (Mraka's rival), **Karol-Vere Belt-Tar** (Cleanser officer), **Mev-Tar Lwen-Tar** (Yelena's mother), the *deceased Iren-Vor* (Tarven's investigation; portrait shown only in flashback/cache-recording), **Sevreth's Child** (tiny biot companion if Mira-Rou allows emergence)
- **Audio** HANDOFF needs voice profiles for the same 4 NPCs + Sevreth's Child's chemical-signaling sound design
- **Testing** HANDOFF needs walk-tests for 5 new side-quests + their cross-quest intersection beats

**Status**: ☐ Open

---

## 2026-05-17 — Two NEW Precursor-faction species — Kovellim + Karavem

**Sources**: `species-the-kovellim.md`, `species-the-karavem.md`. Quests authored: `kovellim_crossing_trade` (10 rows) + `karavem_song_exchange` (8 rows) — both in `tools/quest_inventory.csv` (now at 249 rows total).

### Kovellim implementation

- **Character factory**: `ovala_eight_crossings()` in `src/scz/dialog/characters.py`. `# TODO_AVATAR: Ovala-Eight-Crossings (elder, eight knot-scars, deep cycle-cloak)`. Long pauses canonical in dialog rendering — when Ovala "considers," the dialog FSM should support a *deliberate text-rendering delay* or visual pause beat between phrases.
- **Ship**: Kovellim Crossing-Frigate — `KOVELLIM_CROSSING_FRIGATE` ShipClass — migration-class heavy vessel; Knot-Resonance Beam primary; **Cycle-Fold** special (dimensional-blink within 800 units). Stats per lore doc.
- **Three NEW modules** unlocked via quest:
  - `KOVELLIM_FOLDER_COMPASS` — sensor slot; reveals hyperspace dimensional-stable corridors (deltas TBD, suggest `dimensional_corridor_visibility: 1.0`)
  - `KOVELLIM_CROSSING_BRACE` — hull slot; hyperspace-stress hull-integrity bonus (deltas TBD, suggest `hyperspace_hull_resistance: 0.3`)
  - `KOVELLIM_CYCLE_MEMORY` — passive (no slot? or sensor?); surfaces "this has been tried before" annotations in dialog choices (deltas TBD, suggest `dialog_cycle_context: 1.0` or similar — Lore-chat happy to define the semantics if Design surfaces the framework)
- **Quest contract**: `kovellim_crossing_trade` — branches full-trade (3 modules) / partial-trade (1 module) / listen-only (lore + archive entries, no modules) / Cleanser-pressure-rejected.

### Karavem implementation

- **Character factory**: `veled_of_the_canyon_wall()` — the elder conductor. The Karavem speak in **MUSIC, not words**. The DialogCharacter renderer needs to handle this novel format: each NPC line should be authored as **prose-with-musical-annotation** (per the CSV); the runtime renderer can either (a) render the bracketed annotations as italic stage-direction, (b) trigger audio cues per annotation marker, or (c) both. The CSV's `npc_line` field already contains the bracketed musical annotations Lore authored; Design-chat decides the rendering.
- **Ship**: Karavem Aria-Skiff — `KARAVEM_ARIA_SKIFF` ShipClass — light fast bird-of-prey; Harmonic Lance primary; **Counterpoint Stitch** special (reverses enemy thrust vector for 2 seconds; trap-pursuers effect).
- **Two NEW modules** unlocked via quest:
  - `KARAVEM_RESONANCE_MODULE` — sensor slot (or new "field" slot?); +15% hyperspace fuel efficiency + audio cue warning of dimensional turbulence. (Quest branch: standard song-exchange)
  - `KARAVEM_RESONANCE_MODULE_DELUXE` — same as above + bonus `dialog_context_depth: 1.2` (the song-thinking carries into conversation). (Quest branch: commissioned masterwork)
- **Quest contract**: `karavem_song_exchange` — branches share-furling-song / masterwork / decline / Cleanser-pressure-with-strategic-silence-counterproposal.

**Cross-chat dispatches**:
- **Image** HANDOFF entry posted same date — portraits + canyon-city + Eight-Knot Station + ship sprites
- **Audio** HANDOFF entry updated — Kovellim deep-slow-cyclical voice + Karavem music-as-language voice with the canonical emotional-valence-reversal (major=sad/formal, minor=joyful/exploratory)
- **Testing** entry below — `walk_kovellim` + `walk_karavem` + `walk_kovellim_cleanser_retract` + `walk_karavem_masterwork`

**Status**: ☐ Open

---

## 2026-05-17 — Three new species — DialogCharacter factories + quests + ships

**Sources**: `references/lore/species-the-stelloth.md`, `species-the-selvenne.md`, `species-the-mrokon.md`. All three quests authored in `tools/quest_inventory.csv` (quest_ids: `stelloth_artifact_trade`, `selvenne_memory_archive`, `mrokon_hammer`).

### Stelloth (three-body chord-NPC; novel rendering challenge)

- **Novel dialog rendering requirement**: each Stelloth "individual" is THREE bodies with synchronized-offset voice timing. The DialogCharacter needs to handle a **three-voice line** — Speaker primary, Witness click-emphasis (offset early), Counter bass-affirmation (offset late). Consider extending the dialog FSM to support multi-voice line composition (each line is a tuple of three sub-lines with timing offsets) OR rendering as a single line with inline markup that the renderer parses.
- **Character factory**: `tarvel_three_voices()` in `src/scz/dialog/characters.py`. `# TODO_AVATAR: Tarvel-Three-Voices (chord)` for Image-chat pickup.
- **Ship**: Three-Voice Arc — `STELLOTH_THREE_VOICE_ARC` ShipClass — trader vessel; Contract-Resonance Lance primary; Chord-Witness Scanner special (passive reveal-enemy-stats). Stats per `species-the-stelloth.md`.
- **Quest contract**: `stelloth_artifact_trade` (13 rows) — branches honest-trade / withhold-Witness-caught / Cleanser-pressure-rejected.
- **Special mechanic**: the *withhold-caught* branch requires the system to know what the Steward has in cargo (e.g., `has_taalo_shield_fragment`) and surface a withhold-choice only if there's a hidden artifact. The Witness branch is then triggered by this check.

### Selvenne (planet-scale coral chorus; memory-playback cinematic system)

- **Major new cinematic system needed**: **memory-playback frames**. When a Selvenne polyp transmits a memory to the Steward, the scene transitions to a cinematic showing the memory in first-person POV. Could reuse Distress Beacon cinematic infrastructure if/when wired; otherwise net-new.
- **Character factory**: `choir_of_the_east_reef()` — collective dialog character; the "speaker" is the reef-chorus.
- **No ship**: the Selvenne are sessile coral; transported by Furling migration vessels. No melee ship.
- **Quest contract**: `selvenne_memory_archive` (12 rows) — branches contribute-faithfully / withhold / Cleanser-pressure-via-memory-playback.
- **Special mechanic — qualia transfer**: when the Steward "touches a polyp," the dialog FSM should transition to a memory-replay state. The state's content is a *narrative description* of the memory (already authored in the CSV; Design renders it with the cinematic visual styling per Image HANDOFF).
- **Echo Crystal artifact**: post-quest, the Steward carries an Echo Crystal that lets them re-trigger any memory the reef has shared. Suggested implementation: a new flag-set + a callable from the inventory/Bio-Archive scene.

### Mrokon (warrior-puppet operators)

- **Character factory**: `vrek_the_eighth_body()` — the puppet speaks for the Operator. Note: occasionally the puppet *dies mid-conversation* (a canonical Mrokon quirk — environmental damage, planned puppet-rotation, etc.) and a *different puppet* arrives within minutes carrying the same Operator identity. The dialog FSM should support this — preserve conversation-state across puppet-swap; "Vrek-The-Ninth-Body" picks up where Vrek-The-Eighth-Body left off.
- **Ship**: Mrokon Hammer-Ship — `MROKON_HAMMER_SHIP` ShipClass — heavy battleship; Kinetic Cannon primary; **Hammer-Round single-use special** (devastating one-shot, ship is down 20% effective combat capability for rest of fight).
- **Operator bunker visit**: rare scene, only after `support-the-Hammer` branch is fully committed. Could be a special interior-dialog scene with Vrek the Operator (NOT the puppet); the Steward sees the deep-link interface; intimate.
- **Quest contract**: `mrokon_hammer` (15 rows) — branches support / partial-evac / cleanser-resistance-or-combat / witness-only.
- **Cross-canon implementation**: the `others_marked_permanently` flag from this quest's full-support branch should be readable by any future SC2-canon-checking system (e.g., a slice-epilogue scene reading "the Others' Vessels carry visible marking" if the flag is set).

**Cross-chat dispatches that drop out**:
- **Image** HANDOFF entry posted same date — portraits + ship sprites + Mrokon's Stand surface + the Hammer-Of-Refusal cutscene + the Stelloth super-giant trading post + the Selvenne Brain-Coral Sanctum
- **Audio** HANDOFF entry updated — three voice profiles added (Stelloth three-voice chord, Selvenne chorus, Mrokon puppet+operator)
- **Testing** — see new HANDOFF_testing_chat.md entries for `walk_stelloth`, `walk_selvenne`, `walk_mrokon`

**Status**: ☐ Open

---

## 2026-05-17 — Expose the Others' Vessel in Super-Melee (testing-only)

**Aaron's framing (2026-05-17)**: *"Fighting an Others ship should be quite difficult. Let's expose the Others ship in super-melee for testing."*

**Canon context**: Per `memory/project_ship_roster.md`, the Others' Vessel is **NOT in super-melee normally** — it's acquired through the special Hijack quest in the campaign. Decursion is its signature weapon. This dispatch is for *testing exposure only*, not a canon change to acquisition.

**Implementation request**:

- Register an `OTHERS_VESSEL` (or similar id) `ShipClass` in `src/scz/content/ships.py` (or wherever the ship registry lives) with the canonical Others combat profile:
  - **Difficulty: high** — should be *clearly stronger than any single Furling/Homesteader ship*. The Others should feel like an apex predator in super-melee.
  - **Decursion** as the special weapon (signature mechanic — temporally displaces / rewinds target back N seconds; see related canon in `memory/project_androsynth.md` for the decursion canon they used to displace Coel Tessar's ship)
  - Hull / shield / speed / damage tuned to roughly **2× Furling Scout effective combat power**. Players should be able to win 1v1 only with skilled play and Time Drive abuse.
- Add the Others' Vessel to the **super-melee ship-picker UI** with a *testing-only* flag (`TESTING_ONLY = True` on the ShipClass, or a `super_melee_visible_when` predicate that surfaces it only when `DEBUG=True` or when a console toggle is set). Aaron's intent is *testing*, not "always available in super-melee."
- The **canonical campaign acquisition path** (Hijack quest) remains the only way to get the Others' Vessel during normal play. The testing exposure is parallel.

**Cross-chat dispatches that drop out**:
- **Image chat**: needs an Others' Vessel exterior sprite + Decursion weapon visual. Note: Others-visuals canon is *negative-black distortion, non-Euclidean*; the Vessel sprite should follow this aesthetic. Open a HANDOFF_image_chat.md entry when ready.
- **Audio chat**: Decursion needs an audio signature distinct from any other weapon — *temporally-recursive* feeling. Open HANDOFF_audio_chat.md entry when Design starts.
- **Testing chat**: a `walk_super_melee_others_vs_furling` walk-test would be valuable to verify the Vessel is selectable + the fight is *hard but winnable*. Open HANDOFF_testing_chat.md entry.

**Status**: ☐ Open

---

## 2026-05-17 — Lemmkin species — DialogCharacter factory + ship + science-trade module

**Source**: `references/lore/species-the-lemmkin.md` (full species sheet authored 2026-05-17, replacing the CURIOUS placeholder row).

**Implementation tasks**:

- `src/scz/dialog/characters.py` — new factory: `brisk_ever_onward()` for the Lemmkin elder + supporting factories for `snip()`, `pip()`, `trill()`, etc. as the quest's branches require. Each carries `# TODO_AVATAR: <NPC name>` for Image chat.
- **Quest wiring**: `lemmkin_curiosity` quest in `tools/quest_inventory.csv` — full FSM specification (~22 rows). Side-effects include the new `LEMMKIN_PATTERN_DATABASE` sensor module.
- `src/scz/content/modules.py` — add a new `LEMMKIN_PATTERN_DATABASE` module. Suggested:
  - slot: `sensor`
  - tier: 0 (quest-reward — granted via science-trade)
  - cost: 0
  - deltas: `{"pattern_recognition": 1.5, "dialog_context_depth": 1.2}` or similar — should be a *uniquely Lemmkin* effect, tied to their eclectic-research aesthetic. (Lore can refine if needed; flag back via `HANDOFF_lore_chat.md`.)
  - description: in-fiction Lemmkin-voice; references the science-trade with Snip
- **Lemmkin Skitter ShipClass** in `src/scz/content/ships.py` — small fast glass cannon with Burst-Scatter Probe primary + Tail-Drop 180-pivot special. Stats per the lore doc §Ship Design.
- **Whirligig system** in `src/scz/content/universe/` — Lemmkin homeworld; densely forested terrestrial world; ~6-hour day. Position TBD (Lore can pin to slice-cluster.md once Design confirms there's room).
- **Lemmkin warp-pod palette** in `src/scz/content/species_visual.py` — replace the `CURIOUS` color entry with `LEMMKIN` palette per Image-chat suggestion (bright cheerful, suggest warm orange-cream or keep sky-blue).

**Status**: ✅ PROCESSED 2026-05-17 — shipped end-to-end:
- `lemmkin_brisk_ever_onward()` factory in `dialog/characters.py` (9 states, full 4-branch quest: honor-stay / advocate-evacuation / cleanser-sabotage / science-trade-side-action)
- `LEMMKIN_PATTERN_DATABASE` module granted via science-trade branch (BIO +6 + module-in-inventory)
- Whirligig system at Beta Crucis (5499, 6669) — green dwarf tagged `LEMMKIN_WHIRLIGIG`; hand-built `whirligig_system.py` with 3-planet layout
- `_arrive_whirligig` arrival handler with dialog auto-launch
- `visit_whirligig` council mission
- `walk_lemmkin_quest` (14/14 green) walks honor-stay + science-trade end-to-end
- `LEMMKIN_SKITTER` ShipClass + warp-pod palette already existed from Combat Mechanics chat's prior pass; this dispatch picked up the dialog/quest/system content.
- Side note: species naming convention canonized in `references/lore/species-naming-conventions.md` during this session — Lemmkin names follow the inquiry/footnote-becomes-chapter pattern (*"The Many-Footed Question"*, *"The Inquiring Skitter"*).

---

## 2026-05-17 — Cleanser climax encounter follow-ups (MVP shipped, deferred items in backlog)

**Status of the encounter**: MVP shipped 2026-05-17 in this worktree. What landed:
- `cleanser_vael_souren()` dialog character — 9-state FSM (arrival → about_method → argue_persuader → negotiate_open → negotiate_one/three → agreed_delay → cooperate_confirm / refuse_confirm) per the design doc's verbatim text
- `EncounterSpec` extended with `also_flag_gate` for compound gating; `cleanser_climax_alpha` registered (gates on `met_cleanser_patrol AND heard_about_others`, retires on `met_cleanser_climax`)
- `_trigger_cleanser_climax` opens DialogScene with Vael-Souren; refuse-branch side-effect launches MeleeCombatScene with `CLEANSER_CRUISER` vs `FURLING_SCOUT` (max 60s); win→`killed_cleanser`, loss/timeout→`cleanser_defected`
- Walks: `walk_cleanser_cooperate` (9/9), `walk_cleanser_combat` (9/9)

**Deferred follow-ups** (Aaron explicitly pushed to backlog — pick up in a later round):

1. ~~**HyperspaceBroadcastOverlay** — first-hail audio-text crawl across the hyperspace HUD before the Cleanser materializes. Design doc §Encounter Flow Step 1.~~ ✅ PROCESSED 2026-05-17 — `HyperspaceBroadcast` dataclass + `scene.start_broadcast()` API in `src/scz/hyperspace/scene.py`. Cleanser climax wired (5s text crawl + pulsing banner + progress bar + sender tag "INCOMING HAIL · CLEANSER VESSEL · THE BELL OF THE QUIET LEDGER"). `walk_hyperspace_broadcast` (5/5) + Cleanser cooperate/combat walks updated for the delay.
2. **Pursuit-if-fled path** — if the player flees Step 2, Cleanser pursues; if caught → forced dialog with STAND_AGAINST locked out; if outrun → Cleanser warps to Mh-Lai and waits. Design doc §Step 4.
3. **Time-Drive-aware re-arrival dialog branch** — on combat loss, when Time Drive auto-rewinds, Vael-Souren's first line acknowledges the rewind: *"You return. I felt you slip. The Quiet stutters when one of us refuses to die properly..."* — requires Time Drive integration with combat scene's on_finish path. Design doc §Step 7 loser branch.
4. **CinematicScene** — off-screen Cleansing for the Cooperate / Negotiate-fail branches (Slylandro/Mycon planet fades, voiceover-text, timed transitions). Shared infrastructure also needed by Beat-4 Distress Beacon replay. Design doc §Step 5 + Scene Implementation §3.
5. **Council faction-standing system** — Persuader / Cleanser / Defender tracks per the design doc's branch outcome table. Currently the encounter just sets flags; standings are noted in lore but not wired into any system. Required before the cruel-decline branch of Mraka's recruitment can fire, and before the species-decision flag gating (`slylandro_decision_pending`, etc.) can replace the placeholder `met_cleanser_patrol` gate on the climax.
6. **Species-specific terminal status on cooperate** — currently sets a generic `cleanser_targets_pending` flag because Slylandro/Mycon decision flags aren't wired yet. When those land, the cooperate branch should set `<species>_terminal_status = "Eliminated"` based on which decision was open at trigger time.

**Source of truth**: `references/lore/cleanser-encounter-design.md` (full 7-step spec, unchanged).

**Status**: ☐ Backlog — pick up after the species-decision flag system + faction-standing system are designed.

---

## 2026-05-17 — Quest dialog FSMs from `tools/quest_inventory.csv` (15 quests authored)

**Source**: Lore-chat-authored quest spreadsheet at `tools/quest_inventory.csv` (built from `tools/build_quest_inventory.py`). 152 rows across 15 quests — every state, every choice, every prereq, every side-effect, every terminal Win-condition status.

**Quests in the spreadsheet** (column `quest_id`):
- **Species quests** (10): `slylandro_cloak`, `proto_uplift`, `mycon_whisper`, `arilou_sage`, `androsynth_beacon`, `mmrnmhrm_archive`, `chenjesu_resonance`, `taalo_shield`, `burv_caster`, `utwig_veils`
- **Crew recruitment** (5): `crew_pilot`, `crew_weapons_officer`, `crew_engineer`, `crew_medic`, `crew_navigator`

**Implementation pattern** — for each quest:
1. Read all rows for the quest_id from `quest_inventory.csv`.
2. Build a `DialogCharacter` (or `Quest` framework — Design's call) in `src/scz/dialog/characters.py` — one factory function per NPC.
3. For each unique `state_id`, create a state node with the `npc_speaker` + `npc_line` text.
4. For each row with a non-empty `choice_id`, add a choice from that state with the `choice_label`, the `next_state` transition, and the `prereqs` gate.
5. For each row with a non-empty `terminal_status`, mark that state as terminal and apply the `side_effects` on enter.
6. Side-effect format (Lore-authored, Design-parsed):
   - `flag:<name>=<value>` — set `game.flags[name] = value` (parse `True` / `False` / int / str)
   - `module:<MODULE_ID>` — add the named module from `MODULES` to `game.uninstalled_modules`
   - `standing:<faction><±N>` — adjust `game.faction_standing[faction]` by N (e.g. `persuader+2`, `cleanser-3`)
   - `terminal:<Status>` — set the species' canonical Win-condition status; values match `terminal_status` column
   - `!flag:<name>=<value>` (in prereqs only) — require flag NOT to equal value
7. The arilou_sage quest is already partially implemented in code — use the CSV as a parity check and to surface any branches not yet wired.

**Cross-chat dispatches that drop out of this work**:
- **Image chat** — every quest introduces 1-N new NPCs. Each character factory should carry a `# TODO_AVATAR: <NPC name>` marker for Image-chat pickup. NPC names are in the `npc_speaker` column of the CSV.
- **Audio chat** — same NPC list drives voice-profile authoring (already partially tracked in `HANDOFF_audio_chat.md` species-voices backlog).
- **Testing chat** — every terminal-status branch should have a walk-test. `HANDOFF_testing_chat.md` should be appended with per-quest walk targets once Design lands the FSM.

**Spreadsheet maintenance contract**:
- The CSV is **regenerated** from `build_quest_inventory.py`; never hand-edit `quest_inventory.csv` directly.
- **Lore chat owns** the build script (analogous to species spreadsheet). Design-chat-flagged content questions go via `HANDOFF_lore_chat.md`.
- When Design implements a quest, the quest's row in the spreadsheet should be considered the contract — branching, side effects, terminal statuses are Lore-canonical. Implementation should match. Mismatches are bugs.

**Status**: ⏳ IN-PROGRESS as of 2026-05-17.

| Quest | Status | Where |
|---|---|---|
| `arilou_sage`         | ✅ shipped | `arilou_sage()` factory |
| `androsynth_beacon`   | ✅ shipped | `coel_tessar()` factory + Beat 4 |
| `slylandro_cloak`     | ✅ shipped | `slylandro_witness()` factory + `walk_slylandro_cloak` |
| `mmrnmhrm_archive`    | ✅ shipped | `mmrnmhrm_sentinel()` factory (this session) + `walk_mmrnmhrm_quest` |
| `crew_pilot` (Mraka)  | ✅ shipped | `mraka_yenn_sa()` factory + `walk_recruit_mraka` |
| `proto_uplift`        | ⏳ partial | Dnyarri-survey-commander handles Beta Orionis variant; other proto-species are observation-only |
| `mycon_whisper`       | ☐ open | `_arrive_mycon_hive` data-layer only; Deep Child dialog not wired |
| `chenjesu_resonance`  | ☐ open | `_arrive_chenjesu` data-layer only |
| `taalo_shield`        | ☐ open | no factory |
| `burv_caster`         | ☐ open | no factory |
| `utwig_veils`         | ☐ open | no factory |
| `crew_weapons_officer` | ☐ open | stub only (`bren_vor_telcas`) |
| `crew_engineer`       | ☐ open | stub only (`yelena_lwen_tar`) |
| `crew_medic`          | ☐ open | stub only (`mira_rou_halve_tel`) |
| `crew_navigator`      | ☐ open | stub only (`tarven_olwen_sa`) |

**Remaining work**: 5 species FSMs (Mycon Whisper, Chenjesu Resonance, Taalo Shield, Burv Caster, Utwig Veils) + 4 crew FSMs (weapons/engineer/medic/navigator) + Forward as alternative-weapons. Each pattern follows Mmrnmhrm precedent (homeworld arrival → dialog FSM → terminal branches → walk test).

---

## 2026-05-17 — Bio-Archive scene + entry catalog (Beat 5 closure)

**Source**: Beat 5 design plan + `references/lore/station-screens-design.md`. Closes the station-hub trilogy (Trade + Customization + Archive).

**Implementation**:
- `src/scz/content/archive_entries.py` (NEW) — `ArchiveEntry` dataclass + `ARCHIVE_ENTRIES: list[ArchiveEntry]` (20 entries across 4 categories per the design doc) + `visible_entries(game) -> dict[str, list[ArchiveEntry]]` flag-gated categorizer
- `src/scz/station/archive.py` (NEW) — `BioArchiveScene` with three-region layout (categories → entries → detail pane), standard menu nav, cinematic-replay path for entries with `cinematic_id is not None`
- `src/scz/station/scene.py` (EDIT) — add `("Bio-Archive", "archive")` action with visibility gated on any artifact flag
- Long-form descriptions in Furling Steward voice — Lore chat will author once Design surfaces the entry schema. Until then, stub `long_desc` placeholders are acceptable.
- Dispatches: Testing chat already has `walk_bio_archive` queued in its inbox.

**Status**: ✅ PROCESSED 2026-05-17 — `src/scz/content/archive_entries.py` (ArchiveEntry dataclass + 20+ entries across 4 categories incl. proto-species, Mmrnmhrm sentinel/excerpt, Dnyarri recommendation, Fall of Mh-Lai); `src/scz/station/archive.py` (368 LOC, three-region layout); StationScene wiring with flag-gated visibility. Walk `walk_bio_archive` 5/5 green.

---

## 2026-05-17 — Crew recruitment quest FSMs + flag-gating

**Source**: `references/lore/crew-recruitment-quests.md` (5 quests, one per crew NPC, full content authored).

**Implementation**:
- `src/scz/dialog/characters.py` — 5 new character factories: `mraka_yenn_sa()`, `bren_vor_telcas()`, `yelena_lwen_tar()`, `mira_rou_halve_tel()`, `tarven_olwen_sa()`. Each carries `# TODO_AVATAR: <NPC name>` for Image-chat pickup.
- FSM terminal-state side-effects: set `recruited_<role>` flag + add `crew_<role>` module to `game.uninstalled_modules`
- Hook surfacing logic in `StationScene` / `CustomizationScene` / `CoelTessarScene` per each quest's prerequisite block
- Module gate: tier-1+ crew modules in `src/scz/content/modules.py` are `locked=True` with `UNLOCKED_BY: recruited_<role>` comment markers. Design-chat to either extend `Module` with `unlock_flag: str | None` (and update `purchasable_modules()` to honor it) OR filter at the scene layer based on `game.flags`. Either approach acceptable.
- Optional: Mraka's Drifter's Circuit minigame (Step 2 of her quest). If the minigame is too much scope, drop it — Mraka observes the Furlmart shakedown and approaches in the lounge.
- Dispatches: Testing chat has `walk_recruit_<role>` queued for each of the 5; Image chat will need `# TODO_AVATAR` pickup for the 5 portraits.

**Status**: ⏳ IN-PROGRESS as of 2026-05-17 — **Mraka shipped fully**: `mraka_yenn_sa()` factory + recruit-pilot quest flow + `_recruit_mraka` side-effect + `walk_recruit_mraka` (11/11). The other four (`bren_vor_telcas`, `yelena_lwen_tar`, `mira_rou_halve_tel`, `tarven_olwen_sa`) are scaffolded as `_stub_crew_dialog`-based placeholders — they exist in `characters.py` and Common Room reads them, but their full recruitment FSMs from the lore doc are not yet authored. Forward (Thinn rebel weapons officer, mutually exclusive with Bren-Vor) is also pending — see separate dispatch above. **Open work**: 4 full crew recruitment FSMs + Forward + Mh-Lai install gate for tier-1+ crew modules.

---

## 2026-05-17 — Economy: Schematic Vault scene + Mh-Lai install gate + Melnorme niche narrowing

**Source**: `references/lore/economy-and-trade-loops.md` (full canon authored 2026-05-17).

**Implementation**:
- `src/scz/content/schematics.py` (NEW) — `Schematic` dataclass + `SCHEMATICS` registry. Initial catalog suggestions in the canon doc (`schematic_furling_coil_lance`, `schematic_dimensional_armor`, `schematic_pulse_cannon`, etc. — 15 entries).
- `Game.schematics: set[str]` (or `list[str]` if order matters) — persists across saves.
- `src/scz/station/schematic_vault.py` (NEW) — Mh-Lai sub-screen; catalog of unspent schematics; "use" action consumes one and unlocks its target mod in `MODULES` catalog visibility.
- `Module.unlock_schematic: str | None = None` — new field; filter `purchasable_modules()` to hide unlock_schematic-required mods until the corresponding schematic has been consumed.
- **Mh-Lai install gate**: `ShipCustomizationScene.install_module` checks `game.location == "mh_lai_station"` for tier-1+ modules. Tier-0 quest-reward modules pass through (no gate). Crew modules pass through (they're installed at Mh-Lai by definition since they're recruited there).
- **Melnorme catalog narrowing** — resolve `MELNORME_PLASMA_LANCE` contradiction (Melnorme sell sensors + lander-hardening only per new canon). Recommended path: schematic-convert. Replace the direct module sale with a Melnorme-sold `schematic_furling_coil_lance` (BIO-cargo cost) that consumes at Mh-Lai to unlock a Mh-Lai-buyable weapon mod with the same deltas. Alternative: retire the entry entirely.
- **Lander-hardening sub-system**: new module category needed. Suggested structure — a new `lander_armor` slot (parallel to `sensor`), with starter modules `MELNORME_LANDER_ABLATIVE_HULL`, `MELNORME_LANDER_HAZARD_SHIELD`, `MELNORME_LANDER_TRACTOR_FOCUSER`. All tier-1+, BIO-cargo cost, field-installable.
- Dispatches: Testing chat has `walk_schematic_vault`, `walk_install_gate_remote`, `walk_install_gate_home`, `walk_tier_0_exempt` queued.

**Status**: ⏳ IN-PROGRESS as of 2026-05-18 — **Schematic Vault core mechanic shipped end-to-end**:
- `src/scz/content/schematics.py` — `Schematic` dataclass + `SCHEMATICS` registry (5 starter entries: Furling Coil Lance, Dimensional Armor, Pulse Cannon, Mmrnmhrm Reinforced Plating, Arilou Phase Dampener — each with rarity + source_origin lore blurb)
- `Game.schematics: set[str]` (held) + `Game.consumed_schematics: set[str]` (converted) — both persist across saves
- `Module.unlock_schematic: str | None = None` — new field; `purchasable_modules()` filters modules whose `unlock_schematic` isn't in `game.consumed_schematics`
- 5 new schematic-gated Modules added to `MODULES` (paired with the 5 schematics 1:1)
- `src/scz/station/schematic_vault.py` — `SchematicVaultScene` with held-schematics list + rarity-colored entries + source-origin detail pane + "Press A to convert" action
- StationScene wiring: "Schematic Vault" menu entry gated on `has_held(game)`; appended to ACTIONS so existing index-based walks unaffected
- `walk_schematic_vault` (5/5 green) — seeds a held schematic, opens Station → Vault, converts, verifies `consumed_schematics` contains the id, returns to Station
- New harness primitive `expect_attr_contains(attr, member)` for generic set/list membership assertions on game state

**Still open from this dispatch**:
- **Mh-Lai install gate** — `ShipCustomizationScene.install_module` location check for tier-1+ modules (separate concern; needs a `game.location` concept which doesn't yet exist as a first-class field)
- **Melnorme catalog narrowing** — convert `MELNORME_PLASMA_LANCE` direct-sale to a Melnorme-sold `schematic_furling_coil_lance` (BIO-cargo cost); requires Melnorme dialog FSM extension
- **Lander-hardening sub-system** — new `lander_armor` slot + 3 starter modules; orthogonal to the Vault loop, can ship in a separate dispatch

---

## 2026-05-17 — Allied species ship registry + Mh-Lai purchase UI

**Source**: `references/lore/economy-and-trade-loops.md` "Allied Species Ships" section.

**Implementation**:
- Likely a separate `SHIPS` registry (cleaner than overloading `MODULES`) in `src/scz/content/ships.py` (NEW) or extension of existing ship-roster content. Per `references/lore/ship-roster.md` for the canonical hulls.
- Mh-Lai customization scene catalog extension: "Allied Hulls" section, gated on alliance flags (`allied_slylandro`, `allied_arilou`, `allied_mmrnmhrm`, etc.).
- Hull-swap mechanic: the Steward's primary stays the Furling Scout; allied hulls are alternate loadouts garaged at Mh-Lai, selectable per departure.
- Eligible species (slice list): Slylandro Lift, Arilou Skiff, Androsynth Refugee Fighter, Mmrnmhrm Sentinel, Burvixese Skipper (conditional on Caster quest evacuation branch), Thinn Blade (conditional on Thinn witness branch — species renamed from "Planar" 2026-05-17).
- Ineligible species: Chenjesu, Taalo, Utwig, Mycon biots, proto-species (lore reasons listed in canon doc).
- Dispatches: Testing chat has `walk_allied_ship_slylandro` (and parallels) queued.

**Status**: ✅ PROCESSED 2026-05-18 — shipped end-to-end:
- `src/scz/content/allied_ships.py` — `AlliedShipEntry` dataclass + 6-entry registry (Arilou Skiff, Androsynth Cruiser, Mmrnmhrm Sentinel, Thinn Blade live; Slylandro Lift + Burvixese Skipper marked `unavailable=True` pending Combat Mechanics ShipClass authoring). Helpers: `available_ships`, `is_purchaseable`, `buy_ship`, `any_unlocked`.
- `src/scz/station/shipyard.py` — `ShipyardScene` with vertical list + detail pane + per-row status indicators (purchased / purchaseable / locked / can't-afford / unavailable). Purchase appends ship_class_id to `game.fleet`.
- `src/scz/station/scene.py` — added "Mh-Lai Shipyard" menu entry gated on `any_unlocked(game)`; appended to ACTIONS list so existing index-based walks are not disrupted.
- **Mechanic deviation from original dispatch text**: the dispatch's "hull-swap mechanic — alternate loadouts garaged at Mh-Lai" framing is *superseded* by the SC2 hot-swap fleet canon Aaron set 2026-05-18. Allied ships now **add to `game.fleet`** rather than swap. They participate in `FleetCombatScene` encounters as roster ships with hot-swap on death.
- `walk_allied_ship_purchase` (5/5 green) seeds the alliance flag + credits, navigates the station menu, opens the shipyard, buys Arilou Skiff, verifies credits drop + fleet grows + return-to-station works.
- **Remaining**: (a) the 2 unavailable entries (Slylandro Lift, Burvixese Skipper) need ShipClass authoring from Combat Mechanics chat to come live; (b) parallel walks for the other 3 currently-live entries (Androsynth, Mmrnmhrm, Thinn) are queued for Testing chat per dispatch §Dispatches.

---

## 2026-05-17 — TODO_LORE convention + UNLOCKED_BY comment markers (post-implementation review)

**Source**: `memory/project_dual_chat_split.md` (TODO_LORE + UNLOCKED_BY conventions established 2026-05-17).

**Context**: Lore chat unlocked 5 crew specialists + 2 weapon mods in `src/scz/content/modules.py` by editing `name` / `description` / `locked` (narrow exception to "Lore chat doesn't edit code"). Subsequently re-locked the 5 crew with `UNLOCKED_BY: recruited_<role>` comment markers when reframing them as side-quest rewards. The 2 weapon mods (Patient Eye / Restless Coil) remain `locked=False` as generic shop-buyables.

**Implementation tasks** (Design-chat review + wire-up):
- Confirm the 5 crew modules' framework fields (`cost_credits`, `cost_resources`, `slot`, `tier`, `deltas`) are still appropriate now that they're quest-rewards (cost_credits=0 is correct for quest-rewards; deltas may need balance-pass).
- Decide on the `unlock_flag` field architecture (see economy-and-trade-loops dispatch above — it's the same mechanism).
- Wire `purchasable_modules()` filter to honor both `unlock_schematic` and `unlock_flag` (crew recruitment flags).

**Status**: ☐ Open — non-urgent; review when working in the modules area.

---

*(Future entries appended above this line.)*
