"""Environment profiles and command-line overrides."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

import yaml

from framework.errors import ConfigError

BROWSERS = ("chromium", "firefox", "webkit")


@dataclass(frozen=True)
class Settings:
    env_name: str
    timeout_ms: int
    navigation_timeout_ms: int
    headless: bool
    browser: str
    retries: int
    record_video: bool
    tracing: bool
    base_url: str | None


def _as_bool(value: object, field: str) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, str) and value.lower() in {"1", "true", "yes", "0", "false", "no"}:
        return value.lower() in {"1", "true", "yes"}
    raise ConfigError(f"{field} must be true or false.")


def _env_bool(name: str) -> bool | None:
    raw = os.environ.get(name)
    if raw is None or raw == "":
        return None
    return _as_bool(raw, name)


def load_settings(root: Path, env_name: str, overrides: dict | None = None) -> Settings:
    """Load config/environments/<env>.yaml and apply overrides.

    Precedence is file, then environment variables, then explicit overrides.
    """
    path = root / "config" / "environments" / f"{env_name}.yaml"
    if not path.is_file():
        known = (
            sorted(item.stem for item in path.parent.glob("*.yaml")) if path.parent.is_dir() else []
        )
        raise ConfigError(
            f"Unknown environment '{env_name}'. Available: {', '.join(known) or 'none'}."
        )
    loaded = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    if not isinstance(loaded, dict):
        raise ConfigError(f"{path} must contain a mapping.")

    overrides = overrides or {}
    browser = str(
        overrides.get("browser") or os.environ.get("BROWSER") or loaded.get("browser") or "chromium"
    )
    if browser not in BROWSERS:
        raise ConfigError(f"Browser must be one of {', '.join(BROWSERS)}. Got '{browser}'.")

    headless = _as_bool(loaded.get("headless", True), "headless")
    env_headless = _env_bool("HEADLESS")
    if env_headless is not None:
        headless = env_headless
    if "headless" in overrides:
        headless = _as_bool(overrides["headless"], "headless")

    record_video = _as_bool(loaded.get("record_video", False), "record_video")
    env_video = _env_bool("RECORD_VIDEO")
    if env_video is not None:
        record_video = env_video
    if "record_video" in overrides:
        record_video = _as_bool(overrides["record_video"], "record_video")

    tracing = _as_bool(loaded.get("tracing", True), "tracing")
    env_tracing = _env_bool("TRACING")
    if env_tracing is not None:
        tracing = env_tracing
    if "tracing" in overrides:
        tracing = _as_bool(overrides["tracing"], "tracing")

    base_url = overrides.get("base_url", loaded.get("base_url"))
    if base_url is not None:
        base_url = str(base_url).rstrip("/") or None

    try:
        timeout_ms = int(loaded["timeout_ms"])
        navigation_timeout_ms = int(loaded["navigation_timeout_ms"])
        retries = int(loaded.get("retries", 0))
    except (KeyError, TypeError, ValueError) as exc:
        raise ConfigError(
            "timeout_ms, navigation_timeout_ms, and retries must be integers."
        ) from exc

    return Settings(
        env_name=env_name,
        timeout_ms=timeout_ms,
        navigation_timeout_ms=navigation_timeout_ms,
        headless=headless,
        browser=browser,
        retries=retries,
        record_video=record_video,
        tracing=tracing,
        base_url=base_url,
    )
