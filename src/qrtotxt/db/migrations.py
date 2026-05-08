import sqlite3
from typing import Callable


def _v1(conn: sqlite3.Connection) -> None:
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS settings (
            key   TEXT PRIMARY KEY,
            value TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS generated_qrs (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            content      TEXT    NOT NULL,
            content_type TEXT    NOT NULL,
            file_path    TEXT    NOT NULL DEFAULT '',
            created_at   TEXT    NOT NULL DEFAULT (datetime('now', 'localtime'))
        );

        CREATE TABLE IF NOT EXISTS decoded_qrs (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            source     TEXT NOT NULL,
            content    TEXT NOT NULL,
            created_at TEXT NOT NULL DEFAULT (datetime('now', 'localtime'))
        );
    """)


MIGRATIONS: list[Callable[[sqlite3.Connection], None]] = [
    _v1,
]
