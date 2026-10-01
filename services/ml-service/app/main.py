from fastapi import FastAPI

from app.api.routes.datasets import router as datasets_router
from app.api.routes.health import router as health_router
from app.api.routes.models import router as models_router
from app.api.routes.predictions import router as predictions_router
from app.api.routes.training import router as training_router
from app.config.settings import settings

app = FastAPI(title=settings.app_name, version=settings.app_version)
app.include_router(health_router)
app.include_router(datasets_router)
app.include_router(training_router)
app.include_router(models_router)
app.include_router(predictions_router)


@app.get("/")
def root():
    return {"application": settings.app_name, "version": settings.app_version, "status": "running"}
