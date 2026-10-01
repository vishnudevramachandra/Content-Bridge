import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { MermaidDiagram } from "./MermaidDiagram";

function CodeBlock({
  className,
  children,
}: {
  className?: string;
  children?: React.ReactNode;
}) {
  const text = String(children).replace(/\n$/, "");

  if (className === "language-mermaid") {
    return <MermaidDiagram code={text} />;
  }

  if (!className) {
    // No language class — react-markdown/remark's signal for inline code.
    return <code className="rounded bg-gray-100 px-1 py-0.5 text-[0.85em]">{text}</code>;
  }

  return (
    <pre className="overflow-x-auto rounded-lg bg-gray-900 p-3 text-xs text-gray-100">
      <code>{text}</code>
    </pre>
  );
}

interface MessageBubbleProps {
  text: string;
  align: "left" | "right";
  pending?: boolean;
}

/** Renders one assistant/user text entry as markdown — including
 * rendering any ```mermaid fenced block as an actual diagram instead of
 * a code block, so the orchestrator's get_ontology_data-backed
 * visualizations (see VISUALIZING THE ONTOLOGIES in
 * orchestrator_agent.py) show up as images inline in the transcript. */
export function MessageBubble({ text, align, pending }: MessageBubbleProps) {
  const isUser = align === "right";
  return (
    <div className={`flex ${isUser ? "justify-end" : "justify-start"}`}>
      <div
        className={`max-w-[85%] rounded-2xl px-4 py-2.5 text-sm leading-relaxed ${
          isUser
            ? "bg-indigo-600 text-white"
            : "border border-gray-200 bg-white text-gray-900"
        }`}
      >
        {text === "" && pending ? (
          <span className="inline-block h-4 w-4 animate-pulse rounded-full bg-gray-300" />
        ) : (
          <ReactMarkdown
            remarkPlugins={[remarkGfm]}
            components={{
              code: ({ className, children }) => (
                <CodeBlock className={className}>{children}</CodeBlock>
              ),
              p: ({ children }) => <p className="whitespace-pre-wrap">{children}</p>,
            }}
          >
            {text}
          </ReactMarkdown>
        )}
        {pending && text !== "" && (
          <span className="ml-1 inline-block h-3 w-1.5 animate-pulse bg-gray-400 align-middle" />
        )}
      </div>
    </div>
  );
}
