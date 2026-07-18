# Path to Viable Product

**Status:** DRAFT v0.1.0 — for owner review.
**Purpose:** the umbrella plan the two open scopes hang from. Defines what
"viable product" means for mimir, the phase sequence to reach it, and the
dependency order between the pieces.

---

## 1. What "viable product" means here

Mimir's target market is SME transformation. Viability is therefore **not**
a self-serve SaaS. It is:

> A repeatable, evidence-governed engagement a consultant can run with a
> real client: intake chat → signed ECL → program of work → agents deliver
> → client watches the dashboard.

One repeatable engagement with a real client IS the product. Packaging
(SaaS, licensing, white-label) is a later decision taken from evidence, not
before it.

## 2. Current position (honest baseline)

- Independently audited **58/100 — "Prototype Only"** (ASA v1.0.0); the
  verdict predates the runtime kernel, which was built in response to it.
- Deterministic runtime kernel: REAL, tested (52 runtime tests green).
- **No live agent run has ever completed** — executor adapters are proven
  against fakes; a credentialed end-to-end run is the outstanding proof.
- ECL interview: strong spec (v2.1.0), no harness to execute it.
- Strategy→work translation layer (program of work): missing, scoped.
- Two scopes drafted: `ecl-interview-v2.2-scope` (v0.2.0, decisions
  incorporated, awaiting final sign-off) and
  `program-of-work-layer-scope` (v0.1.0, §8 questions open).
- PraisonAI spike (2026-07-18): adapter built, contract-proven, then
  **dropped by owner decision** — mimir stays Claude-only. See
  `roadmap/praisonai-spike-memo-v1.0.0.md` §0; the adapter survives in git
  history if ever needed.

## 3. Phases

### Phase 0 — Prove the engine lives *(weeks)*

The cheapest, highest-leverage credibility unlock.

- One credentialed end-to-end run of one roster agent through the kernel
  via `ClaudeSubagentExecutor` (requires the `anthropic` SDK and an
  `ANTHROPIC_API_KEY`, BYOK). The adapter exists; only a key and a wired
  tool-set are missing.
- Record the run's ledgers as evidence; note it in the runtime README
  (replacing the "not proven in this sandbox" caveat with a dated proof).

**Exit criterion:** a wave-status ledger showing a real agent run reaching
`COMPLETE`, produced outside a test harness.

### Phase 1 — Build the front door *(interview harness + chat frontend)*

Scope: `roadmap/ecl-interview-v2.2-scope-v0.2.0.md` (decision-complete).

- Harness executes the interview definition: modular sessions, save/resume,
  quality-gate enforcement, evidence locker, weighted scoring.
- Chat frontend per owner decision D2: every module a chat session with
  continuous save; score visible with explainer (D1).
- Session/memory/chat components are built in-house (the PraisonAI
  borrow option was closed by the owner's drop decision).

**Exit criterion:** a full interview run end-to-end in the chat frontend on
a fixture business, producing the five output documents + scores.

### Phase 2 — Build the spine *(program of work layer)*

Scope: `roadmap/program-of-work-layer-scope-v0.1.0.md` (§8 decisions
needed before build).

- Objectives → initiatives → work packages → roster wave plans, with the
  three test objectives (spend/penetration trade-off, rebrand, EBITDA)
  expressible per the scope's acceptance criteria.

**Exit criterion:** a signed ECL fixture decomposed into a human-approved
program whose work packages compile into roster engagement plans.

### Phase 3 — Design-partner pilot, then re-audit

- 1–3 real SMEs (discounted, case-study rights), full lifecycle, warts
  logged. Source from the existing consulting pipeline.
- Re-run the ASA (`audits/agentic-system-auditor-v1.0.0.md`) against the
  working system; **file the report in `audits/reports/`** (currently
  empty); update the README/site score claim with the dated evidence.
- Write the pilot case study (there is precedent: `pilot/CASE-STUDY.md`).

**Exit criterion:** one paid-or-discounted engagement completed + a filed
ASA report. That pair is the definition of "viable product" met.

## 4. Deliberately deferred until after Phase 3

Pricing/packaging, multi-tenant infrastructure, non-SEO roster expansion,
T3–T4 domains, and any marketing claims beyond the honest-status line.

## 5. Sequencing logic

Phase 0 before 1 because every later phase's demos depend on a believed
engine. Phase 1 before 2 because the program of work consumes a signed ECL
and the fastest honest way to a signed ECL is the working intake. Phases 1
and 2 *can* overlap (different layers, different files) if capacity allows.
Phase 3 needs both.

## 6. Standing risks

| Risk | Mitigation |
|------|------------|
| Live-run proof keeps slipping (credentials/tooling friction) | Phase 0 is scoped to ONE wave of ONE agent — resist scope growth |
| Harness build balloons | WS5 spec explicitly separates kernel-reuse from genuinely-new; chat frontend can ship module-by-module |
| Single-provider dependency (Claude-only by owner decision) | The executor seam keeps the engine swappable; the PraisonAI evaluation is on file if a second provider is ever needed |
| Stale audit claim (58/100) misrepresents current state in either direction | Re-audit at Phase 3; until then the honest-status line stays as-is |
