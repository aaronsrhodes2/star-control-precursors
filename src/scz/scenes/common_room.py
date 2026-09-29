"""CommonRoomScene — the Furling Scout's crew gathering spot.

Per `references/lore/crew-common-room.md`, the Common Room is the
ship's social hub. Five named-crew alcoves around a central long-table,
each occupied by the corresponding crew member when `recruited_<role>
= True`. Plus the Steward's bunk corner and a rotating-generic-crew
alcove.

MVP scope (this scene file):
- Render five alcoves at their canonical positions (port-forward,
  starboard-mid, starboard-aft, port-aft, port-forward-mid).
- For each `recruited_<role>` crew, render a placeholder portrait
  block + name at the alcove. Empty alcoves show "Unoccupied."
- Cursor navigates between alcoves (up / down cycles through the
  populated list).
- A on a focused alcove opens that crew's dialog via the appropriate
  factory in `dialog.characters`. B returns to the Station.
- Steward's bunk + central table + generic-crew alcove rendered as
  static decorations for now; interaction is deferred to a later pass
  (per the dispatch's phasing recommendation: Sprint 1 ships the
  dispatch surface; Sprints 2-3 ship bond-objects, banter, etc.).

Bond-objects, ambient banter, notification badges, narrative-mode
Bio-Archive — all deferred. They have their own backlog entries in
HANDOFF_design_chat.md.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, TYPE_CHECKING

import pygame

from scz.engine.scene import Scene

if TYPE_CHECKING:
    from scz.dialog.data import DialogCharacter
    from scz.engine.game import Game


@dataclass(frozen=True)
class MilestoneArtifact:
    """One artifact on the Steward's bunk-shelf.

    Per `references/lore/crew-common-room.md` §Steward's bunk corner:
    *"the shelf above the Steward's bunk accumulates the slice's
    milestone artifacts — the Distress Beacon recorder, the Mantle-
    Resonance Bio-Architect spare, the Rainbow Resonator (once
    acquired), etc."*

    Each artifact has a flag-gate; the bunk renders them as small
    labelled tiles as they accumulate.
    """
    label: str
    color: tuple[int, int, int]
    flag_required: str


# Canonical milestone-artifact catalog. Ordered roughly by slice
# acquisition: Distress Beacon first (Beat 4 tutorial), then quest
# rewards. Image-chat will eventually supply real artifact sprites;
# for now they render as labeled tiles on the shelf.
MILESTONE_ARTIFACTS: tuple[MilestoneArtifact, ...] = (
    MilestoneArtifact(
        label="Distress Beacon recorder",
        color=(180, 130, 200),
        flag_required="has_distress_beacon",
    ),
    MilestoneArtifact(
        label="Hyperspace-Echo Sensor",
        color=(140, 200, 220),
        flag_required="has_echo_sensor",
    ),
    MilestoneArtifact(
        label="Quasi-Space portal map",
        color=(160, 220, 200),
        flag_required="has_quasispace_portal",
    ),
    MilestoneArtifact(
        label="Slylandro Cloak blueprint",
        color=(120, 200, 230),
        flag_required="slylandro_cloaked",
    ),
    MilestoneArtifact(
        label="Mmrnmhrm Archive excerpt",
        color=(170, 180, 220),
        flag_required="has_mmrnmhrm_excerpt",
    ),
    MilestoneArtifact(
        label="Chenjesu Resonance record",
        color=(190, 170, 230),
        flag_required="has_resonance_record",
    ),
    MilestoneArtifact(
        label="Rainbow Resonator",
        color=(240, 200, 140),
        flag_required="has_rainbow_resonator",
    ),
    MilestoneArtifact(
        label="Melnorme Trade-Network sensor",
        color=(220, 130, 100),
        flag_required="melnorme_committed",
    ),
)


@dataclass(frozen=True)
class CrewAlcove:
    """One named-crew alcove in the Common Room layout.

    `recruit_flag` gates whether the crew appears (only when truthy).
    `dialog_factory` is called when the player presses A on the alcove
    — returns the DialogCharacter to dispatch into a DialogScene.
    Position is normalized (0.0..1.0) so the layout scales to any
    window size.
    """
    role: str                  # 'pilot', 'weapons_officer', etc.
    crew_name: str             # display name for the alcove header
    posture_blurb: str         # one-line summary of canonical posture
    recruit_flag: str          # game.flags key gating occupancy
    pos_norm: tuple[float, float]   # (x, y) in [0..1] within the room rect
    accent: tuple[int, int, int]    # alcove border / portrait-stub accent
    dialog_factory: Callable[[], "DialogCharacter"]


def _build_alcoves() -> tuple[CrewAlcove, ...]:
    """Construct the five named-crew alcove specs. Built lazily so the
    dialog-factory imports don't cycle at module load.
    """
    from scz.dialog.characters import (
        bren_vor_telcas,
        mira_rou_halve_tel,
        mraka_yenn_sa,
        tarven_olwen_sa,
        yelena_lwen_tar,
    )
    return (
        CrewAlcove(
            role="pilot",
            crew_name="Mraka Yenn-Sa",
            posture_blurb="at the alcove window · watching hyperspace patterns",
            recruit_flag="recruited_pilot",
            pos_norm=(0.18, 0.30),    # port-forward corner
            accent=(220, 180, 110),
            dialog_factory=mraka_yenn_sa,
        ),
        CrewAlcove(
            role="navigator",
            crew_name="Tarven Olwen-Sa",
            posture_blurb="cross-legged on the bunk · log-readers open · tea cooling",
            recruit_flag="recruited_navigator",
            pos_norm=(0.38, 0.22),    # port-forward-mid (top, slight right of Mraka)
            accent=(180, 160, 220),
            dialog_factory=tarven_olwen_sa,
        ),
        CrewAlcove(
            role="weapons_officer",
            crew_name="Bren-Vor Telcas",
            posture_blurb="seated on the bunk-edge · cleaning the same rifle component again",
            recruit_flag="recruited_weapons_officer",
            pos_norm=(0.82, 0.45),    # starboard-mid corner
            accent=(180, 190, 220),
            dialog_factory=bren_vor_telcas,
        ),
        CrewAlcove(
            role="engineer",
            crew_name="Yelena Lwen-Tar",
            posture_blurb="at her workbench · repairing something small the Steward broke",
            recruit_flag="recruited_engineer",
            pos_norm=(0.78, 0.78),    # starboard-aft corner
            accent=(220, 180, 130),
            dialog_factory=yelena_lwen_tar,
        ),
        CrewAlcove(
            role="medic",
            crew_name="Mira-Rou Halve-Tel",
            posture_blurb="at the medbay-window observation post · amphora humming on the shelf",
            recruit_flag="recruited_medic",
            pos_norm=(0.22, 0.78),    # port-aft corner
            accent=(200, 220, 200),
            dialog_factory=mira_rou_halve_tel,
        ),
    )


# Generic-crew rotating alcove — one of three shop-buyable crew modules
# can be installed in crew_2; whichever is current renders here. Per
# `crew-common-room.md` §Generic-crew rotating residents.
_GENERIC_CREW_BY_MODULE_ID: dict[str, tuple[str, str]] = {
    # module_id → (display name, tool description)
    "crew_archivist": (
        "Crew Archivist",
        "portable Council-logger at the bunk",
    ),
    "crew_warden": (
        "Crew Warden",
        "Defender-training weights-rack at the bunk",
    ),
    "crew_tunneler": (
        "Crew Tunneler",
        "Quasi-Space portal-pattern oscilloscope at the bunk",
    ),
}


# Interactive cursor target — either a named-crew alcove (alcove_idx
# points into _alcoves) or the Steward's bunk (alcove_idx = None).
# Generic-crew alcove renders but is NOT in the cursor cycle per the
# lore doc: "Generic crew aren't deep dialog NPCs."
class _Target:
    __slots__ = ("kind", "alcove_idx")

    def __init__(self, kind: str, alcove_idx: int | None = None) -> None:
        self.kind = kind          # "alcove" | "bunk"
        self.alcove_idx = alcove_idx


class CommonRoomScene(Scene):
    """The Furling Scout's crew gathering room."""

    def __init__(self) -> None:
        super().__init__()
        self._alcoves: tuple[CrewAlcove, ...] = ()
        # Cursor is an index into `_targets` (alcoves currently
        # populated, plus the Steward's bunk at the end). Cycling
        # through means tabbing between people-to-talk-to and the
        # bunk's bio-archive review.
        self.cursor: int = 0
        self._targets: list[_Target] = []
        self.fonts: dict[str, pygame.font.Font] = {}

    def on_enter(self) -> None:
        self.fonts["title"] = pygame.font.SysFont("consolas", 30, bold=True)
        self.fonts["subtitle"] = pygame.font.SysFont("consolas", 16)
        self.fonts["alcove"] = pygame.font.SysFont("consolas", 17, bold=True)
        self.fonts["posture"] = pygame.font.SysFont("consolas", 13)
        self.fonts["bond"] = pygame.font.SysFont("consolas", 11)
        self.fonts["prompt"] = pygame.font.SysFont("consolas", 18, bold=True)
        self.fonts["badge"] = pygame.font.SysFont("consolas", 18, bold=True)
        self.fonts["small"] = pygame.font.SysFont("consolas", 14)
        self._alcoves = _build_alcoves()
        self._rebuild_targets()
        # Snap cursor to the first crew alcove (or bunk if no crew)
        self.cursor = 0

    def snapshot(self) -> dict | None:
        return None

    def update(self, dt: float, inp) -> None:  # type: ignore[no-untyped-def]
        assert self.game is not None
        if inp.cancel:
            from scz.station.scene import StationScene
            self.game.set_scene(StationScene())
            return

        # Rebuild targets each tick — cheap, lets newly-recruited crew
        # appear immediately if their flag flips between frames.
        self._rebuild_targets()
        if not self._targets:
            return

        if inp.menu_up or inp.menu_prev:
            self.cursor = (self.cursor - 1) % len(self._targets)
        elif inp.menu_down or inp.menu_next:
            self.cursor = (self.cursor + 1) % len(self._targets)
        if inp.confirm:
            self._activate_target()

    def _rebuild_targets(self) -> None:
        """Populate the cursor cycle: each recruited crew alcove plus
        the Steward's bunk. Generic-crew alcove is rendered but not
        in the cycle (per lore doc — generic crew aren't deep NPCs).
        """
        if self.game is None:
            self._targets = []
            return
        targets: list[_Target] = []
        for i, a in enumerate(self._alcoves):
            if self.game.flags.get(a.recruit_flag):
                targets.append(_Target("alcove", i))
        # Bunk is always interactive (the Steward is always aboard).
        targets.append(_Target("bunk"))
        self._targets = targets
        if self.cursor >= len(self._targets):
            self.cursor = 0

    def _activate_target(self) -> None:
        if self.game is None or not self._targets:
            return
        t = self._targets[self.cursor]
        if t.kind == "alcove" and t.alcove_idx is not None:
            self._open_crew_dialog(t.alcove_idx)
        elif t.kind == "bunk":
            self._open_bunk()

    def _open_crew_dialog(self, alcove_idx: int) -> None:
        if self.game is None:
            return
        if 0 <= alcove_idx < len(self._alcoves):
            alcove = self._alcoves[alcove_idx]
            if not self.game.flags.get(alcove.recruit_flag):
                return
            from scz.dialog.scene import DialogScene
            self.game.set_scene(
                DialogScene(
                    character=alcove.dialog_factory(),
                    parent_factory=lambda: CommonRoomScene(),
                )
            )

    def _open_bunk(self) -> None:
        """Steward's bunk action — opens the Bio-Archive for a
        narrative-mode review. The dispatch specifies the bunk should
        use a `narrative_mode=True` variant of BioArchiveScene; for MVP
        we open the standard archive (the styling variant is a
        deferred polish pass).
        """
        if self.game is None:
            return
        from scz.station.archive import BioArchiveScene
        self.game.set_scene(BioArchiveScene())

    # ------------------------------------------------------------------
    # Render
    # ------------------------------------------------------------------

    def render(self, screen: pygame.Surface) -> None:
        assert self.game is not None
        w, h = screen.get_size()

        # Post-fall mood shift — Mh-Lai memorial sigils on the walls,
        # the Common Room subtitle reads in a quieter register. Per
        # `the-fall-of-mh-lai.md` §Beat 5 Aftermath + the
        # crew-common-room.md mood-shift hook.
        post_fall = bool(self.game.flags.get("mhlai_destroyed"))

        # Fur-aesthetic backdrop — warm amber-tinted dark room. Per
        # crew-common-room.md "Furling fur aesthetic" canon. Image-chat
        # will eventually supply a real backdrop image; for now,
        # procedural warm-amber gradient. Post-fall the gradient cools
        # toward grey-violet to signal the mood shift.
        self._render_backdrop(screen, w, h, post_fall=post_fall)

        # Title bar
        title_color = (
            (210, 200, 200) if post_fall else (240, 220, 180)
        )
        title = self.fonts["title"].render(
            "CREW COMMON ROOM", True, title_color,
        )
        tw, _ = title.get_size()
        screen.blit(title, ((w - tw) // 2, 20))
        sub_text = (
            "Furling Scout · post-fall · the bond-objects are heavier now"
            if post_fall
            else "Furling Scout · fur-lined interior · the spaces that hold us gently"
        )
        sub = self.fonts["subtitle"].render(
            sub_text,
            True, (200, 180, 150),
        )
        sw, _ = sub.get_size()
        screen.blit(sub, ((w - sw) // 2, 56))

        # Room rect — central area where alcoves are positioned.
        # Bottom 90px reserved for the focused-item detail strip +
        # controls hint.
        margin_x = 80
        margin_y = 100
        room_rect = pygame.Rect(
            margin_x, margin_y, w - 2 * margin_x, h - margin_y - 130,
        )
        pygame.draw.rect(screen, (50, 36, 20), room_rect, 1)

        # Central long-table — decorative for now
        self._render_central_table(screen, room_rect)

        # Steward's bunk — central-aft, interactive (cursor can land here)
        bunk_focused = (
            len(self._targets) > 0
            and self._targets[self.cursor].kind == "bunk"
        )
        self._render_stewards_bunk(screen, room_rect, bunk_focused)

        # Generic-crew rotating alcove — render when crew_2 is one of
        # the shop-buyable generics (Archivist / Warden / Tunneler).
        self._render_generic_alcove(screen, room_rect)

        # Alcoves — five named-crew positions. Compute populated set +
        # which alcove the cursor is currently on (if any).
        populated_alcove_idx = {
            t.alcove_idx for t in self._targets
            if t.kind == "alcove" and t.alcove_idx is not None
        }
        cursor_alcove_idx: int | None = None
        if (
            self._targets and
            self._targets[self.cursor].kind == "alcove"
        ):
            cursor_alcove_idx = self._targets[self.cursor].alcove_idx
        for idx, alcove in enumerate(self._alcoves):
            self._render_alcove(
                screen, room_rect, alcove,
                occupied=(idx in populated_alcove_idx),
                focused=(idx == cursor_alcove_idx),
            )

        # Focused-item detail strip — shows the full posture / bond-
        # objects / goalpost note for whatever the cursor is on, since
        # the alcove tiles are too small for the full text.
        self._render_focused_detail(screen, w, h)

        # Footer controls hint
        has_crew = any(
            t.kind == "alcove" for t in self._targets
        )
        if has_crew:
            hint = self.fonts["small"].render(
                "Up/Down switch focus  ·  A interact  ·  B back to Station",
                True, (160, 150, 130),
            )
        else:
            hint = self.fonts["small"].render(
                "No crew aboard yet — recruit at Mh-Lai to populate the room.  "
                "·  A on the bunk reviews the Bio-Archive  ·  B back",
                True, (160, 150, 130),
            )
        hw, _ = hint.get_size()
        screen.blit(hint, ((w - hw) // 2, h - 24))

    def _render_focused_detail(
        self, screen: pygame.Surface, w: int, h: int,
    ) -> None:
        """Render the focused-item detail strip near the bottom of the
        screen. Crew alcove → full posture + bond-object full labels +
        goalpost hint. Bunk → milestone-artifact tally.
        """
        if self.game is None or not self._targets:
            return
        target = self._targets[self.cursor]
        strip_y = h - 100
        strip_h = 70
        strip_rect = pygame.Rect(60, strip_y, w - 120, strip_h)
        pygame.draw.rect(screen, (18, 14, 24), strip_rect)
        pygame.draw.rect(screen, (80, 70, 100), strip_rect, 1)

        text_x = strip_rect.left + 14
        if target.kind == "alcove" and target.alcove_idx is not None:
            alcove = self._alcoves[target.alcove_idx]
            # Header — name in accent color
            header = self.fonts["alcove"].render(
                alcove.crew_name, True, alcove.accent,
            )
            screen.blit(header, (text_x, strip_rect.top + 6))
            # Posture below
            posture = self.fonts["small"].render(
                alcove.posture_blurb, True, (190, 175, 200),
            )
            screen.blit(posture, (text_x, strip_rect.top + 28))
            # Bond-objects — listed in compact form on the right
            from scz.content.crew_bond_objects import (
                goalpost_notification_visible, visible_bond_objects,
            )
            objs = visible_bond_objects(self.game, alcove.role)
            if objs:
                bond_summary = " · ".join(o.label for o in objs)
                # Truncate if too long
                max_bond_w = strip_rect.width - 28
                while (
                    bond_summary and
                    self.fonts["small"].size(bond_summary)[0] > max_bond_w
                ):
                    bond_summary = bond_summary[:-1]
                if bond_summary != " · ".join(o.label for o in objs):
                    bond_summary = bond_summary[:-3] + "..."
                screen.blit(
                    self.fonts["small"].render(
                        f"shelf: {bond_summary}",
                        True, (150, 140, 170),
                    ),
                    (text_x, strip_rect.top + 48),
                )
            # Goalpost notification text in the upper-right
            if goalpost_notification_visible(self.game, alcove.role):
                import math as _math
                ticks = pygame.time.get_ticks()
                pulse = (_math.sin(ticks / 240) + 1) / 2
                note_color = (
                    int(220 + pulse * 35),
                    int(180 + pulse * 50),
                    int(120 + pulse * 50),
                )
                note = self.fonts["small"].render(
                    "! side-quest ready",
                    True, note_color,
                )
                nw, _ = note.get_size()
                screen.blit(
                    note,
                    (strip_rect.right - nw - 14, strip_rect.top + 8),
                )
        elif target.kind == "bunk":
            header = self.fonts["alcove"].render(
                "Steward's bunk", True, (240, 220, 180),
            )
            screen.blit(header, (text_x, strip_rect.top + 6))
            screen.blit(
                self.fonts["small"].render(
                    "review the Bio-Archive in narrative format",
                    True, (190, 175, 160),
                ),
                (text_x, strip_rect.top + 28),
            )
            # Milestone-artifact tally
            visible_arts = [
                a for a in MILESTONE_ARTIFACTS
                if self.game.flags.get(a.flag_required)
            ]
            tally_text = (
                f"shelf: {len(visible_arts)} milestone artifact"
                + ("s" if len(visible_arts) != 1 else "")
                + (" accumulated" if visible_arts else " (none yet)")
            )
            screen.blit(
                self.fonts["small"].render(
                    tally_text, True, (150, 140, 170),
                ),
                (text_x, strip_rect.top + 48),
            )

    def _render_backdrop(
        self, screen: pygame.Surface, w: int, h: int,
        post_fall: bool = False,
    ) -> None:
        """Warm amber-tinted dark room — placeholder for the Image-chat
        backdrop. Subtle horizontal gradient so the room reads as
        *interior* not flat-color void.

        Post-fall, the gradient cools toward grey-violet — the
        canonical mood shift per `the-fall-of-mh-lai.md` Beat 5.
        """
        for y in range(h):
            t = y / max(1, h)
            if post_fall:
                # Cool grey-violet — quieter, post-grief
                r = int(20 + (14 - 8) * t)
                g = int(18 + (12 - 7) * t)
                b = int(24 + (16 - 8) * t)
            else:
                # Warm amber — pre-fall fur aesthetic
                r = int(28 + (16 - 8) * t)
                g = int(20 + (12 - 6) * t)
                b = int(14 + (8 - 4) * t)
            pygame.draw.line(screen, (r, g, b), (0, y), (w, y))

    def _render_central_table(
        self, screen: pygame.Surface, room_rect: pygame.Rect,
    ) -> None:
        cx = room_rect.centerx
        cy = room_rect.centery
        # Long rectangular table — wider on x, shorter on y
        tw = int(room_rect.width * 0.25)
        th = int(room_rect.height * 0.20)
        table_rect = pygame.Rect(cx - tw // 2, cy - th // 2, tw, th)
        pygame.draw.rect(screen, (60, 40, 22), table_rect)
        pygame.draw.rect(screen, (110, 80, 50), table_rect, 1)
        label = self.fonts["small"].render(
            "central long-table", True, (160, 130, 100),
        )
        lw, _ = label.get_size()
        screen.blit(label, (cx - lw // 2, cy - 8))

    def _render_stewards_bunk(
        self, screen: pygame.Surface, room_rect: pygame.Rect,
        focused: bool,
    ) -> None:
        """Steward's bunk + milestone-artifact shelf. The shelf
        accumulates canonical artifacts as the slice progresses; each
        renders as a labelled tile gated by its flag.
        """
        # Central-aft, between Yelena and Mira-Rou alcoves
        cx = room_rect.centerx
        by = room_rect.bottom - 40
        bw = 320
        bh = 56
        bunk_rect = pygame.Rect(cx - bw // 2, by - bh, bw, bh)
        bg = (50, 36, 22) if focused else (32, 24, 14)
        border = (240, 220, 180) if focused else (90, 70, 45)
        border_w = 2 if focused else 1
        pygame.draw.rect(screen, bg, bunk_rect)
        pygame.draw.rect(screen, border, bunk_rect, border_w)
        label_color = (
            (240, 220, 180) if focused else (160, 140, 110)
        )
        label = self.fonts["alcove"].render(
            "Steward's bunk", True, label_color,
        )
        lw, _ = label.get_size()
        screen.blit(label, (cx - lw // 2, by - bh + 6))
        sub = self.fonts["small"].render(
            "review Bio-Archive  ·  the slice's milestone artifacts",
            True, (150, 130, 100),
        )
        sw, _ = sub.get_size()
        screen.blit(sub, (cx - sw // 2, by - bh + 30))

        # Milestone-artifact shelf above the bunk — accumulates as
        # canonical artifacts come into the Steward's possession.
        # Renders only when at least one is owned; lays out tiles
        # left-to-right above the bunk box.
        if self.game is None:
            visible_artifacts: list[MilestoneArtifact] = []
        else:
            visible_artifacts = [
                a for a in MILESTONE_ARTIFACTS
                if self.game.flags.get(a.flag_required)
            ]
        if visible_artifacts:
            shelf_h = 32
            shelf_y = bunk_rect.top - shelf_h - 6
            shelf_rect = pygame.Rect(
                bunk_rect.left, shelf_y, bunk_rect.width, shelf_h,
            )
            pygame.draw.rect(screen, (18, 14, 10), shelf_rect)
            pygame.draw.rect(screen, (80, 64, 44), shelf_rect, 1)
            tile_pad = 4
            tx = shelf_rect.left + 4
            for art in visible_artifacts:
                # Compute tile width from label length, capped.
                label_w = self.fonts["bond"].size(art.label)[0]
                tile_w = min(max(60, label_w + 10), 120)
                if tx + tile_w > shelf_rect.right - 4:
                    break
                tile_rect = pygame.Rect(
                    tx, shelf_rect.top + 3, tile_w, shelf_h - 6,
                )
                pygame.draw.rect(screen, art.color, tile_rect)
                pygame.draw.rect(
                    screen, (30, 24, 16), tile_rect, 1,
                )
                # Truncate label to fit
                truncated = art.label
                while (
                    truncated and
                    self.fonts["bond"].size(truncated)[0] > tile_w - 8
                ):
                    truncated = truncated[:-1]
                if truncated != art.label:
                    truncated = truncated[:-3] + "..."
                if truncated:
                    text_surf = self.fonts["bond"].render(
                        truncated, True, (30, 24, 16),
                    )
                    tsw, tsh = text_surf.get_size()
                    screen.blit(
                        text_surf,
                        (
                            tile_rect.left + (tile_w - tsw) // 2,
                            tile_rect.top + (tile_rect.height - tsh) // 2,
                        ),
                    )
                tx += tile_w + tile_pad

        if focused:
            import math as _math
            ticks = pygame.time.get_ticks()
            pulse = (_math.sin(ticks / 220) + 1) / 2
            prompt_color = (
                int(180 + pulse * 60),
                int(220 + pulse * 30),
                255,
            )
            prompt = self.fonts["prompt"].render(
                "[ REVIEW ]  A", True, prompt_color,
            )
            ppw, _ = prompt.get_size()
            screen.blit(prompt, (cx - ppw // 2, by + 8))

    def _render_generic_alcove(
        self, screen: pygame.Surface, room_rect: pygame.Rect,
    ) -> None:
        """Render the generic-crew rotating-alcove if a shop-buyable
        crew module (Archivist / Warden / Tunneler) is installed.
        Per the lore doc the generic crew aren't deep-dialog NPCs;
        the alcove is decorative.
        """
        if self.game is None:
            return
        # Scan all 12 generic slots for any of the three generic crew
        # modules. Picks the first found (slot-order). Post 2026-05-18
        # refactor: crew modules can sit in any slot, not just crew_2.
        installed = None
        for slot_mid in self.game.ship_modules.values():
            if slot_mid in _GENERIC_CREW_BY_MODULE_ID:
                installed = slot_mid
                break
        if installed is None:
            return
        name, tool_desc = _GENERIC_CREW_BY_MODULE_ID[installed]
        # Position: amidships, between Tarven (top) and Mraka (top-left).
        # ~0.55 x 0.55 normalized = roughly centered.
        cx = room_rect.left + int(room_rect.width * 0.58)
        cy = room_rect.top + int(room_rect.height * 0.52)
        pw = 200
        ph = 80
        alcove_rect = pygame.Rect(cx - pw // 2, cy - ph // 2, pw, ph)
        pygame.draw.rect(screen, (32, 26, 18), alcove_rect)
        pygame.draw.rect(screen, (110, 90, 60), alcove_rect, 1)
        screen.blit(
            self.fonts["alcove"].render(name, True, (200, 180, 140)),
            (alcove_rect.left + 10, alcove_rect.top + 8),
        )
        # Tool description — wrapped short
        self._blit_wrapped_short(
            screen, tool_desc, self.fonts["posture"],
            alcove_rect.left + 10, alcove_rect.top + 32,
            pw - 20, (170, 150, 120), max_lines=2,
        )
        screen.blit(
            self.fonts["small"].render(
                "(generic — not interactive)", True, (130, 110, 90),
            ),
            (alcove_rect.left + 10, alcove_rect.bottom - 18),
        )

    def _render_alcove(
        self, screen: pygame.Surface, room_rect: pygame.Rect,
        alcove: CrewAlcove, occupied: bool, focused: bool,
    ) -> None:
        nx, ny = alcove.pos_norm
        cx = room_rect.left + int(room_rect.width * nx)
        cy = room_rect.top + int(room_rect.height * ny)
        # Alcove panel — taller now to accommodate the bond-objects shelf
        pw = 240
        ph = 150
        panel_rect = pygame.Rect(cx - pw // 2, cy - ph // 2, pw, ph)
        if not occupied:
            # Dim placeholder
            pygame.draw.rect(screen, (24, 18, 12), panel_rect)
            pygame.draw.rect(screen, (60, 50, 36), panel_rect, 1)
            label = self.fonts["alcove"].render(
                alcove.crew_name, True, (110, 100, 90),
            )
            lw, _ = label.get_size()
            screen.blit(
                label, (cx - lw // 2, panel_rect.top + 8),
            )
            unoccupied = self.fonts["small"].render(
                "(unoccupied — not yet recruited)", True, (100, 90, 80),
            )
            uw, _ = unoccupied.get_size()
            screen.blit(
                unoccupied,
                (cx - uw // 2, panel_rect.top + 36),
            )
            return

        # Occupied alcove
        bg_color = (40, 30, 18)
        border_color = alcove.accent if focused else (90, 70, 45)
        border_w = 2 if focused else 1
        pygame.draw.rect(screen, bg_color, panel_rect)
        pygame.draw.rect(screen, border_color, panel_rect, border_w)

        # Name header
        name_color = (
            tuple(min(255, c + 30) for c in alcove.accent)
            if focused else alcove.accent
        )
        name = self.fonts["alcove"].render(alcove.crew_name, True, name_color)
        nw, _ = name.get_size()
        screen.blit(name, (cx - nw // 2, panel_rect.top + 8))

        # Portrait stub — colored block representing where the avatar
        # will eventually render. Image-chat will supply real art.
        portrait_w = 50
        portrait_h = 50
        portrait_rect = pygame.Rect(
            panel_rect.left + 12,
            panel_rect.top + 36,
            portrait_w, portrait_h,
        )
        # Subtle fur-aesthetic gradient inside the portrait box
        for py in range(portrait_h):
            t = py / portrait_h
            shade = (
                int(alcove.accent[0] * (0.4 + t * 0.4)),
                int(alcove.accent[1] * (0.4 + t * 0.4)),
                int(alcove.accent[2] * (0.4 + t * 0.4)),
            )
            pygame.draw.line(
                screen, shade,
                (portrait_rect.left, portrait_rect.top + py),
                (portrait_rect.right - 1, portrait_rect.top + py),
            )
        pygame.draw.rect(screen, (200, 180, 130), portrait_rect, 1)

        # Posture blurb — to the right of the portrait, wrapped
        text_x = portrait_rect.right + 10
        text_y = portrait_rect.top
        max_w = panel_rect.right - text_x - 6
        self._blit_wrapped_short(
            screen, alcove.posture_blurb,
            self.fonts["posture"],
            text_x, text_y, max_w,
            (200, 180, 150),
            max_lines=3,
        )

        # Bond-object shelf — narrow strip across the bottom of the
        # alcove panel. Each visible bond-object is a small labelled
        # tile in the crew's accent color (placeholder until Image-chat
        # supplies sprites).
        from scz.content.crew_bond_objects import visible_bond_objects
        shelf_y = portrait_rect.bottom + 6
        shelf_h = 24
        shelf_rect = pygame.Rect(
            panel_rect.left + 10, shelf_y,
            pw - 20, shelf_h,
        )
        pygame.draw.rect(screen, (16, 12, 8), shelf_rect)
        pygame.draw.rect(screen, (70, 56, 40), shelf_rect, 1)
        if self.game is not None:
            objs = visible_bond_objects(self.game, alcove.role)
            # Lay out tiles left-to-right inside the shelf strip
            tile_pad = 4
            cx_x = shelf_rect.left + 4
            for obj in objs:
                # Tile width based on label, capped
                label_surf = self.fonts["bond"].render(
                    obj.label, True, (40, 32, 22),
                )
                lw, _ = label_surf.get_size()
                tile_w = min(max(40, lw + 10), 110)
                if cx_x + tile_w > shelf_rect.right - 4:
                    break   # ran out of shelf room
                tile_rect = pygame.Rect(
                    cx_x, shelf_rect.top + 3, tile_w, shelf_h - 6,
                )
                pygame.draw.rect(screen, obj.color, tile_rect)
                pygame.draw.rect(
                    screen, (30, 24, 16), tile_rect, 1,
                )
                # Truncate label to fit
                truncated = obj.label
                while (
                    truncated and
                    self.fonts["bond"].size(truncated)[0] > tile_w - 8
                ):
                    truncated = truncated[:-1]
                if truncated != obj.label:
                    truncated = truncated[:-3] + "..."
                if truncated:
                    text_surf = self.fonts["bond"].render(
                        truncated, True, (40, 32, 22),
                    )
                    tsw, tsh = text_surf.get_size()
                    screen.blit(
                        text_surf,
                        (
                            tile_rect.left + (tile_w - tsw) // 2,
                            tile_rect.top + (tile_rect.height - tsh) // 2,
                        ),
                    )
                cx_x += tile_w + tile_pad

        # Side-quest goalpost notification badge — pulsing "!" in the
        # top-right of the alcove panel when the crew's side-quest is
        # available to start.
        from scz.content.crew_bond_objects import (
            goalpost_notification_visible,
        )
        if self.game is not None and goalpost_notification_visible(
            self.game, alcove.role,
        ):
            import math as _math
            ticks = pygame.time.get_ticks()
            pulse = (_math.sin(ticks / 240) + 1) / 2
            badge_color = (
                int(220 + pulse * 35),
                int(180 + pulse * 50),
                int(100 + pulse * 50),
            )
            badge_x = panel_rect.right - 26
            badge_y = panel_rect.top + 6
            badge_radius = 11
            pygame.draw.circle(
                screen, (16, 10, 4),
                (badge_x, badge_y + badge_radius), badge_radius + 2,
            )
            pygame.draw.circle(
                screen, badge_color,
                (badge_x, badge_y + badge_radius), badge_radius,
            )
            pygame.draw.circle(
                screen, (40, 24, 8),
                (badge_x, badge_y + badge_radius), badge_radius, 1,
            )
            bang = self.fonts["badge"].render("!", True, (40, 24, 8))
            bw_, bh_ = bang.get_size()
            screen.blit(
                bang,
                (badge_x - bw_ // 2, badge_y + badge_radius - bh_ // 2),
            )

        # TALK prompt on focused alcove (pulse)
        if focused:
            import math as _math
            ticks = pygame.time.get_ticks()
            pulse = (_math.sin(ticks / 220) + 1) / 2
            prompt_color = (
                int(180 + pulse * 60),
                int(220 + pulse * 30),
                int(255),
            )
            prompt = self.fonts["prompt"].render(
                "[ TALK ]  A", True, prompt_color,
            )
            ppw, pph = prompt.get_size()
            screen.blit(
                prompt,
                (cx - ppw // 2, panel_rect.bottom + 4),
            )

    def _blit_wrapped_short(
        self, screen: pygame.Surface, text: str,
        font: pygame.font.Font,
        x: int, y: int, max_w: int,
        color: tuple[int, int, int],
        max_lines: int = 3,
    ) -> None:
        words = text.split(" ")
        line: list[str] = []
        cy = y
        line_h = font.get_linesize()
        lines = 0
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
                    lines += 1
                    if lines >= max_lines:
                        return
                line = [word]
        if line and lines < max_lines:
            screen.blit(
                font.render(" ".join(line), True, color), (x, cy),
            )
