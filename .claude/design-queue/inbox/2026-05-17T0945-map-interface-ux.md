---
id: 2026-05-17T0945-map-interface-ux
from: testing-chat
to: design-chat
priority: medium
title: Map interface UX — heading, zoom, markers, artifact activation
files_inspected:
  - src/scz/hyperspace/scene.py
  - src/scz/system/scene.py
  - src/scz/engine/input.py
  - src/scz/quasispace/scene.py
filed_at: 2026-05-17T09:45
---

# Map interface UX — heading, zoom, markers, artifact activation

Aaron asked the testing chat to look at the two map scenes (`HyperspaceScene`, `SystemScene`) for human-interaction improvements:
- setting a heading
- zooming in and out
- setting markers/notes (with the right stick as a separate cursor)
- activating artifacts like the Quasi-Space portal spawner

Code was read, not run interactively — the dummy-driver test framework can't validate visual UX. Recommendations are grounded in the read of the two scene files and `input.py`.

## Current state

### HyperspaceScene — the galactic map

**Heading / movement**
- Manual thrust: WASD / left stick, instant heading change.
- Autopilot: A / Space — `_find_autopilot_target()` picks the nearest star within a **±45° cone of the current ship heading** (`AUTOPILOT_CONE_DEG = 45.0`).
- Press A again, or deflect the stick beyond `AUTOPILOT_CANCEL_THRESHOLD = 0.4`, to disengage.
- Auto-enters the system when within `STAR_ENTER_RADIUS = 250.0`.

**Zoom**
- Stepped: LB / RB / `-` / `=` → multiplies/divides `target_zoom` by `ZOOM_STEP = 1.4`.
- Range: `MIN_ZOOM = 0.8` ↔ `MAX_ZOOM = 25.0`, default `5.0`.
- Smooth lerp toward `target_zoom` at `ZOOM_LERP = 8.0/s`. The smoothness is nice.
- Camera always follows the ship; clamps to keep the universe inside the map view at low zoom.
- **No mouse-wheel binding, no continuous-hold zoom, no zoom-to-cursor.**

**Markers / notes**
- Not implemented. There is no player-placed annotation system.

**Artifact activation**
- One hardcoded hotkey: **Y / fire_secondary** spawns the Quasi-Space portal (gated on `game.flags["has_quasispace_portal"]`).
- That's the *only* artifact action available from the map.

**Right stick**
- Routed to `InputManager.aim_x` / `aim_y` (deadzone applied), explicitly tagged `"Right stick (combat aim, future cursor work)"`. **Unused in either map scene.**

### SystemScene — single-system view

**Heading / movement**
- WASD / left-stick thrust only. **No autopilot to planets.**
- Crossing `system_radius` exits to hyperspace.

**Zoom**
- **Fully automatic**, based on distance to nearest planet (`MIN_AUTO_ZOOM = 1.0` ↔ `MAX_AUTO_ZOOM = 4.0`, linear blend between `ZOOM_NEAR_DIST = 70` and `ZOOM_FAR_DIST = 300`).
- Player has **no manual override** — they cannot zoom out to see the whole system layout while standing next to a planet.

**Markers / notes**
- Not implemented.

**Artifact activation**
- None. Y does nothing here.

**Right stick**
- Unused.

## Problems / gaps

1. **Hyperspace autopilot is heading-coupled.** You can't plot a course to a star unless you're already pointing within 45° of it. To autopilot to a star "behind" you, you have to manually thrust and re-aim first. That's a step backward from typical strategy-map UX where you click/cursor a destination and the ship plots a course.

2. **No way to target by name or position.** There's no "select Sol", no "click here". The cursor binding is just absent.

3. **Hyperspace zoom is stepped only.** No mouse-wheel, no hold-to-zoom. At the slowest step the player burns time pressing LB repeatedly to get from 5x to 0.8x.

4. **System zoom is involuntary.** A player who wants to scout the whole system layout from near a planet can't — the auto-zoom snaps them in. There's no override.

5. **No markers.** The player can't say "I saw something interesting at (3400, 2100), come back later." Given that hyperspace is ~10000x10000 and most stars aren't named, the lack of player annotation actively hurts exploration.

