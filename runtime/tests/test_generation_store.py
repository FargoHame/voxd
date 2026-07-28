import pytest

from voxd.models.audio import AudioResult, SpeechRequest
from voxd.services.generation_store import GenerationStore


def test_generation_store_saves_lists_and_renames(tmp_path):
    store = GenerationStore(tmp_path)
    audio = AudioResult(
        data=b"RIFFdata",
        media_type="audio/wav",
        sample_rate=24000,
        format="wav",
        duration_seconds=1.0,
    )

    record = store.save(SpeechRequest(input="hello world", model="kokoro"), audio, None)

    assert (tmp_path / record.filename).read_bytes() == b"RIFFdata"
    assert store.list()[0].id == record.id
    assert store.audio_path(record.id) == tmp_path / record.filename

    renamed = store.rename(record.id, "New name")

    assert renamed.name == "New name"
    assert store.get(record.id).name == "New name"


def test_generation_store_rejects_invalid_ids(tmp_path):
    store = GenerationStore(tmp_path)

    with pytest.raises(ValueError, match="Invalid generation id"):
        store.get("../bad")
