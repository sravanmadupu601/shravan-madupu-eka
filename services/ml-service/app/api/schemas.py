from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, Field, field_validator

from app.config.settings import settings


class DatasetMetadataResponse(BaseModel):
    dataset_id: str
    name: str
    version: str
    format: str
    number_of_rows: int
    number_of_features: int
    feature_columns: list[str]
    target_column: str | None
    created_at: datetime


class DatasetListResponse(BaseModel):
    datasets: list[DatasetMetadataResponse]


class DatasetDetailResponse(DatasetMetadataResponse):
    preview: list[dict[str, Any]]


class TrainingRequest(BaseModel):
    dataset_id: str = Field(min_length=1, max_length=100)
    target_column: str = Field(min_length=1, max_length=128)
    algorithm: Literal["logistic_regression", "random_forest"] = "logistic_regression"
    test_size: float = Field(default=settings.default_test_size, ge=0.05, le=0.5)
    random_state: int = settings.default_random_state
    model_name: str | None = Field(default=None, pattern=r"^[a-z0-9][a-z0-9-]{0,79}$")
    feature_columns: list[str] | None = None

    @field_validator("feature_columns")
    @classmethod
    def feature_columns_must_be_unique(cls, value: list[str] | None) -> list[str] | None:
        if value is not None and (not value or len(value) != len(set(value))):
            raise ValueError("feature_columns must be non-empty and unique when provided.")
        return value


class ModelMetadataResponse(BaseModel):
    model_id: str
    model_name: str
    version: str
    framework: str
    algorithm: str
    dataset_id: str
    dataset_version: str
    target_column: str
    feature_columns: list[str]
    metrics: dict[str, float]
    preprocessing: dict[str, Any]
    framework_version: str
    model_path: str
    created_at: datetime
    status: str


class ModelListResponse(BaseModel):
    models: list[ModelMetadataResponse]


class ModelVersionsResponse(BaseModel):
    model_id: str
    versions: list[ModelMetadataResponse]


class PredictionRequest(BaseModel):
    model_id: str = Field(min_length=1, max_length=80)
    version: str = Field(pattern=r"^v[1-9][0-9]*$")
    features: list[dict[str, Any]] = Field(min_length=1, max_length=1000)
