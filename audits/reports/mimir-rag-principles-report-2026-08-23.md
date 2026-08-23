# Agentic Systems — Principles & RAG Status Report

| | |
|---|---|
| **System assessed** | Mimir — Organisational Intelligence Engine: `runtime/` kernel + Claude executor, `dashboard/` Console, and the constitutional + roster governance estate (35 agent specs, 6 constitutional documents) |
| **Date** | 2026-08-23 |
| **Basis** | [`audits/reports/mimir-agentic-assurance-audit-2026-08-23.md`](./mimir-agentic-assurance-audit-2026-08-23.md) |
| **Overall posture** | **FAIL as an agentic execution system** — 4 mandatory gates fail Critical, 6 Conditional. The governance methodology is genuinely strong; the engine that would execute it does not yet connect to it. |

Each principle below is explained in plain English, then rated. 🟢 Green means the control is implemented and evidenced. 🟠 Amber means it is defined but not proven, or partial. 🔴 Red means it is absent, or a mandatory release gate fails against it — a principle carrying a failed gate is Red no matter how well the surrounding work scores. Every Red and Amber carries one block per problem, with a priority and a remedy; Greens carry a single evidence line. **Priority key:** P0 before any further use · P1 before production · P2 during pilot · P3 improvement. Every problem here is the same item as in the audit's remediation plan — this is a re-presentation of that list, not a second one.

## Dashboard

| # | Principle | Rating | One-line status |
|---|---|---|---|
| 1 | Agentic justification & right-sized autonomy | 🟠 | The kernel is correctly deterministic; the agent it was built to contain does not exist in code |
| 2 | Goal & measurable outcome | 🔴 | Activity goal, no metric, no cost baseline — gate 1 Conditional Fail |
| 3 | Scope, authority & human oversight | 🟠 | The gate genuinely fails closed; approvals leave no record and the approve button is not connected |
| 4 | Planning & orchestration | 🟠 | Dependency scheduler is real and tested; no context passes between waves |
| 5 | Context, knowledge & provenance | 🔴 | The runtime assembles no context at all and verifies no claim — gate 9 Critical Fail |
| 6 | Tools, permissions & actions | 🔴 | No tools, no allowlist, no schema validation; the harness delegates this to "the integrator" |
| 7 | Harness fit & execution environment | 🔴 | Mandatory H3 absent, H1/H9 absent — real harness, no agent inside it |
| 8 | Review & verification | 🔴 | The model's output is discarded and `COMPLETED` returned anyway — gates 2 and 15 Critical Fail |
| 9 | Triggers, retries, stopping & escalation | 🟠 | Strongest area — stopping conditions are real and tested; escalations reach nobody |
| 10 | Evaluation & reliability | 🔴 | Zero agent evaluation; the only code that can reach a model has no tests — gate 12 Critical Fail |
| 11 | Safety & security boundaries | 🟠 | BYOK is genuinely clean; no injection controls, no trace policy, and a README claim that is false |
| 12 | Monitoring & incident response | 🔴 | No alerting, runbook, responder or kill switch — gate 13 Conditional Fail |
| 13 | Learning, change control & versioning | 🟢 | Semantic versioning, archived supersessions and a real validator enforced in CI |

**Score: 1 Green · 5 Amber · 7 Red.** Six of the seven Reds trace directly to the four Critical gate failures (2, 9, 12, 15), and all four have a single common root: the runtime and the governance estate are two products that share a repository and never call each other.

---

## 1. Agentic justification & right-sized autonomy — 🟠

**The principle.** Before asking whether an agent is well built, ask whether it should be an agent at all. Anything whose path and rules are known in advance — sequencing, permission checks, arithmetic, release gates — belongs in ordinary deterministic software, which is cheaper, faster and cannot be talked out of its own rules. Model-driven autonomy should be reserved for the parts that genuinely require judgement, and the amount of authority granted should match the amount of containment around it.

**Why Amber.** The judgement here is unusually good and the repo argues it explicitly: `runtime/gates.py:1-8` and `runtime/genesis.py:12-15` both state that this class of logic must be rule-based code, and it is. Sequencing, liveness, gating, budgets and state emission are all deterministic and tested. What stops this being Green is the inverse problem — the harness was built to contain a capable agent, and the agent is not there. A live run is a single text call with no tools and no persona (audit F1, F2), while `README.md` describes 35 specialist agents in four teams. This is not the usual "autonomy outgrew its containment"; it is containment built around an empty seat, with the documentation describing the occupant.

