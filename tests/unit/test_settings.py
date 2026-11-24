"""Environment loader tests."""

from pathlib import Path

import pytest

from framework.errors import ConfigError
from framework.settings import load_settings

ROOT = Path(__file__).resolve().parents[2]


@pytest.mark.unit
def test_local_profile_matches_the_example() -> None:
    settings = load_settings(ROOT, "local")
    assert settings.browser == "chromium"
    assert settings.headless is True
    assert settings.timeout_ms == 10000
    assert settings.retries == 0
    assert settings.tracing is True
    assert settings.record_video is False
    assert settings.base_url is None


@pytest.mark.unit
def test_staging_profile_uses_a_longer_timeout_and_one_retry() -> None:
    settings = load_settings(ROOT, "staging")
    assert settings.timeout_ms == 12000
    assert settings.navigation_timeout_ms == 20000
    assert settings.retries == 1


@pytest.mark.unit
def test_cli_overrides_win() -> None:
    settings = load_settings(
        ROOT,
        "local",
        {
            "browser": "firefox",
            "headless": False,
            "record_video": True,
            "base_url": "http://127.0.0.1:9",
        },
    )
    assert settings.browser == "firefox"
    assert settings.headless is False
    assert settings.record_video is True
    assert settings.base_url == "http://127.0.0.1:9"


@pytest.mark.unit
def test_unknown_environment_and_browser_are_rejected() -> None:
    with pytest.raises(ConfigError, match="Unknown environment"):
        load_settings(ROOT, "missing")
    with pytest.raises(ConfigError, match="Browser"):
        load_settings(ROOT, "local", {"browser": "opera"})
