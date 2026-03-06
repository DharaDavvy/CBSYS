import { useState, useRef, useEffect } from "react";
import { useChat } from "../../hooks/useChat";
import MessageBubble from "./MessageBubble";
import ThinkingBubble from "./ThinkingBubble";

export default function ChatWindow() {
  const { messages, loading, error, send } = useChat();
  const [input, setInput] = useState("");
  const bottomRef = useRef(null);

  // Auto-scroll to bottom on new messages
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  function handleSend(e) {
    e.preventDefault();
    if (!input.trim() || loading) return;
    send(input.trim());
    setInput("");
  }

  return (
    <div className="flex flex-col h-[calc(100vh-57px)]">
      {/* Header */}
      <div className="border-b border-gray-200 px-6 py-4">
        <h2 className="text-lg font-semibold text-gray-900">Faculty Advisor</h2>
        <p className="text-sm text-gray-500">
          Ask questions about your curriculum, courses, and career paths
        </p>
      </div>

      {/* Messages area */}
      <div className="flex-1 overflow-y-auto px-6 py-4">
        {messages.length === 0 && (
          <div className="flex flex-col items-center justify-center h-full text-center text-gray-400">
            <div className="w-16 h-16 bg-[#f4fce8] rounded-none flex items-center justify-center mb-4">
              <svg className="w-8 h-8 text-[#8cc63f]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
              </svg>
            </div>
            <p className="font-medium text-gray-600 mb-1">Start a conversation</p>
            <p className="text-sm">
              Try asking about course prerequisites, career paths, or your academic roadmap.
            </p>
          </div>
        )}

        {messages.map((msg, i) => (
          <MessageBubble key={i} message={msg} />
        ))}

        {loading && <ThinkingBubble />}

        {error && (
          <div className="text-sm text-red-600 bg-red-50 px-3 py-2 rounded-none mb-4">
            {error}
          </div>
        )}

        <div ref={bottomRef} />
      </div>

      {/* Input bar */}
      <form onSubmit={handleSend} className="border-t border-gray-200 px-6 py-4">
        <div className="flex gap-3">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Type your question..."
            className="flex-1 px-4 py-2.5 border border-gray-300 rounded-none focus:ring-2 focus:ring-[#8cc63f] focus:border-[#8cc63f] outline-none"
            disabled={loading}
          />
          <button
            type="submit"
            disabled={loading || !input.trim()}
            className="px-5 py-2.5 bg-[#8cc63f] text-white font-medium rounded-none hover:bg-[#7db437] disabled:opacity-50 transition cursor-pointer"
          >
            Send
          </button>
        </div>
      </form>
    </div>
  );
}
