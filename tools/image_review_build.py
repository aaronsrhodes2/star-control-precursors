"""Generate a single-file HTML image reviewer for Aaron's review pass.

Mirror of tools/audio_player_build.py for the image-generation
pipeline. Reads:
  - assets/generated_drafts/firefly/_manifest.json    (source of truth:
        status / prompt_path / aspect / generated_at / tags / destination
        / notes per image)
  - tools/firefly_prompts/<tier>/<name>.txt           (per-image prompt
        body, where present)

Renders one HTML page with:
  - Header showing total count + per-status breakdown
    (pending / keep / reject / wired) + filter buttons + name search
  - One section per tier directory
  - Per image: thumbnail (lazy-loaded, click to open full-size),
    name + status chip + aspect + generated date, prompt text
    (collapsible if long), notes, tags
  - Also surfaces "untracked" images (PNG present but no manifest entry)

Re-run any time new images land:
    python tools/image_review_build.py

Served from the project root via the same HTTP server the audio
player uses:
    python -m http.server 8770
then navigate to http://localhost:8770/tools/image_review.html
"""

from __future__ import annotations

import json
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FIREFLY_DIR = ROOT / "assets" / "generated_drafts" / "firefly"
MANIFEST = FIREFLY_DIR / "_manifest.json"
PROMPTS_ROOT = ROOT / "tools" / "firefly_prompts"
OUT_PATH = Path(__file__).resolve().parent / "image_review.html"


def _load_manifest() -> dict:
    if not MANIFEST.exists():
        return {}
    return json.loads(MANIFEST.read_text(encoding="utf-8"))


def _save_manifest(manifest: dict) -> None:
    """Atomically write the manifest back to disk."""
    tmp = MANIFEST.with_suffix(".json.tmp")
    tmp.write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    tmp.replace(MANIFEST)


def _list_firefly_pngs() -> list[Path]:
    if not FIREFLY_DIR.is_dir():
        return []
    return sorted(FIREFLY_DIR.rglob("*.png"))


# Aspect ratio inferred from file dimensions, with sensible defaults per tier
def _infer_aspect(p: Path) -> str:
    tier = p.relative_to(FIREFLY_DIR).parts[0]
    # Quick tier-based defaults (image dimensions match)
    if tier == "tier1_avatars":
        return "2:3"
    if tier == "tier1_cutscenes":
        return "16:9"
    return "1:1"  # ships, portraits, planets, insignia, artifacts, etc.


def _file_mtime_iso(p: Path) -> str:
    """Return the file's mtime as a UTC ISO8601 string."""
    from datetime import datetime, timezone
    return datetime.fromtimestamp(p.stat().st_mtime, tz=timezone.utc).isoformat()


def index_untracked(manifest: dict, pngs: list[Path]) -> int:
    """Auto-create manifest entries for any PNG that's on disk but not yet
    indexed. New entries default to status=pending so they show up in the
    review queue. The prompt_path is inferred from the conventional filename
    layout (tools/firefly_prompts/<tier>/<name>.txt) and only set if the
    file actually exists.

    Returns the number of new entries added.
    """
    added = 0
    for p in pngs:
        key = _key_from_path(p)
        if key in manifest:
            continue
        tier = _tier_of_path(p)
        name = p.stem
        prompt_rel = f"tools/firefly_prompts/{tier}/{name}.txt"
        prompt_exists = (ROOT / prompt_rel).exists()
        manifest[key] = {
            "prompt_path": prompt_rel if prompt_exists else "",
            "image_path": p.relative_to(ROOT).as_posix(),
            "aspect": _infer_aspect(p),
            "generated_at": _file_mtime_iso(p),
            "status": "pending",
            "tags": [tier.replace("tier1_", "")],
            "destination": None,
            "manifest_entry_to_update": None,
            "notes": "",
        }
        added += 1
    return added


