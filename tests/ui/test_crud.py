"""Create, update, and delete work items from the UI and from the API."""

import pytest
from playwright.sync_api import expect

from demo_app.constants import (
    DESCRIPTION_LONG,
    DESCRIPTION_MAX,
    NOTICES,
    TITLE_LONG,
    TITLE_MAX,
    TITLE_REQUIRED,
)
from pages.screens import Screens

pytestmark = [pytest.mark.ui, pytest.mark.regression, pytest.mark.crud]


@pytest.mark.smoke
def test_create_edit_and_delete_item(screens: Screens, accounts: dict, factory) -> None:
    created = factory.item()
    updated = factory.item()
    screens.sign_in(accounts["member"])
    items = screens.items_page()
    items.open()
    items.start_new()
    form = screens.item_form_page()
    form.fill(created["title"], created["description"], "open", "high")
    form.save_and_return_to_list()
    screens.expect_notice(NOTICES["created"])
    items.expect_title(created["title"])

    items.open_edit(created["title"])
    form.fill(updated["title"], "Updated from the form.", "in_progress", "low")
    form.save_and_return_to_list()
    screens.expect_notice(NOTICES["saved"])
    items.expect_title(updated["title"])
    items.expect_absent(created["title"])

    items.open_edit(updated["title"])
    form.delete()
    screens.expect_notice(NOTICES["deleted"])
    items.expect_absent(updated["title"])


def test_api_created_item_is_visible_and_can_be_removed(screens: Screens, api, factory) -> None:
    user = factory.user()
    item = factory.item()
    api.register(user["name"], user["email"], user["password"])
    api.login(user["email"], user["password"])
    created = api.create_item(item["title"], item["description"], "open", "medium")
    screens.sign_in(user)
    items = screens.items_page()
    items.open()
    items.expect_title(item["title"])
    api.delete_item(created["id"])
    screens.page.reload(wait_until="domcontentloaded")
    expect(screens.page.get_by_test_id("items-heading")).to_be_visible()
    items.expect_absent(item["title"])


@pytest.mark.negative
@pytest.mark.parametrize(
    ("title", "description", "message_field", "message"),
    [
        ("", "notes", "title", TITLE_REQUIRED),
        ("   ", "notes", "title", TITLE_REQUIRED),
        ("T" * (TITLE_MAX + 1), "notes", "title", TITLE_LONG),
        ("Boundary title", "D" * (DESCRIPTION_MAX + 1), "description", DESCRIPTION_LONG),
    ],
    ids=["blank-title", "whitespace-title", "title-too-long", "description-too-long"],
)
def test_item_form_rejects_boundaries(
    screens, accounts, title, description, message_field, message
) -> None:
    screens.sign_in(accounts["member"])
    screens.items_page().open()
    screens.items_page().start_new()
    form = screens.item_form_page()
    form.fill(title, description, "open", "medium")
    form.save()
    form.expect_error(message_field, message)
    expect(screens.page.get_by_test_id("item-form")).to_be_visible()


def test_item_form_accepts_max_lengths(screens: Screens, accounts: dict) -> None:
    title = "M" * TITLE_MAX
    screens.sign_in(accounts["member"])
    screens.items_page().open()
    screens.items_page().start_new()
    form = screens.item_form_page()
    form.fill(title, "D" * DESCRIPTION_MAX, "done", "high")
    form.save_and_return_to_list()
    screens.items_page().expect_title(title)
