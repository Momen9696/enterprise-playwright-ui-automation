"""Pytest fixtures for browsers, the demo app, and failure artifacts."""

from __future__ import annotations

import re
from pathlib import Path

import pytest
from playwright.sync_api import sync_playwright

from demo_app.seed_data import USERS
from framework.api_client import ApiClient
from framework.data_factory import DataFactory
from framework.logging_config import get_logger
from framework.settings import Settings, load_settings
from framework.ui import UiActions
from pages.screens import Screens
from tests.support import app_server

ROOT = Path(__file__).resolve().parents[1]
SETTINGS: Settings | None = None


def pytest_addoption(parser: pytest.Parser) -> None:
    parser.addoption("--env", action="store", default="local", help="Environment profile name.")
    parser.addoption(
        "--browser",
        action="store",
        default=None,
        help="Browser to launch: chromium, firefox, or webkit.",
    )
    parser.addoption(
        "--headed", action="store_true", default=False, help="Show the browser window."
    )
    parser.addoption(
        "--base-url", action="store", default=None, help="Use an already running demo app."
    )
    parser.addoption(
        "--record-video", action="store_true", default=False, help="Keep video when a test fails."
    )


def _is_worker(config: pytest.Config) -> bool:
    return hasattr(config, "workerinput")


def pytest_configure(config: pytest.Config) -> None:
    global SETTINGS
    overrides: dict = {}
    browser = config.getoption("--browser")
    if browser:
        overrides["browser"] = browser
    if config.getoption("--headed"):
        overrides["headless"] = False
    if config.getoption("--record-video"):
        overrides["record_video"] = True
    base_url = config.getoption("--base-url")
    if base_url:
        overrides["base_url"] = base_url
    SETTINGS = load_settings(ROOT, config.getoption("--env"), overrides)
    (ROOT / "reports").mkdir(exist_ok=True)
    (ROOT / "artifacts").mkdir(exist_ok=True)
    if SETTINGS.retries and not getattr(config.option, "reruns", 0):
        config.option.reruns = SETTINGS.retries
    if not _is_worker(config) and not base_url:
        app_server.start_demo_app()


def pytest_unconfigure(config: pytest.Config) -> None:
    if not _is_worker(config) and not config.getoption("--base-url"):
        app_server.stop_demo_app()


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item: pytest.Item, call: pytest.CallInfo):
    outcome = yield
    report = outcome.get_result()
    setattr(item, f"rep_{report.when}", report)


def _failed(request: pytest.FixtureRequest) -> bool:
    return any(
        getattr(getattr(request.node, f"rep_{phase}", None), "failed", False)
        for phase in ("setup", "call")
    )


def _safe(nodeid: str) -> str:
    return re.sub(r"[^A-Za-z0-9_.-]+", "_", nodeid)[-140:]


def _attach(path: Path, name: str) -> None:
    try:
        import allure
    except ImportError:
        return
    suffix = path.suffix.lower()
    if suffix == ".png":
        allure.attach.file(str(path), name=name, attachment_type=allure.attachment_type.PNG)
    else:
        allure.attach.file(str(path), name=name, extension=suffix.lstrip("."))


@pytest.fixture(scope="session")
def settings() -> Settings:
    if SETTINGS is None:
        raise RuntimeError("Settings were not loaded.")
    return SETTINGS


@pytest.fixture(scope="session")
def base_url(pytestconfig: pytest.Config) -> str:
    configured = pytestconfig.getoption("--base-url")
    if configured:
        return str(configured).rstrip("/")
    return app_server.read_base_url()


@pytest.fixture(scope="session")
def accounts() -> dict[str, dict]:
    return {user["key"]: user for user in USERS}


@pytest.fixture
def factory() -> DataFactory:
    return DataFactory()


@pytest.fixture
def api(base_url: str):
    client = ApiClient(base_url)
    yield client
    client.close()


@pytest.fixture(scope="session")
def playwright():
    with sync_playwright() as manager:
        yield manager


@pytest.fixture(scope="session")
def browser(playwright, settings: Settings):
    launcher = getattr(playwright, settings.browser)
    launch_args: dict = {"headless": settings.headless}
    if settings.browser == "chromium":
        launch_args["args"] = ["--disable-dev-shm-usage"]
    instance = launcher.launch(**launch_args)
    yield instance
    instance.close()


@pytest.fixture
def context(browser, settings: Settings, request: pytest.FixtureRequest):
    name = _safe(request.node.nodeid)
    video_dir = ROOT / "artifacts" / "videos" / name
    options: dict = {"viewport": {"width": 1440, "height": 900}}
    if settings.record_video:
        video_dir.mkdir(parents=True, exist_ok=True)
        options["record_video_dir"] = str(video_dir)
        options["record_video_size"] = {"width": 1440, "height": 900}
    browser_context = browser.new_context(**options)
    if settings.tracing:
        browser_context.tracing.start(screenshots=True, snapshots=True, sources=False)
    yield browser_context
    failed = _failed(request)
    if settings.tracing:
        if failed:
            trace = ROOT / "artifacts" / "traces" / f"{name}.zip"
            trace.parent.mkdir(parents=True, exist_ok=True)
            browser_context.tracing.stop(path=str(trace))
            _attach(trace, "trace")
        else:
            browser_context.tracing.stop()
    browser_context.close()
    if settings.record_video and video_dir.exists():
        videos = list(video_dir.glob("*.webm")) + list(video_dir.glob("*.mp4"))
        if failed:
            for video in videos:
                _attach(video, "video")
        else:
            for video in videos:
                video.unlink(missing_ok=True)
            video_dir.rmdir()


@pytest.fixture
def page(context, settings: Settings, request: pytest.FixtureRequest):
    browser_page = context.new_page()
    browser_page.set_default_timeout(settings.timeout_ms)
    browser_page.set_default_navigation_timeout(settings.navigation_timeout_ms)
    yield browser_page
    if _failed(request):
        shot = ROOT / "artifacts" / "screenshots" / f"{_safe(request.node.nodeid)}.png"
        shot.parent.mkdir(parents=True, exist_ok=True)
        try:
            browser_page.screenshot(path=str(shot), full_page=True)
            _attach(shot, "screenshot")
        except Exception as exc:
            get_logger().warning("Could not capture a screenshot: %s", exc)
    browser_page.close()


@pytest.fixture
def screens(page, base_url: str, settings: Settings) -> Screens:
    return Screens(page, base_url, UiActions(page, settings))


@pytest.fixture(autouse=True)
def log_test(request: pytest.FixtureRequest):
    logger = get_logger()
    logger.info("START %s", request.node.nodeid)
    yield
    logger.info("END %s", request.node.nodeid)
