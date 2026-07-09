import pytest

from app.utils.pdf_parser import extract_text_from_pdf, PDFParseError


class TestPDFParser:
    def test_extract_text_from_valid_pdf(self):
        # Simple PDF with minimal structure
        pdf_bytes = b"""%PDF-1.4
1 0 obj
<< /Type /Catalog /Pages 2 0 R >>
endobj
2 0 obj
<< /Type /Pages /Kids [3 0 R] /Count 1 >>
endobj
3 0 obj
<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Contents 4 0 R /Resources << /Font << /F1 << /Type /Font /Subtype /Type1 /BaseFont /Helvetica >> >> >> >>
endobj
4 0 obj
<< /Length 44 >>
stream
BT
/F1 12 Tf
100 700 Td
(Hello World) Tj
ET
endstream
endobj
xref
0 5
0000000000 65535 f
0000000009 00000 n
0000000058 00000 n
0000000115 00000 n
0000000273 00000 n
trailer
<< /Size 5 /Root 1 0 R >>
startxref
366
%%EOF
"""
        text = extract_text_from_pdf(pdf_bytes)
        assert isinstance(text, str)

    def test_empty_pdf_raises_error(self):
        empty_pdf = b"%PDF-1.4\n"
        with pytest.raises(PDFParseError):
            extract_text_from_pdf(empty_pdf)

    def test_invalid_pdf_raises_error(self):
        invalid_pdf = b"This is not a PDF"
        with pytest.raises(PDFParseError):
            extract_text_from_pdf(invalid_pdf)

    def test_corrupted_pdf_raises_error(self):
        corrupted_pdf = b"%PDF-1.4\n%corrupted data here"
        with pytest.raises(PDFParseError):
            extract_text_from_pdf(corrupted_pdf)
