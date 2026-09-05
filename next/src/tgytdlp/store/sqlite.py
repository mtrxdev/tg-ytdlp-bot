import sqlite3
from pathlib import Path


class Store:
    def __init__(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        self._path = path
        self._conn = sqlite3.connect(path)
        self._conn.execute("PRAGMA journal_mode=WAL")
        self._conn.execute(
            """
            CREATE TABLE IF NOT EXISTS meta (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL
            )
            """
        )
        self._conn.execute(
            """
            CREATE TABLE IF NOT EXISTS jobs (
                id TEXT PRIMARY KEY,
                chat_id INTEGER NOT NULL,
                url TEXT NOT NULL,
                status TEXT NOT NULL,
                path TEXT,
                error TEXT
            )
            """
        )
        self._conn.commit()

    def close(self) -> None:
        self._conn.close()

    def get_offset(self) -> int | None:
        row = self._conn.execute(
            "SELECT value FROM meta WHERE key = ?",
            ("offset",),
        ).fetchone()
        if row is None:
            return None
        return int(row[0])

    def set_offset(self, offset: int) -> None:
        self._conn.execute(
            "INSERT INTO meta(key, value) VALUES(?, ?) "
            "ON CONFLICT(key) DO UPDATE SET value = excluded.value",
            ("offset", str(offset)),
        )
        self._conn.commit()

    def upsert_job(
        self,
        job_id: str,
        chat_id: int,
        url: str,
        status: str,
        path: str | None = None,
        error: str | None = None,
    ) -> None:
        self._conn.execute(
            """
            INSERT INTO jobs(id, chat_id, url, status, path, error)
            VALUES(?, ?, ?, ?, ?, ?)
            ON CONFLICT(id) DO UPDATE SET
                status = excluded.status,
                path = excluded.path,
                error = excluded.error
            """,
            (job_id, chat_id, url, status, path, error),
        )
        self._conn.commit()
