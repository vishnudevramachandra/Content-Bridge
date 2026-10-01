import mermaid from "mermaid";
import { useEffect, useId, useRef, useState } from "react";

// "strict" runs mermaid's own DOMPurify-based sanitization on the SVG it
// hands back — worth keeping even though we're in a single-user local
// tool, since the diagram text itself ultimately comes from the model
// (see get_ontology_data/VISUALIZING THE ONTOLOGIES in orchestrator_agent.py),
// not from a fixed template we wrote ourselves.
mermaid.initialize({
  startOnLoad: false,
  securityLevel: "strict",
  theme: "neutral",
  // Without this, mermaid's own fallback on a parse error inserts a
  // "Syntax error in text" box directly into `document.body` — outside
  // any component we control — instead of just rejecting render()'s
  // promise. We already render our own error UI in the catch below.
  suppressErrorRendering: true,
});

/** Renders one ```mermaid fenced code block as a static (non-interactive)
 * SVG diagram — used for both the schema and mapping visualizations the
 * orchestrator produces on request. */
export function MermaidDiagram({ code }: { code: string }) {
  const reactId = useId().replace(/[^a-zA-Z0-9]/g, "");
  const containerRef = useRef<HTMLDivElement>(null);
  const [svg, setSvg] = useState<string | null>(null);
  const [renderError, setRenderError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    setSvg(null);
    setRenderError(null);

    mermaid
      .render(`mermaid-${reactId}`, code)
      .then((result) => {
        if (!cancelled) setSvg(result.svg);
      })
      .catch((e: unknown) => {
        if (!cancelled) setRenderError(e instanceof Error ? e.message : String(e));
      });

    return () => {
      cancelled = true;
    };
  }, [code, reactId]);

  // Mermaid already sets `width="100%"` on the root <svg> itself, but
  // also caps it with an inline `max-width: <computed natural size>px`
  // — fine for shrinking into a narrow container, but it also stops the
  // diagram from growing to fill a *wider* one, leaving dead space on a
  // big screen. Strip that cap once the SVG is in the DOM; height then
  // follows proportionally from the SVG's own viewBox aspect ratio.
  useEffect(() => {
    containerRef.current?.querySelector("svg")?.style.removeProperty("max-width");
  }, [svg]);

  if (renderError) {
    return (
      <div className="rounded border border-red-200 bg-red-50 p-3 text-xs text-red-700">
        <p className="font-medium">Couldn't render this diagram.</p>
        <pre className="mt-1 whitespace-pre-wrap">{renderError}</pre>
        <pre className="mt-2 whitespace-pre-wrap text-red-500">{code}</pre>
      </div>
    );
  }

  if (svg === null) {
    return <div className="text-xs text-gray-400">Rendering diagram…</div>;
  }

  return (
    <div
      ref={containerRef}
      className="h-full w-full overflow-auto rounded-lg border border-gray-200 bg-white p-3"
      // eslint-disable-next-line @typescript-eslint/naming-convention
      dangerouslySetInnerHTML={{ __html: svg }}
    />
  );
}
