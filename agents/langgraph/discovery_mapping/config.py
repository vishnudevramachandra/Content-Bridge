"""Environment/config loading.

Nothing LangGraph-specific here — every framework we evaluate needs this
same plumbing (URLs, credentials, the shared SQLite path), so it's kept
separate from the graph itself.
"""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

# Repo root is four levels up from this file:
#   agents/langgraph/discovery_mapping/config.py -> agents/langgraph -> agents -> <repo root>
REPO_ROOT = Path(__file__).resolve().parents[3]
ENV_PATH = REPO_ROOT / ".env"

load_dotenv(ENV_PATH)

WORDPRESS_BASE_URL = f"http://localhost:{os.environ.get('WORDPRESS_PORT', '8080')}"
WORDPRESS_API = f"{WORDPRESS_BASE_URL}/wp-json/wp/v2"

STRAPI_BASE_URL = f"http://localhost:{os.environ.get('STRAPI_PORT', '1337')}"
STRAPI_ADMIN_EMAIL = os.environ["STRAPI_ADMIN_EMAIL"]
STRAPI_ADMIN_PASSWORD = os.environ["STRAPI_ADMIN_PASSWORD"]

OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY", "")
OPENROUTER_MODEL = os.environ.get("OPENROUTER_MODEL", "anthropic/claude-sonnet-5")
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"

# Single SQLite file at the repo root, deliberately shared by two independent
# consumers: our own `mapping_rules` table (the durable, content-addressed
# resolution cache) and LangGraph's SqliteSaver checkpointer (thread/step
# scoped run state). Same file, different tables — see README.md for why
# that's not the same thing wearing two names.
DB_PATH = REPO_ROOT / "mapping_rules.db"
