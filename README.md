# Mimir — Organisational Intelligence Engine

**A governance-first way to run AI delivery teams.** Interview a business,
agree a manifesto, then let specialist AI agent teams do the work — with a
human approving every significant decision and the whole system versioning
and auditing itself.

Like its namesake, **Mimir counsels; you decide.** In Norse myth, Odin
consulted Mimir before every major decision — but Mimir never ruled. Every
agent in this system works the same way: it detects, evidences, drafts, and
recommends. Humans sign.

> **Honest status:** independently audited **58/100 — "Prototype Only"**
> (bimodal: governance & validation strong; live runtime execution still
> proving out). Read [what it's NOT](site/what-its-not.html) before anything
> else — honesty about stage is a design feature here.

---

## What's in the repo

| Layer | What it is |
|-------|-----------|
| `constitutional/` | The rules of the system: ECL framework, AI Operating Model, engagement lifecycle, context & memory protocol, roster genesis protocol, architecture |
| `agents/` + `rosters/` | 35 versioned agents across 4 specialist rosters (SEO, App Dev, Content, Recruitment seed) + management layer — every one validated in CI |
| `scripts/validate_framework.py` | Machine validator (18 check classes) — agents and manifest cannot drift; CI-enforced on every push |
| `runtime/` | Deterministic kernel: heartbeat/dead-agent detection, checkpoint/resume, gate-runner, budget pause, workspace isolation, BYOK credentials, tool resilience, genesis decision plumbing — 44/44 tests |
| `dashboard/` | Mimir Console: wave board, metrics, decision inbox, document review & approval, interview transcript + evidence locker, RAID, BYOK credentials screen |
| `site/` | The explainer website (what it is / how to use / what it achieves / **what it's NOT**) |
| `pilot/` | Sanitised case study of the live-fire test on a real business |
| `templates/` | 20 canonical artifact templates |
| `audits/` | The independent Agentic System Auditor instrument (and its verdict) |

## Quick start

```bash
pip install pyyaml && python3 scripts/validate_framework.py   # validator: 35 agents, 0 errors
python3 -m pytest runtime/tests/ -q                            # runtime: 44 passed
python3 dashboard/server.py                                    # console on :8000 (sample data)
open site/index.html                                           # the explainer site
```

## Bring your own keys

Mimir ships with **no credentials, ever**. You supply your own Anthropic/
Claude key and service keys per engagement via the Console's Credentials
screen or environment variables. Keys stay client-side, are redacted in all
output, and fail loud if missing. A CI secret-scan gate blocks accidental
commits.

## Licence

**© Russ Perry. All rights reserved.** Shared publicly for evaluation and
transparency while in its testing phase — no licence to use, copy, or
modify is granted at this time. If you want to use Mimir, get in touch.
