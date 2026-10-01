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
* A periodic background task polls Strapi for certifications whose
  `ExpiryDate` has passed. For each one not already alerted on: if a run
  is active, the alert is injected into it via `AgentRun.enqueue()`
  (picked up on the orchestrator's next model request); if the
  conversation is idle (no active run, no pending question), the worker
  starts a *new* orchestrator run itself, the same way `/api/chat` would,
  just with no SSE client attached. Either way the certification is
  marked alerted so it isn't repeated every tick — if a human is mid-
  conversation answering a pending question, the tick is skipped instead
  and retried later rather than lost or forced in.
* The orchestrator's own `ask_user` tool is the only way its run ever
  pauses — both for its own direct questions and to relay a question
  from a paused sub-agent (see `orchestrator_agent._delegate` /
  `answer_sub_agent_question`). That pause ends the run with
  `DeferredToolRequests`, which `POST /api/chat` surfaces as a
  `question` SSE event instead of `final`. `POST /api/answer` just
  resumes the orchestrator's own paused run with the human's answer as
  that tool's result — the orchestrator's own model then decides what
  to do with it (answer the sub-agent, ask again, or respond directly)
  on its next turn, continuing the same SSE streaming as normal.
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
)
from contentbridge.agents.orchestrator.pending import PendingSubAgentRun
from contentbridge.utils.strapi_client import StrapiClient
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
    the duration of one `/api/chat` request (or an autonomous run started
    by the periodic worker — see `_run_autonomous_alert`) so the periodic
    background task can tell whether one is already in flight.
    `pending_sub_agent_runs` and `pending_orchestrator` track at most one
    outstanding human question at a time — also consistent with there
    being a single conversation. `alerted_certification_ids` remembers
    which expired certifications the periodic worker has already surfaced
    (by Strapi `documentId`), so the same expiry doesn't re-trigger every
    tick forever.
    """

    def __init__(self) -> None:
        self.message_history: list[ModelMessage] = []
        self.active_run: AgentRun[AgentDeps, str] | None = None
        self.pending_sub_agent_runs: dict[str, PendingSubAgentRun] = {}
        self.pending_orchestrator: PendingOrchestratorRun | None = None
        self.alerted_certification_ids: set[str] = set()


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
            # The orchestrator called its own `ask_user` — either a direct
            # question, or one it's relaying on behalf of a paused
            # sub-agent (it phrases the question so either case is clear
            # to the human; see `orchestrator_agent.ask_user`).
            call = result.output.calls[0]
            question = result.output.metadata.get(call.tool_call_id, {}).get(
                "question"
            )
            chat_state.pending_orchestrator = PendingOrchestratorRun(
                message_history=result.all_messages(),
                requests=result.output,
            )
            yield _sse_line({"type": "question", "question": question})
        else:
            chat_state.message_history = result.all_messages()
            chat_state.pending_orchestrator = None
            yield _sse_line({"type": "final", "output": result.output})


def _sse_line(payload: dict[str, object]) -> str:
    return f"data: {json.dumps(payload, default=str)}\n\n"


def _format_expiry_alert(certifications: list[dict]) -> str:
    """Build the alert text handed to the orchestrator for newly-expired
    certifications.

    Deliberately reports only each certification's own fields (name,
    documentId, ExpiryDate) — not its linked products or anything else
    pulled from the Strapi response. Which products are linked, which
    WordPress posts those correspond to, and what (if anything) should
    change there are all things the agents are equipped to work out
    themselves (via run_sync_agent and the ontologies/Strapi/WordPress
    tools), not something this plain orchestration code should be
    pre-digesting or baking field-name assumptions about.
    """
    lines = ["SYSTEM ALERT: the following Strapi certifications have expired:"]
    for cert in certifications:
        lines.append(
            f"- '{cert.get('name')}' (documentId={cert.get('documentId')}) "
            f"expired on {cert.get('ExpiryDate')}."
        )
    lines.append(
        "For each one, use run_sync_agent to find its linked product(s) in "
        "Strapi, the corresponding WordPress post(s) via the ontologies, "
        "and update them to reflect the expired certification."
    )
    return "\n".join(lines)


async def _check_expired_certifications() -> list[dict]:
    """Query Strapi for expired certifications off the event loop thread
    (`StrapiClient` is `requests`-based, i.e. blocking) and report, rather
    than raise, any failure — one bad tick (Strapi briefly unreachable,
    rate-limited login, ...) shouldn't take down the periodic worker."""
    try:
        return await asyncio.to_thread(StrapiClient().get_expired_certifications)
    except Exception as e:
        console.log(f"[periodic check] failed to query Strapi for expired certifications: {e}")
        return []


