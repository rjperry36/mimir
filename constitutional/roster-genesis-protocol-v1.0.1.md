# Roster Genesis Protocol
**Document ID:** `roster-genesis-protocol`
**Version:** `v1.0.1`
**Status:** `Active`
**Classification:** `Constitutional — peers with Engagement Lifecycle and Context & Memory Protocol`
**Created:** 2026-07-06
**Owner:** AI Manager (constitutional role) · **Authorised by:** Russ Perry (owner directive)

---

## Version History

| Version | Date | Type | Change Summary | Triggered By |
|---------|------|------|----------------|--------------|
| v1.0.1 | 2026-07-07 | Patch | Detection and approval wired into running software: interview v2.1.0 emits structured `genesis_candidates` (Stage 1); ECL Orchestrator v1.1.0 runs the ladder and drafts proposals (Stage 2); `runtime/genesis.py` queues drafted proposals on the decisions queue as `GENESIS_PROPOSAL` items with the proposal as linked document, decided on the dashboard's decision inbox (Stage 3). No rule change | Owner directive — close the capture + surfacing gaps |
| v1.0.0 | 2026-07-06 | Major | Initial protocol: how new agent teams (rosters) and agents are created from detected capability gaps — detect → right-size → propose → human sign-off → construct → probation | Owner directive — "can the interview create teams?" |

---

## Purpose

The ECL interview and pre-flight can *detect* that a client needs a capability
no existing roster provides (e.g. a care provider needs to recruit care
workers). This protocol defines how that detection becomes a new, governed
team — **and, just as importantly, when it must not**.

Two constitutional constraints frame everything below:

- **The ecosystem never grows itself autonomously.** A new roster or agent is
  always a human-signed decision (AOM Section 4 authority matrix). Agents
  detect, right-size, and draft; humans approve.
- **New teams are a last resort, not a first instinct** (the ASA
  anti-sophistication principle). Most needs are served by a strategy on an
  existing roster. A roster exists to house a *discipline*, not a task.

---

## Stage 0 — Right-Sizing Ladder (mandatory, before any proposal)

Every detected gap must be walked DOWN this ladder and may only escalate a
rung with documented evidence that the rung below cannot serve the need:

