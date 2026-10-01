import { useEffect, useState } from "react";
import { getMappings } from "../../lib/api";
import type { MappingsResponse } from "../../lib/types";

function confidenceColor(confidence: number | null): string {
  if (confidence === null) return "bg-gray-200 text-gray-600";
  if (confidence >= 0.9) return "bg-emerald-100 text-emerald-700";
  if (confidence >= 0.6) return "bg-amber-100 text-amber-700";
  return "bg-red-100 text-red-700";
}

/** Read-only confidence-card view of `GET /api/mappings` — what the
 * Mapping agent already decided and committed to mapping-ontology.ttl
 * (SSSOM), not a pending-approval queue: there's no "proposed but not
 * yet asserted" state in the current pipeline (see the design
 * discussion before this view was built). */
export function MappingView() {
  const [data, setData] = useState<MappingsResponse | null>(null);
  const [loadError, setLoadError] = useState<string | null>(null);

  useEffect(() => {
    getMappings()
      .then(setData)
      .catch((e: unknown) => setLoadError(String(e)));
  }, []);

  if (loadError) return <p className="p-4 text-sm text-red-600">{loadError}</p>;
  if (!data) return <p className="p-4 text-sm text-gray-400">Loading…</p>;
  if (!data.available || data.mappings.length === 0) {
    return (
      <p className="p-4 text-sm text-gray-500">
        No mappings yet — ask the orchestrator to run Mapping once both schemas are discovered.
      </p>
    );
  }

  return (
    <div className="h-full overflow-y-auto p-4">
      <p className="mb-3 text-xs text-gray-500">
        Read-only view of what the Mapping agent already decided and committed — not a review
        queue. See each card's comment for its reasoning.
      </p>
      <div className="space-y-3">
        {data.mappings.map((m) => (
          <div key={m.id} className="rounded-xl border border-gray-200 bg-white p-3">
            <div className="flex items-center justify-between gap-3">
              <p className="font-mono text-sm text-gray-900">
                {m.subject_id} <span className="text-gray-400">{m.predicate ?? "↔"}</span>{" "}
                {m.object_id}
              </p>
              <span
                className={`shrink-0 rounded-full px-2 py-0.5 text-xs font-medium ${confidenceColor(
                  m.confidence,
                )}`}
              >
                {m.confidence !== null ? `${Math.round(m.confidence * 100)}%` : "unscored"}
              </span>
            </div>
            {(m.subject_match_field || m.object_match_field) && (
              <p className="mt-1 text-xs text-gray-400">
                matched on {m.subject_match_field ?? "—"} ↔ {m.object_match_field ?? "—"}
              </p>
            )}
            {m.comment && <p className="mt-2 text-xs text-gray-600">{m.comment}</p>}
          </div>
        ))}
      </div>
    </div>
  );
}
