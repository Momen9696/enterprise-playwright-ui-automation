"""Factory that gives tests page objects sharing one browser page."""

from __future__ import annotations

from playwright.sync_api import Page, expect

from framework.ui import UiActions
from pages.admin_page import AdminPage
from pages.dashboard_page import DashboardPage
from pages.item_form_page import ItemFormPage
from pages.items_page import ItemsPage
from pages.login_page import LoginPage
from pages.profile_page import ProfilePage
from pages.register_page import RegisterPage


class Screens:
    def __init__(self, page: Page, base_url: str, ui: UiActions) -> None:
        self.page = page
        self.base_url = base_url
        self.ui = ui

    def login_page(self) -> LoginPage:
        return LoginPage(self.page, self.base_url, self.ui)

    def register_page(self) -> RegisterPage:
        return RegisterPage(self.page, self.base_url, self.ui)

    def dashboard_page(self) -> DashboardPage:
        return DashboardPage(self.page, self.base_url, self.ui)

    def items_page(self) -> ItemsPage:
        return ItemsPage(self.page, self.base_url, self.ui)

    def item_form_page(self) -> ItemFormPage:
        return ItemFormPage(self.page, self.base_url, self.ui)

    def profile_page(self) -> ProfilePage:
        return ProfilePage(self.page, self.base_url, self.ui)

    def admin_page(self) -> AdminPage:
        return AdminPage(self.page, self.base_url, self.ui)

    def sign_in(self, account: dict) -> DashboardPage:
        login = self.login_page()
        login.open()
        login.sign_in(account["email"], account["password"])
        return self.dashboard_page()

    def expect_notice(self, message: str) -> None:
        expect(self.page.get_by_test_id("notice")).to_have_text(message)

    def expect_forbidden(self) -> None:
        expect(self.page.get_by_test_id("forbidden")).to_be_visible()
