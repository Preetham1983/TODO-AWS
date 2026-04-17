"""Todo Use Cases – application-level orchestration of business operations.

Each public method represents a single use case.  The class depends only
on the *abstract* repository interface (Dependency Inversion Principle).
"""

from __future__ import annotations

import logging
from datetime import UTC, datetime

from src.todo_service.application.dto.todo_dto import (
    CreateTodoRequest,
    TodoListResponse,
    TodoResponse,
    UpdateTodoRequest,
)
from src.todo_service.domain.entities.todo_entity import TodoEntity
from src.todo_service.domain.interfaces.todo_repository_interface import (
    TodoRepositoryInterface,
)

logger = logging.getLogger(__name__)


class TodoUseCases:
    """Encapsulates every business operation on TODO items."""

    def __init__(self, repository: TodoRepositoryInterface) -> None:
        self._repository = repository

    # ── Create ───────────────────────────────────────────────────────────────

    async def create_todo(self, request: CreateTodoRequest) -> TodoResponse:
        """Create and persist a new TODO item."""
        entity = TodoEntity(
            title=request.title,
            description=request.description,
            priority=request.priority,
        )
        saved = await self._repository.create(entity)
        logger.info("Created todo %s – '%s'", saved.id, saved.title)
        return self._to_response(saved)

    # ── Read ─────────────────────────────────────────────────────────────────

    async def get_todo_by_id(self, todo_id: str) -> TodoResponse | None:
        """Fetch a single TODO by ID."""
        entity = await self._repository.get_by_id(todo_id)
        return self._to_response(entity) if entity else None

    async def get_all_todos(self) -> TodoListResponse:
        """Return every TODO."""
        entities = await self._repository.get_all()
        items = [self._to_response(e) for e in entities]
        return TodoListResponse(items=items, total=len(items))

    async def search_todos(self, query: str) -> TodoListResponse:
        """Full-text search across titles and descriptions."""
        entities = await self._repository.search(query)
        items = [self._to_response(e) for e in entities]
        return TodoListResponse(items=items, total=len(items))

    # ── Update ───────────────────────────────────────────────────────────────

    async def update_todo(
        self, todo_id: str, request: UpdateTodoRequest
    ) -> TodoResponse | None:
        """Partially update a TODO item."""
        existing = await self._repository.get_by_id(todo_id)
        if not existing:
            return None

        update_data = request.model_dump(exclude_none=True)
        update_data["updated_at"] = datetime.now(UTC)
        updated_entity = existing.model_copy(update=update_data)
        saved = await self._repository.update(updated_entity)
        logger.info("Updated todo %s", saved.id)
        return self._to_response(saved)

    # ── Delete ───────────────────────────────────────────────────────────────

    async def delete_todo(self, todo_id: str) -> bool:
        """Remove a TODO item permanently."""
        deleted = await self._repository.delete(todo_id)
        if deleted:
            logger.info("Deleted todo %s", todo_id)
        return deleted

    # ── Attachment helpers ───────────────────────────────────────────────────

    async def add_attachment_to_todo(
        self, todo_id: str, attachment_id: str
    ) -> TodoResponse | None:
        """Link an attachment ID to a TODO."""
        entity = await self._repository.get_by_id(todo_id)
        if not entity:
            return None
        updated = entity.add_attachment(attachment_id)
        saved = await self._repository.update(updated)
        return self._to_response(saved)

    async def remove_attachment_from_todo(
        self, todo_id: str, attachment_id: str
    ) -> TodoResponse | None:
        """Unlink an attachment ID from a TODO."""
        entity = await self._repository.get_by_id(todo_id)
        if not entity:
            return None
        updated = entity.remove_attachment(attachment_id)
        saved = await self._repository.update(updated)
        return self._to_response(saved)

    # ── Private helpers ──────────────────────────────────────────────────────

    @staticmethod
    def _to_response(entity: TodoEntity) -> TodoResponse:
        """Map a domain entity to the response DTO."""
        return TodoResponse(**entity.model_dump())
