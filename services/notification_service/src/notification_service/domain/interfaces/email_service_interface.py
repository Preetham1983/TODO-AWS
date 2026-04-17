"""Email Service Interface – port for email-sending infrastructure adapters.

Any email provider (SES, SendGrid, SMTP) can implement this interface.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from src.notification_service.domain.entities.notification_entity import (
    NotificationEntity,
)


class EmailServiceInterface(ABC):
    """Abstract contract for sending email notifications."""

    @abstractmethod
    async def send_email(self, notification: NotificationEntity) -> str:
        """Send an email and return the provider message ID."""

    @abstractmethod
    async def verify_sender_identity(self) -> None:
        """Ensure the sender email is verified (required by SES)."""

    @abstractmethod
    async def list_verified_identities(self) -> list[str]:
        """Return all verified email identities."""
