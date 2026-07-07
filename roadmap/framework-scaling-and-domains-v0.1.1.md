# Open Framework Questions — Scaling & Domain Taxonomy
**Document ID:** `framework-scaling-and-domains`
**Version:** `v0.1.1 (draft — owner-raised design questions, pre-decision)`
**Created:** 2026-07-06
**Raised by:** Russ Perry (owner) · **Status:** Backlog — design questions, not yet version bumps
**Related:** ASA-verdict-v1.0.0 (governance concentration, unexercised machinery findings);
engagement-lifecycle v1.0.0 (full/lite profiles); the proposed mandate/change-tolerance matrix.
**Revision note:** v0.1.1 — Patch — privacy scrub: genericised the worked example (real client business replaced with the fictional "Riverside Bookings"); no rule or behaviour change.

---

## Q1 — Justify or revise the nine functional domains

**The issue.** `ecl-framework-v1.0.0.md` §3 declares nine `[REQUIRED]` functional
domains (Finance, Sales & Revenue, Marketing, Operations, Product/Service,
Technology, HR & People, Legal & Compliance, AI Manager). The framework
**asserts** this taxonomy — it does not justify why nine, why these nine, or
why others (Customer/CX, Supply Chain, Data/Privacy, Risk, ESG, Investor
Relations, M&A) are absent. In the Riverside Bookings pilot several domains were
thin or mostly-TBC (HR at 1.5 people; Product/Technology/Legal carried more gaps
than substance) — evidence the fixed nine is heavier than an SME needs and
lighter than a corporate needs.

**Decision needed.** Either (a) document a defensible rationale for the nine (and
cite a source/model), or (b) revise to a **tier-dependent domain set** where the
required domains scale with engagement tier (see Q2). Current recommendation:
domains become tier-dependent, not a fixed nine.

**Add to the interview:** a "justify or revise domains" step — the interview
confirms which domains are live for THIS business rather than forcing all nine.

---

## Q2 — Does the framework scale, and do we need a business-size signal?

**Honest current state:** the methodology scales; the artifacts are SME-shaped
(one owner, one business, one ECL, single approver, manual runtime).

**Three axes of scale:**
- **Down (micro):** works; arguably over-heavy at the bottom.
- **Up in depth (bigger single business):** partial — breaks on single-approver
  governance (ASA finding) and manual runtime (concurrency).
- **Out (multi-entity / global):** NOT supported — assumes one business = one ECL.
  A global corporate needs an **ECL hierarchy** (Group → Division → Market/BU),
  which is a missing structure, not a tuning gap.

**The sizing signal — recommended as a multi-axis TIERING INSTRUMENT, not one number.**
"Size" (headcount/revenue) misleads; required depth is driven by complexity:

| Axis | Drives |
|------|--------|
| Regulatory / compliance load | Legal/Risk depth, approval gates, audit intensity |
| Business units / legal entities | ONE ECL vs an ECL hierarchy |
| Geographies / markets | Localisation, multi-market cascade |
| Data sensitivity | Security roster + data governance depth |
| Decision value at stake | Separation-of-duties / approval topology |
| Headcount | HR/People depth, cadence |

Answered at interview, **human-confirmed** (recommend a tier, human can override —
no auto-computed false precision). The tier deterministically sets:

1. **ECL depth** — required / optional / skipped domains (ties to Q1)
2. **Roster & agent set** — which rosters activate; lean vs full agents
3. **Cadence** — startup weekly vs corporate quarterly/board cycle
4. **Governance topology** — number of approvers, separation of duties, audit
   intensity (directly addresses ASA governance-concentration finding 4b)

**Proposed tier ladder** (replaces today's binary full/lite):

| Tier | Profile | ECL | Rosters | Governance |
|------|---------|-----|---------|------------|
| T0 | Micro / sole trader | 3–4 domains | 1, lean | Single owner |
| T1 | Small business (pilot sat here) | core domains | 1–2 | Owner + optional advisor |
| T2 | SME / multi-function | most domains | several | Owner + domain approvers |
| T3 | Mid-market / multi-BU | full + Risk/Data | many, multi-roster | Separation of duties, RBAC |
| T4 | Enterprise / global | **ECL hierarchy** | federated | Board/compliance approval topology |

---

## Design discipline (per ASA anti-sophistication warning)

- **Design** the tiering model + extension points now (don't block the path up).
- **Build** only the tiers actually served (SME/agency reality — T0–T2).
- **Reserve** T3–T4 (ECL hierarchy, RBAC, separation of duties, corporate domains)
  as a **documented future path — named and scoped, not coded.** Building enterprise
  multi-entity structures for clients not yet served would be the exact
  "unnecessary sophistication" the ASA flags.

## What genuinely needs NEW design before T3+ (not just tuning)

- **Nested / federated ECLs** — group→division→market objective cascade + upward
  consolidation. No current concept exists.
- **Role-based approval / separation of duties** — replaces the single-approver
  model (ASA finding 4b). Prerequisite for any regulated or multi-stakeholder org.
- **Tier-dependent domain taxonomy** (Q1) — corporate domains (Risk, ESG, IR, M&A,
  Data/Privacy) as first-class.
- **Runtime becomes mandatory** — manual crank cannot serve T3+ concurrency.

## SCOPE DECISION (owner, 2026-07-06): SME only — NOT global corporates

The framework's target market is confirmed as **small-to-large SME**. Tiers T3–T4
(mid-market multi-BU, enterprise/global, ECL hierarchy, RBAC, federated cascade)
are **explicitly OUT OF SCOPE** — retained in this document as a documented,
uncoded reservation only. Build effort focuses on:

- **Tier ladder T0 → T2** (micro → SME), replacing the binary full/lite.
- **Domains tuned for the SME range**, not a global spread — Q1 revision picks the
  SME-relevant domain set and justifies it; corporate domains (Risk/ESG/IR/M&A)
  are reserved, not implemented.
- **No nested/federated ECLs, no RBAC** — single-owner-plus-optional-approvers
  governance is sufficient for the SME range (the AOM constitutional-sign-off rule
  4.1.C already covers the apex-protection need).

This narrows Q1+Q2 to a tractable, in-scope piece of work.

## Status
Q1 + Q2 are linked and now SME-scoped. To be implemented in the framework-backlog
phase as: tier ladder (T0–T2) + tier-dependent SME domain set. T3–T4 reserved.
