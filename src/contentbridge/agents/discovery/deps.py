from dataclasses import dataclass
import httpx

from rich.console import Console


@dataclass
class AgentDeps:
    console: Console
    http_client: httpx.AsyncClient
    search_api_key: str