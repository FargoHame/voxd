from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from voxd.constants.install_status import InstallStatus


@dataclass(slots=True)
class InstalledModel:
    """Metadata for a model installed on the local machine."""

    model_name: str
    engine: str
    version: str

    install_path: Path

    size_bytes: int

    manifest_version: str

    installed_at: datetime
    last_used: datetime | None

    status: InstallStatus