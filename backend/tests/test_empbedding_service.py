import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from fastapi import HTTPException
from app.services.embedding_service import embed_text, embed_chunks


def make_mock_embedding(dimensions: int = 1536) -> list[float]:
    """Helper to create a fake embedding vector."""
    return [0.1] * dimensions


def make_mock_response(count: int = 1) -> MagicMock:
    """Helper to create a mock OpenAI embeddings response."""
    mock_response = MagicMock()
    mock_response.data = [
        MagicMock(embedding=make_mock_embedding())
        for _ in range(count)
    ]
    return mock_response


# embed_text tests

@pytest.mark.asyncio
async def test_embed_text_returns_vector():
    """embed_text should return a list of floats."""
    with patch("app.services.embedding_service.client.embeddings.create", new_callable=AsyncMock) as mock_create:
        mock_create.return_value = make_mock_response(count=1)
        result = await embed_text("Hello world")

    assert isinstance(result, list)
    assert len(result) == 1536
    assert all(isinstance(x, float) for x in result)


@pytest.mark.asyncio
async def test_embed_text_calls_correct_model():
    """embed_text should use the correct embedding model."""
    with patch("app.services.embedding_service.client.embeddings.create", new_callable=AsyncMock) as mock_create:
        mock_create.return_value = make_mock_response(count=1)
        await embed_text("Hello world")

    mock_create.assert_called_once_with(
        model="text-embedding-3-small",
        input="Hello world"
    )


@pytest.mark.asyncio
async def test_embed_text_raises_on_api_failure():
    """embed_text should raise HTTPException if OpenAI call fails."""
    with patch("app.services.embedding_service.client.embeddings.create", new_callable=AsyncMock) as mock_create:
        mock_create.side_effect = Exception("API error")
        with pytest.raises(HTTPException) as exc:
            await embed_text("Hello world")

    assert exc.value.status_code == 500
    assert "Failed to generate embedding" in exc.value.detail


#embed_chunks tests

@pytest.mark.asyncio
async def test_embed_chunks_single_api_call():
    """embed_chunks should make only one API call regardless of chunk count."""
    chunks = [
        {"content": "First chunk", "page_number": 1, "chunk_index": 0},
        {"content": "Second chunk", "page_number": 1, "chunk_index": 1},
        {"content": "Third chunk", "page_number": 2, "chunk_index": 2},
    ]

    with patch("app.services.embedding_service.client.embeddings.create", new_callable=AsyncMock) as mock_create:
        mock_create.return_value = make_mock_response(count=3)
        await embed_chunks(chunks)

    # Should only be called once no matter how many chunks
    assert mock_create.call_count == 1


@pytest.mark.asyncio
async def test_embed_chunks_adds_embedding_to_each_chunk():
    """embed_chunks should add an embedding key to every chunk."""
    chunks = [
        {"content": "First chunk", "page_number": 1, "chunk_index": 0},
        {"content": "Second chunk", "page_number": 1, "chunk_index": 1},
    ]

    with patch("app.services.embedding_service.client.embeddings.create", new_callable=AsyncMock) as mock_create:
        mock_create.return_value = make_mock_response(count=2)
        result = await embed_chunks(chunks)

    assert all("embedding" in chunk for chunk in result)


@pytest.mark.asyncio
async def test_embed_chunks_preserves_chunk_metadata():
    """embed_chunks should not modify existing chunk fields."""
    chunks = [
        {"content": "First chunk", "page_number": 2, "chunk_index": 3},
    ]

    with patch("app.services.embedding_service.client.embeddings.create", new_callable=AsyncMock) as mock_create:
        mock_create.return_value = make_mock_response(count=1)
        result = await embed_chunks(chunks)

    assert result[0]["content"] == "First chunk"
    assert result[0]["page_number"] == 2
    assert result[0]["chunk_index"] == 3


@pytest.mark.asyncio
async def test_embed_chunks_empty_list():
    """embed_chunks should return empty list without calling API."""
    with patch("app.services.embedding_service.client.embeddings.create", new_callable=AsyncMock) as mock_create:
        result = await embed_chunks([])

    assert result == []
    assert mock_create.call_count == 0  # API should never be called


@pytest.mark.asyncio
async def test_embed_chunks_raises_on_api_failure():
    """embed_chunks should raise HTTPException if OpenAI call fails."""
    chunks = [{"content": "chunk", "page_number": 1, "chunk_index": 0}]

    with patch("app.services.embedding_service.client.embeddings.create", new_callable=AsyncMock) as mock_create:
        mock_create.side_effect = Exception("API error")
        with pytest.raises(HTTPException) as exc:
            await embed_chunks(chunks)

    assert exc.value.status_code == 500
    assert "Failed to generate embeddings" in exc.value.detail