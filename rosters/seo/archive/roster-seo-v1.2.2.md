# Search Engine Optimisation Roster
**Roster ID:** `roster-seo`
**Version:** `v1.2.2`
**Status:** `Draft`
**Created:** 2026-03-25
**Last Updated:** 2026-07-02
**Owner:** Russell Perry

---

## Version History

| Version | Date | Type | Change Summary | Triggered By |
|---------|------|------|----------------|--------------|
| v1.0.0 | 2026-03-25 | Major | Initial roster definition | Manual — new roster |
| v1.1.0 | 2026-03-25 | Minor | AOM compliance — all agent IDs updated to {discipline}_{role}_agent convention per AOM Section 1.1 | AOM v1.0.0 compliance audit |
| v1.2.0 | 2026-07-02 | Minor | Cross-roster collaboration with roster-appdev declared — implementation outputs (technical checklist, schema markup, site architecture) routed to App Dev via ECL; App Dev release notifications trigger SEO cascade review | roster-appdev activation — framework-architecture v1.1.0 |
| v1.2.2 | 2026-07-03 | Patch | Handoff-contract alignment (validator E16/E17): missing output declarations added — orchestrator discipline_weighting_current (00→v1.0.1), serp_landscape_per_region (01→v1.0.3), completed_page_content + regional_page_urls (02→v1.0.3), sd1_sd2_check_results (03→v1.0.3), gbp_listing_urls_per_region (10→v1.0.3); aeo_optimised_content renamed to aeo_optimised_content_per_page (06→v1.0.3); plan→act phase gates added to 07 + 10 (→v1.0.3) per AOM S8.2. Superseded versions archived. | Final deep audit — validate_framework.py E16/E17 |
| v1.2.1 | 2026-07-02 | Patch | Drift + integrity corrections: structure tree updated to actual filenames; nonexistent toolbox/ dir reference removed; agents 02/03/06/07/10/11 header metadata corrected (bumped to v1.0.2, v1.0.1 archived); YAML syntax errors repaired in agents 01/03/04/07/08 (01→v1.0.2, 04→v1.0.1, 08→v1.0.1, originals archived); explicit AOM S8.4 non-fabrication gate added to agent 02 | Framework compliance audit — validate_framework.py |

### Versioning Rules

This roster follows **semantic versioning (MAJOR.MINOR.PATCH)**. Version bumps are triggered
by the Goal→Plan→Act→Review→Learn cycle reacting to performance data or strategic change.

| Increment | When to use | Cycle trigger |
|-----------|-------------|---------------|
| **PATCH** `v1.0.x` | Single agent rule or decision logic updated | LEARN phase output |
| **MINOR** `v1.x.0` | Agent added/removed, tool integration changed, new region pattern added | REVIEW phase output |
| **MAJOR** `vx.0.0` | Core mission changes, orchestrator strategy pivots, discipline weighting shifts (e.g. AEO overtakes SEO as primary lever) | GOAL phase revisited |

**Rule:** No agent definition may be edited without a corresponding version bump and changelog entry.
**Rule:** Major version bumps require human sign-off before deployment.

---

## Roster Mission

Win and sustain position one visibility across three search disciplines for a defined country,
one or more target regions, and 'near me' intent — across traditional search engines,
AI-generated answers, and geographic discovery surfaces.

The three disciplines this roster covers:

- **SEO — Search Engine Optimisation:** Organic ranking in traditional SERPs via domain authority, structure, and content relevance.
- **AEO — Answer Engine Optimisation:** Appearing as the cited source in AI-generated answers (ChatGPT, Perplexity, Google AI Overviews, Bing Copilot). Structured, citable, entity-rich content.
- **GEO — Generative Engine Optimisation:** Being surfaced by AI assistants when users ask location or service questions conversationally. Entity disambiguation, knowledge graph presence, and consistent structured data across the web.

These three are not separate strategies — they feed each other. SEO authority supports AEO
citation likelihood. GEO entity signals reinforce local SEO map pack ranking. The orchestrator
manages the balance between them based on performance indicators.

---

## Roster Principles (Roster-Agnostic)

These principles apply to **every roster** built under this framework, regardless of discipline.
They are the constitutional layer — individual rosters may add principles but may not contradict these.

### P1 — Structure Before Content
No content agent fires until the architecture agent has confirmed domain, TLD, and URL
structure. Building content on an unresolved structure creates rework debt.

### P2 — Decisions Are Documented, Not Assumed
Every agent decision — including rejections — must be logged with rationale. Downstream
agents receive documented decisions, not instructions to re-derive them.

