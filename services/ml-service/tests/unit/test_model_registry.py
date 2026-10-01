import pytest

from app.application.dataset_service import DatasetService
from app.application.training_service import TrainingService
from app.domain.exceptions import ModelNotFoundError
from app.infrastructure.datasets import LocalDatasetRepository
from app.infrastructure.ml.sklearn.trainer import SklearnModelTrainer
from app.infrastructure.storage.local_model_repository import LocalModelRepository


def test_training_persists_incrementing_versions_and_metrics(tmp_path):
    datasets = LocalDatasetRepository(tmp_path / "datasets")
    models = LocalModelRepository(tmp_path / "models")
    trainer = SklearnModelTrainer()
    service = TrainingService(datasets, trainer, models)
    try:
        first = service.train("iris", "target", "logistic_regression", 0.2, 42, "iris-demo")
    except Exception as exc:
        from app.domain.exceptions import MLFrameworkUnavailableError

        if isinstance(exc, MLFrameworkUnavailableError):
            pytest.skip(f"Local scikit-learn runtime is unavailable: {exc.message}")
        raise
    second = service.train("iris", "target", "logistic_regression", 0.2, 42, "iris-demo")

    assert first.version == "v1"
    assert second.version == "v2"
    assert set(first.metrics) == {"accuracy", "precision", "recall", "f1"}
    assert 0 <= first.metrics["accuracy"] <= 1
    assert first.framework == "scikit-learn"
    metadata, artifact = models.load(first.model_id, first.version)
    assert metadata.version == "v1"
    assert artifact
    assert [item.version for item in models.list_versions(first.model_id)] == ["v1", "v2"]


def test_registry_rejects_unknown_or_unsafe_models(tmp_path):
    repository = LocalModelRepository(tmp_path)
    with pytest.raises(ModelNotFoundError):
        repository.load("../outside", "v1")
    with pytest.raises(ModelNotFoundError):
        repository.load("missing", "v1")
