"""Drev-Tok climax sim — diagnose why Drev-Tok's coalition is too strong.

Plays the canonical Final Conflict fleet matchup over many seeds:

    Drev-Tok:  DEFENDER + CLEANSER + MYCON + BURV + UTWIG
    Steward:   FURLING_SCOUT (+ ARILOU + ANDROSYNTH + MMRNMHRM
               + THINN + LEMMKIN, depending on alliance count)

Reports:
    1. Aggregate win-rate per Steward fleet size (0..5 alliances)
    2. Per-Drev-Tok-ship win-rates against the entire Steward roster
       (which Drev-Tok unit is carrying the fight?)
    3. Per-class 1v1 matchup table — Drev-Tok ship vs Steward ship,
       same conditions, find the standout.

Run:
    SDL_VIDEODRIVER=dummy python tools/sim_drev_tok.py [runs]

`runs` defaults to 30 (statistically meaningful, ~5 min wall clock).
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


# Canonical fleets per src/scz/content/final_conflict.py
DREV_TOK_IDS = (
    "defender_vessel",
    "cleanser_cruiser",
    "mycon_podship",
    "burv_broadcaster",
    "utwig_jugger",
)

# Steward fleet roster in canonical-display order (matches
# ALLIANCE_SHIP_RULES). Scout always first; allies appended.
STEWARD_FLEET_ORDER = (
    "furling_scout",
    "arilou_skiff",
    "androsynth_cruiser",
    "mmrnmhrm_sentinel",
    "thinn_blade",
    "lemmkin_skitter",
)


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


class _StubGame:
    def __init__(self):
        self.screen = pygame.Surface((1280, 720))
        self.ship_modules: dict[str, str | None] = {
            f"slot_{i+1}": None for i in range(12)
        }
        self.flags: dict = {}

    def effective_stat(self, stat: str, base: float = 0.0) -> float:
        return base

    def set_scene(self, scene):
        pass


def _fight_once(ship_a, ship_b, seed: int,
                a_state: dict | None = None,
                b_state: dict | None = None) -> dict:
    """Run one 1v1 to completion. `a_state` / `b_state` are optional
    starting overrides — `{"hull", "shield", "energy"}` for the ship
    that carried damage from a prior round. Returns winner ("A"/"B"/None)
    and the final hull/shield/energy of both ships."""
    scene = MeleeCombatScene(ship_a, ship_b, seed=seed, max_duration=80.0)
    scene.precursor.side = "_sim_a"
    scene.homesteader.side = "_sim_b"
    scene.game = _StubGame()
    scene.on_enter()
    # Apply damage carry-over (matches FleetCombatScene._on_round_finish
    # which reads the survivor's hull/shield/energy and carries them).
    if a_state is not None:
        scene.precursor.hull = float(a_state["hull"])
        scene.precursor.shield = float(a_state["shield"])
        scene.precursor.energy = float(a_state["energy"])
    if b_state is not None:
        scene.homesteader.hull = float(b_state["hull"])
        scene.homesteader.shield = float(b_state["shield"])
        scene.homesteader.energy = float(b_state["energy"])
    inp = _StubInput()
    dt = 1.0 / 60.0
    max_frames = 60 * 80
    frame = 0
    while scene.result is None and frame < max_frames:
        scene.update(dt, inp)
        frame += 1
    winner: str | None = None
    if scene.result is not None:
        if scene.result.winner_side == "_sim_a":
            winner = "A"
        elif scene.result.winner_side == "_sim_b":
            winner = "B"
    return {
        "winner": winner,
        "a_hull": max(0.0, scene.precursor.hull),
        "a_shield": max(0.0, scene.precursor.shield),
        "a_energy": max(0.0, scene.precursor.energy),
        "b_hull": max(0.0, scene.homesteader.hull),
        "b_shield": max(0.0, scene.homesteader.shield),
        "b_energy": max(0.0, scene.homesteader.energy),
    }


def _fleet_fight(fleet_a, fleet_b, seed: int) -> dict:
    """Sequential super-melee with CARRY-OVER (matches production
    FleetCombatScene._on_round_finish). The surviving ship carries
    its hull/shield/energy into the next round; the loser is
    replaced by a fresh next-in-line ship from its side.

    Returns winner, rounds, ships_left, per_ship_kills.
    """
    rng = _random.Random(seed)
    # Per-ship state — start each unit at full hull/shield/energy.
    a_remaining = [
        {"cls": s, "hull": float(s.hull_max), "shield": float(s.shield_max),
         "energy": float(s.energy_max)} for s in fleet_a
    ]
    b_remaining = [
        {"cls": s, "hull": float(s.hull_max), "shield": float(s.shield_max),
         "energy": float(s.energy_max)} for s in fleet_b
    ]
    rounds = 0
    per_ship_kills: dict[str, int] = {}
    while a_remaining and b_remaining and rounds < 30:
        a = a_remaining[0]
        b = b_remaining[0]
        r = _fight_once(a["cls"], b["cls"],
                        seed=rng.randint(0, 2**31),
                        a_state=a, b_state=b)
        rounds += 1
        if r["winner"] == "A":
            # B fleet loses ship 0; A carries its end-state to next round.
            killed = b_remaining.pop(0)
            per_ship_kills[a["cls"].id] = per_ship_kills.get(a["cls"].id, 0) + 1
            a["hull"] = r["a_hull"]
            a["shield"] = r["a_shield"]
            a["energy"] = r["a_energy"]
        elif r["winner"] == "B":
            killed = a_remaining.pop(0)
            per_ship_kills[b["cls"].id] = per_ship_kills.get(b["cls"].id, 0) + 1
            b["hull"] = r["b_hull"]
            b["shield"] = r["b_shield"]
            b["energy"] = r["b_energy"]
        else:
            # Timeout — both removed (matches the harness convention).
            a_remaining.pop(0)
            b_remaining.pop(0)
    if a_remaining and not b_remaining:
        outcome = "A"
        ships_left = len(a_remaining)
    elif b_remaining and not a_remaining:
        outcome = "B"
        ships_left = len(b_remaining)
    else:
        outcome = "TIE"
        ships_left = 0
    return {
        "winner": outcome,
        "rounds": rounds,
        "ships_left": ships_left,
        "per_ship_kills": per_ship_kills,
    }


def _ships(ids):
    return [SHIPS[i] for i in ids]


def report_aggregate_by_steward_size(runs: int) -> None:
    """Steward fleet from min (Scout only) to max (Scout + 5 allies)
    vs the fixed Drev-Tok 5. Reports Steward win-rate per fleet size.
    """
    print("\n" + "=" * 72)
    print(f"AGGREGATE — Drev-Tok 5-fleet vs Steward 1..6, {runs} runs each")
    print("=" * 72)
    print(f"{'Steward size':<14}{'Roster':<54}{'Win%':<8}{'Avg rounds':<11}{'Drev ships left (avg)':<12}")
    drev_fleet = _ships(DREV_TOK_IDS)
    for size in range(1, len(STEWARD_FLEET_ORDER) + 1):
        steward_ids = STEWARD_FLEET_ORDER[:size]
        steward = _ships(steward_ids)
        wins = 0
        losses = 0
        ties = 0
        sum_rounds = 0
        sum_drev_left_on_loss = 0
        for run_i in range(runs):
            r = _fleet_fight(steward, drev_fleet, seed=1000 + size * 1000 + run_i)
            if r["winner"] == "A":
                wins += 1
            elif r["winner"] == "B":
                losses += 1
                sum_drev_left_on_loss += r["ships_left"]
            else:
                ties += 1
            sum_rounds += r["rounds"]
        win_pct = 100.0 * wins / runs
        avg_rounds = sum_rounds / runs
        avg_drev_left = (sum_drev_left_on_loss / losses) if losses else 0.0
        roster = ", ".join(s.split("_")[0] for s in steward_ids)
        print(f"{size:<14}{roster:<54}{win_pct:<8.1f}{avg_rounds:<11.1f}{avg_drev_left:<12.2f}")


def report_per_drev_ship_carry(runs: int) -> None:
    """For each Drev-Tok ship class, how many Steward kills does it
    rack up in the canonical 5v5 (full Steward fleet)? Reveals which
    ship class is doing the heavy lifting.
    """
    print("\n" + "=" * 72)
    print(f"PER-DREV-SHIP CARRY — Drev fleet vs full Steward 6, {runs} runs")
    print("=" * 72)
    drev_fleet = _ships(DREV_TOK_IDS)
    steward = _ships(STEWARD_FLEET_ORDER)
    kill_totals: dict[str, int] = {s.id: 0 for s in drev_fleet}
    fights_alive: dict[str, int] = {s.id: 0 for s in drev_fleet}
    for run_i in range(runs):
        r = _fleet_fight(steward, drev_fleet, seed=9000 + run_i)
        for sid, kills in r["per_ship_kills"].items():
            if sid in kill_totals:
                kill_totals[sid] += kills
    print(f"{'Drev-Tok ship':<28}{'Total Steward kills':<22}{'Avg / run':<12}")
    for sid in DREV_TOK_IDS:
        kills = kill_totals[sid]
        avg = kills / runs
        ship = SHIPS[sid]
        print(f"{ship.name:<28}{kills:<22}{avg:<12.2f}")


def report_1v1_matchup_grid(runs: int) -> None:
    """Cross-table: each Drev-Tok ship class fought 1v1 vs each Steward
    ship class. Pure stat-vs-stat — no fleet sequencing, no carry-over.
    Highlights the standout offender (or the steward weakling).
    """
    print("\n" + "=" * 72)
    print(f"1v1 MATCHUP GRID — Drev-Tok vs Steward, {runs} runs each")
    print("=" * 72)
    # Header
    drev_names = [SHIPS[i].name.replace(" Vessel", "").replace("Vessel", "") for i in DREV_TOK_IDS]
    drev_names = [n[:10] for n in drev_names]
    header = f"{'Steward ship':<22}" + "".join(f"{n:<12}" for n in drev_names) + f"{'AVG':<8}"
    print(header)
    print("-" * len(header))
    rng = _random.Random(2026)
    for s_id in STEWARD_FLEET_ORDER:
        s_ship = SHIPS[s_id]
        row_vals = []
        for d_id in DREV_TOK_IDS:
            d_ship = SHIPS[d_id]
            s_wins = 0
            for run_i in range(runs):
                # Alternate which side is _sim_a per run so we don't
                # bake in side-A-favoritism (start positions etc.).
                seed = rng.randint(0, 2**31)
                if run_i % 2 == 0:
                    r = _fight_once(s_ship, d_ship, seed=seed)
                    if r["winner"] == "A":
                        s_wins += 1
                else:
                    r = _fight_once(d_ship, s_ship, seed=seed)
                    if r["winner"] == "B":
                        s_wins += 1
            pct = 100.0 * s_wins / runs
            row_vals.append(pct)
        avg = sum(row_vals) / len(row_vals)
        bits = "".join(f"{v:<12.0f}" for v in row_vals)
        name = s_ship.name.replace(" Vessel", "")[:21]
        print(f"{name:<22}{bits}{avg:<8.1f}")
    # Footer — per-Drev-ship column average (Steward win% across all
    # Steward ships against THAT Drev ship). Low column = Drev ship is
    # the strongest (Steward struggles against it).
    print("-" * len(header))
    col_avgs = []
    rng2 = _random.Random(2027)
    for d_id in DREV_TOK_IDS:
        d_ship = SHIPS[d_id]
        s_wins_total = 0
        total_fights = 0
        for s_id in STEWARD_FLEET_ORDER:
            s_ship = SHIPS[s_id]
            for run_i in range(runs):
                seed = rng2.randint(0, 2**31)
                if run_i % 2 == 0:
                    rr = _fight_once(s_ship, d_ship, seed=seed)
                    if rr["winner"] == "A":
                        s_wins_total += 1
                else:
                    rr = _fight_once(d_ship, s_ship, seed=seed)
                    if rr["winner"] == "B":
                        s_wins_total += 1
                total_fights += 1
        col_avgs.append(100.0 * s_wins_total / total_fights)
    col_bits = "".join(f"{v:<12.0f}" for v in col_avgs)
    print(f"{'(Steward W% vs col)':<22}{col_bits}")
    print("    ^ low = that Drev-Tok ship is dominating Steward roster.")


def main():
    runs = int(sys.argv[1]) if len(sys.argv) >= 2 else 30
    print(f"Running Drev-Tok climax balance sim with {runs} runs per cell")
    print(f"Drev-Tok roster: {', '.join(SHIPS[i].name for i in DREV_TOK_IDS)}")
    print(f"Steward roster:  {', '.join(SHIPS[i].name for i in STEWARD_FLEET_ORDER)}")

    report_aggregate_by_steward_size(runs)
    report_per_drev_ship_carry(runs)
    # 1v1 grid is the most expensive (6 * 5 * runs fights). Use half
    # the runs to keep wall-time sane.
    report_1v1_matchup_grid(max(10, runs // 2))


if __name__ == "__main__":
    main()
