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

from scz.engine.input import IS_WEB
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

        # (Debug-only labels — "STUB — content coming soon" tag + F1
        # switcher hint — hidden 2026-05-19. These were never intended
        # for actual gameplay. The F1 hotkey is preserved silently for
        # development use.)

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

        # Controls hint at bottom — gameplay actions only; the F1
        # scene-switcher is a debug surface and intentionally not
        # advertised in this hint.
        if self.font is not None:
            controls = self.font.render(
                "[Esc / B / Backspace] back        [Start] quit",
                True,
                COL_CONTROLS,
            )
            cw, _ = controls.get_size()
            screen.blit(controls, ((w - cw) // 2, h - 60))


# ---------------------------------------------------------------------------
# Stubs — one class per planned scene. Order roughly by gameplay frequency.
# ---------------------------------------------------------------------------

class MainMenuScene(StubScene):
    """Real main menu with campaign management (Aaron 2026-05-18).

    Top-level options:
      Continue        — load the most-recent save of the most-recent campaign
      New Campaign    — create a new campaign and start at Mh-Lai
      Load Campaign   — pick from existing campaigns
      Super Melee     — AI-vs-AI combat picker (no campaign)
      Quit            — exit

    Campaign creation uses an auto-generated stardate name (no name-
    entry UI to keep the menu controller-friendly). The campaign list
    shows display name + "Nm ago" updated time.
    """

    TITLE = "STAR CONTROL ZERO"
    SUBTITLE = "The Precursors — Furling Era"
    ACCENT = (240, 230, 200)
    BACKDROP_PATH = "assets/generated_drafts/firefly/tier1_cutscenes/cutscene_migration_portal.png"
    BACKDROP_DIM = 140
    # Plays the title_menu music context on entry (Eleven-keep 4-min
    # orchestrated piece). Aaron 2026-05-19: was silent because no
    # music_context was declared and the game boots straight into here.
    music_context = "title_menu"

    # Top-level menu items. Each is (label, action_key). The Continue
    # entry is hidden when no campaigns exist; Load is hidden then too.
    _ALL_ITEMS: tuple[tuple[str, str], ...] = (
        ("Continue",       "continue"),
        ("New Campaign",   "new"),
        ("Load Campaign",  "load"),
        ("Super Melee",    "melee"),
        ("Quit",           "quit"),
    )

    def __init__(self) -> None:
        super().__init__(parent_scene_cls=None)
        # Two-mode UI: "main" (top-level menu) or "load" (campaign list).
        self.mode: str = "main"
        self.menu_idx: int = 0
        self.load_idx: int = 0
        self._campaigns_cache: list = []   # CampaignInfo list, refreshed in on_enter

    # ------------------------------------------------------------------

    def on_enter(self) -> None:
        super().on_enter()
        self._refresh_campaigns()
        # Cursor always starts at the first visible item — that's
        # "Continue" when campaigns exist, "New Campaign" otherwise
        # (the no-campaign filter removes Continue+Load from the list).
        # First-press-confirm therefore always routes to a Station entry
        # (load-or-create), which is the canonical "I want to play" path
        # and keeps the test harness's `press("confirm")` walks working.
        self.menu_idx = 0

    def _refresh_campaigns(self) -> None:
        if self.game is None:
            self._campaigns_cache = []
            return
        # Test-harness isolation: walks run in a fresh in-memory game
        # state; if a prior test left a campaign on disk, picking it up
        # here would auto-load and overwrite the walk's pre-seeded
        # credits/cargo/flags. Skip the on-disk scan under isolation.
        cm = self.game.campaign_manager
        if getattr(cm, "_test_isolated", False):
            self._campaigns_cache = []
            return
        self._campaigns_cache = cm.list_campaigns()

    def _has_campaigns(self) -> bool:
        return bool(self._campaigns_cache)

    def _visible_items(self) -> list[tuple[str, str]]:
        """Filter out Continue/Load when no campaigns exist."""
        hidden: set[str] = set()
        if not self._has_campaigns():
            hidden |= {"continue", "load"}
        if IS_WEB:
            hidden.add("quit")      # a browser tab has nothing to quit to
        return [it for it in self._ALL_ITEMS if it[1] not in hidden]

    # ------------------------------------------------------------------

    def update(self, dt: float, inp) -> None:  # type: ignore[no-untyped-def]
        if self.game is None:
            return
        if self.mode == "main":
            self._update_main(inp)
        else:
            self._update_load(inp)

    def _sfx(self, kind: str) -> None:
        if hasattr(self.game, "sfx"):
            self.game.sfx.play(f"ui/menu_{kind}")

    def _update_main(self, inp) -> None:  # type: ignore[no-untyped-def]
        items = self._visible_items()
        n = len(items)
        if inp.cancel:
            # MainMenu's "back" is quit (no parent)
            self._sfx("cancel")
            self.game.quit()
            return
        if inp.menu_up:
            self.menu_idx = (self.menu_idx - 1) % n
            self._sfx("select")
        elif inp.menu_down:
            self.menu_idx = (self.menu_idx + 1) % n
            self._sfx("select")
        if inp.confirm:
            self._sfx("confirm")
            _, action = items[self.menu_idx]
            self._do_action(action)

    def _update_load(self, inp) -> None:  # type: ignore[no-untyped-def]
        n = max(1, len(self._campaigns_cache))
        if inp.cancel:
            self._sfx("cancel")
            self.mode = "main"
            return
        if inp.menu_up:
            self.load_idx = (self.load_idx - 1) % n
            self._sfx("select")
        elif inp.menu_down:
            self.load_idx = (self.load_idx + 1) % n
            self._sfx("select")
        if inp.confirm and self._campaigns_cache:
            self._sfx("confirm")
            self._load_campaign_by_index(self.load_idx)

    # ------------------------------------------------------------------

    def _do_action(self, action: str) -> None:
        if action == "continue":
            # Quick-resume — bypass the scrubber, just restore the
            # latest save from the most-recent campaign and drop into
            # Station. (Aaron 2026-05-18 split: Continue = fast, Load
            # = scrubber-driven moment-picker.)
            if not self._campaigns_cache:
                return
            self._continue_latest(self._campaigns_cache[0].slug)
        elif action == "new":
            self._start_new_campaign()
        elif action == "load":
            self.mode = "load"
            self.load_idx = 0
        elif action == "melee":
            from scz.combat.super_melee import SuperMeleeScene
            self.game.set_scene(SuperMeleeScene())
        elif action == "quit":
            self.game.quit()

    def _continue_latest(self, slug: str) -> None:
        """Quick-resume entry point — auto-load latest save and drop
        into Station. No scrubber UI."""
        state = self.game.campaign_manager.load_latest(slug)
        if state is None:
            return
        from scz.engine.persistence import restore_game
        restore_game(self.game, state)
        self.game.campaign_manager.set_active(slug)
        from scz.station.scene import StationScene
        self.game.set_scene(StationScene())

    def _start_new_campaign(self) -> None:
        # Under test isolation, skip the on-disk campaign creation +
        # auto-snapshot entirely — those would persist to ~/.scz and
        # contaminate subsequent test runs. Just transition to Station.
        cm = self.game.campaign_manager
        if not getattr(cm, "_test_isolated", False):
            # Auto-generate a name. Players who want a specific name can
            # rename the campaign dir on disk later (file rename, no UI
            # for it yet — controller-friendly menus don't need text entry
            # for the MVP).
            import time as _time
            name = _time.strftime("Stardate %Y-%m-%d %H%M")
            slug = cm.create_campaign(name)
            cm.set_active(slug)
            # Take an immediate first snapshot so the campaign has at least
            # one save on disk before the player does anything.
            cm.snapshot(self.game)
        from scz.station.scene import StationScene
        self.game.set_scene(StationScene())

    def _load_campaign_by_index(self, idx: int) -> None:
        """Pick a campaign — open the save scrubber on it (Aaron
        2026-05-18: thumbnail-driven scrubber UI for save selection).
        Doesn't auto-load the latest save; the player picks from the
        20-save scrubber.
        """
        if not self._campaigns_cache:
            return
        idx = max(0, min(idx, len(self._campaigns_cache) - 1))
        info = self._campaigns_cache[idx]
        # Activate the campaign first so the scrubber's auto-save-after-
        # restore goes back into the same dossier.
        self.game.campaign_manager.set_active(info.slug)
        from scz.scenes.save_scrubber import SaveScrubberScene
        self.game.set_scene(SaveScrubberScene(
            slug=info.slug,
            default_cursor_age_s=0.0,   # newest save selected by default
            title_prefix="LOAD A MOMENT",
        ))

    # ------------------------------------------------------------------

    def render(self, screen: pygame.Surface) -> None:
        screen.fill(COL_BG)
        w, h = screen.get_size()

        self._ensure_backdrop((w, h))
        if self._backdrop_surface is not None:
            screen.blit(self._backdrop_surface, (0, 0))

        # (F1-switcher hint hidden 2026-05-19 — it's a debug-only
        # surface, not advertised in production play. F1 hotkey still
        # works for development; players just aren't told about it.)

        # Title — centered.
        if self.title_font is not None:
            title = self.title_font.render(self.TITLE, True, self.ACCENT)
            tw, _ = title.get_size()
            screen.blit(title, ((w - tw) // 2, int(h * 0.14)))

        # Subtitle — centered under title.
        if self.subtitle_font is not None:
            sub = self.subtitle_font.render(self.SUBTITLE, True, COL_SUBTITLE)
            sw, _ = sub.get_size()
            screen.blit(sub, ((w - sw) // 2, int(h * 0.14) + 80))

        if self.mode == "main":
            self._render_main(screen, w, h)
        else:
            self._render_load(screen, w, h)

        # Controls hint at bottom.
        if self.font is not None:
            if self.mode == "main":
                controls = "[W/S or ↑/↓] navigate     [Space / Enter / A] select"
                if not IS_WEB:
                    controls += "     [Esc] quit"
            else:
                controls = "[W/S or ↑/↓] navigate     [Space / Enter / A] load     [Esc] back"
            ctxt = self.font.render(controls, True, COL_CONTROLS)
            cw, _ = ctxt.get_size()
            screen.blit(ctxt, ((w - cw) // 2, h - 60))

    def _render_main(self, screen: pygame.Surface, w: int, h: int) -> None:
        items = self._visible_items()
        if self.menu_idx >= len(items):
            self.menu_idx = 0
        big = pygame.font.SysFont("consolas", 32, bold=True)
        small = pygame.font.SysFont("consolas", 18)
        y = int(h * 0.42)
        for i, (label, _) in enumerate(items):
            is_selected = (i == self.menu_idx)
            color = (255, 240, 200) if is_selected else (160, 170, 200)
            prefix = "▶ " if is_selected else "  "
            surf = big.render(f"{prefix}{label}", True, color)
            lw, _h = surf.get_size()
            screen.blit(surf, ((w - lw) // 2, y))
            y += 50
        # Campaign summary on the right side if any exist.
        if self._campaigns_cache:
            latest = self._campaigns_cache[0]
            txt = f"Last play: {latest.name}  ·  {latest.updated_ago_human()}  ·  {latest.save_count} saves"
            surf = small.render(txt, True, COL_DETAIL)
            tw, _ = surf.get_size()
            screen.blit(surf, ((w - tw) // 2, int(h * 0.82)))

    def _render_load(self, screen: pygame.Surface, w: int, h: int) -> None:
        big = pygame.font.SysFont("consolas", 26, bold=True)
        small = pygame.font.SysFont("consolas", 16)
        header = big.render("LOAD CAMPAIGN", True, COL_TITLE)
        hw, _ = header.get_size()
        screen.blit(header, ((w - hw) // 2, int(h * 0.32)))
        if not self._campaigns_cache:
            empty = small.render(
                "(no campaigns yet — press Esc to go back and start a new one)",
                True, COL_DETAIL,
            )
            ew, _ = empty.get_size()
            screen.blit(empty, ((w - ew) // 2, int(h * 0.45)))
            return
        if self.load_idx >= len(self._campaigns_cache):
            self.load_idx = 0
        y = int(h * 0.40)
        for i, info in enumerate(self._campaigns_cache):
            is_selected = (i == self.load_idx)
            color = (255, 240, 200) if is_selected else (160, 170, 200)
            prefix = "▶ " if is_selected else "  "
            line = f"{prefix}{info.name:32}  ·  {info.save_count:>3} saves  ·  {info.updated_ago_human()}"
            surf = small.render(line, True, color)
            lw, _h = surf.get_size()
            screen.blit(surf, ((w - lw) // 2, y))
            y += 28


# PlanetScanScene retired 2026-05-18 — folded into SystemScene's planet
# list with the LR Mineral Scanner sensor providing the from-orbit
# preview. The "three-spectrum scan" pattern is replaced by the
# always-on sensor pillar (one sensor per discovery axis).

# DialogScene stub retired 2026-05-18 — the real DialogScene lives at
# `scz.dialog.scene`; the stub was vestigial documentation and was
# never imported by any production code path.


class ObservationScene(StubScene):
    TITLE = "Proto-Species Observation"
    SUBTITLE = "Lightweight visit to a pre-sentient species"
    music_context = "proto_species_wonder"
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


# CouncilScene stub retired 2026-05-18 — real scene lives at
# `scz.station.council.CouncilScene` and is wired in the switcher.

# StationScene stub retired 2026-05-18 — real scene lives at
# `scz.station.scene.StationScene` and is wired in the switcher.

# ShipCustomizationScene stub retired 2026-05-18 — real scene lives at
# `scz.station.customization.ShipCustomizationScene`.

# ClusterStatusBoardScene stub retired 2026-05-18 — real scene lives at
# `scz.station.status_board.ClusterStatusBoardScene`.

# ArchiveScene stub retired 2026-05-18 — superseded by
# `scz.station.archive.BioArchiveScene` (wired in switcher + StationScene).


# QuasiSpaceScene is now a real scene — see scz/quasispace/scene.py.


# EndingPlaceholderScene retired 2026-05-18 — superseded by
# `scz.scenes.ending.EndingScene` which renders the canonical 6-tier
# ending per `references/lore/the-endings.md`. FinalConflictScene's win
# path now drives `resolve_ending(game)` + transitions to EndingScene.
