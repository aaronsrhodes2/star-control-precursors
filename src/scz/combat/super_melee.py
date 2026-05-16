"""SuperMeleeScene — pick one Precursor ship and one Homesteader, fight.

Slice scope: 1v1. Both sides flown by the static engine AI (auto-fight
on by default — see `combat/scene.py`). Pressing A on the START row
launches a fight. When the fight ends, control returns here with a
result line printed; another fight can be started immediately.

Layout:
  - Top: title
  - Left column: Precursor ships (D-pad up/down navigates)
  - Right column: Homesteader ships
  - Bottom: START FIGHT row
  - Footer: last result

D-pad left/right switches focus between the two columns. A confirms.
B exits to MainMenu (top-level scene; super-melee is its own loop).
"""

from __future__ import annotations

from typing import Literal

import pygame

from scz.combat.ships import (
    ShipClass,
    homesteader_ships,
    precursor_ships,
)
from scz.engine.scene import Scene


Focus = Literal["precursor", "homesteader", "start"]


class SuperMeleeScene(Scene):
    """Picker + launcher for 1v1 AI-vs-AI super-melee fights."""

    def __init__(self) -> None:
        super().__init__()
        self.precursors = precursor_ships()
        self.homesteaders = homesteader_ships()
        self.p_idx: int = 0
        self.h_idx: int = 0
        self.focus: Focus = "precursor"
        # Last-fight result line, for footer display
        self.last_result: str = ""

        # Set in on_enter
        self.font: pygame.font.Font | None = None
        self.title_font: pygame.font.Font | None = None
        self.big_font: pygame.font.Font | None = None

    # ------------------------------------------------------------------
    # Scene API
    # ------------------------------------------------------------------

    def on_enter(self) -> None:
        self.font = pygame.font.SysFont("consolas", 20)
        self.title_font = pygame.font.SysFont("consolas", 36, bold=True)
        self.big_font = pygame.font.SysFont("consolas", 24, bold=True)

    def snapshot(self) -> dict | None:
        # Picker is intentionally not Time-Drive rewindable.
        return None

    def update(self, dt: float, inp) -> None:  # type: ignore[no-untyped-def]
        if inp.cancel and self.game is not None:
            from scz.scenes.stubs import MainMenuScene
            self.game.set_scene(MainMenuScene())
            return

        # D-pad left / right (menu_prev / menu_next): switch focus column
        if inp.menu_prev:
            self.focus = self._focus_left()
        elif inp.menu_next:
            self.focus = self._focus_right()

        # Up / down within focused column
        if self.focus == "precursor":
            n = len(self.precursors)
            if inp.menu_up:
                self.p_idx = (self.p_idx - 1) % n
            elif inp.menu_down:
                # Wrap into START when at the bottom
                if self.p_idx == n - 1:
                    self.focus = "start"
                else:
                    self.p_idx = (self.p_idx + 1) % n
        elif self.focus == "homesteader":
            n = len(self.homesteaders)
            if inp.menu_up:
                self.h_idx = (self.h_idx - 1) % n
            elif inp.menu_down:
                if self.h_idx == n - 1:
                    self.focus = "start"
                else:
                    self.h_idx = (self.h_idx + 1) % n
        else:  # start
            if inp.menu_up:
                # Pop back to the column we came from
                self.focus = "precursor"
            elif inp.menu_down:
                # Wrap to top of precursor column
                self.focus = "precursor"
                self.p_idx = 0

        # A: confirm
        if inp.confirm and self.game is not None:
            if self.focus == "start":
                self._launch_fight()
            # otherwise A just stays on the row (no per-ship "info" action yet)

    def render(self, screen: pygame.Surface) -> None:
        assert (
            self.font is not None
            and self.title_font is not None
            and self.big_font is not None
        )
        w, h = screen.get_size()
        screen.fill((6, 6, 18))

        # Title
        title = self.title_font.render("SUPER MELEE", True, (220, 230, 250))
        tw, _ = title.get_size()
        screen.blit(title, ((w - tw) // 2, 60))
        sub = self.font.render(
            "Precursor (left) vs Homesteader (right) — AI flies both",
            True, (160, 180, 210),
        )
        sw, _ = sub.get_size()
        screen.blit(sub, ((w - sw) // 2, 110))

        # Columns
        col_y = 170
        col_left_x = 80
        col_right_x = w - 80 - 400
        col_w = 400
        self._render_column(
            screen, "PRECURSORS", self.precursors,
            self.p_idx, self.focus == "precursor",
            col_left_x, col_y, col_w,
        )
        self._render_column(
            screen, "HOMESTEADERS", self.homesteaders,
            self.h_idx, self.focus == "homesteader",
            col_right_x, col_y, col_w,
        )

        # START row
        start_y = h - 200
        start_w = 600
        start_x = (w - start_w) // 2
        active = self.focus == "start"
        start_color = (255, 240, 180) if active else (180, 190, 210)
        start_bg = (60, 80, 100) if active else (24, 28, 50)
        pygame.draw.rect(screen, start_bg, (start_x, start_y, start_w, 70))
        pygame.draw.rect(screen, start_color, (start_x, start_y, start_w, 70), 1)
        prompt = self.big_font.render("► START FIGHT (A)", True, start_color)
        pw, ph = prompt.get_size()
        screen.blit(prompt, ((w - pw) // 2, start_y + (70 - ph) // 2))

        # Matchup summary just above START
        mp = self.precursors[self.p_idx].name
        mh = self.homesteaders[self.h_idx].name
        summary = self.font.render(
            f"{mp}   vs   {mh}",
            True, (220, 220, 240),
        )
        ssw, _ = summary.get_size()
        screen.blit(summary, ((w - ssw) // 2, start_y - 32))

        # Last result footer
        if self.last_result:
            res = self.font.render(self.last_result, True, (180, 220, 180))
            rw, _ = res.get_size()
            screen.blit(res, ((w - rw) // 2, h - 90))

        # Controls hint
        hint = self.font.render(
            "Up/Down  ·  Left/Right switch column  ·  A start  ·  B main menu",
            True, (130, 150, 180),
        )
        hw, _ = hint.get_size()
        screen.blit(hint, ((w - hw) // 2, h - 40))

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _focus_left(self) -> Focus:
        if self.focus == "homesteader":
            return "precursor"
        if self.focus == "start":
            return "precursor"
        return self.focus

    def _focus_right(self) -> Focus:
        if self.focus == "precursor":
            return "homesteader"
        if self.focus == "start":
            return "homesteader"
        return self.focus

    def _render_column(
        self,
        screen: pygame.Surface,
        title: str,
        ships: list[ShipClass],
        sel: int,
        focused: bool,
        x: int,
        y: int,
        w: int,
    ) -> None:
        assert self.font is not None and self.big_font is not None
        # Header
        header_color = (220, 230, 250) if focused else (140, 150, 180)
        screen.blit(self.big_font.render(title, True, header_color), (x, y))
        y_row = y + 40
        row_h = 56
        for i, ship in enumerate(ships):
            is_selected = (i == sel)
            highlight = is_selected and focused
            bg = (40, 60, 100) if highlight else (16, 18, 32)
            border = (200, 220, 240) if highlight else (40, 50, 70)
            pygame.draw.rect(screen, bg, (x, y_row, w, row_h - 6))
            pygame.draw.rect(screen, border, (x, y_row, w, row_h - 6), 1)
            # Mark currently-locked-in selection with a star if not focused
            mark = "►" if highlight else ("• " if is_selected else "  ")
            name_color = ship.accent_color if highlight else (200, 210, 220)
            screen.blit(
                self.font.render(f"{mark} {ship.name}", True, name_color),
                (x + 10, y_row + 6),
            )
            shield_tag = "shielded" if ship.shield_max > 0 else "hull-only"
            sub = (
                f"  {ship.points} pts  ·  hull {ship.hull_max}  ·  "
                f"{shield_tag}  ·  {ship.ai_style}"
            )
            screen.blit(
                self.font.render(sub, True, (160, 170, 200)),
                (x + 10, y_row + 28),
            )
            y_row += row_h

    def _launch_fight(self) -> None:
        from scz.combat.scene import CombatResult, MeleeCombatScene
        precursor = self.precursors[self.p_idx]
        homesteader = self.homesteaders[self.h_idx]

        def _on_finish(result: CombatResult) -> None:
            # Stash a result line in the picker for the next render
            if result.winner_side is None:
                self.last_result = (
                    f"Last fight: DOUBLE KO between {precursor.name} and "
                    f"{homesteader.name}  ({result.duration:.1f}s)"
                )
            else:
                wname = result.winner_ship.name if result.winner_ship else "?"
                tail = "  (timed out)" if result.timed_out else ""
                self.last_result = (
                    f"Last fight: {wname} won  ({result.duration:.1f}s){tail}"
                )
            print(f"[super-melee] {self.last_result}")
            # Persist into game.flags so the test harness can verify the
            # outcome without needing to read scene internals.
            if self.game is not None:
                self.game.flags["last_combat_winner_side"] = result.winner_side
                self.game.flags["last_combat_timed_out"] = result.timed_out
                self.game.set_scene(SuperMeleeScene._with_last_result(self.last_result))

        assert self.game is not None
        self.game.set_scene(
            MeleeCombatScene(
                precursor_ship=precursor,
                homesteader_ship=homesteader,
                on_finish=_on_finish,
            )
        )

    @classmethod
    def _with_last_result(cls, line: str) -> "SuperMeleeScene":
        s = cls()
        s.last_result = line
        return s
