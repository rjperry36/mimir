# Session Handover — 2026-07-18

**From:** Claude Code web session (ECL interview YAML review)
**To:** any environment — VS Code + Claude Code extension, terminal CLI, or a
fresh web session
**State:** everything described here is committed and pushed to branch
`claude/ecl-interview-yaml-review-3be00l`. Nothing lives only in the old
session's conversation.

## Step 0 — before anything else

```bash
git fetch origin
git checkout claude/ecl-interview-yaml-review-3be00l
git pull origin claude/ecl-interview-yaml-review-3be00l
```

Last commit at handover: `d460769` ("Record owner decisions: drop PraisonAI,
program-of-work choices, build order") — if `git log -1` shows something
newer, work has continued since this doc was written; read the newer commits
first. (This handover's own commit will sit on top of `d460769`.)

## What has been done (this branch, newest work first)

| Item | Where |
|------|-------|
| Owner decisions recorded: PraisonAI dropped; ECL Orchestrator is program custodian; auto-pause on guard breach (owner notified); roster-level work packages; interview builds before program layer | `roadmap/program-of-work-layer-scope-v0.2.0.md` §8, `roadmap/praisonai-spike-memo-v1.0.0.md` §0 |
| PraisonAI spike: adapter built, contract-proven (52 tests green), then removed on owner decision — code survives in git history at `fca9574` | `roadmap/praisonai-spike-memo-v1.0.0.md` |
| Umbrella product plan: 4 phases (live-run proof → interview harness → program layer → pilot + ASA re-audit) | `roadmap/path-to-viable-product-v0.1.0.md` |
| Program-of-work layer scoped (the missing objectives→work-packages layer) | `roadmap/program-of-work-layer-scope-v0.2.0.md` |
| ECL interview v2.2 scoped, owner decisions in: interviewee-visible weighted scoring + explainer; chat frontend with save/resume for every module; per-objective 12/24/36-month horizons; one release incl. async | `roadmap/ecl-interview-v2.2-scope-v0.2.0.md` |
| Tracked `__pycache__` bytecode untracked (gitignore now effective) | `3f04518` |

Both scope documents are **decision-complete but not yet formally
signed off** by the owner as whole documents.

## What to produce next (in order)

1. **Phase 0 — first live agent run.** The owner has added (or is adding)
   `ANTHROPIC_API_KEY` to the cloud environment; in VS Code/terminal it just
   needs to be in the shell env. Then: `pip install anthropic pyyaml`, wire
   one roster agent wave through `runtime/` (`ClaudeSubagentExecutor` with
   its real `AnthropicMessagesTransport`), run it, and keep the emitted
   ledgers as evidence. Exit criterion: a wave-status ledger showing a real
   run reach `COMPLETE` outside a test harness. Then update the runtime
   README's "not proven in this sandbox" caveat with the dated proof.
2. **Interview harness + chat frontend build** per
   `roadmap/ecl-interview-v2.2-scope-v0.2.0.md` (owner chose this before the
   program layer). Start with the VBP and the v2.2.0 agent definition
   (deliverables D1/D2 in the scope), then the harness design spec (D4).
3. **Program-of-work layer** per its scope, after (or overlapping the tail
   of) the interview build.

## Constraints that apply

- AOM rules: agent MINOR/MAJOR bumps need VBPs and human sign-off; no silent
  changes; non-fabrication throughout (see `constitutional/`).
- BYOK: keys live in environment variables only — never in the repo, never
  in chat. `.gitignore` already covers `.env`.
- PraisonAI is a **closed decision** (dropped). Do not reintroduce it
  without a new owner decision; the evaluation is on file in the spike memo.
- Develop on `claude/ecl-interview-yaml-review-3be00l` unless the owner
  starts a fresh branch for the build work.

## What NOT to redo

- Don't re-run the yaml-vs-interview gap analysis, the SME availability
  assessment, or the PraisonAI evaluation — their conclusions are baked into
  the two scopes and the memo.
- Don't re-ask the owner the six blocker questions answered 2026-07-18 —
  they're recorded in the scopes' §7/§8 decision tables.

## Context for a fresh Claude session

Point it at this file first ("read HANDOVER.md and continue"). The five
documents that carry the full picture, in reading order:
`roadmap/path-to-viable-product-v0.1.0.md` →
`roadmap/ecl-interview-v2.2-scope-v0.2.0.md` →
`roadmap/program-of-work-layer-scope-v0.2.0.md` →
`roadmap/praisonai-spike-memo-v1.0.0.md` →
`runtime/README.md`.

## Housekeeping

Delete this file (or replace it with a fresh one) once the handover has
happened — a stale handover doc is worse than none.
