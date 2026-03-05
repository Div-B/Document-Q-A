import type { Document } from "../types";
import { UploadButton } from "./UploadButton";
import { sanitizeFileName } from "../utils/sanitize";

interface Props {
  documents: Document[];
  isLoading: boolean;
  isUploading: boolean;
  error: string | null;
  onUpload: (file: File) => void;
  onDelete: (id: string) => void;
}

export const Sidebar = ({ documents, isLoading, isUploading, error, onUpload, onDelete }: Props) => {
  return (
    <div className="w-72 h-screen bg-gray-900 border-r border-gray-700 flex flex-col p-4 gap-4">
      <div>
        <h1 className="text-white text-lg font-semibold">📄 Doc Q&A</h1>
        <p className="text-gray-400 text-xs mt-1">Upload PDFs and ask questions</p>
      </div>

      <UploadButton onUpload={onUpload} isUploading={isUploading} />

      {error && (
        <div className="bg-red-900/50 border border-red-500 text-red-300 text-xs p-2 rounded">
          {error}
        </div>
      )}

      <div className="flex-1 overflow-y-auto">
        <p className="text-gray-500 text-xs uppercase tracking-wide mb-2">
          Documents ({documents.length})
        </p>

        {isLoading ? (
          <p className="text-gray-500 text-sm">Loading...</p>
        ) : documents.length === 0 ? (
          <p className="text-gray-500 text-sm">No documents yet. Upload a PDF to get started.</p>
        ) : (
          <ul className="flex flex-col gap-1">
            {documents.map((doc) => (
              <li
                key={doc.id}
                className="flex items-center justify-between gap-2 p-2 rounded-lg bg-gray-800 group"
              >
                <span className="text-gray-300 text-sm truncate flex-1" title={sanitizeFileName(doc.name)}>
                📄 {sanitizeFileName(doc.name)}
                </span>
                <button
                    onClick={() => {
                        if (window.confirm(`Delete "${sanitizeFileName(doc.name)}"? This cannot be undone.`)) {
                            onDelete(doc.id);
                        }
                    }}
                    className="text-gray-600 hover:text-red-400 transition-colors opacity-0 group-hover:opacity-100 text-xs shrink-0"
                    title="Delete document"
                    >
                    ✕
                </button>
                
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  );
};
