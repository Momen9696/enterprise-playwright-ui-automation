"""Work item list, search, filters, and pagination."""

from __future__ import annotations

import re

from playwright.sync_api import expect

from pages.base_page import BasePage


class ItemsPage(BasePage):
    def open(self) -> None:
        self.open_path("/items", "items-heading")

    def start_new(self) -> None:
        self.ui.click(self.page.get_by_test_id("new-item"), "new item")
        self.ui.wait_visible(self.page.get_by_test_id("item-form"), "item form")

    def apply_filters(self, term: str = "", status: str = "", priority: str = "") -> None:
        self.ui.fill(self.page.get_by_test_id("search-input"), term, "search")
        self.ui.select(self.page.get_by_test_id("status-filter"), status, "status filter")
        self.ui.select(self.page.get_by_test_id("priority-filter"), priority, "priority filter")
        self.ui.click(self.page.get_by_test_id("apply-filters"), "apply filters")
        self.ui.wait_visible(self.page.get_by_test_id("items-heading"), "items")

    def clear_filters(self) -> None:
        self.ui.click(self.page.get_by_test_id("clear-filters"), "clear filters")
        self.ui.wait_visible(self.page.get_by_test_id("items-heading"), "items")

    def expect_result_count(self, total: int) -> None:
        label = "1 item" if total == 1 else f"{total} items"
        expect(self.page.get_by_test_id("result-count")).to_have_text(label)

    def _cells(self, title: str):
        pattern = re.compile(rf"^{re.escape(title)}$")
        return self.page.locator("[data-testid='item-title']", has_text=pattern)

    def expect_title(self, title: str) -> None:
        expect(self._cells(title)).to_have_count(1)

    def expect_absent(self, title: str) -> None:
        expect(self._cells(title)).to_have_count(0)

    def expect_empty(self) -> None:
        self.expect_result_count(0)
        expect(self.page.get_by_test_id("empty-state")).to_be_visible()

    def expect_page(self, page: int, pages: int) -> None:
        expect(self.page.get_by_test_id("page-indicator")).to_have_text(f"Page {page} of {pages}")

    def open_edit(self, title: str) -> None:
        row = self.page.locator("[data-testid='item-row']", has=self._cells(title))
        expect(row).to_have_count(1)
        self.ui.click(row.get_by_test_id("edit-item"), f"edit {title}")
        self.ui.wait_visible(self.page.get_by_test_id("item-form"), "item form")

    def titles(self) -> list[str]:
        return self.page.get_by_test_id("item-title").all_text_contents()
