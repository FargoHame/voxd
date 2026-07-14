from __future__ import annotations

from pathlib import Path

from voxd.engines.base import SpeechEngine
from voxd.models.model_file import ModelFile
from voxd.models.model_info import ModelInfo
from voxd.models.model_manifest import ModelManifest


class VoiceHubEngine(SpeechEngine):
    """VoiceHub speech engine."""

    @property
    def name(self) -> str:
        return "voicehub"

    def available_models(self) -> list[ModelInfo]:
        return [
            ModelInfo(
                name="kokoro",
                engine="voicehub",
                description="Fast lightweight English TTS model",
                size_bytes=123_456_789,
                version="1.0",
                license="Apache-2.0",
            )
        ]

    def get_manifest(self, model_name: str) -> ModelManifest:
        if model_name != "kokoro":
            raise ValueError(f"Unknown model: {model_name}")

        files = [
            ModelFile(
                filename="model.safetensors",
                url="https://example.com/model.safetensors",
                sha256="dummyhash",
                size_bytes=123_456_789,
            )
        ]

        return ModelManifest(
            model_name="kokoro",
            engine="voicehub",
            version="1.0",
            files=files,
            total_size=sum(file.size_bytes for file in files),
            license="Apache-2.0",
            homepage="https://huggingface.co/hexgrad/Kokoro-82M",
        )

    def load(self, model_path: Path) -> None:
        raise NotImplementedError

    def unload(self) -> None:
        raise NotImplementedError

    def synthesize(self, text: str, **kwargs) -> bytes:
        raise NotImplementedError

    def capabilities(self) -> dict:
        return {}

    def health(self) -> bool:
        return True