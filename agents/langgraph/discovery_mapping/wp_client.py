"""Thin WordPress REST API client. Plain HTTP, no auth needed for public
read access to this seed site.

- `get_posts_schema()` — OPTIONS on the collection endpoint. This is the
  *structural* description of the resource: every field's declared type,
  description string, and (for `meta`) the registered post-meta sub-fields.
- `get_posts()` — GET the actual content Mapping reasons over.
- `get_taxonomy_rest_bases()` — WordPress's own self-describing answer to
  "which schema fields are relations," via `/types` + `/taxonomies` rather
  than a hand-authored field-name map (see its docstring below).
"""

from __future__ import annotations

import requests

from .config import WORDPRESS_API


def get_posts_schema() -> dict:
    resp = requests.options(f"{WORDPRESS_API}/posts", timeout=10)
    resp.raise_for_status()
    return resp.json()["schema"]


def get_posts(per_page: int = 100) -> list[dict]:
    # No `_fields` filter: Mapping's Tier 2 pass (see mapping.py) needs
    # every schema-declared field's actual value, not a hand-picked subset —
    # trimming this to "the fields our examples happen to need" would be
    # exactly the kind of tailoring the rest of this build avoids.
    resp = requests.get(
        f"{WORDPRESS_API}/posts",
        params={"per_page": per_page},
        timeout=10,
    )
    resp.raise_for_status()
    return resp.json()


def get_taxonomy_rest_bases(post_type: str = "post") -> set[str]:
    """Which top-level schema field names are taxonomy-backed relations,
    derived from WordPress's own self-describing metadata rather than a
    hand-authored name map.

    `/wp/v2/types/{post_type}` lists which taxonomy slugs apply to this post
    type (e.g. "category", "post_tag"); `/wp/v2/taxonomies` maps each slug
    to the `rest_base` name it's actually exposed under in the post schema
    (e.g. "category" -> "categories"). Chaining the two gives the schema
    field names that are relations, without guessing "categories"/"tags"
    by hand — and it keeps working if a site adds custom taxonomies.
    """
    type_resp = requests.get(f"{WORDPRESS_API}/types/{post_type}", timeout=10)
    type_resp.raise_for_status()
    taxonomy_slugs = type_resp.json().get("taxonomies", [])

    tax_resp = requests.get(f"{WORDPRESS_API}/taxonomies", timeout=10)
    tax_resp.raise_for_status()
    all_taxonomies = tax_resp.json()

    return {
        all_taxonomies[slug]["rest_base"]
        for slug in taxonomy_slugs
        if slug in all_taxonomies
    }
