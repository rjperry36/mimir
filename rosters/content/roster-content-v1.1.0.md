# Content & Copywriting Roster
**Roster ID:** `roster-content`
**Version:** `v1.1.0`
**Status:** `Draft — seed roster`
**Created:** 2026-07-02
**Last Updated:** 2026-07-06
**Owner:** Russell Perry

---

## Version History

| Version | Date | Type | Change Summary | Triggered By |
|---------|------|------|----------------|--------------|
| v1.0.0 | 2026-07-02 | Major | Initial seed roster — orchestrator + copywriter, knowledge toolbox seeded from coreyhaines31/marketingskills (pinned v2.6.0) | Framework review — content discipline gap |
| v1.1.0 | 2026-07-06 | Minor | Added `content_brand_steward_agent` (agent 02) — brand-kit elicitation (create/refresh/adhere), adherence-gate enforcement, deviation escalation. New Brand Kit subsection; brand-kit-template.yaml adopted. | VBP-017 — brand capability (human sign-off) |

### Versioning Rules

Standard semantic versioning per the AOM. This is a **seed roster**: it starts
deliberately small (orchestrator + one specialist) and grows by MINOR bumps as
content workload proves out which specialists to add (see Expansion Path).

---

## Roster Mission

Produce brand-consistent, conversion-aware written content for any active
engagement — email, social, ads copy, landing pages, product marketing, and
general marketing copy — on brief from the ECL and other rosters. This roster
covers the copy disciplines that `roster-seo`'s content agent (which writes
SEO regional pages only) does not.

---

## Roster Principles

Inherits constitutional principles C1–C6 and roster-agnostic principles P1–P8.
Adds:

### CT1 — Voice Is Versioned
The brand voice profile (derived from the ECL Why/What/How/When and any brand
guidelines) is a versioned artifact. Copy is written against a specific voice
version; voice changes are MINOR roster events.

### CT2 — Copy Serves a Declared Outcome
Every piece is briefed against a measurable outcome (signup, reply, click,
retention). Copy without a declared outcome is not briefed into this roster.

### CT3 — Skills Are Reference, Agents Are Authority
The marketingskills knowledge toolbox informs *how* copy is written. Agent
definitions and the ECL decide *what* is written and *whether it ships*. On
any conflict, the agent definition and ECL win.

### CT4 — Brand Change Tolerance Is Explicit and Sourced
Every brand element carries an explicit change tolerance
(LOCKED / REFRESH-WITHIN-BOUNDS / OPEN) with a WHY and a provenance citation.
No element is assumed. Regulatory locks are non-tradeable by any agent. The
Brand Steward owns and enforces this; nothing brand-facing ships past a failed
adherence gate.

---

## Brand Kit

Added in v1.1.0 (VBP-017). The brand kit is the roster's per-element brand
change-tolerance instrument, authored against
`templates/brand-kit-template.yaml` and owned by `content_brand_steward_agent`.

**What it captures**
- A **posture** — `create` / `refresh` / `adhere` — that sets each element's
  default tolerance.
- Per **element** (logo, lockup, colour palette, typography, tone of voice,
  imagery, layout): a tolerance (LOCKED / REFRESH-WITHIN-BOUNDS / OPEN), bounds
  where it may refresh, a WHY with a why_class (preference / contractual /
  regulatory), and provenance.
- A **verified-claims** set — the only factual claims copy may make, each with
  evidence and a verification status.
- **Accessibility requirements** — text/non-text contrast minima, focus
  indicator, target size.

**How it relates to the ECL**
The brand kit refines, at brand granularity, the `brand` area of the ECL
mandate/change-tolerance matrix captured by `ecl_interview_agent` (v2.0.0). The
matrix sets ECL-level tolerances and inherits down via `engagement_context`;
the Brand Steward elicits the element-level detail and enforces it. Verified
claims cite the evidence-locker index. The brand kit is a versioned artifact
(CT1) — brand/voice changes are MINOR roster events.

**Adherence gate**
Brand-facing output passes the Brand Steward's adherence gate before release:
conformance to LOCKED elements, within-bounds on REFRESH elements, only
verified claims, accessibility met. A deviation from a LOCKED element or any
regulatory breach is held and escalated to `roster_content_orchestrator_agent`.

---

## Roster Structure

