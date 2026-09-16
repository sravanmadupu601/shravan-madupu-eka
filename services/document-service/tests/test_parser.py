from io import BytesIO

from pypdf import PdfWriter

from app.services.parser_service import DocumentParserService


def create_test_pdf() -> bytes:
    buffer = BytesIO()

    writer = PdfWriter()
    writer.add_blank_page(
        width=300,
        height=300,
    )

    writer.write(buffer)

    return buffer.getvalue()


def test_parser_rejects_unsupported_file():
    parser = DocumentParserService()

    try:
        parser.parse(
            file_content=b"test",
            filename="test.txt",
        )
        assert False
    except ValueError as exc:
        assert "Unsupported file type" in str(exc)


def test_parser_accepts_pdf():
    parser = DocumentParserService()

    pdf_content = create_test_pdf()

    result = parser.parse(
        file_content=pdf_content,
        filename="test.pdf",
    )

    assert isinstance(result, str)