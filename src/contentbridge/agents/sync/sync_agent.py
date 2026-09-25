import asyncio
import httpx

from pydantic_ai import Agent
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
    "Read mapping-ontology.ttl to understand mappings (pay particular"
    "attention to links like owl:equivalentProperty).\n"
    "When given a Strapi product ID, fetch it, then create/update"
    "the WP post using ontology mappings — not hardcoded rules.\n"
    "Derive custom fields (e.g., slug) from mapped ontology properties.\n"
)

async def run_agent() -> None:
    console = Console()

    provider = OpenAIProvider(
        base_url=get_env("OPENAI_API_BASE"),
        api_key=get_env("OPENAI_API_KEY"),
    )

    model = OpenAIResponsesModel(
        model_name=get_env("MODEL"),
        provider=provider,
    )

    agent = Agent[AgentDeps](
        model=model,
        instructions=_INSTRUCTIONS,
        capabilities=[FileOperations(), StrapiFetch(), WPOperations()],
        deps_type=AgentDeps,
    )

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
            console.print(Markdown(result.output))
            message_history = result.all_messages()


def main() -> None:
    try:
        asyncio.run(run_agent())
    except (EOFError, KeyboardInterrupt):
        pass

if __name__ == "__main__":
    main()