def _load_prompt_body(prompt_path_rel: str) -> str:
    """Read the .txt prompt body. Strip header comment lines (# aspect /
    # notes) so the bulk of the displayed text is the prose."""
    if not prompt_path_rel:
        return ""
    p = ROOT / prompt_path_rel
    if not p.exists():
        return ""
    text = p.read_text(encoding="utf-8", errors="replace").strip()
    # Strip leading # comment lines but keep their content as a header block
    return text


def _asset_url(asset_path: Path) -> str:
    """Image URL with a cache-busting query string keyed on the file's
    mtime. Without this, browsers showed stale cached content when an
    in-place reroll replaced a PNG (the URL didn't change). 2026-05-17
    fix for Aaron's "~1-in-20 mislabel" report."""
    rel = asset_path.relative_to(ROOT).as_posix()
    mtime = int(asset_path.stat().st_mtime)
    return f"../{rel}?v={mtime}"


def _key_from_path(p: Path) -> str:
    """Convert assets/generated_drafts/firefly/tier1_X/y.png ->
    'tier1_X/y' which is the manifest key shape."""
    rel = p.relative_to(FIREFLY_DIR)
    return rel.with_suffix("").as_posix()


def _tier_of_path(p: Path) -> str:
    return p.relative_to(FIREFLY_DIR).parts[0]


def _esc(s: str) -> str:
    return (s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            .replace('"', "&quot;").replace("'", "&#39;"))


def _render_image_card(p: Path, manifest_entry: dict | None) -> str:
    key = _key_from_path(p)
    img_url = _asset_url(p)
    name = p.stem
    status = (manifest_entry or {}).get("status") or "untracked"
    aspect = (manifest_entry or {}).get("aspect") or ""
    generated_at = (manifest_entry or {}).get("generated_at") or ""
    tags = (manifest_entry or {}).get("tags") or []
    notes = (manifest_entry or {}).get("notes") or ""
    destination = (manifest_entry or {}).get("destination") or ""
    prompt_path = (manifest_entry or {}).get("prompt_path") or ""
    prompt_body = _load_prompt_body(prompt_path) if prompt_path else ""
    # Truncate for the collapsed preview
    preview_chars = 140
    prompt_short = prompt_body[:preview_chars] + ("..." if len(prompt_body) > preview_chars else "")
    has_more = len(prompt_body) > preview_chars

    tag_html = "".join(
        f'<span class="tag">{_esc(t)}</span>' for t in tags
    )
    notes_html = (
        f'<div class="notes">📝 {_esc(notes)}</div>' if notes.strip() else ""
    )
    dest_html = (
        f'<div class="dest">→ {_esc(destination)}</div>' if destination else ""
    )
    prompt_html = ""
    if prompt_body:
        if has_more:
            prompt_html = f"""
        <details class="prompt">
          <summary><span class="prompt-short">{_esc(prompt_short)}</span></summary>
          <pre class="prompt-full">{_esc(prompt_body)}</pre>
        </details>"""
        else:
            prompt_html = f'<div class="prompt-full prompt-single">{_esc(prompt_body)}</div>'

    # Review action buttons — only render when the image is tracked
    # in the manifest (otherwise there's no key to POST to). Untracked
    # images need to be added to the manifest first.
    actions_html = ""
    if manifest_entry is not None:
        actions_html = f"""
        <div class="actions" data-key="{_esc(key)}">
          <button class="action-btn approve" data-action="keep" title="Approve — keep as-is, wire this into the game on next integration pass">✓ Approve</button>
          <button class="action-btn reroll" data-action="reroll_requested" title="Re-roll — image is wrong; ALSO add a note describing what to change. Image-lane will rewrite the prompt + regenerate next credit window.">↻ Re-roll</button>
          <button class="action-btn reject" data-action="reject" title="Reject — drop the concept entirely; do NOT re-roll. Use this only when the image shouldn't exist at all. (If you want a different version, use Re-roll with a note.)">✗ Reject</button>
        </div>
        <details class="notes-edit">
          <summary>📝 Edit note</summary>
          <textarea class="notes-input" rows="3" placeholder="what to change on the re-roll, or why rejected">{_esc(notes)}</textarea>
          <button class="save-notes-btn">Save note</button>
          <span class="save-feedback"></span>
        </details>"""

    return f"""
    <div class="img-card" data-name="{_esc(name)}" data-status="{_esc(status)}" data-tier="{_esc(_tier_of_path(p))}" data-key="{_esc(key)}">
      <a class="thumb" href="{img_url}" target="_blank" rel="noopener">
        <img loading="lazy" src="{img_url}" alt="{_esc(name)}" />
      </a>
      <div class="meta">
        <div class="row1">
          <span class="name">{_esc(name)}</span>
          <span class="chip chip-{_esc(status)}">{_esc(status)}</span>
        </div>
        <div class="row2">
          <span class="aspect">{_esc(aspect)}</span>
          <span class="gen-date">{_esc(generated_at[:10] if generated_at else '')}</span>
          {tag_html}
        </div>
        {dest_html}
        {notes_html}
        {actions_html}
        {prompt_html}
      </div>
    </div>"""


