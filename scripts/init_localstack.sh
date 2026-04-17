#!/bin/bash
# =============================================================================
# LocalStack Initialization Script
# Creates S3 buckets, DynamoDB tables, and verifies SES email identities
# =============================================================================

set -euo pipefail

echo "============================================="
echo "  Initializing LocalStack Resources"
echo "============================================="

ENDPOINT="http://localhost:4566"
REGION="us-east-1"

# ── S3: Create attachment bucket ─────────────────────────────────────────────
echo ""
echo "→ Creating S3 bucket: todo-attachments"
awslocal s3 mb s3://todo-attachments --region "$REGION" 2>/dev/null || true

echo "→ Configuring CORS on S3 bucket"
awslocal s3api put-bucket-cors \
    --bucket todo-attachments \
    --cors-configuration '{
        "CORSRules": [
            {
                "AllowedOrigins": ["*"],
                "AllowedMethods": ["GET", "PUT", "POST", "DELETE", "HEAD"],
                "AllowedHeaders": ["*"],
                "MaxAgeSeconds": 3600
            }
        ]
    }' --region "$REGION"

echo "✓ S3 bucket 'todo-attachments' created and configured"

# ── DynamoDB: Create tables ──────────────────────────────────────────────────
echo ""
echo "→ Creating DynamoDB table: todos"
awslocal dynamodb create-table \
    --table-name todos \
    --attribute-definitions \
        AttributeName=id,AttributeType=S \
    --key-schema \
        AttributeName=id,KeyType=HASH \
    --billing-mode PAY_PER_REQUEST \
    --region "$REGION" 2>/dev/null || true

echo "✓ DynamoDB table 'todos' created"

echo ""
echo "→ Creating DynamoDB table: attachments"
awslocal dynamodb create-table \
    --table-name attachments \
    --attribute-definitions \
        AttributeName=id,AttributeType=S \
        AttributeName=todo_id,AttributeType=S \
    --key-schema \
        AttributeName=id,KeyType=HASH \
    --global-secondary-indexes \
        'IndexName=todo_id_index,KeySchema=[{AttributeName=todo_id,KeyType=HASH}],Projection={ProjectionType=ALL}' \
    --billing-mode PAY_PER_REQUEST \
    --region "$REGION" 2>/dev/null || true

echo "✓ DynamoDB table 'attachments' created (with GSI on todo_id)"

echo ""
echo "→ Creating DynamoDB table: notifications"
awslocal dynamodb create-table \
    --table-name notifications \
    --attribute-definitions \
        AttributeName=id,AttributeType=S \
    --key-schema \
        AttributeName=id,KeyType=HASH \
    --billing-mode PAY_PER_REQUEST \
    --region "$REGION" 2>/dev/null || true

echo "✓ DynamoDB table 'notifications' created"

# ── SES: Verify email identities ────────────────────────────────────────────
echo ""
echo "→ Verifying SES email identity: todo-app@example.com"
awslocal ses verify-email-identity \
    --email-address "todo-app@example.com" \
    --region "$REGION"

echo "→ Verifying SES email identity: bandipreethamreddy16@gmail.com"
awslocal ses verify-email-identity \
    --email-address "bandipreethamreddy16@gmail.com" \
    --region "$REGION"

echo "✓ SES email identities verified"

# ── Verify resources ────────────────────────────────────────────────────────
echo ""
echo "============================================="
echo "  Verification"
echo "============================================="
echo ""

echo "S3 Buckets:"
awslocal s3 ls --region "$REGION"

echo ""
echo "DynamoDB Tables:"
awslocal dynamodb list-tables --region "$REGION"

echo ""
echo "SES Verified Identities:"
awslocal ses list-identities --region "$REGION"

echo ""
echo "============================================="
echo "  LocalStack initialization complete!"
echo "============================================="
