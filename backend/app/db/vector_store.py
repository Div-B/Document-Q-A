from app.db.client import get_supabase_client

async def similarity_search(query_embedding: list[float], match_count: int = 5) -> list[dict]:
    """
    Find the most semantically similar chunks to a query embedding.

    Args:
        query_embedding: The embedding vector of the user's question
        match_count: Number of similar chunks to return (default 5)

    Returns:
        List of the most similar chunks with their content and metadata
    """
    client = get_supabase_client()

    response = client.rpc(
        "match_chunks",
        {
            "query_embedding": query_embedding,
            "match_count": match_count
        }
    ).execute()

    return response.data