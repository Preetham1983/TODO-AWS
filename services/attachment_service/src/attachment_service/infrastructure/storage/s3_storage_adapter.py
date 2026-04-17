"""S3 Storage Adapter – concrete implementation of StorageServiceInterface.

Connects to AWS S3 (or LocalStack) using boto3.
This is the only file that knows about S3/boto3.

LocalStack connection guide
───────────────────────────
1. Set AWS_ENDPOINT_URL to http://localstack:4566 (inside Docker)
   or http://localhost:4566 (from host machine).
2. Use dummy credentials (aws_access_key_id=test, aws_secret_access_key=test).
3. The init_localstack.sh script creates the bucket on first run.
4. For pre-signed URLs to work from the browser, the URL host must be
   reachable.  In Docker Compose we expose port 4566 on the host.
"""

from __future__ import annotations

import logging
from functools import cached_property

import boto3
from botocore.config import Config as BotoConfig
from botocore.exceptions import ClientError

from src.attachment_service.config.settings import AttachmentServiceSettings
from src.attachment_service.domain.entities.attachment_entity import AttachmentEntity
from src.attachment_service.domain.interfaces.storage_service_interface import (
    StorageServiceInterface,
)

logger = logging.getLogger(__name__)


class S3StorageAdapter(StorageServiceInterface):
    """Boto3-backed S3 adapter targeting LocalStack or real AWS."""

    def __init__(self, settings: AttachmentServiceSettings) -> None:
        self._settings = settings

    # ── Lazy S3 client (singleton per adapter instance) ──────────────────────

    @cached_property
    def _client(self):
        """Create and cache a boto3 S3 client.

        For LocalStack we need:
        - endpoint_url pointing at the LocalStack container
        - s3 addressing_style = 'path' (virtual-hosted style won't resolve)
        """
        logger.info(
            "Connecting to S3 at %s (region=%s)",
            self._settings.aws_endpoint_url,
            self._settings.aws_region,
        )
        return boto3.client(
            "s3",
            region_name=self._settings.aws_region,
            aws_access_key_id=self._settings.aws_access_key_id,
            aws_secret_access_key=self._settings.aws_secret_access_key,
            endpoint_url=self._settings.aws_endpoint_url,
            config=BotoConfig(s3={"addressing_style": "path"}),
        )

    # ── Interface implementations ────────────────────────────────────────────

    async def upload_file(
        self,
        entity: AttachmentEntity,
        file_content: bytes,
    ) -> AttachmentEntity:
        self._client.put_object(
            Bucket=self._settings.s3_bucket_name,
            Key=entity.s3_key,
            Body=file_content,
            ContentType=entity.content_type,
        )
        logger.debug("Uploaded %s to s3://%s/%s",
                      entity.filename, self._settings.s3_bucket_name, entity.s3_key)
        return entity

    async def download_file(self, s3_key: str) -> bytes:
        response = self._client.get_object(
            Bucket=self._settings.s3_bucket_name,
            Key=s3_key,
        )
        return response["Body"].read()

    async def delete_file(self, s3_key: str) -> bool:
        try:
            self._client.delete_object(
                Bucket=self._settings.s3_bucket_name,
                Key=s3_key,
            )
            return True
        except ClientError:
            logger.exception("Failed to delete %s", s3_key)
            return False

    async def generate_presigned_url(self, s3_key: str) -> str:
        """Generate a pre-signed GET URL.

        NOTE: For LocalStack, the returned URL will contain the internal
        Docker hostname.  When calling from the browser you may need to
        replace 'localstack' with 'localhost' via the frontend proxy or
        a simple URL rewrite.
        """
        url: str = self._client.generate_presigned_url(
            "get_object",
            Params={
                "Bucket": self._settings.s3_bucket_name,
                "Key": s3_key,
            },
            ExpiresIn=self._settings.s3_presigned_url_expiry,
        )
        # Rewrite internal hostname for browser accessibility
        return url.replace("http://localstack:", "http://localhost:")

    async def ensure_bucket_exists(self) -> None:
        """Idempotently create the S3 bucket."""
        try:
            self._client.head_bucket(Bucket=self._settings.s3_bucket_name)
            logger.info("Bucket '%s' already exists", self._settings.s3_bucket_name)
        except ClientError:
            logger.info("Creating bucket '%s'", self._settings.s3_bucket_name)
            self._client.create_bucket(Bucket=self._settings.s3_bucket_name)
