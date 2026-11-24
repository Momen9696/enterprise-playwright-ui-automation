"""In-memory sessions for the demo application."""

import secrets
import time
from dataclasses import dataclass

COOKIE_NAME = "harbordesk_session"


@dataclass
class SessionRecord:
    csrf: str
    user_id: int | None
    expires_at: float


class SessionStore:
    def __init__(self, ttl_seconds: int) -> None:
        self.ttl_seconds = ttl_seconds
        self._sessions: dict[str, SessionRecord] = {}

    def start(self) -> tuple[str, SessionRecord]:
        session_id = secrets.token_urlsafe(32)
        record = SessionRecord(
            csrf=secrets.token_urlsafe(24),
            user_id=None,
            expires_at=time.time() + self.ttl_seconds,
        )
        self._sessions[session_id] = record
        return session_id, record

    def get(self, session_id: str | None) -> tuple[str | None, SessionRecord | None, bool]:
        """Return id, record, and whether the session had expired."""
        if not session_id or session_id not in self._sessions:
            return None, None, False
        record = self._sessions[session_id]
        if record.expires_at <= time.time():
            self._sessions.pop(session_id, None)
            return None, None, True
        record.expires_at = time.time() + self.ttl_seconds
        return session_id, record, False

    def expire(self, session_id: str | None) -> bool:
        record = self._sessions.get(session_id or "")
        if record is None:
            return False
        record.expires_at = time.time() - 5
        return True

    def destroy(self, session_id: str | None) -> None:
        if session_id:
            self._sessions.pop(session_id, None)

    def clear(self) -> None:
        self._sessions.clear()
