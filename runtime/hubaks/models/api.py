from pydantic import BaseModel


class PullModelRequest(BaseModel):
    model: str
