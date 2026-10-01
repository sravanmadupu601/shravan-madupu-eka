from urllib.parse import urlsplit

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "EKA MCP Service"
    app_version: str = "1.0.0"
    environment: str = "development"
    mcp_service_host: str = "127.0.0.1"
    mcp_service_port: int = Field(default=8005, ge=1, le=65535)
    rag_service_url: str = "http://127.0.0.1:8003"
    document_service_url: str = "http://127.0.0.1:8000"
    request_timeout_seconds: float = Field(default=10.0, gt=0, le=120)
    max_document_page_size: int = Field(default=100, ge=1, le=100)

    @field_validator("mcp_service_host")
    @classmethod
    def host_must_be_loopback(cls, value: str) -> str:
        if value not in {"127.0.0.1", "localhost", "::1"}:
            raise ValueError("MCP_SERVICE_HOST must use a loopback address for local-only service binding.")
        return value

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
            raise ValueError("Service URLs must use local loopback HTTP without embedded credentials.")
        return value.rstrip("/")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


settings = Settings()
