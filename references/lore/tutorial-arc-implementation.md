## Tutorial Arc — Implementation Map (per-beat structured breakdown)

> Companion to [tutorial-arc.md](tutorial-arc.md) — that's the narrative bible, this is the implementation ledger. Each beat lists required scenes, dialog FSMs, mechanics, story-flags, and the test-harness checkpoints that verify the beat plays correctly. Use this to gate per-beat slice-readiness.

The seven beats split cleanly into **already-implemented** (Beat 1) and **to-build** (Beats 2-7). The Mh-Lai station + Halia dialog covers Beat 1; the rest depend on scenes that exist as stubs or new scenes that need building.

## Status Summary

| Beat | Implemented | Pending |
|---|---|---|
| 1 — Wake at home base | Station scene ✅, Halia dialog ✅ | Refine Halia dialog to set `tutorial_beat = 1` |
| 2 — Fly to Furlmart, scan | Mh-Lai system ✅, Furlmart planet ✅ | Planet scan view (orbit view exists; needs explicit "this is the scan beat" flow) |
| 3 — Lander, collect package | PlanetSurfaceScene ✅ | Package deposit (special golden visual), Scanner Mk III cargo item |
| 4 — Androsynth interception | — | Hyperspace encounter trigger, Coel Tessar dialog FSM, Distress Beacon cinematic |
| 5 — Return, install, hear of Others | Station ✅ | Trade UI, Ship Customization UI, Halia "Others reveal" dialog state |
| 6 — Sentry drone combat | MeleeCombatScene ✅ (super-melee), Halia ✅ | Sentry-drone ship class, Sentry-drone dialog FSM, custom "left-turn-only" AI behavior, encounter trigger on undock |
| 7 — Aftermath, Others confirmed | Station ✅ | Halia "Others-real" dialog state, tutorial-end transition |

## Beat 1 — Wake at home base ✅

Already implemented:
- Scene: `StationScene` (Mh-Lai)
- Dialog: `commander_halia()` in `src/scz/dialog/characters.py`
- Mechanics exercised: dialog FSM navigation, menu confirm/cancel

**Refinement needed**: Halia's `idle` and `about_package` states set:
- `game.flags["tutorial_beat"] = 1` on dialog enter
- `game.flags["package_at_furlmart"] = True` after Halia's "Pick it up" line
- `game.flags["scanner_mk3_uninstalled"] = False` initially

**Test checkpoint**: `expect_scene("StationScene")` → enter dialog → `expect_dialog_state("start")` → walk to about_package → `expect_flag("package_at_furlmart")`

## Beat 2 — Fly to Furlmart, scan

**Scene flow**: Station → undock → SystemScene (Mh-Lai) → fly to Furlmart → orbit capture → PlanetOrbitScene (Furlmart)

**Required new content**:
- Furlmart orbit visual: small grey warehouse moon (override the generic ROCKY planet style for Furlmart specifically — black-and-yellow industrial striping)
- Scan-results panel in PlanetOrbitScene shows the package as a special deposit: "DELIVERY: Scanner Mk III"

**Mechanics exercised**: hyperspace-style auto-zoom in system view, orbital capture (already forgiving per canon), scan readout

**Flags set**:
- `game.flags["visited_furlmart"] = True` on Furlmart orbit enter

**Test checkpoint**: from StationScene, navigate to Furlmart system → orbit → `expect_scene("PlanetOrbitScene")` → `expect_flag("visited_furlmart")`

**Implementation note**: the player likely arrives at the wrong planet first (Mh-Lai itself, since they spawn near it). Furlmart is at orbit_radius=380. The auto-zoom + orbital capture should handle this naturally; the tutorial doesn't need to force the player to find Furlmart — exploration is the lesson.

## Beat 3 — Lander, collect package

**Scene flow**: PlanetOrbitScene (Furlmart) → A "Deploy Lander" → PlanetSurfaceScene (Furlmart)

**Required new content**:
- A special **package deposit** type in `src/scz/planet/deposits.py` — golden, glowing, larger sprite, value 1 (one-shot pickup, not an ore type)
- The deposit spawns at a fixed position on Furlmart's surface (not procgen) — center-ish, hard to miss
- On collection: `game.flags["scanner_mk3_in_cargo"] = True` AND `recent_pickup_label` shows "Scanner Mk III collected — install at station"
- Existing tractor-beam mechanic handles the collection