> **Problem:** The system is described at C4 autonomy and executes at C1.
> **Priority:** P0
> **Description:** `README.md` describes 35 agents in dependency-ordered waves; the executable path sends the wave ID as the entire prompt with no tools (`runtime/claude_executor.py:452`, probe B1). No live run has ever occurred anywhere. A reader — including a prospective client — would reasonably conclude the described system runs today.
> **Solution:** Add an accurate maturity banner to `README.md` stating that no live run has occurred and that the runtime does not yet execute agent specifications. Closure evidence: the banner, plus a single-sourced maturity table referenced by `README.md`, `runtime/README.md` and `site/what-its-not.html`.

---

## 2. Goal & measurable outcome — 🔴

**The principle.** A system needs a goal you can be wrong about. "Assist users" or "generate content" describe activity, not outcome — they can never be failed, so they can never be verified. A usable outcome states what changes in the world, by how much, by when, with a named owner and a baseline to compare against. Without one, nobody can tell progress from motion, and nobody can say whether the system is worth its cost.

**Why Red.** Mandatory gate 1 fails Conditional and gate 2 fails Critical. The stated aim — "specialist AI agent teams do the work, evidence every claim, and bring you decisions ready to sign" (`README.md:14-17`) — is an activity statement. No success criterion, threshold or unit is defined for the runtime, and `state.py` emits no outcome metric. The engagement layer does far better on paper (`constitutional/ecl-framework-v1.1.1.md` builds a manifesto with a North Star and per-domain objectives), but no code reads it. The project is candid about the consequence: the pilot's headline business metric "was un-measurable at day 14" (`site/what-its-not.html`).

> **Problem:** No measurable outcome exists for the system.
> **Priority:** P1
> **Description:** Nothing in `runtime/` defines or emits a success measure. `TerminationCause.COMPLETED` records that an API stream ended, not that anything was achieved. Without a target there is no basis for evaluation thresholds, escalation triggers, or a judgement on whether the system is working.
> **Solution:** Adopt a falsifiable outcome statement (audit section 3) and emit it to the metrics ledger — e.g. ≥95% of agent outputs pass their deterministic acceptance checks first time, ≥90% of factual claims resolve to a hash-verified evidence-locker ID, zero consequential actions without a logged approval, measured over ≥20 waves across ≥3 engagements.

> **Problem:** Cost per verified outcome is unknown and currently unmeasurable.
> **Priority:** P2
> **Description:** No model spend, human-review time or rework cost is tracked, and the budget guard counts waves rather than money (`runtime/kernel.py:185`, probe B4b — five waves reporting 25,000,000 tokens charged 5.0 of a ceiling of 10). No baseline exists for the human process being displaced, so even a corrected budget would not answer whether the system is worth running.
> **Solution:** Reconcile measured token and tool spend into the budget guard, express ceilings in currency, and capture a time-and-cost baseline for the equivalent human engagement. Closure evidence: a cost-per-completed-wave figure alongside the human baseline.

---

## 3. Scope, authority & human oversight — 🟠

**The principle.** An agent needs a written boundary: what it may do, what it must never do, what requires a human signature, and who is accountable when it goes wrong. Those boundaries have to be enforced by the surrounding software, not by asking the model nicely — a prompt instruction is a request, and a permission check is a control. Approvals must be impossible to skip, and every one must leave a record naming who approved what.

**Why Amber.** There is real, tested enforcement here and it deserves credit. The kernel's human gate fails closed: with no approver configured, a release wave sat at `AWAITING_APPROVAL`, its dependent was `BLOCKED`, and nothing was dispatched (probe B2). `runtime/genesis.py` cannot approve a new roster by construction — "There is no approve path in code" (`:14-15`) — so mandatory gate 11 passes. What holds this at Amber is that the *record* of approval is missing, the two halves of the approval loop never meet, and the authority matrix itself lives only in prose.

> **Problem:** Approvals are unlogged and unattributed; refusals are logged and approvals are not.
> **Priority:** P1
> **Description:** With `approver=lambda w: True`, a release wave completed with no `decisions-queue.yaml` entry, no integrity-register record and no approver identity anywhere (probe B3). The Console independently hardcodes `"decided_by": "local operator (dashboard)"` (`dashboard/server.py:312`), so `README.md`'s promise that "the audit trail shows every decision, who made it, and when" records a constant. This is exactly backwards for accountability.
> **Solution:** Write an integrity-register entry for every approval carrying approver identity, timestamp, the hash of the artefact approved, and the AOM authority reference. Closure evidence: probe B3 re-run showing a complete approval record.

