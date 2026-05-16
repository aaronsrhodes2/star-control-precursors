"""TradeScene — sells minerals from game.cargo for Council Credits.

Sell-only; buying modules happens at ShipCustomizationScene. All-or-
nothing per type for UI simplicity (no per-unit drag/spinner). Quest
items in `game.uninstalled_modules` are listed for awareness but not
sellable.

Per the design in `references/lore/station-screens-design.md`.
"""

from __future__ import annotations

import pygame

from scz.content.modules import MINERAL_PRICES, MODULES
from scz.engine.scene import Scene
from scz.planet.deposits import RESOURCE_VISUAL


# Menu actions — one per sellable mineral + a "sell all" + an exit
ACTIONS: list[tuple[str, str]] = [
    ("Sell COMMON minerals", "sell_common"),
    ("Sell USEFUL minerals", "sell_useful"),
    ("Sell BIO-data",        "sell_bio"),
    ("Sell ENERGY crystals", "sell_energy"),
    ("Sell ALL minerals",    "sell_all"),
    ("Back to Station",      "back"),
]

ACTION_TO_TYPE: dict[str, str] = {
    "sell_common": "COMMON",
    "sell_useful": "USEFUL",
    "sell_bio":    "BIO",
    "sell_energy": "ENERGY",
}


class TradeScene(Scene):
    """Trade-in counter at Mh-Lai Station."""

    def __init__(self) -> None:
        super().__init__()
        self.selected: int = 0
        self.fonts: dict[str, pygame.font.Font] = {}
        self.last_sale_msg: str = ""
        self.last_sale_age: float = 0.0

    def on_enter(self) -> None:
        self.fonts["title"] = pygame.font.SysFont("consolas", 36, bold=True)
        self.fonts["body"] = pygame.font.SysFont("consolas", 20)
        self.fonts["small"] = pygame.font.SysFont("consolas", 16)
        self.fonts["menu"] = pygame.font.SysFont("consolas", 22)

    def snapshot(self) -> dict | None:
        return None    # transactions don't rewind

    def update(self, dt: float, inp) -> None:  # type: ignore[no-untyped-def]
        if self.last_sale_msg:
            self.last_sale_age += dt
            if self.last_sale_age > 2.5:
                self.last_sale_msg = ""

        if inp.cancel and self.game is not None:
            from scz.station.scene import StationScene
            self.game.set_scene(StationScene())
            return

        n = len(ACTIONS)
        if inp.menu_up:
            self.selected = (self.selected - 1) % n
        elif inp.menu_down:
            self.selected = (self.selected + 1) % n

        if inp.confirm and self.game is not None:
            _, action = ACTIONS[self.selected]
            if action == "back":
                from scz.station.scene import StationScene
                self.game.set_scene(StationScene())
                return
            if action == "sell_all":
                total = 0
                for t, price in MINERAL_PRICES.items():
                    qty = self.game.cargo.get(t, 0)
                    if qty:
                        total += qty * price
                        self.game.cargo[t] = 0
                if total > 0:
                    self.game.credits += total
                    self.last_sale_msg = f"sold all minerals  ·  +{total} credits"
                    self.last_sale_age = 0.0
                else:
                    self.last_sale_msg = "nothing to sell"
                    self.last_sale_age = 0.0
                return
            # Sell one mineral type
            t = ACTION_TO_TYPE[action]
            qty = self.game.cargo.get(t, 0)
            if qty <= 0:
                self.last_sale_msg = f"no {t.lower()} to sell"
                self.last_sale_age = 0.0
                return
            value = qty * MINERAL_PRICES[t]
            self.game.cargo[t] = 0
            self.game.credits += value
            self.last_sale_msg = f"sold {qty} {t.lower()}  ·  +{value} credits"
            self.last_sale_age = 0.0

    def render(self, screen: pygame.Surface) -> None:
        screen.fill((6, 8, 20))
        assert self.game is not None
        w, h = screen.get_size()
        title = self.fonts["title"].render("TRADE", True, (220, 230, 250))
        tw, _ = title.get_size()
        screen.blit(title, ((w - tw) // 2, 50))
        sub = self.fonts["small"].render(
            "Mh-Lai Station  ·  sell minerals for Council Credits",
            True,
            (160, 180, 210),
        )
        sw, _ = sub.get_size()
        screen.blit(sub, ((w - sw) // 2, 100))

        # Left column — cargo hold
        x = 100
        y = 150
        screen.blit(
            self.fonts["body"].render("CARGO HOLD", True, (200, 210, 230)),
            (x, y),
        )
        y += 30
        for t in ("COMMON", "USEFUL", "BIO", "ENERGY"):
            qty = self.game.cargo.get(t, 0)
            color = RESOURCE_VISUAL[t]["color"]
            line = f"  {t.lower():9s}  {qty:5d}     @ {MINERAL_PRICES[t]}c"
            screen.blit(
                self.fonts["body"].render(line, True, color),
                (x, y),
            )
            y += 26

        # Quest items (not sellable)
        y += 16
        screen.blit(
            self.fonts["body"].render(
                "QUEST ITEMS (not for sale)", True, (180, 160, 100)
            ),
            (x, y),
        )
        y += 26
        if not self.game.uninstalled_modules:
            screen.blit(
                self.fonts["small"].render("  (none)", True, (130, 140, 160)),
                (x, y),
            )
            y += 22
        else:
            for mod_id in self.game.uninstalled_modules:
                m = MODULES.get(mod_id)
                if m is None:
                    continue
                screen.blit(
                    self.fonts["small"].render(f"  · {m.name}", True, (200, 200, 220)),
                    (x, y),
                )
                y += 22

        # Right column — credits + actions
        rx = w - 580
        ry = 150
        screen.blit(
            self.fonts["body"].render("COUNCIL CREDITS", True, (200, 210, 230)),
            (rx, ry),
        )
        ry += 30
        screen.blit(
            self.fonts["title"].render(
                f"  {self.game.credits} c", True, (220, 230, 180)
            ),
            (rx, ry),
        )
        ry += 50

        # Actions menu
        screen.blit(
            self.fonts["body"].render("ACTIONS", True, (200, 210, 230)),
            (rx, ry),
        )
        ry += 30
        for idx, (label, _) in enumerate(ACTIONS):
            is_selected = idx == self.selected
            color = (255, 240, 180) if is_selected else (180, 190, 210)
            marker = "►" if is_selected else " "
            screen.blit(
                self.fonts["menu"].render(f" {marker}  {label}", True, color),
                (rx, ry),
            )
            ry += 32

        # Last sale message (floater)
        if self.last_sale_msg:
            alpha = max(0, 255 - int(self.last_sale_age / 2.5 * 255))
            msg = self.fonts["body"].render(self.last_sale_msg, True, (180, 240, 200))
            msg.set_alpha(alpha)
            mw, _ = msg.get_size()
            screen.blit(msg, ((w - mw) // 2, h - 100))

        # Controls hint
        hint = self.fonts["small"].render(
            "Up/Down  ·  A confirm  ·  B back to Station",
            True,
            (130, 150, 180),
        )
        hw, _ = hint.get_size()
        screen.blit(hint, ((w - hw) // 2, h - 40))