| Rung | Response | Governance cost | Choose when |
|------|----------|-----------------|-------------|
| **R1** | **Strategy/objective on an existing roster** — the need becomes an ECL objective cascaded to a roster that already has the skills, possibly via declared cross-roster routes | None (cascade) | The skills exist; only the *audience or subject* is new. e.g. job advertising is marketing with a different audience |
| **R2** | **New agent in an existing roster** | Roster MINOR + human sign-off | One missing specialism inside a discipline that has a home. e.g. `content_brand_steward_agent` joined roster-content |
| **R3** | **New seed roster** (this protocol's main path) | New roster + human sign-off | A whole *discipline* has no home — its work, tools, and quality gates don't belong to any existing roster |
| **R4** | **Decline / defer** | Log only | The need is out of scope (tier, exclusion zone, regulatory) or better bought than built |

**Evidence rule:** an R3 proposal must name the existing rosters/agents
considered at R1/R2 and state specifically why each cannot serve the need.
A proposal without this analysis is returned unread.

**Reuse rule:** a new roster may not duplicate a capability that exists —
it must consume it via declared cross-roster routes (e.g. a recruitment
roster does NOT get its own copywriter; job-ad copy routes to roster-content).

---

## Stage 1 — Trigger Sources (who detects)

| Source | Artifact | When |
|--------|----------|------|
| ECL interview (`ecl_interview_agent` v2.1.0+) | `genesis_candidates` — every roster recommendation is checked against `rosters/manifest.yaml`; each UN-HOMED discipline is emitted as a structured Stage 0 evidence package (discipline, objectives served, observed work/tools/gates with citations). Detection only — never a proposal | Onboarding / re-interview |
| Pre-flight gap analysis | Pre-flight checklist §4 ("required capability with NO existing agent/roster") | Engagement sizing |
| In-flight scope events | Owner requests, orchestrator queries (routed via ECL) | Any time |
| LEARN harvest | Version-bump proposals identifying recurring un-homed work | Close-out / quarterly |

All triggers converge on the same next step: the drafting party (below)
runs the Stage 0 ladder and, only if R3 survives, drafts a proposal.

---

## Stage 2 — Genesis Proposal (the draft team)

**Drafted by:** the ECL Orchestrator (business alignment) with the AI Manager
(governance/compliance shape) — in practice the runtime executes the drafting;
neither may approve their own draft.

**Artifact:** `templates/roster-genesis-proposal-template.yaml` — one proposal
per candidate roster, containing:

1. The gap + trigger evidence, and the completed Stage 0 ladder analysis
2. Discipline, mission (one paragraph), and ECL objective(s) served
3. Tier fit (which engagement tiers T0–T2 would activate it)
4. **Seed team — hard cap: orchestrator + max 3 specialists, all lean depth.**
   Each agent: proposed id (AOM naming), role, one-line goal, key gates
5. Toolbox needs (new tools = flagged per AOM Section 6)
6. Cross-roster routes consumed/offered (the reuse rule made explicit)
7. Human-gate and exclusion-zone implications — anything the new team touches
   that is legally sensitive, spend-committing, or brand-affecting gets its
   mandatory human gate stated here, in the proposal, not discovered later
8. Expansion path (like roster-content's) and a **retirement condition**
   (see Stage 5)
9. Cost note: estimated agent-runs per engagement cycle

---

## Stage 3 — Human Sign-Off

Per the AOM authority matrix: **a new roster always requires human sign-off.**
The owner may approve, amend (e.g. cut the seed to fewer agents), or reject.
Rejections are logged with reason — a rejected discipline re-proposed later
must address the recorded reason.

**How it reaches the human:** `runtime/genesis.py` places the drafted proposal
on the engagement's decisions queue as a `GENESIS_PROPOSAL` item (executive
review window per AOM S3.3), with the proposal YAML as the linked document —
the owner reads it on the dashboard's document-review surface and decides it
from the decision inbox like any other gated document. The plumbing is
deterministic software with **no approve path in code**: the only thing the
runtime can do with a proposal is queue it for a human.

---

## Stage 4 — Construction & Activation

On approval, the roster is built with the framework's standard machinery —
nothing bespoke:

1. Roster doc from the established pattern (mission, principles, agent table,
   toolbox, engagement flow, version-bump map) at `v1.0.0`, status `Draft — seed`
2. Agent YAMLs from existing agents as structural templates — full AOM
   compliance (naming, all sections, GPARL cycle, non-fabrication gate,
   escalation handoff), lifecycle `draft`
3. `scripts/validate_framework.py` green + manifest updated **in the same
   commit** (CI enforces)
4. Lifecycle: `draft → review` (compliance check) `→ active` per the AOM;
   activation into an engagement follows the normal pre-flight
5. Registration: framework-architecture registry row (PATCH)

---

## Stage 5 — Probation & Review

A genesis roster's **first engagement is its probation**:

- The LEARN harvest at that engagement's close explicitly reviews the roster:
  deepen (lean → full definitions), reshape (merge/split agents), or retire
- **Retirement condition** (declared in the proposal): a seed roster not
  activated by any engagement within its stated window (default: 2 quarterly
  cycles) is proposed for archive at the AI Manager's quarterly review —
  the ecosystem sheds teams as deliberately as it grows them

---

## Worked Example — "we need to recruit more care workers"

A domiciliary care provider's interview lands a headcount objective in the
ECL HR & People domain: *recruit 12 care workers in 6 months.* The ladder:

- **R1 — partially serves:** job advertising, employer-brand content and a
  careers page are marketing/content work → a recruitment *strategy* cascades
  to roster-content and the marketing rosters via existing routes. ✓ Adopted
  for the attraction half.
- **R2 — fails:** candidate pipeline management, care-sector compliance
  (DBS/safeguarding checks tracking), and offer/contract drafting fit no
  existing roster's discipline; bolting them onto marketing would violate the
  discipline rule.
- **R3 — proposal:** seed `roster-recruitment` — orchestrator +
  `recruitment_talent_attraction_agent` (channels/pipeline, consuming
  roster-content for copy) + `recruitment_compliance_contracts_agent`
  (checks tracking; contract DRAFTING only — every contract and every offer
  is a **mandatory human/legal sign-off**, per the AOM's standing rule that
  legal determinations are never autonomous).
- Sign-off → construct → probation on the first recruitment engagement.

The answer to "HR team, marketing strategy, or contract writers?" is therefore
**all three at the right rung**: strategy on existing teams (R1) + a lean seed
for the un-homed discipline (R3) + contract drafting as a gated agent inside
it — never a standalone autonomous contracts team.

---

## Registry

| Artifact | Location |
|----------|----------|
| Genesis proposal template | `templates/roster-genesis-proposal-template.yaml` |
| Pre-flight trigger | `templates/preflight-checklist-template.md` §4 |
| Interview detection (Stage 1) | `ecl_interview_agent` v2.1.0 — `genesis_candidates` output + genesis-candidate integrity gate |
| Ladder + drafting (Stage 2) | `ecl_orchestrator_agent` v1.1.0 — genesis intake, genesis authority gate |
| Approval surfacing (Stage 3) | `runtime/genesis.py` → decisions queue `GENESIS_PROPOSAL` item → dashboard decision inbox (sample: riverside-bookings `GEN-roster-recruitment`) |
| First live execution (Stages 0–4) | `rosters/recruitment/` — `genesis-proposal.yaml` + `GENESIS-RECORD.md` |
| Authority rule | AOM Section 4 (new roster = human sign-off) |
| Anti-sophistication basis | ASA principles 18–19 (architectural simplicity) |
