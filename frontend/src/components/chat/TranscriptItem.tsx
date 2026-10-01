import type { TranscriptEntry } from "../../lib/types";
import { ErrorBanner } from "./ErrorBanner";
import { MessageBubble } from "./MessageBubble";
import { QuestionItem } from "./QuestionItem";
import { SubAgentActivity } from "./SubAgentActivity";
import { SystemAlertBanner } from "./SystemAlertBanner";
import { ToolActivity } from "./ToolActivity";

export function TranscriptItem({ entry }: { entry: TranscriptEntry }) {
  switch (entry.kind) {
    case "user_message":
      return <MessageBubble text={entry.text} align="right" />;
    case "assistant_text":
      return <MessageBubble text={entry.text} align="left" pending={!entry.done} />;
    case "sub_agent":
      return (
        <SubAgentActivity
          agentName={entry.agentName}
          instruction={entry.instruction}
          status={entry.status}
          summary={entry.summary}
        />
      );
    case "tool":
      return (
        <ToolActivity
          toolName={entry.toolName}
          args={entry.args}
          status={entry.status}
          result={entry.result}
        />
      );
    case "system_alert":
      return <SystemAlertBanner content={entry.content} />;
    case "answered_question":
      return <QuestionItem question={entry.question} answer={entry.answer} />;
    case "error":
      return <ErrorBanner detail={entry.detail} />;
    default:
      return null;
  }
}
