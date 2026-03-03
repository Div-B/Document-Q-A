import pymupdf
from fastapi import UploadFile, HTTPException
from app.config import settings

MAX_FILE_SIZE_BYTES = settings.max_file_size_mb * 1024 * 1024

def validate_pdf_file(file: UploadFile, contents: bytes) ->None:
    """
    Validate a PDF file before processing.

    Args:
        file: The uploaded file object
        contents: The raw bytes of the file

    Raises:
        HTTPException 400: If file type, size, or content is invalid
        HTTPException 422: If PDF is encrypted, empty, or has no extractable text
    """
    if file.content_type != "application/pdf":
        raise HTTPException(
            status_code =400,
            detail=f"Invalid file type '{file.content_type}'. Only PDF files are accepted."
        )
    if not contents:
        raise HTTPException(
            status_code=400,
            detail="Uploaded file is empty."
        )
    if len(contents) > MAX_FILE_SIZE_BYTES:
        raise HTTPException(
            status_code=400,
            detail=f"File too large. Maximum size is {settings.max_file_size_mb}MB, got {len(contents) / 1024 / 1024:.1f}MB."
        )
def validate_pdf_content(pdf: pymupdf.Document) -> None:
    """
    Validate the contents of an opened PDF document.

    Args:
        pdf: An opened fitz PDF document

    Raises:
        HTTPException 422: If PDF is encrypted or has no pages
    """
    if pdf.is_encrypted:
        raise HTTPException(
            status_code=422,
            detail="PDF is encrypted/password protected. Please upload an unprotected PDF."
        )

    if len(pdf) == 0:
        raise HTTPException(
            status_code=422,
            detail="PDF has no pages."
        )
async def extract_text_from_pdf(file: UploadFile) -> list[dict]:
    """
    Extract text from a PDF file page by page.

    Args:
        file: The uploaded PDF file

    Returns:
        List of dicts with page_number and text for each page

    Raises:
        HTTPException 400: If the file is not a PDF, is empty, or exceeds size limit
        HTTPException 422: If the PDF is encrypted, has no pages, or no extractable text
        HTTPException 500: If an unexpected error occurs
    """
    try:
        contents = await file.read()
        validate_pdf_file(file, contents)

        pdf = pymupdf.open(stream=contents, filetype="pdf")

        validate_pdf_content(pdf)

        pages = []
        for page_num in range(len(pdf)):
            page = pdf[page_num]
            text = page.get_text()

            if text.strip():
                pages.append({
                    "page_number": page_num + 1,
                    "text": text.strip()
                })

        pdf.close()
        if not pages:
            raise HTTPException(
                status_code=422,
                detail="Could not extract text from PDF. It may be a scanned image-only PDF."
            )

        return pages

    except HTTPException:
        raise

    except pymupdf.FileDataError:
        raise HTTPException(
            status_code=422,
            detail="PDF file is corrupted or invalid."
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Unexpected error processing PDF: {str(e)}"
        )
