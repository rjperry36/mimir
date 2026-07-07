# Genesis Record — roster-recruitment
**Date:** 2026-07-07
**Protocol:** `constitutional/roster-genesis-protocol` v1.0.0 — **first live execution**
**Scenario:** the protocol's own worked example — a FICTIONAL domiciliary care
provider needing to recruit 12 care workers in 6 months. No real client data.

This record documents the end-to-end run, stage by stage, as evidence that the
protocol executes as written.

---

## Stage-by-stage trace

| Stage | What the protocol requires | What happened | Artifact |
|-------|---------------------------|---------------|----------|
| **1 — Trigger** | A detected gap from interview / pre-flight / scope event / LEARN | Interview-class trigger: HR & People headcount objective with no roster homing the recruitment discipline | `genesis-proposal.yaml` → `trigger` |
| **0 — Right-sizing ladder** | Walk down R1→R4; escalate only with evidence | **R1 partially adopted** (attraction surface → roster-content / roster-appdev / roster-seo via existing routes); **R2 rejected with reasons** (pipeline + compliance + contract drafting is not one specialism and belongs to neither candidate host roster); **R3 concluded** (genuine un-homed discipline) | `genesis-proposal.yaml` → `right_sizing_analysis` |
| **2 — Proposal** | Drafted by ECL Orchestrator + AI Manager roles; template completed in full, incl. seed cap, routes, human gates, retirement condition | Proposal drafted with all mandatory fields: seed team at the hard cap (orchestrator + 2 specialists — UNDER the max-3 cap), cross-roster routes making the reuse rule explicit, five named human gates / exclusion zones, retirement condition (2 quarterly cycles), cost note | `genesis-proposal.yaml` |
| **3 — Human sign-off** | A new roster is ALWAYS a human decision | Approved by owner directive 2026-07-07 (decision recorded with approver, date, and scope: build as protocol demonstration) | `genesis-proposal.yaml` → `decision` |
| **4 — Construction** | Standard machinery only: roster doc pattern, agent YAMLs fully AOM-compliant at lifecycle `draft`, validator green + manifest in the SAME commit, architecture registry PATCH | Roster doc v1.0.0 (`Draft — seed`), 3 lean agent YAMLs at lifecycle `draft` (all GPARL phases, ≥3 constraints, non-fabrication + blocking gates, orchestrator escalation handoffs), manifest block added, framework-architecture → v1.2.5, validator run before commit | this directory + `rosters/manifest.yaml` + `constitutional/framework-architecture-v1.2.5.md` |
| **5 — Probation** | First engagement = probation; retirement condition armed | PENDING by design — no engagement has activated this roster. Retirement clock armed: not activated within 2 quarterly cycles → propose archive | roster doc → Versioning Rules |

## Validator result at construction

```
Framework Validator — 35 agents, 0 errors
```

(32 pre-existing agents + the 3 recruitment seed agents; run
`python3 scripts/validate_framework.py` to reproduce.)

## The three seed agents

| Agent | Authority | Defining gate |
|-------|-----------|---------------|
| `roster_recruitment_orchestrator_agent` | Orchestrates; makes NO hiring decisions | Human-decision gate: no candidate-affecting decision by any agent; offers held at draft until logged human/legal sign-off |
| `recruitment_talent_attraction_agent` | Designs funnel, channels, role profiles; recommendations only | Recommendation-only gate + non-fabrication (market data cited or TBC); brand-facing copy consumed from roster-content, never produced (reuse rule) |
| `recruitment_compliance_contracts_agent` | Tracks checks against evidence; DRAFTS offers/contracts | Contract release gate: nothing leaves draft status — issue is always a human/legal act. A check without evidence is TBC; a TBC mandatory check blocks the offer |

## What this demonstrates

1. **The ladder bites.** The fictional need did NOT become "an HR team" —
   half of it was served by existing rosters at R1, and the seed only houses
   what is genuinely un-homed.
2. **The cap holds.** The seed is orchestrator + 2 specialists — under the
   protocol's max-3 hard cap. Onboarding and retention agents are declared as
   *expansion path*, not built speculatively.
3. **The dangerous part is gated by construction.** Contract work exists in
   the ecosystem now, but issuing a contract is structurally impossible for
   an agent: the constraint, the blocking gate, and the handoff brief all
   state it, and the orchestrator enforces it a second time.
4. **Growth and shrinkage are symmetric.** The roster carries its own
   retirement condition from birth.

## Boundaries of this demonstration

- The scenario is fictional; no interview was actually run. The trigger
  evidence says so explicitly (non-fabrication).
- The agents are at lifecycle `draft` and have never executed. Probation
  (Stage 5) awaits a first real engagement.
- Approval was an owner directive to demonstrate the protocol — a real
  genesis would route the proposal through the AI Manager's sign-off brief.
