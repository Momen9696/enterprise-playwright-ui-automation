"""Intentional failure used only by scripts/capture_failure_evidence.py."""

import pytest
from playwright.sync_api import expect

from pages.screens import Screens

pytestmark = pytest.mark.evidence


def test_failure_artifacts_are_captured(screens: Screens) -> None:
    screens.login_page().open()
    expect(screens.page.get_by_test_id("missing-marker")).to_be_visible(timeout=1000)
