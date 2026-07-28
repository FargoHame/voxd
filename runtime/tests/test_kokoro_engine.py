import sys
import types
from datetime import datetime

from voxd.constants.install_status import InstallStatus
from voxd.engines.kokoro import KokoroEngine
from voxd.models.audio import SpeechRequest
from voxd.models.installed_model import InstalledModel


class FakePipeline:
    def __init__(self, lang_code: str):
        self.lang_code = lang_code

    def __call__(self, text, voice, speed, split_pattern):
        assert text == "hello"
        assert voice == "af_heart"
        assert speed == 1.0
        assert split_pattern == r"\n+"
        yield text, "phonemes", [0.0, 0.25, -0.25]


def test_kokoro_engine_synthesizes_wav(monkeypatch, tmp_path):
    fake_module = types.ModuleType("kokoro")
    fake_module.KPipeline = FakePipeline
    monkeypatch.setitem(sys.modules, "kokoro", fake_module)

    engine = KokoroEngine()
    model = InstalledModel(
        model_name="kokoro",
        engine="kokoro",
        version="1.0",
        install_path=tmp_path / "kokoro",
        size_bytes=0,
        manifest_version="1.0",
        installed_at=datetime.now(),
        last_used=None,
        status=InstallStatus.INSTALLED,
    )
    manifest = engine.get_manifest("kokoro")

    engine.load(model, manifest)
    audio = engine.synthesize(SpeechRequest(input="hello", voice="af_heart"))

    assert audio.media_type == "audio/wav"
    assert audio.sample_rate == 24000
    assert audio.data.startswith(b"RIFF")


def test_kokoro_engine_uses_manifest_default_voice(monkeypatch, tmp_path):
    calls = []

    class BritishPipeline(FakePipeline):
        def __call__(self, text, voice, speed, split_pattern):
            calls.append(
                {
                    "lang_code": self.lang_code,
                    "voice": voice,
                    "speed": speed,
                    "split_pattern": split_pattern,
                }
            )
            yield text, "phonemes", [0.0]

    fake_module = types.ModuleType("kokoro")
    fake_module.KPipeline = BritishPipeline
    monkeypatch.setitem(sys.modules, "kokoro", fake_module)

    engine = KokoroEngine()
    model = InstalledModel(
        model_name="kokoro-british",
        engine="kokoro",
        version="1.0",
        install_path=tmp_path / "kokoro-british",
        size_bytes=0,
        manifest_version="1.0",
        installed_at=datetime.now(),
        last_used=None,
        status=InstallStatus.INSTALLED,
    )
    manifest = engine.get_manifest("kokoro-british")

    engine.load(model, manifest)
    engine.synthesize(SpeechRequest(input="hello"))

    assert calls == [
        {
            "lang_code": "b",
            "voice": "bf_emma",
            "speed": 1.0,
            "split_pattern": r"\n+",
        }
    ]
