"""Attachment Repository Interface – port for persisting attachment metadata.

This is separate from StorageServiceInterface (which handles file bytes in S3).
This interface handles the *metadata* record in DynamoDB.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from src.attachment_service.domain.entities.attachment_entity import AttachmentEntity


class AttachmentRepositoryInterface(ABC):
    """Abstract repository contract for attachment metadata persistence."""

    @abstractmethod
    async def save(self, entity: AttachmentEntity) -> AttachmentEntity:
        """Persist attachment metadata and return the entity."""

    @abstractmethod
    async def get_by_id(self, attachment_id: str) -> AttachmentEntity | None:
        """Retrieve a single attachment's metadata by ID."""

    @abstractmethod
    async def list_by_todo_id(self, todo_id: str) -> list[AttachmentEntity]:
        """Return all attachments linked to a specific TODO."""

    @abstractmethod
    async def delete(self, attachment_id: str) -> AttachmentEntity | None:
        """Remove metadata by ID.  Return the entity if it existed, else None."""

    @abstractmethod
    async def ensure_table_exists(self) -> None:
        """Idempotently create the backing table."""
