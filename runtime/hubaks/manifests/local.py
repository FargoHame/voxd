from __future__ import annotations

import json
from pathlib import Path

from hubaks.manifests.base import ManifestProvider
from hubaks.models.model_file import ModelFile
from hubaks.models.model_info import ModelInfo
from hubaks.models.model_manifest import ModelManifest


class LocalManifestProvider(ManifestProvider):
    """Reads manifests from a bundled JSON catalog."""

    def __init__(self, catalog_path: Path):
        self._catalog_path = catalog_path

        with catalog_path.open("r", encoding="utf-8") as f:
            self._catalog = json.load(f)

    def available_models(self) -> list[ModelInfo]:
        models = []

        for model in self._catalog["models"]:
            size = sum(file["size_bytes"] for file in model["files"])

            models.append(
                ModelInfo(
                    name=model["name"],
                    engine=model["engine"],
                    description=model["description"],
                    size_bytes=size,
                    version=model["version"],
                    license=model["license"],
                )
            )

        return models

    def get_manifest(self, model_name: str) -> ModelManifest:
        for model in self._catalog["models"]:
            if model["name"] == model_name:
                files = [
                    ModelFile(
                        filename=file["filename"],
                        url=file["url"],
                        sha256=file["sha256"],
                        size_bytes=file["size_bytes"],
                    )
                    for file in model["files"]
                ]

                return ModelManifest(
                    model_name=model["name"],
                    engine=model["engine"],
                    version=model["version"],
                    files=files,
                    total_size=sum(f.size_bytes for f in files),
                    license=model["license"],
                    homepage=model["homepage"],
                    options=model.get("options", {}),
                )

        raise ValueError(f"Unknown model: {model_name}")