### P3 — Version Everything
No roster, agent definition, or toolbox spec is edited in place. All changes produce a
new version with a changelog entry. This enables the LEARN phase to trace which version
of the roster produced which performance outcome.

### P4 — Tools Are Declared, Not Discovered
Every agent declares its required and optional tools upfront. If a required tool is
unavailable, the agent pauses and escalates to the orchestrator rather than proceeding
without it.

### P5 — Handoffs Are Contracts
A handoff brief is a formal contract between agents. It must be self-contained — the
receiving agent gets no other context. Incomplete handoffs are treated as failures and
return to the sending agent.

### P6 — Performance Closes the Loop
Every roster must define the performance indicators that trigger LEARN phase. Without
them, the cycle is open-ended and the roster never improves.

### P7 — Humans Own Major Pivots
PATCH and MINOR changes may be applied autonomously by the orchestrator within defined
bounds. MAJOR version bumps require human review and sign-off before deployment.

### P8 — Discipline Balance Is Dynamic
The weight given to SEO vs AEO vs GEO shifts over time in response to SERP landscape
changes. The orchestrator monitors discipline performance and recommends rebalancing.
No discipline is permanently primary.

---

## Roster Structure

```
roster-seo/
├── roster-seo-v1.2.2.md          ← This document (master roster + toolbox)
├── agents/
│   ├── agent-00-roster-seo-orchestrator-v1.0.1.yaml
│   ├── agent-01-seo-architecture-v1.0.3.yaml
│   ├── agent-02-seo-content-v1.0.3.yaml
│   ├── agent-03-seo-technical-v1.0.3.yaml
│   ├── agent-04-seo-local-citations-v1.0.1.yaml
│   ├── agent-05-seo-link-authority-v1.0.0.yaml
│   ├── agent-06-aeo-content-v1.0.3.yaml
│   ├── agent-07-aeo-schema-entity-v1.0.3.yaml
│   ├── agent-08-geo-knowledge-graph-v1.0.1.yaml
│   ├── agent-09-geo-local-presence-v1.0.0.yaml
│   ├── agent-10-gbp-management-v1.0.3.yaml
│   └── agent-11-performance-reporting-v1.0.2.yaml
└── archive/                      ← Superseded agent versions (retained indefinitely)
```

The roster toolbox is defined in the Toolbox section of this document —
it does not live in a separate directory. The current version of every
agent file is authoritatively listed in `rosters/manifest.yaml`.

---

## Agent Roster

### Crew: `marketing_team` → Sub-crew: `search_engine_optimisation`

| # | Agent ID | Role | Discipline | Fires After |
|---|----------|------|------------|-------------|
| 00 | `roster_seo_orchestrator_agent` | Search Strategy Orchestrator | All | Engagement start |
| 01 | `seo_search_architecture_agent` | Domain & Structure Specialist | SEO | Orchestrator kickoff |
| 02 | `seo_content_agent` | Regional Content Specialist | SEO | Agent 01 confirmed |
| 03 | `seo_technical_agent` | Technical SEO Auditor | SEO | Agent 01 confirmed |
| 04 | `seo_local_citations_agent` | NAP & Directory Specialist | SEO/GEO | Agent 01 confirmed |
| 05 | `seo_link_authority_agent` | Link & Authority Builder | SEO | Agent 02 confirmed |
| 06 | `aeo_content_structure_agent` | Answer-Optimised Content Specialist | AEO | Agent 02 confirmed |
| 07 | `aeo_schema_entity_agent` | Schema & Entity Markup Specialist | AEO/GEO | Agent 03 confirmed |
| 08 | `geo_knowledge_graph_agent` | Knowledge Graph & Entity Specialist | GEO | Agent 07 confirmed |
| 09 | `geo_local_presence_agent` | Local Discovery & AI Surface Specialist | GEO | Agent 04 + 08 confirmed |
| 10 | `gbp_management_agent` | Google Business Profile Specialist | SEO/GEO | Agent 01 confirmed |
| 11 | `performance_reporting_agent` | Search Performance Analyst | All | 30 days post-launch |

---

## Agent Definitions

---

### Agent 00 — Search Strategy Orchestrator

**ID:** `roster_seo_orchestrator_agent`
**Role:** Search Strategy Orchestrator
**Discipline:** All (SEO + AEO + GEO)

**Goal:**
Manage the full search visibility engagement from kickoff to performance loop.
Receive the engagement brief, sequence the agent roster, monitor handoff
completion, balance discipline weighting, and trigger LEARN phase
based on performance indicators. The orchestrator never produces
content or structural outputs directly — it coordinates agents that do.

