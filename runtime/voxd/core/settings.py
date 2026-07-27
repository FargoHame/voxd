from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

ROOT_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT_DIR / "data"


class Settings(BaseSettings):
    """Application configuration."""

    host: str = Field(default="127.0.0.1")
    port: int = Field(default=11435)
    api_version: str = Field(default="v1")
    log_level: str = Field(default="INFO")
    device: str = Field(default="cpu")

    database_path: Path = DATA_DIR / "voxd.db"
    cache_dir: Path = DATA_DIR / "cache"
    models_dir: Path = DATA_DIR / "models"
    outputs_dir: Path = DATA_DIR / "outputs"

    model_config = SettingsConfigDict(
        env_prefix="VOXD_",
        case_sensitive=False,
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
