from fastapi import FastAPI
from fastapi.testclient import TestClient

from hubaks.api.generations import router
from hubaks.models.audio import AudioResult, SpeechRequest
from hubaks.services.generation_store import GenerationStore


def test_generations_api_lists_audio_and_renames(tmp_path):
    store = GenerationStore(tmp_path)
    record = store.save(
        SpeechRequest(input="hello", model="kokoro"),
        AudioResult(
            data=b"RIFFdata",
            media_type="audio/wav",
            sample_rate=24000,
            format="wav",
        ),
        None,
    )

    app = FastAPI()
    app.state.generation_store = store
    app.include_router(router, prefix="/v1")
    client = TestClient(app)

    list_response = client.get("/v1/generations")
    assert list_response.status_code == 200
    assert list_response.json()["generations"][0]["id"] == record.id

    audio_response = client.get(f"/v1/generations/{record.id}/audio")
    assert audio_response.status_code == 200
    assert audio_response.content == b"RIFFdata"

    rename_response = client.patch(
        f"/v1/generations/{record.id}",
        json={"name": "Renamed clip"},
    )
    assert rename_response.status_code == 200
    assert rename_response.json()["name"] == "Renamed clip"
