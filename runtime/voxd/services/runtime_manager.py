from __future__ import annotations

from voxd.models.audio import AudioResult, SpeechRequest
from voxd.services.model_manager import ModelManager
from voxd.models.installed_model import InstalledModel


class RuntimeManager:
    """Coordinates the runtime lifecycle of loaded models.

    A thin orchestration layer that delegates model operations
    to ModelManager. Does not duplicate loading or state logic.
    """

    def __init__(
        self,
        model_manager: ModelManager | None = None,
    ) -> None:
        self._models = model_manager or ModelManager()

    def load(self, model_name: str) -> None:
        """Load an installed model."""
        self._models.load(model_name)

    def unload(self) -> None:
        """Unload the current model."""
        self._models.unload()

    def current(self) -> InstalledModel | None:
        """Return the currently loaded model."""
        return self._models.loaded_model()

    def loaded(self) -> bool:
        """Return whether a model is currently loaded."""
        return self.current() is not None

    def synthesize(self, request: SpeechRequest) -> AudioResult:
        """Generate speech using the loaded model."""
        return self._models.synthesize(request)