async def _run_autonomous_alert(alert_text: str) -> None:
    """Start a fresh orchestrator run triggered by the periodic worker
    itself rather than a human request. Reuses `_stream_orchestrator_run`
    — same state bookkeeping (`chat_state.active_run`/`message_history`/
    `pending_orchestrator`) as `/api/chat` — just drained here with no SSE
    client attached; the orchestrator's own tool-call console logging is
    the visibility for this path. If it pauses on a question, it's
    recorded in `chat_state.pending_orchestrator` exactly as if a human
    had started it, answerable later via `/api/answer`.
    """
    async for _ in _stream_orchestrator_run(_build_deps(), user_prompt=alert_text):
        pass


async def _periodic_alert_worker() -> None:
    """Every few seconds, check Strapi for newly-expired certifications and
    alert the orchestrator about any that haven't been alerted on yet.

    Uses `priority="when_idle"` for the enqueue-into-active-run path
    deliberately: the default `"asap"` priority delivers at the *earliest*
    opportunity, which — for a run whose model turn takes longer than the
    alert interval — aborts and restarts the in-flight model request every
    tick, so the run never converges. `"when_idle"` instead waits until the
    agent would otherwise end, giving it one extra look at the alert
    without interrupting whatever it's already doing.
    """
    while True:
        await asyncio.sleep(_PERIODIC_ALERT_INTERVAL_SECONDS)

        expired = await _check_expired_certifications()
        new_expired = [
            cert
            for cert in expired
            if cert["documentId"] not in chat_state.alerted_certification_ids
        ]
        if not new_expired:
            continue

        alert_text = _format_expiry_alert(new_expired)

        active_run = chat_state.active_run
        if active_run is not None:
            active_run.enqueue(alert_text, priority="when_idle")
            chat_state.alerted_certification_ids.update(
                cert["documentId"] for cert in new_expired
            )
        elif chat_state.pending_orchestrator is None:
            # Idle: no one's chatting and nothing's pending — start a run
            # ourselves rather than waiting for a human to show up.
            chat_state.alerted_certification_ids.update(
                cert["documentId"] for cert in new_expired
            )
            asyncio.create_task(_run_autonomous_alert(alert_text))
        # else: a human is mid-conversation answering a pending question.
        # Leave these unmarked so they're retried next tick instead of
        # being lost or forced into an unrelated exchange.


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
    if chat_state.active_run is not None:
        # Guards against racing an autonomous run the periodic worker just
        # started (see `_run_autonomous_alert`) — both would otherwise
        # read/write the same `chat_state.message_history` concurrently.
        raise HTTPException(
            status_code=409,
            detail="A run is already in progress; try again shortly.",
        )

    return StreamingResponse(
        _stream_orchestrator_run(_build_deps(), user_prompt=text),
        media_type="text/event-stream",
    )


@app.post("/api/answer")
async def answer(payload: UserAnswerRequest) -> StreamingResponse:
    """Resume the orchestrator's own paused `ask_user` call with an answer.

    This is just a normal resume via `deferred_tool_results` — same as
    any other turn — because the orchestrator's `ask_user` is the only
    thing that ever pauses its run. Its own model decides on the next
    turn whether this answer actually resolves a relayed sub-agent
    question (calling `answer_sub_agent_question`), needs to be asked
    again, or should be responded to directly; `_stream_orchestrator_run`
    already handles all of those outcomes generically.
    """
    pending = chat_state.pending_orchestrator
    if pending is None:
        raise HTTPException(status_code=400, detail="No question is pending.")

    call = pending.requests.calls[0]
    deferred_results = pending.requests.build_results(
        calls={call.tool_call_id: payload.answer.strip()}
    )

    return StreamingResponse(
        _stream_orchestrator_run(
            _build_deps(),
            message_history=pending.message_history,
            deferred_tool_results=deferred_results,
        ),
        media_type="text/event-stream",
    )


@app.post("/api/reset")
async def reset() -> dict[str, str]:
    chat_state.message_history = []
    chat_state.pending_orchestrator = None
    chat_state.pending_sub_agent_runs.clear()
    chat_state.alerted_certification_ids.clear()
    return {"status": "reset"}


@app.get("/api/status")
async def status() -> dict[str, object]:
    return {
        "run_active": chat_state.active_run is not None,
        "history_length": len(chat_state.message_history),
        "waiting_for_answer": chat_state.pending_orchestrator is not None,
        "alerted_certifications": len(chat_state.alerted_certification_ids),
    }


def main() -> None:
    uvicorn.run(app, host="0.0.0.0", port=8000)


if __name__ == "__main__":
    main()
