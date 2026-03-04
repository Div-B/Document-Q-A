import { useState, useCallback } from "react";
import type { Message } from "../types";
import { streamQuery } from "../services/api";

export const useChat = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const sendMessage = useCallback(async (question: string) => {
    if (!question.trim() || isLoading) return;

    const userMessage: Message = {
      id: crypto.randomUUID(),
      role: "user",
      content: question,
    };

    const assistantMessage: Message = {
      id: crypto.randomUUID(),
      role: "assistant",
      content: "",
      isStreaming: true,
    };

    setMessages((prev) => [...prev, userMessage, assistantMessage]);
    setIsLoading(true);
    setError(null);

    try {
      await streamQuery(
        question,
        (token) => {
          // Append each token to the assistant message
          setMessages((prev) =>
            prev.map((msg) =>
              msg.id === assistantMessage.id
                ? { ...msg, content: msg.content + token }
                : msg
            )
          );
        },
        () => {
          // Mark streaming as done
          setMessages((prev) =>
            prev.map((msg) =>
              msg.id === assistantMessage.id
                ? { ...msg, isStreaming: false }
                : msg
            )
          );
          setIsLoading(false);
        }
      );
    } catch (err: any) {
      setError(err.message || "Failed to get answer.");
      setMessages((prev) => prev.filter((msg) => msg.id !== assistantMessage.id));
      setIsLoading(false);
    }
  }, [isLoading]);

  const clearMessages = () => setMessages([]);

  return { messages, isLoading, error, sendMessage, clearMessages };
};