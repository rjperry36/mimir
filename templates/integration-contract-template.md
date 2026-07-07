# Integration Contract — [integration-id]
**Template version:** `v1.0`
**Owner:** architecture_solution_design_agent (specified) → security_infosec_manager_agent (reviewed)
**ADR ref:** adr-[business-id]-[nn]

Contract for an external/third-party or device integration. The architecture
specifies the credential lifecycle BEFORE security review — so credential
handling is a designed property, not a review-time discovery.

## Integration summary
- **Party / system:** [who/what we integrate with]
- **Direction:** [inbound / outbound / bidirectional]
- **Transport:** [HTTPS request/response / webhook / queue / persistent connection]
- **Contract surface:** [endpoints, payload schema ref, auth scheme]

## Credential lifecycle  (MANDATORY)
| Property | Specification |
|----------|---------------|
| Credential type | [API key / OAuth token / mTLS cert / signed shared secret] |
| Entropy floor | [minimum bits / generation method — no "6–8 char" convenience values; cite the source for any figure] |
| Storage | [reference only — env/secret store; never in repo or client bundle] |
| Rotation semantics | [rotation interval + overlap/grace window so rotation is zero-downtime] |
| Revocation | [how a leaked/retired credential is revoked immediately, and blast radius] |
| Scope / least privilege | [what the credential can and cannot do] |

## Failure & retry
[Timeout, retry/backoff, idempotency key, and the fail-safe default behaviour on outage]

## Security review sign-off
- [ ] Credential lifecycle complete and reviewed
- [ ] No secret values embedded anywhere (references only — AOM Section 6.4)
