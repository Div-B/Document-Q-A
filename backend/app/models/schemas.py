from pydantic import BaseModel
from datetime import datetime

class DocumentResponse(BaseModel):
    """Response model for a document record"""
    id: str
    name: str
    created_at: datetime

class QueryRequest(BaseModel):
    """Reequest model for queryiing a document"""
    question: str
    match_count: int = 5

class SourceChunk(BaseModel):
    """A source chunk returned with every query response"""
    page_number: int
    content: str

class QueryResponse(BaseModel):
    """Response model for a query result."""
    answer: str
    sources: list[SourceChunk]


class DeleteResponse(BaseModel):
    """Response model for a delete operation."""
    message: str   
