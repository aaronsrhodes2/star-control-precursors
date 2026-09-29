"""Pause menu overlay — opened on `cancel` from top-level scenes.

Replaces the legacy "cancel quits the game" behavior in HyperspaceScene
and StationScene (per HANDOFF_design_chat.md 2026-05-18 UX bug entry).

Opens as a modal overlay over whatever scene is active, so the
underlying scene stays loaded and resuming requires no re-init.

Options:
- Resume          → close overlay; underlying scene continues
- Save Now        → take an immediate campaign snapshot (no-op if no
                    active campaign); close overlay
- Return to Title → save (if campaign active) then transition to
                    MainMenuScene (which closes the overlay implicitly)
- Quit Game       → save (if campaign active) then game.quit()

Test-harness contract: under test, the harness can cancel into the
pause menu without terminating the test run. Selecting Resume returns
control to the original scene; selecting Return to Title transitions
to MainMenu (where the walk can `s.end()` cleanly).
"""

from __future__ import annotations

import pygame

from scz.engine.scene import Scene


_PALETTE_DIM_BG = (0, 0, 0, 180)
_PALETTE_PANEL = (16, 18, 32)
_PALETTE_BORDER = (180, 200, 220)
_PALETTE_TITLE = (240, 230, 200)
_PALETTE_ITEM = (200, 210, 220)
_PALETTE_ITEM_HI = (240, 230, 180)
_PALETTE_HINT = (140, 160, 190)


class PauseMenuScene(Scene):
    """Modal overlay — Resume / Save / Return to Title / Quit Game."""

    _ITEMS: tuple[tuple[str, str], ...] = (
        ("Resume",            "resume"),
        ("Save Now",          "save"),
        ("Return to Title",   "main_menu"),
        ("Quit Game",         "quit"),
    )

    def __init__(self) -> None:
        super().__init__()
        self.menu_idx: int = 0
        self.last_msg: str = ""
        self.last_msg_age: float = 0.0
        self.fonts: dict[str, pygame.font.Font] = {}

    def on_enter(self) -> None:
        self.fonts["title"] = pygame.font.SysFont("consolas", 40, bold=True)
        self.fonts["item"] = pygame.font.SysFont("consolas", 26)
        self.fonts["hint"] = pygame.font.SysFont("consolas", 16)
        self.fonts["msg"] = pygame.font.SysFont("consolas", 18)

    def snapshot(self) -> dict | None:
        return None    # the pause menu itself isn't rewindable

    def update(self, dt: float, inp) -> None:  # type: ignore[no-untyped-def]
        if self.last_msg:
            self.last_msg_age += dt
            if self.last_msg_age > 2.5:
                self.last_msg = ""

        # Cancel = Resume — dismisses the pause menu.
        if inp.cancel and self.game is not None:
            self.game.close_overlay()
            return

        n = len(self._ITEMS)
        if inp.menu_up:
            self.menu_idx = (self.menu_idx - 1) % n
        elif inp.menu_down:
            self.menu_idx = (self.menu_idx + 1) % n
        if inp.confirm:
            _label, action = self._ITEMS[self.menu_idx]
            self._do_action(action)

    def _do_action(self, action: str) -> None:
        if self.game is None:
            return
        if action == "resume":
            self.game.close_overlay()
            return
        if action == "save":
            if self.game.campaign_manager.has_active():
                try:
                    self.game.campaign_manager.snapshot(self.game)
                    self.last_msg = "campaign saved"
                except Exception as exc:    # noqa: BLE001
                    self.last_msg = f"save failed: {exc}"
            else:
                self.last_msg = "no active campaign — nothing to save"
            self.last_msg_age = 0.0
            return
        if action == "main_menu":
            if self.game.campaign_manager.has_active():
                try:
                    self.game.campaign_manager.snapshot(self.game)
                except Exception:
                    pass
            # set_scene closes any active overlay; safe to call from
            # within the overlay's own update.
            from scz.scenes.stubs import MainMenuScene
            self.game.set_scene(MainMenuScene())
            return
        if action == "quit":
            if self.game.campaign_manager.has_active():
                try:
                    self.game.campaign_manager.snapshot(self.game)
                except Exception:
                    pass
            self.game.quit()

    def render(self, screen: pygame.Surface) -> None:
        if self.game is None:
            return
        sw, sh = screen.get_size()

        # Dim the underlying scene by blitting a translucent black sheet
        dim = pygame.Surface((sw, sh), pygame.SRCALPHA)
        dim.fill(_PALETTE_DIM_BG)
        screen.blit(dim, (0, 0))

        # Centered panel
        panel_w = 480
        panel_h = 360
        px = (sw - panel_w) // 2
        py = (sh - panel_h) // 2
        pygame.draw.rect(screen, _PALETTE_PANEL, (px, py, panel_w, panel_h))
        pygame.draw.rect(screen, _PALETTE_BORDER, (px, py, panel_w, panel_h), 2)

        # Title
        title = self.fonts["title"].render("PAUSED", True, _PALETTE_TITLE)
        tw, _th = title.get_size()
        screen.blit(title, (px + (panel_w - tw) // 2, py + 32))

        # Menu items
        iy = py + 110
        for i, (label, _action) in enumerate(self._ITEMS):
            is_sel = (i == self.menu_idx)
            color = _PALETTE_ITEM_HI if is_sel else _PALETTE_ITEM
            mark = "> " if is_sel else "  "
            line = self.fonts["item"].render(f"{mark}{label}", True, color)
            lw, _lh = line.get_size()
            screen.blit(line, (px + (panel_w - lw) // 2, iy))
            iy += 44

        # Last-action confirmation (fades over 2.5s)
        if self.last_msg:
            alpha = max(0, 255 - int(self.last_msg_age / 2.5 * 255))
            msg = self.fonts["msg"].render(self.last_msg, True, (180, 240, 200))
            msg.set_alpha(alpha)
            mw, _mh = msg.get_size()
            screen.blit(msg, (px + (panel_w - mw) // 2, py + panel_h - 60))

        # Bottom hint
        hint = self.fonts["hint"].render(
            "B / Esc: resume    A: select", True, _PALETTE_HINT,
        )
        hw, _hh = hint.get_size()
        screen.blit(hint, (px + (panel_w - hw) // 2, py + panel_h - 28))
