# Runtime Kernel

**The minimum deterministic runtime kernel for agent-framework.**

This is the plumbing that runs **between waves** — deterministic software (plain
Python 3, stdlib + `pyyaml` only), **not** agents. It is the #1 item the
independent auditor (ASA verdict v1.0.0, Q9) and the pilot's own backlog
(`runtime_sdk_backlog` RSB-01..05) asked for:

> "Build the minimum deterministic runtime kernel: per-wave heartbeat + hard
> timeout + dead-agent detection, mandatory commit-checkpoint per sub-milestone,
> and a wave sequencer/gate-runner that fires and records gates without a human."

Agents run **only inside waves**, behind a pluggable executor. Everything the
kernel itself does — sequencing, liveness, gates, budget, checkpointing,
isolation, state emission — is rule-based and fully tested.

---

## What's real vs stubbed

| Component | File | Status |
|-----------|------|--------|
| Wave scheduler (topological, dependency-aware) | `kernel.py` | **REAL, tested** |
| Liveness / heartbeat monitor + hard timeout + dead-agent detection (RSB-01) | `kernel.py` | **REAL, tested** |
| Per-sub-milestone checkpointing + idempotent resume (RSB-01) | `checkpoint.py` | **REAL, tested** |
| Deterministic gate-runner (blocks/releases dependents) | `gates.py`, `kernel.py` | **REAL, tested** |
| Budget guard: pre-dispatch quota check + graceful pause/resume (RSB-02) | `budget.py`, `kernel.py` | **REAL, tested** |
| Workspace + port isolation (RSB-03) | `isolation.py` | **REAL, tested** |
| Termination-cause attribution (RSB-04) | `executor.py`, `kernel.py` | **REAL, tested** |
| Structured state emission (4 dashboard ledgers) | `state.py`, `kernel.py` | **REAL, tested** |
| Monotonic, collision-safe ID issuance (RSB-05) | `state.py` | **REAL, tested** |
| Injectable clock (deterministic tests) | `clock.py` | **REAL, tested** |
| `MockExecutor` (scriptable: success / death / hang / crash) | `executor.py` | **REAL, tested** |
| `ClaudeSubagentExecutor` (real agent executor adapter) | `claude_executor.py` | **REAL, fake-transport-tested** (live run needs credentials + SDK) |
| Tool-resilience layer (timeout / retry+backoff / fallback / circuit-breaker) | `resilience.py` | **REAL, tested** |
| BYOK credential resolution (env-first, injected config, redaction) | `credentials.py` | **REAL, tested** |

**The honest limitation:** a *live* Claude agent run is **not proven in this
sandbox** — the `anthropic` SDK is not installed and no API key is configured
here. The executor adapter is complete, contract-conformant code proven against
a deterministic `FakeTransport`; a credentialed live run is what remains to
prove end-to-end (see next section).

---

## Real executor & resilience

### `ClaudeSubagentExecutor` — the real adapter

`ClaudeSubagentExecutor` (in `claude_executor.py`, re-exported from
`executor.py`) is a **drop-in replacement for `MockExecutor`**: the same kernel
logic runs against it unchanged (proven in `tests/test_executor_contract.py`).
It runs a wave as a real Claude agent turn behind a swappable `Transport`:

| Transport | What it is | Status |
|-----------|-----------|--------|
| `FakeTransport` | deterministic, clock-driven; replays a scripted timeline of token / tool-use / completion / error / 429 events | **REAL, what the tests prove** |
| `AnthropicMessagesTransport` | a real streaming tool-use loop over the `anthropic` Messages API (`claude-opus-4-8`), heartbeating on token/tool events, wrapping the request in the resilience layer | **COMPLETE code, unproven without credentials + SDK** |

Outcome → termination-cause mapping the kernel depends on:

| Real outcome | `TerminationCause` |
|--------------|--------------------|
| normal completion | `COMPLETED` (+ metrics: tokens, tool_uses, duration_ms) |
| API error after retries | `DIED` |
| silent hang (heartbeats stop) | `DIED` — detected by the **kernel** (heartbeat stops advancing → grace window elapses → `cancel(DIED)`) |
| hard timeout | `TIMED_OUT` — kernel deadline |
| quota / HTTP 429 | `BUDGET_PAUSED` |
| explicit cancel | `CANCELLED` (new enum member; additive, kernel-safe) |

Heartbeats are emitted on streamed tokens and tool-use events, so the kernel's
dead-agent detection works against real latency.

**What a live credentialed run additionally requires** (not available here):

```bash
pip install anthropic          # the Messages API SDK
export ANTHROPIC_API_KEY=sk-…  # your own key (see BYOK below)
```

With neither present, `default_transport_factory` fails **loud and clear** —
a `CredentialError` if the key is missing, a `RuntimeError` if the SDK is
missing — never a silent skip. Tests bypass this by injecting a `FakeTransport`
factory.

### Bring-your-own-key (BYOK)

