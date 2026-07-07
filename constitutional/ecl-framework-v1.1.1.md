# Executive Command Layer (ECL)
**Framework ID:** `ecl-framework`
**Version:** `v1.1.1`
**Status:** `Template — awaiting business instantiation`
**Created:** 2026-03-25
**Last Updated:** 2026-07-07
**Classification:** Constitutional — sits above all rosters

---

## Version History

| Version | Date | Type | Change Summary | Triggered By |
|---------|------|------|----------------|--------------|
| v1.1.1 | 2026-07-07 | Patch | Privacy scrub — genericised the worked example (real client business replaced with the fictional "Riverside Bookings"); no rule or behaviour change | Repo genericisation for public release |
| v1.0.0 | 2026-03-25 | Major | Initial ECL framework definition | Manual — new framework |
| v1.1.0 | 2026-07-06 | Minor | Section 3 functional domains made TIER-DEPENDENT rather than a fixed nine: core domains (always live) vs tier-gated domains defined; rationale added for the SME domain taxonomy (maps to standard business functions; corporate domains Risk/ESG/IR/M&A reserved for out-of-scope tiers); interview now confirms live domains per business rather than forcing all nine; cross-referenced to engagement-lifecycle tier ladder | Framework backlog (framework-scaling-and-domains Q1, owner scope decision 2026-07-06) — human sign-off received |

### Versioning Rules

The ECL follows the same semantic versioning convention as all rosters (MAJOR.MINOR.PATCH),
but operates on a longer cadence aligned to business planning cycles.

| Increment | When to use | Cadence |
|-----------|-------------|---------|
| **PATCH** `v1.0.x` | KPI threshold updated, metric baseline revised, single objective refined | Monthly management review |
| **MINOR** `v1.x.0` | New functional domain added, roster added/removed, North Star refined | Quarterly (Q1/Q2/Q3/Q4) |
| **MAJOR** `vx.0.0` | North Star changes, business model pivots, full objective rewrite | Annual or triggered by material business event |

**Rule:** Every ECL version bump triggers a cascade review to all active roster orchestrators.
**Rule:** MAJOR bumps require human sign-off and a full roster re-alignment session.
**Rule:** The ECL is the single source of truth for business context. No roster may define
its own business objectives — all objectives flow from the ECL downward.

---

## System Architecture

### Hierarchy

```
┌─────────────────────────────────────────────────────┐
│           EXECUTIVE COMMAND LAYER (ECL)             │
│         One per business / client                   │
│    Cycle: Annual (MAJOR) / Quarterly (MINOR)        │
└─────────────────────┬───────────────────────────────┘
                      │ cascades objectives via
                      │ ECL Orchestrator
          ┌───────────┼───────────┐
          ▼           ▼           ▼
    ┌──────────┐ ┌──────────┐ ┌──────────┐
    │ ROSTER   │ │ ROSTER   │ │ ROSTER   │
    │   SEO    │ │  PAID    │ │  OPS     │  ... n rosters
    │          │ │  MEDIA   │ │          │
    └──────────┘ └──────────┘ └──────────┘
    Each roster has its own orchestrator.
    Roster orchestrators receive ECL cascade briefings.
    Roster orchestrators query ECL on MAJOR decisions.
```

### How Rosters Consume the ECL

**At kickoff (passive read):**
Every roster orchestrator reads the full ECL document at engagement start.
It extracts: North Star, relevant functional objectives, current KPI baselines,
and the SWOT context. These are loaded into the roster's `engagement_context`
and passed through the entire agent chain.

**On major decisions (active query):**
When a roster orchestrator encounters a decision that could affect another
functional domain — e.g. the SEO roster recommends a domain change that has
brand implications — it queries the ECL before proceeding. The query returns
the relevant ECL section and any constraints that apply.