> **Problem:** The Console's approve button is not connected to the runtime.
> **Priority:** P1
> **Description:** The kernel enqueues to `runtime-state/decisions-queue.yaml` and consults an in-process callable (`runtime/kernel.py:324-336, 319-322`); the Console writes `dashboard/local-store/decisions-log.jsonl` and a UI overlay (`dashboard/server.py:287-327`). Nothing reads either back. Today this is safe — the gate can never be passed in any shipped configuration — but it means the human-gate feature the product leads with does not exist end to end.
> **Solution:** One decisions store both sides read and write, with owner, SLA and the `aom_timeout_hours` already modelled in `runtime/genesis.py:27` actually enforced.

> **Problem:** `ai_manager_agent` holds autonomous governance-change authority, enforced only by prompt.
> **Priority:** P2
> **Description:** `agents/agent-ai-manager-v1.0.0.yaml:39-42` grants autonomous approval of PATCH bumps and lifecycle transitions, bounded by prose constraints. `scripts/validate_framework.py` checks schema and versions, not content — a PATCH bump rewriting an agent's `constraints` would pass CI. Latent today (no runtime writes to `agents/`), Critical the moment the runtime gains repo write access.
> **Solution:** Before any write path to `agents/`, `rosters/` or `constitutional/`: a diff-scope check in CI rejecting edits to `constraints`, `quality_gates` and authority fields without a human-signed decision record, plus CODEOWNERS on those paths.

---

## 4. Planning & orchestration — 🟠

**The principle.** Multi-step work needs a bounded plan: a sequence that respects dependencies, adapts when something fails, and stops at defined limits on steps, time and cost. Where several agents are involved, their roles must be genuinely distinct, their handoffs defined, and the context that matters must survive the journey between them — otherwise each step starts blind.

**Why Amber.** The orchestration that exists is real and well tested. `Kernel._topo_sort` is a stable topological sort that raises on cycles; dependency blocking correctly distinguishes a failed upstream gate from a dead upstream and attributes each accurately (`runtime/kernel.py:120-165`). Wave states, causes and transitions are emitted to auditable ledgers. What is missing is everything above the scheduler: there is no in-run planning (a wave is one single-shot call), and no context passes between waves — `WaveTask.payload` is declared at `runtime/executor.py:53` and populated by nothing, so a wave cannot receive the output of the wave it depends on.

> **Problem:** No context flows between waves; handoffs exist only on paper.
> **Priority:** P1
> **Description:** Every agent spec declares `inputs`, `outputs` and `handoffs`, and the validator checks they resolve (E12/E16) — but `runtime/kernel.py:171-172` constructs a `WaveTask` with no payload, so a downstream wave receives nothing from upstream. Combined with the discarded model output (principle 8), the dependency graph orders waves that cannot actually pass work to each other.
> **Solution:** Populate `payload` from the upstream waves' persisted outputs per the agent spec's declared `inputs`, and record the resolved input set in the metrics ledger. Closure evidence: a two-wave test asserting wave 2's prompt contains wave 1's artefact.

---

## 5. Context, knowledge & provenance — 🔴

**The principle.** An agent is only as good as what it knows. Approved sources should be defined, retrieved information should be current and relevant, and every fact should carry its provenance so a claim can be traced back to where it came from. Facts, assumptions and inferences must stay distinguishable; missing evidence must be reported as missing rather than filled in; and anything retrieved from an untrusted document must be treated as data, never as instructions.

**Why Red.** Mandatory gate 9 fails Critical. This is the principle Mimir markets hardest — "Non-fabrication, enforced by architecture" — and it is the one with the widest gap between claim and code. The total enforcement is `scripts/validate_framework.py:173`: a regular expression checking that the string `non-fabricat` appears somewhere in the agent's YAML file. The design behind it is genuinely thoughtful: the evidence locker records SHA-256 hashes per item, and I verified all three sample hashes recompute correctly (probe B7). But no code computes or checks them, and the runtime assembles no context at all — a live run sends `system=None` and the wave ID as the prompt (probe B1), so the manifesto, the locker and the non-fabrication rule never reach the model in the first place.

> **Problem:** The non-fabrication gate is a lint rule, not a control.
> **Priority:** P1
> **Description:** `scripts/validate_framework.py:173` greps for a word in a spec file. There is no runtime claim-checking anywhere in the repository. `README.md` states this is "enforced by architecture"; the architecture contains no enforcement.
> **Solution:** Implement it as executable code — extract claims from agent output, require each to cite an evidence-locker ID or manifesto field, verify the cited item's SHA-256 at read time, and strip-and-flag anything uncited. Closure evidence: proposed tests P2 and P3 passing (an altered locker file blocks the claim; an unavailable metric returns "cannot measure").

