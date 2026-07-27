from __future__ import annotations

import shutil
from datetime import datetime
from pathlib import Path

from voxd.constants.install_status import InstallStatus
from voxd.engines.base import SpeechEngine
from voxd.engines.registry import EngineRegistry
from voxd.models.audio import AudioResult, SpeechRequest
from voxd.models.installed_model import InstalledModel
from voxd.models.model_manifest import ModelManifest
from voxd.services.downloader import Downloader
from voxd.storage.model_registry import ModelRegistry


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

        self._loaded_engine: SpeechEngine | None = None
        self._loaded_model: InstalledModel | None = None

    def available_models(self, engine: str) -> list:
        return self._engines.get(engine).available_models()

    def installed_models(self) -> list[InstalledModel]:
        return self._models.list()

    def is_installed(self, model_name: str) -> bool:
        return self._models.exists(model_name)

    def get_installed_model(
        self,
        model_name: str,
    ) -> InstalledModel | None:
        return self._models.get(model_name)

    def remove(self, model_name: str) -> None:
        """Remove an installed model from the registry and delete its files."""

        # Unload first if this model is currently loaded.
        if (
            self._loaded_model is not None
            and self._loaded_model.model_name == model_name
        ):
            self.unload()

        model = self._models.get(model_name)
        if model is not None and model.install_path.exists():
            shutil.rmtree(model.install_path)
        self._models.remove(model_name)

    def pull(
        self,
        engine_name: str,
        model_name: str,
    ) -> ModelManifest:
        engine = self._engines.get(engine_name)

        if self._models.exists(model_name):
            raise ValueError(f"Model '{model_name}' is already installed.")

        return engine.get_manifest(model_name)

    def prepare_install(
        self,
        engine_name: str,
        model_name: str,
    ) -> Path:

        manifest = self.pull(engine_name, model_name)

        install_dir = self._downloader.prepare_download(manifest)

        self._downloader.download_manifest(
            manifest,
            install_dir,
        )

        if not self._downloader.verify_manifest(
            manifest,
            install_dir,
        ):
            shutil.rmtree(install_dir)
            raise ValueError("Downloaded files failed SHA-256 verification.")

        installed_model = InstalledModel(
            model_name=manifest.model_name,
            engine=manifest.engine,
            version=manifest.version,
            install_path=install_dir,
            size_bytes=manifest.total_size,
            manifest_version=manifest.version,
            installed_at=datetime.now(),
            last_used=None,
            status=InstallStatus.INSTALLED,
        )

        self._models.add(installed_model)

        return install_dir

    def load(
        self,
        model_name: str,
    ) -> InstalledModel:
        """Load an installed model into its engine.

        Idempotent: if the requested model is already loaded, returns it
        without re-initializing the engine.
        """

        if (
            self._loaded_model is not None
            and self._loaded_model.model_name == model_name
        ):
            return self._loaded_model

        if self._loaded_model is not None:
            self.unload()

        model = self._models.get(model_name)

        if model is None:
            raise ValueError(f"Model '{model_name}' is not installed.")

        engine = self._engines.get(model.engine)

        manifest = engine.get_manifest(model.model_name)

        engine.load(
            model=model,
            manifest=manifest,
        )
        self._loaded_engine = engine
        self._loaded_model = model

        model.last_used = datetime.now()

        self._models.update(model)

        return model

    def unload(self) -> None:
        """Unload the currently loaded model."""

        if self._loaded_engine is None:
            return

        self._loaded_engine.unload()

        self._loaded_engine = None
        self._loaded_model = None

    def loaded_model(self) -> InstalledModel | None:
        """Return the currently loaded model."""
        return self._loaded_model

    def synthesize(self, request: SpeechRequest) -> AudioResult:
        """Generate speech using the loaded model."""

        if self._loaded_engine is None:
            raise RuntimeError("No model is currently loaded.")

        return self._loaded_engine.synthesize(request)
