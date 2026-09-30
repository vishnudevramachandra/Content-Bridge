import asyncio
import httpx

from pydantic_ai import Agent, RunContext
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
        The Discovery agent's final summary of what it did.

    """
    await ctx.emit(
        SubAgentStartedEvent(agent_name="discovery_agent", instruction=instruction)
    )

    deps = DiscoveryDeps(
        console=ctx.deps.console,
        http_client=ctx.deps.http_client,
        search_api_key=ctx.deps.search_api_key,
    )
    result = await discovery_agent.run(instruction, deps=deps, usage=ctx.usage)

    await ctx.emit(
        SubAgentFinishedEvent(agent_name="discovery_agent", summary=result.output)
    )
    return result.output


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

    """
    await ctx.emit(
        SubAgentStartedEvent(agent_name="mapping_agent", instruction=instruction)
    )

    deps = MappingDeps(
        console=ctx.deps.console,
        http_client=ctx.deps.http_client,
    )
    result = await mapping_agent.run(instruction, deps=deps, usage=ctx.usage)

    await ctx.emit(
        SubAgentFinishedEvent(agent_name="mapping_agent", summary=result.output)
    )
    return result.output


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

    """
    await ctx.emit(
        SubAgentStartedEvent(agent_name="sync_agent", instruction=instruction)
    )

    deps = SyncDeps(
        console=ctx.deps.console,
        http_client=ctx.deps.http_client,
    )
    result = await sync_agent.run(instruction, deps=deps, usage=ctx.usage)

    await ctx.emit(
        SubAgentFinishedEvent(agent_name="sync_agent", summary=result.output)
    )
    return result.output


async def run_agent() -> None:
    """Drive the orchestrator agent from an interactive terminal REPL."""
    console = Console()

    async with httpx.AsyncClient() as http_client:
        deps = AgentDeps(
            console=console,
            http_client=http_client,
            search_api_key=get_env("SEARCH_API_KEY"),
        )

        message_history: list[ModelMessage] | None = None

        while True:
            user_prompt = console.input(">> ")

            result = await agent.run(
                user_prompt, message_history=message_history, deps=deps
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
