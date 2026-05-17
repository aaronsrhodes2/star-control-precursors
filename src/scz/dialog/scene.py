"""DialogScene — renders an FSM-driven conversation with an NPC.

The scene displays the current state's npc_text in the middle of the
screen, the NPC's portrait disc + name + title at the top, and the
player's choice list at the bottom. Menu-conventions apply: up/down
navigates, A confirms, B closes (returns to parent scene).

Right now the npc_text is rendered as-is (canned). When the LLM renderer
lands, it'll take the npc_text + the character's voice + recent history
and produce the actual surface text. The FSM and choice categories are
the stable contract.
"""

from __future__ import annotations

import math

import pygame

from scz.dialog.data import DialogCharacter, DialogState
from scz.engine.scene import Scene


# Layout constants (tuned for 1920x1080)
PORTRAIT_RADIUS = 90
PORTRAIT_X = 160
PORTRAIT_Y = 160
NAME_X = 280
NAME_Y = 110

TEXT_AREA_X = 280
TEXT_AREA_Y = 240
TEXT_AREA_W = 1480
TEXT_AREA_H = 360

CHOICES_X = 220
CHOICES_Y = 700
CHOICES_W = 1500
CHOICE_ROW_H = 44


class DialogScene(Scene):
    """A conversation with one NPC."""

    def __init__(
        self,
        character: DialogCharacter,
        parent_scene_cls: type | None = None,
        parent_factory=None,
    ) -> None:
        """character: who you're talking to.

        parent_scene_cls / parent_factory: how to return to the parent.
        If parent_factory is provided, it's called with no args to build the
        return scene. Otherwise parent_scene_cls() is used. If neither, the
        game quits.
        """
        super().__init__()
        self.character = character
        self.parent_scene_cls = parent_scene_cls
        self.parent_factory = parent_factory

        self.current_state_id: str = character.initial_state
        self.selected_choice: int = 0
        self.fonts: dict[str, pygame.font.Font] = {}

    # --- Scene API ---

    def on_enter(self) -> None:
        self.fonts["title"] = pygame.font.SysFont("consolas", 32, bold=True)
        self.fonts["subtitle"] = pygame.font.SysFont("consolas", 20)
        self.fonts["npc"] = pygame.font.SysFont("consolas", 24)
        self.fonts["choice"] = pygame.font.SysFont("consolas", 22)
        self.fonts["small"] = pygame.font.SysFont("consolas", 16)

    def update(self, dt: float, inp) -> None:  # type: ignore[no-untyped-def]
        state = self._current_state()

        # B / Esc → exit dialog
        if inp.cancel:
            self._exit_dialog()
            return

        # Auto-terminate if state has no choices (e.g. one-shot farewell)
        if not state.choices:
            self._exit_dialog()
            return

        # Menu navigation: D-pad up/down + arrow keys (edge), wrap
        n = len(state.choices)
        if inp.menu_up:
            self.selected_choice = (self.selected_choice - 1) % n
        elif inp.menu_down:
            self.selected_choice = (self.selected_choice + 1) % n

        # Confirm → pick this choice
        if inp.confirm:
            choice = state.choices[self.selected_choice]
            override_state: str | None = None
            if choice.side_effect is not None and self.game is not None:
                override_state = choice.side_effect(self.game)
                # If the side-effect changed scenes (e.g. launched combat),
                # don't run _exit_dialog — it would overwrite the new scene.
                if self.game.current_scene is not self:
                    return
            # Side-effect override takes precedence over the static
            # next_state_id (used for "did the purchase succeed?"-style
            # conditional routing).
            target = override_state if override_state is not None else choice.next_state_id
            if target is None:
                # Farewell / close
                self._exit_dialog()
                return
            self.current_state_id = target
            self.selected_choice = 0
            return

    def render(self, screen: pygame.Surface) -> None:
        screen.fill((10, 12, 24))
        # Faint starfield-ish backdrop hint
        sw, sh = screen.get_size()
        # No actual stars — just a subtle gradient via a dark rect
        pygame.draw.rect(screen, (16, 18, 32), (0, sh // 2, sw, sh // 2))

        # Portrait disc
        cx, cy = PORTRAIT_X, PORTRAIT_Y
        pygame.draw.circle(
            screen, self.character.portrait_color, (cx, cy), PORTRAIT_RADIUS
        )
        # Ring around the portrait, slightly darker
        rim = tuple(max(0, c - 50) for c in self.character.portrait_color)
        pygame.draw.circle(screen, rim, (cx, cy), PORTRAIT_RADIUS, 3)

        # Name + title
        name_surf = self.fonts["title"].render(
            self.character.name, True, (235, 240, 250)
        )
        screen.blit(name_surf, (NAME_X, NAME_Y))
        title_surf = self.fonts["subtitle"].render(
            self.character.title, True, (160, 180, 210)
        )
        screen.blit(title_surf, (NAME_X, NAME_Y + 44))

        # NPC text block — word-wrapped
        state = self._current_state()
        self._render_wrapped(
            screen,
            state.npc_text,
            self.fonts["npc"],
            (TEXT_AREA_X, TEXT_AREA_Y, TEXT_AREA_W, TEXT_AREA_H),
            (230, 230, 240),
        )

        # Choices
        self._render_choices(screen, state)

        # Footer / controls hint
        self._render_controls_hint(screen)

    # --- Helpers ---

    def _current_state(self) -> DialogState:
        return self.character.states[self.current_state_id]

    def _exit_dialog(self) -> None:
        if self.game is None:
            return
        if self.parent_factory is not None:
            self.game.set_scene(self.parent_factory())
        elif self.parent_scene_cls is not None:
            self.game.set_scene(self.parent_scene_cls())
        else:
            self.game.quit()

    def _render_choices(self, screen: pygame.Surface, state: DialogState) -> None:
        if not state.choices:
            # State has no exits — render a faint "..." marker
            txt = self.fonts["choice"].render("...", True, (120, 140, 170))
            screen.blit(txt, (CHOICES_X + 40, CHOICES_Y))
            return

        for idx, choice in enumerate(state.choices):
            is_selected = idx == self.selected_choice
            y = CHOICES_Y + idx * CHOICE_ROW_H
            if is_selected:
                # Highlight bar behind the selected choice
                hilite_rect = pygame.Rect(CHOICES_X, y - 6, CHOICES_W, CHOICE_ROW_H - 4)
                pygame.draw.rect(screen, (40, 50, 80), hilite_rect)
                pygame.draw.rect(screen, (140, 180, 220), hilite_rect, 1)
                marker = "►"
                color = (255, 240, 180)
            else:
                marker = " "
                color = (180, 190, 210)
            text = self.fonts["choice"].render(
                f"  {marker}   {choice.text}", True, color
            )
            screen.blit(text, (CHOICES_X + 10, y))

    def _render_controls_hint(self, screen: pygame.Surface) -> None:
        sw, sh = screen.get_size()
        hint = self.fonts["small"].render(
            "Up/Down (D-pad, arrows, L-stick)   ·   A / Space pick   ·   B / Esc leave",
            True,
            (130, 150, 180),
        )
        hw, _ = hint.get_size()
        screen.blit(hint, ((sw - hw) // 2, sh - 40))

    def _render_wrapped(
        self,
        screen: pygame.Surface,
        text: str,
        font: pygame.font.Font,
        rect: tuple[int, int, int, int],
        color: tuple[int, int, int],
    ) -> None:
        """Word-wrap text inside the given rect (x, y, w, h)."""
        x, y, w, h = rect
        line_h = font.get_height() + 4
        max_w = w
        cursor_y = y
        # Treat \n as a paragraph break (forced newline + small spacing)
        for paragraph in text.split("\n\n"):
            if cursor_y >= y + h:
                break
            # Wrap this paragraph
            words = paragraph.replace("\n", " ").split()
            line: list[str] = []
            for word in words:
                trial = " ".join(line + [word])
                surf = font.render(trial, True, color)
                if surf.get_width() > max_w and line:
                    # Render current line and start a new one
                    line_surf = font.render(" ".join(line), True, color)
                    screen.blit(line_surf, (x, cursor_y))
                    cursor_y += line_h
                    if cursor_y >= y + h:
                        return
                    line = [word]
                else:
                    line.append(word)
            if line:
                line_surf = font.render(" ".join(line), True, color)
                screen.blit(line_surf, (x, cursor_y))
                cursor_y += line_h
            cursor_y += line_h // 2  # paragraph break extra space
