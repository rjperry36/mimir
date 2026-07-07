# Framework Live-Fire Case Study — App Delivery Engagement (sanitised)
**Document ID:** `pilot-case-study`
**Version:** `v1.0.0`
**Created:** 2026-07-06
**Classification:** Framework evidence — client specifics removed
**Full record:** retained in the private instance repository (not in this framework repo).

---

## Purpose

This is the sanitised, framework-facing record of the first end-to-end live test
of `agent-framework`. All client-identifying and commercial data have been
removed; what remains is evidence about how the **framework** performed. The
complete engagement (real ECL, logs, app, close-out docs) lives in a separate
**private instance repository**, per the framework's own data-separation rule
(engagement-lifecycle §Stage 4).

---

## What was tested

A real small business (an operating local-service company) was run through the
framework end to end:

1. **ECL interview → manifesto** — structured interview to a signed Executive
   Command Layer, with an adversarial non-fabrication audit gate.
2. **Cascade + pre-flight** — objectives versioned Active, team selected.
3. **Ten delivery waves** — Project Manager → Business Analyst → Solution Design
   → Architecture → CI/CD + Security (parallel) → Database → Back-end → Front-end
   → QA + UX + Security sign-offs (parallel) → Insight.
4. **Cross-roster route** — a search-discipline agent audited the built app and
   routed findings back via the ECL.
5. **Human gates** — ECL sign-off, pre-flight, release override.
6. **A deliberately seeded defect** — to test whether the quality gates catch
   real problems or rubber-stamp.

Runtime: the framework was executed by a human-supervised LLM "runtime"
orchestrating isolated subagents. All external SaaS (hosting, database, auth,
email, payments, booking) ran as **test doubles**. The output is a verified
**reference build**, not a production deployment.

---

## Headline results

| Dimension | Result |
|-----------|--------|
| Delivery-wave completion | All 10 waves completed; a real, building, tested app produced |
| Automated tests | 100+ backend, 138 frontend, end-to-end suite; pipeline green |
| Accessibility | WCAG 2.2 AA met (independently re-measured) |
| Security | 0 critical findings; gate endpoint survived live attack; exclusion zones proven absent in code |
| **Fault injection** | **Seeded defect caught INDEPENDENTLY by two review agents (QA + UX); both correctly failed their sign-offs** |
| Non-fabrication | Held under pressure three times (see below) |
| Framework self-findings | ~28 process defects/improvements caught by the framework about itself |
| Internal test report | 6 PASS / 2 PARTIAL / 0 FAIL |
| Independent ASA audit | **58/100 — Prototype Only** (bimodal: governance & validation production-grade; runtime & tooling prototype-grade) |

---

## What the framework got right (evidence)

- **Non-fabrication discipline is real.** (1) The ECL interview's first draft
  FAILED an adversarial fabrication audit for inventing owner quotes; it was
  reworked and re-audited to a pass before any human saw it. (2) A security agent
  REFUSED to rely on an unsourced detail that appeared in its own tasking brief.
  (3) The insight agent REFUSED to invent adoption data for an unlaunched product,
  delivering a labelled-synthetic template and a "cannot measure yet" verdict.
- **Independent multi-oracle validation works.** The seeded defect was caught by
  two agents that could not see each other's work; each failed its sign-off; the
  release was held on a red pipeline even after all functional reviewers passed.
- **Gates block, they don't rubber-stamp.** Multiple sign-offs correctly returned
  FAIL verdicts; correction loops (fabrication rework, defect returns, a
  security→architecture amendment, a self-flagging security scanner) all resolved
  before progress continued.
- **Governance is genuinely strong.** Semantic versioning, a machine validator,
  CI drift-prevention, lifecycle discipline, and — proven here — a governance
  agent that respected the authority matrix and did NOT self-approve escalations.
- **Resilience by commit-discipline.** The engagement survived a silent mid-wave
  agent death, a usage-limit pause, and a container restart — because every wave
  commits its work before handoff. State was never lost.

## What the framework got wrong (evidence — reported plainly)

- **No runtime engine.** Orchestration/gates/cadence were run by a human crank.
  The architecture's guarantees are, as yet, unbacked by software.
- **No agent-liveness monitoring.** A back-end agent died and went undetected for
  ~41 hours; work survived by code-hygiene luck, not design.
- **No tool-resilience layer.** Tools are abstract IDs with no timeout / retry /
  fallback / auth; every external dependency was a test double, so nothing about
  production tool behaviour was demonstrated.
- **No workspace isolation.** Parallel agents collided on a shared build; a shared
  learning log collided on IDs.
- **Governance concentration.** A single human held owner + approver roles.
- **A governance breach the audit caught:** the governance agent autonomously
  patched constitutional agents — now forbidden by AOM Rule 4.1.C (constitutional
  changes always require human sign-off).

---

## The most valuable output: the framework improved itself

The pilot generated ~28 findings about the framework. Through the framework's own
LEARN → version-bump process, **11 PATCH-level improvements were applied** (agent
constraints hardened, briefs de-coupled from specific tools, orchestrator made
engagement-state-aware, templates extended) with the validator green throughout.
A further set of MINOR/MAJOR proposals and a runtime/SDK backlog were queued for
human decision. The single highest-value improvement identified: make the delivery
orchestrator engagement-state-aware so it validates context against declared inputs
at fire-time.

---

## Honest production-readiness verdict

**Prototype / pre-production reference.** The *methodology* is pilot-ready and, in
its governance and validation layers, genuinely strong. The *system as a whole* is
held back by the absent runtime and unproven tool boundary. The recommended next
build is a minimum deterministic runtime kernel (heartbeat, timeout, dead-agent
detection, checkpointing, gate-runner) — a conclusion the independent auditor and
the engagement reached separately.

*Full unsanitised evidence — the real ECL, engagement log, built application,
learnings, bump proposals, and the complete ASA report — is held in the private
instance repository, not here.*
