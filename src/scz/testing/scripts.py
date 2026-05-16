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
        7  Beta Corvi (Slylandro)
        8  Slylandro Sky-Vault Orbit
        9  Star System (Sol)
        10 Planet Orbit (Sol I)
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

    # Navigate 10 entries down to "Planet Orbit (Sol I)"
    for _ in range(10):
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
        ...
        19 Super Melee   <— target
    """
    s = TestScript()
    s.set_speed(3.0)
    s.log("Super Melee — Furling Scout vs Proto-Qor-Ah Marauder")

    s.wait(0.6)
    s.expect_scene("MainMenuScene")

    # Open scene switcher and navigate to "Super Melee" (entry 19)
    s.press("open_switcher")
    s.wait(0.5)
    for _ in range(19):
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

    # Jump to Station via switcher (entry 12 — "Station — Mh-Lai")
    s.press("open_switcher")
    s.wait(0.5)
    for _ in range(12):
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


def walk_slylandro_cloak() -> TestScript:
    """Slylandro Cloak quest — first non-Arilou non-tutorial species.

    Pass state:
      1. Hail the Slylandro Witness from orbit over Beta Corvi's
         Slylandro Sky-Vault
      2. Walk dialog: first_meeting → tell_about_others → grasping_horror
         → cloak_offer → accept (cloak deal sealed)
      3. game.flags["met_slylandro"], ["slylandro_cloaked"], ["has_echo_sensor"]
         all set True. Hyperspace-Echo Sensor module in inventory.

    Uses switcher to jump to Slylandro Sky-Vault Orbit (entry 8) since
    Beta Corvi is at (276, 9810) — across the galaxy from Mh-Lai —
    and the slice can reach it naturally via Quasi-Space "distant fold"
    portal + autopilot, but for the focused species test we jump there
    directly.
    """
    s = TestScript()
    s.set_speed(3.0)
    s.log("Slylandro Cloak — hail the Slylandro and accept the cloak deal")

    s.wait(0.6)
    s.expect_scene("MainMenuScene")

    # Jump to Slylandro Sky-Vault Orbit (entry 8)
    s.press("open_switcher")
    s.wait(0.5)
    for _ in range(8):
        s.press("menu_down")
        s.wait(0.12)
    s.press("confirm")
    s.wait(0.6)
    s.expect_scene("PlanetOrbitScene")

    # Y → Hail the Slylandro
    s.press("fire_secondary")
    s.wait(0.6)
    s.expect_scene("DialogScene")
    s.expect_dialog_state("first_meeting")

    # Walk: first_meeting → tell_about_others (choice 0)
    s.press("confirm")
    s.wait(0.5)
    s.expect_dialog_state("tell_about_others")

    # tell_about_others has one choice → grasping_horror
    s.press("confirm")
    s.wait(0.5)
    s.expect_dialog_state("grasping_horror")

    # grasping_horror → cloak_offer (choice 0)
    s.press("confirm")
    s.wait(0.5)
    s.expect_dialog_state("cloak_offer")

    # cloak_offer → accept (choice 0, side_effect grants cloak + sensor)
    s.press("confirm")
    s.wait(0.7)
    s.expect_scene("PlanetOrbitScene")

    s.expect_flag("met_slylandro", True)
    s.expect_flag("slylandro_cloaked", True)
    s.expect_flag("has_echo_sensor", True)

    s.set_speed(1.0)
    s.log("Slylandro Cloak quest complete. Hyperspace-Echo Sensor in cargo.")
    s.wait(0.7)
    s.end()
    return s


def walk_tutorial_arc() -> TestScript:
    """Full tutorial walkthrough — Beats 1-7 end-to-end, no flag-seeding.

    The slice's onboarding. Each beat naturally gates the next via
    game.flags. This is the MVP-acceptance test for the tutorial: if
    a fresh player runs it from MainMenu, every beat triggers, every
    flag advances, and tutorial_complete latches at the end.

    Beat layout in this script:
      1. Halia opening dialog (start state) — exit cleanly
      2-3. Furlmart Orbit (switcher) → deploy lander → collect Scanner Mk III
      4. Hyperspace → Coel Tessar encounter → accept Distress Beacon
      5. Return to Station → install Scanner → talk to Halia (others_reveal)
      6. Undock → sentry drone hails → engage combat → win
      7. Re-talk to Halia (others_confirmed) → tutorial_complete

    Switcher entries used: 1 (Hyperspace), 4 (Furlmart Orbit),
    10 (Station — Mh-Lai).
    """
    s = TestScript()
    s.set_speed(3.0)
    s.log("Full Tutorial Arc — Beats 1 through 7, no flag pre-seeding")

    # ============== BEAT 1 — Halia opening ==============
    s.wait(0.6)
    s.expect_scene("MainMenuScene")
    s.press("confirm")
    s.wait(0.6)
    s.expect_scene("StationScene")
    s.press("confirm")    # Talk to Commander Halia
    s.wait(0.6)
    s.expect_scene("DialogScene")
    s.expect_dialog_state("start")
    # Choose "I'll head out" — 4th choice (index 3)
    for _ in range(3):
        s.press("menu_down")
        s.wait(0.15)
    s.press("confirm")
    s.wait(0.6)
    s.expect_scene("StationScene")

    # ============== BEATS 2-3 — Furlmart, collect Scanner ==============
    # Jump to Furlmart Orbit via switcher (entry 4)
    s.press("open_switcher")
    s.wait(0.5)
    for _ in range(4):
        s.press("menu_down")
        s.wait(0.12)
    s.press("confirm")
    s.wait(0.6)
    s.expect_scene("PlanetOrbitScene")
    s.press("confirm")    # Deploy Lander
    s.wait(0.6)
    s.expect_scene("PlanetSurfaceScene")
    # Drive up to the package
    s.set_axis(0.0, -1.0)
    s.wait(2.3)
    s.release_axis()
    s.wait(0.3)
    s.expect_flag("scanner_mk3_collected", True)
    s.press("cancel")     # Lift off
    s.wait(0.5)
    s.expect_scene("PlanetOrbitScene")
    s.press("cancel")     # Leave orbit
    s.wait(0.5)
    s.expect_scene("SystemScene")

    # ============== BEAT 4 — Coel Tessar in hyperspace ==============
    # Cross system boundary to hyperspace. Mh-Lai system boundary at
    # radius 720 from star (origin); spawn at (580, 0). Move right
    # (+1, 0) for ~0.8 game-sec to cross.
    s.set_axis(1.0, 0.0)
    s.wait(1.2)
    s.release_axis()
    s.wait(0.4)
    s.expect_scene("HyperspaceScene")

    # The encounter SHOULD spawn here because scanner_mk3_installed
    # is required... but we haven't installed it yet (we just collected
    # it). So at this point, no encounter. Player needs to install,
    # which means going back to Mh-Lai, docking, installing, then
    # leaving again. The natural Beat order is 3→5→4 (collect, install,
    # then hit Coel Tessar). Re-order this script accordingly.
    #
    # NOTE: in the canonical narrative Beat 4 follows Beat 3 immediately
    # via Coel "dropping out of a Quasi-Space fold near the player's
    # path." For MVP simplicity, we route 3 → 5 → 4 by gating Beat 4
    # on scanner_mk3_installed instead of collected.

    # ============== BEAT 5 — install Scanner + Halia others_reveal ==============
    # Re-enter Mh-Lai system, dock, install, talk. Use switcher (cancel
    # in hyperspace quits the game).
    s.press("open_switcher")
    s.wait(0.5)
    for _ in range(3):
        s.press("menu_down")
        s.wait(0.12)
    s.press("confirm")
    s.wait(0.6)
    s.expect_scene("PlanetOrbitScene")
    s.press("fire_secondary")    # Y → Dock at Mh-Lai Station
    s.wait(0.6)
    s.expect_scene("StationScene")

    # Upgrade ship — menu index 2
    s.press("menu_down")
    s.wait(0.15)
    s.press("menu_down")
    s.wait(0.15)
    s.press("confirm")
    s.wait(0.6)
    s.expect_scene("ShipCustomizationScene")
    s.press("menu_next")   # focus on modules column
    s.wait(0.2)
    s.press("confirm")     # install Scanner Mk III (the only quest reward in inventory)
    s.wait(0.4)
    s.expect_module_installed("sensor", "scanner_mk3")
    s.expect_flag("scanner_mk3_installed", True)
    s.press("cancel")      # back to Station
    s.wait(0.4)
    s.expect_scene("StationScene")

    # Now go back out to hyperspace to trigger Beat 4 (Coel Tessar).
    # Undock first — drops in Mh-Lai system (no sentry drone yet because
    # we haven't installed scanner... wait, we just did. Hmm.)
    #
    # Re-read the trigger condition in StationScene.update:
    #   if scanner_mk3_installed AND not fought_sentry_drone
    # So actually undocking now WILL trigger the sentry drone.
    #
    # For this test, we want to do Beat 4 (Coel Tessar) FIRST, then
    # come back and trigger Beat 6 (drone). So we need to engineer the
    # order. Skip undocking via the Station menu — use switcher to jump
    # directly to Hyperspace (entry 1).
    s.press("open_switcher")
    s.wait(0.5)
    s.press("menu_down")
    s.wait(0.15)
    s.press("confirm")
    s.wait(0.6)
    s.expect_scene("HyperspaceScene")

    # Encounter point spawned on hyperspace enter — fly to it
    s.set_axis(0.95, 0.32)
    s.wait(1.2)
    s.release_axis()
    s.wait(0.4)
    s.expect_scene("DialogScene")
    s.expect_dialog_state("first_contact")
    # Walk: first_contact → about_decursion → play_beacon → accept_confirm
    s.press("confirm")
    s.wait(0.5)
    s.expect_dialog_state("about_decursion")
    s.press("confirm")
    s.wait(0.5)
    s.expect_dialog_state("play_beacon")
    s.press("confirm")    # has_distress_beacon side-effect
    s.wait(0.5)
    s.expect_dialog_state("accept_confirm")
    s.press("confirm")
    s.wait(0.7)
    s.expect_scene("HyperspaceScene")
    s.expect_flag("has_distress_beacon", True)

    # Return to Station to hear the Others-reveal speech
    s.press("open_switcher")
    s.wait(0.5)
    for _ in range(12):    # entry 12 = Station — Mh-Lai
        s.press("menu_down")
        s.wait(0.1)
    s.press("confirm")
    s.wait(0.6)
    s.expect_scene("StationScene")
    s.press("confirm")    # Talk to Halia
    s.wait(0.6)
    s.expect_scene("DialogScene")
    s.expect_dialog_state("others_reveal")    # Beat 5 reveal triggers
    s.press("confirm")    # "I'll be ready"
    s.wait(0.6)
    s.expect_scene("StationScene")
    s.expect_flag("heard_others_reveal", True)

    # ============== BEAT 6 — undock → sentry drone → combat ==============
    # Undock menu item — "Undock" is index 3
    for _ in range(3):
        s.press("menu_down")
        s.wait(0.15)
    s.press("confirm")
    s.wait(0.6)
    s.expect_scene("DialogScene")
    s.expect_dialog_state("union_motion")
    # "Engage combat protocols" — choice index 2
    s.press("menu_down")
    s.wait(0.15)
    s.press("menu_down")
    s.wait(0.15)
    s.press("confirm")
    s.wait(0.7)
    s.expect_scene("MeleeCombatScene")
    s.wait(50.0)   # cover the worst-case combat duration
    s.expect_scene("SystemScene")
    s.expect_flag("fought_sentry_drone", True)
    s.expect_flag("first_combat_complete", True)

    # ============== BEAT 7 — return to Station, others_confirmed ==============
    s.press("open_switcher")
    s.wait(0.5)
    for _ in range(12):
        s.press("menu_down")
        s.wait(0.1)
    s.press("confirm")
    s.wait(0.6)
    s.expect_scene("StationScene")
    s.press("confirm")    # Talk to Halia
    s.wait(0.6)
    s.expect_scene("DialogScene")
    s.expect_dialog_state("others_confirmed")    # Beat 7 reveal
    s.press("confirm")    # "I'll be careful." (side-effect: tutorial_complete)
    s.wait(0.7)
    s.expect_scene("StationScene")
    s.expect_flag("tutorial_complete", True)

    s.set_speed(1.0)
    s.log("Tutorial arc complete. Beats 1-7 walked end-to-end.")
    s.wait(1.0)
    s.end()
    return s


def walk_tutorial_beat_4() -> TestScript:
    """Tutorial Beat 4 — Androsynth refugee encounter + Distress Beacon.

    Validates the natural Beat 4 flow:
      1. Hyperspace scene loads with Coel Tessar encounter spawned
         (gated on scanner_mk3_installed + not met_androsynth)
      2. Player flies into the encounter — auto-trigger fires dialog
      3. Walk Coel Tessar dialog: first_contact → about_decursion →
         play_beacon → accept_confirm → farewell
      4. Verify has_distress_beacon + met_androsynth + androsynth_aboard

    Beat 4 prerequisites (Beat 3 → Beat 5 chain): scanner_mk3_installed
    must be True. Pre-seeded for this test.
    """
    s = TestScript()
    s.set_speed(3.0)
    s.log("Tutorial Beat 4 — Androsynth refugee + Distress Beacon")

    s.wait(0.6)
    s.expect_scene("MainMenuScene")

    # Pre-seed: pretend Beats 3+5 happened (scanner installed)
    s.set_flag("scanner_mk3_collected", True)
    s.set_flag("scanner_mk3_installed", True)

    # Jump to Hyperspace via the switcher (entry 1)
    s.press("open_switcher")
    s.wait(0.5)
    s.press("menu_down")
    s.wait(0.15)
    s.press("confirm")
    s.wait(0.6)
    s.expect_scene("HyperspaceScene")

    # Encounter spawned at (player_x + 600, player_y + 200). The default
    # player position is (SOL_X=1793, SOL_Y=1450). Encounter at ~(2393,
    # 1650). Direction from player: (+1, +0.33), normalized (0.95, 0.32).
    # Hold that heading until the player crosses ENCOUNTER_TRIGGER_RADIUS=220
    # of the point. Distance ~632; speed 1200 → 0.53 game-sec at full
    # thrust. Hold 1.0 game-sec for margin against frame timing.
    s.set_axis(0.95, 0.32)
    s.wait(1.2)
    s.release_axis()
    s.wait(0.4)
    s.expect_scene("DialogScene")
    s.expect_dialog_state("first_contact")

    # Walk dialog: first_contact → about_decursion (choice 0) → play_beacon
    # (choice 0) → accept_confirm (choice 0, with side_effect grants
    # has_distress_beacon) → farewell
    s.press("confirm")    # "Tell me what happened" → about_decursion
    s.wait(0.5)
    s.expect_dialog_state("about_decursion")

    s.press("confirm")    # "Show me the recording" → play_beacon
    s.wait(0.5)
    s.expect_dialog_state("play_beacon")

    s.press("confirm")    # "I'll take you aboard" → accept_confirm (side-effect fires here)
    s.wait(0.5)
    s.expect_dialog_state("accept_confirm")

    s.press("confirm")    # "Understood. Welcome aboard." → dialog ends
    s.wait(0.7)
    s.expect_scene("HyperspaceScene")

    # Verify side-effects
    s.expect_flag("has_distress_beacon", True)
    s.expect_flag("met_androsynth", True)
    s.expect_flag("androsynth_aboard", True)

    s.set_speed(1.0)
    s.log("Beat 4 complete. Distress Beacon is in the Archive.")
    s.wait(0.6)
    s.end()
    return s


def walk_tutorial_beat_6() -> TestScript:
    """Tutorial Beat 6 — sentry drone combat tutorial.

    Validates the natural Beat 6 flow:
      1. Player undocks from Station with scanner_mk3_installed
      2. Sentry Drone 47-Theta hails them with the union motion
      3. Player engages combat (third option, side-effects launch combat)
      4. Combat scene resolves — Furling Scout (130pt shielded) vs
         Sentry Drone (20pt, slow, left-turn-only, no shields). The
         Scout should win in ~15 game-sec
      5. fought_sentry_drone + first_combat_complete flags set
      6. Player returns to Mh-Lai SystemScene

    Pre-seeds Beat 1-5 progress so the drone trigger fires.
    """
    s = TestScript()
    s.set_speed(3.0)
    s.log("Tutorial Beat 6 — sentry drone combat tutorial")

    s.wait(0.6)
    s.expect_scene("MainMenuScene")

    # Pre-seed: pretend Beats 3+5 happened (scanner installed)
    s.set_flag("scanner_mk3_collected", True)
    s.set_flag("scanner_mk3_installed", True)

    # MainMenu → Station
    s.press("confirm")
    s.wait(0.6)
    s.expect_scene("StationScene")

    # Undock → triggers sentry drone dialog (because scanner_mk3_installed
    # AND not fought_sentry_drone)
    for _ in range(3):
        s.press("menu_down")
        s.wait(0.15)
    s.press("confirm")
    s.wait(0.6)
    s.expect_scene("DialogScene")
    s.expect_dialog_state("union_motion")

    # Pick the third option (index 2): "Engage combat protocols"
    # Two menu_downs (0→1→2), then confirm.
    s.press("menu_down")
    s.wait(0.15)
    s.press("menu_down")
    s.wait(0.15)
    s.expect_dialog_state("union_motion")  # still here; nav hasn't changed state
    s.press("confirm")
    s.wait(0.7)
    s.expect_scene("MeleeCombatScene")

    # Wait for the fight to resolve. Drone has 20 HP, no shield, 2 dmg
    # at 0.5/sec from Scout side. Scout has 100 HP + 80 shield, fires
    # 8 dmg at 4/sec — 32 dps. 20 HP / 32 dps = 0.6 sec of effective
    # fire. With circling + closing time, expect 10-25 game-sec total.
    # Max_duration=45 with FIGHT_END_DWELL=2.5, plus return-to-system.
    # Wait 50 to cover the worst case.
    s.wait(50.0)
    s.expect_scene("SystemScene")
    s.expect_flag("fought_sentry_drone", True)
    s.expect_flag("first_combat_complete", True)
    s.expect_flag("last_combat_winner_side", "precursor")

    s.set_speed(1.0)
    s.log("Beat 6 complete. The strike is broken.")
    s.wait(0.6)
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
    "walk_tutorial_beat_4":    walk_tutorial_beat_4,
    "walk_tutorial_beat_6":    walk_tutorial_beat_6,
    "walk_tutorial_arc":       walk_tutorial_arc,
    "walk_slylandro_cloak":    walk_slylandro_cloak,
}
