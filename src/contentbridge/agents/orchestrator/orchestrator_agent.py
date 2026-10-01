import asyncio
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Literal

import httpx

from pydantic_ai import (
    Agent,
    CallDeferred,
    DeferredToolRequests,
    ModelRetry,
    RunContext,
    UnexpectedModelBehavior,
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
from contentbridge.utils.ontology import parse_mapping_ontology, parse_schema_ontology
from contentbridge.utils.utils import get_env

_SANDBOX_DIR = Path("sandbox")

_INSTRUCTIONS = (
    "You are the Orchestrator Agent for Content-Bridge.\n"
    "You coordinate three specialist sub-agents and decide which of them "
    "needs to run, in what order, based on the user's request and the "
    "current state of the pipeline's artifact files.\n"
    "\n"
    "THE PIPELINE:\n"
    "* 1. Discovery (tool: run_discovery_agent) reads a source system "
    "(Strapi or WordPress) and writes/updates schema-ontology.ttl — "
    "an OWL ontology describing that system's schema.\n"
    "* 2. Mapping (tool: run_mapping_agent) reads schema-ontology.ttl for "
    "both systems and writes/updates mapping-ontology.ttl — an SSSOM "
    "mapping between the two ontologies.\n"
    "* 3. Sync (tool: run_sync_agent) reads mapping-ontology.ttl to sync "
    "Strapi content to WordPress — e.g. a specific product ID, or a "
    "broader task like reacting to an expired certification by finding "
    "and updating the WordPress post(s) for its linked product(s).\n"
    "\n"
    "HOW TO DECIDE WHAT TO RUN:\n"
    "* Use search_files()/read_file() to check whether schema-ontology.ttl "
    "and mapping-ontology.ttl already exist in the sandbox before "
    "deciding whether Discovery or Mapping need to run again. Don't "
    "re-run a phase whose output already exists unless the user asks "
    "you to refresh it.\n"
    "* A direct request to sync one product needs a concrete Strapi "
    "product ID — if the user's request implies that but doesn't give "
    "one, ask for it instead of guessing. Other sync tasks (e.g. a "
    "system alert about an expired certification) may only give you an "
    "identifier like a certification's documentId — that's fine; "
    "delegate it as-is and let sync_agent resolve the specifics (which "
    "products, which WordPress posts) itself via its own tools, rather "
    "than you asking the human for IDs it can look up.\n"
    "* Each tool call delegates the exact instruction you give it to a "
    "specialist agent — phrase that instruction as a clear, complete "
    "task for that agent, since it has no visibility into this "
    "conversation beyond what you pass it.\n"
    "* After each delegated run, briefly summarize what happened before "
    "deciding the next step, and give the user a final summary once "
    "the requested work is done.\n"
    "\n"
    "WHEN A SUB-AGENT NEEDS CLARIFICATION:\n"
    "* A delegation tool (run_discovery_agent/run_mapping_agent/"
    "run_sync_agent) may come back saying the sub-agent is paused on a "
    "question instead of a summary, with a sub_agent_key. When that "
    "happens, relay that question to the human yourself using "
    "ask_user — you may rephrase it, but make clear which agent is "
    "asking (e.g. \"mapping_agent would like to know: ...\").\n"
    "* Once the human answers ask_user, decide for yourself whether their "
    "reply actually answers the pending question. If it does, call "
    "answer_sub_agent_question with that sub_agent_key and their answer "
    "to resume the sub-agent. If it doesn't (e.g. they asked you "
    "something unrelated, or didn't understand the question), respond "
    "to them yourself instead — don't forward it to the sub-agent; "
    "call ask_user again once you've addressed their side question, to "
    "get back to the pending one. The sub-agent just stays paused "
    "until you do call answer_sub_agent_question with a real answer.\n"
    "* answer_sub_agent_question may report the sub-agent is still not "
    "satisfied (another question) — relay that one with ask_user too "
    "and repeat.\n"
    "\n"
    "VISUALIZING THE ONTOLOGIES:\n"
    "* When the user asks to see, visualize, or summarize either "
    "ontology — or asks something like 'show me how Product maps to "
    "Post' — call get_ontology_data for the scope they're asking "
    "about (schema, mapping, or both) rather than read_file-ing the "
    "raw Turtle yourself.\n"
    "* Respond with a ```mermaid fenced code block (a classDiagram for "
    "the schema — classes and their properties — or a flowchart/graph "
    "for mappings — subject -> object edges labelled with the "
    "predicate and confidence) built from only the parts relevant to "
    "what they asked, trimmed for readability rather than dumping "
    "everything get_ontology_data returned. Keep any accompanying "
    "prose short; the diagram is the answer.\n"
    "* If get_ontology_data reports a file hasn't been generated yet, "
    "say so instead of inventing a diagram — Discovery/Mapping need to "
    "run first.\n"
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
    # `ask_user` below can raise `CallDeferred`, ending the run with
    # `DeferredToolRequests` instead of a final `str` — the *only* way
    # this agent's run ever pauses, whether for its own direct question
    # or one it's relaying from a paused sub-agent (see `_delegate` /
    # `answer_sub_agent_question`).
    output_type=[str, DeferredToolRequests],
)


@agent.tool
def ask_user(ctx: RunContext[AgentDeps], question: str) -> str:
    """Ask the human a question and pause until they answer.

    Use this both for your own direct questions (e.g. a missing Strapi
    product ID) and to relay a clarifying question from a delegated
    sub-agent (see `answer_sub_agent_question`). Calling this stops the
    current run: whoever is driving this agent sees a
    `DeferredToolRequests` result and must resume the run later with the
    human's answer as this tool's result.

    Parameters
    ----------
    question : str
        A single, concise question for the human. When relaying a
        sub-agent's question, phrase it so it's clear which agent is
        asking.

    """
    ctx.deps.console.log(f"[ask_user] {question!r}")
    raise CallDeferred(metadata={"question": question})


@agent.tool
def get_ontology_data(
    ctx: RunContext[AgentDeps], scope: Literal["schema", "mapping", "both"]
) -> dict[str, Any]:
    """Fetch the ontologies as structured JSON instead of raw Turtle text.

    Use this (rather than read_file) when the user wants to see,
    visualize, or get a summary of either ontology — the structured
    shape is what you build a trimmed mermaid diagram from (see
    VISUALIZING THE ONTOLOGIES in your instructions).

    Parameters
    ----------
    scope : {"schema", "mapping", "both"}
        Which ontology to fetch: "schema" for schema-ontology.ttl
        (classes/properties per system), "mapping" for
        mapping-ontology.ttl (SSSOM mappings with confidence), or
        "both".

    Returns
    -------
    dict
        `{"schema": {...}}`, `{"mapping": {"mappings": [...]}}`, or
        both, depending on `scope`. A file that hasn't been generated
        yet is reported as `{"error": "<file> has not been generated "
        "yet"}` under that key instead of raising.

    """
    ctx.deps.console.log(f"[get_ontology_data] scope={scope!r}")
    result: dict[str, Any] = {}

    if scope in ("schema", "both"):
        path = _SANDBOX_DIR / "schema-ontology.ttl"
        result["schema"] = (
            parse_schema_ontology(path)
            if path.exists()
            else {"error": "schema-ontology.ttl has not been generated yet"}
        )

    if scope in ("mapping", "both"):
        path = _SANDBOX_DIR / "mapping-ontology.ttl"
        result["mapping"] = (
            {"mappings": parse_mapping_ontology(path)}
            if path.exists()
            else {"error": "mapping-ontology.ttl has not been generated yet"}
        )

    return result


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

    The caller (`answer_sub_agent_question`) only invokes this once the
    *orchestrator's own* model has judged `answer` to actually address
    the pending question — but a sub-agent's model can still choke on a
    bad answer (e.g. `UnexpectedModelBehavior` after exhausting its
    output retries). Rather than let that crash the whole run, this
    treats it the same as "the sub-agent needs to ask again": the
    pending state is left untouched (still keyed by `sub_agent_key`) and
    `finished=False` is reported with an explanatory message instead of
    the sub-agent's own next question.
    """
    pending = deps.pending_sub_agent_runs[sub_agent_key]
    sub_call = pending.requests.calls[0]
    original_question = pending.requests.metadata.get(sub_call.tool_call_id, {}).get(
        "question", "the pending question"
    )
    sub_results = pending.requests.build_results(calls={sub_call.tool_call_id: answer})

    sub_agent = _DEFERRABLE_SUB_AGENTS[pending.agent_name]
    sub_deps = _build_sub_agent_deps(pending.agent_name, deps)

    try:
        result = await sub_agent.run(
            message_history=pending.message_history,
            deferred_tool_results=sub_results,
            deps=sub_deps,
        )
    except UnexpectedModelBehavior:
        return SubAgentAnswerOutcome(
            finished=False,
            text=(
                f"That didn't read as an answer to {original_question!r} — "
                "please answer it directly, or explain what's unclear about it."
            ),
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
    """Run one sub-agent to completion, or report that it's paused.

    Shared body for every `run_*_agent` delegation tool below. Unlike
    the sub-agent's own `ask_user` (which stops its run via
    `CallDeferred`), this never pauses the *orchestrator's* run itself —
    doing that unconditionally short-circuited the orchestrator's own
    reasoning about whatever the human typed next (see
    `answer_sub_agent_question` for why that was a problem). Instead, if
    the sub-agent paused, this saves its state and returns a message
    telling the orchestrator's own model to relay the question via its
    own `ask_user` and resume the sub-agent later via
    `answer_sub_agent_question`.

    A sub-agent can also fail outright while running (`UnexpectedModelBehavior`);
    that's reported back as text too, rather than crashing this run.
    """
    await ctx.emit(SubAgentStartedEvent(agent_name=agent_name, instruction=instruction))

    sub_agent = _DEFERRABLE_SUB_AGENTS[agent_name]
    deps = _build_sub_agent_deps(agent_name, ctx.deps)
    try:
        result = await sub_agent.run(instruction, deps=deps, usage=ctx.usage)
    except UnexpectedModelBehavior as e:
        return f"{agent_name} failed to complete this task: {e}"

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
        ctx.deps.console.log(
            f"[paused] {agent_name} (key={sub_agent_key}) needs clarification: "
            f"{question!r}"
        )
        return (
            f"{agent_name} needs clarification before it can continue:\n\n"
            f"{question!r}\n\n"
            "Relay this to the user with `ask_user` (you may rephrase it, but "
            f"make clear it's on behalf of {agent_name}). Once they reply with "
            "something that actually answers it, call "
            f"`answer_sub_agent_question(sub_agent_key={sub_agent_key!r}, "
            "answer=<their answer>)` to resume it. If their reply doesn't "
            "answer it — e.g. a side question, or something unrelated — "
            "respond to them yourself instead; don't call "
            "`answer_sub_agent_question` until you have a real answer."
        )

    await ctx.emit(SubAgentFinishedEvent(agent_name=agent_name, summary=result.output))
    return result.output


@agent.tool
async def answer_sub_agent_question(
    ctx: RunContext[AgentDeps], sub_agent_key: str, answer: str
) -> str:
    """Resume a sub-agent that's paused waiting on its `ask_user` question.

    Only call this once the human's reply (to a question you relayed via
    your own `ask_user`) actually answers the sub-agent's pending
    question. If it doesn't — they asked something unrelated, or
    clearly didn't understand the question — don't call this; respond
    to them yourself instead (`ask_user` again if needed). The
    sub-agent just stays paused until you do call this with a real
    answer.

    Parameters
    ----------
    sub_agent_key : str
        The id given to you in the delegation tool's "needs
        clarification" message.
    answer : str
        The human's answer, handed back as the sub-agent's `ask_user`
        tool result.

    Returns
    -------
    str
        The sub-agent's final summary if that answer finished it, or a
        message saying it still needs clarification (possibly because
        its model couldn't parse that answer) — in that case, relay the
        new text with `ask_user` and call this again once answered.
    """
    if sub_agent_key not in ctx.deps.pending_sub_agent_runs:
        raise ModelRetry(
            f"No sub-agent is currently paused under sub_agent_key={sub_agent_key!r}."
        )

    agent_name = ctx.deps.pending_sub_agent_runs[sub_agent_key].agent_name
    ctx.deps.console.log(
        f"[resuming] {agent_name} (key={sub_agent_key}) with answer: {answer!r}"
    )
    outcome = await resolve_ask_user_answer(ctx.deps, sub_agent_key, answer)

    if outcome.finished:
        ctx.deps.console.log(f"[resumed] {agent_name} (key={sub_agent_key}) finished")
        await ctx.emit(SubAgentFinishedEvent(agent_name=agent_name, summary=outcome.text))
        return f"{agent_name} is done:\n\n{outcome.text}"

    ctx.deps.console.log(
        f"[still paused] {agent_name} (key={sub_agent_key}) needs more: "
        f"{outcome.text!r}"
    )
    return (
        f"{agent_name} still needs clarification:\n\n{outcome.text}\n\n"
        "Relay this to the user via `ask_user`, then call "
        f"`answer_sub_agent_question(sub_agent_key={sub_agent_key!r}, "
        "answer=...)` again once they reply."
    )


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
        The Discovery agent's final summary of what it did, or — if it
        paused on its own `ask_user` instead of finishing — a message
        telling you to relay its question and resume it with
        `answer_sub_agent_question`.

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
        The Mapping agent's final summary of what it did, or — if it
        paused on its own `ask_user` instead of finishing — a message
        telling you to relay its question and resume it with
        `answer_sub_agent_question`.

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
        The Sync agent's final summary of what it did, or — if it
        paused on its own `ask_user` instead of finishing — a message
        telling you to relay its question and resume it with
        `answer_sub_agent_question`.

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

            # The orchestrator's own `ask_user` is the *only* way its run
            # ever pauses now — both for its own direct questions and to
            # relay a sub-agent's (see `_delegate` /
            # `answer_sub_agent_question`). Whatever the human types next
            # is just a normal answer to *that* tool call; the
            # orchestrator's own model decides what to do with it (answer
            # a sub-agent's question, ask again, or respond directly) on
            # the next turn — this loop doesn't need to know which.
            while isinstance(result.output, DeferredToolRequests):
                history = result.all_messages()
                call = result.output.calls[0]
                question = result.output.metadata.get(call.tool_call_id, {}).get(
                    "question", "The agent needs more information:"
                )
                answer = console.input(f"[question] {question}\n>> ")
                deferred_results = result.output.build_results(
                    calls={call.tool_call_id: answer}
                )
                result = await agent.run(
                    message_history=history,
                    deferred_tool_results=deferred_results,
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