> **Problem:** The runtime assembles no context; the manifesto and locker never reach the model.
> **Priority:** P1
> **Description:** `runtime/claude_executor.py:452` sends `payload.get("prompt", wave_id)`, and nothing populates `payload`; `system_prompt` defaults to `""` and no shipped caller sets it. Probe B1 confirms a live run of `seo_architecture_agent` would send `system=None` and the literal string `"w1-seo-architecture"`.
> **Solution:** Build the agent-spec loader and prompt assembler: role, backstory and constraints into `system`; manifesto excerpt, locker index and wave brief into the user turn; record the assembled prompt's hash per run.

> **Problem:** Evidence-locker integrity is unverified by any code.
> **Priority:** P2
> **Description:** Hashes are recorded in `locker-index.yaml` and displayed by the Console (`dashboard/static/app.js:433`), but nothing computes or compares them. Tamper detection currently depends on nobody editing the files.
> **Solution:** Verify each item's hash on read, fail loud on mismatch, and record verification in the integrity register.

---

## 6. Tools, permissions & actions — 🔴

**The principle.** Tools are where an agent stops talking and starts acting, so each needs a stated purpose, validated input and output schemas, the narrowest permissions that work, and structured errors. Consequential or destructive actions need approval; repeated actions need protection against running twice; and every tool result must be treated as potentially wrong, incomplete or hostile — including the model's own output where something downstream consumes it.

**Why Red.** There are no tools. `client.messages.stream(...)` is called with no `tools=` argument (`runtime/claude_executor.py:454-460`), so the tool-use branch at `:467-472` is unreachable and the `tool_uses` counter is dead in the real path. The `tools:` blocks in all 35 agent specs are documentation with no runtime registry behind them. Mandatory gates 5 and 8 are Not Applicable today purely because no capability exists — and the harness explicitly hands off the control that would govern it: "wiring concrete tools is deployment-specific and intentionally left to the integrator" (`:350-354`). Genuine credit where due: `runtime/resilience.py` implements timeout, retry with backoff, fallback and a circuit breaker, all deterministic and covered by 224 lines of tests — it is real, and it currently wraps nothing but the API request.

> **Problem:** No tool registry, allowlist or schema enforcement exists — and the harness delegates it.
> **Priority:** P1
> **Description:** The first tool wired into this harness will land in an environment with no allowlist, no input/output schema validation, no separation of read from destructive tools, no idempotency, and no per-call logging. Gates 5 and 8 flip from Not Applicable to Critical at that moment, while `README.md` already implies the controls exist.
> **Solution:** Build the registry before the first tool: per-agent allowlist derived from the spec's `tools.required`, deterministic JSON-schema validation both directions, unknown or malformed calls rejected pre-execution, destructive tools requiring approval, idempotency keys on writes, every call logged to the integrity register, and every call routed through the existing `ResilientTool` wrapper. Closure evidence: proposed tests P5 and P8 passing.

---

## 7. Harness fit & execution environment — 🔴

**The principle.** The harness is everything around the model that holds regardless of what the model says: sandboxing, scoped credentials, tool allowlists, budget and step limits, checkpoints, approval gates, tracing, and a kill switch. The test is simple — a harness control still holds when the model emits the worst possible output. Anything that holds only because the prompt asked politely is a claim, not a control. The harness must match the system's complexity: too little and the agent outruns its containment; too much and you pay for machinery that reduces no risk.

**Why Red.** Assessed at C2 — the level the code is plainly built toward — a Mandatory capability is absent, which caps this area regardless of the rest. **H3 (tool exposure and schema enforcement) is absent** in both senses: no tool allowlist, and no deterministic schema validation of model output. **H1 (containment) is absent** — `runtime/isolation.py` allocates directories and port numbers, which is collision avoidance rather than a security boundary, and the real transport ignores the workspace entirely. **H9 (kill switch) is absent** — `cancel()` sets a flag the worker only notices on the next stream event, so a genuinely hung request is never interrupted and in-flight spend does not stop. H2, H6, H7, H8 and H10 are all partial. What is present is real: H5 checkpoint/resume is implemented and tested, H8 emits four correlated ledgers with atomic writes, and H2's BYOK layer is clean and tested. The misfit is inverted — the containment is real and the agent it contains is not.

> **Problem:** Mandatory H3 is absent: no schema enforcement on model output.
> **Priority:** P1
> **Description:** `AnthropicMessagesTransport._output` is initialised `{}` at `runtime/claude_executor.py:400` and never assigned; `poll()` returns it empty (`:492`). Nothing validates what the model produced because nothing retains it. For an AI-assisted workflow, output-schema enforcement is the harness's central job.
> **Solution:** Persist the response, validate it against a per-agent output schema deterministically, and map a schema failure to a gate failure rather than to `COMPLETED`.

