"""Mapping nodes: the only place cross-system judgment happens.

Three functions matter here, and they map onto three different LangGraph
ideas:

- `plan_mapping_tasks` is a normal node. It's also the exact moment the
  pipeline crosses the Discovery/Mapping boundary: it's the first function
  in the whole codebase that fetches WordPress *and* Strapi data into the
  same scope and reasons about which Strapi entities a WordPress field or
  value could even plausibly correspond to. Discovery was never allowed to
  do this; Mapping is defined by being allowed to.

- `route_mapping_tasks` is a *conditional edge* function, registered with
  `add_conditional_edges`. LangGraph calls it with the current state after
  `plan_mapping_tasks` runs, and uses its return value to decide what
  happens next. Returning a plain node name is the simple case (the
  empty-task-list branch). Returning a list of `Send(...)` objects is
  LangGraph's dynamic fan-out primitive: each `Send` schedules one more
  invocation of `resolve_mapping_task`, with its own private input (just
  that one task's dict, not the whole graph state), and all of them run as
  part of the same superstep. This is the mechanism that would let this
  same graph handle 3 fields or 3,000 without changing shape — see
  README.md for the scalability discussion this enables.

- `resolve_mapping_task` is the node those `Send`s target. It's invoked once
  per task, each with only that task's dict as input — deliberately not the
  full graph state, which is why every task dict below is self-contained
  (it carries whatever evidence it needs, pre-computed by
  `plan_mapping_tasks`, rather than re-fetching or re-deriving it per task).

=== Why every field gets a task, not just Discovery's ambiguous ones ===
An earlier version of this file only looked at `state["wp_ambiguous_fields"]`
by literal name (`meta.get("related_product_ids", ...)`). Two problems with
that, both real: (1) hardcoding field names by string defeats the whole
point of Discovery being generic — a fourth ambiguous field would silently
never get examined; (2) restricting Mapping's attention to *only*
Discovery-flagged fields would make Discovery's ambiguous/not-ambiguous
split load-bearing in a way the corrected boundary never intended —
Discovery's flag says "this needs prose reasoning to explain," not "only
this needs checking." A field with a perfectly good WordPress-side
description (say, `categories`) could still, in principle, also correspond
to something in Strapi; nothing about having a description rules that out.

So every field Discovery reported gets *some* Mapping-level attention
below, but at two different costs:

- Tier 1 (ambiguous STRING fields + post body text): the full deterministic
  cascade; anything it can't resolve for free is handed off, unresolved, as
  a `residue` item for the agent tier (see README.md's escalation-ladder
  redesign) instead of being judged by an LLM call here.
- Tier 2 (every other field, including ambiguous integer/array fields):
  a cheap, deterministic-only check against Strapi attributes flagged
  `unique` (the one structural signal Strapi gives us for "this looks like
  an identifier"). It never calls an LLM: there is no sensible "ask an LLM
  whether this integer matches that integer" step — a match is either
  exactly present in real data or it isn't. Integer-shaped fields
  therefore always take this cheap path regardless of Discovery's
  ambiguous flag (that's how `meta.related_product_ids` gets resolved with
  zero LLM calls); the ambiguous flag only ever gates the STRING fallback,
  because a bare string is the one case where "no deterministic match"
  doesn't yet mean "no match" — it might mean "needs prose judgment."
"""

from __future__ import annotations

import re

from langgraph.types import Send

from . import store, vocab, wp_client
from .strapi_client import StrapiClient

_TAG_RE = re.compile(r"<[^>]+>")
_INT_TOKEN_RE = re.compile(r"[^0-9-]+")


def _strip_html(html: str) -> str:
    text = _TAG_RE.sub(" ", html)
    text = text.replace("&#8217;", "'").replace("&#038;", "&").replace("&#8211;", "-")
    return re.sub(r"\s+", " ", text).strip()


def _get_field_value(post: dict, field_name: str):
    """`field_name` is either a top-level key (e.g. "author") or
    "meta.<name>" (e.g. "meta.slug") — the same two shapes discovery.py
    uses when building `wp_schema`, so callers can iterate that dict
    directly without re-deriving which fields live under `meta`."""
    if field_name.startswith("meta."):
        return post.get("meta", {}).get(field_name[len("meta."):])
    return post.get(field_name)


