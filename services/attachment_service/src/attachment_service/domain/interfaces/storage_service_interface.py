"""Storage Interface – port for file-storage infrastructure adapters.

Any cloud storage provider (S3, GCS, Azure Blob) can implement this
interface without changing the domain or application layers.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from src.attachment_service.domain.entities.attachment_entity import AttachmentEntity


class StorageServiceInterface(ABC):
    """Abstract contract for object-storage operations."""

    @abstractmethod
    async def upload_file(
        self,
        entity: AttachmentEntity,
        file_content: bytes,
    ) -> AttachmentEntity:
        """Upload a file and return the entity with populated S3 key."""

    @abstractmethod
    async def download_file(self, s3_key: str) -> bytes:
        """Download raw bytes for a given object key."""

    @abstractmethod
    async def delete_file(self, s3_key: str) -> bool:
        """Delete an object by key. Return True if it existed."""

    @abstractmethod
    async def generate_presigned_url(self, s3_key: str) -> str:
        """Create a time-limited download URL for the object."""

    @abstractmethod
    async def ensure_bucket_exists(self) -> None:
        """Create the bucket if it does not already exist."""
