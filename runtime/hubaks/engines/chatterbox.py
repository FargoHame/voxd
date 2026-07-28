from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from hubaks.core.settings import settings
from hubaks.engines.base import SpeechEngine
from hubaks.manifests.base import ManifestProvider
from hubaks.manifests.local import LocalManifestProvider
from hubaks.models.audio import AudioResult, SpeechRequest
from hubaks.models.installed_model import InstalledModel
from hubaks.models.model_info import ModelInfo
from hubaks.models.model_manifest import ModelManifest
from hubaks.services.audio import encode_wav


class ChatterboxEngine(SpeechEngine):
    """Direct Chatterbox speech engine."""

    def __init__(self, manifest_provider: ManifestProvider | None = None):
        self._loaded_model: InstalledModel | None = None
        self._loaded_manifest: ModelManifest | None = None
        self._tts_model = None
        self._manifest_provider = manifest_provider or LocalManifestProvider(
            Path(__file__).parent.parent / "manifests" / "catalog" / "chatterbox.json"
        )

    @property
    def name(self) -> str:
        return "chatterbox"

    def available_models(self) -> list[ModelInfo]:
        return self._manifest_provider.available_models()

    def get_manifest(self, model_name: str) -> ModelManifest:
        return self._manifest_provider.get_manifest(model_name)

    def load(
        self,
        model: InstalledModel,
        manifest: ModelManifest,
    ) -> None:
        self._ensure_cache_dir()
        self._tts_model = self._load_model(manifest)
        self._loaded_model = model
        self._loaded_manifest = manifest

    def unload(self) -> None:
        self._tts_model = None
        self._loaded_model = None
        self._loaded_manifest = None

    def synthesize(self, request: SpeechRequest) -> AudioResult:
        if self._tts_model is None:
            raise RuntimeError("No model loaded.")

        options = dict(self._loaded_manifest.options if self._loaded_manifest else {})
        options.update(request.options)

        kwargs: dict[str, Any] = {
            "repetition_penalty": options.get("repetition_penalty", 1.2),
            "min_p": options.get("min_p", 0.05),
            "top_p": options.get("top_p", 1.0),
            "exaggeration": options.get("exaggeration", 0.5),
            "cfg_weight": options.get("cfg_weight", 0.5),
            "temperature": options.get("temperature", 0.8),
        }

        if request.speed is not None:
            kwargs["cfg_weight"] = request.speed

        audio_prompt_path = request.voice or options.get("audio_prompt_path")
        if audio_prompt_path:
            kwargs["audio_prompt_path"] = str(audio_prompt_path)

        model_kind = options.get("model_kind", "english")
        if model_kind == "multilingual":
            kwargs["language_id"] = options.get("language_id", "en")
        elif model_kind == "turbo":
            kwargs["min_p"] = options.get("min_p", 0.0)
            kwargs["top_p"] = options.get("top_p", 0.95)
            kwargs["exaggeration"] = options.get("exaggeration", 0.0)
            kwargs["cfg_weight"] = options.get("cfg_weight", 0.0)
            kwargs["top_k"] = options.get("top_k", 1000)
            kwargs["norm_loudness"] = options.get("norm_loudness", True)

        audio = self._tts_model.generate(request.input, **kwargs)
        sample_rate = int(getattr(self._tts_model, "sr", options.get("sample_rate", 24000)))

        return encode_wav(audio, sample_rate=sample_rate)

    def capabilities(self) -> dict:
        return {
            "streaming": False,
            "voice_cloning": True,
            "multi_speaker": True,
            "device": settings.device,
        }

    def health(self) -> bool:
        return True

    def loaded_model(self) -> InstalledModel | None:
        return self._loaded_model

    def _load_model(self, manifest: ModelManifest):
        model_kind = manifest.options.get("model_kind", "english")
        device = self._device()

        try:
            if model_kind == "multilingual":
                import torch
                from chatterbox.mtl_tts import ChatterboxMultilingualTTS
                from chatterbox import mtl_tts

                self._patch_module_watermarker(mtl_tts)

                return ChatterboxMultilingualTTS.from_pretrained(
                    device=torch.device(device)
                )

            if model_kind == "turbo":
                from chatterbox.tts_turbo import ChatterboxTurboTTS
                from chatterbox import tts_turbo

                self._patch_module_watermarker(tts_turbo)

                return ChatterboxTurboTTS.from_pretrained(device=device)

            from chatterbox.tts import ChatterboxTTS
            from chatterbox import tts

            self._patch_module_watermarker(tts)

            return ChatterboxTTS.from_pretrained(device=device)
        except ImportError as exc:
            raise RuntimeError(
                "Chatterbox is not installed. Install Hubaks with the Chatterbox "
                "engine extra, or install chatterbox-tts in this environment."
            ) from exc

    def _ensure_cache_dir(self) -> None:
        cache_dir = settings.cache_dir / "huggingface"
        cache_dir.mkdir(parents=True, exist_ok=True)
        os.environ.setdefault("HF_HOME", str(cache_dir))

    def _device(self) -> str:
        try:
            import torch
        except ImportError:
            return "cpu"

        if settings.device == "cuda" and torch.cuda.is_available():
            return "cuda"
        return "cpu"

    @staticmethod
    def _patch_watermarker(perth_module) -> None:
        if getattr(perth_module, "PerthImplicitWatermarker", None) is not None:
            return

        dummy = getattr(perth_module, "DummyWatermarker", None)
        if dummy is None:
            raise RuntimeError("Chatterbox watermarker is unavailable.")

        perth_module.PerthImplicitWatermarker = dummy

    @classmethod
    def _patch_module_watermarker(cls, chatterbox_module) -> None:
        perth_module = getattr(chatterbox_module, "perth", None)
        if perth_module is not None:
            cls._patch_watermarker(perth_module)
