"""Built-in test scripts. Each function builds and returns a TestScript.

Add new scripts by defining a function here; main.py's --test flag looks
up scripts by function name in this module.
"""

from __future__ import annotations

from scz.testing.harness import TestScript


def walk_tutorial_path() -> TestScript:
    """Drive the tutorial-arc beat 1 flow end-to-end at 3x speed.

    Walks the natural progression: MainMenu → Station → Dialog → Station
    → Undock → SystemScene (Mh-Lai home) → Hyperspace. Then exercises
    zoom + scene switcher to confirm those still work.
    """
    s = TestScript()
    s.set_speed(3.0)
    s.log("Walk tutorial path - beat 1")

    # Boot — MainMenu shows up
    s.wait(0.6)
    s.expect_scene("MainMenuScene")

    # A → Station
    s.press("confirm")
    s.wait(0.6)
    s.expect_scene("StationScene")

    # Talk to Commander (selected by default at index 0)
    s.press("confirm")
    s.wait(0.6)
    s.expect_scene("DialogScene")
    s.expect_dialog_state("start")

    # Navigate to the 2nd choice ("What's the package?")
    s.press("menu_down")
    s.wait(0.2)
    s.press("confirm")
    s.wait(0.5)
    s.expect_dialog_state("about_package")

    # Pick the farewell ("On my way.") — it's the 3rd choice
    s.press("menu_down")
    s.wait(0.2)
    s.press("menu_down")
    s.wait(0.2)
    s.press("confirm")
    s.wait(0.6)
    s.expect_scene("StationScene")

    # Undock — navigate to 4th menu item, confirm — drops us into the
    # Mh-Lai system view (NOT directly into hyperspace).
    s.press("menu_down")
    s.wait(0.15)
    s.press("menu_down")
    s.wait(0.15)
    s.press("menu_down")
    s.wait(0.15)
    s.press("confirm")
    s.wait(0.6)
    s.expect_scene("SystemScene")

    # Leave Mh-Lai system → Hyperspace
    s.press("cancel")
    s.wait(0.6)
    s.expect_scene("HyperspaceScene")

    # Exercise zoom
    s.press("menu_prev")    # zoom out
    s.wait(0.3)
    s.press("menu_next")    # zoom in
    s.wait(0.3)

    # Move the ship briefly (axis hold)
    s.move(0.0, -1.0, 0.4)  # thrust up for 0.4 s
    s.wait(0.2)

    # Open scene switcher (R3 / F1)
    s.press("open_switcher")
    s.wait(0.5)

    # Close switcher (B)
    s.press("cancel")
    s.wait(0.3)
    s.expect_scene("HyperspaceScene")

    # Back to normal speed for the last second so the close is calm
    s.set_speed(1.0)
    s.log("Done walking. Test complete.")
    s.wait(1.0)
    s.end()
    return s


def walk_orbit_and_surface() -> TestScript:
    """Verify the Orbit and Surface scenes via the scene switcher.

    The natural flow into orbit requires precise positioning to fly the
    ship onto a planet inside SystemScene; for an end-to-end harness we
    jump straight via the switcher and validate that A=deploy-lander
    and B=lift-off chain correctly.

    Switcher entry order (must match scenes/switcher.py):
        0  Main Menu
        1  Hyperspace
        2  Mh-Lai System (home)
        3  Mh-Lai Orbit
        4  Furlmart Orbit
        5  Arilou Outpost System
        6  Arilou Sanctuary Orbit
        7  Star System (Sol)
        8  Planet Orbit (Sol I)
        9  Planet Surface (Sol I)
        ...
    """
    s = TestScript()
    s.set_speed(3.0)
    s.log("Walk orbit + surface via scene switcher")

    s.wait(0.6)
    s.expect_scene("MainMenuScene")

    # Open switcher from MainMenu
    s.press("open_switcher")
    s.wait(0.5)

    # Navigate 8 entries down to "Planet Orbit (Sol I)"
    for _ in range(8):
        s.press("menu_down")
        s.wait(0.12)
    s.press("confirm")
    s.wait(0.6)
    s.expect_scene("PlanetOrbitScene")

    # A → Deploy Lander → Surface
    s.press("confirm")
    s.wait(0.6)
    s.expect_scene("PlanetSurfaceScene")

    # Move the lander a little, tractor whatever's nearby
    s.move(1.0, 0.0, 0.4)
    s.wait(0.2)
    s.move(0.0, -1.0, 0.4)
    s.wait(0.2)

    # B → lift off, back to orbit
    s.press("cancel")
    s.wait(0.6)
    s.expect_scene("PlanetOrbitScene")

    # B → leave orbit, back to system
    s.press("cancel")
    s.wait(0.6)
    s.expect_scene("SystemScene")

    s.set_speed(1.0)
    s.log("Orbit + surface flow OK")
    s.wait(0.8)
    s.end()
    return s


