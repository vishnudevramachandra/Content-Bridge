import { NavLink, Route, Routes } from "react-router-dom";
import { StatusBadge } from "./components/StatusBadge";
import { ChatView } from "./components/chat/ChatView";
import { MappingView } from "./components/mapping/MappingView";
import { SchemaView } from "./components/schema/SchemaView";
import { SyncLogView } from "./components/synclog/SyncLogView";
import { ChatProvider } from "./lib/ChatContext";

const NAV_ITEMS = [
  { to: "/", label: "Chat" },
  { to: "/schema", label: "Schema" },
  { to: "/mappings", label: "Mapping Review" },
  { to: "/sync-log", label: "Sync Activity" },
];

function App() {
  return (
    // Mounted once here, outside <Routes> — App itself never unmounts
    // on navigation, so the one chat conversation it owns survives
    // switching to another page and back.
    <ChatProvider>
      <div className="flex h-screen bg-gray-50 text-gray-900">
        <aside className="flex w-52 flex-col border-r border-gray-200 bg-white">
          <div className="px-4 py-4">
            <h1 className="text-sm font-bold">Content-Bridge</h1>
            <p className="text-xs text-gray-400">Orchestrator console</p>
          </div>
          <nav className="flex-1 space-y-1 px-2">
            {NAV_ITEMS.map((item) => (
              <NavLink
                key={item.to}
                to={item.to}
                end={item.to === "/"}
                className={({ isActive }) =>
                  `block rounded-lg px-3 py-2 text-sm ${
                    isActive ? "bg-indigo-50 text-indigo-700" : "text-gray-600 hover:bg-gray-50"
                  }`
                }
              >
                {item.label}
              </NavLink>
            ))}
          </nav>
          <div className="border-t border-gray-100 px-3 py-3">
            <StatusBadge />
          </div>
        </aside>
        <main className="flex-1 overflow-hidden">
          <Routes>
            <Route path="/" element={<ChatView />} />
            <Route path="/schema" element={<SchemaView />} />
            <Route path="/mappings" element={<MappingView />} />
            <Route path="/sync-log" element={<SyncLogView />} />
          </Routes>
        </main>
      </div>
    </ChatProvider>
  );
}

export default App;
