# Agent Framework — Full System Architecture
**Document ID:** `framework-architecture`
**Version:** `v1.2.6`
**Created:** 2026-03-25
**Last Updated:** 2026-07-07
**Scope:** Constitutional — applies to all businesses and clients

---

## Version History

| Version | Date | Type | Change Summary | Triggered By |
|---------|------|------|----------------|--------------|
| v1.2.3 | 2026-07-07 | Patch | Privacy scrub — genericised the worked example (real client business replaced with the fictional "Riverside Bookings"); no rule or behaviour change | Repo genericisation for public release |
| v1.0.0 | 2026-03-25 | Major | Initial architecture definition | Manual — framework creation |
| v1.2.6 | 2026-07-07 | Patch | Genesis pipeline wired end-to-end: interview v2.1.0 (structured `genesis_candidates` detection), ECL Orchestrator v1.1.0 (ladder + proposal drafting, genesis authority gate), `runtime/genesis.py` (proposal → decisions queue → dashboard decision inbox; no approve path in code); roster-genesis-protocol v1.0.1. Constitutional-doc registry version column refreshed | Owner directive — close the genesis capture + surfacing gaps |
| v1.2.5 | 2026-07-07 | Patch | roster-recruitment registered — first live execution of the Roster Genesis Protocol (approved proposal at rosters/recruitment/genesis-proposal.yaml): seed roster at lifecycle draft, orchestrator + talent attraction + compliance/contracts (drafting only), probation pending first engagement | Genesis proposal approved — human sign-off (owner directive) |
| v1.2.4 | 2026-07-06 | Patch | Roster Genesis Protocol registered (constitutional/roster-genesis-protocol-v1.0.0.md) — governed creation of new rosters/agents from detected gaps: right-sizing ladder, human-signed proposals, seed cap, probation/retirement. Templates set v1.3.0. | Owner directive |
| v1.1.0 | 2026-07-02 | Minor | roster-appdev registered; cross-roster collaboration routes (SEO ↔ App Dev) documented; registry versions refreshed | roster-appdev v1.0.0 activation — human sign-off received |
| v1.2.2 | 2026-07-06 | Patch | Runtime kernel built and registered — minimum deterministic kernel at `runtime/` (heartbeat/dead-agent detection, checkpointing, gate-runner, budget pause/resume, workspace isolation, termination attribution, structured state emission; 14/14 tests). Real subagent executor stubbed. Also reflects pilot backlog bumps (AOM v1.2.0, engagement-lifecycle v1.1.0, context-memory v1.1.0, ecl-framework v1.1.0, interview v2.0.0, roster-content v1.1.0). | Pilot RSB-01..05 + ASA recommendation #9 |
| v1.2.1 | 2026-07-03 | Patch | Registry refresh (AOM v1.0.2) — and roster/agent version columns replaced with a pointer to rosters/manifest.yaml, which is the single authoritative, CI-validated version registry. Prose tables no longer duplicate versions that drift. | Final deep audit |
| v1.2.0 | 2026-07-02 | Minor | Framework hardening: engagement-lifecycle + context-memory-protocol registered; ai_manager_agent + client_account_manager_agent added; roster-content (seed) registered; roster manifest, Python validator + CI, and templates/ introduced; runtime designated (Claude Code → Agent SDK) | Framework review — human sign-off received |

---

## The Full Stack

