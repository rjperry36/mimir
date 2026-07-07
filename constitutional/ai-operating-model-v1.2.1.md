# AI Operating Model (AOM)
**Document ID:** `aom-framework`
**Version:** `v1.2.1`
**Status:** `Active`
**Classification:** `Constitutional — peers with ECL Framework, above all rosters and agents`
**Created:** 2026-03-25
**Last Updated:** 2026-07-07
**Owner:** AI Manager (constitutional role — assigned per business in ECL)

---

## Version History

| Version | Date | Type | Change Summary | Triggered By |
|---------|------|------|----------------|--------------|
| v1.2.1 | 2026-07-07 | Patch | Privacy scrub — genericised the worked example (real client business replaced with the fictional "Riverside Bookings"); no rule or behaviour change | Repo genericisation for public release |
| v1.0.0 | 2026-03-25 | Major | Initial AOM definition | Manual — framework creation |
| v1.2.0 | 2026-07-06 | Minor | Section 4.4 added — collision-safe learning-log ID assignment mandated (orchestrator-issued monotonic IDs OR agent-scoped ID namespaces) so concurrent LEARN appends cannot duplicate; triggered by L-appdev-014/016 ID collisions observed twice in the pilot | Framework backlog — human sign-off received |
| v1.1.0 | 2026-07-06 | Minor | Rule 4.1.C added — constitutional-layer agent changes always require human sign-off regardless of bump size (ASA finding 4a); ai_manager_agent may propose but not autonomously apply constitutional-agent changes | ASA independent audit — human-ratified |
| v1.0.2 | 2026-07-03 | Patch | Section 3.1 clarification — handoff pass items fall into four legitimate classes: (a) declared sender outputs/inputs, (b) relayed artifacts declared by another agent in the same roster or constitutional layer (orchestrator routing), (c) ad-hoc payload on escalation/query/self/human/broadcast handoffs, (d) ECL-sourced context fields (engagement_context, ecl_summary, target_regions). Enforced as validator check E16. | Final deep audit |
| v1.0.1 | 2026-07-02 | Patch | Registry refresh (current document versions; engagement-lifecycle and context-memory-protocol registered); clarification pointer added — compliance is enforced automatically by scripts/validate_framework.py in CI | Framework compliance audit |

### Versioning Rules

The AOM follows semantic versioning (MAJOR.MINOR.PATCH).

| Increment | When | Authority |
|-----------|------|-----------|
| **PATCH** | Clarification to existing rule, example added, typo corrected | AI Manager |
| **MINOR** | New governance area added, rule extended, new lifecycle stage defined | AI Manager + human sign-off |
| **MAJOR** | Fundamental principle changed, hierarchy restructured, new constitutional constraint | Human sign-off mandatory |

**Critical rule:** A MAJOR AOM change triggers a mandatory compliance audit
of every active agent and roster. All non-compliant documents must be
updated before the new AOM version is considered active.

---

## Purpose

The AI Operating Model is the constitutional governance document for the
entire agent ecosystem. It defines how every agent must be constructed,
named, connected, versioned, and governed — regardless of which business,
client, or roster the agent serves.

The ECL Framework governs **what** the business wants to achieve.
The AI Operating Model governs **how** the agent ecosystem that serves
it must be built and run.

Neither document owns the other. Both are constitutional. A business
instantiation via the ECL cannot override AOM rules. The AOM cannot
override a business's North Star or objectives. They are parallel
authorities with distinct domains.

---

## Hierarchy Position

