"""
RAM-cached SQLite layer.

All reads are served from in-memory cache (loaded at startup).
All writes are synchronous to the cache and dispatched to SQLite
in a background thread so the UI never blocks on disk I/O.
"""

import sqlite3
import threading
from pathlib import Path

from .migrations import MIGRATIONS

_DATA_DIR = Path.home() / ".local" / "share" / "QRtoTXT"
_DB_PATH  = _DATA_DIR / "app.db"


class _Cache:
    __slots__ = ("settings", "generated_qrs", "decoded_qrs")

    def __init__(self) -> None:
        self.settings:      dict[str, str] = {}
        self.generated_qrs: list[dict]     = []
        self.decoded_qrs:   list[dict]     = []


class AppDB:
    """Singleton database with an in-memory cache."""

    _instance: "AppDB | None" = None

    def __init__(self, path: Path = _DB_PATH) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        self._conn = sqlite3.connect(str(path), check_same_thread=False)
        self._conn.row_factory = sqlite3.Row
        self._lock  = threading.Lock()
        self._cache = _Cache()
        self._apply_migrations()
        self._load()

    # ── Singleton ─────────────────────────────────────────────────────────────

    @classmethod
    def instance(cls) -> "AppDB":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    # ── Migrations ────────────────────────────────────────────────────────────

    def _apply_migrations(self) -> None:
        with self._lock:
            self._conn.execute(
                "CREATE TABLE IF NOT EXISTS schema_version (version INTEGER NOT NULL)"
            )
            row = self._conn.execute(
                "SELECT MAX(version) FROM schema_version"
            ).fetchone()
            current: int = row[0] or 0
            for i, fn in enumerate(MIGRATIONS, start=1):
                if i > current:
                    fn(self._conn)
                    self._conn.execute(
                        "INSERT INTO schema_version VALUES (?)", (i,)
                    )
            self._conn.commit()

    # ── Cache load ────────────────────────────────────────────────────────────

    def _load(self) -> None:
        with self._lock:
            self._cache.settings = {
                r["key"]: r["value"]
                for r in self._conn.execute("SELECT key, value FROM settings")
            }
            self._cache.generated_qrs = [
                dict(r) for r in self._conn.execute(
                    "SELECT * FROM generated_qrs ORDER BY created_at DESC"
                )
            ]
            self._cache.decoded_qrs = [
                dict(r) for r in self._conn.execute(
                    "SELECT * FROM decoded_qrs ORDER BY created_at DESC"
                )
            ]

    # ── Settings ──────────────────────────────────────────────────────────────

    def get(self, key: str, default: str = "") -> str:
        return self._cache.settings.get(key, default)

    def set(self, key: str, value: str) -> None:
        self._cache.settings[key] = value
        threading.Thread(target=self._db_set, args=(key, value), daemon=True).start()

    def _db_set(self, key: str, value: str) -> None:
        with self._lock:
            self._conn.execute(
                "INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)",
                (key, value),
            )
            self._conn.commit()

    # ── Generated QRs ─────────────────────────────────────────────────────────

    def add_generated(self, content: str, content_type: str, file_path: str) -> dict:
        entry: dict = {
            "content": content,
            "content_type": content_type,
            "file_path": file_path,
        }
        self._cache.generated_qrs.insert(0, entry)
        threading.Thread(
            target=self._db_add_generated,
            args=(content, content_type, file_path, entry),
            daemon=True,
        ).start()
        return entry

    def _db_add_generated(
        self, content: str, content_type: str, file_path: str, entry: dict
    ) -> None:
        with self._lock:
            cur = self._conn.execute(
                "INSERT INTO generated_qrs (content, content_type, file_path)"
                " VALUES (?, ?, ?)",
                (content, content_type, file_path),
            )
            self._conn.commit()
            row = self._conn.execute(
                "SELECT * FROM generated_qrs WHERE id = ?", (cur.lastrowid,)
            ).fetchone()
            if row:
                entry.update(dict(row))

    def get_generated(self) -> list[dict]:
        return list(self._cache.generated_qrs)

    # ── Decoded QRs ───────────────────────────────────────────────────────────

    def add_decoded(self, source: str, content: str) -> dict:
        entry: dict = {"source": source, "content": content}
        self._cache.decoded_qrs.insert(0, entry)
        threading.Thread(
            target=self._db_add_decoded,
            args=(source, content, entry),
            daemon=True,
        ).start()
        return entry

    def _db_add_decoded(self, source: str, content: str, entry: dict) -> None:
        with self._lock:
            cur = self._conn.execute(
                "INSERT INTO decoded_qrs (source, content) VALUES (?, ?)",
                (source, content),
            )
            self._conn.commit()
            row = self._conn.execute(
                "SELECT * FROM decoded_qrs WHERE id = ?", (cur.lastrowid,)
            ).fetchone()
            if row:
                entry.update(dict(row))

    def get_decoded(self) -> list[dict]:
        return list(self._cache.decoded_qrs)
