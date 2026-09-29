"""FinalConflictScene — the slice climax orchestrator.

Canon: `references/lore/the-final-conflict.md` §"Canon revision
2026-05-18". Aaron's spec, verbatim:

    "At the last goalpost for the game, we are going to meet at the
    tip of the arrow of the rainbow worlds and depart, but when we
    arrive, the Homesteaders fleet is there, lead by our arch nemesis
    who has convinced them that the precursors leaving is what would
    bring destruction. No matter how we try to wiggle out of it or
    negotiate, we end in conflict. Super-melee, they get all of their
    ships, one of each, and we get all of our ships, one of each
    friendly species we helped with their quest. If we win, we get to
    go see the ending, otherwise, re-load last save (our time drive
    takes us back before the conflict starts)."

Flow:

1. **Briefing phase** — short Drev-Tok narration. Three player
   choices, all of which canonically fail to defuse the conflict.
2. **Combat phase** — `FleetCombatScene` orchestrates fleet-vs-fleet
   between the alliance-composed Steward roster and Drev-Tok's
   canonical 5-ship coalition.
3. **Resolution**:
   - **Win** → `final_conflict_resolved=True`, `resolve_ending(game)`
     evaluates + applies the canonical slice ending tier, transition
     to `EndingScene` which renders the tier-specific cinematic.
   - **Loss** → Time Drive restore from the pre-conflict snapshot +
     transition back to HyperspaceScene at a position just OUTSIDE
     the Rainbow Worlds trigger zone (so the player can prepare and
     try again).

State machine for the dialogue is simple — 4 internal states with
"all roads lead to combat" structure.
"""

from __future__ import annotations

from typing import Callable

import pygame

from scz.content.final_conflict import (
    build_drev_tok_fleet,
    build_steward_fleet,
    restore_pre_conflict_snapshot,
    take_pre_conflict_snapshot,
)
from scz.engine.scene import Scene


# Internal dialog phase enum
_PHASE_INTRO = "intro"
_PHASE_NEGOTIATE = "negotiate"
_PHASE_PERSUADER = "persuader"
_PHASE_CONFLICT = "conflict"   # transient — about to spawn FleetCombatScene


