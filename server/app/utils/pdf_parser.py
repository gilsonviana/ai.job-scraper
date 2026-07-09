from pypdf import PdfReader
from io import BytesIO


class PDFParseError(Exception):
    """Raised when PDF parsing fails."""

    pass


def extract_text_from_pdf(pdf_bytes: bytes) -> str:
    """
    Extract text from a PDF file.

    Args:
        pdf_bytes: Raw PDF file bytes

    Returns:
        Extracted text content

    Raises:
        PDFParseError: If the PDF is corrupted, password-protected, or unsupported
    """
    try:
        pdf_file = BytesIO(pdf_bytes)
        reader = PdfReader(pdf_file)

        if reader.is_encrypted:
            raise PDFParseError("PDF is password-protected")

        text = ""
        for page in reader.pages:
            text += page.extract_text() or ""

        if not text.strip():
            raise PDFParseError("No text could be extracted from PDF")

        return text
    except PDFParseError:
        raise
    except Exception as e:
        raise PDFParseError(f"Corrupted or unsupported PDF format: {str(e)}")
