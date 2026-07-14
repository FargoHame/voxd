from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path

from voxd.models.model_info import ModelInfo
from voxd.models.model_manifest import ModelManifest


class SpeechEngine(ABC):
    """Abstract interface for all speech engines."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Unique engine name."""
        ...

    @abstractmethod
    def available_models(self) -> list[ModelInfo]:
        """Return available models."""
        ...

    @abstractmethod
    def get_manifest(self, model_name: str) -> ModelManifest:
        """Return a model manifest."""
        ...

    @abstractmethod
    def load(self, model_path: Path) -> None:
        """Load a model into memory."""
        ...

    @abstractmethod
    def unload(self) -> None:
        """Unload the current model."""
        ...

    @abstractmethod
    def synthesize(self, text: str, **kwargs) -> bytes:
        """Run text-to-speech."""
        ...

    @abstractmethod
    def capabilities(self) -> dict:
        """Return engine capabilities."""
        ...

    @abstractmethod
    def health(self) -> bool:
        """Return engine health."""
        ...