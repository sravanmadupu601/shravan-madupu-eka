from pathlib import Path
from uuid import UUID


class DocumentNotFoundError(FileNotFoundError):
    pass


class SharedDocumentStorage:
    """Read-only access to Block 1's local document storage contract."""

    def __init__(self, base_path: str):
        self.base_path = Path(base_path).resolve()

    def locate(self, document_id: UUID) -> Path:
        identifier = str(document_id)
        candidates = [
            self.base_path / identifier,
            self.base_path / f"{identifier}.pdf",
            self.base_path / f"{identifier}.docx",
        ]
        for candidate in candidates:
            if candidate.is_file() and candidate.resolve().is_relative_to(self.base_path):
                return candidate.resolve()

        if self.base_path.is_dir():
            for candidate in self.base_path.rglob(f"{identifier}.*"):
                if candidate.is_file() and candidate.resolve().is_relative_to(self.base_path):
                    return candidate.resolve()
            directory = self.base_path / identifier
            if directory.is_dir() and directory.resolve().is_relative_to(self.base_path):
                for candidate in directory.iterdir():
                    if candidate.is_file() and candidate.resolve().is_relative_to(self.base_path):
                        return candidate.resolve()

        raise DocumentNotFoundError(f"Document {identifier} was not found in shared storage.")

    def read(self, document_id: UUID) -> tuple[Path, bytes]:
        path = self.locate(document_id)
        return path, path.read_bytes()
