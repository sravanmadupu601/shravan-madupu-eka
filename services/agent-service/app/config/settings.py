from urllib.parse import urlsplit

from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import field_validator


class Settings(BaseSettings):
    app_name: str = "EKA Agent Service"
    app_version: str = "1.0.0"
    environment: str = "development"
    agent_service_port: int = 8004
    rag_service_url: str = "http://127.0.0.1:8003"
    document_service_url: str = "http://127.0.0.1:8000"
    max_agent_retries: int = 2
    llm_provider: str = "mock"

    @field_validator("rag_service_url", "document_service_url")
    @classmethod
    def service_urls_must_be_loopback(cls, value: str) -> str:
        parsed = urlsplit(value)
        if (
            parsed.scheme != "http"
            or parsed.hostname not in {"127.0.0.1", "localhost", "::1"}
            or parsed.username is not None
            or parsed.password is not None
        ):
            raise ValueError("Agent service integrations must use local loopback HTTP URLs.")
        return value.rstrip("/")

    @field_validator("llm_provider")
    @classmethod
    def only_local_mock_provider_is_supported(cls, value: str) -> str:
        if value.lower() != "mock":
            raise ValueError("Only the local mock response provider is implemented.")
        return value.lower()

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


settings = Settings()
