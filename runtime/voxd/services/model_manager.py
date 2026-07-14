from __future__ import annotations

from voxd.engines.registry import EngineRegistry
from voxd.models.installed_model import InstalledModel
from voxd.storage.model_registry import ModelRegistry


class ModelManager:
    """Coordinates model management across engines and storage."""

    def __init__(
        self,
        engine_registry: EngineRegistry | None = None,
        model_registry: ModelRegistry | None = None,
    ) -> None:
        self._engines = engine_registry or EngineRegistry()
        self._models = model_registry or ModelRegistry()

    def available_models(self, engine: str) -> list:
        """Return models available from an engine."""
        return self._engines.get(engine).available_models()

    def installed_models(self) -> list[InstalledModel]:
        """Return installed models."""
        return self._models.list()

    def is_installed(self, model_name: str) -> bool:
        """Check whether a model is installed."""
        return self._models.exists(model_name)

    def get_installed_model(
        self,
        model_name: str,
    ) -> InstalledModel | None:
        """Return an installed model."""
        return self._models.get(model_name)

    def remove(self, model_name: str) -> None:
        """Remove a model from the registry."""
        self._models.remove(model_name)