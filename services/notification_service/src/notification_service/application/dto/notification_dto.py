"""Notification DTOs – request / response schemas."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field

from src.notification_service.domain.entities.notification_entity import (
    NotificationStatus,
    NotificationType,
)

# ── Request DTOs ─────────────────────────────────────────────────────────────


class SendNotificationRequest(BaseModel):
    """Payload to trigger an email notification."""

    recipient_email: str = Field(..., min_length=5, examples=["user@example.com"])
    subject: str = Field(..., min_length=1, max_length=500, examples=["Your TODO is due!"])
    body_text: str = Field(default="", examples=["Remember to complete your task."])
    body_html: str = Field(default="")
    notification_type: NotificationType = Field(default=NotificationType.CUSTOM)
    todo_id: str | None = Field(default=None)


# ── Response DTOs ────────────────────────────────────────────────────────────


class NotificationResponse(BaseModel):
    """Serialised representation of a sent notification."""

    id: str
    recipient_email: str
    subject: str
    notification_type: NotificationType
    status: NotificationStatus
    ses_message_id: str | None
    todo_id: str | None
    created_at: datetime


class NotificationListResponse(BaseModel):
    """Wrapper for a list of notifications."""

    items: list[NotificationResponse]
    total: int


class VerifiedIdentitiesResponse(BaseModel):
    """List of SES-verified email identities."""

    identities: list[str]
