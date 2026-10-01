from dataclasses import dataclass
from typing import Any

import requests
from pydantic_ai import RunContext
from pydantic_ai.capabilities import AbstractCapability
from pydantic_ai.messages import ToolCallPart
from pydantic_ai.tools import ToolDefinition
from pydantic_ai.toolsets import FunctionToolset

from contentbridge.agents.sync.deps import AgentDeps
from contentbridge.utils.wp_client import WORDPRESS_API, WPClient


def fetch_wp_record(post_id: int) -> dict:
    """Fetch one WP post by ID.

    Parameters
    ----------
    post_id : int
        The WordPress post ID.

    Returns
    -------
    dict
        The post record on success. On failure, an error dict shaped
        `{"error": <message>, "code": ..., "status": ..., "details":
        ..., "post_id": ...}`, with `error`/`code` taken directly from
        WP's own response (e.g. `{"error": "Invalid post ID.", "code":
        "rest_post_invalid_id", "status": 404, ...}`).
    """
    return WPClient().get_post(post_id)


def fetch_wp_posts(page: int = 1, per_page: int = 10) -> list[dict] | dict:
    """Fetch multiple WP posts (bulk query) with pagination.

    Parameters
    ----------
    page : int
        Page number for pagination (default 1).
    per_page : int
        Maximum posts per page (default 10). WP's REST API only accepts
        values from 1 to 100; anything outside that range is rejected by
        WP itself (see the error case below).

    Returns
    -------
    list[dict] | dict
        A list of post records on success. On failure, an error dict
        shaped `{"error": <message>, "code": ..., "status": ...,
        "details": ..., "page": ..., "per_page": ...}`, with
        `error`/`code`/`details` taken directly from WP's own response
        (e.g. an out-of-range `per_page` returns `"per_page must be
        between 1 (inclusive) and 100 (inclusive)"`).
    """
    return WPClient().get_posts(page=page, per_page=per_page)


def create_wp_post(title: str, content: str, meta: dict) -> dict:
    """Create a new WordPress post.

    Parameters
    ----------
    title : str
        The post title.
    content : str
        The post content (HTML/plain text, per WP's own handling).
    meta : dict
        Custom field values to set on the new post.

    Returns
    -------
    dict
        The created post record.
    """
    resp = requests.post(
        f"{WORDPRESS_API}/posts",
        json={"title": title, "content": content, "meta": meta},
        timeout=10,
    )
    resp.raise_for_status()
    return resp.json()


@dataclass
class WPOperations(AbstractCapability[Any]):
    def get_toolset(self) -> FunctionToolset:
        ts = FunctionToolset()
        ts.add_function(fetch_wp_record)
        ts.add_function(fetch_wp_posts)
        ts.add_function(create_wp_post)
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
        elif call.tool_name == "fetch_wp_posts":
            ctx.deps.console.log(f"Fetching WP posts: {args}")
        elif call.tool_name == "create_wp_post":
            ctx.deps.console.log(f"Creating WP post: {args}")

        return args
