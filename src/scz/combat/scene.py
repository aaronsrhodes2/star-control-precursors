"""MeleeCombatScene — 1v1 ship combat with Newtonian movement.

Both sides AI-controlled by default (the auto-fight commitment). The
test harness uses this to drive Super Melee fights to completion. A
player-control path will land later; the engine treats it as just
another action source feeding the same physics + weapons code.

Slice scope per the design canon:
- 2D top-down, screen-wrapping arena
- Newtonian momentum (velocity persists; thrust adds to it)
- Projectile primary weapons (no specials yet — those land in pass 2)
- Hull + regenerating shield (shields only on Furling-faction ships)
- Win = one ship's hull hits 0; the surviving side is the winner

When the fight ends the scene calls `on_finish(winner_side)` if provided,
else falls back to set_scene(SuperMeleeScene). The win callback is what
the SuperMelee picker uses to advance to a result screen.
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass, field
from typing import Callable

import pygame

from scz.combat.ai import AIAction, decide
from scz.combat.ships import ShipClass
from scz.engine.scene import Scene


# Arena dimensions in world units — wraps at edges.
ARENA_W = 1600.0
ARENA_H = 1000.0

# Projectile pool cap (slice — we won't approach this)
MAX_PROJECTILES = 200

# How long after fight-end before the scene auto-exits
FIGHT_END_DWELL = 2.5

# Damage smear constant — when shields take damage they refill more
# slowly while damage continues. We do this by resetting the regen
# cooldown each tick of damage taken.
SHIELD_HIT_REGEN_DELAY_RESET = True


@dataclass
class ShipState:
    """Runtime state of one ship in combat. The ShipClass is the read-only
    spec; this is the mutable counterpart.
    """
    cls: ShipClass
    side: str
    x: float
    y: float
    heading: float
    vx: float = 0.0
    vy: float = 0.0
    hull: float = 0.0
    shield: float = 0.0
    energy: float = 0.0
    shield_regen_cooldown: float = 0.0
    primary_cooldown: float = 0.0
    alive: bool = True
    hit_flash: float = 0.0     # render flash on damage

    @classmethod
    def spawn(cls, ship_cls: ShipClass, x: float, y: float, heading: float) -> "ShipState":
        return cls(
            cls=ship_cls,
            side=ship_cls.side,
            x=x, y=y, heading=heading,
            hull=ship_cls.hull_max,
            shield=ship_cls.shield_max,
            energy=ship_cls.energy_max,
        )

    def apply_damage(self, amount: float) -> None:
        """Apply incoming damage. Shields absorb first, then hull."""
        if amount <= 0 or not self.alive:
            return
        self.hit_flash = 0.25
        if self.shield > 0:
            absorbed = min(self.shield, amount)
            self.shield -= absorbed
            amount -= absorbed
            if SHIELD_HIT_REGEN_DELAY_RESET:
                self.shield_regen_cooldown = self.cls.shield_regen_delay
        if amount > 0:
            self.hull -= amount
            if self.hull <= 0:
                self.hull = 0
                self.alive = False


@dataclass
class Projectile:
    x: float
    y: float
    vx: float
    vy: float
    damage: float
    range_left: float   # max distance before despawn
    owner_side: str
    color: tuple[int, int, int]
    radius: float = 3.0


@dataclass
class CombatResult:
    winner_side: str | None
    winner_ship: ShipClass | None
    loser_ship: ShipClass | None
    duration: float
    timed_out: bool


class MeleeCombatScene(Scene):
    """1v1 ship combat. Both ships AI-driven by default."""

    def __init__(
        self,
        precursor_ship: ShipClass,
        homesteader_ship: ShipClass,
        max_duration: float = 60.0,
        on_finish: Callable[[CombatResult], None] | None = None,
        seed: int | None = None,
    ) -> None:
        super().__init__()
        self.max_duration = max_duration
        self.on_finish = on_finish
        # A per-fight RNG so spawns aren't pixel-perfect identical each
        # run — Aaron specifically wants "somewhat but not perfectly
        # predictable" outcomes. The seed comes from the wall clock if
        # not provided.
        self.rng = random.Random(seed) if seed is not None else random.Random()

        # Spawn at opposite ends, facing each other, with a little jitter
        margin = 200.0
        spread_y = 200.0
        p_y = ARENA_H / 2 + self.rng.uniform(-spread_y, spread_y)
        h_y = ARENA_H / 2 + self.rng.uniform(-spread_y, spread_y)
        self.precursor = ShipState.spawn(
            precursor_ship, margin, p_y, heading=math.pi / 2  # facing +x
        )
        self.homesteader = ShipState.spawn(
            homesteader_ship, ARENA_W - margin, h_y, heading=-math.pi / 2  # facing -x
        )

        self.projectiles: list[Projectile] = []

        # Scene-time
        self.time_in_scene: float = 0.0
        self.result: CombatResult | None = None
        self.time_since_result: float = 0.0

        # Set in on_enter
        self.font: pygame.font.Font | None = None
        self.big_font: pygame.font.Font | None = None
        self.screen_w: int = 0
        self.screen_h: int = 0

    # ------------------------------------------------------------------
    # Scene API
    # ------------------------------------------------------------------

    def on_enter(self) -> None:
        assert self.game is not None
        self.screen_w, self.screen_h = self.game.screen.get_size()
        self.font = pygame.font.SysFont("consolas", 18)
        self.big_font = pygame.font.SysFont("consolas", 36, bold=True)

    def snapshot(self) -> dict | None:
        # Combat is intentionally NOT rewindable — committing to a fight
        # is committing. Time Drive rewinds you to BEFORE the combat
        # started, not partway through.
        return None

    def update(self, dt: float, inp) -> None:  # type: ignore[no-untyped-def]
        self.time_in_scene += dt

        if self.result is not None:
            # Fight is over — dwell briefly, then finish.
            self.time_since_result += dt
            if self.time_since_result >= FIGHT_END_DWELL:
                self._finish()
            return

        # --- Per-ship update ---
        for me, other in (
            (self.precursor, self.homesteader),
            (self.homesteader, self.precursor),
        ):
            if not me.alive:
                continue
            action = decide(me, other)
            self._apply_action(me, action, dt)
            self._integrate(me, dt)
            self._regen(me, dt)
            if action.fire_primary:
                self._fire_primary(me)
            if me.hit_flash > 0:
                me.hit_flash = max(0.0, me.hit_flash - dt)

        # --- Projectiles ---
        self._update_projectiles(dt)

        # --- Win detection ---
        if not self.precursor.alive and self.homesteader.alive:
            self._record_result(self.homesteader, self.precursor)
        elif not self.homesteader.alive and self.precursor.alive:
            self._record_result(self.precursor, self.homesteader)
        elif not self.precursor.alive and not self.homesteader.alive:
            # Double-KO. Call it a draw by treating Precursor as not winning.
            self._record_result(None, None)
        elif self.time_in_scene >= self.max_duration:
            # Timeout — whoever has more total HP wins, ties go to Precursor
            p_score = self.precursor.hull + self.precursor.shield
            h_score = self.homesteader.hull + self.homesteader.shield
            if p_score >= h_score:
                self._record_result(self.precursor, self.homesteader, timed_out=True)
            else:
                self._record_result(self.homesteader, self.precursor, timed_out=True)

    def render(self, screen: pygame.Surface) -> None:
        screen.fill((4, 4, 14))

        # Arena boundary (wraps but we draw it as a faint frame)
        scale = self._scale()
        ox = (self.screen_w - ARENA_W * scale) / 2
        oy = (self.screen_h - ARENA_H * scale) / 2
        pygame.draw.rect(
            screen, (28, 28, 48),
            (ox, oy, ARENA_W * scale, ARENA_H * scale),
            1,
        )

        # Starfield backdrop — deterministic seed so it doesn't shimmer
        rng = random.Random(101)
        for _ in range(180):
            sx = ox + rng.uniform(0, ARENA_W * scale)
            sy = oy + rng.uniform(0, ARENA_H * scale)
            b = rng.randint(60, 200)
            pygame.draw.circle(screen, (b // 2, b // 2, b), (int(sx), int(sy)), 1)

        # Projectiles
        for p in self.projectiles:
            sx, sy = self._world_to_screen(p.x, p.y, ox, oy, scale)
            pygame.draw.circle(screen, p.color, (int(sx), int(sy)), max(2, int(p.radius * scale)))

        # Ships
        for ship in (self.precursor, self.homesteader):
            self._draw_ship(screen, ship, ox, oy, scale)

        # HUDs (one per side)
        self._draw_hud(screen)

        # Big result overlay
        if self.result is not None and self.big_font is not None:
            text_winner = self._result_text()
            label = self.big_font.render(text_winner, True, (255, 230, 180))
            lw, lh = label.get_size()
            box = pygame.Surface((lw + 80, lh + 60), pygame.SRCALPHA)
            box.fill((10, 10, 30, 220))
            screen.blit(box, ((self.screen_w - lw - 80) // 2, (self.screen_h - lh - 60) // 2))
            screen.blit(label, ((self.screen_w - lw) // 2, (self.screen_h - lh) // 2))

    # ------------------------------------------------------------------
    # Physics + actions
    # ------------------------------------------------------------------

    def _apply_action(self, ship: ShipState, action: AIAction, dt: float) -> None:
        cls = ship.cls
        # Rotation
        if action.turn_dir != 0:
            ship.heading += action.turn_dir * cls.turn_rate * dt
            ship.heading = (ship.heading + math.pi) % (2 * math.pi) - math.pi
        # Thrust
        if action.thrust:
            fx = math.sin(ship.heading) * cls.acceleration * dt
            fy = -math.cos(ship.heading) * cls.acceleration * dt
            ship.vx += fx
            ship.vy += fy
            speed = math.hypot(ship.vx, ship.vy)
            if speed > cls.top_speed:
                # Cap
                ship.vx *= cls.top_speed / speed
                ship.vy *= cls.top_speed / speed
        # Primary cooldown decrement (independent of fire decision)
        if ship.primary_cooldown > 0:
            ship.primary_cooldown = max(0.0, ship.primary_cooldown - dt)

    def _integrate(self, ship: ShipState, dt: float) -> None:
        ship.x += ship.vx * dt
        ship.y += ship.vy * dt
        # Arena wrap
        ship.x %= ARENA_W
        ship.y %= ARENA_H

    def _regen(self, ship: ShipState, dt: float) -> None:
        cls = ship.cls
        if ship.shield_regen_cooldown > 0:
            ship.shield_regen_cooldown = max(0.0, ship.shield_regen_cooldown - dt)
        elif ship.shield < cls.shield_max:
            ship.shield = min(cls.shield_max, ship.shield + cls.shield_regen * dt)
        if ship.energy < cls.energy_max:
            ship.energy = min(cls.energy_max, ship.energy + cls.energy_regen * dt)

    def _fire_primary(self, ship: ShipState) -> None:
        cls = ship.cls
        if ship.energy < cls.primary_energy:
            return
        ship.energy -= cls.primary_energy
        ship.primary_cooldown = 1.0 / max(0.5, cls.primary_rate)
        # Spawn projectile from the ship's nose
        nose_offset = 16.0
        sx = ship.x + math.sin(ship.heading) * nose_offset
        sy = ship.y - math.cos(ship.heading) * nose_offset
        vx = math.sin(ship.heading) * cls.primary_speed
        vy = -math.cos(ship.heading) * cls.primary_speed
        # Projectiles inherit a fraction of the ship's velocity (looks
        # right + gives faster ships subtle aim leading help)
        vx += ship.vx * 0.3
        vy += ship.vy * 0.3
        if len(self.projectiles) < MAX_PROJECTILES:
            self.projectiles.append(Projectile(
                x=sx, y=sy, vx=vx, vy=vy,
                damage=cls.primary_damage,
                range_left=cls.primary_range,
                owner_side=ship.side,
                color=cls.primary_color,
            ))

    def _update_projectiles(self, dt: float) -> None:
        survivors: list[Projectile] = []
        for p in self.projectiles:
            speed = math.hypot(p.vx, p.vy)
            step = speed * dt
            if step > p.range_left:
                continue
            p.x = (p.x + p.vx * dt) % ARENA_W
            p.y = (p.y + p.vy * dt) % ARENA_H
            p.range_left -= step

            # Check hits against the *other* side's ship
            for target in (self.precursor, self.homesteader):
                if not target.alive:
                    continue
                if target.side == p.owner_side:
                    continue
                # Account for arena wrap — check against the toroidal-nearest copy
                dx = self._wrap_delta(p.x, target.x, ARENA_W)
                dy = self._wrap_delta(p.y, target.y, ARENA_H)
                d = math.hypot(dx, dy)
                hit_radius = 18.0 + p.radius
                if d <= hit_radius:
                    target.apply_damage(p.damage)
                    p = None  # type: ignore[assignment]
                    break
            if p is not None:
                survivors.append(p)
        self.projectiles = survivors

    def _wrap_delta(self, a: float, b: float, axis: float) -> float:
        d = a - b
        if d > axis / 2:
            d -= axis
        elif d < -axis / 2:
            d += axis
        return d

    # ------------------------------------------------------------------
    # Result + finish
    # ------------------------------------------------------------------

    def _record_result(
        self,
        winner: ShipState | None,
        loser: ShipState | None,
        timed_out: bool = False,
    ) -> None:
        self.result = CombatResult(
            winner_side=winner.side if winner else None,
            winner_ship=winner.cls if winner else None,
            loser_ship=loser.cls if loser else None,
            duration=self.time_in_scene,
            timed_out=timed_out,
        )
        self.time_since_result = 0.0

    def _finish(self) -> None:
        assert self.game is not None
        if self.on_finish is not None:
            self.on_finish(self.result)
        else:
            # Default: bounce back to SuperMelee picker
            from scz.combat.super_melee import SuperMeleeScene
            self.game.set_scene(SuperMeleeScene())

    def _result_text(self) -> str:
        if self.result is None:
            return ""
        if self.result.winner_side is None:
            return "DOUBLE KO"
        winner_name = (
            self.result.winner_ship.name if self.result.winner_ship else "?"
        )
        if self.result.timed_out:
            return f"TIMEOUT  ·  {winner_name} stands"
        return f"VICTORY  ·  {winner_name}"

    # ------------------------------------------------------------------
    # Rendering helpers
    # ------------------------------------------------------------------

    def _scale(self) -> float:
        # Fit the arena to the window. Slight margin.
        sx = (self.screen_w - 80) / ARENA_W
        sy = (self.screen_h - 200) / ARENA_H
        return min(sx, sy)

    def _world_to_screen(
        self, x: float, y: float, ox: float, oy: float, scale: float
    ) -> tuple[float, float]:
        return (ox + x * scale, oy + y * scale)

    def _draw_ship(
        self,
        screen: pygame.Surface,
        ship: ShipState,
        ox: float,
        oy: float,
        scale: float,
    ) -> None:
        if not ship.alive:
            # Brief wreck
            sx, sy = self._world_to_screen(ship.x, ship.y, ox, oy, scale)
            pygame.draw.circle(screen, (180, 60, 60), (int(sx), int(sy)), 14, 1)
            pygame.draw.circle(screen, (140, 40, 40), (int(sx), int(sy)), 8, 1)
            return
        sx, sy = self._world_to_screen(ship.x, ship.y, ox, oy, scale)
        cos_h = math.cos(ship.heading)
        sin_h = math.sin(ship.heading)
        # Silhouette: simple shape; mass + style suggest tweaks
        size = 14
        s = ship.cls.silhouette
        if s in ("scout", "skiff"):
            pts = [(0, -size), (-size * 0.65, size * 0.55), (size * 0.65, size * 0.55)]
        elif s == "blade":
            pts = [(0, -size), (-size * 0.4, size * 0.6), (0, size * 0.3), (size * 0.4, size * 0.6)]
        elif s in ("heavy", "cruiser"):
            size = 18
            pts = [
                (0, -size), (-size * 0.85, -size * 0.1),
                (-size * 0.6, size * 0.7), (size * 0.6, size * 0.7),
                (size * 0.85, -size * 0.1),
            ]
        elif s == "warship":
            size = 16
            pts = [(0, -size), (-size, size * 0.4), (-size * 0.3, size * 0.5),
                   (size * 0.3, size * 0.5), (size, size * 0.4)]
        else:  # sentinel
            size = 15
            pts = [(0, -size), (-size * 0.5, -size * 0.2), (-size * 0.7, size * 0.5),
                   (size * 0.7, size * 0.5), (size * 0.5, -size * 0.2)]
        rotated = []
        for lx, ly in pts:
            rx = lx * cos_h - ly * sin_h
            ry = lx * sin_h + ly * cos_h
            rotated.append((sx + rx * scale, sy + ry * scale))
        # Flash on damage
        body_color = ship.cls.hull_color
        if ship.hit_flash > 0:
            t = ship.hit_flash / 0.25
            body_color = (
                min(255, int(body_color[0] + t * 120)),
                min(255, int(body_color[1] + t * 60)),
                min(255, int(body_color[2] + t * 60)),
            )
        pygame.draw.polygon(screen, body_color, rotated)
        pygame.draw.polygon(screen, ship.cls.accent_color, rotated, 1)
        # Shield ring
        if ship.cls.shield_max > 0 and ship.shield > 0:
            frac = max(0.0, min(1.0, ship.shield / ship.cls.shield_max))
            shield_color = (
                min(255, int(120 * frac + 60)),
                min(255, int(160 * frac + 60)),
                min(255, int(180 * frac + 60)),
            )
            pygame.draw.circle(
                screen, shield_color, (int(sx), int(sy)),
                max(1, int((size + 6) * scale * 1.3)), 1,
            )

    def _draw_hud(self, screen: pygame.Surface) -> None:
        assert self.font is not None
        # Side panels — left = Precursor, right = Homesteader
        for ship, x_anchor, align in (
            (self.precursor, 24, "left"),
            (self.homesteader, self.screen_w - 380, "left"),
        ):
            cls = ship.cls
            y = 24
            screen.blit(
                self.font.render(cls.name, True, ship.cls.accent_color),
                (x_anchor, y),
            )
            y += 28
            screen.blit(
                self.font.render(
                    f"{cls.side.upper():<12s}  {cls.points} pts",
                    True, (180, 180, 200),
                ),
                (x_anchor, y),
            )
            y += 24
            # Hull bar
            self._bar(
                screen, x_anchor, y, 320, 12,
                ship.hull / max(1, cls.hull_max),
                (220, 80, 80),
                f"HULL   {int(ship.hull):3d}/{cls.hull_max}",
            )
            y += 22
            # Shield bar (if any)
            if cls.shield_max > 0:
                self._bar(
                    screen, x_anchor, y, 320, 12,
                    ship.shield / max(1, cls.shield_max),
                    (90, 180, 240),
                    f"SHIELD {int(ship.shield):3d}/{cls.shield_max}",
                )
                y += 22
            else:
                screen.blit(
                    self.font.render("(no shields)", True, (130, 140, 170)),
                    (x_anchor, y),
                )
                y += 22
            # Energy bar
            self._bar(
                screen, x_anchor, y, 320, 8,
                ship.energy / max(1, cls.energy_max),
                (140, 220, 160),
                f"NRG    {int(ship.energy):3d}/{int(cls.energy_max)}",
            )

        # Center bottom — time remaining
        remaining = max(0, self.max_duration - self.time_in_scene)
        timer = self.font.render(
            f"FIGHT  ·  t={self.time_in_scene:5.1f}s  ·  cap {self.max_duration:.0f}s",
            True, (180, 190, 210),
        )
        tw, _ = timer.get_size()
        screen.blit(timer, ((self.screen_w - tw) // 2, self.screen_h - 36))

    def _bar(
        self,
        screen: pygame.Surface,
        x: int,
        y: int,
        w: int,
        h: int,
        frac: float,
        color: tuple[int, int, int],
        label: str,
    ) -> None:
        assert self.font is not None
        frac = max(0.0, min(1.0, frac))
        pygame.draw.rect(screen, (30, 30, 50), (x, y, w, h))
        pygame.draw.rect(screen, color, (x, y, int(w * frac), h))
        pygame.draw.rect(screen, (90, 100, 130), (x, y, w, h), 1)
        screen.blit(self.font.render(label, True, (200, 210, 230)), (x + w + 8, y - 3))
