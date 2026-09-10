"""Discovery nodes: single-schema structural profiling.

=== LangGraph concept: nodes ===
A LangGraph "node" is just a Python callable: `def node(state: State) -> dict`.
You take the current state, do some work, and return a *partial* update —
the keys you return get merged into state (via whatever reducer each key's
type declares; plain overwrite by default). That's it. There's no base
class to inherit, no decorator required to make something "a node" — a node
becomes a node only once you register it with `graph.add_node(name, fn)` in
graph.py. Keeping these functions here, undecorated and framework-agnostic,
is deliberate: it means `discover_wordpress` and `discover_strapi` are just
functions you could unit-test or call from a REPL with zero LangGraph in
scope. That's a genuine strength of LangGraph's node model worth noting
early — the graph wiring is a thin, separable layer on top of ordinary code.

=== The Discovery/Mapping boundary, enforced here in code ===
Every ambiguity check in this file uses ONLY information visible from one
system's schema: is there a description string, and does the field
participate in a structural relation signal (WordPress's `_links`, Strapi's
`type: "relation"`). Nothing here ever asks "does this correspond to a field
in the other system" — that question needs both schemas in scope at once,
which only mapping.py is allowed to do.
"""

from __future__ import annotations

from . import wp_client
from .strapi_client import StrapiClient


def _ambiguous(description: str | None, has_relation: bool) -> bool:
    """The single-schema ambiguity rule, spelled out once so both discovery
    functions below apply the exact same test: ambiguous iff there's no
    description text AND the field doesn't participate in a relation."""
    no_description = not description
    return no_description and not has_relation


def discover_wordpress(state: dict) -> dict:
    schema = wp_client.get_posts_schema()
    # Which top-level field names are taxonomy-backed relations, derived
    # from WordPress's own /types + /taxonomies metadata (see wp_client) —
    # not a hand-authored {"categories": ..., "tags": ...} guess.
    relation_fields = wp_client.get_taxonomy_rest_bases("post")

    fields: dict[str, dict] = {}

    for name, spec in schema["properties"].items():
        if name == "meta":
            continue  # meta's sub-fields are handled below, individually
        description = spec.get("description") or ""
        has_relation = name in relation_fields
        fields[name] = {
            "location": "top-level",
            "type": spec.get("type"),
            # Sub-properties (e.g. title/content/excerpt/guid's nested
            # {"raw": ..., "rendered": ...} shape) are kept, not flattened
            # away, so Mapping can structurally detect "this is WordPress's
            # rendered-HTML-object convention" from `wp_schema` alone,
            # instead of re-fetching the raw OPTIONS schema itself.
            "properties": spec.get("properties"),
            "description": description,
            "has_relation": has_relation,
            "ambiguous": _ambiguous(description, has_relation),
        }

    meta_props = schema["properties"].get("meta", {}).get("properties", {})
    for name, spec in meta_props.items():
        description = spec.get("description") or ""
        # Custom post-meta is never relation-backed in WordPress's REST
        # representation — there is no taxonomy or `_links` entry a meta
        # field could possibly correspond to. That structural fact alone
        # (not any comparison to Strapi) is why `has_relation` is always
        # False here.
        fields[f"meta.{name}"] = {
            "location": "meta",
            "type": spec.get("type"),
            "description": description,
            "has_relation": False,
            "ambiguous": _ambiguous(description, False),
        }

    ambiguous = sorted(k for k, v in fields.items() if v["ambiguous"])
    return {
        "wp_schema": fields,
        "wp_ambiguous_fields": ambiguous,
    }


def discover_strapi(state: dict) -> dict:
    client = StrapiClient()
    content_types: dict[str, dict] = {}
    uids: dict[str, str] = {}
    ambiguous: list[str] = []

    # Enumerated live from Strapi's own content-type-builder API (see
    # strapi_client.list_content_type_uids), not a hardcoded
    # {"product": ..., "standard": ..., "certification": ...} dict — this
    # is what lets Discovery's Strapi side scale to N content types.
    for uid in client.list_content_type_uids():
        schema = client.get_content_type_schema(uid)
        short_name = schema["singularName"]
        fields: dict[str, dict] = {}
        for attr_name, attr_spec in schema["attributes"].items():
            description = attr_spec.get("description") or ""
            has_relation = attr_spec.get("type") == "relation"
            is_ambiguous = _ambiguous(description, has_relation)
            fields[attr_name] = {
                "type": attr_spec.get("type"),
                "unique": attr_spec.get("unique", False),
                "description": description,
                "has_relation": has_relation,
                "ambiguous": is_ambiguous,
            }
            if is_ambiguous:
                ambiguous.append(f"{short_name}.{attr_name}")
        content_types[short_name] = fields
        # Mapping needs the raw `api::x.x` uid to call get_entries(uid); kept
        # as a side table (short_name -> uid) rather than folding it into
        # `content_types` so that dict stays a pure field-map, easy to read.
        uids[short_name] = uid

    return {
        "strapi_schemas": content_types,
        "strapi_uids": uids,
        "strapi_ambiguous_fields": sorted(ambiguous),
    }
