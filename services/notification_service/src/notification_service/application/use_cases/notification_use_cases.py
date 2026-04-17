"""Notification Use Cases – application-level email operations.

Orchestrates domain entities, the email service interface (SES),
and the notification repository (DynamoDB).
"""

from __future__ import annotations

import logging

from src.notification_service.application.dto.notification_dto import (
    NotificationListResponse,
    NotificationResponse,
    SendNotificationRequest,
    VerifiedIdentitiesResponse,
)
from src.notification_service.domain.entities.notification_entity import (
    NotificationEntity,
)
from src.notification_service.domain.interfaces.email_service_interface import (
    EmailServiceInterface,
)
from src.notification_service.domain.interfaces.notification_repository_interface import (
    NotificationRepositoryInterface,
)

logger = logging.getLogger(__name__)


class NotificationUseCases:
    """Business operations for email notifications."""

    def __init__(
        self,
        email_service: EmailServiceInterface,
        repository: NotificationRepositoryInterface,
    ) -> None:
        self._email_service = email_service
        self._repository = repository

    # ── Send ─────────────────────────────────────────────────────────────────

    async def send_notification(
        self, request: SendNotificationRequest
    ) -> NotificationResponse:
        """Compose and dispatch an email notification via SES."""
        entity = NotificationEntity(
            recipient_email=request.recipient_email,
            subject=request.subject,
            body_text=request.body_text,
            body_html=request.body_html or self._build_html(request.subject, request.body_text),
            notification_type=request.notification_type,
            todo_id=request.todo_id,
        )

        try:
            message_id = await self._email_service.send_email(entity)
            entity = entity.mark_sent(message_id)
            logger.info(
                "Sent notification %s to %s (SES: %s)",
                entity.id,
                entity.recipient_email,
                message_id,
            )
        except Exception:
            entity = entity.mark_failed()
            logger.exception("Failed to send notification %s", entity.id)

        await self._repository.save(entity)
        return self._to_response(entity)

    # ── List ─────────────────────────────────────────────────────────────────

    async def list_notifications(self) -> NotificationListResponse:
        """Return all logged notifications from DynamoDB."""
        entities = await self._repository.get_all()
        items = [self._to_response(e) for e in entities]
        return NotificationListResponse(items=items, total=len(items))

    # ── Get single ───────────────────────────────────────────────────────────

    async def get_notification(self, notification_id: str) -> NotificationResponse | None:
        """Fetch a single notification by ID."""
        entity = await self._repository.get_by_id(notification_id)
        return self._to_response(entity) if entity else None

    # ── Verified identities ──────────────────────────────────────────────────

    async def get_verified_identities(self) -> VerifiedIdentitiesResponse:
        """Proxy to the email adapter to list SES-verified identities."""
        identities = await self._email_service.list_verified_identities()
        return VerifiedIdentitiesResponse(identities=identities)

    # ── Private helpers ──────────────────────────────────────────────────────

    @staticmethod
    def _to_response(entity: NotificationEntity) -> NotificationResponse:
        return NotificationResponse(
            id=entity.id,
            recipient_email=entity.recipient_email,
            subject=entity.subject,
            notification_type=entity.notification_type,
            status=entity.status,
            ses_message_id=entity.ses_message_id,
            todo_id=entity.todo_id,
            created_at=entity.created_at,
        )

    @staticmethod
    def _build_html(subject: str, body_text: str) -> str:
        """Generate a minimal HTML email body."""
        return f"""
        <html>
        <body style="font-family: Arial, sans-serif; padding: 20px; background: #1a1a2e; color: #e0e0e0;">
            <div style="max-width: 600px; margin: auto; background: #16213e; padding: 30px; border-radius: 10px;">
                <h2 style="color: #7c83ff;">{subject}</h2>
                <p style="line-height: 1.6;">{body_text}</p>
                <hr style="border-color: #2a2a4a;" />
                <small style="color: #888;">Sent by TODO App Notification Service</small>
            </div>
        </body>
        </html>
        """
