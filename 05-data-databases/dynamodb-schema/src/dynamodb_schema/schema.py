"""DynamoDB Schema Design Utilities.

This module provides utilities for working with DynamoDB single-table design
patterns including key generation, GSI management, and table operations.
"""

from typing import Any

import boto3
from botocore.config import Config


def create_composite_key(*components: str, separator: str = "#") -> str:
    """Create a composite key from multiple components.

    Args:
        *components: Key components to join
        separator: Separator between components (default: #)

    Returns:
        Composite key string

    Example:
        >>> create_composite_key("USER", "123")
        'USER#123'
        >>> create_composite_key("ORDER", "2024-01-15", "456")
        'ORDER#2024-01-15#456'
    """
    return separator.join(components)


def create_gsi_key(
    entity_type: str,
    attribute_value: str,
    gsi_number: int = 1,
    key_type: str = "PK",
) -> tuple[str, str]:
    """Create a GSI key attribute name and value.

    Args:
        entity_type: Type prefix for the key
        attribute_value: Value to include in key
        gsi_number: GSI number (1, 2, etc.)
        key_type: Either 'PK' or 'SK'

    Returns:
        Tuple of (attribute_name, attribute_value)

    Example:
        >>> create_gsi_key("STATUS", "pending", gsi_number=1, key_type="PK")
        ('GSI1PK', 'STATUS#pending')
    """
    attr_name = f"GSI{gsi_number}{key_type}"
    attr_value = create_composite_key(entity_type, attribute_value)
    return attr_name, attr_value


