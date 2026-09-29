"""Fleet-vs-fleet super-melee balance sim.

Per Aaron 2026-05-18: Game-Design canon is that combat encounters are
super-melees. The two typical scenarios are:

  1. The modded Scout fights ALONE against a fleet of 1-5 enemy ships.
     The Scout is the most-upgradable hull, so a well-modded Scout
     should be able to handle small fleets.

  2. The Scout + 1-4 allied fleet ships fight an enemy fleet of 1-5.
     Both sides deploy one ship at a time; on death, the next ship
     from that side enters.

This harness simulates both scenarios. For each fleet matchup it runs
a sequence of 1v1 fights (the existing MeleeCombatScene); when one
ship dies, the next from that side spawns at the same starting margin.
Fleet wins when the other side has no ships left.

Usage:
    python tools/sim_fleet.py                # default battery
    python tools/sim_fleet.py modded_scout   # scout-with-mods scenarios
    python tools/sim_fleet.py allied         # scout+allies vs enemy fleet

The harness reports win-rate, average-fight-duration, average-ships-
remaining-on-winning-side per scenario.
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

import dataclasses as _dc
from scz.combat.scene import MeleeCombatScene  # noqa: E402
from scz.combat.ships import (  # noqa: E402
    FURLING_SCOUT, SHIPS, apply_scout_mods,
    homesteader_ships, precursor_ships,
)
from scz.content.modules import MODULES  # noqa: E402


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


class _FleetGame:
    """Minimal Game stand-in. Carries a `ship_modules` dict so
    apply_scout_mods + _init_scout_mod_effects work without the full
    Game runtime. Also satisfies effective_stat lookups for the Scout's
    behavior-flag deltas (damage_reduction, bounce_chance, etc.).
    """
    def __init__(self, mods: list[str] | None = None):
        # MeleeCombatScene.on_enter reads game.screen.get_size() — give
        # it a tiny dummy surface that returns a valid size.
        self.screen = pygame.Surface((1280, 720))
        # Reserve one weapon slot, one drive, one hull, one field for
        # mods. Crew/sensor slots aren't combat-relevant.
        self.ship_modules: dict[str, str | None] = {
            "hull": None, "drive": None, "weapon": None,
            "sensor": None, "field": None,
            "crew_1": None, "crew_2": None,
        }
        if mods:
            for m_id in mods:
                m = MODULES.get(m_id)
                if m is None:
                    print(f"WARN: unknown mod id {m_id!r}")
                    continue
                slot = m.slot
                if slot in ("crew_1", "crew_2"):
                    slot = "crew_1" if self.ship_modules["crew_1"] is None else "crew_2"
                self.ship_modules[slot] = m_id
        self.flags: dict = {}

    def effective_stat(self, stat: str, base: float = 0.0) -> float:
        total = base
        for mod_id in self.ship_modules.values():
            if mod_id is None:
                continue
            mod = MODULES.get(mod_id)
            if mod is None:
                continue
            total += mod.deltas.get(stat, 0.0)
        return total

    def set_scene(self, scene):
        pass


def _fight_once(ship_a, ship_b, seed: int, game=None) -> dict:
    """Run one 1v1 fight to completion. Returns winner side ("A"/"B"),
    duration, and remaining hull/shield on both sides at fight end."""
    scene = MeleeCombatScene(ship_a, ship_b, seed=seed, max_duration=80.0)
    # _sim_a / _sim_b sides so friendly-fire filter doesn't suppress
    # damage in mirror matchups.
    scene.precursor.side = "_sim_a"
    scene.homesteader.side = "_sim_b"
    if game is None:
        game = _FleetGame()
    scene.game = game
    scene.on_enter()
    inp = _StubInput()
    dt = 1.0 / 60.0
    max_frames = 60 * 80
    frame = 0
    while scene.result is None and frame < max_frames:
        scene.update(dt, inp)
        frame += 1
    duration = frame / 60.0
    winner_side = None
    if scene.result is not None:
        if scene.result.winner_side == "_sim_a":
            winner_side = "A"
        elif scene.result.winner_side == "_sim_b":
            winner_side = "B"
    return {
        "winner": winner_side,
        "duration": duration,
        "a_hull": scene.precursor.hull,
        "a_shield": scene.precursor.shield,
        "b_hull": scene.homesteader.hull,
        "b_shield": scene.homesteader.shield,
    }


def _fleet_fight(fleet_a: list, fleet_b: list, seed: int, game_a=None) -> dict:
    """Sequential super-melee: each side has a list of ShipClass.
    A's ship 0 fights B's ship 0; loser is removed; survivor faces
    next from the other side fresh (winning ship keeps state? No —
    SC2 canon: ships keep their damage between deployments, but for
    simplicity here we reset the survivor to full hull each round.
    This is a conservative balance approximation; future iteration
    could carry-over damage.)

    Returns: winner ("A"/"B"/"TIE"), rounds_played, ships_left_winner,
    total_duration.
    """
    rng = _random.Random(seed)
    a_remaining = list(fleet_a)
    b_remaining = list(fleet_b)
    rounds = 0
    total_dur = 0.0
    last_winner = None
    while a_remaining and b_remaining and rounds < 30:
        # A always deploys the first ship in its list. game_a only
        # used for player-side Scout mods.
        a_ship = a_remaining[0]
        b_ship = b_remaining[0]
        r = _fight_once(a_ship, b_ship, seed=rng.randint(0, 2**31), game=game_a)
        total_dur += r["duration"]
        rounds += 1
        if r["winner"] == "A":
            b_remaining.pop(0)
            last_winner = "A"
        elif r["winner"] == "B":
            a_remaining.pop(0)
            last_winner = "B"
        else:
            # Timeout — count as a tie, remove both
            a_remaining.pop(0)
            b_remaining.pop(0)
    if a_remaining and not b_remaining:
        return {"winner": "A", "rounds": rounds, "ships_left": len(a_remaining), "duration": total_dur}
    if b_remaining and not a_remaining:
        return {"winner": "B", "rounds": rounds, "ships_left": len(b_remaining), "duration": total_dur}
    return {"winner": "TIE", "rounds": rounds, "ships_left": 0, "duration": total_dur}


def _enemy_fleet_pool(n: int, rng: _random.Random) -> list:
    """Pick N random enemy ships from a pool excluding Scout + tutorial
    drone. Mixes Precursor and Homesteader so fleets aren't single-faction.
    """
    pool = [s for s in SHIPS.values()
            if s.id not in ("furling_scout", "sentry_drone_47t")]
    return [rng.choice(pool) for _ in range(n)]


def scenario_solo_scout_vs_fleet(mods: list[str], fleet_sizes: list[int], runs: int = 20) -> None:
    """Modded Scout SOLO vs random enemy fleets of size 1..N."""
    print(f"\n=== Solo modded Scout vs random fleet ===")
    print(f"Mods: {', '.join(mods) if mods else '(none)'}")
    game = _FleetGame(mods)
    modded_scout = apply_scout_mods(FURLING_SCOUT, game)
    print(f"Modded Scout: hull={modded_scout.hull_max} shield={modded_scout.shield_max} "
          f"primary_pat={modded_scout.primary_pattern} special={modded_scout.special_ability}")
    print(f"{'Fleet size':<12}{'Win%':<8}{'Avg rnds':<10}{'Avg dur':<10}")
    for fleet_size in fleet_sizes:
        rng = _random.Random(42 + fleet_size)
        wins = 0
        sum_rounds = 0
        sum_dur = 0.0
        for run_i in range(runs):
            enemy_fleet = _enemy_fleet_pool(fleet_size, rng)
            result = _fleet_fight([modded_scout], enemy_fleet, seed=rng.randint(0, 2**31), game_a=game)
            if result["winner"] == "A":
                wins += 1
            sum_rounds += result["rounds"]
            sum_dur += result["duration"]
        win_pct = 100.0 * wins / runs
        avg_rounds = sum_rounds / runs
        avg_dur = sum_dur / runs
        print(f"{fleet_size:<12}{win_pct:<8.1f}{avg_rounds:<10.1f}{avg_dur:<10.1f}")


def scenario_scout_with_allies(allied_size: int, enemy_sizes: list[int], runs: int = 20,
                                mods: list[str] | None = None) -> None:
    """Scout + allies vs enemy fleet."""
    print(f"\n=== Scout + {allied_size} allies vs enemy fleet ===")
    print(f"Scout mods: {', '.join(mods) if mods else '(none)'}")
    game = _FleetGame(mods or [])
    modded_scout = apply_scout_mods(FURLING_SCOUT, game)
    allied_pool = [
        SHIPS["persuader_vessel"],
        SHIPS["arilou_skiff"],
        SHIPS["mmrnmhrm_sentinel"],
        SHIPS["proto_qor_ah"],
    ]
    print(f"{'Enemy size':<12}{'Win%':<8}{'Avg rnds':<10}{'Ships left avg':<14}")
    for enemy_size in enemy_sizes:
        rng = _random.Random(101 + enemy_size)
        wins = 0
        sum_rounds = 0
        sum_left = 0
        for run_i in range(runs):
            ally_fleet = [modded_scout] + [
                rng.choice(allied_pool) for _ in range(allied_size)
            ]
            enemy_fleet = _enemy_fleet_pool(enemy_size, rng)
            result = _fleet_fight(ally_fleet, enemy_fleet, seed=rng.randint(0, 2**31), game_a=game)
            if result["winner"] == "A":
                wins += 1
                sum_left += result["ships_left"]
            sum_rounds += result["rounds"]
        win_pct = 100.0 * wins / runs
        avg_rounds = sum_rounds / runs
        avg_left = sum_left / max(1, wins)
        print(f"{enemy_size:<12}{win_pct:<8.1f}{avg_rounds:<10.1f}{avg_left:<14.1f}")


def battery_solo_mod_compare(runs: int = 15) -> None:
    """Compare a few representative mod-loadouts vs solo enemy fleets."""
    loadouts = [
        ("vanilla",          []),
        ("damage focus",     ["mod_beam_mod_ii", "mod_hull_reinforcement", "mod_shield_capacitor", "mod_power_regenerator"]),
        ("lance sniper",     ["mod_lance_coil", "mod_sensor_array" if "mod_sensor_array" in MODULES else "mod_thruster_boost", "mod_shield_capacitor", "mod_gyro_stabilizer"]),
        ("tracking auto",    ["mod_tracking_laser", "mod_shield_catalyst", "mod_energy_cell", "mod_maneuvering_jets"]),
        ("blade brawler",    ["mod_lawnmower_disc", "mod_hull_reinforcement", "mod_repair_drone", "mod_thruster_boost"]),
        ("scatter rush",     ["mod_scatter_array", "mod_thruster_boost", "mod_maneuvering_jets", "mod_phase_skip"]),
        ("disruptor crowd",  ["mod_engine_disruptor", "mod_chaff_spray", "mod_crystalline_armor", "mod_repair_drone"]),
        ("twin spray",       ["mod_twin_beam", "mod_power_regenerator", "mod_shield_catalyst", "mod_gyro_stabilizer"]),
    ]
    fleet_sizes = [1, 2, 3, 4, 5]
    print("\n" + "=" * 70)
    print("BATTERY: Solo modded Scout vs random enemy fleets of 1..5")
    print("=" * 70)
    for name, mods in loadouts:
        scenario_solo_scout_vs_fleet(mods, fleet_sizes, runs)


def battery_scout_with_allies(runs: int = 15) -> None:
    print("\n" + "=" * 70)
    print("BATTERY: Scout + N allies vs random enemy fleet")
    print("=" * 70)
    for allied_size, enemy_sizes in (
        (1, [1, 2, 3]),
        (2, [2, 3, 4]),
        (4, [3, 4, 5]),
    ):
        scenario_scout_with_allies(allied_size, enemy_sizes, runs,
                                    mods=["mod_beam_mod_ii", "mod_shield_capacitor", "mod_thruster_boost"])


def main():
    if len(sys.argv) >= 2 and sys.argv[1] == "allied":
        battery_scout_with_allies()
        return
    if len(sys.argv) >= 2 and sys.argv[1] == "modded_scout":
        battery_solo_mod_compare()
        return
    battery_solo_mod_compare()
    battery_scout_with_allies()


if __name__ == "__main__":
    main()
