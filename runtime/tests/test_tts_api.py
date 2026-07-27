from fastapi import FastAPI
from fastapi.testclient import TestClient

from voxd.api.tts import router
from voxd.models.audio import AudioResult, SpeechRequest


class FakeRuntime:
    def synthesize(self, request: SpeechRequest) -> AudioResult:
        assert request.input == "hello"
        return AudioResult(
            data=b"RIFFfake",
            media_type="audio/wav",
            sample_rate=24000,
            format="wav",
        )


def test_audio_speech_returns_engine_audio():
    app = FastAPI()
    app.state.runtime = FakeRuntime()
    app.include_router(router, prefix="/v1")

    response = TestClient(app).post(
        "/v1/audio/speech",
        json={"input": "hello"},
    )

    assert response.status_code == 200
    assert response.content == b"RIFFfake"
    assert response.headers["content-type"] == "audio/wav"
    assert response.headers["x-voxd-sample-rate"] == "24000"
