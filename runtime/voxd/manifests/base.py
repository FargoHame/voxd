from __future__ import annotations

from abc import ABC, abstractmethod

from voxd.models.model_info import ModelInfo
from voxd.models.model_manifest import ModelManifest


class ManifestProvider(ABC):
    """Provides model catalogs and installation manifests."""

    @abstractmethod
    def available_models(self) -> list[ModelInfo]:
        """Return all available models."""
        raise NotImplementedError

    @abstractmethod
    def get_manifest(self, model_name: str) -> ModelManifest:
        """Return the installation manifest for a model."""
        raise NotImplementedError