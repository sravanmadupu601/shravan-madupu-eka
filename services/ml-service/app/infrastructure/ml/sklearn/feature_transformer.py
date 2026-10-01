from typing import Any


class SklearnFeatureTransformer:
    """Deterministic feature selection shared by training and inference."""

    def select(
        self,
        records: list[dict[str, Any]],
        target_column: str,
        requested_columns: list[str] | None = None,
    ) -> list[str]:
        available = list(records[0]) if records else []
        selected = requested_columns or [column for column in available if column != target_column]
        if not selected or target_column in selected:
            raise ValueError("Select one or more feature columns excluding the target.")
        if len(selected) != len(set(selected)) or any(column not in available for column in selected):
            raise ValueError("Feature columns must be unique columns in the dataset.")
        return selected