> **Problem:** No kill switch; cancellation does not stop in-flight spend.
> **Priority:** P1
> **Description:** `close()` sets `self._closed`, which the worker thread observes only when the next stream event arrives (`runtime/claude_executor.py`, `_one_request` loop). A silently hung request is never interrupted, and there is no named mechanism to stop the system or revoke its credentials independently of deployment.
> **Solution:** A hard-cancellation path (the `run_with_hard_timeout` watchdog already in `resilience.py` is the building block), plus a documented and tested kill switch and credential-revocation procedure. Closure evidence: proposed test P12.

> **Problem:** Budget enforcement uses the wrong unit.
> **Priority:** P1
> **Description:** `runtime/kernel.py:185` charges the declared static `est_cost` regardless of consumption. Probe B4b: five waves reporting 25,000,000 tokens charged 5.0 against a ceiling of 10 and ran to completion. H7 is Mandatory at C2; the control that exists is a wave counter wearing a budget's name.
> **Solution:** Reconcile measured spend after each wave, keep the estimate as a pre-dispatch admission check, add an in-wave cap that cancels a breaching run, and express ceilings in currency.

> **Problem:** No containment boundary around agent execution.
> **Priority:** P2
> **Description:** `runtime/isolation.py` creates a directory and reserves a port in an in-process set (`:33`); nothing constrains filesystem, network or process access, and the real transport never receives the workspace. `README.md` describes "workspace isolation for parallel agents", which is accurate as namespacing and misleading as containment — and the kernel's loop is strictly sequential, so the parallelism it guards against does not yet exist either.
> **Solution:** When tools arrive, run tool execution in an actual sandbox with an explicit egress policy; until then, correct the wording.

> **Problem:** Unvalidated model alias with no snapshot pin or re-baselining rule.
> **Priority:** P1
> **Description:** `DEFAULT_MODEL = "claude-opus-4-8"` (`runtime/claude_executor.py:55`) is a bare alias that has never been resolved against the API, with no dated snapshot, no defined behaviour on deprecation or outage beyond mapping 429 to `BUDGET_PAUSED`, and no rule requiring re-baselining after a model, prompt or provider swap. The system's most important dependency has no contingency.
> **Solution:** Pin a dated snapshot in config with a startup smoke check that fails loudly, define outage behaviour, and require an evaluation re-run on any model or prompt change before autonomy resumes.

---

## 8. Review & verification — 🔴

**The principle.** Nothing an agent produces should be trusted because it sounds right. Structured output should be validated deterministically, calculations independently recomputed, factual claims traced to sources, and tool results confirmed against the external state they claim to have changed. Crucially, the agent must not be the only judge of its own work — self-assessment is not verification.

**Why Red.** Mandatory gates 2 and 15 fail Critical. There is genuine strength underneath: the gate-runner is deterministic with no model involved (`runtime/gates.py`), a failed gate blocks dependents and writes an integrity record, and `scripts/validate_framework.py` is a real deterministic check on the governance estate enforced by CI on every push (verified: 35 agents, 0 errors). But none of it reaches the model's work, because the work is thrown away. Probe B4a: a normal text response yields `status=COMPLETED`, `tokens=812`, `output={}`. The gate predicates therefore evaluate transport metrics — tokens, durations, counters — never the artefact. The quality gates in the agent specs, each carrying `blocking: true`, are natural-language `check:` fields that no code executes; the validator only confirms the flag exists.

> **Problem:** The model's output is discarded and `COMPLETED` returned regardless.
> **Priority:** P1
> **Description:** `runtime/claude_executor.py:474` reads only `usage.output_tokens` from the final message and drops the content; `_output` stays empty (`:400`, `:492`); the handle maps `COMPLETED` on stream termination alone (`:232-241`). Probe B1 confirms end to end: a wave whose entire prompt was `"w1-seo-architecture"` was reported `COMPLETED`. This is mandatory gate 15 — claiming success when the outcome has not occurred — as the system's default behaviour rather than an edge case.
> **Solution:** Persist the response to the wave workspace, return it, validate it against an output schema, and make `COMPLETED` conditional on that validation. Closure evidence: probes B1 and B4a re-run, plus proposed tests P7 and P11.

