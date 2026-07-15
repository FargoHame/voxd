from __future__ import annotations

import hashlib
import shutil
from pathlib import Path

import httpx

from voxd.models.model_file import ModelFile
from voxd.core.settings import settings
from voxd.models.model_manifest import ModelManifest


class Downloader:
    """Downloads model files."""

    def download(
        self,
        model_file: ModelFile,
        destination: Path,
    ) -> Path:
        destination.mkdir(parents=True, exist_ok=True)

        output_path = destination / model_file.filename

        with httpx.stream("GET", model_file.url, follow_redirects=True) as response:
            response.raise_for_status()

            with output_path.open("wb") as f:
                shutil.copyfileobj(response, f)

        return output_path

    def verify(
        self,
        file_path: Path,
        expected_sha256: str,
    ) -> bool:
        sha256 = hashlib.sha256()

        with file_path.open("rb") as f:
            while chunk := f.read(1024 * 1024):
                sha256.update(chunk)

        return sha256.hexdigest() == expected_sha256
    def prepare_download(self, manifest: ModelManifest) -> Path:
        """Create the installation directory for a model."""

        model_dir = settings.models_dir / manifest.model_name
        model_dir.mkdir(parents=True, exist_ok=True)

        return model_dir