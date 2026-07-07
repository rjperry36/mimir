# Engagement Lifecycle Protocol
**Document ID:** `engagement-lifecycle`
**Version:** `v1.1.0`
**Status:** `Active`
**Classification:** `Constitutional — peers with ECL Framework and AOM`
**Created:** 2026-07-02
**Owner:** AI Manager (constitutional role)

---

## Version History

| Version | Date | Type | Change Summary | Triggered By |
|---------|------|------|----------------|--------------|
| v1.0.0 | 2026-07-02 | Major | Initial lifecycle protocol: pre-flight, profiles, in-flight cadence ownership, pause, offboarding | Framework review — human sign-off received |
| v1.1.0 | 2026-07-06 | Minor | Replaced the binary full/lite profile with an SME-scoped TIER LADDER (T0 micro / T1 small business / T2 SME); added the multi-axis sizing instrument (human-confirmed tier recommendation, human override); tier drives ECL depth, roster+agent set, cadence, governance topology; full/lite retained as back-compat aliases for T1/T0; T3–T4 (mid-market/enterprise, ECL hierarchy, RBAC) documented as explicitly OUT OF SCOPE / reserved-uncoded | Framework backlog (framework-scaling-and-domains Q2, owner scope decision 2026-07-06) — human sign-off received |

---

## Purpose

The ECL Framework defines *what* a business is aiming for. The AOM defines
*how* agents must be built. This document defines **the life of an
engagement**: how it is sized before it starts, who turns the crank while
it runs, and how it ends cleanly. An engagement that cannot be started
proportionately, run without human toil, or ended without loose ends is
a liability regardless of how well its agents are defined.

---

## Stage 1 — Pre-Flight (before activation)

Run after ECL sign-off, before any roster activates.
**Artifact:** `templates/preflight-checklist-template.md` → completed
pre-flight record stored in the instance repo.
**Run by:** `ecl_orchestrator_agent`, signed by the human.

Pre-flight answers four questions:

1. **Which outcome?** Every engagement names the ECL objective it serves.
   No orphan engagements.
2. **Which tier?** (see Engagement Tiers below) — the sizing instrument
   is answered at interview, the recommended tier is human-confirmed,
   and the confirmed tier is recorded in `roster-config.yaml`.
3. **Which team?** Roster-by-roster, agent-by-agent selection, driven by
   the confirmed tier. Lower-tier engagements explicitly exclude agents —
   exclusions are recorded with reasons in `roster-config.yaml`, so a
   lean crew is a decision, not an accident.
4. **What's missing?** Gap analysis: required capabilities with no
   existing agent (→ MINOR roster bump to add) or no existing roster
   (→ framework addition, human sign-off). Required tools missing from
   toolboxes (→ AI Manager toolbox proposal). Human dependencies with
   named owners and AOM timeout classes.

**Rule:** activation without a completed, human-signed pre-flight record
is a compliance failure.

---

## Engagement Tiers

The framework scales to the business, not the other way round. Sizing is
a **tier ladder**, not a binary. The framework's target market is
**small-to-large SME**, so the coded ladder runs **T0 → T2**; larger
tiers are documented and reserved but not built (see *Out of Scope*
below). This replaces the earlier binary full/lite profile
(framework-scaling-and-domains Q2; owner scope decision 2026-07-06).

### The tier ladder (SME-scoped — coded)

| Tier | Profile | ECL depth | Rosters | Governance / approval topology |
|------|---------|-----------|---------|--------------------------------|
| **T0** | **Micro / sole trader** | 3–4 core domains only | 1 lean roster | Single owner |
| **T1** | **Small business** (the pilot sat here) | Core domains populated; others skipped | 1–2 rosters | Owner + optional advisor |
| **T2** | **SME / multi-function** | Most domains populated | Several rosters | Owner + domain approvers |

Domain depth per tier is defined by the ECL Framework's tier-dependent
domain set (see `ecl-framework` §3 — core domains always live,
tier-gated domains switch on as the tier rises). The interview confirms
which domains are live for **this** business rather than forcing all
nine.

### The sizing instrument (multi-axis, human-confirmed)

"Size" as headcount or revenue misleads — required depth is driven by
complexity. The instrument scores six axes at interview:

| Axis | Drives |
|------|--------|
| Regulatory / compliance load | Legal depth, approval gates, audit intensity |
| Business units / legal entities | Domain breadth and roster count |
| Geographies / markets | Localisation, multi-market cadence |
| Data sensitivity | Security/data-governance depth |
| Decision value at stake | Approval topology (owner vs owner + approvers) |
| Headcount | HR/People depth, cadence |

The instrument **recommends** a tier; it never auto-computes a binding
one (no false precision). The recommendation is **human-confirmed at
interview and the human may override it** in either direction. The
confirmed tier is recorded in every `roster-config.yaml`.

### What the tier drives

A confirmed tier deterministically sets four things:

1. **ECL depth** — which functional domains are required, optional, or
   skipped (per `ecl-framework` §3 tier-dependent domain set).
