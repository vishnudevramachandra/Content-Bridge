"""FastAPI backend that drives the orchestrator agent over SSE.

Architecture, in short:
* `POST /api/chat` starts one orchestrator run per request and streams it
  back as Server-Sent Events (SSE) — text deltas, tool calls/results, and
  our own `SubAgentStartedEvent`/`SubAgentFinishedEvent` progress markers
  — using `agent.iter()` so the run stays a first-class `AgentRun` object
  we can also inject into from the outside.
* `message_history` is kept for a single global conversation (this is a
  single-user dev backend, not a multi-tenant one) and passed into the
  next run so the orchestrator remembers earlier turns.
* A periodic background task checks whether a run is currently active and,
  if so, injects a "system alert" into it via `AgentRun.enqueue()` — the
  orchestrator picks it up on its next model request. If no run is
  active, the tick is simply skipped.
"""

import asyncio
import json
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

import httpx
import uvicorn
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from rich.console import Console

from pydantic_ai import Agent
from pydantic_ai.messages import (
    EnqueuedMessagesEvent,
    FunctionToolCallEvent,
    FunctionToolResultEvent,
    ModelMessage,
    PartDeltaEvent,
    PartStartEvent,
    TextPart,
    TextPartDelta,
)
from pydantic_ai.run import AgentRun

from contentbridge.agents.orchestrator.deps import AgentDeps
from contentbridge.agents.orchestrator.events import (
    SubAgentFinishedEvent,
    SubAgentStartedEvent,
)
from contentbridge.agents.orchestrator.orchestrator_agent import (
    agent as orchestrator_agent,
)
from contentbridge.utils.utils import get_env

_PERIODIC_ALERT_INTERVAL_SECONDS = 5


class ChatState:
    """Process-wide conversation + streaming state.

    This is a single global conversation (no per-user/session handling
    yet), which matches the original prototype. `active_run` is set for
    the duration of one `/api/chat` request so the periodic background
    task can inject into it.
    """

    def __init__(self) -> None:
        self.message_history: list[ModelMessage] = []
        self.active_run: AgentRun[AgentDeps, str] | None = None


chat_state = ChatState()
console = Console()


class UserPromptRequest(BaseModel):
    message: str


def _event_to_sse(event: object) -> str | None:
    """Convert one agent stream event into an SSE `data: ...` line.

    Returns None for event types we don't forward to the frontend.
    """
    payload: dict[str, object]

    if isinstance(event, PartStartEvent) and isinstance(event.part, TextPart):
        payload = {"type": "text_start", "content": event.part.content}
    elif isinstance(event, PartDeltaEvent) and isinstance(
        event.delta, TextPartDelta
    ):
        payload = {"type": "text_delta", "content": event.delta.content_delta}
    elif isinstance(event, FunctionToolCallEvent):
        payload = {
            "type": "tool_call",
            "tool_name": event.part.tool_name,
            "args": event.part.args,
        }
    elif isinstance(event, FunctionToolResultEvent):
        payload = {
            "type": "tool_result",
            "tool_name": getattr(event.part, "tool_name", None),
            "content": event.content,
        }
    elif isinstance(event, SubAgentStartedEvent):
        payload = {
            "type": "sub_agent_started",
            "agent_name": event.agent_name,
            "instruction": event.instruction,
        }
    elif isinstance(event, SubAgentFinishedEvent):
        payload = {
            "type": "sub_agent_finished",
            "agent_name": event.agent_name,
            "summary": event.summary,
        }
    elif isinstance(event, EnqueuedMessagesEvent):
        # Content injected mid-run (e.g. the periodic system alert below),
        # surfaced so the frontend can show it was delivered into the
        # conversation.
        texts = [
            part.content
            for message in event.messages
            for part in message.parts
            if isinstance(getattr(part, "content", None), str)
        ]
        payload = {
            "type": "system_alert",
            "enqueue_id": event.enqueue_id,
            "content": " ".join(texts),
        }
    else:
        return None

    return f"data: {json.dumps(payload, default=str)}\n\n"


async def _stream_orchestrator_run(
    user_prompt: str, deps: AgentDeps
) -> AsyncGenerator[str]:
    """Drive one orchestrator run via `agent.iter()`, yielding SSE lines.

    Using `agent.iter()` (rather than the simpler `run_stream_events()`)
    is what lets us hand the live `AgentRun` to `chat_state.active_run`,
    so the periodic background task can call `.enqueue()` on it.
    """
    async with orchestrator_agent.iter(
        user_prompt,
        deps=deps,
        message_history=chat_state.message_history,
    ) as agent_run:
        chat_state.active_run = agent_run
        try:
            async for node in agent_run:
                if Agent.is_model_request_node(
                    node
                ) or Agent.is_call_tools_node(node):
                    async with node.stream(agent_run.ctx) as stream:
                        async for event in stream:
                            sse_line = _event_to_sse(event)
                            if sse_line is not None:
                                yield sse_line
        finally:
            chat_state.active_run = None

        result = agent_run.result
        if result is not None:
            chat_state.message_history = result.all_messages()
            yield f"data: {json.dumps({'type': 'final', 'output': result.output})}\n\n"


async def _periodic_alert_worker() -> None:
    """Every few seconds, inject a system alert into the active run, if any.

    Uses `priority="when_idle"` deliberately: the default `"asap"` priority
    delivers at the *earliest* opportunity, which — for a run whose model
    turn takes longer than the alert interval — aborts and restarts the
    in-flight model request every tick, so the run never converges.
    `"when_idle"` instead waits until the agent would otherwise end,
    giving it one extra look at the alert without interrupting whatever
    it's already doing.
    """
    while True:
        await asyncio.sleep(_PERIODIC_ALERT_INTERVAL_SECONDS)

        active_run = chat_state.active_run
        if active_run is None:
            continue

        active_run.enqueue(
            "SYSTEM ALERT: periodic health check triggered. If this is "
            "not relevant to the current task, ignore it and continue.",
            priority="when_idle",
        )


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None]:
    async with httpx.AsyncClient() as http_client:
        app.state.http_client = http_client
        alert_task = asyncio.create_task(_periodic_alert_worker())
        try:
            yield
        finally:
            alert_task.cancel()


app = FastAPI(title="Content-Bridge Backend", lifespan=lifespan)


@app.post("/api/chat")
async def chat(payload: UserPromptRequest) -> StreamingResponse:
    text = payload.message.strip()
    if not text:
        return StreamingResponse(
            iter([f"data: {json.dumps({'type': 'error', 'detail': 'empty message'})}\n\n"]),
            media_type="text/event-stream",
            status_code=400,
        )

    deps = AgentDeps(
        console=console,
        http_client=app.state.http_client,
        search_api_key=get_env("SEARCH_API_KEY"),
    )

    return StreamingResponse(
        _stream_orchestrator_run(text, deps), media_type="text/event-stream"
    )


@app.post("/api/reset")
async def reset() -> dict[str, str]:
    chat_state.message_history = []
    return {"status": "reset"}


@app.get("/api/status")
async def status() -> dict[str, object]:
    return {
        "run_active": chat_state.active_run is not None,
        "history_length": len(chat_state.message_history),
    }


def main() -> None:
    uvicorn.run(app, host="0.0.0.0", port=8000)


if __name__ == "__main__":
    main()
