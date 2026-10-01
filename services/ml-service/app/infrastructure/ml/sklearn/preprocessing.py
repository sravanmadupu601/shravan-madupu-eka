from __future__ import annotations

from typing import Any

from app.domain.exceptions import DatasetValidationError
from app.infrastructure.ml.sklearn.feature_transformer import SklearnFeatureTransformer


class SklearnPreprocessor:
    def __init__(self):
        self.feature_transformer = SklearnFeatureTransformer()

    def build(self, records: list[dict[str, Any]], target_column: str, feature_columns: list[str] | None = None):
        try:
            from sklearn.compose import ColumnTransformer
            from sklearn.impute import SimpleImputer
            from sklearn.pipeline import Pipeline
            from sklearn.preprocessing import OneHotEncoder, StandardScaler
        except Exception as exc:
            from app.domain.exceptions import MLFrameworkUnavailableError

            raise MLFrameworkUnavailableError(
                "ML_FRAMEWORK_UNAVAILABLE",
                "The local scikit-learn preprocessing runtime could not be loaded.",
            ) from exc
        if not records:
            raise DatasetValidationError("EMPTY_DATASET", "Dataset contains no rows.")
        if target_column not in records[0]:
            raise DatasetValidationError("TARGET_NOT_FOUND", "target_column is not present in the dataset.")
        try:
            selected = self.feature_transformer.select(records, target_column, feature_columns)
        except ValueError as exc:
            raise DatasetValidationError("INVALID_FEATURES", str(exc)) from exc

        numeric_indices = []
        categorical_indices = []
        for index, name in enumerate(selected):
            values = [row.get(name) for row in records if row.get(name) is not None]
            if not values:
                categorical_indices.append(index)
            elif all(isinstance(value, (int, float)) and not isinstance(value, bool) for value in values):
                numeric_indices.append(index)
            else:
                categorical_indices.append(index)

        transformers = []
        if numeric_indices:
            numeric = Pipeline([
                ("imputer", SimpleImputer(strategy="median")),
                ("scaler", StandardScaler()),
            ])
            transformers.append(("numeric", numeric, numeric_indices))
        if categorical_indices:
            categorical = Pipeline([
                ("imputer", SimpleImputer(strategy="most_frequent")),
                ("encoder", OneHotEncoder(handle_unknown="ignore")),
            ])
            transformers.append(("categorical", categorical, categorical_indices))
        transformer = ColumnTransformer(transformers=transformers, remainder="drop")
        features = [[row.get(name) for name in selected] for row in records]
        targets = [row.get(target_column) for row in records]
        if any(value is None for value in targets):
            raise DatasetValidationError("MISSING_TARGET", "Target column cannot contain missing values.")
        return transformer, features, targets, selected
