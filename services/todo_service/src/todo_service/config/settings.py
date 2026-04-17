"""Todo Service – Pydantic Settings loaded from .env.docker."""

from __future__ import annotations

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class TodoServiceSettings(BaseSettings):
    """Centralised, typed configuration for the Todo Service.

    Values are loaded from the `.env.docker` file (or real environment
    variables when running outside Docker).
    """

    model_config = SettingsConfigDict(
        env_file=".env.docker",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # ── Service ──────────────────────────────────────────────────────────────
    app_env: str = Field(validation_alias="APP_ENV")
    debug: bool = Field(validation_alias="DEBUG")
    log_level: str = Field(validation_alias="LOG_LEVEL")

    host: str = Field(validation_alias="TODO_SERVICE_HOST")
    port: int = Field(validation_alias="TODO_SERVICE_PORT")
    todo_service_prefix: str = Field(
        validation_alias="TODO_SERVICE_PREFIX",
    )

    # ── AWS / LocalStack ─────────────────────────────────────────────────────
    aws_region: str = Field(validation_alias="AWS_REGION")
    aws_access_key_id: str = Field(validation_alias="AWS_ACCESS_KEY_ID")
    aws_secret_access_key: str = Field(
        validation_alias="AWS_SECRET_ACCESS_KEY",
    )
    aws_endpoint_url: str = Field(
        validation_alias="AWS_ENDPOINT_URL",
    )

    # ── DynamoDB ─────────────────────────────────────────────────────────────
    dynamodb_todos_table: str = Field(
        validation_alias="DYNAMODB_TODOS_TABLE",
    )

    # ── CORS ─────────────────────────────────────────────────────────────────
    cors_origins: list[str] = Field(
        validation_alias="CORS_ORIGINS",
    )

    # ── Inter-service URLs ───────────────────────────────────────────────────
    attachment_service_url: str = Field(
        validation_alias="ATTACHMENT_SERVICE_URL",
    )
    notification_service_url: str = Field(
        validation_alias="NOTIFICATION_SERVICE_URL",
    )
