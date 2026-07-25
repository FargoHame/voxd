from pydantic import BaseModel


class LoadRuntimeRequest(BaseModel):
    model: str


class SpeechRequest(BaseModel):
    text: str