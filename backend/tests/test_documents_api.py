import pytest
from httpx import AsyncClient, ASGITransport
from unittest.mock import AsyncMock, patch, MagicMock
from app.main import app


def make_mock_document():
    """Helper to create a mock document record."""
    return {
        "id": "abc-123",
        "name": "test.pdf",
        "created_at": "2024-01-01T00:00:00+00:00"
    }


def make_mock_chunks():
    """Helper to create mock similarity search results."""
    return [
        {
            "content": "Relevant content here.",
            "page_number": 1,
            "chunk_index": 0,
            "similarity": 0.9
        }
    ]


@pytest.fixture
def mock_pdf_pipeline():
    """Mock the entire PDF processing pipeline."""
    with patch("app.api.documents.extract_text_from_pdf", new_callable=AsyncMock) as mock_extract, \
         patch("app.api.documents.chunk_pages") as mock_chunk, \
         patch("app.api.documents.embed_chunks", new_callable=AsyncMock) as mock_embed, \
         patch("app.api.documents.save_document", new_callable=AsyncMock) as mock_save_doc, \
         patch("app.api.documents.save_chunks", new_callable=AsyncMock) as mock_save_chunks:

        mock_extract.return_value = [{"page_number": 1, "text": "Sample text"}]
        mock_chunk.return_value = [{"content": "Sample chunk", "page_number": 1, "chunk_index": 0}]
        mock_embed.return_value = [{"content": "Sample chunk", "page_number": 1, "chunk_index": 0, "embedding": [0.1] * 1536}]
        mock_save_doc.return_value = make_mock_document()
        mock_save_chunks.return_value = None

        yield {
            "extract": mock_extract,
            "chunk": mock_chunk,
            "embed": mock_embed,
            "save_doc": mock_save_doc,
            "save_chunks": mock_save_chunks
        }


# upload tests

@pytest.mark.asyncio
async def test_upload_document_success(mock_pdf_pipeline):
    """Should successfully upload and process a PDF."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post(
            "/documents/upload",
            files={"file": ("test.pdf", b"fake pdf content", "application/pdf")}
        )

    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "test.pdf"
    assert data["id"] == "abc-123"


@pytest.mark.asyncio
async def test_upload_rejects_non_pdf():
    """Should reject non-PDF files."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post(
            "/documents/upload",
            files={"file": ("test.png", b"fake image content", "image/png")}
        )

    assert response.status_code == 400
    assert "Invalid file type" in response.json()["detail"]


# list documents tests 

@pytest.mark.asyncio
async def test_list_documents():
    """Should return list of uploaded documents."""
    with patch("app.api.documents.get_documents", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = [make_mock_document()]

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.get("/documents/")

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["name"] == "test.pdf"


@pytest.mark.asyncio
async def test_list_documents_empty():
    """Should return empty list when no documents uploaded."""
    with patch("app.api.documents.get_documents", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = []

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.get("/documents/")

    assert response.status_code == 200
    assert response.json() == []


# delete tests 

@pytest.mark.asyncio
async def test_delete_document():
    """Should successfully delete a document."""
    with patch("app.api.documents.delete_document", new_callable=AsyncMock) as mock_delete:
        mock_delete.return_value = None

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.delete("/documents/abc-123")

    assert response.status_code == 200
    assert "deleted successfully" in response.json()["message"]


# ── query tests ───────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_query_document_success():
    """Should return answer and sources for a valid question."""
    with patch("app.api.documents.query_document", new_callable=AsyncMock) as mock_query:
        mock_query.return_value = {
            "answer": "The answer is 42.",
            "sources": [{"page_number": 1, "content": "Relevant content..."}]
        }

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post(
                "/documents/query",
                json={"question": "What is the answer?"}
            )

    assert response.status_code == 200
    data = response.json()
    assert data["answer"] == "The answer is 42."
    assert len(data["sources"]) == 1


@pytest.mark.asyncio
async def test_query_rejects_empty_question():
    """Should reject empty questions."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post(
            "/documents/query",
            json={"question": ""}
        )

    assert response.status_code == 400
    assert "empty" in response.json()["detail"]