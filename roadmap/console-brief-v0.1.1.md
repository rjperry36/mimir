# Framework Console — Seed Brief
**Document ID:** `console-brief`
**Version:** `v0.1.1 (draft — owner-originated requirements, pre-engagement)`
**Created:** 2026-07-04
**Author:** Russ Perry (requirements) + runtime (mapping)
**Status:** Input to engagement #2 (roster-appdev builds the Console). Build starts
only after pilot close-out + ASA verdict + mutual process approval.
**Positioning:** NOT a chat UI. A dashboard / visibility / decision system for the
human operator of the agent framework.
**Revision note:** v0.1.1 — Patch — privacy scrub: genericised the worked example (booking/payment vendors named generically); no rule or behaviour change.

---

## Owner's user-journey requirements (verbatim starting point)

1. Describe the wave statuses
2. Agent metrics in a timeline
3. Agents to show learning and efficiency over time — "I would expect the agents to get better over time"
4. Log of any errors, hallucinations and whatever else is useful
5. Approval system
6. RAG (Red/Amber/Green status — interpreted per UK PM convention, paired with RAID; confirm)
7. RAID
8. **Document review & approval surface** (added 2026-07-06) — every document/artifact an
   agent produces is viewable in the dashboard, clearly rendered for the user to READ, with
   inline **Approve / Comment / Save** actions. This is the human-gate interface: the gates the
   framework already enforces (ECL sign-off, pre-flight, release, bump approvals) surface here as
   readable documents with a one-click decision + comment thread, and the decision writes back to
   the engagement log + decisions-queue. Markdown/YAML rendered readably; diffs shown for version
   bumps; comments captured against the artifact + version.

---

## Mapping: each view → its data source (what exists vs what's missing)

