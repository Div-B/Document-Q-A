
def chunk_text(text: str, chunk_size: int = 500, overlap: int = 50) -> list[str]:
    """
    Split text into overlapping chunks by word count.

    Overlapped so that sentences split across chunk boundaries
    still appear in full in at least one chunk, preserving context.

    Args:
        text: The raw text to split
        chunk_size: Number of words per chunk
        overlap: Number of words to repeat from the previous chunk

    Returns:
        List of text chunks
    """
    words = text.split()
    chunks = []
    start = 0

    while start <len(words):
        end = start + chunk_size
        chunk = " ".join(words[start:end])
        chunks.append(chunk)

        start += chunk_size - overlap
    return chunks

def chunk_pages(pages: list[dict], chunk_size: int = 500, overlap: int = 50) -> list[dict]:
    """
    Chunk all pages from a PDF into overlapping text chunks.

    Args:
        pages: List of page dicts from extract_text_from_pdf
        chunk_size: Number of words per chunk
        overlap: Number of words to repeat between chunks

    Returns:
        List of chunk dicts with content, page_number, chunk_index
    """
    all_chunks = []
    chunk_index = 0

    for page in pages:
        page_chunks = chunk_text(page["text"], chunk_size, overlap)

        for chunk in page_chunks:
            all_chunks.append({
                "content": chunk,
                "page_number": page["page_number"],
                "chunk_index": chunk_index
            })
            chunk_index += 1
    return all_chunks
