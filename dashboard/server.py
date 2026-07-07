#!/usr/bin/env python3
"""Framework Console — a deterministic visibility dashboard for the agent-framework.

Reads the four ledgers the runtime kernel emits (wave-status.yaml,
metrics-ledger.jsonl, integrity-register.jsonl, decisions-queue.yaml) plus an
optional raid-log.yaml, and serves 9 read-only views over them. The only writes
this server performs are LOCAL: an append-only decisions log and a resolved-items
overlay under ``local-store/`` — never back to the sample state, never off-box.

Data source resolution (in priority order):
  1. STATE_DIR env var, if set, pointing at a real ``runtime-state/`` root that
     contains one sub-directory per engagement (as StateEmitter writes them).
  2. the bundled ``sample-state/engagements/`` fixtures (default), so the
     dashboard renders out of the box with no runtime attached.

BYOK: this server never asks for, stores, or transmits any API key. Credentials
are entered on the client Credentials screen and kept in the browser's
localStorage only. Nothing here reads or forwards a secret.

Run:  python3 server.py [--port 8000]     (stdlib only; pyyaml required)
"""
from __future__ import annotations

import argparse
import json
import os
import posixpath
import urllib.parse
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(HERE, "static")
LOCAL_STORE = os.path.join(HERE, "local-store")
DECISIONS_LOG = os.path.join(LOCAL_STORE, "decisions-log.jsonl")
RESOLVED_OVERLAY = os.path.join(LOCAL_STORE, "resolved.json")

os.makedirs(LOCAL_STORE, exist_ok=True)


def state_root() -> str:
    env = os.environ.get("STATE_DIR")
    if env and os.path.isdir(env):
        return env
    return os.path.join(HERE, "sample-state", "engagements")


def _read_yaml(path: str) -> dict:
    if not os.path.exists(path):
        return {}
    with open(path, encoding="utf-8") as fh:
        return yaml.safe_load(fh) or {}


def _read_jsonl(path: str) -> list:
    if not os.path.exists(path):
        return []
    out = []
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line:
                try:
                    out.append(json.loads(line))
                except json.JSONDecodeError:
                    pass
    return out


def _load_resolved() -> dict:
    if not os.path.exists(RESOLVED_OVERLAY):
        return {}
    try:
        with open(RESOLVED_OVERLAY, encoding="utf-8") as fh:
            return json.load(fh)
    except (json.JSONDecodeError, OSError):
        return {}


def _save_resolved(data: dict) -> None:
    tmp = RESOLVED_OVERLAY + ".tmp"
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(data, fh, indent=2)
    os.replace(tmp, RESOLVED_OVERLAY)


def _is_using_sample() -> bool:
    return not (os.environ.get("STATE_DIR") and os.path.isdir(os.environ["STATE_DIR"]))


# --- RAG roll-up: worst-of the wave states (brief view 6) --------------------
# order: higher = worse. Deterministic, no AI.
_RAG_RED = {"DEAD", "GATE_BLOCKED", "TIMED_OUT"}
_RAG_AMBER = {"BLOCKED", "PAUSED", "AWAITING_APPROVAL"}


def rag_for_waves(waves: dict) -> str:
    states = {(w or {}).get("state") for w in (waves or {}).values()}
    if states & _RAG_RED:
        return "RED"
    if states & _RAG_AMBER:
        return "AMBER"
    return "GREEN"


def build_state() -> dict:
    root = state_root()
    resolved = _load_resolved()
    engagements = []
    if os.path.isdir(root):
        for name in sorted(os.listdir(root)):
            edir = os.path.join(root, name)
            if not os.path.isdir(edir):
                continue
            wave_status = _read_yaml(os.path.join(edir, "wave-status.yaml"))
            metrics = _read_jsonl(os.path.join(edir, "metrics-ledger.jsonl"))
            integrity = _read_jsonl(os.path.join(edir, "integrity-register.jsonl"))
            decisions = _read_yaml(os.path.join(edir, "decisions-queue.yaml"))
            raid = _read_yaml(os.path.join(edir, "raid-log.yaml"))

            # mark resolved decision items from the local overlay
            open_items = (decisions or {}).get("open_items") or []
            for item in open_items:
                rid = item.get("id")
                if rid and rid in resolved.get(name, {}):
                    item["resolved"] = resolved[name][rid]

            docs = []
            ddir = os.path.join(edir, "documents")
            if os.path.isdir(ddir):
                for fn in sorted(os.listdir(ddir)):
                    if fn.startswith("."):
                        continue
                    docs.append(fn)

            # interview surface: transcript + evidence locker (read-only)
            has_transcript = os.path.isfile(
                os.path.join(edir, "interview", "transcript.md"))
            locker = _read_yaml(
                os.path.join(edir, "evidence-locker", "locker-index.yaml"))
            locker_items = (locker or {}).get("items") or []

            engagements.append({
                "id": name,
                "wave_status": wave_status,
                "metrics": metrics,
                "integrity": integrity,
                "decisions": decisions,
                "raid": raid,
                "documents": docs,
                "has_transcript": has_transcript,
                "locker": locker_items,
                "rag": rag_for_waves((wave_status or {}).get("waves") or {}),
            })
    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "using_sample": _is_using_sample(),
        "state_root": root,
        "engagements": engagements,
    }


def read_document(engagement: str, name: str) -> dict | None:
    # sanitise: no traversal
    safe = posixpath.normpath("/" + name).lstrip("/")
    if safe != name or ".." in safe:
        return None
    path = os.path.join(state_root(), engagement, "documents", safe)
    if not os.path.isfile(path):
        return None
    with open(path, encoding="utf-8") as fh:
        content = fh.read()
    ext = os.path.splitext(name)[1].lower().lstrip(".")
    return {"engagement": engagement, "name": name, "ext": ext, "content": content}


