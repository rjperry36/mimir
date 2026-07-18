# PraisonAI Spike — Decision Memo

**Date:** 2026-07-18
**Status:** spike COMPLETE — adapter built and contract-proven; decision
recommended below, owner to ratify.
**Question:** should mimir utilise PraisonAI
(github.com/MervinPraison/PraisonAI), adapt against it, or ignore it?

---

## 1. What was evaluated

- `praisonaiagents` 1.6.154 (the core library; MIT licence), installed and
  exercised in this sandbox.
- Public docs/repo review: YAML-defined agents, sequential/hierarchical/
  workflow processes, memory, guardrails, human-approval callbacks, MCP tool
  support, chat surfaces; ~8.5k stars, very active release cadence.

## 2. What was built (the proof)

`runtime/praison_executor.py` + `runtime/tests/test_praison_executor.py`:

- **`PraisonAIExecutor`** satisfies the kernel's `AgentExecutor` contract by
  reusing the kernel-proven `_SubagentHandle` and `Transport` seam from the
  Claude adapter — PraisonAI slots UNDER the deterministic kernel; nothing
  constitutional is bypassed.
- **`PraisonAgentTransport`** runs one blocking PraisonAI agent turn on a
  worker thread; heartbeats from `llm_content` / `tool_call` display
  callbacks feed the kernel's silent-death detection.
- **Outcome mapping proven:** completion → `COMPLETED` (+ output,
  tool-use metrics), provider error → `DIED`, 429 → `BUDGET_PAUSED`,
  silent hang → frozen heartbeat (kernel-detectable), cancel →
  `CANCELLED`/`TIMED_OUT`, late results after cancel discarded.
- **Kernel drop-in proven with real threads:** a two-wave engagement runs
  through the unmodified kernel against `PraisonAIExecutor`
  (MonotonicClock, tight timings).
- **YAML mapping proven:** the live ECL interview definition
  (`agents/agent-ecl-interview-v2.1.0.yaml`) constructs a real
  `praisonaiagents.Agent` — mimir's `name/role/goal/backstory` map 1:1.
- **Suite green:** 52/52 runtime tests (44 existing + 8 new).
- **BYOK preserved:** key resolved via `runtime.credentials` env-first and
  passed explicitly; no key → loud `CredentialError` before any praison
  import. Core runtime keeps its stdlib+pyyaml claim — `praisonaiagents` is
  imported lazily, live-run only.

## 3. Findings and caveats

| Finding | Consequence |
|---------|-------------|
| Agent API maps 1:1 to mimir agent YAML | Adaptation is translation, not reinvention |
| Display callbacks are process-global | Fine at one wave per process; needs care if waves ever share a process |
| No hard-cancel API | `close()` is cooperative; orphaned turns end on their own — kernel timeout/death handling unaffected |
| Token counts not in the public return | `tokens` metric absent, not fabricated (framework rule) |
| Installs `posthog` (telemetry dependency) | Must be verified DISABLED for client-confidential engagements before any live use |
| `anthropic/...` model strings route via litellm (not installed by default) | Live Anthropic runs need `pip install litellm`, or use an OpenAI-compatible endpoint |
| Effectively single-maintainer, very high release churn | Real dependency risk — contained entirely behind the executor seam |
| Governance features (approval, guardrails) are basic vs mimir's AOM | Confirms: PraisonAI cannot replace the constitutional layer |

## 4. Decision (recommended)

**ADAPT, don't adopt-as-foundation; contained behind the executor seam.**

1. Keep mimir's kernel, gates, and constitutional layer exactly where they
   are — they are the product's moat and PraisonAI offers no equivalent.
2. `PraisonAIExecutor` becomes an optional, supported execution backend
   alongside `ClaudeSubagentExecutor` — useful for multi-provider BYOK and
   as a second route to the Phase 0 live-run proof.
3. Do NOT take praisonaiagents as a dependency of the core runtime, the
   dashboard, or any constitutional document. Lazy import, live-run only.
4. Re-evaluate PraisonAI's session/memory/chat components during the
   Phase 1 interview-harness spec (scope WS5) as borrow-candidates — a
   separate decision with its own memo if pursued.
5. Before any live client use: confirm telemetry is disabled and pin the
   dependency version.

## 5. What this spike deliberately did not do

No live LLM call was made (no key configured in this sandbox — consistent
with the repo's standing honest-limitation). The adapter is complete,
contract-proven code; the live run is Phase 0 of
`roadmap/path-to-viable-product-v0.1.0.md`.
