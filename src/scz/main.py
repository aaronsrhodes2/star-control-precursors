"""Entry point for `python -m scz`.

For now: open a window, render the precursor-era starmap, let the player
fly a ship around with controller or keyboard. The rest of Phase 2 (system
view, planet surface, melee combat, dialog) will add scenes; this one is
the foundation.
"""

from __future__ import annotations

import argparse
import sys

from scz.engine.game import Game


def main() -> int:
    parser = argparse.ArgumentParser(prog="scz", description="Star Control Zero")
    parser.add_argument(
        "--windowed",
        action="store_true",
        help="Run in a 1280x720 window instead of 1920x1080 fullscreen",
    )
    parser.add_argument(
        "--width", type=int, default=None, help="Override logical width"
    )
    parser.add_argument(
        "--height", type=int, default=None, help="Override logical height"
    )
    parser.add_argument(
        "--scene",
        default="menu",
        choices=("menu", "hyperspace"),
        help="Which scene to launch into (default: menu). "
             "Use 'hyperspace' to skip the title screen.",
    )
    parser.add_argument(
        "--test",
        default=None,
        help="Run a built-in test script (e.g. walk_tutorial_path). "
             "The script drives input + speed; window stays interactive so "
             "you can take over by pressing buttons yourself.",
    )
    args = parser.parse_args()

    if args.windowed:
        width = args.width or 1280
        height = args.height or 720
        fullscreen = False
    else:
        width = args.width or 1920
        height = args.height or 1080
        fullscreen = True

    game = Game(
        width=width,
        height=height,
        title="Star Control Zero: The Precursors",
        target_fps=60,
        fullscreen=fullscreen,
    )

    # Attach the test script BEFORE setting the first scene — the
    # TestHarness __init__ flips campaign-manager isolation on, which
    # must be in effect when MainMenuScene.on_enter runs (it reads the
    # campaign-cache to decide menu state). If the harness is wired
    # AFTER set_scene, the initial on_enter sees stale on-disk
    # campaigns and the walks pick up garbage state on confirm.
    if args.test is not None:
        from scz.testing.harness import TestHarness
        from scz.testing.scripts import SCRIPTS
        if args.test not in SCRIPTS:
            print(f"Unknown test script: {args.test!r}")
            print(f"Available: {sorted(SCRIPTS)}")
            return 1
        script = SCRIPTS[args.test]()
        game.test_harness = TestHarness(game, script)
        print(f"[test] running {args.test} ({len(script.actions)} actions)")

    if args.scene == "hyperspace":
        from scz.hyperspace.scene import HyperspaceScene
        game.set_scene(HyperspaceScene())
    else:
        from scz.scenes.stubs import MainMenuScene
        game.set_scene(MainMenuScene())

    game.run()

    if game.test_harness is not None:
        return 0 if not game.test_harness.failures else 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
