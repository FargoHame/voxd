from pydantic import BaseModel


class LoadRuntimeRequest(BaseModel):
    model: str