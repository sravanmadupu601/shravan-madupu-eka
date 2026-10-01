from typing import Any


class UnavailableDocumentClient:
    """Local stub because Block 1 currently exposes upload and health only."""

    def __init__(self, service_url: str):
        self.service_url = service_url

    def get_document(self, document_id: str) -> dict[str, Any] | None:
        return None