> **Problem:** All 35 agents' quality gates are natural-language text nothing executes.
> **Priority:** P1
> **Description:** Each spec declares gates with `blocking: true` (e.g. `rosters/appdev/agents/agent-09-security-infosec-v1.0.0.yaml:118-129`), and `validate_framework.py` verifies only that such a flag is present. No runtime evaluates any of them, so every quality gate in the framework rests on the model complying with prose.
> **Solution:** Give each gate an executable predicate — the `Gate` type already supports exactly this (`runtime/gates.py:23-35`) — and run it in the kernel's existing gate-runner, which already blocks dependents correctly on failure.

> **Problem:** A raising gate predicate crashes the kernel and freezes wave state.
> **Priority:** P2
> **Description:** `run_gate` (`runtime/gates.py:37-39`) is unguarded and `runtime/kernel.py:264` calls it unguarded. Probe B6: a raising predicate propagated out of `Kernel.run`, leaving the emitted wave-status at `state: RUNNING` with no termination cause and no integrity entry — the Console would render a permanently in-progress wave. Once gates do real work (parsing output, verifying hashes), raising becomes routine.
> **Solution:** Treat a raising predicate as `GATE_BLOCKED` with the exception recorded and a `CRITICAL` integrity entry; emit state in a `finally` so no run can leave a stale `RUNNING`.

---

## 9. Triggers, retries, stopping & escalation — 🟠

**The principle.** An agent needs to know when to start, when to try again, when to give up, and who to tell. Retry limits, cost and time ceilings, and stopping conditions must be enforced by the runtime, and they must key off validated system state rather than the agent's own assertion that it is finished. When the system cannot proceed, escalation must reach a named human with enough context to act.

**Why Amber, and this is the repo's strongest area.** Every stopping condition is implemented and tested: heartbeat grace with dead-agent detection (`runtime/kernel.py:193-231`, `test_liveness.py`), a hard wave deadline and an iteration backstop, bounded retries with exponential backoff and a circuit breaker (`runtime/resilience.py`, `test_resilience.py`), a pre-dispatch budget pause that checkpoints and resumes (`test_budget.py`, `test_checkpoint.py`), and accurate termination-cause attribution so a crash is recorded as `DIED` and never as `COMPLETED`. That is genuine engineering and mandatory gate 3 passes on it. Three things hold it back: escalations reach nobody, concurrent runs are unprotected, and the budget ceiling is in the wrong unit (covered under principles 3 and 7).

> **Problem:** Escalations are written and never collected.
> **Priority:** P1
> **Description:** `runtime/kernel.py:324-336` writes items to `decisions-queue.yaml`; no consumer reads them back, no owner is named, no alert fires, and the `aom_timeout_hours` modelled in `runtime/genesis.py:27` is not enforced. Mandatory gate 4 fails Conditional.
> **Solution:** Route queue items to a named responder with an SLA and alerting, and enforce the timeout. Closure evidence: an escalation reaching a responder and being actioned within its window.

> **Problem:** Concurrent runs double-dispatch and crash the state writer.
> **Priority:** P2
> **Description:** `Kernel.run` takes no lock on the engagement root, `Checkpointer` loads once at construction and rewrites wholesale, and `StateEmitter` uses a fixed shared temp path (`runtime/state.py:132-137`). Probe B5: two kernels on one root both dispatched wave `w1`, and one died with `FileNotFoundError` on the shared `.tmp`. The atomicity claim at `runtime/state.py:69-73` holds for one writer plus a crash, not for two writers — and the loser dies rather than degrading.
> **Solution:** An `O_EXCL` lock file on the engagement root refusing a second concurrent run, unique temp suffixes per write, and port allocation checked against the OS rather than in-process state.

---

## 10. Evaluation & reliability — 🔴

**The principle.** An agent that works once has not been shown to work. Evaluation means running representative cases repeatedly and measuring: does it complete, is it accurate, does it pick the right tools, does it escalate when it should, does it refuse what it should refuse, does it hold up against adversarial input, and how much does it cost each time. Past failures become permanent regression cases, and any change of model, prompt or tool is compared against a baseline before it ships.

**Why Red.** Mandatory gate 12 fails Critical. There is no agent evaluation of any kind. The 44 passing tests are software tests of the deterministic kernel — valuable, verified, and not the same thing. `AnthropicMessagesTransport` appears in zero test files despite the code providing a `client=` injection hook specifically for that purpose, so the only code that can reach a model is entirely unexercised. There is no eval set, no adversarial suite, no reliability measurement, no cost or latency baseline, and no calibration of any model-based judgement. The pilot's ~28 self-findings exist as prose in `pilot/CASE-STUDY.md`, not as regression cases.

