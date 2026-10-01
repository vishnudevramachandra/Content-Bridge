import { useEffect, useState } from "react";
import { getStatus } from "../lib/api";
import type { StatusResponse } from "../lib/types";

const POLL_MS = 5000;

/** Small header strip polling `GET /api/status` — surfaces the
 * backend's single global `ChatState` (run active / waiting for an
 * answer / certifications the periodic worker has alerted on) regardless
 * of which page is open. */
export function StatusBadge() {
  const [status, setStatus] = useState<StatusResponse | null>(null);

  useEffect(() => {
    let cancelled = false;
    const poll = () => {
      getStatus()
        .then((s) => {
          if (!cancelled) setStatus(s);
        })
        .catch(() => undefined);
    };
    poll();
    const interval = setInterval(poll, POLL_MS);
    return () => {
      cancelled = true;
      clearInterval(interval);
    };
  }, []);

  if (!status) return null;

  return (
    <div className="flex items-center gap-3 text-xs text-gray-500">
      <span className="flex items-center gap-1.5">
        <span
          className={`h-2 w-2 rounded-full ${status.run_active ? "animate-pulse bg-amber-400" : "bg-emerald-500"}`}
        />
        {status.run_active ? "Run active" : "Idle"}
      </span>
      {status.waiting_for_answer && <span className="text-indigo-600">Awaiting answer</span>}
      <span>{status.alerted_certifications} cert alert(s)</span>
    </div>
  );
}
