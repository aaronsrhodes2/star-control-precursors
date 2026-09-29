# Manual Playtest — Lander Resource-Gathering Mini-Game

**Purpose:** Human verification of the lander surface scene. Walk-tests run
headless (`SDL_VIDEODRIVER=dummy`) and can't see pixels, so this checklist
covers the *visual* side: procedural terrain, fuzz-to-sharp sensor mechanic,
sensor-ring overlay, scan pulse, hazard warning chevron, HUD sensor readout.

**Who runs this:** the Testing chat, or Aaron when he wants a quick sanity
pass. Estimated time: 8–12 minutes for a full sweep, 2 minutes for a fast
spot-check.

**What this is NOT:** an automated test. If you can express the check as a
`flag X = Y` assertion, put it in `walk_*` instead and file it via
`.claude/test-queue/`.

---

## Quick launch

From the worktree root:

```powershell
cd D:\Aaron\development\star-control-precursors\.claude\worktrees\elegant-bartik-733a37\src
python -m scz.main --windowed
```

That opens a 1280×720 window on the main menu — no fullscreen takeover.

If you want to skip past tutorial dialog and land fast, use the walk launcher
in pass-through mode (the script drives until it ends, then leaves the window
interactive so you can play normally):

```powershell
python -m scz.main --windowed --test walk_orbit_and_surface
```

When the walk finishes it leaves you in `SystemScene` after a clean lift-off.
Press D-pad / arrows to fly to a planet and dock again to re-enter the lander.

---

## Path to the surface (fastest manual route from main menu)

1. Main menu → **New Game** (A / Enter)
2. Dialog: hammer **A** through the opening lines until you're back at
   StationScene.
3. StationScene → **Undock** → SystemScene
4. SystemScene → fly to **Mh-Lai II** (a hazard-bearing planet — closest to
   the home star). Dock at it.
5. PlanetOrbitScene → **Land** (A / Enter)
6. You should now be in **PlanetSurfaceScene**.

Other useful surface destinations once you're on the starmap:
- **Mh-Lai II** — has heat hazards, good for hazard checks
- **Furlmart** — has the Scanner Mk III package; no hazards (safe)
- Any TERRESTRIAL or PRIMORDIAL world — best terrain texture variety

---

## Checklist (run top-to-bottom)

### 1. Procedural terrain texture

Land on a planet. Look at the surface tile (the inset rectangle inside the
larger surface frame).

- [ ] The surface has *visual texture* — not flat color. You should see at
      least one of: boulder dots, dune lines, ice cracks, lava veins, wave
      strokes, glowing blotches, vegetation+water patches.
- [ ] Different planet types show different patterns. Lift off, fly to a
      different planet type, land. Confirm the texture changes.
- [ ] **Deterministic:** Lift off the same planet and re-land. Texture
      should be **identical** (same seed → same pattern).

