import axios, { AxiosError } from "axios";
import type { Document, QueryRequest } from "../types";

const BASE_URL = "http://localhost:8000";

const api = axios.create({
  baseURL: BASE_URL,
  headers: {
    "Content-Type": "application/json",
  },
  timeout: 30000,
});
// Global response interceptor — normalize all errors
api.interceptors.response.use(
    (response) => response,
    (error: AxiosError<{ detail: string }>) => {
      if (error.code === "ECONNABORTED") {
        throw new Error("Request timed out. Please try again.");
      }
      if (!error.response) {
        throw new Error("Cannot connect to server. Is the backend running?");
      }
      const detail = error.response.data?.detail;
      if (typeof detail === "string") {
        throw new Error(detail);
      }
      throw new Error(`Request failed with status ${error.response.status}`);
    }
  );
export const uploadDocument = async (file: File): Promise<Document> => {
  const formData = new FormData();
  formData.append("file", file);

  const response = await api.post<Document>("/documents/upload", formData, {
    headers: { "Content-Type": "multipart/form-data" },
  });
  return response.data;
};

export const getDocuments = async (): Promise<Document[]> => {
  const response = await api.get<Document[]>("/documents/");
  return response.data;
};

export const deleteDocument = async (id: string): Promise<void> => {
  await api.delete(`/documents/${id}`);
};


export const queryDocuments = async (request: QueryRequest) => {
  const response = await api.post("/documents/query", request);
  return response.data;
};

export const streamQuery = async (
  question: string,
  onToken: (token: string) => void,
  onDone: () => void
): Promise<void> => {
  const response = await fetch(`${BASE_URL}/documents/query/stream`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ question, match_count: 5 }),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || "Failed to get answer");
  }

  const reader = response.body?.getReader();
  const decoder = new TextDecoder();

  if (!reader) throw new Error("No response body");

  while (true) {
    const { done, value } = await reader.read();
    if (done) {
      onDone();
      break;
    }
    const token = decoder.decode(value);
    onToken(token);
  }
};