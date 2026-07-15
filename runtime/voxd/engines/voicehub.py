from __future__ import annotations

from pathlib import Path

from voxd.engines.base import SpeechEngine
from voxd.manifests.base import ManifestProvider
from voxd.manifests.local import LocalManifestProvider
from voxd.models.model_info import ModelInfo
from voxd.models.model_manifest import ModelManifest


class VoiceHubEngine(SpeechEngine):
    """VoiceHub speech engine."""

    def __init__(self, manifest_provider: ManifestProvider | None = None):
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

    def load(self, model_path: Path) -> None:
        raise NotImplementedError

    def unload(self) -> None:
        raise NotImplementedError

    def synthesize(self, text: str, **kwargs) -> bytes:
        raise NotImplementedError

    def capabilities(self) -> dict:
        return {
            "streaming": False,
            "voice_cloning": False,
            "multi_speaker": False,
        }

    def health(self) -> bool:
        return True