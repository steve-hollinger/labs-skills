# Code Patterns: AWS Service Clients

## Pattern 1: DynamoDB with Retry Decorator

**When to Use:** Building services that need resilient DynamoDB access with single-table design. Essential for high-throughput operations during peak hours (receipt scanning, reward redemptions).

```python
# src/database/dynamodb_repository.py
import logging
from functools import wraps
from typing import Optional, Dict, Any, List
import time

import boto3
from botocore.exceptions import ClientError

logger = logging.getLogger(__name__)


def retry_with_backoff(max_attempts: int = 3, base_delay: float = 0.5):
    """Decorator for exponential backoff on throttling errors."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except ClientError as e:
                    error_code = e.response["Error"]["Code"]
                    if error_code == "ProvisionedThroughputExceededException":
                        if attempt < max_attempts - 1:
                            delay = base_delay * (2 ** attempt)
                            logger.warning(f"Throttled, retrying in {delay}s (attempt {attempt + 1}/{max_attempts})")
                            time.sleep(delay)
                            continue
                    logger.error(f"DynamoDB error: {error_code}", exc_info=True)
                    raise
            return None
        return wrapper
    return decorator


class UserRepository:
    """Repository for user data using single-table design."""

    def __init__(self, table_name: str = "fetch-data", region: str = "us-east-1"):
        self.dynamodb = boto3.resource("dynamodb", region_name=region)
        self.table = self.dynamodb.Table(table_name)

    @retry_with_backoff(max_attempts=3, base_delay=0.5)
    def get_user(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user by ID using PK/SK pattern."""
        try:
            response = self.table.get_item(
                Key={
                    "PK": f"USER#{user_id}",
                    "SK": f"USER#{user_id}"
                }
            )
            return response.get("Item")
        except ClientError as e:
            if e.response["Error"]["Code"] == "ResourceNotFoundException":
                logger.warning(f"Table {self.table.table_name} not found")
                return None
            raise

    @retry_with_backoff(max_attempts=3, base_delay=0.5)
    def save_user(self, user_id: str, user_data: Dict[str, Any]) -> bool:
        """Save or update user data."""
        item = {
            "PK": f"USER#{user_id}",
            "SK": f"USER#{user_id}",
            "entity_type": "USER",
            **user_data
        }
        self.table.put_item(Item=item)
        logger.info(f"Saved user {user_id}")
        return True

    @retry_with_backoff(max_attempts=3, base_delay=0.5)
    def get_user_rewards(self, user_id: str) -> List[Dict[str, Any]]:
        """Query all rewards for a user using begins_with on SK."""
        response = self.table.query(
            KeyConditionExpression="PK = :pk AND begins_with(SK, :sk_prefix)",
            ExpressionAttributeValues={
                ":pk": f"USER#{user_id}",
                ":sk_prefix": "REWARD#"
            }
        )
        return response.get("Items", [])
```

**Pitfalls:**
- **Not using PK/SK patterns**: Single-table design requires composite keys. Always prefix partition and sort keys (e.g., `USER#123`, `REWARD#456`).
- **Missing entity_type attribute**: Add `entity_type` to all items for filtering and debugging.
- **Retrying non-idempotent operations**: Only retry reads or idempotent writes. For non-idempotent operations, use condition expressions.

## Pattern 2: S3 Presigned URLs

**When to Use:** Client applications (mobile, web) need direct access to S3 objects without proxying through your API. Common for receipt uploads and image downloads.

