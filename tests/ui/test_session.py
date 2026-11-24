"""Server-side session expiry."""

import pytest
from playwright.sync_api import expect

from demo_app.constants import NOTICES
from pages.screens import Screens

pytestmark = [pytest.mark.ui, pytest.mark.regression, pytest.mark.auth]


def test_expired_session_returns_to_login(screens: Screens, accounts: dict) -> None:
    screens.sign_in(accounts["member"])
    response = screens.page.request.post(f"{screens.base_url}/api/test/expire-session")
    assert response.ok
    assert response.json()["expired"] is True
    screens.ui.click(screens.page.get_by_test_id("nav-items"), "work items")
    expect(screens.page.get_by_test_id("login-form")).to_be_visible()
    screens.expect_notice(NOTICES["session_expired"])
