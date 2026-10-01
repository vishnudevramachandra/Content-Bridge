import type { MappingEntry, SchemaClass } from "./types";

// Mermaid erDiagram/flowchart identifiers must be simple tokens — class
// names in schema-ontology.ttl already are (see e.g. db:Post, strapi:Product),
// but sanitize defensively rather than assume Discovery never emits anything
// stranger.
function safeId(name: string): string {
  return name.replace(/[^a-zA-Z0-9_]/g, "_");
}

/**
 * Builds a mermaid `erDiagram` for one system's classes.
 *
 * Datatype properties become entity attributes. Object properties whose
 * `range` resolves to another class in the *same* system (e.g.
 * `db:postCategories` -> `db:Category`) become relationship lines
 * instead of attributes — using a generic "zero-or-many to
 * zero-or-many" crow's-foot (`}o--o{`) on both ends, since
 * schema-ontology.ttl only carries real cardinality for a property's
 * *own* class (`owl:maxCardinality`), not for cross-class links.
 */
export function buildErDiagram(classes: SchemaClass[]): string {
  const classNames = new Set(classes.map((c) => c.name));
  const entityLines: string[] = [];
  const relationshipLines: string[] = [];

  for (const cls of classes) {
    const id = safeId(cls.name);
    entityLines.push(`    ${id} {`);
    for (const prop of cls.properties) {
      if (prop.type === "object" && prop.range !== null && classNames.has(prop.range)) {
        relationshipLines.push(`    ${id} }o--o{ ${safeId(prop.range)} : "${prop.name}"`);
        continue;
      }
      entityLines.push(`        ${safeId(prop.range ?? "unknown")} ${safeId(prop.name)}`);
    }
    entityLines.push("    }");
  }

  return ["erDiagram", ...entityLines, ...relationshipLines].join("\n");
}

export interface SchemaSystem {
  /** Matches the SSSOM compact-id prefix each system's resources use —
   * `db:` for WordPress, `strapi:` for Strapi (see `_SYSTEM_PREFIXES`
   * in src/contentbridge/utils/ontology.py). */
  prefix: "db" | "strapi";
  label: string;
  classes: SchemaClass[];
}

/**
 * Builds one combined mermaid `flowchart` spanning both systems — an
 * RDF-style graph of the schema: classes are boxes, literal datatypes
 * are shared circles, and every property (object *and* datatype) is a
 * labeled edge between them, grouped into one `subgraph` per system.
 * Cross-system `mapping-ontology.ttl` (SSSOM) entries are layered on
 * top as thick edges between whichever nodes their `subject_id`/
 * `object_id` resolve to — a class node if they name one, or a small
 * hexagon created on the fly for a bare property/field reference (e.g.
 * `strapi:productLegacyId`) that otherwise has no node of its own in
 * the schema graph.
 */
export function buildRdfGraph(systems: SchemaSystem[], mappings: MappingEntry[]): string {
  const lines: string[] = ["flowchart LR"];
  const classNodeId = new Map<string, string>(); // "db:Post" -> node id
  const literalNodeId = new Map<string, string>(); // "db:string" -> node id
  const fieldNodeId = new Map<string, string>(); // "db:postMetaSlug" -> node id (mapping-only)
  const systemByPrefix = new Map(systems.map((s) => [s.prefix, s]));

  function classKey(prefix: string, name: string) {
    return `${prefix}:${name}`;
  }

  for (const system of systems) {
    const classNames = new Set(system.classes.map((c) => c.name));
    lines.push(`    subgraph ${safeId(system.prefix)} ["${system.label}"]`);

    for (const cls of system.classes) {
      const id = safeId(`${system.prefix}_${cls.name}`);
      classNodeId.set(classKey(system.prefix, cls.name), id);
      lines.push(`        ${id}["${cls.name}"]`);
    }

    const literalTypes = new Set(
      system.classes
        .flatMap((c) => c.properties)
        .filter((p) => p.type === "datatype" && p.range !== null && !classNames.has(p.range))
        .map((p) => p.range as string),
    );
    for (const type of literalTypes) {
      const id = safeId(`${system.prefix}_lit_${type}`);
      literalNodeId.set(classKey(system.prefix, type), id);
      lines.push(`        ${id}((${type}))`);
    }

    lines.push("    end");
  }

  for (const system of systems) {
    const classNames = new Set(system.classes.map((c) => c.name));
    for (const cls of system.classes) {
      const fromId = classNodeId.get(classKey(system.prefix, cls.name));
      for (const prop of cls.properties) {
        if (prop.range === null || fromId === undefined) continue;
        if (prop.type === "object" && classNames.has(prop.range)) {
          const toId = classNodeId.get(classKey(system.prefix, prop.range));
          if (toId !== undefined) lines.push(`    ${fromId} -->|${prop.name}| ${toId}`);
        } else if (prop.type === "datatype") {
          const toId = classNames.has(prop.range)
            ? classNodeId.get(classKey(system.prefix, prop.range))
            : literalNodeId.get(classKey(system.prefix, prop.range));
          if (toId !== undefined) lines.push(`    ${fromId} -.->|${prop.name}| ${toId}`);
        }
      }
    }
  }

  function resolveMappingNode(compactId: string | null): string | null {
    if (compactId === null) return null;
    const [prefix, localName] = compactId.split(":");
    const system = systemByPrefix.get(prefix as "db" | "strapi");
    if (system === undefined || localName === undefined) return null;

    const classId = classNodeId.get(classKey(prefix, localName));
    if (classId !== undefined) return classId;

    const key = classKey(prefix, localName);
    let id = fieldNodeId.get(key);
    if (id === undefined) {
      id = safeId(`${prefix}_field_${localName}`);
      fieldNodeId.set(key, id);
      lines.push(`    ${id}{{${localName}}}`);
    }
    return id;
  }

  for (const mapping of mappings) {
    const fromId = resolveMappingNode(mapping.subject_id);
    const toId = resolveMappingNode(mapping.object_id);
    if (fromId === null || toId === null) continue;
    const confidence = mapping.confidence !== null ? ` ${Math.round(mapping.confidence * 100)}%` : "";
    lines.push(`    ${fromId} ===|"${mapping.predicate ?? "mapsTo"}${confidence}"| ${toId}`);
  }

  return lines.join("\n");
}
