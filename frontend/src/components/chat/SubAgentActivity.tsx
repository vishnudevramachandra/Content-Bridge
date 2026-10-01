import { ActivityCard } from "./ActivityCard";

// Matches `_DEFERRABLE_SUB_AGENTS` in orchestrator_agent.py.
const AGENT_LABELS: Record<string, string> = {
  discovery_agent: "Discovery",
  mapping_agent: "Mapping",
  sync_agent: "Sync",
};

interface SubAgentActivityProps {
  agentName: string;
  instruction: string;
  status: "running" | "done";
  summary?: string;
}

export function SubAgentActivity({
  agentName,
  instruction,
  status,
  summary,
}: SubAgentActivityProps) {
  const label = AGENT_LABELS[agentName] ?? agentName;
  return (
    <ActivityCard
      icon="🧭"
      title={`${label} agent ${status === "running" ? "is running…" : "finished"}`}
      status={status}
    >
      <div>
        <p className="font-semibold text-gray-500">Instruction</p>
        <p className="whitespace-pre-wrap">{instruction}</p>
      </div>
      {status === "done" && summary && (
        <div>
          <p className="font-semibold text-gray-500">Summary</p>
          <p className="whitespace-pre-wrap">{summary}</p>
        </div>
      )}
    </ActivityCard>
  );
}
