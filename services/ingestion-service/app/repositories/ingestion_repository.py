from uuid import UUID

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.db.models.ingestion import IngestionChunk, IngestionRun


class IngestionRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_run(self, document_id: str, processing_version: str) -> IngestionRun | None:
        statement = select(IngestionRun).where(
            IngestionRun.document_id == document_id,
            IngestionRun.processing_version == processing_version,
        )
        return self.db.execute(statement).scalar_one_or_none()

    def create_run(self, run: IngestionRun) -> IngestionRun:
        self.db.add(run)
        self.db.flush()
        return run

    def delete_chunks(self, run_id: UUID) -> None:
        self.db.execute(delete(IngestionChunk).where(IngestionChunk.ingestion_run_id == run_id))

    def create_chunks(self, chunks: list[IngestionChunk]) -> None:
        self.db.add_all(chunks)
