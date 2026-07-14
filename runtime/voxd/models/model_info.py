from dataclasses import dataclass


@dataclass(slots=True, frozen=True)
class ModelInfo:
    """Lightweight information shown when browsing available models."""

    name: str
    engine: str
    description: str
    size_bytes: int
    version: str
    license: str