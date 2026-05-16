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
        3  Star System (Sol)
        4  Planet Orbit (Sol I)
        5  Planet Surface (Sol I)
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

    # Navigate 4 entries down to "Planet Orbit (Sol I)"
    for _ in range(4):
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


# Registry — main.py uses this to look up scripts by name.
SCRIPTS = {
    "walk_tutorial_path":   walk_tutorial_path,
    "walk_orbit_and_surface": walk_orbit_and_surface,
}