This framework is shared publicly and **ships no credentials of its own.**
`credentials.py` resolves every secret — the Claude API key and any downstream
tool credential (Vercel, Neon, Clerk, Resend, a booking provider, a payment provider) — from, in
priority order: (1) an **injected config dict** (how the future dashboard passes
a user's own keys in at runtime), then (2) the **process environment**
(`ANTHROPIC_API_KEY`, `PAYMENT_PROVIDER_API_KEY`, …). There is no third source: no
hardcoded value, no committed dotfile, no default fallback.

* Secrets are referenced **by name only**; `KNOWN_SERVICES` maps short service
  names to their env-var names — never a value in code.
* Missing a required key → `Credentials.require(...)` raises an **actionable**
  `CredentialError` ("no API key configured … set `ANTHROPIC_API_KEY` or provide
  it in the app") — the executor never silently proceeds.
* Keys are **never written** into wave-status / metrics / integrity ledgers or
  error messages. `mask()` redacts any value to at most its last four characters
  for the rare diagnostic that must mention one.

### Tool-resilience layer (`resilience.py`)

The ASA flagged that tools had no timeout/retry/fallback. `resilient_call(fn,
clock=…, …)` (and the `ResilientTool` wrapper) add all four, deterministically,
driven by the kernel's injectable clock (no real sleeps in tests):

* **timeout** — a per-call budget; cooperative against the injected clock (a
  slow tool that advances the clock past the budget trips `CallTimeout`).
  `run_with_hard_timeout` is the real-thread escape hatch for a genuinely-hung
  call (wall-clock; kept out of the deterministic tests).
* **retry** — exponential backoff + jitter, configurable factor and a cap,
  bounded attempts; backoff sleeps go through `clock.sleep`.
* **fallback** — a value or callable returned when attempts are exhausted or the
  breaker is open, instead of raising.
* **circuit-breaker** — opens after N consecutive failures, blocks calls while
  open, half-opens for a single probe after a cooldown, closes on success.

The real transport wraps its API request in this layer, tying the two
deliverables together.

---

## The AgentExecutor contract

The kernel never spawns anything itself. It talks to an executor:

```python
handle = executor.submit(task, workspace, clock)  # non-blocking
result = handle.poll()            # AgentResult when finished, else None
hb     = handle.last_heartbeat()  # clock time of last progress signal
handle.cancel(cause)              # kernel judged it DIED / TIMED_OUT
```

* `last_heartbeat()` is what makes **silent-death detection** possible: if the
  gap between now and the last heartbeat exceeds the grace window, the kernel
  marks the wave `DEAD`.
* `poll()` returns an `AgentResult` carrying the **termination cause** and the
  knowable metrics (tokens, tool_uses, duration_ms, defects, …) — absent fields
  are simply omitted, never fabricated.

Swap `MockExecutor` for `ClaudeSubagentExecutor` (once implemented) and the same
kernel logic runs real agents.

---

## How the dashboard consumes the emitted state

The kernel continuously writes four files under `runtime-state/`, which are
exactly the four data sources the Framework Console brief
(`roadmap/console-brief-v0.1.0.md`) maps its views onto:

| File | Format | Console view |
|------|--------|--------------|
| `wave-status.yaml` | full snapshot, rewritten each transition | View 1 — Wave board (per-wave state machine) |
| `metrics-ledger.jsonl` | append-only, one line per agent run | View 2 — Agent metrics timeline (plot by `agent_version` for View 3) |
| `integrity-register.jsonl` | append-only, typed events | View 4 — Integrity log (dead agents, gate failures, budget pauses) |
| `decisions-queue.yaml` | full snapshot of open items | View 5 — Decision inbox (human gates awaiting approval) |

Views 3 (learning-over-time), 6 (RAG) and 7 (RAID) are deterministic
*derivations* of these ledgers plus existing instance files, so they need
nothing new from the kernel. Writes are atomic (temp-file + `os.replace`) so a
crash mid-write cannot leave a ledger the dashboard would choke on.

---

## Run it

```bash
# tests (38, all passing)
python -m pytest runtime/tests/ -q
#   or, without pytest (repo root as top-level so package imports resolve):
python -m unittest discover -t . -s runtime/tests -p 'test_*.py'

# see it work: a 3-wave toy engagement incl. a wave that DIES and a gate that
# BLOCKS, printing the resulting structured state
python -m runtime.demo
```

The demo uses a `ManualClock`, so it runs instantly and deterministically while
exercising the exact code path a real run would.

---

## Module map

```
runtime/
├── clock.py           # injectable Clock (Monotonic / Manual)
├── executor.py        # AgentExecutor interface, MockExecutor, ClaudeSubagentExecutor re-export
├── claude_executor.py # REAL executor adapter + Transport / FakeTransport / Anthropic transport
├── resilience.py      # timeout / retry+backoff / fallback / circuit-breaker
├── credentials.py     # BYOK credential resolution (env-first, injected, redaction)
├── isolation.py       # WorkspaceManager (dir + port isolation)          [RSB-03]
├── budget.py          # BudgetGuard (pre-dispatch quota, pause/resume)   [RSB-02]
├── gates.py           # Gate + deterministic gate-runner
├── checkpoint.py      # Checkpointer (per-wave, idempotent resume)       [RSB-01]
├── state.py           # StateEmitter (4 ledgers) + IdIssuer              [RSB-05]
├── kernel.py          # Kernel: scheduler + liveness monitor + orchestration
├── demo.py            # python -m runtime.demo
└── tests/             # 38 tests, all passing
```
