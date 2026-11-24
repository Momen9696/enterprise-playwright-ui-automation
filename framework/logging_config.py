"""Test log formatting. Field values marked secret are not written."""

from __future__ import annotations

import logging
from pathlib import Path

_CONFIGURED = False


def get_logger() -> logging.Logger:
    global _CONFIGURED
    logger = logging.getLogger("harbordesk.tests")
    if _CONFIGURED:
        return logger
    logger.setLevel(logging.INFO)
    logger.propagate = False
    log_dir = Path(__file__).resolve().parents[1] / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    formatter = logging.Formatter("%(asctime)s %(levelname)s %(message)s")
    file_handler = logging.FileHandler(log_dir / "framework.log", encoding="utf-8")
    file_handler.setFormatter(formatter)
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)
    _CONFIGURED = True
    return logger


def describe_value(value: str, *, secret: bool) -> str:
    if secret:
        return "***"
    collapsed = value.replace("\n", "\\n")
    if len(collapsed) > 120:
        return collapsed[:117] + "..."
    return collapsed
