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
from scz.hyperspace.scene import HyperspaceScene


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
    game.set_scene(HyperspaceScene())
    game.run()
    return 0


if __name__ == "__main__":
    sys.exit(main())
