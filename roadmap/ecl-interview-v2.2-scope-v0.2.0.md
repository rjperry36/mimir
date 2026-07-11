# Scope — ECL Interview v2.2: SME-Calibrated Asynchronous Intake

**Status:** DRAFT v0.2.0 — owner decisions on the §7 open questions
incorporated (2026-07-11). Awaiting final owner sign-off of the scope as a
whole; nothing is scheduled until then.
**Author:** drafted for owner review following the ECL interview gap analysis
(session 2026-07-09).
**Reviewers:** owner (sign-off), AI Manager (feasibility).

## Version history

| Version | Date | Change |
|---------|------|--------|
| v0.1.0 | 2026-07-09 | Initial draft with four open questions |
| v0.2.0 | 2026-07-11 | Owner decisions incorporated: interviewee-facing scoring with explainer (WS1); chat-frontend delivery with save/resume moved into scope (WS4/WS5, out-of-scope list amended); per-objective 12/24/36-month horizon (WS3); single v2.2.0 release including async (§7 D4) |

---

## 1. Background

The ECL Interview Agent (v2.1.0) was compared against an external
"AI Transformation Discovery Framework" schema and against the realities of
SME-level transformation engagements. The comparison found the interview
already stronger than the external schema in evidence handling (Evidence
Locker with provenance), anti-fabrication, answer quality (quality bar +
pushback), and gap ownership (TBC items with named owners).

Four genuine gaps were identified, plus one structural finding:

| # | Gap | Today (v2.1.0) |
|---|-----|----------------|
| G1 | Weighted completion scoring | Gates are binary pass/fail; no graded "% complete" signal per section or engagement |
| G2 | Evidence-artifact expectations | Documents are always optional; no tier-dependent expectation of what SHOULD exist |
| G3 | Strategic horizon | Functional objectives are 12-month framed; no 2–3 year objective capture, no execution-history question, no cost-reduction prompt |
| G4 | Parallel asynchronous modules | Modules are independently re-runnable but only sequentially — one interview thread with TBC delegation; no concurrent per-executive intake |
| G5 | Interview harness | The interview definition has no runtime that executes it — session persistence, gate enforcement, locker storage, and output generation are unimplemented (the `runtime/` kernel runs roster waves, not the intake interview) |

SME calibration (the market this framework explicitly targets — see
`constitutional/ecl-framework` §3.0.1) is the design constraint threaded
through all five: at T0/T1 the interview **creates** the business's first
written strategy rather than collecting existing documents. Board-approved
strategy artifacts effectively do not exist below ~50–100 headcount; any
scoring or evidence model that assumes them fails on contact.

## 2. Objectives

1. Give every engagement a graded, tier-calibrated completeness signal that
   is honest at SME scale (a thin-but-complete T0 engagement scores well).
2. Make evidence expectations tier-dependent: corroboration at T0/T1,
   required artifacts only at T2 where they plausibly exist.
3. Capture the 2–3 year strategic picture and the business's execution
   track record — the strongest available predictor of transformation
   absorption capacity.
4. Allow domain modules to be completed concurrently by different
   executives, with a controlled merge, so intake elapsed time is no longer
   bounded by one person's diary.
5. Specify (not necessarily build — see §5) the interview harness that
   executes all of the above.

## 3. In scope

### WS1 — Weighted completion scoring (G1)

- Per-section score: weighted REQUIRED/OPTIONAL field completion, where a
  field counts only if it passed the quality bar (a vague answer scores 0
  until refined). TBC items score partial credit (assigned ≠ resolved).
- Per-module and per-engagement rollup; deferred (unfired) modules are
  excluded from the denominator — T0 is scored against T0's obligations.