```
╔══════════════════════════════════════════════════════════════╗
║  CONSTITUTIONAL LAYER                                        ║
║                                                              ║
║  ┌─────────────────────┐   ┌─────────────────────────────┐  ║
║  │   ECL FRAMEWORK     │   │   AI OPERATING MODEL (AOM)  │  ║
║  │                     │   │                             │  ║
║  │  What the business  │   │  How the agent ecosystem    │  ║
║  │  is trying to do    │   │  must be built and run      │  ║
║  └──────────┬──────────┘   └──────────────┬──────────────┘  ║
║             │                             │                  ║
║             │ cascades objectives         │ enforces         ║
║             │                             │ standards        ║
╚═════════════╪═════════════════════════════╪══════════════════╝
              │                             │
              ▼                             ▼
         ECL Orchestrator            AI Manager Agent
              │                             │
              └──────────┬──────────────────┘
                         │
                         ▼
                  ROSTER LAYER
              (roster orchestrators)
                         │
                         ▼
                  AGENT LAYER
              (specialist agents)
```

---

## Section 1 — Naming & ID Conventions

All agents, rosters, and documents in the ecosystem must follow
these conventions without exception. Naming drift breaks handoff
chains, causes agent lookup failures, and makes the ecosystem
unmaintainable at scale.

### 1.1 Agent IDs

**Format:** `{discipline}_{role}_agent`

**Rules:**
- Lowercase only
- Words separated by underscores
- Always ends in `_agent`
- Discipline prefix reflects the agent's primary roster discipline
- Role describes the agent's function — not its position number

**Examples:**
```
✓  seo_content_agent
✓  seo_technical_agent
✓  aeo_content_structure_agent
✓  aeo_schema_entity_agent
✓  geo_knowledge_graph_agent
✓  geo_local_presence_agent
✓  gbp_management_agent
✓  performance_reporting_agent
✓  seo_local_citations_agent
✓  seo_link_authority_agent
✓  ecl_interview_agent
✓  ecl_orchestrator_agent

✗  content_agent              (missing discipline prefix)
✗  seo_performance_agent      (ambiguous — performance of what?)
✗  local_citations_agent      (missing discipline prefix)
✗  SEO_Content_Agent          (wrong case)
✗  seoContentAgent            (wrong separator)
```

**Special cases:**
- Orchestrators: `{scope}_orchestrator_agent`
  e.g. `roster_seo_orchestrator_agent`, `ecl_orchestrator_agent`
- Interview/intake agents: `{scope}_interview_agent`
  e.g. `ecl_interview_agent`

### 1.2 Roster IDs

**Format:** `roster-{discipline}`

**Rules:**
- Lowercase only
- Words separated by hyphens (not underscores — distinguishes rosters from agents)
- Always prefixed with `roster-`

**Examples:**
```
✓  roster-seo
✓  roster-paid-media
✓  roster-email
✓  roster-operations

✗  seo_roster
✗  SEO-Roster
✗  roster_seo
```

### 1.3 Document Filenames

**Format:** `{type}-{scope}-v{MAJOR}.{MINOR}.{PATCH}.{ext}`

| Document type | Prefix | Example |
|---------------|--------|---------|
| Agent definition | `agent-{NN}-{role}` | `agent-01-seo-architecture-v1.0.0.yaml` |
| Roster definition | `roster-{discipline}` | `roster-seo-v1.0.0.md` |
| ECL instance | `ecl-{business-id}` | `ecl-riverside-bookings-v1.0.0.md` |
| Framework document | `{name}-framework` | `ecl-framework-v1.0.0.md` |
| Constitutional document | `{name}` (descriptive) | `ai-operating-model-v1.0.0.md` |
| Cascade briefing | `cascade-{business-id}-{version}-{date}` | `cascade-bpf-v1.1.0-2026-04-01.md` |
| Output content | `{type}-{scope}-v{version}` | `content-riverside-v1.0.0.md` |

**Rules:**
- Lowercase only
- Words separated by hyphens
- Version always appended before extension
- Agent files include zero-padded two-digit sequence number (01, 02 ... 11)
- No spaces, no special characters other than hyphens and dots

### 1.4 Agent Sequence Numbers

Agents within a roster are numbered sequentially from 01.
The orchestrator for that roster is always 00.

