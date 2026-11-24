"""SQLite access for the demo application."""

import sqlite3
import threading
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path

SCHEMA = """
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY,
    email TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL,
    password_hash TEXT NOT NULL,
    role TEXT NOT NULL,
    created_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS items (
    id INTEGER PRIMARY KEY,
    owner_id INTEGER NOT NULL,
    title TEXT NOT NULL,
    description TEXT NOT NULL,
    status TEXT NOT NULL,
    priority TEXT NOT NULL,
    created_at TEXT NOT NULL,
    FOREIGN KEY(owner_id) REFERENCES users(id)
);
CREATE INDEX IF NOT EXISTS idx_items_owner ON items(owner_id);
"""

_lock = threading.RLock()
_db_path: str | None = None


def configure(path: str) -> None:
    global _db_path
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    _db_path = str(target)


def database_path() -> str:
    if not _db_path:
        raise RuntimeError("Database path is not configured.")
    return _db_path


@contextmanager
def connection() -> Iterator[sqlite3.Connection]:
    conn = sqlite3.connect(database_path(), check_same_thread=False)
    conn.row_factory = sqlite3.Row
    try:
        with _lock:
            yield conn
            conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def init_db(path: str) -> None:
    configure(path)
    with connection() as conn:
        conn.executescript(SCHEMA)


def reset_tables() -> None:
    with connection() as conn:
        conn.execute("DELETE FROM items")
        conn.execute("DELETE FROM users")
