import type {
  MappingsResponse,
  SchemaResponse,
  StatusResponse,
  SyncLogResponse,
} from "./types";

async function getJson<T>(path: string): Promise<T> {
  const res = await fetch(path);
  if (!res.ok) {
    throw new Error(`${path} failed: ${res.status} ${res.statusText}`);
  }
  return res.json() as Promise<T>;
}

export const getStatus = () => getJson<StatusResponse>("/api/status");
export const getSchema = () => getJson<SchemaResponse>("/api/schema");
export const getMappings = () => getJson<MappingsResponse>("/api/mappings");
export const getSyncLog = () => getJson<SyncLogResponse>("/api/sync-log");

export async function resetConversation(): Promise<void> {
  const res = await fetch("/api/reset", { method: "POST" });
  if (!res.ok) {
    throw new Error(`reset failed: ${res.status} ${res.statusText}`);
  }
}
