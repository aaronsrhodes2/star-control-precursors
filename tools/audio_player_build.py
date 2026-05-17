"""Generate a single-file HTML audio player for Aaron's review pass.

Scans assets/music/ (every context dir with a manifest.json) and
assets/sfx/ (every .wav under it) and emits a self-contained HTML
page with:
  - Per music context: "play all stems" sync button + per-stem volume
    sliders + per-stem solo button. Plays as the game would mix them.
  - Per SFX category: one-click preview + a (loop) indicator where the
    spec marks it.
  - Spec metadata visible: key/bpm/description/SC2 idiom for music;
    prompt text for SFX.

The page expects to be served from the project root (relative paths
under assets/music and assets/sfx). Pair this build script with:
    python -m http.server 8770
in the project root, then navigate to
    http://localhost:8770/tools/audio_player.html

Re-run this script any time you generate new audio.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MUSIC_ROOT = ROOT / "assets" / "music"
SFX_ROOT = ROOT / "assets" / "sfx"
OUT_PATH = Path(__file__).resolve().parent / "audio_player.html"


def _load_manifest(ctx_dir: Path) -> dict:
    p = ctx_dir / "manifest.json"
    if not p.exists():
        return {}
    return json.loads(p.read_text(encoding="utf-8"))


def _list_music_contexts() -> list[tuple[Path, dict]]:
    """Return (ctx_dir, manifest) for every music context found."""
    if not MUSIC_ROOT.is_dir():
        return []
    items: list[tuple[Path, dict]] = []
    for d in sorted(MUSIC_ROOT.iterdir()):
        if d.is_dir():
            items.append((d, _load_manifest(d)))
    return items


def _list_sfx_groups() -> dict[str, list[Path]]:
    """Group SFX paths by their immediate parent dir."""
    if not SFX_ROOT.is_dir():
        return {}
    groups: dict[str, list[Path]] = {}
    for p in sorted(SFX_ROOT.rglob("*.wav")):
        rel_parent = p.parent.relative_to(SFX_ROOT)
        key = str(rel_parent).replace("\\", "/")
        groups.setdefault(key, []).append(p)
    return groups


def _try_lookup_sfx_spec(name: str, out_subdir: str) -> dict | None:
    """Pull the prompt + duration_s + loop flag from audio_sfx_specs."""
    try:
        sys.path.insert(0, str(ROOT / "tools"))
        from audio_sfx_specs import ALL_SFX  # type: ignore
    except Exception:
        return None
    target_subdir = out_subdir
    for s in ALL_SFX:
        if s.name == name and s.out_subdir == target_subdir:
            return {
                "prompt": s.prompt,
                "duration_s": s.duration_s,
                "loop": s.loop,
                "category": s.category,
                "species_id": s.species_id,
            }
    return None


def _audio_url(asset_path: Path) -> str:
    """Project-root-relative URL the served HTML can hit."""
    rel = asset_path.relative_to(ROOT).as_posix()
    return f"../{rel}"


def _esc(s: str) -> str:
    return (s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            .replace('"', "&quot;").replace("'", "&#39;"))


def _render_music_section(ctx_dir: Path, manifest: dict) -> str:
    name = ctx_dir.name
    key = manifest.get("key", "?")
    bpm = manifest.get("bpm", "?")
    desc = manifest.get("description", "")
    category = manifest.get("category", "")
    dur = manifest.get("duration_s", "?")

    audio_files = (
        sorted(ctx_dir.glob("*.mp3"))
        + sorted(ctx_dir.glob("*.ogg"))
        + sorted(ctx_dir.glob("*.wav"))
    )
    # Order stems: bass, percussion, pad, lead, ambient, drone, pulse, texture,
    # then any state-driven or extra stems alphabetical.
    pref_order = ["bass", "percussion", "pad", "lead", "ambient",
                  "drone", "pulse", "texture"]
    def stem_sort(p: Path):
        try:
            return (0, pref_order.index(p.stem), p.stem)
        except ValueError:
            return (1, 0, p.stem)
    audio_files.sort(key=stem_sort)

    if not audio_files:
        return ""

    stems_html = []
    for p in audio_files:
        url = _audio_url(p)
        stem_name = p.stem
        is_state = stem_name not in pref_order
        cls = "stem state-stem" if is_state else "stem"
        stems_html.append(f"""
        <div class="{cls}">
          <label>{_esc(stem_name)}{' (state)' if is_state else ''}</label>
          <input type="range" min="0" max="1" step="0.01" value="0.85"
                 oninput="setStemVol('{_esc(name)}', '{_esc(stem_name)}', this.value); this.nextElementSibling.textContent = (+this.value).toFixed(2);" />
          <span class="vol-readout">0.85</span>
          <button class="solo-btn" onclick="soloStem('{_esc(name)}', '{_esc(stem_name)}')">solo</button>
          <button class="mute-btn" onclick="toggleMute('{_esc(name)}', '{_esc(stem_name)}', this)">mute</button>
          <audio data-ctx="{_esc(name)}" data-stem="{_esc(stem_name)}"
                 src="{url}" preload="auto" loop></audio>
        </div>""")

    return f"""
    <section class="music-ctx" data-ctx="{_esc(name)}">
      <h3>{_esc(name)} <span class="meta">— {_esc(str(key))} / {_esc(str(bpm))} bpm / {_esc(str(dur))}s loop</span></h3>
      <p class="desc">{_esc(desc)}</p>
      <p class="category">[{_esc(category)}]</p>
      <div class="ctx-ctrl">
        <button class="play-btn" onclick="playAllStems('{_esc(name)}')">▶ Play all stems</button>
        <button class="stop-btn" onclick="stopAllStems('{_esc(name)}')">⏹ Stop</button>
        <button class="reset-btn" onclick="resetStems('{_esc(name)}')">reset volumes</button>
      </div>
      <div class="stems">{''.join(stems_html)}
      </div>
    </section>"""


def _render_sfx_group(group_label: str, paths: list[Path]) -> str:
    items_html = []
    for p in paths:
        spec = _try_lookup_sfx_spec(p.stem, group_label) or {}
        prompt = spec.get("prompt", "")
        dur = spec.get("duration_s", "")
        loop_flag = spec.get("loop", False)
        cat = spec.get("category", "")
        items_html.append(f"""
        <div class="sfx-item{' loopable' if loop_flag else ''}">
          <button class="play-sfx" onclick="playSfx(this)">▶</button>
          <span class="sfx-name">{_esc(p.stem)}</span>
          <span class="sfx-meta">{_esc(str(dur))}s{' · LOOP' if loop_flag else ''}{(' · ' + _esc(cat)) if cat else ''}</span>
          <span class="sfx-prompt">{_esc(prompt)}</span>
          <audio src="{_audio_url(p)}" preload="metadata" {'loop' if loop_flag else ''}></audio>
        </div>""")
    return f"""
    <section class="sfx-group">
      <h3>{_esc(group_label)} <span class="meta">— {len(paths)} sound{'s' if len(paths)!=1 else ''}</span></h3>
      <div class="sfx-list">{''.join(items_html)}
      </div>
    </section>"""


HTML_HEAD = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>SCZ Audio Review</title>
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
  }
  * { box-sizing: border-box; }
  body {
    margin: 0; padding: 1.5em 2em; background: var(--bg); color: var(--text);
    font-family: -apple-system, "Segoe UI", system-ui, sans-serif;
    font-size: 14px; line-height: 1.4;
  }
  header {
    border-bottom: 2px solid var(--border); padding-bottom: 1em; margin-bottom: 1em;
    display: flex; gap: 1.5em; align-items: baseline; flex-wrap: wrap;
  }
  h1 { color: var(--accent); margin: 0; font-size: 1.6em; }
  h2 { color: var(--accent); border-bottom: 1px solid var(--border); padding-bottom: .3em; margin-top: 2em; }
  h3 { color: var(--text); margin-bottom: .2em; }
  .meta { color: var(--muted); font-weight: normal; font-size: .85em; }
  .desc { color: var(--text); margin: .2em 0; }
  .category { color: var(--warn); margin: 0 0 .8em; font-size: .85em; }
  .global-ctrl { display: flex; gap: 1em; align-items: center; }
  .global-ctrl label { color: var(--muted); }
  .music-ctx, .sfx-group {
    background: var(--panel); border: 1px solid var(--border);
    border-radius: 6px; padding: 1em 1.2em; margin-bottom: 1em;
  }
  .ctx-ctrl { display: flex; gap: .5em; margin: .5em 0; }
  button {
    background: var(--accent-dim); color: var(--accent); border: 1px solid var(--accent-dim);
    padding: .35em .8em; cursor: pointer; border-radius: 3px; font-family: inherit;
    font-size: .85em;
  }
  button:hover { background: var(--accent); color: var(--bg); }
  button.stop-btn, button.reset-btn { color: var(--muted); border-color: var(--border); background: var(--panel); }
  button.stop-btn:hover, button.reset-btn:hover { color: var(--text); }
  .stems { margin-top: .3em; }
  .stem {
    display: grid;
    grid-template-columns: 110px 240px 50px 50px 50px;
    gap: .5em; align-items: center; padding: .15em 0;
  }
  .stem label { color: var(--text); font-family: monospace; }
  .state-stem label { color: var(--warn); font-weight: bold; }
  .vol-readout { font-family: monospace; color: var(--muted); font-size: .85em; }
  input[type="range"] { accent-color: var(--accent); width: 100%; }
  .sfx-list { display: flex; flex-direction: column; gap: .25em; margin-top: .5em; }
  .sfx-item {
    display: grid;
    grid-template-columns: 50px 240px 130px 1fr;
    gap: .5em; align-items: center; padding: .25em .5em;
    border-left: 2px solid var(--border);
  }
  .sfx-item.loopable { border-left-color: var(--warn); }
  .sfx-name { font-family: monospace; color: var(--text); }
  .sfx-meta { color: var(--muted); font-size: .85em; font-family: monospace; }
  .sfx-prompt { color: var(--muted); font-size: .85em; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
  .play-sfx { width: 40px; }
  audio { display: none; }
  .playing { background: var(--accent); color: var(--bg) !important; }
  .summary { color: var(--muted); margin-bottom: 1em; }
  details { margin-top: .5em; }
  details summary { cursor: pointer; color: var(--accent); font-size: .85em; }
</style>
</head>
<body>
<header>
  <h1>★ SCZ Audio Review</h1>
  <div class="global-ctrl">
    <label>Master volume</label>
    <input type="range" id="master-vol" min="0" max="1" step="0.05" value="0.7"
           oninput="setMasterVolume(this.value)" style="width: 160px;" />
    <span id="master-readout">0.70</span>
  </div>
  <button onclick="stopEverything()" class="stop-btn">⏹ STOP EVERYTHING</button>
</header>
"""


