---
id: 2026-05-17T1000-golden-rule-human-review
from: testing-chat
to: design-chat
priority: high
title: Canonicalize the "human review of generated media" golden rule in references/project-rules.md
files_inspected:
  - references/project-rules.md (per memory; design chat to confirm current rule count)
filed_at: 2026-05-17T10:00
---

# Canonicalize the "human review of generated media" golden rule

Aaron asked the testing chat to record this as a golden rule for the project. Memory has been updated immediately (`~/.claude/projects/.../memory/project_golden_rule_human_review.md`) so all three chats see it now; this dispatch asks the design chat to canonicalize it in the repo's rulebook so it survives memory pruning and shows up in git history.

## The rule (Aaron's words, lightly normalized)

> **Prepare and prompt Aaron for review of every batch of generated images and audio as they're generated.** No image or audio asset is "done" until Aaron has signed off.

## Where to put it

`references/project-rules.md` already has three numbered mandates per memory:
1. Improve every UQM-placeholder asset before 1.0
2. Engine before variation
3. Tests as repeatable scripts

Add this as **Rule 4** (or whatever the next number is — design chat to verify). Suggested wording, to be edited:

---

### Rule 4 — Human Review of Generated Media

Every batch of generated images or audio MUST be staged for Aaron's review and accompanied by an **explicit prompt** to review before the chat moves on. No image or audio asset is "done" until Aaron has signed off.

**Applies to** — every category of generated media: portraits, ship sprites, cutscene backdrops, planet sprites, faction insignia, module icons, UI elements, music stems, voice samples, SFX, ambient audio, and any future generative pipeline output.

**"Prepare"** —
- *Images*: manifest entry with status `pending` in `assets/generated_drafts/firefly/_manifest.json`, ready for `tools/firefly_review.py` to display. Group the batch so Aaron isn't asked to review one image at a time.
- *Audio*: stage in a documented directory with a manifest listing each file's path, intended use, and a one-line playback command.

**"Explicit prompt"** — end the chat turn with a clear sentence: *"Generated N new X in <path>. Please run <review command> and keep/reject. I'll wait."*

**Forbidden** —
- Silently marking assets `keep` without Aaron looking.
- Wiring newly-generated assets into game code without sign-off.
- Mentioning the review in passing while moving on to the next task.

**Rationale.** Generative pipelines drift. A keep/reject pass is the only way to maintain the project's visual + auditory identity. The cost of asking is small; the cost of unreviewed drift is large.

---

## Cross-chat enforcement to spell out

The rule is owned by the image chat (most generation happens there), but design and testing each have a duty:
- **Design chat**: do not wire assets into game code (e.g. `characters.py` avatar fields, scene backdrop paths) without confirming the asset's manifest status is `keep`.
- **Testing chat**: when running walks, can flag if it notices an unreviewed asset wired into game code (status `pending` or absent from manifest).

Worth mentioning explicitly in the rule body so neither chat silently bypasses it.

## Why high priority

Image chat is actively generating assets. Without this rule landing in the canonical doc, the next chat that opens fresh won't see it unless it reads the memory file first — and memory files can be pruned. A repo-tracked rule survives.

## Notes

- The memory file at `~/.claude/projects/.../memory/project_golden_rule_human_review.md` is the authoritative source until this lands. After this is canonicalized in `references/project-rules.md`, the memory file should reference the canonical doc rather than duplicate it.
- Confirm the canonical rule path with Aaron before editing — memory says `references/project-rules.md` but if it's been moved (e.g. `references/lore/project-rules.md`), use the actual current path.
- After landing: file a test-queue job is NOT needed — this is a doc change with no walk-test impact.
