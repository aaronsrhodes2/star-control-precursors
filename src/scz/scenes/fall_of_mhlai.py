"""FallOfMhLaiScene — the slice's mid-game catastrophe sequence.

Five beats per `references/lore/the-fall-of-mh-lai.md`:

1. **Detection** (forced, ~3s) — dimensional ripple alarm; the player
   sees the alarm overlay and can't act. Halia's transmission queues.
2. **Halia's first transmission** (~6s) — her formal voice opens the
   scene. Forced text crawl; the Steward CANNOT interrupt.
3. **The Decision** (~60s timer, pausable) — vertical list of 3-4
   branches with a countdown bar. Pick or time out (→ honor-migration).
4. **The Fall (cinematic)** (~8s) — narrated text crawl over a dim
   backdrop. The chamber's last transmission cuts mid-broadcast.
5. **The Aftermath** (~3s) — silence + a fade-out line. Returns to
   hyperspace with all branch flags set; `mhlai_destroyed = True`.

Tone: humor doctrine ZERO throughout. The scene is heavy by design.

Time-constrained decision UI is novel for this slice (existing dialog
FSMs are untimed). Implemented locally to this scene only — a general
timed-decision UI is deferred until a second use case demands it.
"""

from __future__ import annotations

from typing import Literal

import pygame

from scz.content.fall_of_mhlai import (
    DECISION_WINDOW_SECONDS,
    FallBranch,
    visible_branches,
)
from scz.engine.scene import Scene


# Phase enum. Each phase has its own update / render logic.
Phase = Literal[
    "detection",      # Beat 1 — forced alarm
    "transmission",   # Beat 2 — Halia's transmission (forced)
    "decision",       # Beat 3 — timed 4-branch picker
    "fall",           # Beat 4 — cinematic narration
    "aftermath",      # Beat 5 — silence + return
]


# Per-phase durations (game-seconds). Decision phase uses
# DECISION_WINDOW_SECONDS from the content module.
PHASE_DURATIONS: dict[str, float] = {
    "detection": 3.0,
    "transmission": 8.0,
    "fall": 8.0,
    "aftermath": 3.0,
}


# Halia's transmission text — canonical per the lore doc's Beat 2.
# Single paragraph, character-revealed.
HALIA_TRANSMISSION_TEXT: str = (
    "Steward of Mh-Lai. The probe-shadow has resolved. They are here.\n\n"
    "The Council chamber detected a dimensional ripple twelve minutes "
    "ago. We have between forty and ninety minutes before the Others "
    "cross into our atmosphere. The Migration vessels are pulling away "
    "as I speak. The Hearth-of-Iron is breaking orbit.\n\n"
    "I have a choice to make. So do you. You can race to Mh-Lai — "
    "burn the drive open, slam the Quasi-Drive if you have one — "
    "and arrive ahead of the Others, and fight to evacuate me and "
    "what remains of the Council. The math is *tight*. You might not "
    "make it. Or you might arrive in time to watch.\n\n"
    "Or you can stay on the Migration's trajectory. Honor the "
    "timetable. Trust the math. Grieve at a distance.\n\n"
    "I will not tell you which to choose, Steward. I will tell you "
    "this: the Migration must continue. Whatever you decide, it must "
    "continue. The Persuader bench has done its work. The vessels are "
    "loaded. The corridors are mapped.\n\n"
    "Choose. The window is open."
)


# Cinematic narration for Beat 4 — multi-line; revealed line-by-line
# over the fall's duration.
FALL_NARRATION_LINES: tuple[str, ...] = (
    "The dimensional ripple touches Mh-Lai's outer halo.",
    "The atmosphere flickers — a brief planetary aurora.",
    "The Others' substrate intersects the biosphere.",
    "Cognition extinguishes en masse. In waves. Like a tide receding.",
    "The Council chamber's last data transmission cuts mid-broadcast.",
    "The Migration vessels in standby orbit pull away — silent.",
    "Mh-Lai's surface continues to unmake itself. For hours.",
    "There is no debris field. The planet is less than it was.",
    "Your comm cuts to silence.",
)


AFTERMATH_LINE: str = (
    "The Hearth-of-Iron and her sister vessels burn for the corridors. "
    "Mev-Tar Lwen-Tar has moved the Unzervalt tooling. The services "
    "continue. The slice continues. *The slice has changed.*"
)


