import asyncio
import uuid
from dataclasses import dataclass

import httpx

from pydantic_ai import (
    Agent,
    CallDeferred,
    DeferredToolRequests,
    RunContext,
)
from pydantic_ai.messages import ModelMessage
from pydantic_ai.models.openai import OpenAIResponsesModel
from pydantic_ai.providers.openai import OpenAIProvider
from rich.console import Console
from rich.markdown import Markdown

from contentbridge.agents.discovery.capabilities.file_operations import FileOperations
from contentbridge.agents.discovery.discovery_agent import agent as discovery_agent
from contentbridge.agents.discovery.deps import AgentDeps as DiscoveryDeps
from contentbridge.agents.mapping.mapping_agent import agent as mapping_agent
from contentbridge.agents.mapping.deps import AgentDeps as MappingDeps
from contentbridge.agents.sync.sync_agent import agent as sync_agent
from contentbridge.agents.sync.deps import AgentDeps as SyncDeps
from contentbridge.agents.orchestrator.deps import AgentDeps
from contentbridge.agents.orchestrator.events import (
    SubAgentFinishedEvent,
    SubAgentStartedEvent,
)
from contentbridge.agents.orchestrator.pending import PendingSubAgentRun
from contentbridge.utils.utils import get_env

_INSTRUCTIONS = (
    "You are the Orchestrator Agent for Content-Bridge.\n"
    "You coordinate three specialist sub-agents and decide which of them\n"
    "needs to run, in what order, based on the user's request and the\n"
    "current state of the pipeline's artifact files.\n"
    "\n"
    "THE PIPELINE:\n"
    "* 1. Discovery (tool: run_discovery_agent) reads a source system\n"
    "  (Strapi or WordPress) and writes/updates schema-ontology.ttl —\n"
    "  an OWL ontology describing that system's schema.\n"
    "* 2. Mapping (tool: run_mapping_agent) reads schema-ontology.ttl for\n"
    "  both systems and writes/updates mapping-ontology.ttl — an SSSOM\n"
    "  mapping between the two ontologies.\n"
    "* 3. Sync (tool: run_sync_agent) reads mapping-ontology.ttl and,\n"
    "  given a specific Strapi product ID, creates/updates the\n"
    "  corresponding WordPress post.\n"
    "\n"
    "HOW TO DECIDE WHAT TO RUN:\n"
    "* Use search_files()/read_file() to check whether schema-ontology.ttl\n"
    "  and mapping-ontology.ttl already exist in the sandbox before\n"
    "  deciding whether Discovery or Mapping need to run again. Don't\n"
    "  re-run a phase whose output already exists unless the user asks\n"
    "  you to refresh it.\n"
    "* Sync requires a concrete Strapi product ID. If the user's request\n"
    "  implies a sync but doesn't give one, ask for it instead of\n"
    "  guessing.\n"
    "* Each tool call delegates the exact instruction you give it to a\n"
    "  specialist agent — phrase that instruction as a clear, complete\n"
    "  task for that agent, since it has no visibility into this\n"
    "  conversation beyond what you pass it.\n"
    "* After each delegated run, briefly summarize what happened before\n"
    "  deciding the next step, and give the user a final summary once\n"
    "  the requested work is done.\n"
    "* A delegated agent may come back with a clarifying question\n"
    "  instead of a summary (e.g. Discovery asking for a base URL). When\n"
    "  that happens, the run pauses for a human to answer — you don't\n"
    "  need to do anything about it yourself; you'll be resumed with\n"
    "  that agent's summary once it's answered and the agent is done.\n"
)

# Module-level agent instance so it can be imported by the FastAPI app
# (or driven directly via its own REPL below).
_provider = OpenAIProvider(
    base_url=get_env("OPENAI_API_BASE"),
    api_key=get_env("OPENAI_API_KEY"),
)

_model = OpenAIResponsesModel(
    model_name=get_env("MODEL"),
    provider=_provider,
)

agent = Agent[AgentDeps](
    model=_model,
    name="orchestrator_agent",
    instructions=_INSTRUCTIONS,
    capabilities=[FileOperations()],
    deps_type=AgentDeps,
    # A delegation tool below can raise `CallDeferred` (when the sub-agent
    # it called did) so the orchestrator's own run can pause too, ending
    # with `DeferredToolRequests` instead of a final `str`.
    output_type=[str, DeferredToolRequests],
)

