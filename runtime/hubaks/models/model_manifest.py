from dataclasses import dataclass, field
from typing import Any

from hubaks.models.model_file import ModelFile


@dataclass(slots=True, frozen=True)
class ModelManifest:
    """Complete installation manifest for a model."""

    model_name: str
    engine: str
    version: str
    files: list[ModelFile]
    total_size: int
    license: str
    homepage: str
    options: dict[str, Any] = field(default_factory=dict)