ATTACHMENT_TYPES = {
    ".pdf": "application/pdf",
    ".png": "image/png",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".csv": "text/csv; charset=utf-8",
    ".md": "text/plain; charset=utf-8",
    ".txt": "text/plain; charset=utf-8",
    ".yaml": "text/plain; charset=utf-8",
    ".xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
}


def read_transcript(engagement: str) -> dict | None:
    path = os.path.join(state_root(), engagement, "interview", "transcript.md")
    if not os.path.isfile(path):
        return None
    with open(path, encoding="utf-8") as fh:
        return {"engagement": engagement, "content": fh.read()}


def attachment_path(engagement: str, name: str) -> str | None:
    # sanitise: no traversal (same rule as read_document)
    safe = posixpath.normpath("/" + name).lstrip("/")
    if safe != name or ".." in safe:
        return None
    path = os.path.join(state_root(), engagement, "evidence-locker", safe)
    return path if os.path.isfile(path) else None


class Handler(BaseHTTPRequestHandler):
    server_version = "FrameworkConsole/0.1"

    def log_message(self, fmt, *args):  # quieter logs
        pass

    def _send(self, code: int, body: bytes, ctype: str):
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def _json(self, obj, code=200):
        self._send(code, json.dumps(obj).encode("utf-8"), "application/json; charset=utf-8")

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        qs = urllib.parse.parse_qs(parsed.query)

        if path in ("/", "/index.html"):
            return self._serve_static("index.html")
        if path == "/api/state":
            return self._json(build_state())
        if path == "/api/document":
            eng = (qs.get("engagement") or [""])[0]
            name = (qs.get("name") or [""])[0]
            doc = read_document(eng, name)
            if doc is None:
                return self._json({"error": "not found"}, 404)
            return self._json(doc)
        if path == "/api/transcript":
            eng = (qs.get("engagement") or [""])[0]
            doc = read_transcript(eng)
            if doc is None:
                return self._json({"error": "not found"}, 404)
            return self._json(doc)
        if path == "/api/attachment":
            eng = (qs.get("engagement") or [""])[0]
            name = (qs.get("name") or [""])[0]
            full = attachment_path(eng, name)
            if full is None:
                return self._json({"error": "not found"}, 404)
            ctype = ATTACHMENT_TYPES.get(
                os.path.splitext(full)[1].lower(), "application/octet-stream")
            with open(full, "rb") as fh:
                data = fh.read()
            self.send_response(200)
            self.send_header("Content-Type", ctype)
            self.send_header("Content-Disposition",
                             f'inline; filename="{os.path.basename(full)}"')
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)
            return None
        if path == "/api/decisions-log":
            return self._json({"entries": _read_jsonl(DECISIONS_LOG)})
        if path.startswith("/static/"):
            return self._serve_static(path[len("/static/"):])
        return self._json({"error": "not found"}, 404)

    def _serve_static(self, rel: str):
        safe = posixpath.normpath("/" + rel).lstrip("/")
        full = os.path.join(STATIC_DIR, safe)
        if not full.startswith(STATIC_DIR) or not os.path.isfile(full):
            return self._json({"error": "not found"}, 404)
        ctype = {
            ".html": "text/html; charset=utf-8",
            ".js": "application/javascript; charset=utf-8",
            ".css": "text/css; charset=utf-8",
            ".png": "image/png",
            ".svg": "image/svg+xml",
        }.get(os.path.splitext(full)[1], "application/octet-stream")
        with open(full, "rb") as fh:
            return self._send(200, fh.read(), ctype)

    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)
        if parsed.path != "/api/decision":
            return self._json({"error": "not found"}, 404)
        length = int(self.headers.get("Content-Length") or 0)
        try:
            payload = json.loads(self.rfile.read(length) or b"{}")
        except json.JSONDecodeError:
            return self._json({"error": "bad json"}, 400)

        engagement = payload.get("engagement")
        item_id = payload.get("item_id")
        action = payload.get("action")  # APPROVE | COMMENT | SAVE
        comment = payload.get("comment", "")
        document = payload.get("document")
        if not engagement or not item_id or action not in ("APPROVE", "COMMENT", "SAVE"):
            return self._json({"error": "engagement, item_id and a valid action are required"}, 400)

        entry = {
            "ts": datetime.now(timezone.utc).isoformat(),
            "engagement": engagement,
            "item_id": item_id,
            "action": action,
            "comment": comment,
            "document": document,
            "decided_by": "local operator (dashboard)",
        }
        # 1. append to the local, gitignored decisions log
        with open(DECISIONS_LOG, "a", encoding="utf-8") as fh:
            fh.write(json.dumps(entry) + "\n")

        # 2. APPROVE clears the matching queue item via the local overlay
        #    (the bundled sample fixture is never mutated)
        if action == "APPROVE":
            resolved = _load_resolved()
            resolved.setdefault(engagement, {})[item_id] = {
                "action": action, "ts": entry["ts"], "comment": comment,
            }
            _save_resolved(resolved)

        return self._json({"ok": True, "logged": entry})


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--port", type=int, default=int(os.environ.get("PORT", "8000")))
    ap.add_argument("--host", default=os.environ.get("HOST", "127.0.0.1"))
    args = ap.parse_args()
    srv = ThreadingHTTPServer((args.host, args.port), Handler)
    using = "SAMPLE fixtures" if _is_using_sample() else f"STATE_DIR={os.environ.get('STATE_DIR')}"
    print(f"Framework Console -> http://{args.host}:{args.port}  (data: {using})")
    print("BYOK: this server stores no API keys. Keys live in your browser only.")
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        srv.shutdown()


if __name__ == "__main__":
    main()
