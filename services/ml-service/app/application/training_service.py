import logging
from time import perf_counter

from app.domain.interfaces import DatasetRepository, ModelRepository, ModelTrainer
from app.domain.models import ModelMetadata

logger = logging.getLogger(__name__)


class TrainingService:
    def __init__(self, datasets: DatasetRepository, trainer: ModelTrainer, models: ModelRepository):
        self.datasets = datasets
        self.trainer = trainer
        self.models = models

    def train(
        self,
        dataset_id: str,
        target_column: str,
        algorithm: str,
        test_size: float,
        random_state: int,
        model_name: str | None = None,
        feature_columns: list[str] | None = None,
    ) -> ModelMetadata:
        started = perf_counter()
        dataset = self.datasets.get_dataset(dataset_id)
        artifact = self.trainer.train(
            dataset,
            target_column,
            algorithm,
            test_size,
            random_state,
            feature_columns,
        )
        name = model_name or f"{dataset_id}-classifier"
        metadata = self.models.save(name, dataset, target_column, algorithm, artifact.artifact, artifact)
        logger.info(
            "ML training completed: model_id=%s version=%s algorithm=%s duration_ms=%.2f",
            metadata.model_id,
            metadata.version,
            metadata.algorithm,
            (perf_counter() - started) * 1000,
        )
        return metadata