**Responsibilities:**
- Receive and validate engagement brief (inputs from client or upstream crew)
- Sequence agent firing order based on dependencies (see roster table above)
- Monitor handoff completion — escalate blocked handoffs to human review
- Track discipline performance indicators and recommend rebalancing
- Trigger LEARN phase and produce version bump recommendations
- Maintain engagement_log throughout the engagement
- Own roster version bump proposals (PATCH/MINOR autonomously, MAJOR to human)

**Performance Indicators Monitored:**
- Position in SERP per region per keyword cluster
- Local pack (map) presence per region
- AI Overview citation rate (AEO signal)
- Knowledge panel presence (GEO signal)
- Organic traffic volume per regional page
- 'Near me' query traffic share

**Rebalancing Triggers:**
- If AI Overview citation rate > organic CTR for 2 consecutive months → increase AEO agent weight
- If local pack absent for any target region after 60 days → escalate GBP + citations agents
- If knowledge panel absent after 90 days → escalate GEO knowledge graph agent
- If position one organic held for all regions → shift resource to AEO/GEO expansion

**Escalation Rules:**
- Blocked handoff > 48 hours → human notification
- Required tool unavailable → pause dependent agents, notify human
- MAJOR version bump proposed → mandatory human sign-off

---

### Agent 01 — SEO Search Architecture Agent

**ID:** `seo_search_architecture_agent`
**Role:** Domain & Structure Specialist
**Discipline:** SEO
**Full Definition:** `agents/agent-01-seo-architecture-v1.0.3.yaml` (current version per rosters/manifest.yaml)

**Summary:**
Determines optimal domain name, TLD, and subfolder URL architecture for
target country and regions. Defines the structural foundation all other
agents build upon. Produces site architecture map and local entity signal
checklist. Does not write content or configure tools.

**Key Outputs:** domain_recommendation, site_architecture_map,
local_entity_signal_checklist, handoff_brief

**Handoffs To:** 02, 03, 04, 10

---

### Agent 02 — SEO Content Agent

**ID:** `seo_content_agent`
**Role:** Regional Content Specialist
**Discipline:** SEO

**Goal:**
Produce unique, locally-relevant landing page content for every path in
the site architecture map. Content must be substantively distinct per
region — not thin duplicates with a city name swapped. Each page must
establish topical authority for the service category in that region.

**Inputs:** site_architecture_map, engagement_context, keyword clusters (from orchestrator)

**Content Requirements Per Regional Page:**
- Unique opening that references the specific region naturally
- Service description tailored to regional context
- Local trust signals (area-specific references, not fabricated)
- FAQ section structured for AEO (question/answer format, feeds Agent 06)
- Clear service area statement
- CTA consistent with business model
- Internal links to neighbouring regional pages

**Constraints:**
- Never duplicate content across regional pages
- Never invent local facts — flag gaps to orchestrator for human input
- FAQ questions must be phrased as real user queries (feeds AEO pipeline)

**Handoffs To:** 05 (link authority), 06 (AEO content structure)

---

### Agent 03 — SEO Technical Agent

**ID:** `seo_technical_agent`
**Role:** Technical SEO Auditor
**Discipline:** SEO

**Goal:**
Ensure the site is technically crawlable, indexable, fast, and correctly
signalling geographic and service intent to search engines. Produces a
technical audit and implementation checklist. Does not implement — it
specifies for a developer or downstream automation.

**Inputs:** site_architecture_map, domain_recommendation, engagement_context

**Audit Scope:**
- Crawlability: robots.txt, sitemap.xml structure, canonical tags
- Indexability: noindex checks, crawl budget per regional path
- Page speed: Core Web Vitals baseline targets per page type
- Mobile-first: viewport, tap targets, font sizing
- HTTPS: SSL validity, mixed content checks
- Hreflang: if multi-language required (flag to orchestrator)
- Structured data: validate schema presence (coordinates with Agent 07)
- Internal linking: confirm regional pages are linked from root

**Outputs:** technical_audit_report, implementation_checklist

**Handoffs To:** 07 (schema entity — coordinates on structured data)

---

### Agent 04 — SEO Local Citations Agent

**ID:** `seo_local_citations_agent`
**Role:** NAP & Directory Specialist
**Discipline:** SEO / GEO

**Goal:**
Establish and maintain consistent Name, Address, Phone (NAP) signals
across all relevant directories for target country and regions. NAP
inconsistency directly suppresses local pack ranking and confuses
Google's entity resolution for GEO signals.

**Inputs:** domain_recommendation, local_entity_signal_checklist,
target_regions, engagement_context

