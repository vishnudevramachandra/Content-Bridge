import { useEffect, useMemo, useState } from "react";
import { getMappings, getSchema } from "../../lib/api";
import { buildErDiagram, buildRdfGraph } from "../../lib/schemaDiagrams";
import type { MappingEntry, SchemaClass, SchemaResponse } from "../../lib/types";
import { MermaidDiagram } from "../chat/MermaidDiagram";

type ViewType = "list" | "erd" | "graph";

const VIEW_LABELS: Record<ViewType, string> = {
  list: "List",
  erd: "ERD",
  graph: "Graph",
};

const VIEW_ORDER: ViewType[] = ["list", "erd", "graph"];

function ClassCard({ cls }: { cls: SchemaClass }) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-3">
      <h3 className="text-sm font-semibold text-gray-900">{cls.name}</h3>
      {cls.properties.length === 0 ? (
        <p className="mt-1 text-xs text-gray-400">No properties discovered.</p>
      ) : (
        <table className="mt-2 w-full text-xs">
          <tbody>
            {cls.properties.map((p) => (
              <tr key={p.name} className="border-t border-gray-100">
                <td className="py-1 pr-2 font-mono text-gray-700">{p.name}</td>
                <td className="py-1 text-gray-400">{p.range ?? "—"}</td>
                <td className="py-1 text-right text-gray-400">{p.type}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}

/** List or ERD panel — both are still per-system (each is a view of one
 * schema's own internal structure), shown as WordPress/Strapi stacked
 * inside one panel. Built client-side from the already-fetched classes
 * (see lib/schemaDiagrams.ts) — no backend round trip, unlike the
 * chat's on-demand diagrams which need the model to decide what to trim
 * to; these two are fixed, deterministic transforms of data already on
 * the page. */
function PerSystemPanel({ view, data }: { view: "list" | "erd"; data: SchemaResponse }) {
  const wordpressCode = useMemo(
    () => (view === "erd" ? buildErDiagram(data.wordpress.classes) : null),
    [view, data.wordpress.classes],
  );
  const strapiCode = useMemo(
    () => (view === "erd" ? buildErDiagram(data.strapi.classes) : null),
    [view, data.strapi.classes],
  );

  return (
    <div className="flex h-full min-w-[300px] flex-1 flex-col gap-4 border-r border-gray-100 px-4 py-4 last:border-r-0">
      <h2 className="text-xs font-bold uppercase tracking-wide text-indigo-600">
        {VIEW_LABELS[view]}
      </h2>
      <div
        className={
          view === "erd"
            ? "flex min-h-0 flex-1 flex-col gap-4"
            : "min-h-0 flex-1 space-y-4 overflow-y-auto"
        }
      >
        <section className={view === "erd" ? "flex min-h-0 flex-1 flex-col" : undefined}>
          <h3 className="mb-2 text-xs font-semibold uppercase tracking-wide text-gray-500">
            WordPress
          </h3>
          {view === "list" ? (
            <div className="space-y-3">
              {data.wordpress.classes.map((c) => (
                <ClassCard key={c.name} cls={c} />
              ))}
            </div>
          ) : (
            <div className="min-h-0 flex-1">
              <MermaidDiagram code={wordpressCode ?? ""} />
            </div>
          )}
        </section>
        <section className={view === "erd" ? "flex min-h-0 flex-1 flex-col" : undefined}>
          <h3 className="mb-2 text-xs font-semibold uppercase tracking-wide text-gray-500">
            Strapi
          </h3>
          {view === "list" ? (
            <div className="space-y-3">
              {data.strapi.classes.map((c) => (
                <ClassCard key={c.name} cls={c} />
              ))}
            </div>
          ) : (
            <div className="min-h-0 flex-1">
              <MermaidDiagram code={strapiCode ?? ""} />
            </div>
          )}
        </section>
      </div>
    </div>
  );
}

/** Graph panel — unlike List/ERD, this is *one* combined RDF-style
 * diagram spanning both systems (classes/literals/properties, grouped
 * into a subgraph per system) plus mapping-ontology.ttl's cross-system
 * connections layered on top as thick edges, so the mapping Discovery
 * and Mapping agents produced is visible right alongside each system's
 * own structure. */
function GraphPanel({ data, mappings }: { data: SchemaResponse; mappings: MappingEntry[] }) {
  const code = useMemo(
    () =>
      buildRdfGraph(
        [
          { prefix: "db", label: "WordPress", classes: data.wordpress.classes },
          { prefix: "strapi", label: "Strapi", classes: data.strapi.classes },
        ],
        mappings,
      ),
    [data, mappings],
  );

  return (
    <div className="flex h-full min-w-[360px] flex-1 flex-col gap-2 border-r border-gray-100 px-4 py-4 last:border-r-0">
      <h2 className="text-xs font-bold uppercase tracking-wide text-indigo-600">Graph</h2>
      <p className="text-xs text-gray-400">
        RDF-style view of both schemas — circles are literal types, hexagons are mapping-only
        fields — plus mapping-ontology connections between them (thick lines).
      </p>
      <div className="min-h-0 flex-1">
        <MermaidDiagram code={code} />
      </div>
    </div>
  );
}

/** Schema view of `GET /api/schema` (and `GET /api/mappings` for the
 * Graph panel) — the class/property structure Discovery wrote into
 * schema-ontology.ttl for each system, parsed by `parse_schema_ontology`
 * (see src/contentbridge/utils/ontology.py) rather than shipped to the
 * browser as raw Turtle. Three independently toggleable representations
 * (list table, ERD, RDF-style graph) can be shown at once, side by
 * side. */
export function SchemaView() {
  const [data, setData] = useState<SchemaResponse | null>(null);
  const [mappings, setMappings] = useState<MappingEntry[]>([]);
  const [loadError, setLoadError] = useState<string | null>(null);
  const [activeViews, setActiveViews] = useState<Record<ViewType, boolean>>({
    list: true,
    erd: false,
    graph: false,
  });

  useEffect(() => {
    getSchema()
      .then(setData)
      .catch((e: unknown) => setLoadError(String(e)));
    // Mappings are supplementary to this page (only the Graph panel uses
    // them) — Mapping not having run yet shouldn't block the rest of the
    // Schema view, so this failure is swallowed rather than surfaced.
    getMappings()
      .then((r) => setMappings(r.mappings))
      .catch(() => undefined);
  }, []);

  function toggleView(view: ViewType) {
    setActiveViews((prev) => ({ ...prev, [view]: !prev[view] }));
  }

  if (loadError) return <p className="p-4 text-sm text-red-600">{loadError}</p>;
  if (!data) return <p className="p-4 text-sm text-gray-400">Loading…</p>;
  if (!data.available) {
    return (
      <p className="p-4 text-sm text-gray-500">
        No schema yet — ask the orchestrator to run Discovery for WordPress and Strapi first.
      </p>
    );
  }

  const enabledViews = VIEW_ORDER.filter((v) => activeViews[v]);

  return (
    <div className="flex h-full flex-col">
      <div className="flex items-center gap-2 border-b border-gray-200 px-4 py-3">
        {VIEW_ORDER.map((view) => (
          <button
            key={view}
            type="button"
            onClick={() => toggleView(view)}
            aria-pressed={activeViews[view]}
            className={`rounded-full px-3 py-1 text-xs font-medium transition-colors ${
              activeViews[view]
                ? "bg-indigo-600 text-white"
                : "border border-gray-300 text-gray-600 hover:bg-gray-50"
            }`}
          >
            {VIEW_LABELS[view]}
          </button>
        ))}
      </div>

      {enabledViews.length === 0 ? (
        <p className="p-4 text-sm text-gray-400">
          Toggle at least one view (List, ERD, or Graph) above to see the schema.
        </p>
      ) : (
        <div className="flex flex-1 overflow-x-auto">
          {enabledViews.map((view) => (
            <div key={view} className="h-full">
              {view === "graph" ? (
                <GraphPanel data={data} mappings={mappings} />
              ) : (
                <PerSystemPanel view={view} data={data} />
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
