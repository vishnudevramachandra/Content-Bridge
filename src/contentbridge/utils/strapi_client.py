"""Thin Strapi client: admin auth + two kinds of introspection.

- `get_content_type_schema(uid)` hits the content-type-builder API, Strapi's
  equivalent of WordPress's OPTIONS call: the declared shape of a collection
  (attributes, types, relation targets) with no actual records involved.
- `get_entries(plural)` hits the content-manager API for real records
  (used by Mapping to read actual `legacyId`/`sku` values — Discovery never
  calls this one, since Discovery only looks at structure, not data).

Both require an admin JWT, which is why login happens once and the token is
reused (Strapi's admin JWT is short-lived-ish but plenty long for one CLI run).
"""

from __future__ import annotations

import requests

from contentbridge.utils.utils import get_env

# Strapi's content-type-builder "list all content types" endpoint returns
# EVERY content type the running instance knows about, including its own
# internal plugin/admin machinery (plugin::upload.file, admin::user, ...).
# `api::` is Strapi's own naming convention for "a content type this
# application defined" — filtering on it is a structural distinction Strapi
# itself draws, not a guess at which three types happen to matter for this
# demo. This is what makes Discovery's Strapi side scale to N content types
# instead of 3 without code changes: add a fourth `api::` content type to
# this Strapi instance, and it shows up here automatically.
API_UID_PREFIX = "api::"


# Cached at module scope, not per-instance: `discover_strapi` and
# `plan_mapping_tasks` each construct their own `StrapiClient()` (nodes are
# meant to be independent, self-contained callables — see mapping.py's
# docstring — so they don't share an object across the graph). Without this
# cache, that independence meant logging in twice per pipeline run, and
# Strapi's admin login endpoint is rate-limited (429s start after a
# handful of attempts) — hit during development by simply re-running
# discovery a few times in a row. One admin JWT is valid far longer than
# one CLI run needs, so reusing it across StrapiClient instances within the
# same process is the right fix, not a workaround.
_cached_token: str | None = None

STRAPI_BASE_URL = f"http://localhost:{get_env("STRAPI_PORT")}"
STRAPI_ADMIN_EMAIL = get_env("STRAPI_ADMIN_EMAIL")
STRAPI_ADMIN_PASSWORD = get_env("STRAPI_ADMIN_PASSWORD")

def _login() -> str:
    global _cached_token
    if _cached_token is not None:
        return _cached_token
    resp = requests.post(
        f"{STRAPI_BASE_URL}/admin/login",
        json={"email": STRAPI_ADMIN_EMAIL, "password": STRAPI_ADMIN_PASSWORD},
        timeout=10,
    )
    resp.raise_for_status()
    _cached_token = resp.json()["data"]["token"]
    return _cached_token


def _to_qs_pairs(params: dict) -> list[tuple[str, str]]:
    """Flatten a dict with nested dicts/lists (e.g. `{"filters": {"legacyId":
    {"$in": [1, 2]}}}`) into the bracket-notation pairs Strapi's `qs`-based
    query parser expects (`filters[legacyId][$in][0]=1&filters[legacyId][$in][1]=2`).

    `requests` has no built-in support for this: passed a nested dict as
    `params`, it silently mis-serializes it — for a dict value it iterates
    the *value's own keys* instead of recursing, so `{"filters": {"legacyId":
    ...}}` becomes the single pair `filters=legacyId` and the actual filter
    condition is dropped, which is why Strapi ignored filters entirely and
    returned every row instead of raising an error.
    """
    pairs: list[tuple[str, str]] = []

    def _walk(key: str, value) -> None:
        if isinstance(value, dict):
            for k, v in value.items():
                _walk(f"{key}[{k}]", v)
        elif isinstance(value, (list, tuple)):
            for i, v in enumerate(value):
                _walk(f"{key}[{i}]", v)
        elif isinstance(value, bool):
            pairs.append((key, "true" if value else "false"))
        elif value is not None:
            pairs.append((key, str(value)))

    for top_key, top_value in params.items():
        _walk(top_key, top_value)

    return pairs


def _strapi_error(resp: requests.Response, **extra: object) -> dict:
    """Build a structured error dict from a failed Strapi response, shared by
    every client method so callers/agents always get the same shape
    (`error`/`code`/`status`/`details` plus whatever call-specific fields the
    caller passes in, e.g. `uid`, `entry_id`) instead of each method
    inventing its own ad-hoc error format — and the same shape produced by
    `wp_client._wp_error`, so an agent handling errors from either backend
    doesn't need two different parsing branches.

    Surfaces Strapi's own error body (e.g. `{"error": {"name":
    "ValidationError", "message": "Invalid key notARealColumn", "details":
    {...}}}`) when present: `name` is Strapi's machine-readable error-type
    identifier (mapped to `code` here), analogous to WP's `code` field
    (e.g. `"rest_post_invalid_id"`).
    """
    try:
        detail = resp.json().get("error", {})
    except ValueError:
        detail = {}
    return {
        "error": detail.get("message", "Strapi request failed"),
        "code": detail.get("name"),
        "status": resp.status_code,
        "details": detail.get("details"),
        **extra,
    }