**Failure mode to flag:** flat-color terrain (texture didn't generate);
identical pattern on every planet (seed isn't being used).

### 2. Sensor ring (dashed circle around lander)

Look at the lander icon (yellow diamond).

- [ ] There's a faint **dashed ring** around the lander. The dashes rotate
      slowly clockwise (~0.5 rad/s).
- [ ] The ring is *roughly* 1/5th of the surface width across in diameter
      at base sensor (`SURFACE_SENSOR_BASE = 0.20`).

### 3. Scan pulse (expanding ripple)

- [ ] A second ring **expands outward** from the lander, restarts every
      ~2.4 seconds. It fades as it grows; not garish.
- [ ] The pulse's max radius matches the sensor ring's radius.

### 4. Deposit fuzz-to-sharp (the core mini-game mechanic)

Spawn on a planet with deposits (any non-Furlmart planet).

- [ ] Deposits **outside** the sensor ring are **invisible**.
- [ ] Deposits **just inside** the sensor ring render as **wide, dim halos** —
      you can see *direction* but not exact position.
- [ ] As you fly toward a halo, it **sharpens** — halo shrinks + bright
      center dot appears + label/value resolves.
- [ ] At very close range, the deposit reads as a **tight bright marker**.

**Failure mode:** all deposits visible from anywhere on the map (fuzz
mechanic isn't gating); deposits never sharpen (distance isn't being
calculated against `surface_sensor_range`).

### 5. Hazard fuzz-to-sharp + warning chevron

Land on **Mh-Lai II** (or any planet with hazards — flag is "hazards: N total"
in the HUD bottom).

- [ ] Hazards too far away: **invisible**.
- [ ] Mid-range hazards: faint danger-colored cloud (translucent disc).
- [ ] Close-range *active* hazards: full filled disc + bright outline.
- [ ] Inactive (between-pulse) hazards: faint outline only; fades to nothing
      at long distance.

For the **warning chevron** specifically:
- [ ] Fly the lander to within ~half a hazard-radius of an *active* hazard
      *edge* (close but not yet overlapping).
- [ ] A **pulsing red chevron** appears on the side of the lander facing
      the hazard. It has three short red ticks + a triangle pointing at
      the threat.
- [ ] The chevron rotates with you — always pointing toward the nearest
      threatening hazard.
- [ ] Fly away → chevron disappears.

### 6. Damage and destruction

- [ ] Fly *into* an active hazard. HP bar in the HUD drops visibly. Color
      shifts red as it nears zero.
- [ ] Sit inside the hazard. Lander destruction screen appears. Trip haul
      is lost. After ~2.5s, you auto-eject to PlanetOrbitScene.
- [ ] Check the HUD on next land: `landers_lost` flag should have
      incremented; cargo[COMMON] decreased by replacement cost.

### 7. HUD sensor readout

In the HUD's left panel, below "DEPOSITS REMAINING":

- [ ] There's a **SENSORS** section showing three values:
  - `deposit  0.20` (or higher if upgraded)
  - `hazard   0.30` (or higher if upgraded)
  - `tractor  0.06` (or higher if upgraded — TRACTOR_BEAM_BASE)
- [ ] **At base values:** numbers render in dim gray-blue (no upgrade yet).
- [ ] **After installing an upgrade** (see §8): the upgraded number renders
      in **bright** sensor-blue. Visible difference at a glance.

### 8. Upgrade pillar verification (sensor module install)

Most informative end-to-end test. Demonstrates that the surface visuals
respond to module installs.

1. Lift off back to PlanetOrbitScene → SystemScene → dock at the station.
2. Trade → sell enough USEFUL to afford the Scanner Mk III (or install
   the tutorial-quest one if you grabbed it on Furlmart).
3. ShipCustomization → install **scanner_mk3** into the sensor slot.
4. Undock → fly back to any planet → land.

Now on the surface:
- [ ] The **dashed sensor ring is visibly larger** than at base.
- [ ] The **scan pulse expands further** to match.
- [ ] More deposits resolve out of the fog at the same lander position.
- [ ] HUD's **`deposit  0.30`** line is now bright (was dim before).

If you have a **LR Mineral Scanner** (`lr_mineral_scanner`) installed
*and* you exit to hyperspace, the HUD there should show:
- [ ] **ECHO SENSOR range … · N ripples** line
- [ ] A per-system **resource scan** block with mineral totals when you're
      near a star.

(That's outside the lander loop, but it's the same pillar.)

### 9. Trip-haul commit + lift-off

- [ ] Tractor some deposits. THIS TRIP column in the HUD shows them.
- [ ] Press **Esc / B** to lift off. The trip-haul collapses into SHIP HOLD
      on the next scene (PlanetOrbitScene → back to lander, you'll see the
      new totals).
- [ ] If you die instead of lifting off, the trip-haul is **lost** (compare
      with the destruction path in §6).

---

## Reporting back

After running the sweep, if anything failed, file a fix request to the
**design chat** with:

- Which checklist item failed (e.g. "§5: warning chevron doesn't appear")
- What you saw vs what was expected
- Planet name + module loadout when you saw it
- Screenshot helpful but not required

If everything passes, a one-liner is enough: "Manual playtest passed — full
checklist green on commit `<hash>`."

If you have followup ideas for new lander features that this surfaced (the
checklist is light on, e.g., audio feedback, particle effects on tractor
pickup, deposit kind-icons), capture them and pass them to the design chat —
this doc is the *current* feature set, not the wish list.