| # | Console view | Data source that EXISTS today | Instrumentation MISSING (add at close-out) |
|---|--------------|-------------------------------|--------------------------------------------|
| 1 | **Wave board** — per engagement: waves as swim-lanes, status (pending/running/gate-blocked/complete/failed), current agent, gate results | `engagement-log.yaml` (every dispatch/completion/gate event is already logged) | A structured `wave-status.yaml` per engagement (machine-readable state, not prose log entries) written by the runtime on every transition |
| 2 | **Agent metrics timeline** — per run: tokens, duration, tool calls, gate pass/fail, defects found / defects caused, rework loops | Subagent usage is reported per run (tokens/tool_uses/duration) but only in chat notifications — NOT persisted | A `metrics-ledger.yaml` appended per agent run: agent_id, agent_version, engagement, wave, tokens, duration_ms, tool_uses, gates_passed/failed, defects_found, defects_attributed, rework_count |
| 3 | **Learning & efficiency over time** — the "agents get better" view | `learning-log.yaml` (13 entries so far), `learnings.yaml` (memory), version-bump history per agent in manifest + changelogs | Nothing structural — but see HONEST NOTE below: plot metrics BY AGENT VERSION so improvement is attributable to specific LEARN→bump cycles, not assumed |
| 4 | **Integrity log** — errors, fabrication/hallucination events, gate failures, policy blocks | Fabrication audit reports (3 in pilot), gate-failure log events, validator CI results, blocked-dependency events | A structured `integrity-register.yaml`: every fabrication-audit finding, gate failure, validator error, and policy denial as typed entries (severity, agent, artifact, resolution) — currently these live in prose reports |
| 5 | **Decision inbox** — the approval system: every item awaiting the human, gate-shaped (context, options, deadline per AOM timeouts, one signature) | Gates exist in process (ECL sign-off, pre-flight, release override, exclusion zones, bump approvals) and land in the engagement log after the fact | A `decisions-queue.yaml`: open items with AOM timeout clocks, so the inbox shows "3 awaiting you, oldest 26h, breach in 22h" — this is also what client_account_manager_agent chases from |
| 6 | **RAG status** — Red/Amber/Green per engagement and per domain (Finance/Sales/Marketing... from the ECL's KR statuses) | ECL key results already carry status (on-track/at-risk/off-track = G/A/R); performance/insight reports score KPIs | A roll-up rule (worst-of vs weighted) defined once in the ECL cycle protocol; computed deterministically — no AI needed |
| 7 | **RAID board** — risks/assumptions/issues/dependencies across engagements | `raid-log.yaml` per engagement (already structured YAML, already maintained by the PM agent) | Nothing — render it. Cross-engagement roll-up only |
| 8 | **Document review & approval surface** — read any agent artifact clearly; Approve / Comment / Save inline; version diffs for bumps | Every artifact is a markdown/YAML file in the instance; gates already exist in-process; decisions-queue (view #5) tracks what's pending | A readable renderer (markdown/YAML → clean HTML, diff view for versioned docs) + an approval-action writer that appends the decision + comment to the engagement log and clears the decisions-queue item. Deterministic; the only AI (optional, later) is a per-doc summary. This IS the human-gate UI. |

## Honest note on requirement #3 ("agents get better over time")

Agents do not improve implicitly — no weights change between runs. Improvement in
this framework happens through exactly three mechanisms, all already built:
1. **Definition changes** — LEARN entries → version-bump proposals → PATCH/MINOR
   bumps to the agent YAML (the definition IS the memory of record)
2. **Memory** — `learnings.yaml` distillation loaded at kickoff (client-specifics
   + what-works/what-fails)
3. **Better inputs** — improved briefs, templates, and upstream artifact quality

Therefore the Console must plot metrics **by agent version**, annotated with bump
events, so "getting better" is a measurable, attributable claim (e.g. "BA v1.0.3
produces 40% fewer open-question round-trips than v1.0.1") rather than a hope.
Fair metrics require normalisation — first-pass gate success rate, defect escape
rate, rework loops per wave, and owner-turnaround-per-decision are the honest
quality signals; raw token counts vary with task size and mislead.

## Credentials — BRING-YOUR-OWN-KEY (BYOK) — OWNER SECURITY REQUIREMENT (2026-07-06)

This framework will be shared publicly on GitHub. **Nobody may ever use the
owner's API credentials.** Every user supplies their own. Non-negotiable rules
for the dashboard (and the runtime it drives):

- **A Credentials screen in the app UI** where the user enters their OWN keys:
  Anthropic/Claude API key (to run agents) and, per engagement, the client's
  own service keys (Vercel / Neon / Clerk / Resend / a booking provider / a payment provider).
- **Stored client-side / locally only** — browser localStorage or the user's own
  local `.env`/OS keychain. **Never** committed, never transmitted to any
  server the framework owner controls, never bundled.
- **No key values in the repo, ever** — `.gitignore` blocks `.env*`; only
  `.env.example` with placeholder NAMES is tracked; the existing CI secret-scan
  gate stays on and blocks any accidental key.
- **Redacted everywhere** — no key value in logs, emitted state
  (wave-status/metrics/integrity), error messages, or the UI beyond last-4.
- **Fail loud if absent** — if a user hasn't entered their key, the app tells
  them clearly and stops; it never falls back to a default or the owner's key.
- **BYOK banner** — the app states plainly: "You provide your own API keys.
  They stay on your device. The project ships with none."

This is the standard "bring your own key" model (like most open-source AI tools):
the code is shared; the keys are each user's own.

## Architecture posture (per SDK roadmap decision)

- Views 1, 5, 6, 7 are **pure deterministic rendering** of instance files — zero AI
- Views 2, 3, 4 are deterministic aggregation of the new ledgers — zero AI
- AI appears in the Console only as: links INTO agent artifacts, and (later,
  optional) a natural-language query over the audit trail. The dashboard itself
  is software, per the "prefer deterministic software" principle the ASA enforces
- Built on the default stack as roster-appdev engagement #2; single-operator v1;
  decision inbox is the core product, visualisation second

## Next actions (folded into close-out package)

- [ ] Add the four instrumentation artifacts (wave-status, metrics-ledger,
      integrity-register, decisions-queue) as templates + runtime obligations —
      MINOR framework bump, so data accumulates from the next engagement onward
- [ ] Retro-populate pilot metrics from the engagement log + notification records
      where recoverable (partial — token figures for completed waves exist)
- [ ] Confirm RAG interpretation with owner (Red/Amber/Green assumed)
- [ ] Console engagement #2 pre-flight after ASA verdict
