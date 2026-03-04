from openai import AsyncOpenAI
from app.config import settings
from fastapi import HTTPException

client = AsyncOpenAI(api_key=settings.openai_api_key)
EMBEDDING_MODEL = "text-embedding-3-small"
EMBEDDING_DIMENSIONS = 1536

async def embed_text(text: str) -> list[float]:
    """
    Convert a single text string into an embedding vector.

    Args:
        text: The text to embed

    Returns:
        A list of 1536 floats representing the text's meaning

    Raises:
        HTTPException 500: If the OpenAI API call fails
    """
    try:

        response = await client.embeddings.create(
            model=EMBEDDING_MODEL,
            input=text
        )
        return response.data[0].embedding
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate embedding: {str(e)}"
        )
    
async def embed_chunks(chunks: list[dict]) -> list[dict]:
    """
    Embed all chunks in a single API call.

    Sends all chunk contents to OpenAI at once instead of one by one,
    which is faster and uses fewer API calls.

    Args:
        chunks: List of chunk dicts from chunk_pages()

    Returns:
        The same chunks with an added 'embedding' key on each

    Raises:
        HTTPException 500: If the OpenAI API call fails
    """
    if not chunks:
        return []

    try:
        # Send all chunk contents in one API call
        response = await client.embeddings.create(
            model=EMBEDDING_MODEL,
            input=[chunk["content"] for chunk in chunks]
        )

        # response.data is ordered the same as our input
        # so we can zip them together safely
        for chunk, embedding_data in zip(chunks, response.data):
            chunk["embedding"] = embedding_data.embedding

        return chunks

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate embeddings: {str(e)}"
        )