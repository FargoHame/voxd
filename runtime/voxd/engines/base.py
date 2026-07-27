from __future__ import annotations

from abc import ABC, abstractmethod

from voxd.models.audio import AudioResult, SpeechRequest
from voxd.models.model_info import ModelInfo
from voxd.models.model_manifest import ModelManifest
from voxd.models.installed_model import InstalledModel


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
    def load(
        self,
        model: InstalledModel,
        manifest: ModelManifest,
    ) -> None:
        """Load a model into memory."""
        ...

    @abstractmethod
    def unload(self) -> None:
        """Unload the current model."""
        ...

    @abstractmethod
    def synthesize(self, request: SpeechRequest) -> AudioResult:
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

    @abstractmethod
    def loaded_model(self) -> InstalledModel | None:
        """Return the currently loaded model."""
        ...
