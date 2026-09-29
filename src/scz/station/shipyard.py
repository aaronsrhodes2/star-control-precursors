"""ShipyardScene — Mh-Lai-only sub-screen for buying allied hulls.

Canon: `references/lore/economy-and-trade-loops.md` + HANDOFF dispatch
"Allied species ship registry + Mh-Lai purchase UI" (2026-05-17).
Pairs with the new fleet-combat engine (`scenes/fleet_combat.py`,
2026-05-18) — each purchase grows `game.fleet`, which `FleetCombatScene`
uses to populate the player's roster at encounter time.

UI shape (parallels TradeScene + ShipCustomizationScene):
- Vertical list of allied ships from `ALLIED_SHIPS`
- Per-entry status indicator: locked / unlocked / purchased / can't-afford
- A "Back to Station" entry pinned at the bottom
- Right-side detail pane shows the highlighted entry's blurb +
  cost / unlock-flag explanation
- Confirm to purchase; B to return to StationScene
- Last-action floater (fades after ~2.5s) gives feedback per
  TradeScene convention
"""

from __future__ import annotations

import pygame

from scz.content.allied_ships import (
    ALLIED_SHIPS,
    AlliedShipEntry,
    buy_ship,
    is_purchaseable,
)
from scz.engine.scene import Scene


# Status enum for each row's render — drives the row color + label
_STATUS_PURCHASED = "purchased"
_STATUS_PURCHASEABLE = "purchaseable"
_STATUS_LOCKED = "locked"
_STATUS_CANT_AFFORD = "cant_afford"
_STATUS_UNAVAILABLE = "unavailable"


