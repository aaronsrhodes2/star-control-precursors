"""ShipCustomizationScene — install/uninstall ship modules.

Two-column layout: ship slot state (left) + available modules (right).
A focused column highlights its selection; left/right switches focus.
A confirms (install or uninstall the highlighted thing). B exits.

Per the design in `references/lore/station-screens-design.md`.
"""

from __future__ import annotations

from typing import Literal

import pygame

from scz.content.modules import (
    MODULES,
    Module,
    SLOTS,
    crew_slot_compatible,
    purchasable_modules,
)
from scz.engine.scene import Scene


Focus = Literal["slots", "modules"]


class ShipCustomizationScene(Scene):
    """Module install/uninstall UX."""

    # Furling Mh-Lai theme carries through the shipyard.
    music_context: str | None = "furling_home"

    def __init__(self) -> None:
        super().__init__()
        self.focus: Focus = "slots"
        self.slot_idx: int = 0
        self.module_idx: int = 0
        self.last_msg: str = ""
        self.last_msg_age: float = 0.0

        # Set in on_enter
        self.fonts: dict[str, pygame.font.Font] = {}

    def on_enter(self) -> None:
        self.fonts["title"] = pygame.font.SysFont("consolas", 32, bold=True)
        self.fonts["body"] = pygame.font.SysFont("consolas", 18)
        self.fonts["small"] = pygame.font.SysFont("consolas", 14)
        self.fonts["menu"] = pygame.font.SysFont("consolas", 20)

    def snapshot(self) -> dict | None:
        return None

    def update(self, dt: float, inp) -> None:  # type: ignore[no-untyped-def]
        assert self.game is not None
        if self.last_msg:
            self.last_msg_age += dt
            if self.last_msg_age > 3.0:
                self.last_msg = ""

        def _click(kind: str = "select") -> None:
            if hasattr(self.game, "sfx"):
                self.game.sfx.play(f"ui/menu_{kind}")

        if inp.cancel:
            _click("cancel")
            from scz.station.scene import StationScene
            self.game.set_scene(StationScene())
            return

        if inp.menu_prev:
            self.focus = "slots"
            _click()
        elif inp.menu_next:
            self.focus = "modules"
            _click()

        # Available modules — purchasable + uninstalled quest rewards
        avail = self._available_modules_list()

        if self.focus == "slots":
            n = len(SLOTS)
            if inp.menu_up:
                self.slot_idx = (self.slot_idx - 1) % n
                _click()
            elif inp.menu_down:
                self.slot_idx = (self.slot_idx + 1) % n
                _click()
            if inp.confirm:
                _click("confirm")
                # A on a slot uninstalls the currently-equipped module
                self._try_uninstall(SLOTS[self.slot_idx])
        else:  # modules
            n = len(avail)
            if n > 0:
                if inp.menu_up:
                    self.module_idx = (self.module_idx - 1) % n
                    _click()
                elif inp.menu_down:
                    self.module_idx = (self.module_idx + 1) % n
                    _click()
                if inp.confirm:
                    _click("confirm")
                    self._try_install(avail[self.module_idx])

    def render(self, screen: pygame.Surface) -> None:
        assert self.game is not None
        screen.fill((6, 8, 20))
        w, h = screen.get_size()

        title = self.fonts["title"].render("SHIP CUSTOMIZATION", True, (220, 230, 250))
        tw, _ = title.get_size()
        screen.blit(title, ((w - tw) // 2, 30))
        sub = self.fonts["small"].render(
            "Furling Scout  ·  install modules into slots  ·  L/R switch column",
            True,
            (160, 180, 210),
        )
        sw, _ = sub.get_size()
        screen.blit(sub, ((w - sw) // 2, 78))

        # Layout
        left_x = 80
        right_x = w - 80 - 480
        col_y = 120
        col_w_left = 460
        col_w_right = 480

        self._render_slots_column(screen, left_x, col_y, col_w_left)
        self._render_modules_column(screen, right_x, col_y, col_w_right)

        # Credits readout
        ry = h - 80
        screen.blit(
            self.fonts["body"].render(
                f"COUNCIL CREDITS  ·  {self.game.credits} c",
                True, (220, 230, 180),
            ),
            (left_x, ry),
        )

        # Last action message
        if self.last_msg:
            alpha = max(0, 255 - int(self.last_msg_age / 3.0 * 255))
            msg = self.fonts["body"].render(self.last_msg, True, (180, 240, 200))
            msg.set_alpha(alpha)
            mw, _ = msg.get_size()
            screen.blit(msg, ((w - mw) // 2, h - 110))

        # Controls hint
        hint = self.fonts["small"].render(
            "Up/Down nav  ·  Left/Right switch column  ·  A install/uninstall  ·  B back",
            True,
            (130, 150, 180),
        )
        hw, _ = hint.get_size()
        screen.blit(hint, ((w - hw) // 2, h - 40))

    # ------------------------------------------------------------------
    # Render helpers
    # ------------------------------------------------------------------

    def _render_slots_column(
        self, screen: pygame.Surface, x: int, y: int, w: int
    ) -> None:
        assert self.game is not None
        focused = self.focus == "slots"
        header_color = (220, 230, 250) if focused else (140, 150, 180)
        screen.blit(
            self.fonts["menu"].render("SHIP SLOTS", True, header_color),
            (x, y),
        )
        ry = y + 32
        for idx, slot in enumerate(SLOTS):
            is_selected = idx == self.slot_idx
            highlight = is_selected and focused
            bg = (40, 60, 100) if highlight else (16, 18, 32)
            border = (200, 220, 240) if highlight else (40, 50, 70)
            pygame.draw.rect(screen, bg, (x, ry, w, 44))
            pygame.draw.rect(screen, border, (x, ry, w, 44), 1)
            installed = self.game.ship_modules.get(slot)
            if installed:
                mod = MODULES.get(installed)
                label = mod.name if mod else installed
                module_color = (220, 230, 180)
            else:
                label = "[empty]"
                module_color = (130, 140, 160)
            mark = "►" if highlight else (" " if is_selected else " ")
            screen.blit(
                self.fonts["body"].render(
                    f"{mark}  {slot:8s}  {label}", True, module_color
                ),
                (x + 10, ry + 12),
            )
            ry += 50

    def _render_modules_column(
        self, screen: pygame.Surface, x: int, y: int, w: int
    ) -> None:
        focused = self.focus == "modules"
        header_color = (220, 230, 250) if focused else (140, 150, 180)
        screen.blit(
            self.fonts["menu"].render("AVAILABLE MODULES", True, header_color),
            (x, y),
        )
        avail = self._available_modules_list()
        ry = y + 32
        if not avail:
            screen.blit(
                self.fonts["body"].render(
                    "  (no modules available)", True, (130, 140, 160)
                ),
                (x, ry),
            )
            return
        for idx, mod in enumerate(avail):
            is_selected = idx == self.module_idx
            highlight = is_selected and focused
            bg = (40, 60, 100) if highlight else (16, 18, 32)
            border = (200, 220, 240) if highlight else (40, 50, 70)
            pygame.draw.rect(screen, bg, (x, ry, w, 44))
            pygame.draw.rect(screen, border, (x, ry, w, 44), 1)
            mark = "►" if highlight else " "
            tag = "★" if mod.tier == 0 else f"T{mod.tier}"
            cost_str = (
                f"  ({mod.cost_credits}c"
                + (
                    "  + " + ", ".join(
                        f"{q} {t.lower()}" for t, q in mod.cost_resources.items()
                    )
                    if mod.cost_resources else ""
                )
                + ")"
            ) if mod.cost_credits > 0 or mod.cost_resources else ""
            screen.blit(
                self.fonts["body"].render(
                    f"{mark} {tag}  {mod.name}{cost_str}",
                    True,
                    (220, 230, 180) if mod.tier == 0 else (200, 210, 220),
                ),
                (x + 8, ry + 12),
            )
            ry += 50

    # ------------------------------------------------------------------
    # Install / uninstall logic
    # ------------------------------------------------------------------

    def _available_modules_list(self) -> list[Module]:
        """All modules the player can currently install:
        - tier-0 (quest reward) modules sitting in uninstalled_modules
        - tier-1+ modules from the shop catalog (purchasable)
        """
        assert self.game is not None
        out: list[Module] = []
        # Quest rewards in inventory first
        for mod_id, count in self.game.uninstalled_modules.items():
            if count <= 0:
                continue
            m = MODULES.get(mod_id)
            if m is not None:
                out.append(m)
        # Then purchasable
        for m in purchasable_modules(self.game):
            out.append(m)
        return out

    def _try_install(self, mod: Module) -> None:
        assert self.game is not None
        # Determine target slot. Default to mod.slot; for crew, prefer
        # crew_1 then crew_2 (whichever's empty).
        if mod.slot in ("crew_1", "crew_2"):
            target = None
            for s in ("crew_1", "crew_2"):
                if self.game.ship_modules.get(s) is None:
                    target = s
                    break
            if target is None:
                self.last_msg = "no crew slots available — uninstall one first"
                self.last_msg_age = 0.0
                return
        else:
            target = mod.slot

        # If slot is occupied, refuse — player must explicitly uninstall first
        if self.game.ship_modules.get(target) is not None:
            self.last_msg = f"{target} slot is occupied — uninstall first"
            self.last_msg_age = 0.0
            return

        # If quest reward: requires count >= 1 in inventory
        if mod.tier == 0:
            if self.game.uninstalled_modules.get(mod.id, 0) <= 0:
                self.last_msg = f"{mod.name} not in inventory"
                self.last_msg_age = 0.0
                return
        else:
            # Purchasable — check credits + resources
            if self.game.credits < mod.cost_credits:
                self.last_msg = f"need {mod.cost_credits}c, have {self.game.credits}"
                self.last_msg_age = 0.0
                return
            for t, q in mod.cost_resources.items():
                if self.game.cargo.get(t, 0) < q:
                    self.last_msg = (
                        f"need {q} {t.lower()}, have {self.game.cargo.get(t, 0)}"
                    )
                    self.last_msg_age = 0.0
                    return

        # Pay costs and install
        if mod.tier == 0:
            self.game.uninstalled_modules[mod.id] -= 1
            if self.game.uninstalled_modules[mod.id] <= 0:
                del self.game.uninstalled_modules[mod.id]
        else:
            self.game.credits -= mod.cost_credits
            for t, q in mod.cost_resources.items():
                self.game.cargo[t] -= q

        self.game.ship_modules[target] = mod.id
        # Set a friendly flag for the slice's tutorial Beat 5 — when the
        # Scanner Mk III is installed for the first time, the in_cargo
        # flag clears and a permanent install flag latches.
        if mod.id == "scanner_mk3":
            self.game.flags["scanner_mk3_in_cargo"] = False
            self.game.flags["scanner_mk3_installed"] = True
        self.last_msg = f"installed {mod.name} → {target}"
        self.last_msg_age = 0.0

    def _try_uninstall(self, slot: str) -> None:
        assert self.game is not None
        installed_id = self.game.ship_modules.get(slot)
        if installed_id is None:
            self.last_msg = f"{slot} is already empty"
            self.last_msg_age = 0.0
            return
        # Return module to inventory
        self.game.uninstalled_modules[installed_id] = (
            self.game.uninstalled_modules.get(installed_id, 0) + 1
        )
        self.game.ship_modules[slot] = None
        # Reverse the special-case flags for Scanner Mk III
        if installed_id == "scanner_mk3":
            self.game.flags["scanner_mk3_in_cargo"] = True
            self.game.flags["scanner_mk3_installed"] = False
        mod = MODULES.get(installed_id)
        name = mod.name if mod else installed_id
        self.last_msg = f"uninstalled {name} from {slot}"
        self.last_msg_age = 0.0
