"""Pure validation used by HTML forms and the JSON API."""

import re

from demo_app.constants import (
    DESCRIPTION_LONG,
    DESCRIPTION_MAX,
    EMAIL_INVALID,
    EMAIL_REQUIRED,
    NAME_LONG,
    NAME_MAX,
    NAME_REQUIRED,
    PASSWORD_MAX,
    PASSWORD_MIN,
    PASSWORD_MISMATCH,
    PASSWORD_REQUIRED,
    PASSWORD_RULE,
    PRIORITIES,
    PRIORITY_INVALID,
    STATUS_INVALID,
    STATUSES,
    TITLE_LONG,
    TITLE_MAX,
    TITLE_REQUIRED,
)

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def normalize_email(value: str) -> str:
    return value.strip().lower()


def validate_email(value: str) -> str | None:
    email = normalize_email(value)
    if not email:
        return EMAIL_REQUIRED
    if not EMAIL_RE.fullmatch(email):
        return EMAIL_INVALID
    return None


def validate_password(value: str) -> str | None:
    if not value:
        return PASSWORD_REQUIRED
    has_letter = re.search(r"[A-Za-z]", value) is not None
    has_digit = re.search(r"\d", value) is not None
    if not (PASSWORD_MIN <= len(value) <= PASSWORD_MAX and has_letter and has_digit):
        return PASSWORD_RULE
    return None


def validate_name(value: str) -> str | None:
    name = value.strip()
    if not name:
        return NAME_REQUIRED
    if len(name) > NAME_MAX:
        return NAME_LONG
    return None


def validate_registration(
    name: str,
    email: str,
    password: str,
    confirm: str | None = None,
    *,
    check_confirm: bool = True,
) -> dict[str, str]:
    errors: dict[str, str] = {}
    name_error = validate_name(name)
    email_error = validate_email(email)
    password_error = validate_password(password)
    if name_error:
        errors["name"] = name_error
    if email_error:
        errors["email"] = email_error
    if password_error:
        errors["password"] = password_error
    if check_confirm and confirm is not None and password and confirm != password:
        errors["confirm"] = PASSWORD_MISMATCH
    return errors


def validate_item(title: str, description: str, status: str, priority: str) -> dict[str, str]:
    errors: dict[str, str] = {}
    cleaned_title = title.strip()
    if not cleaned_title:
        errors["title"] = TITLE_REQUIRED
    elif len(cleaned_title) > TITLE_MAX:
        errors["title"] = TITLE_LONG
    if len(description) > DESCRIPTION_MAX:
        errors["description"] = DESCRIPTION_LONG
    if status not in STATUSES:
        errors["status"] = STATUS_INVALID
    if priority not in PRIORITIES:
        errors["priority"] = PRIORITY_INVALID
    return errors


def parse_page(raw: str | None) -> int:
    """Return a 1-based page. Invalid text and values below 1 become page 1.

    Values above the last page stay as entered so the list can show an empty page.
    """
    if raw is None or raw == "":
        return 1
    try:
        page = int(raw)
    except ValueError:
        return 1
    return 1 if page < 1 else page


def like_pattern(term: str) -> str:
    escaped = term.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
    return f"%{escaped}%"
