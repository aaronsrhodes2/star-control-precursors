"""CouncilScene — Furling Council deliberation chamber at Mh-Lai.

Two-track interaction:

1. **MISSIONS** (left column): the Council *assigns* the Steward work.
   Each mission has a status (AVAILABLE / ACTIVE / COMPLETED) that
   updates as the Steward accepts briefings and completes quests in
   the field. Selecting a mission opens its briefing in the detail
   pane; A on an AVAILABLE mission accepts the assignment.

2. **RECOMMENDATIONS** (right column): the Council formalises *the
   Steward's* decisions on open species questions. Selecting a
   recommendation shows its options; A on an option commits the
   choice (sets terminal-status flags + shifts faction standings).

Faction-standing strip at the top, six factions with current scores.

Standard nav:
- Up/Down: scroll within focused column
- Left/Right: switch focus between MISSIONS and RECOMMENDATIONS columns
- A: select / accept / commit (context-dependent)
- B: return to Station

See `references/lore/factions-and-war.md` for faction canon,
`src/scz/content/council_recommendations.py` for the recommendation
registry, and `src/scz/content/council_missions.py` for missions.
"""

from __future__ import annotations

from typing import Literal

import pygame

from scz.content.council_missions import (
    STATUS_ACTIVE,
    STATUS_AVAILABLE,
    STATUS_COLORS as MISSION_STATUS_COLORS,
    STATUS_COMPLETED,
    CouncilMission,
    accept_mission,
    mission_status,
    visible_missions,
)
from scz.content.council_recommendations import (
    FACTION_LABELS,
    FACTIONS,
    CouncilOption,
    CouncilRecommendation,
    faction_standing,
    open_recommendations,
)
from scz.engine.scene import Scene


# Focus modes — drives input routing and column-highlight rendering.
# - "missions" / "recommendations": at the list level, cursor moves
#   within the focused column; A acts on the current item.
# - "rec_options": after selecting a recommendation, the detail pane's
#   option list takes focus; cursor moves through options; A commits.
Focus = Literal["missions", "recommendations", "rec_options"]


