import sys
import types
from datetime import datetime

from voxd.constants.install_status import InstallStatus
from voxd.engines.piper import PiperEngine
from voxd.models.audio import SpeechRequest
from voxd.models.installed_model import InstalledModel


class FakeConfig:
    sample_rate = 22050


class FakeChunk:
    sample_rate = 22050
    sample_width = 2
    sample_channels = 1
    audio_int16_bytes = b"\x00\x00\x01\x00"


class FakeVoice:
    config = FakeConfig()

    @staticmethod
    def load(model_path, config_path, use_cuda, download_dir):
        assert model_path.name == "en_US-lessac-low.onnx"
        assert config_path.name == "en_US-lessac-low.onnx.json"
        assert use_cuda is False
        assert download_dir == model_path.parent
        return FakeVoice()

    def synthesize(self, text, syn_config):
        assert text == "hello"
        assert syn_config.volume == 1.0
        yield FakeChunk()


class FakeSynthesisConfig:
    def __init__(self, length_scale, noise_scale, noise_w_scale, volume):
        self.length_scale = length_scale
        self.noise_scale = noise_scale
        self.noise_w_scale = noise_w_scale
        self.volume = volume


def test_piper_engine_synthesizes_wav(monkeypatch, tmp_path):
    fake_module = types.ModuleType("piper")
    fake_module.PiperVoice = FakeVoice
    fake_module.SynthesisConfig = FakeSynthesisConfig
    monkeypatch.setitem(sys.modules, "piper", fake_module)

    engine = PiperEngine()
    model = InstalledModel(
        model_name="piper-lessac-low",
        engine="piper",
        version="1.0",
        install_path=tmp_path / "piper-lessac-low",
        size_bytes=0,
        manifest_version="1.0",
        installed_at=datetime.now(),
        last_used=None,
        status=InstallStatus.INSTALLED,
    )
    manifest = engine.get_manifest("piper-lessac-low")

    engine.load(model, manifest)
    audio = engine.synthesize(SpeechRequest(input="hello"))

    assert audio.media_type == "audio/wav"
    assert audio.sample_rate == 22050
    assert audio.data.startswith(b"RIFF")