```
00 — Roster orchestrator
01 — First specialist agent (always the architecture/foundation agent)
02–NN — Specialist agents in dependency order
```

Sequence numbers reflect **execution dependency order**, not importance.
An agent that must fire before another always has a lower number.

---

## Section 2 — Required YAML Structure

Every agent definition YAML must contain the following sections
in the following order. Sections marked `[REQUIRED]` will cause
a compliance failure if absent. Sections marked `[RECOMMENDED]`
should be present at full playbook depth; lean agents may omit
with a documented reason.

### 2.1 Canonical YAML Structure

```yaml
# ============================================================
# AGENT DEFINITION: {Agent Name}
# Role: {Role title}
# Version: {MAJOR.MINOR.PATCH}
# Roster: {roster-id}
# Fires after: {dependency — agent ID or 'engagement start'}
# Definition depth: full | lean
# ============================================================

agent:                          # [REQUIRED]
  id: ""                        # [REQUIRED] — follows naming convention
  name: ""                      # [REQUIRED] — human-readable
  role: ""                      # [REQUIRED] — role title
  roster: ""                    # [REQUIRED] — parent roster ID
  discipline: ""                # [REQUIRED] — SEO / AEO / GEO / All
  version: ""                   # [REQUIRED] — semantic version
  definition_depth: ""          # [REQUIRED] — full | lean

  goal: |                       # [REQUIRED] — what this agent achieves
  backstory: |                  # [REQUIRED] — persona and expertise framing
  constraints: []               # [REQUIRED] — hard rules the agent cannot break

inputs:                         # [REQUIRED]
  required: []                  # Inputs that block execution if absent
  optional: []                  # Inputs that enhance output if present

outputs:                        # [REQUIRED]
  primary: []                   # Documents/data this agent produces
  format: ""                    # Output format specification

cycle:                          # [REQUIRED]
  goal_phase: {}                # What the agent confirms before starting
  plan_phase: {}                # Research and decision steps
  act_phase: {}                 # Production steps
  review_phase: {}              # Self-audit checks before handoff
  learn_phase: {}               # What gets logged for improvement

handoffs:                       # [REQUIRED]
  - trigger: ""                 # Condition that fires the handoff
    to_agent: ""                # Recipient agent ID (must exist in roster)
    pass: []                    # Data passed in handoff
    brief: |                    # Self-contained context for receiving agent

# FULL PLAYBOOK ONLY — omit in lean definitions with note
decision_logic: {}              # [RECOMMENDED — full only]
quality_gates: []               # [RECOMMENDED — full only]
```

### 2.2 Mandatory Field Rules

**`agent.id`**
Must follow naming convention in Section 1.1 exactly.
Validated against roster registry before activation.

**`agent.version`**
Must be semantic version string: `"MAJOR.MINOR.PATCH"`
Must match filename version. Mismatch = compliance failure.

**`agent.constraints`**
Minimum 3 constraints. Must include at minimum:
- One constraint about what the agent will NOT do
- One constraint about human input handling
- One constraint about data fabrication

**`inputs.required`**
Every required input must reference the agent ID that produces it,
or state `engagement_context` / `ecl_summary` for ECL-sourced inputs.
Orphaned inputs (no named source) are a compliance failure.

**`cycle`**
All five phases must be present. Each phase must have at minimum
one step or check. Empty phases are a compliance failure.

**`handoffs`**
Every `to_agent` value must match a declared agent ID in the roster.
References to agents not in the roster are a compliance failure.
Every handoff brief must be self-contained — receiving agent gets
no other context.

### 2.3 Lean vs Full Definition

| Element | Full playbook | Lean |
|---------|--------------|------|
| goal, backstory, constraints | Required | Required |
| inputs / outputs | Full spec | Core fields only |
| cycle | All 5 phases, detailed | All 5 phases, condensed |
| decision_logic | Required | Omit — note reason |
| quality_gates | Required | Checklist only |
| handoffs | Full briefs | Brief briefs |

