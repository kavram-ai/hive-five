"""
Kafka Service - Producer/Consumer infrastructure for agent communication

Handles all Kafka interactions with proper error handling and monitoring.
"""

import asyncio
import logging
from typing import Callable, Optional, List
from confluent_kafka import Producer, Consumer, KafkaError, KafkaException
from confluent_kafka.admin import AdminClient, NewTopic

from ..models.event import Event

logger = logging.getLogger(__name__)


class KafkaService:
    """
    Kafka service for agent event bus

    Features:
    - Async producer for sending events
    - Async consumer for receiving events
    - Topic management
    - Error handling with callbacks
    """

    def __init__(
        self,
        bootstrap_servers: str,
        consumer_group: str = "agent-system",
        auto_offset_reset: str = "latest"
    ):
        """
        Initialize Kafka service

        Args:
            bootstrap_servers: Kafka broker addresses
            consumer_group: Consumer group ID
            auto_offset_reset: Where to start consuming (earliest/latest)
        """
        self.bootstrap_servers = bootstrap_servers
        self.consumer_group = consumer_group
        self.auto_offset_reset = auto_offset_reset

        self.producer: Optional[Producer] = None
        self.consumer: Optional[Consumer] = None
        self._running = False

    async def start_producer(self):
        """Initialize Kafka producer"""
        config = {
            'bootstrap.servers': self.bootstrap_servers,
            'client.id': 'hive-five-producer'
        }

        self.producer = Producer(config)
        logger.info("Kafka producer started")

    async def start_consumer(self, topics: List[str]):
        """
        Initialize Kafka consumer

        Args:
            topics: List of topics to subscribe to
        """
        config = {
            'bootstrap.servers': self.bootstrap_servers,
            'group.id': self.consumer_group,
            'auto.offset.reset': self.auto_offset_reset,
            'enable.auto.commit': True
        }

        self.consumer = Consumer(config)
        self.consumer.subscribe(topics)
        logger.info(f"Kafka consumer started, subscribed to: {topics}")

    async def close(self):
        """Close producer and consumer"""
        self._running = False

        if self.producer:
            self.producer.flush()
            logger.info("Kafka producer closed")

        if self.consumer:
            self.consumer.close()
            logger.info("Kafka consumer closed")

    async def publish_event(self, topic: str, event: Event) -> bool:
        """
        Publish event to Kafka topic

        Args:
            topic: Kafka topic name
            event: Event to publish

        Returns:
            True if successful, False otherwise
        """
        if not self.producer:
            logger.error("Producer not started")
            return False

        try:
            # Serialize event to JSON
            message = event.to_kafka_message()

            # Use agent ID as key for partitioning
            key = event.source_id.encode('utf-8')
            value = message.encode('utf-8')

            # Async produce
            self.producer.produce(
                topic=topic,
                key=key,
                value=value,
                callback=self._delivery_callback
            )

            # Trigger callback processing
            self.producer.poll(0)

            return True

        except Exception as e:
            logger.error(f"Failed to publish event: {e}")
            return False

    def _delivery_callback(self, err, msg):
        """Callback for delivery reports"""
        if err:
            logger.error(f"Message delivery failed: {err}")
        else:
            logger.debug(f"Message delivered to {msg.topic()} [{msg.partition()}]")

    async def consume_events(
        self,
        callback: Callable[[Event], None],
        timeout: float = 1.0
    ):
        """
        Consume events from subscribed topics

        Args:
            callback: Function to call for each event
            timeout: Poll timeout in seconds
        """
        if not self.consumer:
            logger.error("Consumer not started")
            return

        self._running = True

        try:
            while self._running:
                # Poll for messages
                msg = self.consumer.poll(timeout=timeout)

                if msg is None:
                    # No message, continue
                    await asyncio.sleep(0.01)
                    continue

                if msg.error():
                    if msg.error().code() == KafkaError._PARTITION_EOF:
                        # End of partition, not an error
                        continue
                    else:
                        logger.error(f"Consumer error: {msg.error()}")
                        continue

                try:
                    # Deserialize event
                    message_value = msg.value().decode('utf-8')
                    event = Event.from_kafka_message(message_value)

                    # Call callback
                    await callback(event)

                except Exception as e:
                    logger.error(f"Error processing message: {e}")

        except KeyboardInterrupt:
            logger.info("Consumer interrupted")
        finally:
            self._running = False


class KafkaTopics:
    """Standard Kafka topics"""
    MESSAGES = "agent.messages"
    ACTIONS = "agent.actions"
    INTERNAL = "agent.internal"
    CONTROL = "system.control"

    @classmethod
    def all_topics(cls) -> List[str]:
        """Get all topic names"""
        return [cls.MESSAGES, cls.ACTIONS, cls.INTERNAL, cls.CONTROL]


async def create_topics(bootstrap_servers: str):
    """
    Create Kafka topics if they don't exist

    Args:
        bootstrap_servers: Kafka broker addresses
    """
    admin_client = AdminClient({'bootstrap.servers': bootstrap_servers})

    topics = [
        NewTopic(topic, num_partitions=3, replication_factor=1)
        for topic in KafkaTopics.all_topics()
    ]

    try:
        # Create topics
        fs = admin_client.create_topics(topics)

        # Wait for operations to finish
        for topic, f in fs.items():
            try:
                f.result()  # Raises exception if topic creation failed
                logger.info(f"Topic {topic} created")
            except KafkaException as e:
                if e.args[0].code() == KafkaError.TOPIC_ALREADY_EXISTS:
                    logger.info(f"Topic {topic} already exists")
                else:
                    logger.error(f"Failed to create topic {topic}: {e}")

    except Exception as e:
        logger.error(f"Failed to create topics: {e}")
