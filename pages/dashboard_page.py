"""Dashboard page."""

from __future__ import annotations

from playwright.sync_api import expect

from pages.base_page import BasePage


class DashboardPage(BasePage):
    def open(self) -> None:
        self.open_path("/dashboard", "dashboard-heading")

    def logout(self) -> None:
        self.ui.click(self.page.get_by_test_id("logout"), "log out")
        self.ui.wait_visible(self.page.get_by_test_id("login-form"), "login form")

    def expect_welcome(self, name: str) -> None:
        expect(self.page.get_by_test_id("welcome-name")).to_have_text(name)

    def expect_count(self, status: str, count: int) -> None:
        expect(self.page.get_by_test_id(f"stat-{status}")).to_have_text(str(count))
