from __future__ import annotations

from pathlib import Path

from voxd.core.settings import settings
from voxd.engines.base import SpeechEngine
from voxd.manifests.base import ManifestProvider
from voxd.manifests.local import LocalManifestProvider
from voxd.models.audio import AudioResult, SpeechRequest
from voxd.models.installed_model import InstalledModel
from voxd.models.model_info import ModelInfo
from voxd.models.model_manifest import ModelManifest
from voxd.services.audio import encode_wav


class KokoroEngine(SpeechEngine):
    """Direct Kokoro speech engine."""

    def __init__(self, manifest_provider: ManifestProvider | None = None):
        self._loaded_model: InstalledModel | None = None
        self._pipeline = None
        self._manifest_provider = manifest_provider or LocalManifestProvider(
            Path(__file__).parent.parent / "manifests" / "catalog" / "kokoro.json"
        )

    @property
    def name(self) -> str:
        return "kokoro"

    def available_models(self) -> list[ModelInfo]:
        return self._manifest_provider.available_models()

    def get_manifest(self, model_name: str) -> ModelManifest:
        return self._manifest_provider.get_manifest(model_name)

    def load(
        self,
        model: InstalledModel,
        manifest: ModelManifest,
    ) -> None:
        try:
            from kokoro import KPipeline
        except ImportError as exc:
            raise RuntimeError(
                "Kokoro is not installed. Install the Kokoro engine dependency "
                "in this environment before loading Kokoro models."
            ) from exc

        lang_code = manifest.options.get("lang_code", "a")
        self._pipeline = KPipeline(lang_code=lang_code)
        self._loaded_model = model

    def unload(self) -> None:
        self._pipeline = None
        self._loaded_model = None

    def synthesize(self, request: SpeechRequest) -> AudioResult:
        if self._pipeline is None:
            raise RuntimeError("No model loaded.")

        voice = request.voice or "af_heart"
        speed = request.speed or 1.0
        split_pattern = request.options.get("split_pattern", r"\n+")

        generator = self._pipeline(
            request.input,
            voice=voice,
            speed=speed,
            split_pattern=split_pattern,
        )
        audios = [audio for _, _, audio in generator]

        if not audios:
            raise RuntimeError("Kokoro did not generate any audio.")

        return encode_wav(audios, sample_rate=24000)

    def capabilities(self) -> dict:
        return {
            "streaming": False,
            "voice_cloning": False,
            "multi_speaker": True,
            "device": settings.device,
        }

    def health(self) -> bool:
        return True

    def loaded_model(self) -> InstalledModel | None:
        return self._loaded_model
