import type { ReactNode } from "react";
import { ChatContext } from "./chatContextInstance";
import { useChat } from "./useChat";

/**
 * Owns the one `useChat()` instance for the whole app, mounted once in
 * `App.tsx` *outside* `<Routes>` so it survives route changes. Without
 * this, `ChatView` owned its own `useChat()` call directly — fine while
 * it stayed mounted, but react-router unmounts the previous route's
 * element on navigation, which threw the entire transcript away the
 * moment you switched to another page and back.
 */
export function ChatProvider({ children }: { children: ReactNode }) {
  const chat = useChat();
  return <ChatContext.Provider value={chat}>{children}</ChatContext.Provider>;
}
