from io import BytesIO
from pathlib import Path

from docx import Document as DocxDocument
from pypdf import PdfReader


class DocumentParserService:
    """Extract text from supported document formats."""

    SUPPORTED_EXTENSIONS = {
        ".pdf",
        ".docx",
    }

    def parse(
        self,
        file_content: bytes,
        filename: str,
    ) -> str:
        extension = Path(filename).suffix.lower()

        if extension == ".pdf":
            return self._parse_pdf(file_content)

        if extension == ".docx":
            return self._parse_docx(file_content)

        raise ValueError(
            f"Unsupported file type: {extension}"
        )

    def _parse_pdf(
        self,
        file_content: bytes,
    ) -> str:
        reader = PdfReader(BytesIO(file_content))

        pages = []

        for page in reader.pages:
            text = page.extract_text() or ""

            if text.strip():
                pages.append(text.strip())

        return "\n\n".join(pages)

    def _parse_docx(
        self,
        file_content: bytes,
    ) -> str:
        document = DocxDocument(
            BytesIO(file_content)
        )

        paragraphs = []

        for paragraph in document.paragraphs:
            text = paragraph.text.strip()

            if text:
                paragraphs.append(text)

        return "\n\n".join(paragraphs)