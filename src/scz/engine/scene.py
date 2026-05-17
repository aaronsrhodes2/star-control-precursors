"""Scene base class. Each scene = one screen / mode of the game.

Hyperspace, star system view, planet surface, melee combat, dialog encounter,
Council scene — each is a Scene subclass. The Game holds one current scene
and forwards update/render to it. Scenes can push new scenes (modal) or
replace themselves.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import pygame

if TYPE_CHECKING:
    from scz.engine.game import Game
    from scz.engine.input import InputManager


class Scene:
    """Base class for game scenes."""

    # Audio: the music context this scene wants playing while active.
    # The Game's set_scene() reads this attribute and cross-fades the
    # MusicDirector into the named context. Map to an
    # assets/music/<name>/ directory. None = leave music alone (carry
    # over from prior scene; appropriate for modal overlays that
    # shouldn't interrupt the underlying music).
    # Override in subclasses by setting the class attribute, e.g.:
    #   class HyperspaceScene(Scene):
    #       music_context = "hyperspace"
    music_context: str | None = None

    def __init__(self) -> None:
        self.game: "Game | None" = None

    def on_enter(self) -> None:
        """Called once when the scene becomes active. Override for setup
        that requires the Game (e.g. screen size)."""

    def on_exit(self) -> None:
        """Called once when the scene is being replaced or popped."""

    def update(self, dt: float, inp: "InputManager") -> None:
        """Per-frame update. dt = seconds since last frame."""

    def render(self, screen: pygame.Surface) -> None:
        """Per-frame render to the screen surface."""

    # ----- Time Drive API -----
    # Scenes opt in to rewind by overriding snapshot() and restore().
    # Returning None from snapshot() makes this scene non-rewindable
    # (the Time Drive will skip taking snapshots in this scene).

    def snapshot(self) -> dict | None:
        """Return a JSON-serializable dict of rewindable state, or None
        to mark this scene non-rewindable (e.g. mid-combat lock-in)."""
        return None

    def restore(self, state: dict) -> None:
        """Restore from a state dict produced by snapshot()."""