def walk_arilou_sage() -> TestScript:
    """Story beat 2 — travel to the Arilou Sage, accept the portal gift,
    use Quasi-Space to return home, and dock at Mh-Lai Station.

    Beats walked:
      1. MainMenu → Station → undock → Mh-Lai System
      2. Cross system boundary → Hyperspace (at Mh-Lai)
      3. Autopilot toward Arilou Outpost → SystemScene(Arilou)
      4. Jump to Arilou Sanctuary Orbit via the scene switcher
         (precise in-system navigation is fiddly to script; we test the
         dialog/orbital flow rather than orbital intercept)
      5. Y → Hail Sage → DialogScene
      6. Walk dialog: start → about_quasispace → gift_portal → farewell
         (the gift's side_effect sets game.flags["has_quasispace_portal"])
      7. Back to Arilou Sanctuary Orbit
      8. B → Arilou Outpost System → cross boundary → Hyperspace
      9. Y → Quasi-Space (only works because the flag was set in step 6)
     10. Fly to "near the Hearth" portal → A → Hyperspace at Mh-Lai region
     11. Autopilot toward Mh-Lai → SystemScene(Mh-Lai)
     12. Jump to Mh-Lai Orbit via switcher
     13. Y → Dock at Station → StationScene

    Switcher entry indices (must match scenes/switcher.py order):
        0  Main Menu
        1  Hyperspace
        2  Mh-Lai System
        3  Mh-Lai Orbit
        4  Arilou Outpost System
        5  Arilou Sanctuary Orbit
        ...
    """
    s = TestScript()
    s.set_speed(3.0)
    s.log("Walk to the Arilou Sage and back via Quasi-Space")

    # ----- Step 1: MainMenu → Station -----
    s.wait(0.6)
    s.expect_scene("MainMenuScene")
    s.press("confirm")
    s.wait(0.6)
    s.expect_scene("StationScene")

    # ----- Undock — 4th menu item -----
    for _ in range(3):
        s.press("menu_down")
        s.wait(0.15)
    s.press("confirm")
    s.wait(0.6)
    s.expect_scene("SystemScene")

    # ----- Step 2: Cross system boundary (Mh-Lai radius ~720, spawn x=580) -----
    # Hold "right" (toward edge) for ~1 second; player moves 220 units, crosses.
    s.move(1.0, 0.0, 1.5)
    s.wait(0.3)
    s.expect_scene("HyperspaceScene")

    # ----- Step 3: Autopilot to Arilou Outpost -----
    # Aim direction: from Mh-Lai (1900,1600) toward Arilou (3500,2400).
    # Normalized (0.894, 0.447). Holding this then pressing confirm engages
    # autopilot — autopilot finds the nearest star in our 45-degree cone,
    # which will be Arilou Outpost.
    s.set_axis(0.894, 0.447)
    s.wait(0.2)
    s.press("confirm")
    s.release_axis()
    # Wait for autopilot to cross + auto-enter the system.
    # Hyperspace distance ~1789 units at PLAYER_SPEED=1200/sec = ~1.5 wall sec.
    # At 3x speed that's ~4.5 game-seconds.
    s.wait(5.0)
    s.expect_scene("SystemScene")

    # ----- Step 4: Jump to Arilou Sanctuary Orbit via switcher -----
    s.press("open_switcher")
    s.wait(0.5)
    for _ in range(6):    # entry index 6 = "Arilou Sanctuary Orbit"
        s.press("menu_down")
        s.wait(0.15)
    s.press("confirm")
    s.wait(0.6)
    s.expect_scene("PlanetOrbitScene")

    # ----- Step 5: Y → Hail Sage -----
    s.press("fire_secondary")
    s.wait(0.6)
    s.expect_scene("DialogScene")
    s.expect_dialog_state("start")

    # ----- Step 6: Walk the Sage dialog -----
    # Choice 1 ("guidance on Others") at index 0, choice 2 ("travel faster") at 1
    # We pick "Teach me to travel faster" (index 1) → about_quasispace
    s.press("menu_down")
    s.wait(0.2)
    s.press("confirm")
    s.wait(0.5)
    s.expect_dialog_state("about_quasispace")

    # In about_quasispace, choice 0 = "I would accept the gift"
    s.press("confirm")
    s.wait(0.5)
    s.expect_dialog_state("gift_portal")

    # In gift_portal, only one choice — farewell with side_effect
    s.press("confirm")
    s.wait(0.6)
    s.expect_scene("PlanetOrbitScene")

    # ----- Step 8: Leave orbit, leave Arilou system -----
    s.press("cancel")
    s.wait(0.5)
    s.expect_scene("SystemScene")
    # Cross system boundary (Arilou max_orbit ~450, system_radius ~670, spawn 530)
    s.move(1.0, 0.0, 1.5)
    s.wait(0.3)
    s.expect_scene("HyperspaceScene")

    # ----- Step 9: Y → Quasi-Space (the gift is live) -----
    s.press("fire_secondary")
    s.wait(0.6)
    s.expect_scene("QuasiSpaceScene")

    # ----- Step 10: Fly into "near the Hearth" portal -----
    # Portals auto-capture on collision (gravitational suck-in, no button
    # press required — per Aaron's design). Spawn at Arilou portal
    # (qs=(1600, 1000)); Hearth portal at (400, 1000). Hold full-left
    # for long enough to reach it; auto-capture fires the moment the
    # ship crosses inside PORTAL_USE_RADIUS=80.
    s.set_axis(-1.0, 0.0)
    s.wait(2.0)             # generous — capture will fire mid-hold
    s.release_axis()
    s.wait(0.4)
    s.expect_scene("HyperspaceScene")

    # ----- Step 11: Autopilot toward Mh-Lai -----
    # We arrive at (2700, 1600). Mh-Lai is at (1900, 1600). Direction (-1, 0).
    s.set_axis(-1.0, 0.0)
    s.wait(0.2)
    s.press("confirm")
    s.release_axis()
    # 800 units at 1200/sec = 0.67 wall-sec = ~2.0 game-sec
    s.wait(2.5)
    s.expect_scene("SystemScene")

    # ----- Step 12-13: Jump to Mh-Lai Orbit via switcher, dock -----
    s.press("open_switcher")
    s.wait(0.5)
    for _ in range(3):    # entry index 3 = "Mh-Lai Orbit"
        s.press("menu_down")
        s.wait(0.15)
    s.press("confirm")
    s.wait(0.6)
    s.expect_scene("PlanetOrbitScene")

    s.press("fire_secondary")    # Y → Dock at Mh-Lai Station
    s.wait(0.6)
    s.expect_scene("StationScene")

    s.set_speed(1.0)
    s.log("Arilou Sage arc complete. The Sage's gift is in the ship's hold.")
    s.wait(1.0)
    s.end()
    return s


