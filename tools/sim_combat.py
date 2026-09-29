"""Headless combat-matchup simulator.

Runs MeleeCombatScene with a stubbed input + no pygame display, advancing
the AI-driven physics until one side wins (or the fight times out).
Loops over a matrix of ship matchups, repeats each with N seeds for
variance, and writes a CSV + a human-readable summary.

This is the validation harness behind the deferred "Combat strategy
archetypes + matchup validation sweep" in memory. Use it to:

- Sanity check that no ship has a >95% win rate against another
- See whether same-side fights produce diverse winners
- Spot fights that always time out (passive AI / stalemate)
- Diff the balance before/after AI or stat changes

Usage:
    # Default: all-vs-all, 10 seeds per matchup, results to data/
    python tools/sim_combat.py

    # Specific ship-id matchup only, 50 seeds
    python tools/sim_combat.py --a furling_scout --b cleanser_cruiser --n 50

    # Limit to same-side comparisons
    python tools/sim_combat.py --mode same-side

The MeleeCombatScene `field name` precursor_ship / homesteader_ship is
misleading — it just means "ship_a" and "ship_b". This tool uses
ship_a/ship_b in its own naming.
"""

from __future__ import annotations

import argparse
import csv
import os
import statistics
import sys
import time
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path

# Resolve repo root so this script works regardless of cwd
_REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_REPO_ROOT / "src"))

# Force the dummy SDL driver before importing pygame — no window opens.
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame  # noqa: E402

# Initialize pygame BEFORE importing scenes (some modules touch fonts on import)
pygame.init()
pygame.display.set_mode((1, 1))

from scz.combat.scene import MeleeCombatScene, CombatResult, FIGHT_END_DWELL  # noqa: E402
from scz.combat.ships import SHIPS, ShipClass  # noqa: E402


# ---------------------------------------------------------------------------
# Sim primitives
# ---------------------------------------------------------------------------


class _StubInput:
    """Minimal stand-in for InputManager — combat AI doesn't read input
    on either side (both ships are AI-driven). Any access returns the
    "no input" value.
    """
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


_STUB_INPUT = _StubInput()


@dataclass
class FightOutcome:
    """One simulated fight's result, normalized for CSV output."""
    ship_a_id: str
    ship_b_id: str
    seed: int
    winner_id: str | None       # None == double-KO
    duration: float
    timed_out: bool
    a_hull_remaining: float
    a_shield_remaining: float
    b_hull_remaining: float
    b_shield_remaining: float


def simulate_fight(
    ship_a: ShipClass,
    ship_b: ShipClass,
    seed: int,
    dt: float = 1.0 / 60.0,
    max_real_seconds: float = 30.0,
) -> FightOutcome:
    """Run one 1v1 fight headlessly. Returns the FightOutcome.

    Bypasses Scene.on_enter (which requires a real screen surface for
    font setup) — neither update() nor the AI need font state.

    `max_real_seconds` is a safety guard against an unkillable bug
    looping forever. Game-time is bounded by MeleeCombatScene's own
    max_duration (default 60s) plus FIGHT_END_DWELL (2.5s) so we should
    never approach this limit in practice.
    """
    scene = MeleeCombatScene(
        precursor_ship=ship_a,
        homesteader_ship=ship_b,
        seed=seed,
    )
    # Skip on_enter — combat update() doesn't touch fonts/screen.
    # We need a `game` attribute on the scene because some code paths
    # (e.g. _finish) check self.game. Set a small shim that exposes
    # `set_scene` as a no-op so we never call into other scenes.
    scene.game = _GameShim()
    # **Critical sim invariant**: force distinct sides on the two
    # ShipState instances regardless of the ship class canon side. The
    # combat scene's projectile-vs-ship hit check filters by side
    # equality (friendly fire prevention), so two ships sharing a side
    # cannot damage each other — that's correct in canonical super-melee
    # (precursor vs homesteader) but breaks same-side matchups
    # (furling_scout vs furling_scout — both side=precursor in the
    # roster), which we very much want to be able to simulate for
    # mirror-balance sanity checks. Override here.
    scene.precursor.side = "_sim_a"
    scene.homesteader.side = "_sim_b"

    start_wall = time.monotonic()
    while scene.result is None:
        scene.update(dt, _STUB_INPUT)
        if time.monotonic() - start_wall > max_real_seconds:
            # Catastrophic wall-clock guard — should never trip
            return FightOutcome(
                ship_a_id=ship_a.id, ship_b_id=ship_b.id, seed=seed,
                winner_id=None, duration=scene.time_in_scene,
                timed_out=True,
                a_hull_remaining=scene.precursor.hull,
                a_shield_remaining=scene.precursor.shield,
                b_hull_remaining=scene.homesteader.hull,
                b_shield_remaining=scene.homesteader.shield,
            )

    r: CombatResult = scene.result
    # Map winner_side back to ship_id. With our side override the side
    # strings are "_sim_a" / "_sim_b" — winner_ship.id is still the
    # ship class id, which is what we want for stats.
    winner_id = r.winner_ship.id if r.winner_ship is not None else None
    return FightOutcome(
        ship_a_id=ship_a.id, ship_b_id=ship_b.id, seed=seed,
        winner_id=winner_id, duration=r.duration,
        timed_out=r.timed_out,
        a_hull_remaining=scene.precursor.hull,
        a_shield_remaining=scene.precursor.shield,
        b_hull_remaining=scene.homesteader.hull,
        b_shield_remaining=scene.homesteader.shield,
    )


