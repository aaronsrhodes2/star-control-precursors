"""Emit a JS snippet that sets the Firefly textarea to a prompt-file body.

Usage:
  python tools/firefly_jspayload.py path/to/prompt.txt

Writes a self-contained JS snippet to stdout that:
  1. Sets window.__sczTextarea.value using window.__sczSetter
  2. Dispatches an 'input' event (React-compatible)
  3. Returns a small status JSON
"""

import sys, pathlib, json

fn = sys.argv[1]
raw = pathlib.Path(fn).read_text(encoding='utf-8')
lines = raw.splitlines()
body = []
for line in lines:
    if line.startswith('#'):
        continue
    if line.strip().startswith('ARTICULATION BRIEF'):
        break
    body.append(line)
text = '\n'.join(body).strip()
js_literal = json.dumps(text, ensure_ascii=False)

snippet = (
    "const v = " + js_literal + ";\n"
    "window.__sczSetter.call(window.__sczTextarea, v);\n"
    "window.__sczTextarea.dispatchEvent(new Event('input', { bubbles: true }));\n"
    "JSON.stringify({ ok: true, len: v.length, prefix: v.slice(0, 60) });"
)
sys.stdout.buffer.write(snippet.encode('utf-8'))