class FallOfMhLaiScene(Scene):
    """The mid-game catastrophe scene. Auto-fired from hyperspace
    when the trigger contract in `fall_of_mhlai.should_fire_fall`
    returns True.
    """

    def __init__(self) -> None:
        super().__init__()
        self.phase: Phase = "detection"
        self.phase_elapsed: float = 0.0
        self._branches: list[FallBranch] = []
        # Decision phase state
        self.decision_cursor: int = 0
        # When None, the timer hasn't been initialized; set on
        # entering the decision phase.
        self.decision_remaining: float = DECISION_WINDOW_SECONDS
        self.fonts: dict[str, pygame.font.Font] = {}
        # Narration line cursor (Beat 4)
        self.narration_revealed: int = 0
        # Branch that was committed (post-decision)
        self.committed_branch: FallBranch | None = None

    def on_enter(self) -> None:
        self.fonts["title"] = pygame.font.SysFont("consolas", 32, bold=True)
        self.fonts["subtitle"] = pygame.font.SysFont("consolas", 18)
        self.fonts["body"] = pygame.font.SysFont("consolas", 19)
        self.fonts["small"] = pygame.font.SysFont("consolas", 14)
        self.fonts["item"] = pygame.font.SysFont("consolas", 18)
        self.fonts["timer"] = pygame.font.SysFont("consolas", 26, bold=True)
        self.fonts["alarm"] = pygame.font.SysFont("consolas", 36, bold=True)
        if self.game is not None:
            self._branches = visible_branches(self.game)
            self.decision_cursor = 0

    def snapshot(self) -> dict | None:
        """The Fall is non-rewindable — Time Drive cannot undo this.
        Snapshot returns None to make the scene rewind-opaque.
        """
        return None

    def update(self, dt: float, inp) -> None:  # type: ignore[no-untyped-def]
        assert self.game is not None
        self.phase_elapsed += dt

        if self.phase == "detection":
            if self.phase_elapsed >= PHASE_DURATIONS["detection"]:
                self._enter_phase("transmission")
            return

        if self.phase == "transmission":
            if self.phase_elapsed >= PHASE_DURATIONS["transmission"]:
                self._enter_phase("decision")
            return

        if self.phase == "decision":
            # Countdown — timer-expiry defaults to honor-migration
            self.decision_remaining -= dt
            if self.decision_remaining <= 0.0:
                # Default branch: honor-migration (index 2 in BRANCHES_BASE)
                default = next(
                    (b for b in self._branches if b.id == "honor_migration"),
                    self._branches[0],
                )
                self._commit_branch(default)
                return
            n = len(self._branches)
            if n > 0:
                if inp.menu_up:
                    self.decision_cursor = (self.decision_cursor - 1) % n
                elif inp.menu_down:
                    self.decision_cursor = (self.decision_cursor + 1) % n
                if inp.confirm:
                    self._commit_branch(
                        self._branches[self.decision_cursor],
                    )
            return

        if self.phase == "fall":
            # Reveal narration lines progressively
            n_lines = len(FALL_NARRATION_LINES)
            duration = PHASE_DURATIONS["fall"]
            self.narration_revealed = min(
                n_lines,
                int(self.phase_elapsed / duration * n_lines) + 1,
            )
            if self.phase_elapsed >= duration:
                self._enter_phase("aftermath")
            return

        if self.phase == "aftermath":
            if self.phase_elapsed >= PHASE_DURATIONS["aftermath"]:
                # Return to hyperspace at SOL coords (canonical home
                # position; Mh-Lai's coords were near here but the
                # system is now empty space + debris).
                from scz.hyperspace.scene import (
                    HyperspaceScene,
                    SOL_X,
                    SOL_Y,
                )
                h = HyperspaceScene()
                h.player_x = SOL_X
                h.player_y = SOL_Y
                self.game.set_scene(h)
            return

    def _enter_phase(self, new_phase: Phase) -> None:
        self.phase = new_phase
        self.phase_elapsed = 0.0
        if new_phase == "decision":
            self.decision_remaining = DECISION_WINDOW_SECONDS

    def _commit_branch(self, branch: FallBranch) -> None:
        """Apply branch side-effect; advance to the fall cinematic.
        Also unlocks the THE_FALL_OF_MH_LAI archive entry by setting
        the canonical archive flag.
        """
        assert self.game is not None
        branch.side_effect(self.game)
        # Unlock the archive entry for the slice ledger
        self.game.flags["mhlai_fall_witnessed"] = True
        self.committed_branch = branch
        self._enter_phase("fall")

    # ------------------------------------------------------------------
    # Render
    # ------------------------------------------------------------------

    def render(self, screen: pygame.Surface) -> None:
        assert self.game is not None
        # Each phase has its own visual treatment
        if self.phase == "detection":
            self._render_detection(screen)
        elif self.phase == "transmission":
            self._render_transmission(screen)
        elif self.phase == "decision":
            self._render_decision(screen)
        elif self.phase == "fall":
            self._render_fall(screen)
        else:   # aftermath
            self._render_aftermath(screen)

    def _render_detection(self, screen: pygame.Surface) -> None:
        """Beat 1 — pulsing red alarm overlay across the screen."""
        w, h = screen.get_size()
        # Pulsing red background
        ticks = pygame.time.get_ticks()
        pulse = (pygame.math.Vector2(1, 0).rotate(ticks * 0.5).x + 1) / 2
        bg = (int(30 + pulse * 80), 8, 8)
        screen.fill(bg)
        text = self.fonts["alarm"].render(
            "DIMENSIONAL RIPPLE DETECTED", True, (255, 220, 220),
        )
        tw, th = text.get_size()
        screen.blit(text, ((w - tw) // 2, h // 2 - th))
        sub = self.fonts["subtitle"].render(
            "Mh-Lai outer halo  ·  Council chamber transmitting",
            True, (220, 180, 180),
        )
        sw, _ = sub.get_size()
        screen.blit(sub, ((w - sw) // 2, h // 2 + 8))

    def _render_transmission(self, screen: pygame.Surface) -> None:
        """Beat 2 — Halia's transmission with character-revealed text."""
        w, h = screen.get_size()
        screen.fill((8, 6, 14))
        # Header
        title = self.fonts["title"].render(
            "INCOMING TRANSMISSION  ·  COMMANDER HALIA",
            True, (220, 200, 240),
        )
        tw, _ = title.get_size()
        screen.blit(title, ((w - tw) // 2, 28))
        sub = self.fonts["subtitle"].render(
            "Mh-Lai Council Chamber  ·  Persuader Bench",
            True, (180, 170, 210),
        )
        sw, _ = sub.get_size()
        screen.blit(sub, ((w - sw) // 2, 68))

        # Character reveal — text appears progressively
        reveal_frac = min(
            1.0,
            self.phase_elapsed / max(0.1, PHASE_DURATIONS["transmission"] * 0.85),
        )
        n_show = int(len(HALIA_TRANSMISSION_TEXT) * reveal_frac)
        shown = HALIA_TRANSMISSION_TEXT[:n_show]
        body_x = 80
        body_y = 130
        max_w = w - 160
        self._blit_wrapped(
            screen, shown, self.fonts["body"], body_x, body_y, max_w,
            (220, 220, 240),
        )

    def _render_decision(self, screen: pygame.Surface) -> None:
        """Beat 3 — timed decision picker."""
        w, h = screen.get_size()
        screen.fill((6, 4, 12))

        # Header
        title = self.fonts["title"].render(
            "THE DECISION", True, (250, 220, 180),
        )
        tw, _ = title.get_size()
        screen.blit(title, ((w - tw) // 2, 28))

        # Countdown bar + timer
        bar_y = 80
        bar_h = 8
        bar_pad = 80
        bar_w = w - 2 * bar_pad
        frac = max(0.0, self.decision_remaining / DECISION_WINDOW_SECONDS)
        pygame.draw.rect(screen, (40, 30, 20), (bar_pad, bar_y, bar_w, bar_h))
        # Color shifts as time runs low
        if frac > 0.5:
            bar_color = (180, 220, 180)
        elif frac > 0.2:
            bar_color = (240, 200, 130)
        else:
            bar_color = (240, 120, 100)
        pygame.draw.rect(
            screen, bar_color,
            (bar_pad, bar_y, int(bar_w * frac), bar_h),
        )
        timer_text = self.fonts["timer"].render(
            f"{int(self.decision_remaining):02d}s",
            True, bar_color,
        )
        ttw, _ = timer_text.get_size()
        screen.blit(timer_text, ((w - ttw) // 2, bar_y + 14))

        # Warning text when timer is short
        if self.decision_remaining < 10.0:
            warn = self.fonts["subtitle"].render(
                "The window is closing. Decide.",
                True, (240, 140, 120),
            )
            ww, _ = warn.get_size()
            screen.blit(warn, ((w - ww) // 2, bar_y + 50))

        # Branch list
        list_top = 180
        for i, branch in enumerate(self._branches):
            row_y = list_top + i * 60
            is_selected = i == self.decision_cursor
            bg = (40, 30, 50) if is_selected else (18, 14, 28)
            border = (240, 220, 180) if is_selected else (60, 50, 70)
            row_rect = pygame.Rect(80, row_y, w - 160, 52)
            pygame.draw.rect(screen, bg, row_rect)
            pygame.draw.rect(screen, border, row_rect, 1)
            mark = "►" if is_selected else " "
            label_color = (
                (240, 230, 200) if is_selected else (190, 180, 210)
            )
            screen.blit(
                self.fonts["item"].render(
                    f"{mark}  {branch.label}", True, label_color,
                ),
                (row_rect.left + 14, row_rect.top + 14),
            )

        # Detail pane — selected branch's summary
        detail_y = list_top + len(self._branches) * 60 + 30
        detail_h = h - detail_y - 50
        detail_rect = pygame.Rect(80, detail_y, w - 160, detail_h)
        pygame.draw.rect(screen, (12, 8, 22), detail_rect)
        pygame.draw.rect(screen, (60, 50, 80), detail_rect, 1)
        if 0 <= self.decision_cursor < len(self._branches):
            b = self._branches[self.decision_cursor]
            self._blit_wrapped(
                screen, b.summary, self.fonts["body"],
                detail_rect.left + 16, detail_rect.top + 14,
                detail_rect.width - 32, (200, 200, 220),
                max_height=detail_h - 28,
            )

        # Hint
        hint = self.fonts["small"].render(
            "Up/Down select  ·  A commit  ·  timer expiry → honor migration",
            True, (140, 140, 170),
        )
        hw, _ = hint.get_size()
        screen.blit(hint, ((w - hw) // 2, h - 30))

    def _render_fall(self, screen: pygame.Surface) -> None:
        """Beat 4 — cinematic narration. Lines reveal progressively over
        the fall's duration; background dims to near-black.
        """
        w, h = screen.get_size()
        # Background fades from dark blue to near-black over the duration
        frac = min(1.0, self.phase_elapsed / PHASE_DURATIONS["fall"])
        bg_v = int(8 - frac * 4)
        screen.fill((bg_v, bg_v, max(0, bg_v + 2)))

        # Title
        title = self.fonts["subtitle"].render(
            "Mh-Lai  ·  Council Chamber  ·  final transmission cut",
            True, (180, 160, 180),
        )
        tw, _ = title.get_size()
        screen.blit(title, ((w - tw) // 2, 30))

        # Narration lines, centered vertically as more reveal
        line_h = self.fonts["body"].get_linesize() + 8
        total_lines = self.narration_revealed
        y_start = h // 2 - (total_lines * line_h) // 2
        for i, line in enumerate(FALL_NARRATION_LINES[:total_lines]):
            # Fade older lines slightly
            age = total_lines - i
            alpha = max(120, 240 - age * 12)
            text = self.fonts["body"].render(line, True, (220, 220, 240))
            text.set_alpha(alpha)
            tw_l, _ = text.get_size()
            screen.blit(text, ((w - tw_l) // 2, y_start + i * line_h))

    def _render_aftermath(self, screen: pygame.Surface) -> None:
        """Beat 5 — silence + a fade-out line."""
        w, h = screen.get_size()
        screen.fill((4, 4, 8))
        # Aftermath text — centered
        self._blit_wrapped(
            screen, AFTERMATH_LINE, self.fonts["body"],
            80, h // 2 - 40, w - 160, (200, 200, 220),
            max_height=200,
        )

    def _blit_wrapped(
        self, screen: pygame.Surface, text: str,
        font: pygame.font.Font,
        x: int, y: int, max_w: int,
        color: tuple[int, int, int],
        max_height: int = 9999,
    ) -> None:
        line_h = font.get_linesize()
        cy = y
        for paragraph in text.split("\n"):
            if not paragraph.strip():
                cy += line_h // 2
                if cy - y > max_height:
                    return
                continue
            words = paragraph.split(" ")
            line: list[str] = []
            for word in words:
                test = " ".join(line + [word])
                if font.size(test)[0] <= max_w:
                    line.append(word)
                else:
                    if line:
                        screen.blit(
                            font.render(" ".join(line), True, color),
                            (x, cy),
                        )
                        cy += line_h
                        if cy - y > max_height:
                            return
                    line = [word]
            if line:
                screen.blit(
                    font.render(" ".join(line), True, color), (x, cy),
                )
                cy += line_h
                if cy - y > max_height:
                    return
