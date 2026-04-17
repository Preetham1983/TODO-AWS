"""DynamoDB Todo Repository – infrastructure adapter for AWS DynamoDB.

Implements the TodoRepositoryInterface using DynamoDB (via LocalStack).
Replaces the in-memory store with persistent, cloud-native storage.

LocalStack DynamoDB connection
──────────────────────────────
1. endpoint_url = http://localstack:4566 (Docker) / http://localhost:4566 (host)
2. Dummy credentials: aws_access_key_id=test, aws_secret_access_key=test
3. Table 'todos' is created by scripts/init_localstack.sh on container startup.
4. Partition key: id (String) – no sort key needed for simple CRUD.
"""

from __future__ import annotations

import logging
from datetime import datetime
from functools import cached_property
from typing import Any

import boto3
from botocore.exceptions import ClientError

from src.todo_service.config.settings import TodoServiceSettings
from src.todo_service.domain.entities.todo_entity import (
    TodoEntity,
    TodoPriority,
    TodoStatus,
)
from src.todo_service.domain.interfaces.todo_repository_interface import (
    TodoRepositoryInterface,
)

logger = logging.getLogger(__name__)


class DynamoDbTodoRepository(TodoRepositoryInterface):
    """DynamoDB-backed TODO persistence using boto3 resource API."""

    def __init__(self, settings: TodoServiceSettings) -> None:
        self._settings = settings

    # ── Lazy DynamoDB resource & table ───────────────────────────────────────

    @cached_property
    def _resource(self):
        logger.info(
            "Connecting to DynamoDB at %s (region=%s)",
            self._settings.aws_endpoint_url,
            self._settings.aws_region,
        )
        return boto3.resource(
            "dynamodb",
            region_name=self._settings.aws_region,
            aws_access_key_id=self._settings.aws_access_key_id,
            aws_secret_access_key=self._settings.aws_secret_access_key,
            endpoint_url=self._settings.aws_endpoint_url,
        )

    @cached_property
    def _table(self):
        return self._resource.Table(self._settings.dynamodb_todos_table)

    # ── Interface implementations ────────────────────────────────────────────

    async def create(self, entity: TodoEntity) -> TodoEntity:
        item = self._entity_to_item(entity)
        self._table.put_item(Item=item)
        logger.debug("Stored todo %s in DynamoDB", entity.id)
        return entity

    async def get_by_id(self, todo_id: str) -> TodoEntity | None:
        try:
            response = self._table.get_item(Key={"id": todo_id})
        except ClientError:
            logger.exception("Failed to get todo %s", todo_id)
            return None

        item = response.get("Item")
        return self._item_to_entity(item) if item else None

    async def get_all(self) -> list[TodoEntity]:
        items: list[dict[str, Any]] = []
        response = self._table.scan()
        items.extend(response.get("Items", []))

        # Handle pagination
        while "LastEvaluatedKey" in response:
            response = self._table.scan(
                ExclusiveStartKey=response["LastEvaluatedKey"]
            )
            items.extend(response.get("Items", []))

        return [self._item_to_entity(item) for item in items]

    async def update(self, entity: TodoEntity) -> TodoEntity:
        item = self._entity_to_item(entity)
        self._table.put_item(Item=item)
        logger.debug("Updated todo %s in DynamoDB", entity.id)
        return entity

    async def delete(self, todo_id: str) -> bool:
        try:
            self._table.delete_item(
                Key={"id": todo_id},
                ConditionExpression="attribute_exists(id)",
            )
            return True
        except ClientError as exc:
            if exc.response["Error"]["Code"] == "ConditionalCheckFailedException":
                return False
            logger.exception("Failed to delete todo %s", todo_id)
            return False

    async def search(self, query: str) -> list[TodoEntity]:
        # DynamoDB doesn't support full-text search natively.
        # For a small dataset we scan and filter in application code.
        # For production, consider OpenSearch or a GSI on a tokenised field.
        all_entities = await self.get_all()
        query_lower = query.lower()
        return [
            entity
            for entity in all_entities
            if query_lower in entity.title.lower()
            or query_lower in entity.description.lower()
        ]

    # ── Table management ─────────────────────────────────────────────────────

    async def ensure_table_exists(self) -> None:
        """Idempotently create the DynamoDB table (in case init script hasn't run)."""
        try:
            self._table.table_status  # noqa: B018 – triggers DescribeTable
            logger.info("DynamoDB table '%s' exists", self._settings.dynamodb_todos_table)
        except ClientError:
            logger.info("Creating DynamoDB table '%s'", self._settings.dynamodb_todos_table)
            self._resource.create_table(
                TableName=self._settings.dynamodb_todos_table,
                KeySchema=[{"AttributeName": "id", "KeyType": "HASH"}],
                AttributeDefinitions=[{"AttributeName": "id", "AttributeType": "S"}],
                BillingMode="PAY_PER_REQUEST",
            )
            self._table.wait_until_exists()

    # ── Serialisation helpers ────────────────────────────────────────────────

    @staticmethod
    def _entity_to_item(entity: TodoEntity) -> dict[str, Any]:
        """Convert a domain entity to a DynamoDB-safe dict."""
        return {
            "id": entity.id,
            "title": entity.title,
            "description": entity.description,
            "status": entity.status.value,
            "priority": entity.priority.value,
            "attachment_ids": entity.attachment_ids,
            "created_at": entity.created_at.isoformat(),
            "updated_at": entity.updated_at.isoformat(),
        }

    @staticmethod
    def _item_to_entity(item: dict[str, Any]) -> TodoEntity:
        """Convert a DynamoDB item back to a domain entity."""
        return TodoEntity(
            id=item["id"],
            title=item["title"],
            description=item.get("description", ""),
            status=TodoStatus(item["status"]),
            priority=TodoPriority(item["priority"]),
            attachment_ids=item.get("attachment_ids", []),
            created_at=datetime.fromisoformat(item["created_at"]),
            updated_at=datetime.fromisoformat(item["updated_at"]),
        )
