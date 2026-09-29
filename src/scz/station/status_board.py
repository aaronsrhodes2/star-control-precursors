"""ClusterStatusBoardScene — slice-wide win-condition dashboard.

The "am I winning?" view. Three regions:

1. **Faction strip** (top) — six Furling factions with current standing.
2. **Species table** (middle, scrollable) — every tracked species with
   its current terminal status badge + one-line context.
3. **Slice metrics** (bottom) — resolved-species count, Rainbow Worlds
   discovered, Bio-Archive entries unlocked.

Read-only. No mutation. Navigation: D-pad / arrows scroll the species
list; B returns to Station.
"""

from __future__ import annotations

import pygame

from scz.content.cluster_status import (
    SPECIES,
    STATUS_COLORS,
    STATUS_ORDER,
    archive_entry_count,
    rainbow_worlds_discovered,
    resolved_count,
)
from scz.content.council_recommendations import (
    FACTION_LABELS,
    FACTIONS,
    faction_standing,
)
from scz.engine.scene import Scene


# How many species rows fit in the scrollable region. Computed once at
# layout time; this constant is a fallback if the scene runs at an
# unexpected screen height.
_DEFAULT_VISIBLE_ROWS: int = 14


class ClusterStatusBoardScene(Scene):
    """The slice's win-condition dashboard."""

    def __init__(self) -> None:
        super().__init__()
        # Top of the scrolling window — index into SPECIES that's
        # rendered at the top of the species table.
        self.scroll_top: int = 0
        # Cursor — highlights one species. Drives the optional context
        # blurb at the bottom of the species table.
        self.cursor: int = 0
        self.fonts: dict[str, pygame.font.Font] = {}

    def on_enter(self) -> None:
        self.fonts["title"] = pygame.font.SysFont("consolas", 32, bold=True)
        self.fonts["subtitle"] = pygame.font.SysFont("consolas", 18)
        self.fonts["section"] = pygame.font.SysFont("consolas", 22)
        self.fonts["item"] = pygame.font.SysFont("consolas", 18)
        self.fonts["badge"] = pygame.font.SysFont("consolas", 15, bold=True)
        self.fonts["small"] = pygame.font.SysFont("consolas", 14)

    def snapshot(self) -> dict | None:
        return None

    def update(self, dt: float, inp) -> None:  # type: ignore[no-untyped-def]
        assert self.game is not None
        if inp.cancel:
            from scz.station.scene import StationScene
            self.game.set_scene(StationScene())
            return

        n = len(SPECIES)
        if inp.menu_up:
            self.cursor = (self.cursor - 1) % n
            self._ensure_visible()
        elif inp.menu_down:
            self.cursor = (self.cursor + 1) % n
            self._ensure_visible()

    def _ensure_visible(self) -> None:
        """Scroll the visible window so the cursor stays in view."""
        # Computed at render time; keep a sane default until the first
        # render sets the visible-rows count.
        visible = getattr(self, "_visible_rows", _DEFAULT_VISIBLE_ROWS)
        if self.cursor < self.scroll_top:
            self.scroll_top = self.cursor
        elif self.cursor >= self.scroll_top + visible:
            self.scroll_top = self.cursor - visible + 1
        self.scroll_top = max(
            0, min(len(SPECIES) - visible, self.scroll_top),
        )
        if self.scroll_top < 0:
            self.scroll_top = 0

    # ------------------------------------------------------------------
    # Render
    # ------------------------------------------------------------------

    def render(self, screen: pygame.Surface) -> None:
        assert self.game is not None
        screen.fill((8, 8, 18))
        w, h = screen.get_size()

        # Header
        title = self.fonts["title"].render(
            "CLUSTER STATUS BOARD", True, (250, 230, 180),
        )
        tw, _ = title.get_size()
        screen.blit(title, ((w - tw) // 2, 24))
        sub = self.fonts["subtitle"].render(
            "Mh-Lai Operations  ·  the slice at a glance",
            True, (190, 180, 160),
        )
        sw, _ = sub.get_size()
        screen.blit(sub, ((w - sw) // 2, 64))

        # Faction strip
        self._render_faction_strip(screen, w)

        # Species table — middle region, scrollable
        table_top = 200
        table_bottom = h - 180
        table_left = 60
        table_right = w - 60
        self._render_species_table(
            screen, table_left, table_top, table_right - table_left,
            table_bottom - table_top,
        )

        # Bottom metrics strip
        self._render_metrics(screen, w, h - 140)

        # Controls hint
        hint = self.fonts["small"].render(
            "Up/Down scroll  ·  B back to Station",
            True, (140, 150, 180),
        )
        hw, _ = hint.get_size()
        screen.blit(hint, ((w - hw) // 2, h - 36))

    def _render_faction_strip(self, screen: pygame.Surface, w: int) -> None:
        standing = faction_standing(self.game) if self.game else {}
        strip_y = 110
        strip_h = 70
        pad = 60
        usable = w - 2 * pad
        cell_w = usable // len(FACTIONS)
        for i, fac in enumerate(FACTIONS):
            cx = pad + i * cell_w
            pygame.draw.rect(
                screen, (22, 22, 38), (cx, strip_y, cell_w - 8, strip_h),
            )
            pygame.draw.rect(
                screen, (60, 60, 90), (cx, strip_y, cell_w - 8, strip_h), 1,
            )
            label = self.fonts["small"].render(
                FACTION_LABELS[fac], True, (180, 180, 210),
            )
            lw, _ = label.get_size()
            screen.blit(label, (cx + (cell_w - 8 - lw) // 2, strip_y + 10))
            score = standing.get(fac, 0)
            sign = "+" if score > 0 else ""
            color = (
                (180, 220, 180) if score > 0 else
                (200, 160, 160) if score < 0 else
                (160, 160, 180)
            )
            score_text = self.fonts["section"].render(
                f"{sign}{score}", True, color,
            )
            stw, _ = score_text.get_size()
            screen.blit(
                score_text,
                (cx + (cell_w - 8 - stw) // 2, strip_y + 32),
            )

    def _render_species_table(
        self, screen: pygame.Surface, x: int, y: int, w: int, h: int,
    ) -> None:
        row_h = 32
        header_h = 30
        screen.blit(
            self.fonts["section"].render("SPECIES", True, (230, 220, 180)),
            (x, y),
        )
        y += header_h

        visible = max(1, (h - header_h) // row_h)
        self._visible_rows = visible

        for i in range(visible):
            idx = self.scroll_top + i
            if idx >= len(SPECIES):
                break
            sp = SPECIES[idx]
            row_y = y + i * row_h
            status = sp.resolver(self.game) if self.game else "Unknown"
            status_color = STATUS_COLORS.get(status, (170, 170, 200))

            is_cursor = idx == self.cursor
            row_bg = (32, 30, 50) if is_cursor else (16, 16, 30)
            row_border = (200, 200, 230) if is_cursor else (40, 40, 60)
            pygame.draw.rect(screen, row_bg, (x, row_y, w, row_h - 4))
            pygame.draw.rect(screen, row_border, (x, row_y, w, row_h - 4), 1)

            # Name column
            name_color = (230, 220, 200) if is_cursor else (200, 190, 170)
            screen.blit(
                self.fonts["item"].render(sp.name, True, name_color),
                (x + 12, row_y + 6),
            )

            # Status badge — fixed-width pill on the right
            badge_w = 130
            badge_x = x + w - badge_w - 320
            badge_y = row_y + 4
            badge_h = row_h - 12
            pygame.draw.rect(
                screen, (8, 8, 14), (badge_x, badge_y, badge_w, badge_h),
            )
            pygame.draw.rect(
                screen, status_color, (badge_x, badge_y, badge_w, badge_h), 1,
            )
            badge_text = self.fonts["badge"].render(
                status.upper(), True, status_color,
            )
            btw, bth = badge_text.get_size()
            screen.blit(
                badge_text,
                (badge_x + (badge_w - btw) // 2,
                 badge_y + (badge_h - bth) // 2),
            )

            # Blurb to the right of the badge
            blurb_x = badge_x + badge_w + 14
            blurb_color = (170, 175, 195) if is_cursor else (140, 145, 165)
            screen.blit(
                self.fonts["small"].render(sp.short_blurb, True, blurb_color),
                (blurb_x, row_y + 9),
            )

        # Scroll-position indicator
        if len(SPECIES) > visible:
            sb_x = x + w - 8
            sb_y = y
            sb_h = visible * row_h
            pygame.draw.rect(screen, (30, 30, 50), (sb_x, sb_y, 4, sb_h))
            thumb_h = max(8, sb_h * visible // len(SPECIES))
            thumb_y = sb_y + (sb_h - thumb_h) * self.scroll_top // max(
                1, len(SPECIES) - visible,
            )
            pygame.draw.rect(
                screen, (160, 170, 210), (sb_x, thumb_y, 4, thumb_h),
            )

    def _render_metrics(
        self, screen: pygame.Surface, w: int, y: int,
    ) -> None:
        """Bottom strip: resolved-count, Rainbow Worlds, Archive count."""
        if self.game is None:
            return
        resolved, total = resolved_count(self.game)
        rainbows = rainbow_worlds_discovered(self.game)
        archive_unlocked, archive_total = archive_entry_count(self.game)

        # Three equal-width cells
        pad = 60
        usable = w - 2 * pad
        cell_w = usable // 3
        items = [
            (
                "SPECIES RESOLVED",
                f"{resolved} / {total}",
                (180, 220, 180) if resolved == total else (220, 200, 130),
            ),
            (
                "RAINBOW WORLDS",
                f"{rainbows} / 10",
                (240, 200, 140) if rainbows < 10 else (140, 220, 160),
            ),
            (
                "BIO-ARCHIVE",
                f"{archive_unlocked} / {archive_total}",
                (180, 200, 220),
            ),
        ]
        for i, (label, value, color) in enumerate(items):
            cx = pad + i * cell_w
            pygame.draw.rect(
                screen, (22, 22, 38), (cx, y, cell_w - 8, 80),
            )
            pygame.draw.rect(
                screen, (60, 60, 90), (cx, y, cell_w - 8, 80), 1,
            )
            lbl = self.fonts["small"].render(label, True, (170, 170, 200))
            lw, _ = lbl.get_size()
            screen.blit(lbl, (cx + (cell_w - 8 - lw) // 2, y + 10))
            val = self.fonts["section"].render(value, True, color)
            vw, _ = val.get_size()
            screen.blit(val, (cx + (cell_w - 8 - vw) // 2, y + 36))
