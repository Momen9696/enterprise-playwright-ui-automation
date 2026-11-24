"""JSON API helper used to arrange and clean up UI scenarios."""

from __future__ import annotations

import httpx


class ApiError(RuntimeError):
    def __init__(self, response: httpx.Response) -> None:
        self.status_code = response.status_code
        self.body = response.text
        detail = f"{response.status_code}: {response.text}"
        super().__init__(f"API {response.request.method} {response.request.url} -> {detail}")


class ApiClient:
    def __init__(self, base_url: str) -> None:
        self.base_url = base_url.rstrip("/")
        self.client = httpx.Client(base_url=self.base_url, timeout=10.0, trust_env=False)

    def close(self) -> None:
        self.client.close()

    def health(self) -> httpx.Response:
        return self.client.get("/api/health")

    def register(self, name: str, email: str, password: str) -> dict:
        response = self.client.post(
            "/api/auth/register",
            json={"name": name, "email": email, "password": password},
        )
        if response.status_code != 201:
            raise ApiError(response)
        return response.json()

    def login(self, email: str, password: str) -> dict:
        response = self.client.post("/api/auth/login", json={"email": email, "password": password})
        if response.status_code != 200:
            raise ApiError(response)
        return response.json()

    def list_items(self, **params: str) -> dict:
        response = self.client.get("/api/items", params=params)
        if response.status_code != 200:
            raise ApiError(response)
        return response.json()

    def create_item(self, title: str, description: str, status: str, priority: str) -> dict:
        response = self.client.post(
            "/api/items",
            json={
                "title": title,
                "description": description,
                "status": status,
                "priority": priority,
            },
        )
        if response.status_code != 201:
            raise ApiError(response)
        return response.json()

    def update_item(self, item_id: int, **fields: str) -> httpx.Response:
        return self.client.put(f"/api/items/{item_id}", json=fields)

    def delete_item(self, item_id: int) -> dict:
        response = self.client.delete(f"/api/items/{item_id}")
        if response.status_code != 200:
            raise ApiError(response)
        return response.json()

    def expire_session(self) -> httpx.Response:
        return self.client.post("/api/test/expire-session")
