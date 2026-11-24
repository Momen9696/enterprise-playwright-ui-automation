"""Start and stop the local HarborDesk process for a pytest session."""

from __future__ import annotations

import json
import os
import signal
import socket
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RUN_DIR = ROOT / ".run"
STATE_FILE = RUN_DIR / "demo_server.json"

_process: subprocess.Popen | None = None
_log_handle = None


def _free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])


def _healthy(url: str) -> bool:
    try:
        with urllib.request.urlopen(url, timeout=0.5) as response:
            return response.status == 200
    except (urllib.error.URLError, TimeoutError, ConnectionError):
        return False


def start_demo_app() -> str:
    """Launch uvicorn and return the base URL. Safe to call once per session."""
    global _process, _log_handle
    if _process is not None and _process.poll() is None and STATE_FILE.exists():
        payload = json.loads(STATE_FILE.read_text(encoding="utf-8"))
        return f"http://127.0.0.1:{payload['port']}"

    RUN_DIR.mkdir(parents=True, exist_ok=True)
    port = _free_port()
    db_path = RUN_DIR / "harbordesk.sqlite"
    db_path.unlink(missing_ok=True)
    log_path = RUN_DIR / "uvicorn.log"
    _log_handle = log_path.open("w", encoding="utf-8")
    env = os.environ.copy()
    env["DEMO_DB_PATH"] = str(db_path)
    env["DEMO_ALLOW_TEST_HOOKS"] = "true"
    env["DEMO_SESSION_SECONDS"] = "3600"
    env["PYTHONUNBUFFERED"] = "1"
    _process = subprocess.Popen(
        [
            sys.executable,
            "-m",
            "uvicorn",
            "demo_app.main:app",
            "--host",
            "127.0.0.1",
            "--port",
            str(port),
            "--log-level",
            "warning",
        ],
        cwd=ROOT,
        env=env,
        stdout=_log_handle,
        stderr=subprocess.STDOUT,
        start_new_session=True,
    )
    health = f"http://127.0.0.1:{port}/api/health"
    deadline = time.time() + 20
    while time.time() < deadline:
        if _process.poll() is not None:
            break
        if _healthy(health):
            STATE_FILE.write_text(
                json.dumps({"port": port, "pid": _process.pid}),
                encoding="utf-8",
            )
            return f"http://127.0.0.1:{port}"
        time.sleep(0.15)
    stop_demo_app()
    details = log_path.read_text(encoding="utf-8")[-4000:] if log_path.exists() else ""
    raise RuntimeError(f"HarborDesk did not become healthy.\n{details}")


def read_base_url() -> str:
    deadline = time.time() + 20
    while time.time() < deadline:
        if STATE_FILE.exists():
            payload = json.loads(STATE_FILE.read_text(encoding="utf-8"))
            return f"http://127.0.0.1:{payload['port']}"
        time.sleep(0.1)
    raise RuntimeError("Demo server details were not published. The app process did not start.")


def stop_demo_app() -> None:
    global _process, _log_handle
    if _process is not None and _process.poll() is None:
        os.killpg(_process.pid, signal.SIGTERM)
        try:
            _process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            os.killpg(_process.pid, signal.SIGKILL)
            _process.wait(timeout=5)
    _process = None
    if _log_handle is not None:
        _log_handle.close()
        _log_handle = None
    STATE_FILE.unlink(missing_ok=True)
