from __future__ import annotations

from pathlib import Path

from voicehub.automodel import AutoInferenceModel

from voxd.engines.base import SpeechEngine
from voxd.manifests.base import ManifestProvider
from voxd.manifests.local import LocalManifestProvider
from voxd.models.model_info import ModelInfo
from voxd.models.model_manifest import ModelManifest
from voxd.models.installed_model import InstalledModel


class VoiceHubEngine(SpeechEngine):
    """VoiceHub speech engine."""

    def __init__(self, manifest_provider: ManifestProvider | None = None):
        self._loaded_model: InstalledModel | None = None
        self._tts_model = None

        self._manifest_provider = (
            manifest_provider
            or LocalManifestProvider(
                Path(__file__).parent.parent
                / "manifests"
                / "catalog"
                / "voicehub.json"
            )
        )

    @property
    def name(self) -> str:
        return "voicehub"

    def available_models(self) -> list[ModelInfo]:
        return self._manifest_provider.available_models()

    def get_manifest(self, model_name: str) -> ModelManifest:
        return self._manifest_provider.get_manifest(model_name)

    def load(
        self,
        model: InstalledModel,
        manifest: ModelManifest,
    ) -> None:
        """Load an installed model."""

        if not model.install_path.exists():
            raise FileNotFoundError(
                f"Model directory does not exist: {model.install_path}"
            )

        self._tts_model = AutoInferenceModel.from_pretrained(
            model_type=model.model_name,
            model_path=str(model.install_path),
            device="cpu",
        )

        self._loaded_model = model

    def unload(self) -> None:
        """Unload the current model."""

        self._tts_model = None
        self._loaded_model = None

    def synthesize(self, text: str, **kwargs):
        if self._tts_model is None:
            raise RuntimeError("No model loaded.")

        return self._tts_model.synthesize(
            text=text,
            **kwargs,
        )

    def capabilities(self) -> dict:
        return {
            "streaming": False,
            "voice_cloning": False,
            "multi_speaker": False,
        }

    def health(self) -> bool:
        return True
    
    def loaded_model(self) -> InstalledModel | None:
        """Return the currently loaded model."""

        return self._loaded_model