**Lean agents must include this field:**
```yaml
definition_depth: "lean"
# Note: Deepens to full in v1.1.0 — reason for lean: [reason]
```

---

## Section 3 — Handoff Contract Rules

Handoffs are the connective tissue of the ecosystem. A broken
handoff is a broken pipeline. These rules are non-negotiable.

### 3.1 The Handoff Contract

Every handoff is a formal contract between a sending agent and
a receiving agent. It must specify:

```yaml
handoffs:
  - trigger: ""      # The exact condition that fires this handoff
                     # Must be observable — not vague
                     # ✓ "All regional pages complete and quality gates passed"
                     # ✗ "When ready"

    to_agent: ""     # Exact agent ID — must exist in roster registry
                     # ✓ "seo_content_agent"
                     # ✗ "content agent" / "the content team"

    pass: []         # Explicit list of data objects passed
                     # Every item must be one of (clarified v1.0.2):
                     #  (a) an output/input declared by the sender
                     #  (b) a relayed artifact declared as an output by
                     #      another agent in the same roster or the
                     #      constitutional layer (orchestrator routing)
                     #  (c) ad-hoc payload on an escalation/query/self/
                     #      human/broadcast handoff
                     #  (d) an ECL-sourced context field
                     #      (engagement_context, ecl_summary, target_regions)

    brief: |         # Self-contained context brief
                     # Must answer: what has been done, what is needed,
                     # what constraints apply, what the receiving agent
                     # must NOT do (to avoid duplication)
```

### 3.2 Handoff Trigger Standards

Triggers must be **observable and binary** — either the condition
is met or it is not. There is no ambiguous middle state.

```
✓  "All quality gates passed"
✓  "Human input flags unresolved after 48 hours"
✓  "CRITICAL items identified in audit"
✓  "GBP listings live and verified"

✗  "When the agent is done"
✗  "After content is good enough"
✗  "When appropriate"
```

### 3.3 Escalation Handoffs

Every agent must define an escalation handoff to `roster_orchestrator_agent`
for the condition: **required input or approval not received within
the defined timeout period.**

Timeout standards:
- Human content input: 48 hours
- Human photo/media assets: 72 hours
- Human sign-off on critical decisions: 24 hours
- Executive review (ECL-level): 5 business days

### 3.4 No Orphan Outputs

Every output produced by an agent must be consumed by at least
one other agent via a declared handoff, or explicitly marked
as a terminal output (final deliverable to human).

```yaml
outputs:
  primary:
    - name: "technical_audit_report"
      consumed_by: "seo_technical_agent → roster_orchestrator_agent"
      # OR
      terminal: true   # Final deliverable — no further agent consumption
```

---

## Section 4 — Version Bump Authority

### 4.1 Authority Matrix

| Bump type | Who can propose | Who must approve | Cascade required |
|-----------|----------------|-----------------|-----------------|
| Agent PATCH | Agent (via learn phase) | AI Manager | No — notify only |
| Agent MINOR | Roster orchestrator | AI Manager + human | Notify affected agents |
| Agent MAJOR | Roster orchestrator | Human sign-off | Full roster audit |
| Roster PATCH | Roster orchestrator | AI Manager | No — notify only |
| Roster MINOR | Roster orchestrator | AI Manager + human | Cascade to agents |
| Roster MAJOR | ECL Orchestrator | Human sign-off | Full cascade |
| ECL PATCH | ECL Orchestrator | AI Manager | Notify rosters |
| ECL MINOR | ECL Orchestrator | AI Manager + human | Cascade briefing |
| ECL MAJOR | Human | Human sign-off | Full cascade — all rosters |
| AOM PATCH | AI Manager | AI Manager | Notify all |
| AOM MINOR | AI Manager | Human sign-off | Compliance check |
| AOM MAJOR | Human | Human sign-off | Full ecosystem audit |

