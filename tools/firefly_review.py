"""Firefly image review — pygame keep/reject viewer.

Walks all `status: pending` entries in the manifest and displays each
generated image one at a time with its prompt and category. Aaron uses
keystrokes:

    K  → mark "keep"   (advances to next pending)
    R  → mark "reject" (advances to next pending)
    N  → skip (leave pending; advance)
    P  → previous image (re-review)
    1-4 → tag with a 1-4 quality star (optional)
    arrow keys → previous / next
    Esc / Q → save manifest and quit

The manifest is updated in real time so quitting mid-review preserves
progress.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pygame

# Allow running from project root or anywhere
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))

import firefly_index  # noqa: E402


WINDOW_W = 1400
WINDOW_H = 900
IMAGE_AREA_X = 40
IMAGE_AREA_Y = 80
IMAGE_AREA_W = 800
IMAGE_AREA_H = 800
SIDE_X = IMAGE_AREA_X + IMAGE_AREA_W + 40
SIDE_W = WINDOW_W - SIDE_X - 40


def _load_pending(only_status: str | None = "pending") -> list[tuple[str, dict]]:
    data = firefly_index.load()
    if only_status is None:
        items = [(k, v) for k, v in data.items()]
    else:
        items = [(k, v) for k, v in data.items() if v["status"] == only_status]
    items.sort()
    return items


def _scaled_image_for(entry: dict) -> pygame.Surface | None:
    p = ROOT / entry["image_path"]
    if not p.exists():
        return None
    try:
        raw = pygame.image.load(str(p)).convert_alpha()
    except pygame.error:
        return None
    rw, rh = raw.get_size()
    scale = min(IMAGE_AREA_W / rw, IMAGE_AREA_H / rh, 1.0)
    new_size = (max(1, int(rw * scale)), max(1, int(rh * scale)))
    return pygame.transform.smoothscale(raw, new_size)


def _wrap(text: str, font: pygame.font.Font, max_w: int) -> list[str]:
    lines: list[str] = []
    for paragraph in text.split("\n"):
        words = paragraph.split()
        cur: list[str] = []
        for w in words:
            test = " ".join(cur + [w])
            if font.size(test)[0] > max_w and cur:
                lines.append(" ".join(cur))
                cur = [w]
            else:
                cur.append(w)
        if cur:
            lines.append(" ".join(cur))
        else:
            lines.append("")
    return lines


def main() -> int:
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_W, WINDOW_H))
    pygame.display.set_caption("Firefly Image Review")
    clock = pygame.time.Clock()
    font_title = pygame.font.SysFont("consolas", 22, bold=True)
    font_body = pygame.font.SysFont("consolas", 16)
    font_small = pygame.font.SysFont("consolas", 14)
    font_help = pygame.font.SysFont("consolas", 14)

    review_mode = "pending"
    items = _load_pending(review_mode)
    idx = 0
    sticky_msg = ""
    cached_img: pygame.Surface | None = None
    cached_key: str | None = None
    running = True

    def refresh_items() -> None:
        nonlocal items, cached_img, cached_key
        items = _load_pending(review_mode)
        cached_img = None
        cached_key = None

    while running:
        if not items:
            screen.fill((10, 12, 20))
            t = font_title.render(
                f"No images with status={review_mode!r}", True, (220, 220, 240)
            )
            screen.blit(t, (40, 40))
            help_text = (
                "Press [A] all, [P] pending, [K] keep, [R] reject, [Esc] quit"
            )
            screen.blit(font_help.render(help_text, True, (160, 180, 210)),
                        (40, 80))
        else:
            idx = max(0, min(len(items) - 1, idx))
            key, entry = items[idx]

            if key != cached_key:
                cached_img = _scaled_image_for(entry)
                cached_key = key

            screen.fill((10, 12, 20))

            # Image area
            pygame.draw.rect(
                screen, (24, 28, 40),
                (IMAGE_AREA_X, IMAGE_AREA_Y, IMAGE_AREA_W, IMAGE_AREA_H), 0,
            )
            if cached_img is not None:
                iw, ih = cached_img.get_size()
                cx = IMAGE_AREA_X + (IMAGE_AREA_W - iw) // 2
                cy = IMAGE_AREA_Y + (IMAGE_AREA_H - ih) // 2
                screen.blit(cached_img, (cx, cy))
            else:
                msg = font_body.render(
                    "(image missing — file not on disk)",
                    True, (220, 100, 100),
                )
                screen.blit(msg, (IMAGE_AREA_X + 20, IMAGE_AREA_Y + 20))

            # Title bar
            title = font_title.render(
                f"[{idx + 1}/{len(items)}] {key}", True, (255, 230, 160),
            )
            screen.blit(title, (IMAGE_AREA_X, 30))
            sub = font_small.render(
                f"status={entry['status']}  ·  aspect={entry.get('aspect','?')}"
                f"  ·  generated_at={entry.get('generated_at') or '-'}",
                True, (160, 180, 210),
            )
            screen.blit(sub, (IMAGE_AREA_X, 56))

            # Side panel: prompt text + metadata
            prompt_path = ROOT / entry["prompt_path"]
            prompt_body = ""
            if prompt_path.exists():
                lines = prompt_path.read_text(encoding="utf-8").splitlines()
                body_lines = [l for l in lines if not l.startswith("#")]
                prompt_body = "\n".join(body_lines).strip()

            y = IMAGE_AREA_Y
            screen.blit(font_title.render("PROMPT", True, (220, 220, 240)),
                        (SIDE_X, y))
            y += 32
            for line in _wrap(prompt_body, font_small, SIDE_W)[:38]:
                screen.blit(font_small.render(line, True, (200, 210, 230)),
                            (SIDE_X, y))
                y += 18

            y += 12
            screen.blit(font_title.render("DESTINATION", True, (220, 220, 240)),
                        (SIDE_X, y))
            y += 28
            dest = entry.get("destination") or "(not yet assigned — wire-time)"
            for line in _wrap(dest, font_small, SIDE_W)[:3]:
                screen.blit(font_small.render(line, True, (180, 210, 180)),
                            (SIDE_X, y))
                y += 18

            y += 12
            if entry.get("notes"):
                screen.blit(font_title.render("NOTES", True, (220, 220, 240)),
                            (SIDE_X, y))
                y += 28
                for line in _wrap(entry["notes"], font_small, SIDE_W)[:6]:
                    screen.blit(font_small.render(line, True, (240, 220, 180)),
                                (SIDE_X, y))
                    y += 18

        # Help bar
        help_text = (
            "K=keep  R=reject  N=skip-as-pending  P=prev  arrows=nav  "
            "A=show-all  Esc/Q=save+quit"
        )
        screen.blit(font_help.render(help_text, True, (160, 180, 210)),
                    (40, WINDOW_H - 40))
        if sticky_msg:
            screen.blit(font_help.render(sticky_msg, True, (255, 240, 160)),
                        (40, WINDOW_H - 60))

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_ESCAPE, pygame.K_q):
                    running = False
                elif not items:
                    if event.key == pygame.K_a:
                        review_mode = None
                        refresh_items()
                    elif event.key == pygame.K_p:
                        review_mode = "pending"
                        refresh_items()
                elif event.key == pygame.K_k:
                    data = firefly_index.load()
                    data[key]["status"] = "keep"
                    firefly_index.save(data)
                    sticky_msg = f"marked {key} -> keep"
                    refresh_items()
                elif event.key == pygame.K_r:
                    data = firefly_index.load()
                    data[key]["status"] = "reject"
                    firefly_index.save(data)
                    sticky_msg = f"marked {key} -> reject"
                    refresh_items()
                elif event.key == pygame.K_n:
                    sticky_msg = f"skipped {key} (still pending)"
                    idx += 1
                elif event.key in (pygame.K_RIGHT, pygame.K_p):
                    idx += 1
                elif event.key == pygame.K_LEFT:
                    idx -= 1
                elif event.key == pygame.K_a:
                    review_mode = None
                    refresh_items()

        clock.tick(30)

    pygame.quit()
    return 0


if __name__ == "__main__":
    sys.exit(main())
