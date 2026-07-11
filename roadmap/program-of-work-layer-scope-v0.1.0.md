# Scope — Program of Work & Tactical Briefing Layer

**Status:** DRAFT v0.1.0 — for owner review. Nothing in this document is
approved or scheduled until signed off.
**Author:** drafted for owner review following the objectives-to-work-packages
gap analysis (session 2026-07-11).
**Reviewers:** owner (sign-off), AI Manager (feasibility).
**Relationship to other scopes:** independent of, and downstream from,
`roadmap/ecl-interview-v2.2-scope-v0.1.0.md` (intake). This layer consumes a
signed-off ECL regardless of which interview version produced it. The two
scopes can be approved and sequenced separately.

---

## 1. Background

The framework has a strategic plan at the top (the ECL: OKR-structured
objectives per domain, baselines, KPI cascade triggers, roster priority
weighting) and tactical execution at the bottom (roster orchestrators running
fixed discipline playbooks as dependency-sequenced waves on the runtime
kernel). Between them there is no **program of work**: objectives currently
select and prioritise rosters — they do not compose work.

Consequences, tested against three representative SME objectives:

| Objective | What happens today |
|-----------|--------------------|
| "Reduce marketing spend 10%, hold 30% market penetration" | Budget ceiling lands in the mandate matrix; each roster keeps running its standing playbook with less money; the penetration guard is discovered via KPI breach, not planned against. The trade-off — the point of the objective — has no home. |
| "Rebrand my website" | No home at all. A finite, cross-roster initiative (brand, content, SEO migration, app dev) has no object to exist in: the framework only models standing discipline cadences, not projects with a start, an end, and cross-roster dependencies. |
| "Increase EBITDA to 35%" | Recorded faithfully as a Finance OKR, then broadcast verbatim to every roster and owned by none. An outcome objective requiring decomposition into levers (pricing, cost lines, mix) has no decomposition mechanism. |

Two adjacent findings are included in this scope's problem statement:

- The **cascade briefing is a change notification, not a work directive** —
  it quotes changed objectives verbatim and sets
  `required action: none/review/update/pause`. Nothing tells a roster *what
  to deliver*.
- The **ECL §2.3 TOM is current-state only** — operating boundaries as they
  exist today. There is no target-state operating model or transition path,
  which is what transformation work steers by.

## 2. Objectives

1. Give every ECL objective a decomposed, human-signed **program of work**:
   objective → initiative → work package, with progress rolling back up the
   same spine into the ECL's existing OKR status fields.
2. Make the **work package the tactical brief**: a self-contained directive
   a roster orchestrator can compile into its wave plan without further
   context.
3. Support all three objective shapes: standing improvement (spend/penetration
   trade-off), finite initiative (rebrand), and outcome decomposition (EBITDA).
4. Add a **target operating model** alongside the current-state TOM, so work
   packages can cite the to-be state they move the business toward.
5. Keep the human in the same position they occupy everywhere else in the
   framework: the decomposition is proposed by agents, **approved by the
   owner**, and re-planned on cascade — never silently.

## 3. Design principles (constraints on any solution)

- **Nothing existing is bypassed.** Work packages inherit constraints from
  the mandate matrix, envelopes from `roster_priority_weighting`, and
  re-planning triggers from the cascade protocol. The roster orchestrator's
  `engagement_plan` remains the compile target; the runtime kernel remains
  the executor. This layer is a missing floor, not a new building.
- **Non-fabrication carries through.** Every initiative and work package
  cites the ECL objective (and KR) it serves; every lever in an outcome
  decomposition cites evidence (transcript, locker item, or baseline metric)
  or is marked assumption-for-approval. No invented baselines.
- **Decomposition is proposal, approval is human.** Same posture as the
  roster-genesis protocol: agents draft, the owner signs. Applies to the
  program, to material re-plans, and to any lever tree.
- **SME-proportionate.** At T0 a program may be one initiative with two work
  packages. The layer must not impose corporate programme-office ceremony on
  a five-person business.

## 4. In scope

### WS1 — Program of Work document (the strategic plan made executable)

- New constitutional-layer document type, one per engagement, versioned in
  lockstep with the ECL (an ECL MINOR/MAJOR bump forces a program review):
  - `program_of_work`: for each in-scope ECL objective, its initiatives;
    for each initiative: owner, horizon, guard metrics, and its work
    packages by roster.
  - Explicit `not_programmed` list: ECL objectives deliberately left as
    standing-cadence work (with rationale) — no silent omissions.
- Status model per initiative and work package
  (`proposed / approved / in-flight / blocked / done / cancelled`) with
  roll-up rules into the ECL KR status fields
  (`on-track / at-risk / off-track / achieved`).
- Human sign-off gate before any work package dispatches.

### WS2 — Work package = tactical brief (schema + template)

- New template (`templates/work-package-template.yaml`) carrying, per package:
  - deliverable + acceptance criteria (reusing the user-story Given/When/Then
    pattern where the deliverable is buildable);
  - the ECL objective and KR it moves, with expected contribution;
  - budget envelope and **guard metrics** (the "hold 30% penetration" half of
    a trade-off objective, checked at the same cadence as delivery KPIs);
  - constraints inherited from the mandate matrix (quoted, not referenced —
    briefs are self-contained, matching the cascade content rules);
  - timeframe, cross-roster dependencies, and the roster + agent chain
    expected to deliver it;
  - source citations (non-fabrication).
- Dispatch rule: a work package is issued by the ECL Orchestrator to a roster
  orchestrator, which acknowledges and compiles it into its `engagement_plan`
  (wave sequence) — the existing hook, now fed by a directive instead of
  only a passive ECL read.

