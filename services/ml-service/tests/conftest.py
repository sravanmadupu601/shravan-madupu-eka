import pytest
from fastapi.testclient import TestClient

from app.api.dependencies import get_dataset_service, get_prediction_service, get_repositories, get_training_service
from app.application.dataset_service import DatasetService
from app.application.prediction_service import PredictionService
from app.application.training_service import TrainingService
from app.infrastructure.datasets import LocalDatasetRepository
from app.infrastructure.ml.sklearn.trainer import SklearnModelTrainer
from app.infrastructure.storage.local_model_repository import LocalModelRepository
from app.main import app


@pytest.fixture
def repositories(tmp_path):
    datasets_path = tmp_path / "datasets"
    models_path = tmp_path / "models"
    datasets_path.mkdir()
    models_path.mkdir()
    return LocalDatasetRepository(datasets_path), LocalModelRepository(models_path), SklearnModelTrainer()


@pytest.fixture
def client(repositories):
    datasets, models, trainer = repositories
    app.dependency_overrides[get_repositories] = lambda: repositories
    app.dependency_overrides[get_dataset_service] = lambda: DatasetService(datasets)
    app.dependency_overrides[get_training_service] = lambda: TrainingService(datasets, trainer, models)
    app.dependency_overrides[get_prediction_service] = lambda: PredictionService(models, trainer)
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
