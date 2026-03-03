import pytest
from unittest.mock import AsyncMock, MagicMock
from fastapi import HTTPException
from app.services.pdf_service import (
    extract_text_from_pdf,
    validate_pdf_file,
    validate_pdf_content
)


def make_mock_file(content_type: str = "application/pdf", contents: bytes = b"fake pdf bytes"):
    """Helper to create a mock UploadFile."""
    mock_file = MagicMock()
    mock_file.content_type = content_type
    mock_file.read = AsyncMock(return_value=contents)
    return mock_file


#validate_pdf_file tests

def test_validate_rejects_non_pdf():
    """Should reject non-PDF content types."""
    mock_file = make_mock_file(content_type="image/png")
    with pytest.raises(HTTPException) as exc:
        validate_pdf_file(mock_file, b"some content")
    assert exc.value.status_code == 400
    assert "Invalid file type" in exc.value.detail


def test_validate_rejects_empty_file():
    """Should reject empty file contents."""
    mock_file = make_mock_file()
    with pytest.raises(HTTPException) as exc:
        validate_pdf_file(mock_file, b"")
    assert exc.value.status_code == 400
    assert "empty" in exc.value.detail


def test_validate_rejects_file_too_large():
    """Should reject files exceeding the size limit."""
    large_content = b"x" * (10 * 1024 * 1024 + 1)
    mock_file = make_mock_file()
    with pytest.raises(HTTPException) as exc:
        validate_pdf_file(mock_file, large_content)
    assert exc.value.status_code == 400
    assert "too large" in exc.value.detail


def test_validate_accepts_valid_file():
    """Should not raise for a valid file."""
    mock_file = make_mock_file()
    validate_pdf_file(mock_file, b"valid content")  # should not raise


# validate_pdf_content tests

def test_validate_rejects_encrypted_pdf():
    """Should reject encrypted PDFs."""
    mock_pdf = MagicMock()
    mock_pdf.is_encrypted = True
    with pytest.raises(HTTPException) as exc:
        validate_pdf_content(mock_pdf)
    assert exc.value.status_code == 422
    assert "encrypted" in exc.value.detail


def test_validate_rejects_empty_pdf():
    """Should reject PDFs with no pages."""
    mock_pdf = MagicMock()
    mock_pdf.is_encrypted = False
    mock_pdf.__len__ = MagicMock(return_value=0)
    with pytest.raises(HTTPException) as exc:
        validate_pdf_content(mock_pdf)
    assert exc.value.status_code == 422
    assert "no pages" in exc.value.detail


# extract_text_from_pdf tests 
@pytest.mark.asyncio
async def test_rejects_corrupted_pdf():
    """Should reject corrupted PDF files."""
    mock_file = make_mock_file(contents=b"this is not a real pdf")
    with pytest.raises(HTTPException) as exc:
        await extract_text_from_pdf(mock_file)
    assert exc.value.status_code == 422