"""Search and filter scenarios driven by JSON cases."""

from pathlib import Path

import pytest

from framework.data_factory import load_cases
from pages.screens import Screens

ROOT = Path(__file__).resolve().parents[2]
CASES = load_cases(ROOT, "search_cases.json")

pytestmark = [pytest.mark.ui, pytest.mark.regression]


@pytest.mark.parametrize("case", CASES, ids=[case["case"] for case in CASES])
def test_search_and_filters(screens: Screens, accounts: dict, case: dict) -> None:
    screens.sign_in(accounts["pager"])
    items = screens.items_page()
    items.open()
    items.apply_filters(case["q"], case["status"], case["priority"])
    items.expect_result_count(case["count"])
    if case["count"] == 0:
        items.expect_empty()
    if case["q"] == "Pager Item 01":
        items.expect_title("Pager Item 01")


def test_clear_filters_restores_the_full_list(screens: Screens, accounts: dict) -> None:
    screens.sign_in(accounts["pager"])
    items = screens.items_page()
    items.open()
    items.apply_filters("no-such-item-xyz")
    items.expect_empty()
    items.clear_filters()
    items.expect_result_count(12)
    items.expect_title("Pager Item 01")
