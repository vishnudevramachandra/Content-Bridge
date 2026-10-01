import type { ReactNode } from "react";

interface ActivityCardProps {
  icon: string;
  title: string;
  status: "running" | "done";
  children?: ReactNode;
}

/** A collapsible `<details>` card for a tool call or delegated sub-agent
 * run — kept collapsed by default since these are secondary to the
 * assistant's own text, but expandable to inspect args/results. */
export function ActivityCard({ icon, title, status, children }: ActivityCardProps) {
  return (
    <div className="flex justify-start">
      <details className="max-w-[85%] rounded-xl border border-gray-200 bg-gray-50 px-3 py-2 text-xs text-gray-700 open:bg-white">
        <summary className="flex cursor-pointer select-none items-center gap-2">
          <span>{icon}</span>
          <span className="font-medium text-gray-600">{title}</span>
          <span
            className={`ml-1 inline-flex h-2 w-2 rounded-full ${
              status === "running" ? "animate-pulse bg-amber-400" : "bg-emerald-500"
            }`}
          />
        </summary>
        <div className="mt-2 space-y-2">{children}</div>
      </details>
    </div>
  );
}
