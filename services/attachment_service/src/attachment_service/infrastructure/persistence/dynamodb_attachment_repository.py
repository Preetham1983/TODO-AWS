"""DynamoDB Attachment Repository – stores attachment metadata in DynamoDB.

File bytes live in S3 (handled by S3StorageAdapter).
This adapter only persists the metadata record so that the in-memory
index is no longer needed – data survives container restarts.

Table schema
────────────
  Partition key : id       (S)
  GSI           : todo_id_index  (partition key = todo_id)
"""

from __future__ import annotations

import logging
from datetime import datetime
from functools import cached_property
from typing import Any

import boto3
from boto3.dynamodb.conditions import Key
from botocore.exceptions import ClientError

from src.attachment_service.config.settings import AttachmentServiceSettings
from src.attachment_service.domain.entities.attachment_entity import AttachmentEntity
from src.attachment_service.domain.interfaces.attachment_repository_interface import (
    AttachmentRepositoryInterface,
)

logger = logging.getLogger(__name__)


class DynamoDbAttachmentRepository(AttachmentRepositoryInterface):
    """DynamoDB-backed attachment metadata persistence."""

    def __init__(self, settings: AttachmentServiceSettings) -> None:
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
        return self._resource.Table(self._settings.dynamodb_attachments_table)

    # ── Interface implementations ────────────────────────────────────────────

    async def save(self, entity: AttachmentEntity) -> AttachmentEntity:
        item = self._entity_to_item(entity)
        self._table.put_item(Item=item)
        logger.debug("Stored attachment metadata %s in DynamoDB", entity.id)
        return entity

    async def get_by_id(self, attachment_id: str) -> AttachmentEntity | None:
        try:
            response = self._table.get_item(Key={"id": attachment_id})
        except ClientError:
            logger.exception("Failed to get attachment %s", attachment_id)
            return None
        item = response.get("Item")
        return self._item_to_entity(item) if item else None

    async def list_by_todo_id(self, todo_id: str) -> list[AttachmentEntity]:
        """Query the GSI to get all attachments for a TODO."""
        try:
            response = self._table.query(
                IndexName="todo_id_index",
                KeyConditionExpression=Key("todo_id").eq(todo_id),
            )
            return [self._item_to_entity(item) for item in response.get("Items", [])]
        except ClientError:
            logger.exception("Failed to list attachments for todo %s", todo_id)
            return []

    async def delete(self, attachment_id: str) -> AttachmentEntity | None:
        # Get first so we can return the entity for S3 cleanup
        entity = await self.get_by_id(attachment_id)
        if not entity:
            return None
        try:
            self._table.delete_item(Key={"id": attachment_id})
            return entity
        except ClientError:
            logger.exception("Failed to delete attachment %s", attachment_id)
            return None

    async def ensure_table_exists(self) -> None:
        """Idempotently create the DynamoDB table with GSI."""
        table_name = self._settings.dynamodb_attachments_table
        try:
            self._table.table_status  # noqa: B018
            logger.info("DynamoDB table '%s' exists", table_name)
        except ClientError:
            logger.info("Creating DynamoDB table '%s'", table_name)
            self._resource.create_table(
                TableName=table_name,
                KeySchema=[{"AttributeName": "id", "KeyType": "HASH"}],
                AttributeDefinitions=[
                    {"AttributeName": "id", "AttributeType": "S"},
                    {"AttributeName": "todo_id", "AttributeType": "S"},
                ],
                GlobalSecondaryIndexes=[
                    {
                        "IndexName": "todo_id_index",
                        "KeySchema": [
                            {"AttributeName": "todo_id", "KeyType": "HASH"},
                        ],
                        "Projection": {"ProjectionType": "ALL"},
                    }
                ],
                BillingMode="PAY_PER_REQUEST",
            )
            self._table.wait_until_exists()

    # ── Serialisation helpers ────────────────────────────────────────────────

    @staticmethod
    def _entity_to_item(entity: AttachmentEntity) -> dict[str, Any]:
        return {
            "id": entity.id,
            "todo_id": entity.todo_id,
            "filename": entity.filename,
            "content_type": entity.content_type,
            "size_bytes": entity.size_bytes,
            "s3_key": entity.s3_key,
            "download_url": entity.download_url,
            "created_at": entity.created_at.isoformat(),
        }

    @staticmethod
    def _item_to_entity(item: dict[str, Any]) -> AttachmentEntity:
        return AttachmentEntity(
            id=item["id"],
            todo_id=item["todo_id"],
            filename=item["filename"],
            content_type=item.get("content_type", "application/octet-stream"),
            size_bytes=int(item.get("size_bytes", 0)),
            s3_key=item.get("s3_key", ""),
            download_url=item.get("download_url", ""),
            created_at=datetime.fromisoformat(item["created_at"]),
        )
