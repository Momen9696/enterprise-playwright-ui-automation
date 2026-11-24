"""Create and edit form for a work item."""

from __future__ import annotations

from playwright.sync_api import expect

from pages.base_page import BasePage


class ItemFormPage(BasePage):
    def fill(self, title: str, description: str, status: str, priority: str) -> None:
        self.ui.fill(self.page.get_by_test_id("item-title"), title, "title")
        self.ui.fill(self.page.get_by_test_id("item-description"), description, "description")
        self.ui.select(self.page.get_by_test_id("item-status"), status, "status")
        self.ui.select(self.page.get_by_test_id("item-priority"), priority, "priority")

    def save(self) -> None:
        self.ui.click(self.page.get_by_test_id("save-item"), "save item")

    def save_and_return_to_list(self) -> None:
        self.save()
        self.ui.wait_visible(self.page.get_by_test_id("items-heading"), "items")

    def delete(self) -> None:
        self.ui.click(self.page.get_by_test_id("delete-item"), "delete item")
        self.ui.wait_visible(self.page.get_by_test_id("items-heading"), "items")

    def expect_error(self, field: str, message: str) -> None:
        expect(self.page.get_by_test_id(f"error-{field}")).to_have_text(message)

    def expect_title_value(self, title: str) -> None:
        expect(self.page.get_by_test_id("item-title")).to_have_value(title)
