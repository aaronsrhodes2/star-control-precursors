"""Built-in test scripts. Each function builds and returns a TestScript.

Add new scripts by defining a function here; main.py's --test flag looks
up scripts by function name in this module.
"""

from __future__ import annotations

from scz.testing.harness import TestScript


def walk_tutorial_path() -> TestScript:
    """Drive the tutorial-arc beat 1 flow end-to-end at 3x speed.

    Validates: MainMenu loads → A advances to Station → Talk opens Dialog
    with Commander Halia → navigating choices works → cancel returns to
    Station → Undock leads to Hyperspace → zoom in/out works → F1/R3
    opens scene switcher → cancel closes it → exit.
    """
    s = TestScript()
    s.set_speed(3.0)
    s.log("Walk tutorial path — beat 1")

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

    # Undock — navigate to 4th menu item, confirm
    s.press("menu_down")
    s.wait(0.15)
    s.press("menu_down")
    s.wait(0.15)
    s.press("menu_down")
    s.wait(0.15)
    s.press("confirm")
    s.wait(0.6)
    s.expect_scene("HyperspaceScene")

    # Exercise zoom
    s.press("menu_prev")    # zoom out
    s.wait(0.3)
    s.press("menu_prev")
    s.wait(0.3)
    s.press("menu_next")    # zoom in
    s.wait(0.3)

    # Move the ship briefly (axis hold)
    s.move(0.0, -1.0, 0.4)  # thrust up for 0.4 s
    s.wait(0.2)

    # Open scene switcher (R3 / F1)
    s.press("open_switcher")
    s.wait(0.5)

    # Navigate down the list a few entries to prove menu nav works in the
    # switcher overlay too
    for _ in range(5):
        s.press("menu_down")
        s.wait(0.12)

    # Close switcher (B)
    s.press("cancel")
    s.wait(0.3)
    s.expect_scene("HyperspaceScene")

    # Hop back to Station via the scene switcher
    s.press("open_switcher")
    s.wait(0.5)
    # Station — Mh-Lai is entry index 4 ([4] number key)
    # The menu starts at index 0. Press down 4 times to reach Station.
    for _ in range(4):
        s.press("menu_down")
        s.wait(0.12)
    s.press("confirm")
    s.wait(0.5)
    s.expect_scene("StationScene")

    # Back to normal speed for the last second so the close is calm
    s.set_speed(1.0)
    s.log("Done walking. Test complete.")
    s.wait(1.0)
    s.end()
    return s


# Registry — main.py uses this to look up scripts by name.
SCRIPTS = {
    "walk_tutorial_path": walk_tutorial_path,
}
