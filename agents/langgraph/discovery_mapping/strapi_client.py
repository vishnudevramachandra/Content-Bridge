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

from .config import STRAPI_ADMIN_EMAIL, STRAPI_ADMIN_PASSWORD, STRAPI_BASE_URL

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


class StrapiClient:
    def __init__(self) -> None:
        self._token = _login()

    def _headers(self) -> dict:
        return {"Authorization": f"Bearer {self._token}"}

    def list_content_type_uids(self) -> list[str]:
        """Every user-defined (`api::`) content type this Strapi instance
        currently has, discovered live — not a hardcoded list. This is the
        piece that lets Discovery's Strapi side be agnostic to which (or
        how many) collections exist."""
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
        resp = requests.get(
            f"{STRAPI_BASE_URL}/content-type-builder/content-types/{uid}",
            headers=self._headers(),
            timeout=10,
        )
        resp.raise_for_status()
        return resp.json()["data"]["schema"]

    def get_content_type_configuration(self, uid: str) -> dict:
        """Strapi's own generic answer to "which attribute is this content
        type's human-readable name": `settings.mainField` on the
        content-manager configuration endpoint. Not every content type sets
        this (see vocab.pick_label_attribute for the fallback used when it's
        empty), but when it IS set it's the authoritative, self-declared
        answer — preferred over any convention-based guess."""
        resp = requests.get(
            f"{STRAPI_BASE_URL}/content-manager/content-types/{uid}/configuration",
            headers=self._headers(),
            timeout=10,
        )
        resp.raise_for_status()
        return resp.json()["data"]["contentType"]["settings"]

    def get_entries(self, uid: str, page_size: int = 100) -> list[dict]:
        resp = requests.get(
            f"{STRAPI_BASE_URL}/content-manager/collection-types/{uid}",
            headers=self._headers(),
            params={"populate": "*", "pageSize": page_size},
            timeout=10,
        )
        resp.raise_for_status()
        return resp.json()["results"]
