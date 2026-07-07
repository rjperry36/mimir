# Templates
**Version:** `v1.2.0` (templates version as a set — individual instantiations are versioned per instance)

Canonical templates for every recurring artifact in the framework.
`new-instance.sh` copies the instance-level ones at bootstrap; agents
reference the rest by name in their output specs. Editing a template is
a framework change — PATCH bump the template set via changelog below.

| Template | Used by | Purpose |
|----------|---------|---------|
| ecl-instance-template.md | ecl_interview_agent | Skeleton the interview populates to draft ECL |
| brand-kit-template.yaml | content_brand_steward_agent | Per-element brand change-tolerance spectrum (lock/refresh/open), posture, verified claims, accessibility |
| ecl-summary-card-template.md | ecl_orchestrator_agent | 1-page layered-context card agents load instead of the full ECL |
| roster-config-template.yaml | new-instance.sh | Per-instance roster configuration |
| preflight-checklist-template.md | ecl_orchestrator_agent + human | Engagement sizing: profile, team selection, gap analysis |
| cascade-briefing-template.md | ecl_orchestrator_agent | Version-bump cascade to roster orchestrators |
| handoff-brief-template.md | all agents | Self-contained agent-to-agent handoff |
| user-story-template.yaml | analysis_business_analyst_agent | Story + acceptance criteria (epic + blocking open-questions) |
| raid-log-template.yaml | delivery_project_manager_agent | Risks/Assumptions/Issues/Dependencies |
| adr-template.md | architecture_solution_design_agent | Architecture decision record |
| migration-rollback-template.md | engineering_database_agent | Migration naming, data-loss note, up/down/up CI test |
| integration-contract-template.md | architecture_solution_design_agent | External/device integration contract + credential lifecycle |
| performance-report-template.md | performance_reporting_agent | SEO/AEO/GEO KPI report |
| insight-report-template.md | insight_business_analytics_agent | Post-launch product/business outcome report |
| version-bump-proposal-template.yaml | all orchestrators / ai_manager_agent | AOM S4.2 bump proposal |
| override-log-entry-template.yaml | all agents | AOM S7.4 human override record |
| learning-log-entry-template.yaml | all agents (LEARN phase) | Single structured learning |
| learnings-memory-template.yaml | roster orchestrators / ai_manager_agent | Rolling distilled memory per roster per business |
| engagement-closeout-template.md | ecl_orchestrator_agent + human | Offboarding / close-out record |
| roster-genesis-proposal-template.yaml | ecl_orchestrator_agent + ai_manager_agent → human | Draft new-roster proposal per the Roster Genesis Protocol |

## Changelog
| Version | Date | Change |
|---------|------|--------|
| v1.0.0 | 2026-07-02 | Initial template set (16) |
| v1.1.0 | 2026-07-06 | PATCH (VBP-010): user-story gains epic + blocking-flag on open_questions; adr-template versioned (v1.1); added migration-rollback-template and integration-contract-template (credential-lifecycle). Set now 18 templates. |
| v1.2.0 | 2026-07-06 | MINOR (VBP-017): added brand-kit-template.yaml — per-element brand change-tolerance spectrum (lock/refresh/open), create/refresh/adhere posture, verified-claims set, accessibility requirements. New brand capability. Set now 19 templates. |
| v1.3.0 | 2026-07-06 | MINOR: added roster-genesis-proposal-template.yaml (Roster Genesis Protocol); preflight-checklist §4 gap analysis now routes through the protocol's right-sizing ladder. Set now 20 templates. |