def _parse_int_list(raw) -> list[int] | None:
    """Opportunistically read a value as a list of integers, regardless of
    its declared JSON-schema type.

    This matters because WordPress's custom-meta convention types every
    meta field as "string" in the OPTIONS schema (confirmed live:
    related_product_ids, slug, and footnotes are ALL declared
    `"type": "string"` — there is no meta-level "array of integers" type
    WordPress exposes). A schema-type-only rule would therefore never
    recognize "104,891,233" as a candidate integer list; it would only
    ever try string-matching the whole blob. Detecting "this string is
    actually a delimited list of integers" from the VALUE's own shape is
    what lets a comma-separated id field get treated as one on any field
    name, without hardcoding "related_product_ids" anywhere.
    """
    if isinstance(raw, list) and raw and all(isinstance(v, int) for v in raw):
        return list(raw)
    if not isinstance(raw, str) or not raw.strip():
        return None
    tokens = [t for t in _INT_TOKEN_RE.split(raw) if t not in ("", "-")]
    if not tokens:
        return None
    try:
        return [int(t) for t in tokens]
    except ValueError:
        return None


def _is_text_bearing(field_spec: dict) -> bool:
    """Structural detection of WordPress's "object with a rendered HTML
    string" shape (title, content, excerpt, guid all share it — confirmed
    live). No field names are hardcoded: any field matching this shape is
    treated as prose worth body-scanning."""
    if field_spec.get("type") != "object":
        return False
    props = field_spec.get("properties", {})
    return isinstance(props.get("rendered"), dict) and props["rendered"].get("type") == "string"


def _build_unique_indices(strapi_schemas: dict, entries_by_type: dict[str, list[dict]]):
    """Every (content_type, attribute) pair Strapi itself flagged `unique`,
    turned into a value -> documentId lookup built from real entries.

    This is the one structural signal Strapi gives for "this attribute
    looks like an identifier" — using it (rather than attribute names like
    "legacyId"/"sku") is what makes the matcher below work against any
    Strapi content type, including ones that don't exist yet.
    """
    int_indices: list[tuple[str, str, dict[int, str]]] = []
    string_indices: list[tuple[str, str, dict[str, str]]] = []

    for content_type, attrs in strapi_schemas.items():
        entries = entries_by_type.get(content_type, [])
        for attr_name, spec in attrs.items():
            if not spec.get("unique"):
                continue
            attr_type = spec.get("type")
            if attr_type in ("integer", "biginteger"):
                value_map = {
                    e[attr_name]: e["documentId"]
                    for e in entries
                    if isinstance(e.get(attr_name), int)
                }
                if value_map:
                    int_indices.append((content_type, attr_name, value_map))
            elif attr_type == "string":
                value_map = {
                    e[attr_name].lower(): e["documentId"]
                    for e in entries
                    if isinstance(e.get(attr_name), str) and e[attr_name]
                }
                if value_map:
                    string_indices.append((content_type, attr_name, value_map))
    return int_indices, string_indices


def _match_ints(values: list[int], int_indices) -> dict | None:
    """Best match across every unique-integer attribute: the one with the
    most values from `values` actually present in its real data. Iterating
    every discovered index rather than a hardcoded ("product", "legacyId")
    pair is what lets this generalize past the current three content
    types."""
    best = None
    for content_type, attr_name, value_map in int_indices:
        hits = {v: value_map[v] for v in values if v in value_map}
        if not hits:
            continue
        if best is None or len(hits) > len(best["matched_refs"]):
            best = {
                "content_type": content_type,
                "attribute": attr_name,
                "matched_refs": sorted(hits.values()),
                "confidence": len(hits) / len(values),
            }
    return best


def _match_string(value: str, string_indices) -> dict | None:
    lowered = value.lower()
    for content_type, attr_name, value_map in string_indices:
        if lowered in value_map:
            return {
                "content_type": content_type,
                "attribute": attr_name,
                "matched_refs": [value_map[lowered]],
                "confidence": 1.0,
            }
    return None