```
roster-content/
├── roster-content-v1.1.0.md      ← This document (master roster + toolbox)
└── agents/
    ├── agent-00-roster-content-orchestrator-v1.0.0.yaml
    ├── agent-01-content-copywriter-v1.0.0.yaml
    └── agent-02-brand-steward-v1.0.0.yaml
```

---

## Agent Roster

### Crew: `marketing_team` → Sub-crew: `content`

| # | Agent ID | Role | Discipline | Fires After |
|---|----------|------|------------|-------------|
| 00 | `roster_content_orchestrator_agent` | Content Strategy Orchestrator | Content | Engagement start |
| 01 | `content_copywriter_agent` | Copywriter | Content | Orchestrator brief confirmed |
| 02 | `content_brand_steward_agent` | Brand Steward | Content | Orchestrator brief confirmed (brand posture set) |

---

## Toolbox

### Toolbox Version: `v1.0.0`

### Tool Category 1: Knowledge Skills (external, pinned)

| Tool | Purpose | Agents | Integration |
|------|---------|--------|-------------|
| **marketingskills** (`coreyhaines31/marketingskills`) | Reference playbooks: copywriting, copy-editing, emails, social, ads, product-marketing, content-strategy, marketing-psychology, offers, launch | 00, 01 | **Pinned to release v2.6.0** (MIT). Installed per instance as a Claude Code plugin or git submodule. Upgrading the pin is a MINOR roster bump. Precedence per CT3: skills inform technique; agent definitions + ECL decide content and approval. |

### Tool Category 2: Production & Distribution

| Tool | Purpose | Agents | Integration |
|------|---------|--------|-------------|
| **Document store** | Draft, review, and version copy deliverables | 00, 01 | Instance outputs/ directory |
| **Resend / ESP** | Email dispatch (via roster-appdev integration where built) | 01 | Routed via ECL to owning roster |
| **Analytics (GA4 / product analytics)** | Outcome measurement for CT2 | 00 | Read-only — measurement source shared with other rosters |

---

## Cross-Roster Collaboration

Per `framework-architecture` — all routes via the ECL Orchestrator:

| Route | What flows |
|-------|-----------|
| SEO → Content | `aeo_content_structure_agent` patterns and FAQ styles inform copy structure; SEO briefs regional-page-adjacent copy needs |
| Content → SEO | Copy destined for web pages returns through SEO roster review for search alignment before publish |
| App Dev → Content | UI copy / microcopy / transactional email copy requirements from `design_business_solution_agent` and `engineering_backend_agent` briefs |
| Content → App Dev | Approved copy delivered as confirmed content inputs into the App Dev backlog |

---

## Engagement Flow

```
ORCHESTRATOR (00)
│  receives ECL cascade / cross-roster copy briefs
│  produces voice profile (from ECL Why/What/How/When) + content briefs
│
├── FIRES: Agent 02 (Brand Steward) per brand posture
│       └── Outputs: versioned brand kit (tolerances + verified claims + a11y)
│             └── Brand kit informs briefs; adherence gate guards release
│
└── FIRES: Agent 01 (Copywriter) per brief
        └── Outputs: copy deliverable + variants
              └── Review gates → Brand Steward adherence gate (02)
                    └── human brand approval (first publish)
                          └── Approved copy routed via ECL to consuming roster
```

---

## Expansion Path (MINOR bumps, in likely order)

- ✅ `content_brand_steward_agent` — brand-kit elicitation + adherence gate
  (**added v1.1.0**, VBP-017).
1. `content_editor_agent` — dedicated copy-editing/QA when volume justifies it
2. `content_strategist_agent` — calendar and campaign planning across channels
3. `email_marketing_agent` — lifecycle/sequence specialism (seeded from `emails` skill)
4. `social_content_agent` — channel-native social (seeded from `social` skill)

---

## Performance Indicators → Version Bump Map

| Indicator | Threshold | Action | Version Bump |
|-----------|-----------|--------|--------------|
| Copy repeatedly fails brand approval | 2+ rejections same class | Voice profile or copywriter definition review | PATCH |
| Declared outcomes consistently unmet | 2 consecutive review cycles | Brief quality + skill usage review | PATCH |
| New channel needed (e.g. SMS) | — | Add specialist or extend copywriter scope | MINOR |
| marketingskills pin upgrade | New upstream release adopted | Toolbox update | MINOR |
| Voice/brand repositioning | — | Voice profile MAJOR revision | MAJOR |