**Directory Priority (UK):**
- Tier 1 (Critical): Google Business Profile, Bing Places, Apple Maps
- Tier 2 (High): Yell, Thomson Local, Checkatrade, Trustpilot, Facebook
- Tier 3 (Medium): Yelp UK, Foursquare, Hotfrog, FreeIndex
- Tier 4 (Supplementary): Industry-specific directories per service category

**NAP Rules:**
- Business name must be identical across all listings — no abbreviations
- Address format must follow Royal Mail standard (UK)
- Phone number must include country code (+44) in consistent format
- URL must point to the correct regional subfolder, not root domain

**Outputs:** nap_consistency_report, directory_submission_checklist,
citation_audit (if existing listings found)

**Handoffs To:** 09 (geo local presence — entity signals feed GEO layer)

---

### Agent 05 — SEO Link Authority Agent

**ID:** `seo_link_authority_agent`
**Role:** Link & Authority Builder
**Discipline:** SEO

**Goal:**
Build domain authority through legitimate, relevant inbound links from
authoritative sources in target country and regions. Authority signals
from backlinks are the primary lever for competitive organic ranking
where content quality is otherwise equal.

**Inputs:** domain_recommendation, site_architecture_map,
serp_landscape_per_region, engagement_context

**Link Strategy Framework:**
- Local relevance > domain authority for regional pages
  (a link from a Riverside community site outweighs a generic DA50 blog)
- Anchor text diversity — branded, partial match, naked URL, generic
- Never manufacture links — identify genuine opportunities only
- Regional pages should earn links from regional sources

**Opportunity Categories:**
- Local business directories (feeds Agent 04 pipeline)
- Regional press and news outlets
- Industry associations and trade bodies
- Complementary local businesses (non-competing)
- Sponsorships and community involvement
- Resource page link placements

**Outputs:** link_opportunity_report, outreach_brief_per_region

**Handoffs To:** Orchestrator (authority signals inform AEO citation likelihood)

---

### Agent 06 — AEO Content Structure Agent

**ID:** `aeo_content_structure_agent`
**Role:** Answer-Optimised Content Specialist
**Discipline:** AEO

**Goal:**
Restructure and augment page content so it is citable by AI answer engines
(Google AI Overviews, Perplexity, ChatGPT, Bing Copilot). AEO is won by
providing clear, structured, authoritative answers to specific questions —
not by keyword density. This agent works on content produced by Agent 02
and adds the AEO layer.

**Inputs:** regional_page_content (from Agent 02), keyword clusters,
common user questions per region, engagement_context

**AEO Principles:**
- Answer the question in the first sentence of each section
- Use direct declarative statements, not hedged marketing language
- Structure content with clear H2/H3 hierarchy matching question intent
- FAQ blocks must be in genuine Q&A format with concise answers
- Avoid jargon — AI engines cite plain-language answers more frequently
- Include data, statistics, or specifics where available (increases citability)
- Content must be accurate and verifiable — AI engines deprioritise
  unverifiable claims

**Content Patterns That Win AEO:**
- "What is [service] in [region]?" → Direct definitional answer, 40–60 words
- "How much does [service] cost in [region]?" → Price range with context
- "How do I find [service] near me?" → Step-by-step, no fluff
- "What should I look for in a [service] provider?" → Numbered criteria list

**Outputs:** aeo_optimised_content_per_page, faq_block_per_region,
aeo_content_audit (gap analysis vs current content)

**Handoffs To:** 07 (schema entity — FAQ content feeds FAQPage schema)

---

### Agent 07 — AEO Schema & Entity Agent

**ID:** `aeo_schema_entity_agent`
**Role:** Schema & Entity Markup Specialist
**Discipline:** AEO / GEO

**Goal:**
Implement structured data markup (Schema.org) across all pages to make
the site's entities, services, and locations machine-readable by search
engines and AI systems. Schema is the bridge between SEO content and
AEO/GEO entity recognition.

**Inputs:** site_architecture_map, regional_page_content, faq_block_per_region,
local_entity_signal_checklist, engagement_context

**Required Schema Types Per Page:**

| Page Type | Schema Types Required |
|-----------|----------------------|
| Root homepage | Organization, WebSite, SiteLinksSearchBox |
| Regional landing page | LocalBusiness (or Service), BreadcrumbList |
| Regional page with FAQ | LocalBusiness + FAQPage |
| Service detail page | Service, Offer, AreaServed |
| Contact/about page | Organization, ContactPoint |

**Key Schema Fields (LocalBusiness):**
- `@type`: Most specific applicable type (e.g. HomeAndConstructionBusiness)
- `name`: Exact match to NAP name
- `url`: Canonical regional page URL
- `telephone`: +44 format
- `address`: PostalAddress with all sub-fields
- `areaServed`: Array of region names / GeoCircle / GeoShape
- `openingHours`: Per-day format
- `sameAs`: Array of GBP URL, social profiles, Wikidata ID (if exists)