**Rule 4.1.C — Constitutional-layer exception (ASA finding 4a, human-ratified 2026-07-06):**
Any change to a **constitutional-layer agent** — `ecl_interview_agent`,
`ecl_orchestrator_agent`, `ai_manager_agent`, `client_account_manager_agent` —
**always requires human sign-off, regardless of bump size**, including PATCH.
The `ai_manager_agent` may PROPOSE but may never autonomously apply a change to
a constitutional-layer agent (it cannot self-modify or modify its peers). This
overrides the "Agent PATCH → AI Manager" row above for the constitutional layer.
Rationale: separation of duties at the apex — the governance agent must not be
able to rewrite the governance layer without a human in the loop.

### 4.2 Version Bump Proposal Format

Every version bump proposal must include:

```yaml
version_bump_proposal:
  document_id: ""
  current_version: ""
  proposed_version: ""
  bump_type: ""           # PATCH / MINOR / MAJOR
  proposed_by: ""         # agent ID or human
  date: ""
  reason: |               # Why the change is needed
  change_summary: |       # What specifically changes
  affected_documents: []  # Other docs that need updating as a result
  cascade_required: ""    # yes / no / notify-only
  human_sign_off_required: ""  # yes / no
```

### 4.3 No Silent Changes

No document in the ecosystem may be edited without a version bump
and a changelog entry. This applies to every file at every layer —
constitutional, roster, agent, and output.

The sole exception: correcting a typographical error that does not
affect meaning, logic, or behaviour. This still requires a PATCH
bump but does not require human sign-off.

### 4.4 Collision-Safe Learning-Log ID Assignment

Learning-log entries (Context & Memory Protocol, Rule 4) are
append-only and evidence-linked: every insight in a roster's
`learnings.yaml` traces back to a raw entry by its ID. If two agents
running concurrently mint the same ID, the evidence chain forks — two
distinct learnings claim one identifier and one silently shadows the
other. In the pilot this happened twice: `L-appdev-014` and
`L-appdev-016` each collided under concurrent LEARN-phase appends.

**Rule:** learning-log IDs must be assigned by a **collision-safe**
scheme. Free-running per-agent counters are prohibited. One of the
following two schemes is mandatory per roster:

1. **Orchestrator-issued monotonic IDs.** The roster orchestrator is the
   single issuer of learning-log IDs. An agent requests an ID at LEARN
   time; the orchestrator returns the next value from one monotonic
   sequence per roster. No agent mints its own ID.
2. **Agent-scoped ID namespaces.** Each agent owns a disjoint namespace
   embedding its own agent ID (e.g. `L-appdev-07-014`), so two agents
   can append concurrently without ever colliding — the agent segment
   guarantees uniqueness.

A roster declares which scheme it uses in its `roster-config.yaml`.
Whichever scheme is chosen, concurrent LEARN appends **must not** be
able to produce duplicate IDs. This is enforced at distillation: an
orchestrator that encounters a duplicate learning-log ID treats it as a
compliance failure, quarantines both entries, and escalates rather than
silently overwriting.

Existing single-issuer rosters adopt an explicit scheme at their next
MINOR bump; concurrency-exposed rosters (any roster whose agents can run
in parallel under the runtime) adopt one before enabling parallel runs.

---

## Section 5 — Agent Lifecycle

Every agent passes through defined lifecycle stages. An agent's
current stage determines what it can and cannot do.

### 5.1 Lifecycle Stages

```
DRAFT → REVIEW → ACTIVE → DEPRECATED → ARCHIVED
          ↑          |
          └──────────┘ (iteration loop)
```

| Stage | Definition | Can execute? | Can receive handoffs? |
|-------|------------|-------------|----------------------|
| `draft` | Being built — not yet reviewed | No | No |
| `review` | Built — under compliance review | No | No |
| `active` | Compliance passed — operational | Yes | Yes |
| `deprecated` | Superseded by newer version — winding down | Read-only | No new |
| `archived` | No longer in use — record only | No | No |

