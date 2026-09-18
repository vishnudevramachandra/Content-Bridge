from dataclasses import dataclass
from typing import Any
from pydantic_ai.capabilities import AbstractCapability
from pydantic_ai.toolsets import FunctionToolset
from typing import Any
import requests
from contentbridge.utils.wp_client import WORDPRESS_API

def create_wp_post(title: str, content: str, meta: dict) -> dict:
    resp = requests.post(f"{WORDPRESS_API}/posts", json={"title": title, "content": content, "meta": meta}, timeout=10)
    resp.raise_for_status()
    return resp.json()

@dataclass
class WPOperations(AbstractCapability[Any]):
    def get_toolset(self) -> FunctionToolset:
        ts = FunctionToolset()
        ts.add_function(create_wp_post)
        return ts
