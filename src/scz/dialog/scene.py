"""DialogScene — renders an FSM-driven conversation with an NPC.

The scene displays the current state's npc_text in the middle of the
screen, the NPC's portrait disc + name + title at the top, and the
player's choice list at the bottom. Menu-conventions apply: up/down
navigates, A confirms, B closes (returns to parent scene).

Right now the npc_text is rendered as-is (canned). When the LLM renderer
lands, it'll take the npc_text + the character's voice + recent history
and produce the actual surface text. The FSM and choice categories are
the stable contract.

Portrait animation: the static Firefly portrait sways and breathes inside
its rim and "speaks" with a faster bob for the first 1–4s of each new
state. This is procedural — no frame art needed. Future upgrade path:
the Flask-SD service on localhost:5000 could generate per-character
mouth/eye frame banks on demand and a PortraitAnimator could cycle them
during NPC speech for true SC2-style animation.
"""

from __future__ import annotations

import math
from pathlib import Path

import pygame

from scz.dialog.data import DialogCharacter, DialogState
from scz.engine.scene import Scene


# Where to look for portrait_image_path strings. They're written as paths
# relative to project root (e.g. "assets/comm/melnorme/melnorme-000.png").
_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent


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

# Portrait animation tuning. The portrait image is loaded slightly larger
# than the rim so it can translate inside the circular window without
# exposing transparent edges. Amplitudes are in pixels.
PORTRAIT_ANIM_HEADROOM = 6
PORTRAIT_IDLE_SWAY_AMPLITUDE_X = 2.0
PORTRAIT_IDLE_BREATH_AMPLITUDE_Y = 1.5
PORTRAIT_IDLE_SWAY_HZ = 0.25            # ~4 s period horizontal
PORTRAIT_IDLE_BREATH_HZ = 0.33          # ~3 s period vertical (de-synced)
PORTRAIT_SPEAK_BOB_AMPLITUDE_Y = 1.5
PORTRAIT_SPEAK_BOB_HZ = 2.2             # ~7 Hz visual mouth-flap feel
# How long the "speaking" bob lasts, derived from npc_text length and
# clamped to a sensible range. ~25 ms per character of text.
PORTRAIT_SPEAK_PER_CHAR_S = 0.025
PORTRAIT_SPEAK_MIN_S = 1.0
PORTRAIT_SPEAK_MAX_S = 4.0


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
        # Lazily-loaded portrait image (if character.portrait_image_path
        # is set). Pre-scaled to a square that fits the portrait disc
        # bounds — we render it as a circular crop to match the existing
        # portrait shape.
        self._portrait_surface: pygame.Surface | None = None
        self._portrait_failed: bool = False
        # Animation clock + state-change tracker for the speaking bob.
        self._time: float = 0.0
        self._state_entered_at: float = 0.0
        self._last_seen_state_id: str | None = None

    # --- Scene API ---

    def on_enter(self) -> None:
        self.fonts["title"] = pygame.font.SysFont("consolas", 32, bold=True)
        self.fonts["subtitle"] = pygame.font.SysFont("consolas", 20)
        self.fonts["npc"] = pygame.font.SysFont("consolas", 24)
        self.fonts["choice"] = pygame.font.SysFont("consolas", 22)
        self.fonts["small"] = pygame.font.SysFont("consolas", 16)
        self._load_portrait_image()

    def _load_portrait_image(self) -> None:
        """Load + scale character.portrait_image_path (if any) once per
        scene entry. Silently no-ops if missing or unloadable."""
        path_str = self.character.portrait_image_path
        if not path_str:
            return
        path = Path(path_str)
        if not path.is_absolute():
            path = _PROJECT_ROOT / path_str
        if not path.exists():
            self._portrait_failed = True
            return
        try:
            raw = pygame.image.load(str(path)).convert_alpha()
        except pygame.error:
            self._portrait_failed = True
            return
        # Fit the raw image into a bounding square slightly LARGER than the
        # portrait disc, giving the animation layer headroom to translate
        # the image inside the static circular rim without revealing
        # transparent edges.
        target = 2 * PORTRAIT_RADIUS + PORTRAIT_ANIM_HEADROOM * 2
        rw, rh = raw.get_size()
        scale = min(target / rw, target / rh)
        new_size = (max(1, int(rw * scale)), max(1, int(rh * scale)))
        self._portrait_surface = pygame.transform.smoothscale(raw, new_size)

    def update(self, dt: float, inp) -> None:  # type: ignore[no-untyped-def]
        self._time += dt

        # Re-arm the speaking bob whenever the FSM moves to a new state.
        if self._last_seen_state_id != self.current_state_id:
            self._state_entered_at = self._time
            self._last_seen_state_id = self.current_state_id

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

        # Portrait — image if loaded, else colored disc fallback.
        cx, cy = PORTRAIT_X, PORTRAIT_Y

        # Idle animation (always on): the portrait sways horizontally and
        # breathes vertically inside its rim. Hz values are deliberately
        # incommensurate so the motion never visually loops.
        anim_x = math.sin(self._time * 2.0 * math.pi * PORTRAIT_IDLE_SWAY_HZ)
        anim_x *= PORTRAIT_IDLE_SWAY_AMPLITUDE_X
        anim_y = math.sin(self._time * 2.0 * math.pi * PORTRAIT_IDLE_BREATH_HZ)
        anim_y *= PORTRAIT_IDLE_BREATH_AMPLITUDE_Y
        # Speaking bob: a faster vertical jitter for the first N seconds
        # after a state change, where N scales with npc_text length.
        if self._is_speaking():
            anim_y += (
                math.sin(self._time * 2.0 * math.pi * PORTRAIT_SPEAK_BOB_HZ)
                * PORTRAIT_SPEAK_BOB_AMPLITUDE_Y
            )

        if self._portrait_surface is not None:
            # Build a circular alpha mask the size of the portrait disc,
            # blit the (slightly-oversized) image into it shifted by the
            # animation offsets, then mask + blit onto screen. The rim is
            # drawn at FIXED coordinates so the character moves INSIDE the
            # rim instead of dragging it around.
            d = 2 * PORTRAIT_RADIUS
            disc = pygame.Surface((d, d), pygame.SRCALPHA)
            iw, ih = self._portrait_surface.get_size()
            offset_x = (d - iw) // 2 + int(round(anim_x))
            offset_y = (d - ih) // 2 + int(round(anim_y))
            disc.blit(self._portrait_surface, (offset_x, offset_y))
            mask = pygame.Surface((d, d), pygame.SRCALPHA)
            pygame.draw.circle(mask, (255, 255, 255, 255), (d // 2, d // 2), PORTRAIT_RADIUS)
            disc.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
            screen.blit(disc, (cx - PORTRAIT_RADIUS, cy - PORTRAIT_RADIUS))
        else:
            # Fallback: no inner image to translate, so move the whole disc.
            pygame.draw.circle(
                screen, self.character.portrait_color,
                (cx + int(round(anim_x)), cy + int(round(anim_y))),
                PORTRAIT_RADIUS,
            )
        # Ring around the portrait, slightly darker — drawn at the FIXED
        # portrait center so it acts as the static window the character
        # inhabits.
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

    def _is_speaking(self) -> bool:
        """True for the first 1–4 seconds after the FSM enters a state,
        with the duration scaled to the npc_text length. Drives the
        portrait's mouth-flap bob without needing per-character mouth
        sprites."""
        state = self._current_state()
        speech_s = max(
            PORTRAIT_SPEAK_MIN_S,
            min(PORTRAIT_SPEAK_MAX_S, len(state.npc_text) * PORTRAIT_SPEAK_PER_CHAR_S),
        )
        return (self._time - self._state_entered_at) < speech_s

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