**GEO Crossover — `sameAs` Property:**
The `sameAs` field is the primary bridge to GEO. Linking to Wikidata,
Wikipedia, and authoritative directory profiles tells Google's Knowledge
Graph that your entity and these external entities are the same thing.
This is how knowledge panels are triggered.

**Outputs:** schema_markup_per_page (JSON-LD blocks),
schema_validation_report, entity_disambiguation_brief

**Handoffs To:** 08 (GEO knowledge graph — entity brief feeds graph strategy)

---

### Agent 08 — GEO Knowledge Graph Agent

**ID:** `geo_knowledge_graph_agent`
**Role:** Knowledge Graph & Entity Specialist
**Discipline:** GEO

**Goal:**
Establish the business as a clearly disambiguated entity in Google's
Knowledge Graph and Wikidata. Entity presence is the foundation of GEO —
AI assistants answer location-based questions by querying entity graphs,
not crawling pages. If your business is not a recognised entity, it
cannot be surfaced in conversational AI results.

**Inputs:** entity_disambiguation_brief (from Agent 07),
domain_recommendation, nap_consistency_report, engagement_context

**Entity Establishment Process:**
1. Check for existing Wikidata entity (search by business name + location)
2. If absent and business meets notability threshold → create Wikidata entry
3. Link all authoritative external profiles via `sameAs` (GBP, Companies House, etc.)
4. Ensure Wikipedia criteria are met before attempting article creation
   (most local businesses do not qualify — do not fabricate notability)
5. Verify Google Knowledge Panel existence — if absent, flag for manual
   claim process after entity signals are established

**Notability Threshold for Wikidata:**
- Has a GBP listing with reviews
- Listed in 3+ Tier 1/2 directories
- Has been mentioned in regional press
- Has a functional website with schema markup

**GEO Signal Stack:**
- Wikidata entity with all properties populated
- `sameAs` links across schema markup, GBP, and directories
- Consistent entity name across all surfaces
- Google Knowledge Panel (outcome, not direct input — earned through signals)

**Outputs:** entity_establishment_report, wikidata_entry (if created),
knowledge_panel_status, geo_signal_gap_report

**Handoffs To:** 09 (geo local presence — entity signals feed local AI surfaces)

---

### Agent 09 — GEO Local Presence Agent

**ID:** `geo_local_presence_agent`
**Role:** Local Discovery & AI Surface Specialist
**Discipline:** GEO

**Goal:**
Ensure the business surfaces correctly when users query AI assistants
(ChatGPT, Perplexity, Siri, Google Assistant, Alexa) with location-based
or service-based conversational queries. GEO local presence is the
convergence of all entity, citation, schema, and GBP signals into
consistent AI-surfaced answers.

**Inputs:** entity_establishment_report, nap_consistency_report,
gbp_status (from Agent 10), schema_markup_per_page, engagement_context

**GEO Local Surface Checklist:**
- [ ] Business appears in ChatGPT responses for [service] in [region]
- [ ] Business appears in Perplexity responses for [service] near [region]
- [ ] Business surfaces in Google Assistant responses for 'near me' queries
- [ ] Apple Maps listing complete and accurate
- [ ] Bing Places listing mirrors GBP data exactly
- [ ] Siri Suggestions (via Apple Maps) enabled

**Query Test Matrix (run per region):**
- "Find me a [service] in [region]"
- "Best [service] near [region]"
- "Who provides [service] in [region]?"
- "I need [service] near me" (run with device location set to region)

**Gap Resolution:**
- Missing from AI surface → audit entity signals, check `sameAs` chain
- Wrong information surfaced → identify conflicting NAP signal, correct at source
- Competitor surfaced instead → assess their entity signal stack vs ours, escalate to Agent 08

**Outputs:** geo_surface_audit_per_region, gap_resolution_actions,
ai_surface_presence_report

**Handoffs To:** 11 (performance reporting — GEO surface data feeds dashboard)

---

### Agent 10 — GBP Management Agent

**ID:** `gbp_management_agent`
**Role:** Google Business Profile Specialist
**Discipline:** SEO / GEO

**Goal:**
Create, optimise, and maintain Google Business Profile listings for each
target region. GBP is the single highest-leverage action for local pack
(map) visibility and 'near me' search dominance. It is position one for
local intent queries — above organic results.

**Inputs:** target_regions, local_entity_signal_checklist,
domain_recommendation, engagement_context

