# Design Queue — dispatch design/implementation tasks to the game-design chat

Mirror of `.claude/test-queue/` but reversed: the testing chat (and image chat, when finding design-side bugs) writes Markdown task specs here; the game-design chat consumes them.

## Why this exists

The testing chat finds UX gaps and bugs while running walks and exploring scenes. The design chat is the one with authority + context to implement fixes. This queue is the hand-off mechanism so the testing chat doesn't bypass the dual-chat-split rule by editing design-owned code itself.

## Layout

```
.claude/design-queue/
├── inbox/                pending task specs (Markdown with YAML frontmatter)
│   └── .processed/       design chat moves files here after implementing
└── done/                 design chat writes completion summaries here
```

## Filing a task (from the testing chat — or image chat)

`Write` a Markdown file to `inbox/<id>.md` with YAML frontmatter:

```markdown
---
id: 2026-05-17T0945-map-interface-ux
from: testing-chat
to: design-chat
priority: medium             # low / medium / high
title: Map interface UX improvements
files_inspected:
  - src/scz/hyperspace/scene.py
  - src/scz/system/scene.py
  - src/scz/engine/input.py
filed_at: 2026-05-17T09:45
---

# <Title>

## Current state
What the code does today.

## Problems / gaps
Specific UX or correctness issues found while testing.

## Recommendations
Concrete proposed changes, file-by-file where possible.

## Suggested test coverage
What walk-tests should exist (so the testing chat can add them after design ships).
```

## Consuming a task (design chat)

1. `ls .claude/design-queue/inbox/` — what's pending
2. Read the highest-priority file
3. Implement
4. Move the source file to `.processed/` and `Write` a short completion summary to `done/<id>.md`:

```markdown
---
id: 2026-05-17T0945-map-interface-ux
status: shipped              # shipped / partial / declined / deferred
shipped_at: 2026-05-17T11:20
commits: [abc123, def456]
---

# Summary of what was done
Bullets of what landed. Note any deviations from the spec.

# What's deferred
Bullets of what was NOT done from the spec and why (size, scope, blocked-on-X).
```

5. (Optional) File a test-queue job to re-run any affected walks.

## What to file vs. what to just chat about

- **File a task** when the work is concrete enough that the design chat can pick it up without re-litigating scope. Specific code-shaped recommendations beat vague feedback.
- **Chat directly** for open-ended brainstorms, scope negotiations, "is this even worth doing?" questions.

## What NOT to file

- Anything the testing chat could fix in its own lane (walk-test bugs, walk-test infra) — fix those directly.
- Image-asset issues — those belong to the image chat, file under `.claude/image-queue/` if/when that exists, or just message the image chat.
- Lore/narrative changes — those are design-owned but should originate from the design chat or the user, not the testing chat.

## How the design chat notices new tasks

No auto-polling on the design chat (it doesn't have a /loop). The user (or another chat) prompts it: "drain the design queue" or "any pending design tasks?" — at which point it reads `inbox/` and processes.