class _GameShim:
    """Minimal Game-shaped object so MeleeCombatScene's `assert game is
    not None` checks pass during headless sim. Nothing on it is actually
    invoked by update()."""
    flags: dict[str, object] = {}
    def set_scene(self, scene) -> None:  # type: ignore[no-untyped-def]
        pass


# ---------------------------------------------------------------------------
# Sweep + reporting
# ---------------------------------------------------------------------------


def run_matchup(
    ship_a: ShipClass,
    ship_b: ShipClass,
    seeds: int,
) -> list[FightOutcome]:
    return [
        simulate_fight(ship_a, ship_b, seed=s)
        for s in range(seeds)
    ]


def sweep_all_vs_all(
    ships: list[ShipClass],
    seeds: int,
    same_side_only: bool = False,
    cross_side_only: bool = False,
    exclude_tutorial: bool = True,
) -> list[FightOutcome]:
    """Run every distinct ordered matchup. Same-pair runs are included
    by default (ship vs identical-ship is a useful symmetry check). The
    exclude_tutorial flag drops the unionized sentry drone (a deliberate
    one-trick punching bag, not a balance candidate).
    """
    ships = [s for s in ships if (not exclude_tutorial) or s.id != "sentry_drone_47t"]
    outcomes: list[FightOutcome] = []
    for a in ships:
        for b in ships:
            if same_side_only and a.side != b.side:
                continue
            if cross_side_only and a.side == b.side:
                continue
            outcomes.extend(run_matchup(a, b, seeds))
    return outcomes


