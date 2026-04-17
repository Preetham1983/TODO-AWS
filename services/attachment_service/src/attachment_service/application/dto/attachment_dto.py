"""Attachment DTOs – request / response schemas."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field

# ── Response DTOs ────────────────────────────────────────────────────────────


class AttachmentResponse(BaseModel):
    """Serialised representation of an attachment."""

    id: str
    todo_id: str
    filename: str
    content_type: str
    size_bytes: int
    s3_key: str
    download_url: str
    created_at: datetime


class AttachmentListResponse(BaseModel):
    """Wrapper for a list of attachments."""

    items: list[AttachmentResponse]
    total: int


class UploadResponse(BaseModel):
    """Response after a successful file upload."""

    attachment: AttachmentResponse
    message: str = Field(default="File uploaded successfully")
