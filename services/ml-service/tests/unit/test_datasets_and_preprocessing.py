import pytest

from app.domain.exceptions import DatasetNotFoundError, DatasetValidationError
from app.infrastructure.datasets import LocalDatasetRepository
from app.infrastructure.ml.sklearn.feature_transformer import SklearnFeatureTransformer
from app.infrastructure.ml.sklearn.preprocessing import SklearnPreprocessor


def test_builtin_iris_metadata_and_rows(tmp_path):
    repository = LocalDatasetRepository(tmp_path)
    try:
        dataset = repository.get_dataset("iris")
    except Exception as exc:
        pytest.skip(f"Local scikit-learn runtime is unavailable: {exc}")
    assert dataset.metadata.number_of_rows == 150
    assert dataset.metadata.version == "1"
    assert dataset.metadata.target_column == "target"
    assert len(dataset.metadata.feature_columns) == 4


def test_local_csv_upload_and_safe_dataset_id(tmp_path):
    repository = LocalDatasetRepository(tmp_path)
    metadata = repository.save_csv("customers.csv", b"age,segment,target\n20,A,yes\n30,B,no\n")
    assert metadata.dataset_id.startswith("csv-")
    assert metadata.number_of_rows == 2
    assert repository.get_dataset(metadata.dataset_id).records[0]["age"] == 20


def test_dataset_repository_rejects_paths_and_invalid_csv(tmp_path):
    repository = LocalDatasetRepository(tmp_path)
    with pytest.raises(DatasetNotFoundError):
        repository.get_dataset("../secret")
    with pytest.raises(DatasetValidationError):
        repository.save_csv("data.csv", b"only_one_column\nvalue\n")


def test_preprocessor_handles_numeric_and_categorical_features():
    records = [
        {"age": 20, "segment": "A", "label": "yes"},
        {"age": None, "segment": "B", "label": "no"},
        {"age": 40, "segment": "A", "label": "yes"},
        {"age": 50, "segment": "B", "label": "no"},
    ]
    try:
        transformer, features, target, columns = SklearnPreprocessor().build(records, "label")
    except Exception as exc:
        from app.domain.exceptions import MLFrameworkUnavailableError

        if isinstance(exc, MLFrameworkUnavailableError):
            pytest.skip(f"Local scikit-learn runtime is unavailable: {exc.message}")
        raise
    transformed = transformer.fit_transform(features)
    assert columns == ["age", "segment"]
    assert transformed.shape[0] == 4
    assert target == ["yes", "no", "yes", "no"]


def test_feature_selection_is_reproducible_and_rejects_missing_columns():
    selector = SklearnFeatureTransformer()
    records = [{"x": 1, "y": 2, "target": 0}]
    assert selector.select(records, "target", ["y", "x"]) == ["y", "x"]
    with pytest.raises(ValueError):
        selector.select(records, "target", ["unknown"])
