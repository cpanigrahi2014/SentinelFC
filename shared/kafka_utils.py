"""Shared Kafka producer/consumer utilities."""

import json
import logging
from typing import Any, Callable, Optional

from aiokafka import AIOKafkaConsumer, AIOKafkaProducer

logger = logging.getLogger(__name__)


class KafkaConfig:
    """Kafka connection configuration."""

    def __init__(
        self,
        bootstrap_servers: str = "localhost:9092",
        group_id: Optional[str] = None,
    ):
        self.bootstrap_servers = bootstrap_servers
        self.group_id = group_id


class EventProducer:
    """Async Kafka event producer."""

    def __init__(self, config: KafkaConfig):
        self.config = config
        self._producer: Optional[AIOKafkaProducer] = None

    async def start(self):
        self._producer = AIOKafkaProducer(
            bootstrap_servers=self.config.bootstrap_servers,
            value_serializer=lambda v: json.dumps(v, default=str).encode("utf-8"),
            key_serializer=lambda k: k.encode("utf-8") if k else None,
        )
        await self._producer.start()
        logger.info("Kafka producer started")

    async def stop(self):
        if self._producer:
            await self._producer.stop()
            logger.info("Kafka producer stopped")

    async def send(self, topic: str, value: dict, key: Optional[str] = None):
        if not self._producer:
            raise RuntimeError("Producer not started")
        await self._producer.send_and_wait(topic=topic, value=value, key=key)
        logger.debug(f"Event sent to topic={topic}")


class EventConsumer:
    """Async Kafka event consumer."""

    def __init__(self, config: KafkaConfig, topics: list[str]):
        self.config = config
        self.topics = topics
        self._consumer: Optional[AIOKafkaConsumer] = None
        self._handlers: dict[str, list[Callable]] = {}

    def on_event(self, topic: str):
        """Decorator to register an event handler for a topic."""
        def decorator(func: Callable):
            if topic not in self._handlers:
                self._handlers[topic] = []
            self._handlers[topic].append(func)
            return func
        return decorator

    async def start(self):
        self._consumer = AIOKafkaConsumer(
            *self.topics,
            bootstrap_servers=self.config.bootstrap_servers,
            group_id=self.config.group_id,
            value_deserializer=lambda v: json.loads(v.decode("utf-8")),
            auto_offset_reset="latest",
        )
        await self._consumer.start()
        logger.info(f"Kafka consumer started for topics={self.topics}")

    async def stop(self):
        if self._consumer:
            await self._consumer.stop()
            logger.info("Kafka consumer stopped")

    async def consume(self):
        """Main consumption loop - dispatches messages to registered handlers."""
        if not self._consumer:
            raise RuntimeError("Consumer not started")
        async for message in self._consumer:
            topic = message.topic
            handlers = self._handlers.get(topic, [])
            for handler in handlers:
                try:
                    await handler(message.value)
                except Exception:
                    logger.exception(f"Error handling message from topic={topic}")


def serialize_event(event: Any) -> dict:
    """Convert a Pydantic model to a Kafka-serializable dict."""
    if hasattr(event, "model_dump"):
        return event.model_dump(mode="json")
    return dict(event)
