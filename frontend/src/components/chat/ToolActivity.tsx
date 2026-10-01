import { ActivityCard } from "./ActivityCard";

interface ToolActivityProps {
  toolName: string;
  args: Record<string, unknown>;
  status: "running" | "done";
  result?: unknown;
}

export function ToolActivity({ toolName, args, status, result }: ToolActivityProps) {
  return (
    <ActivityCard
      icon="🔧"
      title={status === "running" ? `${toolName}…` : toolName}
      status={status}
    >
      <div>
        <p className="font-semibold text-gray-500">Args</p>
        <pre className="mt-1 overflow-x-auto rounded bg-gray-900 p-2 text-[11px] text-gray-100">
          {JSON.stringify(args, null, 2)}
        </pre>
      </div>
      {status === "done" && (
        <div>
          <p className="font-semibold text-gray-500">Result</p>
          <pre className="mt-1 overflow-x-auto rounded bg-gray-900 p-2 text-[11px] text-gray-100">
            {JSON.stringify(result, null, 2)}
          </pre>
        </div>
      )}
    </ActivityCard>
  );
}
