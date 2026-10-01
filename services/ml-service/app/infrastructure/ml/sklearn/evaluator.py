from typing import Any


class SklearnClassificationEvaluator:
    def evaluate(self, actual: list[Any], predicted: list[Any]) -> dict[str, float]:
        try:
            from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score
        except Exception as exc:
            from app.domain.exceptions import MLFrameworkUnavailableError

            raise MLFrameworkUnavailableError(
                "ML_FRAMEWORK_UNAVAILABLE",
                "The local scikit-learn evaluation runtime could not be loaded.",
            ) from exc

        return {
            "accuracy": float(accuracy_score(actual, predicted)),
            "precision": float(precision_score(actual, predicted, average="weighted", zero_division=0)),
            "recall": float(recall_score(actual, predicted, average="weighted", zero_division=0)),
            "f1": float(f1_score(actual, predicted, average="weighted", zero_division=0)),
        }
