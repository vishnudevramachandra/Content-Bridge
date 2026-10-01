from dataclasses import dataclass
from typing import Any

from pydantic_ai import RunContext
from pydantic_ai.capabilities import AbstractCapability
from pydantic_ai.messages import ToolCallPart
from pydantic_ai.tools import ToolDefinition
from pydantic_ai.toolsets import FunctionToolset

from contentbridge.agents.sync.deps import AgentDeps
from contentbridge.utils.strapi_client import StrapiClient


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
class StrapiFetch(AbstractCapability[Any]):
    def get_toolset(self) -> FunctionToolset:
        toolset = FunctionToolset()
        toolset.add_function(get_strapi_schema)
        toolset.add_function(fetch_strapi_record)
        return toolset

    async def before_tool_execute(
        self,
        ctx: RunContext[AgentDeps],
        *,
        call: ToolCallPart,
        tool_def: ToolDefinition,
        args: dict[str, Any],
    ) -> dict[str, Any]:
        if call.tool_name == "fetch_strapi_record":
            ctx.deps.console.log(f"Fetching Strapi record: {args}")
        elif call.tool_name == "get_strapi_schema":
            ctx.deps.console.log(f"Fetching Strapi schema: {args}")

        return args
