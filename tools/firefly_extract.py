"""Extract clean Firefly prompt body from a tier1_*/*.txt file.

Strips:
 - all lines starting with `#` (header comments)
 - everything from "ARTICULATION BRIEF" onwards (rig spec, dev-only)
 - leading/trailing blank lines

Writes the result to stdout as UTF-8.
"""

import sys, pathlib

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
sys.stdout.buffer.write(text.encode('utf-8'))
