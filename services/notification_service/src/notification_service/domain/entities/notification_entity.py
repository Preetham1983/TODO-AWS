"""Notification Entity – domain model for an email notification."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from enum import StrEnum

from pydantic import BaseModel, Field


class NotificationStatus(StrEnum):
    """Lifecycle of a notification."""

    QUEUED = "queued"
    SENT = "sent"
    FAILED = "failed"


class NotificationType(StrEnum):
    """Categories of notification triggers."""

    TODO_CREATED = "todo_created"
    TODO_COMPLETED = "todo_completed"
    TODO_DELETED = "todo_deleted"
    ATTACHMENT_UPLOADED = "attachment_uploaded"
    CUSTOM = "custom"


class NotificationEntity(BaseModel):
    """Value-object representing an outbound email notification."""

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    recipient_email: str = Field(..., min_length=5)
    subject: str = Field(..., min_length=1, max_length=500)
    body_text: str = Field(default="")
    body_html: str = Field(default="")
    notification_type: NotificationType = Field(default=NotificationType.CUSTOM)
    status: NotificationStatus = Field(default=NotificationStatus.QUEUED)
    todo_id: str | None = Field(default=None)
    ses_message_id: str | None = Field(default=None)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    def mark_sent(self, message_id: str) -> NotificationEntity:
        """Return a copy marked as sent with the SES message ID."""
        return self.model_copy(
            update={
                "status": NotificationStatus.SENT,
                "ses_message_id": message_id,
            }
        )

    def mark_failed(self) -> NotificationEntity:
        """Return a copy marked as failed."""
        return self.model_copy(update={"status": NotificationStatus.FAILED})