# Every sub-agent has an `ask_user` tool and `output_type=[str,
# DeferredToolRequests]`, so any of them can pause to ask the human a
# question. Extend this mapping (and `_build_sub_agent_deps` below) when
# a new sub-agent is added.
_DEFERRABLE_SUB_AGENTS = {
    "discovery_agent": discovery_agent,
    "mapping_agent": mapping_agent,
    "sync_agent": sync_agent,
}


def _build_sub_agent_deps(
    agent_name: str, deps: AgentDeps
) -> DiscoveryDeps | MappingDeps | SyncDeps:
    """Build the dependency object for one of the deferrable sub-agents."""
    if agent_name == "discovery_agent":
        return DiscoveryDeps(
            console=deps.console,
            http_client=deps.http_client,
            search_api_key=deps.search_api_key,
        )
    if agent_name == "mapping_agent":
        return MappingDeps(
            console=deps.console,
            http_client=deps.http_client,
            search_api_key=deps.search_api_key,
        )
    if agent_name == "sync_agent":
        return SyncDeps(console=deps.console, http_client=deps.http_client)
    raise ValueError(f"Unknown deferrable sub-agent: {agent_name!r}")


@dataclass
class SubAgentAnswerOutcome:
    """Result of resuming a paused sub-agent with the human's answer."""

    # True once the sub-agent is done (no more questions) — `text` is then
    # its final summary, ready to resume the orchestrator with. False
    # means the sub-agent asked another question — `text` is that
    # question, and the orchestrator itself is *not* touched; it's still
    # paused on the same delegation call.
    finished: bool
    text: str


async def resolve_ask_user_answer(
    deps: AgentDeps, sub_agent_key: str, answer: str
) -> SubAgentAnswerOutcome:
    """Resume whichever sub-agent is paused on `ask_user` with an answer.

    Looks up the sub-agent's saved `message_history` + pending
    `DeferredToolRequests` in `deps.pending_sub_agent_runs`, resumes its
    run with the human's answer, and reports whether it's now finished
    (so the caller can resume the orchestrator itself) or asked another
    question (so the caller can just show that question again).
    """
    pending = deps.pending_sub_agent_runs[sub_agent_key]
    sub_call = pending.requests.calls[0]
    sub_results = pending.requests.build_results(calls={sub_call.tool_call_id: answer})

    sub_agent = _DEFERRABLE_SUB_AGENTS[pending.agent_name]
    sub_deps = _build_sub_agent_deps(pending.agent_name, deps)

    result = await sub_agent.run(
        message_history=pending.message_history,
        deferred_tool_results=sub_results,
        deps=sub_deps,
    )

    if isinstance(result.output, DeferredToolRequests):
        # Still not done — save the new pending state under the same key
        # and report the new question. The orchestrator's own paused run
        # is untouched.
        deps.pending_sub_agent_runs[sub_agent_key] = PendingSubAgentRun(
            agent_name=pending.agent_name,
            message_history=result.all_messages(),
            requests=result.output,
        )
        next_call = result.output.calls[0]
        question = result.output.metadata.get(next_call.tool_call_id, {}).get(
            "question", "The agent needs more information:"
        )
        return SubAgentAnswerOutcome(finished=False, text=question)

    del deps.pending_sub_agent_runs[sub_agent_key]
    return SubAgentAnswerOutcome(finished=True, text=result.output)


async def _delegate(
    ctx: RunContext[AgentDeps], agent_name: str, instruction: str
) -> str:
    """Run one sub-agent to completion, or pause the orchestrator with it.

    Shared body for every `run_*_agent` delegation tool below: emits
    progress events, runs the sub-agent, and — if *it* paused on its own
    `ask_user` — saves its state and re-raises `CallDeferred` so the
    orchestrator's own run pauses too (see `resolve_ask_user_answer` for
    how that's resumed later).
    """
    await ctx.emit(SubAgentStartedEvent(agent_name=agent_name, instruction=instruction))

    sub_agent = _DEFERRABLE_SUB_AGENTS[agent_name]
    deps = _build_sub_agent_deps(agent_name, ctx.deps)
    result = await sub_agent.run(instruction, deps=deps, usage=ctx.usage)

    if isinstance(result.output, DeferredToolRequests):
        sub_agent_key = str(uuid.uuid4())
        ctx.deps.pending_sub_agent_runs[sub_agent_key] = PendingSubAgentRun(
            agent_name=agent_name,
            message_history=result.all_messages(),
            requests=result.output,
        )
        call = result.output.calls[0]
        question = result.output.metadata.get(call.tool_call_id, {}).get(
            "question", "The agent needs more information:"
        )
        raise CallDeferred(
            metadata={
                "sub_agent_key": sub_agent_key,
                "agent_name": agent_name,
                "question": question,
            }
        )

    await ctx.emit(SubAgentFinishedEvent(agent_name=agent_name, summary=result.output))
    return result.output