class FinalConflictScene(Scene):
    """Slice-climax orchestration scene.

    Lifetime: enters briefing phase → spawns FleetCombatScene → reaps
    result → transitions to ending (win) or restores snapshot (loss).
    """

    def __init__(self) -> None:
        super().__init__()
        self.phase: str = _PHASE_INTRO
        self.selected: int = 0
        self.fonts: dict[str, pygame.font.Font] = {}
        # Pre-conflict snapshot — populated in on_enter. Used to
        # restore on loss per the Time Drive canon.
        self._snapshot: dict | None = None
        # Hyperspace position at the moment of trigger — captured by
        # the hyperspace scene before transition; restored on loss.
        self._restore_hyperspace_xy: tuple[float, float] | None = None

    def on_enter(self) -> None:
        self.fonts["title"] = pygame.font.SysFont("consolas", 36, bold=True)
        self.fonts["body"] = pygame.font.SysFont("consolas", 20)
        self.fonts["small"] = pygame.font.SysFont("consolas", 16)
        self.fonts["menu"] = pygame.font.SysFont("consolas", 22)
        # Snapshot on FIRST entry only (the scene re-enters on round
        # transitions through FleetCombatScene; subsequent enters
        # mustn't overwrite the snapshot taken before the combat).
        if self._snapshot is None and self.game is not None:
            self._snapshot = take_pre_conflict_snapshot(self.game)

    def snapshot(self) -> dict | None:
        return None    # the slice climax doesn't permit rewind mid-scene

    # ------------------------------------------------------------------
    # External wiring — called by HyperspaceScene before transition
    # ------------------------------------------------------------------

    def set_restore_position(self, x: float, y: float) -> None:
        """Capture the hyperspace coords to restore the player to on
        loss. Per canon, the Time Drive rewinds them to just BEFORE
        the trigger fired — which means hyperspace at the position
        that crossed the trigger threshold.
        """
        self._restore_hyperspace_xy = (float(x), float(y))

    # ------------------------------------------------------------------
    # Dialogue phase
    # ------------------------------------------------------------------

    def update(self, dt: float, inp) -> None:  # type: ignore[no-untyped-def]
        # The conflict phase is transient — we just trigger the
        # FleetCombatScene transition once and never come back here.
        if self.phase == _PHASE_CONFLICT:
            return

        if inp.menu_up:
            self.selected = max(0, self.selected - 1)
        elif inp.menu_down:
            self.selected = min(self._choice_count() - 1, self.selected + 1)

        if inp.confirm:
            self._handle_confirm()

    def _choice_count(self) -> int:
        if self.phase == _PHASE_INTRO:
            return 3        # Stand aside / Negotiate / Persuader
        if self.phase == _PHASE_NEGOTIATE:
            return 1        # only "We have to fight, then."
        if self.phase == _PHASE_PERSUADER:
            return 1        # only "We have to fight, then."
        return 1

    def _handle_confirm(self) -> None:
        if self.phase == _PHASE_INTRO:
            # All three choices route to a Drev-Tok rejection.
            if self.selected == 0:
                self.phase = _PHASE_NEGOTIATE
            elif self.selected == 1:
                self.phase = _PHASE_NEGOTIATE
            else:
                self.phase = _PHASE_PERSUADER
            self.selected = 0
            return
        # All non-intro phases have one choice — proceed to combat.
        self._begin_combat()

    def _begin_combat(self) -> None:
        """Compose fleets, spawn FleetCombatScene, hand off."""
        if self.game is None:
            return
        self.phase = _PHASE_CONFLICT
        from scz.combat import ships as ships_mod
        from scz.scenes.fleet_combat import FleetCombatScene

        # Resolve ship-class ids → ShipClass instances. Skip unknown
        # ids defensively — the alliance builder is robust but Combat
        # Mechanics might rename a class.
        def _resolve(ids: list[str]):
            out = []
            for sid in ids:
                cls = getattr(ships_mod, sid, None)
                if cls is not None:
                    out.append(cls)
            return out

        steward_fleet = _resolve(build_steward_fleet(self.game))
        drev_tok_fleet = _resolve(build_drev_tok_fleet())

        # Defensive: ensure both sides have at least one ship.
        # FleetCombatScene raises ValueError on empty fleet; we don't
        # want to crash the climax over a content registry typo.
        if not steward_fleet:
            from scz.combat.ships import FURLING_SCOUT
            steward_fleet = [FURLING_SCOUT]
        if not drev_tok_fleet:
            from scz.combat.ships import DEFENDER_VESSEL
            drev_tok_fleet = [DEFENDER_VESSEL]

        # The fleet on_finish is the resolution handler — fires when
        # one side's fleet is empty (or timed out).
        def _on_fleet_finish(result) -> None:  # type: ignore[no-untyped-def]
            self._on_combat_resolved(result)

        scene = FleetCombatScene(
            precursor_fleet=steward_fleet,
            homesteader_fleet=drev_tok_fleet,
            on_finish=_on_fleet_finish,
            max_round_duration=60.0,
        )
        self.game.set_scene(scene)

    # ------------------------------------------------------------------
    # Resolution
    # ------------------------------------------------------------------

    def _on_combat_resolved(self, result) -> None:  # type: ignore[no-untyped-def]
        """Fleet-level on_finish — branches on winner_side."""
        if self.game is None:
            return
        if result.winner_side == "precursor":
            self._handle_win()
        else:
            # Loss OR timeout — both go down the rewind path (timeout
            # at the Final Conflict canonically reads as "no winner
            # yet; try again" rather than "draw").
            self._handle_loss()

    def _handle_win(self) -> None:
        """Player victory → resolve ending tier, transition to EndingScene.

        The win path calls `resolve_ending(game)` which:
          1. Evaluates the slice's ending tier from `game.flags`
             (species saved / crew aboard / side-quests done)
          2. Writes the canonical slice_ending flags
          3. Returns the tier (Best/Great/Good/AT_COST; combat-victory
             at the Final Conflict can never produce Unsuccessful or
             Disastrous since the player necessarily had enough fleet
             support to win the climax fight)

        EndingScene reads `game.flags["slice_ending"]` and renders the
        canonical tier presentation.
        """
        assert self.game is not None
        self.game.flags["final_conflict_resolved"] = True
        from scz.content.endings import resolve_ending
        from scz.scenes.ending import EndingScene
        resolve_ending(self.game)
        self.game.set_scene(EndingScene())

    def _handle_loss(self) -> None:
        """Time Drive rewind — restore snapshot, place player back in
        hyperspace just outside the trigger zone."""
        assert self.game is not None
        if self._snapshot is not None:
            restore_pre_conflict_snapshot(self.game, self._snapshot)
        # Post-restore — the snapshot wiped flags so anything we want to
        # PRESERVE through a rewind has to be written here. Tracking
        # rewind count is also useful for save-scumming-resistant ending
        # variants ("the Steward who succeeded on the first try" etc.).
        self.game.flags["final_conflict_rewound_count"] = (
            int(self.game.flags.get("final_conflict_rewound_count", 0)) + 1
        )
        # Drop the player back into hyperspace at the captured pre-
        # trigger position. If no position was captured (e.g. invoked
        # directly via switcher), fall back to a safe position near
        # Sol — the player can re-approach the Rainbow Worlds.
        from scz.hyperspace.scene import HyperspaceScene
        hyper = HyperspaceScene()
        if self._restore_hyperspace_xy is not None:
            hyper.player_x, hyper.player_y = self._restore_hyperspace_xy
        else:
            hyper.player_x = 1793.0   # Sol
            hyper.player_y = 1450.0
        # Mark a flag the hyperspace scene can use to BRIEFLY suppress
        # the auto-trigger on next entry, so the rewound player isn't
        # instantly re-pulled into the Final Conflict. We just clear
        # the resonator-equipped signal temporarily — the player has
        # to re-equip it (which they will via Customization).
        self.game.flags["final_conflict_just_rewound"] = True
        self.game.set_scene(hyper)

    # ------------------------------------------------------------------
    # Render
    # ------------------------------------------------------------------

    def render(self, screen: pygame.Surface) -> None:
        screen.fill((4, 6, 18))
        if self.game is None:
            return
        sw, sh = screen.get_size()

        # Title block
        screen.blit(
            self.fonts["title"].render(
                "THE RAINBOW WORLDS — ARROW-TIP",
                True, (220, 200, 140),
            ),
            (40, 40),
        )
        screen.blit(
            self.fonts["body"].render(
                "Admiral Drev-Tok Velt-Mar, Sa-Matra Prototype, "
                "Homesteader Coalition Fleet",
                True, (200, 160, 140),
            ),
            (40, 84),
        )

        if self.phase == _PHASE_INTRO:
            self._render_intro(screen, sw, sh)
        elif self.phase == _PHASE_NEGOTIATE:
            self._render_negotiate(screen, sw, sh)
        elif self.phase == _PHASE_PERSUADER:
            self._render_persuader(screen, sw, sh)
        else:
            # transient
            screen.blit(
                self.fonts["body"].render(
                    "(engaging combat...)", True, (200, 200, 220),
                ),
                (40, 140),
            )

    def _render_intro(self, screen, sw, sh):
        body = [
            "Steward.  *Two years* I have spoken on the Council channels —",
            "the voice that argued every Migration vote into a longer",
            "conversation.  Today is the conversation's end.",
            "",
            "Your fleet is *abandoning* the species who cannot follow.",
            "Cloaking is admitting we are small.  Migrating is admitting",
            "we cannot solve the problem.  Defending is impossible — *so*",
            "the Persuaders said.  And yet here I am, defending.",
            "",
            "Stand aside.  Return to the cluster.  Fight with us.",
            "Or come through me.",
        ]
        self._render_lines(screen, body, 140, (200, 220, 240))
        choices = [
            "Stand aside, Admiral. Let us pass.",
            "There must be a way through this without combat.",
            "The Migration is the right call. Step down.",
        ]
        self._render_choices(screen, choices, sh - 200)

    def _render_negotiate(self, screen, sw, sh):
        body = [
            "Drev-Tok:",
            "",
            "Two years of *please*, Steward.  Two years of *reason*.",
            "You have not understood; I have understood you perfectly.",
            "",
            "*Flat finality.*",
            "",
            "Combat engagement in thirty seconds.  Move your fleet to",
            "defensive formation.  I have honor to return; I owe my",
            "cohort the gesture; I will not be denied.",
        ]
        self._render_lines(screen, body, 140, (200, 200, 220))
        self._render_choices(
            screen,
            ["We have to fight, then. Fleet to formation."],
            sh - 200,
        )

    def _render_persuader(self, screen, sw, sh):
        body = [
            "Drev-Tok:",
            "",
            "Every species you 'saved' had a *choice* because of the",
            "Migration, you say.  Cloaked.  Hidden.  Devolved.  Defiant.",
            "",
            "*A pause.*",
            "",
            "The cloaked die slower.  The hidden die alone.  The devolved",
            "die without remembering.  The defiant die *defiantly*.",
            "",
            "I do not call that 'saved,' Steward.  I call that *recorded*.",
            "Move your fleet.  The volleys come in thirty seconds.",
        ]
        self._render_lines(screen, body, 140, (200, 200, 220))
        self._render_choices(
            screen,
            ["The argument is over. Fleet to formation."],
            sh - 200,
        )

    def _render_lines(self, screen, lines, y_start, color):
        y = y_start
        for line in lines:
            if line:
                screen.blit(self.fonts["body"].render(line, True, color), (40, y))
            y += 26

    def _render_choices(self, screen, choices, y_start):
        y = y_start
        screen.blit(
            self.fonts["small"].render(
                "RESPONSE", True, (180, 200, 220),
            ),
            (40, y),
        )
        y += 24
        for i, label in enumerate(choices):
            is_sel = (i == self.selected)
            color = (240, 220, 180) if is_sel else (180, 190, 200)
            arrow = "> " if is_sel else "  "
            screen.blit(
                self.fonts["menu"].render(
                    f"{arrow}{label}", True, color,
                ),
                (60, y),
            )
            y += 30
