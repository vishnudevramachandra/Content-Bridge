from dataclasses import dataclass
from typing import Any

from pydantic_ai import RunContext
from pydantic_ai.capabilities import AbstractCapability
from pydantic_ai.messages import ToolCallPart
from pydantic_ai.tools import ToolDefinition
from pydantic_ai.toolsets import FunctionToolset

from contentbridge.agents.discovery.deps import AgentDeps
# from . import wp_client
from ....utils.strapi_client import StrapiClient


# def _ambiguous(description: str | None, has_relation: bool) -> bool:
#     """Ambiguity rule: like checking if a column has no COMMENT and no FOREIGN KEY — ambiguous."""
#     no_description = not description
#     return no_description and not has_relation


# def discover_wordpress(state: dict) -> dict:
#     schema = wp_client.get_posts_schema()
#     # Which top-level field names are taxonomy-backed relations, derived
#     # from WordPress's own /types + /taxonomies metadata (see wp_client) —
#     # not a hand-authored {"categories": ..., "tags": ...} guess.
#     relation_fields = wp_client.get_taxonomy_rest_bases("post")

#     fields: dict[str, dict] = {}

#     for name, spec in schema["properties"].items():
#         if name == "meta":
#             continue  # meta's sub-fields are handled below, individually
#         description = spec.get("description") or ""
#         has_relation = name in relation_fields
#         fields[name] = {
#             "location": "top-level",
#             "type": spec.get("type"),
#             # Sub-properties (e.g. title/content/excerpt/guid's nested
#             # {"raw": ..., "rendered": ...} shape) are kept, not flattened
#             # away, so Mapping can structurally detect "this is WordPress's
#             # rendered-HTML-object convention" from `wp_schema` alone,
#             # instead of re-fetching the raw OPTIONS schema itself.
#             "properties": spec.get("properties"),
#             "description": description,
#             "has_relation": has_relation,
#             "ambiguous": _ambiguous(description, has_relation),
#         }

#     meta_props = schema["properties"].get("meta", {}).get("properties", {})
#     for name, spec in meta_props.items():
#         description = spec.get("description") or ""
#         # Custom post-meta is never relation-backed in WordPress's REST
#         # representation — there is no taxonomy or `_links` entry a meta
#         # field could possibly correspond to. That structural fact alone
#         # (not any comparison to Strapi) is why `has_relation` is always
#         # False here.
#         fields[f"meta.{name}"] = {
#             "location": "meta",
#             "type": spec.get("type"),
#             "description": description,
#             "has_relation": False,
#             "ambiguous": _ambiguous(description, False),
#         }

#     ambiguous = sorted(k for k, v in fields.items() if v["ambiguous"])
#     return {
#         "wp_schema": fields,
#         "wp_ambiguous_fields": ambiguous,
#     }


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

        return args
