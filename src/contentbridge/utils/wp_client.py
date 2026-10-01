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

# WP's REST API requires auth for writes (creating/updating posts); reads
# don't need it, which is why only `create_post`/`update_post` below pass
# this. The login password in WP_ADMIN_PASSWORD can't be used directly for
# REST auth — this is a separate WP Application Password (see
# docker-compose.yml's WP_ENVIRONMENT_TYPE comment for why those even work
# here, over plain HTTP).
_WP_ADMIN_AUTH = (get_env("WP_ADMIN_USER"), get_env("WP_ADMIN_APP_PASSWORD"))


def _wp_error(resp: requests.Response, **extra: object) -> dict:
    """Build a structured error dict from a failed WP REST response, shared
    by every client method so callers/agents get one consistent shape
    (`error`/`code`/`status`/`details` plus call-specific fields like
    `post_id`) instead of a generic hardcoded message.

    Surfaces WP's own error body (e.g. `{"code": "rest_post_invalid_id",
    "message": "Invalid post ID.", "data": {...}}`) when present, since
    that's far more actionable than "WP fetch failed" for an agent trying
    to self-correct.
    """
    try:
        body = resp.json()
    except ValueError:
        body = {}
    return {
        "error": body.get("message", "WP request failed"),
        "code": body.get("code"),
        "status": resp.status_code,
        "details": body.get("data"),
        **extra,
    }


class WPClient:
    def get_posts_schema(self) -> dict:
        """Like `DESCRIBE posts`: declared column types and descriptions."""
        resp = requests.options(f"{WORDPRESS_API}/posts", timeout=10)
        resp.raise_for_status()
        return resp.json()["schema"]

    def get_taxonomy_rest_bases(self, post_type: str = "post") -> set[str]:
        """Like checking `FOREIGN KEY` relations: which schema fields link to taxonomies."""
        type_resp = requests.get(f"{WORDPRESS_API}/types/{post_type}", timeout=10)
        type_resp.raise_for_status()
        taxonomy_slugs = type_resp.json().get("taxonomies", [])
        tax_resp = requests.get(f"{WORDPRESS_API}/taxonomies", timeout=10)
        tax_resp.raise_for_status()
        all_taxonomies = tax_resp.json()
        return {all_taxonomies[slug]["rest_base"] for slug in taxonomy_slugs if slug in all_taxonomies}

    def get_posts(self, page: int = 1, per_page: int = 100) -> list[dict] | dict:
        """Like `SELECT * FROM posts`: actual rows with pagination.

        Returns a list of posts on success, or a structured error dict
        (see `_wp_error`) on failure, e.g. if `per_page` is outside WP's
        accepted 1-100 range.
        """
        resp = requests.get(f"{WORDPRESS_API}/posts", params={"page": page, "per_page": per_page}, timeout=10)
        try:
            resp.raise_for_status()
            return resp.json()
        except requests.HTTPError:
            return _wp_error(resp, page=page, per_page=per_page)

    def get_post(self, post_id: int) -> dict:
        """Fetch a single WP post by ID; return a structured error dict
        (see `_wp_error`) on any HTTP error, e.g. an unknown post_id."""
        resp = requests.get(f"{WORDPRESS_API}/posts/{post_id}", timeout=10)
        try:
            resp.raise_for_status()
            return resp.json()
        except requests.HTTPError:
            return _wp_error(resp, post_id=post_id)

    def create_post(self, title: str, content: str, meta: dict | None = None) -> dict:
        """Create a new WP post; return a structured error dict (see
        `_wp_error`) on any HTTP error, e.g. missing required fields."""
        payload: dict = {"title": title, "content": content}
        if meta is not None:
            payload["meta"] = meta
        resp = requests.post(f"{WORDPRESS_API}/posts", json=payload, auth=_WP_ADMIN_AUTH, timeout=10)
        try:
            resp.raise_for_status()
            return resp.json()
        except requests.HTTPError:
            return _wp_error(resp)

    def update_post(
        self,
        post_id: int,
        *,
        title: str | None = None,
        content: str | None = None,
        meta: dict | None = None,
    ) -> dict:
        """Partially update an existing WP post — only the fields passed
        (non-`None`) are sent, so e.g. `update_post(14, content="...")`
        changes the post's content and leaves its title/meta untouched.
        Returns a structured error dict (see `_wp_error`) on any HTTP
        error, e.g. an unknown post_id."""
        payload: dict = {}
        if title is not None:
            payload["title"] = title
        if content is not None:
            payload["content"] = content
        if meta is not None:
            payload["meta"] = meta
        resp = requests.post(
            f"{WORDPRESS_API}/posts/{post_id}", json=payload, auth=_WP_ADMIN_AUTH, timeout=10
        )
        try:
            resp.raise_for_status()
            return resp.json()
        except requests.HTTPError:
            return _wp_error(resp, post_id=post_id)
