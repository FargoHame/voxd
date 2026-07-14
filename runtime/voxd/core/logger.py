import logging

from voxd.core.settings import settings


def configure_logging() -> None:
    """Configure application logging."""

    logging.basicConfig(
        level=getattr(logging, settings.log_level.upper()),
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )


logger = logging.getLogger("voxd")