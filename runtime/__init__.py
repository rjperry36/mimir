"""agent-framework deterministic runtime kernel.

The minimum deterministic plumbing that runs BETWEEN waves: liveness/timeout +
dead-agent detection, checkpointing, gate-runner, budget guard, workspace
isolation, termination-cause attribution, and structured state emission for the
Framework Console dashboard.

This is DETERMINISTIC SOFTWARE (plain Python), not agents. Agents run only
INSIDE waves, behind the pluggable AgentExecutor interface.
"""

from .budget import BudgetGuard
from .checkpoint import Checkpointer
from .clock import Clock, ManualClock, MonotonicClock
from .credentials import Credentials, CredentialError, KNOWN_SERVICES, mask
from .executor import (
    AgentExecutor,
    AgentResult,
    AnthropicMessagesTransport,
    ClaudeSubagentExecutor,
    FakeEvent,
    FakeTransport,
    MockExecutor,
    MockScenario,
    TerminationCause,
    Transport,
    TransportPoll,
    TransportStatus,
    WaveTask,
    default_transport_factory,
)
from .resilience import (
    BreakerState,
    CallTimeout,
    CircuitBreaker,
    CircuitOpen,
    ResilientTool,
    RetryPolicy,
    resilient_call,
    run_with_hard_timeout,
)
from .gates import Gate, GateResult, require_no_defects, run_gate
from .isolation import Workspace, WorkspaceManager
from .kernel import (
    EngagementSpec,
    Kernel,
    KernelConfig,
    RunResult,
    RunStatus,
    WaveSpec,
)
from .state import IdIssuer, StateEmitter, WaveState

__all__ = [
    "BudgetGuard", "Checkpointer", "Clock", "ManualClock", "MonotonicClock",
    "AgentExecutor", "AgentResult", "ClaudeSubagentExecutor", "MockExecutor",
    "MockScenario", "TerminationCause", "WaveTask", "Gate", "GateResult",
    "require_no_defects", "run_gate", "Workspace", "WorkspaceManager",
    "EngagementSpec", "Kernel", "KernelConfig", "RunResult", "RunStatus",
    "WaveSpec", "IdIssuer", "StateEmitter", "WaveState",
    # real executor adapter + transports
    "AnthropicMessagesTransport", "FakeEvent", "FakeTransport", "Transport",
    "TransportPoll", "TransportStatus", "default_transport_factory",
    # tool-resilience layer
    "BreakerState", "CallTimeout", "CircuitBreaker", "CircuitOpen",
    "ResilientTool", "RetryPolicy", "resilient_call", "run_with_hard_timeout",
    # BYOK credential resolution
    "Credentials", "CredentialError", "KNOWN_SERVICES", "mask",
]
