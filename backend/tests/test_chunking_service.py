import pytest
from app.services.chunking_service import chunk_text, chunk_pages


# chunk_text tests 

def test_chunk_text_basic():
    """A long text should be split into multiple chunks."""
    text = " ".join(["word"] * 1100)  # 1100 words
    chunks = chunk_text(text, chunk_size=500, overlap=50)
    assert len(chunks) > 1


def test_chunk_text_respects_chunk_size():
    """Each chunk should contain at most chunk_size words."""
    text = " ".join(["word"] * 1000)
    chunks = chunk_text(text, chunk_size=500, overlap=50)
    for chunk in chunks:
        assert len(chunk.split()) <= 500


def test_chunk_text_overlap():
    """Consecutive chunks should share words at the boundary."""
    text = " ".join([str(i) for i in range(200)])  # "0 1 2 3 ... 199"
    chunks = chunk_text(text, chunk_size=100, overlap=20)

    # Get last 20 words of first chunk
    first_chunk_tail = chunks[0].split()[-20:]
    # Get first 20 words of second chunk
    second_chunk_head = chunks[1].split()[:20]

    assert first_chunk_tail == second_chunk_head


def test_chunk_text_short_text():
    """Text shorter than chunk_size should return a single chunk."""
    text = "This is a short text"
    chunks = chunk_text(text, chunk_size=500, overlap=50)
    assert len(chunks) == 1
    assert chunks[0] == text


def test_chunk_text_empty_string():
    """Empty text should return a single empty chunk."""
    chunks = chunk_text("", chunk_size=500, overlap=50)
    assert chunks == []


# chunk_pages tests 

def test_chunk_pages_basic():
    """Pages should be chunked and returned with metadata."""
    pages = [
        {"page_number": 1, "text": " ".join(["word"] * 600)},
        {"page_number": 2, "text": " ".join(["word"] * 600)},
    ]
    chunks = chunk_pages(pages)
    assert len(chunks) > 2


def test_chunk_pages_preserves_page_number():
    """Each chunk should know which page it came from."""
    pages = [
        {"page_number": 3, "text": " ".join(["word"] * 100)},
    ]
    chunks = chunk_pages(pages)
    for chunk in chunks:
        assert chunk["page_number"] == 3


def test_chunk_pages_chunk_index_increments():
    """chunk_index should increment across all pages."""
    pages = [
        {"page_number": 1, "text": " ".join(["word"] * 600)},
        {"page_number": 2, "text": " ".join(["word"] * 600)},
    ]
    chunks = chunk_pages(pages)
    indices = [c["chunk_index"] for c in chunks]
    assert indices == list(range(len(chunks)))


def test_chunk_pages_empty():
    """Empty pages list should return empty chunks list."""
    chunks = chunk_pages([])
    assert chunks == []