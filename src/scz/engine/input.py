"""Input abstraction: pygame events → semantic events.

Treats keyboard and Xbox controller as equivalent semantic input streams so
the rest of the engine never sees raw keys or button codes. Per-scene
interpretation is the rule — the input layer surfaces well-named events,
each scene decides which ones it cares about.

Aaron's universal control scheme:
- **A**            confirm / menu select / autopilot toggle / thrust
- **B**            cancel / menu back
- **X + RT**       fire (primary weapon in combat)
- **Y + RB**       fire (special weapon in combat)
- **D-pad up/dn**  menu navigation (also arrow keys; menus wrap)
- **D-pad lt/rt**  menu nav left/right (also zoom in hyperspace; - / =)
- **Left stick**   move (with WASD as keyboard alternate)
- **Right stick**  aim (combat / future cursor)
- **Back (View)**  Time Drive rewind
- **Start (Menu)** quit game
- **R-stick click**open scene switcher (debug, also F1)

All menus throughout the game stack vertically and wrap from bottom to top.
The SceneSwitcher is the reference implementation.
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
XBOX_LSTICK = 8   # press the left stick (L3)
XBOX_RSTICK = 9   # press the right stick (R3) — bound to scene switcher

# Trigger axes (analog). On Windows SDL2 Xbox mapping these are axes 4 and 5;
# both report -1.0 fully released, +1.0 fully pressed.
XBOX_LT_AXIS = 4
XBOX_RT_AXIS = 5

# Threshold for treating an analog trigger as a discrete "pressed" event.
# Hysteresis: must cross 0.5 to fire, must fall below 0.3 to re-arm.
TRIGGER_PRESS_THRESHOLD = 0.5
TRIGGER_RELEASE_THRESHOLD = 0.3

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

        # Analog (level) — left stick + arrow/WASD blend
        self.move_x: float = 0.0
        self.move_y: float = 0.0
        # Right stick (combat aim, future cursor work)
        self.aim_x: float = 0.0
        self.aim_y: float = 0.0

        # Discrete (edge-triggered, reset each update). Some events have
        # multiple bindings (e.g. fire_primary fires on X *or* RT).
        self.confirm: bool = False        # A / Space / Enter — select / autopilot / thrust
        self.cancel: bool = False         # B / Esc / Backspace — back
        self.fire_primary: bool = False   # X / RT / F — fire weapon
        self.fire_secondary: bool = False # Y / RB / Shift — special weapon
        self.menu_up: bool = False        # D-pad up / arrow up — navigate menu
        self.menu_down: bool = False      # D-pad down / arrow down
        self.menu_prev: bool = False      # D-pad left / arrow left / - / LB — menu left / zoom out
        self.menu_next: bool = False      # D-pad right / arrow right / = / RB — menu right / zoom in
        self.rewind: bool = False         # Back / R — Time Drive
        self.open_switcher: bool = False  # R3 / F1 — scene switcher
        self.quit: bool = False           # Start — quit game
        self.toggle_zones: bool = False   # Z — hyperspace species-zone overlay
        self.open_search: bool = False    # / — hyperspace star-name search

        # Internal state — for trigger edge detection across frames
        self._rt_was_pressed: bool = False
        self._lt_was_pressed: bool = False
        # And for hat (D-pad) edge detection — pygame surfaces hat as level
        # state but only emits JOYHATMOTION when it changes, so we track the
        # previous (x, y) to detect direction changes properly.
        self._prev_hat: tuple[int, int] = (0, 0)

    def _refresh_joysticks(self) -> None:
        self.joysticks = []
        for i in range(pygame.joystick.get_count()):
            j = pygame.joystick.Joystick(i)
            j.init()
            self.joysticks.append(j)
        self._rt_was_pressed = False
        self._lt_was_pressed = False
        self._prev_hat = (0, 0)

    def has_controller(self) -> bool:
        return len(self.joysticks) > 0

    def update(self, events: list[pygame.event.Event]) -> None:
        # Stash this frame's raw events for consumers like text-input
        # modals (SearchOverlay) that need full keydown / TEXTINPUT data.
        self.recent_events: list[pygame.event.Event] = events
        # Reset edge-triggered state
        self.confirm = False
        self.cancel = False
        self.fire_primary = False
        self.fire_secondary = False
        self.menu_up = False
        self.menu_down = False
        self.menu_prev = False
        self.menu_next = False
        self.rewind = False
        self.open_switcher = False
        self.quit = False
        self.toggle_zones = False
        self.open_search = False

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

        # ----- Controller (left stick overrides keyboard when active) -----
        if self.joysticks:
            j = self.joysticks[0]
            try:
                left_x = _apply_deadzone(j.get_axis(0))
                left_y = _apply_deadzone(j.get_axis(1))
                if left_x != 0.0 or left_y != 0.0:
                    self.move_x = left_x
                    self.move_y = left_y
                # Right stick — combat aim
                if j.get_numaxes() >= 4:
                    self.aim_x = _apply_deadzone(j.get_axis(2))
                    self.aim_y = _apply_deadzone(j.get_axis(3))

                # Analog triggers as edge-triggered buttons
                if j.get_numaxes() >= XBOX_RT_AXIS + 1:
                    rt_val = j.get_axis(XBOX_RT_AXIS)
                    rt_pressed_now = rt_val > TRIGGER_PRESS_THRESHOLD
                    if rt_pressed_now and not self._rt_was_pressed:
                        self.fire_primary = True
                    if rt_val < TRIGGER_RELEASE_THRESHOLD:
                        self._rt_was_pressed = False
                    elif rt_pressed_now:
                        self._rt_was_pressed = True
                if j.get_numaxes() >= XBOX_LT_AXIS + 1:
                    lt_val = j.get_axis(XBOX_LT_AXIS)
                    lt_pressed_now = lt_val > TRIGGER_PRESS_THRESHOLD
                    # LT not yet bound to anything; reserved for future
                    # boost/brake. We track the edge so re-binding is trivial.
                    if lt_val < TRIGGER_RELEASE_THRESHOLD:
                        self._lt_was_pressed = False
                    elif lt_pressed_now:
                        self._lt_was_pressed = True
            except pygame.error:
                # Joystick may have been disconnected mid-frame
                self._refresh_joysticks()

        # ----- Discrete events (edge-triggered) -----
        for ev in events:
            if ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_ESCAPE:
                    self.cancel = True
                elif ev.key in (pygame.K_RETURN, pygame.K_SPACE):
                    self.confirm = True
                elif ev.key == pygame.K_BACKSPACE:
                    self.cancel = True
                elif ev.key == pygame.K_f:
                    self.fire_primary = True
                elif ev.key in (pygame.K_LSHIFT, pygame.K_RSHIFT):
                    self.fire_secondary = True
                elif ev.key == pygame.K_UP:
                    self.menu_up = True
                elif ev.key == pygame.K_DOWN:
                    self.menu_down = True
                elif ev.key in (pygame.K_LEFT, pygame.K_LEFTBRACKET):
                    self.menu_prev = True
                elif ev.key in (pygame.K_RIGHT, pygame.K_RIGHTBRACKET):
                    self.menu_next = True
                elif ev.key in (pygame.K_MINUS, pygame.K_KP_MINUS):
                    self.menu_prev = True
                elif ev.key in (pygame.K_EQUALS, pygame.K_KP_PLUS):
                    self.menu_next = True
                elif ev.key == pygame.K_r:
                    self.rewind = True
                elif ev.key == pygame.K_F1:
                    self.open_switcher = True
                elif ev.key == pygame.K_z:
                    self.toggle_zones = True
                elif ev.key == pygame.K_SLASH:
                    self.open_search = True

            elif ev.type == pygame.JOYBUTTONDOWN:
                if ev.button == XBOX_A:
                    self.confirm = True
                elif ev.button == XBOX_B:
                    self.cancel = True
                elif ev.button == XBOX_X:
                    self.fire_primary = True
                elif ev.button == XBOX_Y:
                    self.fire_secondary = True
                elif ev.button == XBOX_LB:
                    self.menu_prev = True
                elif ev.button == XBOX_RB:
                    # RB fires both special-weapon AND menu-next (zoom-in
                    # in hyperspace). Per Aaron's bindings: RB is special
                    # weapon in combat; in non-combat scenes the menu_next
                    # semantic carries it. Scenes choose which to read.
                    self.fire_secondary = True
                    self.menu_next = True
                elif ev.button == XBOX_START:
                    self.quit = True
                elif ev.button == XBOX_BACK:
                    self.rewind = True
                elif ev.button == XBOX_RSTICK:
                    self.open_switcher = True

            elif ev.type == pygame.JOYHATMOTION:
                # D-pad: hat value is (x, y) where +y is up on Xbox SDL2
                hx, hy = ev.value
                # Edge-triggered: only fire on changes, not held state
                prev_hx, prev_hy = self._prev_hat
                if hy == 1 and prev_hy != 1:
                    self.menu_up = True
                elif hy == -1 and prev_hy != -1:
                    self.menu_down = True
                if hx == -1 and prev_hx != -1:
                    self.menu_prev = True
                elif hx == 1 and prev_hx != 1:
                    self.menu_next = True
                self._prev_hat = (hx, hy)

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
