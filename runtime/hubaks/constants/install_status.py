from enum import StrEnum


class InstallStatus(StrEnum):
    """Current installation state of a model."""

    DOWNLOADING = "downloading"
    INSTALLED = "installed"
    FAILED = "failed"