import type { Message } from "../types";

interface Props {
  message: Message;
}

export const MessageBubble = ({ message }: Props) => {
  const isUser = message.role === "user";

  return (
    <div className={`flex ${isUser ? "justify-end" : "justify-start"}`}>
      <div className={`max-w-[80%] rounded-2xl px-4 py-3 ${
        isUser
          ? "bg-blue-600 text-white rounded-br-sm"
          : "bg-gray-800 text-gray-100 rounded-bl-sm"
      }`}>
        <p className="text-sm whitespace-pre-wrap leading-relaxed">
          {message.content}
          {message.isStreaming && (
            <span className="inline-block w-1 h-4 bg-gray-400 animate-pulse ml-1 align-middle" />
          )}
        </p>

        {/* Source citations */}
        {message.sources && message.sources.length > 0 && (
          <div className="mt-3 pt-3 border-t border-gray-600">
            <p className="text-xs text-gray-400 mb-2">Sources:</p>
            <div className="flex flex-col gap-1">
              {message.sources.map((source, i) => (
                <div key={i} className="text-xs text-gray-400 bg-gray-700/50 rounded p-2">
                  <span className="text-blue-400 font-medium">Page {source.page_number}</span>
                  {" — "}
                  {source.content.slice(0, 100)}...
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};