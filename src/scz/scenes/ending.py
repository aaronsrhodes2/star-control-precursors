"""EndingScene — tier-aware slice-resolution cinematic.

Canon: `references/lore/the-endings.md`. Six tiers, each with its own
canonical final-narration line, tonal palette, and tone:

  BEST          — "The Quiet Resolution. The bookkeeping is the dignity..."
  GREAT         — "The work was good. Some of it was not done. We continue."
  GOOD          — "...The home is smaller than I hoped."
  AT_COST       — "...The dignity is in not pretending otherwise."
  UNSUCCESSFUL  — "I am the only one. The galaxy is the kitchen now..."
  DISASTROUS    — "Good job."

This scene reads `game.flags["slice_ending"]` and renders the tier's
canonical narration. Cinematic backdrop art is Image chat's lane — when
those assets land, plug them in via `BACKDROP_PATH_BY_TIER`.

Closing: a long display dwell (so the canonical narration lands), then
A/Confirm returns to MainMenu. Esc/Cancel is suppressed during the
dwell so the player can't speed past the canon line.
"""

from __future__ import annotations

import pygame

from scz.content.endings import (
    TIER_AT_COST,
    TIER_BEST,
    TIER_DISASTROUS,
    TIER_GOOD,
    TIER_GREAT,
    TIER_UNSUCCESSFUL,
)
from scz.engine.scene import Scene


# Per-tier title + final canonical line + tonal palette per the-endings.md.
#
# Each entry: (title, subtitle, body_lines, accent_color, bg_color).
# Colors per the doc's "Tonal palette per ending" table.
_TIER_PRESENTATION: dict[str, dict] = {
    TIER_BEST: {
        "title": "THE QUIET RESOLUTION",
        "subtitle": "Honored Fully",
        "body": [
            "The Migration crossing opens. The fleet enters in canonical order.",
            "Every named NPC is alive or canonically honored.",
            "Halia stands beside you (or her memorial sigil glows on the bridge).",
            "Kovellim record this as their 9th crossing.",
            "Karavem perch-cities rise in new canyons.",
            "The Selvenne reef arrives intact. Lemmkin archives unpacked.",
            "The Mrokon memorial inscribed — their dead are named in Andromeda.",
            "",
            "\"The Quiet Resolution. The bookkeeping is the dignity.",
            " The dignity is the work. We continue.\"",
        ],
        "accent": (240, 220, 160),   # warm gold-cream
        "bg":     ( 28,  24,  44),   # Andromeda-promise indigo wash
    },
    TIER_GREAT: {
        "title": "THE QUIET RESOLUTION",
        "subtitle": "Honored",
        "body": [
            "The Migration crossing opens. The fleet enters as planned.",
            "Most personal threads tied. Some unfinished.",
            "The galaxy was saved. Some of the work was not done.",
            "",
            "\"The work was good. Some of it was not done. We continue.\"",
        ],
        "accent": (220, 200, 150),
        "bg":     ( 32,  28,  44),
    },
    TIER_GOOD: {
        "title": "THE QUIET RESOLUTION",
        "subtitle": "Partially Honored",
        "body": [
            "The Migration crossing opens. The galaxy's species arrive.",
            "The named-crew alcoves in your Common Room are partially empty.",
            "The home you arrive with is not the home you could have had.",
            "",
            "\"The galaxy was the work. The galaxy made it.",
            " The home was also the work. The home is smaller than I hoped.\"",
        ],
        "accent": (200, 180, 140),   # warm but cooler
        "bg":     ( 30,  30,  46),
    },
    TIER_AT_COST: {
        "title": "THE QUIET RESOLUTION",
        "subtitle": "Roughly",
        "body": [
            "The Migration crossing opens. The fleet is visibly thinner.",
            "Some species's vessels never arrived.",
            "The bridge is professional, not warm.",
            "",
            "\"The work was the work. We did what we could.",
            " Some did not arrive. The dignity is in not pretending otherwise.\"",
        ],
        "accent": (180, 170, 150),   # cool greys + amber accents
        "bg":     ( 32,  34,  44),
    },
    TIER_UNSUCCESSFUL: {
        "title": "THE STEWARD ESCAPES",
        "subtitle": "The Galaxy Is Consumed",
        "body": [
            "The Migration could not assemble. Drev-Tok stood unopposed.",
            "The Others arrived during the assembly.",
            "You crossed alone — one ship, the corridor closing behind.",
            "",
            "The Others, satisfied with the easy meal, stay.",
            "They consume the galaxy entirely. Forever.",
            "",
            "\"I am the only one. The galaxy is the kitchen now.",
            " I will tell Andromeda what we were.",
            " I will hope no one comes back.\"",
        ],
        "accent": (160, 170, 220),   # deep blues + violet
        "bg":     ( 14,  16,  36),   # lonely
    },
    TIER_DISASTROUS: {
        "title": "THE TREATY",
        "subtitle": "Signed In Steward Blood",
        "body": [
            "You arrived at the Rainbow Worlds alone.",
            "You attempted to negotiate. The Others do not negotiate.",
            "",
            "You drafted a treaty unilaterally — cession of the galaxy,",
            "in perpetuity, in exchange for safe passage.",
            "",
            "They approached your ship. They consumed it.",
            "They used your blood to imprint the treaty",
            "onto the substrate of the galaxy itself.",
            "",
            "The treaty is binding.",
            "",
            "\"You led negotiations to hand over the galaxy to the Others,",
            " for all time, and then they ate you and used your blood",
            " to sign the treaty.",
            "",
            " Good job.\"",
        ],
        "accent": (200,  60,  60),   # harsh blood-red
        "bg":     (  0,   0,   0),   # negative-black
    },
}


