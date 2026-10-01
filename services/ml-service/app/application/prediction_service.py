import logging
from time import perf_counter
from typing import Any

from app.domain.interfaces import ModelRepository, ModelTrainer

logger = logging.getLogger(__name__)


class PredictionService:
    def __init__(self, models: ModelRepository, trainer: ModelTrainer):
        self.models = models
        self.trainer = trainer

    def predict(self, model_id: str, version: str, features: list[dict[str, Any]]) -> dict[str, Any]:
        started = perf_counter()
        metadata, artifact = self.models.load(model_id, version)
        predictions = self.trainer.predict(artifact, features)
        logger.info(
            "ML prediction completed: model_id=%s version=%s rows=%d duration_ms=%.2f",
            model_id,
            version,
            len(features),
            (perf_counter() - started) * 1000,
        )
        return {
            "model_id": metadata.model_id,
            "version": metadata.version,
            "algorithm": metadata.algorithm,
            "predictions": predictions,
        }
