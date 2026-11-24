"""Shared browser interactions with explicit waits."""

from __future__ import annotations

from playwright.sync_api import Locator, Page

from framework.logging_config import describe_value, get_logger
from framework.settings import Settings


class UiActions:
    """Small wrapper around Playwright locators.

    Each action waits until the target is visible, then performs one interaction.
    Callers pass a human-readable name so the log explains the step without
    dumping secret field values.
    """

    def __init__(self, page: Page, settings: Settings) -> None:
        self.page = page
        self.settings = settings
        self.log = get_logger()

    def goto(self, url: str) -> None:
        self.log.info("navigate %s", url)
        self.page.goto(
            url, wait_until="domcontentloaded", timeout=self.settings.navigation_timeout_ms
        )

    def wait_visible(self, locator: Locator, name: str) -> None:
        self.log.info("wait for %s", name)
        locator.first.wait_for(state="visible", timeout=self.settings.timeout_ms)

    def click(self, locator: Locator, name: str) -> None:
        self.log.info("click %s", name)
        locator.wait_for(state="visible", timeout=self.settings.timeout_ms)
        locator.click(timeout=self.settings.timeout_ms)

    def fill(self, locator: Locator, value: str, name: str, *, secret: bool = False) -> None:
        shown = describe_value(value, secret=secret)
        self.log.info("fill %s = %s", name, shown)
        locator.wait_for(state="visible", timeout=self.settings.timeout_ms)
        locator.fill(value, timeout=self.settings.timeout_ms)

    def select(self, locator: Locator, value: str, name: str) -> None:
        self.log.info("select %s = %s", name, value or "(any)")
        locator.wait_for(state="visible", timeout=self.settings.timeout_ms)
        locator.select_option(value, timeout=self.settings.timeout_ms)
