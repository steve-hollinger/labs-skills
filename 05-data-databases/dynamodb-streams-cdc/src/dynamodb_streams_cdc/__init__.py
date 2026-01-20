"""DynamoDB Streams CDC - Labs Skills.

This module provides utilities and examples for DynamoDB Streams
change data capture patterns including stream processing, event-driven
architectures, and Lambda triggers.
"""

from dynamodb_streams_cdc.deserializer import (
    deserialize_dynamodb_item,
    deserialize_stream_record,
)
from dynamodb_streams_cdc.processor import (
    StreamProcessor,
    StreamRecord,
    process_stream_event,
)

__all__ = [
    "StreamProcessor",
    "StreamRecord",
    "process_stream_event",
    "deserialize_dynamodb_item",
    "deserialize_stream_record",
]
