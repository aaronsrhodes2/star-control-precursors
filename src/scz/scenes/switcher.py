"""Scene Switcher — F1 debug overlay for jumping to any scene.

Opens as a modal over the current scene. Arrow keys / D-pad navigate the
list; Enter / A launches; Esc / B dismisses (restoring the underlying scene
unchanged).

This is a *debug* tool for testing scaffolded views. The real game will
flow through MainMenu → Hyperspace → etc. without exposing the switcher
to players.
"""

from __future__ import annotations

import pygame

from scz.engine.scene import Scene


# Entry: (label, factory function that returns a new scene instance, key shortcut)
def _entries():
    """Build the list at import time. Each factory returns a fresh scene."""
    from scz.hyperspace.scene import HyperspaceScene
    from scz.system.scene import SystemScene
    from scz.planet.scene import PlanetSurfaceScene
    from scz.scenes.stubs import (
        MainMenuScene,
        PlanetScanScene,
        DialogScene,
        ObservationScene,
        MeleeCombatScene,
        CouncilScene,
        StationScene,
        ShipCustomizationScene,
        ClusterStatusBoardScene,
        ArchiveScene,
        QuasiSpaceScene,
    )

    # Returning Hyperspace/System/Planet to fresh instances loses state,
    # which is expected for the debug switcher — we're jumping for testing.
    def _fresh_planet():
        # Need a star + planet to seed; pick Sol's first non-gas planet
        from scz.hyperspace.scene import STARMAP_JSON
        from scz.hyperspace.starmap import Starmap
        from scz.system.scene import SystemScene as _Sys
        sm = Starmap(STARMAP_JSON)
        star = next(s for s in sm.stars if s.get("defined_name") == "SOL_PROTO")
        sys = _Sys(star)
        planet = next(p for p in sys.planets if p.type != "GAS_GIANT")
        return PlanetSurfaceScene(planet=planet, star=star, parent_scene_cls=_Sys)

    def _fresh_system():
        from scz.hyperspace.scene import STARMAP_JSON
        from scz.hyperspace.starmap import Starmap
        sm = Starmap(STARMAP_JSON)
        star = next(s for s in sm.stars if s.get("defined_name") == "SOL_PROTO")
        return SystemScene(star)

    return [
        # Live scenes
        ("Main Menu",              lambda: MainMenuScene(),         pygame.K_0),
        ("Hyperspace (galaxy)",    lambda: HyperspaceScene(),       pygame.K_1),
        ("Star System (Sol)",      _fresh_system,                   pygame.K_2),
        ("Planet Surface (Sol I)", _fresh_planet,                   pygame.K_3),
        # Stubs
        ("Planet Scan",            lambda: PlanetScanScene(),       pygame.K_4),
        ("Dialog",                 lambda: DialogScene(),           pygame.K_5),
        ("Observation Encounter",  lambda: ObservationScene(),      pygame.K_6),
        ("Melee Combat",           lambda: MeleeCombatScene(),      pygame.K_7),
        ("Furling Council",        lambda: CouncilScene(),          pygame.K_8),
        ("Station / Home Port",    lambda: StationScene(),          pygame.K_9),
        ("Ship Customization",     lambda: ShipCustomizationScene(), None),
        ("Cluster Status Board",   lambda: ClusterStatusBoardScene(), None),
        ("Bio-Archive",            lambda: ArchiveScene(),          None),
        ("Quasi-Space",            lambda: QuasiSpaceScene(),       None),
    ]


class SceneSwitcher(Scene):
    """Modal overlay listing all scenes; pick one to launch."""

    def __init__(self) -> None:
        super().__init__()
        self.entries = _entries()
        self.selected = 0
        # Repeat-rate state so holding the stick scrolls, not flicks
        self._axis_cooldown = 0.0
        self.font: pygame.font.Font | None = None
        self.title_font: pygame.font.Font | None = None

    def on_enter(self) -> None:
        self.font = pygame.font.SysFont("consolas", 22)
        self.title_font = pygame.font.SysFont("consolas", 36, bold=True)

    def update(self, dt: float, inp) -> None:  # type: ignore[no-untyped-def]
        # Esc / B / F1 → dismiss (overlay closes, underlying scene resumes)
        if inp.cancel or inp.open_switcher:
            if self.game is not None:
                self.game.close_overlay()
            return

        # Move selection
        # Discrete key/button events (already edge-triggered) handled below;
        # for the analog stick, use a cooldown so holding doesn't flood.
        moved = False
        if self._axis_cooldown > 0:
            self._axis_cooldown -= dt
        else:
            if inp.move_y < -0.3:
                self.selected = (self.selected - 1) % len(self.entries)
                self._axis_cooldown = 0.18
                moved = True
            elif inp.move_y > 0.3:
                self.selected = (self.selected + 1) % len(self.entries)
                self._axis_cooldown = 0.18
                moved = True

        # Confirm → launch
        if inp.confirm:
            label, factory, _ = self.entries[self.selected]
            if self.game is not None:
                self.game.set_scene(factory())
            return

        # Number-key shortcuts (1-9, 0)
        # Read raw pygame state for digits since we don't surface them in
        # InputManager.
        keys = pygame.key.get_pressed()
        for idx, (label, factory, key) in enumerate(self.entries):
            if key is not None and keys[key]:
                self.selected = idx
                if self.game is not None:
                    self.game.set_scene(factory())
                return

    def render(self, screen: pygame.Surface) -> None:
        # Translucent backdrop over the underlying scene
        overlay = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
        overlay.fill((6, 6, 18, 220))
        screen.blit(overlay, (0, 0))

        if self.title_font is None or self.font is None:
            return

        w, h = screen.get_size()
        # Title
        title = self.title_font.render("SCENE SWITCHER (F1)", True, (220, 230, 250))
        tw, th = title.get_size()
        screen.blit(title, ((w - tw) // 2, 80))

        sub = self.font.render(
            "↑↓ / left-stick · Enter / A to launch · Esc / B to dismiss",
            True,
            (160, 180, 210),
        )
        sw, _ = sub.get_size()
        screen.blit(sub, ((w - sw) // 2, 130))

        # List entries
        y_start = 200
        row_h = 36
        for idx, (label, _, key) in enumerate(self.entries):
            is_selected = idx == self.selected
            color = (255, 240, 180) if is_selected else (180, 190, 210)
            prefix = "►" if is_selected else " "
            key_label = ""
            if key is not None:
                if key == pygame.K_0:
                    key_label = " [0]"
                elif pygame.K_1 <= key <= pygame.K_9:
                    key_label = f" [{key - pygame.K_0}]"
            line = self.font.render(
                f" {prefix}  {label}{key_label}", True, color
            )
            x = (w - 480) // 2
            screen.blit(line, (x, y_start + idx * row_h))

        # Footer
        footer = self.font.render(
            "Stubs show their planned design; live scenes (Hyperspace / System / Planet) work fully.",
            True,
            (120, 140, 170),
        )
        fw, _ = footer.get_size()
        screen.blit(footer, ((w - fw) // 2, h - 80))
