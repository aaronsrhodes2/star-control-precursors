"""The Time Drive — Furling chronometric reverse-flow capacitor.

Continuously snapshots the active scene's rewindable state and lets the
player roll back exactly 5 minutes of real time. Triggered manually (player
decision to escape a bad situation) or automatically (on ship death — not
wired yet since combat doesn't exist).

Architecture notes:
- Lives in the engine layer. Scenes opt in by implementing snapshot()/restore().
- Scenes that return None from snapshot() are non-rewindable (Council scene,
  dialog where the player has *committed* to a decision, etc.).
- After a successful rewind the buffer empties; you can't rewind again until
  the buffer has refilled (5 min of real play).
- This is *cosmetically* part of the variation layer's spirit (separable,
  doesn't change gameplay rules — the engine just gets told "restore this
  state") but architecturally it lives in engine because it's load-bearing
  for gameplay logic (no death = no game over = no save/load needed).
"""

from __future__ import annotations

import time
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

import pygame

if TYPE_CHECKING:
    from scz.engine.scene import Scene


@dataclass
class Snapshot:
    timestamp: float                 # wall-clock seconds since epoch
    state: dict[str, Any]            # scene's serialized state


class TimeDrive:
    """Rolling buffer of scene snapshots; provides rewind."""

    # Tunables. The lore commits to "exactly 5 minutes"; the snapshot interval
    # controls how granular our buffer is (smaller = more memory, finer rewind).
    REWIND_SECONDS: float = 300.0     # 5 minutes
    SNAPSHOT_INTERVAL: float = 10.0   # snapshot every 10s
    # Allow rewind once we have at least this much buffer (slightly less than
    # full so the player isn't waiting an extra interval after a fresh start).
    READY_THRESHOLD: float = 295.0

    def __init__(self) -> None:
        self.snapshots: list[Snapshot] = []
        self._last_snapshot_time: float = 0.0
        # Visual effect bookkeeping
        self.flash_remaining: float = 0.0  # 0 = no flash, 1.0 = full flash
        self.FLASH_DURATION: float = 0.55  # seconds

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def maybe_snapshot(self, scene: "Scene") -> None:
        """Take a snapshot if SNAPSHOT_INTERVAL has elapsed."""
        now = time.monotonic()
        if now - self._last_snapshot_time < self.SNAPSHOT_INTERVAL:
            return
        state = scene.snapshot()
        if state is None:
            # Scene doesn't support rewind right now (e.g., combat lock-in).
            return
        self.snapshots.append(Snapshot(now, state))
        self._last_snapshot_time = now
        # Trim snapshots older than REWIND_SECONDS (we don't need them)
        cutoff = now - self.REWIND_SECONDS - self.SNAPSHOT_INTERVAL
        self.snapshots = [s for s in self.snapshots if s.timestamp >= cutoff]

    def is_ready(self) -> bool:
        """True if a rewind is available."""
        if not self.snapshots:
            return False
        oldest_age = time.monotonic() - self.snapshots[0].timestamp
        return oldest_age >= self.READY_THRESHOLD

    def time_until_ready(self) -> float:
        """Seconds until is_ready() becomes True. 0 if already ready."""
        if self.is_ready():
            return 0.0
        if not self.snapshots:
            return self.REWIND_SECONDS
        oldest_age = time.monotonic() - self.snapshots[0].timestamp
        return max(0.0, self.READY_THRESHOLD - oldest_age)

    def buffer_seconds(self) -> float:
        """How much rewindable history is currently buffered."""
        if not self.snapshots:
            return 0.0
        return time.monotonic() - self.snapshots[0].timestamp

    def rewind(self, scene: "Scene") -> bool:
        """Restore the oldest snapshot. Returns True on success."""
        if not self.is_ready():
            return False
        target = self.snapshots[0]
        scene.restore(target.state)
        # Buffer empties — must recharge before next rewind
        self.snapshots = []
        self._last_snapshot_time = time.monotonic()
        self.flash_remaining = self.FLASH_DURATION
        return True

    # ------------------------------------------------------------------
    # Per-frame update / overlay
    # ------------------------------------------------------------------

    def update(self, dt: float) -> None:
        if self.flash_remaining > 0:
            self.flash_remaining = max(0.0, self.flash_remaining - dt)

    def render_overlay(self, screen: pygame.Surface) -> None:
        """Draw the chronometric flash effect. Call after the scene renders."""
        if self.flash_remaining <= 0:
            return
        # Two phases: bright flash then fade. Fades from bright cyan-white
        # to nothing over FLASH_DURATION.
        progress = self.flash_remaining / self.FLASH_DURATION  # 1.0 → 0.0
        alpha = int(220 * progress)
        overlay = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
        # Cyan-white "chronometric reflux" color
        overlay.fill((180, 220, 255, alpha))
        screen.blit(overlay, (0, 0))
        # Show "TIME DRIVE" text on top of the flash
        if alpha > 60:
            font = pygame.font.SysFont("consolas", 56, bold=True)
            text_alpha = min(255, alpha + 40)
            text = font.render("TIME DRIVE", True, (20, 40, 80))
            text.set_alpha(text_alpha)
            tw, th = text.get_size()
            sw, sh = screen.get_size()
            screen.blit(text, ((sw - tw) // 2, (sh - th) // 2 - 20))
            sub = pygame.font.SysFont("consolas", 22).render(
                "— five minutes rewound —", True, (40, 60, 100)
            )
            sub.set_alpha(text_alpha)
            sw2, sh2 = sub.get_size()
            screen.blit(sub, ((sw - sw2) // 2, (sh - sh2) // 2 + 40))
