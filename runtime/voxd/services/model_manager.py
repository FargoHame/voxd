from __future__ import annotations
from pathlib import Path

from voxd.models.model_manifest import ModelManifest
from voxd.engines.registry import EngineRegistry
from voxd.models.installed_model import InstalledModel
from voxd.storage.model_registry import ModelRegistry
from voxd.services.downloader import Downloader

class ModelManager:
    """Coordinates model management across engines and storage."""

    def __init__(
        self,
        engine_registry: EngineRegistry | None = None,
        model_registry: ModelRegistry | None = None,
        downloader: Downloader | None = None,
    ) -> None:
        self._engines = engine_registry or EngineRegistry()
        self._models = model_registry or ModelRegistry()
        self._downloader = downloader or Downloader()

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

    def pull(self, engine_name: str, model_name: str) -> ModelManifest:
        """Prepare a model for installation."""

        engine = self._engines.get(engine_name)

        if self._models.exists(model_name):
            raise ValueError(f"Model '{model_name}' is already installed.")

        return engine.get_manifest(model_name)
    def prepare_install(self, engine_name: str, model_name: str) -> Path:
        """Prepare a model installation directory."""

        manifest = self.pull(engine_name, model_name)

        return self._downloader.prepare_download(manifest)