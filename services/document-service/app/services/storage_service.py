import uuid
from pathlib import Path


class LocalStorageService:
    """Local filesystem storage abstraction.

    This can later be replaced with a cloud storage implementation
    without changing the document business logic.
    """

    def __init__(self, base_path: str = "storage/documents"):
        self.base_path = Path(base_path)
        self.base_path.mkdir(
            parents=True,
            exist_ok=True,
        )

    def save(
        self,
        file_content: bytes,
        filename: str,
    ) -> str:
        document_id = uuid.uuid4()

        extension = Path(filename).suffix.lower()

        stored_filename = f"{document_id}{extension}"

        file_path = self.base_path / stored_filename

        file_path.write_bytes(file_content)

        return str(file_path)

    def read(self, storage_path: str) -> bytes:
        return Path(storage_path).read_bytes()

    def delete(self, storage_path: str) -> None:
        path = Path(storage_path)

        if path.exists():
            path.unlink()