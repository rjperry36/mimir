# Executive Command Layer — [Business Name]
**Business ID:** `[business-id]`  ·  **Version:** `v0.1.0 (draft)`  ·  **Status:** `Draft — awaiting human sign-off`
**Created:** [date]  ·  **Framework:** ecl-framework v1.0.0

> Populated by `ecl_interview_agent`. Every [TBC] item must carry a named
> owner in the gap report. Human sign-off versions this to v1.0.0 Active.

## 1. Business Identity [REQUIRED]
```yaml
business_id: ""
business_name: ""
business_type: ""        # SME / startup / enterprise / client
industry: ""
stage: ""                # pre-revenue / growth / scale / mature
geography: {primary_country: "", operating_regions: [], target_regions: []}
business_model: ""
primary_channels: []
```

### 1.2 North Star [REQUIRED]
```yaml
north_star: {statement: "", metric: "", current_baseline: "", target: "", horizon: ""}
```

### 1.3 Why / What / How / When [REQUIRED]
```yaml
why: ""
what: ""
how: ""
when: ""
```

## 2. Strategic Context [REQUIRED]
```yaml
swot: {strengths: [], weaknesses: [], opportunities: [], threats: []}
competitors: {direct: [], indirect: []}
target_operating_model:
  delivery_model: ""
  human_touchpoints: []
  automated_touchpoints: []
  technology_stack: []
  capacity_constraints: []
```

## 3. Functional Objectives [REQUIRED]
One block per domain — Finance, Sales, Marketing, Operations, Product,
Technology, HR & People, Legal & Compliance, AI Manager (full schemas in
ecl-framework Section 3):
```yaml
[domain]:
  domain_lead: ""
  cycle: ""
  baseline_metrics: {}
  objectives: [{objective: "", key_results: [{kr: "", target: "", current: "", status: ""}]}]
  cascade_triggers: [{condition: "", action: ""}]
```

## 4. Cascade Protocol — per ecl-framework Section 4
## 5. Roster Registry — see roster-registry.yaml
## 6. Cycle Cadence [REQUIRED]
```yaml
ecl_cycle:
  annual_review: {month: "", participants: []}
  h1_review: {month: ""}
  quarterly_reviews: [{quarter: "Q1", month: ""}, {quarter: "Q2", month: ""}, {quarter: "Q3", month: ""}, {quarter: "Q4", month: ""}]
  monthly_management_review: {scope: "KPI dashboard — Finance, Sales, Marketing, AI Manager"}
```

## Sign-off
| Role | Name | Date | Signature/Record |
|------|------|------|------------------|
| CEO / Business owner | | | |