**On cascade (push from ECL):**
When the ECL runs its quarterly or annual cycle and produces a new version,
the ECL Orchestrator generates a cascade briefing per active roster. Each
briefing contains: what changed, which objectives are affected, and what
action (if any) the roster orchestrator must take. Roster orchestrators
acknowledge receipt and log the update.

---

## ECL Creation Protocol

The ECL for any new business or client is built through a structured AI interview,
reviewed by a human, and signed off before any roster is activated.

### Phase 1 — AI Interview

The ECL Interview Agent conducts a structured conversation covering the
functional domains **live for this business** — the core domains always, and
the tier-gated domains where the confirmed engagement tier and the business's
actual complexity call for them (see Section 3 and the engagement-lifecycle
tier ladder). The interview explicitly **confirms which domains are live**
rather than forcing all nine. Questions are adaptive — depth increases where
answers reveal complexity or risk. The interview produces a draft ECL document.

**Estimated interview time:** 45–90 minutes (first instantiation)
**Subsequent reviews:** 15–30 minutes per quarterly cycle

**Interview Agent ID:** `ecl_interview_agent`
**Interview output:** `ecl-draft-[business-id]-v0.1.0.md`

### Phase 2 — Human Review

The draft ECL is presented to the business owner or client for review.
All sections are editable. The review focuses on:
- Accuracy of business description and context
- Validity of objectives and KPI baselines
- North Star alignment
- SWOT completeness and honesty
- AI Manager domain appropriateness

### Phase 3 — Sign-off and Activation

Once approved, the ECL is versioned to `v1.0.0`, marked `Active`, and
the ECL Orchestrator is initialised. Roster activation may then begin.

---

## ECL Document Structure

Every instantiated ECL contains the following sections.
Sections marked `[REQUIRED]` must be completed before roster activation.
Sections marked `[RECOMMENDED]` should be completed within the first quarterly cycle.

```
ecl-[business-id]/
├── ecl-[business-id]-v1.0.0.md        ← Master ECL document
├── interview-transcript-v1.0.0.md     ← Raw interview output (archived)
├── cascade-briefings/
│   ├── cascade-v1.1.0-[date].md       ← One briefing per version bump
│   └── ...
└── roster-registry.yaml               ← Active rosters and their versions
```

---

## Section 1 — Business Identity `[REQUIRED]`

**Purpose:** Establishes the fixed context that all rosters and agents
operate within. This never changes without a MAJOR version bump.

### 1.1 Business Description

```yaml
business_id: ""                    # Unique slug e.g. riverside-bookings
business_name: ""                  # Full legal or trading name
business_type: ""                  # e.g. SME, startup, enterprise, client
industry: ""                       # Primary industry category
sub_industry: ""                   # More specific category
founded: ""                        # Year founded
stage: ""                          # e.g. pre-revenue, growth, scale, mature
geography:
  primary_country: ""              # ISO 3166-1 alpha-2
  operating_regions: []            # List of active regions
  target_regions: []               # List of planned expansion regions
headcount: ""                      # Approximate current headcount
annual_revenue_band: ""            # e.g. £0-50k, £50k-250k, £250k-1m, £1m+
business_model: ""                 # e.g. B2C subscription, B2B service, marketplace
primary_channels: []               # e.g. direct, OTA, referral, organic search
```

### 1.2 North Star `[REQUIRED]`

The single metric or outcome that defines success for this business at this stage.
Everything else — objectives, KPIs, roster priorities — exists to move the North Star.

```yaml
north_star:
  statement: ""                    # One sentence. What does winning look like?
  metric: ""                       # The single measurable indicator
  current_baseline: ""             # Where are we now?
  target: ""                       # Where do we need to be?
  horizon: ""                      # Timeframe (e.g. 12 months, 3 years)
```

**Worked Example:**
```yaml
north_star:
  statement: "Become the most trusted local service provider in our category
              across all target regions within 24 months."
  metric: "Monthly recurring revenue from repeat customers"
  current_baseline: "£0 (pre-launch)"
  target: "£15,000 MRR"
  horizon: "24 months"
```

