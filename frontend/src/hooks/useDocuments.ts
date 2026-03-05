import { useState, useEffect, useCallback } from "react";
import toast from "react-hot-toast";
import type { Document } from "../types";
import { getDocuments, uploadDocument, deleteDocument } from "../services/api";

export const useDocuments = () => {
  const [documents, setDocuments] = useState<Document[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchDocuments = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const docs = await getDocuments();
      setDocuments(docs);
    } catch (err: any) {
    const message = err.message || "Failed to load documents";
      setError(message);
      toast.error(message);
    } finally {
      setIsLoading(false);
    }
  }, []);

  const upload = async (file: File) => {
    setIsUploading(true);
    setError(null);
    const toastId = toast.loading(`Uploading ${file.name}...`);
    try {
      const doc = await uploadDocument(file);
      setDocuments((prev) => [doc, ...prev]);
      toast.success(`${file.name} uploaded successfully!`, { id: toastId });
      return doc;
    } catch (err: any) {
      const message = err.response?.data?.detail || "Failed to upload document.";
      toast.error(message, { id: toastId });
      setError(message);
      throw err;
    } finally {
      setIsUploading(false);
    }
  };

  const remove = async (id: string) => {
    try {
      await deleteDocument(id);
      setDocuments((prev) => prev.filter((doc) => doc.id !== id));
      toast.success("Document deleted.");
    } catch (err: any) {
        const message = err.message || "Failed to delete document.";
        setError(message);
        toast.error(message);
    }
  };

  useEffect(() => {
    fetchDocuments();
  }, [fetchDocuments]);

  return { documents, isLoading, isUploading, error, upload, remove, fetchDocuments };
};