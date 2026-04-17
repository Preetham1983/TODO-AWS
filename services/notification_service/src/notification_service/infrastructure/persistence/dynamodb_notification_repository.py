"""DynamoDB Notification Repository – stores notification logs in DynamoDB.

Email dispatch is handled by SesEmailAdapter.  This adapter only
persists the *record* of each notification so logs survive restarts.

Table schema
────────────
  Partition key : id  (S)
"""

from __future__ import annotations

import logging
from datetime import datetime
from functools import cached_property
from typing import Any

import boto3
from botocore.exceptions import ClientError

from src.notification_service.config.settings import NotificationServiceSettings
from src.notification_service.domain.entities.notification_entity import (
    NotificationEntity,
    NotificationStatus,
    NotificationType,
)
from src.notification_service.domain.interfaces.notification_repository_interface import (
    NotificationRepositoryInterface,
)

logger = logging.getLogger(__name__)


class DynamoDbNotificationRepository(NotificationRepositoryInterface):
    """DynamoDB-backed notification log persistence."""

    def __init__(self, settings: NotificationServiceSettings) -> None:
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
        return self._resource.Table(self._settings.dynamodb_notifications_table)

    # ── Interface implementations ────────────────────────────────────────────

    async def save(self, entity: NotificationEntity) -> NotificationEntity:
        item = self._entity_to_item(entity)
        self._table.put_item(Item=item)
        logger.debug("Stored notification %s in DynamoDB", entity.id)
        return entity

    async def get_by_id(self, notification_id: str) -> NotificationEntity | None:
        try:
            response = self._table.get_item(Key={"id": notification_id})
        except ClientError:
            logger.exception("Failed to get notification %s", notification_id)
            return None
        item = response.get("Item")
        return self._item_to_entity(item) if item else None

    async def get_all(self) -> list[NotificationEntity]:
        items: list[dict[str, Any]] = []
        response = self._table.scan()
        items.extend(response.get("Items", []))

        while "LastEvaluatedKey" in response:
            response = self._table.scan(
                ExclusiveStartKey=response["LastEvaluatedKey"]
            )
            items.extend(response.get("Items", []))

        return [self._item_to_entity(item) for item in items]

    async def ensure_table_exists(self) -> None:
        table_name = self._settings.dynamodb_notifications_table
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
                ],
                BillingMode="PAY_PER_REQUEST",
            )
            self._table.wait_until_exists()

    # ── Serialisation helpers ────────────────────────────────────────────────

    @staticmethod
    def _entity_to_item(entity: NotificationEntity) -> dict[str, Any]:
        return {
            "id": entity.id,
            "recipient_email": entity.recipient_email,
            "subject": entity.subject,
            "body_text": entity.body_text,
            "body_html": entity.body_html,
            "notification_type": entity.notification_type.value,
            "status": entity.status.value,
            "todo_id": entity.todo_id or "",
            "ses_message_id": entity.ses_message_id or "",
            "created_at": entity.created_at.isoformat(),
        }

    @staticmethod
    def _item_to_entity(item: dict[str, Any]) -> NotificationEntity:
        return NotificationEntity(
            id=item["id"],
            recipient_email=item["recipient_email"],
            subject=item["subject"],
            body_text=item.get("body_text", ""),
            body_html=item.get("body_html", ""),
            notification_type=NotificationType(item["notification_type"]),
            status=NotificationStatus(item["status"]),
            todo_id=item.get("todo_id") or None,
            ses_message_id=item.get("ses_message_id") or None,
            created_at=datetime.fromisoformat(item["created_at"]),
        )