def _fuzzy_candidates(value: str, token_index: dict, exclude=frozenset()) -> list[dict]:
    seen = set(exclude)
    candidates = []
    for token in vocab.tokenize(value):
        for entity in token_index.get(token, []):
            key = (entity.content_type, entity.ref)
            if key in seen:
                continue
            seen.add(key)
            candidates.append({"content_type": entity.content_type, "ref": entity.ref, "label": entity.label})
    return candidates


def plan_mapping_tasks(state: dict) -> dict:
    posts = wp_client.get_posts()
    client = StrapiClient()

    strapi_schemas = state["strapi_schemas"]
    strapi_uids = state["strapi_uids"]
    entries_by_type = {
        content_type: client.get_entries(uid) for content_type, uid in strapi_uids.items()
    }
    int_indices, string_indices = _build_unique_indices(strapi_schemas, entries_by_type)

    # The body-scan vocabulary: real entity labels, from real data, across
    # every discovered content type — see vocab.py. `label_attr` prefers
    # Strapi's own `settings.mainField` and falls back to a schema
    # convention only when that isn't set.
    entities = []
    for content_type, uid in strapi_uids.items():
        main_field = client.get_content_type_configuration(uid).get("mainField")
        label_attr = main_field or vocab.pick_label_attribute(strapi_schemas[content_type])
        entities.extend(vocab.build_entities(content_type, label_attr, entries_by_type[content_type]))
    token_index = vocab.build_token_index(entities)

    ambiguous_fields = set(state["wp_ambiguous_fields"])
    wp_schema = state["wp_schema"]
    tasks: list[dict] = []

    # --- Field-level tasks: every WP field Discovery reported, not just
    # the ambiguous ones (see module docstring for why). ---
    for field_name, spec in wp_schema.items():
        if _is_text_bearing(spec):
            continue  # handled by the body-scan pass below instead

        is_ambiguous = field_name in ambiguous_fields
        match_by_post: dict[int, dict] = {}
        schema_match = None

        for post in posts:
            raw = _get_field_value(post, field_name)
            if raw in (None, "", [], {}):
                continue

            if isinstance(raw, bool):
                continue  # no sensible identifier-matching semantics for booleans
            int_list = _parse_int_list(raw) or ([raw] if isinstance(raw, int) else None)
            if int_list:
                match = _match_ints(int_list, int_indices)
                match_by_post[post["id"]] = {"kind": "int", "values": int_list, "match": match}
            elif isinstance(raw, str):
                match = _match_string(raw, string_indices)
                entry = {"kind": "string", "values": [raw], "match": match}
                if not match and is_ambiguous:
                    # Deterministic check failed on a field Discovery
                    # couldn't self-explain from its own schema alone —
                    # this is the free-text/ambiguous-naming case (e.g.
                    # meta.slug). Candidates come from tokenizing the VALUE
                    # itself against the real-data vocabulary, exactly the
                    # same mechanism the body scan uses.
                    entry["fuzzy_candidates"] = _fuzzy_candidates(raw, token_index)
                match_by_post[post["id"]] = entry
            else:
                continue

            if match_by_post[post["id"]]["match"] and schema_match is None:
                schema_match = match_by_post[post["id"]]["match"]

        tasks.append({
            "kind": "field_match",
            "field_name": field_name,
            "match_by_post": match_by_post,
            "schema_match": schema_match,
        })

    # --- Body-scan tasks: one per post, over every text-bearing field
    # (title/content/excerpt/... — detected structurally above). ---
    text_fields = [name for name, spec in wp_schema.items() if _is_text_bearing(spec)]
    for post in posts:
        raw_parts = [
            _strip_html(post[name]["rendered"])
            for name in text_fields
            if isinstance(post.get(name), dict) and post[name].get("rendered")
        ]
        full_text = " ".join(raw_parts)
        if not full_text:
            continue

        lower_text = full_text.lower()
        exact_hits = [e for e in entities if e.label and e.label.lower() in lower_text]
        exact_keys = {(e.content_type, e.ref) for e in exact_hits}
        fuzzy = _fuzzy_candidates(full_text, token_index, exclude=exact_keys)
        # Group fuzzy candidates by the token that surfaced them so that
        # each distinct mention gets its own, independently cacheable
        # judgment — two different tokens in the same post are two
        # different resolutions, not one.
        fuzzy_by_token: dict[str, list[dict]] = {}
        for token in vocab.tokenize(full_text):
            for entity in token_index.get(token, []):
                key = (entity.content_type, entity.ref)
                if key in exact_keys:
                    continue
                fuzzy_by_token.setdefault(token, [])
                cand = {"content_type": entity.content_type, "ref": entity.ref, "label": entity.label}
                if cand not in fuzzy_by_token[token]:
                    fuzzy_by_token[token].append(cand)

        tasks.append({
            "kind": "body_scan",
            "post_id": post["id"],
            "exact_hits": [
                {"content_type": e.content_type, "ref": e.ref, "label": e.label} for e in exact_hits
            ],
            "fuzzy_by_token": fuzzy_by_token,
        })

    return {"mapping_tasks": tasks}


