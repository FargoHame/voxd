import wave
from io import BytesIO

from voxd.services.audio import encode_wav


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