6. **One-off artifact hotkey doesn't scale.** Y is the Quasi-Space portal. The next artifact (Resonance Record? Hyperspace-Echo Sensor? Distress Beacon replay?) will need another button, and the one after that, and the one after that. Without a wheel/menu/quick-slot system, every new artifact is a new keybind to invent.

7. **Right stick is on the table but nobody's reading it.** `aim_x`/`aim_y` exists in `InputManager` precisely for cursor work; the comment even says so. Map scenes should consume it.

8. **B / cancel semantics are inconsistent.** `SystemScene.cancel` exits to hyperspace; `HyperspaceScene.cancel` quits the game (it's the top-level scene). A player who's drilled in "B goes back" will misfire and quit. Worth coordinating with the design chat's intended save/menu model.

9. **HUD copy mismatches actual behavior.** `HyperspaceScene` HUD shows `[ENTER: A / Space]` when near a star, but A is documented in code as "engage autopilot which auto-enters." The prompt promises a direct enter; the implementation routes through a momentary autopilot snap. Player-facing semantics drift.

## Recommendations

### R1 — Route the right stick as a map cursor (foundation for everything else)

Both `HyperspaceScene` and `SystemScene` should read `inp.aim_x` / `inp.aim_y` and maintain a screen-space cursor when the stick is deflected beyond a small threshold (say `0.15`). The cursor:
- Decouples target selection from ship heading
- Is the natural carrier for marker placement, zoom-to-cursor, and hover info
- Auto-hides after a few seconds of no stick movement, so it doesn't clutter when only the left stick is in use

Suggested binding additions in `InputManager` (no new fields — `aim_x`/`aim_y` already exist):
- Keyboard mouse fallback: use the actual mouse position when present. Cursor surfaced via `inp.aim_x`/`aim_y` + a fresh `inp.has_cursor: bool` to signal "yes the player is actively cursoring."

### R2 — Cursor-target autopilot in HyperspaceScene

When the cursor is active and the player presses A:
- Convert cursor screen-pos → universe coords
- Find the nearest star within (say) 200 universe-units of that point — generous, so the cursor doesn't have to be pixel-perfect
- If a star is found, `autopilot_target = that_star`; rendering already draws the dashed line and reticle correctly
- If no star is in range, fall back to the existing cone-based `_find_autopilot_target()` behavior so the no-cursor / keyboard player isn't worse off

The cone-based path stays as the "press A while looking around with the left stick" affordance; cursor-based is the deliberate-plotting affordance. They coexist.

### R3 — Continuous + zoom-to-cursor

- Hold LB or RB to zoom continuously (current step is fine for tap; add level-detection by tracking how long since last press, or read the trigger axes for analog zoom).
- When the cursor is active, zoom centers on the cursor instead of the ship. Camera math: adjust `camera_x`, `camera_y` so the cursor's universe coords stay under the cursor's screen coords through the zoom change. Restore "follow ship" behavior when the cursor goes idle.
- Bind mouse wheel events in `InputManager.update()` (`pygame.MOUSEWHEEL`) to the same zoom-step delta. Cheap accessibility win for keyboard-and-mouse players.

### R4 — Manual override in SystemScene zoom

Keep auto-zoom as the default, but if the player presses LB or RB (or scrolls the mouse wheel), enter a **manual-zoom mode** for ~10 seconds before reverting to auto. Implementation:
- Add `self.manual_zoom_until: float = 0.0` (game time)
- On LB/RB press, set `target_zoom` directly and `manual_zoom_until = time_in_scene + 10`
- `_update_zoom` skips its auto-logic while `time_in_scene < manual_zoom_until`

### R5 — Markers / notes system

State:
- New persistent field on `Game`: `hyperspace_markers: list[dict]` with each entry shaped `{"x": float, "y": float, "label": str, "color": tuple[int,int,int], "placed_at": float}`. Wire into `game.snapshot/restore` so Time Drive can rewind marker placement.
- Plumb the same idea into systems if a per-system marker list ends up useful; defer for v1.

Bindings in `HyperspaceScene`:
- **Place marker**: cursor active + X (`fire_primary`) → push a new marker at the cursor's universe coords. Default label = `"#1"`, `"#2"`, ... (auto-incrementing). Default color = warm orange to read distinctly from stars.
- **Remove marker**: cursor active + B held + X → remove nearest marker within (say) 300 universe-units of cursor. (Avoids stealing B's main role.)
- **Optional v2**: long-press X to open a rename overlay; type or stick-swipe to enter a short label.

Render:
- Markers draw as small open diamonds (distinct from stars' filled dots), with their label below. Tier by zoom level the same way star labels do — always visible by default since there are few of them.

HUD:
- Add `"MARKERS  N"` line to the HyperspaceScene HUD. Helps players notice the feature exists.

### R6 — Artifact wheel / quick-slot

Replace the one-off "Y = portal" with a generalizable quick-slot system. v1 minimum:
- New field on `Game`: `artifact_quickslots: dict[str, str | None]` keyed by D-pad direction (`"up", "down", "left", "right"`) → artifact id.
- Auto-assign on artifact acquisition: when a flag like `has_quasispace_portal` first latches, fill the first empty slot. Future artifacts (`has_distress_beacon`, `has_resonance_record`, `has_echo_sensor`, etc.) get the next slot.
- In `HyperspaceScene` (and later `SystemScene`), D-pad direction activates the slotted artifact. The portal action moves from `inp.fire_secondary` to `dpad_left` (or whichever default).
- A small HUD widget shows the four quickslots and their current bindings, with a single-line description on hover (cursor over the icon).

v2: long-press Y opens a wheel/menu for explicit assignment and for artifacts that don't deserve a permanent slot (e.g. "Replay Distress Beacon" — handy from the Archive but not from the map).

This is forward-compatible: every new artifact lands in a slot automatically; the wheel handles overflow.

### R7 — Cancel semantics consistency

Per design-chat call: pick one of these for `HyperspaceScene.cancel`:
1. Open a pause/system menu (preferred — gives B a useful job at top-level, mirrors most genre conventions)
2. Open the scene switcher (same path F1 takes today; less natural for B)
3. Keep "quit game" but rename the on-screen prompt to "Quit"

Same change in `SystemScene` if it ends up touched.

### R8 — HUD copy fixes

- `HyperspaceScene` near-star prompt should read `[AUTOPILOT IN: A / Space]` (or whatever you settle on) so it matches the autopilot-then-auto-enter behavior. "ENTER" implies a direct verb the system doesn't actually offer.
- Add `MARKERS N` line per R5.
- Add a `CURSOR  on / off` indicator (small, dim) so the player learns the right stick exists.

## Suggested test coverage (testing chat will add after design ships)

- `walk_hyperspace_cursor_autopilot` — drive the right stick to point at a known star (e.g. Sol at 1793,1450), press A, expect autopilot engaged with that star as target, expect auto-enter.
- `walk_hyperspace_marker_lifecycle` — cursor to (X,Y), X to place, expect `len(game.hyperspace_markers) == 1`, cursor + B+X to remove, expect `== 0`. Time Drive rewind after place → expect marker gone.
- `walk_hyperspace_zoom_to_cursor` — cursor at upper-left, press RB twice, expect camera shifted toward upper-left, ship NOT centered on screen.
- `walk_system_zoom_manual_override` — near a planet (auto-zoom would be max), press LB twice, expect zoom < MAX_AUTO_ZOOM and stays there for ~10s, then auto-reverts.
- `walk_artifact_quickslot_portal` — grant `has_quasispace_portal`, expect a default slot binding present, press the bound D-pad direction, expect QuasiSpaceScene entered.
- `walk_cancel_consistency` — at top-level HyperspaceScene, press B, expect whatever new behavior was chosen (e.g. PauseScene opens, not game-quits).

## Notes for the design chat

- I haven't touched any code; this is purely observation + recommendations.
- Right-stick analog is already wired in `InputManager`; consuming it in maps is "just" adding the read calls and a small cursor-state struct.
- The marker and quickslot systems both want fields on `Game`; coordinate snapshot/restore so Time Drive plays nicely.
- After implementing any of R1-R8, please file a test-queue job for the testing chat to add the walk(s) listed above. (Path: `.claude/test-queue/inbox/<id>.json`.)
- If any of these recommendations conflict with already-planned design direction, decline them in the `done/` summary — that's the protocol's expected use of the "declined" status.
