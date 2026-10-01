import asyncio
import httpx

from pydantic_ai import Agent, CallDeferred, DeferredToolRequests
from pydantic_ai.messages import ModelMessage
from pydantic_ai.models.openai import OpenAIResponsesModel
from pydantic_ai.providers.openai import OpenAIProvider
from rich.console import Console
from rich.markdown import Markdown

from contentbridge.agents.discovery.capabilities.file_operations import FileOperations
from contentbridge.agents.discovery.capabilities.web_search import SearchOperations
from contentbridge.agents.mapping.capabilities.mapping_operations import MappingOps
from contentbridge.agents.mapping.deps import AgentDeps
from contentbridge.utils.utils import get_env

_INSTRUCTIONS = (
    "You are a Mapping Agent for Content-Bridge.\n"
    "Refer to https://mapping-commons.github.io/sssom/dev/ "
    "for SSSOM vocabulary and mapping design.\n"
    "Read schema-ontology.ttl (created by discovery agent) "
    "to understand both ontology graphs.\n"
    "Before writing anything, check whether mapping-ontology.ttl already "
    "exists and read it — it is a living document of your reasoning so "
    "far, so incrementally extend it rather than re-deriving or "
    "duplicating mappings already recorded there.\n"
    "Approach:\n"
    "1) Schema-level matching (same entities, different names) — save to "
    "mapping-ontology.ttl immediately.\n"
    "2) Instance-based matching — probe real records on both sides: use "
    "fetch_wp_posts() to sample WordPress posts, then fetch_wp_record() "
    "for a specific post. Reason over its fields (including meta fields) "
    "and, considering transformations/combinations, hypothesize which "
    "Strapi column/s and value/s could correspond to it. Use "
    "get_strapi_schema() to confirm that column/s exist, then "
    "fetch_strapi_record() with a filter on it to fetch the candidate "
    "Strapi entries. Compare the actual field values returned from both "
    "sides to confirm or refine the mapping. Save after every mapping "
    "resolution.\n"
    "Use SSSOM mapping relations (appropriate to context), e.g. "
    "skos:exactMatch/closeMatch/broadMatch/narrowMatch or "
    "owl:equivalentClass/equivalentProperty as fits the confidence and "
    "semantics of the match. For each mapping, also record SSSOM "
    "provenance metadata — mapping_justification, confidence, and "
    "(for instance-based matches) subject_match_field/object_match_field "
    "— so the reasoning behind it is auditable later.\n"
    "Save output to mapping-ontology.ttl; do not overwrite schema-ontology.ttl.\n"
    "Build ontology-to-ontology map incrementally.\n"
    "Do not invent mappings. When field matches are unclear or weak, "
    "instead of assuming a connection, skip that field, "
    "continue with others, then use the ask_user() tool to ask about "
    "skipped items at the end (one concise question at a time) rather "
    "than guessing.\n"
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
    name="mapping_agent",
    instructions=_INSTRUCTIONS,
    capabilities=[FileOperations(), MappingOps(), SearchOperations()],
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
            search_api_key=get_env("SEARCH_API_KEY"),
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
