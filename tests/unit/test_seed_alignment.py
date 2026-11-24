"""Keep the published demo accounts aligned with the environment files."""

from pathlib import Path

import pytest
import yaml

from demo_app.seed_data import USERS

ROOT = Path(__file__).resolve().parents[2]


@pytest.mark.unit
@pytest.mark.parametrize("env_name", ["local", "staging"])
def test_environment_users_match_the_seed(env_name: str) -> None:
    path = ROOT / "config" / "environments" / f"{env_name}.yaml"
    loaded = yaml.safe_load(path.read_text(encoding="utf-8"))
    expected = {
        user["key"]: {
            "email": user["email"],
            "password": user["password"],
            "role": user["role"],
        }
        for user in USERS
    }
    assert loaded["users"] == expected
