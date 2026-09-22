class EmbeddingError(Exception):
    """Base error for embedding domain/application failures."""


class EmptyTextError(EmbeddingError, ValueError):
    pass


class EmbeddingDimensionError(EmbeddingError, ValueError):
    pass
