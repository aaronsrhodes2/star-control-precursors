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
