# Framework Console

A runnable **operator dashboard** for the agent-framework — the visibility &
decision surface described in `roadmap/console-brief-v0.1.0.md`. NOT a chat UI.
It is (almost entirely) deterministic rendering of the state the runtime kernel
emits; there is no AI in the dashboard itself.

## Run it — one command

```bash
python3 dashboard/server.py --port 8000
# then open http://127.0.0.1:8000
```

Requirements: Python 3 + `pyyaml` (already used by `runtime/`). No Node, no build
step, no external packages, no network. Stdlib `http.server` only.

By default it reads the bundled **sample fixtures** under
`sample-state/engagements/` so it renders out of the box. To point it at a real
run instead:

```bash
STATE_DIR=/path/to/runtime-state python3 dashboard/server.py
```

where `STATE_DIR` contains one sub-directory per engagement, each holding the
four ledgers `runtime/state.py::StateEmitter` writes (`wave-status.yaml`,
`metrics-ledger.jsonl`, `integrity-register.jsonl`, `decisions-queue.yaml`) and
optionally `raid-log.yaml` + a `documents/` folder. To generate a real set:
`python -m runtime.demo` writes ledgers to a temp dir you can pass here.

## The nine views

| # | Tab | What it shows | Source |
|---|-----|---------------|--------|
| 1 | **Wave board** | Every wave as a status card (PENDING / RUNNING / COMPLETE / GATE_BLOCKED / BLOCKED / DEAD / TIMED_OUT / PAUSED / AWAITING_APPROVAL). DEAD & GATE_BLOCKED & TIMED_OUT are flagged **red** (left border + solid red pill); the death/gate detail is shown. | `wave-status.yaml` |
| 2 | **Metrics timeline** | One row per agent run: ts, wave, agent, version, termination cause, tokens, duration, tool_uses, gates ✓/✗, rework. Missing fields render `—`, never a fabricated number. | `metrics-ledger.jsonl` |
| 3 | **Learning by version** | Metrics grouped by `agent_version` across **all** engagements, so "getting better" is attributable to LEARN→bump cycles. Bars = avg rework loops/run (lower better) + gate-pass rate per version. **Honestly flags** any agent with <2 versions as "data is sparse". | derived from `metrics-ledger.jsonl` |
| 4 | **Integrity log** | Typed events: gate failures, dead agents, budget pauses, policy blocks, fabrication-audit findings — with severity chip and OPEN/RESOLVED resolution. | `integrity-register.jsonl` |
| 5 | **Decision inbox** | Items awaiting the human, each with age and an **AOM-timeout breach clock** ("breach in 4h" / "BREACHED"). Approve/Comment buttons write to the local decisions log; Approve clears the item. | `decisions-queue.yaml` |
| 6 | **RAG** | Red/Amber/Green per engagement, computed **worst-of** its wave states (deterministic). RED = any DEAD/GATE_BLOCKED/TIMED_OUT; AMBER = any BLOCKED/PAUSED/AWAITING_APPROVAL; else GREEN. | derived from `wave-status.yaml` |
| 7 | **RAID** | Risks / Assumptions / Issues / Dependencies tables. | `raid-log.yaml` |
| 8 | **Document review & approval** | List the engagement's documents; click to read rendered cleanly (markdown→HTML, YAML pretty-printed). Inline **Approve / Comment** write the decision + comment to the local log and clear the matching queue item. **Version diff** view when two versions of a doc exist (e.g. delivery-plan v1.0.0 ↔ v1.0.1). | `documents/*` + write-back |
| 9 | **Credentials (BYOK)** | Enter **your own** keys (Anthropic + per-service). Stored in the browser's `localStorage` only, masked to last-4. Missing key → "enter your key" prompt, never a default. Persistent BYOK banner on every screen. | browser localStorage |

Screenshots of five views are in `screenshots/`.

## BYOK — bring your own key

- Persistent banner on every screen: *"You provide your own API keys. They stay
  on your device. This project ships with none."*
- Keys are entered on the Credentials screen and kept in **browser
  `localStorage` only** (`framework-console-byok`). The server never receives,
  stores, or forwards a key — `server.py` has no key-handling code path at all.
- Stored keys are shown masked to last-4 (mirrors `runtime/credentials.py::mask`).
- No key set → the feature shows a clear "enter your key" prompt and the runtime
  would fail loud (`CredentialError`), never a default/owner key.
- `.gitignore` blocks `.env*` (except `.env.example`), `local-store/`, and any
  localStorage dump.

## What writes where (honest)

The only writes the server performs are **local and gitignored**, under
`local-store/`:

- `decisions-log.jsonl` — append-only record of every Approve/Comment/Save.
- `resolved.json` — overlay marking which queue items you've approved.

The bundled `sample-state/` fixtures are **never mutated** — approvals are
layered on top via the overlay, so the demo stays reproducible. Nothing is ever
sent to any owner-controlled backend.

## What's real vs sample

- **Real:** the data contract (schemas match `runtime/state.py` exactly), the
  RAG roll-up rule, the write-back, the diff, the BYOK handling, path-traversal
  guards. Point `STATE_DIR` at a live run and it renders real state unchanged.
- **Sample:** the ledger *contents* under `sample-state/` are hand-built
  fixtures (one degraded engagement + one healthy one) so every state and view
  has something to show out of the box. They are clearly tagged **SAMPLE DATA**
  in the header. `raid-log.yaml` is a fictional demo RAID log — no real client
  data — matching the same schema.

## Files

```
dashboard/
├── server.py              # stdlib http server: reads ledgers, serves views, local write-back
├── static/
│   ├── index.html         # shell + BYOK banner
│   ├── app.js             # all 9 views, markdown/diff renderers, BYOK localStorage
│   └── styles.css         # theme-aware (light/dark), dataviz-validated palette
├── sample-state/engagements/
│   ├── riverside-bookings/  # degraded: a DEAD wave, a GATE_BLOCKED wave, 4 open decisions, docs
│   └── dorchester-collection-loyalty/   # healthy: gives RAG + learning-trend contrast
├── local-store/           # gitignored: decisions-log.jsonl + resolved.json (created at runtime)
├── screenshots/
├── .gitignore
└── README.md
```