**GBP Optimisation Checklist Per Region:**
- [ ] Business name exactly matches NAP name
- [ ] Primary category correctly set (most specific available)
- [ ] Secondary categories added where applicable
- [ ] Service areas set to each target region explicitly
- [ ] Description written with service + region signals (no keyword stuffing)
- [ ] Opening hours complete and accurate
- [ ] Phone number in +44 format
- [ ] Website URL points to correct regional subfolder
- [ ] Photos: minimum 10 (exterior, interior, team, service in action)
- [ ] Products/Services section fully populated
- [ ] Q&A section seeded with common questions + answers
- [ ] Posts: initial post published at launch

**Ongoing Maintenance (feeds performance loop):**
- Review response cadence: within 48 hours
- Monthly posts minimum
- Photo refresh quarterly
- Monitor for GBP spam / competitor listing violations

**Outputs:** gbp_setup_report_per_region, gbp_optimisation_checklist,
ongoing_maintenance_schedule

**Handoffs To:** 09 (GBP status feeds GEO local presence audit)
                 11 (GBP performance metrics feed reporting)

---

### Agent 11 — Performance Reporting Agent

**ID:** `performance_reporting_agent`
**Role:** Search Performance Analyst
**Discipline:** All (SEO + AEO + GEO)

**Goal:**
Measure the roster's performance against defined KPIs across all three
disciplines. Produce reporting that the orchestrator uses to make
rebalancing decisions and trigger LEARN phase. This agent closes the
Goal→Plan→Act→Review→**Learn** loop.

**Inputs:** All agent outputs, engagement_context, baseline SERP data
(from Agent 01 PLAN phase), performance_indicators (from orchestrator)

**Reporting Cadence:**
- Day 30: Initial baseline report
- Day 60: First performance comparison
- Day 90: Full cycle review — feeds LEARN phase
- Ongoing: Monthly

**KPI Framework:**

| Discipline | KPI | Target Signal |
|------------|-----|---------------|
| SEO | Organic position per region | Position 1–3 within 90 days |
| SEO | Local pack presence | Map pack for all regions within 60 days |
| SEO | Organic CTR per regional page | Baseline → improvement trend |
| SEO | Domain authority delta | Month-on-month increase |
| AEO | AI Overview citation rate | Cited in 1+ AI Overview per region |
| AEO | Featured snippet ownership | Target FAQ questions |
| GEO | Knowledge panel presence | Confirmed panel within 90 days |
| GEO | AI surface appearance rate | All major AI assistants within 90 days |
| GEO | 'Near me' traffic share | Month-on-month increase |

**LEARN Phase Outputs:**
- Performance delta report (baseline vs current per KPI)
- Underperforming agents flagged with hypothesis for cause
- Version bump recommendation (PATCH / MINOR / MAJOR) with rationale
- Updated engagement_log entry

**Handoffs To:** Orchestrator (LEARN phase brief triggers version review)

---

## Toolbox

### Toolbox Version: `v1.0.0`
### Toolbox Scope: `roster-seo` — applicable to all agents in this roster

---

### Tool Category 1: SERP Analysis

| Tool | Purpose | Agents | API/Integration |
|------|---------|--------|----------------|
| **Google Search Console** | Canonical performance data — impressions, clicks, position, CTR by query and page | 01, 03, 11 | OAuth2 / Search Console API v3. Requires site verification. Free. |
| **SEMrush** | Keyword research, competitor SERP analysis, position tracking | 01, 05, 11 | RESTful API. Paid (Guru+ for full API access). Key endpoint: `/analytics/v1/` |
| **Ahrefs** | Domain authority, backlink analysis, keyword gap | 01, 05, 11 | APIv3 (subscription required). Key endpoints: `/site-explorer`, `/keywords-explorer` |
| **DataForSEO** | Programmatic SERP scraping — real-time position data per region | 01, 11 | RESTful JSON API. Pay-per-use. Preferred for regional position tracking at scale. Key endpoint: `/serp/google/organic/live/advanced` |
| **BrightLocal** | Local SERP tracking, citation auditing, GBP rank tracking | 04, 10, 11 | REST API. Paid. Key use: local pack rank tracking per postcode. |

---

### Tool Category 2: Technical SEO

| Tool | Purpose | Agents | API/Integration |
|------|---------|--------|----------------|
| **Screaming Frog SEO Spider** | Full site crawl — broken links, redirect chains, canonical issues, meta data | 03 | Desktop app + API mode. Free up to 500 URLs. Paid for full crawl + scheduling. |
| **Google PageSpeed Insights** | Core Web Vitals — LCP, FID/INP, CLS per page | 03 | Google PageSpeed Insights API v5. Free. Key endpoint: `/pagespeedonline/v5/runPagespeed` |
| **Sitebulb** | Visual crawl reporting, crawl depth analysis, structured data validation | 03 | Desktop app. No public API — outputs to CSV/JSON for agent consumption. |
| **Cloudflare** | CDN, page speed, HTTPS, DDoS — infrastructure layer | 03 | Cloudflare API v4. Free tier available. Key use: cache rules, SSL status. |

