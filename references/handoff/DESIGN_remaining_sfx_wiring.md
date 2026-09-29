# HANDOFF → Design lane: 33 remaining SFX needing system-level hooks

**From**: Audio chat (2026-05-19)
**To**: Design chat (code-mod lane)
**Status**: Files generated + reviewed + manifest=wired; no code paths play them yet
**Source**: `tools/audio_sfx_specs.py` + `assets/sfx/<subdir>/<name>.wav`

## Context

Aaron's directive 2026-05-19: "Wire all remaining sound effects into the right
place, or tell game design to do it. We can duplicate some sounds if there are
some missing." This is the "tell game design" half of that — the SFX whose play
sites need code that doesn't exist yet, not just an additional `sfx.play()`
call. The audio chat wired everything that just needed a play-call drop-in
(scene lifecycle, menu nav, hazard contact, alert thresholds, engine loops).

Each row below maps a generated SFX file → the game-system change that would
make it audible. Pick them up in any order; none blocks any other.

---

## A. Ship special weapons — 24 SFX

| SFX file | Trigger needed |
|---|---|
| `ships/<id>/special_fire.wav`  (×12) | Player or AI fires the ship's *special* weapon |
| `ships/<id>/special_impact.wav` (×12) | The special weapon's projectile/effect hits a target |

**Ships affected**: furling_scout, persuader_vessel, defender_vessel, cleanser_cruiser, melnorme_trader, arilou_skiff, androsynth_cruiser, mmrnmhrm_sentinel, proto_ur_quan, proto_qor_ah, lemmkin_skitter, sentry_drone_47t.

**Why blocked**: `src/scz/combat/scene.py` line 11 says "no specials yet — those land in pass 2." The combat code has `action.fire_primary` but no `fire_secondary` (or `fire_special`) hook, so there's nothing to attach the SFX to.

**Suggested wiring once specials land** — mirror the existing primary pattern:

```python
# In MeleeCombatScene.update / projectile loop:
if action.fire_special:
    self._fire_special(me)
    if self.game is not None and hasattr(self.game, "sfx"):
        self.game.sfx.play(f"ships/{cls.id}/special_fire")

# In projectile-hit loop (when a special-weapon projectile lands):
if self.game is not None and hasattr(self.game, "sfx"):
    self.game.sfx.play(f"ships/{shooter.cls.id}/special_impact")
```

Special-weapon mechanics per ship are catalogued in
`references/lore/ship-design-schema.md` (Time Drive Pulse, Quasi-Jump,
Dimensional Shear, Sa-Matra Lance, etc.).

---

## B. Lemmkin + Sentry Drone ship registration — 8 SFX

| SFX file | Ship class |
|---|---|
| `ships/lemmkin_skitter/primary_fire`, `primary_impact`, `special_fire`, `special_impact` | LEMMKIN_SKITTER (Homesteader) |
| `ships/sentry_drone_47t/primary_fire`, `primary_impact`, `special_fire`, `special_impact` | SENTRY_DRONE_47T (tutorial enemy) |

**Why blocked**: `src/scz/combat/ships.py` has 10 registered ShipClass entries; lemmkin and sentry_drone are referenced by name in the SFX dispatch (which is `f"ships/{cls.id}/primary_fire"`) but their ShipClass objects aren't constructed in the registry, so they're never spawned into combat.

**Suggested wiring**: add ShipClass entries per the lore docs:
- Lemmkin Skitter: `references/lore/the-lemmkin.md` + ship-roster
- Sentry Drone 47-T: `references/lore/tutorial-arc-implementation.md` (Beat 6 — unionizing sentry-drone combat tutorial)

Once added to `combat/ships.py` and a `precursor_ships()` / `homesteader_ships()` / `tutorial_ships()` returner, the existing SFX dispatch code resolves automatically — no SFX-side edit needed.

---

## C. Orbital scan UI — 4 SFX

| SFX file | Trigger needed |
|---|---|
| `scan/scan_begin` | Player starts a planet scan from orbit |
| `scan/scan_progress_tick` | Per-percentage-point of scan progress |
| `scan/scan_sweep` (loop) | Looping sonar-pulse during active scan |
| `scan/scan_complete` | Scan completes; mineral/bio readout becomes visible |

**Why blocked**: there is no orbital scan UI yet. The `PlanetOrbitScene`
currently jumps straight from "enter orbit" to "deploy lander" with no scan
phase in between.

**Suggested wiring** (in `src/scz/system/orbit.py`):
- Add a "scan" action (Y button? new button?) that opens a scan progress bar.
- On scan start: `sfx.play("scan/scan_begin")` + `sfx.play_loop("scan/scan_sweep")`.
- On each ~10% progress: `sfx.play("scan/scan_progress_tick")`.
- On scan complete: stop the loop + `sfx.play("scan/scan_complete")`.

Reveals planet's mineral / bio composition to the HUD before the player commits
the lander. Touches `system/orbit.py` + needs a `Planet.scan_results` model.

---

## What WAS wired by the audio chat in this pass

Coverage: 46 / 79 SFX (58%). The wired set covers every code-side trigger
that already existed — only the system-level gaps above remain. Touched files:

- `src/scz/audio/sfx_bus.py` — added `play_loop()` for looping SFX
- `src/scz/audio/mixer.py` — crossfade between music contexts (no silent gaps)
- `src/scz/engine/game.py` — `ui/screen_transition` on every set_scene
- `src/scz/scenes/switcher.py` — modal_open / modal_close on overlay
- `src/scz/scenes/stubs.py` — music_context + menu_confirm/cancel on MainMenu + every stub
- `src/scz/dialog/scene.py` — modal_open + hud_acknowledge + menu_select/confirm/cancel
- `src/scz/station/scene.py` + `trade.py` + `customization.py` — full nav SFX + menu_invalid on rejection paths
- `src/scz/combat/super_melee.py` — full nav SFX
- `src/scz/combat/scene.py` — alert_warning (<25% shield) + alert_danger (<25% hull) one-shot thresholds
- `src/scz/system/orbit.py` — enter_orbit + cloak_engage on enter, cloak_disengage on exit
- `src/scz/planet/scene.py` — atmospheric_entry + deploy + arrive on enter; engine_idle loop; hazard_warning on contact-entry; damage_taken throttled to 0.6s/tick; scan_ping if scanner installed; lift_off on exit; resource_chime_bio/mineral layered over pickup tones

All 6 walk-tests still pass (walk_tutorial_path, walk_orbit_and_surface,
walk_arilou_sage, walk_super_melee, walk_customization, walk_melnorme).
