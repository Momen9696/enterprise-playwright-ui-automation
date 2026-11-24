"""Profile updates."""

import pytest

from demo_app.constants import NAME_REQUIRED, NOTICES
from pages.screens import Screens

pytestmark = [pytest.mark.ui, pytest.mark.regression]


def test_user_can_update_display_name(screens: Screens, api, factory) -> None:
    user = factory.user()
    api.register(user["name"], user["email"], user["password"])
    screens.sign_in(user)
    profile = screens.profile_page()
    profile.open()
    profile.expect_email(user["email"])
    profile.update_name("Casey Updated")
    screens.expect_notice(NOTICES["profile_saved"])
    screens.dashboard_page().open()
    screens.dashboard_page().expect_welcome("Casey Updated")


@pytest.mark.negative
def test_blank_profile_name_is_rejected(screens: Screens, api, factory) -> None:
    user = factory.user()
    api.register(user["name"], user["email"], user["password"])
    screens.sign_in(user)
    profile = screens.profile_page()
    profile.open()
    profile.update_name("   ")
    profile.expect_error("name", NAME_REQUIRED)
    screens.dashboard_page().open()
    screens.dashboard_page().expect_welcome(user["name"])
