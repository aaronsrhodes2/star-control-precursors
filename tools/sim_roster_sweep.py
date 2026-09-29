"""Roster-wide N×N matchup sweep — find outliers across the whole roster.

Runs each pair of ships against each other for N seeds (alternating
side-A vs side-B per seed to wash out start-position bias), reports:

  - Per-ship column average win-rate (one row in the table). Ships
    outside the 35-65% band are flagged as outliers — too-strong above,
    too-weak below.
  - Diagonal self-mirror as sanity check (~50%).
  - Full grid for picking specific lopsided matchups.

Usage:
    SDL_VIDEODRIVER=dummy python tools/sim_roster_sweep.py [runs]

`runs` defaults to 10 (full N×N over 14 ships × 10 = 1960 fights ~6min).
"""

from __future__ import annotations

import os
import random as _random
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


# Skip tutorial-only / non-fightable hulls
SKIP_IDS = {"sentry_drone_47t"}

# Roster order — try to keep faction-grouped so the grid reads cleanly.
ROSTER = [
    s for sid, s in SHIPS.items() if sid not in SKIP_IDS
]


class _StubInput:
    move_x = move_y = 0.0
    confirm = cancel = False
    fire_primary = fire_secondary = False
    menu_prev = menu_next = False
    menu_up = menu_down = False
    menu_left = menu_right = False


class _StubGame:
    def __init__(self):
        self.screen = pygame.Surface((1280, 720))
        self.ship_modules = {f"slot_{i+1}": None for i in range(12)}
        self.flags: dict = {}

    def effective_stat(self, stat: str, base: float = 0.0) -> float:
        return base

    def set_scene(self, scene):
        pass


def _fight_once(ship_a, ship_b, seed: int) -> str | None:
    scene = MeleeCombatScene(ship_a, ship_b, seed=seed, max_duration=60.0)
    scene.precursor.side = "_sim_a"
    scene.homesteader.side = "_sim_b"
    scene.game = _StubGame()
    scene.on_enter()
    inp = _StubInput()
    dt = 1.0 / 60.0
    max_frames = 60 * 60
    frame = 0
    while scene.result is None and frame < max_frames:
        scene.update(dt, inp)
        frame += 1
    if scene.result is None:
        return None
    if scene.result.winner_side == "_sim_a":
        return "A"
    if scene.result.winner_side == "_sim_b":
        return "B"
    return None


def _matchup_win_rate(ship_a, ship_b, runs: int, seed_base: int) -> float:
    """Returns ship_a's win rate vs ship_b over `runs` seeds, alternating
    side assignment to wash out start-position bias. Ties count as 0.5.
    """
    a_wins = 0.0
    rng = _random.Random(seed_base)
    for i in range(runs):
        seed = rng.randint(0, 2**31)
        if i % 2 == 0:
            w = _fight_once(ship_a, ship_b, seed=seed)
            if w == "A":
                a_wins += 1
            elif w is None:
                a_wins += 0.5
        else:
            w = _fight_once(ship_b, ship_a, seed=seed)
            if w == "B":
                a_wins += 1
            elif w is None:
                a_wins += 0.5
    return a_wins / runs


def main():
    runs = int(sys.argv[1]) if len(sys.argv) >= 2 else 10
    n = len(ROSTER)
    print(f"\nRunning {n}x{n} roster sweep, {runs} runs per cell "
          f"({n * n * runs} fights total)\n")
    short_name = lambda s: s.name.replace(" Vessel", "").replace(" Cruiser", "")[:11]
    headers = [short_name(s) for s in ROSTER]

    # Grid of win rates: grid[i][j] = ship_i's win% vs ship_j
    grid = [[0.5 for _ in range(n)] for _ in range(n)]
    for i in range(n):
        for j in range(n):
            if i == j:
                # Self-mirror — run a few to confirm ~50% (skip on speed)
                continue
            if j < i:
                # Already computed as 1-grid[j][i]
                grid[i][j] = 1.0 - grid[j][i]
                continue
            wr = _matchup_win_rate(ROSTER[i], ROSTER[j], runs, seed_base=1000 * i + j)
            grid[i][j] = wr

    # Render header
    print(f"{'':<22}", end="")
    for h in headers:
        print(f"{h:<10}", end="")
    print("AVG")
    print("-" * (22 + 10 * n + 5))

    col_sums = [0.0] * n
    col_counts = [0] * n
    for i, row_ship in enumerate(ROSTER):
        row_total = 0.0
        row_count = 0
        line = f"{row_ship.name[:21]:<22}"
        for j in range(n):
            if i == j:
                line += f"{' . ':<10}"
                continue
            pct = grid[i][j] * 100
            line += f"{pct:<10.0f}"
            row_total += pct
            row_count += 1
            col_sums[j] += pct
            col_counts[j] += 1
        avg = row_total / max(1, row_count)
        marker = ""
        if avg < 35:
            marker = "  <-- UNDERPOWERED"
        elif avg > 65:
            marker = "  <-- OVERPOWERED"
        line += f"{avg:<8.1f}{marker}"
        print(line)

    # Footer — column averages (should mirror the row averages; sanity check)
    print("-" * (22 + 10 * n + 5))
    print(f"{'(inverse col avg)':<22}", end="")
    inv_col_avgs = []
    for j in range(n):
        # Each cell in row j (the column) represents "how often opponent
        # beats ship_j". So inverse is ship_j's win rate.
        col_avg = col_sums[j] / max(1, col_counts[j])
        inv = 100 - col_avg
        inv_col_avgs.append(inv)
        print(f"{inv:<10.0f}", end="")
    print()

    # Outlier summary
    print("\n" + "=" * 60)
    print("OUTLIER SUMMARY (target band 35-65%)")
    print("=" * 60)
    row_avgs = []
    for i, s in enumerate(ROSTER):
        row = grid[i]
        avg = sum(row[j] * 100 for j in range(n) if j != i) / (n - 1)
        row_avgs.append((s.name, avg, s.points, s.primary_range, s.ai_style))
    row_avgs.sort(key=lambda x: x[1])
    print(f"{'Ship':<30}{'Avg W%':<10}{'Points':<10}{'Range':<10}{'AI':<14}{'Status':<14}")
    for name, avg, pts, rng, ai in row_avgs:
        status = "OK"
        if avg < 35:
            status = "UNDERPOWERED"
        elif avg > 65:
            status = "OVERPOWERED"
        print(f"{name[:29]:<30}{avg:<10.1f}{pts:<10}{rng:<10}{ai:<14}{status:<14}")


if __name__ == "__main__":
    main()