def route_mapping_tasks(state: dict):
    """=== LangGraph concept: conditional edges + Send ===

    This function's return value, not a fixed graph edge, decides what runs
    next. An empty task list (nothing needed mapping this run) routes
    straight to "summarize" — a plain node-name return. Otherwise, a list of
    `Send("resolve_mapping_task", task)` fans out one graph step per task,
    all executing as part of the same superstep. Whether `mapping_tasks` has
    3 entries or 3,000, this function's shape doesn't change — see
    README.md.
    """
    tasks = state.get("mapping_tasks", [])
    if not tasks:
        return "summarize"
    return [Send("resolve_mapping_task", task) for task in tasks]


def _resolve_or_defer(
    conn, *, source_content_type: str, source_ref: str, evidence: str,
    candidates: list[dict], post_id: int,
) -> tuple[dict | None, dict | None]:
    """Look up an already-committed decision for `source_ref`; if none
    exists, either resolve it for free (no candidates -> confident
    no-match) or hand it back as an unresolved residue item for the agent
    tier to pick up.

    Returns `(resolution, residue)` — exactly one of the two is non-None.
    Nothing in this function calls the LLM; that responsibility moved to
    the agent tier (see README.md's escalation-ladder redesign) once a
    genuinely ambiguous case can't be settled by a free deterministic
    check. This is the direct fix for Bug 6's isolated-per-token LLM call:
    that call site is gone, not just relocated.
    """
    cached = store.lookup(conn, "wordpress", source_content_type, source_ref)
    if cached:
        return cached, None

    if not candidates:
        # Nothing even fuzzily plausible — a confident, cheap, non-LLM
        # conclusion, not a punt. Still fully resolved by tier 1.
        resolution = store.record(
            conn,
            source_system="wordpress", source_content_type=source_content_type,
            source_ref=source_ref, evidence=evidence,
            target_system=None, target_content_type=None, target_ref=None,
            confidence=0.0, method="no_match_confirmed",
        )
        return resolution, None

    # Genuinely ambiguous: tier 1 can't settle this for free. Defer to the
    # agent tier instead of guessing here — nothing is written to
    # mapping_rules yet, and no LLM is called.
    residue_item = {
        "source_content_type": source_content_type,
        "source_ref": source_ref,
        "evidence": evidence,
        "candidates": candidates,
        "post_id": post_id,
    }
    return None, residue_item


