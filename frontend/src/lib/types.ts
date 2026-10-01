// Mirrors the SSE payload shapes `_event_to_sse` in
// `src/contentbridge/main.py` emits from `POST /api/chat` and
// `POST /api/answer`, plus the JSON shapes the new read-only endpoints
// return (`/api/schema`, `/api/mappings`, `/api/sync-log`, `/api/status`).

export type ChatEvent =
  | { type: "text_start"; content: string }
  | { type: "text_delta"; content: string }
  | { type: "tool_call"; tool_name: string; args: Record<string, unknown> }
  | { type: "tool_result"; tool_name: string | null; content: unknown }
  | { type: "sub_agent_started"; agent_name: string; instruction: string }
  | { type: "sub_agent_finished"; agent_name: string; summary: string }
  | { type: "system_alert"; enqueue_id: string; content: string }
  | { type: "question"; question: string }
  | { type: "final"; output: string }
  | { type: "error"; detail: string };

/** One entry in the locally-rendered transcript, built up from `ChatEvent`s
 * as they stream in. This is purely a frontend view model — the backend
 * has no concept of per-entry ids; it just streams a flat event sequence
 * for one global conversation. */
export type TranscriptEntry =
  | { id: string; kind: "user_message"; text: string }
  | { id: string; kind: "assistant_text"; text: string; done: boolean }
  | {
      id: string;
      kind: "sub_agent";
      agentName: string;
      instruction: string;
      status: "running" | "done";
      summary?: string;
    }
  | {
      id: string;
      kind: "tool";
      toolName: string;
      args: Record<string, unknown>;
      status: "running" | "done";
      result?: unknown;
    }
  | { id: string; kind: "system_alert"; content: string }
  | { id: string; kind: "answered_question"; question: string; answer?: string }
  | { id: string; kind: "error"; detail: string };

export interface StatusResponse {
  run_active: boolean;
  history_length: number;
  waiting_for_answer: boolean;
  pending_question: string | null;
  alerted_certifications: number;
}

export interface SchemaProperty {
  name: string;
  type: "datatype" | "object";
  range: string | null;
}

export interface SchemaClass {
  name: string;
  properties: SchemaProperty[];
}

export interface SchemaResponse {
  available: boolean;
  wordpress: { classes: SchemaClass[] };
  strapi: { classes: SchemaClass[] };
}

export interface MappingEntry {
  id: string;
  subject_id: string | null;
  predicate: string | null;
  object_id: string | null;
  confidence: number | null;
  justification: string | null;
  subject_match_field: string | null;
  object_match_field: string | null;
  comment: string | null;
}

export interface MappingsResponse {
  available: boolean;
  mappings: MappingEntry[];
}

export interface SyncLogEntryRecord {
  timestamp: number;
  tool_name: string;
  args: Record<string, unknown>;
  result: Record<string, unknown>;
  success: boolean;
}

export interface SyncLogResponse {
  entries: SyncLogEntryRecord[];
}
