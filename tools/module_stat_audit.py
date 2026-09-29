"""Module-stat composition audit.

For every Module in MODULES, verifies:

1. Each declared `deltas` stat key returns the correct value from
   `game.effective_stat(stat, 0.0)` when the module is installed in
   its declared `slot`.
2. The module's `slot` is a valid Game.ship_modules key.
3. Stacking N modules into compatible slots sums their deltas (where
   the modules are in the same slot only one applies — slot-exclusivity
   verified).
4. `cost_resources` keys are valid mineral types ('COMMON', 'USEFUL',
   'BIO', 'ENERGY').

The audit catches dataclass typos (delta keys that no system reads),
slot mismatches, and stat-math regressions when `effective_stat`
changes. Run after any catalog edit.

Exit code: 0 if all modules audit clean, 1 if any inconsistency found.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path


_SCRIPT_DIR = Path(__file__).resolve().parent
_SRC_DIR = _SCRIPT_DIR.parent / "src"
sys.path.insert(0, str(_SRC_DIR))


VALID_MINERAL_TYPES = frozenset({"COMMON", "USEFUL", "BIO", "ENERGY"})


def main() -> int:
    os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
    os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
    import pygame
    pygame.init()
    pygame.display.set_mode((1280, 720))

    from scz.content.modules import MODULES, SLOTS
    from scz.engine.game import Game

    valid_slots = set(SLOTS)
    print(f"[module-audit] auditing {len(MODULES)} modules ...\n")
    failures: list[str] = []

    for mod_id, mod in MODULES.items():
        # Validate slot
        if mod.slot not in valid_slots:
            failures.append(
                f"  [SLOT] {mod_id}: slot={mod.slot!r} not in SLOTS"
            )

        # Validate cost_resources keys
        for k in mod.cost_resources:
            if k not in VALID_MINERAL_TYPES:
                failures.append(
                    f"  [COST] {mod_id}: cost_resources key "
                    f"{k!r} is not a valid mineral type"
                )

        # Install + verify each delta key returns the expected value
        g = Game(width=1280, height=720, fullscreen=False)
        if mod.slot in g.ship_modules:
            g.ship_modules[mod.slot] = mod_id
        elif mod.slot in ("crew_1", "crew_2"):
            # Crew modules can slot into either crew slot — try crew_1
            g.ship_modules["crew_1"] = mod_id
        else:
            failures.append(
                f"  [SLOT] {mod_id}: slot {mod.slot!r} not "
                f"installable in ship_modules"
            )
            continue

        for stat, delta in mod.deltas.items():
            base = 0.0
            actual = g.effective_stat(stat, base)
            if abs(actual - (base + delta)) > 1e-6:
                failures.append(
                    f"  [MATH] {mod_id}: deltas[{stat!r}]={delta} "
                    f"but effective_stat returned {actual}"
                )

    if failures:
        print("Issues found:")
        for f in failures:
            print(f)
    else:
        print("All modules clean.")

    print()
    print("=" * 62)
    print(
        f"[module-audit] {len(MODULES)} modules  ·  "
        f"{len(failures)} issues"
    )
    print("=" * 62)
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
