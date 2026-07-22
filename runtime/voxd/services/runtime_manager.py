from __future__ import annotations

from voxd.engines.registry import EngineRegistry
from voxd.state import RuntimeState
from voxd.storage.model_registry import ModelRegistry
from voxd.models.installed_model import InstalledModel


class RuntimeManager:
    """Coordinates the runtime lifecycle of loaded models."""

    def __init__(
        self,
        engine_registry: EngineRegistry | None = None,
        model_registry: ModelRegistry | None = None,
        state: RuntimeState | None = None,
    ) -> None:
        self._engines = engine_registry or EngineRegistry()
        self._models = model_registry or ModelRegistry()
        self._state = state or RuntimeState()

    def load(self, model_name: str) -> None:
        """Load an installed model."""

        # If the requested model is already loaded, do nothing.
        if (
            self._state.loaded
            and self._state.model is not None
            and self._state.model.model_name == model_name
        ):
            return

        # If another model is loaded, unload it first.
        if self._state.loaded:
            self.unload()

        model = self._models.get(model_name)

        if model is None:
            raise ValueError(f"Model '{model_name}' is not installed.")

        engine = self._engines.get(model.engine)

        if engine is None:
            raise ValueError(f"Engine '{model.engine}' is not registered.")

        engine.load(model)

        self._state.set(model, engine)

    def unload(self) -> None:
        """Unload the current model."""

        if not self._state.loaded:
            return

        if self._state.engine is not None:
            self._state.engine.unload()

        self._state.clear()

    def current(self) -> InstalledModel | None:
        """Return the currently loaded model."""
        return self._state.model

    def loaded(self) -> bool:
        """Return whether a model is currently loaded."""
        return self._state.loaded