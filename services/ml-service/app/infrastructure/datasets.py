from __future__ import annotations

import csv
import io
import re
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from app.domain.exceptions import DatasetNotFoundError, DatasetValidationError
from app.domain.models import DatasetMetadata, DatasetSnapshot


class LocalDatasetRepository:
    def __init__(self, storage_path: Path):
        self.storage_path = storage_path.resolve()
        self.storage_path.mkdir(parents=True, exist_ok=True)

    def list_datasets(self) -> list[DatasetMetadata]:
        iris = self._iris_metadata()
        datasets = [iris]
        for path in sorted(self.storage_path.glob("*.csv")):
            try:
                datasets.append(self._load_csv(path).metadata)
            except DatasetValidationError:
                continue
        return datasets

    def get_dataset(self, dataset_id: str) -> DatasetSnapshot:
        if dataset_id == "iris":
            return self._iris_snapshot()
        if not re.fullmatch(r"csv-[0-9a-f]{32}", dataset_id):
            raise DatasetNotFoundError("DATASET_NOT_FOUND", "Dataset was not found.")
        path = (self.storage_path / f"{dataset_id}.csv").resolve()
        if path.parent != self.storage_path or not path.is_file():
            raise DatasetNotFoundError("DATASET_NOT_FOUND", "Dataset was not found.")
        return self._load_csv(path)

    def save_csv(self, filename: str, content: bytes) -> DatasetMetadata:
        if not filename.lower().endswith(".csv"):
            raise DatasetValidationError("INVALID_DATASET_FORMAT", "Only CSV datasets are supported.")
        if not content:
            raise DatasetValidationError("EMPTY_DATASET", "Dataset file is empty.")
        try:
            decoded = content.decode("utf-8-sig")
            rows = list(csv.DictReader(io.StringIO(decoded)))
        except (UnicodeDecodeError, csv.Error) as exc:
            raise DatasetValidationError("INVALID_CSV", "Dataset must be a valid UTF-8 CSV file.") from exc
        if not rows or not rows[0] or len(rows[0]) < 2:
            raise DatasetValidationError("INVALID_DATASET", "CSV must contain a header and at least one row and two columns.")
        dataset_id = f"csv-{uuid.uuid4().hex}"
        path = self.storage_path / f"{dataset_id}.csv"
        path.write_bytes(content)
        return self._load_csv(path).metadata

    @staticmethod
    def _iris_metadata() -> DatasetMetadata:
        return DatasetMetadata(
            dataset_id="iris",
            name="Iris flower classification",
            version="1",
            format="builtin",
            number_of_rows=150,
            feature_columns=[
                "sepal length (cm)",
                "sepal width (cm)",
                "petal length (cm)",
                "petal width (cm)",
            ],
            target_column="target",
            created_at=datetime(2026, 1, 1, tzinfo=timezone.utc),
        )

    @classmethod
    def _iris_snapshot(cls) -> DatasetSnapshot:
        try:
            from sklearn.datasets import load_iris
        except Exception as exc:
            from app.domain.exceptions import MLFrameworkUnavailableError

            raise MLFrameworkUnavailableError(
                "ML_FRAMEWORK_UNAVAILABLE",
                "The local scikit-learn runtime could not be loaded.",
            ) from exc
        iris = load_iris()
        feature_names = list(iris.feature_names)
        records = [
            {
                **{name: float(value) for name, value in zip(feature_names, row, strict=True)},
                "target": str(iris.target_names[int(target)]),
            }
            for row, target in zip(iris.data.tolist(), iris.target.tolist(), strict=True)
        ]
        metadata = cls._iris_metadata()
        return DatasetSnapshot(metadata, records)

    @staticmethod
    def _coerce(value: str) -> Any:
        value = value.strip()
        if value == "":
            return None
        if value.lower() in {"true", "false"}:
            return value.lower() == "true"
        try:
            number = float(value)
        except ValueError:
            return value
        return int(number) if number.is_integer() else number

    @classmethod
    def _load_csv(cls, path: Path) -> DatasetSnapshot:
        try:
            with path.open("r", newline="", encoding="utf-8-sig") as stream:
                reader = csv.DictReader(stream)
                if not reader.fieldnames or len(reader.fieldnames) < 2:
                    raise DatasetValidationError("INVALID_DATASET", "CSV needs at least two columns.")
                rows = [{key: cls._coerce(value) for key, value in row.items()} for row in reader]
        except (OSError, csv.Error, UnicodeDecodeError) as exc:
            raise DatasetValidationError("INVALID_CSV", "Dataset CSV could not be parsed.") from exc
        if not rows:
            raise DatasetValidationError("EMPTY_DATASET", "CSV dataset has no data rows.")
        dataset_id = path.stem
        metadata = DatasetMetadata(
            dataset_id=dataset_id,
            name=path.name,
            version="1",
            format="csv",
            number_of_rows=len(rows),
            feature_columns=list(reader.fieldnames),
            target_column=None,
            created_at=datetime.fromtimestamp(path.stat().st_mtime, tz=timezone.utc),
        )
        return DatasetSnapshot(metadata, rows)
