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

CONTENT_TYPES = {
    "product": "api::product.product",
    "standard": "api::standard.standard",
    "certification": "api::certification.certification",
}


def _login() -> str:
    resp = requests.post(
        f"{STRAPI_BASE_URL}/admin/login",
        json={"email": STRAPI_ADMIN_EMAIL, "password": STRAPI_ADMIN_PASSWORD},
        timeout=10,
    )
    resp.raise_for_status()
    return resp.json()["data"]["token"]


class StrapiClient:
    def __init__(self) -> None:
        self._token = _login()

    def _headers(self) -> dict:
        return {"Authorization": f"Bearer {self._token}"}

    def get_content_type_schema(self, uid: str) -> dict:
        resp = requests.get(
            f"{STRAPI_BASE_URL}/content-type-builder/content-types/{uid}",
            headers=self._headers(),
            timeout=10,
        )
        resp.raise_for_status()
        return resp.json()["data"]["schema"]

    def get_entries(self, uid: str, page_size: int = 100) -> list[dict]:
        resp = requests.get(
            f"{STRAPI_BASE_URL}/content-manager/collection-types/{uid}",
            headers=self._headers(),
            params={"populate": "*", "pageSize": page_size},
            timeout=10,
        )
        resp.raise_for_status()
        return resp.json()["results"]
