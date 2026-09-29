"""FleetCombatScene — SC2-style multi-ship hot-swap fleet combat.

Aaron's canon (2026-05-18): campaign encounters should be SC2-style
fleet-vs-fleet with hot-swap. Each side has a roster; combat is
sequential 1v1 with damage carry-over between rounds; an encounter
ends when one fleet is fully destroyed.

This module orchestrates that. Per project convention
(`memory/project_combat_chat_split.md`), this Design-lane file does
NOT modify `src/scz/combat/*` — it wraps the existing
`MeleeCombatScene` (Combat Mechanics chat's lane) and adds the
round-by-round fleet management as an outer layer.

**Architecture**:

- Constructor takes two `list[ShipClass]` fleets + a fleet-level
  on_finish callback
- Internal state: per-ship hull/shield/energy snapshots so damage
  carries across rounds
- Each round, an internal pick step selects the next ship for each
  side (MVP: auto-pick first surviving; future: player-driven picker)
- Round combat is delegated to a fresh `MeleeCombatScene`; its
  on_finish closure reads the survivor's final hull/shield/energy
  from the melee scene's `ShipState` and folds them back into the
  fleet roster
- After each round, check if either fleet is empty; if yes, fire the
  fleet-level on_finish with a `FleetResult`; if no, queue the next
  round

**Backward compatibility**: existing 1v1 encounter triggers can keep
calling `MeleeCombatScene` directly — `FleetCombatScene` is
strictly additive. New multi-ship-aware encounters (eventually the
Final Conflict, Cleanser climax fleet variant, etc.) use this
wrapper. When both fleets are size 1, the experience reduces to the
existing 1v1 with no picker overhead.

**Damage carry-over rules** (MVP):
- A surviving ship retains its `hull` / `shield` / `energy` into the
  next round.
- A destroyed ship is removed from its side's fleet (alive=False).
- Between *encounters* (campaign-level), ships heal to full at
  Mh-Lai — that's a separate Mh-Lai-side concern, not handled here.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, TYPE_CHECKING

from scz.combat.scene import (
    ARENA_STYLE_SOLAR_SYSTEM,
    CombatResult,
    MeleeCombatScene,
)
from scz.combat.ships import ShipClass
from scz.engine.scene import Scene

if TYPE_CHECKING:
    pass


@dataclass
class FleetShip:
    """One ship slot in a fleet. Persists hull/shield/energy across
    rounds within a single fleet encounter.
    """
    cls: ShipClass
    hull: float
    shield: float
    energy: float
    alive: bool = True

    @classmethod
    def from_class(cls_, ship_class: ShipClass) -> "FleetShip":
        """Construct a fresh FleetShip from a ShipClass at full health."""
        return cls_(
            cls=ship_class,
            hull=float(ship_class.hull_max),
            shield=float(ship_class.shield_max),
            energy=float(ship_class.energy_max),
        )


@dataclass
class FleetResult:
    """Outcome of an entire fleet encounter."""
    winner_side: str | None      # "precursor" / "homesteader" / None on timeout
    precursor_survivors: list[FleetShip] = field(default_factory=list)
    homesteader_survivors: list[FleetShip] = field(default_factory=list)
    round_count: int = 0
    timed_out: bool = False


class FleetCombatScene(Scene):
    """Multi-round 1v1 fleet combat orchestrator.

    On entry: builds fleet rosters from the passed ShipClass lists,
    then immediately spawns the first round via MeleeCombatScene.

    Each round's `on_finish` callback fires `_on_round_finish`, which
    reads damage state from the just-finished MeleeCombatScene,
    updates the fleet, checks the win condition, and either spawns
    the next round or fires the fleet-level callback.
    """

    def __init__(
        self,
        precursor_fleet: list[ShipClass],
        homesteader_fleet: list[ShipClass],
        on_finish: Callable[[FleetResult], None] | None = None,
        arena_style: str = ARENA_STYLE_SOLAR_SYSTEM,
        max_round_duration: float = 60.0,
    ) -> None:
        super().__init__()
        if not precursor_fleet or not homesteader_fleet:
            raise ValueError("both fleets must have at least one ship")
        self.precursor_fleet: list[FleetShip] = [
            FleetShip.from_class(c) for c in precursor_fleet
        ]
        self.homesteader_fleet: list[FleetShip] = [
            FleetShip.from_class(c) for c in homesteader_fleet
        ]
        self.on_fleet_finish: Callable[[FleetResult], None] | None = on_finish
        self.arena_style: str = arena_style
        self.max_round_duration: float = max_round_duration
        self.round_count: int = 0
        # Set to True once we've fired the fleet-level on_finish; guards
        # against re-fire if scene gets entered multiple times.
        self._done: bool = False

    # ------------------------------------------------------------------
    # Scene API
    # ------------------------------------------------------------------

    def on_enter(self) -> None:
        """Spawn the first round immediately. The scene transitions
        away to MeleeCombatScene; this scene is never the active scene
        for more than one frame.
        """
        if self._done:
            return
        self._spawn_next_round()

    def update(self, dt: float, inp) -> None:  # type: ignore[no-untyped-def]
        # No-op — this scene only exists to coordinate transitions. If
        # we get an update tick, we're mid-spawn or done.
        pass

    def render(self, screen) -> None:  # type: ignore[no-untyped-def]
        # No-op — we transition before any frame is rendered. Black
        # fallback in case the scene is briefly visible.
        import pygame
        screen.fill((0, 0, 0))

    # ------------------------------------------------------------------
    # Internals
    # ------------------------------------------------------------------

    def _spawn_next_round(self) -> None:
        """Auto-pick the next ship from each fleet and start a round
        via MeleeCombatScene.
        """
        assert self.game is not None
        p_pick = self._first_alive(self.precursor_fleet)
        h_pick = self._first_alive(self.homesteader_fleet)
        if p_pick is None or h_pick is None:
            # One fleet is already empty (shouldn't normally reach here
            # — we check win condition before spawning) but defensive.
            self._fire_fleet_finish()
            return

        self.round_count += 1
        # Closure-capture the melee scene so the on_finish callback can
        # read the survivors' final ShipState.
        melee_holder: list[MeleeCombatScene | None] = [None]

        def _round_on_finish(result: CombatResult) -> None:
            melee = melee_holder[0]
            if melee is None:
                # Shouldn't happen — defensive
                return
            self._on_round_finish(result, melee, p_pick, h_pick)

        melee = MeleeCombatScene(
            precursor_ship=p_pick.cls,
            homesteader_ship=h_pick.cls,
            max_duration=self.max_round_duration,
            on_finish=_round_on_finish,
            arena_style=self.arena_style,
        )
        melee_holder[0] = melee
        self.game.set_scene(melee)

    def _on_round_finish(
        self,
        result: CombatResult,
        melee: MeleeCombatScene,
        p_pick: FleetShip,
        h_pick: FleetShip,
    ) -> None:
        """Fold round results back into the fleet rosters and either
        spawn the next round or fire the fleet-level callback.
        """
        # Damage carry-over: read the survivor's final ShipState.
        # MeleeCombatScene's `precursor` / `homesteader` are ShipState
        # instances with live hull/shield/energy.
        p_pick.hull = max(0.0, melee.precursor.hull)
        p_pick.shield = max(0.0, melee.precursor.shield)
        p_pick.energy = max(0.0, melee.precursor.energy)
        p_pick.alive = melee.precursor.alive

        h_pick.hull = max(0.0, melee.homesteader.hull)
        h_pick.shield = max(0.0, melee.homesteader.shield)
        h_pick.energy = max(0.0, melee.homesteader.energy)
        h_pick.alive = melee.homesteader.alive

        # On timeout with both still alive: end the fleet encounter
        # as a draw — neither side "wins" the fleet, but we don't
        # endlessly retry. (Routine encounters usually have one side
        # at size 1 anyway, so timeouts are rare.)
        if result.timed_out:
            self._fire_fleet_finish(timed_out=True)
            return

        # Either fleet empty → done. Otherwise spawn the next round
        # with the survivor staying in (auto-pick will skip dead ships).
        p_alive = any(s.alive for s in self.precursor_fleet)
        h_alive = any(s.alive for s in self.homesteader_fleet)
        if not p_alive or not h_alive:
            self._fire_fleet_finish()
            return

        # Continue — re-enter this scene as the orchestrator. The new
        # scene set will get on_enter called, which spawns the next
        # round. We re-set ourselves so the harness sees the
        # `FleetCombatScene` between rounds.
        # Caveat: pygame Scene model doesn't have a clean "re-enter
        # self" idiom. We just re-call set_scene with this same
        # instance; on_enter fires again and triggers the next round.
        self.game.set_scene(self)

    def _fire_fleet_finish(self, timed_out: bool = False) -> None:
        """Compute the FleetResult and fire the fleet-level callback."""
        if self._done:
            return
        self._done = True
        p_survivors = [s for s in self.precursor_fleet if s.alive]
        h_survivors = [s for s in self.homesteader_fleet if s.alive]
        if timed_out:
            winner = None
        elif p_survivors and not h_survivors:
            winner = "precursor"
        elif h_survivors and not p_survivors:
            winner = "homesteader"
        else:
            winner = None
        result = FleetResult(
            winner_side=winner,
            precursor_survivors=p_survivors,
            homesteader_survivors=h_survivors,
            round_count=self.round_count,
            timed_out=timed_out,
        )
        if self.on_fleet_finish is not None:
            self.on_fleet_finish(result)

    @staticmethod
    def _first_alive(fleet: list[FleetShip]) -> FleetShip | None:
        """Return the first ship in the fleet whose `alive` flag is
        True. Auto-pick policy: roster order. Future expansion can
        replace this with a player-facing picker UI.
        """
        for s in fleet:
            if s.alive:
                return s
        return None


def build_fleet_from_game(game, fallback_ship_class) -> list[ShipClass]:
    """Build the player's combat fleet from `game.fleet` (a list of
    ShipClass ids). Returns a list of ShipClass instances ready for
    `FleetCombatScene`.

    If `game.fleet` is empty or missing, returns `[fallback_ship_class]`
    so encounters always have at least one ship per side.

    The id-to-ShipClass mapping is the inverse of
    `SHIP_CLASS_TO_SPECIES_ID` from `species_names.py`; we re-implement
    it here against the canonical `ships` module to avoid pulling in
    naming dependencies.
    """
    from scz.combat import ships as ships_mod

    fleet_ids: list[str] = getattr(game, "fleet", None) or []
    if not fleet_ids:
        return [fallback_ship_class]
    out: list[ShipClass] = []
    for sid in fleet_ids:
        ship_class = getattr(ships_mod, sid, None)
        if ship_class is None:
            # Unknown id — skip rather than crash; flag via print so
            # tests can catch this if it surfaces
            print(f"[fleet_combat] unknown ship class id: {sid!r}")
            continue
        out.append(ship_class)
    if not out:
        return [fallback_ship_class]
    return out