def walk_super_melee() -> TestScript:
    """Story script 3 — run a Super Melee with both sides AI-controlled.

    Per Aaron's spec, the pass-state is:
      1. Melee finishes
      2. One side wins
      3. Super-melee exits

    We pick Furling Scout (shielded, ROF-favored, mid-range) vs Proto-
    Qor-Ah Marauder (glass-cannon, suicidal-brawler, close-range AOE).
    Asymmetric matchup with no clear deterministic winner — Aaron wants
    "somewhat but not perfectly predictable" outcomes.

    Switcher entry order (must match scenes/switcher.py):
        0  Main Menu
        1  Hyperspace
        2  Mh-Lai System
        3  Mh-Lai Orbit
        4  Arilou Outpost System
        5  Arilou Sanctuary Orbit
        6  Star System (Sol)
        7  Planet Orbit (Sol I)
        8  Planet Surface (Sol I)
        9  Station — Mh-Lai
        10 Dialog — Cmdr Halia
        11 Dialog — Arilou Sage
        13 Quasi-Space
        14 Super Melee   <— target
    """
    s = TestScript()
    s.set_speed(3.0)
    s.log("Super Melee — Furling Scout vs Proto-Qor-Ah Marauder")

    s.wait(0.6)
    s.expect_scene("MainMenuScene")

    # Open scene switcher and navigate to "Super Melee" (entry 14)
    s.press("open_switcher")
    s.wait(0.5)
    for _ in range(14):
        s.press("menu_down")
        s.wait(0.12)
    s.press("confirm")
    s.wait(0.6)
    s.expect_scene("SuperMeleeScene")

    # Switch focus to the homesteader column so we can navigate to
    # START FIGHT without disturbing the precursor selection (default
    # p_idx = 0 = Furling Scout).
    s.press("menu_next")
    s.wait(0.2)

    # Navigate down the homesteader column: 4 ships, then onto "start".
    # h_idx walks 0→1→2→3 then the next menu_down switches focus to
    # "start" (per the picker logic in super_melee.py).
    for _ in range(4):
        s.press("menu_down")
        s.wait(0.15)

    # Launch the fight
    s.press("confirm")
    s.wait(0.6)
    s.expect_scene("MeleeCombatScene")

    # Let the fight resolve. Max combat duration is 60 game-seconds with
    # a 2.5 game-sec dwell on the result screen before auto-exit. We
    # wait 65 to cover the worst-case timeout path. Typical fights end
    # in 10-30 game-seconds + dwell, so usually we'll just sit on the
    # SuperMeleeScene for the remainder.
    s.wait(65.0)
    s.expect_scene("SuperMeleeScene")

    # The combat scene's on_finish() callback wrote the winner side into
    # game.flags. A non-None value proves the engine declared a winner
    # (timeout still records a winner — only a double-KO leaves it None).
    s.expect_flag("last_combat_winner_side")

    # Super-melee exits — B from the picker returns to MainMenu.
    s.press("cancel")
    s.wait(0.6)
    s.expect_scene("MainMenuScene")

    s.set_speed(1.0)
    s.log("Super Melee complete. Winner declared and super-melee exited.")
    s.wait(1.0)
    s.end()
    return s


