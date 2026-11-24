"""Application services shared by HTML and JSON routes."""

from demo_app import repository
from demo_app.constants import CREDENTIALS, EMAIL_REQUIRED, EMAIL_TAKEN, PASSWORD_REQUIRED
from demo_app.repository import DuplicateEmailError
from demo_app.validation import validate_item, validate_name, validate_registration


def register_account(
    name: str,
    email: str,
    password: str,
    confirm: str | None = None,
    *,
    check_confirm: bool = True,
) -> tuple[dict[str, str], dict | None]:
    errors = validate_registration(name, email, password, confirm, check_confirm=check_confirm)
    if errors:
        return errors, None
    try:
        user = repository.create_user(name, email, password)
    except DuplicateEmailError:
        return {"email": EMAIL_TAKEN}, None
    return {}, user


def login_account(email: str, password: str) -> tuple[dict[str, str], dict | None]:
    errors: dict[str, str] = {}
    if not email.strip():
        errors["email"] = EMAIL_REQUIRED
    if not password:
        errors["password"] = PASSWORD_REQUIRED
    if errors:
        return errors, None
    user = repository.authenticate(email, password)
    if user is None:
        return {"form": CREDENTIALS}, None
    return {}, user


def update_profile(user_id: int, name: str) -> tuple[dict[str, str], dict | None]:
    error = validate_name(name)
    if error:
        return {"name": error}, None
    return {}, repository.update_name(user_id, name)


def save_item(
    owner_id: int, fields: dict, item_id: int | None = None
) -> tuple[dict[str, str], dict | None]:
    errors = validate_item(
        fields.get("title", ""),
        fields.get("description", ""),
        fields.get("status", ""),
        fields.get("priority", ""),
    )
    if errors:
        return errors, None
    if item_id is None:
        return {}, repository.create_item(owner_id, fields)
    return {}, repository.update_item(item_id, fields)
