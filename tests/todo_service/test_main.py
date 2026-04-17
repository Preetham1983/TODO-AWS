from __future__ import annotations

from fastapi import APIRouter
from fastapi.testclient import TestClient


class FakeSettings:
    log_level = "INFO"
    cors_origins = ["http://localhost:3000"]
    host = "127.0.0.1"
    port = 8001


def test_create_application_exposes_health_and_runs_startup(monkeypatch) -> None:
    from tests.pathing import import_service_main

    todo_main = import_service_main("todo_service")
    calls: list[str] = []

    class FakeRepository:
        def __init__(self, settings) -> None:
            self.settings = settings

        async def ensure_table_exists(self) -> None:
            calls.append("ensure_table_exists")

    class FakeUseCases:
        def __init__(self, repository) -> None:
            self.repository = repository

    class FakeController:
        def __init__(self, use_cases) -> None:
            self.use_cases = use_cases
            self.router = APIRouter()

            @self.router.get("/internal-test")
            async def internal_test() -> dict[str, str]:
                return {"result": "ok"}

    monkeypatch.setattr(todo_main, "TodoServiceSettings", FakeSettings)
    monkeypatch.setattr(todo_main, "DynamoDbTodoRepository", FakeRepository)
    monkeypatch.setattr(todo_main, "TodoUseCases", FakeUseCases)
    monkeypatch.setattr(todo_main, "TodoController", FakeController)

    app = todo_main.create_application()

    with TestClient(app) as client:
        health_response = client.get("/health")
        internal_response = client.get("/internal-test")

    assert health_response.status_code == 200
    assert health_response.json() == {"status": "healthy", "service": "todo-service"}
    assert internal_response.status_code == 200
    assert internal_response.json() == {"result": "ok"}
    assert calls == ["ensure_table_exists"]
    assert app.title == "Todo Service"
    assert app.docs_url == "/api/v1/todos/docs"
