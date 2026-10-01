from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "EKA ML Service"
    app_version: str = "1.0.0"
    environment: str = "development"
    ml_service_port: int = Field(default=8006, ge=1, le=65535)
    dataset_storage_path: str = "../../data/datasets"
    model_storage_path: str = "./models"
    default_test_size: float = Field(default=0.2, gt=0.05, lt=0.5)
    default_random_state: int = 42
    max_upload_bytes: int = Field(default=10_000_000, ge=1_024, le=100_000_000)

    def resolve_path(self, value: str) -> Path:
        path = Path(value).expanduser()
        if not path.is_absolute():
            path = Path.cwd() / path
        return path.resolve()

    @property
    def dataset_path(self) -> Path:
        return self.resolve_path(self.dataset_storage_path)

    @property
    def model_path(self) -> Path:
        return self.resolve_path(self.model_storage_path)

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


settings = Settings()
