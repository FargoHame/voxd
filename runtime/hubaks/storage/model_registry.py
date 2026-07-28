from __future__ import annotations

from datetime import datetime
from pathlib import Path

from hubaks.constants.install_status import InstallStatus
from hubaks.models.installed_model import InstalledModel
from hubaks.storage.database import Database


class ModelRegistry:
    """Persistence layer for installed models."""

    def __init__(self, database: Database | None = None):
        self._database = database or Database()
        self._create_tables()

    def _create_tables(self) -> None:
        with self._database.connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS installed_models (
                    model_name TEXT PRIMARY KEY,
                    engine TEXT NOT NULL,
                    version TEXT NOT NULL,
                    install_path TEXT NOT NULL,
                    size_bytes INTEGER NOT NULL,
                    manifest_version TEXT NOT NULL,
                    installed_at TEXT NOT NULL,
                    last_used TEXT,
                    status TEXT NOT NULL
                )
                """
            )

    def add(self, model: InstalledModel) -> None:
        with self._database.connect() as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO installed_models
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    model.model_name,
                    model.engine,
                    model.version,
                    str(model.install_path),
                    model.size_bytes,
                    model.manifest_version,
                    model.installed_at.isoformat(),
                    model.last_used.isoformat() if model.last_used else None,
                    model.status.value,
                ),
            )

    def get(self, model_name: str) -> InstalledModel | None:
        with self._database.connect() as conn:
            row = conn.execute(
                """
                SELECT *
                FROM installed_models
                WHERE model_name = ?
                """,
                (model_name,),
            ).fetchone()

        return self._row_to_model(row) if row else None
    
    def exists(self, model_name: str) -> bool:
        return self.get(model_name) is not None
    
    def list(self) -> list[InstalledModel]:
        with self._database.connect() as conn:
            rows = conn.execute(
                """
                SELECT *
                FROM installed_models
                ORDER BY model_name
                """
            ).fetchall()

        return [self._row_to_model(row) for row in rows]

    def remove(self, model_name: str) -> None:
        with self._database.connect() as conn:
            conn.execute(
                """
                DELETE FROM installed_models
                WHERE model_name = ?
                """,
                (model_name,),
            )

    def update(self, model: InstalledModel) -> None:
        self.add(model)

    @staticmethod
    def _row_to_model(row) -> InstalledModel:
        return InstalledModel(
            model_name=row["model_name"],
            engine=row["engine"],
            version=row["version"],
            install_path=Path(row["install_path"]),
            size_bytes=row["size_bytes"],
            manifest_version=row["manifest_version"],
            installed_at=datetime.fromisoformat(row["installed_at"]),
            last_used=datetime.fromisoformat(row["last_used"])
            if row["last_used"]
            else None,
            status=InstallStatus(row["status"]),
        )