from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.infrastructure.database.session import get_db

router = APIRouter(prefix="/health", tags=["Health"])


@router.get("")
def health():
    return {"status": "healthy"}


@router.get("/live")
def live():
    return {"status": "live"}


@router.get("/ready")
def ready(db: Session = Depends(get_db)):
    db.execute(text("SELECT 1"))
    if db.bind is None or db.bind.dialect.name != "postgresql":
        return {"status": "ready", "database": "connected", "pgvector": "not_checked", "result": 1}
    extension = db.execute(
        text("SELECT 1 FROM pg_extension WHERE extname = 'vector'")
    ).scalar_one_or_none()
    if extension != 1:
        raise HTTPException(status_code=503, detail="pgvector extension is unavailable.")
    return {"status": "ready", "database": "connected", "pgvector": "available", "result": 1}


@router.get("/db")
def database_health(db: Session = Depends(get_db)):
    db.execute(text("SELECT 1"))
    return {"status": "healthy", "database": "connected", "result": 1}
