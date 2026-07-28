from pydantic import BaseModel


class GenerationRecord(BaseModel):
    id: str
    name: str
    model: str | None
    engine: str | None
    text: str
    filename: str
    media_type: str
    sample_rate: int
    size_bytes: int
    duration_seconds: float | None
    created_at: str


class GenerationListResponse(BaseModel):
    generations: list[GenerationRecord]


class RenameGenerationRequest(BaseModel):
    name: str
