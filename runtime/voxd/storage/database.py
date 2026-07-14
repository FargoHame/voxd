from pathlib import Path
import sqlite3

from voxd.core.settings import settings


class Database:
    """SQLite database connection manager."""

    def __init__(self, path: Path | None = None):
        self._path = path or settings.database_path
        self._path.parent.mkdir(parents=True, exist_ok=True)

    def connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self._path)
        connection.row_factory = sqlite3.Row

        connection.execute("PRAGMA foreign_keys = ON;")
        connection.execute("PRAGMA journal_mode = WAL;")

        return connection