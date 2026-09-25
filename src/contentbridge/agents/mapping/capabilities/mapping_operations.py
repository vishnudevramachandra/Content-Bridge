from pydantic_ai.toolsets import FunctionToolset
from contentbridge.utils.wp_client import WPClient

def fetch_wp_record(criteria: dict) -> dict:
    """Fetch one WP post by schema-derived criteria (e.g., {"postId": 42})."""
    client = WPClient()
    # Uses criteria keys matching schema-ontology fields
    return {"record": criteria, "source": "wordpress"}

from contentbridge.utils.strapi_client import StrapiClient

def fetch_strapi_record(uid: str, criteria: dict) -> dict:
    """Fetch one Strapi entry by uid and schema-derived criteria."""
    client = StrapiClient()
    return {"uid": uid, "criteria": criteria, "source": "strapi"}
