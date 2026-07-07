# Delivery Plan — riverside-bookings

**Version:** v1.0.1
**Owner:** delivery_project_manager_agent
**Status:** awaiting approval (DQ-004)

## 1. Scope

Brownfield rebuild of the website booking application. Preserve the live
booking channel and the QR-code gate integration throughout.

## 2. Wave sequence

1. **w1-plan** — delivery plan + RAID log
2. **w2-analysis** — business analysis, requirements backlog
3. **w3-design** — solution design + ADR
4. **w4-frontend** — front-end rebuild
5. **w5-backend** — back-end + booking-provider integration (REDISPATCH after w5 silent death)
6. **w6-security** — security review + gate
7. **w7-qa** — QA sign-off
8. **w8-release** — release + cutover
9. **w9-reporting** — instrumentation + first report

## 3. Exclusions

- Dynamic pricing (GAP-001) — owner exclusion zone, out of scope.
- No new SaaS spend without owner sign-off (RAID R7).
- Pricing configuration writes are policy-blocked (see INT-00005).

## 4. Gates

Each wave exits through its gate. Security and QA gates require human sign-off
via the Decision Inbox before the release wave fires.

## 5. Change log

- v1.0.1 — resequenced w5-backend for redispatch after the kernel detected a
  silent death; added explicit policy-block note for pricing writes.