> **Problem:** The real transport has zero test coverage.
> **Priority:** P1
> **Description:** The `client=` hook at `runtime/claude_executor.py` is documented as "injectable for testing the real code path" and no test uses it. The streaming loop, `usage` parsing, retry behaviour and 429 mapping are all unexercised — I had to write probes to establish what the code does.
> **Solution:** Cover the real transport via its own injection hook, including a normal completion, a mid-stream error, a 429, and a hang. Closure evidence: those cases in `runtime/tests/`.

> **Problem:** No agent evaluation exists at all.
> **Priority:** P1
> **Description:** No eval set, no adversarial cases, no reliability runs, no refusal tests, no escalation tests, no cost or latency baseline. The 12 proposed behavioural tests in the audit cannot even be attempted until the runtime passes agent specifications to the model.
> **Solution:** Build the suite from the audit's proposed tests P1–P12, convert the pilot's ~28 findings into regression cases, set thresholds by business risk, and run it in CI. Closure evidence: a green suite with a published reliability baseline over ≥20 repeated runs.

---

## 11. Safety & security boundaries — 🟠

**The principle.** The system must not leak data across users or clients, must not be steered by instructions hidden in the content it reads, must not hold more permission than it needs, and must keep its secrets out of logs and model context. Traces cut both ways: full observability over personal or client data is itself a liability unless retention is bounded, sensitive fields are redacted, and deletion reaches the logs too.

**Why Amber.** The credential handling is genuinely good and tested: no third source beyond injected config and environment, fail-loud `require()` with an actionable message, `mask()` redacting to last-4, and no secret found anywhere in the repository (verified). The Console binds to loopback by default, forwards no key, and writes only local files. There is no cross-client path because there is no multi-tenancy. What holds this at Amber is a false public claim, the absence of any injection control for the moment retrieval exists, and no trace-retention policy for the moment client data starts flowing.

> **Problem:** `README.md` states a CI secret-scan gate that does not exist.
> **Priority:** P0
> **Description:** "a CI secret-scan gate blocks accidental commits" appears in `README.md`; `.github/workflows/validate.yml` runs the validator and the shell compliance check and nothing else. Every repo-wide match for secret-scanning tooling is prescriptive text inside agent specs describing CI for applications those agents would build. Two further README claims fail the same way — "Non-fabrication, enforced by architecture" (principle 5) and "the full verdict ships in this repo (`audits/`)", where `audits/reports/` contains only `.gitkeep` and `site/README.md:55` states the verdict lives in the private instance repo.
> **Solution:** Add a real secret-scanning step to CI or remove the claim; commit the ASA verdict or state where it lives; adopt a rule that every capability claim in `README.md` cites the file that implements it. This is P0 because the claims are public now and the project's stated differentiator is calibrated honesty — the excellent `site/what-its-not.html` page is undercut by its own front page.

> **Problem:** No prompt-injection controls, and none possible while retrieval is unbuilt.
> **Priority:** P1
> **Description:** Untrusted content is handled by prose instruction in agent specs only. Today nothing reaches a model, so nothing can be injected (proposed test P4 would "pass" for the wrong reason). The moment the manifesto, evidence locker and web content start flowing into prompts, every injection defence in this system will be a prompt asking the model to behave.
> **Solution:** Mark retrieved content as data at assembly time, keep tool authorisation outside model influence (principle 6), and add injection cases to the evaluation suite before retrieval ships.

> **Problem:** No trace retention, redaction or deletion policy.
> **Priority:** P2
> **Description:** `metrics-ledger.jsonl` and `integrity-register.jsonl` are unbounded append-only files with no rotation, redaction or access control (`runtime/state.py:108-120`), and the Console serves whatever is under `STATE_DIR` over unauthenticated HTTP, bindable beyond loopback via `--host` (`dashboard/server.py:287-288`). Low exposure today; once prompts and responses are captured (principle 8), these files will hold client business data.
> **Solution:** Retention windows per ledger, write-time redaction of designated fields, authentication required for non-loopback binding, and deletion that propagates into ledgers, the evidence locker and any future memory store.

---

## 12. Monitoring & incident response — 🔴

**The principle.** Once a system runs unattended, someone has to see it working and know what to do when it stops. That means production monitoring, alerts that route to a named person, a runbook that person has actually read, a tested way to interrupt or kill a run, and a process for turning incidents into test cases. An agent audited as safe is unsafe in untrained hands.

