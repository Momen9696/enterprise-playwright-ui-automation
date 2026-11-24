#!/usr/bin/env python3
"""Fail if a tracked-looking file contains a real credential pattern.

Demo passwords in seed data and environment files are fixtures. This scan looks
for private keys and live tokens, not the word "password".
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKIP_DIRS = {
    ".git",
    ".venv",
    ".run",
    "artifacts",
    "reports",
    "logs",
    "__pycache__",
    ".pytest_cache",
    ".ruff_cache",
}
PATTERNS = (
    ("private key", re.compile(r"-----BEGIN (?:RSA |OPENSSH |EC )?PRIVATE KEY-----")),
    ("aws access key", re.compile(r"AKIA[0-9A-Z]{16}")),
    ("github token", re.compile(r"gh[pousr]_[A-Za-z0-9]{20,}")),
    ("slack token", re.compile(r"xox[baprs]-[A-Za-z0-9-]{10,}")),
    (
        "generic api key assignment",
        re.compile(r"(?i)(api[_-]?key|secret[_-]?key)\s*[:=]\s*['\"][A-Za-z0-9_\-]{16,}['\"]"),
    ),
)


def iter_files() -> list[Path]:
    found: list[Path] = []
    for path in ROOT.rglob("*"):
        if not path.is_file():
            continue
        if any(part in SKIP_DIRS for part in path.parts):
            continue
        if path.suffix.lower() in {".png", ".zip", ".webm", ".mp4", ".sqlite", ".pyc"}:
            continue
        found.append(path)
    return found


def main() -> int:
    findings: list[str] = []
    for path in iter_files():
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        for label, pattern in PATTERNS:
            if pattern.search(text):
                findings.append(f"{path.relative_to(ROOT)}: {label}")
    if findings:
        print("Secret scan failed:")
        for finding in findings:
            print(f"  {finding}")
        return 1
    print(f"Secret scan passed ({len(list(iter_files()))} files).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
