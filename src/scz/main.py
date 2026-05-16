"""Entry point for `python -m scz`.

For now: open a window, render the precursor-era starmap, let the player
fly a ship around with controller or keyboard. The rest of Phase 2 (system
view, planet surface, melee combat, dialog) will add scenes; this one is
the foundation.
"""

from __future__ import annotations

import sys

from scz.engine.game import Game
from scz.hyperspace.scene import HyperspaceScene


def main() -> int:
    game = Game(
        width=1280,
        height=720,
        title="Star Control Zero: The Precursors",
        target_fps=60,
    )
    game.set_scene(HyperspaceScene())
    game.run()
    return 0


if __name__ == "__main__":
    sys.exit(main())
