"""Attachment Controller – HTTP endpoint definitions for file operations."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, UploadFile, status
from fastapi.responses import Response

from src.attachment_service.application.dto.attachment_dto import (
    AttachmentListResponse,
    AttachmentResponse,
    UploadResponse,
)
from src.attachment_service.application.use_cases.attachment_use_cases import (
    AttachmentUseCases,
)


class AttachmentController:
    """REST controller for the /api/v1/attachments resource."""

    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB

    def __init__(self, use_cases: AttachmentUseCases) -> None:
        self._use_cases = use_cases
        self.router = APIRouter(prefix="/api/v1/attachments", tags=["Attachments"])
        self._register_routes()

    # ── Route registration ───────────────────────────────────────────────────

    def _register_routes(self) -> None:
        self.router.post(
            "/upload/{todo_id}",
            response_model=UploadResponse,
            status_code=status.HTTP_201_CREATED,
        )(self.upload_file)

        self.router.get(
            "/todo/{todo_id}",
            response_model=AttachmentListResponse,
        )(self.list_for_todo)

        self.router.get(
            "/{attachment_id}",
            response_model=AttachmentResponse,
        )(self.get_attachment)

        self.router.get("/{attachment_id}/download")(self.download_file)

        self.router.delete(
            "/{attachment_id}",
            status_code=status.HTTP_204_NO_CONTENT,
        )(self.delete_attachment)

    # ── Handlers ─────────────────────────────────────────────────────────────

    async def upload_file(self, todo_id: str, file: UploadFile) -> UploadResponse:
        """POST /api/v1/attachments/upload/{todo_id} – upload a file for a TODO."""
        content = await file.read()
        if len(content) > self.MAX_FILE_SIZE:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"File exceeds maximum size of {self.MAX_FILE_SIZE} bytes",
            )

        return await self._use_cases.upload_attachment(
            todo_id=todo_id,
            filename=file.filename or "unnamed",
            content_type=file.content_type or "application/octet-stream",
            file_content=content,
        )

    async def list_for_todo(self, todo_id: str) -> AttachmentListResponse:
        """GET /api/v1/attachments/todo/{todo_id} – list attachments for a TODO."""
        return await self._use_cases.list_attachments_for_todo(todo_id)

    async def get_attachment(self, attachment_id: str) -> AttachmentResponse:
        """GET /api/v1/attachments/{attachment_id} – get attachment metadata."""
        result = await self._use_cases.get_attachment(attachment_id)
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Attachment '{attachment_id}' not found",
            )
        return result

    async def download_file(self, attachment_id: str) -> Response:
        """GET /api/v1/attachments/{attachment_id}/download – raw file bytes."""
        result = await self._use_cases.download_attachment(attachment_id)
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Attachment '{attachment_id}' not found",
            )
        content, entity = result
        return Response(
            content=content,
            media_type=entity.content_type,
            headers={
                "Content-Disposition": f'attachment; filename="{entity.filename}"'
            },
        )

    async def delete_attachment(self, attachment_id: str) -> None:
        """DELETE /api/v1/attachments/{attachment_id} – remove an attachment."""
        deleted = await self._use_cases.delete_attachment(attachment_id)
        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Attachment '{attachment_id}' not found",
            )
