"""Verbose per-frame trace of a single combat sim. Used to diagnose
why same-pair fights time out 100% of the time.

Usage:
    python tools/sim_combat_trace.py furling_scout furling_scout 0
"""

from __future__ import annotations

import math
import os
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_REPO_ROOT / "src"))

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame  # noqa: E402
pygame.init()
pygame.display.set_mode((1, 1))

from scz.combat.scene import MeleeCombatScene  # noqa: E402
from scz.combat.ships import SHIPS  # noqa: E402


class _StubInput:
    move_x = 0.0
    move_y = 0.0
    confirm = False
    cancel = False
    fire_primary = False
    fire_secondary = False
    menu_prev = False
    menu_next = False
    menu_up = False
    menu_down = False
    menu_left = False
    menu_right = False


class _GameShim:
    flags: dict = {}
    def set_scene(self, scene): pass


def main():
    if len(sys.argv) != 4:
        print("Usage: sim_combat_trace.py <ship_a> <ship_b> <seed>")
        return 2
    a_id, b_id, seed = sys.argv[1], sys.argv[2], int(sys.argv[3])
    if a_id not in SHIPS or b_id not in SHIPS:
        print(f"Unknown ship_id. Known: {sorted(SHIPS)}")
        return 2

    scene = MeleeCombatScene(SHIPS[a_id], SHIPS[b_id], seed=seed)
    scene.game = _GameShim()
    # Force distinct sides so same-roster-side matchups can damage each
    # other (same fix as sim_combat.py — friendly-fire filter otherwise
    # blocks all hits in mirror fights).
    scene.precursor.side = "_sim_a"
    scene.homesteader.side = "_sim_b"

    inp = _StubInput()
    dt = 1.0 / 60.0

    shots_a = 0
    shots_b = 0
    hits_on_a = 0
    hits_on_b = 0
    prev_a_hull, prev_a_shield = scene.precursor.hull, scene.precursor.shield
    prev_b_hull, prev_b_shield = scene.homesteader.hull, scene.homesteader.shield
    prev_a_alive = scene.precursor.alive
    prev_b_alive = scene.homesteader.alive

    frame = 0
    log_interval = 60  # 1 log per game-second

    print(f"=== {a_id} (A) vs {b_id} (B), seed={seed} ===")
    print(f"  arena: 1600 × 1000  ·  margin spawn at x=200 / x=1400")
    print(f"  A start: ({scene.precursor.x:.0f}, {scene.precursor.y:.0f})  "
          f"B start: ({scene.homesteader.x:.0f}, {scene.homesteader.y:.0f})")
    print()

    while scene.result is None and frame < 60 * 65:
        prev_projectiles = len(scene.projectiles)
        prev_a_hull = scene.precursor.hull
        prev_a_shield = scene.precursor.shield
        prev_b_hull = scene.homesteader.hull
        prev_b_shield = scene.homesteader.shield

        scene.update(dt, inp)
        frame += 1

        # Count new projectiles
        new_p_count = len(scene.projectiles) - (prev_projectiles - 0)
        if new_p_count > 0:
            # Hack — we can't tell whose without inspecting. Just count
            # total projectiles fired by checking the side of newly added
            for p in scene.projectiles[-new_p_count:] if new_p_count > 0 else []:
                if p.owner_side == scene.precursor.side:
                    shots_a += 1
                else:
                    shots_b += 1

        # Detect damage
        a_dmg = (prev_a_hull + prev_a_shield) - (scene.precursor.hull + scene.precursor.shield)
        b_dmg = (prev_b_hull + prev_b_shield) - (scene.homesteader.hull + scene.homesteader.shield)
        if a_dmg > 0:
            hits_on_a += 1
        if b_dmg > 0:
            hits_on_b += 1

        if frame % log_interval == 0:
            dx = scene.homesteader.x - scene.precursor.x
            dy = scene.homesteader.y - scene.precursor.y
            # account for wrap
            if abs(dx) > 800:
                dx = dx - math.copysign(1600, dx)
            if abs(dy) > 500:
                dy = dy - math.copysign(1000, dy)
            dist = math.hypot(dx, dy)
            print(
                f"t={frame/60:5.1f}s  "
                f"A=({scene.precursor.x:4.0f},{scene.precursor.y:4.0f})  "
                f"B=({scene.homesteader.x:4.0f},{scene.homesteader.y:4.0f})  "
                f"dist={dist:5.0f}  "
                f"A_HP={scene.precursor.hull:5.1f}/{scene.precursor.shield:5.1f}  "
                f"B_HP={scene.homesteader.hull:5.1f}/{scene.homesteader.shield:5.1f}  "
                f"projs={len(scene.projectiles):3d}  "
                f"shots_A={shots_a:4d}  shots_B={shots_b:4d}  "
                f"hits_on_A={hits_on_a:3d}  hits_on_B={hits_on_b:3d}"
            )

    print()
    if scene.result:
        r = scene.result
        print(f"RESULT: winner={r.winner_ship.id if r.winner_ship else 'DRAW'}  "
              f"duration={r.duration:.1f}s  timed_out={r.timed_out}")
    else:
        print("LOOP ENDED WITHOUT RESULT (frame guard)")

    print(f"Final: A_HP={scene.precursor.hull:.1f}+{scene.precursor.shield:.1f}  "
          f"B_HP={scene.homesteader.hull:.1f}+{scene.homesteader.shield:.1f}")
    print(f"Total shots fired: A={shots_a}  B={shots_b}")
    print(f"Total hit events:  A={hits_on_a}  B={hits_on_b}")
    print(f"Hit rate: A->B = {hits_on_b/max(1,shots_a)*100:.1f}%  "
          f"B->A = {hits_on_a/max(1,shots_b)*100:.1f}%")
    return 0


if __name__ == "__main__":
    sys.exit(main())
