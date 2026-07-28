import sys
import types
from datetime import datetime

from hubaks.constants.install_status import InstallStatus
from hubaks.engines.chatterbox import ChatterboxEngine
from hubaks.models.audio import SpeechRequest
from hubaks.models.installed_model import InstalledModel


class FakeChatterboxTTS:
    sr = 24000
    last_device = None
    last_kwargs = None

    @classmethod
    def from_pretrained(cls, device):
        cls.last_device = device
        return cls()

    def generate(self, text, **kwargs):
        assert text == "hello"
        self.__class__.last_kwargs = kwargs
        return [0.0, 0.25, -0.25]


def test_chatterbox_engine_synthesizes_with_audio_prompt(monkeypatch, tmp_path):
    fake_package = types.ModuleType("chatterbox")
    fake_tts_module = types.ModuleType("chatterbox.tts")
    fake_tts_module.ChatterboxTTS = FakeChatterboxTTS
    monkeypatch.setitem(sys.modules, "chatterbox", fake_package)
    monkeypatch.setitem(sys.modules, "chatterbox.tts", fake_tts_module)

    engine = ChatterboxEngine()
    model = InstalledModel(
        model_name="chatterbox",
        engine="chatterbox",
        version="0.1.7",
        install_path=tmp_path / "chatterbox",
        size_bytes=0,
        manifest_version="0.1.7",
        installed_at=datetime.now(),
        last_used=None,
        status=InstallStatus.INSTALLED,
    )
    manifest = engine.get_manifest("chatterbox")

    engine.load(model, manifest)
    audio = engine.synthesize(
        SpeechRequest(
            input="hello",
            options={
                "audio_prompt_path": str(tmp_path / "voice.wav"),
                "temperature": 0.7,
            },
        )
    )

    assert FakeChatterboxTTS.last_device == "cpu"
    assert FakeChatterboxTTS.last_kwargs["audio_prompt_path"].endswith("voice.wav")
    assert FakeChatterboxTTS.last_kwargs["temperature"] == 0.7
    assert audio.media_type == "audio/wav"
    assert audio.sample_rate == 24000
    assert audio.data.startswith(b"RIFF")
