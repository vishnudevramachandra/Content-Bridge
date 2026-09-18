from dataclasses import dataclass
from typing import Any

from pydantic_ai import RunContext
from pydantic_ai.capabilities import AbstractCapability
from pydantic_ai.messages import ToolCallPart
from pydantic_ai.tools import ToolDefinition
from pydantic_ai.toolsets import FunctionToolset

from contentbridge.agents.discovery.deps import AgentDeps
from ....utils.strapi_client import StrapiClient
from ....utils.wp_client import WPClient


def discover_wordpress() -> dict:
    """Fetch minimal WordPress post schema.

    Parameters
    ----------
    None

    Returns
    -------
    dict
        {"wp_schema": {"fields": {...}, "relations": set[str]}}
        Like DESCRIBE posts; includes meta sub-fields and taxonomy relations.

    """
    client = WPClient()
    schema = client.get_posts_schema()
    relations = client.get_taxonomy_rest_bases("post")
    fields: dict[str, dict] = {}
    for name, spec in schema["properties"].items():
        if name == "meta":
            continue
        fields[name] = spec
    meta_props = schema["properties"].get("meta", {}).get("properties", {})
    for name, spec in meta_props.items():
        fields[f"meta.{name}"] = spec
    return {"wp_schema": {"fields": fields, "relations": list(relations)}}


def discover_strapi() -> dict:
    """Fetch minimal Strapi schema for all user-defined content types.

    Parameters
    ----------
    None

    Returns
    -------
    dict
        {"strapi_schemas": [{"table": str, "uid": str, "columns": {...}}]}
        Like DESCRIBE for each `api::` table; no SELECT rows.

    """
    client = StrapiClient()
    result: list[dict] = []
    for uid in client.list_content_type_uids():
        schema = client.get_content_type_schema(uid)
        result.append({
            "table": schema["singularName"],
            "uid": uid,
            "columns": schema.get("attributes", {}),
        })
    return {"strapi_schemas": result}

@dataclass
class DatabaseOperations(AbstractCapability[Any]):
    def get_toolset(self) -> FunctionToolset:
        toolset = FunctionToolset()

        toolset.add_function(discover_strapi)
        toolset.add_function(discover_wordpress)

        return toolset

    async def before_tool_execute(
        self,
        ctx: RunContext[AgentDeps],
        *,
        call: ToolCallPart,
        tool_def: ToolDefinition,
        args: dict[str, Any],
    ) -> dict[str, Any]:
        if call.tool_name == "discover_strapi":
            ctx.deps.console.log(f"Discovering Strapi schemas")
        elif call.tool_name == "discover_wordpress":
            ctx.deps.console.log(f"Discovering WordPress schema")

        return args