**Why Red.** Mandatory gate 13 fails Conditional and there is nothing to offset it. The Mimir Console is a read-only local viewer that renders bundled sample fixtures by default; no kernel has ever emitted state that the Console then displayed end to end. There is no alerting, no named responder, no on-call, no runbook anywhere in the repository, no absence cover, and no tested kill switch (principle 7). The observability foundations are genuinely present — four correlated ledgers with atomic writes and accurate termination-cause attribution — which is what makes this Red rather than hopeless: the data exists and nobody is watching it.

> **Problem:** No monitoring, alerting, runbook or named responder exists.
> **Priority:** P1
> **Description:** Nothing pages anyone, and no document tells an operator how to start, interrupt, kill or escalate a run. Release is conditional on someone being able to operate the system, and there is currently nobody assigned and nothing to train them on.
> **Solution:** Author the runbook, assign a named operator with absence cover, route alerts on `DEAD`/`GATE_FAILURE`/`BUDGET_PAUSED` integrity events, and rehearse the interrupt and kill procedures. Closure evidence: runbook committed, alert delivered in a drill, kill switch demonstrated.

> **Problem:** No incident-response process, and incidents do not become test cases.
> **Priority:** P2
> **Description:** No IR process exists in the repo. The pilot's ~28 self-findings were captured as narrative and never became regression tests, so the same failures can recur undetected.
> **Solution:** A lightweight IR process (detect, contain, record, remediate, regress) with every incident producing a permanent case in the evaluation suite.

---

## 13. Learning, change control & versioning — 🟢

**The principle.** Anything that changes an agent's behaviour — prompts, tools, policies, evaluators, the model itself — must be versioned, reviewed, and reversible, and the agent must never be able to rewrite its own governance. Changes should be tested against a baseline before they ship, and improvement should be attributable rather than assumed.

**Why Green.** This is the part of Mimir that is genuinely production-grade, and it earns the rating on the same evidence discipline applied to the Reds. Every agent and constitutional document carries a semantic version, superseded versions are retained under `archive/` rather than deleted (47 archived agent-version files), and `scripts/validate_framework.py` enforces eighteen error classes including filename-to-field version agreement, header-comment drift, manifest consistency, handoff resolution and pass-item contracts — verified live at 35 agents, 0 errors, 6 warnings. `.github/workflows/validate.yml` runs it on every push and pull request, so drift cannot merge. `runtime/genesis.py` guarantees the system cannot approve its own expansion, backed by tests. Two caveats keep this from being unqualified: the runtime's own configuration (model, prompts once they exist, harness knobs) is not yet under the same discipline (principle 7), and `ai_manager_agent`'s autonomous change authority is prompt-enforced (principle 3) — both are tracked there rather than duplicated here. **Evidence:** `scripts/validate_framework.py` (E1–E18), `.github/workflows/validate.yml`, `runtime/genesis.py` + `runtime/tests/test_genesis.py`, 47 archived agent versions.

---

## Re-rating triggers

1. **README corrections land (P0 — F3, maturity banner).** Principle 11 moves toward Green on the secret-scan claim; principle 1's problem block closes. This is hours of work and is the only P0 in the plan.
2. **Agent-spec loader and prompt assembler ship (P1 — F1).** Principle 5 Red → Amber; principle 4 Amber → Green. **Warning:** shipping F1 without the tool registry (F4) and the executable non-fabrication gate makes the system *worse* than today, because every model-layer control in the audit's Appendix B becomes live prompt-only enforcement. Sequence F4 and the non-fabrication gate alongside or ahead of F1.
3. **Model output captured, persisted and schema-validated (P1 — F2).** Closes Critical gates 2 and 15; principle 8 Red → Amber, and Green once agent quality gates are executable predicates.
4. **Tool registry with allowlist and schema validation ships (P1 — F4).** Principle 6 Red → Amber; principle 7 unblocks its Mandatory H3 cap. Gates 5 and 8 become live and must be re-tested rather than marked Not Applicable.
5. **Budget in real units, kill switch, approval records, escalation routing (P1).** Principle 7 Red → Amber; principle 3 Amber → Green; principle 9 Amber → Green.
6. **Evaluation suite green with a published reliability baseline over ≥20 runs (P1).** Closes Critical gate 12; principle 10 Red → Amber, Green once thresholds are enforced in CI and incidents feed back as regression cases.
7. **Runbook, named operator, alert routing and a rehearsed kill switch (P1).** Principle 12 Red → Amber; Green after a drill.
8. **Any of these events triggers an immediate full re-audit regardless of schedule:** the first credentialed live run; the first write-capable tool; any repo write path granted to the runtime; a model or provider swap; any proposal to increase autonomy.
9. **Calendar backstop: 2026-11-21 (90 days).** Re-rate then even if nothing above has moved — a stalled remediation plan is itself a finding.
