"""Todo Repository Interface – port that infrastructure adapters must implement.

This follows the *Dependency Inversion Principle*: the domain defines
the interface; the infrastructure provides the concrete implementation.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from src.todo_service.domain.entities.todo_entity import TodoEntity


class TodoRepositoryInterface(ABC):
    """Abstract repository contract for persisting TODO entities."""

    @abstractmethod
    async def create(self, entity: TodoEntity) -> TodoEntity:
        """Persist a new TODO and return it."""

    @abstractmethod
    async def get_by_id(self, todo_id: str) -> TodoEntity | None:
        """Retrieve a single TODO by its unique ID."""

    @abstractmethod
    async def get_all(self) -> list[TodoEntity]:
        """Return every TODO in storage."""

    @abstractmethod
    async def update(self, entity: TodoEntity) -> TodoEntity:
        """Replace an existing TODO with the supplied entity."""

    @abstractmethod
    async def delete(self, todo_id: str) -> bool:
        """Remove a TODO by ID. Return True if it existed."""

    @abstractmethod
    async def search(self, query: str) -> list[TodoEntity]:
        """Return TODOs whose title or description match the query."""
