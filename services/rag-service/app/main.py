from fastapi import FastAPI

from app.api.routes.health import router as health_router
from app.api.routes.rag import router as rag_router
from app.config.settings import settings

app = FastAPI(title=settings.app_name, version=settings.app_version)
app.include_router(health_router)
app.include_router(rag_router)


@app.get("/")
def root():
    return {"application": settings.app_name, "version": settings.app_version, "status": "running"}


@app.get("/info")
def info():
    return {"service": "rag-service", "block": 4, "local_only": True}
