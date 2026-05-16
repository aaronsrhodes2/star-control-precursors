"""Main Game class: window, loop, scene management."""

from __future__ import annotations

import pygame

from scz.engine.input import InputManager
from scz.engine.scene import Scene
from scz.engine.time_drive import TimeDrive


class Game:
    """Owns the pygame window and the main loop.

    Holds one current scene (no stack yet; we'll add modal push later).
    Caps the loop at target_fps and feeds dt to the scene.

    Renders at the logical (width, height). With fullscreen=True we use
    pygame.SCALED so the logical resolution is preserved regardless of the
    monitor's actual size — much friendlier than asking the OS to change
    display mode.
    """

    def __init__(
        self,
        width: int = 1920,
        height: int = 1080,
        title: str = "Star Control Zero: The Precursors",
        target_fps: int = 60,
        fullscreen: bool = True,
    ) -> None:
        pygame.init()
        pygame.joystick.init()
        flags = 0
        if fullscreen:
            flags = pygame.FULLSCREEN | pygame.SCALED
        self.screen = pygame.display.set_mode((width, height), flags)
        pygame.display.set_caption(title)
        pygame.mouse.set_visible(not fullscreen)
        self.clock = pygame.time.Clock()
        self.running = True
        self.input = InputManager()
        self.current_scene: Scene | None = None
        # An overlay scene is rendered on top of and intercepts input from
        # the main scene without unloading it. Used for the F1 scene-
        # switcher (and future modal dialogs).
        self.overlay_scene: Scene | None = None
        self.target_fps = target_fps
        self.frame_count = 0
        self.time_drive = TimeDrive()

        # Test mode — when running under a script, the harness overlays
        # scripted input each frame and the speed multiplier lets the
        # whole game run faster while still rendering at the normal
        # framerate so Aaron can watch the playback in real time.
        from scz.testing.harness import TestHarness   # local to avoid cycles
        self.test_harness: TestHarness | None = None
        self.test_speed: float = 1.0

    def set_scene(self, scene: Scene) -> None:
        """Replace the current scene with a new one."""
        # Setting a new main scene closes any active overlay.
        self.close_overlay()
        if self.current_scene is not None:
            self.current_scene.on_exit()
        scene.game = self
        self.current_scene = scene
        scene.on_enter()

    def open_overlay(self, scene: Scene) -> None:
        """Open a modal overlay on top of the current scene.

        The main scene is paused (not updated, but still rendered as
        backdrop). Input goes to the overlay only. The overlay can
        call close_overlay() to dismiss itself, or set_scene() to
        replace the main scene entirely (which also closes the overlay).
        """
        if self.overlay_scene is not None:
            self.overlay_scene.on_exit()
        scene.game = self
        self.overlay_scene = scene
        scene.on_enter()

    def close_overlay(self) -> None:
        if self.overlay_scene is not None:
            self.overlay_scene.on_exit()
            self.overlay_scene = None

    def _render_test_hud(self) -> None:
        """Render a 'TEST MODE' badge + current scripted action + pass/fail
        counts in the top-right corner. Only called when a TestHarness is
        attached."""
        if self.test_harness is None:
            return
        font = pygame.font.SysFont("consolas", 16, bold=True)
        body_font = pygame.font.SysFont("consolas", 14)
        w = self.screen.get_size()[0]
        x = w - 360
        y = 10
        # Badge
        badge_color = (220, 80, 80) if self.test_harness.failures else (130, 220, 160)
        pygame.draw.rect(self.screen, (10, 10, 20), (x - 8, y - 4, 350, 80))
        pygame.draw.rect(self.screen, badge_color, (x - 8, y - 4, 350, 80), 1)
        label = font.render(
            f"TEST MODE  ·  speed {self.test_speed:g}x", True, badge_color
        )
        self.screen.blit(label, (x, y))
        action_label = body_font.render(
            f"→ {self.test_harness.last_action_label}", True, (220, 220, 240)
        )
        self.screen.blit(action_label, (x, y + 22))
        counts = body_font.render(
            f"pass {len(self.test_harness.successes)}  ·  fail {len(self.test_harness.failures)}",
            True,
            (180, 200, 220),
        )
        self.screen.blit(counts, (x, y + 44))
        t_label = body_font.render(
            f"t = {self.test_harness.game_time:6.2f} game-s", True, (140, 160, 200)
        )
        self.screen.blit(t_label, (x, y + 60))

    def quit(self) -> None:
        """Request the loop to exit at end of current frame."""
        self.running = False

    def run(self) -> None:
        """Main loop. Returns when the loop exits."""
        try:
            while self.running:
                real_dt = self.clock.tick(self.target_fps) / 1000.0
                # Apply the test-mode speed multiplier. real_dt is wall time;
                # dt is game time. The harness uses dt for its scheduling so
                # scripts are speed-independent.
                dt = real_dt * self.test_speed
                events = pygame.event.get()
                for ev in events:
                    if ev.type == pygame.QUIT:
                        self.running = False

                self.input.update(events)

                # Apply any scripted input from the test harness — overlay
                # on top of real input so a human can still take over.
                if self.test_harness is not None:
                    self.test_harness.step(dt)
                    self.test_harness.apply_to_input(self.input)
                    if self.test_harness.done:
                        self.running = False

                if self.input.quit:
                    self.running = False

                if self.current_scene is not None:
                    # F1 anywhere → open the scene switcher overlay.
                    # Must be checked BEFORE updating scenes, and only when
                    # no overlay is already up (so switcher's own F1 doesn't
                    # toggle).
                    if self.input.open_switcher and self.overlay_scene is None:
                        from scz.scenes.switcher import SceneSwitcher
                        self.open_overlay(SceneSwitcher())

                    # Time Drive sampling + rewind handling (engine layer).
                    # Only the main scene contributes to the rewind buffer.
                    self.time_drive.maybe_snapshot(self.current_scene)
                    self.time_drive.update(dt)
                    if self.input.rewind and self.time_drive.is_ready():
                        self.time_drive.rewind(self.current_scene)

                    # Main scene always renders (as backdrop when overlay is up).
                    self.current_scene.render(self.screen)

                    # Update the active scene. Overlay intercepts input if up.
                    # Cache the overlay reference before calling update — the
                    # update may close the overlay (e.g. SceneSwitcher picking
                    # a target calls set_scene, which closes the overlay). If
                    # that happens we skip the post-update render of the now-
                    # dismissed overlay.
                    overlay_at_update = self.overlay_scene
                    if overlay_at_update is not None:
                        overlay_at_update.update(dt, self.input)
                        if self.overlay_scene is overlay_at_update:
                            overlay_at_update.render(self.screen)
                    else:
                        self.current_scene.update(dt, self.input)

                    self.time_drive.render_overlay(self.screen)

                # Test-mode HUD overlay on top of everything
                if self.test_harness is not None:
                    self._render_test_hud()

                pygame.display.flip()
                self.frame_count += 1
        finally:
            if self.current_scene is not None:
                self.current_scene.on_exit()
            pygame.quit()
