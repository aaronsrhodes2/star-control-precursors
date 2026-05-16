"""TestScript builder + TestHarness runner.

Usage pattern:

    from scz.testing.harness import TestScript

    def my_test():
        s = TestScript()
        s.set_speed(3.0)
        s.wait(0.5)
        s.expect_scene("MainMenuScene")
        s.press("confirm")          # MainMenu A button -> Station
        s.wait(0.5)
        s.expect_scene("StationScene")
        s.press("confirm")          # Talk to Commander (default-selected)
        s.wait(0.5)
        s.expect_scene("DialogScene")
        s.press("cancel")           # Back to Station
        s.wait(0.5)
        s.set_speed(1.0)
        s.end()
        return s

Time advances at *game time*, not wall time — so if the script says "wait
0.5 seconds" and the harness is running at 3x speed, the wait elapses in
0.17 wall-seconds. This way scripts are speed-independent.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from scz.engine.game import Game
    from scz.engine.input import InputManager


# Names of InputManager fields the harness can pulse for one frame
PULSE_FIELDS: set[str] = {
    "confirm",
    "cancel",
    "fire_primary",
    "fire_secondary",
    "menu_up",
    "menu_down",
    "menu_prev",
    "menu_next",
    "rewind",
    "open_switcher",
    "quit",
}


@dataclass
class TestAction:
    """One scheduled action. The harness executes it when game_time >= t."""
    t: float                # game-seconds from script start
    kind: str               # 'press' | 'set_axis' | 'set_speed' | 'expect_scene' | 'expect_dialog_state' | 'log' | 'end'
    params: dict[str, Any] = field(default_factory=dict)


class TestScript:
    """Fluent builder for an action sequence."""

    def __init__(self) -> None:
        self.actions: list[TestAction] = []
        # Cursor advances with wait(); each press/set_axis/etc uses the
        # current cursor as its scheduled time.
        self.cursor: float = 0.0

    def wait(self, seconds: float) -> "TestScript":
        self.cursor += seconds
        return self

    def press(self, button: str) -> "TestScript":
        if button not in PULSE_FIELDS:
            raise ValueError(
                f"Unknown button '{button}'. Valid: {sorted(PULSE_FIELDS)}"
            )
        self.actions.append(TestAction(self.cursor, "press", {"button": button}))
        return self

    def set_axis(self, x: float, y: float) -> "TestScript":
        self.actions.append(TestAction(self.cursor, "set_axis", {"x": x, "y": y}))
        return self

    def release_axis(self) -> "TestScript":
        return self.set_axis(0.0, 0.0)

    def move(self, x: float, y: float, duration: float) -> "TestScript":
        """Hold (x, y) on the left stick for duration seconds, then release."""
        self.set_axis(x, y)
        self.wait(duration)
        self.release_axis()
        return self

    def set_speed(self, multiplier: float) -> "TestScript":
        if multiplier <= 0:
            raise ValueError("speed multiplier must be positive")
        self.actions.append(
            TestAction(self.cursor, "set_speed", {"mult": float(multiplier)})
        )
        return self

    def expect_scene(self, scene_class_name: str) -> "TestScript":
        self.actions.append(
            TestAction(self.cursor, "expect_scene", {"name": scene_class_name})
        )
        return self

    def expect_dialog_state(self, state_id: str) -> "TestScript":
        self.actions.append(
            TestAction(self.cursor, "expect_dialog_state", {"state": state_id})
        )
        return self

    def expect_flag(
        self,
        key: str,
        expected: Any = "ANY_NON_NONE",
    ) -> "TestScript":
        """Assert that game.flags[key] is set.

        With no `expected` argument, just verifies the flag exists and is
        not None (use for "did this side-effect fire?" checks). Pass an
        explicit value to assert equality.
        """
        self.actions.append(
            TestAction(self.cursor, "expect_flag", {"key": key, "expected": expected})
        )
        return self

    def log(self, message: str) -> "TestScript":
        self.actions.append(TestAction(self.cursor, "log", {"msg": message}))
        return self

    def end(self) -> "TestScript":
        self.actions.append(TestAction(self.cursor, "end", {}))
        return self


class TestHarness:
    """Runs a TestScript against a live Game.

    Wired into Game.run() — each frame, after input.update() and before
    the scene's update(), the harness:
      1. Advances game_time by dt
      2. Executes any actions whose t <= game_time
      3. Overlays scripted input on top of the real InputManager fields

    Failures are collected (and printed) but don't stop the script; this
    lets Aaron watch a whole playthrough and see all failing checkpoints
    in one pass.
    """

    def __init__(self, game: "Game", script: TestScript) -> None:
        self.game = game
        self.actions = list(script.actions)
        self.next_idx: int = 0
        self.game_time: float = 0.0
        # Pulses queued by 'press' actions — applied on next apply_to_input(),
        # then cleared.
        self.pulse: dict[str, bool] = {}
        # Persistent axis values from set_axis()
        self.axis_x: float = 0.0
        self.axis_y: float = 0.0
        self.use_axes: bool = False
        # Tracking
        self.failures: list[str] = []
        self.successes: list[str] = []
        self.last_action_label: str = "(starting)"
        self.done: bool = False
        # Diagnostics: presses that arrived in a frame where another press
        # of the same button was already pending (and would coalesce in
        # pulse[button] = True). Printed in the test summary.
        self._coalesce_warnings: list[str] = []

    def step(self, dt: float) -> None:
        """Called each frame by Game.run after input.update(). Advances
        the script clock and fires any actions whose scheduled time has
        arrived."""
        self.game_time += dt
        while self.next_idx < len(self.actions):
            action = self.actions[self.next_idx]
            if action.t > self.game_time:
                break
            self._execute(action)
            self.next_idx += 1

    def _execute(self, action: TestAction) -> None:
        kind = action.kind
        p = action.params
        if kind == "press":
            # If a press is being queued the same frame as a previous press
            # for the same button, the second one would coalesce and be lost
            # (inp.menu_down is a single bool). Track this so we can stretch
            # the pulse across frames.
            if self.pulse.get(p["button"]):
                self._coalesce_warnings.append(
                    f"[t={self.game_time:5.2f}] coalesced press {p['button']}"
                )
            self.pulse[p["button"]] = True
            self.last_action_label = f"press {p['button']}"
        elif kind == "set_axis":
            self.axis_x = float(p["x"])
            self.axis_y = float(p["y"])
            self.use_axes = (self.axis_x != 0.0 or self.axis_y != 0.0)
            self.last_action_label = (
                f"axis ({self.axis_x:+.1f}, {self.axis_y:+.1f})"
                if self.use_axes
                else "axis released"
            )
        elif kind == "set_speed":
            self.game.test_speed = float(p["mult"])
            self.last_action_label = f"speed {p['mult']}x"
        elif kind == "expect_scene":
            actual = type(self.game.current_scene).__name__ if self.game.current_scene else "None"
            expected = p["name"]
            if actual == expected:
                msg = f"[t={self.game_time:5.2f}] OK   scene = {expected}"
                self.successes.append(msg)
                print(msg)
            else:
                msg = (
                    f"[t={self.game_time:5.2f}] FAIL expected scene {expected!r}, "
                    f"got {actual!r}"
                )
                self.failures.append(msg)
                print(msg)
            self.last_action_label = f"expect_scene {expected}"
        elif kind == "expect_dialog_state":
            from scz.dialog.scene import DialogScene
            scene = self.game.current_scene
            expected = p["state"]
            if isinstance(scene, DialogScene):
                actual = scene.current_state_id
                if actual == expected:
                    msg = f"[t={self.game_time:5.2f}] OK   dialog state = {expected}"
                    self.successes.append(msg)
                    print(msg)
                else:
                    msg = (
                        f"[t={self.game_time:5.2f}] FAIL dialog state expected "
                        f"{expected!r}, got {actual!r}"
                    )
                    self.failures.append(msg)
                    print(msg)
            else:
                msg = (
                    f"[t={self.game_time:5.2f}] FAIL not in DialogScene "
                    f"(scene = {type(scene).__name__ if scene else None})"
                )
                self.failures.append(msg)
                print(msg)
            self.last_action_label = f"expect_dialog_state {expected}"
        elif kind == "expect_flag":
            key = p["key"]
            expected = p["expected"]
            actual = self.game.flags.get(key)
            if expected == "ANY_NON_NONE":
                ok = actual is not None
                expected_str = "not None"
            else:
                ok = actual == expected
                expected_str = repr(expected)
            if ok:
                msg = (
                    f"[t={self.game_time:5.2f}] OK   flag {key} = "
                    f"{actual!r}  (expected {expected_str})"
                )
                self.successes.append(msg)
                print(msg)
            else:
                msg = (
                    f"[t={self.game_time:5.2f}] FAIL flag {key} expected "
                    f"{expected_str}, got {actual!r}"
                )
                self.failures.append(msg)
                print(msg)
            self.last_action_label = f"expect_flag {key}"
        elif kind == "log":
            print(f"[t={self.game_time:5.2f}] LOG  {p['msg']}")
            self.last_action_label = p["msg"]
        elif kind == "end":
            self.done = True
            self.last_action_label = "END"
            self._print_summary()

    def apply_to_input(self, inp: "InputManager") -> None:
        """Overlay scripted pulses + axes on top of real input. Call after
        InputManager.update() so the scene sees the combined state."""
        for k, v in self.pulse.items():
            if hasattr(inp, k):
                setattr(inp, k, v)
        self.pulse.clear()
        if self.use_axes:
            inp.move_x = self.axis_x
            inp.move_y = self.axis_y

    def _print_summary(self) -> None:
        print()
        print("=" * 60)
        print(
            f"Test complete: {len(self.successes)} passed, "
            f"{len(self.failures)} failed."
        )
        if self.failures:
            print("\nFailures:")
            for f in self.failures:
                print("  " + f)
        if self._coalesce_warnings:
            print(
                f"\n{len(self._coalesce_warnings)} press(es) coalesced "
                "into the same frame (lost):"
            )
            for w in self._coalesce_warnings:
                print("  " + w)
        print("=" * 60)