class CouncilScene(Scene):
    """Furling Council deliberation chamber."""

    def __init__(self) -> None:
        super().__init__()
        self.focus: Focus = "missions"
        self.mission_idx: int = 0
        self.rec_idx: int = 0
        self.opt_idx: int = 0
        # Cached open lists (rebuilt each on_enter / after a commit)
        self._missions: list[CouncilMission] = []
        self._recs: list[CouncilRecommendation] = []
        # Transient message (mission-accepted, recommendation-committed)
        # held briefly in the detail pane footer.
        self.last_outcome: str = ""
        self.last_outcome_age: float = 0.0
        self.fonts: dict[str, pygame.font.Font] = {}

    def on_enter(self) -> None:
        self.fonts["title"] = pygame.font.SysFont("consolas", 32, bold=True)
        self.fonts["subtitle"] = pygame.font.SysFont("consolas", 18)
        self.fonts["section"] = pygame.font.SysFont("consolas", 22)
        self.fonts["item"] = pygame.font.SysFont("consolas", 18)
        self.fonts["detail"] = pygame.font.SysFont("consolas", 17)
        self.fonts["badge"] = pygame.font.SysFont("consolas", 13, bold=True)
        self.fonts["small"] = pygame.font.SysFont("consolas", 14)
        if self.game is not None:
            self._refresh()
            # Open on missions tab if there are any available briefings;
            # otherwise jump to recommendations.
            if not self._missions and self._recs:
                self.focus = "recommendations"

    def snapshot(self) -> dict | None:
        return None

    def update(self, dt: float, inp) -> None:  # type: ignore[no-untyped-def]
        assert self.game is not None

        if self.last_outcome:
            self.last_outcome_age += dt

        if inp.cancel:
            from scz.station.scene import StationScene
            self.game.set_scene(StationScene())
            return

        # Tab switching — only at the list level. From rec_options the
        # player must back out first (which we don't currently expose as
        # a button; B exits the whole scene, so they re-enter — fine
        # for MVP).
        if self.focus in ("missions", "recommendations"):
            if inp.menu_prev:
                self.focus = "missions" if self._missions else self.focus
            elif inp.menu_next:
                self.focus = "recommendations" if self._recs else self.focus

        if self.focus == "missions":
            self._update_missions_focus(inp)
        elif self.focus == "recommendations":
            self._update_recs_focus(inp)
        else:  # rec_options
            self._update_rec_options_focus(inp)

    # --- focus-mode update handlers -----------------------------------------

    def _update_missions_focus(self, inp) -> None:  # type: ignore[no-untyped-def]
        n = len(self._missions)
        if n == 0:
            return
        if inp.menu_up:
            self.mission_idx = (self.mission_idx - 1) % n
        elif inp.menu_down:
            self.mission_idx = (self.mission_idx + 1) % n
        if inp.confirm:
            m = self._missions[self.mission_idx]
            if mission_status(self.game, m) == STATUS_AVAILABLE:
                accept_mission(self.game, m)
                self.last_outcome = m.accept_line
                self.last_outcome_age = 0.0
                self._refresh()
                # Re-clamp index — mission is still in the list, status
                # just changed to ACTIVE
                self.mission_idx = min(self.mission_idx, len(self._missions) - 1)

    def _update_recs_focus(self, inp) -> None:  # type: ignore[no-untyped-def]
        n = len(self._recs)
        if n == 0:
            return
        if inp.menu_up:
            self.rec_idx = (self.rec_idx - 1) % n
            self.opt_idx = 0
        elif inp.menu_down:
            self.rec_idx = (self.rec_idx + 1) % n
            self.opt_idx = 0
        if inp.confirm:
            self.focus = "rec_options"
            self.opt_idx = 0

    def _update_rec_options_focus(self, inp) -> None:  # type: ignore[no-untyped-def]
        rec = self._current_rec()
        if rec is None:
            self.focus = "recommendations"
            return
        n = len(rec.options)
        if inp.menu_up:
            self.opt_idx = (self.opt_idx - 1) % n
        elif inp.menu_down:
            self.opt_idx = (self.opt_idx + 1) % n
        if inp.confirm:
            self._commit_recommendation(rec, rec.options[self.opt_idx])

    # --- state mutation -----------------------------------------------------

    def _refresh(self) -> None:
        """Rebuild missions + recommendations caches; clamp indices."""
        assert self.game is not None
        self._missions = visible_missions(self.game)
        self._recs = open_recommendations(self.game)
        if self.mission_idx >= len(self._missions):
            self.mission_idx = 0
        if self.rec_idx >= len(self._recs):
            self.rec_idx = 0
        rec = self._current_rec()
        if rec is None or self.opt_idx >= len(rec.options):
            self.opt_idx = 0

    def _current_mission(self) -> CouncilMission | None:
        if not self._missions:
            return None
        return self._missions[self.mission_idx]

    def _current_rec(self) -> CouncilRecommendation | None:
        if not self._recs:
            return None
        return self._recs[self.rec_idx]

    def _commit_recommendation(
        self, rec: CouncilRecommendation, opt: CouncilOption,
    ) -> None:
        assert self.game is not None
        custom_line = opt.side_effect(self.game)
        self.last_outcome = custom_line or opt.outcome_line
        self.last_outcome_age = 0.0
        self._refresh()
        self.focus = "recommendations"
        # If no recommendations remain, fall back to missions tab
        if not self._recs and self._missions:
            self.focus = "missions"

    # ------------------------------------------------------------------
    # Render
    # ------------------------------------------------------------------

    def render(self, screen: pygame.Surface) -> None:
        assert self.game is not None
        screen.fill((10, 8, 20))
        w, h = screen.get_size()

        title = self.fonts["title"].render(
            "FURLING COUNCIL", True, (230, 220, 250),
        )
        tw, _ = title.get_size()
        screen.blit(title, ((w - tw) // 2, 26))
        sub = self.fonts["subtitle"].render(
            "Mh-Lai Council Chamber  ·  briefings and recommendations",
            True, (180, 170, 210),
        )
        sw, _ = sub.get_size()
        screen.blit(sub, ((w - sw) // 2, 68))

        self._render_faction_strip(screen, w)

        # Two columns + detail pane
        col_w = (w - 180) // 2
        left_x = 60
        right_x = left_x + col_w + 60
        col_top = 200
        detail_y = h - 320
        detail_h = 240
        top_h = detail_y - col_top - 30

        self._render_missions_column(screen, left_x, col_top, col_w, top_h)
        self._render_recs_column(screen, right_x, col_top, col_w, top_h)
        self._render_detail_pane(screen, left_x, detail_y, w - 120, detail_h)

        # Outcome fade
        if self.last_outcome:
            alpha = max(0, 255 - int(self.last_outcome_age / 3.0 * 255))
            msg = self.fonts["detail"].render(
                self.last_outcome, True, (220, 220, 180),
            )
            msg.set_alpha(alpha)
            mw, _ = msg.get_size()
            screen.blit(msg, ((w - mw) // 2, h - 80))

        # Controls hint
        hint = self.fonts["small"].render(
            "Up/Down nav  ·  Left/Right switch column  ·  A select  ·  B back to Station",
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
                screen, (24, 22, 40), (cx, strip_y, cell_w - 8, strip_h),
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

    def _render_missions_column(
        self, screen: pygame.Surface, x: int, y: int, w: int, h: int,
    ) -> None:
        focused = self.focus == "missions"
        header_color = (230, 220, 250) if focused else (160, 150, 180)
        screen.blit(
            self.fonts["section"].render("MISSIONS", True, header_color),
            (x, y),
        )
        ry = y + 36
        if not self._missions:
            screen.blit(
                self.fonts["item"].render(
                    "No briefings on the docket.", True, (140, 140, 170),
                ),
                (x + 6, ry + 4),
            )
            return
        for idx, m in enumerate(self._missions):
            status = mission_status(self.game, m)
            is_selected = idx == self.mission_idx
            highlight = is_selected and focused
            bg = (40, 40, 80) if highlight else (18, 16, 36)
            border = (220, 220, 240) if highlight else (50, 50, 80)
            pygame.draw.rect(screen, bg, (x, ry, w, 60))
            pygame.draw.rect(screen, border, (x, ry, w, 60), 1)
            mark = "►" if highlight else " "
            label_color = (
                (230, 220, 240) if highlight else
                (210, 200, 230) if is_selected else
                (170, 170, 200)
            )
            # Title (truncate if too long for the column)
            title_text = m.title
            if self.fonts["item"].size(title_text)[0] > w - 28:
                while (
                    title_text and
                    self.fonts["item"].size(title_text + "...")[0] > w - 28
                ):
                    title_text = title_text[:-1]
                title_text = title_text + "..."
            screen.blit(
                self.fonts["item"].render(
                    f"{mark}  {title_text}", True, label_color,
                ),
                (x + 10, ry + 8),
            )
            # Status badge — small pill at lower-right of the row
            status_color = MISSION_STATUS_COLORS.get(status, (170, 170, 200))
            badge_w = 96
            badge_x = x + w - badge_w - 10
            badge_y = ry + 32
            badge_h = 20
            pygame.draw.rect(
                screen, (8, 8, 14), (badge_x, badge_y, badge_w, badge_h),
            )
            pygame.draw.rect(
                screen, status_color,
                (badge_x, badge_y, badge_w, badge_h), 1,
            )
            badge_text = self.fonts["badge"].render(
                status, True, status_color,
            )
            btw, bth = badge_text.get_size()
            screen.blit(
                badge_text,
                (badge_x + (badge_w - btw) // 2,
                 badge_y + (badge_h - bth) // 2),
            )
            # Objective line — small, dim, left-of-badge
            obj_color = (
                (180, 175, 200) if is_selected else (140, 140, 165)
            )
            obj_text = m.objective
            obj_max = w - 28 - badge_w - 14
            if self.fonts["small"].size(obj_text)[0] > obj_max:
                while (
                    obj_text and
                    self.fonts["small"].size(obj_text + "...")[0] > obj_max
                ):
                    obj_text = obj_text[:-1]
                obj_text = obj_text + "..."
            screen.blit(
                self.fonts["small"].render(obj_text, True, obj_color),
                (x + 16, ry + 36),
            )
            ry += 66

    def _render_recs_column(
        self, screen: pygame.Surface, x: int, y: int, w: int, h: int,
    ) -> None:
        focused = self.focus in ("recommendations", "rec_options")
        header_color = (230, 220, 250) if focused else (160, 150, 180)
        screen.blit(
            self.fonts["section"].render("RECOMMENDATIONS", True, header_color),
            (x, y),
        )
        ry = y + 36
        if not self._recs:
            screen.blit(
                self.fonts["item"].render(
                    "No recommendations pending.", True, (140, 140, 170),
                ),
                (x + 6, ry + 4),
            )
            return
        for idx, rec in enumerate(self._recs):
            is_selected = idx == self.rec_idx
            highlight = (
                is_selected and self.focus in ("recommendations", "rec_options")
            )
            bg = (40, 40, 80) if highlight else (18, 16, 36)
            border = (220, 220, 240) if highlight else (50, 50, 80)
            pygame.draw.rect(screen, bg, (x, ry, w, 50))
            pygame.draw.rect(screen, border, (x, ry, w, 50), 1)
            mark = "►" if highlight else " "
            label_color = (
                (230, 220, 240) if highlight else
                (210, 200, 230) if is_selected else
                (170, 170, 200)
            )
            title_text = rec.title
            if self.fonts["item"].size(title_text)[0] > w - 28:
                while (
                    title_text and
                    self.fonts["item"].size(title_text + "...")[0] > w - 28
                ):
                    title_text = title_text[:-1]
                title_text = title_text + "..."
            screen.blit(
                self.fonts["item"].render(
                    f"{mark}  {title_text}", True, label_color,
                ),
                (x + 10, ry + 14),
            )
            if rec.read_only:
                screen.blit(
                    self.fonts["small"].render(
                        "  (read-only — already decided)",
                        True, (140, 140, 170),
                    ),
                    (x + 16, ry + 34),
                )
            ry += 56

    def _render_detail_pane(
        self, screen: pygame.Surface, x: int, y: int, w: int, h: int,
    ) -> None:
        """Bottom-of-screen detail pane. Content varies by focus:
        - missions: selected mission's briefing + objective
        - recommendations: selected rec's context
        - rec_options: selected option's summary
        """
        pygame.draw.rect(screen, (16, 14, 28), (x, y, w, h))
        pygame.draw.rect(screen, (60, 60, 90), (x, y, w, h), 1)

        text_x = x + 16
        text_y = y + 12
        max_w = w - 32

        if self.focus == "missions":
            m = self._current_mission()
            if m is None:
                return
            status = mission_status(self.game, m)
            header = self.fonts["section"].render(
                m.title, True, (230, 220, 240),
            )
            screen.blit(header, (text_x, text_y))
            text_y += 32
            # Status-specific subline
            status_label = {
                STATUS_AVAILABLE: "NEW BRIEFING — Press A to accept",
                STATUS_ACTIVE:    "ACTIVE — Steward in field",
                STATUS_COMPLETED: "COMPLETED — closed by the Council",
            }.get(status, status)
            status_color = MISSION_STATUS_COLORS.get(status, (170, 170, 200))
            screen.blit(
                self.fonts["small"].render(status_label, True, status_color),
                (text_x, text_y),
            )
            text_y += 24
            # Either the completion line (if done) or the briefing
            body = (
                m.completion_line if status == STATUS_COMPLETED
                else m.briefing
            )
            self._blit_wrapped(
                screen, body, self.fonts["detail"],
                text_x, text_y, max_w, (200, 200, 220),
                max_height=h - (text_y - y) - 20,
            )
        elif self.focus == "rec_options":
            rec = self._current_rec()
            if rec is None:
                return
            opt = rec.options[self.opt_idx]
            header = self.fonts["section"].render(
                opt.label, True, (230, 220, 200),
            )
            screen.blit(header, (text_x, text_y))
            text_y += 32
            screen.blit(
                self.fonts["small"].render(
                    "Press A to commit this recommendation.",
                    True, (170, 170, 200),
                ),
                (text_x, text_y),
            )
            text_y += 24
            self._blit_wrapped(
                screen, opt.summary, self.fonts["detail"],
                text_x, text_y, max_w, (200, 200, 220),
                max_height=h - (text_y - y) - 20,
            )
        else:  # recommendations
            rec = self._current_rec()
            if rec is None:
                return
            header = self.fonts["section"].render(
                rec.title, True, (220, 210, 240),
            )
            screen.blit(header, (text_x, text_y))
            text_y += 32
            screen.blit(
                self.fonts["small"].render(
                    "Press A to view options.",
                    True, (170, 170, 200),
                ),
                (text_x, text_y),
            )
            text_y += 24
            self._blit_wrapped(
                screen, rec.context, self.fonts["detail"],
                text_x, text_y, max_w, (190, 195, 220),
                max_height=h - (text_y - y) - 20,
            )

    def _blit_wrapped(
        self, screen: pygame.Surface, text: str, font: pygame.font.Font,
        x: int, y: int, max_w: int, color: tuple[int, int, int],
        max_height: int = 999,
    ) -> None:
        """Word-wrap a paragraph into the detail pane, preserving \\n
        paragraph breaks.
        """
        line_h = font.get_linesize()
        cy = y
        for paragraph in text.split("\n"):
            if not paragraph.strip():
                cy += line_h // 2
                if cy - y > max_height:
                    return
                continue
            words = paragraph.split(" ")
            line: list[str] = []
            for word in words:
                test = " ".join(line + [word])
                if font.size(test)[0] <= max_w:
                    line.append(word)
                else:
                    if line:
                        screen.blit(
                            font.render(" ".join(line), True, color), (x, cy),
                        )
                        cy += line_h
                        if cy - y > max_height:
                            return
                    line = [word]
            if line:
                screen.blit(
                    font.render(" ".join(line), True, color), (x, cy),
                )
                cy += line_h
                if cy - y > max_height:
                    return
