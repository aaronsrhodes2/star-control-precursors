"""Live AI-vs-AI super-melee demo.

Opens a 1280x720 window and runs a sequence of randomly-picked
1v1 combats with both sides flown by the static engine AI. When
each fight finishes, picks two new random ships and starts another.
Close the window to exit.

Usage:
    python tools/demo_ai_melee.py                     # random matchups
    python tools/demo_ai_melee.py furling_scout       # always one side is Scout
    python tools/demo_ai_melee.py cleanser cleanser   # specific matchup, loops
"""

from __future__ import annotations

import os
import random
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_REPO_ROOT / "src"))

# Do NOT set SDL_VIDEODRIVER — we want a visible window.
import pygame  # noqa: E402

from scz.combat.scene import MeleeCombatScene  # noqa: E402
from scz.combat.ships import (  # noqa: E402
    SHIPS, homesteader_ships, precursor_ships,
)
from scz.engine.game import Game  # noqa: E402


def pick_pair(force_a: str | None = None, force_b: str | None = None):
    """Pick (precursor-side, homesteader-side) ship classes for a fight.

    Always forces opposing sides via the existing engine pool. Sentry
    Drone is excluded from random picks — it's tutorial-only and dies
    in seconds.
    """
    precursor_pool = [s for s in precursor_ships() if s.id != "sentry_drone_47t"]
    homesteader_pool = [s for s in homesteader_ships() if s.id != "sentry_drone_47t"]
    if force_a and force_a in SHIPS:
        a = SHIPS[force_a]
    else:
        a = random.choice(precursor_pool)
    if force_b and force_b in SHIPS:
        b = SHIPS[force_b]
    else:
        b = random.choice(homesteader_pool)
    return a, b


def main() -> int:
    force_a = sys.argv[1] if len(sys.argv) > 1 else None
    force_b = sys.argv[2] if len(sys.argv) > 2 else None

    game = Game(
        width=1280,
        height=720,
        title="SCZ — AI Super-Melee Demo (close window to exit)",
        target_fps=60,
        fullscreen=False,
    )

    fight_count = [0]

    def start_next_fight(result=None):
        if result is not None:
            print(
                f"[fight {fight_count[0]}] {result.winner_ship.name if result.winner_ship else 'DRAW'} "
                f"wins in {result.duration:.1f}s"
                + ("  (timeout)" if result.timed_out else "")
            )
        fight_count[0] += 1
        a, b = pick_pair(force_a, force_b)
        print(f"[fight {fight_count[0]}] {a.name}  vs  {b.name}")
        scene = MeleeCombatScene(
            a, b,
            max_duration=60.0,
            on_finish=start_next_fight,
            seed=random.randint(0, 2**31 - 1),
        )
        game.set_scene(scene)

    start_next_fight()
    game.run()
    return 0


if __name__ == "__main__":
    sys.exit(main())
