"""DynamoDB Stream record deserializer.

Converts DynamoDB wire format (with type descriptors) to Python objects.
"""

from decimal import Decimal
from typing import Any


def deserialize_value(value: dict[str, Any]) -> Any:
    """Deserialize a single DynamoDB attribute value.

    DynamoDB values are represented as {"TYPE": value} where TYPE is:
    - S: String
    - N: Number (stored as string)
    - B: Binary
    - BOOL: Boolean
    - NULL: Null
    - L: List
    - M: Map
    - SS: String Set
    - NS: Number Set
    - BS: Binary Set

    Args:
        value: DynamoDB attribute value with type descriptor

    Returns:
        Deserialized Python value
    """
    if not value:
        return None

    type_key = list(value.keys())[0]
    type_value = value[type_key]

    if type_key == "S":
        return type_value
    elif type_key == "N":
        # Use Decimal for precision
        return Decimal(type_value)
    elif type_key == "B":
        return type_value  # Binary, keep as-is
    elif type_key == "BOOL":
        return type_value
    elif type_key == "NULL":
        return None
    elif type_key == "L":
        return [deserialize_value(item) for item in type_value]
    elif type_key == "M":
        return deserialize_dynamodb_item(type_value)
    elif type_key == "SS":
        return set(type_value)
    elif type_key == "NS":
        return {Decimal(n) for n in type_value}
    elif type_key == "BS":
        return set(type_value)
    else:
        raise ValueError(f"Unknown DynamoDB type: {type_key}")


def deserialize_dynamodb_item(item: dict[str, Any]) -> dict[str, Any]:
    """Deserialize a complete DynamoDB item.

    Args:
        item: DynamoDB item with typed attributes

    Returns:
        Python dictionary with deserialized values

    Example:
        >>> item = {"name": {"S": "Alice"}, "age": {"N": "30"}}
        >>> deserialize_dynamodb_item(item)
        {"name": "Alice", "age": Decimal("30")}
    """
    if not item:
        return {}

    return {key: deserialize_value(value) for key, value in item.items()}


def deserialize_stream_record(record: dict[str, Any]) -> dict[str, Any]:
    """Deserialize a DynamoDB Streams record.

    Extracts and deserializes Keys, NewImage, and OldImage from a stream record.

    Args:
        record: Raw stream record from Lambda event

    Returns:
        Dictionary with deserialized keys and images

    Example:
        >>> record = {
        ...     "eventName": "MODIFY",
        ...     "dynamodb": {
        ...         "Keys": {"PK": {"S": "USER#123"}, "SK": {"S": "PROFILE#123"}},
        ...         "NewImage": {"name": {"S": "Alice"}, ...},
        ...         "OldImage": {"name": {"S": "Alice Smith"}, ...}
        ...     }
        ... }
        >>> result = deserialize_stream_record(record)
        >>> result["keys"]
        {"PK": "USER#123", "SK": "PROFILE#123"}
    """
    dynamodb = record.get("dynamodb", {})

    result: dict[str, Any] = {
        "event_id": record.get("eventID"),
        "event_name": record.get("eventName"),
        "event_source": record.get("eventSource"),
        "aws_region": record.get("awsRegion"),
        "keys": deserialize_dynamodb_item(dynamodb.get("Keys", {})),
        "sequence_number": dynamodb.get("SequenceNumber"),
        "size_bytes": dynamodb.get("SizeBytes"),
        "stream_view_type": dynamodb.get("StreamViewType"),
    }

    # Optional fields based on stream view type
    if "NewImage" in dynamodb:
        result["new_image"] = deserialize_dynamodb_item(dynamodb["NewImage"])

    if "OldImage" in dynamodb:
        result["old_image"] = deserialize_dynamodb_item(dynamodb["OldImage"])

    # Approximate creation time (Unix epoch)
    if "ApproximateCreationDateTime" in dynamodb:
        result["approximate_creation_time"] = dynamodb["ApproximateCreationDateTime"]

    return result


def serialize_value(value: Any) -> dict[str, Any]:
    """Serialize a Python value to DynamoDB format.

    Args:
        value: Python value to serialize

    Returns:
        DynamoDB attribute value with type descriptor
    """
    if value is None:
        return {"NULL": True}
    elif isinstance(value, bool):
        return {"BOOL": value}
    elif isinstance(value, str):
        return {"S": value}
    elif isinstance(value, (int, float, Decimal)):
        return {"N": str(value)}
    elif isinstance(value, bytes):
        return {"B": value}
    elif isinstance(value, list):
        return {"L": [serialize_value(item) for item in value]}
    elif isinstance(value, dict):
        return {"M": serialize_dynamodb_item(value)}
    elif isinstance(value, set):
        # Determine set type from first element
        sample = next(iter(value))
        if isinstance(sample, str):
            return {"SS": list(value)}
        elif isinstance(sample, (int, float, Decimal)):
            return {"NS": [str(n) for n in value]}
        elif isinstance(sample, bytes):
            return {"BS": list(value)}
    raise TypeError(f"Cannot serialize type: {type(value)}")


def serialize_dynamodb_item(item: dict[str, Any]) -> dict[str, dict[str, Any]]:
    """Serialize a Python dictionary to DynamoDB item format.

    Args:
        item: Python dictionary

    Returns:
        DynamoDB item with typed attributes
    """
    return {key: serialize_value(value) for key, value in item.items()}