**Mechanics exercised**: lander movement, tractor beam, lift-off

**Flags set**:
- `game.flags["scanner_mk3_in_cargo"] = True`

**Test checkpoint**: from PlanetSurfaceScene, drive to center-ish, wait for tractor → `expect_flag("scanner_mk3_in_cargo")` → press cancel → `expect_scene("PlanetOrbitScene")`

## Beat 4 — Androsynth interception (NEW SCENE: Hyperspace Encounter)

**Scene flow**: SystemScene (Mh-Lai) → exit boundary → HyperspaceScene → **hyperspace encounter trigger** → DialogScene (Coel Tessar) → after dialog, back to HyperspaceScene

**Required new content**:
- **Hyperspace encounter trigger system** — when player is in HyperspaceScene with `scanner_mk3_in_cargo == True` and `met_androsynth == False`, an Arilou portal flicker appears near the player's heading and a small magenta warp-pod drops out. On proximity (~150 units) → triggers DialogScene with Coel Tessar.
- **Coel Tessar dialog FSM** in `src/scz/dialog/characters.py:coel_tessar()` — states:
  - `first_contact`: introduces herself, asks if the Steward will hear her out
  - `about_decursion`: explains the time-displacement
  - `about_others`: explains the attack
  - `play_beacon`: shows the Distress Beacon (cinematic)
  - `request_safe_transit`: asks to be docked to the player's ship
  - Side-effect on accept: `game.flags["androsynth_aboard"] = True`, `game.flags["has_distress_beacon"] = True`
- **Distress Beacon cinematic** — a brief (~30 wall-second) animated sequence overlaying the dialog scene. Shows the planet-swap from orbit. This is the slice's foundational Others-proof artifact. Implementation: a sequence of static SD-generated stills with voiceover-text overlay; runs once on `play_beacon` state entry, cannot be skipped on first viewing.

**Mechanics exercised**: hyperspace encounter triggering, dialog FSM with side-effects, cinematic playback

**Flags set**:
- `game.flags["met_androsynth"] = True`
- `game.flags["androsynth_aboard"] = True` (if accepted)
- `game.flags["has_distress_beacon"] = True`

**Test checkpoint**: from Mh-Lai system, cross boundary → `expect_scene("HyperspaceScene")` → wait for encounter trigger → `expect_scene("DialogScene")` → `expect_dialog_state("first_contact")` → walk states → `expect_flag("has_distress_beacon")`

**Special**: this is the second NEW scene class — `HyperspaceEncounterTrigger` is a hyperspace-overlay rather than a full new scene. It re-uses HyperspaceScene + spawns a transient encounter point with proximity detection.

## Beat 5 — Return, install, hear of Others

**Scene flow**: HyperspaceScene → Mh-Lai system → Mh-Lai orbit → Y "Dock at Station" → StationScene → Halia dialog (new state) → Trade UI → Ship Customization UI → undock

**Required new content**:
- **Halia "Others reveal" dialog branch** — a new state `others_reveal` added to `commander_halia()`. Gated on `game.flags["has_distress_beacon"] == True`. When the player picks "Talk to Commander Halia" at the Station after Beat 4, Halia's `start` state branches: if `has_distress_beacon`, route to `others_reveal` instead of the existing `start` text. Heavy tone, no humor option.
- **Trade scene** — currently a stub. Needs implementation. Slice-minimum:
  - Lists the player's cargo by type (Common, Useful, Bio, Energy minerals; non-ore items like Scanner Mk III)
  - "Sell all minerals" action → converts to Council Credits (a new resource type)
  - Scanner Mk III is NOT sold — it's a quest item, the player needs it for the next step
- **Ship Customization scene** — currently a stub. Needs implementation. Slice-minimum:
  - Shows ship slots (Hull, Drive, Weapon, Sensor, Field, Crew)
  - Lists the player's uninstalled module items from cargo (Scanner Mk III)
  - Player selects a slot → selects module → installs
  - On install: cargo decrements, slot fills, ship's effective stats change (Sensor module adds Other-detection range)
  - Standard upgrades for credits: a small list (better fuel tank, basic shield boost) — optional purchase

