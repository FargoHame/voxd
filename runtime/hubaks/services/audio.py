from __future__ import annotations

import io
import math
import wave
from collections.abc import Iterable
from typing import Any

from hubaks.models.audio import AudioResult


def encode_wav(
    audio: Any,
    sample_rate: int,
) -> AudioResult:
    """Encode mono float/int audio samples as 16-bit PCM WAV bytes."""

    samples = list(_iter_samples(_to_plain_audio(audio)))

    buffer = io.BytesIO()
    with wave.open(buffer, "wb") as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(sample_rate)
        wav.writeframes(b"".join(_pcm16(sample) for sample in samples))

    duration = len(samples) / sample_rate if sample_rate else None

    return AudioResult(
        data=buffer.getvalue(),
        media_type="audio/wav",
        sample_rate=sample_rate,
        format="wav",
        duration_seconds=duration,
    )


def _to_plain_audio(audio: Any) -> Any:
    if hasattr(audio, "detach"):
        audio = audio.detach().cpu()

    if hasattr(audio, "numpy"):
        audio = audio.numpy()

    if hasattr(audio, "tolist"):
        return audio.tolist()

    return audio


def _iter_samples(audio: Any) -> Iterable[float | int]:
    audio = _to_plain_audio(audio)

    if isinstance(audio, (bytes, bytearray)):
        raise TypeError("Raw bytes cannot be encoded as numeric audio samples.")

    if isinstance(audio, Iterable) and not isinstance(audio, (str, bytes, bytearray)):
        for item in audio:
            yield from _iter_samples(item)
        return

    yield audio


def _pcm16(sample: float | int) -> bytes:
    value = float(sample)

    if math.isnan(value) or math.isinf(value):
        value = 0.0

    if -1.0 <= value <= 1.0:
        value = max(-1.0, min(1.0, value))
        int_value = int(value * 32767)
    else:
        int_value = int(max(-32768, min(32767, value)))

    return int_value.to_bytes(2, byteorder="little", signed=True)