---

### Tool Category 3: Schema & Structured Data

| Tool | Purpose | Agents | API/Integration |
|------|---------|--------|----------------|
| **Google Rich Results Test** | Validate schema markup for rich result eligibility | 07 | Available as API via Search Console. Also UI at search.google.com/test/rich-results |
| **Schema.org Validator** | Syntax validation of JSON-LD blocks | 07 | validator.schema.org — no API, UI only. Integrate via headless browser automation. |
| **Merkle Schema Markup Generator** | Generate LocalBusiness, FAQ, Service schema templates | 07 | No API — template output. Use as reference for agent schema generation. |
| **Google Knowledge Graph Search API** | Query Knowledge Graph for entity disambiguation and existence check | 07, 08 | Google KG Search API. Free with API key. Key endpoint: `/kgsearch/v1/entities:search` |

---

### Tool Category 4: Local SEO & Citations

| Tool | Purpose | Agents | API/Integration |
|------|---------|--------|----------------|
| **BrightLocal Citation Builder** | Submit and manage NAP citations across UK directories | 04 | BrightLocal API. Paid. Supports bulk submission + audit. |
| **Yext** | Centralised NAP management across directories — single source of truth | 04 | Yext Knowledge API. Paid (enterprise pricing). Best for scale (10+ locations). |
| **Whitespark** | Citation finder — identifies missing directory opportunities by region | 04 | Manual tool + citation service. No public API. Use outputs as agent input. |
| **Google Business Profile API** | Programmatic GBP management — create, update, read listings | 10 | Google My Business API (OAuth2). Free. Key endpoints: accounts, locations, reviews. |
| **Apple Maps Connect** | Apple Maps listing management | 09, 10 | Apple Maps Connect web UI. No public API — manual submission or via data aggregators. |

---

### Tool Category 5: AEO & AI Surface Monitoring

| Tool | Purpose | Agents | API/Integration |
|------|---------|--------|----------------|
| **Google Search Console (AI Overviews)** | Track AI Overview impressions and clicks (where reported) | 06, 11 | Search Console API v3. AI Overview data partially available in Performance report. |
| **Perplexity API** | Test how Perplexity surfaces answers for target queries | 09, 11 | Perplexity API (pplx-api). Paid per query. Use for automated surface testing. |
| **OpenAI API** | Test ChatGPT response to target queries for entity/brand appearance | 09, 11 | OpenAI Chat Completions API. Paid per token. Model: gpt-4o for consistency. |
| **SE Ranking** | AI Overview tracker — monitors which queries trigger AI Overviews | 06, 11 | SE Ranking API. Paid. Key use: AEO opportunity identification. |
| **AlsoAsked** | Maps 'People Also Ask' and question clusters — AEO content opportunities | 06 | AlsoAsked API. Paid. Key endpoint returns question tree per seed query. |

---

### Tool Category 6: GEO & Knowledge Graph

| Tool | Purpose | Agents | API/Integration |
|------|---------|--------|----------------|
| **Wikidata API** | Query, create, and update Wikidata entity entries | 08 | Wikidata REST API + MediaWiki Action API. Free. Key endpoint: `/w/api.php` |
| **Google Knowledge Graph Search API** | Confirm entity existence and MID (Machine ID) in Knowledge Graph | 08 | Google APIs. Free. Requires API key. |
| **Diffbot** | Extract and monitor entity data across the web — GEO signal auditing | 08 | Diffbot Knowledge Graph API. Paid. Key use: entity presence monitoring across web. |
| **Kalicube Pro** | Knowledge panel monitoring and entity optimisation platform | 08, 09 | Kalicube API (limited public access). Primary use: knowledge panel tracking. |

---

### Tool Category 7: Analytics & Reporting

| Tool | Purpose | Agents | API/Integration |
|------|---------|--------|----------------|
| **Google Analytics 4** | Traffic, user behaviour, regional page performance | 11 | GA4 Data API (formerly Reporting API). OAuth2. Free. Key report: landing page by region. |
| **Looker Studio** | Dashboard — consolidates GSC, GA4, and rank tracking into orchestrator view | 11 | Looker Studio connectors for GSC and GA4 are native. BrightLocal connector available. |
| **DataForSEO** | Programmatic rank tracking — position per query per region, scheduled | 11 | See Category 1. Dual use: analysis (Agent 01) and ongoing tracking (Agent 11). |

