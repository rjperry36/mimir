# Security Review Report — riverside-bookings

**Version:** v1.0.0
**Owner:** security_infosec_manager_agent
**Gate result:** FAILED (blocks w8-release)

## Findings

| ID | Severity | Finding | Status |
|----|----------|---------|--------|
| S1 | HIGH | CI secret-scan gate not wired into the pipeline | OPEN |
| S2 | HIGH | Missing Content-Security-Policy header on booking routes | OPEN |
| S3 | MEDIUM | Pricing configuration write attempted (exclusion zone) — policy-blocked | ROUTED TO OWNER |

## Recommendation

Do not release. Wire the secret-scan gate and add the CSP header, then
re-run the security gate. S3 is an owner decision (see Decision Inbox DQ-003).

## BYOK note

No credentials appear in this report or in any emitted ledger. Any key value is
redacted to last-4 by `runtime/credentials.py::mask` before it can reach a log.
