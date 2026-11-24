"""Synthetic data and log masking."""

from framework.data_factory import DataFactory
from framework.logging_config import describe_value


def test_generated_user_meets_the_password_policy() -> None:
    factory = DataFactory()
    first = factory.user()
    second = factory.user()
    assert first["email"] != second["email"]
    assert first["email"].endswith("@demo.local")
    assert any(character.isdigit() for character in first["password"])
    assert any(character.isalpha() for character in first["password"])
    assert len(first["password"]) >= 8
    item = factory.item()
    assert item["title"].startswith("Task ")
    assert item["status"] == "open"


def test_secret_values_are_masked_in_logs() -> None:
    assert describe_value("Validpass1", secret=True) == "***"
    assert describe_value("visible", secret=False) == "visible"
