"""Counter-matchup analyzer — does each ship have an Achilles-heel?

SC2's matchup web was famous for asymmetric counters: every ship had at
least one opponent that *hard-countered* it (Pkunk-vs-everything-fast,
Slylandro-Probe-vs-anything-slow, Spathi-Eluder-vs-anything-without-
backfire-protection, etc.). The system created tactical depth without
needing perfectly balanced 50/50 matchups everywhere.

This tool runs the same N×N matchup grid as sim_roster_sweep, then
reports the COUNTER STRUCTURE rather than the win-rate band:

  - Per-ship NEMESIS (the ship that hard-counters it — lowest win%)
  - Per-ship PREY (the ship it hard-counters — highest win%)
  - Reciprocity check: is your nemesis YOUR prey-of-your-prey? (the
    rock-paper-scissors triangle structure)
  - Coverage check: does every ship have at least one strong nemesis
    (>=65% loss rate) and one strong prey (>=65% win rate)?

A "hard counter" threshold of 65% is used (matches SC2's typical
counter strength — not a 90% wipe, but a clear tactical edge).

Usage:
    SDL_VIDEODRIVER=dummy python tools/sim_counter_analysis.py [runs]
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


SKIP_IDS = {"sentry_drone_47t"}
ROSTER = [s for sid, s in SHIPS.items() if sid not in SKIP_IDS]
HARD_COUNTER_THRESHOLD = 0.65    # 65% win = "hard counters"
SOFT_COUNTER_THRESHOLD = 0.60    # 60% = "slight edge"


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
    runs = int(sys.argv[1]) if len(sys.argv) >= 2 else 16
    n = len(ROSTER)
    print(f"\nBuilding counter-relationship grid: "
          f"{n}x{n}, {runs} runs/cell ({n*(n-1)*runs//2} fights)\n")

    # Symmetric grid: grid[i][j] = i's win rate vs j; grid[j][i] = 1-grid[i][j]
    grid: list[list[float]] = [[0.5] * n for _ in range(n)]
    for i in range(n):
        for j in range(i + 1, n):
            wr = _matchup_win_rate(ROSTER[i], ROSTER[j], runs,
                                    seed_base=1000 * i + j)
            grid[i][j] = wr
            grid[j][i] = 1.0 - wr

    # -----------------------------------------------------------------
    # Per-ship nemesis + prey
    # -----------------------------------------------------------------
    print("=" * 84)
    print("PER-SHIP ACHILLES-HEEL TABLE")
    print("=" * 84)
    print(f"{'Ship':<28}{'Nemesis (vs)':<27}{'Win%':<7}{'Prey (vs)':<24}")
    print("-" * 84)

    nemesis_of: list[tuple[int, float]] = []   # for each i: (worst_j, worst_wr)
    prey_of: list[tuple[int, float]] = []      # for each i: (best_j, best_wr)
    for i in range(n):
        row = grid[i]
        worst_j = min(range(n), key=lambda j: row[j] if j != i else 2.0)
        best_j = max(range(n), key=lambda j: row[j] if j != i else -1.0)
        nemesis_of.append((worst_j, row[worst_j]))
        prey_of.append((best_j, row[best_j]))
        ship_name = ROSTER[i].name[:27]
        nem_name = ROSTER[worst_j].name[:21]
        prey_name = ROSTER[best_j].name[:21]
        nem_loss = (1.0 - row[worst_j]) * 100
        prey_win = row[best_j] * 100
        nem_mark = " " if nem_loss < HARD_COUNTER_THRESHOLD * 100 else "*"
        prey_mark = " " if prey_win < HARD_COUNTER_THRESHOLD * 100 else "*"
        print(f"{ship_name:<28}"
              f"{nem_name:<23}{nem_mark}{nem_loss:>3.0f}% "
              f"{prey_name:<21}{prey_mark}{prey_win:>3.0f}%")
    print()
    print("(* = hard counter — >=65% one-way)")

    # -----------------------------------------------------------------
    # Counter-coverage summary
    # -----------------------------------------------------------------
    print("\n" + "=" * 84)
    print("COUNTER-COVERAGE SUMMARY")
    print("=" * 84)

    ships_with_hard_nemesis = sum(
        1 for _, wr in nemesis_of if (1.0 - wr) >= HARD_COUNTER_THRESHOLD
    )
    ships_with_hard_prey = sum(
        1 for _, wr in prey_of if wr >= HARD_COUNTER_THRESHOLD
    )
    print(f"Ships with at least one HARD NEMESIS (>=65% loss): "
          f"{ships_with_hard_nemesis}/{n}")
    print(f"Ships with at least one HARD PREY (>=65% win):     "
          f"{ships_with_hard_prey}/{n}")

    # SC2-style ideal: every ship has BOTH a hard nemesis AND a hard prey
    both = sum(
        1 for i in range(n)
        if (1.0 - nemesis_of[i][1]) >= HARD_COUNTER_THRESHOLD
        and prey_of[i][1] >= HARD_COUNTER_THRESHOLD
    )
    print(f"Ships with BOTH a hard nemesis AND a hard prey:   "
          f"{both}/{n}    "
          f"(SC2-style tactical-depth target)")

    neither = sum(
        1 for i in range(n)
        if (1.0 - nemesis_of[i][1]) < HARD_COUNTER_THRESHOLD
        and prey_of[i][1] < HARD_COUNTER_THRESHOLD
    )
    print(f"Ships with NEITHER (every fight ~50/50):          "
          f"{neither}/{n}    "
          f"(lower = more tactical variety)")

    # -----------------------------------------------------------------
    # Rock-paper-scissors triangles
    # -----------------------------------------------------------------
    # A ↦ B ↦ C ↦ A type cycles. List the strongest cycles found.
    print("\n" + "=" * 84)
    print("ROCK-PAPER-SCISSORS TRIANGLES (A beats B, B beats C, C beats A)")
    print("=" * 84)
    triangles = []
    for i in range(n):
        for j in range(n):
            if j == i:
                continue
            for k in range(n):
                if k == i or k == j:
                    continue
                wr_ij = grid[i][j]
                wr_jk = grid[j][k]
                wr_ki = grid[k][i]
                if (wr_ij >= SOFT_COUNTER_THRESHOLD
                    and wr_jk >= SOFT_COUNTER_THRESHOLD
                    and wr_ki >= SOFT_COUNTER_THRESHOLD):
                    # Strength = product of the three edges
                    strength = wr_ij * wr_jk * wr_ki
                    triangles.append((strength, i, j, k))
    triangles.sort(reverse=True)
    seen = set()
    count = 0
    for strength, i, j, k in triangles:
        # Canonical key (sorted triple) — skip rotations of triangles
        # we've already shown.
        key = tuple(sorted((i, j, k)))
        if key in seen:
            continue
        seen.add(key)
        count += 1
        if count > 10:
            break
        a = ROSTER[i].name[:16]
        b = ROSTER[j].name[:16]
        c = ROSTER[k].name[:16]
        print(f"  {a:<17} -> {b:<17} -> {c:<17} -> {a}")
        print(f"    {grid[i][j]*100:>3.0f}%       "
              f"{grid[j][k]*100:>3.0f}%       "
              f"{grid[k][i]*100:>3.0f}%       (strength: {strength:.2f})")
    if count == 0:
        print("  (no soft-or-stronger triangles found — matchups too "
              "transitive — would suggest a 'tier list' problem)")

    # -----------------------------------------------------------------
    # Mutual matchup polarity
    # -----------------------------------------------------------------
    print("\n" + "=" * 84)
    print("MATCHUP POLARITY DISTRIBUTION")
    print("=" * 84)
    bins = {"swept (>=75)": 0, "hard (65-74)": 0, "soft (55-64)": 0,
            "even (45-54)": 0}
    total_pairs = 0
    for i in range(n):
        for j in range(i + 1, n):
            total_pairs += 1
            wr = grid[i][j]
            higher = max(wr, 1.0 - wr) * 100
            if higher >= 75:
                bins["swept (>=75)"] += 1
            elif higher >= 65:
                bins["hard (65-74)"] += 1
            elif higher >= 55:
                bins["soft (55-64)"] += 1
            else:
                bins["even (45-54)"] += 1
    for label, count in bins.items():
        pct = 100.0 * count / total_pairs
        print(f"  {label:<16}{count:>4}/{total_pairs} pairs ({pct:.0f}%)")
    print()
    print("SC2 referenced ~30-40% hard-counter pairs as the 'tactical "
          "depth' target.")


if __name__ == "__main__":
    main()