### WS3 — Objective decomposition protocol (the EBITDA case)

- A defined procedure for outcome objectives that span domains:
  1. ECL Orchestrator (with AI Manager) drafts a **lever tree** — candidate
     levers, each with baseline evidence, estimated contribution, affected
     domains/rosters, and confidence;
  2. owner approves/edits the lever tree (decisions-queue item, same
     plumbing as genesis proposals);
  3. approved levers become initiatives/work packages in the program.
- Explicitly a proposal instrument: unevidenced levers are marked as
  assumptions and cannot proceed to work packages until owner-confirmed.

### WS4 — Initiative support for finite projects (the rebrand case)

- Initiatives carry start/end, milestone gates, and cross-roster dependency
  declarations the kernel's wave scheduler can respect across rosters (today
  dependencies are sequenced only within a roster's own plan).
- Close-out rule: a finished initiative archives into the engagement record
  and its guard/result metrics post back to the ECL KR — initiatives cannot
  linger as zombie standing work.

### WS5 — Target operating model (ECL extension)

- ECL §2.3 splits into **current TOM** (as-is, unchanged semantics) and
  **target TOM** (to-be: what is automated, human touchpoints, systems,
  capacity at the strategic horizon) plus a transition note per material gap.
- Work packages may cite the target-TOM gap they close; the interview scope
  (v2.2 WS3, strategic horizon) supplies the capture questions if approved —
  otherwise the target TOM is drafted at program creation from existing ECL
  content and owner review.

### WS6 — Cascade and re-planning integration

- Cascade briefings gain an optional `work_package_impact` section: which
  in-flight packages an ECL change touches and the proposed disposition
  (continue / amend / pause / cancel), owner-signed where material.
- KPI cascade triggers (already in ECL §3) can now target a *program*
  response ("penetration guard breached → pause spend-reduction package,
  escalate") instead of only a query to a roster.

## 5. Out of scope

- Building runtime/harness code. This scope produces the document types,
  templates, agent-definition changes, and protocol text; kernel changes
  (cross-roster dependency scheduling) are specified as requirements only.
- Any change to the interview agent (that is the v2.2 scope; this layer
  works from a signed ECL whatever produced it).
- Portfolio/multi-engagement programme management (one program per
  engagement; T3–T4 concerns stay reserved).
- Resource/capacity planning of human staff — work packages direct agent
  rosters; human tasks appear only as dependencies or approval gates.
- Financial modelling tooling for lever trees (the protocol defines what a
  lever must evidence, not how the numbers are modelled).

## 6. Deliverables

| # | Deliverable | Form |
|---|-------------|------|
| D1 | Program-of-Work protocol (constitutional doc, new) | `constitutional/program-of-work-protocol-v1.0.0.md` |
| D2 | Work-package template | `templates/work-package-template.yaml` |
| D3 | Program-of-work template | `templates/program-of-work-template.yaml` |
| D4 | ECL Orchestrator MINOR bump (program custodian, decomposition + dispatch responsibilities, cascade §WS6) | VBP + `agents/agent-ecl-orchestrator-v1.2.0.yaml` |
| D5 | ECL framework MINOR bump (target TOM, KR roll-up fields) | VBP + `constitutional/ecl-framework` |
| D6 | Roster orchestrator contract addendum (work-package intake → engagement_plan compile, acknowledgement) | VBP per affected roster orchestrator |
| D7 | Kernel requirements note (cross-roster dependencies, program state emission for the dashboard) | `runtime/` design note — spec only |

All land as drafts pending owner sign-off, per AOM version-bump authority.

## 7. Acceptance criteria (owner checks these)

- [ ] "Reduce marketing spend 10%, hold 30% penetration" can be expressed as
      one initiative with coordinated work packages across the affected
      rosters, a shared shrinking envelope, and a penetration guard metric
      that pauses the programme on breach — not discovered after the fact.
- [ ] "Rebrand my website" can be expressed as a finite initiative with
      cross-roster dependencies and a close-out that posts results back to
      the ECL — and it cannot become permanent standing work.
- [ ] "EBITDA to 35%" produces an evidence-cited lever tree the owner
      approves before any work package exists.
- [ ] A roster orchestrator can compile a work package into its wave plan
      using only the brief's own content (self-contained test).
- [ ] Every work package traces to an ECL objective/KR; every ECL objective
      is either programmed or explicitly listed as standing-cadence.
- [ ] Program status is visible on the dashboard from the existing ledgers
      plus at most one new state emission.
- [ ] A T0 engagement can run a one-initiative, two-package program without
      any additional ceremony.

## 8. Open questions for the owner

1. **Program custodian** — the draft assigns program ownership to the ECL
   Orchestrator (strategy custodian). Alternative: a new dedicated
   `program_manager_agent`. Extending the orchestrator is leaner; a separate
   agent isolates a large new responsibility. Which?
2. **Re-plan authority** — when a guard metric breaches, may the orchestrator
   pause in-flight work packages autonomously (owner notified), or is pause
   itself owner-signed? (Framework precedent: PATCH autonomous, MAJOR
   signed — where does "pause a package" sit?)
3. **Granularity floor** — is a work package always roster-level, or may it
   target a single agent within a roster? (Draft says roster-level; the
   roster orchestrator decides internal sequencing.)
4. **Sequencing vs the interview scope** — build this layer first (it
   unlocks value from every existing signed ECL), or after v2.2 intake?
   The two are independent; my recommendation is this one first.

## 9. Explicitly not decided here

Effort estimates, kernel implementation of cross-roster scheduling, dashboard
UI treatment, and whether lever-tree drafting warrants its own agent. Those
follow once this scope is confirmed.