2. **Roster & agent set** — which rosters activate and whether agents run
   lean or full; exclusions recorded in `roster-config.yaml`.
3. **Cadence** — from T0 light-touch monthly review up to the full ECL
   cycle (monthly/quarterly/annual) at T2.
4. **Governance / approval topology** — from single-owner sign-off (T0)
   to owner + domain approvers (T2). Full AOM governance applies at every
   tier — governance never gets a lite mode; only the number of approvers
   and audit intensity scale with tier.

A business may be re-tiered up (or down) at any quarterly review (MINOR
event, cascade issued), re-running the sizing instrument.

### Back-compat aliases

The retired `full` / `lite` labels remain valid as **aliases** for
back-compatibility: **`lite` → T0**, **`full` → T1**. Existing
`roster-config.yaml` records carrying a profile are read as their alias
tier until re-tiered at the next quarterly review.

### Out of scope — reserved, not coded (T3–T4)

Tiers **T3** (mid-market / multi-BU) and **T4** (enterprise / global)
are **explicitly OUT OF SCOPE** and deliberately **not coded**. They are
retained here only as a named, documented reservation. They require
genuinely new design — a **nested / federated ECL hierarchy** (Group →
Division → Market cascade + upward consolidation), **role-based access
control and separation of duties** replacing the single-approver model,
and **corporate domains** (Risk, ESG, Investor Relations, M&A,
Data/Privacy) as first-class. Building these for businesses not yet
served would be exactly the unnecessary sophistication the framework
avoids. Extension points are designed (the tier ladder does not block
the path up); the structures themselves are not built.

---

## Stage 2 — In-Flight (who turns the crank)

The framework runs on schedules, and schedules need an executor. The
crank has three layers of ownership:

| Layer | Owner | What it turns |
|-------|-------|---------------|
| Delivery | Roster orchestrators | Wave sequencing, handoff monitoring, agent queries, KPI watch between reports |
| Governance | `ai_manager_agent` | Daily flag scans, monthly reviews + digests, quarterly compliance audits, bump processing (its `operating_cadence`) |
| Client | `client_account_manager_agent` | Communication cadence, input/approval chasing before AOM timeouts, client signal capture |

**The human is in the loop by exception:** informed via the governance
digest and client packs; interrupted only for AOM Section 4/7 sign-offs
and threshold breaches. The human never has to remember to check —
the system's job is to bring decisions to them, prepared.

**Runtime note:** these cadences require a scheduler. The designated
runtime (framework-architecture, Runtime section) is responsible for
firing scheduled agent runs. Until a runtime is live for an instance,
cadence execution is manual and the pre-flight record must say so.

---

## Stage 3 — Pause

A pause suspends an engagement without ending it (payment issues,
client-side blockage, seasonal stop).

```
Human authorises pause (always human — AOM S7)
  → ecl_orchestrator_agent notifies all active roster orchestrators
    → In-flight agent tasks: complete if <48h to finish, else checkpoint
      state to engagement_log and stop
      → Scheduled cadences suspended EXCEPT: ai_manager_agent daily
        flag scan (governance never pauses) and legal/compliance
        cascade triggers
        → roster-registry status → paused · client informed via
          client_account_manager_agent
```

Resume = reverse, with a mandatory cascade check first (has the ECL
version moved while paused?).

**Rule:** a pause older than 90 days triggers a human decision:
resume, or proceed to offboarding. No zombie engagements.

---

## Stage 4 — Offboarding / Close-Out

Ends an engagement cleanly — client departure, completion, or
termination. **Artifact:** `templates/engagement-closeout-template.md`.
**Always human-signed.**

The six close-out obligations, in order:

1. **In-flight disposition** — every running task completed, handed
   over, or explicitly abandoned. Nothing left mid-air.
2. **Deliverable handover** — terminal outputs delivered; client-owned
   assets (domains, GBP listings, repos, analytics) confirmed under
   client control.
3. **Data retention & destruction** — PII purged per Legal domain
   constraints; credentials revoked and rotated; instance repo archived
   private with a stated retention period.
4. **Memory harvest** — a final LEARN cycle runs across active agents;
   `learnings.yaml` distilled per the Context & Memory Protocol;
   client-specific memory marked as such, generalisable insights
   promoted to roster memory. The engagement's experience survives it.
5. **Registry & logs** — rosters deprecated/archived in the registry;
   all logs finalised and archived (principle C6: history stays
   reconstructable).
6. **Final client communication** — close-out pack via
   `client_account_manager_agent`.

**Rule:** an offboarding is complete only when the close-out record is
signed. Unsigned close-outs appear in every `ai_manager_agent` digest
until resolved.

---

## Registry

| Stage | Artifact | Template |
|-------|----------|----------|
| Pre-flight | Pre-flight record | preflight-checklist-template.md |
| Activation | (existing) framework-architecture activation checklist | — |
| In-flight | Governance digest, client packs, logs | — |
| Pause | Pause record in engagement_log | — |
| Close-out | Close-out record | engagement-closeout-template.md |
