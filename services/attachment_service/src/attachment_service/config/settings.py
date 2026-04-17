"""Attachment Service – Pydantic Settings loaded from .env.docker."""

from __future__ import annotations

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class AttachmentServiceSettings(BaseSettings):
    """Centralised, typed configuration for the Attachment Service."""

    model_config = SettingsConfigDict(
        env_file=".env.docker",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # ── Service ──────────────────────────────────────────────────────────────
    app_env: str = Field(validation_alias="APP_ENV")
    debug: bool = Field(validation_alias="DEBUG")
    log_level: str = Field(validation_alias="LOG_LEVEL")

    host: str = Field(validation_alias="ATTACHMENT_SERVICE_HOST")
    port: int = Field(validation_alias="ATTACHMENT_SERVICE_PORT")
    attachment_service_prefix: str = Field(
        validation_alias="ATTACHMENT_SERVICE_PREFIX",
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
    dynamodb_attachments_table: str = Field(
        validation_alias="DYNAMODB_ATTACHMENTS_TABLE",
    )

    # ── S3 ───────────────────────────────────────────────────────────────────
    s3_bucket_name: str = Field(
        validation_alias="S3_BUCKET_NAME",
    )
    s3_presigned_url_expiry: int = Field(
        validation_alias="S3_PRESIGNED_URL_EXPIRY",
    )

    # ── CORS ─────────────────────────────────────────────────────────────────
    cors_origins: list[str] = Field(
        validation_alias="CORS_ORIGINS",
    )

    # ── Inter-service URLs ───────────────────────────────────────────────────
    todo_service_url: str = Field(
        validation_alias="TODO_SERVICE_URL",
    )
