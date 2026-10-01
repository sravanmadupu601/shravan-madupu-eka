from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app.api.dependencies import get_prediction_service
from app.api.schemas import PredictionRequest
from app.application.prediction_service import PredictionService
from app.domain.exceptions import DatasetValidationError, ModelNotFoundError

router = APIRouter(prefix="/ml/predict", tags=["Predictions"])


class PredictionResponse(BaseModel):
    model_id: str
    version: str
    algorithm: str
    predictions: list[Any]


@router.post("", response_model=PredictionResponse)
def predict(request: PredictionRequest, service: PredictionService = Depends(get_prediction_service)):
    try:
        result = service.predict(request.model_id, request.version, request.features)
    except ModelNotFoundError as exc:
        raise HTTPException(status_code=404, detail=exc.message) from exc
    except DatasetValidationError as exc:
        raise HTTPException(status_code=422, detail={"code": exc.code, "message": exc.message}) from exc
    return PredictionResponse(**result)
