from functools import lru_cache

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


def _ensure_async_pg(url: str) -> str:
    """Coerce Railway/Heroku-style `postgres://` URLs into async SQLAlchemy form."""
    if url.startswith("postgres://"):
        url = "postgresql://" + url[len("postgres://") :]
    if url.startswith("postgresql://"):
        url = "postgresql+asyncpg://" + url[len("postgresql://") :]
    return url


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/app"
    test_database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/app_test"
    anthropic_api_key: str = ""
    anthropic_model: str = "claude-sonnet-4-6"
    cors_origins: str = "http://localhost:3000"
    max_upload_bytes: int = 32 * 1024 * 1024

    @field_validator("database_url", "test_database_url", mode="before")
    @classmethod
    def _normalize_db_url(cls, v: object) -> object:
        return _ensure_async_pg(v) if isinstance(v, str) else v

    @property
    def cors_origins_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
