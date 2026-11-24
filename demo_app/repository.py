"""Persistence for users and work items."""

import sqlite3
from datetime import UTC, datetime

from demo_app.db import connection, reset_tables
from demo_app.security import hash_password, verify_password
from demo_app.seed_data import USERS, member_items, pager_items
from demo_app.validation import like_pattern, normalize_email


class DuplicateEmailError(Exception):
    """Raised when an email is already registered."""


def _now() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat()


def public_user(row) -> dict:
    return {
        "id": row["id"],
        "email": row["email"],
        "name": row["name"],
        "role": row["role"],
    }


def public_item(row) -> dict:
    return {
        "id": row["id"],
        "owner_id": row["owner_id"],
        "owner_email": row["owner_email"],
        "title": row["title"],
        "description": row["description"],
        "status": row["status"],
        "priority": row["priority"],
        "created_at": row["created_at"],
    }


_ITEM_SELECT = """
SELECT items.id, items.owner_id, users.email AS owner_email, items.title,
       items.description, items.status, items.priority, items.created_at
FROM items
JOIN users ON users.id = items.owner_id
"""


def seed_if_empty() -> None:
    with connection() as conn:
        count = conn.execute("SELECT COUNT(*) AS total FROM users").fetchone()["total"]
        if count:
            return
        for user in USERS:
            conn.execute(
                """
                INSERT INTO users (email, name, password_hash, role, created_at)
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    user["email"],
                    user["name"],
                    hash_password(user["password"]),
                    user["role"],
                    _now(),
                ),
            )
        owners = {
            row["email"]: row["id"]
            for row in conn.execute("SELECT id, email FROM users").fetchall()
        }
        pager_id = owners["pager@demo.local"]
        member_id = owners["member@demo.local"]
        for item in pager_items():
            _insert_item(conn, pager_id, item)
        for item in member_items():
            _insert_item(conn, member_id, item)


def reset_and_seed() -> None:
    reset_tables()
    seed_if_empty()


def _insert_item(conn, owner_id: int, item: dict) -> int:
    cursor = conn.execute(
        """
        INSERT INTO items (owner_id, title, description, status, priority, created_at)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (
            owner_id,
            item["title"].strip(),
            item["description"],
            item["status"],
            item["priority"],
            _now(),
        ),
    )
    return int(cursor.lastrowid)


def create_user(name: str, email: str, password: str, role: str = "member") -> dict:
    try:
        with connection() as conn:
            cursor = conn.execute(
                """
                INSERT INTO users (email, name, password_hash, role, created_at)
                VALUES (?, ?, ?, ?, ?)
                """,
                (normalize_email(email), name.strip(), hash_password(password), role, _now()),
            )
            row = conn.execute("SELECT * FROM users WHERE id = ?", (cursor.lastrowid,)).fetchone()
            return public_user(row)
    except sqlite3.IntegrityError as exc:
        raise DuplicateEmailError from exc


def authenticate(email: str, password: str) -> dict | None:
    with connection() as conn:
        row = conn.execute(
            "SELECT * FROM users WHERE email = ?",
            (normalize_email(email),),
        ).fetchone()
    if row is None or not verify_password(password, row["password_hash"]):
        return None
    return public_user(row)


def get_user(user_id: int) -> dict | None:
    with connection() as conn:
        row = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
    return public_user(row) if row else None


def update_name(user_id: int, name: str) -> dict | None:
    with connection() as conn:
        conn.execute("UPDATE users SET name = ? WHERE id = ?", (name.strip(), user_id))
        row = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
    return public_user(row) if row else None


def list_users() -> list[dict]:
    with connection() as conn:
        rows = conn.execute("SELECT * FROM users ORDER BY id").fetchall()
    return [public_user(row) for row in rows]


def create_item(owner_id: int, item: dict) -> dict:
    with connection() as conn:
        item_id = _insert_item(conn, owner_id, item)
        row = conn.execute(f"{_ITEM_SELECT} WHERE items.id = ?", (item_id,)).fetchone()
    return public_item(row)


def update_item(item_id: int, item: dict) -> dict | None:
    with connection() as conn:
        conn.execute(
            """
            UPDATE items
            SET title = ?, description = ?, status = ?, priority = ?
            WHERE id = ?
            """,
            (item["title"].strip(), item["description"], item["status"], item["priority"], item_id),
        )
        row = conn.execute(f"{_ITEM_SELECT} WHERE items.id = ?", (item_id,)).fetchone()
    return public_item(row) if row else None


def delete_item(item_id: int) -> bool:
    with connection() as conn:
        cursor = conn.execute("DELETE FROM items WHERE id = ?", (item_id,))
    return cursor.rowcount > 0


def get_item(item_id: int) -> dict | None:
    with connection() as conn:
        row = conn.execute(f"{_ITEM_SELECT} WHERE items.id = ?", (item_id,)).fetchone()
    return public_item(row) if row else None


def search_items(
    *,
    owner_id: int | None,
    term: str,
    status: str,
    priority: str,
    page: int,
    page_size: int,
) -> tuple[list[dict], int]:
    clauses = ["1 = 1"]
    params: list[object] = []
    if owner_id is not None:
        clauses.append("items.owner_id = ?")
        params.append(owner_id)
    if term:
        pattern = like_pattern(term)
        clauses.append("(items.title LIKE ? ESCAPE '\\' OR items.description LIKE ? ESCAPE '\\')")
        params.extend([pattern, pattern])
    if status:
        clauses.append("items.status = ?")
        params.append(status)
    if priority:
        clauses.append("items.priority = ?")
        params.append(priority)
    where = " AND ".join(clauses)
    offset = (page - 1) * page_size
    with connection() as conn:
        count_sql = (
            "SELECT COUNT(*) AS total FROM items "
            "JOIN users ON users.id = items.owner_id "
            f"WHERE {where}"
        )
        total = conn.execute(count_sql, params).fetchone()["total"]
        rows = conn.execute(
            f"""
            {_ITEM_SELECT}
            WHERE {where}
            ORDER BY items.id
            LIMIT ? OFFSET ?
            """,
            [*params, page_size, offset],
        ).fetchall()
    return [public_item(row) for row in rows], int(total)


def status_counts(owner_id: int | None) -> dict[str, int]:
    clause = ""
    params: tuple = ()
    if owner_id is not None:
        clause = "WHERE owner_id = ?"
        params = (owner_id,)
    counts = {"open": 0, "in_progress": 0, "done": 0}
    with connection() as conn:
        rows = conn.execute(
            f"SELECT status, COUNT(*) AS total FROM items {clause} GROUP BY status",
            params,
        ).fetchall()
    for row in rows:
        counts[row["status"]] = int(row["total"])
    return counts