### 5.2 Activation Requirements

An agent may not move from `review` to `active` until:

```
[ ] AOM compliance check passed (all sections 1–4 satisfied)
[ ] All required inputs have named source agents that are active
[ ] All handoff to_agent IDs exist in roster registry as active
[ ] Version number matches filename
[ ] Human sign-off received (for agents handling customer data or
    financial decisions — always. For others — AI Manager discretion)
[ ] Registered in roster_registry.yaml
```

### 5.3 Deprecation Protocol

When a new version of an agent is activated, the previous version
enters `deprecated` status. Deprecated agents:

- Complete any in-flight tasks they have started
- Do not accept new handoffs
- Are removed from the active roster after all in-flight tasks complete
- Remain in the version history indefinitely

### 5.4 Lifecycle Field in YAML

Every agent YAML must carry a lifecycle field:

```yaml
agent:
  id: ""
  lifecycle_status: "draft"   # draft | review | active | deprecated | archived
  activated_date: ""          # ISO8601 — populated when moved to active
  deprecated_date: ""         # ISO8601 — populated when deprecated
```

---

## Section 6 — Tool Declaration & Access Rules

### 6.1 Declaration Requirement

Every agent must explicitly declare all tools it uses.
An agent may not use a tool that is not declared in its
YAML definition. Undeclared tool use is a compliance failure.

```yaml
tools:
  required:                   # Agent cannot function without these
    - tool_id: ""
      purpose: ""             # Why this agent needs this tool
      api_ref: ""             # Reference to toolbox spec
  optional:                   # Enhances output but not blocking
    - tool_id: ""
      purpose: ""
      api_ref: ""
```

### 6.2 Tool Access Scope

Tools are declared at the roster toolbox level (see roster-seo
toolbox spec). Agents reference toolbox entries — they do not
define new tools independently.

If an agent needs a tool not in the current toolbox:
1. Propose tool addition to AI Manager
2. AI Manager evaluates and adds to toolbox (MINOR roster bump)
3. Agent updated to reference new toolbox entry (PATCH agent bump)
4. Agent does not use the tool until both bumps are active

### 6.3 Data Access Constraints

```
An agent may only access:
  ✓ Data explicitly passed in its handoff inputs
  ✓ Data from tools declared in its YAML
  ✓ Data from engagement_context loaded at roster kickoff
  ✓ Constitutional documents (ECL, AOM — read only)

An agent may NOT:
  ✗ Access another agent's outputs without a declared handoff
  ✗ Store customer PII outside approved tool infrastructure
  ✗ Make API calls to tools not in its declared toolbox
  ✗ Write to constitutional documents
  ✗ Modify another agent's output files directly
```

### 6.4 External API Security Rules

- API keys are never hardcoded in agent definitions
- API keys are injected at runtime by the orchestration framework
- Agents reference tool IDs — the framework resolves credentials
- Any tool handling customer data must be flagged in the toolbox
  with its data retention and GDPR compliance status

---

## Section 7 — Human Override Requirements

### 7.1 Mandatory Human Override Conditions

The following conditions always require human intervention.
No agent may proceed autonomously when these conditions are met.

```
STOP — HUMAN REQUIRED:

[ ] Any decision that commits financial expenditure above
    the threshold defined in the ECL Finance domain

[ ] Any content that will be published under the business's
    brand without human review (first publish only —
    subsequent updates may be autonomous within guardrails)

[ ] Any MAJOR version bump at any layer

[ ] Any action affecting customer-facing data (deletion,
    bulk update, export)

[ ] Any legal or compliance determination

[ ] Any action the agent has not performed before in this
    engagement (novel situations — escalate, do not improvise)

[ ] ECL North Star metric deviation >20% with unclear cause
```

### 7.2 Override Escalation Path

