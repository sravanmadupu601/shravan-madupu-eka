from fastapi import (
    APIRouter,
    Depends,
    File,
    HTTPException,
    UploadFile,
)
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.database import get_db
from app.schemas.document import DocumentResponse
from app.services.document_service import DocumentService


router = APIRouter(
    prefix="/documents",
    tags=["Documents"],
)


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