### 1.3 Why / What / How / When `[REQUIRED]`

Simon Sinek's Golden Circle extended with a temporal dimension.
This is the strategic narrative — used by all agents when producing
external-facing content or making brand-aligned decisions.

```yaml
why: ""    # The purpose or cause. Why does this business exist beyond making money?
what: ""   # What does the business do? (product/service description)
how: ""    # How does it deliver that? (differentiator, method, approach)
when: ""   # When does the business deliver value? (trigger, timing, lifecycle moment)
```

**Worked Example:**
```yaml
why: "We believe people should arrive at their destination relaxed, not stressed
      by parking logistics."
what: "We provide automated, secure parking and accommodation near major
       transport hubs."
how:  "Through fully automated booking, gate access, and guest management —
       with no manual check-in required."
when: "When a traveller needs overnight parking or accommodation the night
      before an early departure."
```

---

## Section 2 — Strategic Context `[REQUIRED]`

### 2.1 SWOT Analysis

```yaml
swot:
  strengths:
    - ""   # Internal positive factors — what you do well
  weaknesses:
    - ""   # Internal negative factors — what needs improving
  opportunities:
    - ""   # External positive factors — market conditions in your favour
  threats:
    - ""   # External negative factors — risks from market or competition
```

**Roster consumption note:** Roster orchestrators use SWOT to contextualise
their discipline strategy. A weakness in brand awareness directly informs
the SEO and content roster priorities. A threat from a new competitor
triggers a SERP landscape re-audit.

### 2.2 Competitive Landscape `[RECOMMENDED]`

```yaml
competitors:
  direct:
    - name: ""
      strength: ""
      weakness: ""
      primary_channel: ""
  indirect:
    - name: ""
      relevance: ""
market_position: ""    # e.g. challenger, niche leader, new entrant
differentiation: ""    # What makes this business meaningfully different?
```

### 2.3 Target Operating Model `[REQUIRED]`

The structural description of how the business delivers value.
Defines the boundaries within which rosters must operate.

```yaml
target_operating_model:
  delivery_model: ""           # e.g. fully automated, service-led, hybrid
  human_touchpoints: []        # Where humans are essential in the process
  automated_touchpoints: []    # Where automation handles delivery
  technology_stack: []         # Core systems (e.g. a booking provider, a payment provider, GBP)
  key_partners: []             # Critical third-party dependencies
  capacity_constraints: []     # What limits scale? (e.g. physical space, headcount)
  scalability_model: ""        # How does the business scale? What breaks first?
```

---

## Section 3 — Functional Objectives `[REQUIRED]`

Each functional domain has: a domain lead (human role or AI manager agent),
current baseline metrics, active objectives, and KPI thresholds that trigger
cascade events to relevant rosters.

Objectives follow OKR structure: **Objective** (qualitative direction) +
**Key Results** (measurable outcomes). Key Results carry a status:
`on-track`, `at-risk`, `off-track`, `achieved`.

### 3.0 The domain set is TIER-DEPENDENT, not a fixed nine

Earlier versions asserted nine `[REQUIRED]` domains for every business. That
is heavier than a micro-business needs and lighter than a corporate needs —
in the Riverside Bookings pilot (a T1 small business) several domains were
thin or mostly-TBC. The domain set is therefore **tier-dependent**: which
domains are live scales with the confirmed engagement tier (see the
`engagement-lifecycle` tier ladder, T0–T2). The interview **confirms the live
domains for this business** rather than populating all nine by default.

**Core domains — always live at every tier (T0 upward):**

- **Finance** (§3.1)
- **Sales & Revenue** (§3.2)
- **Marketing** (§3.3)
- **Operations** (§3.4)
- **AI Manager** (§3.9) — governs the agent ecosystem itself; never optional

These five are the irreducible spine of any trading business — money in,
demand, delivery, and the governance of the system running it.