class DynamoDBSchema:
    """Utility class for DynamoDB table operations with single-table design."""

    def __init__(
        self,
        table_name: str,
        region: str = "us-east-1",
        endpoint_url: str | None = None,
    ) -> None:
        """Initialize DynamoDB schema utility.

        Args:
            table_name: Name of the DynamoDB table
            region: AWS region
            endpoint_url: Optional endpoint URL for local DynamoDB
        """
        self.table_name = table_name
        self.region = region
        self.endpoint_url = endpoint_url

        config = Config(
            retries={"max_attempts": 3, "mode": "adaptive"},
        )

        self.dynamodb = boto3.resource(
            "dynamodb",
            region_name=region,
            endpoint_url=endpoint_url,
            config=config,
        )
        self.client = boto3.client(
            "dynamodb",
            region_name=region,
            endpoint_url=endpoint_url,
            config=config,
        )
        self._table: Any | None = None

    @property
    def table(self) -> Any:
        """Get the DynamoDB table resource."""
        if self._table is None:
            self._table = self.dynamodb.Table(self.table_name)
        return self._table

    def create_table(
        self,
        gsi_definitions: list[dict[str, Any]] | None = None,
        lsi_definitions: list[dict[str, Any]] | None = None,
    ) -> None:
        """Create the DynamoDB table with optional GSIs and LSIs.

        Args:
            gsi_definitions: List of GSI definitions
            lsi_definitions: List of LSI definitions
        """
        key_schema = [
            {"AttributeName": "PK", "KeyType": "HASH"},
            {"AttributeName": "SK", "KeyType": "RANGE"},
        ]

        attribute_definitions = [
            {"AttributeName": "PK", "AttributeType": "S"},
            {"AttributeName": "SK", "AttributeType": "S"},
        ]

        # Add GSI attribute definitions
        if gsi_definitions:
            for gsi in gsi_definitions:
                for key in gsi["KeySchema"]:
                    attr_name = key["AttributeName"]
                    if not any(a["AttributeName"] == attr_name for a in attribute_definitions):
                        attribute_definitions.append(
                            {"AttributeName": attr_name, "AttributeType": "S"}
                        )

        # Add LSI attribute definitions
        if lsi_definitions:
            for lsi in lsi_definitions:
                for key in lsi["KeySchema"]:
                    attr_name = key["AttributeName"]
                    if not any(a["AttributeName"] == attr_name for a in attribute_definitions):
                        attribute_definitions.append(
                            {"AttributeName": attr_name, "AttributeType": "S"}
                        )

        create_params: dict[str, Any] = {
            "TableName": self.table_name,
            "KeySchema": key_schema,
            "AttributeDefinitions": attribute_definitions,
            "BillingMode": "PAY_PER_REQUEST",
        }

        if gsi_definitions:
            create_params["GlobalSecondaryIndexes"] = gsi_definitions

        if lsi_definitions:
            create_params["LocalSecondaryIndexes"] = lsi_definitions

        self.client.create_table(**create_params)

        # Wait for table to be active
        waiter = self.client.get_waiter("table_exists")
        waiter.wait(TableName=self.table_name)

    def delete_table(self) -> None:
        """Delete the DynamoDB table."""
        self.client.delete_table(TableName=self.table_name)

    def put_item(self, item: dict[str, Any]) -> dict[str, Any]:
        """Put an item into the table.

        Args:
            item: Item to put (must include PK and SK)

        Returns:
            DynamoDB response
        """
        return self.table.put_item(Item=item)

    def get_item(self, pk: str, sk: str) -> dict[str, Any] | None:
        """Get an item by its primary key.

        Args:
            pk: Partition key
            sk: Sort key

        Returns:
            Item if found, None otherwise
        """
        response = self.table.get_item(Key={"PK": pk, "SK": sk})
        return response.get("Item")

    def query(
        self,
        pk: str,
        sk_prefix: str | None = None,
        index_name: str | None = None,
        scan_forward: bool = True,
        limit: int | None = None,
    ) -> list[dict[str, Any]]:
        """Query items by partition key with optional sort key prefix.

        Args:
            pk: Partition key value
            sk_prefix: Optional sort key prefix for begins_with
            index_name: Optional GSI/LSI name
            scan_forward: Sort order (True=ascending, False=descending)
            limit: Maximum items to return

        Returns:
            List of matching items
        """
        query_params: dict[str, Any] = {
            "ScanIndexForward": scan_forward,
        }

        if index_name:
            query_params["IndexName"] = index_name
            pk_attr = f"{index_name.upper()}PK" if index_name.startswith("GSI") else "PK"
            sk_attr = f"{index_name.upper()}SK" if index_name.startswith("GSI") else "SK"
        else:
            pk_attr = "PK"
            sk_attr = "SK"

        if sk_prefix:
            query_params["KeyConditionExpression"] = (
                f"{pk_attr} = :pk AND begins_with({sk_attr}, :sk_prefix)"
            )
            query_params["ExpressionAttributeValues"] = {
                ":pk": pk,
                ":sk_prefix": sk_prefix,
            }
        else:
            query_params["KeyConditionExpression"] = f"{pk_attr} = :pk"
            query_params["ExpressionAttributeValues"] = {":pk": pk}

        if limit:
            query_params["Limit"] = limit

        response = self.table.query(**query_params)
        return response.get("Items", [])

    def query_gsi(
        self,
        index_name: str,
        pk_value: str,
        sk_prefix: str | None = None,
        scan_forward: bool = True,
        limit: int | None = None,
    ) -> list[dict[str, Any]]:
        """Query a Global Secondary Index.

        Args:
            index_name: Name of the GSI (e.g., 'GSI1')
            pk_value: Partition key value
            sk_prefix: Optional sort key prefix
            scan_forward: Sort order
            limit: Maximum items to return

        Returns:
            List of matching items
        """
        pk_attr = f"{index_name}PK"
        sk_attr = f"{index_name}SK"

        query_params: dict[str, Any] = {
            "IndexName": index_name,
            "ScanIndexForward": scan_forward,
        }

        if sk_prefix:
            query_params["KeyConditionExpression"] = (
                f"{pk_attr} = :pk AND begins_with({sk_attr}, :sk_prefix)"
            )
            query_params["ExpressionAttributeValues"] = {
                ":pk": pk_value,
                ":sk_prefix": sk_prefix,
            }
        else:
            query_params["KeyConditionExpression"] = f"{pk_attr} = :pk"
            query_params["ExpressionAttributeValues"] = {":pk": pk_value}

        if limit:
            query_params["Limit"] = limit

        response = self.table.query(**query_params)
        return response.get("Items", [])

    def batch_write(self, items: list[dict[str, Any]]) -> None:
        """Batch write multiple items.

        Args:
            items: List of items to write
        """
        with self.table.batch_writer() as batch:
            for item in items:
                batch.put_item(Item=item)

    def transact_write(self, items: list[dict[str, Any]]) -> dict[str, Any]:
        """Write multiple items in a transaction.

        Args:
            items: List of items to write transactionally

        Returns:
            DynamoDB response
        """
        transact_items = [
            {
                "Put": {
                    "TableName": self.table_name,
                    "Item": self._serialize_item(item),
                }
            }
            for item in items
        ]

        return self.client.transact_write_items(TransactItems=transact_items)

    def _serialize_item(self, item: dict[str, Any]) -> dict[str, dict[str, Any]]:
        """Serialize an item for DynamoDB client operations.

        Args:
            item: Item to serialize

        Returns:
            Serialized item with DynamoDB type descriptors
        """
        serialized: dict[str, dict[str, Any]] = {}
        for key, value in item.items():
            if isinstance(value, str):
                serialized[key] = {"S": value}
            elif isinstance(value, (int, float)):
                serialized[key] = {"N": str(value)}
            elif isinstance(value, bool):
                serialized[key] = {"BOOL": value}
            elif isinstance(value, list):
                serialized[key] = {"L": [self._serialize_value(v) for v in value]}
            elif isinstance(value, dict):
                serialized[key] = {"M": self._serialize_item(value)}
            elif value is None:
                serialized[key] = {"NULL": True}
        return serialized

    def _serialize_value(self, value: Any) -> dict[str, Any]:
        """Serialize a single value for DynamoDB."""
        if isinstance(value, str):
            return {"S": value}
        elif isinstance(value, (int, float)):
            return {"N": str(value)}
        elif isinstance(value, bool):
            return {"BOOL": value}
        elif isinstance(value, list):
            return {"L": [self._serialize_value(v) for v in value]}
        elif isinstance(value, dict):
            return {"M": self._serialize_item(value)}
        elif value is None:
            return {"NULL": True}
        return {"S": str(value)}
