from fastapi import (
    APIRouter,
    Depends,
    File,
    HTTPException,
    UploadFile,
)
from uuid import UUID
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.database import get_db
from app.schemas.document import DocumentListResponse, DocumentResponse
from app.services.document_service import DocumentService


router = APIRouter(
    prefix="/documents",
    tags=["Documents"],
)


@router.get("", response_model=DocumentListResponse)
def list_documents(
    limit: int = 50,
    offset: int = 0,
    db: Session = Depends(get_db),
):
    if not 1 <= limit <= 100 or offset < 0:
        raise HTTPException(status_code=422, detail="limit must be 1..100 and offset must be non-negative.")
    documents, total = DocumentService(db).list_documents(limit, offset)
    return DocumentListResponse(documents=documents, total=total, limit=limit, offset=offset)


@router.get("/{document_id}", response_model=DocumentResponse)
def get_document(document_id: UUID, db: Session = Depends(get_db)):
    document = DocumentService(db).get_document(document_id)
    if document is None:
        raise HTTPException(status_code=404, detail="Document not found.")
    return document


ALLOWED_CONTENT_TYPES = {
    "application/pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
}


@router.post(
    "/upload",
    response_model=DocumentResponse,
)
async def upload_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="Filename is required.",
        )

    if file.content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(
            status_code=415,
            detail="Only PDF and DOCX files are supported.",
        )

    file_content = await file.read()

    max_file_size = settings.max_file_size_mb * 1024 * 1024

    if len(file_content) > max_file_size:
        raise HTTPException(
            status_code=413,
            detail=(
                f"File size exceeds the maximum allowed size of "
                f"{settings.max_file_size_mb} MB."
            ),
        )

    service = DocumentService(db)

    try:
        return service.ingest_document(
            filename=file.filename,
            content_type=file.content_type,
            file_content=file_content,
        )

    except ValueError as exc:
        message = str(exc)

        if "already exists" in message:
            raise HTTPException(
                status_code=409,
                detail=message,
            )

        raise HTTPException(
            status_code=400,
            detail=message,
        )

    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Document ingestion failed.",
        )