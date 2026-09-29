"""SchematicVaultScene — Mh-Lai sub-screen for converting schematics
into shop-catalog unlocks.

Canon: `references/lore/economy-and-trade-loops.md` §Schematic Loop +
HANDOFF dispatch "Economy: Schematic Vault scene + Mh-Lai install
gate + Melnorme niche narrowing" (2026-05-17).

UI shape (mirrors `ShipyardScene` and `TradeScene`):
- Vertical list of held schematics from `game.schematics` →
  `held_schematics(game)`
- Per-entry rarity tag (color-coded by rarity tier)
- Trailing "Back to Station" row
- Right-side detail pane: schematic name + rarity + source_origin +
  what the unlocked module is
- Confirm consumes the highlighted schematic; B returns to Station
- Last-action floater (~2.5s) shows feedback per the TradeScene
  convention

The Vault is the *only* place in the slice where schematics can be
converted — Mh-Lai-exclusive by canon. Player can hold any number of
schematics in `game.schematics`; consumption is one-at-a-time.
"""

from __future__ import annotations

import pygame

from scz.content.schematics import (
    SCHEMATICS,
    consume,
    held_schematics,
)
from scz.engine.scene import Scene


# Rarity → display color (most-special first, in canonical order).
_RARITY_COLORS: dict[str, tuple[int, int, int]] = {
    "unique":   (220, 180, 220),    # violet — the rarest tier
    "rare":     (180, 200, 240),    # cool blue
    "uncommon": (200, 220, 200),    # pale green
    "common":   (180, 190, 200),    # neutral
}


