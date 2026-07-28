from pathlib import Path
from datetime import datetime

import pytest

from voxd.constants.install_status import InstallStatus
from voxd.core.settings import settings
from voxd.models.installed_model import InstalledModel
from voxd.models.model_file import ModelFile
from voxd.models.model_manifest import ModelManifest
from voxd.services.model_manager import ModelManager


class FakeEngine:
    def __init__(self, manifest: ModelManifest):
        self.manifest = manifest

    def get_manifest(self, model_name: str) -> ModelManifest:
        return self.manifest


class FakeEngineRegistry:
    def __init__(self, manifest: ModelManifest):
        self.engine = FakeEngine(manifest)

    def get(self, name: str) -> FakeEngine:
        return self.engine

    def list(self) -> list[FakeEngine]:
        return [self.engine]


class FakeModelRegistry:
    def __init__(self):
        self.models = {}

    def exists(self, model_name: str) -> bool:
        return model_name in self.models

    def get(self, model_name: str):
        return self.models.get(model_name)

    def add(self, model):
        self.models[model.model_name] = model

    def list(self):
        return list(self.models.values())

    def remove(self, model_name: str) -> None:
        self.models.pop(model_name, None)

    def update(self, model) -> None:
        self.add(model)


class FakeDownloader:
    def __init__(self, staging_dir: Path, verified: bool = True):
        self.staging_dir = staging_dir
        self.verified = verified

    def prepare_download(self, manifest: ModelManifest) -> Path:
        self.staging_dir.mkdir(parents=True)
        return self.staging_dir

    def download_manifest(self, manifest: ModelManifest, install_dir: Path) -> None:
        (install_dir / "model.bin").write_text("model", encoding="utf-8")

    def verify_manifest(self, manifest: ModelManifest, install_dir: Path) -> bool:
        return self.verified


@pytest.fixture
def manifest():
    return ModelManifest(
        model_name="demo",
        engine="fake",
        version="1.0",
        files=[
            ModelFile(
                filename="model.bin",
                url="https://example.invalid/model.bin",
                sha256="abc",
                size_bytes=5,
            )
        ],
        total_size=5,
        license="MIT",
        homepage="https://example.invalid",
    )


def test_prepare_install_moves_verified_download_to_final_dir(
    tmp_path, monkeypatch, manifest
):
    monkeypatch.setattr(settings, "models_dir", tmp_path / "models")

    registry = FakeModelRegistry()
    manager = ModelManager(
        engine_registry=FakeEngineRegistry(manifest),
        model_registry=registry,
        downloader=FakeDownloader(tmp_path / "cache" / "downloads" / "demo"),
    )

    install_dir = manager.prepare_install("fake", "demo")

    assert install_dir == tmp_path / "models" / "demo"
    assert (install_dir / "model.bin").read_text(encoding="utf-8") == "model"
    assert not (tmp_path / "cache" / "downloads" / "demo").exists()
    assert registry.get("demo").install_path == install_dir


def test_prepare_install_removes_failed_staging_dir(tmp_path, monkeypatch, manifest):
    monkeypatch.setattr(settings, "models_dir", tmp_path / "models")
    staging_dir = tmp_path / "cache" / "downloads" / "demo"

    manager = ModelManager(
        engine_registry=FakeEngineRegistry(manifest),
        model_registry=FakeModelRegistry(),
        downloader=FakeDownloader(staging_dir, verified=False),
    )

    with pytest.raises(ValueError, match="SHA-256"):
        manager.prepare_install("fake", "demo")

    assert not staging_dir.exists()
    assert not (tmp_path / "models" / "demo").exists()


def test_install_resolves_engine_from_catalog(tmp_path, monkeypatch, manifest):
    monkeypatch.setattr(settings, "models_dir", tmp_path / "models")

    registry = FakeModelRegistry()
    manager = ModelManager(
        engine_registry=FakeEngineRegistry(manifest),
        model_registry=registry,
        downloader=FakeDownloader(tmp_path / "cache" / "downloads" / "demo"),
    )

    install_dir = manager.install("demo")

    assert install_dir == tmp_path / "models" / "demo"
    assert registry.get("demo").engine == "fake"


def test_install_reconciles_existing_model_engine(tmp_path, monkeypatch, manifest):
    monkeypatch.setattr(settings, "models_dir", tmp_path / "models")
    install_path = tmp_path / "models" / "demo"

    registry = FakeModelRegistry()
    registry.add(
        InstalledModel(
            model_name="demo",
            engine="old-engine",
            version="old",
            install_path=install_path,
            size_bytes=99,
            manifest_version="old",
            installed_at=datetime.now(),
            last_used=None,
            status=InstallStatus.INSTALLED,
        )
    )
    manager = ModelManager(
        engine_registry=FakeEngineRegistry(manifest),
        model_registry=registry,
        downloader=FakeDownloader(tmp_path / "cache" / "downloads" / "demo"),
    )

    resolved_path = manager.install("demo")

    model = registry.get("demo")
    assert resolved_path == install_path
    assert model.engine == "fake"
    assert model.version == "1.0"
    assert model.size_bytes == 5
