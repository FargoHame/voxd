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

        actual = sha256.hexdigest()

        return actual.casefold() == expected_sha256.casefold()

    def prepare_download(self, manifest: ModelManifest) -> Path:
        """Create the installation directory for a model."""

        model_dir = settings.models_dir / manifest.model_name
        model_dir.mkdir(parents=True, exist_ok=True)

        return model_dir

    def download_manifest(self, manifest: ModelManifest, install_dir: Path) -> None:
        for file in manifest.files:
            print(f"Downloading: {file.filename}")
            destination = install_dir / file.filename
            self.download_file(file.url, destination)
            print(f"Finished: {file.filename}")

    def download_file(self, url: str, destination: Path) -> None:
        """Download a single file."""

        destination.parent.mkdir(parents=True, exist_ok=True)

        with httpx.stream(
            "GET",
            url,
            follow_redirects=True,
            timeout=None,
        ) as response:
            response.raise_for_status()

            total = int(response.headers.get("Content-Length", 0))
            downloaded = 0

            with destination.open("wb") as file:
                for chunk in response.iter_bytes(chunk_size=1024 * 1024):
                    if not chunk:
                        continue

                    file.write(chunk)
                    downloaded += len(chunk)

                    if total:
                        percent = downloaded * 100 // total
                        print(
                            f"\r{percent}% ({downloaded:,}/{total:,} bytes)",
                            end="",
                            flush=True,
                        )
                    else:
                        print(
                            f"\rDownloaded {downloaded:,} bytes",
                            end="",
                            flush=True,
                        )

            print()

    def verify_manifest(
        self,
        manifest: ModelManifest,
        install_dir: Path,
    ) -> bool:
        """Verify every downloaded file."""

        for model_file in manifest.files:
            file_path = install_dir / model_file.filename

            ok = self.verify(file_path, model_file.sha256)

            print(f"{model_file.filename}: {ok}")

            if not ok:
                return False

        return True
