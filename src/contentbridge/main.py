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
* A sub-agent (e.g. Discovery) can pause mid-task to ask the human a
  question via its own `ask_user` tool. That pause bubbles up through the
  orchestrator's delegation tool as `DeferredToolRequests`, which
  `POST /api/chat` surfaces as a `question` SSE event instead of `final`.
  `POST /api/answer` resumes the paused sub-agent with the human's
  answer, and — once the sub-agent is done — resumes the orchestrator
  with that summary, continuing the same SSE streaming as normal.
"""

import asyncio
import json
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from dataclasses import dataclass

import httpx
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from rich.console import Console

from pydantic_ai import Agent, DeferredToolRequests, DeferredToolResults
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
    resolve_ask_user_answer,
)
from contentbridge.agents.orchestrator.pending import PendingSubAgentRun
from contentbridge.utils.utils import get_env

_PERIODIC_ALERT_INTERVAL_SECONDS = 5


@dataclass
class PendingOrchestratorRun:
    """The orchestrator's own paused state, while a sub-agent's question
    (bubbled up through a delegation tool) is waiting on a human answer.
    """

    message_history: list[ModelMessage]
    requests: DeferredToolRequests


class ChatState:
    """Process-wide conversation + streaming state.

    This is a single global conversation (no per-user/session handling
    yet), which matches the original prototype. `active_run` is set for
    the duration of one `/api/chat` request so the periodic background
    task can inject into it. `pending_sub_agent_runs` and
    `pending_orchestrator` track at most one outstanding human question
    at a time — also consistent with there being a single conversation.
    """

    def __init__(self) -> None:
        self.message_history: list[ModelMessage] = []
        self.active_run: AgentRun[AgentDeps, str] | None = None
        self.pending_sub_agent_runs: dict[str, PendingSubAgentRun] = {}
        self.pending_orchestrator: PendingOrchestratorRun | None = None


chat_state = ChatState()
console = Console()


def _build_deps() -> AgentDeps:
    return AgentDeps(
        console=console,
        http_client=app.state.http_client,
        search_api_key=get_env("SEARCH_API_KEY"),
        pending_sub_agent_runs=chat_state.pending_sub_agent_runs,
    )


class UserPromptRequest(BaseModel):
    message: str


class UserAnswerRequest(BaseModel):
    answer: str


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
    deps: AgentDeps,
    *,
    user_prompt: str | None = None,
    message_history: list[ModelMessage] | None = None,
    deferred_tool_results: DeferredToolResults | None = None,
) -> AsyncGenerator[str]:
    """Drive one orchestrator run (fresh or resumed) via `agent.iter()`.

    Using `agent.iter()` (rather than the simpler `run_stream_events()`)
    is what lets us hand the live `AgentRun` to `chat_state.active_run`,
    so the periodic background task can call `.enqueue()` on it.

    Pass `user_prompt=` for a normal new chat turn (uses
    `chat_state.message_history` unless `message_history=` overrides it).
    Pass `deferred_tool_results=` together with `message_history=` (the
    exact history of the paused run) to resume after a sub-agent's
    question has been answered — no `user_prompt` in that case.
    """
    history = (
        message_history if message_history is not None else chat_state.message_history
    )

    async with orchestrator_agent.iter(
        user_prompt,
        deps=deps,
        message_history=history,
        deferred_tool_results=deferred_tool_results,
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
        if result is None:
            return

        if isinstance(result.output, DeferredToolRequests):
            # A sub-agent asked a question that bubbled all the way up;
            # pause the orchestrator here instead of finishing normally.
            orch_call = result.output.calls[0]
            meta = result.output.metadata.get(orch_call.tool_call_id, {})
            chat_state.pending_orchestrator = PendingOrchestratorRun(
                message_history=result.all_messages(),
                requests=result.output,
            )
            yield _sse_line(
                {
                    "type": "question",
                    "agent_name": meta.get("agent_name"),
                    "question": meta.get("question"),
                }
            )
        else:
            chat_state.message_history = result.all_messages()
            chat_state.pending_orchestrator = None
            yield _sse_line({"type": "final", "output": result.output})


def _sse_line(payload: dict[str, object]) -> str:
    return f"data: {json.dumps(payload, default=str)}\n\n"


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
            iter([_sse_line({"type": "error", "detail": "empty message"})]),
            media_type="text/event-stream",
            status_code=400,
        )
    if chat_state.pending_orchestrator is not None:
        raise HTTPException(
            status_code=409,
            detail="A sub-agent question is pending; answer it via /api/answer first.",
        )

    return StreamingResponse(
        _stream_orchestrator_run(_build_deps(), user_prompt=text),
        media_type="text/event-stream",
    )


@app.post("/api/answer")
async def answer(payload: UserAnswerRequest) -> StreamingResponse:
    pending = chat_state.pending_orchestrator
    if pending is None:
        raise HTTPException(status_code=400, detail="No question is pending.")

    orch_call = pending.requests.calls[0]
    meta = pending.requests.metadata.get(orch_call.tool_call_id, {})
    sub_agent_key = meta.get("sub_agent_key")
    if sub_agent_key is None:
        raise HTTPException(
            status_code=500, detail="Pending question is missing its sub-agent key."
        )

    deps = _build_deps()
    outcome = await resolve_ask_user_answer(
        deps, sub_agent_key, payload.answer.strip()
    )

    if not outcome.finished:
        # The sub-agent asked another question. The orchestrator's own
        # paused run is untouched — surface just the new question.
        async def one_more_question() -> AsyncGenerator[str]:
            yield _sse_line(
                {
                    "type": "question",
                    "agent_name": meta.get("agent_name"),
                    "question": outcome.text,
                }
            )

        return StreamingResponse(
            one_more_question(), media_type="text/event-stream"
        )

    # The sub-agent is done — resume the orchestrator with its summary as
    # the delegation tool's result, and keep streaming as normal.
    #
    # Note: resuming a deferred tool call does *not* re-run
    # `run_discovery_agent`'s body — the framework substitutes the
    # answer directly as that call's result — so the `SubAgentFinishedEvent`
    # emitted from inside that tool never fires for this path. We emit the
    # equivalent SSE line by hand here instead, since we already have
    # everything it needs.
    orch_results = pending.requests.build_results(
        calls={orch_call.tool_call_id: outcome.text}
    )

    async def resume_after_answer() -> AsyncGenerator[str]:
        yield _sse_line(
            {
                "type": "sub_agent_finished",
                "agent_name": meta.get("agent_name"),
                "summary": outcome.text,
            }
        )
        async for sse_line in _stream_orchestrator_run(
            deps,
            message_history=pending.message_history,
            deferred_tool_results=orch_results,
        ):
            yield sse_line

    return StreamingResponse(resume_after_answer(), media_type="text/event-stream")


@app.post("/api/reset")
async def reset() -> dict[str, str]:
    chat_state.message_history = []
    chat_state.pending_orchestrator = None
    chat_state.pending_sub_agent_runs.clear()
    return {"status": "reset"}


@app.get("/api/status")
async def status() -> dict[str, object]:
    return {
        "run_active": chat_state.active_run is not None,
        "history_length": len(chat_state.message_history),
        "waiting_for_answer": chat_state.pending_orchestrator is not None,
    }


def main() -> None:
    uvicorn.run(app, host="0.0.0.0", port=8000)


if __name__ == "__main__":
    main()
