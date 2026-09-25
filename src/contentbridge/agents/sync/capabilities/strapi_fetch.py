from dataclasses import dataclass
from typing import Any

from pydantic_ai import RunContext
from pydantic_ai.capabilities import AbstractCapability
from pydantic_ai.messages import ToolCallPart
from pydantic_ai.tools import ToolDefinition
from pydantic_ai.toolsets import FunctionToolset
from typing import Any

from contentbridge.utils.strapi_client import StrapiClient
from contentbridge.agents.sync.deps import AgentDeps


def fetch_strapi_product(product_id: str) -> dict:
    """Fetch a Strapi product by ID using StrapiClient.

    Parameters
    ----------
    product_id : str
        The Strapi product ID.

    Returns
    -------
    dict
        A product record/row from Strapi.
    """
    client = StrapiClient()
    # Fetch from api::product.product; filter by documentId or id
    entries = client.get_entries("api::product.product")
    for entry in entries:
        if str(entry.get("id")) == product_id or str(entry.get("documentId")) == product_id:
            return entry
    return {}


@dataclass
class StrapiFetch(AbstractCapability[Any]):
    def get_toolset(self) -> FunctionToolset:
        toolset = FunctionToolset()
        toolset.add_function(fetch_strapi_product)
        return toolset
