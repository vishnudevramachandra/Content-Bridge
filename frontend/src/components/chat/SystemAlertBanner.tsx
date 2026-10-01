/** The periodic certification-expiry worker (see `_periodic_alert_worker`
 * in main.py) injects alerts straight into the live run via
 * `AgentRun.enqueue()` — this renders that as a distinct banner rather
 * than a normal chat bubble, since the human didn't type it. */
export function SystemAlertBanner({ content }: { content: string }) {
  return (
    <div className="flex justify-center">
      <div className="max-w-[90%] rounded-lg border border-amber-300 bg-amber-50 px-3 py-2 text-xs text-amber-800">
        <span className="font-semibold">System alert: </span>
        <span className="whitespace-pre-wrap">{content}</span>
      </div>
    </div>
  );
}
