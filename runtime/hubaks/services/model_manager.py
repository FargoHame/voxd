from __future__ import annotations

import shutil
from datetime import datetime
from pathlib import Path

from hubaks.constants.install_status import InstallStatus
from hubaks.core.settings import settings
from hubaks.engines.base import SpeechEngine
from hubaks.engines.registry import EngineRegistry
from hubaks.models.audio import AudioResult, SpeechRequest
from hubaks.models.installed_model import InstalledModel
from hubaks.models.model_manifest import ModelManifest
from hubaks.services.downloader import Downloader
from hubaks.storage.model_registry import ModelRegistry


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

    def available_models(self, engine: str | None = None) -> list:
        if engine is not None:
            return self._engines.get(engine).available_models()

        models = []
        for speech_engine in self._engines.list():
            models.extend(speech_engine.available_models())

        return models

    def installed_models(self) -> list[InstalledModel]:
        return [self._reconcile_model(model) for model in self._models.list()]

    def is_installed(self, model_name: str) -> bool:
        return self._models.exists(model_name)

    def get_installed_model(
        self,
        model_name: str,
    ) -> InstalledModel | None:
        model = self._models.get(model_name)
        return self._reconcile_model(model) if model is not None else None

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

        final_dir = self._install_dir(manifest.model_name)
        if final_dir.exists():
            shutil.rmtree(final_dir)

        final_dir.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(install_dir), str(final_dir))

        installed_model = InstalledModel(
            model_name=manifest.model_name,
            engine=manifest.engine,
            version=manifest.version,
            install_path=final_dir,
            size_bytes=manifest.total_size,
            manifest_version=manifest.version,
            installed_at=datetime.now(),
            last_used=None,
            status=InstallStatus.INSTALLED,
        )

        self._models.add(installed_model)

        return final_dir

    def install(self, model_name: str) -> Path:
        """Install a model by resolving its owning engine from the catalog."""

        manifest = self.get_manifest(model_name)

        existing = self._models.get(model_name)
        if existing is not None:
            return self._reconcile_model(existing, manifest).install_path

        return self.prepare_install(manifest.engine, model_name)

    def get_manifest(self, model_name: str) -> ModelManifest:
        for engine in self._engines.list():
            try:
                return engine.get_manifest(model_name)
            except ValueError:
                continue

        raise ValueError(f"Unknown model: {model_name}")

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

        manifest = self.get_manifest(model.model_name)
        model = self._reconcile_model(model, manifest)
        engine = self._engines.get(model.engine)

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

    @staticmethod
    def _install_dir(model_name: str) -> Path:
        return settings.models_dir / model_name

    def _reconcile_model(
        self,
        model: InstalledModel,
        manifest: ModelManifest | None = None,
    ) -> InstalledModel:
        """Update installed metadata when the catalog changes engine ownership."""

        if manifest is None:
            try:
                manifest = self.get_manifest(model.model_name)
            except ValueError:
                return model

        changed = False

        if model.engine != manifest.engine:
            model.engine = manifest.engine
            changed = True

        if model.version != manifest.version:
            model.version = manifest.version
            changed = True

        if model.manifest_version != manifest.version:
            model.manifest_version = manifest.version
            changed = True

        if model.size_bytes != manifest.total_size:
            model.size_bytes = manifest.total_size
            changed = True

        if changed:
            self._models.update(model)

        return model
