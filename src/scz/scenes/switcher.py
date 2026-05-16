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
    from scz.system.orbit import PlanetOrbitScene
    from scz.planet.scene import PlanetSurfaceScene
    from scz.scenes.stubs import (
        MainMenuScene,
        ObservationScene,
        CouncilScene,
        ClusterStatusBoardScene,
        ArchiveScene,
    )
    # Real implementations (replacing stubs)
    from scz.dialog.characters import arilou_sage, coel_tessar, commander_halia, sentry_drone_47t
    from scz.dialog.scene import DialogScene
    from scz.station.scene import StationScene
    from scz.content.home_system import home_star
    from scz.content.arilou_outpost import arilou_outpost_star
    from scz.quasispace.scene import QuasiSpaceScene
    from scz.combat.super_melee import SuperMeleeScene
    from scz.station.trade import TradeScene
    from scz.station.customization import ShipCustomizationScene

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

    def _fresh_orbit():
        from scz.hyperspace.scene import STARMAP_JSON
        from scz.hyperspace.starmap import Starmap
        from scz.system.scene import SystemScene as _Sys
        sm = Starmap(STARMAP_JSON)
        star = next(s for s in sm.stars if s.get("defined_name") == "SOL_PROTO")
        sys = _Sys(star)
        planet = next(p for p in sys.planets if p.type != "GAS_GIANT")
        return PlanetOrbitScene(planet=planet, star=star, parent_scene_cls=_Sys)

    def _fresh_system():
        from scz.hyperspace.scene import STARMAP_JSON
        from scz.hyperspace.starmap import Starmap
        sm = Starmap(STARMAP_JSON)
        star = next(s for s in sm.stars if s.get("defined_name") == "SOL_PROTO")
        return SystemScene(star)

    def _home_system():
        return SystemScene(home_star())

    def _arilou_system():
        return SystemScene(arilou_outpost_star())

    def _arilou_sanctuary_orbit():
        from scz.system.scene import SystemScene as _Sys
        sys = _Sys(arilou_outpost_star())
        planet = next(p for p in sys.planets if p.name == "Arilou Sanctuary")
        return PlanetOrbitScene(planet=planet, star=arilou_outpost_star(), parent_scene_cls=_Sys)

    def _mh_lai_orbit():
        from scz.system.scene import SystemScene as _Sys
        sys = _Sys(home_star())
        planet = next(p for p in sys.planets if p.name == "Mh-Lai")
        return PlanetOrbitScene(planet=planet, star=home_star(), parent_scene_cls=_Sys)

    def _furlmart_orbit():
        from scz.system.scene import SystemScene as _Sys
        sys = _Sys(home_star())
        planet = next(p for p in sys.planets if p.name == "Furlmart")
        return PlanetOrbitScene(planet=planet, star=home_star(), parent_scene_cls=_Sys)

    return [
        # Live scenes
        ("Main Menu",                lambda: MainMenuScene(),                pygame.K_0),
        ("Hyperspace (galaxy)",      lambda: HyperspaceScene(),              pygame.K_1),
        ("Mh-Lai System (home)",     _home_system,                           pygame.K_2),
        ("Mh-Lai Orbit",             _mh_lai_orbit,                          pygame.K_3),
        ("Furlmart Orbit",           _furlmart_orbit,                        pygame.K_4),
        ("Arilou Outpost System",    _arilou_system,                         pygame.K_5),
        ("Arilou Sanctuary Orbit",   _arilou_sanctuary_orbit,                pygame.K_6),
        ("Star System (Sol)",        _fresh_system,                          pygame.K_7),
        ("Planet Orbit (Sol I)",     _fresh_orbit,                           pygame.K_8),
        ("Planet Surface (Sol I)",   _fresh_planet,                          pygame.K_9),
        ("Station — Mh-Lai",         lambda: StationScene(),                 None),
        ("Dialog — Cmdr Halia",      lambda: DialogScene(commander_halia()), None),
        ("Dialog — Arilou Sage",     lambda: DialogScene(arilou_sage()),     None),
        ("Dialog — Coel Tessar",     lambda: DialogScene(coel_tessar()),     None),
        ("Dialog — Sentry Drone",    lambda: DialogScene(sentry_drone_47t()), None),
        ("Quasi-Space",              lambda: QuasiSpaceScene(),              None),
        ("Super Melee",              lambda: SuperMeleeScene(),              None),
        ("Trade",                    lambda: TradeScene(),                   None),
        ("Ship Customization",       lambda: ShipCustomizationScene(),       None),
        # Stubs
        ("Observation Encounter",    lambda: ObservationScene(),             None),
        ("Furling Council",          lambda: CouncilScene(),                 None),
        ("Cluster Status Board",     lambda: ClusterStatusBoardScene(),      None),
        ("Bio-Archive",              lambda: ArchiveScene(),                 None),
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
        # Esc / B → dismiss (overlay closes, underlying scene resumes).
        # NOTE: F1 (open_switcher) is NOT a dismiss trigger — the game loop
        # only opens the switcher when no overlay exists, but the same frame
        # that opens us still has open_switcher=True. Listening for it here
        # would dismiss us in the same frame we opened.
        if inp.cancel:
            if self.game is not None:
                self.game.close_overlay()
            return

        # Discrete D-pad / arrow keys (edge-triggered by InputManager)
        if inp.menu_up:
            self.selected = (self.selected - 1) % len(self.entries)
        elif inp.menu_down:
            self.selected = (self.selected + 1) % len(self.entries)

        # Analog stick (continuous, with cooldown so holding doesn't flood)
        if self._axis_cooldown > 0:
            self._axis_cooldown -= dt
        else:
            if inp.move_y < -0.3:
                self.selected = (self.selected - 1) % len(self.entries)
                self._axis_cooldown = 0.18
            elif inp.move_y > 0.3:
                self.selected = (self.selected + 1) % len(self.entries)
                self._axis_cooldown = 0.18

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
            "Up/Down (D-pad, arrows, L-stick)  -  A / Space launch  -  B / Esc dismiss",
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
