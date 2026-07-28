from hubaks.models.audio import SpeechRequest


from pydantic import BaseModel

__all__ = ["LoadRuntimeRequest", "SpeechRequest"]


class LoadRuntimeRequest(BaseModel):
    model: str
