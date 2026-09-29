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
        The post record on success. On failure, an error dict shaped
        `{"error": <message>, "code": ..., "status": ..., "details":
        ..., "post_id": ...}`, with `error`/`code` taken directly from
        WP's own response (e.g. `{"error": "Invalid post ID.", "code":
        "rest_post_invalid_id", "status": 404, ...}`).
    """
    return WPClient().get_post(post_id)

def fetch_wp_posts(page: int = 1, per_page: int = 10) -> list[dict] | dict:
    """Fetch multiple WP posts (bulk query for mapping/probing) with pagination.

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

def get_strapi_schema(uid: str) -> dict:
    """Get Strapi content type schema by UID.

    Returns
    -------
    dict
        Schema dict or error dict.
    """
    return StrapiClient().get_content_type_schema(uid)

def fetch_strapi_record(uid: str, params: dict | None = None) -> dict:
    """Query Strapi entries by UID with optional filters/sort/pagination.

    Look up valid column names for `uid` with `get_strapi_schema` before
    writing `filters` — Strapi rejects unknown columns (see the `error`
    return case below), and only real attributes can be filtered on.

    Parameters
    ----------
    uid : str
        The Strapi content type UID.
    params : dict, optional
        Query params, all optional:
        - filters : dict
            Strapi filter conditions, each field mapped to an operator:
            `{"legacyId": {"$eq": 104}}`, `{"legacyId": {"$in": [1, 2, 3]}}`.
            Common operators: `$eq`, `$ne`, `$lt`, `$lte`, `$gt`, `$gte`,
            `$in`, `$notIn`, `$contains`, `$null`, `$notNull`.
            Combine conditions on different fields with the logical
            operators `$and` / `$or` / `$not`, each taking a list of
            filter dicts, e.g.
            `{"$or": [{"sku": {"$eq": "A"}}, {"sku": {"$eq": "B"}}]}`.
        - sort : list[str]
            e.g. `["legacyId:asc"]`.
        - page, pageSize : int
            Pagination. A "raw" query (no `filters`/`sort`, i.e. only
            `page`/`pageSize`/`populate`) is capped at `pageSize=10` to
            avoid accidentally dumping the whole table; queries that
            include `filters` or `sort` allow any `pageSize`.

    Returns
    -------
    dict
        On success, Strapi's response (`results` + `meta`). On failure,
        an error dict shaped `{"error": <message>, "code": ..., "uid":
        ..., "status": ..., "details": ...}` — either because the
        raw-query page_size cap above was exceeded, or because Strapi
        itself rejected the query (e.g. `{"error": "Invalid key
        notARealColumn", "code": "ValidationError", "status": 400,
        "details": {"key": "notARealColumn", ...}}`). `code` is a
        machine-readable error-type identifier (e.g. `"ValidationError"`,
        `"NotFoundError"`); re-check column names against
        `get_strapi_schema` and retry.
    """
    params = params or {}
    is_raw = not any(k not in ("page", "pageSize", "populate") for k in params)
    if is_raw and params.get("pageSize", 10) > 10:
        return {
            "error": "Raw query page_size > 10 not allowed",
            "code": "RawQueryPageSizeExceeded",
            "uid": uid,
            "status": 400,
            "details": {"pageSize": params.get("pageSize")},
        }
    return StrapiClient().query_entries(uid, params=params)

@dataclass
class MappingOps(AbstractCapability[Any]):
    def get_toolset(self) -> FunctionToolset:
        ts = FunctionToolset()

        ts.add_function(get_strapi_schema)
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