"""
Extracts plain text from an uploaded file (PDF, DOCX, or TXT), or passes
through plain pasted text unchanged.
"""
import io

from fastapi import HTTPException, UploadFile, status


def extract_text_from_pdf(file_bytes: bytes) -> str:
    from pypdf import PdfReader

    reader = PdfReader(io.BytesIO(file_bytes))
    pages_text = [page.extract_text() or "" for page in reader.pages]
    return "\n".join(pages_text).strip()


def extract_text_from_docx(file_bytes: bytes) -> str:
    import docx

    document = docx.Document(io.BytesIO(file_bytes))
    paragraphs = [p.text for p in document.paragraphs]
    return "\n".join(paragraphs).strip()


async def extract_text_from_upload(file: UploadFile) -> str:
    """
    Reads an UploadFile and returns its plain text content, based on the
    file extension. Raises a 400 error for unsupported file types.
    """
    filename = (file.filename or "").lower()
    file_bytes = await file.read()

    if filename.endswith(".pdf"):
        text = extract_text_from_pdf(file_bytes)
    elif filename.endswith(".docx"):
        text = extract_text_from_docx(file_bytes)
    elif filename.endswith(".txt"):
        text = file_bytes.decode("utf-8", errors="ignore")
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unsupported file type. Please upload a .pdf, .docx, or .txt file.",
        )

    if not text.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Could not extract any text from '{file.filename}'. The file may be empty, "
                   f"scanned/image-based, or corrupted.",
        )

    return text
