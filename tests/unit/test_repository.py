"""Repository behavior against a private SQLite file, not the live demo server."""

from pathlib import Path

import pytest

from demo_app import repository
from demo_app.db import init_db
from demo_app.repository import DuplicateEmailError
from demo_app.seed_data import PAGER_ITEM_COUNT


@pytest.fixture
def database(tmp_path: Path) -> None:
    init_db(str(tmp_path / "unit.sqlite"))
    repository.seed_if_empty()


@pytest.mark.unit
def test_seed_creates_stable_accounts_and_items(database: None) -> None:
    users = {user["email"]: user for user in repository.list_users()}
    assert set(users) == {"admin@demo.local", "member@demo.local", "pager@demo.local"}
    assert users["admin@demo.local"]["role"] == "admin"
    pager = users["pager@demo.local"]
    items, total = repository.search_items(
        owner_id=pager["id"],
        term="",
        status="",
        priority="",
        page=1,
        page_size=20,
    )
    assert total == PAGER_ITEM_COUNT
    assert items[0]["title"] == "Pager Item 01"
    assert items[-1]["title"] == "Pager Item 12"


@pytest.mark.unit
def test_duplicate_email_is_rejected(database: None) -> None:
    with pytest.raises(DuplicateEmailError):
        repository.create_user("Other", "admin@demo.local", "Validpass1")


@pytest.mark.unit
def test_search_does_not_treat_percent_as_a_wildcard(database: None) -> None:
    _items, total = repository.search_items(
        owner_id=None,
        term="%",
        status="",
        priority="",
        page=1,
        page_size=20,
    )
    assert total == 0


@pytest.mark.unit
def test_authenticate_rejects_a_wrong_password(database: None) -> None:
    assert repository.authenticate("admin@demo.local", "not-the-password") is None
    user = repository.authenticate("admin@demo.local", "AdminPass123!")
    assert user is not None
    assert "password" not in user
