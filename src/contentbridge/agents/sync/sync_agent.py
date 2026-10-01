import asyncio
import httpx

from pydantic_ai import Agent, CallDeferred, DeferredToolRequests
from pydantic_ai.messages import ModelMessage
from pydantic_ai.models.openai import OpenAIResponsesModel
from pydantic_ai.providers.openai import OpenAIProvider
from rich.console import Console
from rich.markdown import Markdown

from contentbridge.agents.sync.deps import AgentDeps
from contentbridge.agents.sync.capabilities.file_operations import FileOperations
from contentbridge.agents.sync.capabilities.strapi_fetch import StrapiFetch
from contentbridge.agents.sync.capabilities.wp_client import WPOperations
from contentbridge.utils.utils import get_env

_INSTRUCTIONS = (
    "You are a Sync Agent for Content-Bridge.\n"
    "Read mapping-ontology.ttl to understand mappings (pay particular "
    "attention to links like owl:equivalentProperty).\n"
    "When given a Strapi product ID, fetch it, then create/update "
    "the WP post using ontology mappings — not hardcoded rules.\n"
    "Derive custom fields (e.g., slug) from mapped ontology properties.\n"
    "If the Strapi product ID is missing or you hit an ambiguity you "
    "can't resolve from the ontology or the fetched record, use the "
    "ask_user() tool to ask a single, concise question rather than "
    "guessing.\n"
)

# Module-level agent instance so it can be imported and delegated to
# (e.g. by the orchestrator agent) instead of only being driven by the
# interactive REPL in `run_agent()` below.
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
    name="sync_agent",
    instructions=_INSTRUCTIONS,
    capabilities=[FileOperations(), StrapiFetch(), WPOperations()],
    deps_type=AgentDeps,
    # `DeferredToolRequests` lets a run end early (via `ask_user` raising
    # `CallDeferred` below) instead of only ever producing a final `str`.
    output_type=[str, DeferredToolRequests],
)


@agent.tool_plain
def ask_user(question: str) -> str:
    """Ask the human a clarifying question and pause until they answer.

    Calling this stops the current run: whoever is driving this agent
    (e.g. the orchestrator) sees a `DeferredToolRequests` result and must
    resume the run later with the human's answer as this tool's result.

    Parameters
    ----------
    question : str
        A single, concise question for the human.

    """
    raise CallDeferred(metadata={"question": question})


async def run_agent() -> None:
    console = Console()

    async with httpx.AsyncClient() as http_client:

        deps = AgentDeps(
            console=console,
            http_client=http_client,
        )

        message_history: list[ModelMessage] | None = None

        while True:
            user_prompt = console.input(">> ")
            result = await agent.run(
                user_prompt, message_history=message_history, deps=deps
            )

            # `ask_user()` can defer the run instead of returning a plain
            # string; keep resuming with the human's answer until the
            # agent produces one.
            while isinstance(result.output, DeferredToolRequests):
                answers: dict[str, str] = {}
                for call in result.output.calls:
                    question = result.output.metadata.get(
                        call.tool_call_id, {}
                    ).get("question", "The agent needs more information:")
                    answers[call.tool_call_id] = console.input(
                        f"[question] {question}\n>> "
                    )
                deferred_results = result.output.build_results(calls=answers)

                result = await agent.run(
                    message_history=result.all_messages(),
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
