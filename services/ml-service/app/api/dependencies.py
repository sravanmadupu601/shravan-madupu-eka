from functools import lru_cache

from app.application.dataset_service import DatasetService
from app.application.prediction_service import PredictionService
from app.application.training_service import TrainingService
from app.config.settings import settings
from app.infrastructure.datasets import LocalDatasetRepository
from app.infrastructure.ml.sklearn.trainer import SklearnModelTrainer
from app.infrastructure.storage.local_model_repository import LocalModelRepository


@lru_cache(maxsize=1)
def get_repositories():
    return (
        LocalDatasetRepository(settings.dataset_path),
        LocalModelRepository(settings.model_path),
        SklearnModelTrainer(),
    )


def get_dataset_service() -> DatasetService:
    datasets, _, _ = get_repositories()
    return DatasetService(datasets)


def get_training_service() -> TrainingService:
    datasets, models, trainer = get_repositories()
    return TrainingService(datasets, trainer, models)


def get_prediction_service() -> PredictionService:
    _, models, trainer = get_repositories()
    return PredictionService(models, trainer)
