import { useContext } from "react";
import { ChatContext, type ChatContextValue } from "./chatContextInstance";

export function useChatContext(): ChatContextValue {
  const ctx = useContext(ChatContext);
  if (ctx === null) {
    throw new Error("useChatContext must be used within a ChatProvider");
  }
  return ctx;
}
