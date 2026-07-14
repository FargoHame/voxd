from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application configuration."""

    host: str = Field(default="127.0.0.1")
    port: int = Field(default=11435)
    api_version: str = Field(default="v1")
    log_level: str = Field(default="INFO")

    model_config = SettingsConfigDict(
        env_prefix="VOXD_",
        case_sensitive=False,
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    """Return a cached Settings instance."""
    return Settings()


settings = get_settings()