HTML_TAIL = """
<script>
// All <audio> on the page. Used for global stop + master volume scaling.
const allAudio = () => Array.from(document.querySelectorAll('audio'));
let masterVol = 0.7;

function setMasterVolume(v) {
  masterVol = +v;
  document.getElementById('master-readout').textContent = masterVol.toFixed(2);
  // Re-apply per-stem volumes since their saved level multiplies by master.
  document.querySelectorAll('.music-ctx').forEach(ctx => {
    ctx.querySelectorAll('audio').forEach(a => {
      const sv = +a.dataset.stemVol || 0.85;
      a.volume = Math.max(0, Math.min(1, sv * masterVol));
    });
  });
  document.querySelectorAll('.sfx-item').forEach(item => {
    const a = item.querySelector('audio');
    if (a) a.volume = masterVol;
  });
}

function _ctxAudios(ctxName) {
  return Array.from(document.querySelectorAll(`audio[data-ctx="${ctxName}"]`));
}

function setStemVol(ctxName, stemName, v) {
  const audios = _ctxAudios(ctxName).filter(a => a.dataset.stem === stemName);
  audios.forEach(a => {
    a.dataset.stemVol = v;
    a.volume = Math.max(0, Math.min(1, (+v) * masterVol));
  });
}

function playAllStems(ctxName) {
  stopEverythingExcept(ctxName);
  const audios = _ctxAudios(ctxName);
  audios.forEach(a => {
    a.currentTime = 0;
    if (!a.dataset.stemVol) a.dataset.stemVol = 0.85;
    a.volume = (+a.dataset.stemVol) * masterVol;
    a.play().catch(e => console.warn('play failed:', a.src, e));
  });
}

function stopAllStems(ctxName) {
  _ctxAudios(ctxName).forEach(a => { a.pause(); a.currentTime = 0; });
}

function soloStem(ctxName, stemName) {
  // Pause the others in this context, play just the target.
  stopEverythingExcept(ctxName);
  const audios = _ctxAudios(ctxName);
  audios.forEach(a => {
    if (a.dataset.stem === stemName) {
      a.currentTime = 0;
      a.volume = (+a.dataset.stemVol || 0.85) * masterVol;
      a.play().catch(e => console.warn(e));
    } else {
      a.pause();
    }
  });
}

function toggleMute(ctxName, stemName, btn) {
  const audios = _ctxAudios(ctxName).filter(a => a.dataset.stem === stemName);
  audios.forEach(a => {
    a.muted = !a.muted;
    btn.textContent = a.muted ? 'unmute' : 'mute';
    btn.classList.toggle('playing', a.muted);
  });
}

function resetStems(ctxName) {
  document.querySelectorAll(`.music-ctx[data-ctx="${ctxName}"] .stem`).forEach(stem => {
    const range = stem.querySelector('input[type="range"]');
    const readout = stem.querySelector('.vol-readout');
    const audio = stem.querySelector('audio');
    range.value = 0.85;
    readout.textContent = '0.85';
    audio.muted = false;
    audio.dataset.stemVol = 0.85;
    audio.volume = 0.85 * masterVol;
    const muteBtn = stem.querySelector('.mute-btn');
    muteBtn.textContent = 'mute';
    muteBtn.classList.remove('playing');
  });
}

function playSfx(btn) {
  const audio = btn.parentElement.querySelector('audio');
  // For non-looping SFX, stop any other SFX currently playing.
  document.querySelectorAll('.sfx-item audio').forEach(a => {
    if (a !== audio && !a.loop) { a.pause(); a.currentTime = 0; }
  });
  audio.currentTime = 0;
  audio.volume = masterVol;
  if (audio.loop && !audio.paused) {
    audio.pause();
    audio.currentTime = 0;
    btn.classList.remove('playing');
    btn.textContent = '▶';
  } else {
    audio.play().catch(e => console.warn(e));
    if (audio.loop) {
      btn.classList.add('playing');
      btn.textContent = '⏸';
    }
  }
}

function stopEverything() {
  allAudio().forEach(a => { a.pause(); a.currentTime = 0; });
  document.querySelectorAll('.play-sfx.playing').forEach(b => {
    b.classList.remove('playing'); b.textContent = '▶';
  });
}

function stopEverythingExcept(ctxName) {
  document.querySelectorAll('.music-ctx').forEach(ctx => {
    if (ctx.dataset.ctx !== ctxName) {
      ctx.querySelectorAll('audio').forEach(a => { a.pause(); a.currentTime = 0; });
    }
  });
}

// On load, give every <audio> the initial stem volume so master scaling works.
document.querySelectorAll('audio[data-stem]').forEach(a => {
  a.dataset.stemVol = 0.85;
  a.volume = 0.85 * masterVol;
});
</script>
</body>
</html>
"""