@agent.tool
async def run_discovery_agent(ctx: RunContext[AgentDeps], instruction: str) -> str:
    """Delegate a task to the Discovery agent.

    Use this to have the Discovery agent inspect a source system's schema
    (Strapi or WordPress) and write/update schema-ontology.ttl.

    Parameters
    ----------
    instruction : str
        A complete, self-contained task description for the Discovery
        agent (e.g. "Discover the Strapi schema and build its OWL
        ontology").

    Returns
    -------
    str
        The Discovery agent's final summary of what it did.

    Raises
    ------
    CallDeferred
        If the Discovery agent paused on its own `ask_user` tool instead
        of finishing. This propagates the pause up to the orchestrator's
        own run — see `resolve_ask_user_answer` for how it's resumed.

    """
    return await _delegate(ctx, "discovery_agent", instruction)


@agent.tool
async def run_mapping_agent(ctx: RunContext[AgentDeps], instruction: str) -> str:
    """Delegate a task to the Mapping agent.

    Use this to have the Mapping agent compare schema-ontology.ttl for both
    systems and write/update mapping-ontology.ttl.

    Parameters
    ----------
    instruction : str
        A complete, self-contained task description for the Mapping agent.

    Returns
    -------
    str
        The Mapping agent's final summary of what it did.

    Raises
    ------
    CallDeferred
        If the Mapping agent paused on its own `ask_user` tool instead of
        finishing — see `run_discovery_agent` for how this is resumed.

    """
    return await _delegate(ctx, "mapping_agent", instruction)


@agent.tool
async def run_sync_agent(ctx: RunContext[AgentDeps], instruction: str) -> str:
    """Delegate a task to the Sync agent.

    Use this to have the Sync agent push a specific Strapi product to
    WordPress using mapping-ontology.ttl. The instruction must include the
    Strapi product ID to sync.

    Parameters
    ----------
    instruction : str
        A complete, self-contained task description for the Sync agent,
        including the Strapi product ID.

    Returns
    -------
    str
        The Sync agent's final summary of what it did.

    Raises
    ------
    CallDeferred
        If the Sync agent paused on its own `ask_user` tool instead of
        finishing — see `run_discovery_agent` for how this is resumed.

    """
    return await _delegate(ctx, "sync_agent", instruction)


async def run_agent() -> None:
    """Drive the orchestrator agent from an interactive terminal REPL."""
    console = Console()

    async with httpx.AsyncClient() as http_client:
        deps = AgentDeps(
            console=console,
            http_client=http_client,
            search_api_key=get_env("SEARCH_API_KEY"),
            pending_sub_agent_runs={},
        )

        message_history: list[ModelMessage] | None = None

        while True:
            user_prompt = console.input(">> ")

            result = await agent.run(
                user_prompt, message_history=message_history, deps=deps
            )

            # A delegated sub-agent may pause on `ask_user`, which bubbles
            # up as the orchestrator's own `DeferredToolRequests` output.
            # Keep resuming — first the sub-agent, then (once it's done)
            # the orchestrator itself — until we get a final summary.
            while isinstance(result.output, DeferredToolRequests):
                orchestrator_history = result.all_messages()
                orch_call = result.output.calls[0]
                meta = result.output.metadata.get(orch_call.tool_call_id, {})
                sub_agent_key = meta["sub_agent_key"]
                question = meta.get("question", "The agent needs more information:")

                # Keep asking on behalf of the same paused sub-agent until
                # it stops asking and hands back a final summary.
                outcome = None
                while outcome is None or not outcome.finished:
                    answer = console.input(f"[question] {question}\n>> ")
                    outcome = await resolve_ask_user_answer(
                        deps, sub_agent_key, answer
                    )
                    question = outcome.text

                orch_results = result.output.build_results(
                    calls={orch_call.tool_call_id: outcome.text}
                )
                result = await agent.run(
                    message_history=orchestrator_history,
                    deferred_tool_results=orch_results,
                    deps=deps,
                )

            console.print(Markdown(result.output))

            message_history = result.all_messages()


def main() -> None:
    try:
        asyncio.run(run_agent())
    except (EOFError, KeyboardInterrupt):
        pass


if __name__ == "__main__":
    main()
