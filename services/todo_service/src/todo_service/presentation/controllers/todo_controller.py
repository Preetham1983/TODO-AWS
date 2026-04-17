"""Todo Controller – HTTP endpoint definitions.

The controller is a thin translation layer between HTTP and the
application use cases.  It contains no business logic (SRP).
"""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, status

from src.todo_service.application.dto.todo_dto import (
    CreateTodoRequest,
    TodoListResponse,
    TodoResponse,
    UpdateTodoRequest,
)
from src.todo_service.application.use_cases.todo_use_cases import TodoUseCases


class TodoController:
    """REST controller for the /api/v1/todos resource."""

    def __init__(self, use_cases: TodoUseCases) -> None:
        self._use_cases = use_cases
        self.router = APIRouter(prefix="/api/v1/todos", tags=["Todos"])
        self._register_routes()

    # ── Route registration ───────────────────────────────────────────────────

    def _register_routes(self) -> None:
        """Bind handler methods to HTTP verbs & paths."""
        self.router.post(
            "",
            response_model=TodoResponse,
            status_code=status.HTTP_201_CREATED,
        )(self.create_todo)

        self.router.get("", response_model=TodoListResponse)(self.list_todos)
        self.router.get("/search", response_model=TodoListResponse)(self.search_todos)
        self.router.get("/{todo_id}", response_model=TodoResponse)(self.get_todo)
        self.router.put("/{todo_id}", response_model=TodoResponse)(self.update_todo)
        self.router.delete("/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)(
            self.delete_todo
        )
        self.router.post(
            "/{todo_id}/attachments/{attachment_id}",
            response_model=TodoResponse,
        )(self.add_attachment)
        self.router.delete(
            "/{todo_id}/attachments/{attachment_id}",
            response_model=TodoResponse,
        )(self.remove_attachment)

    # ── Handlers ─────────────────────────────────────────────────────────────

    async def create_todo(self, request: CreateTodoRequest) -> TodoResponse:
        """POST /api/v1/todos – create a new TODO."""
        return await self._use_cases.create_todo(request)

    async def list_todos(self) -> TodoListResponse:
        """GET /api/v1/todos – list all TODOs."""
        return await self._use_cases.get_all_todos()

    async def search_todos(self, q: str = "") -> TodoListResponse:
        """GET /api/v1/todos/search?q=... – full-text search."""
        return await self._use_cases.search_todos(q)

    async def get_todo(self, todo_id: str) -> TodoResponse:
        """GET /api/v1/todos/{todo_id} – fetch a single TODO."""
        result = await self._use_cases.get_todo_by_id(todo_id)
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Todo '{todo_id}' not found",
            )
        return result

    async def update_todo(
        self, todo_id: str, request: UpdateTodoRequest
    ) -> TodoResponse:
        """PUT /api/v1/todos/{todo_id} – partial update."""
        result = await self._use_cases.update_todo(todo_id, request)
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Todo '{todo_id}' not found",
            )
        return result

    async def delete_todo(self, todo_id: str) -> None:
        """DELETE /api/v1/todos/{todo_id} – remove a TODO."""
        deleted = await self._use_cases.delete_todo(todo_id)
        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Todo '{todo_id}' not found",
            )

    async def add_attachment(
        self, todo_id: str, attachment_id: str
    ) -> TodoResponse:
        """POST /api/v1/todos/{todo_id}/attachments/{attachment_id}"""
        result = await self._use_cases.add_attachment_to_todo(todo_id, attachment_id)
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Todo '{todo_id}' not found",
            )
        return result

    async def remove_attachment(
        self, todo_id: str, attachment_id: str
    ) -> TodoResponse:
        """DELETE /api/v1/todos/{todo_id}/attachments/{attachment_id}"""
        result = await self._use_cases.remove_attachment_from_todo(
            todo_id, attachment_id
        )
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Todo '{todo_id}' not found",
            )
        return result
