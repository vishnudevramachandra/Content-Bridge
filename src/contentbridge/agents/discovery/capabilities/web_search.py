from dataclasses import dataclass
from typing import Any

from pydantic_ai import RunContext
from pydantic_ai.capabilities import AbstractCapability
from pydantic_ai.messages import ToolCallPart
from pydantic_ai.tools import ToolDefinition
from pydantic_ai.toolsets import FunctionToolset

from contentbridge.agents.discovery.deps import AgentDeps

async def search_tavily(
    ctx: RunContext[AgentDeps],
    query: str,
) -> dict:
    """Search the live internet for recent news, facts, or information.

    Parameters
    ----------
    query : str
        The search engine query string.

    Returns
    -------
    dict
        {
            "results": [
                {
                    "title": str,
                    "url": str,
                    "content": str,
                }
            ]
        }
    """

    url = "https://api.tavily.com/search"

    headers = {
        "Authorization": f"Bearer {ctx.deps.search_api_key}",
        "Content-Type": "application/json",
    }

    payload = {
        "query": query,
        "include_answer": False,
        "max_results": 3,
    }

    response = await ctx.deps.http_client.post(
        url,
        headers=headers,
        json=payload,
    )

    response.raise_for_status()

    data = response.json()

    results = []

    for result in data.get("results", []):
        results.append({
            "title": result.get("title", ""),
            "url": result.get("url", ""),
            "content": result.get("content", ""),
        })

    return {"results": results}


@dataclass
class SearchOperations(AbstractCapability[Any]):
    def get_toolset(self) -> FunctionToolset:
        toolset = FunctionToolset()

        toolset.add_function(search_tavily)

        return toolset

    async def before_tool_execute(
        self,
        ctx: RunContext[AgentDeps],
        *,
        call: ToolCallPart,
        tool_def: ToolDefinition,
        args: dict[str, Any],
    ) -> dict[str, Any]:
        if call.tool_name == "search_tavily":
            query = args.get("query", "")
            ctx.deps.console.log(
                f"Searching Tavily: {query}"
            )

        return args