"""Attachment Entity – domain model for a file attachment."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

from pydantic import BaseModel, Field


class AttachmentEntity(BaseModel):
    """Value-object representing a file stored in S3.

    The entity is storage-agnostic: it knows nothing about S3.
    That detail lives in the infrastructure layer.
    """

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    todo_id: str = Field(..., description="ID of the parent TODO item")
    filename: str = Field(..., min_length=1, max_length=500)
    content_type: str = Field(default="application/octet-stream")
    size_bytes: int = Field(default=0, ge=0)
    s3_key: str = Field(default="", description="Object key inside the S3 bucket")
    download_url: str = Field(default="", description="Pre-signed download URL")
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    def build_s3_key(self) -> str:
        """Deterministic key: <todo_id>/<attachment_id>/<filename>."""
        return f"{self.todo_id}/{self.id}/{self.filename}"
