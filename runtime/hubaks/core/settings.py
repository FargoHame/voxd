import os
import sys
from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


def _default_data_dir() -> Path:
    if value := os.environ.get("HUBAKS_HOME"):
        return Path(value).expanduser()

    if sys.platform == "darwin":
        return Path.home() / "Library" / "Application Support" / "Hubaks"

    if os.name == "nt":
        base = os.environ.get("LOCALAPPDATA")
        if base:
            return Path(base) / "Hubaks"
        return Path.home() / "AppData" / "Local" / "Hubaks"

    base = os.environ.get("XDG_DATA_HOME")
    if base:
        return Path(base) / "hubaks"
    return Path.home() / ".local" / "share" / "hubaks"


DATA_DIR = _default_data_dir()


class Settings(BaseSettings):
    """Application configuration."""

    host: str = Field(default="127.0.0.1")
    port: int = Field(default=11435)
    api_version: str = Field(default="v1")
    log_level: str = Field(default="INFO")
    device: str = Field(default="cpu")

    database_path: Path = DATA_DIR / "hubaks.db"
    cache_dir: Path = DATA_DIR / "cache"
    models_dir: Path = DATA_DIR / "models"
    outputs_dir: Path = DATA_DIR / "outputs"

    model_config = SettingsConfigDict(
        env_prefix="HUBAKS_",
        case_sensitive=False,
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
