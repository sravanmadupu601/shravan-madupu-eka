from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "EKA Embedding Service"
    app_version: str = "1.0.0"
    environment: str = "development"
    database_url: str
    embedding_model_name: str = "sentence-transformers/all-MiniLM-L6-v2"
    embedding_model_version: str = "1"
    embedding_dimension: int = 384
    vector_dimension: int | None = None
    vector_distance_metric: str = "cosine"

    @property
    def configured_vector_dimension(self) -> int:
        dimension = self.vector_dimension or self.embedding_dimension
        if dimension != self.embedding_dimension:
            raise ValueError("VECTOR_DIMENSION must match EMBEDDING_DIMENSION.")
        return dimension

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


settings = Settings()