HTML_HEAD = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>SCZ Image Review</title>
<style>
  :root {
    --bg: #0a0a0d;
    --panel: #14141a;
    --border: #2a2a36;
    --accent: #00ff88;
    --accent-dim: #006644;
    --text: #f0f0f0;
    --muted: #8888a0;
    --warn: #ffaa00;
    --danger: #ff4444;
    --info: #00ccff;
  }
  * { box-sizing: border-box; }
  body {
    margin: 0; padding: 1.5em 2em; background: var(--bg); color: var(--text);
    font-family: -apple-system, "Segoe UI", system-ui, sans-serif;
    font-size: 14px; line-height: 1.4;
  }
  header {
    border-bottom: 2px solid var(--border); padding-bottom: 1em; margin-bottom: 1em;
    display: flex; gap: 1.5em; align-items: center; flex-wrap: wrap;
    position: sticky; top: 0; background: var(--bg); z-index: 100;
    padding-top: .8em;
  }
  h1 { color: var(--accent); margin: 0; font-size: 1.5em; }
  h2 { color: var(--accent); border-bottom: 1px solid var(--border);
       padding-bottom: .3em; margin-top: 2em; font-size: 1.2em; }
  .summary { color: var(--muted); }
  .summary .num { color: var(--text); font-weight: bold; }
  .filters { display: flex; gap: .35em; flex-wrap: wrap; }
  .filter-btn {
    background: var(--panel); color: var(--muted); border: 1px solid var(--border);
    padding: .35em .8em; cursor: pointer; border-radius: 3px; font-family: inherit;
    font-size: .85em;
  }
  .filter-btn:hover { color: var(--text); }
  .filter-btn.active { background: var(--accent-dim); color: var(--accent); border-color: var(--accent); }
  #search {
    background: var(--panel); border: 1px solid var(--border); color: var(--text);
    padding: .4em .7em; font-family: inherit; font-size: .9em; min-width: 200px;
  }
  .grid {
    display: grid; gap: 1em;
    grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  }
  .img-card {
    background: var(--panel); border: 1px solid var(--border); border-radius: 6px;
    padding: .6em; display: flex; flex-direction: column; gap: .4em;
  }
  .img-card.hidden { display: none; }
  .thumb {
    display: block; background: #000; border-radius: 4px; overflow: hidden;
    aspect-ratio: 1; max-height: 280px;
  }
  .thumb img {
    width: 100%; height: 100%; object-fit: contain; display: block;
  }
  .meta { display: flex; flex-direction: column; gap: .3em; }
  .row1 { display: flex; align-items: center; justify-content: space-between; gap: .5em; }
  .name { color: var(--text); font-family: monospace; font-weight: bold; font-size: .9em;
          overflow: hidden; text-overflow: ellipsis; }
  .row2 { display: flex; gap: .4em; align-items: center; flex-wrap: wrap; }
  .aspect, .gen-date { color: var(--muted); font-family: monospace; font-size: .8em; }
  .tag {
    color: var(--info); background: rgba(0,204,255,.1); border: 1px solid rgba(0,204,255,.3);
    padding: 0 .35em; border-radius: 3px; font-size: .75em;
  }
  .chip {
    padding: .15em .55em; border-radius: 3px; font-size: .75em; font-weight: bold;
    text-transform: uppercase; letter-spacing: .05em;
  }
  .chip-pending { background: rgba(136,136,160,.15); color: var(--muted); border: 1px solid var(--muted); }
  .chip-provisional { background: rgba(136,204,136,.08); color: #88cc88; border: 1px dashed #88cc88; }
  .chip-keep    { background: rgba(0,255,136,.12); color: var(--accent); border: 1px solid var(--accent); }
  .chip-reject  { background: rgba(255,68,68,.12);  color: var(--danger); border: 1px solid var(--danger); }
  .chip-wired   { background: rgba(0,204,255,.12);  color: var(--info); border: 1px solid var(--info); }
  .chip-untracked { background: rgba(255,170,0,.12); color: var(--warn); border: 1px solid var(--warn); }
  .chip-reroll_requested { background: rgba(255,170,0,.15); color: var(--warn); border: 1px solid var(--warn); }
  .notes { color: var(--warn); font-size: .8em; font-style: italic; }
  .dest { color: var(--info); font-size: .8em; font-family: monospace; }
  .actions { display: flex; gap: .3em; margin-top: .25em; }
  .action-btn {
    flex: 1; background: var(--panel); color: var(--muted); border: 1px solid var(--border);
    padding: .3em .5em; cursor: pointer; border-radius: 3px; font-family: inherit;
    font-size: .8em; transition: background .15s, color .15s, border-color .15s;
  }
  .action-btn:hover { color: var(--text); background: #1c1c24; }
  .action-btn.approve:hover { color: var(--accent); border-color: var(--accent); }
  .action-btn.reroll:hover  { color: var(--warn);   border-color: var(--warn);   }
  .action-btn.reject:hover  { color: var(--danger); border-color: var(--danger); }
  .action-btn.active.approve { color: var(--accent); border-color: var(--accent); background: rgba(0,255,136,.08); }
  .action-btn.active.reroll  { color: var(--warn);   border-color: var(--warn);   background: rgba(255,170,0,.08); }
  .action-btn.active.reject  { color: var(--danger); border-color: var(--danger); background: rgba(255,68,68,.08); }
  .action-btn:disabled { opacity: .5; cursor: not-allowed; }
  .notes-edit { margin-top: .25em; font-size: .8em; }
  .notes-edit summary { cursor: pointer; color: var(--muted); outline: none; }
  .notes-edit summary:hover { color: var(--text); }
  .notes-input {
    width: 100%; margin-top: .3em; background: var(--bg); color: var(--text);
    border: 1px solid var(--border); border-radius: 3px; padding: .3em .5em;
    font-family: inherit; font-size: .85em; resize: vertical;
  }
  .save-notes-btn {
    background: var(--panel); color: var(--muted); border: 1px solid var(--border);
    padding: .25em .7em; margin-top: .3em; cursor: pointer; border-radius: 3px;
    font-family: inherit; font-size: .8em;
  }
  .save-notes-btn:hover { color: var(--accent); border-color: var(--accent); }
  .save-feedback { font-size: .75em; margin-left: .6em; color: var(--accent); }
  .save-feedback.error { color: var(--danger); }
  .prompt { margin-top: .2em; }
  .prompt summary { cursor: pointer; color: var(--muted); font-size: .8em; outline: none; }
  .prompt summary:hover { color: var(--text); }
  .prompt-full { color: var(--muted); font-size: .8em; line-height: 1.45;
                 white-space: pre-wrap; margin: .3em 0 0; padding-top: .3em;
                 border-top: 1px dashed var(--border); font-family: monospace; }
  .prompt-single { padding-top: 0; border-top: none; }
  .tier-stats { color: var(--muted); font-size: .85em; font-weight: normal; }
</style>
</head>
<body>
"""


HTML_TAIL = """
<script>
const cards = Array.from(document.querySelectorAll('.img-card'));
const searchInput = document.getElementById('search');
const filterBtns = Array.from(document.querySelectorAll('.filter-btn'));
let activeStatus = 'all';

function applyFilters() {
  const q = searchInput.value.trim().toLowerCase();
  let shown = 0;
  cards.forEach(c => {
    const name = c.dataset.name.toLowerCase();
    const status = c.dataset.status;
    const matchSearch = !q || name.includes(q) || c.dataset.tier.includes(q);
    const matchStatus = activeStatus === 'all' || status === activeStatus;
    const show = matchSearch && matchStatus;
    c.classList.toggle('hidden', !show);
    if (show) shown++;
  });
  document.getElementById('shown-count').textContent = shown;
  document.querySelectorAll('section').forEach(sec => {
    const visible = sec.querySelectorAll('.img-card:not(.hidden)').length;
    sec.style.display = visible ? '' : 'none';
  });
}

filterBtns.forEach(btn => {
  btn.addEventListener('click', () => {
    filterBtns.forEach(b => b.classList.remove('active'));
    btn.classList.add('active');
    activeStatus = btn.dataset.filter;
    applyFilters();
  });
});

searchInput.addEventListener('input', applyFilters);

// Keyboard: '/' focuses search; Escape clears it
document.addEventListener('keydown', e => {
  if (e.key === '/' && document.activeElement !== searchInput) {
    e.preventDefault();
    searchInput.focus();
    searchInput.select();
  } else if (e.key === 'Escape' && document.activeElement === searchInput) {
    searchInput.value = '';
    applyFilters();
    searchInput.blur();
  }
});

// ============================================================
// Review action buttons — POST status updates to /api/review/<key>
// ============================================================

function updateCardChip(card, newStatus) {
  const chip = card.querySelector('.chip');
  if (!chip) return;
  // Remove old chip-* class
  chip.className = chip.className.replace(/\\bchip-\\S+/g, '').trim();
  chip.classList.add('chip', 'chip-' + newStatus);
  chip.textContent = newStatus;
  card.dataset.status = newStatus;
}

function highlightActiveButton(actionsEl, status) {
  actionsEl.querySelectorAll('.action-btn').forEach(btn => {
    btn.classList.toggle('active', btn.dataset.action === status);
  });
}

async function postReview(key, payload) {
  const r = await fetch('/api/review/' + encodeURIComponent(key), {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });
  if (!r.ok) throw new Error('HTTP ' + r.status + ': ' + await r.text());
  return await r.json();
}

// Wire up Approve/Re-roll/Reject buttons
document.querySelectorAll('.actions').forEach(actionsEl => {
  const key = actionsEl.dataset.key;
  const card = actionsEl.closest('.img-card');
  // Pre-highlight whichever status is currently set
  highlightActiveButton(actionsEl, card.dataset.status);
  actionsEl.querySelectorAll('.action-btn').forEach(btn => {
    btn.addEventListener('click', async () => {
      const status = btn.dataset.action;
      actionsEl.querySelectorAll('.action-btn').forEach(b => b.disabled = true);
      try {
        await postReview(key, { status });
        updateCardChip(card, status);
        highlightActiveButton(actionsEl, status);
      } catch (e) {
        alert('Failed to update review: ' + e.message);
      } finally {
        actionsEl.querySelectorAll('.action-btn').forEach(b => b.disabled = false);
      }
    });
  });
});

// Wire up notes save buttons
document.querySelectorAll('.notes-edit').forEach(editEl => {
  const card = editEl.closest('.img-card');
  const key = card.dataset.key;
  const textarea = editEl.querySelector('.notes-input');
  const saveBtn = editEl.querySelector('.save-notes-btn');
  const feedback = editEl.querySelector('.save-feedback');
  if (!saveBtn) return;
  saveBtn.addEventListener('click', async () => {
    saveBtn.disabled = true;
    feedback.classList.remove('error');
    feedback.textContent = 'saving...';
    try {
      await postReview(key, { notes: textarea.value });
      feedback.textContent = '✓ saved';
      setTimeout(() => { feedback.textContent = ''; }, 2000);
    } catch (e) {
      feedback.classList.add('error');
      feedback.textContent = '✗ ' + e.message;
    } finally {
      saveBtn.disabled = false;
    }
  });
});
</script>
</body>
</html>
"""


def build() -> Path:
    manifest = _load_manifest()
    pngs = _list_firefly_pngs()

    # Auto-index any PNGs that aren't in the manifest yet so they show up
    # in the review UI with action buttons. New entries default to pending.
    added = index_untracked(manifest, pngs)
    if added > 0:
        _save_manifest(manifest)
        print(f"indexed {added} new images into the manifest")

    # Build (tier -> [(path, manifest_entry_or_None)])
    by_tier: dict[str, list[tuple[Path, dict | None]]] = defaultdict(list)
    status_counts: dict[str, int] = defaultdict(int)
    untracked_count = 0
    for p in pngs:
        key = _key_from_path(p)
        entry = manifest.get(key)
        tier = _tier_of_path(p)
        by_tier[tier].append((p, entry))
        if entry:
            status_counts[entry.get("status") or "pending"] += 1
        else:
            untracked_count += 1
            status_counts["untracked"] += 1

    total = len(pngs)

    # Header
    summary_html = (
        f'<div class="summary">'
        f'<span class="num">{total}</span> images · '
        f'<span class="num" id="shown-count">{total}</span> shown · '
    )
    for s in ("pending", "keep", "reject", "wired", "untracked"):
        if status_counts.get(s):
            summary_html += (
                f'<span class="chip chip-{s}">{s}: {status_counts[s]}</span> '
            )
    summary_html += "</div>"

    filter_html = (
        '<div class="filters">'
        '<button class="filter-btn active" data-filter="all">all</button>'
    )
    for s in ("pending", "keep", "reject", "wired", "untracked"):
        if status_counts.get(s):
            filter_html += (
                f'<button class="filter-btn" data-filter="{s}">{s}</button>'
            )
    filter_html += "</div>"

    search_html = (
        '<input type="search" id="search" '
        'placeholder="search by name/tier (press / to focus)" />'
    )

    body = HTML_HEAD + f"""
<header>
  <h1>★ SCZ Image Review</h1>
  {summary_html}
  {filter_html}
  {search_html}
</header>
"""

    # Sections per tier in alphabetical order
    for tier in sorted(by_tier):
        items = by_tier[tier]
        section_status_counts: dict[str, int] = defaultdict(int)
        for _, e in items:
            section_status_counts[(e or {}).get("status") or "untracked"] += 1
        stats_parts = " · ".join(
            f"{s}: {n}" for s, n in section_status_counts.items() if n
        )
        body += f"""
<section>
  <h2>{_esc(tier)} <span class="tier-stats">— {len(items)} images · {_esc(stats_parts)}</span></h2>
  <div class="grid">
"""
        for p, entry in items:
            body += _render_image_card(p, entry)
        body += "  </div>\n</section>\n"

    body += HTML_TAIL
    OUT_PATH.write_text(body, encoding="utf-8")
    return OUT_PATH


if __name__ == "__main__":
    p = build()
    n_imgs = len(_list_firefly_pngs())
    print(f"wrote {p} ({n_imgs} images indexed)")
    print()
    print("Start the review server (replaces python -m http.server):")
    print(f"  cd {ROOT}")
    print("  .venv/Scripts/python.exe tools/image_review_server.py")
    print("Then open: http://localhost:8770/tools/image_review.html")
    print()
    print("Approve/Re-roll/Reject buttons POST back to the manifest at")
    print("  assets/generated_drafts/firefly/_manifest.json")
    print("Claude reads this manifest in future sessions to know which")
    print("images to wire in, which to re-generate, and which to drop.")
