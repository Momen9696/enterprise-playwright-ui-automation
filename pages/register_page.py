"""Registration page."""

from __future__ import annotations

from playwright.sync_api import expect

from pages.base_page import BasePage


class RegisterPage(BasePage):
    def open(self) -> None:
        self.open_path("/register", "register-form")

    def submit(self, name: str, email: str, password: str, confirm: str | None = None) -> None:
        self.ui.fill(self.page.get_by_test_id("reg-name"), name, "name")
        self.ui.fill(self.page.get_by_test_id("reg-email"), email, "email")
        self.ui.fill(self.page.get_by_test_id("reg-password"), password, "password", secret=True)
        self.ui.fill(
            self.page.get_by_test_id("reg-confirm"),
            password if confirm is None else confirm,
            "confirm password",
            secret=True,
        )
        self.ui.click(self.page.get_by_test_id("register-submit"), "create account")

    def expect_error(self, field: str, message: str) -> None:
        expect(self.page.get_by_test_id(f"error-{field}")).to_have_text(message)
