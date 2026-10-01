from importlib import import_module
import os

from fastapi import APIRouter, HTTPException

from app.config.settings import settings

router = APIRouter(tags=["Health"])


@router.get("/health")
def health():
    return {"status": "healthy"}


@router.get("/ready")
def ready():
    unavailable = []
    for name in ("numpy", "sklearn", "joblib"):
        try:
            import_module(name)
        except Exception:
            unavailable.append(name)
    paths = {"datasets": settings.dataset_path, "models": settings.model_path}
    inaccessible = [name for name, path in paths.items() if not path.is_dir() or not os.access(path, os.R_OK | os.W_OK)]
    if unavailable or inaccessible:
        raise HTTPException(
            status_code=503,
            detail={"status": "not_ready", "unavailable_dependencies": unavailable, "inaccessible_paths": inaccessible},
        )
    return {"status": "ready", "dataset_storage": "available", "model_registry": "available"}


@router.get("/info")
def info():
    return {
        "service": settings.app_name,
        "version": settings.app_version,
        "port": settings.ml_service_port,
        "frameworks": {"scikit_learn": "implemented", "pytorch": "extension_point", "tensorflow": "extension_point"},
        "algorithms": ["logistic_regression", "random_forest"],
    }