class StrapiClient:
    def __init__(self) -> None:
        self._token = _login()

    def _headers(self) -> dict:
        return {"Authorization": f"Bearer {self._token}"}

    def list_content_type_uids(self) -> list[str]:
        """Like `SELECT table_name FROM information_schema.tables` — returns
        all user-defined (`api::`) table names (e.g. `api::product.product`).
        `uid` = table name; filtering on `api::` excludes Strapi's internal
        plugin/admin tables."""
        resp = requests.get(
            f"{STRAPI_BASE_URL}/content-type-builder/content-types",
            headers=self._headers(),
            timeout=10,
        )
        resp.raise_for_status()
        return sorted(
            d["uid"] for d in resp.json()["data"] if d["uid"].startswith(API_UID_PREFIX)
        )

    def get_content_type_schema(self, uid: str) -> dict:
        """Like `DESCRIBE api::product.product` — returns the column schema
        (attributes, types, relations) for the given table (`uid`)."""
        resp = requests.get(
            f"{STRAPI_BASE_URL}/content-type-builder/content-types/{uid}",
            headers=self._headers(),
            timeout=10,
        )
        resp.raise_for_status()
        return resp.json()["data"]["schema"]

    def get_content_type_configuration(self, uid: str) -> dict:
        """Like reading a table's `COMMENT` / `mainField` metadata: which
        column is the display name? Returns settings dict; `mainField` may
        be empty (see `pick_label_attribute` fallback)."""
        resp = requests.get(
            f"{STRAPI_BASE_URL}/content-manager/content-types/{uid}/configuration",
            headers=self._headers(),
            timeout=10,
        )
        resp.raise_for_status()
        return resp.json()["data"]["contentType"]["settings"]

    def get_entries(self, uid: str, page_size: int = 100) -> list[dict]:
        """Like `SELECT * FROM table` (`uid` = table name) — returns actual rows."""
        resp = requests.get(
            f"{STRAPI_BASE_URL}/content-manager/collection-types/{uid}",
            headers=self._headers(),
            params={"populate": "*", "pageSize": page_size},
            timeout=10,
        )
        resp.raise_for_status()
        return resp.json()["results"]

    def query_entries(self, uid: str, params: dict | None = None) -> dict:
        """Query Strapi entries with arbitrary filters/sort/pagination.

        Filter-column validation is left to Strapi itself (via its 400
        response, surfaced below) rather than pre-checked against the schema
        here: a local check can only see top-level attribute names, so it
        would either need to special-case every Strapi filter operator
        (`$or`/`$and`/`$not`, ...) and relation/nested-field syntax, or reject
        valid queries that use them. Strapi's own validator already handles
        all of that correctly and is the authority on what's valid anyway.
        """
        query_params = {"populate": "*"}
        if params:
            query_params.update(params)
        resp = requests.get(
            f"{STRAPI_BASE_URL}/content-manager/collection-types/{uid}",
            headers=self._headers(),
            params=_to_qs_pairs(query_params),
            timeout=10,
        )
        try:
            resp.raise_for_status()
            return resp.json()
        except requests.HTTPError:
            return _strapi_error(resp, uid=uid)

    def get_entry(self, uid: str, entry_id: int | str) -> dict:
        """Fetch a single Strapi entry by numeric `id` or `documentId`.

        Strapi v5's content-manager single-entry endpoint is keyed by
        `documentId` (a string, e.g. `"uk5w2fa0..."`) — not the numeric `id`
        every record still has — so passing a numeric id straight into the
        URL 404s even for a real entry. When `entry_id` looks numeric (an
        `int`, or an all-digit `str`), this resolves it to a `documentId`
        via a filtered `query_entries` lookup first; a non-numeric `str` is
        assumed to already be a `documentId` and used as-is.
        """
        document_id = entry_id
        if isinstance(entry_id, int) or (isinstance(entry_id, str) and entry_id.isdigit()):
            lookup = self.query_entries(uid, params={"filters": {"id": {"$eq": entry_id}}, "pageSize": 1})
            if "error" in lookup:
                return {**lookup, "entry_id": entry_id}
            results = lookup.get("results", [])
            if not results:
                return {
                    "error": "Not Found",
                    "code": "NotFoundError",
                    "status": 404,
                    "details": {},
                    "uid": uid,
                    "entry_id": entry_id,
                }
            document_id = results[0]["documentId"]

        resp = requests.get(
            f"{STRAPI_BASE_URL}/content-manager/collection-types/{uid}/{document_id}",
            headers=self._headers(), timeout=10,
        )
        try:
            resp.raise_for_status()
            return resp.json()["data"]
        except requests.HTTPError:
            return _strapi_error(resp, uid=uid, entry_id=entry_id)