```python
# src/storage/s3_client.py
import logging
from datetime import timedelta
from typing import Optional

import boto3
from botocore.exceptions import ClientError
from botocore.client import Config

logger = logging.getLogger(__name__)


class S3Client:
    """S3 client for generating presigned URLs and file operations."""

    def __init__(self, bucket_name: str, region: str = "us-east-1"):
        self.bucket_name = bucket_name
        # Signature version 4 required for presigned URLs
        self.s3_client = boto3.client(
            "s3",
            region_name=region,
            config=Config(signature_version="s3v4")
        )

    def generate_upload_url(
        self,
        key: str,
        expires_in: int = 3600,
        content_type: Optional[str] = None
    ) -> str:
        """Generate presigned URL for uploading to S3.

        Args:
            key: S3 object key (e.g., "receipts/user123/receipt456.jpg")
            expires_in: URL expiration in seconds (default 1 hour)
            content_type: MIME type (e.g., "image/jpeg")

        Returns:
            Presigned URL string
        """
        params = {
            "Bucket": self.bucket_name,
            "Key": key
        }
        if content_type:
            params["ContentType"] = content_type

        try:
            url = self.s3_client.generate_presigned_url(
                ClientMethod="put_object",
                Params=params,
                ExpiresIn=expires_in
            )
            logger.info(f"Generated upload URL for {key}, expires in {expires_in}s")
            return url
        except ClientError as e:
            logger.error(f"Failed to generate upload URL: {e}", exc_info=True)
            raise

    def generate_download_url(self, key: str, expires_in: int = 3600) -> str:
        """Generate presigned URL for downloading from S3."""
        try:
            url = self.s3_client.generate_presigned_url(
                ClientMethod="get_object",
                Params={"Bucket": self.bucket_name, "Key": key},
                ExpiresIn=expires_in
            )
            logger.info(f"Generated download URL for {key}")
            return url
        except ClientError as e:
            logger.error(f"Failed to generate download URL: {e}", exc_info=True)
            raise

    def upload_file(self, local_path: str, key: str) -> bool:
        """Upload file directly from service (for server-side operations)."""
        try:
            self.s3_client.upload_file(local_path, self.bucket_name, key)
            logger.info(f"Uploaded {local_path} to s3://{self.bucket_name}/{key}")
            return True
        except ClientError as e:
            logger.error(f"Upload failed: {e}", exc_info=True)
            return False


# Usage in FastAPI endpoint
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()
s3_client = S3Client(bucket_name="fetch-receipts")


class UploadRequest(BaseModel):
    user_id: str
    filename: str
    content_type: str


@app.post("/api/v1/receipts/upload-url")
def get_receipt_upload_url(request: UploadRequest) -> dict:
    """Return presigned URL for client to upload receipt directly to S3."""
    key = f"receipts/{request.user_id}/{request.filename}"
    try:
        url = s3_client.generate_upload_url(
            key=key,
            expires_in=900,  # 15 minutes
            content_type=request.content_type
        )
        return {"upload_url": url, "key": key}
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to generate upload URL")
```

**Pitfalls:**
- **Wrong signature version**: Presigned URLs require signature version 4. Always set `Config(signature_version="s3v4")`.
- **Not validating content_type**: Enforce content types to prevent abuse. Check uploaded files match the declared type.
- **Long expiration times**: Keep URLs short-lived (15-60 minutes) to limit security exposure.

## Pattern 3: Secrets Manager Integration

**When to Use:** Accessing secrets during service initialization (database credentials, API keys, partner secrets). Essential for secure configuration management without hardcoded values.

