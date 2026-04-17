"""Notification Service – Application entry point and FastAPI factory."""

import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.notification_service.application.use_cases.notification_use_cases import (
    NotificationUseCases,
)
from src.notification_service.config.settings import NotificationServiceSettings
from src.notification_service.infrastructure.email.ses_email_adapter import (
    SesEmailAdapter,
)
from src.notification_service.infrastructure.persistence.dynamodb_notification_repository import (
    DynamoDbNotificationRepository,
)
from src.notification_service.presentation.controllers.notification_controller import (
    NotificationController,
)

logger = logging.getLogger(__name__)


def create_application() -> FastAPI:
    """Application factory – wires up all layers following Dependency Injection."""

    # ── Configuration ────────────────────────────────────────────────────────
    settings = NotificationServiceSettings()

    logging.basicConfig(
        level=getattr(logging, settings.log_level.upper(), logging.INFO),
        format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    )

    # ── FastAPI Instance ─────────────────────────────────────────────────────
    app = FastAPI(
        title="Notification Service",
        description="Microservice for email notifications via SES + DynamoDB",
        version="1.0.0",
        docs_url="/api/v1/notifications/docs",
        openapi_url="/api/v1/notifications/openapi.json",
    )

    # ── CORS Middleware ──────────────────────────────────────────────────────
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # ── Dependency Injection (Composition Root) ──────────────────────────────
    email_adapter = SesEmailAdapter(settings=settings)
    notification_repository = DynamoDbNotificationRepository(settings=settings)
    use_cases = NotificationUseCases(
        email_service=email_adapter,
        repository=notification_repository,
    )
    controller = NotificationController(use_cases=use_cases)

    # ── Register Routes ──────────────────────────────────────────────────────
    app.include_router(controller.router)

    # ── Startup ──────────────────────────────────────────────────────────────
    @app.on_event("startup")
    async def on_startup() -> None:
        await email_adapter.verify_sender_identity()
        logger.info("SES sender identity verified")
        await notification_repository.ensure_table_exists()
        logger.info("DynamoDB notifications table verified/created")

    # ── Health Check ─────────────────────────────────────────────────────────
    @app.get("/health", tags=["Health"])
    async def health_check() -> dict:
        return {"status": "healthy", "service": "notification-service"}

    logger.info(
        "Notification Service started on %s:%s", settings.host, settings.port
    )
    return app
