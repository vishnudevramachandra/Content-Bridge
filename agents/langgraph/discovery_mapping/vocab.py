"""Strapi's "known vocabulary," and the heuristic used to spot mentions of
it inside free-text WordPress content.

This module is deliberately Mapping-only: it hard-codes knowledge of BOTH
systems (Strapi's catalog entities on one side, WordPress post bodies on
the other), which is exactly the kind of cross-system knowledge Discovery
is not allowed to hold.

Two tiers, matching the task brief:

- `EXACT names`: the literal `name` string of a product/standard/certification.
  A verbatim (case-insensitive) match in a post body is deterministic —
  no judgment involved, just string containment.
- `SIGNATURE_TOKENS`: shorter, looser substrings associated with one or more
  entities. A hit here means "this post *might* be talking about one of
  these," not "it definitely is." Some tokens are deliberately coarse
  (`"BX54"`, `"Veridian"` match a whole product family; `"UL"` matches any
  UL-flavored standard number, not just our seeded "UL Listed" certification)
  precisely so that real ambiguity — including genuine non-matches — shows
  up instead of being quietly designed away. Whether a signature-token hit
  becomes a real correspondence is exactly the judgment Mapping's LLM step
  is for.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Entity:
    content_type: str  # "product" | "standard" | "certification"
    ref: str  # legacyId (product) or name (standard/certification) as a string
    name: str


# Populated at runtime from Strapi's actual content-manager data (see
# mapping.py) rather than hard-coded here — this dict starts empty and is
# filled once per run so the vocabulary always reflects live seed data.
def build_entities(products: list[dict], standards: list[dict], certifications: list[dict]) -> list[Entity]:
    entities = []
    for p in products:
        entities.append(Entity("product", str(p["legacyId"]), p["name"]))
    for s in standards:
        entities.append(Entity("standard", s["name"], s["name"]))
    for c in certifications:
        entities.append(Entity("certification", c["name"], c["name"]))
    return entities


# token -> list of (content_type, ref) tuples. Refs are legacyId strings for
# products, names for standards/certifications, resolved against the live
# `entities` list at match time (see mapping.find_candidates).
SIGNATURE_TOKENS: dict[str, list[tuple[str, str]]] = {
    # Coarse family tokens — intentionally ambiguous across multiple products.
    "bx54": [("product", "104"), ("product", "233"), ("product", "891")],
    "veridian": [("product", "512"), ("product", "618"), ("product", "734")],
    # Precise tokens — narrow to a single product.
    "engraver": [("product", "104")],
    "laser": [("product", "104")],
    "filter": [("product", "233")],
    "cartridge": [("product", "233")],
    "focus lens": [("product", "891")],
    "lens": [("product", "891")],
    "interlock": [("product", "512")],
    "safety switch": [("product", "512")],
    "emergency stop": [("product", "618")],
    "e-stop": [("product", "618")],
    "estop": [("product", "618")],
    "pushbutton": [("product", "618")],
    "light curtain": [("product", "734")],
    "curtain": [("product", "734")],
    # Standards / certifications. "UL" is deliberately loose: it fires on
    # "UL508A" (a real standard number that is *not* in our seed data) just
    # as readily as on anything actually meaning the "UL Listed" mark — the
    # whole point being that a token hit is a candidate, not a verdict.
    "ansi": [("standard", "ANSI B11.1")],
    "iec": [("standard", "IEC 61496-2")],
    "ul": [("certification", "UL Listed")],
    "ce mark": [("certification", "CE Marked")],
}
