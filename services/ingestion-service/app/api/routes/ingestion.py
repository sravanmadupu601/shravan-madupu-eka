from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.schemas.ingestion import IngestionResponse
from app.services.ingestion_service import IngestionService
from app.services.parser_service import UnsupportedDocumentError
from app.services.storage_service import DocumentNotFoundError

router = APIRouter(prefix="/ingestion", tags=["Ingestion"])


@router.post("/{document_id}", response_model=IngestionResponse)
def ingest_document(document_id: UUID, db: Session = Depends(get_db)):
    service = IngestionService(db)
    try:
        run = service.ingest(document_id)
    except DocumentNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except UnsupportedDocumentError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail="Document ingestion failed.") from exc

    message = "Document was already ingested." if run.status == "COMPLETED" else "Document ingested successfully."
    return IngestionResponse(
        document_id=document_id,
        status=run.status,
        chunk_count=run.chunk_count,
        processing_version=run.processing_version,
        message=message,
        created_at=run.created_at,
        updated_at=run.updated_at,
    )