class SchematicVaultScene(Scene):
    """The Mh-Lai Schematic Vault sub-screen."""

    def __init__(self) -> None:
        super().__init__()
        self.selected: int = 0
        self.fonts: dict[str, pygame.font.Font] = {}
        self.last_msg: str = ""
        self.last_msg_age: float = 0.0

    def on_enter(self) -> None:
        self.fonts["title"] = pygame.font.SysFont("consolas", 36, bold=True)
        self.fonts["body"] = pygame.font.SysFont("consolas", 20)
        self.fonts["small"] = pygame.font.SysFont("consolas", 16)
        self.fonts["menu"] = pygame.font.SysFont("consolas", 22)

    def snapshot(self) -> dict | None:
        return None    # consumption is irreversible — no rewind

    def update(self, dt: float, inp) -> None:  # type: ignore[no-untyped-def]
        if self.last_msg:
            self.last_msg_age += dt
            if self.last_msg_age > 2.5:
                self.last_msg = ""

        if inp.cancel and self.game is not None:
            from scz.station.scene import StationScene
            self.game.set_scene(StationScene())
            return

        assert self.game is not None
        held = held_schematics(self.game)
        n = len(held) + 1   # +1 for the Back row

        # If held list shrank below the cursor (e.g. last schematic
        # consumed), clamp.
        if self.selected >= n:
            self.selected = max(0, n - 1)

        if inp.menu_up:
            self.selected = (self.selected - 1) % n
        elif inp.menu_down:
            self.selected = (self.selected + 1) % n

        if inp.confirm:
            # Last index = Back row
            if self.selected == len(held):
                from scz.station.scene import StationScene
                self.game.set_scene(StationScene())
                return
            schem = held[self.selected]
            ok = consume(self.game, schem.id)
            if ok:
                self.last_msg = (
                    f"converted: {schem.name}  ·  "
                    f"{schem.target_module_id} unlocked in shop"
                )
                self.last_msg_age = 0.0
            else:
                # Shouldn't happen given the list comes from held — but
                # defensive in case of race with quest side-effects
                self.last_msg = "conversion failed"
                self.last_msg_age = 0.0

    def render(self, screen: pygame.Surface) -> None:
        screen.fill((6, 8, 20))
        assert self.game is not None
        sw, sh = screen.get_size()

        # Title block
        screen.blit(
            self.fonts["title"].render(
                "SCHEMATIC VAULT", True, (210, 220, 250),
            ),
            (40, 32),
        )
        screen.blit(
            self.fonts["body"].render(
                f"held: {len(self.game.schematics or set())} schematic(s)  ·  "
                f"converted: {len(self.game.consumed_schematics or set())}",
                True, (180, 200, 220),
            ),
            (40, 78),
        )
        screen.blit(
            self.fonts["small"].render(
                "Convert held schematics into shop-catalog unlocks. "
                "Conversion is one-way — the schematic is consumed.",
                True, (140, 160, 180),
            ),
            (40, 106),
        )

        held = held_schematics(self.game)
        x = 60
        y = 160

        # Empty state
        if not held:
            screen.blit(
                self.fonts["body"].render(
                    "No schematics in hand.",
                    True, (140, 160, 180),
                ),
                (x, y),
            )
            y += 28
            screen.blit(
                self.fonts["small"].render(
                    "Schematics are awarded by species quests, salvage, "
                    "Hider research-fund witness-payments, and rare "
                    "proto-species exchanges.",
                    True, (120, 140, 160),
                ),
                (x, y),
            )
            y += 36
            # Back row
            is_sel = (self.selected == 0)
            back_color = (220, 220, 240) if is_sel else (180, 190, 210)
            arrow = "> " if is_sel else "  "
            screen.blit(
                self.fonts["menu"].render(
                    f"{arrow}Back to Station", True, back_color,
                ),
                (x, y),
            )
            self._render_floater_and_controls(screen, sw, sh)
            return

        # Non-empty: list of held schematics
        for i, schem in enumerate(held):
            is_sel = (i == self.selected)
            color = _RARITY_COLORS.get(schem.rarity, (180, 190, 200))
            if not is_sel:
                # Dim non-selected slightly
                color = (color[0] * 7 // 10, color[1] * 7 // 10, color[2] * 7 // 10)
            arrow = "> " if is_sel else "  "
            label = f"{arrow}{schem.name}  [{schem.rarity}]"
            screen.blit(self.fonts["menu"].render(label, True, color), (x, y))
            y += 34

        # Back row
        is_sel = (self.selected == len(held))
        back_color = (220, 220, 240) if is_sel else (180, 190, 210)
        arrow = "> " if is_sel else "  "
        screen.blit(
            self.fonts["menu"].render(
                f"{arrow}Back to Station", True, back_color,
            ),
            (x, y + 8),
        )

        # Right-side detail pane
        if self.selected < len(held):
            schem = held[self.selected]
            detail_x = sw // 2 + 40
            detail_y = 160
            screen.blit(
                self.fonts["body"].render(
                    schem.name, True, (220, 230, 250),
                ),
                (detail_x, detail_y),
            )
            detail_y += 32
            rarity_c = _RARITY_COLORS.get(schem.rarity, (180, 190, 200))
            screen.blit(
                self.fonts["small"].render(
                    f"rarity: {schem.rarity}    "
                    f"unlocks: {schem.target_module_id}",
                    True, rarity_c,
                ),
                (detail_x, detail_y),
            )
            detail_y += 28
            screen.blit(
                self.fonts["small"].render(
                    "ORIGIN", True, (180, 200, 220),
                ),
                (detail_x, detail_y),
            )
            detail_y += 22
            detail_y = self._wrap_text(
                screen, schem.source_origin, detail_x, detail_y,
                sw - detail_x - 40, (200, 215, 230),
            )
            detail_y += 12
            screen.blit(
                self.fonts["small"].render(
                    "TARGET MODULE", True, (180, 200, 220),
                ),
                (detail_x, detail_y),
            )
            detail_y += 22
            detail_y = self._wrap_text(
                screen, schem.description, detail_x, detail_y,
                sw - detail_x - 40, (200, 215, 230),
            )
            detail_y += 16
            screen.blit(
                self.fonts["small"].render(
                    "Press A to convert. The schematic is consumed.",
                    True, (200, 220, 160),
                ),
                (detail_x, detail_y),
            )

        self._render_floater_and_controls(screen, sw, sh)

    def _render_floater_and_controls(
        self, screen: pygame.Surface, sw: int, sh: int,
    ) -> None:
        if self.last_msg:
            alpha_frac = max(0.0, 1.0 - (self.last_msg_age / 2.5))
            c = (
                int(140 + alpha_frac * 100),
                int(180 + alpha_frac * 60),
                int(200 + alpha_frac * 40),
            )
            screen.blit(
                self.fonts["body"].render(self.last_msg, True, c),
                (40, sh - 80),
            )
        screen.blit(
            self.fonts["small"].render(
                "[A] convert    [B] back to station",
                True, (150, 170, 190),
            ),
            (sw - 380, sh - 28),
        )

    def _wrap_text(
        self,
        screen: pygame.Surface,
        text: str,
        x: int,
        y: int,
        max_width: int,
        color: tuple[int, int, int],
    ) -> int:
        font = self.fonts["small"]
        line_h = font.get_linesize()
        words = text.split()
        line = ""
        for word in words:
            test = f"{line} {word}".strip()
            if font.size(test)[0] <= max_width:
                line = test
            else:
                if line:
                    screen.blit(font.render(line, True, color), (x, y))
                    y += line_h
                line = word
        if line:
            screen.blit(font.render(line, True, color), (x, y))
            y += line_h
        return y
