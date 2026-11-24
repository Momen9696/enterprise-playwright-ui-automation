"""Browser edge cases that are not covered by the JSON tables."""

import pytest

from pages.screens import Screens

pytestmark = [pytest.mark.ui, pytest.mark.regression, pytest.mark.negative]


def test_markup_in_a_title_is_text_and_does_not_run(screens: Screens, accounts: dict) -> None:
    payload = "<script>alert('xss')</script>"
    dialogs: list[str] = []

    def capture(dialog) -> None:
        dialogs.append(dialog.message)
        dialog.dismiss()

    screens.page.on("dialog", capture)
    screens.sign_in(accounts["member"])
    screens.items_page().open()
    screens.items_page().start_new()
    form = screens.item_form_page()
    form.fill(payload, "Stored as text.", "open", "low")
    form.save_and_return_to_list()
    screens.items_page().expect_title(payload)
    assert dialogs == []
