"""Kafka Event Streaming - Event-driven architecture with Apache Kafka."""

from kafka_event_streaming.producer import KafkaEventProducer
from kafka_event_streaming.consumer import KafkaEventConsumer
from kafka_event_streaming.schemas import BaseEvent, OrderEvent, UserEvent

__all__ = [
    "KafkaEventProducer",
    "KafkaEventConsumer",
    "BaseEvent",
    "OrderEvent",
    "UserEvent",
]