```
╔═══════════════════════════════════════════════════════════════════╗
║              EXECUTIVE COMMAND LAYER (ECL)                        ║
║                                                                   ║
║  North Star · Why/What/How/When · SWOT · Target Operating Model  ║
║                                                                   ║
║  Functional Domains:                                              ║
║  Finance | Sales | Marketing | Ops | Product | Tech |            ║
║  HR & People | Legal | AI Manager                                 ║
║                                                                   ║
║  Cycle: Annual (MAJOR) · H1 · Quarterly (MINOR) · Monthly (PATCH)║
║                                                                   ║
║  [ ECL Orchestrator ]                                             ║
║       │                                                           ║
║       │  cascades objectives · responds to queries               ║
║       │  escalates MAJOR decisions to human                       ║
╚═══════╪═══════════════════════════════════════════════════════════╝
        │
        ├──────────────────────────────────────────────┐
        │                                              │
        ▼                                              ▼
╔═══════════════════════════╗   ╔═══════════════════════════╗   ╔═══════════════════╗
║   ROSTER: SEO             ║   ║   ROSTER: APP DEV         ║   ║   ROSTER: [NEXT]  ║
║   roster-seo              ║   ║   roster-appdev           ║   ║   e.g. Paid Media ║
║                           ║   ║                           ║   ║   e.g. Email      ║
║   [ Roster Orchestrator ] ║   ║   [ Lead Dev Orchestrator]║   ║   e.g. Operations ║
║          │                ║   ║          │                ║   ╚═══════════════════╝
║    ┌─────┼──────┐         ║   ║   ┌──────┼────────┐       ║
║    ▼     ▼      ▼         ║   ║   ▼      ▼        ▼       ║
║   SEO   AEO    GEO        ║   ║  Plan/  Eng     QA/Sec/   ║
║   Agents Agents Agents    ║   ║  Design Agents  Insight   ║
╚═══════════════════════════╝   ╚═══════════════════════════╝
```

---

## Information Flow

### Downward (ECL → Rosters)
```
ECL produces objectives
    → ECL Orchestrator generates cascade briefing
        → Roster orchestrators receive briefing
            → Roster agents load updated engagement_context
                → Agent decisions align to new objectives
```

### Upward (Rosters → ECL)
```
Roster performance data collected by Agent 11 (Performance Reporting)
    → Roster orchestrator compiles KPI report
        → ECL Orchestrator receives cross-roster health data
            → AI Manager domain updated
                → Monthly/quarterly ECL review informed
                    → Objectives refined if needed
```

### Lateral (Roster → ECL → Roster)
```
Roster A encounters a major decision
    → Queries ECL Orchestrator
        → ECL returns relevant objectives + constraints
            → Roster A proceeds with decision aligned to ECL
                → If decision affects Roster B:
                    → ECL Orchestrator notifies Roster B orchestrator
```

**Rule:** Rosters never hand off to each other directly. A cross-roster
dependency is always routed through the ECL Orchestrator, which validates
it against current objectives before notifying the receiving roster's
orchestrator. Direct roster-to-roster handoffs would bypass ECL scope
control and are an AOM Section 3 compliance failure.

### Declared Cross-Roster Collaboration Routes

Cross-roster routes that recur are declared here so both rosters carry
the same contract. All routes below run via the ECL Orchestrator per the
lateral rule.

| Route | From (producing roster/agent) | To (consuming roster) | What flows |
|-------|------------------------------|----------------------|------------|
| SEO → App Dev | `roster-seo` / `seo_technical_agent` | `roster-appdev` (requirements intake) | `implementation_checklist` — technical SEO fixes specified for developers |
| SEO → App Dev | `roster-seo` / `aeo_schema_entity_agent` | `roster-appdev` (requirements intake) | `schema_markup_per_page` + placement spec — JSON-LD to implement in the build |
| SEO → App Dev | `roster-seo` / `seo_search_architecture_agent` | `roster-appdev` (architecture input) | `site_architecture_map` — URL structure the build must implement and preserve |
| App Dev → SEO | `roster-appdev` / release notification | `roster-seo` (orchestrator) | Site structure, routing, or performance changes → SEO cascade review (MINOR-bump event) |
| App Dev → SEO | `roster-appdev` / `insight_business_analytics_agent` | `roster-seo` / `performance_reporting_agent` | Shared analytics instrumentation (GA4/Vercel) — one measurement source, two reporting views |

