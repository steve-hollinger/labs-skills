---
name: integrating-aws-services
description: Integrate AWS services (DynamoDB, S3, Secrets Manager) with boto3 and proper retry logic. Use when building Python services that interact with AWS.
tags: ['python', 'aws', 'boto3', 'dynamodb', 's3', 'secrets']
---

# AWS Service Clients

## Quick Start
```python
# src/client/dynamodb_client.py
import boto3
from botocore.exceptions import ClientError
from typing import Optional, Dict, Any

class DynamoDBClient:
    """DynamoDB client with single-table design support."""

    def __init__(self, table_name: str, region: str = "us-east-1"):
        self.table_name = table_name
        self.dynamodb = boto3.resource("dynamodb", region_name=region)
        self.table = self.dynamodb.Table(table_name)

    def get_item(self, pk: str, sk: str) -> Optional[Dict[str, Any]]:
        """Get item using partition and sort key."""
        try:
            response = self.table.get_item(Key={"PK": pk, "SK": sk})
            return response.get("Item")
        except ClientError as e:
            if e.response["Error"]["Code"] == "ResourceNotFoundException":
                return None
            raise

    def put_item(self, item: Dict[str, Any]) -> bool:
        """Put item with automatic retry on throttling."""
        self.table.put_item(Item=item)
        return True
```

## Key Points
- Use boto3 resource interface for DynamoDB operations (simpler than client)
- Single-table design: All entities share one table with PK/SK pattern
- Implement retry decorators for transient failures (throttling, network errors)
- Use IAM roles from FSD deployments, never hardcode credentials
- Async operations with aioboto3 prevent blocking event loops in services

## Common Mistakes
1. **Using client instead of resource for DynamoDB** - boto3.client() requires manual marshalling/unmarshalling. Use boto3.resource() for automatic Python type conversion.
2. **Hardcoding AWS credentials** - Never use access keys in code. Rely on IAM roles assigned via FSD service definitions.
3. **Not handling throttling errors** - DynamoDB returns ProvisionedThroughputExceededException. Always implement exponential backoff with retry decorators.
4. **Loading large S3 objects into memory** - Use streaming with download_fileobj() or generate presigned URLs for client-side downloads.
5. **Blocking calls in async services** - boto3 is synchronous. Use aioboto3 for async/await compatibility in FastAPI or async handlers.

## More Detail
- [docs/concepts.md](docs/concepts.md) - Core concepts and theory
- [docs/patterns.md](docs/patterns.md) - Full code patterns and examples
