from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "EKA Ingestion Service"
    app_version: str = "1.0.0"
    environment: str = "development"
    database_url: str = "postgresql+psycopg://eka:eka@localhost:5432/eka"
    document_storage_path: str = "../document-service/storage/documents"
    chunk_size: int = 1000
    chunk_overlap: int = 200
    chunking_strategy: str = "fixed"
    semantic_model_name: str = "sentence-transformers/all-MiniLM-L6-v2"
    semantic_similarity_threshold: float = 0.70
    semantic_min_sentences: int = 1
    semantic_max_sentences: int = 20
    embedding_device: str = "cpu"
    processing_version: str = "1.0"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


settings = Settings()
