# Recruitment Roster
**Roster ID:** `roster-recruitment`
**Version:** `v1.0.0`
**Status:** `Draft — seed roster (genesis; probation pending first engagement)`
**Created:** 2026-07-07
**Owner:** Russell Perry
**Provenance:** `rosters/recruitment/genesis-proposal.yaml` — first live execution of `constitutional/roster-genesis-protocol` v1.0.0

---

## Version History

| Version | Date | Type | Change Summary | Triggered By |
|---------|------|------|----------------|--------------|
| v1.0.0 | 2026-07-07 | Major | Initial seed roster via the Roster Genesis Protocol (Stage 4 construction): orchestrator + talent attraction + compliance/contracts (drafting only). Built at lifecycle `draft`; activation follows the first pre-flight. | Genesis proposal approved — human sign-off (owner directive 2026-07-07) |

### Versioning Rules

Standard semantic versioning per the AOM. This is a **genesis seed roster**: it
starts at the protocol's hard cap (orchestrator + max 3 specialists, all lean)
and its **first engagement is its probation** (protocol Stage 5) — the LEARN
harvest at that engagement's close explicitly decides deepen / reshape / retire.
**Retirement condition:** not activated by any engagement within 2 quarterly
cycles → proposed for archive at the AI Manager's quarterly review.

---

## Roster Mission

Run the recruitment engagement for a client hiring objective: turn an ECL
headcount objective (HR & People domain) into a managed candidate pipeline —
sourcing channels, role profiles, stage tracking, pre-employment compliance
evidence, and human-ready offer/contract drafts — while consuming attraction
work (copy, pages, discoverability) from the rosters that own those
disciplines. **Humans make every hiring decision and sign every offer and
contract.**

---

## Roster Principles

Inherits constitutional principles C1–C6 and roster-agnostic principles P1–P8.
Adds:

### RC1 — Humans Hire
No agent in this roster makes, implies, or communicates a hiring, rejection,
or screening decision. Agents produce evidence, rankings-with-reasons, and
recommendations; every decision that affects a candidate is a logged human act.

### RC2 — Drafting Is Not Issuing
Offers and employment contracts are DRAFTED inside this roster from
human-approved templates and are ISSUED only after a logged human/legal
sign-off. Nothing candidate-binding leaves draft status autonomously — this is
the AOM's standing rule (legal determinations are never autonomous) applied
as a roster-level gate.

### RC3 — Compliance Is Evidence, Not Assertion
A pre-employment check (DBS, right-to-work, references, safeguarding training)
is `passed` only against a named evidence reference in the instance's evidence
locker. A status without evidence is `TBC`, and no candidate progresses to
offer with a TBC mandatory check.

### RC4 — Attraction Is Consumed, Not Duplicated
Job-ad copy, employer-brand content, careers pages, and discoverability belong
to roster-content, roster-appdev, and roster-seo. This roster briefs those
needs out via the ECL (reuse rule, genesis protocol Stage 0) and never
produces brand-facing content itself.

### RC5 — Candidate Data Stays Private
Candidate personal data lives in the private instance repository only — never
in the framework repo, logs, or learning entries (data-separation rule).
Learning-log entries about recruitment reference candidates only by stage
counts and anonymous identifiers.

---

## Roster Structure

```
roster-recruitment/
├── roster-recruitment-v1.0.0.md      ← This document
├── genesis-proposal.yaml             ← Provenance: approved Stage 0–3 record
└── agents/
    ├── agent-00-roster-recruitment-orchestrator-v1.0.0.yaml
    ├── agent-01-talent-attraction-v1.0.0.yaml
    └── agent-02-compliance-contracts-v1.0.0.yaml
```

---

## Agent Roster

### Crew: `people_team` → Sub-crew: `recruitment`

| # | Agent ID | Role | Discipline | Fires After |
|---|----------|------|------------|-------------|
| 00 | `roster_recruitment_orchestrator_agent` | Recruitment Delivery Orchestrator | Recruitment | Engagement start (ECL cascade) |
| 01 | `recruitment_talent_attraction_agent` | Talent Attraction & Pipeline Specialist | Recruitment | Orchestrator brief confirmed |
| 02 | `recruitment_compliance_contracts_agent` | Compliance & Contracts Specialist (drafting only) | Recruitment | Candidate reaches compliance/offer stage |

All three agents are **lean** definitions at lifecycle **`draft`** — per the
genesis protocol, promotion to `active` happens through the AOM lifecycle
(draft → review → active) at the first pre-flight that activates this roster.

---

## Toolbox

### Toolbox Version: `v1.0.0`

| Tool | Purpose | Agents | Integration |
|------|---------|--------|-------------|
| **Document store** | Role profiles, pipeline tracker, compliance register, offer/contract drafts | 00, 01, 02 | Instance outputs/ directory |
| **Candidate pipeline tracker** | Stage tracking + funnel metrics (structured document; ATS-lite) | 01 | New tool flagged per AOM S6 — document-based, no new SaaS commitment at seed |
| **Compliance checklist register** | Per-candidate check status + evidence-locker references | 02 | New tool flagged per AOM S6 — document-based |
| **marketingskills** (roster-content's) | Job-ad / employer-brand technique | — | NOT installed here — consumed via the roster-content route (RC4) |

---

## Cross-Roster Collaboration

Per `framework-architecture` — all routes via the ECL Orchestrator:

| Route | What flows |
|-------|-----------|
| Recruitment → Content | Job-ad copy, employer-brand content, candidate comms template briefs (role-profile facts supplied as verified inputs) |
| Recruitment → App Dev | Careers page / application form build requirements |
| Recruitment → SEO | Careers-page discoverability review request |
| Recruitment → ECL | Hiring-funnel performance data (objective progress reporting) |

---

## Engagement Flow

```
ORCHESTRATOR (00)
│  receives ECL cascade (HR & People hiring objective)
│  decomposes: attraction surface → briefed OUT via ECL (RC4)
│              pipeline + compliance → briefed IN to specialists
│
├── FIRES: Agent 01 (Talent Attraction) per role brief
│       └── Outputs: role profiles, channel plan, pipeline design,
│             funnel tracking reports
│             └── screening RECOMMENDATIONS only → human decides (RC1)
│
└── FIRES: Agent 02 (Compliance & Contracts) per candidate at offer stage
        └── Outputs: compliance checklist (evidence-referenced),
              offer/contract DRAFTS
              └── contract release gate → human/legal sign-off (RC2)
                    └── issued by humans; funnel status → ECL
```

---

## Expansion Path (MINOR bumps, in likely order)

1. `recruitment_onboarding_agent` — post-offer onboarding coordination
2. `recruitment_retention_insight_agent` — attrition/retention analysis feeding the ECL HR domain

---

## Performance Indicators → Version Bump Map

| Indicator | Threshold | Action | Version Bump |
|-----------|-----------|--------|--------------|
| Funnel stalls at the same stage | 2 consecutive review cycles | Pipeline design / channel plan review | PATCH |
| Compliance TBCs repeatedly block offers | 2+ candidates same check class | Evidence-collection process review | PATCH |
| Offer drafts repeatedly amended at legal sign-off | 2+ same amendment class | Template escalation to human/legal owner | PATCH |
| Onboarding coordination needed | First engagement proves the gap | Add `recruitment_onboarding_agent` | MINOR |
| Probation review (first engagement close) | — | Deepen / reshape / retire per protocol Stage 5 | MINOR/MAJOR |
| Not activated within 2 quarterly cycles | — | Propose archive (retirement condition) | — |
