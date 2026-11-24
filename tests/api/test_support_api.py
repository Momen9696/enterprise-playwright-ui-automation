"""JSON API used for setup, cleanup, and authorization checks."""

import pytest

from framework.api_client import ApiClient


@pytest.mark.api
def test_health(api: ApiClient) -> None:
    response = api.health()
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


@pytest.mark.api
def test_items_require_a_session(api: ApiClient) -> None:
    response = api.client.get("/api/items")
    assert response.status_code == 401


@pytest.mark.api
def test_member_list_is_limited_to_owned_items(api: ApiClient, accounts: dict) -> None:
    account = accounts["member"]
    api.login(account["email"], account["password"])
    own = api.list_items(q="Member Seed Note A")
    foreign = api.list_items(q="Pager Item 01")
    assert own["total"] == 1
    assert own["items"][0]["owner_email"] == account["email"]
    assert foreign["total"] == 0


@pytest.mark.api
def test_admin_can_search_another_users_item(api: ApiClient, accounts: dict) -> None:
    account = accounts["admin"]
    api.login(account["email"], account["password"])
    payload = api.list_items(q="Pager Item 01")
    assert payload["total"] == 1
    assert payload["items"][0]["owner_email"] == accounts["pager"]["email"]


@pytest.mark.api
def test_invalid_item_status_is_rejected(api: ApiClient, accounts: dict) -> None:
    account = accounts["member"]
    api.login(account["email"], account["password"])
    response = api.client.post(
        "/api/items",
        json={"title": "Bad status", "description": "", "status": "later", "priority": "low"},
    )
    assert response.status_code == 422
    assert "status" in response.json()["errors"]


@pytest.mark.api
def test_member_cannot_update_a_foreign_item(base_url: str, accounts: dict) -> None:
    pager = ApiClient(base_url)
    member = ApiClient(base_url)
    try:
        pager.login(accounts["pager"]["email"], accounts["pager"]["password"])
        original = pager.list_items()["items"][0]
        member.login(accounts["member"]["email"], accounts["member"]["password"])
        response = member.update_item(
            original["id"],
            title="Taken over",
            description="no",
            status="done",
            priority="high",
        )
        assert response.status_code == 403
        again = pager.list_items(q=original["title"])
        assert again["total"] == 1
        assert again["items"][0]["title"] == original["title"]
    finally:
        pager.close()
        member.close()


@pytest.mark.api
def test_register_rejects_a_weak_password(api: ApiClient) -> None:
    response = api.client.post(
        "/api/auth/register",
        json={"name": "Weak User", "email": "weak@demo.local", "password": "password"},
    )
    assert response.status_code == 422


@pytest.mark.api
def test_expire_session_hook_ends_api_access(api: ApiClient, accounts: dict) -> None:
    account = accounts["member"]
    api.login(account["email"], account["password"])
    expired = api.expire_session()
    assert expired.status_code == 200
    assert expired.json()["expired"] is True
    assert api.client.get("/api/items").status_code == 401
