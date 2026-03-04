import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from fastapi import HTTPException
from app.services.query_service import generate_answer, query_document

def make_mock_chunks(count: int = 2) -> list[dict]:
    """Helper to create mock similarity search results."""
    return [
        {
            "content": f"This is chunk {i} with relevant content.",
            "page_number": i + 1,
            "chunk_index": i,
            "similarity": 0.9 - (i * 0.1)
        }
        for i in range(count)
    ]
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from fastapi import HTTPException
from app.services.query_service import generate_answer, query_document


def make_mock_chunks(count: int = 2) -> list[dict]:
    """Helper to create mock similarity search results."""
    return [
        {
            "content": f"This is chunk {i} with relevant content.",
            "page_number": i + 1,
            "chunk_index": i,
            "similarity": 0.9 - (i * 0.1)
        }
        for i in range(count)
    ]


# ── generate_answer tests ─────────────────────────────────────────

@pytest.mark.asyncio
async def test_generate_answer_returns_string():
    """generate_answer should return a string response."""
    mock_response = MagicMock()
    mock_response.choices = [MagicMock(message=MagicMock(content="This is the answer."))]

    with patch("app.services.query_service.client.chat.completions.create", new_callable=AsyncMock) as mock_create:
        mock_create.return_value = mock_response
        result = await generate_answer("What is this about?", make_mock_chunks())

    assert isinstance(result, str)
    assert result == "This is the answer."


@pytest.mark.asyncio
async def test_generate_answer_raises_on_api_failure():
    """generate_answer should raise HTTPException if OpenAI call fails."""
    with patch("app.services.query_service.client.chat.completions.create", new_callable=AsyncMock) as mock_create:
        mock_create.side_effect = Exception("API error")
        with pytest.raises(HTTPException) as exc:
            await generate_answer("What is this about?", make_mock_chunks())

    assert exc.value.status_code == 500
    assert "Failed to generate answer" in exc.value.detail


# ── query_document tests ──────────────────────────────────────────

@pytest.mark.asyncio
async def test_query_document_rejects_empty_question():
    """query_document should reject empty questions."""
    with pytest.raises(HTTPException) as exc:
        await query_document("")

    assert exc.value.status_code == 400
    assert "empty" in exc.value.detail


@pytest.mark.asyncio
async def test_query_document_returns_answer_and_sources():
    """query_document should return answer and source chunks."""
    mock_answer = MagicMock()
    mock_answer.choices = [MagicMock(message=MagicMock(content="The answer is 42."))]

    with patch("app.services.query_service.embed_text", new_callable=AsyncMock) as mock_embed, \
         patch("app.services.query_service.similarity_search", new_callable=AsyncMock) as mock_search, \
         patch("app.services.query_service.client.chat.completions.create", new_callable=AsyncMock) as mock_create:

        mock_embed.return_value = [0.1] * 1536
        mock_search.return_value = make_mock_chunks()
        mock_create.return_value = mock_answer

        result = await query_document("What is the answer?")

    assert "answer" in result
    assert "sources" in result
    assert result["answer"] == "The answer is 42."
    assert len(result["sources"]) == 2


@pytest.mark.asyncio
async def test_query_document_raises_when_no_chunks_found():
    """query_document should raise 404 if no similar chunks are found."""
    with patch("app.services.query_service.embed_text", new_callable=AsyncMock) as mock_embed, \
         patch("app.services.query_service.similarity_search", new_callable=AsyncMock) as mock_search:

        mock_embed.return_value = [0.1] * 1536
        mock_search.return_value = []  # no chunks found

        with pytest.raises(HTTPException) as exc:
            await query_document("What is the answer?")

    assert exc.value.status_code == 404
    assert "No relevant content found" in exc.value.detail