def _resolve_field_match(conn, task: dict) -> tuple[list[dict], list[dict]]:
    field_name = task["field_name"]
    results = []
    residue = []
    schema_ref = f"schema:{field_name}"

    if task["schema_match"] is None:
        cached = store.lookup(conn, "wordpress", "post", schema_ref)
        results.append(cached or store.record(
            conn,
            source_system="wordpress", source_content_type="post", source_ref=schema_ref,
            evidence=f"no real-data overlap found for field '{field_name}' across the corpus",
            target_system=None, target_content_type=None, target_ref=None,
            confidence=0.0, method="no_match_confirmed",
        ))
    else:
        match = task["schema_match"]
        cached = store.lookup(conn, "wordpress", "post", schema_ref)
        results.append(cached or store.record(
            conn,
            source_system="wordpress", source_content_type="post", source_ref=schema_ref,
            evidence=f"field '{field_name}' values overlap {match['content_type']}.{match['attribute']} real data",
            target_system="strapi", target_content_type=match["content_type"], target_ref=None,
            confidence=match["confidence"], method="schema_declared",
        ))

    # Per-post rows: apply the (established, or absent) schema-level rule
    # to each post's own value. An established rule turns into a plain
    # value lookup (no judgment left to make); a field with no rule but a
    # genuinely ambiguous string value defers to the agent tier instead of
    # calling the LLM here.
    for post_id, per_post in task["match_by_post"].items():
        source_ref = f"post:{post_id}:{field_name}"
        if per_post["match"]:
            cached = store.lookup(conn, "wordpress", "post", source_ref)
            results.append(cached or store.record(
                conn,
                source_system="wordpress", source_content_type="post", source_ref=source_ref,
                evidence=f"{field_name}={per_post['values']!r}",
                target_system="strapi", target_content_type=per_post["match"]["content_type"],
                target_ref=",".join(per_post["match"]["matched_refs"]),
                confidence=per_post["match"]["confidence"],
                method="value_range_match" if per_post["kind"] == "int" else "exact_string_match",
            ))
        elif "fuzzy_candidates" in per_post:
            resolution, residue_item = _resolve_or_defer(
                conn,
                source_content_type="post", source_ref=source_ref,
                evidence=f"{field_name}={per_post['values'][0]!r}",
                candidates=per_post["fuzzy_candidates"], post_id=post_id,
            )
            if resolution:
                results.append(resolution)
            if residue_item:
                residue.append(residue_item)
    return results, residue


def _resolve_body_scan(conn, task: dict) -> tuple[list[dict], list[dict]]:
    post_id = task["post_id"]
    results = []
    residue = []

    for hit in task["exact_hits"]:
        source_ref = f"post:{post_id}:body:{hit['content_type']}:{hit['ref']}"
        cached = store.lookup(conn, "wordpress", "post", source_ref)
        results.append(cached or store.record(
            conn,
            source_system="wordpress", source_content_type="post", source_ref=source_ref,
            evidence=f"body text contains '{hit['label']}' verbatim",
            target_system="strapi", target_content_type=hit["content_type"], target_ref=hit["ref"],
            confidence=1.0, method="exact_string_match",
        ))

    for token, candidates in task["fuzzy_by_token"].items():
        source_ref = f"post:{post_id}:body:mention:{token}"
        resolution, residue_item = _resolve_or_defer(
            conn,
            source_content_type="post", source_ref=source_ref,
            evidence=f"body text mentions '{token}'", candidates=candidates,
            post_id=post_id,
        )
        if resolution:
            results.append(resolution)
        if residue_item:
            residue.append(residue_item)
    return results, residue


def resolve_mapping_task(task: dict) -> dict:
    """The node every `Send` in `route_mapping_tasks` targets. Its input is
    exactly one task dict — LangGraph's `Send(node, arg)` passes `arg` as
    the node's *entire* input, not merged into full graph state — which is
    why `plan_mapping_tasks` above pre-computes everything each task needs
    (including per-post fuzzy candidates for the free-text fallback)
    rather than leaving this function to re-fetch or re-derive anything.

    Returns two lists, both merged across every parallel `Send` via
    `PipelineState`'s `operator.add` reducers (see graph.py):
    `resolutions` (fully-committed `mapping_rules` rows, exactly as
    before) and `residue` (genuinely ambiguous cases tier 1 can't settle
    for free — no `mapping_rules` row written yet, no LLM called here).
    A task can produce some of each: e.g. a field_match task with several
    posts might resolve most of them via `value_range_match` and still
    defer one post's free-text value to the agent tier.
    """
    conn = store.get_connection()
    if task["kind"] == "field_match":
        results, residue = _resolve_field_match(conn, task)
    elif task["kind"] == "body_scan":
        results, residue = _resolve_body_scan(conn, task)
    else:
        results, residue = [], []
    conn.close()
    return {"resolutions": results, "residue": residue}