def write_csv(outcomes: list[FightOutcome], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow([
            "ship_a", "ship_b", "seed", "winner", "duration_s",
            "timed_out", "a_hull", "a_shield", "b_hull", "b_shield",
        ])
        for o in outcomes:
            w.writerow([
                o.ship_a_id, o.ship_b_id, o.seed,
                o.winner_id if o.winner_id is not None else "DRAW",
                f"{o.duration:.2f}",
                "1" if o.timed_out else "0",
                f"{o.a_hull_remaining:.1f}", f"{o.a_shield_remaining:.1f}",
                f"{o.b_hull_remaining:.1f}", f"{o.b_shield_remaining:.1f}",
            ])


def summarize(outcomes: list[FightOutcome]) -> dict:
    """Aggregate per-matchup statistics. Output is a dict keyed by
    (a_id, b_id) → {a_wins, b_wins, draws, mean_duration, timeout_rate}.
    """
    summary: dict[tuple[str, str], dict] = defaultdict(lambda: {
        "n": 0, "a_wins": 0, "b_wins": 0, "draws": 0,
        "durations": [], "timeouts": 0,
    })
    for o in outcomes:
        key = (o.ship_a_id, o.ship_b_id)
        s = summary[key]
        s["n"] += 1
        if o.winner_id == o.ship_a_id:
            s["a_wins"] += 1
        elif o.winner_id == o.ship_b_id:
            s["b_wins"] += 1
        else:
            s["draws"] += 1
        s["durations"].append(o.duration)
        if o.timed_out:
            s["timeouts"] += 1

    final: dict[tuple[str, str], dict] = {}
    for key, s in summary.items():
        durs = s["durations"]
        final[key] = {
            "n": s["n"],
            "a_wins": s["a_wins"],
            "b_wins": s["b_wins"],
            "draws": s["draws"],
            "a_win_rate": s["a_wins"] / s["n"],
            "mean_duration": statistics.mean(durs) if durs else 0.0,
            "median_duration": statistics.median(durs) if durs else 0.0,
            "timeout_rate": s["timeouts"] / s["n"],
        }
    return final


def print_summary(summary: dict, top_imbalance: int = 8) -> None:
    """Print a human-readable balance report to stdout."""
    print("=" * 70)
    print(f"Matchups simulated: {len(summary)}")
    print("=" * 70)

    # 1) Symmetry check on same-pair fights (a vs a should be ~50/50)
    same_pair = {
        k: v for k, v in summary.items() if k[0] == k[1]
    }
    if same_pair:
        print("\nSAME-PAIR FIGHTS (a vs a — expect ~50% a_wins)")
        print("-" * 70)
        print(f"{'ship':28s} {'n':>4} {'a_win%':>8} {'med_dur':>8} {'to%':>6}")
        for (a, _), s in sorted(same_pair.items()):
            print(
                f"{a:28s} {s['n']:>4d} "
                f"{s['a_win_rate']*100:>7.1f}% "
                f"{s['median_duration']:>7.1f}s "
                f"{s['timeout_rate']*100:>5.1f}%"
            )

    # 2) Most-imbalanced matchups (|win_rate - 0.5| highest), excluding
    #    same-pair (those have a known bias from spawn-position chance)
    imbalanced = sorted(
        ((k, v) for k, v in summary.items() if k[0] != k[1]),
        key=lambda kv: abs(kv[1]["a_win_rate"] - 0.5),
        reverse=True,
    )
    print(f"\nMOST IMBALANCED CROSS-PAIR MATCHUPS (top {top_imbalance})")
    print("-" * 70)
    print(f"{'ship_a':22s} vs {'ship_b':22s} {'a_win%':>7} {'med_dur':>8} {'to%':>6}")
    for (a, b), s in imbalanced[:top_imbalance]:
        print(
            f"{a:22s} vs {b:22s} "
            f"{s['a_win_rate']*100:>6.1f}% "
            f"{s['median_duration']:>7.1f}s "
            f"{s['timeout_rate']*100:>5.1f}%"
        )

    # 3) Matchups that often time out — likely passive AI / stalemate
    high_timeout = sorted(
        summary.items(),
        key=lambda kv: kv[1]["timeout_rate"],
        reverse=True,
    )
    print(f"\nHIGH-TIMEOUT MATCHUPS (top {top_imbalance})")
    print("-" * 70)
    print(f"{'ship_a':22s} vs {'ship_b':22s} {'to%':>7} {'med_dur':>8}")
    for (a, b), s in high_timeout[:top_imbalance]:
        if s["timeout_rate"] == 0.0:
            break
        print(
            f"{a:22s} vs {b:22s} "
            f"{s['timeout_rate']*100:>6.1f}% "
            f"{s['median_duration']:>7.1f}s"
        )

    # 4) Win-count totals per ship (averaged win-rate-as-ship-a)
    ship_records: dict[str, list[float]] = defaultdict(list)
    for (a, b), s in summary.items():
        if a == b:
            continue
        ship_records[a].append(s["a_win_rate"])
        ship_records[b].append(1.0 - s["a_win_rate"])
    print("\nAVERAGE WIN RATE PER SHIP (across all cross-pair matchups)")
    print("-" * 70)
    print(f"{'ship':28s} {'avg_win%':>10} {'matchups':>10}")
    for ship_id, rates in sorted(
        ship_records.items(), key=lambda kv: -statistics.mean(kv[1])
    ):
        print(
            f"{ship_id:28s} "
            f"{statistics.mean(rates)*100:>9.1f}% "
            f"{len(rates):>10d}"
        )


# ---------------------------------------------------------------------------
# CLI entry
# ---------------------------------------------------------------------------


def main() -> int:
    parser = argparse.ArgumentParser(description="Headless combat sim sweep")
    parser.add_argument(
        "--a", help="ship_id A (default: all ships)", default=None,
    )
    parser.add_argument(
        "--b", help="ship_id B (default: all ships)", default=None,
    )
    parser.add_argument(
        "--n", type=int, default=10,
        help="seeds per matchup (default 10)",
    )
    parser.add_argument(
        "--mode", choices=("all", "same-side", "cross-side"), default="all",
        help="restrict matchups: all (default) | same-side | cross-side",
    )
    parser.add_argument(
        "--include-tutorial", action="store_true",
        help="include the Sentry Drone (excluded by default — it's a tutorial punching bag)",
    )
    parser.add_argument(
        "--csv", default="data/combat_sim.csv",
        help="output CSV path (default: data/combat_sim.csv)",
    )
    parser.add_argument(
        "--quiet", action="store_true",
        help="suppress the printed summary (CSV still written)",
    )
    args = parser.parse_args()

    if args.a or args.b:
        # Targeted matchup
        if not (args.a and args.b):
            print("--a and --b must both be set, or neither.")
            return 2
        if args.a not in SHIPS:
            print(f"Unknown ship_id: {args.a}. Known: {sorted(SHIPS)}")
            return 2
        if args.b not in SHIPS:
            print(f"Unknown ship_id: {args.b}. Known: {sorted(SHIPS)}")
            return 2
        outcomes = run_matchup(SHIPS[args.a], SHIPS[args.b], args.n)
    else:
        ships = list(SHIPS.values())
        outcomes = sweep_all_vs_all(
            ships, seeds=args.n,
            same_side_only=(args.mode == "same-side"),
            cross_side_only=(args.mode == "cross-side"),
            exclude_tutorial=not args.include_tutorial,
        )

    csv_path = _REPO_ROOT / args.csv
    write_csv(outcomes, csv_path)
    print(f"\nWrote {len(outcomes)} fight outcomes to {csv_path}")

    summary = summarize(outcomes)
    if not args.quiet:
        print_summary(summary)

    return 0


if __name__ == "__main__":
    sys.exit(main())