**Tier-gated domains — switch on as tier and complexity rise:**

| Domain | Typically lives from | Gating signal |
|--------|----------------------|---------------|
| **Product / Service** (§3.5) | T1 | A distinct product/service portfolio to manage |
| **Technology** (§3.6) | T1–T2 | Material systems/integration surface |
| **HR & People** (§3.7) | T2 (or T1 with staff) | Headcount beyond the owner |
| **Legal & Compliance** (§3.8) | T2 (earlier if regulated) | Regulatory / data-sensitivity load |

A tier-gated domain that is not live for a business is **skipped** (not left
as an empty `[REQUIRED]` shell). A domain can be switched on at any quarterly
review if the business's complexity grows — a MINOR ECL bump with a cascade.

### 3.0.1 Rationale for the SME domain taxonomy

The domain set maps to the **standard functional breakdown of a trading
business** — finance, sales, marketing, operations, product, technology,
people, and legal — the same functions a conventional org chart or a standard
management-accounting/value-chain view would name. It is chosen for the
framework's target market: **small-to-large SME**. It is not an arbitrary
nine; it is the SME-relevant function set, tier-gated so an SME populates only
what it actually runs.

**Corporate domains are deliberately excluded and reserved.** Risk, ESG,
Investor Relations, and M&A are first-class functions only at mid-market and
enterprise scale (tiers T3–T4), which are **explicitly out of scope** for the
current framework (see `engagement-lifecycle` — *Out of scope, reserved not
coded*). They are named here as a reservation so the taxonomy has a documented
path up; they are not implemented as SME domains.

---

### 3.1 Finance

```yaml
finance:
  domain_lead: ""
  cycle: "monthly-review"
  baseline_metrics:
    monthly_revenue: ""
    monthly_costs: ""
    gross_margin: ""
    cash_runway: ""
    outstanding_receivables: ""
  objectives:
    - objective: ""
      key_results:
        - kr: ""
          target: ""
          current: ""
          status: ""
  cascade_triggers:
    - condition: "Monthly revenue drops >15% vs prior month"
      action: "Escalate to ECL Orchestrator — review all roster spend allocations"
    - condition: "Cash runway falls below 90 days"
      action: "MAJOR escalation — human review required before any new roster activation"
```

---

### 3.2 Sales & Revenue

```yaml
sales_revenue:
  domain_lead: ""
  cycle: "monthly-review"
  baseline_metrics:
    monthly_bookings: ""
    average_order_value: ""
    conversion_rate: ""
    lead_volume: ""
    customer_acquisition_cost: ""
    customer_lifetime_value: ""
  objectives:
    - objective: ""
      key_results:
        - kr: ""
          target: ""
          current: ""
          status: ""
  cascade_triggers:
    - condition: "Lead volume drops >20% month-on-month"
      action: "Query SEO and Paid Media roster orchestrators — demand generation review"
    - condition: "Conversion rate drops >10% month-on-month"
      action: "Query Operations and Product roster orchestrators — funnel review"
```

---

### 3.3 Marketing

```yaml
marketing:
  domain_lead: ""
  cycle: "monthly-review"
  active_rosters: []             # e.g. [roster-seo, roster-paid-media, roster-email]
  baseline_metrics:
    organic_traffic: ""
    paid_traffic: ""
    brand_search_volume: ""
    social_reach: ""
    email_list_size: ""
    content_pieces_live: ""
  objectives:
    - objective: ""
      key_results:
        - kr: ""
          target: ""
          current: ""
          status: ""
  roster_priority_weighting:    # How budget/effort splits across active rosters
    roster-seo: ""              # e.g. 40%
    roster-paid-media: ""       # e.g. 30%
    roster-email: ""            # e.g. 30%
  cascade_triggers:
    - condition: "Organic traffic drops >25% month-on-month"
      action: "Query SEO roster orchestrator — algorithm or ranking change audit"
    - condition: "Brand search volume increases >30% month-on-month"
      action: "Notify all roster orchestrators — brand momentum, capitalise"
```