- Tier-calibrated weights (replaces the external schema's fixed 80/20):
  - T0/T1: interview-derived answers carry the mandatory weight;
    document evidence scores as corroboration bonus.
  - T2: named evidence artifacts join the mandatory weight (see WS2).
- Score emitted into `session_state` and the gap report; surfaced on the
  dashboard's engagement view.
- **Interviewee-facing (owner decision, §7 D1):** the score is shown to the
  interviewee during the session, accompanied by a plain-language
  summary/explainer ("what this number means, what moves it, what's left").
  Two safeguards follow from making it visible:
  - the explainer states that answer *quality* drives the score — a field
    scores only once it passes the quality bar, so rushing thin answers
    does not move the number (anti-gaming);
  - the score is framed as engagement progress, never as a grade of the
    business (a T0 firm with no strategy documents can still reach 100%).
- **Scoring is advisory** — it never replaces the existing blocking gates
  (critical TBC block, non-fabrication, sign-off authority). A 95% score
  with an unresolved critical TBC still blocks.

### WS2 — Tier-dependent evidence model (G2)

- An `expected_artifacts` map per tier: what documents an engagement of this
  tier plausibly has (T0: accounts + insurance; T1: + management accounts,
  brand assets, key contracts; T2: + strategy deck, org chart, compliance
  register).
- Each expected artifact carries `acceptable_sources` including
  "executive interview" as an explicit fallback — absence of the document
  is recorded as a *finding about the business* (maturity signal), never an
  interview failure.
- Locker ingestion unchanged (verbatim, provenance, hash); this workstream
  only adds the expectation layer and its scoring hook into WS1.

### WS3 — Strategic horizon extension (G3)

- New questions in the core module (Section 2 extension or new Section 2b):
  - Top 3–5 strategic objectives, each with its own horizon of 12, 24, or
    36 months **chosen by the complexity of the objective** (owner decision,
    §7 D3) — a channel-shift objective may be 12 months while a market-entry
    objective is 36. The interview proposes the horizon band and the
    interviewee confirms it; a portfolio where everything lands at 12 months
    is challenged as operational-not-strategic (quality bar). OKR-shaped,
    consistent with ECL §3's existing OKR structure.
  - Execution history: "What did you intend to do in the last 12 months
    that didn't happen — and why?" (SME-graceful form of
    "which objectives are behind schedule"). Feeds a
    `change_absorption_signal` into the sizing axes.
  - Explicit cost-reduction target prompt in Section 5 (Finance).
- 12-month functional objectives (Sections 5–8) become the *near horizon*
  and must nest under a 2–3 year objective or be flagged as orphaned.
- ECL framework impact: MINOR bump — §1.2/§3 gain a horizon linkage field.

### WS4 — Parallel asynchronous module completion (G4)

- Per-module session state (module status, owner, transcript ref) replacing
  the single linear `current_section` cursor; core module remains the
  anchor and must complete first (identity, North Star, sizing, mandate
  matrix anchor — everything downstream modules depend on).
- Module assignment: each fired domain module can be assigned to its
  `executive_owner` (already declared in v2.1.0 for Sections 5–7) and run
  as a self-contained session with its own resume capability.
- **Delivery channel (owner decision, §7 D2):** every module — core and
  domain — is delivered through a web chat frontend. Each assigned module is
  a chat session the executive opens via a link; progress **saves
  continuously** so a session abandoned mid-answer resumes exactly where it
  left off (no "complete in one sitting" requirement). The module logic
  itself stays channel-agnostic (the spec permits other channels later), but
  the chat frontend is the primary, first-built channel.
- Merge step (deterministic, in the harness): when a module completes, its
  answers merge into the draft ECL; conflicts with core-module answers
  (e.g. CFO's revenue figure vs owner's estimate) are surfaced as explicit
  reconciliation items for the owner — never silently overwritten,
  consistent with the non-fabrication constraint.
- Cross-module consistency gate runs at merge, not only at final output.
- The mandate/change-tolerance matrix remains single-custodian (owner via
  core module); domain modules may *propose* elements but not set
  tolerances.

### WS5 — Interview harness & chat frontend specification (G5)

- A written spec (`runtime/` extension design, not code — see §5) covering:
  - Loading and executing an agent-definition YAML as a multi-session,
    multi-participant interview.
  - Session persistence and resume; per-module state (WS4).
  - Mid-conversation gate enforcement (quality bar, non-fabrication).
  - Evidence Locker storage backend (verbatim file store + hash + index),
    including document upload through the chat frontend.
  - Output-document generation (the five v2.1.0 outputs + scores from WS1).
  - Reuse boundaries: what the existing kernel already provides
    (checkpointing, gates, state emission, executor adapter, resilience)
    vs what is genuinely new (conversational session loop, merge logic).
