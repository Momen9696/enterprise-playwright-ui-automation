"""JSON case loader and synthetic identities for data-driven tests."""

from __future__ import annotations

import json
from pathlib import Path

from faker import Faker


def load_cases(root: Path, name: str) -> list[dict]:
    path = root / "test_data" / name
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, list):
        raise ValueError(f"{path} must be a list of cases.")
    return data


class DataFactory:
    """Builds unique users and items that satisfy HarborDesk validation."""

    def __init__(self) -> None:
        self._faker = Faker("en_US")

    def user(self) -> dict[str, str]:
        suffix = self._faker.uuid4().split("-")[0]
        name = self._faker.name()[:40].strip() or "Test User"
        return {
            "name": name,
            "email": f"user.{suffix}@demo.local",
            "password": f"Validpass1{suffix}",
        }

    def item(self) -> dict[str, str]:
        suffix = self._faker.uuid4().split("-")[0]
        return {
            "title": f"Task {suffix}",
            "description": self._faker.sentence(nb_words=8),
            "status": "open",
            "priority": "high",
        }
