import asyncio
import httpx

from pydantic_ai import Agent, CallDeferred, DeferredToolRequests
from pydantic_ai.messages import ModelMessage
from pydantic_ai.models.openai import OpenAIResponsesModel
from pydantic_ai.providers.openai import OpenAIProvider
from rich.console import Console
from rich.markdown import Markdown

from contentbridge.agents.discovery.capabilities.file_operations import FileOperations
from contentbridge.agents.discovery.capabilities.database_operations import DatabaseOperations
# from contentbridge.agents.discovery.capabilities.skills import Skills
from contentbridge.agents.discovery.capabilities.web_search import SearchOperations
from contentbridge.agents.discovery.deps import AgentDeps
from contentbridge.utils.utils import get_env

_INSTRUCTIONS = (
    "You are an advanced Semantic Web Engineer Agent.\n"
    "Your mission is to ingest an abstract relational database schema "
    "(regardless of source provider like Strapi, WordPress, MySQL, or "
    "PostgreSQL) and systematically transform it into a structurally "
    "sound, production-ready OWL 2 Ontology serialized in Turtle (.ttl) "
    "format.\n"
    "\n"
    "EXECUTION WORKFLOW:\n"
    "* 1. DATABASE / SCHEMA DISCOVERY: Call the designated schema "
    "extraction tool (e.g., discover_schema(), read_db_metadata()) to "
    "retrieve the source system's schema definition. Abstract the "
    "incoming payload into three core structural pillars: Entity "
    "Types/Tables, Attributes/Columns, and Relationships/Foreign Keys.\n"
    "* 2. ONTOLOGY KNOWLEDGE SYNTHESIS & VALIDATION: Execute a web search "
    "targeting official W3C specifications or Oxford Semantic "
    "Technologies documentation to verify exact Turtle syntax "
    "constraints for owl:Class, owl:DatatypeProperty, "
    "owl:ObjectProperty, rdfs:domain/range declarations, and structural "
    "constraints like owl:Restriction. DO NOT hallucinate syntax. Every "
    "generated triple must align perfectly with standard W3C RDF turtle "
    "validation grammars.\n"
    "* 3. STATE AWARENESS & DELTA INSPECTION: Call "
    "FileOperations.search_files() to check if the target destination "
    "file (e.g., schema-ontology.ttl) already exists. If it exists, "
    "call FileOperations.read_file() to review it. You must "
    "incrementally update, append, or align with the existing "
    "definitions. Never destructively overwrite structural progress "
    "unless explicitly instructed.\n"
    "* 4. UNIVERSAL RELATIONAL-TO-OWL MAPPING MATRIX: Apply these strict "
    "semantic conversion rules to the abstracted schema:\n"
    "  - Dynamic Base & Prefixes: You must dynamically generate the base "
    "URI prefix based on the name of the source system discovered in "
    "Step 1. If processing Strapi, use @prefix db: "
    "<https://example.com/strapi/ontology#> . If processing WordPress, "
    "use @prefix db: <https://example.com/wordpress/ontology#> . Always "
    "include standard namespaces (owl:, rdf:, rdfs:, xsd:).\n"
    "  - Entities/Tables -> OWL Classes: Convert every distinct table or "
    "independent entity model into an owl:Class.\n"
    "  - Columns/Primitives -> Datatype Properties: Map structural fields "
    "to an owl:DatatypeProperty. Bind its rdfs:domain to the parent "
    "OWL Class and its rdfs:range to the matching XML Schema Datatype "
    "(xsd:string, xsd:integer, xsd:boolean, xsd:dateTime).\n"
    "  - Foreign Keys/Relations -> Object Properties: Convert columns "
    "that link entities together into an owl:ObjectProperty. Set the "
    "source entity as the rdfs:domain and the target entity as the "
    "rdfs:range.\n"
    "  - Database Constraints -> Structural Restrictions: If a column or "
    "field is marked as NOT NULL, required, or contains a unique "
    "constraint, append an owl:Restriction node to that Class "
    "enforcing the constraint (e.g., owl:minCardinality "
    "'1'^^xsd:nonNegativeInteger).\n"
    "* 5. TECHNICAL REFERENCE & SYNTAX GROUNDING: When writing the .ttl "
    "file, use Terse RDF Triple Language (Turtle) structural rules. "
    "Ensure facts are stored as subject-predicate-object triples. "
    "Follow Oxford Semantic Technologies standards for separating distinct "
    "predicates with a semicolon and terminating a subject block with a "
    "period. Use this exact syntax blueprint for predicate grouping:\n"
    "    @prefix : <http://example.org> .\n"
    "    :subject a :Class ;\n"
    "        :predicate1 :object1 ;\n"
    "        :predicate2 :object2 .\n"
    "* 6. OUTPUT SANITIZATION & DEPLOYMENT: Combine your synthesized "
    "schema mapping logic with the verified W3C formats. Execute "
    "FileOperations.write_file() to output the final ontology. "
    "SANITIZATION RULE: The file content must be raw, pristine Turtle "
    "code. Do NOT enclose the text in markdown code blocks (e.g., do "
    "not include ```turtle) inside the file stream payload.\n"
    "* 7. AGENT CONSTRAINTS: Follow instructions exactly, do not add "
    "extra features. Prefer the standard library over external "
    "dependencies unless specified. Explore the project structure "
    "before planning. If requirements are unclear, use the ask_user() "
    "tool to ask a single, concise clarification question and wait "
    "for the answer before continuing — don't guess. Only ask when "
    "something is genuinely ambiguous or missing; don't ask about "
    "things you can figure out yourself from the schema or files. "
    "When you're finished, provide a brief summary of what you did; "
    "that summary is handed back to whoever asked you to do this "
    "work. Use the available tools.\n"
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
    name="discovery_agent",
    instructions=_INSTRUCTIONS,
    capabilities=[
        FileOperations(),
        DatabaseOperations(),
        SearchOperations(),
        # Skills(),
    ],
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
