import asyncio
import httpx

from pydantic_ai import Agent
from pydantic_ai.messages import ModelMessage
from pydantic_ai.models.openai import OpenAIResponsesModel
from pydantic_ai.providers.openai import OpenAIProvider
from rich.console import Console
from rich.markdown import Markdown

from contentbridge.agents.discovery.deps import AgentDeps
from contentbridge.agents.discovery.capabilities.file_operations import FileOperations
from contentbridge.agents.discovery.capabilities.web_search import SearchOperations
from contentbridge.agents.mapping.capabilities.mapping_operations import MappingOps
from contentbridge.utils.utils import get_env

_INSTRUCTIONS = (
    "You are a Mapping Agent for Content-Bridge.\n"
    "Refer to https://mapping-commons.github.io/sssom/dev/ "
    "for SSSOM vocabulary and mapping design.\n"
    "Read schema-ontology.ttl (created by discovery agent) "
    "to understand both ontology graphs.\n"
    "Approach: 1) schema-level matching (same entities, different names)"
    " — save to mapping-ontology.ttl immediately; 2) instance-based (use get_posts() to probe, "
    "then get_post() for specific fetch; reason over meta fields etc., "
    "considering transformations/combinations) — save after every mapping resolution. "
    "Treat mapping-ontology.ttl as a living document (agent reasoning so far).\n"
    "Use SSSOM mapping relations (appropriate to context).\n"
    "Save output to mapping-ontology.ttl; do not overwrite schema-ontology.ttl.\n"
    "Build ontology-to-ontology map incrementally.\n"
    "Do not invent mappings. When field matches are unclear or weak, "
    "instead of assuming a connection, skip that field, "
    "continue with others, then ask the user about skipped items at the end.\n"
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
            capabilities=[FileOperations(), MappingOps(), SearchOperations()],
            deps_type=AgentDeps,
        )

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