**Consumption rule:** outputs arriving from another roster enter the
receiving roster as **confirmed requirements/inputs** (e.g. into
`analysis_business_analyst_agent`'s backlog for App Dev), never as direct
agent-to-agent handoffs. The receiving orchestrator sequences them like
any other engagement input.

---

## Document Registry

### Constitutional Documents (apply to all businesses)

| Document | ID | Current Version | Purpose |
|----------|----|----------------|---------|
| ECL Framework | `ecl-framework` | v1.1.1 | Master ECL template; tier-dependent domains |
| AI Operating Model | `aom-framework` | v1.2.1 | Agent ecosystem governance |
| Framework Architecture | `framework-architecture` | v1.2.6 | This document — system overview |
| Engagement Lifecycle | `engagement-lifecycle` | v1.1.0 | Tier ladder T0-T2 (SME) + sizing instrument; pre-flight, cadence, pause, offboarding |
| Roster Genesis Protocol | `roster-genesis-protocol` | v1.0.1 | Governed creation of new rosters/agents: detect → right-size → propose → human sign-off → construct → probation. Detection/surfacing wired: interview `genesis_candidates` → orchestrator ladder/draft → runtime decisions queue |
| Context & Memory Protocol | `context-memory-protocol` | v1.1.0 | Layered context, retrieval ladder, log rotation, learnings memory, token budgets |

### Constitutional Agents

| Agent | ID | Purpose |
|-------|----|---------|
| ECL Interview | `ecl_interview_agent` | Business intake (modular, mandate matrix, evidence locker) — produces the draft ECL |
| ECL Orchestrator | `ecl_orchestrator_agent` | Apex orchestrator — cascades, queries, arbitration |
| AI Manager | `ai_manager_agent` | Governance crank-turner — audits, digests, bump processing, human sign-off briefs |
| Client Account Manager | `client_account_manager_agent` | Client comms cadence, approval chasing, signal capture |

Current versions: `rosters/manifest.yaml` (authoritative, CI-validated).

### Roster Documents (discipline-specific, reusable)

| Document | ID | Purpose |
|----------|----|---------|
| SEO Roster | `roster-seo` | SEO/AEO/GEO agent roster (12 agents) |
| App Dev Roster | `roster-appdev` | Application development roster (13 agents) — default stack Vercel/Neon/Clerk/Resend |
| Content Roster | `roster-content` | Content & copywriting roster (3 agents incl. brand steward) — marketingskills pinned v2.6.0 |
| Recruitment Roster | `roster-recruitment` | Recruitment seed roster (3 agents, lifecycle draft) — Roster Genesis Protocol first run; contracts drafting-only, every offer human/legal-signed |

Current roster and agent versions: `rosters/manifest.yaml` (authoritative, CI-validated).

### Framework Infrastructure

| Artifact | Location | Purpose |
|----------|----------|---------|
| Roster Manifest | `rosters/manifest.yaml` | Machine-readable registry of every agent, version, file — validated in CI |
| Validator | `scripts/validate_framework.py` | Authoritative AOM compliance + drift check (CI-enforced on every push) |
| CI Workflow | `.github/workflows/validate.yml` | Runs the validator + legacy shell checker on push/PR |
| Templates | `templates/` | Canonical artifact templates (16) — see templates/README.md |

---

## Runtime

**Designated runtime:** Claude Code. Agent definitions map to Claude Code
subagents/skills; orchestrator logic runs as the main loop; instance
repos hold logs, cards, and memory files; scheduled cadences
(engagement-lifecycle Stage 2) run via scheduled sessions or CI cron.

**Productisation path:** when engagements need unattended scheduled
execution at scale, migrate the orchestration loop to the Claude Agent
SDK (same definitions, programmatic harness). Changing the designated
runtime is a MINOR bump to this document.

**Runtime kernel (built — `runtime/`).** A minimum deterministic kernel now
exists: per-wave heartbeat + hard timeout + **dead-agent detection** (fixes the
pilot's 41h silent death), state checkpointing with idempotent resume, a
**gate-runner** (failed gates block dependents, recorded), **budget-aware**
graceful pause/resume, per-agent **workspace/port isolation**, accurate
**termination-cause attribution**, and **structured state emission**
(`wave-status.yaml`, `metrics-ledger.jsonl`, `integrity-register.jsonl`,
`decisions-queue.yaml`) — the dashboard's data contract. 14/14 tests pass;
`python -m runtime.demo` shows death-detection and gate-blocking live.

**Real vs stubbed (honest):** the kernel logic is real and tested against a
pluggable `MockExecutor`; the `ClaudeSubagentExecutor` (real subagent spawning)
is a documented stub. Wiring it + a tool-resilience layer is the next milestone.
Until then, cadence execution remains human-supervised and the pre-flight record
must state so (engagement-lifecycle, Stage 2).

### Business Instance Documents (one set per business/client)

| Document | ID | Template Source | Purpose |
|----------|----|----------------|---------|
| `ecl-[business-id]-v1.0.0.md` | Unique per business | `ecl-framework` | Live ECL for this business |
| `roster-registry-[business-id].yaml` | Unique per business | Section 5 of ECL | Active rosters for this business |
| `cascade-[business-id]-[version]-[date].md` | Generated per cycle | ECL cascade protocol | Briefing issued to rosters |

---

## Versioning Across the Stack

```
CONSTITUTIONAL LAYER
ecl-framework            v1.0.0   ← Changes only when framework itself evolves
aom-framework            v1.0.2   ← Changes only when governance rules evolve
framework-architecture   v1.2.1   ← Changes only when architecture changes
engagement-lifecycle     v1.0.0   ← Changes when lifecycle protocol evolves
context-memory-protocol  v1.0.0   ← Changes when context/memory rules evolve

ROSTER LAYER (reusable across businesses) — versions illustrative;
rosters/manifest.yaml is authoritative
roster-seo             v1.2.x   ← Changes when SEO discipline evolves
roster-appdev          v1.0.x   ← Changes when delivery discipline evolves
roster-content         v1.0.x   ← Changes when content discipline evolves
roster-recruitment     v1.0.x   ← Changes when recruitment discipline evolves
                                   PATCH: agent rule updated
                                   MINOR: agent added/removed
                                   MAJOR: discipline strategy pivots

BUSINESS INSTANCE LAYER (unique per business)
ecl-riverside-bookings   v1.0.0   ← Changes when business objectives change
                                   PATCH: KPI threshold updated
                                   MINOR: new objective added
                                   MAJOR: North Star changes
```

**Key principle:** A business instance ECL changing does NOT automatically
version-bump the ECL framework. The framework only changes when the
template itself is improved. Business instances are populated from the
framework template — they are not the framework.

---

## Activation Checklist — New Business or Client

```
[ ] 1. ECL Interview Agent conducts business interview
[ ] 2. Draft ECL produced (v0.1.0)
[ ] 3. Human reviews and edits draft ECL
[ ] 4. Human signs off — ECL versioned to v1.0.0, status: Active
[ ] 5. Roster Registry initialised
[ ] 6. ECL Orchestrator initialised with business ECL loaded
[ ] 7. First roster identified and activated (read ECL at kickoff)
[ ] 8. Subsequent rosters activated in dependency order
[ ] 9. First cascade briefing issued (confirms all rosters on same ECL version)
[ ] 10. First monthly management review scheduled
[ ] 11. Quarterly review dates set for full year
```

---

## Cycle Cadence Overview

```
ANNUAL          ┌─────────────────────────────────────────────────┐
                │  ECL MAJOR review · North Star check             │
                │  All roster MAJOR decisions reviewed             │
                │  New year objectives set                         │
                └─────────────────────────────────────────────────┘

H1              ┌─────────────────────────────────────────────────┐
                │  Mid-year strategic check                        │
                │  SWOT refresh · Roster priority rebalance        │
                └─────────────────────────────────────────────────┘

QUARTERLY       ┌───────────┐ ┌───────────┐ ┌───────────┐ ┌──────┐
                │    Q1     │ │    Q2     │ │    Q3     │ │  Q4  │
                │OKR review │ │OKR review │ │OKR review │ │Y/E   │
                │Cascade    │ │Cascade    │ │Cascade    │ │      │
                └───────────┘ └───────────┘ └───────────┘ └──────┘

MONTHLY         ┌──┐┌──┐┌──┐┌──┐┌──┐┌──┐┌──┐┌──┐┌──┐┌──┐┌──┐┌──┐
                │M ││M ││M ││M ││M ││M ││M ││M ││M ││M ││M ││M │
                │KPI dashboard · PATCH bumps · AI Manager review  │
                └──┘└──┘└──┘└──┘└──┘└──┘└──┘└──┘└──┘└──┘└──┘└──┘

CONTINUOUS      Agent cycle: Goal→Plan→Act→Review→Learn
                Roster orchestrators monitor KPIs · Agents execute tasks
                Performance data flows upward to ECL
```

