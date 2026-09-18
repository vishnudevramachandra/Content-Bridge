"""Thin WordPress REST client: like querying a relational DB's information_schema.

- `get_posts_schema()` — `DESCRIBE posts` (OPTIONS call): column types, descriptions.
- `get_posts()` — `SELECT * FROM posts` (actual rows for Mapping).
- `get_taxonomy_rest_bases()` — `SELECT foreign_key FROM relations` via WP's own metadata.
"""
from __future__ import annotations
import requests
from contentbridge.utils.utils import get_env

WORDPRESS_BASE_URL = f"http://localhost:{get_env('WORDPRESS_PORT')}"
WORDPRESS_API = f"{WORDPRESS_BASE_URL}/wp-json/wp/v2"

class WPClient:
    def get_posts_schema(self) -> dict:
        """Like `DESCRIBE posts`: declared column types and descriptions."""
        resp = requests.options(f"{WORDPRESS_API}/posts", timeout=10)
        resp.raise_for_status()
        return resp.json()["schema"]

    def get_posts(self, per_page: int = 100) -> list[dict]:
        """Like `SELECT * FROM posts`: actual rows."""
        resp = requests.get(f"{WORDPRESS_API}/posts", params={"per_page": per_page}, timeout=10)
        resp.raise_for_status()
        return resp.json()

    def get_taxonomy_rest_bases(self, post_type: str = "post") -> set[str]:
        """Like checking `FOREIGN KEY` relations: which schema fields link to taxonomies."""
        type_resp = requests.get(f"{WORDPRESS_API}/types/{post_type}", timeout=10)
        type_resp.raise_for_status()
        taxonomy_slugs = type_resp.json().get("taxonomies", [])
        tax_resp = requests.get(f"{WORDPRESS_API}/taxonomies", timeout=10)
        tax_resp.raise_for_status()
        all_taxonomies = tax_resp.json()
        return {all_taxonomies[slug]["rest_base"] for slug in taxonomy_slugs if slug in all_taxonomies}
