from dataclasses import dataclass
from datetime import datetime
from typing import Any


@dataclass(frozen=True)
class DatasetMetadata:
    dataset_id: str
    name: str
    version: str
    format: str
    number_of_rows: int
    feature_columns: list[str]
    target_column: str | None
    created_at: datetime

    @property
    def number_of_features(self) -> int:
        return len(self.feature_columns)


@dataclass(frozen=True)
class DatasetSnapshot:
    metadata: DatasetMetadata
    records: list[dict[str, Any]]


@dataclass(frozen=True)
class ModelMetadata:
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


@dataclass(frozen=True)
class TrainingArtifact:
    artifact: bytes
    metrics: dict[str, float]
    framework_version: str
    preprocessing: dict[str, Any]
    feature_columns: list[str]
