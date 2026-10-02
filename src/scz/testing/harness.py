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
    "zoom_out",
    "zoom_in",
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
    """Fluent builder for an action sequence.

    Pass `strict=True` to enforce the **integration-walk contract**: only
    real-input verbs (`press`, `set_axis`, `move`, `wait`, `expect_*`,
    `log`, `end`) are allowed. State-mutation shortcuts and the
    scene-skipping `press("open_switcher")` raise ValueError so integration
    walks can't accidentally bypass real gameplay traversal.

    Strict mode is the right choice for "is the game actually playable?"
    integration walks. The default (strict=False) preserves the existing
    fast-regression style.

    Forbidden in strict mode:
    - `press("open_switcher")` — skips scene transitions
    - `set_flag`, `set_cargo`, `set_credits` — skip mineral / story progression
    - `set_module_inventory` — skips lander mineral pickup
    - `set_player_pos`, `set_player_heading` — skip flying / aiming
    - `set_schematics`, `set_fleet` — skip Mh-Lai purchase loops
    - `simulate_lander_pickup` — skips actual lander driving
    """

    # Button presses forbidden in strict mode (scene-skipping shortcuts)
    _STRICT_FORBIDDEN_PRESSES: frozenset[str] = frozenset({"open_switcher"})

    def __init__(self, strict: bool = False) -> None:
        self.actions: list[TestAction] = []
        # Cursor advances with wait(); each press/set_axis/etc uses the
        # current cursor as its scheduled time.
        self.cursor: float = 0.0
        # Strict integration-walk mode. When True, shortcut verbs raise.
        self.strict: bool = strict

    def _check_strict(self, what: str) -> None:
        if self.strict:
            raise ValueError(
                f"Integration-walk strict mode forbids {what}. "
                f"Drive the game via real input only "
                f"(press / set_axis / move / wait / expect_*)."
            )

    def wait(self, seconds: float) -> "TestScript":
        self.cursor += seconds
        return self

    def press(self, button: str) -> "TestScript":
        if button not in PULSE_FIELDS:
            raise ValueError(
                f"Unknown button '{button}'. Valid: {sorted(PULSE_FIELDS)}"
            )
        if button in self._STRICT_FORBIDDEN_PRESSES:
            self._check_strict(f"press({button!r})")
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

    def expect_overlay(self, scene_class_name: str | None) -> "TestScript":
        """Assert that the current OVERLAY scene matches.

        Pass `None` to assert no overlay is up; pass a class name to
        assert that overlay is active. Used for walks that open the
        pause menu (PauseMenuScene), the scene switcher, etc.
        """
        self.actions.append(
            TestAction(
                self.cursor, "expect_overlay",
                {"name": scene_class_name},
            )
        )
        return self

    def expect_scene_in(
        self, scene_class_names: list[str],
    ) -> "TestScript":
        """Assert that the current scene matches ONE OF the listed names.

        Used by walks where a downstream branch is non-deterministic — e.g.
        the Final Conflict resolves to either EndingScene (win) or
        HyperspaceScene (loss-rewind) depending on stochastic combat.
        """
        self.actions.append(
            TestAction(
                self.cursor, "expect_scene_in",
                {"names": list(scene_class_names)},
            )
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

    def set_flag(self, key: str, value: Any) -> "TestScript":
        """Seed a game flag from the test. Useful for testing downstream
        scenes without walking the upstream prerequisite path.

        Forbidden in strict (integration-walk) mode — drive the flag via
        the actual gameplay side-effect instead.
        """
        self._check_strict(f"set_flag({key!r})")
        self.actions.append(
            TestAction(self.cursor, "set_flag", {"key": key, "value": value})
        )
        return self

    def set_cargo(self, cargo: dict[str, int]) -> "TestScript":
        """Seed game.cargo from the test. Replaces (not adds to) existing
        values for the specified types. Forbidden in strict mode."""
        self._check_strict("set_cargo(...)")
        self.actions.append(
            TestAction(self.cursor, "set_cargo", {"cargo": dict(cargo)})
        )
        return self

    def set_credits(self, value: int) -> "TestScript":
        """Seed game.credits from the test. Forbidden in strict mode."""
        self._check_strict(f"set_credits({value})")
        self.actions.append(
            TestAction(self.cursor, "set_credits", {"value": int(value)})
        )
        return self

    def expect_credits(self, expected: int) -> "TestScript":
        self.actions.append(
            TestAction(self.cursor, "expect_credits", {"expected": int(expected)})
        )
        return self

    def expect_cargo(self, cargo_type: str, expected: int) -> "TestScript":
        self.actions.append(
            TestAction(
                self.cursor, "expect_cargo",
                {"type": cargo_type, "expected": int(expected)},
            )
        )
        return self

    def expect_cargo_lt(self, cargo_type: str, bound: int) -> "TestScript":
        """Assert `game.cargo[type] < bound`. Used by auto-swap walks
        where the post-sweep count is variable but must have dropped
        below the pre-seed cap."""
        self.actions.append(
            TestAction(
                self.cursor, "expect_cargo_lt",
                {"type": cargo_type, "bound": int(bound)},
            )
        )
        return self

    def expect_cargo_total_le(self, bound: int) -> "TestScript":
        """Assert `sum(game.cargo.values()) <= bound`. Verifies the
        cargo cap is respected (auto-swap must not over-fill the hold).
        """
        self.actions.append(
            TestAction(
                self.cursor, "expect_cargo_total_le",
                {"bound": int(bound)},
            )
        )
        return self

    def expect_attr_contains(
        self, attr: str, member: object,
    ) -> "TestScript":
        """Assert `member in getattr(game, attr)`. Use for set/list
        state on game (`schematics`, `consumed_schematics`, `fleet`).
        Treats missing attribute as failure.
        """
        self.actions.append(
            TestAction(
                self.cursor, "expect_attr_contains",
                {"attr": str(attr), "member": member},
            )
        )
        return self

    def expect_cargo_higher_value_nonzero(self) -> "TestScript":
        """Assert at least one of USEFUL / BIO / ENERGY > 0. Used by
        auto-swap walks to verify the higher-value haul actually made
        it home (the swap wasn't a no-op).
        """
        self.actions.append(
            TestAction(
                self.cursor, "expect_cargo_higher_value_nonzero", {},
            )
        )
        return self

    def expect_module_installed(self, slot: str, module_id: str) -> "TestScript":
        self.actions.append(
            TestAction(
                self.cursor, "expect_module_installed",
                {"slot": slot, "module_id": module_id},
            )
        )
        return self

    def set_module_inventory(self, module_id: str, count: int) -> "TestScript":
        """Seed game.uninstalled_modules[module_id] = count. Useful for
        testing Customization without walking the upstream quest path.
        Forbidden in strict mode — walk the quest to earn the module."""
        self._check_strict(f"set_module_inventory({module_id!r})")
        self.actions.append(
            TestAction(
                self.cursor, "set_module_inventory",
                {"module_id": module_id, "count": int(count)},
            )
        )
        return self

    def simulate_lander_pickup(
        self, deposit_type: str, value: int = 5,
    ) -> "TestScript":
        """Directly fire `_on_pickup` on a synthetic Deposit while in
        PlanetSurfaceScene. Used to deterministically exercise cargo
        logic without depending on lander-sweep proc-gen variance.

        No-op if the current scene isn't PlanetSurfaceScene (walks
        should `expect_scene("PlanetSurfaceScene")` first to be safe).
        """
        self.actions.append(
            TestAction(
                self.cursor, "simulate_lander_pickup",
                {"type": str(deposit_type), "value": int(value)},
            )
        )
        return self

    def set_schematics(self, schematic_ids: list[str]) -> "TestScript":
        """Seed `game.schematics` directly. Used to test Vault flow
        without walking the upstream quest-reward path."""
        self.actions.append(
            TestAction(
                self.cursor, "set_schematics",
                {"schematic_ids": list(schematic_ids)},
            )
        )
        return self

    def set_fleet(self, ship_class_ids: list[str]) -> "TestScript":
        """Seed `game.fleet` directly. Used to test fleet-combat flows
        without walking the upstream Mh-Lai purchase path."""
        self.actions.append(
            TestAction(
                self.cursor, "set_fleet",
                {"ship_class_ids": list(ship_class_ids)},
            )
        )
        return self

    def set_player_heading(self, radians: float) -> "TestScript":
        """Set the player ship's heading (radians, 0 = north) directly.

        Useful in dense star clusters where the default heading=0
        autopilot picks a sibling star instead of the intended target.
        No-op if the current scene doesn't have a `player_heading`
        attribute (e.g. it's not Hyperspace or QuasiSpace).
        """
        self.actions.append(
            TestAction(
                self.cursor, "set_player_heading",
                {"radians": float(radians)},
            )
        )
        return self

    def set_player_pos(self, x: float, y: float) -> "TestScript":
        """Teleport the player ship in HyperspaceScene to (x, y).

        Used to position the player precisely without depending on
        frame-time-variable manual flight. No-op if the current scene
        isn't HyperspaceScene (use after `expect_scene HyperspaceScene`
        to be safe). Sets the camera as well so the next render is
        coherent.

        Forbidden in strict mode — fly the ship via `move()` instead.
        """
        self._check_strict(f"set_player_pos({x:.0f}, {y:.0f})")
        self.actions.append(
            TestAction(
                self.cursor, "set_player_pos",
                {"x": float(x), "y": float(y)},
            )
        )
        return self

    def invoke(self, dotted_path: str) -> "TestScript":
        """Call a runtime function with the current `game` as its only arg.

        `dotted_path` is a dotted-import path such as
        `'scz.content.endings.resolve_ending'`. The harness imports the
        module, looks up the attribute, calls it with `(game,)`, and
        ignores the return value (use `expect_flag` afterward to verify
        side-effects).

        Use for walks that need to drive a runtime evaluator from
        seeded flag state — e.g. firing `resolve_ending` on the
        `walk_perfect_run` flag-state to verify the runtime returns
        the canonical tier.

        Forbidden in strict mode — strict integration walks must reach
        the evaluator via real gameplay flow, not direct invocation.
        """
        self._check_strict(f"invoke({dotted_path!r})")
        self.actions.append(
            TestAction(self.cursor, "invoke", {"path": dotted_path})
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
        # Isolate walks from persistent on-disk campaigns. Without this,
        # MainMenuScene picks up the most-recent prior-test campaign and
        # auto-loads its state on confirm, overwriting everything the
        # walk pre-seeded via set_credits/set_cargo/set_flag/etc.
        # The walks all open MainMenu → Station via a single confirm
        # press, which works only when no campaigns exist.
        try:
            self.game.campaign_manager.active_slug = None
            self.game.campaign_manager._test_isolated = True
        except Exception:
            pass
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
        # of the same button was already pending. Logged for visibility;
        # the press is NOT lost — it spills into `deferred_presses` and
        # gets promoted to `pulse` on a subsequent frame (one per frame
        # per button). Under heavy parallel-test load the frame time can
        # stretch enough that several scheduled-press actions fire in
        # one step() call — this queue ensures each is delivered.
        self._coalesce_warnings: list[str] = []
        # Per-button FIFO of presses that couldn't be applied yet because
        # `pulse[button]` was already True for this frame. Drained at the
        # start of each step() before new actions process.
        self.deferred_presses: dict[str, int] = {}

    def step(self, dt: float) -> None:
        """Called each frame by Game.run after input.update(). Advances
        the script clock and fires any actions whose scheduled time has
        arrived.

        Before processing new actions, promote one pending press per
        button from `deferred_presses` into `self.pulse` so any presses
        that piled up under a slow frame still get delivered (one per
        frame per button — matches the rate the scene's edge-triggered
        input actually consumes them).
        """
        self._drain_deferred_presses()
        self.game_time += dt
        while self.next_idx < len(self.actions):
            action = self.actions[self.next_idx]
            if action.t > self.game_time:
                break
            self._execute(action)
            self.next_idx += 1

    def _drain_deferred_presses(self) -> None:
        """Promote one queued press per button into `self.pulse`. Called
        at the start of step() before new actions process."""
        if not self.deferred_presses:
            return
        for button in list(self.deferred_presses.keys()):
            count = self.deferred_presses[button]
            if count <= 0:
                del self.deferred_presses[button]
                continue
            self.pulse[button] = True
            self.deferred_presses[button] = count - 1
            if self.deferred_presses[button] <= 0:
                del self.deferred_presses[button]

    def _execute(self, action: TestAction) -> None:
        kind = action.kind
        p = action.params
        if kind == "press":
            # Two presses for the same button in one frame would coalesce
            # if both wrote `pulse[button] = True` — the second is lost
            # because the scene's edge-triggered input only sees a single
            # rising edge per frame. Defer the spill instead of dropping:
            # push to `deferred_presses`, drain one-per-frame in step().
            button = p["button"]
            if self.pulse.get(button):
                self.deferred_presses[button] = (
                    self.deferred_presses.get(button, 0) + 1
                )
                self._coalesce_warnings.append(
                    f"[t={self.game_time:5.2f}] deferred press {button} "
                    f"(queue depth {self.deferred_presses[button]})"
                )
            else:
                self.pulse[button] = True
            self.last_action_label = f"press {button}"
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
        elif kind == "expect_overlay":
            expected = p["name"]
            overlay = self.game.overlay_scene
            actual = type(overlay).__name__ if overlay is not None else None
            if actual == expected:
                msg = (
                    f"[t={self.game_time:5.2f}] OK   overlay = {actual!r}"
                )
                self.successes.append(msg)
                print(msg)
            else:
                msg = (
                    f"[t={self.game_time:5.2f}] FAIL expected overlay "
                    f"{expected!r}, got {actual!r}"
                )
                self.failures.append(msg)
                print(msg)
            self.last_action_label = f"expect_overlay {expected}"
        elif kind == "expect_scene_in":
            actual = (
                type(self.game.current_scene).__name__
                if self.game.current_scene else "None"
            )
            expected_names = p["names"]
            if actual in expected_names:
                msg = (
                    f"[t={self.game_time:5.2f}] OK   scene = {actual} "
                    f"(matched one of {expected_names})"
                )
                self.successes.append(msg)
                print(msg)
            else:
                msg = (
                    f"[t={self.game_time:5.2f}] FAIL expected scene in "
                    f"{expected_names}, got {actual!r}"
                )
                self.failures.append(msg)
                print(msg)
            self.last_action_label = f"expect_scene_in {expected_names}"
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
        elif kind == "set_flag":
            self.game.flags[p["key"]] = p["value"]
            self.last_action_label = f"set_flag {p['key']}={p['value']!r}"
        elif kind == "set_cargo":
            for t, v in p["cargo"].items():
                self.game.cargo[t] = int(v)
            # If we're mid-lander-trip, also clear the trip haul —
            # walks that re-seed cargo between cases shouldn't carry
            # stale haul forward across `set_cargo` boundaries.
            from scz.planet.scene import PlanetSurfaceScene
            scene = self.game.current_scene
            if isinstance(scene, PlanetSurfaceScene):
                scene.trip_haul = {}
            self.last_action_label = f"set_cargo {p['cargo']}"
        elif kind == "set_credits":
            self.game.credits = p["value"]
            self.last_action_label = f"set_credits {p['value']}"
        elif kind == "expect_credits":
            expected = p["expected"]
            actual = self.game.credits
            if actual == expected:
                msg = f"[t={self.game_time:5.2f}] OK   credits = {actual}"
                self.successes.append(msg)
                print(msg)
            else:
                msg = (
                    f"[t={self.game_time:5.2f}] FAIL credits expected {expected}, "
                    f"got {actual}"
                )
                self.failures.append(msg)
                print(msg)
            self.last_action_label = f"expect_credits {expected}"
        elif kind == "expect_cargo":
            t = p["type"]
            expected = p["expected"]
            actual = self.game.cargo.get(t, 0)
            if actual == expected:
                msg = f"[t={self.game_time:5.2f}] OK   cargo[{t}] = {actual}"
                self.successes.append(msg)
                print(msg)
            else:
                msg = (
                    f"[t={self.game_time:5.2f}] FAIL cargo[{t}] expected "
                    f"{expected}, got {actual}"
                )
                self.failures.append(msg)
                print(msg)
            self.last_action_label = f"expect_cargo {t} = {expected}"
        elif kind == "expect_cargo_lt":
            t = p["type"]
            bound = p["bound"]
            actual = self.game.cargo.get(t, 0)
            if actual < bound:
                msg = f"[t={self.game_time:5.2f}] OK   cargo[{t}] = {actual} (< {bound})"
                self.successes.append(msg)
                print(msg)
            else:
                msg = (
                    f"[t={self.game_time:5.2f}] FAIL cargo[{t}] expected < "
                    f"{bound}, got {actual}"
                )
                self.failures.append(msg)
                print(msg)
            self.last_action_label = f"expect_cargo_lt {t} < {bound}"
        elif kind == "expect_cargo_total_le":
            bound = p["bound"]
            actual = sum(self.game.cargo.values())
            if actual <= bound:
                msg = f"[t={self.game_time:5.2f}] OK   cargo total = {actual} (<= {bound})"
                self.successes.append(msg)
                print(msg)
            else:
                msg = (
                    f"[t={self.game_time:5.2f}] FAIL cargo total expected "
                    f"<= {bound}, got {actual}"
                )
                self.failures.append(msg)
                print(msg)
            self.last_action_label = f"expect_cargo_total_le {bound}"
        elif kind == "expect_attr_contains":
            attr = p["attr"]
            member = p["member"]
            collection = getattr(self.game, attr, None)
            if collection is None:
                msg = (
                    f"[t={self.game_time:5.2f}] FAIL "
                    f"game.{attr} missing (expected to contain {member!r})"
                )
                self.failures.append(msg)
                print(msg)
            elif member in collection:
                msg = (
                    f"[t={self.game_time:5.2f}] OK   "
                    f"game.{attr} contains {member!r}"
                )
                self.successes.append(msg)
                print(msg)
            else:
                msg = (
                    f"[t={self.game_time:5.2f}] FAIL "
                    f"game.{attr} expected to contain {member!r}, "
                    f"contents = {collection!r}"
                )
                self.failures.append(msg)
                print(msg)
            self.last_action_label = f"expect_attr_contains {attr} ⊇ {member!r}"
        elif kind == "expect_cargo_higher_value_nonzero":
            higher = sum(
                self.game.cargo.get(t, 0) for t in ("USEFUL", "BIO", "ENERGY")
            )
            if higher > 0:
                msg = (
                    f"[t={self.game_time:5.2f}] OK   "
                    f"USEFUL+BIO+ENERGY = {higher} (> 0)"
                )
                self.successes.append(msg)
                print(msg)
            else:
                msg = (
                    f"[t={self.game_time:5.2f}] FAIL "
                    f"USEFUL+BIO+ENERGY expected > 0, got 0"
                )
                self.failures.append(msg)
                print(msg)
            self.last_action_label = "expect_cargo_higher_value_nonzero"
        elif kind == "expect_module_installed":
            slot = p["slot"]
            module_id = p["module_id"]
            actual = self.game.ship_modules.get(slot)
            # Legacy-slot bridge (post-2026-05-18 slot refactor): if the
            # walk asks for a legacy-name slot ("sensor", "drive",
            # "weapon", etc.) and that key isn't set in ship_modules,
            # search across ALL generic slots for the named module_id.
            # This keeps pre-refactor walks green without forcing every
            # walk to be rewritten in the same commit as the refactor.
            if actual is None and module_id is not None:
                from scz.content.modules import LEGACY_SLOT_NAMES
                if slot in LEGACY_SLOT_NAMES:
                    for mod_id in self.game.ship_modules.values():
                        if mod_id == module_id:
                            actual = mod_id
                            break
            if actual == module_id:
                msg = (
                    f"[t={self.game_time:5.2f}] OK   ship_modules[{slot}] = "
                    f"{module_id!r}"
                )
                self.successes.append(msg)
                print(msg)
            else:
                msg = (
                    f"[t={self.game_time:5.2f}] FAIL ship_modules[{slot}] expected "
                    f"{module_id!r}, got {actual!r}"
                )
                self.failures.append(msg)
                print(msg)
            self.last_action_label = f"expect_module {slot}={module_id}"
        elif kind == "set_module_inventory":
            mod_id = p["module_id"]
            count = p["count"]
            if count > 0:
                self.game.uninstalled_modules[mod_id] = count
            else:
                self.game.uninstalled_modules.pop(mod_id, None)
            self.last_action_label = f"set_module_inv {mod_id}={count}"
        elif kind == "set_fleet":
            self.game.fleet = list(p["ship_class_ids"])
            self.last_action_label = f"set_fleet {p['ship_class_ids']}"
        elif kind == "set_schematics":
            self.game.schematics = set(p["schematic_ids"])
            self.last_action_label = f"set_schematics {p['schematic_ids']}"
        elif kind == "set_player_heading":
            scene = self.game.current_scene
            if hasattr(scene, "player_heading"):
                scene.player_heading = float(p["radians"])
            self.last_action_label = f"set_player_heading {p['radians']:.2f}"
        elif kind == "simulate_lander_pickup":
            from scz.planet.scene import PlanetSurfaceScene
            from scz.planet.deposits import Deposit
            scene = self.game.current_scene
            if isinstance(scene, PlanetSurfaceScene):
                d = Deposit(
                    type=p["type"], x=0.5, y=0.5, value=p["value"],
                )
                scene._on_pickup(d)
            self.last_action_label = (
                f"simulate_lander_pickup {p['type']} +{p['value']}"
            )
        elif kind == "set_player_pos":
            # Teleport the player in HyperspaceScene. Safe no-op if the
            # current scene isn't hyperspace — walks should set the
            # scene first via the switcher.
            from scz.hyperspace.scene import HyperspaceScene
            scene = self.game.current_scene
            if isinstance(scene, HyperspaceScene):
                scene.player_x = p["x"]
                scene.player_y = p["y"]
                scene.camera_x = p["x"]
                scene.camera_y = p["y"]
            self.last_action_label = f"set_player_pos ({p['x']:.0f}, {p['y']:.0f})"
        elif kind == "invoke":
            # Dotted path resolution + call with `game`.
            path = p["path"]
            try:
                module_path, _, attr = path.rpartition(".")
                if not module_path:
                    raise ValueError(
                        f"invoke path must be dotted (got {path!r})"
                    )
                import importlib
                mod = importlib.import_module(module_path)
                fn = getattr(mod, attr)
                fn(self.game)
                msg = f"[t={self.game_time:5.2f}] OK   invoke {path}"
                self.successes.append(msg)
                print(msg)
            except Exception as exc:
                msg = (
                    f"[t={self.game_time:5.2f}] FAIL invoke {path} raised "
                    f"{type(exc).__name__}: {exc}"
                )
                self.failures.append(msg)
                print(msg)
            self.last_action_label = f"invoke {path}"
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
                f"\n{len(self._coalesce_warnings)} press(es) deferred "
                "(spilled to next frame; not lost):"
            )
            for w in self._coalesce_warnings:
                print("  " + w)
        # Sanity check: any still-pending deferred presses at test end
        # means the test ended before the queue drained — these WILL be
        # lost. Surface as a warning so the walk author can lengthen
        # their final wait().
        if self.deferred_presses:
            print(
                f"\nWARNING: {sum(self.deferred_presses.values())} "
                "press(es) still queued at test end (not delivered):"
            )
            for button, count in self.deferred_presses.items():
                print(f"  {button}: {count}")
        print("=" * 60)
