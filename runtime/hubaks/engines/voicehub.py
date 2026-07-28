from __future__ import annotations

from pathlib import Path

from hubaks.engines.base import SpeechEngine
from hubaks.core.settings import settings
from hubaks.manifests.base import ManifestProvider
from hubaks.manifests.local import LocalManifestProvider
from hubaks.models.audio import AudioResult, SpeechRequest
from hubaks.models.model_info import ModelInfo
from hubaks.models.model_manifest import ModelManifest
from hubaks.models.installed_model import InstalledModel
from hubaks.services.audio import encode_wav


class VoiceHubEngine(SpeechEngine):
    """VoiceHub speech engine."""

    def __init__(self, manifest_provider: ManifestProvider | None = None):
        self._loaded_model: InstalledModel | None = None
        self._tts_model = None

        self._manifest_provider = manifest_provider or LocalManifestProvider(
            Path(__file__).parent.parent / "manifests" / "catalog" / "voicehub.json"
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

        try:
            from voicehub.automodel import AutoInferenceModel
        except ImportError as exc:
            raise RuntimeError(
                "VoiceHub is not installed. Install hubaks with the VoiceHub "
                "engine extra, or install the VoiceHub package in this environment."
            ) from exc

        self._tts_model = AutoInferenceModel.from_pretrained(
            model_type=model.model_name,
            model_path=str(model.install_path),
            device=settings.device,
        )

        self._loaded_model = model

    def unload(self) -> None:
        """Unload the current model."""

        self._tts_model = None
        self._loaded_model = None

    def synthesize(self, request: SpeechRequest) -> AudioResult:
        if self._tts_model is None:
            raise RuntimeError("No model loaded.")

        kwargs = dict(request.options)
        if request.voice is not None:
            kwargs["voice"] = request.voice
        if request.speed is not None:
            kwargs["speed"] = request.speed

        audio = self._call_loaded_model(request.input, kwargs)
        sample_rate = getattr(self._tts_model, "sample_rate", 24000)

        return encode_wav(audio, sample_rate=sample_rate)

    def _call_loaded_model(self, text: str, kwargs: dict):
        model_name = self._loaded_model.model_name if self._loaded_model else ""

        if model_name in {"orpheustts", "dia"}:
            return self._tts_model.synthesize(prompt=text, **kwargs)

        return self._tts_model.synthesize(text=text, **kwargs)

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