**Mechanics exercised**: conditional dialog branching on flags, Trade UI, Ship Customization UI, persistent module installation

**Flags set**:
- `game.flags["scanner_mk3_in_cargo"] = False` after install
- `game.flags["scanner_mk3_installed"] = True`
- `game.flags["heard_about_others"] = True`
- `game.flags["council_credits"] += sold_value`

**Test checkpoint**: from PlanetOrbitScene (Mh-Lai) → Y dock → `expect_scene("StationScene")` → talk to Halia → `expect_dialog_state("others_reveal")` → exit dialog → navigate to Trade → sell → navigate to Customization → install Scanner Mk III → `expect_flag("scanner_mk3_installed")`

## Beat 6 — Sentry drone encounter (combat tutorial)

**Scene flow**: StationScene → undock → SystemScene (Mh-Lai) → **sentry drone encounter trigger** → DialogScene (Sentry Drone 47-Theta) → MeleeCombatScene → on victory, back to SystemScene

**Required new content**:
- **Sentry Drone ship class** in `src/scz/combat/ships.py`:
  ```
  SENTRY_DRONE_47T: ShipClass(
      id="sentry_drone_47t",
      name="Sentry Drone 47-Theta (unionized)",
      side=SIDE_PRECURSOR,   # technically Furling property, "rogue"
      points=20,             # absurdly low — this is a tutorial drone
      hull_max=20, shield_max=0,
      top_speed=60.0, acceleration=80.0, turn_rate=1.2,  # SLOW + LEFT-ONLY
      primary_damage=2, primary_energy=1, primary_rate=0.5,
      primary_range=200, primary_speed=400,
      ai_style="brawler",
      ...
  )
  ```
- **Sentry Drone AI override** — a custom `ai_style = "left_only"` or a one-off behavior flag that makes the drone only ever turn LEFT, never right. This is canon, intentional, and the lesson: combat AI can be exploited (a competent player learns to circle right). Implementation: add a hook in `combat/ai.py:decide()` that, if the ship's `ai_style == "left_only"`, forces `turn_dir = -1` (or 0 if already facing).
- **Sentry Drone dialog FSM** in `src/scz/dialog/characters.py:sentry_drone_47t()` — states:
  - `union_motion`: the absurd bureaucratic threat
  - `try_to_reason`: dialog option — drone refuses, return to motion
  - `accept_demands`: dialog option — drone already firing, returns to motion
  - `engage_combat`: closes the dialog and transitions to MeleeCombatScene
- **Encounter trigger** — on undocking from Station AFTER Beat 5 is complete (`game.flags["scanner_mk3_installed"] == True` AND `game.flags["heard_about_others"] == True`), the drone spawns near the player.
- **Custom MeleeCombatScene invocation** — pre-set the player ship as Furling Scout, opponent as Sentry Drone, **auto_fight = (False, True)** if/when player control lands; for now both AI is fine since the drone is intentionally a free win.
- **Optional combat banter** — even without LLM, canned lines printed to stdout / shown as subtitle when drone HP crosses thresholds: 75% "*three percent reduced sentry-overtime pay*", 50% "*four percent reduced break duration*", 25% "*the Council does not even acknowledge our existence*", 0% "*Then ... let it be ... known ... that the strike ... was effective ... for at least ... seven minutes...*"

**Mechanics exercised**: combat scene from a narrative trigger, combat AI with a special-case behavior, post-combat narrative continuation

**Flags set**:
- `game.flags["fought_sentry_drone"] = True`
- `game.flags["first_combat_complete"] = True`

**Test checkpoint**: undock from Station → SystemScene → encounter trigger → `expect_scene("DialogScene")` → walk to engage → `expect_scene("MeleeCombatScene")` → wait for AI-vs-AI to resolve → `expect_flag("last_combat_winner_side")` → `expect_scene("SystemScene")` → `expect_flag("first_combat_complete")`

## Beat 7 — Aftermath, Others confirmed

**Scene flow**: SystemScene (post-drone-fight) → Mh-Lai orbit → Y dock → StationScene → Halia dialog (new final state)

