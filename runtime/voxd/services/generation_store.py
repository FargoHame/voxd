from __future__ import annotations

import json
import re
import uuid
from datetime import datetime
from pathlib import Path

from voxd.core.settings import settings
from voxd.models.audio import AudioResult, SpeechRequest
from voxd.models.generation import GenerationRecord
from voxd.models.installed_model import InstalledModel


class GenerationStore:
    """File-backed store for generated audio and metadata."""

    def __init__(self, root: Path | None = None):
        self._root = root or settings.outputs_dir / "generations"
        self._root.mkdir(parents=True, exist_ok=True)

    def save(
        self,
        request: SpeechRequest,
        audio: AudioResult,
        model: InstalledModel | None,
    ) -> GenerationRecord:
        generation_id = uuid.uuid4().hex
        name = _default_name(request.input)
        filename = f"{generation_id}.{audio.format}"
        audio_path = self._root / filename
        metadata_path = self._metadata_path(generation_id)

        audio_path.write_bytes(audio.data)

        record = GenerationRecord(
            id=generation_id,
            name=name,
            model=model.model_name if model else request.model,
            engine=model.engine if model else None,
            text=request.input,
            filename=filename,
            media_type=audio.media_type,
            sample_rate=audio.sample_rate,
            size_bytes=len(audio.data),
            duration_seconds=audio.duration_seconds,
            created_at=datetime.now().isoformat(),
        )
        metadata_path.write_text(
            record.model_dump_json(indent=2),
            encoding="utf-8",
        )

        return record

    def list(self) -> list[GenerationRecord]:
        records = []

        for metadata_path in self._root.glob("*.json"):
            try:
                records.append(self._read_metadata(metadata_path))
            except (OSError, ValueError):
                continue

        return sorted(records, key=lambda item: item.created_at, reverse=True)

    def get(self, generation_id: str) -> GenerationRecord:
        metadata_path = self._metadata_path(generation_id)
        if not metadata_path.exists():
            raise ValueError(f"Unknown generation: {generation_id}")

        return self._read_metadata(metadata_path)

    def audio_path(self, generation_id: str) -> Path:
        record = self.get(generation_id)
        audio_path = self._root / record.filename
        if not audio_path.exists():
            raise ValueError(f"Audio file is missing for generation: {generation_id}")

        return audio_path

    def rename(self, generation_id: str, name: str) -> GenerationRecord:
        cleaned_name = _clean_name(name)
        record = self.get(generation_id)
        record.name = cleaned_name

        self._metadata_path(generation_id).write_text(
            record.model_dump_json(indent=2),
            encoding="utf-8",
        )

        return record

    def _metadata_path(self, generation_id: str) -> Path:
        if not re.fullmatch(r"[a-f0-9]{32}", generation_id):
            raise ValueError(f"Invalid generation id: {generation_id}")

        return self._root / f"{generation_id}.json"

    @staticmethod
    def _read_metadata(metadata_path: Path) -> GenerationRecord:
        data = json.loads(metadata_path.read_text(encoding="utf-8"))
        return GenerationRecord.model_validate(data)


def _default_name(text: str) -> str:
    words = _clean_name(text)
    return words[:48].rstrip() or "Untitled"


def _clean_name(name: str) -> str:
    cleaned = " ".join(name.split())
    if not cleaned:
        raise ValueError("Name cannot be empty.")

    return cleaned[:80]
