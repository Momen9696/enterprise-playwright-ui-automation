"""Validator and parser unit tests."""

import pytest

from demo_app.constants import (
    DESCRIPTION_LONG,
    DESCRIPTION_MAX,
    EMAIL_INVALID,
    EMAIL_REQUIRED,
    NAME_LONG,
    NAME_MAX,
    NAME_REQUIRED,
    PASSWORD_MISMATCH,
    PASSWORD_RULE,
    TITLE_LONG,
    TITLE_MAX,
    TITLE_REQUIRED,
)
from demo_app.validation import (
    like_pattern,
    normalize_email,
    parse_page,
    validate_item,
    validate_registration,
)


@pytest.mark.unit
def test_email_is_trimmed_and_lowercased() -> None:
    assert normalize_email("  Admin@Demo.local ") == "admin@demo.local"


@pytest.mark.unit
@pytest.mark.parametrize(
    ("name", "email", "password", "confirm", "field", "message"),
    [
        ("", "user@demo.local", "Validpass1", "Validpass1", "name", NAME_REQUIRED),
        ("A" * (NAME_MAX + 1), "user@demo.local", "Validpass1", "Validpass1", "name", NAME_LONG),
        ("User", "", "Validpass1", "Validpass1", "email", EMAIL_REQUIRED),
        ("User", "bad", "Validpass1", "Validpass1", "email", EMAIL_INVALID),
        ("User", "user@demo.local", "short1", "short1", "password", PASSWORD_RULE),
        ("User", "user@demo.local", "Validpass1", "Validpass2", "confirm", PASSWORD_MISMATCH),
    ],
    ids=[
        "blank-name",
        "long-name",
        "blank-email",
        "invalid-email",
        "short-password",
        "password-mismatch",
    ],
)
def test_registration_rules(name, email, password, confirm, field, message) -> None:
    errors = validate_registration(name, email, password, confirm)
    assert errors[field] == message


@pytest.mark.unit
def test_registration_api_can_skip_confirmation() -> None:
    errors = validate_registration("User", "user@demo.local", "Validpass1", check_confirm=False)
    assert errors == {}


@pytest.mark.unit
@pytest.mark.parametrize(
    ("title", "description", "status", "priority", "field", "message"),
    [
        ("", "notes", "open", "low", "title", TITLE_REQUIRED),
        ("   ", "notes", "open", "low", "title", TITLE_REQUIRED),
        ("T" * (TITLE_MAX + 1), "notes", "open", "low", "title", TITLE_LONG),
        ("Title", "D" * (DESCRIPTION_MAX + 1), "open", "low", "description", DESCRIPTION_LONG),
        ("Title", "notes", "later", "low", "status", "Choose a valid status."),
        ("Title", "notes", "open", "urgent", "priority", "Choose a valid priority."),
    ],
    ids=[
        "blank-title",
        "whitespace-title",
        "long-title",
        "long-description",
        "bad-status",
        "bad-priority",
    ],
)
def test_item_rules(title, description, status, priority, field, message) -> None:
    errors = validate_item(title, description, status, priority)
    assert errors[field] == message


@pytest.mark.unit
def test_item_at_max_lengths_is_valid() -> None:
    assert validate_item("T" * TITLE_MAX, "D" * DESCRIPTION_MAX, "done", "high") == {}


@pytest.mark.unit
@pytest.mark.parametrize(
    ("raw", "expected"),
    [("1", 1), (None, 1), ("", 1), ("0", 1), ("-4", 1), ("abc", 1), ("99", 99)],
)
def test_parse_page(raw, expected) -> None:
    assert parse_page(raw) == expected


@pytest.mark.unit
def test_like_pattern_escapes_wildcards() -> None:
    assert like_pattern(r"100%_done") == r"%100\%\_done%"
