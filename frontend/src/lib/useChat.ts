import { useCallback, useEffect, useRef, useState } from "react";
import { getStatus, resetConversation } from "./api";
import { ChatRequestError, streamChat } from "./sse";
import type { ChatEvent, TranscriptEntry } from "./types";

const STATUS_POLL_MS = 4000;

function newId(): string {
  return crypto.randomUUID();
}

/**
 * Drives one global orchestrator conversation (matching the backend's
 * single `ChatState` — see `main.py`) and keeps a local transcript view
 * built up from the raw `ChatEvent` stream.
 *
 * Runs started elsewhere (the periodic certification-alert worker, or
 * another browser tab) aren't visible as a live stream here — there's
 * no backend endpoint for that — but are still surfaced via polling
 * `GET /api/status`: `pending_question` lets a fresh page load show and
 * answer a question it didn't see asked, and `run_active` disables the
 * composer while something else is mid-run.
 */
export function useChat() {
  const [transcript, setTranscript] = useState<TranscriptEntry[]>([]);
  const [pendingQuestion, setPendingQuestion] = useState<string | null>(null);
  const [isStreaming, setIsStreaming] = useState(false);
  const [externallyBusy, setExternallyBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Mutable, per-run bookkeeping that event handling needs but that
  // shouldn't trigger re-renders by itself — reset at the start of each
  // `streamChat` call.
  const runState = useRef({
    currentAssistantId: null as string | null,
    pendingToolIds: [] as string[],
    pendingSubAgentIds: {} as Record<string, string[]>,
  });

  const pushEntry = useCallback((entry: TranscriptEntry) => {
    setTranscript((prev) => [...prev, entry]);
  }, []);

  // `ChatEvent` has no explicit "text part ended" event — a part is only
  // implicitly done once another one starts, or the run itself ends
  // (`final`/`question`), or the stream dies mid-run. This flips `done`
  // on whichever assistant_text entry is still open, if any.
  const finalizeOpenAssistantText = useCallback(() => {
    const id = runState.current.currentAssistantId;
    if (id === null) return;
    setTranscript((prev) =>
      prev.map((e) => (e.id === id && e.kind === "assistant_text" ? { ...e, done: true } : e)),
    );
  }, []);

  const handleEvent = useCallback((event: ChatEvent) => {
    const state = runState.current;

    switch (event.type) {
      case "text_start": {
        finalizeOpenAssistantText();
        const id = newId();
        state.currentAssistantId = id;
        pushEntry({ id, kind: "assistant_text", text: event.content, done: false });
        break;
      }
      case "text_delta": {
        const id = state.currentAssistantId;
        if (id === null) break;
        setTranscript((prev) =>
          prev.map((e) =>
            e.id === id && e.kind === "assistant_text"
              ? { ...e, text: e.text + event.content }
              : e,
          ),
        );
        break;
      }
      case "tool_call": {
        const id = newId();
        state.pendingToolIds.push(id);
        pushEntry({
          id,
          kind: "tool",
          toolName: event.tool_name,
          args: event.args,
          status: "running",
        });
        break;
      }
      case "tool_result": {
        const id = state.pendingToolIds.shift();
        if (id === undefined) break;
        setTranscript((prev) =>
          prev.map((e) =>
            e.id === id && e.kind === "tool"
              ? { ...e, status: "done", result: event.content }
              : e,
          ),
        );
        break;
      }
      case "sub_agent_started": {
        const id = newId();
        (state.pendingSubAgentIds[event.agent_name] ??= []).push(id);
        pushEntry({
          id,
          kind: "sub_agent",
          agentName: event.agent_name,
          instruction: event.instruction,
          status: "running",
        });
        break;
      }
      case "sub_agent_finished": {
        const queue = state.pendingSubAgentIds[event.agent_name];
        const id = queue?.shift();
        if (id === undefined) break;
        setTranscript((prev) =>
          prev.map((e) =>
            e.id === id && e.kind === "sub_agent"
              ? { ...e, status: "done", summary: event.summary }
              : e,
          ),
        );
        break;
      }
      case "system_alert": {
        pushEntry({ id: newId(), kind: "system_alert", content: event.content });
        break;
      }
      case "question": {
        finalizeOpenAssistantText();
        state.currentAssistantId = null;
        setPendingQuestion(event.question);
        pushEntry({ id: newId(), kind: "answered_question", question: event.question });
        break;
      }
      case "final": {
        finalizeOpenAssistantText();
        state.currentAssistantId = null;
        break;
      }
      case "error": {
        pushEntry({ id: newId(), kind: "error", detail: event.detail });
        break;
      }
    }
  }, [finalizeOpenAssistantText, pushEntry]);

  const runStream = useCallback(
    async (path: "/api/chat" | "/api/answer", body: Record<string, unknown>) => {
      runState.current = {
        currentAssistantId: null,
        pendingToolIds: [],
        pendingSubAgentIds: {},
      };
      setIsStreaming(true);
      setError(null);
      try {
        await streamChat(path, body, handleEvent);
      } catch (e) {
        const message = e instanceof ChatRequestError ? e.message : String(e);
        setError(message);
        pushEntry({ id: newId(), kind: "error", detail: message });
      } finally {
        // Covers the stream dying mid-run (network drop, backend
        // restart) without a `final`/`question` event to close out
        // whatever assistant_text entry was still open.
        finalizeOpenAssistantText();
        setIsStreaming(false);
      }
    },
    [finalizeOpenAssistantText, handleEvent, pushEntry],
  );

  const sendMessage = useCallback(
    (text: string) => {
      const trimmed = text.trim();
      if (!trimmed || isStreaming) return;
      pushEntry({ id: newId(), kind: "user_message", text: trimmed });
      void runStream("/api/chat", { message: trimmed });
    },
    [isStreaming, pushEntry, runStream],
  );

  const answerQuestion = useCallback(
    (answer: string) => {
      const trimmed = answer.trim();
      if (!trimmed || isStreaming) return;
      setTranscript((prev) => {
        const lastQuestionIndex = [...prev].reverse().findIndex(
          (e) => e.kind === "answered_question" && e.answer === undefined,
        );
        if (lastQuestionIndex === -1) return prev;
        const index = prev.length - 1 - lastQuestionIndex;
        return prev.map((e, i) => (i === index ? { ...e, answer: trimmed } : e));
      });
      setPendingQuestion(null);
      void runStream("/api/answer", { answer: trimmed });
    },
    [isStreaming, runStream],
  );

  const reset = useCallback(async () => {
    await resetConversation();
    setTranscript([]);
    setPendingQuestion(null);
    setError(null);
  }, []);

  // Poll status so a fresh/other tab can see a run or question that
  // started elsewhere (the periodic alert worker, or another client) —
  // skipped while this tab is itself actively streaming, since that
  // already reflects the live state.
  useEffect(() => {
    if (isStreaming) return;
    let cancelled = false;

    const poll = async () => {
      try {
        const status = await getStatus();
        if (cancelled) return;
        setExternallyBusy(status.run_active);
        if (status.waiting_for_answer && pendingQuestion === null) {
          setPendingQuestion(status.pending_question);
        } else if (!status.waiting_for_answer && pendingQuestion !== null) {
          setPendingQuestion(null);
        }
      } catch {
        // Backend unreachable — leave state as-is, try again next tick.
      }
    };

    void poll();
    const interval = setInterval(poll, STATUS_POLL_MS);
    return () => {
      cancelled = true;
      clearInterval(interval);
    };
  }, [isStreaming, pendingQuestion]);

  return {
    transcript,
    pendingQuestion,
    isStreaming,
    externallyBusy,
    error,
    sendMessage,
    answerQuestion,
    reset,
  };
}
