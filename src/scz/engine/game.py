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

    def quit(self) -> None:
        """Request the loop to exit at end of current frame."""
        self.running = False

    def run(self) -> None:
        """Main loop. Returns when the loop exits."""
        try:
            while self.running:
                dt = self.clock.tick(self.target_fps) / 1000.0
                events = pygame.event.get()
                for ev in events:
                    if ev.type == pygame.QUIT:
                        self.running = False

                self.input.update(events)
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
                    if self.overlay_scene is not None:
                        self.overlay_scene.update(dt, self.input)
                        self.overlay_scene.render(self.screen)
                    else:
                        self.current_scene.update(dt, self.input)

                    self.time_drive.render_overlay(self.screen)

                pygame.display.flip()
                self.frame_count += 1
        finally:
            if self.current_scene is not None:
                self.current_scene.on_exit()
            pygame.quit()
