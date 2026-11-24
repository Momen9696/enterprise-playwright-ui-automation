"""Dashboard counts for the stable pager account."""

import pytest
from playwright.sync_api import expect

from pages.screens import Screens

pytestmark = [pytest.mark.ui, pytest.mark.regression]


def test_pager_dashboard_counts(screens: Screens, accounts: dict) -> None:
    dashboard = screens.sign_in(accounts["pager"])
    dashboard.expect_count("open", 4)
    dashboard.expect_count("in-progress", 4)
    dashboard.expect_count("done", 4)
    expect(screens.page.get_by_test_id("recent-item").first).to_have_text("Pager Item 01")