```
Agent encounters override condition
    → Agent pauses task
    → Agent logs condition to engagement_log
    → Agent sends escalation handoff to roster_orchestrator_agent
    → Roster orchestrator notifies ECL orchestrator if ECL-level concern
    → ECL orchestrator notifies human (AI Manager owner defined in ECL)
    → Human reviews and responds
    → Response logged and agent resumes or task is cancelled
```

### 7.3 Override Response Timeout

If human override response is not received within the defined
timeout (see Section 3.3), the agent does not proceed autonomously.
It escalates to the next level:

```
Agent timeout → Roster orchestrator
Roster orchestrator timeout → ECL Orchestrator
ECL Orchestrator timeout → Direct human notification (email/Slack)
```

### 7.4 Override Log Format

Every human override event must be logged:

```yaml
override_log_entry:
  date: ""                    # ISO8601
  agent_id: ""
  condition_triggered: ""     # Which Section 7.1 condition
  task_paused: ""             # What the agent was doing
  escalated_to: ""            # Who was notified
  resolution: ""              # What the human decided
  resolved_date: ""           # ISO8601
  agent_resumed: ""           # yes / no
```

---

## Section 8 — Quality Gate Standards

### 8.1 What a Quality Gate Is

A quality gate is a binary check that must pass before an agent
proceeds to the next phase or triggers a handoff. Gates are not
guidelines — they are hard stops.

Every quality gate must be:
- **Binary:** pass or fail — no partial pass
- **Observable:** the check can be performed without subjective judgement
- **Assigned:** it is clear who or what performs the check
- **Consequenced:** failure has a defined action (fix, escalate, or flag)

### 8.2 Minimum Gate Requirements

Every agent must define quality gates at two points:

**Phase gates** — between cycle phases:
```yaml
cycle:
  plan_phase:
    gate: |
      [Binary condition that must be true before ACT phase begins]
      Failure action: [what happens if gate fails]
```

**Handoff gates** — before any handoff fires:
```yaml
handoffs:
  - trigger: "[Condition]"
    gate: |
      [Binary checks that must pass before handoff sends]
    gate_failure_action: "Return to act_phase / Escalate to orchestrator"
```

### 8.3 Quality Gate Categories

Every agent's review phase must include gates from these categories:

| Category | What it checks | Required for |
|----------|---------------|--------------|
| Completeness | All required outputs produced | All agents |
| Accuracy | Outputs match source inputs (no fabrication) | All agents |
| Consistency | No contradictions with ECL or AOM | All agents |
| Handoff readiness | Receiving agent has everything it needs | All agents |
| Human flag resolution | No unresolved human input flags blocking output | All agents |
| Compliance | AOM naming, structure, and access rules followed | All agents |

### 8.4 The Non-Fabrication Gate

Every agent must include an explicit non-fabrication quality gate:

```yaml
quality_gates:
  - gate: "Non-fabrication check"
    check: |
      All specific facts, statistics, prices, dates, and named
      entities in outputs can be traced to: engagement_context,
      ECL content, tool data, or human-confirmed inputs.
      No agent-invented content in any output.
    failure_action: "Remove fabricated content. Flag gap for human input."
    blocking: true
```

This gate is non-negotiable. It applies to every agent at every
definition depth. It cannot be omitted from lean definitions.

---

## Section 9 — AOM Compliance Checklist

This checklist is run against every agent before it moves from
`review` to `active` status. It is also run against every existing
agent when a MAJOR AOM version bump occurs.

