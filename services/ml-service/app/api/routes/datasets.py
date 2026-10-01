from fastapi import APIRouter, Depends, File, HTTPException, UploadFile

from app.api.dependencies import get_dataset_service
from app.api.schemas import DatasetDetailResponse, DatasetListResponse, DatasetMetadataResponse
from app.application.dataset_service import DatasetService
from app.config.settings import settings
from app.domain.exceptions import DatasetNotFoundError, DatasetValidationError, MLFrameworkUnavailableError

router = APIRouter(prefix="/ml/datasets", tags=["Datasets"])


def _metadata(metadata):
    return DatasetMetadataResponse(**metadata.__dict__, number_of_features=metadata.number_of_features)


@router.get("", response_model=DatasetListResponse)
def list_datasets(service: DatasetService = Depends(get_dataset_service)):
    return DatasetListResponse(datasets=[_metadata(item) for item in service.list_datasets()])


@router.get("/{dataset_id}", response_model=DatasetDetailResponse)
def get_dataset(dataset_id: str, service: DatasetService = Depends(get_dataset_service)):
    try:
        snapshot = service.get_dataset(dataset_id)
    except DatasetNotFoundError as exc:
        raise HTTPException(status_code=404, detail=exc.message) from exc
    except MLFrameworkUnavailableError as exc:
        raise HTTPException(status_code=503, detail={"code": exc.code, "message": exc.message}) from exc
    metadata = _metadata(snapshot.metadata).model_dump()
    return DatasetDetailResponse(**metadata, preview=snapshot.records[:10])


@router.post("", response_model=DatasetMetadataResponse, status_code=201)
async def upload_dataset(
    file: UploadFile = File(...),
    service: DatasetService = Depends(get_dataset_service),
):
    content = await file.read(settings.max_upload_bytes + 1)
    if len(content) > settings.max_upload_bytes:
        raise HTTPException(status_code=413, detail="Dataset exceeds the configured upload limit.")
    try:
        return _metadata(service.upload_csv(file.filename or "dataset.csv", content))
    except DatasetValidationError as exc:
        raise HTTPException(status_code=422, detail={"code": exc.code, "message": exc.message}) from exc