- **Chat frontend spec (owner decision, §7 D2)** — added to this workstream:
  - one chat session per module; per-executive access links; continuous
    save with resume-from-exact-point (extends the v2.1.0 resume_message
    pattern to every participant, not just the owner);
  - live progress and completion-score display with the WS1 explainer;
  - document upload feeding the Evidence Locker (verbatim + provenance
    captured at upload: who, when, filename hash);
  - BYOK posture consistent with the existing dashboard: credentials
    client-side only, no secrets stored server-side;
  - candidate implementation home: alongside the existing dashboard server
    (`dashboard/`), which already renders engagement state — final placement
    decided in the spec, not here.

## 4. Out of scope

- Building the harness code itself (spec only — build is a follow-on with
  its own scope once this is approved).
- Any change to roster agents, the ECL Orchestrator's custodian role, or
  the cascade protocol beyond the MINOR framework bump in WS3.
- T3/T4 (mid-market/enterprise) domains — remain reserved, not coded.
- ~~Web/self-serve questionnaire UI~~ — **moved into scope** as the chat
  frontend (WS5) by owner decision §7 D2. What remains out of scope:
  *building* the frontend and harness code (this scope specifies them;
  build is the follow-on), and any non-chat channel (email-form,
  phone-transcription) beyond noting the channel-agnostic seam.
- Vercel or any hosting/deployment work.
- Changes to the genesis-candidate detection pipeline (v2.1.0 behaviour
  carries forward unchanged).

## 5. Deliverables

| # | Deliverable | Form |
|---|-------------|------|
| D1 | VBP for agent-ecl-interview v2.1.0 → v2.2.0 (MINOR: WS1–WS4 spec changes) | `templates/version-bump-proposal-template.yaml` instance |
| D2 | Updated agent definition v2.2.0 | `agents/agent-ecl-interview-v2.2.0.yaml` |
| D3 | ECL framework MINOR bump (horizon linkage, scoring fields) | `constitutional/ecl-framework` |
| D4 | Interview harness + chat frontend design spec | `roadmap/` or `runtime/` design doc |
| D5 | Updated engagement-lifecycle note (async intake pattern) | MINOR bump if wording requires |

Per AOM rules: agent MINOR bump requires human sign-off; all documents land
as drafts pending owner approval.

## 6. Acceptance criteria (owner checks these)

- [ ] A T0 engagement completed verbally by a solo owner, with accounts as
      the only document, can score ≥80% — thin is not penalised.
- [ ] A missing "strategy document" at T1 appears as a maturity finding,
      not a blocked or failed section.
- [ ] The Finance module can be completed by the accountant in a separate
      session while the Marketing module is still open with the owner, and
      the merge surfaces any figure conflicts for the owner to resolve.
- [ ] Every engagement captures: 2–3yr objectives, the execution-history
      answer, and an explicit cost-reduction position (even if "none").
- [ ] No existing blocking gate is weakened; scoring is additive.
- [ ] The harness spec identifies which kernel components are reused vs new.
- [ ] A participant can close the chat mid-answer and resume later from the
      exact point, with the score and progress display consistent on return.
- [ ] The interviewee-facing score always appears with its plain-language
      explainer, and completing fields below the quality bar does not
      increase it.
- [ ] Each captured strategic objective carries a confirmed 12/24/36-month
      horizon, and near-horizon functional objectives nest under one.

## 7. Owner decisions (recorded 2026-07-11)

| # | Question | Decision |
|---|----------|----------|
| D1 | Scoring visibility | **Interviewee-facing**, with a simple summary/explainer alongside the number. Incorporated into WS1. |
| D2 | Module assignment channel | **Web chat frontend for every module** — each part of the interview runs as a chat session with continuous save/resume, so no participant has to complete in one sitting. Incorporated into WS4 (delivery) and WS5 (frontend spec); out-of-scope list amended. |
| D3 | Horizon | **Per-objective, complexity-dependent: 12, 24, or 36 months** — no single fixed horizon. Incorporated into WS3. |
| D4 | Sequencing | **Async is core — ship as one v2.2.0** including WS4+WS5; the calibration-first split (v2.3.0 deferral of async) is rejected. *Interpretation note: "async seems more sensible" is read as keeping the async workstreams in the release, not deferring them — correct this if the intent was the opposite.* |

## 8. Explicitly not decided here

Effort estimates, build sequencing beyond §7 Q4, and harness implementation
technology. Those follow once this scope is confirmed.
