"""Progress events the orchestrator emits while delegating to a sub-agent.

These are `CustomEvent`s: they flow through the orchestrator's event stream
(`agent.iter()` / `run_stream_events()` / `event_stream_handler`) without
being added to the model's own context, so a frontend consuming the stream
can show "Discovery agent is running..." while the delegated run is still
in progress.
"""

from dataclasses import dataclass

from pydantic_ai import CustomEvent


@dataclass(kw_only=True)
class SubAgentStartedEvent(CustomEvent):
    """Emitted right before the orchestrator delegates to a sub-agent."""

    agent_name: str
    instruction: str


@dataclass(kw_only=True)
class SubAgentFinishedEvent(CustomEvent):
    """Emitted right after a delegated sub-agent run completes."""

    agent_name: str
    summary: str