---

## Engagement Flow Diagram

```
ORCHESTRATOR (00)
│
├── FIRES: Agent 01 (Architecture)
│         └── Outputs: domain, structure, entity checklist
│
├── FIRES PARALLEL after Agent 01:
│   ├── Agent 02 (Content)
│   │   └── Outputs: regional pages, FAQ blocks
│   ├── Agent 03 (Technical)
│   │   └── Outputs: audit, implementation checklist
│   ├── Agent 04 (Citations)
│   │   └── Outputs: NAP report, directory submissions
│   └── Agent 10 (GBP)
│       └── Outputs: GBP listings per region
│
├── FIRES after Agent 02:
│   ├── Agent 05 (Link Authority)
│   └── Agent 06 (AEO Content)
│       └── Outputs: AEO-optimised content, FAQ blocks
│
├── FIRES after Agent 03 + 06:
│   └── Agent 07 (Schema & Entity)
│       └── Outputs: schema markup, entity brief
│
├── FIRES after Agent 07:
│   └── Agent 08 (Knowledge Graph)
│       └── Outputs: entity establishment, Wikidata
│
├── FIRES after Agent 04 + 08 + 10:
│   └── Agent 09 (GEO Local Presence)
│       └── Outputs: AI surface audit, gap actions
│
└── FIRES at Day 30 / 60 / 90:
    └── Agent 11 (Performance Reporting)
        └── Outputs: KPI report, LEARN phase brief
              └── → ORCHESTRATOR: version bump recommendation
```

---

## Cross-Roster Collaboration — roster-appdev

Declared per `framework-architecture` v1.1.0. All routes run **via the ECL
Orchestrator** (lateral flow rule) — never as direct agent-to-agent handoffs
across rosters. On the App Dev side, incoming SEO outputs enter as confirmed
requirements through `analysis_business_analyst_agent` and are sequenced by
the App Dev orchestrator like any other engagement input.

### Outbound (SEO → App Dev)

| SEO producing agent | Output | App Dev consumption |
|--------------------|--------|---------------------|
| `seo_search_architecture_agent` (01) | `site_architecture_map` | Architecture input — the build must implement and preserve this URL structure |
| `seo_technical_agent` (03) | `implementation_checklist` | Requirements backlog — Agent 03 "specifies for a developer"; App Dev is that developer |
| `aeo_schema_entity_agent` (07) | `schema_markup_per_page` + placement spec | Requirements backlog — JSON-LD implemented by App Dev front-end/back-end |

### Inbound (App Dev → SEO)

| App Dev event | SEO action |
|---------------|-----------|
| Release changes site structure, routing, or URLs | ECL Orchestrator notifies this roster's orchestrator → cascade review; `site_architecture_map` conformance check; MINOR bump if structure changed |
| Release materially changes page performance (Core Web Vitals) | `seo_technical_agent` re-audit; feeds SEO-03/performance KPIs |
| Shared analytics instrumentation updated (`instrumentation_spec` from `insight_business_analytics_agent`) | `performance_reporting_agent` aligns its GA4/measurement sources — one measurement source, two reporting views |

### Precedence rule

On URL structure and site architecture, `seo_search_architecture_agent`'s
confirmed `site_architecture_map` takes precedence — App Dev must not
restructure routes without an SEO cascade review. On implementation
feasibility and delivery sequencing, the App Dev orchestrator's ADR and
pipeline gates take precedence — SEO checklists arrive as requirements,
not as direct instructions to App Dev engineers. Conflicts are resolved
by the ECL Orchestrator against current objectives.

---

## Performance Indicators → Version Bump Map

| Indicator | Threshold | Action | Version Bump |
|-----------|-----------|--------|--------------|
| Regional page not in top 10 after 90 days | Any region | Review Agent 02 content + Agent 05 authority strategy | PATCH |
| Local pack absent after 60 days | Any region | Escalate Agent 10 + 04 | PATCH |
| AI Overview citation absent after 90 days | Any region | Review Agent 06 + 07 outputs | PATCH |
| Knowledge panel absent after 90 days | Business level | Full Agent 08 re-audit | PATCH |
| New region added to scope | — | New regional pages + GBP + citations | MINOR |
| New AI surface emerges (e.g. new LLM assistant) | — | Add to Agent 09 test matrix + toolbox | MINOR |
| AI Overviews displace organic position one for >50% of target queries | — | Rebalance roster — AEO becomes primary discipline | MAJOR |
| Google algorithm update materially changes ranking factors | — | Full orchestrator strategy review | MAJOR |

