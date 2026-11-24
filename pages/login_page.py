"""Sign-in page."""

from __future__ import annotations

from playwright.sync_api import Locator, expect

from pages.base_page import BasePage


class LoginPage(BasePage):
    def open(self) -> None:
        self.open_path("/login", "login-form")

    def sign_in(self, email: str, password: str, *, expect_success: bool = True) -> None:
        self.ui.fill(self.page.get_by_test_id("login-email"), email, "email")
        self.ui.fill(self.page.get_by_test_id("login-password"), password, "password", secret=True)
        self.ui.click(self.page.get_by_test_id("login-submit"), "sign in")
        if expect_success:
            self.ui.wait_visible(self.page.get_by_test_id("dashboard-heading"), "dashboard")

    def error(self, field: str) -> Locator:
        return self.page.get_by_test_id(f"error-{field}")

    def expect_error(self, field: str, message: str) -> None:
        expect(self.error(field)).to_have_text(message)
