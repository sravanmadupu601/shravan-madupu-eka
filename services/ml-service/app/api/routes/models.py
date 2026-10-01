from fastapi import APIRouter, Depends, HTTPException

from app.api.dependencies import get_repositories
from app.api.schemas import ModelListResponse, ModelMetadataResponse, ModelVersionsResponse
from app.domain.exceptions import ModelNotFoundError

router = APIRouter(prefix="/ml/models", tags=["Models"])


@router.get("", response_model=ModelListResponse)
def list_models(repositories=Depends(get_repositories)):
    _, model_repository, _ = repositories
    return ModelListResponse(models=[ModelMetadataResponse(**item.__dict__) for item in model_repository.list_models()])


@router.get("/{model_id}", response_model=ModelVersionsResponse)
def list_model_versions(model_id: str, repositories=Depends(get_repositories)):
    _, model_repository, _ = repositories
    try:
        versions = model_repository.list_versions(model_id)
    except ModelNotFoundError as exc:
        raise HTTPException(status_code=404, detail=exc.message) from exc
    return ModelVersionsResponse(model_id=model_id, versions=[ModelMetadataResponse(**item.__dict__) for item in versions])


@router.get("/{model_id}/{version}", response_model=ModelMetadataResponse)
def get_model(model_id: str, version: str, repositories=Depends(get_repositories)):
    _, model_repository, _ = repositories
    try:
        metadata, _ = model_repository.load(model_id, version)
    except ModelNotFoundError as exc:
        raise HTTPException(status_code=404, detail=exc.message) from exc
    return ModelMetadataResponse(**metadata.__dict__)
