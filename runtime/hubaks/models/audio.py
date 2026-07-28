from dataclasses import dataclass
from typing import Any

from pydantic import BaseModel, Field


class SpeechRequest(BaseModel):
    """Normalized request contract for speech synthesis."""

    input: str = Field(alias="input")
    model: str | None = None
    voice: str | None = None
    speed: float | None = None
    format: str = "wav"
    options: dict[str, Any] = Field(default_factory=dict)

    model_config = {
        "populate_by_name": True,
        "extra": "forbid",
    }


@dataclass(slots=True, frozen=True)
class AudioResult:
    """Encoded audio returned by an engine."""

    data: bytes
    media_type: str
    sample_rate: int
    format: str
    duration_seconds: float | None = None
