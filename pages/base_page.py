"""Shared page behavior."""

from __future__ import annotations

from playwright.sync_api import Page

from framework.ui import UiActions


class BasePage:
    def __init__(self, page: Page, base_url: str, ui: UiActions) -> None:
        self.page = page
        self.base_url = base_url.rstrip("/")
        self.ui = ui

    def open_path(self, path: str, ready: str) -> None:
        self.ui.goto(f"{self.base_url}{path}")
        self.ui.wait_visible(self.page.get_by_test_id(ready), ready)

    def click_nav(self, test_id: str, ready: str) -> None:
        self.ui.click(self.page.get_by_test_id(test_id), test_id)
        self.ui.wait_visible(self.page.get_by_test_id(ready), ready)