```python
# src/config/secrets.py
import json
import logging
from functools import lru_cache
from typing import Dict, Any

import boto3
from botocore.exceptions import ClientError

logger = logging.getLogger(__name__)


class SecretsManager:
    """Secrets Manager client with caching for initialization-time secrets."""

    def __init__(self, region: str = "us-east-1"):
        self.client = boto3.client("secretsmanager", region_name=region)

    @lru_cache(maxsize=128)
    def get_secret(self, secret_name: str) -> str:
        """Get secret value with LRU cache to minimize API calls.

        Args:
            secret_name: Secret ID (e.g., "prod/fetch/database-credentials")

        Returns:
            Secret string (may be JSON-encoded)
        """
        try:
            response = self.client.get_secret_value(SecretId=secret_name)
            logger.info(f"Retrieved secret: {secret_name}")
            return response["SecretString"]
        except ClientError as e:
            error_code = e.response["Error"]["Code"]
            if error_code == "ResourceNotFoundException":
                logger.error(f"Secret not found: {secret_name}")
            elif error_code == "AccessDeniedException":
                logger.error(f"Access denied to secret: {secret_name}")
            else:
                logger.error(f"Secrets Manager error: {error_code}", exc_info=True)
            raise

    def get_secret_json(self, secret_name: str) -> Dict[str, Any]:
        """Get secret and parse as JSON."""
        secret_string = self.get_secret(secret_name)
        return json.loads(secret_string)


# src/config/settings.py
from pydantic_settings import BaseSettings
from functools import cached_property


class Settings(BaseSettings):
    """Application settings with secrets from AWS Secrets Manager."""

    environment: str = "dev"
    aws_region: str = "us-east-1"
    service_name: str = "user-service"

    # FSD provides IAM role with these permissions
    database_secret_name: str = "prod/fetch/postgres-credentials"
    partner_api_secret_name: str = "prod/fetch/partner-api-keys"

    @cached_property
    def database_credentials(self) -> Dict[str, str]:
        """Load database credentials from Secrets Manager."""
        secrets = SecretsManager(region=self.aws_region)
        return secrets.get_secret_json(self.database_secret_name)

    @cached_property
    def database_url(self) -> str:
        """Construct database URL from secrets."""
        creds = self.database_credentials
        return (
            f"postgresql://{creds['username']}:{creds['password']}"
            f"@{creds['host']}:{creds['port']}/{creds['database']}"
        )

    @cached_property
    def partner_api_key(self) -> str:
        """Load partner API key from Secrets Manager."""
        secrets = SecretsManager(region=self.aws_region)
        keys = secrets.get_secret_json(self.partner_api_secret_name)
        return keys["partner_api_key"]


# Usage in service initialization
from contextlib import asynccontextmanager
from fastapi import FastAPI

settings = Settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Load secrets during startup."""
    logger.info("Loading secrets from AWS Secrets Manager...")
    try:
        # Trigger cached_property evaluation during startup
        db_url = settings.database_url
        api_key = settings.partner_api_key
        logger.info("Secrets loaded successfully")
    except Exception as e:
        logger.error(f"Failed to load secrets: {e}", exc_info=True)
        raise

    yield  # Application runs

    logger.info("Shutting down...")


app = FastAPI(lifespan=lifespan)
```

**Pitfalls:**
- **Loading secrets on every request**: Use `@lru_cache` or `@cached_property` to cache secrets loaded during initialization. Don't fetch secrets in request handlers.
- **Not handling missing secrets**: Always catch `ResourceNotFoundException` and fail fast during startup, not during request handling.
- **IAM permission issues**: Ensure FSD service definition includes `secretsmanager:GetSecretValue` permission for the specific secret ARN.
- **Plaintext secrets in logs**: Never log secret values. Only log secret names and success/failure.

---

## Additional Patterns

### Async DynamoDB with aioboto3

For FastAPI services, use async operations to prevent blocking:

```python
import aioboto3
from typing import Optional, Dict, Any


class AsyncUserRepository:
    def __init__(self, table_name: str = "fetch-data", region: str = "us-east-1"):
        self.table_name = table_name
        self.region = region

    async def get_user(self, user_id: str) -> Optional[Dict[str, Any]]:
        session = aioboto3.Session()
        async with session.resource("dynamodb", region_name=self.region) as dynamodb:
            table = await dynamodb.Table(self.table_name)
            response = await table.get_item(
                Key={"PK": f"USER#{user_id}", "SK": f"USER#{user_id}"}
            )
            return response.get("Item")
```

### Batch Operations for DynamoDB

For bulk reads or writes, use batch operations:

```python
def batch_get_users(self, user_ids: List[str]) -> List[Dict[str, Any]]:
    """Get multiple users in a single batch request."""
    response = self.dynamodb.batch_get_item(
        RequestItems={
            self.table.table_name: {
                "Keys": [
                    {"PK": f"USER#{uid}", "SK": f"USER#{uid}"}
                    for uid in user_ids
                ]
            }
        }
    )
    return response["Responses"].get(self.table.table_name, [])
```

