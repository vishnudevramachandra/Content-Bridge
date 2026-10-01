import type { ChatEvent } from "./types";

/** Thrown for a non-2xx response before any SSE streaming starts — e.g.
 * the 409s `_event_to_sse`'s callers (`/api/chat`/`/api/answer`) raise
 * when a run is already active or a question is already pending. */
export class ChatRequestError extends Error {}

/**
 * Stream one orchestrator run's `ChatEvent`s from `POST /api/chat` or
 * `POST /api/answer`.
 *
 * Rolled by hand instead of using a reconnecting-SSE library: these
 * endpoints are one-shot (one POST, one stream, done), and a non-2xx
 * response here is a plain JSON error body (`{"detail": "..."}`) rather
 * than an event stream — simpler to handle directly than to fight a
 * client built around long-lived, auto-reconnecting GET streams.
 */
export async function streamChat(
  path: "/api/chat" | "/api/answer",
  body: Record<string, unknown>,
  onEvent: (event: ChatEvent) => void,
  signal?: AbortSignal,
): Promise<void> {
  const res = await fetch(path, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
    signal,
  });

  if (!res.ok || !res.body) {
    let detail = `${res.status} ${res.statusText}`;
    try {
      const data = (await res.json()) as { detail?: string };
      detail = data.detail ?? detail;
    } catch {
      // Not a JSON body — fall back to the status line above.
    }
    throw new ChatRequestError(detail);
  }

  const reader = res.body.getReader();
  const decoder = new TextDecoder();
  let buffer = "";

  for (;;) {
    const { done, value } = await reader.read();
    if (done) break;
    buffer += decoder.decode(value, { stream: true });

    // Each SSE frame is one "data: <json>" line followed by a blank
    // line (see `_sse_line` in main.py) — split on the blank-line
    // separator rather than assuming one frame per chunk.
    let separatorIndex: number;
    while ((separatorIndex = buffer.indexOf("\n\n")) !== -1) {
      const frame = buffer.slice(0, separatorIndex).trim();
      buffer = buffer.slice(separatorIndex + 2);
      if (!frame.startsWith("data:")) continue;
      const jsonText = frame.slice("data:".length).trim();
      if (jsonText) onEvent(JSON.parse(jsonText) as ChatEvent);
    }
  }
}
