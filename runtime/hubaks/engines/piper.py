from __future__ import annotations

import io
import wave
from pathlib import Path

from hubaks.core.settings import settings
from hubaks.engines.base import SpeechEngine
from hubaks.manifests.base import ManifestProvider
from hubaks.manifests.local import LocalManifestProvider
from hubaks.models.audio import AudioResult, SpeechRequest
from hubaks.models.installed_model import InstalledModel
from hubaks.models.model_info import ModelInfo
from hubaks.models.model_manifest import ModelManifest


class PiperEngine(SpeechEngine):
    """Direct Piper ONNX speech engine."""

    def __init__(self, manifest_provider: ManifestProvider | None = None):
        self._loaded_model: InstalledModel | None = None
        self._loaded_manifest: ModelManifest | None = None
        self._voice = None
        self._manifest_provider = manifest_provider or LocalManifestProvider(
            Path(__file__).parent.parent / "manifests" / "catalog" / "piper.json"
        )

    @property
    def name(self) -> str:
        return "piper"

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
            from piper import PiperVoice
        except ImportError as exc:
            raise RuntimeError(
                "Piper is not installed. Install the Piper engine dependency "
                "in this environment before loading Piper models."
            ) from exc

        model_file = manifest.options["model_file"]
        config_file = manifest.options.get("config_file", f"{model_file}.json")
        use_cuda = settings.device == "cuda"

        self._voice = PiperVoice.load(
            model.install_path / model_file,
            config_path=model.install_path / config_file,
            use_cuda=use_cuda,
            download_dir=model.install_path,
        )
        self._loaded_model = model
        self._loaded_manifest = manifest

    def unload(self) -> None:
        self._voice = None
        self._loaded_model = None
        self._loaded_manifest = None

    def synthesize(self, request: SpeechRequest) -> AudioResult:
        if self._voice is None:
            raise RuntimeError("No model loaded.")

        try:
            from piper import SynthesisConfig
        except ImportError as exc:
            raise RuntimeError("Piper is not installed.") from exc

        syn_config = SynthesisConfig(
            length_scale=request.options.get("length_scale"),
            noise_scale=request.options.get("noise_scale"),
            noise_w_scale=request.options.get("noise_w_scale"),
            volume=request.options.get("volume", 1.0),
        )

        buffer = io.BytesIO()
        wav_params_set = False

        with wave.open(buffer, "wb") as wav:
            for chunk in self._voice.synthesize(request.input, syn_config):
                if not wav_params_set:
                    wav.setframerate(chunk.sample_rate)
                    wav.setsampwidth(chunk.sample_width)
                    wav.setnchannels(chunk.sample_channels)
                    wav_params_set = True

                wav.writeframes(chunk.audio_int16_bytes)

        sample_rate = self._voice.config.sample_rate

        return AudioResult(
            data=buffer.getvalue(),
            media_type="audio/wav",
            sample_rate=sample_rate,
            format="wav",
        )

    def capabilities(self) -> dict:
        return {
            "streaming": False,
            "voice_cloning": False,
            "multi_speaker": False,
            "device": settings.device,
        }

    def health(self) -> bool:
        return True

    def loaded_model(self) -> InstalledModel | None:
        return self._loaded_model
