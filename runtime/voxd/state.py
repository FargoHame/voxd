from __future__ import annotations

from voxd.engines.base import SpeechEngine
from voxd.models.installed_model import InstalledModel


class RuntimeState:
    """Tracks the currently loaded model and engine."""

    def __init__(self) -> None:
        self._model: InstalledModel | None = None
        self._engine: SpeechEngine | None = None

    @property
    def model(self) -> InstalledModel | None:
        return self._model

    @property
    def engine(self) -> SpeechEngine | None:
        return self._engine

    @property
    def loaded(self) -> bool:
        return self._model is not None

    def set(
        self,
        model: InstalledModel,
        engine: SpeechEngine,
    ) -> None:
        self._model = model
        self._engine = engine

    def clear(self) -> None:
        self._model = None
        self._engine = None