class ShipyardScene(Scene):
    """Mh-Lai Shipyard — browse and buy allied hulls."""

    def __init__(self) -> None:
        super().__init__()
        self.selected: int = 0
        self.fonts: dict[str, pygame.font.Font] = {}
        # Floater message + age (TradeScene convention: ~2.5s fade)
        self.last_msg: str = ""
        self.last_msg_age: float = 0.0

    def on_enter(self) -> None:
        self.fonts["title"] = pygame.font.SysFont("consolas", 36, bold=True)
        self.fonts["body"] = pygame.font.SysFont("consolas", 20)
        self.fonts["small"] = pygame.font.SysFont("consolas", 16)
        self.fonts["menu"] = pygame.font.SysFont("consolas", 22)

    def snapshot(self) -> dict | None:
        return None        # purchases don't rewind

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _entries(self) -> list[AlliedShipEntry]:
        """All ALLIED_SHIPS — locked entries are shown greyed so the
        player learns what's coming, but `unavailable` entries (no
        ShipClass yet) are filtered out entirely."""
        return [s for s in ALLIED_SHIPS if not s.unavailable]

    def _status_for(self, entry: AlliedShipEntry) -> str:
        if entry.unavailable:
            return _STATUS_UNAVAILABLE
        assert self.game is not None
        if entry.ship_class_id in (self.game.fleet or []):
            return _STATUS_PURCHASED
        if not self.game.flags.get(entry.unlock_flag):
            return _STATUS_LOCKED
        if self.game.credits < entry.cost_credits:
            return _STATUS_CANT_AFFORD
        return _STATUS_PURCHASEABLE

    def update(self, dt: float, inp) -> None:  # type: ignore[no-untyped-def]
        # Floater age-out
        if self.last_msg:
            self.last_msg_age += dt
            if self.last_msg_age > 2.5:
                self.last_msg = ""

        # B → back to Station
        if inp.cancel and self.game is not None:
            from scz.station.scene import StationScene
            self.game.set_scene(StationScene())
            return

        entries = self._entries()
        # +1 for the trailing "Back to Station" pseudo-row
        n = len(entries) + 1
        if inp.menu_up:
            self.selected = (self.selected - 1) % n
        elif inp.menu_down:
            self.selected = (self.selected + 1) % n

        if inp.confirm and self.game is not None:
            # Last row is "Back to Station"
            if self.selected == len(entries):
                from scz.station.scene import StationScene
                self.game.set_scene(StationScene())
                return
            entry = entries[self.selected]
            status = self._status_for(entry)
            if status == _STATUS_PURCHASEABLE:
                if buy_ship(self.game, entry):
                    self.last_msg = (
                        f"acquired {entry.display_name}  ·  "
                        f"-{entry.cost_credits} credits  ·  "
                        f"fleet now {len(self.game.fleet)} hulls"
                    )
                    self.last_msg_age = 0.0
                else:
                    # Shouldn't happen given the status check, but be
                    # defensive in case unlock_flag flips between check
                    # and call.
                    self.last_msg = "purchase failed"
                    self.last_msg_age = 0.0
            elif status == _STATUS_PURCHASED:
                self.last_msg = f"{entry.display_name} already in fleet"
                self.last_msg_age = 0.0
            elif status == _STATUS_CANT_AFFORD:
                self.last_msg = (
                    f"need {entry.cost_credits - self.game.credits} more credits"
                )
                self.last_msg_age = 0.0
            elif status == _STATUS_LOCKED:
                self.last_msg = (
                    f"locked  ·  unlocks via {entry.unlock_flag}"
                )
                self.last_msg_age = 0.0

    def render(self, screen: pygame.Surface) -> None:
        screen.fill((6, 8, 20))
        assert self.game is not None
        sw, sh = screen.get_size()

        # Title + credits
        screen.blit(
            self.fonts["title"].render(
                "MH-LAI SHIPYARD", True, (210, 220, 250),
            ),
            (40, 32),
        )
        screen.blit(
            self.fonts["body"].render(
                f"credits: {self.game.credits}  ·  fleet: "
                f"{len(self.game.fleet)} hull(s)",
                True, (180, 200, 220),
            ),
            (40, 78),
        )
        screen.blit(
            self.fonts["small"].render(
                "Allied hulls grow your combat fleet. Hot-swap on death; "
                "damage carries over within an encounter.",
                True, (140, 160, 180),
            ),
            (40, 106),
        )

        # Left column — list of allied ships
        entries = self._entries()
        x = 60
        y = 160
        for i, entry in enumerate(entries):
            status = self._status_for(entry)
            is_sel = (i == self.selected)

            # Colors by status
            if status == _STATUS_PURCHASED:
                base = (140, 200, 140)
            elif status == _STATUS_PURCHASEABLE:
                base = (220, 220, 240) if is_sel else (190, 200, 220)
            elif status == _STATUS_CANT_AFFORD:
                base = (220, 180, 130) if is_sel else (170, 150, 110)
            elif status == _STATUS_LOCKED:
                base = (140, 140, 160) if is_sel else (100, 100, 120)
            else:
                base = (90, 90, 110)

            arrow = "> " if is_sel else "  "
            status_tag = {
                _STATUS_PURCHASED:    "  [IN FLEET]",
                _STATUS_PURCHASEABLE: f"  [{entry.cost_credits}c]",
                _STATUS_CANT_AFFORD:  f"  [{entry.cost_credits}c · short]",
                _STATUS_LOCKED:       "  [locked]",
                _STATUS_UNAVAILABLE:  "  [under construction]",
            }[status]
            label = f"{arrow}{entry.display_name}{status_tag}"
            screen.blit(self.fonts["menu"].render(label, True, base), (x, y))
            y += 34

        # Trailing Back row
        is_sel = (self.selected == len(entries))
        back_color = (220, 220, 240) if is_sel else (180, 190, 210)
        arrow = "> " if is_sel else "  "
        screen.blit(
            self.fonts["menu"].render(
                f"{arrow}Back to Station", True, back_color,
            ),
            (x, y + 8),
        )

        # Right column — detail pane for highlighted entry
        if self.selected < len(entries):
            entry = entries[self.selected]
            status = self._status_for(entry)
            detail_x = sw // 2 + 40
            detail_y = 160
            screen.blit(
                self.fonts["body"].render(
                    entry.display_name, True, (220, 230, 250),
                ),
                (detail_x, detail_y),
            )
            detail_y += 32
            screen.blit(
                self.fonts["small"].render(
                    f"species: {entry.species_id}    "
                    f"class: {entry.ship_class_id}",
                    True, (150, 170, 200),
                ),
                (detail_x, detail_y),
            )
            detail_y += 24
            screen.blit(
                self.fonts["small"].render(
                    f"price: {entry.cost_credits} credits",
                    True, (200, 200, 160),
                ),
                (detail_x, detail_y),
            )
            detail_y += 28
            # Blurb — word-wrap to fit
            detail_y = self._wrap_text(
                screen, entry.blurb, detail_x, detail_y,
                sw - detail_x - 40, (200, 210, 230),
            )
            detail_y += 12
            # Status explanation
            if status == _STATUS_LOCKED:
                screen.blit(
                    self.fonts["small"].render(
                        f"Locked. Unlocks when `{entry.unlock_flag}` is set "
                        f"(complete the relevant species quest).",
                        True, (180, 160, 130),
                    ),
                    (detail_x, detail_y),
                )
            elif status == _STATUS_CANT_AFFORD:
                gap = entry.cost_credits - self.game.credits
                screen.blit(
                    self.fonts["small"].render(
                        f"Short by {gap} credits. Sell more cargo at Trade.",
                        True, (220, 180, 130),
                    ),
                    (detail_x, detail_y),
                )
            elif status == _STATUS_PURCHASED:
                screen.blit(
                    self.fonts["small"].render(
                        "Already in your fleet.",
                        True, (140, 200, 140),
                    ),
                    (detail_x, detail_y),
                )
            elif status == _STATUS_PURCHASEABLE:
                screen.blit(
                    self.fonts["small"].render(
                        "Press A to acquire.",
                        True, (200, 220, 160),
                    ),
                    (detail_x, detail_y),
                )

        # Floater
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

        # Controls pinned bottom-right
        screen.blit(
            self.fonts["small"].render(
                "[A] purchase    [B] back to station",
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
