import asyncio
from app.db.client import get_supabase_client


async def save_document(name: str) -> dict:
    """
    Save a document record to the database.

    Args:
        name: The filename of the uploaded PDF

    Returns:
        The created document record including its generated id
    """
    def _save():
        client = get_supabase_client()
        response = client.table("documents").insert({"name": name}).execute()
        return response.data[0]

    return await asyncio.to_thread(_save)


async def save_chunks(document_id: str, chunks: list[dict]) -> None:
    """
    Save all chunks for a document to the database.

    Args:
        document_id: The id of the parent document
        chunks: List of chunk dicts with content, embedding, page_number, chunk_index
    """
    rows = [
        {
            "document_id": document_id,
            "content": chunk["content"],
            "embedding": chunk["embedding"],
            "page_number": chunk["page_number"],
            "chunk_index": chunk["chunk_index"]
        }
        for chunk in chunks
    ]

    def _save():
        client = get_supabase_client()
        client.table("chunks").insert(rows).execute()

    await asyncio.to_thread(_save)


async def get_documents() -> list[dict]:
    """
    Retrieve all uploaded documents.

    Returns:
        List of document records ordered by most recent first
    """
    def _get():
        client = get_supabase_client()
        response = (
            client.table("documents")
            .select("*")
            .order("created_at", desc=True)
            .execute()
        )
        return response.data

    return await asyncio.to_thread(_get)


async def delete_document(document_id: str) -> None:
    """
    Delete a document and all its chunks (cascade handles chunks).

    Args:
        document_id: The id of the document to delete
    """
    def _delete():
        client = get_supabase_client()
        client.table("documents").delete().eq("id", document_id).execute()

    await asyncio.to_thread(_delete)