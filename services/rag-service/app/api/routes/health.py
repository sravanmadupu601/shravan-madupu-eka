from fastapi import APIRouter

router = APIRouter(prefix="/health", tags=["Health"])


@router.get("")
def health():
    return {"status": "healthy"}


@router.get("/live")
def live():
    return {"status": "live"}


@router.get("/ready")
def ready():
    return {"status": "ready", "vector_backend": "configured"}


@router.get("/info")
def info():
    return {"service": "rag-service", "block": 4, "local_only": True}
