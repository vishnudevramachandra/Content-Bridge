"""Parse the Discovery/Mapping agents' Turtle output into plain JSON.

`schema-ontology.ttl` (an OWL ontology) and `mapping-ontology.ttl` (an
SSSOM mapping set) are written and read by the agents as raw text via
their generic `read_file`/`write_file` tools — nothing about their
structure is otherwise exposed. These two functions parse that Turtle
with `rdflib` into JSON shapes a frontend can render directly, without
shipping an RDF library (or Turtle syntax) to the browser.
"""

from pathlib import Path
from typing import Any

from rdflib import RDF, RDFS, Graph, Namespace, URIRef
from rdflib.namespace import OWL

_WP_NS = Namespace("https://example.com/wordpress/ontology#")
_STRAPI_NS = Namespace("https://example.com/strapi/ontology#")
_SSSOM = Namespace("https://w3id.org/sssom/")

# Matches the `db:`/`strapi:` prefixes the agents themselves use when
# writing these files, so ids in the API response read the same as the
# Turtle source (e.g. `strapi:Product`, `db:Post`).
_SYSTEM_PREFIXES = {"wordpress": ("db", _WP_NS), "strapi": ("strapi", _STRAPI_NS)}


def _local_name(uri: URIRef) -> str:
    text = str(uri)
    return text.rsplit("#", 1)[-1].rsplit("/", 1)[-1]


def _system_for(uri: URIRef) -> str | None:
    text = str(uri)
    for system, (_, ns) in _SYSTEM_PREFIXES.items():
        if text.startswith(str(ns)):
            return system
    return None


def _compact(uri: URIRef | None) -> str | None:
    """Render a URI as `<prefix>:<local name>`, matching the Turtle source."""
    if uri is None:
        return None
    system = _system_for(uri)
    if system is not None:
        prefix, _ = _SYSTEM_PREFIXES[system]
        return f"{prefix}:{_local_name(uri)}"
    return _local_name(uri)


def parse_schema_ontology(path: Path) -> dict[str, Any]:
    """Parse schema-ontology.ttl into per-system classes and properties.

    Parameters
    ----------
    path : Path
        Path to the schema ontology Turtle file.

    Returns
    -------
    dict
        `{"wordpress": {"classes": [...]}, "strapi": {"classes": [...]}}`,
        each class shaped `{"name", "properties": [{"name", "type",
        "range"}]}` (`type` is `"datatype"` or `"object"`).

    """
    graph = Graph()
    graph.parse(path, format="turtle")

    classes_by_system: dict[str, dict[str, dict[str, Any]]] = {
        system: {} for system in _SYSTEM_PREFIXES
    }

    for cls in graph.subjects(RDF.type, OWL.Class):
        if not isinstance(cls, URIRef):
            continue
        system = _system_for(cls)
        if system is None:
            continue
        name = _local_name(cls)
        classes_by_system[system].setdefault(name, {"name": name, "properties": []})

    for prop_type, type_label in (
        (OWL.DatatypeProperty, "datatype"),
        (OWL.ObjectProperty, "object"),
    ):
        for prop in graph.subjects(RDF.type, prop_type):
            if not isinstance(prop, URIRef):
                continue
            system = _system_for(prop)
            if system is None:
                continue
            ranges = [r for r in graph.objects(prop, RDFS.range) if isinstance(r, URIRef)]
            range_name = _local_name(ranges[0]) if ranges else None
            for domain in graph.objects(prop, RDFS.domain):
                if not isinstance(domain, URIRef):
                    continue
                cls_name = _local_name(domain)
                classes_by_system[system].setdefault(
                    cls_name, {"name": cls_name, "properties": []}
                )
                classes_by_system[system][cls_name]["properties"].append(
                    {"name": _local_name(prop), "type": type_label, "range": range_name}
                )

    return {
        system: {
            "classes": sorted(classes.values(), key=lambda c: c["name"])
        }
        for system, classes in classes_by_system.items()
    }


def parse_mapping_ontology(path: Path) -> list[dict[str, Any]]:
    """Parse mapping-ontology.ttl (SSSOM) into a list of mapping dicts.

    Parameters
    ----------
    path : Path
        Path to the mapping ontology Turtle file.

    Returns
    -------
    list[dict]
        One dict per `sssom:Mapping`, shaped `{"id", "subject_id",
        "predicate", "object_id", "confidence", "justification",
        "subject_match_field", "object_match_field", "comment"}`, sorted
        by descending confidence (unscored mappings last).

    """
    graph = Graph()
    graph.parse(path, format="turtle")

    def _first(subject: URIRef, predicate: URIRef) -> Any:
        values = list(graph.objects(subject, predicate))
        return values[0] if values else None

    mappings = []
    for mapping in graph.subjects(RDF.type, _SSSOM.Mapping):
        if not isinstance(mapping, URIRef):
            continue
        confidence = _first(mapping, _SSSOM.confidence)
        justification = _first(mapping, _SSSOM.mapping_justification)
        subject_field = _first(mapping, _SSSOM.subject_match_field)
        object_field = _first(mapping, _SSSOM.object_match_field)
        comment = _first(mapping, RDFS.comment)
        mappings.append(
            {
                "id": _local_name(mapping),
                "subject_id": _compact(_first(mapping, _SSSOM.subject_id)),
                "predicate": _local_name(_first(mapping, _SSSOM.predicate_id))
                if _first(mapping, _SSSOM.predicate_id) is not None
                else None,
                "object_id": _compact(_first(mapping, _SSSOM.object_id)),
                "confidence": float(confidence) if confidence is not None else None,
                "justification": _local_name(justification)
                if justification is not None
                else None,
                "subject_match_field": str(subject_field)
                if subject_field is not None
                else None,
                "object_match_field": str(object_field)
                if object_field is not None
                else None,
                "comment": str(comment) if comment is not None else None,
            }
        )

    mappings.sort(key=lambda m: (m["confidence"] is None, -(m["confidence"] or 0.0)))
    return mappings
