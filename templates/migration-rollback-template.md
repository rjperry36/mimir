# Migration & Rollback — [migration-id]
**Template version:** `v1.0`
**Owner:** engineering_database_agent · **ADR ref:** adr-[business-id]-[nn]

Lightweight per-migration record so every schema change ships with a tested
reverse path. Drizzle-kit (and similar) emit up-only migrations — the down and
the up→down→up CI test are authored here, not assumed.

## Naming convention
`[NNNN]_[verb]_[object].(up|down).sql` — zero-padded, monotonic, one concern per migration.

## Change summary
[What this migration does, and which domain entities/tables it touches]

## Data-loss note
- [ ] No data loss (additive / reversible)
- [ ] Data loss possible on rollback — describe what is lost and the mitigation (backup/export before apply):

## Up / Down
| Direction | File | Reversible? | Notes |
|-----------|------|-------------|-------|
| up | `[NNNN]_..._up.sql` | — | |
| down | `[NNNN]_..._down.sql` | | If not cleanly reversible, state why + the manual step |

## Journal-cleanup clause
[If the migration tool leaves a journal / snapshot artifact (e.g. drizzle `meta/`),
state how a rolled-back migration is removed from the journal so the tree stays truthful.]

## CI test — up → down → up
- [ ] Migration applied (up), reverted (down), and re-applied (up) in CI against a
      throwaway branch DB — all three green. A down that is not authored fails this gate.
