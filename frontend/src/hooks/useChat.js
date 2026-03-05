import { useState, useCallback, useRef, useEffect } from "react";
import { sendMessage, getChatHistory } from "../services/api";
import { useAuth } from "../context/AuthContext";

export function useChat() {
  const { currentUser } = useAuth();
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const initialised = useRef(false);

  // Load chat history on mount (only when authenticated)
  useEffect(() => {
    if (initialised.current || !currentUser) return;
    initialised.current = true;

    getChatHistory()
      .then((data) => {
        if (data.messages?.length) {
          setMessages(data.messages);
        }
      })
      .catch(() => {
        // Silently fail — history just won't load
      });
  }, [currentUser]);

  const send = useCallback(async (text) => {
    if (!text.trim()) return;

    const userMsg = { role: "user", content: text, sources: [] };
    setMessages((prev) => [...prev, userMsg]);
    setLoading(true);
    setError(null);

    try {
      const data = await sendMessage(text);
      const botMsg = {
        role: "assistant",
        content: data.response,
        sources: data.sources || [],
      };
      setMessages((prev) => [...prev, botMsg]);
    } catch (err) {
      setError(err.response?.data?.detail || "Failed to get response");
    } finally {
      setLoading(false);
    }
  }, []);

  const clear = useCallback(() => {
    setMessages([]);
  }, []);

  return { messages, loading, error, send, clear };
}
