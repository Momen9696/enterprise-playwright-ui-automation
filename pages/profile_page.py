"""Profile page."""

from __future__ import annotations

from playwright.sync_api import expect

from pages.base_page import BasePage


class ProfilePage(BasePage):
    def open(self) -> None:
        self.open_path("/profile", "profile-form")

    def update_name(self, name: str) -> None:
        self.ui.fill(self.page.get_by_test_id("profile-name"), name, "name")
        self.ui.click(self.page.get_by_test_id("save-profile"), "save profile")

    def expect_error(self, field: str, message: str) -> None:
        expect(self.page.get_by_test_id(f"error-{field}")).to_have_text(message)

    def expect_email(self, email: str) -> None:
        expect(self.page.get_by_test_id("profile-email")).to_have_value(email)
