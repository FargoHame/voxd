from fastapi import FastAPI
from fastapi.testclient import TestClient

from voxd.api.tts import router
from voxd.models.audio import AudioResult, SpeechRequest


class FakeRuntime:
    def __init__(self):
        self.loaded_model = None

    def current(self):
        return None

    def load(self, model: str) -> None:
        self.loaded_model = model

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


def test_audio_speech_loads_requested_model():
    app = FastAPI()
    runtime = FakeRuntime()
    app.state.runtime = runtime
    app.include_router(router, prefix="/v1")

    response = TestClient(app).post(
        "/v1/audio/speech",
        json={
            "model": "kokoro",
            "input": "hello",
        },
    )

    assert response.status_code == 200
    assert runtime.loaded_model == "kokoro"


def test_audio_speech_returns_not_found_for_unknown_model():
    class MissingModelRuntime(FakeRuntime):
        def load(self, model: str) -> None:
            raise ValueError(f"Model '{model}' is not installed.")

    app = FastAPI()
    app.state.runtime = MissingModelRuntime()
    app.include_router(router, prefix="/v1")

    response = TestClient(app).post(
        "/v1/audio/speech",
        json={
            "model": "missing",
            "input": "hello",
        },
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Model 'missing' is not installed."
