"""Registration UI scenarios, including JSON cases and generated users."""

from pathlib import Path

import pytest
from playwright.sync_api import expect

from demo_app.constants import NOTICES
from framework.data_factory import load_cases
from pages.screens import Screens

ROOT = Path(__file__).resolve().parents[2]
CASES = load_cases(ROOT, "registration_cases.json")

pytestmark = [pytest.mark.ui, pytest.mark.regression, pytest.mark.auth]


@pytest.mark.smoke
def test_register_generated_user(screens: Screens, factory) -> None:
    user = factory.user()
    register = screens.register_page()
    register.open()
    register.submit(user["name"], user["email"], user["password"])
    expect(screens.page.get_by_test_id("dashboard-heading")).to_be_visible()
    screens.expect_notice(NOTICES["welcome"])
    screens.dashboard_page().expect_welcome(user["name"])


@pytest.mark.negative
@pytest.mark.parametrize("case", CASES, ids=[case["case"] for case in CASES])
def test_register_rejects_invalid_input(screens: Screens, case: dict) -> None:
    register = screens.register_page()
    register.open()
    register.submit(case["name"], case["email"], case["password"], case["confirm"])
    expect(screens.page.get_by_test_id("register-form")).to_be_visible()
    for field, message in case["errors"].items():
        register.expect_error(field, message)
