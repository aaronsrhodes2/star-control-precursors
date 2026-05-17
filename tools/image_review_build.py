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


def _list_firefly_pngs() -> list[Path]:
    if not FIREFLY_DIR.is_dir():
        return []
    return sorted(FIREFLY_DIR.rglob("*.png"))


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
    rel = asset_path.relative_to(ROOT).as_posix()
    return f"../{rel}"


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

    return f"""
    <div class="img-card" data-name="{_esc(name)}" data-status="{_esc(status)}" data-tier="{_esc(_tier_of_path(p))}">
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
  .chip-keep    { background: rgba(0,255,136,.12); color: var(--accent); border: 1px solid var(--accent); }
  .chip-reject  { background: rgba(255,68,68,.12);  color: var(--danger); border: 1px solid var(--danger); }
  .chip-wired   { background: rgba(0,204,255,.12);  color: var(--info); border: 1px solid var(--info); }
  .chip-untracked { background: rgba(255,170,0,.12); color: var(--warn); border: 1px solid var(--warn); }
  .notes { color: var(--warn); font-size: .8em; font-style: italic; }
  .dest { color: var(--info); font-size: .8em; font-family: monospace; }
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
</script>
</body>
</html>
"""


def build() -> Path:
    manifest = _load_manifest()
    pngs = _list_firefly_pngs()

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
    print("Serve from the project root (same server the audio player uses):")
    print(f"  cd {ROOT}")
    print("  python -m http.server 8770")
    print("Then open: http://localhost:8770/tools/image_review.html")
