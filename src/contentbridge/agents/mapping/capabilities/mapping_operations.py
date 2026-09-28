from dataclasses import dataclass
from typing import Any

from pydantic_ai import RunContext
from pydantic_ai.capabilities import AbstractCapability
from pydantic_ai.messages import ToolCallPart
from pydantic_ai.tools import ToolDefinition
from pydantic_ai.toolsets import FunctionToolset

from contentbridge.agents.discovery.deps import AgentDeps
from contentbridge.utils.wp_client import WPClient
from contentbridge.utils.strapi_client import StrapiClient

def fetch_wp_record(post_id: int) -> dict:
    """Fetch one WP post by ID.

    Parameters
    ----------
    post_id : int
        The WordPress post ID.

    Returns
    -------
    dict
        The post record.
    """
    return WPClient().get_post(post_id)

def fetch_wp_posts(per_page: int = 10) -> list:
    """Fetch multiple WP posts (bulk query for mapping/probing).

    Parameters
    ----------
    per_page : int
        Maximum number of posts to retrieve (default 10).

    Returns
    -------
    list
        List of post record dicts.
    """
    return WPClient().get_posts(per_page=per_page)

def fetch_strapi_record(uid: str, entry_id: int) -> dict:
    """Fetch one Strapi entry by UID and entry ID.

    Parameters
    ----------
    uid : str
        The Strapi content type UID.
    entry_id : int
        The entry document ID.

    Returns
    -------
    dict
        The entry record.
    """
    return StrapiClient().get_entry(uid, entry_id)

@dataclass
class MappingOps(AbstractCapability[Any]):
    def get_toolset(self) -> FunctionToolset:
        ts = FunctionToolset()

        ts.add_function(fetch_wp_record)
        ts.add_function(fetch_strapi_record)
        ts.add_function(fetch_wp_posts)

        return ts

    async def before_tool_execute(
        self,
        ctx: RunContext[AgentDeps],
        *,
        call: ToolCallPart,
        tool_def: ToolDefinition,
        args: dict[str, Any],
    ) -> dict[str, Any]:
        if call.tool_name == "fetch_wp_record":
            ctx.deps.console.log(f"Fetching WP record: {args}")
        elif call.tool_name == "fetch_strapi_record":
            ctx.deps.console.log(f"Fetching Strapi record: {args}")
        elif call.tool_name == "fetch_wp_posts":
            ctx.deps.console.log(f"Fetching WP posts: {args}")

        return args