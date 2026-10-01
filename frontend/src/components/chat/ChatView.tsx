import { useEffect, useRef } from "react";
import { useChatContext } from "../../lib/useChatContext";
import { Composer } from "./Composer";
import { TranscriptItem } from "./TranscriptItem";

export function ChatView() {
  const {
    transcript,
    pendingQuestion,
    isStreaming,
    externallyBusy,
    error,
    sendMessage,
    answerQuestion,
    reset,
  } = useChatContext();
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [transcript, pendingQuestion]);

  return (
    <div className="flex h-full flex-col">
      <div className="flex items-center justify-between border-b border-gray-200 px-4 py-3">
        <div>
          <h1 className="text-sm font-semibold text-gray-900">Orchestrator conversation</h1>
          <p className="text-xs text-gray-500">
            {isStreaming ? "Running…" : externallyBusy ? "Busy elsewhere…" : "Idle"}
          </p>
        </div>
        <button
          type="button"
          onClick={() => void reset()}
          className="rounded-full border border-gray-300 px-3 py-1 text-xs text-gray-600 hover:bg-gray-50"
        >
          New conversation
        </button>
      </div>

      <div className="flex-1 space-y-3 overflow-y-auto px-4 py-4">
        {transcript.length === 0 && (
          <p className="mt-8 text-center text-sm text-gray-400">
            Ask the orchestrator to discover a schema, build a mapping, or sync a product.
          </p>
        )}
        {transcript.map((entry) => (
          <TranscriptItem key={entry.id} entry={entry} />
        ))}
        <div ref={bottomRef} />
      </div>

      <div className="border-t border-gray-200 px-4 py-3">
        {error && <p className="mb-2 text-xs text-red-600">{error}</p>}
        {pendingQuestion !== null ? (
          <Composer
            variant="question"
            placeholder={`Answer: ${pendingQuestion}`}
            disabled={isStreaming}
            onSubmit={answerQuestion}
          />
        ) : (
          <Composer
            placeholder="Message the orchestrator…"
            disabled={isStreaming || externallyBusy}
            onSubmit={sendMessage}
          />
        )}
      </div>
    </div>
  );
}
