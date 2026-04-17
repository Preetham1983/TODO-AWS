"""Notification Controller – HTTP endpoint definitions for email operations."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, status

from src.notification_service.application.dto.notification_dto import (
    NotificationListResponse,
    NotificationResponse,
    SendNotificationRequest,
    VerifiedIdentitiesResponse,
)
from src.notification_service.application.use_cases.notification_use_cases import (
    NotificationUseCases,
)


class NotificationController:
    """REST controller for the /api/v1/notifications resource."""

    def __init__(self, use_cases: NotificationUseCases) -> None:
        self._use_cases = use_cases
        self.router = APIRouter(
            prefix="/api/v1/notifications", tags=["Notifications"]
        )
        self._register_routes()

    # ── Route registration ───────────────────────────────────────────────────

    def _register_routes(self) -> None:
        self.router.post(
            "/send",
            response_model=NotificationResponse,
            status_code=status.HTTP_201_CREATED,
        )(self.send_notification)

        self.router.get("", response_model=NotificationListResponse)(
            self.list_notifications
        )

        self.router.get("/identities", response_model=VerifiedIdentitiesResponse)(
            self.list_identities
        )

        self.router.get("/{notification_id}", response_model=NotificationResponse)(
            self.get_notification
        )

    # ── Handlers ─────────────────────────────────────────────────────────────

    async def send_notification(
        self, request: SendNotificationRequest
    ) -> NotificationResponse:
        """POST /api/v1/notifications/send – dispatch an email notification."""
        return await self._use_cases.send_notification(request)

    async def list_notifications(self) -> NotificationListResponse:
        """GET /api/v1/notifications – list all sent notifications."""
        return await self._use_cases.list_notifications()

    async def get_notification(self, notification_id: str) -> NotificationResponse:
        """GET /api/v1/notifications/{notification_id} – get one notification."""
        result = await self._use_cases.get_notification(notification_id)
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Notification '{notification_id}' not found",
            )
        return result

    async def list_identities(self) -> VerifiedIdentitiesResponse:
        """GET /api/v1/notifications/identities – SES verified emails."""
        return await self._use_cases.get_verified_identities()
