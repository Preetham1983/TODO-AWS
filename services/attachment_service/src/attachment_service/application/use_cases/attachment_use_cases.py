"""Attachment Use Cases – application-level file operations.

Orchestrates domain entities, the storage interface (S3), and the
attachment metadata repository (DynamoDB).
"""

from __future__ import annotations

import logging

from src.attachment_service.application.dto.attachment_dto import (
    AttachmentListResponse,
    AttachmentResponse,
    UploadResponse,
)
from src.attachment_service.domain.entities.attachment_entity import AttachmentEntity
from src.attachment_service.domain.interfaces.attachment_repository_interface import (
    AttachmentRepositoryInterface,
)
from src.attachment_service.domain.interfaces.storage_service_interface import (
    StorageServiceInterface,
)

logger = logging.getLogger(__name__)


class AttachmentUseCases:
    """Business operations for file attachments."""

    def __init__(
        self,
        storage: StorageServiceInterface,
        repository: AttachmentRepositoryInterface,
    ) -> None:
        self._storage = storage
        self._repository = repository

    # ── Upload ───────────────────────────────────────────────────────────────

    async def upload_attachment(
        self,
        todo_id: str,
        filename: str,
        content_type: str,
        file_content: bytes,
    ) -> UploadResponse:
        """Upload a file to S3 and persist metadata in DynamoDB."""
        entity = AttachmentEntity(
            todo_id=todo_id,
            filename=filename,
            content_type=content_type,
            size_bytes=len(file_content),
        )
        entity = entity.model_copy(update={"s3_key": entity.build_s3_key()})

        saved = await self._storage.upload_file(entity, file_content)
        presigned = await self._storage.generate_presigned_url(saved.s3_key)
        saved = saved.model_copy(update={"download_url": presigned})

        await self._repository.save(saved)
        logger.info("Uploaded attachment %s for todo %s", saved.id, todo_id)

        return UploadResponse(attachment=self._to_response(saved))

    # ── Download ─────────────────────────────────────────────────────────────

    async def download_attachment(self, attachment_id: str) -> tuple[bytes, AttachmentEntity] | None:
        """Retrieve the raw file bytes plus metadata."""
        entity = await self._repository.get_by_id(attachment_id)
        if not entity:
            return None
        content = await self._storage.download_file(entity.s3_key)
        return content, entity

    # ── List ─────────────────────────────────────────────────────────────────

    async def list_attachments_for_todo(self, todo_id: str) -> AttachmentListResponse:
        """Return every attachment linked to a specific TODO."""
        entities = await self._repository.list_by_todo_id(todo_id)
        items = [self._to_response(e) for e in entities]
        return AttachmentListResponse(items=items, total=len(items))

    # ── Get single ───────────────────────────────────────────────────────────

    async def get_attachment(self, attachment_id: str) -> AttachmentResponse | None:
        """Fetch metadata for one attachment."""
        entity = await self._repository.get_by_id(attachment_id)
        if not entity:
            return None
        presigned = await self._storage.generate_presigned_url(entity.s3_key)
        entity = entity.model_copy(update={"download_url": presigned})
        return self._to_response(entity)

    # ── Delete ───────────────────────────────────────────────────────────────

    async def delete_attachment(self, attachment_id: str) -> bool:
        """Remove from DynamoDB and S3."""
        entity = await self._repository.delete(attachment_id)
        if not entity:
            return False
        await self._storage.delete_file(entity.s3_key)
        logger.info("Deleted attachment %s", attachment_id)
        return True

    # ── Private helpers ──────────────────────────────────────────────────────

    @staticmethod
    def _to_response(entity: AttachmentEntity) -> AttachmentResponse:
        return AttachmentResponse(**entity.model_dump())