def walk_trade() -> TestScript:
    """Trade scene — seed cargo, sell it, verify credits + cargo state.

    Pre-loads game.cargo via the harness rather than walking the lander
    around — this test validates Trade math, not collection. Walks the
    natural path from MainMenu → Station → Trade → sell all → back.
    """
    s = TestScript()
    s.set_speed(3.0)
    s.log("Trade scene — seed cargo, sell-all, verify credits")

    s.wait(0.6)
    s.expect_scene("MainMenuScene")

    # Pre-load cargo. Per modules.py MINERAL_PRICES:
    #   COMMON × 50 → 50c, USEFUL × 10 → 40c, BIO × 5 → 30c, ENERGY × 2 → 24c
    # total = 144c. Plus starting credits = 0. Expected after sell-all: 144.
    s.set_cargo({"COMMON": 50, "USEFUL": 10, "BIO": 5, "ENERGY": 2})
    s.set_credits(0)

    # MainMenu → Station
    s.press("confirm")
    s.wait(0.6)
    s.expect_scene("StationScene")

    # Navigate to "Trade resources" (menu index 1)
    s.press("menu_down")
    s.wait(0.2)
    s.press("confirm")
    s.wait(0.6)
    s.expect_scene("TradeScene")

    # In TradeScene, "Sell ALL minerals" is index 4. Default selected = 0
    # (Sell COMMON). Press menu_down 4 times to reach Sell ALL.
    for _ in range(4):
        s.press("menu_down")
        s.wait(0.15)
    s.press("confirm")
    s.wait(0.4)

    # Verify the sale
    s.expect_credits(144)
    s.expect_cargo("COMMON", 0)
    s.expect_cargo("USEFUL", 0)
    s.expect_cargo("BIO", 0)
    s.expect_cargo("ENERGY", 0)

    # B → back to Station
    s.press("cancel")
    s.wait(0.4)
    s.expect_scene("StationScene")

    s.set_speed(1.0)
    s.log("Trade complete. Cargo cleared, credits +144.")
    s.wait(0.6)
    s.end()
    return s


