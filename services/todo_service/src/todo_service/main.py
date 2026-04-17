"""Todo Service – Application entry point and FastAPI factory."""

import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.todo_service.application.use_cases.todo_use_cases import TodoUseCases
from src.todo_service.config.settings import TodoServiceSettings
from src.todo_service.infrastructure.repositories.dynamodb_todo_repository import (
    DynamoDbTodoRepository,
)
from src.todo_service.presentation.controllers.todo_controller import TodoController

logger = logging.getLogger(__name__)


def create_application() -> FastAPI:
    """Application factory – wires up all layers following Dependency Injection."""

    # ── Configuration ────────────────────────────────────────────────────────
    settings = TodoServiceSettings()

    logging.basicConfig(
        level=getattr(logging, settings.log_level.upper(), logging.INFO),
        format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    )

    # ── FastAPI Instance ─────────────────────────────────────────────────────
    app = FastAPI(
        title="Todo Service",
        description="Microservice for managing TODO items",
        version="1.0.0",
        docs_url="/api/v1/todos/docs",
        openapi_url="/api/v1/todos/openapi.json",
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
    repository = DynamoDbTodoRepository(settings=settings)
    use_cases = TodoUseCases(repository=repository)
    controller = TodoController(use_cases=use_cases)

    # ── Register Routes ──────────────────────────────────────────────────────
    app.include_router(controller.router)

    # ── Startup ──────────────────────────────────────────────────────────────
    @app.on_event("startup")
    async def on_startup() -> None:
        await repository.ensure_table_exists()
        logger.info("DynamoDB table verified/created")

    # ── Health Check ─────────────────────────────────────────────────────────
    @app.get("/health", tags=["Health"])
    async def health_check() -> dict:
        return {"status": "healthy", "service": "todo-service"}

    logger.info("Todo Service started on %s:%s", settings.host, settings.port)
    return app
