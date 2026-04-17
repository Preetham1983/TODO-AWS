"""Attachment Service – Application entry point and FastAPI factory."""

import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.attachment_service.application.use_cases.attachment_use_cases import (
    AttachmentUseCases,
)
from src.attachment_service.config.settings import AttachmentServiceSettings
from src.attachment_service.infrastructure.persistence.dynamodb_attachment_repository import (
    DynamoDbAttachmentRepository,
)
from src.attachment_service.infrastructure.storage.s3_storage_adapter import (
    S3StorageAdapter,
)
from src.attachment_service.presentation.controllers.attachment_controller import (
    AttachmentController,
)

logger = logging.getLogger(__name__)


def create_application() -> FastAPI:
    """Application factory – wires up all layers following Dependency Injection."""

    # ── Configuration ────────────────────────────────────────────────────────
    settings = AttachmentServiceSettings()

    logging.basicConfig(
        level=getattr(logging, settings.log_level.upper(), logging.INFO),
        format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    )

    # ── FastAPI Instance ─────────────────────────────────────────────────────
    app = FastAPI(
        title="Attachment Service",
        description="Microservice for file uploads/downloads via S3 + DynamoDB",
        version="1.0.0",
        docs_url="/api/v1/attachments/docs",
        openapi_url="/api/v1/attachments/openapi.json",
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
    storage_adapter = S3StorageAdapter(settings=settings)
    metadata_repository = DynamoDbAttachmentRepository(settings=settings)
    use_cases = AttachmentUseCases(storage=storage_adapter, repository=metadata_repository)
    controller = AttachmentController(use_cases=use_cases)

    # ── Register Routes ──────────────────────────────────────────────────────
    app.include_router(controller.router)

    # ── Startup ──────────────────────────────────────────────────────────────
    @app.on_event("startup")
    async def on_startup() -> None:
        await storage_adapter.ensure_bucket_exists()
        logger.info("S3 bucket verified/created")
        await metadata_repository.ensure_table_exists()
        logger.info("DynamoDB attachments table verified/created")

    # ── Health Check ─────────────────────────────────────────────────────────
    @app.get("/health", tags=["Health"])
    async def health_check() -> dict:
        return {"status": "healthy", "service": "attachment-service"}

    logger.info(
        "Attachment Service started on %s:%s", settings.host, settings.port
    )
    return app
