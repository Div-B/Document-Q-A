import { Sidebar } from "./components/Sidebar";
import { ChatWindow } from "./components/ChatWindow";
import { useDocuments } from "./hooks/useDocuments";
import { useChat } from "./hooks/useChat";

export default function App() {
  const { documents, isLoading, isUploading, error, upload, remove } = useDocuments();
  const { messages, isLoading: isChatLoading, error: chatError, sendMessage, clearMessages } = useChat();

  return (
    <div className="flex h-screen bg-gray-950 overflow-hidden">
      <Sidebar
        documents={documents}
        isLoading={isLoading}
        isUploading={isUploading}
        error={error}
        onUpload={upload}
        onDelete={remove}
      />
      <ChatWindow
        messages={messages}
        isLoading={isChatLoading}
        error={chatError}
        onSend={sendMessage}
        onClear={clearMessages}
      />
    </div>
  );
}