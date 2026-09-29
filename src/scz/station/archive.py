"""BioArchiveScene — Furling Bio-Archive at Mh-Lai Station.

Three-pane layout:
  CATEGORIES (left)  ─  ENTRIES (middle)  ─  DETAIL (bottom, full width)

Standard menu nav: D-pad / arrows / L-stick up-down move within the focused
column; menu_prev / menu_next switch column focus (slots <-> modules style);
A on an entry replays its cinematic if it has one; B returns to Station.

Per the design in `references/lore/station-screens-design.md` §3.
"""

from __future__ import annotations

from typing import Literal

import pygame

from scz.content.archive_entries import (
    ARCHIVE_ENTRIES,
    CATEGORY_DISPLAY,
    CATEGORY_ORDER,
    ArchiveEntry,
    visible_entries,
)
from scz.engine.scene import Scene


Focus = Literal["categories", "entries"]


class BioArchiveScene(Scene):
    """Browsable archive of every species, artifact, council recommendation,
    and Other-evidence the Steward has accumulated.
    """

    def __init__(self) -> None:
        super().__init__()
        self.focus: Focus = "categories"
        self.category_idx: int = 0
        self.entry_idx: int = 0
        self.last_msg: str = ""
        self.last_msg_age: float = 0.0
        # Cache of visible-entries built once per on_enter / update; rebuilt
        # cheaply, doesn't need invalidation logic.
        self._visible: dict[str, list[ArchiveEntry]] = {}
        self.fonts: dict[str, pygame.font.Font] = {}

    def on_enter(self) -> None:
        self.fonts["title"] = pygame.font.SysFont("consolas", 32, bold=True)
        self.fonts["subtitle"] = pygame.font.SysFont("consolas", 18)
        self.fonts["category"] = pygame.font.SysFont("consolas", 22)
        self.fonts["entry"] = pygame.font.SysFont("consolas", 18)
        self.fonts["detail"] = pygame.font.SysFont("consolas", 18)
        self.fonts["small"] = pygame.font.SysFont("consolas", 14)
        if self.game is not None:
            self._visible = visible_entries(self.game)
            # Clamp indices to non-empty initial state
            self._clamp_indices()

    def snapshot(self) -> dict | None:
        return None

    def update(self, dt: float, inp) -> None:  # type: ignore[no-untyped-def]
        assert self.game is not None
        if self.last_msg:
            self.last_msg_age += dt
            if self.last_msg_age > 3.0:
                self.last_msg = ""

        # Rebuild visibility — a new entry could have unlocked between frames
        # (cheap; ~20 dict lookups). Reset entry_idx if the current entry
        # disappeared (shouldn't happen mid-scene, but be defensive).
        self._visible = visible_entries(self.game)
        self._clamp_indices()

        if inp.cancel:
            from scz.station.scene import StationScene
            self.game.set_scene(StationScene())
            return

        if inp.menu_prev:
            self.focus = "categories"
        elif inp.menu_next:
            self.focus = "entries"

        if self.focus == "categories":
            n = len(CATEGORY_ORDER)
            if inp.menu_up:
                self.category_idx = (self.category_idx - 1) % n
                self.entry_idx = 0
            elif inp.menu_down:
                self.category_idx = (self.category_idx + 1) % n
                self.entry_idx = 0
            # A on a non-empty category jumps focus into its entries
            if inp.confirm:
                entries = self._current_entries()
                if entries:
                    self.focus = "entries"
                    self.entry_idx = 0
        else:  # entries
            entries = self._current_entries()
            if entries:
                n = len(entries)
                if inp.menu_up:
                    self.entry_idx = (self.entry_idx - 1) % n
                elif inp.menu_down:
                    self.entry_idx = (self.entry_idx + 1) % n
                if inp.confirm:
                    self._activate_entry(entries[self.entry_idx])

    def _clamp_indices(self) -> None:
        if self.category_idx >= len(CATEGORY_ORDER):
            self.category_idx = 0
        entries = self._current_entries()
        if entries:
            if self.entry_idx >= len(entries):
                self.entry_idx = 0
        else:
            self.entry_idx = 0

    def _current_category(self) -> str:
        return CATEGORY_ORDER[self.category_idx]

    def _current_entries(self) -> list[ArchiveEntry]:
        return self._visible.get(self._current_category(), [])

    def _selected_entry(self) -> ArchiveEntry | None:
        entries = self._current_entries()
        if not entries:
            return None
        return entries[self.entry_idx]

    def _activate_entry(self, entry: ArchiveEntry) -> None:
        # If the entry carries a cinematic_id, attempt to replay. For the
        # slice, the actual cinematic playback is owned by the image-chat;
        # we log a hand-off line so the wiring is visible when it lands.
        if entry.cinematic_id is not None:
            self.last_msg = f"[cinematic replay: {entry.cinematic_id}]"
            self.last_msg_age = 0.0
            print(f"[BioArchive] cinematic replay requested: {entry.cinematic_id}")
        else:
            self.last_msg = "Entry recorded. The Steward turns the page."
            self.last_msg_age = 0.0

    # ------------------------------------------------------------------
    # Render
    # ------------------------------------------------------------------

    def render(self, screen: pygame.Surface) -> None:
        assert self.game is not None
        screen.fill((6, 8, 20))
        w, h = screen.get_size()

        title = self.fonts["title"].render(
            "FURLING BIO-ARCHIVE", True, (220, 230, 250),
        )
        tw, _ = title.get_size()
        screen.blit(title, ((w - tw) // 2, 30))
        sub = self.fonts["subtitle"].render(
            "Mh-Lai Station  ·  the Steward's accumulated record",
            True,
            (160, 180, 210),
        )
        sw, _ = sub.get_size()
        screen.blit(sub, ((w - sw) // 2, 75))

        # Layout (top two columns + bottom full-width detail pane)
        left_x = 60
        mid_x = 380
        col_top = 120
        col_w_left = 280
        col_w_mid = w - mid_x - 60
        detail_y = h - 360
        detail_h = 280
        # Cap top columns so they don't overlap the detail pane
        top_h = detail_y - col_top - 30

        self._render_category_column(screen, left_x, col_top, col_w_left, top_h)
        self._render_entry_column(screen, mid_x, col_top, col_w_mid, top_h)
        self._render_detail_pane(screen, left_x, detail_y, w - 120, detail_h)

        # Last-action message (e.g. cinematic replay)
        if self.last_msg:
            alpha = max(0, 255 - int(self.last_msg_age / 3.0 * 255))
            msg = self.fonts["entry"].render(
                self.last_msg, True, (180, 240, 200),
            )
            msg.set_alpha(alpha)
            mw, _ = msg.get_size()
            screen.blit(msg, ((w - mw) // 2, h - 70))

        # Controls hint
        hint = self.fonts["small"].render(
            "Up/Down nav  ·  Left/Right switch column  ·  A view/replay  ·  B back",
            True, (130, 150, 180),
        )
        hw, _ = hint.get_size()
        screen.blit(hint, ((w - hw) // 2, h - 36))

    def _render_category_column(
        self, screen: pygame.Surface, x: int, y: int, w: int, h: int,
    ) -> None:
        focused = self.focus == "categories"
        header_color = (220, 230, 250) if focused else (140, 150, 180)
        screen.blit(
            self.fonts["category"].render("CATEGORIES", True, header_color),
            (x, y),
        )
        ry = y + 36
        for idx, cat in enumerate(CATEGORY_ORDER):
            entries = self._visible.get(cat, [])
            is_selected = idx == self.category_idx
            highlight = is_selected and focused
            bg = (40, 60, 100) if highlight else (16, 18, 32)
            border = (200, 220, 240) if highlight else (40, 50, 70)
            pygame.draw.rect(screen, bg, (x, ry, w, 44))
            pygame.draw.rect(screen, border, (x, ry, w, 44), 1)
            count = len(entries)
            mark = "►" if highlight else (" " if is_selected else " ")
            label_color = (
                (220, 230, 180) if count > 0 else (110, 120, 150)
            )
            label = f"{mark}  {CATEGORY_DISPLAY[cat]:11s}  ({count})"
            screen.blit(
                self.fonts["entry"].render(label, True, label_color),
                (x + 10, ry + 12),
            )
            ry += 50

        # Total-unlocked tally below the column
        total = sum(len(v) for v in self._visible.values())
        max_total = len(ARCHIVE_ENTRIES)
        screen.blit(
            self.fonts["small"].render(
                f"{total} / {max_total} entries unlocked",
                True, (130, 150, 180),
            ),
            (x, ry + 12),
        )

    def _render_entry_column(
        self, screen: pygame.Surface, x: int, y: int, w: int, h: int,
    ) -> None:
        focused = self.focus == "entries"
        header_color = (220, 230, 250) if focused else (140, 150, 180)
        screen.blit(
            self.fonts["category"].render(
                CATEGORY_DISPLAY[self._current_category()],
                True, header_color,
            ),
            (x, y),
        )
        entries = self._current_entries()
        ry = y + 36
        if not entries:
            screen.blit(
                self.fonts["entry"].render(
                    "  (no entries in this category yet)",
                    True, (130, 140, 160),
                ),
                (x, ry),
            )
            return
        for idx, entry in enumerate(entries):
            is_selected = idx == self.entry_idx
            highlight = is_selected and focused
            bg = (40, 60, 100) if highlight else (16, 18, 32)
            border = (200, 220, 240) if highlight else (40, 50, 70)
            pygame.draw.rect(screen, bg, (x, ry, w, 44))
            pygame.draw.rect(screen, border, (x, ry, w, 44), 1)
            mark = "►" if highlight else " "
            tag = "▶" if entry.cinematic_id is not None else " "
            screen.blit(
                self.fonts["entry"].render(
                    f"{mark} {tag} {entry.name}",
                    True, (220, 230, 180),
                ),
                (x + 8, ry + 4),
            )
            screen.blit(
                self.fonts["small"].render(
                    f"     {entry.short_desc}",
                    True, (160, 175, 200),
                ),
                (x + 8, ry + 24),
            )
            ry += 50

    def _render_detail_pane(
        self, screen: pygame.Surface, x: int, y: int, w: int, h: int,
    ) -> None:
        # Frame
        pygame.draw.rect(screen, (12, 14, 26), (x, y, w, h))
        pygame.draw.rect(screen, (60, 80, 120), (x, y, w, h), 1)

        entry = self._selected_entry()
        if entry is None:
            screen.blit(
                self.fonts["entry"].render(
                    "Select an unlocked entry to view its record.",
                    True, (130, 150, 180),
                ),
                (x + 20, y + 24),
            )
            return

        # Entry title
        screen.blit(
            self.fonts["category"].render(entry.name, True, (240, 230, 200)),
            (x + 20, y + 16),
        )
        # cinematic indicator
        if entry.cinematic_id is not None:
            screen.blit(
                self.fonts["small"].render(
                    "▶ replayable cinematic — press A on this entry",
                    True, (180, 240, 200),
                ),
                (x + 20, y + 50),
            )

        # Body — wrap manually to the pane width
        body_x = x + 20
        body_y = y + 78
        body_w = w - 40
        line_height = 22
        max_lines = (h - 90) // line_height

        font = self.fonts["detail"]
        rendered = 0
        for paragraph in entry.long_desc.split("\n\n"):
            for line in _wrap_text(paragraph.strip(), font, body_w):
                if rendered >= max_lines:
                    break
                surf = font.render(line, True, (210, 215, 230))
                screen.blit(surf, (body_x, body_y + rendered * line_height))
                rendered += 1
            if rendered >= max_lines:
                break
            # Blank line between paragraphs
            rendered += 1
            if rendered >= max_lines:
                break


def _wrap_text(text: str, font: pygame.font.Font, max_width: int) -> list[str]:
    """Greedy word-wrap to fit a pygame Font into a pixel width.

    Empty or whitespace-only `text` returns a single empty line so the caller's
    paragraph-spacing logic still steps a row.
    """
    if not text.strip():
        return [""]
    words = text.split()
    lines: list[str] = []
    cur: list[str] = []
    for word in words:
        trial = " ".join(cur + [word])
        if font.size(trial)[0] <= max_width:
            cur.append(word)
        else:
            if cur:
                lines.append(" ".join(cur))
            cur = [word]
    if cur:
        lines.append(" ".join(cur))
    return lines
