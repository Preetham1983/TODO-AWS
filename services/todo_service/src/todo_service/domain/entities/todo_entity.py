"""Todo Entity – core domain model for a TODO item."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from enum import StrEnum

from pydantic import BaseModel, Field


class TodoPriority(StrEnum):
    """Allowed priority levels for a TODO item."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class TodoStatus(StrEnum):
    """Lifecycle states of a TODO item."""

    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"


class TodoEntity(BaseModel):
    """Immutable value-object representing a single TODO item.

    All business rules live here so the rest of the application
    can stay free of domain logic (Single Responsibility).
    """

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str = Field(..., min_length=1, max_length=200)
    description: str = Field(default="", max_length=2000)
    status: TodoStatus = Field(default=TodoStatus.PENDING)
    priority: TodoPriority = Field(default=TodoPriority.MEDIUM)
    attachment_ids: list[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    # ── Domain behaviour ─────────────────────────────────────────────────────

    def mark_completed(self) -> TodoEntity:
        """Return a new entity marked as completed."""
        return self.model_copy(
            update={
                "status": TodoStatus.COMPLETED,
                "updated_at": datetime.now(UTC),
            }
        )

    def mark_in_progress(self) -> TodoEntity:
        """Return a new entity marked as in-progress."""
        return self.model_copy(
            update={
                "status": TodoStatus.IN_PROGRESS,
                "updated_at": datetime.now(UTC),
            }
        )

    def add_attachment(self, attachment_id: str) -> TodoEntity:
        """Return a new entity with an attachment ID appended."""
        return self.model_copy(
            update={
                "attachment_ids": [*self.attachment_ids, attachment_id],
                "updated_at": datetime.now(UTC),
            }
        )

    def remove_attachment(self, attachment_id: str) -> TodoEntity:
        """Return a new entity with an attachment ID removed."""
        return self.model_copy(
            update={
                "attachment_ids": [
                    aid for aid in self.attachment_ids if aid != attachment_id
                ],
                "updated_at": datetime.now(UTC),
            }
        )
