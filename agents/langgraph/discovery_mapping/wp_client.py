"""Thin WordPress REST API client.

Two kinds of calls, both plain HTTP, no auth needed for public read access:

1. `get_posts_schema()` — OPTIONS on the collection endpoint. This is the
   *structural* description of the resource: every field's declared type,
   description string, and (for `meta`) the registered post-meta sub-fields.
2. `get_posts()` / `get_post()` — GET the actual content, including the
   `_links` hypermedia block, which is how WordPress represents relations
   (featured media, taxonomy terms, etc.) at the instance level rather than
   in the OPTIONS schema itself.

Discovery needs both: the schema for field-level structure, and one real
response to see which fields actually participate in `_links`.
"""

from __future__ import annotations

import requests

from .config import WORDPRESS_API


def get_posts_schema() -> dict:
    resp = requests.options(f"{WORDPRESS_API}/posts", timeout=10)
    resp.raise_for_status()
    return resp.json()["schema"]


def get_posts(per_page: int = 100) -> list[dict]:
    resp = requests.get(
        f"{WORDPRESS_API}/posts",
        params={"per_page": per_page, "_fields": "id,slug,title,content,meta"},
        timeout=10,
    )
    resp.raise_for_status()
    return resp.json()


def get_post(post_id: int) -> dict:
    """Full representation of a single post, including `_links` — used by
    Discovery to see which fields are relation-backed in practice."""
    resp = requests.get(f"{WORDPRESS_API}/posts/{post_id}", timeout=10)
    resp.raise_for_status()
    return resp.json()
