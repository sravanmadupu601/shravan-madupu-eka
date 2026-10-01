from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app.api.dependencies import get_training_service
from app.api.schemas import ModelMetadataResponse, TrainingRequest
from app.application.training_service import TrainingService
from app.domain.exceptions import DatasetNotFoundError, DatasetValidationError, MLFrameworkUnavailableError
from app.domain.models import ModelMetadata

router = APIRouter(prefix="/ml/train", tags=["Training"])


class TrainingResponse(BaseModel):
    model: ModelMetadataResponse
    status: str


def _metadata(metadata: ModelMetadata) -> ModelMetadataResponse:
    return ModelMetadataResponse(**metadata.__dict__)


@router.post("", response_model=TrainingResponse, status_code=201)
def train_model(
    request: TrainingRequest,
    service: TrainingService = Depends(get_training_service),
):
    try:
        metadata = service.train(
            dataset_id=request.dataset_id,
            target_column=request.target_column,
            algorithm=request.algorithm,
            test_size=request.test_size,
            random_state=request.random_state,
            model_name=request.model_name,
            feature_columns=request.feature_columns,
        )
    except DatasetNotFoundError as exc:
        raise HTTPException(status_code=404, detail=exc.message) from exc
    except DatasetValidationError as exc:
        raise HTTPException(status_code=422, detail={"code": exc.code, "message": exc.message}) from exc
    except MLFrameworkUnavailableError as exc:
        raise HTTPException(status_code=503, detail={"code": exc.code, "message": exc.message}) from exc
    return TrainingResponse(model=_metadata(metadata), status="COMPLETED")