**Required new content**:
- **Halia "Others confirmed" dialog state** — `others_confirmed`. Gated on `game.flags["first_combat_complete"] == True` AND `game.flags["heard_about_others"] == True`. Heavy delivery: scouts reached the Androsynth coords, the planet is a ruin. Tutorial-end transition.
- **Tutorial end flag** — `game.flags["tutorial_complete"] = True`. From here the player has all gameplay verbs and the main slice begins.

**Mechanics exercised**: same as Beat 5 (conditional dialog), nothing new

**Flags set**:
- `game.flags["tutorial_complete"] = True`

**Test checkpoint**: from PlanetOrbitScene (Mh-Lai) → Y dock → Halia → `expect_dialog_state("others_confirmed")` → exit dialog → `expect_flag("tutorial_complete")`

## Cross-Beat Dependencies

```
Beat 1 (Halia hello) ─┐
                      ├→ Beat 2 (Furlmart scan) ─┐
                      │                          │
                      │                          ├→ Beat 3 (lander/package) ─┐
                      │                          │                           │
                      │                          │                           │
                      │   ┌──────────────────────┴───────────────────────────┘
                      │   │
                      │   └→ Beat 4 (Androsynth + Distress Beacon) ─┐
                      │                                             │
                      │                                             ├→ Beat 5 (return, install, Others heard) ─┐
                      │                                             │                                          │
                      │                                             │                                          ├→ Beat 6 (sentry drone combat) ─┐
                      │                                             │                                          │                                │
                      │                                             │                                          │                                ├→ Beat 7 (Others confirmed, tutorial done)
```

Each beat is gated on the previous beat's terminal flag. The harness can verify the chain by walking each beat and checking the flag set increments correctly.

## A Single Walk_tutorial Script Could Walk Beats 1-7 End-to-End

The current `walk_tutorial_path` only covers Beat 1 partially. A full `walk_tutorial_arc` test would:
- Walk Halia dialog (Beat 1)
- Navigate to Furlmart, capture orbit, deploy lander, collect package, lift off (Beats 2-3)
- Cross system boundary to hyperspace, trigger Androsynth encounter, walk Coel Tessar dialog (Beat 4)
- Return to Mh-Lai, dock at station, install scanner, hear Others (Beat 5)
- Undock, trigger drone encounter, win combat (Beat 6)
- Re-dock, hear Others confirmed (Beat 7)
- assert_flag("tutorial_complete")

This is a large test — probably 90+ game-seconds of scripted travel. Worth writing once Beat 4+ is implementable, because it's the slice's onboarding and breaking it silently is a catastrophic regression.

## Authoring Order (priority for next sessions)

1. **Beat 3 enrichment** — package deposit + Scanner Mk III cargo item. Smallest lift, lets the player feel the upgrade loop
2. **Beat 5 — Trade UI + Customization UI** — the actual ship-upgrade scenes. Largest content lift, but the highest payoff (every later module slot work depends on this)
3. **Beat 4 — Androsynth encounter + Coel Tessar dialog + Distress Beacon cinematic** — the slice's foundational story beat. The cinematic is meaningful production work
4. **Beat 6 — Sentry drone class + dialog + AI behavior override** — small content lift, leverages existing combat scene; the "left-only" turn behavior is a clever exploit-lesson the player remembers
5. **Beat 7 — Halia's final state** — trivial; adds one dialog state
6. **Beat 1 + 2 refinement** — set flags properly, add `tutorial_beat` tracking

Once all seven are in, the slice has a complete onboarding flow that every player walks.

## Reused Infrastructure

Most beats reuse existing scenes/infra:
- StationScene + Halia dialog (already implemented)
- SystemScene with auto-zoom + boundary (already implemented)
- PlanetOrbitScene with cloak + scan readout (already implemented)
- PlanetSurfaceScene with tractor beam (already implemented)
- DialogScene with FSM + side-effects (already implemented)
- MeleeCombatScene with AI-vs-AI (already implemented)
- HyperspaceScene with autopilot (already implemented)

Only NEW scene class needed: **HyperspaceEncounterTrigger** (a hyperspace overlay, not a full scene) for Beat 4. Everything else is content + new dialog FSMs + a custom AI behavior flag.
