from fastapi import APIRouter, UploadFile, File, HTTPException, Request
from fastapi.responses import StreamingResponse
from app.models.schemas import DocumentResponse, QueryRequest, QueryResponse, DeleteResponse
from app.services.pdf_service import extract_text_from_pdf
from app.services.chunking_service import chunk_pages
from app.services.embedding_service import embed_chunks
from app.services.query_service import stream_answer, query_document
from app.db.document_store import save_document, save_chunks, get_documents, delete_document
from app.db.vector_store import similarity_search
from app.services.embedding_service import embed_text
from slowapi import Limiter
from slowapi.util import get_remote_address
router = APIRouter(prefix="/documents", tags=["documents"])
limiter = Limiter(key_func=get_remote_address)


@router.post("/upload", response_model=DocumentResponse)
@limiter.limit("10/minute")
async def upload_document(request: Request, file: UploadFile = File(...)):
    """
    Upload a PDF document and process it for querying.
    Pipeline: parse → chunk → embed → store
    Limited to 10 uploads per minute per IP.
    """
    pages = await extract_text_from_pdf(file)
    chunks = chunk_pages(pages)
    if not chunks:
        raise HTTPException(
            status_code=422,
            detail="Could not extract any content from pdf"
        )
    embedded_chunks = await embed_chunks(chunks)
    document = await save_document(file.filename)
    await save_chunks(document["id"], embedded_chunks)
    return DocumentResponse(**document)


@router.get("/", response_model=list[DocumentResponse])
async def list_documents():
    """Retrieve all uploaded documents."""
    documents = await get_documents()
    return [DocumentResponse(**doc) for doc in documents]


@router.delete("/{document_id}", response_model=DeleteResponse)
async def remove_document(document_id: str):
    """Delete a document and all its associated chunks."""
    await delete_document(document_id)
    return DeleteResponse(message=f"Document {document_id} deleted successfully.")


@router.post("/query", response_model=QueryResponse)
@limiter.limit("30/minute")
async def query(request: Request, body: QueryRequest):
    """
    Query across all uploaded documents using RAG.
    Pipeline: embed question → similarity search → generate answer
    Limited to 30 queries per minute per IP.
    """
    result = await query_document(body.question, body.match_count)
    return QueryResponse(
        answer=result["answer"],
        sources=result["sources"]
    )


@router.post("/query/stream")
@limiter.limit("30/minute")
async def query_stream(request: Request, body: QueryRequest):
    """
    Stream an answer token by token using server sent events.
    Limited to 30 queries per minute per IP.
    """
    if not body.question.strip():
        raise HTTPException(
            status_code=400,
            detail="Question cannot be empty."
        )
    question_embedding = await embed_text(body.question)
    similar_chunks = await similarity_search(question_embedding, body.match_count)

    if not similar_chunks:
        raise HTTPException(
            status_code=404,
            detail="No relevant content found. Please upload a document first."
        )

    return StreamingResponse(
        stream_answer(body.question, similar_chunks),
        media_type="text/event-stream"
    )
