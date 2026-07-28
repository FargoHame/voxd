from __future__ import annotations

from hubaks.engines.base import SpeechEngine
from hubaks.engines.kokoro import KokoroEngine
from hubaks.engines.piper import PiperEngine
from hubaks.engines.voicehub import VoiceHubEngine


class EngineRegistry:
    """Registry of available speech engines."""

    def __init__(self) -> None:
        self._engines: dict[str, SpeechEngine] = {}
        self.register(KokoroEngine())
        self.register(PiperEngine())
        self.register(VoiceHubEngine())

    def register(self, engine: SpeechEngine) -> None:
        self._engines[engine.name] = engine

    def get(self, name: str) -> SpeechEngine:
        try:
            return self._engines[name]
        except KeyError as exc:
            raise ValueError(f"Unknown engine: {name}") from exc

    def exists(self, name: str) -> bool:
        return name in self._engines

    def list(self) -> list[SpeechEngine]:
        return list(self._engines.values())
