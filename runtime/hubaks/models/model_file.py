from dataclasses import dataclass


@dataclass(slots=True, frozen=True)
class ModelFile:
    """A single file required for a model."""

    filename: str
    url: str
    sha256: str
    size_bytes: int