import { useEffect, useState } from "react";
import { getSyncLog } from "../../lib/api";
import type { SyncLogEntryRecord } from "../../lib/types";

function formatTime(timestamp: number): string {
  return new Date(timestamp * 1000).toLocaleString();
}

/** Timeline view of `GET /api/sync-log` — every `create_wp_post`/
 * `update_wp_post` call the Sync agent has made, persisted by
 * `WPOperations.after_tool_execute` (see wp_client.py capability) to
 * `data/sync-log.jsonl` so it survives backend restarts, unlike the
 * in-memory `message_history`. */
export function SyncLogView() {
  const [entries, setEntries] = useState<SyncLogEntryRecord[] | null>(null);
  const [loadError, setLoadError] = useState<string | null>(null);

  useEffect(() => {
    getSyncLog()
      .then((r) => setEntries(r.entries))
      .catch((e: unknown) => setLoadError(String(e)));
  }, []);

  if (loadError) return <p className="p-4 text-sm text-red-600">{loadError}</p>;
  if (!entries) return <p className="p-4 text-sm text-gray-400">Loading…</p>;
  if (entries.length === 0) {
    return (
      <p className="p-4 text-sm text-gray-500">
        No WordPress writes logged yet — they're recorded here as soon as the Sync agent creates
        or updates a post.
      </p>
    );
  }

  return (
    <div className="h-full overflow-y-auto p-4">
      <div className="space-y-3">
        {entries.map((e, i) => (
          <div key={`${e.timestamp}-${i}`} className="rounded-xl border border-gray-200 bg-white p-3">
            <div className="flex items-center justify-between">
              <p className="text-sm font-medium text-gray-900">{e.tool_name}</p>
              <span
                className={`rounded-full px-2 py-0.5 text-xs font-medium ${
                  e.success ? "bg-emerald-100 text-emerald-700" : "bg-red-100 text-red-700"
                }`}
              >
                {e.success ? "ok" : "failed"}
              </span>
            </div>
            <p className="mt-1 text-xs text-gray-400">{formatTime(e.timestamp)}</p>
            <pre className="mt-2 overflow-x-auto rounded bg-gray-900 p-2 text-[11px] text-gray-100">
              {JSON.stringify(e.args, null, 2)}
            </pre>
          </div>
        ))}
      </div>
    </div>
  );
}
