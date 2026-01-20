"""DynamoDB Schema Design - Labs Skills.

This module provides utilities and examples for DynamoDB schema design patterns
including single-table design, GSIs, LSIs, and access pattern modeling.
"""

from dynamodb_schema.models import (
    BaseEntity,
    Order,
    OrderItem,
    Product,
    User,
)
from dynamodb_schema.schema import (
    DynamoDBSchema,
    create_composite_key,
    create_gsi_key,
)

__all__ = [
    "BaseEntity",
    "User",
    "Order",
    "OrderItem",
    "Product",
    "DynamoDBSchema",
    "create_composite_key",
    "create_gsi_key",
]