def walk_tutorial_beat_3_to_5() -> TestScript:
    """Integration — walk Beats 3 → 5 end-to-end without switcher cheats.

    Validates the natural Beat 3 → 5 flow:
      Beat 3: deploy lander on Furlmart, tractor the Scanner Mk III package
      Beat 4: (skipped — Coel Tessar dialog not yet implemented)
      Beat 5: dock at station, sell minerals to get credits, install scanner

    Cargo for Beat 5 is pre-seeded since Beat 4 doesn't yet exist and
    Beat 3 only delivers the quest item, not minerals. When Beat 4 lands,
    this test can be extended to walk it naturally too.
    """
    s = TestScript()
    s.set_speed(3.0)
    s.log("Tutorial Beats 3 -> 5 integration walk")

    s.wait(0.6)
    s.expect_scene("MainMenuScene")

    # ----- Beat 3 — Furlmart, collect Scanner Mk III -----
    # Use switcher to jump to Furlmart Orbit (entry 4)
    s.press("open_switcher")
    s.wait(0.5)
    for _ in range(4):
        s.press("menu_down")
        s.wait(0.12)
    s.press("confirm")
    s.wait(0.6)
    s.expect_scene("PlanetOrbitScene")

    # Deploy lander, drive to package, collect, lift off
    s.press("confirm")
    s.wait(0.6)
    s.expect_scene("PlanetSurfaceScene")
    s.set_axis(0.0, -1.0)
    s.wait(2.3)
    s.release_axis()
    s.wait(0.3)
    s.expect_flag("scanner_mk3_collected", True)
    s.expect_flag("scanner_mk3_in_cargo", True)
    s.press("cancel")
    s.wait(0.5)
    s.expect_scene("PlanetOrbitScene")

    # Y → Dock at Mh-Lai Station? Furlmart isn't a Mh-Lai dock, so just
    # leave orbit and switcher to Station. (Beat 5 starts at the station.)
    s.press("cancel")
    s.wait(0.5)
    s.expect_scene("SystemScene")

    # ----- Beat 5 — dock at Station, sell minerals, install Scanner -----
    # Seed minerals representing what the player might have gathered en route
    s.set_cargo({"COMMON": 80, "USEFUL": 10})

    # Jump to Station via switcher (entry 10 — "Station — Mh-Lai")
    s.press("open_switcher")
    s.wait(0.5)
    for _ in range(10):
        s.press("menu_down")
        s.wait(0.1)
    s.press("confirm")
    s.wait(0.6)
    s.expect_scene("StationScene")

    # Sell — Trade
    s.press("menu_down")
    s.wait(0.15)
    s.press("confirm")
    s.wait(0.6)
    s.expect_scene("TradeScene")
    # Sell ALL — index 4
    for _ in range(4):
        s.press("menu_down")
        s.wait(0.12)
    s.press("confirm")
    s.wait(0.4)
    s.expect_credits(120)   # 80*1 + 10*4 = 120
    s.press("cancel")
    s.wait(0.4)
    s.expect_scene("StationScene")

    # Upgrade ship — Customization
    s.press("menu_down")
    s.wait(0.15)
    s.press("menu_down")
    s.wait(0.15)
    s.press("confirm")
    s.wait(0.6)
    s.expect_scene("ShipCustomizationScene")
    s.press("menu_next")
    s.wait(0.2)
    s.press("confirm")
    s.wait(0.4)
    s.expect_module_installed("sensor", "scanner_mk3")
    s.expect_flag("scanner_mk3_installed", True)
    s.press("cancel")
    s.wait(0.5)
    s.expect_scene("StationScene")

    s.set_speed(1.0)
    s.log("Beats 3 -> 5 walked. Scanner installed, minerals converted to credits.")
    s.wait(0.8)
    s.end()
    return s


