"""Navigation between primary screens."""

import pytest
from playwright.sync_api import expect

from demo_app.constants import NOTICES
from pages.screens import Screens

pytestmark = [pytest.mark.ui, pytest.mark.regression]

PROTECTED = ["/dashboard", "/items", "/items/new", "/profile", "/admin/users"]


@pytest.mark.parametrize("path", PROTECTED)
def test_guest_is_sent_to_login(screens: Screens, path: str) -> None:
    screens.page.goto(f"{screens.base_url}{path}", wait_until="domcontentloaded")
    expect(screens.page.get_by_test_id("login-form")).to_be_visible()
    screens.expect_notice(NOTICES["auth_required"])


def test_primary_navigation(screens: Screens, accounts: dict) -> None:
    screens.sign_in(accounts["member"])
    screens.dashboard_page().click_nav("nav-items", "items-heading")
    screens.dashboard_page().click_nav("nav-profile", "profile-form")
    screens.dashboard_page().click_nav("nav-dashboard", "dashboard-heading")
    screens.dashboard_page().click_nav("brand", "dashboard-heading")
    expect(screens.page.get_by_test_id("nav-admin")).to_have_count(0)


def test_login_and_register_links(screens: Screens) -> None:
    screens.login_page().open()
    screens.ui.click(screens.page.get_by_test_id("link-register"), "create one")
    expect(screens.page.get_by_test_id("register-form")).to_be_visible()
    screens.ui.click(screens.page.get_by_test_id("link-login"), "sign in")
    expect(screens.page.get_by_test_id("login-form")).to_be_visible()
