"""SES Email Adapter – concrete implementation of EmailServiceInterface.

Connects to AWS SES (or LocalStack) using boto3.

LocalStack SES connection guide
────────────────────────────────
1. Set AWS_ENDPOINT_URL to http://localstack:4566 (inside Docker)
   or http://localhost:4566 (from host machine).
2. Use dummy credentials (aws_access_key_id=test, aws_secret_access_key=test).
3. Before sending, the sender email must be "verified" – even on LocalStack.
   The init_localstack.sh script runs `awslocal ses verify-email-identity` for you.
4. On LocalStack, emails are not actually delivered.  You can inspect them
   at http://localhost:4566/_aws/ses (the SES developer endpoint).
"""

from __future__ import annotations

import logging
from functools import cached_property

import boto3
from botocore.exceptions import ClientError

from src.notification_service.config.settings import NotificationServiceSettings
from src.notification_service.domain.entities.notification_entity import (
    NotificationEntity,
)
from src.notification_service.domain.interfaces.email_service_interface import (
    EmailServiceInterface,
)

logger = logging.getLogger(__name__)


class SesEmailAdapter(EmailServiceInterface):
    """Boto3-backed SES adapter targeting LocalStack or real AWS."""

    def __init__(self, settings: NotificationServiceSettings) -> None:
        self._settings = settings

    # ── Lazy SES client ──────────────────────────────────────────────────────

    @cached_property
    def _client(self):
        """Create and cache a boto3 SES client."""
        logger.info(
            "Connecting to SES at %s (region=%s)",
            self._settings.aws_endpoint_url,
            self._settings.aws_region,
        )
        return boto3.client(
            "ses",
            region_name=self._settings.aws_region,
            aws_access_key_id=self._settings.aws_access_key_id,
            aws_secret_access_key=self._settings.aws_secret_access_key,
            endpoint_url=self._settings.aws_endpoint_url,
        )

    # ── Interface implementations ────────────────────────────────────────────

    async def send_email(self, notification: NotificationEntity) -> str:
        """Send an email via SES and return the MessageId."""
        try:
            response = self._client.send_email(
                Source=self._settings.ses_sender_email,
                Destination={
                    "ToAddresses": [notification.recipient_email],
                },
                Message={
                    "Subject": {
                        "Data": notification.subject,
                        "Charset": "UTF-8",
                    },
                    "Body": {
                        "Text": {
                            "Data": notification.body_text,
                            "Charset": "UTF-8",
                        },
                        "Html": {
                            "Data": notification.body_html,
                            "Charset": "UTF-8",
                        },
                    },
                },
            )
            message_id: str = response["MessageId"]
            logger.debug(
                "SES email sent: MessageId=%s, To=%s",
                message_id,
                notification.recipient_email,
            )
            return message_id

        except ClientError as exc:
            logger.error("SES send_email failed: %s", exc)
            raise

    async def verify_sender_identity(self) -> None:
        """Idempotently verify the configured sender email on SES.

        On LocalStack this succeeds instantly.  On real AWS this triggers
        a verification email that the owner must click.
        """
        try:
            self._client.verify_email_identity(
                EmailAddress=self._settings.ses_sender_email,
            )
            logger.info(
                "Verification requested for '%s'",
                self._settings.ses_sender_email,
            )
        except ClientError:
            logger.exception("Failed to verify sender identity")

    async def list_verified_identities(self) -> list[str]:
        """Return all verified email addresses / domains."""
        try:
            response = self._client.list_identities(IdentityType="EmailAddress")
            identities: list[str] = response.get("Identities", [])
            return identities
        except ClientError:
            logger.exception("Failed to list SES identities")
            return []
