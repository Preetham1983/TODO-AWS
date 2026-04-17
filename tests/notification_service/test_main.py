from __future__ import annotations

from fastapi import APIRouter
from fastapi.testclient import TestClient


class FakeSettings:
    log_level = "INFO"
    cors_origins = ["http://localhost:3000"]
    host = "127.0.0.1"
    port = 8003


def test_create_application_exposes_health_and_runs_startup(monkeypatch) -> None:
    from tests.pathing import import_service_main

    notification_main = import_service_main("notification_service")
    calls: list[str] = []

    class FakeEmailAdapter:
        def __init__(self, settings) -> None:
            self.settings = settings

        async def verify_sender_identity(self) -> None:
            calls.append("verify_sender_identity")

    class FakeRepository:
        def __init__(self, settings) -> None:
            self.settings = settings

        async def ensure_table_exists(self) -> None:
            calls.append("ensure_table_exists")

    class FakeUseCases:
        def __init__(self, email_service, repository) -> None:
            self.email_service = email_service
            self.repository = repository

    class FakeController:
        def __init__(self, use_cases) -> None:
            self.use_cases = use_cases
            self.router = APIRouter()

            @self.router.get("/internal-test")
            async def internal_test() -> dict[str, str]:
                return {"result": "ok"}

    monkeypatch.setattr(
        notification_main,
        "NotificationServiceSettings",
        FakeSettings,
    )
    monkeypatch.setattr(notification_main, "SesEmailAdapter", FakeEmailAdapter)
    monkeypatch.setattr(
        notification_main,
        "DynamoDbNotificationRepository",
        FakeRepository,
    )
    monkeypatch.setattr(notification_main, "NotificationUseCases", FakeUseCases)
    monkeypatch.setattr(notification_main, "NotificationController", FakeController)

    app = notification_main.create_application()

    with TestClient(app) as client:
        health_response = client.get("/health")
        internal_response = client.get("/internal-test")

    assert health_response.status_code == 200
    assert health_response.json() == {
        "status": "healthy",
        "service": "notification-service",
    }
    assert internal_response.status_code == 200
    assert internal_response.json() == {"result": "ok"}
    assert calls == ["verify_sender_identity", "ensure_table_exists"]
    assert app.title == "Notification Service"
    assert app.docs_url == "/api/v1/notifications/docs"
