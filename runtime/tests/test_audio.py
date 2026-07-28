import wave
from io import BytesIO

from hubaks.services.audio import encode_wav


def test_encode_wav_returns_valid_wav_bytes():
    result = encode_wav([0.0, 0.5, -0.5], sample_rate=24000)

    assert result.media_type == "audio/wav"
    assert result.sample_rate == 24000
    assert result.data.startswith(b"RIFF")

    with wave.open(BytesIO(result.data), "rb") as wav:
        assert wav.getnchannels() == 1
        assert wav.getsampwidth() == 2
        assert wav.getframerate() == 24000
        assert wav.getnframes() == 3


def test_encode_wav_recursively_converts_tensor_like_audio():
    class FakeTensor:
        def __init__(self, value):
            self.value = value

        def detach(self):
            return self

        def cpu(self):
            return self

        def numpy(self):
            return self

        def tolist(self):
            return self.value

    result = encode_wav([FakeTensor([0.0, FakeTensor(0.25)])], sample_rate=24000)

    with wave.open(BytesIO(result.data), "rb") as wav:
        assert wav.getnframes() == 2
