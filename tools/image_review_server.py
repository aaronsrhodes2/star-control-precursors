"""Image-review HTTP server — drop-in replacement for `python -m http.server`.

Serves project files identically to `python -m http.server 8770` AND exposes
POST endpoints that write Aaron's approve/reroll/reject decisions back into
`assets/generated_drafts/firefly/_manifest.json`.

Why: the manifest is the durable contract between Aaron (reviewing the
generated images at http://localhost:8770/tools/image_review.html) and Claude
(reading the manifest in a future session to know which images to keep,
which to re-generate with adjusted prompts, and which to discard).

Standard-library only — no Flask, no requirements.txt entry needed. Just:

    cd D:/Aaron/development/star-control-precursors
    .venv/Scripts/python.exe tools/image_review_server.py

Then open http://localhost:8770/tools/image_review.html and click the
Approve / Re-roll / Reject buttons on each card. Notes are saved per-card.

API (POST application/json):
    POST /api/review/<image_key>
      body: { "status"?: "keep"|"reroll_requested"|"reject"|"wired", "notes"?: str }
      effect: updates manifest[<image_key>] in place, plus sets
              reviewed_at = current UTC ISO timestamp
      response: { "ok": true, "entry": { ... updated entry ... } }

    POST /api/review-all
      body: { "<key1>": {"status":..., "notes":...}, "<key2>": {...} }
      effect: batch update
      response: { "ok": true, "updated": [keys...] }

    GET /api/manifest
      returns the current manifest as JSON (useful for the UI to refresh)
"""

from __future__ import annotations

import http.server
import json
import socketserver
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MANIFEST = ROOT / "assets" / "generated_drafts" / "firefly" / "_manifest.json"

PORT = 8770

VALID_STATUSES = {"pending", "keep", "reroll_requested", "reject", "wired"}


def _load_manifest() -> dict:
    if not MANIFEST.exists():
        return {}
    return json.loads(MANIFEST.read_text(encoding="utf-8"))


def _save_manifest(manifest: dict) -> None:
    # Write atomically to avoid corrupting the file mid-write
    tmp = MANIFEST.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")
    tmp.replace(MANIFEST)


class ReviewHandler(http.server.SimpleHTTPRequestHandler):
    """Serves project files like SimpleHTTPRequestHandler + adds /api routes."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(ROOT), **kwargs)

    def _send_json(self, status: int, payload: dict) -> None:
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def _read_json_body(self) -> dict:
        length = int(self.headers.get("Content-Length", 0))
        if length == 0:
            return {}
        raw = self.rfile.read(length).decode("utf-8")
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            return {}

    def do_GET(self):  # noqa: N802
        if self.path == "/api/manifest":
            self._send_json(200, _load_manifest())
            return
        # Everything else: static file serving
        super().do_GET()

    def do_POST(self):  # noqa: N802
        if self.path.startswith("/api/review/"):
            key = self.path[len("/api/review/"):]
            data = self._read_json_body()
            manifest = _load_manifest()
            if key not in manifest:
                self._send_json(404, {"error": f"unknown image key: {key}"})
                return
            entry = manifest[key]
            if "status" in data:
                if data["status"] not in VALID_STATUSES:
                    self._send_json(400, {
                        "error": f"invalid status {data['status']!r}, "
                                 f"want one of {sorted(VALID_STATUSES)}"})
                    return
                entry["status"] = data["status"]
            if "notes" in data:
                entry["notes"] = data["notes"]
            entry["reviewed_at"] = datetime.now(timezone.utc).isoformat()
            _save_manifest(manifest)
            self._send_json(200, {"ok": True, "entry": entry, "key": key})
            return

        if self.path == "/api/review-all":
            data = self._read_json_body()
            if not isinstance(data, dict):
                self._send_json(400, {"error": "body must be a JSON object"})
                return
            manifest = _load_manifest()
            now = datetime.now(timezone.utc).isoformat()
            updated = []
            for key, patch in data.items():
                if key not in manifest or not isinstance(patch, dict):
                    continue
                entry = manifest[key]
                if "status" in patch and patch["status"] in VALID_STATUSES:
                    entry["status"] = patch["status"]
                if "notes" in patch:
                    entry["notes"] = patch["notes"]
                entry["reviewed_at"] = now
                updated.append(key)
            _save_manifest(manifest)
            self._send_json(200, {"ok": True, "updated": updated})
            return

        self._send_json(405, {"error": "method not allowed"})

    # Quieter logs (the build serves a lot of PNGs)
    def log_message(self, fmt, *args):  # noqa: N802
        if not self.path.startswith("/api/"):
            return
        sys.stderr.write(f"[review] {fmt % args}\n")


def main() -> int:
    if not MANIFEST.exists():
        sys.stderr.write(
            f"[review] WARNING: manifest not found at {MANIFEST}\n"
            f"[review] approve/reject buttons will 404 until images are indexed.\n"
        )
    with socketserver.ThreadingTCPServer(("127.0.0.1", PORT), ReviewHandler) as srv:
        srv.allow_reuse_address = True
        print(f"[review] serving project at http://localhost:{PORT}/")
        print(f"[review] open http://localhost:{PORT}/tools/image_review.html")
        print(f"[review] manifest: {MANIFEST}")
        print("[review] press Ctrl-C to stop")
        try:
            srv.serve_forever()
        except KeyboardInterrupt:
            print("\n[review] shutting down")
    return 0


if __name__ == "__main__":
    sys.exit(main())