---

### 3.4 Operations

```yaml
operations:
  domain_lead: ""
  cycle: "monthly-review"
  baseline_metrics:
    service_capacity: ""         # e.g. available units, slots, hours
    utilisation_rate: ""         # % of capacity used
    fulfilment_rate: ""          # % of bookings/orders fulfilled successfully
    operational_cost_per_unit: ""
    automation_coverage: ""      # % of operational touchpoints automated
  objectives:
    - objective: ""
      key_results:
        - kr: ""
          target: ""
          current: ""
          status: ""
  cascade_triggers:
    - condition: "Utilisation rate exceeds 90% for 2 consecutive months"
      action: "Notify Sales roster — constrain demand generation until capacity increases"
    - condition: "Fulfilment rate drops below 95%"
      action: "Pause all demand-generating roster activity — operations review first"
```

---

### 3.5 Product / Service

```yaml
product_service:
  domain_lead: ""
  cycle: "quarterly"
  core_products_services: []     # List of primary offerings
  baseline_metrics:
    customer_satisfaction_score: ""   # e.g. NPS, CSAT, star rating average
    review_volume: ""
    review_average_rating: ""
    repeat_purchase_rate: ""
    product_complaint_rate: ""
  objectives:
    - objective: ""
      key_results:
        - kr: ""
          target: ""
          current: ""
          status: ""
  cascade_triggers:
    - condition: "Average review rating drops below 4.0"
      action: "Pause GBP roster review response cadence — escalate to human"
    - condition: "New product/service launched"
      action: "Notify all roster orchestrators — update engagement context"
```

---

### 3.6 Technology

```yaml
technology:
  domain_lead: ""
  cycle: "quarterly"
  core_stack: []                 # Primary systems and integrations
  baseline_metrics:
    system_uptime: ""            # % availability of core systems
    integration_failure_rate: "" # % of automated integrations failing
    tech_debt_rating: ""         # e.g. low / medium / high (human assessment)
    automation_roi: ""           # Revenue or time saved by automation
  objectives:
    - objective: ""
      key_results:
        - kr: ""
          target: ""
          current: ""
          status: ""
  cascade_triggers:
    - condition: "Core system downtime exceeds 2 hours"
      action: "Pause all roster activity dependent on affected system"
    - condition: "New integration required by any roster"
      action: "Technology domain review before roster activation proceeds"
```

---

### 3.7 HR & People

```yaml
hr_people:
  domain_lead: ""
  cycle: "quarterly"
  baseline_metrics:
    headcount: ""
    open_roles: ""
    employee_satisfaction: ""    # e.g. eNPS
    training_hours_per_person: ""
    ai_tool_adoption_rate: ""    # % of team actively using AI tooling
  objectives:
    - objective: ""
      key_results:
        - kr: ""
          target: ""
          current: ""
          status: ""
  cascade_triggers:
    - condition: "AI tool adoption rate below 50% after 60 days"
      action: "Notify AI Manager domain — training intervention required"
    - condition: "Critical role vacant for >30 days"
      action: "Notify ECL Orchestrator — assess roster coverage impact"
```

---

### 3.8 Legal & Compliance

```yaml
legal_compliance:
  domain_lead: ""
  cycle: "quarterly"
  applicable_regulations: []     # e.g. GDPR, PCI-DSS, ICO registration
  baseline_metrics:
    open_compliance_issues: ""
    data_incidents_ytd: ""
    policy_review_date: ""
    gdpr_compliance_status: ""   # e.g. compliant / review-needed / non-compliant
  objectives:
    - objective: ""
      key_results:
        - kr: ""
          target: ""
          current: ""
          status: ""
  constraints_on_rosters:
    - "All marketing content must comply with ASA UK guidelines"
    - "Customer data collected via any roster tool must be GDPR-compliant"
    - "No roster may store PII outside approved data infrastructure"
  cascade_triggers:
    - condition: "Any data incident detected"
      action: "IMMEDIATE pause of all data-processing roster activity — human escalation"
    - condition: "New regulation identified affecting operations"
      action: "Legal review before affected roster continues"
```