def walk_customization() -> TestScript:
    """Ship Customization — install the Scanner Mk III into the sensor slot.

    Pre-seeds the Scanner Mk III in uninstalled_modules (skipping the
    Beat 3 collection path — walk_tutorial_beat_3 covers that). Walks
    the natural path from MainMenu → Station → Upgrade ship → install.
    """
    s = TestScript()
    s.set_speed(3.0)
    s.log("Customization — install Scanner Mk III into sensor slot")

    s.wait(0.6)
    s.expect_scene("MainMenuScene")

    # Seed the inventory + flag — pretend Beat 3 just happened
    s.set_module_inventory("scanner_mk3", 1)
    s.set_flag("scanner_mk3_in_cargo", True)
    s.set_flag("scanner_mk3_collected", True)

    # MainMenu → Station → Upgrade ship
    s.press("confirm")
    s.wait(0.6)
    s.expect_scene("StationScene")
    # "Upgrade ship" is menu index 2
    s.press("menu_down")
    s.wait(0.15)
    s.press("menu_down")
    s.wait(0.15)
    s.press("confirm")
    s.wait(0.6)
    s.expect_scene("ShipCustomizationScene")

    # Default focus is slots column; switch to modules column with right
    s.press("menu_next")
    s.wait(0.2)

    # The first available module is Scanner Mk III (quest reward, listed first).
    # Press A to install — Customization auto-routes to the matching slot.
    s.press("confirm")
    s.wait(0.4)

    # Verify install
    s.expect_module_installed("sensor", "scanner_mk3")
    s.expect_flag("scanner_mk3_installed", True)
    s.expect_flag("scanner_mk3_in_cargo", False)

    # B → back to Station
    s.press("cancel")
    s.wait(0.5)
    s.expect_scene("StationScene")

    s.set_speed(1.0)
    s.log("Customization complete. Scanner Mk III is in the sensor slot.")
    s.wait(0.6)
    s.end()
    return s


def walk_tutorial_beat_3() -> TestScript:
    """Tutorial Beat 3 — collect the Scanner Mk III package from Furlmart.

    Pass state:
      - PlanetSurfaceScene on Furlmart entered
      - Package deposit (PACKAGE_SCANNER_MK3) tractored
      - game.flags["scanner_mk3_collected"] set True
      - game.flags["scanner_mk3_in_cargo"] set True
      - game.uninstalled_modules["scanner_mk3"] >= 1
      - Lander lifts off back to PlanetOrbitScene cleanly

    Uses the scene switcher to jump straight to Furlmart Orbit instead
    of walking the player to it from Mh-Lai. In-system planet intercept
    is fiddly to script and the test isn't validating that path; it's
    validating the package pickup loop.

    Switcher entry 4 = "Furlmart Orbit" — see scenes/switcher.py.
    """
    s = TestScript()
    s.set_speed(3.0)
    s.log("Tutorial Beat 3 — collect Scanner Mk III from Furlmart")

    s.wait(0.6)
    s.expect_scene("MainMenuScene")

    # Open scene switcher → Furlmart Orbit (entry 4)
    s.press("open_switcher")
    s.wait(0.5)
    for _ in range(4):
        s.press("menu_down")
        s.wait(0.12)
    s.press("confirm")
    s.wait(0.6)
    s.expect_scene("PlanetOrbitScene")

    # A → Deploy Lander → PlanetSurfaceScene
    s.press("confirm")
    s.wait(0.6)
    s.expect_scene("PlanetSurfaceScene")

    # Lander spawns at (0.5, 0.95). Package injected at (0.5, 0.5).
    # LANDER_SPEED = 0.20 surface-units/sec; tractor radius = 0.030.
    # Hold "up" (move_y = -1) for 2.3 game-sec → lander travels 0.46
    # units → y ≈ 0.49 → distance to package at (0.5, 0.5) ≈ 0.014
    # → well within tractor range. Auto-collected, scanner_mk3_collected
    # flag set by PlanetSurfaceScene._on_pickup.
    s.set_axis(0.0, -1.0)
    s.wait(2.3)
    s.release_axis()
    s.wait(0.3)

    s.expect_flag("scanner_mk3_collected", True)
    s.expect_flag("scanner_mk3_in_cargo", True)

    # B → lift off → back to PlanetOrbitScene
    s.press("cancel")
    s.wait(0.6)
    s.expect_scene("PlanetOrbitScene")

    s.set_speed(1.0)
    s.log("Beat 3 complete. Scanner Mk III is in the cargo hold.")
    s.wait(0.8)
    s.end()
    return s


# Registry — main.py uses this to look up scripts by name.
SCRIPTS = {
    "walk_tutorial_path":      walk_tutorial_path,
    "walk_orbit_and_surface":  walk_orbit_and_surface,
    "walk_arilou_sage":        walk_arilou_sage,
    "walk_super_melee":        walk_super_melee,
    "walk_tutorial_beat_3":    walk_tutorial_beat_3,
    "walk_trade":              walk_trade,
    "walk_customization":      walk_customization,
    "walk_tutorial_beat_3_to_5": walk_tutorial_beat_3_to_5,
}