# Optional Image-chat-owned backdrop image paths per tier. When the
# Image chat ships these, drop them here and the scene will use them.
BACKDROP_PATH_BY_TIER: dict[str, str | None] = {
    TIER_BEST:         None,
    TIER_GREAT:        None,
    TIER_GOOD:         None,
    TIER_AT_COST:      None,
    TIER_UNSUCCESSFUL: None,
    TIER_DISASTROUS:   None,
}


# Minimum display time before the player can dismiss the ending. The
# canon line should be readable; Disastrous in particular needs the
# silence to land.
_DWELL_TIME_BY_TIER: dict[str, float] = {
    TIER_BEST:         8.0,
    TIER_GREAT:        7.0,
    TIER_GOOD:         7.0,
    TIER_AT_COST:      7.0,
    TIER_UNSUCCESSFUL: 9.0,
    TIER_DISASTROUS:   10.0,   # slice's audio masterpiece — let it breathe
}


class EndingScene(Scene):
    """Renders the canonical ending for the tier stored in
    `game.flags["slice_ending"]`. Reads the tier from flags so the
    scene can be entered from anywhere — FinalConflictScene's win path,
    the migration-timeline-fail path, or a direct switcher entry.

    Defaults to UNSUCCESSFUL if no tier is set (so a stray entry from
    the switcher renders something meaningful rather than crashing).
    """

    def __init__(self) -> None:
        super().__init__()
        self.tier: str = TIER_UNSUCCESSFUL    # safe default; overridden in on_enter
        self.dwell_remaining: float = 0.0
        self.fonts: dict[str, pygame.font.Font] = {}

    def on_enter(self) -> None:
        assert self.game is not None
        flag_tier = self.game.flags.get("slice_ending")
        if flag_tier in _TIER_PRESENTATION:
            self.tier = flag_tier
        # else: keep default UNSUCCESSFUL (degraded but readable)
        self.dwell_remaining = _DWELL_TIME_BY_TIER.get(self.tier, 7.0)

        self.fonts["title"] = pygame.font.SysFont("consolas", 56, bold=True)
        self.fonts["subtitle"] = pygame.font.SysFont("consolas", 28, italic=True)
        self.fonts["body"] = pygame.font.SysFont("consolas", 22)
        self.fonts["hint"] = pygame.font.SysFont("consolas", 16)

    def snapshot(self) -> dict | None:
        return None    # the ending is non-rewindable

    def update(self, dt: float, inp) -> None:  # type: ignore[no-untyped-def]
        if self.dwell_remaining > 0.0:
            self.dwell_remaining -= dt
            return
        # Past the dwell — A or B both return to MainMenu.
        if (inp.confirm or inp.cancel) and self.game is not None:
            from scz.scenes.stubs import MainMenuScene
            self.game.set_scene(MainMenuScene())

    def render(self, screen: pygame.Surface) -> None:
        pres = _TIER_PRESENTATION[self.tier]
        screen.fill(pres["bg"])
        w, h = screen.get_size()

        # Title — centered, large, in the tier's accent color
        title_surf = self.fonts["title"].render(
            pres["title"], True, pres["accent"],
        )
        tw, _th = title_surf.get_size()
        screen.blit(title_surf, ((w - tw) // 2, int(h * 0.10)))

        # Subtitle — italic, centered
        sub_surf = self.fonts["subtitle"].render(
            pres["subtitle"], True, pres["accent"],
        )
        sw, _sh = sub_surf.get_size()
        screen.blit(sub_surf, ((w - sw) // 2, int(h * 0.10) + 72))

        # Body — vertical column of canon lines
        y = int(h * 0.30)
        for line in pres["body"]:
            if not line:
                y += 16
                continue
            body_surf = self.fonts["body"].render(
                line, True, (220, 220, 220),
            )
            lw, _lh = body_surf.get_size()
            screen.blit(body_surf, ((w - lw) // 2, y))
            y += 30

        # Hint at the bottom — only after dwell completes
        if self.dwell_remaining <= 0.0:
            hint_surf = self.fonts["hint"].render(
                "[A / B] return to main menu", True, (140, 140, 160),
            )
            hw, _ = hint_surf.get_size()
            screen.blit(hint_surf, ((w - hw) // 2, h - 40))