def build() -> Path:
    contexts = _list_music_contexts()
    sfx_groups = _list_sfx_groups()

    music_sections = []
    for ctx_dir, manifest in contexts:
        s = _render_music_section(ctx_dir, manifest)
        if s.strip():
            music_sections.append(s)

    sfx_sections = []
    for group_label, paths in sfx_groups.items():
        sfx_sections.append(_render_sfx_group(group_label, paths))

    total_audio_files = sum(
        len(list(d.glob("*.mp3"))) + len(list(d.glob("*.wav"))) + len(list(d.glob("*.ogg")))
        for d, _ in contexts
    ) + sum(len(paths) for paths in sfx_groups.values())

    summary = (
        f'<div class="summary">'
        f'{len(contexts)} music context{"s" if len(contexts)!=1 else ""} · '
        f'{sum(len(paths) for paths in sfx_groups.values())} SFX · '
        f'{total_audio_files} audio files total'
        f'</div>'
    )

    body = HTML_HEAD + summary
    if music_sections:
        body += "<h2>Music</h2>" + "".join(music_sections)
    else:
        body += '<p class="summary">(no music yet — run audio_generate.py --round N)</p>'
    if sfx_sections:
        body += "<h2>SFX</h2>" + "".join(sfx_sections)
    else:
        body += '<p class="summary">(no SFX yet — run audio_sfx_generate.py --round N)</p>'
    body += HTML_TAIL

    OUT_PATH.write_text(body, encoding="utf-8")
    return OUT_PATH


if __name__ == "__main__":
    p = build()
    print(f"wrote {p}")
    print()
    print("Serve from the project root:")
    print(f"  cd {ROOT}")
    print("  python -m http.server 8770")
    print("Then open: http://localhost:8770/tools/audio_player.html")
