from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.db.database import get_db


router = APIRouter(
    prefix="/health",
    tags=["Health"],
)


@router.get("/live")
def liveness():
    """
    Liveness probe.

    Confirms that the application process is running.
    """
    return {
        "status": "alive",
    }


@router.get("/ready")
def readiness(db: Session = Depends(get_db)):
    """
    Readiness probe.

    Confirms that the application can communicate
    with its database.
    """
    try:
        result = db.execute(text("SELECT 1"))
        value = result.scalar_one()

        return {
            "status": "ready",
            "database": "connected",
            "result": value,
        }

    except Exception:
        raise HTTPException(
            status_code=503,
            detail="Database is unavailable.",
        )


@router.get("")
def health():
    """
    Backward-compatible health endpoint.
    """
    return {
        "status": "healthy",
    }


@router.get("/db")
def database_health(db: Session = Depends(get_db)):
    """
    Backward-compatible database health endpoint.
    """
    result = db.execute(text("SELECT 1"))
    value = result.scalar_one()

    return {
        "status": "healthy",
        "database": "connected",
        "result": value,
    }