"""Notification Repository Interface – port for persisting notification logs.

Separates the act of *sending* (EmailServiceInterface) from the act
of *recording* the notification (this interface) – Single Responsibility.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from src.notification_service.domain.entities.notification_entity import (
    NotificationEntity,
)


class NotificationRepositoryInterface(ABC):
    """Abstract repository contract for notification log persistence."""

    @abstractmethod
    async def save(self, entity: NotificationEntity) -> NotificationEntity:
        """Persist a notification record and return it."""

    @abstractmethod
    async def get_by_id(self, notification_id: str) -> NotificationEntity | None:
        """Retrieve a single notification by ID."""

    @abstractmethod
    async def get_all(self) -> list[NotificationEntity]:
        """Return every persisted notification."""

    @abstractmethod
    async def ensure_table_exists(self) -> None:
        """Idempotently create the backing table."""
