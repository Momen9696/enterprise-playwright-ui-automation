"""Pagination of the stable pager list."""

import pytest
from playwright.sync_api import expect

from pages.screens import Screens

pytestmark = [pytest.mark.ui, pytest.mark.regression]


def test_next_and_previous_move_between_pages(screens: Screens, accounts: dict) -> None:
    screens.sign_in(accounts["pager"])
    items = screens.items_page()
    items.open()
    items.expect_page(1, 3)
    items.expect_result_count(12)
    assert items.titles()[0] == "Pager Item 01"
    assert items.titles()[-1] == "Pager Item 05"
    assert screens.page.get_by_test_id("page-prev").evaluate("element => element.tagName") == "SPAN"

    screens.ui.click(screens.page.get_by_test_id("page-next"), "next page")
    items.expect_page(2, 3)
    assert items.titles()[0] == "Pager Item 06"
    assert items.titles()[-1] == "Pager Item 10"

    screens.ui.click(screens.page.get_by_test_id("page-prev"), "previous page")
    items.expect_page(1, 3)
    assert items.titles()[0] == "Pager Item 01"


@pytest.mark.parametrize(
    ("query", "page_number", "empty"),
    [("99", 99, True), ("abc", 1, False), ("0", 1, False)],
)
def test_page_query_edges(
    screens: Screens, accounts: dict, query: str, page_number: int, empty: bool
) -> None:
    screens.sign_in(accounts["pager"])
    screens.page.goto(f"{screens.base_url}/items?page={query}", wait_until="domcontentloaded")
    expect(screens.page.get_by_test_id("items-heading")).to_be_visible()
    screens.items_page().expect_page(page_number, 3)
    if empty:
        expect(screens.page.get_by_test_id("item-row")).to_have_count(0)
        screens.items_page().expect_result_count(12)
    else:
        assert screens.items_page().titles()[0] == "Pager Item 01"
