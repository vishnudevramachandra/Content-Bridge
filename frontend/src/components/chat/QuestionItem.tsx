/** A question the orchestrator's `ask_user` paused on — either its own,
 * or one it's relaying from a delegated sub-agent. Shown as a durable
 * marker in the transcript, with the human's answer attached once
 * `POST /api/answer` resolves it. */
export function QuestionItem({
  question,
  answer,
}: {
  question: string;
  answer?: string;
}) {
  return (
    <div className="flex justify-start">
      <div className="max-w-[85%] rounded-xl border border-indigo-200 bg-indigo-50 px-4 py-2.5 text-sm text-indigo-900">
        <p className="font-medium">❓ {question}</p>
        {answer !== undefined ? (
          <p className="mt-1 text-indigo-700">↳ {answer}</p>
        ) : (
          <p className="mt-1 text-xs text-indigo-400">Waiting for an answer…</p>
        )}
      </div>
    </div>
  );
}
