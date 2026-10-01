from fastapi import FastAPI

from app.api.routes.embedding import router as embedding_router
from app.api.routes.health import router as health_router
from app.config.settings import settings

app = FastAPI(title=settings.app_name, version=settings.app_version)
app.include_router(health_router)
app.include_router(embedding_router)


@app.get("/")
def root():
    return {"application": settings.app_name, "version": settings.app_version, "status": "running"}
