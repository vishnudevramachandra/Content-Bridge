"""State for a sub-agent run that's paused waiting on `ask_user`.

When a sub-agent's `ask_user` tool raises `CallDeferred`, its run ends
early with a `DeferredToolRequests` result instead of a final summary.
To resume that *exact* run later with the human's answer, we need to keep
its `message_history` and the pending `DeferredToolRequests` around,
keyed by an id the orchestrator's own deferred tool call carries in its
metadata (see `run_discovery_agent` in orchestrator_agent.py).
"""

from dataclasses import dataclass

from pydantic_ai import DeferredToolRequests
from pydantic_ai.messages import ModelMessage


@dataclass
class PendingSubAgentRun:
    agent_name: str
    message_history: list[ModelMessage]
    requests: DeferredToolRequests
