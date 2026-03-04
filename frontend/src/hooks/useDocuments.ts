import { useState, useEffect, useCallback } from "react";
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
    } catch {
      setError("Failed to load documents.");
    } finally {
      setIsLoading(false);
    }
  }, []);

  const upload = async (file: File) => {
    setIsUploading(true);
    setError(null);
    try {
      const doc = await uploadDocument(file);
      setDocuments((prev) => [doc, ...prev]);
      return doc;
    } catch (err: any) {
      const message = err.response?.data?.detail || "Failed to upload document.";
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
    } catch {
      setError("Failed to delete document.");
    }
  };

  useEffect(() => {
    fetchDocuments();
  }, [fetchDocuments]);

  return { documents, isLoading, isUploading, error, upload, remove, fetchDocuments };
};