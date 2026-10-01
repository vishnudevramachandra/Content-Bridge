import { createContext } from "react";
import type { useChat } from "./useChat";

export type ChatContextValue = ReturnType<typeof useChat>;

export const ChatContext = createContext<ChatContextValue | null>(null);
