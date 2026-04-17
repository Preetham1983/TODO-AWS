"""Todo DTOs – request / response schemas used by the presentation layer.

DTOs decouple the API surface from the internal domain model, following
the Interface Segregation Principle.
"""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field

from src.todo_service.domain.entities.todo_entity import TodoPriority, TodoStatus

# ── Request DTOs ─────────────────────────────────────────────────────────────


class CreateTodoRequest(BaseModel):
    """Payload for creating a new TODO."""

    title: str = Field(..., min_length=1, max_length=200, examples=["Buy groceries"])
    description: str = Field(default="", max_length=2000, examples=["Milk, eggs, bread"])
    priority: TodoPriority = Field(default=TodoPriority.MEDIUM)


class UpdateTodoRequest(BaseModel):
    """Payload for updating an existing TODO (partial)."""

    title: str | None = Field(default=None, min_length=1, max_length=200)
    description: str | None = Field(default=None, max_length=2000)
    status: TodoStatus | None = None
    priority: TodoPriority | None = None


# ── Response DTOs ────────────────────────────────────────────────────────────


class TodoResponse(BaseModel):
    """Serialised representation of a single TODO sent back to clients."""

    id: str
    title: str
    description: str
    status: TodoStatus
    priority: TodoPriority
    attachment_ids: list[str]
    created_at: datetime
    updated_at: datetime


class TodoListResponse(BaseModel):
    """Wrapper for a list of TODOs."""

    items: list[TodoResponse]
    total: int
