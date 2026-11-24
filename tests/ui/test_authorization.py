"""Role checks in the browser."""

import pytest
from playwright.sync_api import expect

from demo_app.constants import FORBIDDEN_TEXT
from framework.api_client import ApiClient
from pages.screens import Screens

pytestmark = [pytest.mark.ui, pytest.mark.regression]


def test_member_cannot_open_the_user_directory(screens: Screens, accounts: dict) -> None:
    screens.sign_in(accounts["member"])
    expect(screens.page.get_by_test_id("nav-admin")).to_have_count(0)
    screens.page.goto(f"{screens.base_url}/admin/users", wait_until="domcontentloaded")
    screens.expect_forbidden()
    expect(screens.page.get_by_test_id("forbidden")).to_have_text(FORBIDDEN_TEXT)


def test_admin_can_review_users(screens: Screens, accounts: dict) -> None:
    screens.sign_in(accounts["admin"])
    screens.admin_page().open()
    screens.admin_page().expect_user(accounts["pager"]["email"])
    screens.admin_page().expect_user(accounts["member"]["email"])


def test_member_cannot_edit_another_users_item(
    screens: Screens, accounts: dict, base_url: str
) -> None:
    pager = ApiClient(base_url)
    try:
        pager.login(accounts["pager"]["email"], accounts["pager"]["password"])
        item_id = pager.list_items()["items"][0]["id"]
    finally:
        pager.close()
    screens.sign_in(accounts["member"])
    screens.page.goto(f"{screens.base_url}/items/{item_id}/edit", wait_until="domcontentloaded")
    screens.expect_forbidden()


def test_admin_can_open_another_users_item(screens: Screens, accounts: dict) -> None:
    screens.sign_in(accounts["admin"])
    items = screens.items_page()
    items.open()
    items.apply_filters("Pager Item 01")
    items.open_edit("Pager Item 01")
    screens.item_form_page().expect_title_value("Pager Item 01")


def test_member_search_does_not_reveal_other_owners(screens: Screens, accounts: dict) -> None:
    screens.sign_in(accounts["member"])
    items = screens.items_page()
    items.open()
    items.apply_filters("Pager Item 01")
    items.expect_empty()
    items.apply_filters("Member Seed Note A")
    items.expect_title("Member Seed Note A")
    items.expect_result_count(1)