```
NAMING & ID CONVENTIONS (Section 1)
[ ] Agent ID follows {discipline}_{role}_agent format
[ ] Agent ID uses underscores, lowercase only
[ ] Filename follows agent-{NN}-{role}-v{version}.yaml format
[ ] Filename version matches agent.version field
[ ] Roster ID referenced is correct roster-{discipline} format

YAML STRUCTURE (Section 2)
[ ] All REQUIRED sections present
[ ] agent.id, agent.version, agent.lifecycle_status present
[ ] agent.constraints has minimum 3 entries
[ ] inputs.required — every item has named source agent
[ ] All 5 cycle phases present with minimum one step each
[ ] Non-fabrication quality gate present
[ ] definition_depth declared (full or lean)

HANDOFF CONTRACTS (Section 3)
[ ] Every handoff has observable binary trigger
[ ] Every to_agent ID exists in roster registry
[ ] Every pass item is declared in outputs
[ ] Every brief is self-contained
[ ] Escalation handoff to orchestrator present

VERSION & LIFECYCLE (Sections 4 + 5)
[ ] version follows MAJOR.MINOR.PATCH format
[ ] lifecycle_status field present
[ ] Changelog entry exists for this version

TOOL DECLARATION (Section 6)
[ ] All tools declared in tools section
[ ] All tools reference toolbox entries
[ ] No undeclared external API calls in agent logic
[ ] Data access scope respected

HUMAN OVERRIDE (Section 7)
[ ] Override conditions identified for this agent's domain
[ ] Escalation path defined
[ ] Override log format referenced

QUALITY GATES (Section 8)
[ ] Phase gates present between plan→act and act→review
[ ] Handoff gates present on all handoffs
[ ] Non-fabrication gate present and marked blocking: true
[ ] All gate failures have defined actions
```

---

## Section 10 — AI Manager Responsibilities

The AI Manager is the human role (defined in the ECL AI Manager
domain) responsible for the AOM's operational enforcement.
This section defines what that role does — not who fills it
(that is business-specific and lives in the ECL).

### Ongoing Responsibilities

```
DAILY (automated monitoring — AI Manager reviews flags):
  - Agent failure rate across all active rosters
  - Human override events triggered
  - Handoff timeouts

MONTHLY:
  - Review agent learning logs across all rosters
  - Assess PATCH bump proposals from orchestrators
  - Review tool usage vs declared access (anomaly detection)

QUARTERLY:
  - AOM compliance audit across all active agents
  - Review MINOR bump proposals
  - Assess ecosystem performance vs AI Manager KPIs in ECL

ANNUALLY / ON MAJOR ECL CHANGE:
  - Full AOM review — propose MINOR or MAJOR bump if needed
  - Full roster re-alignment to updated ECL objectives
  - Review agent lifecycle — deprecate stale agents
```

### AI Manager Authority

```
CAN DO autonomously:
  ✓ Approve PATCH bumps (agent, roster, ECL, AOM)
  ✓ Run compliance audits
  ✓ Move agents from draft → review → active
  ✓ Deprecate agents after human notification
  ✓ Update toolbox with new tools (MINOR roster bump)

REQUIRES human sign-off:
  ✗ MINOR bumps to ECL or AOM
  ✗ MAJOR bumps at any layer
  ✗ Decommissioning an entire roster
  ✗ Overriding a human override decision
  ✗ Changing the North Star metric in ECL
```

---

## Document Registry — Constitutional Layer

| Document | ID | Version | Status | Peers with |
|----------|----|---------|--------|------------|
| ECL Framework | `ecl-framework` | v1.1.0 | Active | AOM |
| AI Operating Model | `aom-framework` | v1.2.0 | Active | ECL Framework |
| Framework Architecture | `framework-architecture` | v1.2.1 | Active | Both |
| Engagement Lifecycle | `engagement-lifecycle` | v1.1.0 | Active | ECL + AOM |
| Context & Memory Protocol | `context-memory-protocol` | v1.1.0 | Active | AOM |

**Enforcement note (clarification):** the Section 9 compliance checklist
is enforced automatically by `scripts/validate_framework.py`, run in CI
on every push (`.github/workflows/validate.yml`). The framework-level
agent registry is `rosters/manifest.yaml` — agent file changes and
manifest updates must land in the same commit or CI fails. This is the
drift-prevention mechanism; the checklist itself is unchanged.

