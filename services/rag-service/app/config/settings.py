from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "EKA RAG Service"
    app_version: str = "1.0.0"
    environment: str = "development"
    database_url: str = ""
    rag_port: int = 8003
    query_embedding_model_name: str = "sentence-transformers/all-MiniLM-L6-v2"
    query_embedding_dimension: int = 384
    embedding_device: str = "cpu"
    default_top_k: int = 5
    similarity_threshold: float = 0.0
    max_context_characters: int = 12000
    vector_backend: str = "memory"
    llm_provider: str = "local"
    llm_model: str = "local-deterministic"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


settings = Settings()
