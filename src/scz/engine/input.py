"""Input abstraction: pygame events → semantic events.

Treats keyboard and Xbox controller as equivalent semantic input streams so
the rest of the engine never sees raw keys or button codes. This keeps the
controller-first design promise: every scene gets the same semantic events,
and a future rebinding screen has only one layer to change.
"""

from __future__ import annotations

import pygame


# Xbox controller button conventions (pygame on Windows, default SDL mapping):
# 0=A, 1=B, 2=X, 3=Y, 4=LB, 5=RB, 6=Back/View, 7=Start/Menu,
# 8=Left-stick-click, 9=Right-stick-click
XBOX_A = 0
XBOX_B = 1
XBOX_X = 2
XBOX_Y = 3
XBOX_LB = 4
XBOX_RB = 5
XBOX_BACK = 6
XBOX_START = 7

# Analog stick deadzone (sticks at rest report small non-zero values)
STICK_DEADZONE = 0.18


class InputManager:
    """Polls pygame events and exposes semantic input state.

    Per-frame discrete events (fire, confirm, etc.) are *edge-triggered* — set
    True for one frame on press, then back to False. Analog axes are
    *level* — updated every frame to current value.
    """

    def __init__(self) -> None:
        self.joysticks: list[pygame.joystick.JoystickType] = []
        self._refresh_joysticks()

        # Analog (level)
        self.move_x: float = 0.0
        self.move_y: float = 0.0
        self.aim_x: float = 0.0
        self.aim_y: float = 0.0

        # Discrete (edge-triggered, reset each update)
        self.confirm: bool = False
        self.cancel: bool = False
        self.fire_primary: bool = False
        self.fire_secondary: bool = False
        self.open_map: bool = False
        self.quit: bool = False
        self.menu_prev: bool = False
        self.menu_next: bool = False
        # Time Drive — engage chronometric rewind (5-min real-time)
        self.rewind: bool = False
        # Debug: open the scene switcher (F1)
        self.open_switcher: bool = False

    def _refresh_joysticks(self) -> None:
        self.joysticks = []
        for i in range(pygame.joystick.get_count()):
            j = pygame.joystick.Joystick(i)
            j.init()
            self.joysticks.append(j)

    def has_controller(self) -> bool:
        return len(self.joysticks) > 0

    def update(self, events: list[pygame.event.Event]) -> None:
        # Reset edge-triggered state
        self.confirm = False
        self.cancel = False
        self.fire_primary = False
        self.fire_secondary = False
        self.open_map = False
        self.quit = False
        self.menu_prev = False
        self.menu_next = False
        self.rewind = False
        self.open_switcher = False

        # ----- Keyboard (level axes from held keys) -----
        keys = pygame.key.get_pressed()

        kbd_x = (
            (1.0 if keys[pygame.K_d] or keys[pygame.K_RIGHT] else 0.0)
            - (1.0 if keys[pygame.K_a] or keys[pygame.K_LEFT] else 0.0)
        )
        kbd_y = (
            (1.0 if keys[pygame.K_s] or keys[pygame.K_DOWN] else 0.0)
            - (1.0 if keys[pygame.K_w] or keys[pygame.K_UP] else 0.0)
        )

        self.move_x = kbd_x
        self.move_y = kbd_y
        self.aim_x = 0.0
        self.aim_y = 0.0

        # ----- Controller (overrides keyboard when stick is active) -----
        if self.joysticks:
            j = self.joysticks[0]
            try:
                left_x = _apply_deadzone(j.get_axis(0))
                left_y = _apply_deadzone(j.get_axis(1))
                if left_x != 0.0 or left_y != 0.0:
                    self.move_x = left_x
                    self.move_y = left_y
                # Right stick (axes 2 and 3 on most Xbox mappings, but driver
                # quirks exist; we just read whatever's there)
                if j.get_numaxes() >= 4:
                    self.aim_x = _apply_deadzone(j.get_axis(2))
                    self.aim_y = _apply_deadzone(j.get_axis(3))
            except pygame.error:
                # Joystick may have been disconnected mid-frame
                self._refresh_joysticks()

        # ----- Discrete events (edge-triggered) -----
        for ev in events:
            if ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_ESCAPE:
                    # Esc backs out of the current scene (cancel). The
                    # outermost scene treats unhandled cancel as quit.
                    # This prevents the "I pressed Esc and lost my game"
                    # bug; window-close / Start button / Alt+F4 still quit.
                    self.cancel = True
                elif ev.key in (pygame.K_RETURN, pygame.K_SPACE):
                    self.confirm = True
                elif ev.key == pygame.K_BACKSPACE:
                    self.cancel = True
                elif ev.key == pygame.K_m:
                    self.open_map = True
                elif ev.key in (pygame.K_LSHIFT, pygame.K_RSHIFT):
                    self.fire_secondary = True
                elif ev.key == pygame.K_LEFTBRACKET:
                    self.menu_prev = True
                elif ev.key == pygame.K_RIGHTBRACKET:
                    self.menu_next = True
                elif ev.key == pygame.K_r:
                    self.rewind = True
                elif ev.key == pygame.K_F1:
                    # Debug: open the scene switcher
                    self.open_switcher = True

            elif ev.type == pygame.JOYBUTTONDOWN:
                if ev.button == XBOX_A:
                    self.confirm = True
                elif ev.button == XBOX_B:
                    self.cancel = True
                elif ev.button == XBOX_X:
                    self.fire_secondary = True
                elif ev.button == XBOX_Y:
                    self.open_map = True
                elif ev.button == XBOX_LB:
                    self.menu_prev = True
                elif ev.button == XBOX_RB:
                    self.menu_next = True
                elif ev.button == XBOX_START:
                    self.quit = True
                elif ev.button == XBOX_BACK:
                    # Back button = "go back in time" — engage Time Drive
                    self.rewind = True

            elif ev.type == pygame.JOYDEVICEADDED:
                self._refresh_joysticks()
            elif ev.type == pygame.JOYDEVICEREMOVED:
                self._refresh_joysticks()


def _apply_deadzone(v: float) -> float:
    """Map raw stick value through a deadzone, then re-scale to [-1, 1]."""
    if abs(v) < STICK_DEADZONE:
        return 0.0
    sign = 1.0 if v > 0 else -1.0
    return sign * (abs(v) - STICK_DEADZONE) / (1.0 - STICK_DEADZONE)
