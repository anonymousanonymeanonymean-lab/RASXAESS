"""SQLite database manager.

Phase B: connection + health check only. Schema in Phase C.
"""
from __future__ import annotations

import logging
import sqlite3
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


class Database:
    """SQLite connection manager."""

    def __init__(self, db_path: str) -> None:
        self._path = Path(db_path)
        self._path.parent.mkdir(parents=True, exist_ok=True)
        self._conn: Optional[sqlite3.Connection] = None

    def connect(self) -> sqlite3.Connection:
        if self._conn is None:
            self._conn = sqlite3.connect(str(self._path),
                                         check_same_thread=False)
            self._conn.row_factory = sqlite3.Row
            self._conn.execute("PRAGMA foreign_keys = ON;")
            self._conn.execute("PRAGMA journal_mode = WAL;")
        return self._conn

    def close(self) -> None:
        if self._conn is not None:
            self._conn.close()
            self._conn = None

    def health_check(self) -> bool:
        try:
            conn = self.connect()
            conn.execute("SELECT 1;")
            return True
        except sqlite3.Error as exc:
            logger.error("Database health check failed: %s", exc)
            return False

    @property
    def path(self) -> Path:
        return self._path