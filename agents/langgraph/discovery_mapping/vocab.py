"""Building a Strapi "vocabulary" for body-scan matching — entirely from
live schema + data, no hardcoded entity names or keyword lists.

This module used to hard-code which words point at which products
(`"bx54" -> [104, 233, 891]`, etc.) after a human read the seed catalog.
That's exactly the kind of tailoring the rest of this build is trying to
avoid: it would silently go stale the moment the catalog changed, and it
wouldn't work at all against a different Strapi instance. Everything here
is derived at runtime instead:

- `pick_label_attribute` finds, generically, which attribute of a content
  type acts as its human-readable name — the thing a WordPress post would
  plausibly mention in prose. Strapi has an official place for this
  (content-manager's `settings.mainField`), so that's checked first; this
  seed doesn't set it, so we fall back to a schema-shape convention
  (first required string attribute) that's still a generic rule, not a
  name lookup.
- `build_entities` turns each content type's real records into `Entity`
  objects carrying that label, keyed by Strapi's own `documentId` — the one
  identifier every Strapi content type has, regardless of domain.
- `build_token_index` tokenizes real labels into single words, so
  "BX54 Replacement Focus Lens" naturally yields a token index where "bx54"
  legitimately points at every BX54-family product (because they all
  really contain that word), not because someone wrote that down.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

_WORD_RE = re.compile(r"[a-z0-9]+")
_MIN_TOKEN_LEN = 4  # filters noise like "the", "for", "ul" without a hardcoded stopword list


@dataclass(frozen=True)
class Entity:
    content_type: str  # short name, e.g. "product"
    ref: str            # Strapi documentId — stable, generic across all content types
    label: str           # the human-readable name used for matching


def pick_label_attribute(attributes: dict) -> str | None:
    """Generic heuristic for "which attribute is this content type's name."

    Strapi's own generic answer to this question is content-manager's
    `settings.mainField`, which we check for first (see mapping.py's caller).
    This function is the fallback used when that isn't set: the first
    required string-typed attribute, in schema declaration order. That's a
    real (if imperfect) convention most Strapi content types follow — not
    a guess tailored to this catalog's field names.
    """
    for name, spec in attributes.items():
        if spec.get("type") == "string" and spec.get("required"):
            return name
    for name, spec in attributes.items():
        if spec.get("type") == "string":
            return name
    return None


def build_entities(content_type: str, label_attr: str | None, entries: list[dict]) -> list[Entity]:
    if label_attr is None:
        return []
    entities = []
    for entry in entries:
        label = entry.get(label_attr)
        if isinstance(label, str) and label:
            entities.append(Entity(content_type, entry["documentId"], label))
    return entities


def tokenize(text: str) -> set[str]:
    return {w for w in _WORD_RE.findall(text.lower()) if len(w) >= _MIN_TOKEN_LEN}


def build_token_index(entities: list[Entity]) -> dict[str, list[Entity]]:
    """token -> every entity whose label contains that token.

    A coarse token like "bx54" ends up pointing at multiple products
    because multiple real product names really contain it — that
    ambiguity is discovered from data, not authored by hand.
    """
    index: dict[str, list[Entity]] = {}
    for entity in entities:
        for token in tokenize(entity.label):
            index.setdefault(token, []).append(entity)
    return index
