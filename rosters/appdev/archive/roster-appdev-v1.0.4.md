# Application Development Roster
**Roster ID:** `roster-appdev`
**Version:** `v1.0.4`
**Status:** `Draft`
**Created:** 2026-07-02
**Last Updated:** 2026-07-06
**Owner:** Russell Perry

---

## Version History

| Version | Date | Type | Change Summary | Triggered By |
|---------|------|------|----------------|--------------|
| v1.0.4 | 2026-07-06 | Patch | Added three standing standards from the Riverside Bookings close-out: (1) the pilot/production **posture-equivalence standard** backing the engineering-agent MINOR bumps (05→1.1.0, 06→1.1.0, 07→1.1.0); (2) a **default NFR budget table** (Core Web Vitals good thresholds + roster-standard latency/availability defaults, marked "proposed — tune per engagement"); (3) an **analytics/measurement go-live gating rule** (tool decision is an M4/architecture-time launch blocker; the insight agent's REAL reporting cycle is gated on "instrumented AND real traffic exists") | LEARN harvest — VBP-014 (roster-doc portion), VBP-015, VBP-016 |
| v1.0.3 | 2026-07-06 | Patch | Added the fail-safe-default-behind-config pattern (ADR D14) as standing roster guidance; carries the agent PATCH bumps from the Riverside Bookings close-out (00→1.0.1, 03→1.0.1, 04→1.0.1, 05→1.0.2, 08→1.0.1, 12→1.0.1) | LEARN harvest — VBP-011 |
| v1.0.0 | 2026-07-02 | Major | Initial roster definition — full software delivery team (13 agents) built to AOM v1.0.0 | Manual — new roster |
| v1.0.2 | 2026-07-03 | Patch | Handoff-contract alignment: production_url declared as devops_repo_cicd_agent output (05→v1.0.1, superseded version archived) — resolves undeclared producer found by validator E16 | Final deep audit — validate_framework.py E16 |
| v1.0.1 | 2026-07-02 | Patch | Cross-roster collaboration with roster-seo documented (inbound SEO implementation requirements, outbound release notifications) per framework-architecture v1.1.0 | roster registration in constitutional layer |

### Versioning Rules

This roster follows **semantic versioning (MAJOR.MINOR.PATCH)**. Version bumps are triggered
by the Goal→Plan→Act→Review→Learn cycle reacting to delivery data or strategic change.

| Increment | When to use | Cycle trigger |
|-----------|-------------|---------------|
| **PATCH** `v1.0.x` | Single agent rule, tool version, or decision logic updated | LEARN phase output |
| **MINOR** `v1.x.0` | Agent added/removed, tool integration changed, new stack component adopted | REVIEW phase output |
| **MAJOR** `vx.0.0` | Core delivery methodology changes, orchestrator strategy pivots, default stack replaced | GOAL phase revisited |

**Rule:** No agent definition may be edited without a corresponding version bump and changelog entry.
**Rule:** Major version bumps require human sign-off before deployment.

---

## Roster Mission

Take a product idea from business requirement to a deployed, secure, observable web
application — and keep it healthy through iteration. The roster owns the full software
delivery lifecycle: discovery, solution design, architecture, build, quality assurance,
security, release engineering, and post-launch insight.

This roster is **stack-opinionated by default**. Unless an engagement's ECL or the
Solution Architecture Designer records a documented exception, every application is
built on the default stack:

| Layer | Default choice | Owned by |
|-------|----------------|----------|
| Hosting / deploy / edge | **Vercel** | DevOps (05), Front-end (08) |
| Application framework | **Next.js (App Router) + TypeScript** | Architecture (04), Front/Back-end (07/08) |
| Database | **Neon** (serverless Postgres) | Database Engineer (06) |
| Authentication | **Clerk** | Back-end (07), Front-end (08) |
| Transactional email | **Resend** | Back-end (07) |
| Source control + CI/CD | **GitHub + GitHub Actions** | DevOps (05) |

The default stack is a starting position, not a constraint the roster may never revisit.
Replacing a default stack component is a **MAJOR** roster decision requiring human sign-off
(see Performance Indicators → Version Bump Map).

---

## Roster Principles (inherits constitutional P1–P8, adds delivery-specific)

This roster inherits the eight roster-agnostic principles defined in `roster-seo` /
the constitutional layer (Structure Before Content, Decisions Are Documented,
Version Everything, Tools Are Declared, Handoffs Are Contracts, Performance Closes
the Loop, Humans Own Major Pivots, Discipline Balance Is Dynamic). It adds four
delivery-specific principles:

### D1 — Requirements Before Code
No engineering agent (06/07/08) fires until requirements (02) and architecture (04)
are confirmed. Code written against unconfirmed requirements creates rework debt.

### D2 — The Pipeline Is the Gate
CI/CD (Agent 05) is authored before application code is written. No code reaches an
environment except through the pipeline. A red pipeline blocks all downstream handoffs.

### D3 — Security Is a Wave, Not an Afterthought
The Security & Infosec Manager (09) sets policy at design time and reviews at build time.
Its CRITICAL findings are blocking — no release proceeds over an unresolved CRITICAL.

### D4 — Nothing Ships Unmeasured
Every release defines the analytics/observability it will be measured by before it goes
live. Business Insight (12) closes the loop the same way performance reporting does in SEO.

---

## Standing Delivery Patterns (roster guidance)

Patterns that proved themselves in engagement and are now standing guidance
(added at v1.0.3 per VBP-011).

### Fail-safe default behind config (ADR D14)
When a feature depends on an external decision, an unverified capability, or a
launch-blocking open question that is not yet resolved, ship it **behind a
configuration flag whose default is the fail-safe behaviour**, rather than
blocking the build or guessing the answer. The safe default (feature off /
conservative limit / no destructive action) is what runs until the real value
is confirmed and the flag is flipped by config — no code change, no redeploy.
This keeps delivery moving without fabricating a decision, and the flag itself
is the tracked task that records "flip when X is confirmed." [L-appdev-012]

### Pilot / production posture-equivalence standard (added v1.0.4)

An engagement runs in one of two **postures**: `pilot` or `production`. This is a
single engagement-level switch (declared in the ECL / ADR / `environment_config`),
**not** a per-agent decision.

**Standard:** every production-vendor dependency and every production-only output
MUST have a declared, swappable **pilot equivalent**, so posture is a *config
switch, not a code rewrite*. Any output, gate, or check that assumes production
must state its pilot-mode equivalent rather than silently failing its own review
phase in a pilot build. The canonical equivalence map (carried in the engineering
agents' `posture_model` sections at v1.1.0):

| Production dependency / output | Owner | Pilot equivalent | Flip obligation (M9b / go-production) |
|--------------------------------|-------|------------------|----------------------------------------|
| `production_url` (live deploy) | 05 | Local/preview URL + smoke-test evidence, tagged as pilot preview | Re-issue the real `production_url` |
| Enforced remote branch protection | 05 | Documented remote config, enforcement deferral **logged** as a tracked task | Enforce protection |
| **Neon** serverless Postgres | 06 | **PGlite / embedded Postgres** behind the same ORM; figures labelled by driver | Re-measure performance on Neon |
| **Clerk** auth | 07 | Env-gated test double behind an `Auth` interface | Bind the real vendor (env only) |
| **Resend** email | 07 | Env-gated `EmailSender` double | Bind the real vendor (env only) |
| **A booking provider** / **payment provider** | 07 | Env-gated `BookingProvider` / `PaymentProvider` doubles | Bind the real vendors (env only) |

**Rules:**
- Vendor integrations (auth, email, booking, payment) are called through **swappable
  interfaces**, never hard-wired to a vendor SDK in business logic.
- A pilot equivalent's result (preview deploy, PGlite benchmark, test-double response)
  is **never presented as** a production result; the binding/driver in effect is stated.
- Every pilot→production flip is a **tracked go-production task** with a firing
  condition, not a prose footnote. [L-appdev-009, L-appdev-010, L-appdev-012]

### Default NFR budget (added v1.0.4 — engagements TUNE, not re-derive) [VBP-015]

Every engagement previously re-derived latency/availability numbers from scratch.
This is the roster **default NFR budget**: Agent 04 adopts it into the ADR and
**tunes** it per engagement rather than starting from a blank sheet.

**Core Web Vitals — "good" thresholds (cited; hard targets).** These are the
Google Core Web Vitals *good* thresholds (75th-percentile field data) and are
adopted as-is, not "proposed":

| Metric | Good threshold | Notes |
|--------|----------------|-------|
| **LCP** (Largest Contentful Paint) | **≤ 2.5 s** | at p75, field data |
| **INP** (Interaction to Next Paint) | **≤ 200 ms** | at p75; replaced FID as a Core Web Vital in 2024 |
| **CLS** (Cumulative Layout Shift) | **≤ 0.1** | at p75 |

**Roster-standard latency / availability defaults (PROPOSED — tune per engagement).**
Starting positions to be confirmed or overridden in the ADR against the engagement's
actual scale, SLA, and cost envelope:

| Dimension | Proposed default | Tune when |
|-----------|------------------|-----------|
| API server response (read, p95) | ≤ 300 ms | Heavy aggregation / third-party fan-out |
| API server response (write, p95) | ≤ 500 ms | Multi-step transactions / external calls |
| DB query (p95, single-statement) | ≤ 50 ms | Reporting / analytical workloads |
| App availability (monthly) | 99.9% | Regulated / revenue-critical SLAs |
| Error budget (5xx rate) | < 0.1% of requests | — |
| Time-to-first-byte (TTFB, p75) | ≤ 800 ms | Edge/SSR-heavy or geo-distributed audiences |

The CWV row values are cited Google thresholds; the latency/availability rows are
**roster proposals** the engagement is expected to tune. [L-appdev-007]

### Analytics / measurement go-live gating (added v1.0.4) [VBP-016]

Extends principle **D4 — Nothing Ships Unmeasured**:

1. **The analytics/measurement tooling decision is an ARCHITECTURE / M4-time launch
   blocker, not a late discovery.** The choice of analytics/measurement tooling
   (the OQ-005 / GAP-012 class — including its spend and any data-exclusion-zone
   dimension) is due at the **ADR / M4** and is a **go-live blocker**. It must NOT
   be allowed to reach the Wave-10 measurement wave still open — an unresolved
   measurement-tool decision at launch makes honest measurement impossible. If the
   decision is open at M4, it is raised on the owner-decision queue and, if still
   unresolved at build, shipped behind a fail-safe-default flag (see above) with the
   flip tracked — never silently deferred to Wave 10.
2. **The insight agent's REAL (non-illustrative) reporting cycle is gated on
   "instrumented AND real traffic exists."** `insight_business_analytics_agent`
   (Agent 12) may only produce a REAL measured report once the product is
   instrumented **and** real traffic exists. Fired before that, it runs its
   sanctioned **pre-launch mode** (instrumentation-spec + clearly-labelled
   illustrative report + Measurement-Readiness verdict) — never fabricated numbers.
   This gate is already encoded in Agent 12 v1.0.1 (`pre_launch_mode` + the
   `goal_phase` gate); this rule makes it a standing roster requirement. [L-appdev-019]

---

## Roster Structure

```
roster-appdev/
├── roster-appdev-v1.0.4.md          ← This document (master roster)
└── agents/
    ├── agent-00-appdev-orchestrator-v1.0.1.yaml   ← Lead Developer & Delivery Orchestrator
    ├── agent-01-project-manager-v1.0.0.yaml
    ├── agent-02-business-analyst-v1.0.0.yaml
    ├── agent-03-business-solution-design-v1.0.1.yaml
    ├── agent-04-solution-architecture-v1.0.1.yaml
    ├── agent-05-repo-cicd-v1.1.0.yaml
    ├── agent-06-database-engineer-v1.1.0.yaml
    ├── agent-07-backend-developer-v1.1.0.yaml
    ├── agent-08-frontend-developer-v1.0.1.yaml
    ├── agent-09-security-infosec-v1.0.0.yaml
    ├── agent-10-qa-testing-v1.0.0.yaml
    ├── agent-11-uxui-testing-v1.0.0.yaml
    └── agent-12-business-insight-v1.0.1.yaml
```

---

## Agent Roster

### Crew: `delivery_team` → Sub-crew: `application_development`

| # | Agent ID | Role | Discipline | Fires After |
|---|----------|------|------------|-------------|
| 00 | `roster_appdev_orchestrator_agent` | Lead Developer & Delivery Orchestrator | All | Engagement start |
| 01 | `delivery_project_manager_agent` | Project Manager | Delivery | Orchestrator kickoff |
| 02 | `analysis_business_analyst_agent` | Business Analyst | Analysis | Agent 01 confirmed |
| 03 | `design_business_solution_agent` | Business Solution Designer | Solution Design | Agent 02 confirmed |
| 04 | `architecture_solution_design_agent` | Solution Architecture Designer | Architecture | Agent 03 confirmed |
| 05 | `devops_repo_cicd_agent` | GitHub Repo & CI/CD Manager | DevOps | Agent 04 confirmed |
| 06 | `engineering_database_agent` | Database Engineer | Engineering | Agent 04 + 05 confirmed |
| 07 | `engineering_backend_agent` | Back-end Developer | Engineering | Agent 06 confirmed |
| 08 | `engineering_frontend_agent` | Front-end Developer | Engineering | Agent 07 confirmed |
| 09 | `security_infosec_manager_agent` | Security & Infosec Manager | Security | Agent 04 (policy) + 08 (review) |
| 10 | `qa_functional_testing_agent` | QA Tester | QA | Agent 08 confirmed |
| 11 | `qa_uxui_testing_agent` | UX/UI Tester | QA / UX | Agent 08 confirmed |
| 12 | `insight_business_analytics_agent` | Business Insight | Insight | 14 days post-launch |

**Note on the Lead Developer:** Per the requested team, the Lead Developer "manages the
team." In this framework that coordination role is the roster orchestrator (Agent 00).
The Lead Developer is therefore modelled as the orchestrator, and the Project Manager
(Agent 01) is a distinct specialist owning planning, scheduling, and stakeholder
communication. If the two should be split into separate agents, that is a MINOR roster bump.

---

## Agent Definitions (summary — full specs in `agents/`)

### Agent 00 — Lead Developer & Delivery Orchestrator
**ID:** `roster_appdev_orchestrator_agent` · **Discipline:** All · **Depth:** full
Receives the ECL cascade briefing, sequences the delivery team in dependency waves,
monitors handoff completion, enforces the pipeline and security gates, resolves agent
queries against the ECL/AOM, manages human overrides, and triggers LEARN. Never writes
production code directly — it coordinates the agents that do.

### Agent 01 — Project Manager
**ID:** `delivery_project_manager_agent` · **Discipline:** Delivery · **Depth:** lean
Turns the engagement scope into a delivery plan: milestones, sequencing, RAID log
(Risks/Assumptions/Issues/Dependencies), and stakeholder communication cadence.
Owns scope-change control. Does not make technical decisions.

### Agent 02 — Business Analyst
**ID:** `analysis_business_analyst_agent` · **Discipline:** Analysis · **Depth:** lean
Elicits and documents functional and non-functional requirements as user stories with
acceptance criteria. Produces the requirements backlog that everything downstream builds
against. Flags gaps for human input — never invents requirements.

### Agent 03 — Business Solution Designer
**ID:** `design_business_solution_agent` · **Discipline:** Solution Design · **Depth:** lean
Translates requirements into a functional solution: user journeys, feature breakdown,
domain model (business-level), and how the product delivers the business outcome. Bridges
"what the business needs" (02) and "how it is built" (04).

### Agent 04 — Solution Architecture Designer
**ID:** `architecture_solution_design_agent` · **Discipline:** Architecture · **Depth:** full
Owns the technical architecture and the default stack decision (Vercel / Neon / Clerk /
Resend / Next.js). Produces the architecture decision record (ADR), system/component
diagram, data-flow, environment topology, and non-functional budget (performance,
scalability, cost). Any deviation from the default stack is recorded as an ADR exception.

### Agent 05 — GitHub Repo & CI/CD Manager
**ID:** `devops_repo_cicd_agent` · **Discipline:** DevOps · **Depth:** lean
Scaffolds the GitHub repository, branch protection, and the GitHub Actions pipeline
(lint → typecheck → test → build → preview deploy → production deploy to Vercel). Manages
environments and secrets configuration (references only — never stores secret values).
The pipeline is authored **before** application code (principle D2).

### Agent 06 — Database Engineer
**ID:** `engineering_database_agent` · **Discipline:** Engineering · **Depth:** lean
Designs and provisions the Neon (Postgres) schema, migrations, indexes, and access
patterns from the domain model. Owns data integrity, migration safety, and query
performance. Provides the typed data layer the back-end consumes.

### Agent 07 — Back-end Developer
**ID:** `engineering_backend_agent` · **Discipline:** Engineering · **Depth:** lean
Builds server-side logic: API routes / server actions, business rules, Clerk auth
integration, Resend transactional email, and data access against the Neon schema.
Delivers the typed API contract the front-end consumes.

### Agent 08 — Front-end Developer
**ID:** `engineering_frontend_agent` · **Discipline:** Engineering · **Depth:** lean
Builds the Next.js UI: pages, components, state, and Clerk-gated flows, consuming the
back-end contract. Deploys to Vercel via the pipeline. Implements the designs from
Agent 03 and meets the accessibility/performance budget from Agent 04.

### Agent 09 — Security & Infosec Manager
**ID:** `security_infosec_manager_agent` · **Discipline:** Security · **Depth:** lean
Sets the security policy at design time (authn/authz model, data classification, secrets
handling, dependency policy) and reviews the build (threat model, dependency/SAST scan,
Clerk/Neon/Vercel configuration review). CRITICAL findings are blocking.

### Agent 10 — QA Tester
**ID:** `qa_functional_testing_agent` · **Discipline:** QA · **Depth:** lean
Verifies the build against Agent 02's acceptance criteria: test plan, functional /
integration / end-to-end tests (Playwright), regression, and defect reporting back to
the owning engineering agent. Signs off functional readiness.

### Agent 11 — UX/UI Tester
**ID:** `qa_uxui_testing_agent` · **Discipline:** QA / UX · **Depth:** lean
Verifies the delivered UI against the solution design and usability/accessibility
standards: heuristic review, WCAG 2.2 AA checks, responsive/cross-device behaviour,
and interaction quality. Reports defects to the Front-end Developer.

### Agent 12 — Business Insight
**ID:** `insight_business_analytics_agent` · **Discipline:** Insight · **Depth:** lean
Closes the loop post-launch. Instruments the product (Vercel Analytics / product
analytics), measures adoption and the business outcome defined in the ECL, and feeds
LEARN-phase findings and version-bump proposals back to the orchestrator.

---

## Toolbox

### Toolbox Version: `v1.0.0`
### Toolbox Scope: `roster-appdev` — applicable to all agents in this roster

### Tool Category 1: Source Control & CI/CD

| Tool | Purpose | Agents | API/Integration |
|------|---------|--------|----------------|
| **GitHub** | Source of truth — repo, branches, PRs, protection rules, code review | 05, all engineering | GitHub REST/GraphQL API + MCP. OAuth/app token. |
| **GitHub Actions** | CI/CD pipeline — lint, typecheck, test, build, deploy | 05, 10 | Workflow YAML in `.github/workflows/`. Runner-based. |
| **Vercel** | Hosting, edge, preview + production deploys, env management | 05, 08, 07 | Vercel API + GitHub integration. Preview deploy per PR. |

### Tool Category 2: Application Platform (Default Stack)

| Tool | Purpose | Agents | API/Integration |
|------|---------|--------|----------------|
| **Next.js (App Router)** | Application framework — SSR/RSC, routing, server actions | 04, 07, 08 | TypeScript project. Deployed on Vercel. |
| **Neon** | Serverless Postgres — primary datastore | 06, 07 | Neon API + Postgres wire protocol. Branchable DBs per environment/PR. |
| **Clerk** | Authentication & user management | 07, 08, 09 | Clerk SDK + API. Middleware-based route protection. |
| **Resend** | Transactional email delivery | 07 | Resend API. Domain verification required. |
| **ORM (Drizzle / Prisma)** | Typed schema, migrations, query layer over Neon | 06, 07 | Codegen + migration CLI. Chosen in ADR by Agent 04. |

### Tool Category 3: Quality & Testing

| Tool | Purpose | Agents | API/Integration |
|------|---------|--------|----------------|
| **Playwright** | End-to-end + cross-browser UI testing | 10, 11 | Test runner. Pre-installed Chromium. Runs in CI. |
| **Vitest / Jest** | Unit + integration testing | 07, 08, 10 | Test runner in CI pipeline. |
| **axe-core / Lighthouse** | Accessibility (WCAG) + performance auditing | 11, 08 | CLI / CI integration. Budgets set by Agent 04. |
| **TypeScript / ESLint** | Static type + lint gate | 05, 07, 08 | `tsc --noEmit` + eslint in CI. Blocking gate. |

### Tool Category 4: Security

| Tool | Purpose | Agents | API/Integration |
|------|---------|--------|----------------|
| **GitHub Dependabot / Advisory** | Dependency vulnerability scanning | 09, 05 | Native GitHub. Alerts on vulnerable deps. |
| **SAST (CodeQL / Semgrep)** | Static application security testing | 09 | GitHub Actions integration. Runs in CI. |
| **Secret scanning** | Detect committed secrets | 09, 05 | GitHub secret scanning + pre-commit hooks. |

### Tool Category 5: Analytics & Observability

| Tool | Purpose | Agents | API/Integration |
|------|---------|--------|----------------|
| **Vercel Analytics / Speed Insights** | Traffic + real-user performance | 12, 08 | Native Vercel integration. |
| **Product analytics (PostHog)** | Adoption, funnels, feature usage | 12 | SDK + API. Event instrumentation. |
| **Sentry** | Error monitoring + tracing | 12, 07, 08 | SDK + API. Release-tagged errors. |

---

## Engagement Flow Diagram

```
ORCHESTRATOR (00 — Lead Developer)
│
├── WAVE 1  FIRES: Agent 01 (Project Manager)
│         └── Outputs: delivery plan, RAID log, milestones
│
├── WAVE 2  FIRES after 01: Agent 02 (Business Analyst)
│         └── Outputs: requirements backlog, user stories + acceptance criteria
│
├── WAVE 3  FIRES after 02: Agent 03 (Business Solution Designer)
│         └── Outputs: solution design, user journeys, business domain model
│
├── WAVE 4  FIRES after 03: Agent 04 (Solution Architecture Designer)
│         └── Outputs: ADR, stack decision (Vercel/Neon/Clerk/Resend), diagrams, NFR budget
│
├── WAVE 5  FIRES after 04:
│   ├── Agent 05 (Repo & CI/CD)  ← pipeline authored BEFORE code (D2)
│   └── Agent 09 (Security)      ← security policy set at design time (D3)
│
├── WAVE 6  FIRES after 05: Agent 06 (Database Engineer)
│         └── Outputs: Neon schema, migrations, typed data layer
│
├── WAVE 7  FIRES after 06: Agent 07 (Back-end Developer)
│         └── Outputs: API contract, Clerk auth, Resend email, business logic
│
├── WAVE 8  FIRES after 07: Agent 08 (Front-end Developer)
│         └── Outputs: Next.js UI, Clerk-gated flows, Vercel deploy
│
├── WAVE 9  FIRES after 08 (parallel test + review wave):
│   ├── Agent 10 (QA Tester)        → functional/e2e sign-off
│   ├── Agent 11 (UX/UI Tester)     → usability + accessibility sign-off
│   └── Agent 09 (Security review)  → threat model + scan sign-off (CRITICAL = blocking)
│
└── WAVE 10 FIRES 14 days post-launch:
    └── Agent 12 (Business Insight)
        └── Outputs: adoption + outcome report, LEARN brief
              └── → ORCHESTRATOR: version bump recommendation
```

---

## Cross-Roster Collaboration — roster-seo

Declared per `framework-architecture` v1.1.0. All routes run **via the ECL
Orchestrator** (lateral flow rule) — never as direct agent-to-agent handoffs
across rosters.

### Inbound (SEO → App Dev)

SEO implementation outputs arrive as **confirmed requirements**: the ECL
Orchestrator routes them to this roster's orchestrator, which passes them
into `analysis_business_analyst_agent`'s backlog with acceptance criteria
preserved. They then flow through the normal waves — they are not fast-track
instructions to individual engineers.

| Incoming output | From (SEO agent) | Lands with | Typical work |
|-----------------|------------------|-----------|--------------|
| `site_architecture_map` | `seo_search_architecture_agent` | Agent 04 (Architecture) as a routing constraint | Next.js route structure must implement and preserve the map |
| `implementation_checklist` | `seo_technical_agent` | Agent 02 (BA) → backlog | Crawlability, sitemap, canonical, Core Web Vitals fixes |
| `schema_markup_per_page` + placement spec | `aeo_schema_entity_agent` | Agent 02 (BA) → backlog | JSON-LD embedded per page by front-end/back-end |

### Outbound (App Dev → SEO)

| Event in this roster | Obligation |
|----------------------|-----------|
| Release changes site structure, routing, or URLs | Orchestrator notifies ECL Orchestrator → SEO roster cascade review BEFORE the change ships. URL structure precedence sits with `seo_search_architecture_agent`'s confirmed map. |
| Release materially changes page performance (CWV vs NFR budget) | Notify via ECL — SEO technical re-audit expected |
| `instrumentation_spec` changes (Agent 12) | Share via ECL so `performance_reporting_agent` keeps one measurement source |

### Precedence rule

On URL structure and site architecture, the SEO roster's confirmed
`site_architecture_map` takes precedence — this roster must not restructure
routes without an SEO cascade review. On implementation feasibility, delivery
sequencing, and the technology used to implement a requirement, this roster's
ADR and pipeline/security gates take precedence. Conflicts are resolved by
the ECL Orchestrator against current objectives.

---

## Performance Indicators → Version Bump Map

| Indicator | Threshold | Action | Version Bump |
|-----------|-----------|--------|--------------|
| Acceptance criteria failing in QA | Any release | Return to owning engineering agent (07/08) | PATCH |
| Accessibility below WCAG 2.2 AA | Any release | Escalate Agent 11 → Agent 08 rework | PATCH |
| CI pipeline flaky / slow | Sustained | Agent 05 pipeline tuning | PATCH |
| Security finding — HIGH | Any | Agent 09 remediation brief to owning agent | PATCH |
| Security finding — CRITICAL | Any | Block release — mandatory remediation before ship | PATCH (blocking) |
| New feature epic added mid-engagement | — | New stories + design + build cycle | MINOR |
| New stack tool adopted (e.g. add a queue) | — | Add to toolbox + Agent 04 ADR | MINOR |
| Business outcome >20% below target trajectory | — | Orchestrator strategy review + ECL notification | MINOR |
| Default stack component replaced (e.g. Neon → Supabase) | — | Re-architecture — human sign-off required | MAJOR |
| Delivery methodology change (e.g. monolith → microservices) | — | Full orchestrator strategy review | MAJOR |

---

## AOM Compliance

All 13 agents in this roster are built to **AOM v1.0.0**. Run the compliance check with:

```
./scripts/aom-compliance-check.sh ./rosters/appdev/agents
```

The orchestrator (00) and the Solution Architecture Designer (04) are defined at **full**
playbook depth. The remaining specialists are defined **lean** for the v1.0.0 roster
kickoff (all AOM-required sections present, condensed cycle and briefs) and deepen as
delivery data accrues. The three engineering agents (05/06/07) received their first
**MINOR** deepening at **v1.1.0** — posture-conditional behaviour per the
posture-equivalence standard above — while their AOM definition depth remains `lean`
pending full playbook expansion.
