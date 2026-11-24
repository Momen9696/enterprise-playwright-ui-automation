"""Authentication UI scenarios."""

from pathlib import Path

import pytest
from playwright.sync_api import expect

from demo_app.constants import NOTICES
from framework.data_factory import load_cases
from pages.screens import Screens

ROOT = Path(__file__).resolve().parents[2]
LOGIN_CASES = load_cases(ROOT, "login_cases.json")

pytestmark = [pytest.mark.ui, pytest.mark.regression, pytest.mark.auth]


@pytest.mark.smoke
def test_admin_can_sign_in(screens: Screens, accounts: dict) -> None:
    dashboard = screens.sign_in(accounts["admin"])
    dashboard.expect_welcome(accounts["admin"]["name"])
    expect(screens.page.get_by_test_id("signed-in-role")).to_have_text("admin")


@pytest.mark.smoke
def test_member_can_sign_in(screens: Screens, accounts: dict) -> None:
    dashboard = screens.sign_in(accounts["member"])
    dashboard.expect_welcome(accounts["member"]["name"])
    expect(screens.page.get_by_test_id("signed-in-role")).to_have_text("member")


@pytest.mark.negative
@pytest.mark.parametrize("case", LOGIN_CASES, ids=[case["case"] for case in LOGIN_CASES])
def test_login_rejects_invalid_input(screens: Screens, case: dict) -> None:
    login = screens.login_page()
    login.open()
    login.sign_in(case["email"], case["password"], expect_success=False)
    for field, message in case["errors"].items():
        login.expect_error(field, message)


def test_logout_ends_the_session(screens: Screens, accounts: dict) -> None:
    dashboard = screens.sign_in(accounts["member"])
    dashboard.logout()
    screens.expect_notice(NOTICES["logged_out"])
    screens.page.goto(f"{screens.base_url}/dashboard", wait_until="domcontentloaded")
    expect(screens.page.get_by_test_id("login-form")).to_be_visible()
    screens.expect_notice(NOTICES["auth_required"])
