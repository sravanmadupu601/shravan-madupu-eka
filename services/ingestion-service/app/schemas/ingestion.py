from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class IngestionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    document_id: UUID
    status: str
    chunk_count: int
    processing_version: str
    message: str
    created_at: datetime | None = None
    updated_at: datetime | None = None
