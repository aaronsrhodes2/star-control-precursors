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

# Layered-render layout (only used when character.avatar_path is set).
# A rectangular scene panel takes the place of the circular disc — the
# background fills the panel, the transparent avatar floats on top with
# procedural motion. Name/title/text shift right to clear the wider
# panel. All coords assume a 1920x1080 canvas; the panel scales with
# the screen via render-time clamping.
LAYERED_PANEL_X = 40
LAYERED_PANEL_Y = 60
LAYERED_PANEL_W = 420
LAYERED_PANEL_H = 600
LAYERED_PANEL_BORDER_PX = 3
LAYERED_NAME_X = LAYERED_PANEL_X + LAYERED_PANEL_W + 40
LAYERED_NAME_Y = 110
LAYERED_TEXT_AREA_X = LAYERED_NAME_X
LAYERED_TEXT_AREA_Y = 240
LAYERED_TEXT_AREA_W = 1920 - LAYERED_NAME_X - 160
LAYERED_TEXT_AREA_H = 380
LAYERED_AVATAR_MARGIN_PX = 24
# Headroom for animation translation inside the panel.
LAYERED_AVATAR_ANIM_HEADROOM_PX = 14


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
        # Layered-render surfaces (only when character.avatar_path is set).
        # _avatar_surface holds the transparent character image, pre-scaled
        # to fit inside (panel - margin) bounds with anim headroom. The
        # background list is pre-scaled to panel dims; the active one is
        # picked at render time. None means "fall through to legacy disc".
        self._avatar_surface: pygame.Surface | None = None
        self._background_surfaces: list[pygame.Surface] = []
        self._active_background_idx: int = 0
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
        # Dialog opens as a modal-like overlay over the prior scene's
        # music. Play modal_open + acknowledge so the player knows
        # contact has been established.
        if self.game is not None and hasattr(self.game, "sfx"):
            self.game.sfx.play("ui/modal_open")
            self.game.sfx.play("ui/hud_acknowledge")
        # Prefer the layered (avatar + backgrounds) render path. If the
        # avatar fails to load OR the character has no avatar configured,
        # fall through to the legacy disc loader.
        if self.character.avatar_path is not None:
            self._load_layered_surfaces()
        if self._avatar_surface is None:
            self._load_portrait_image()

    def on_exit(self) -> None:
        # Dialog closing — modal_close on the way out.
        if self.game is not None and hasattr(self.game, "sfx"):
            self.game.sfx.play("ui/modal_close")

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

    def _load_layered_surfaces(self) -> None:
        """Load + pre-scale the avatar and each registered background for
        the layered render path. The avatar is the transparent character
        PNG; backgrounds are scene-setting backdrops. If avatar loading
        fails, leave `_avatar_surface` None so the caller falls back to
        the legacy disc."""
        avatar_path_str = self.character.avatar_path
        if not avatar_path_str:
            return
        avatar_path = Path(avatar_path_str)
        if not avatar_path.is_absolute():
            avatar_path = _PROJECT_ROOT / avatar_path_str
        if not avatar_path.exists():
            return
        try:
            raw = pygame.image.load(str(avatar_path)).convert_alpha()
        except pygame.error:
            return
        # Scale the avatar to fit the panel interior (panel minus border
        # minus margin), with an anim-headroom bonus so the avatar can
        # translate without revealing transparent edges of the panel.
        target_w = LAYERED_PANEL_W - 2 * LAYERED_AVATAR_MARGIN_PX
        target_h = LAYERED_PANEL_H - 2 * LAYERED_AVATAR_MARGIN_PX
        rw, rh = raw.get_size()
        s = min(target_w / rw, target_h / rh)
        new_size = (max(1, int(rw * s)), max(1, int(rh * s)))
        self._avatar_surface = pygame.transform.smoothscale(raw, new_size)
        # Backgrounds — scale each to panel dims. Iterating tuple keeps
        # the registered order so the active-index selection is stable.
        for bg in self.character.backgrounds:
            bg_path = Path(bg.image_path)
            if not bg_path.is_absolute():
                bg_path = _PROJECT_ROOT / bg.image_path
            if not bg_path.exists():
                continue
            try:
                raw_bg = pygame.image.load(str(bg_path)).convert_alpha()
            except pygame.error:
                continue
            scaled = pygame.transform.smoothscale(
                raw_bg, (LAYERED_PANEL_W, LAYERED_PANEL_H)
            )
            self._background_surfaces.append(scaled)

    def update(self, dt: float, inp) -> None:  # type: ignore[no-untyped-def]
        self._time += dt

        # Re-arm the speaking bob whenever the FSM moves to a new state.
        if self._last_seen_state_id != self.current_state_id:
            self._state_entered_at = self._time
            self._last_seen_state_id = self.current_state_id

        state = self._current_state()

        # B / Esc → exit dialog
        if inp.cancel:
            if self.game is not None and hasattr(self.game, "sfx"):
                self.game.sfx.play("ui/menu_cancel")
            self._exit_dialog()
            return

        # Auto-terminate if state has no choices (e.g. one-shot farewell)
        if not state.choices:
            self._exit_dialog()
            return

        def _click(kind: str = "select") -> None:
            if self.game is not None and hasattr(self.game, "sfx"):
                self.game.sfx.play(f"ui/menu_{kind}")

        # Menu navigation: D-pad up/down + arrow keys (edge), wrap
        n = len(state.choices)
        if inp.menu_up:
            self.selected_choice = (self.selected_choice - 1) % n
            _click()
        elif inp.menu_down:
            self.selected_choice = (self.selected_choice + 1) % n
            _click()

        # Confirm → pick this choice
        if inp.confirm:
            _click("confirm")
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

        # Procedural animation offsets — shared by both render paths.
        # Idle sway/breath are always on; speak bob fires for the first
        # 1-4 s of each new state (duration scales with npc_text length).
        anim_x, anim_y, anim_tilt_rad = self._procedural_offsets()

        if self._avatar_surface is not None:
            self._render_layered(screen, anim_x, anim_y, anim_tilt_rad)
            name_x = LAYERED_NAME_X
            name_y = LAYERED_NAME_Y
            text_rect = (
                LAYERED_TEXT_AREA_X, LAYERED_TEXT_AREA_Y,
                LAYERED_TEXT_AREA_W, LAYERED_TEXT_AREA_H,
            )
        else:
            self._render_legacy_disc(screen, anim_x, anim_y)
            name_x = NAME_X
            name_y = NAME_Y
            text_rect = (TEXT_AREA_X, TEXT_AREA_Y, TEXT_AREA_W, TEXT_AREA_H)

        # Name + title
        name_surf = self.fonts["title"].render(
            self.character.name, True, (235, 240, 250)
        )
        screen.blit(name_surf, (name_x, name_y))
        title_surf = self.fonts["subtitle"].render(
            self.character.title, True, (160, 180, 210)
        )
        screen.blit(title_surf, (name_x, name_y + 44))

        # NPC text block — word-wrapped
        state = self._current_state()
        self._render_wrapped(
            screen,
            state.npc_text,
            self.fonts["npc"],
            text_rect,
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

    def _procedural_offsets(self) -> tuple[float, float, float]:
        """Compute the current frame's (sway_x, breath_y, tilt_rad) for
        the portrait. Reads articulation amplitude overrides if present
        on the character; falls back to defaults otherwise."""
        spec = self.character.articulation
        sway_amp = spec.sway_amplitude_px if spec else PORTRAIT_IDLE_SWAY_AMPLITUDE_X
        breath_amp = spec.breath_amplitude_px if spec else PORTRAIT_IDLE_BREATH_AMPLITUDE_Y
        bob_amp = spec.speak_bob_amplitude_px if spec else PORTRAIT_SPEAK_BOB_AMPLITUDE_Y
        tilt_amp = spec.speak_tilt_amplitude_rad if spec else 0.0

        anim_x = math.sin(self._time * 2.0 * math.pi * PORTRAIT_IDLE_SWAY_HZ) * sway_amp
        anim_y = math.sin(self._time * 2.0 * math.pi * PORTRAIT_IDLE_BREATH_HZ) * breath_amp
        anim_tilt = 0.0
        if self._is_speaking():
            anim_y += math.sin(self._time * 2.0 * math.pi * PORTRAIT_SPEAK_BOB_HZ) * bob_amp
            anim_tilt = math.sin(self._time * 2.0 * math.pi * PORTRAIT_SPEAK_BOB_HZ * 0.6) * tilt_amp
        return anim_x, anim_y, anim_tilt

    def _render_legacy_disc(
        self, screen: pygame.Surface, anim_x: float, anim_y: float
    ) -> None:
        """Render the original circular-disc portrait. Used when the
        character has portrait_image_path but no avatar_path."""
        cx, cy = PORTRAIT_X, PORTRAIT_Y
        if self._portrait_surface is not None:
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
            pygame.draw.circle(
                screen, self.character.portrait_color,
                (cx + int(round(anim_x)), cy + int(round(anim_y))),
                PORTRAIT_RADIUS,
            )
        rim = tuple(max(0, c - 50) for c in self.character.portrait_color)
        pygame.draw.circle(screen, rim, (cx, cy), PORTRAIT_RADIUS, 3)

    def _render_layered(
        self, screen: pygame.Surface, anim_x: float, anim_y: float, anim_tilt_rad: float
    ) -> None:
        """Render the layered scene panel: background (full-bleed inside
        the panel) + transparent avatar (centered, animated). Both layers
        are clipped to the panel rect so the avatar can translate outside
        the visible area without bleeding into the dialog text."""
        panel_rect = pygame.Rect(
            LAYERED_PANEL_X, LAYERED_PANEL_Y, LAYERED_PANEL_W, LAYERED_PANEL_H,
        )

        # Panel surface composes the layers; we blit it to the screen at
        # the end so clipping is local.
        panel = pygame.Surface((LAYERED_PANEL_W, LAYERED_PANEL_H), pygame.SRCALPHA)

        # Background — pick the active one if any, else a dark navy fill
        # that matches the prompt-spec background color so avatar-on-bg
        # looks consistent with avatar-on-fallback.
        if self._background_surfaces:
            bg = self._background_surfaces[
                self._active_background_idx % len(self._background_surfaces)
            ]
            panel.blit(bg, (0, 0))
        else:
            panel.fill((10, 14, 26))

        # Avatar — rotate first (if speaking-tilt is non-zero), then translate
        # within the panel. Rotation uses rotozoom to also handle scaling=1.
        avatar_surf = self._avatar_surface
        assert avatar_surf is not None
        if abs(anim_tilt_rad) > 0.001:
            avatar_surf = pygame.transform.rotozoom(
                avatar_surf, math.degrees(anim_tilt_rad), 1.0,
            )
        aw, ah = avatar_surf.get_size()
        avatar_cx = LAYERED_PANEL_W // 2 + int(round(anim_x))
        # Bottom-anchor the avatar with a small margin so feet/base are
        # near the panel floor and the head/upper body draws the eye.
        avatar_bottom = LAYERED_PANEL_H - LAYERED_AVATAR_MARGIN_PX
        avatar_top = avatar_bottom - ah + int(round(anim_y))
        panel.blit(avatar_surf, (avatar_cx - aw // 2, avatar_top))

        # Frame the panel with a subtle border so it reads as a portrait
        # window rather than free-floating art. Uses the character's
        # portrait_color for tonal coherence.
        screen.blit(panel, panel_rect.topleft)
        rim = tuple(min(255, max(0, c)) for c in self.character.portrait_color)
        pygame.draw.rect(screen, rim, panel_rect, LAYERED_PANEL_BORDER_PX)

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
