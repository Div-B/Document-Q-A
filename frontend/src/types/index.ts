export interface Document {
    id: string;
    name: string;
    created_at: string;
  }
  
  export interface SourceChunk {
    page_number: number;
    content: string;
  }
  
  export interface Message {
    id: string;
    role: "user" | "assistant";
    content: string;
    sources?: SourceChunk[];
    isStreaming?: boolean;
  }
  
  export interface QueryRequest {
    question: string;
    match_count?: number;
  }