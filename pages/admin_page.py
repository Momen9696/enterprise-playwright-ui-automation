"""Admin user directory."""

from __future__ import annotations

from playwright.sync_api import expect

from pages.base_page import BasePage


class AdminPage(BasePage):
    def open(self) -> None:
        self.open_path("/admin/users", "admin-heading")

    def expect_user(self, email: str) -> None:
        expect(self.page.get_by_test_id("user-email").filter(has_text=email)).to_be_visible()
