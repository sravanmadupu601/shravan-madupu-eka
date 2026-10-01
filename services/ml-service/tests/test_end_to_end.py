import pytest

from app.application.dataset_service import DatasetService
from app.application.prediction_service import PredictionService
from app.application.training_service import TrainingService
from app.infrastructure.datasets import LocalDatasetRepository
from app.infrastructure.ml.sklearn.trainer import SklearnModelTrainer
from app.infrastructure.storage.local_model_repository import LocalModelRepository


def test_iris_train_persist_load_predict_lifecycle(tmp_path):
    datasets = LocalDatasetRepository(tmp_path / "datasets")
    registry = LocalModelRepository(tmp_path / "models")
    trainer = SklearnModelTrainer()
    try:
        metadata = TrainingService(datasets, trainer, registry).train(
            dataset_id="iris",
            target_column="target",
            algorithm="logistic_regression",
            test_size=0.2,
            random_state=42,
        )
    except Exception as exc:
        from app.domain.exceptions import MLFrameworkUnavailableError

        if isinstance(exc, MLFrameworkUnavailableError):
            pytest.skip(f"Local scikit-learn runtime is unavailable: {exc.message}")
        raise

    prediction = PredictionService(registry, trainer).predict(
        metadata.model_id,
        metadata.version,
        [{"sepal length (cm)": 5.1, "sepal width (cm)": 3.5, "petal length (cm)": 1.4, "petal width (cm)": 0.2}],
    )

    assert metadata.version == "v1"
    assert prediction["version"] == "v1"
    assert prediction["predictions"] == ["setosa"]
