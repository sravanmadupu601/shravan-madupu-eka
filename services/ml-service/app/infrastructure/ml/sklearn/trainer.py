from __future__ import annotations

import io
import logging
from importlib.metadata import version
from typing import Any

import joblib

from app.domain.exceptions import DatasetValidationError, MLFrameworkUnavailableError
from app.domain.models import DatasetSnapshot, TrainingArtifact
from app.infrastructure.ml.sklearn.evaluator import SklearnClassificationEvaluator
from app.infrastructure.ml.sklearn.preprocessing import SklearnPreprocessor

logger = logging.getLogger(__name__)


class SklearnModelTrainer:
    SUPPORTED_ALGORITHMS = {"logistic_regression", "random_forest"}

    def __init__(self):
        self.preprocessor = SklearnPreprocessor()
        self.evaluator = SklearnClassificationEvaluator()

    def train(
        self,
        dataset: DatasetSnapshot,
        target_column: str,
        algorithm: str,
        test_size: float,
        random_state: int,
        feature_columns: list[str] | None = None,
    ) -> TrainingArtifact:
        try:
            from sklearn.ensemble import RandomForestClassifier
            from sklearn.linear_model import LogisticRegression
            from sklearn.model_selection import train_test_split
            from sklearn.pipeline import Pipeline
        except Exception as exc:
            raise MLFrameworkUnavailableError(
                "ML_FRAMEWORK_UNAVAILABLE",
                "The local scikit-learn runtime could not be loaded.",
            ) from exc
        if algorithm not in self.SUPPORTED_ALGORITHMS:
            raise DatasetValidationError("UNSUPPORTED_ALGORITHM", "Supported algorithms are logistic_regression and random_forest.")
        if not 0.05 <= test_size <= 0.5:
            raise DatasetValidationError("INVALID_TEST_SIZE", "test_size must be between 0.05 and 0.5.")

        transformer, features, targets, selected = self.preprocessor.build(
            dataset.records,
            target_column,
            feature_columns,
        )
        try:
            train_x, test_x, train_y, test_y = train_test_split(
                features,
                targets,
                test_size=test_size,
                random_state=random_state,
                stratify=targets,
            )
        except ValueError as exc:
            raise DatasetValidationError("INVALID_SPLIT", "Dataset cannot be split with the requested test_size and class distribution.") from exc

        if algorithm == "logistic_regression":
            estimator = LogisticRegression(max_iter=1000, random_state=random_state)
        else:
            estimator = RandomForestClassifier(n_estimators=120, random_state=random_state)

        pipeline = Pipeline([("preprocessing", transformer), ("model", estimator)])
        logger.info("ML training started: dataset_id=%s algorithm=%s rows=%d", dataset.metadata.dataset_id, algorithm, len(dataset.records))
        pipeline.fit(train_x, train_y)
        predicted = pipeline.predict(test_x).tolist()
        metrics = self.evaluator.evaluate(test_y, predicted)
        payload = {
            "pipeline": pipeline,
            "feature_columns": selected,
            "target_column": target_column,
            "algorithm": algorithm,
        }
        stream = io.BytesIO()
        joblib.dump(payload, stream)
        logger.info("ML evaluation completed: algorithm=%s accuracy=%.4f", algorithm, metrics["accuracy"])
        return TrainingArtifact(
            artifact=stream.getvalue(),
            metrics=metrics,
            framework_version=version("scikit-learn"),
            preprocessing={
                "numeric": "median imputation + standard scaling",
                "categorical": "most-frequent imputation + one-hot encoding",
                "selected_features": selected,
                "target_column": target_column,
                "test_size": test_size,
                "random_state": random_state,
            },
            feature_columns=selected,
        )

    @staticmethod
    def predict(artifact: bytes, features: list[dict[str, Any]]) -> list[Any]:
        try:
            from sklearn.exceptions import NotFittedError
        except Exception as exc:
            raise MLFrameworkUnavailableError(
                "ML_FRAMEWORK_UNAVAILABLE",
                "The local scikit-learn prediction runtime could not be loaded.",
            ) from exc
        if not features:
            raise DatasetValidationError("EMPTY_PREDICTION_INPUT", "At least one feature row is required.")
        try:
            payload = joblib.load(io.BytesIO(artifact))
            feature_columns = payload["feature_columns"]
            rows = []
            for row in features:
                missing = [name for name in feature_columns if name not in row]
                extra = [name for name in row if name not in feature_columns]
                if missing or extra:
                    raise DatasetValidationError(
                        "INVALID_PREDICTION_FEATURES",
                        "Prediction rows must contain exactly the trained feature columns.",
                    )
                rows.append([row[name] for name in feature_columns])
            return payload["pipeline"].predict(rows).tolist()
        except DatasetValidationError:
            raise
        except (NotFittedError, KeyError, ValueError, TypeError, OSError) as exc:
            raise DatasetValidationError("INVALID_PREDICTION", "Prediction input or stored model artifact is invalid.") from exc