---

### 3.9 AI Manager

```yaml
ai_manager:
  domain_lead: ""
  cycle: "monthly-review"
  framework_version: ""          # Version of this ECL/roster framework
  active_rosters: []             # All currently active rosters
  active_agents: []              # All currently active agents across all rosters
  baseline_metrics:
    total_agents_active: ""
    roster_performance_avg: ""   # Average KPI achievement across all rosters
    agent_failure_rate: ""       # % of agent tasks failing or requiring human override
    human_override_rate: ""      # % of decisions escalated to human
    version_bump_frequency: ""   # Average bumps per month (health indicator)
    cost_per_outcome: ""         # e.g. cost per lead, cost per ranking gained
  objectives:
    - objective: "Maintain a high-performing, well-governed AI agent ecosystem"
      key_results:
        - kr: "Agent failure rate below 5%"
          target: "<5%"
          current: ""
          status: ""
        - kr: "Human override rate below 15%"
          target: "<15%"
          current: ""
          status: ""
        - kr: "All active rosters at MINOR version or above within 90 days"
          target: "100%"
          current: ""
          status: ""
  governance_rules:
    - "No new roster activates without ECL sign-off"
    - "No agent may access systems outside its declared toolbox"
    - "All MAJOR version bumps require human review regardless of trigger"
    - "Agent learning logs are reviewed monthly by AI Manager domain lead"
    - "Roster version history is maintained indefinitely — no deletion"
  cascade_triggers:
    - condition: "Agent failure rate exceeds 10% in any roster"
      action: "Pause affected roster — AI Manager audit before restart"
    - condition: "Human override rate exceeds 25% in any roster"
      action: "Review roster agent definitions — possible MINOR version bump"
    - condition: "New AI capability available (e.g. new model, new tool)"
      action: "AI Manager evaluates applicability — propose toolbox update via MINOR bump"
```

---

## Section 4 — Cascade Briefing Protocol `[REQUIRED]`

When the ECL runs its quarterly or annual cycle and produces a new version,
the ECL Orchestrator generates a cascade briefing for every active roster.

### Cascade Briefing Structure

```markdown
# ECL Cascade Briefing
**ECL Version:** v1.x.x → v1.y.y
**Date:** YYYY-MM-DD
**Triggered By:** [quarterly review / annual review / material business event]
**Cascade To:** [list of active roster IDs]

## What Changed
[Summary of version changes — which sections, which objectives, which KPIs]

## Impact Assessment Per Roster
### roster-seo
- Affected objectives: [list]
- Required action: [none / review / update / pause]
- Priority: [low / medium / high / critical]

### roster-[x]
- ...

## Constraints Updated
[Any new legal, operational, or strategic constraints rosters must observe]

## Human Sign-off Required
[List any items requiring human approval before rosters action this briefing]

## Acknowledgement Required
Each roster orchestrator must log receipt of this briefing in their
engagement_log before proceeding with any cycle activity.
```

---

## Section 5 — Roster Registry `[REQUIRED]`

```yaml
roster_registry:
  business_id: ""
  last_updated: ""
  active_rosters:
    - roster_id: ""
      version: ""
      status: ""             # active / paused / draft / deprecated
      orchestrator_id: ""
      activated_date: ""
      last_cascade_received: ""
      last_cascade_version: ""
  planned_rosters:
    - roster_id: ""
      target_activation: ""
      dependency: ""         # e.g. "requires Finance domain objectives finalised"
```

---

## Section 6 — ECL Cycle Cadence `[REQUIRED]`

