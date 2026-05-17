"""Hyperspace star-name search overlay.

The player presses `/` to open a text-input modal at the top of the
hyperspace view. They type any partial name (e.g. "Sol", "Procy",
"Beta C"), the overlay matches against `Starmap.stars[*].cluster_name`
(case-insensitive substring), and the best match is highlighted.

On Enter, the camera pans to the matched star and fires a pulse
animation; the overlay closes. On Esc, the overlay closes without
moving.

Search is dirty-substring + lore-name priority (a "MELNORME_PROTO"
defined_name match beats a "Mel..." cluster prefix). Cheap enough to
run on every keystroke against ~500 stars.

This module is UI-only — it doesn't touch the camera directly. The
caller (HyperspaceScene) reads `pending_target` after each update and
pans toward it if non-None, then clears it.
"""

from __future__ import annotations

import pygame


SEARCH_PANEL_HEIGHT = 92
SEARCH_PANEL_MARGIN = 24
SEARCH_PANEL_BG = (10, 12, 30, 220)
SEARCH_PANEL_BORDER = (140, 200, 255)
SEARCH_TEXT_COLOR = (235, 240, 250)
SEARCH_HINT_COLOR = (140, 160, 200)
SEARCH_MATCH_COLOR = (255, 230, 140)


class SearchOverlay:
    """Modal text-input search over the starmap. Hidden by default."""

    def __init__(self, starmap) -> None:
        self.starmap = starmap
        self.visible: bool = False
        self.text: str = ""
        self.current_match: dict | None = None
        # When non-None, the caller should pan the camera here and clear it.
        self.pending_target: dict | None = None
        # Re-resolved per update so different screen sizes work
        self._panel_rect: pygame.Rect = pygame.Rect(0, 0, 0, 0)

    def open(self) -> None:
        self.visible = True
        self.text = ""
        self.current_match = None

    def close(self) -> None:
        self.visible = False
        self.text = ""
        self.current_match = None

    def update_events(self, events: list[pygame.event.Event]) -> bool:
        """Handle the search overlay's keyboard events. Returns True if the
        overlay consumed input (so the parent scene should skip its own
        keypress handling this frame)."""
        if not self.visible:
            return False
        for ev in events:
            if ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_ESCAPE:
                    self.close()
                    return True
                if ev.key == pygame.K_RETURN:
                    if self.current_match is not None:
                        self.pending_target = self.current_match
                    self.close()
                    return True
                if ev.key == pygame.K_BACKSPACE:
                    self.text = self.text[:-1]
                    self._recompute_match()
                    return True
            elif ev.type == pygame.TEXTINPUT:
                # Any printable text → append
                self.text += ev.text
                # Cap to a sane length
                if len(self.text) > 40:
                    self.text = self.text[:40]
                self._recompute_match()
                return True
        # Overlay consumes ALL keyboard while open even if no event matched
        # (so the player doesn't accidentally move their ship while typing).
        return True

    def _recompute_match(self) -> None:
        if not self.text:
            self.current_match = None
            return
        self.current_match = self._best_match(self.text)

    def _best_match(self, query: str) -> dict | None:
        """Score every star against the query; return the best."""
        q = query.strip().lower()
        if not q:
            return None
        best: dict | None = None
        best_score = -1
        for star in self.starmap.stars:
            cluster = (star.get("cluster_name") or "").lower()
            defined = (star.get("defined_name") or "").lower()
            score = 0
            # Exact cluster name = strongest
            if cluster == q:
                score = 1000
            # Cluster startswith query
            elif cluster.startswith(q):
                score = 500 + (40 - min(40, len(cluster)))
            # Cluster contains query
            elif q in cluster:
                score = 300 + (40 - min(40, len(cluster)))
            # Defined-name match (lore tag like "SOL_PROTO" still finds "sol")
            if defined:
                if q == defined:
                    score = max(score, 950)
                elif defined.startswith(q):
                    score = max(score, 480)
                elif q in defined:
                    score = max(score, 280)
            if score > best_score:
                best_score = score
                best = star
        # Don't return a match we don't actually trust
        return best if best_score > 0 else None

    def render(self, surface: pygame.Surface, font: pygame.font.Font) -> None:
        if not self.visible:
            return
        sw, sh = surface.get_size()
        panel_w = sw - 2 * SEARCH_PANEL_MARGIN
        self._panel_rect = pygame.Rect(
            SEARCH_PANEL_MARGIN, SEARCH_PANEL_MARGIN,
            panel_w, SEARCH_PANEL_HEIGHT,
        )

        # Panel background
        panel = pygame.Surface(self._panel_rect.size, pygame.SRCALPHA)
        panel.fill(SEARCH_PANEL_BG)
        surface.blit(panel, self._panel_rect.topleft)
        pygame.draw.rect(surface, SEARCH_PANEL_BORDER, self._panel_rect, 2)

        # Hint
        hint = font.render(
            "Find star  (Enter = jump, Esc = cancel)", True, SEARCH_HINT_COLOR
        )
        surface.blit(
            hint, (self._panel_rect.x + 18, self._panel_rect.y + 10),
        )

        # Text input with caret
        prompt = f"/ {self.text}_"
        text_surf = font.render(prompt, True, SEARCH_TEXT_COLOR)
        surface.blit(
            text_surf, (self._panel_rect.x + 18, self._panel_rect.y + 36),
        )

        # Current match preview
        match = self.current_match
        if match is not None:
            name = match.get("cluster_name", "?")
            defined = match.get("defined_name")
            if defined and not defined.endswith("_PROTO"):
                detail = f"  → {name}  [{defined}]"
            elif defined:
                detail = f"  → {name}  ({defined})"
            else:
                detail = f"  → {name}"
            match_surf = font.render(detail, True, SEARCH_MATCH_COLOR)
            surface.blit(
                match_surf,
                (self._panel_rect.x + 18 + text_surf.get_width() + 12,
                 self._panel_rect.y + 36),
            )
