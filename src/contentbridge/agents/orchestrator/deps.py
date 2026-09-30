from dataclasses import dataclass
import httpx

from rich.console import Console

from contentbridge.agents.orchestrator.pending import PendingSubAgentRun


@dataclass
class AgentDeps:
    console: Console
    http_client: httpx.AsyncClient
    search_api_key: str
    # Shared, mutable across requests: main.py owns the dict and passes the
    # same object in on every call, so a sub-agent's paused state survives
    # between the request that created it and the later `/api/answer` call
    # that resumes it.
    pending_sub_agent_runs: dict[str, PendingSubAgentRun]
