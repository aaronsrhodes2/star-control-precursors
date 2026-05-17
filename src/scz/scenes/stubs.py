"""Stub scenes — one per planned game view.

Each scaffold scene shows a clear title, a description of what the scene WILL
do, and standard back-out control. Real content will replace each stub when
the corresponding feature lands; until then, they're useful for navigating
the eventual game structure and validating the look/feel of each context.

Common controls (handled by StubScene base):
    Esc / B / Backspace  →  back to parent scene (or quit if no parent)
    F1                   →  open scene switcher
"""

from __future__ import annotations

import os

import pygame

from scz.engine.scene import Scene


# Common HUD colors for the stub UI
COL_BG = (6, 6, 18)
COL_PANEL = (10, 10, 26)
COL_BORDER = (40, 40, 70)
COL_TITLE = (220, 230, 250)
COL_SUBTITLE = (150, 180, 220)
COL_DETAIL = (160, 170, 190)
COL_BULLET = (120, 200, 180)
COL_STUB_TAG = (255, 180, 120)
COL_CONTROLS = (120, 140, 170)


class StubScene(Scene):
    """Base class for all stub scenes.

    Subclasses set TITLE, SUBTITLE, DETAILS, and ACCENT — the rest is
    handled here. Override update() or render() if a stub needs custom
    behavior beyond title-card display.
    """

    TITLE: str = "Stub Scene"
    SUBTITLE: str = "Description"
    DETAILS: list[str] = []
    ACCENT: tuple[int, int, int] = (140, 180, 255)  # title color override
    # Optional backdrop image path (relative to project root). When set,
    # the image is loaded once in on_enter, scaled to fill the window,
    # and blitted darkened so the title/details text remains legible.
    BACKDROP_PATH: str | None = None
    BACKDROP_DIM: int = 170  # 0-255 alpha of the dark overlay over the image

    def __init__(self, parent_scene_cls: type | None = None) -> None:
        super().__init__()
        self.parent_scene_cls = parent_scene_cls
        self.font: pygame.font.Font | None = None
        self.title_font: pygame.font.Font | None = None
        self.subtitle_font: pygame.font.Font | None = None
        self.tag_font: pygame.font.Font | None = None
        self._backdrop_surface: pygame.Surface | None = None
        self._backdrop_size: tuple[int, int] | None = None

    def on_enter(self) -> None:
        self.font = pygame.font.SysFont("consolas", 20)
        self.title_font = pygame.font.SysFont("consolas", 64, bold=True)
        self.subtitle_font = pygame.font.SysFont("consolas", 26)
        self.tag_font = pygame.font.SysFont("consolas", 18, bold=True)

    def update(self, dt: float, inp) -> None:  # type: ignore[no-untyped-def]
        # Back out on cancel
        if inp.cancel and self.game is not None:
            self._back()

    def _back(self) -> None:
        """Return to parent scene, or quit if no parent."""
        assert self.game is not None
        if self.parent_scene_cls is not None:
            self.game.set_scene(self.parent_scene_cls())
        else:
            self.game.quit()

    def _ensure_backdrop(self, size: tuple[int, int]) -> None:
        """Lazy-load and scale the backdrop image to the current screen."""
        if self.BACKDROP_PATH is None:
            return
        if self._backdrop_surface is not None and self._backdrop_size == size:
            return
        if not os.path.isfile(self.BACKDROP_PATH):
            self._backdrop_surface = None
            return
        try:
            img = pygame.image.load(self.BACKDROP_PATH).convert_alpha()
        except (pygame.error, OSError):
            self._backdrop_surface = None
            return
        scaled = pygame.transform.smoothscale(img, size)
        dim = pygame.Surface(size, pygame.SRCALPHA)
        dim.fill((0, 0, 0, self.BACKDROP_DIM))
        scaled.blit(dim, (0, 0))
        self._backdrop_surface = scaled
        self._backdrop_size = size

    def render(self, screen: pygame.Surface) -> None:
        screen.fill(COL_BG)
        w, h = screen.get_size()

        self._ensure_backdrop((w, h))
        if self._backdrop_surface is not None:
            screen.blit(self._backdrop_surface, (0, 0))

        # STUB tag in top-right
        if self.tag_font is not None:
            tag = self.tag_font.render("STUB — content coming soon", True, COL_STUB_TAG)
            tw, _ = tag.get_size()
            screen.blit(tag, (w - tw - 20, 20))

        # F1 hint top-left
        if self.tag_font is not None:
            f1 = self.tag_font.render("F1: scene switcher", True, COL_DETAIL)
            screen.blit(f1, (20, 20))

        # Title — centered, large
        if self.title_font is not None:
            title = self.title_font.render(self.TITLE, True, self.ACCENT)
            tw, th = title.get_size()
            screen.blit(title, ((w - tw) // 2, h * 0.20))

        # Subtitle — centered, medium
        if self.subtitle_font is not None:
            sub = self.subtitle_font.render(self.SUBTITLE, True, COL_SUBTITLE)
            sw, sh = sub.get_size()
            screen.blit(sub, ((w - sw) // 2, h * 0.20 + 90))

        # Details — list of bullets, centered column
        if self.font is not None and self.DETAILS:
            y = int(h * 0.36)
            for line in self.DETAILS:
                surf = self.font.render(f"   {line}", True, COL_DETAIL)
                lw, _ = surf.get_size()
                screen.blit(surf, ((w - lw) // 2 - 80, y))
                y += 30

        # Controls hint at bottom
        if self.font is not None:
            controls = self.font.render(
                "[Esc / B / Backspace] back        [F1] scene switcher        [Start] quit",
                True,
                COL_CONTROLS,
            )
            cw, _ = controls.get_size()
            screen.blit(controls, ((w - cw) // 2, h - 60))


# ---------------------------------------------------------------------------
# Stubs — one class per planned scene. Order roughly by gameplay frequency.
# ---------------------------------------------------------------------------

class MainMenuScene(StubScene):
    TITLE = "STAR CONTROL ZERO"
    SUBTITLE = "The Precursors — Furling Era"
    ACCENT = (240, 230, 200)
    BACKDROP_PATH = "assets/generated_drafts/firefly/tier1_cutscenes/cutscene_migration_portal.png"
    BACKDROP_DIM = 140
    DETAILS = [
        "Title screen — entry point of the game.",
        "",
        "Will offer:  Continue · New Game · Super Melee · Settings · Quit",
        "",
        "Press F1 to open the scene switcher and jump straight into any view.",
        "",
        "Press A / Space to begin (you'll start at Mh-Lai Station).",
    ]

    def __init__(self) -> None:
        super().__init__(parent_scene_cls=None)

    def update(self, dt: float, inp) -> None:  # type: ignore[no-untyped-def]
        # MainMenu's "back" is quit (no parent)
        if inp.cancel and self.game is not None:
            self.game.quit()
            return
        # Confirm → launch the real game (Station: home base)
        if inp.confirm and self.game is not None:
            from scz.station.scene import StationScene
            self.game.set_scene(StationScene())
            return


class PlanetScanScene(StubScene):
    TITLE = "Planet Scan"
    SUBTITLE = "Pre-landing reconnaissance from orbit"
    ACCENT = (140, 230, 200)
    DETAILS = [
        "From the star-system view, before landing on a planet,",
        "the player initiates a three-spectrum scan:",
        "",
        "   MINERAL scan      reveals common/useful element deposits",
        "   BIOLOGICAL scan   reveals bio-data nodes & living organisms",
        "   ENERGY scan       reveals artifact/anomaly emissions",
        "",
        "Scan results determine whether a planet is worth landing on,",
        "and pre-reveal the deposit locations the lander will collect.",
        "",
        "Implementation note: lightweight overlay/sub-mode of SystemScene,",
        "not strictly its own scene. Stub for reference only.",
    ]


class DialogScene(StubScene):
    TITLE = "Dialog"
    SUBTITLE = "Alien conversation — LLM-rendered text over a fixed FSM"
    ACCENT = (180, 200, 255)
    DETAILS = [
        "The central LLM-powered system. Each alien species has:",
        "",
        "   • a deterministic finite state machine (FSM) of conversation states",
        "   • per-state choice categories (FIGHT / FLEE / TALK / GIVE / ASK / ...)",
        "   • side effects (SET_GAME_STATE) on transitions",
        "",
        "The LLM renders ONLY the surface text — the words the alien says, and the",
        "player's choice phrasings — based on species voice profile + disposition",
        "+ recent history. Same encounter twice = same outcome, different words.",
        "",
        "Fallback: canned text per (state, intent) when the LLM is unavailable.",
    ]


class ObservationScene(StubScene):
    TITLE = "Proto-Species Observation"
    SUBTITLE = "Lightweight visit to a pre-sentient species"
    ACCENT = (140, 220, 160)
    BACKDROP_PATH = "assets/generated_drafts/firefly/tier1_planets/planet_sol_iii.png"
    DETAILS = [
        "Land on a planet hosting pre-sentient life (proto-Spathi, proto-VUX,",
        "proto-humans on Sol, etc.). No choices, no FSM — just observe.",
        "",
        "   The LLM produces a Furling Archivist log entry in",
        "   Attenborough-warm voice, 3-5 sentences describing what",
        "   the species is doing and where their trajectory points.",
        "",
        "Player may add an optional personal annotation. Bio-data reward.",
        "Permanent Archive flag (Time Drive cannot undo — they exist).",
        "",
        "Thematic counterweight to the Ur-Quan uplift dilemma:",
        "most species are better off left alone.",
    ]


# MeleeCombatScene is now a real scene — see scz/combat/scene.py.
# SuperMeleeScene picks ships and launches it; both sides are AI-driven.


class CouncilScene(StubScene):
    TITLE = "Furling Council"
    SUBTITLE = "Internal debate over species fates and migration policy"
    ACCENT = (220, 180, 240)
    BACKDROP_PATH = "assets/generated_drafts/firefly/tier1_backdrops/backdrop_council_chamber.png"
    DETAILS = [
        "The Furling player's home base. A circular chamber with six faction",
        "representatives, each an LLM-driven NPC:",
        "",
        "   Persuaders  • Compellers  • Cleansers",
        "   Defenders   • Deniers     • Hiders",
        "",
        "The player presents observation reports and recommendations on each",
        "species' fate (Migrate / Cloak / Cleanse / Leave-alone, etc.).",
        "Each faction reacts in character; the Council updates faction balance.",
        "",
        "Unique to our game — SC2 has nothing equivalent.",
    ]


class StationScene(StubScene):
    TITLE = "Station / Home Port"
    SUBTITLE = "Furling waystation — commander, trade, upgrade"
    ACCENT = (180, 220, 240)
    BACKDROP_PATH = "assets/generated_drafts/firefly/tier1_cutscenes/cutscene_cloak_install.png"
    DETAILS = [
        "The Furling equivalent of SC2's Earth Starbase. Three sub-modes:",
        "",
        "   COMMANDER — dialog with the station commander (mission briefings,",
        "               lore, rumor about other species, plot beats)",
        "",
        "   TRADE     — sell resources (minerals, bio-data, energy) for",
        "               Furling Council credits / faction standing / module parts",
        "",
        "   UPGRADE   — install ship modules (Ship Customization scene)",
        "",
        "Stations are visible on the starmap as special points. The slice",
        "may have one or two; the full game would have several.",
    ]


class ShipCustomizationScene(StubScene):
    TITLE = "Ship Customization"
    SUBTITLE = "Modular Furling Scout — install / swap / remove modules"
    ACCENT = (240, 200, 140)
    DETAILS = [
        "The player's Furling Scout has slots for:",
        "",
        "   Hull modules     — armor, structure, crew capacity, hangars, cargo",
        "   Drive modules    — thrusters, hyperdrive class, Time Drive capacity",
        "   Weapon modules   — beams, missiles, point-defense",
        "   Sensor modules   — bio-scanner, mineral-scanner, Other-detector",
        "   Field modules    — shields, cloaks, terraforming, Rainbow Resonator",
        "   Crew specialists — Archivist, Bio-Architect, Warden, Tunneler",
        "",
        "Many quest rewards are permanent ship upgrades. Ship silhouette",
        "changes visibly with the installed module config.",
    ]


class ClusterStatusBoardScene(StubScene):
    TITLE = "Cluster Status Board"
    SUBTITLE = "Win-condition tracking — every species, every terminal status"
    ACCENT = (255, 230, 140)
    BACKDROP_PATH = "assets/generated_drafts/firefly/tier1_cutscenes/cutscene_rainbow_seeding.png"
    DETAILS = [
        "The slice's win-condition view. Each sentient species in the cluster",
        "is listed with its current terminal status:",
        "",
        "   Slylandro Observers      [ Cloaking Satellite installed → CLOAKED ]",
        "   Mycon Biot Hive          [ Deep Child suppressed → PRE-SENTIENT  ]",
        "   Proto-Ur-Quan colonies   [ left undisturbed → PRE-SENTIENT       ]",
        "   Arilou Outpost           [ withdrawing to exile → HIDDEN          ]",
        "",
        "Plus:  Migration deadline countdown (T-minus years/months)",
        "       Furling Council faction standings",
        "       Bio-Archive entries collected",
        "",
        "Win = every species in a terminal status + Rainbow World seeded.",
    ]


class ArchiveScene(StubScene):
    TITLE = "Furling Bio-Archive"
    SUBTITLE = "Codex — observations, council reports, lore unlocked"
    ACCENT = (160, 220, 200)
    BACKDROP_PATH = "assets/generated_drafts/firefly/tier1_cutscenes/cutscene_distress_beacon.png"
    DETAILS = [
        "The player's accumulated knowledge. Browsable by category:",
        "",
        "   SPECIES     — every alien encountered (proto-, sentient, refugees)",
        "                 with the Archivist's log entries + your annotations",
        "",
        "   ARTIFACTS   — Rainbow Worlds seeded, Cloaking Satellites installed,",
        "                 found Furling-era objects (Sa-Matra updates, Moonbase, etc.)",
        "",
        "   COUNCIL     — Furling Council ledger: your recommendations, their",
        "                 outcomes, faction standings over time",
        "",
        "   THE OTHERS  — what the Furlings know about the threat (grows with",
        "                 each Androsynth/Chenjesu/Mmrnmhrm testimony)",
    ]


# QuasiSpaceScene is now a real scene — see scz/quasispace/scene.py.