```yaml
ecl_cycle:
  annual_review:
    month: ""                # e.g. January (aligns with fiscal year)
    scope: "Full ECL review — all sections, North Star, MAJOR bump if required"
    participants: []         # Human roles required

  h1_review:
    month: ""                # e.g. July
    scope: "Mid-year strategic check — objectives on track, SWOT refresh"
    participants: []

  quarterly_reviews:
    - quarter: "Q1"
      month: ""
      scope: "OKR progress, KPI baselines updated, cascade issued"
    - quarter: "Q2"
      month: ""
      scope: "OKR progress, KPI baselines updated, cascade issued"
    - quarter: "Q3"
      month: ""
      scope: "OKR progress, KPI baselines updated, cascade issued"
    - quarter: "Q4"
      month: ""
      scope: "Year-end review, next year objectives set"

  monthly_management_review:
    scope: "KPI dashboard review — Finance, Sales, Marketing, AI Manager"
    output: "PATCH bumps if thresholds breached, no structural changes"
```

---

## ECL Orchestrator Definition

**ID:** `ecl_orchestrator`
**Role:** Executive Command Orchestrator
**Classification:** Constitutional — sits above all roster orchestrators

**Goal:**
Maintain the ECL as the single source of truth for business context.
Run the ECL cycle at defined cadences. Cascade objective updates to
all active roster orchestrators. Respond to queries from roster
orchestrators on major decisions. Escalate to human when required.

**Responsibilities:**
- Conduct the ECL interview for new business instantiation
- Maintain and version the ECL document
- Generate cascade briefings on every version bump
- Receive and resolve queries from roster orchestrators
- Monitor cross-roster KPI health via AI Manager domain
- Propose MAJOR version bumps to human for sign-off
- Maintain the roster registry

**Query Response Protocol:**
When a roster orchestrator submits a query:
1. Identify which ECL section is relevant
2. Return the relevant section content
3. State any constraints that apply
4. Log the query and response in the engagement_log
5. If the query reveals an ECL gap → flag for next quarterly review

**Escalation Rules:**
- Any MAJOR version bump → human sign-off required
- Any cross-roster conflict → human arbitration required
- Any legal/compliance trigger → immediate human notification
- Any North Star metric deviation >20% → human strategic review

**Tools Required:**
- document_store_api      # Read/write ECL documents
- roster_registry_api     # Read/write roster registry
- cascade_broadcast_api   # Push briefings to roster orchestrators
- analytics_dashboard     # Monitor cross-roster KPI health
- interview_agent         # Conduct ECL creation interviews

---

## Framework Principles (Constitutional — applies to ECL and all rosters)

These sit above the roster-agnostic principles defined in individual rosters.
They cannot be overridden at any level.

### C1 — The ECL Is the Single Source of Truth
Business objectives, context, and constraints live in the ECL only.
No roster, agent, or document may define or redefine business objectives.
Rosters act on ECL objectives — they do not create them.

### C2 — Cascade Before Action
No roster orchestrator may act on a new ECL version without
acknowledging the cascade briefing. Unacknowledged briefings block
new cycle activity in the affected roster.

### C3 — Constraints Cascade With Objectives
When the ECL updates objectives, any constraints attached to those
objectives (legal, operational, financial) cascade simultaneously.
Roster orchestrators may not cherry-pick objectives without constraints.

### C4 — The North Star Arbitrates Conflicts
When two rosters have competing priorities, the North Star metric
is the tiebreaker. The activity that most directly moves the North
Star takes precedence. The ECL Orchestrator arbitrates.

### C5 — Human Authority Is Preserved
The AI agent ecosystem — ECL Orchestrator, roster orchestrators,
and all agents — exists to inform and execute human decisions,
not replace them. MAJOR strategic decisions always require
human sign-off. The system surfaces options and recommendations;
humans choose.

### C6 — Transparency Across the Stack
Every agent decision, every version bump, every cascade, and every
human override is logged. The full history of how the business was
run by this system is always reconstructable from the logs.
```

