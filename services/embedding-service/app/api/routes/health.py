from fastapi import APIRouter, Depends
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
    return {"status": "ready", "database": "connected", "result": 1}


@router.get("/db")
def database_health(db: Session = Depends(get_db)):
    db.execute(text("SELECT 1"))
    return {"status": "healthy", "database": "connected", "result": 1}
