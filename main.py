"""
Hive Five - Main Orchestrator

MVP version: Start agents, trigger conversation, watch them interact.
"""

import asyncio
import logging
import signal
import sys

from src.utils.logging import setup_logging
from src.utils.config import Config
from src.services.llm_client import GLMClient
from src.services.kafka_service import KafkaService, KafkaTopics, create_topics
from src.agents.agent_factory import create_all_agents
from src.models.event import create_system_event

logger = logging.getLogger(__name__)


class HiveFive:
    """
    Main orchestrator for the multi-agent system
    """

    def __init__(self, config: Config):
        """
        Initialize the system

        Args:
            config: Application configuration
        """
        self.config = config
        self.agents = []
        self.llm_client = None
        self.kafka_service = None
        self._shutdown = False

    async def start(self):
        """Start the system"""
        logger.info("🐝 Starting Hive Five Multi-Agent System")

        # Initialize services
        await self._init_services()

        # Create agents
        self._create_agents()

        # Start agents
        await self._start_agents()

        # Start Kafka consumer
        consumer_task = asyncio.create_task(self._consume_events())

        # Send initial trigger
        await self._send_initial_trigger()

        logger.info("✅ System ready - agents are interacting!")
        logger.info("Press Ctrl+C to stop")

        # Wait for shutdown
        try:
            while not self._shutdown:
                await asyncio.sleep(1.0)
        except KeyboardInterrupt:
            logger.info("Received shutdown signal")

        # Cleanup
        await self.stop()

    async def _init_services(self):
        """Initialize core services"""
        logger.info("Initializing services...")

        # Create Kafka topics
        await create_topics(self.config.kafka_bootstrap_servers)

        # Initialize LLM client
        self.llm_client = GLMClient(
            api_key=self.config.glm_api_key,
            api_url=self.config.glm_api_url,
            model=self.config.glm_model
        )
        await self.llm_client.start()

        # Initialize Kafka service
        self.kafka_service = KafkaService(
            bootstrap_servers=self.config.kafka_bootstrap_servers,
            consumer_group=self.config.kafka_consumer_group
        )
        await self.kafka_service.start_producer()
        await self.kafka_service.start_consumer([KafkaTopics.MESSAGES])

        logger.info("✓ Services initialized")

    def _create_agents(self):
        """Create all agents"""
        logger.info("Creating agents...")
        self.agents = create_all_agents(self.llm_client, self.kafka_service)
        logger.info(f"✓ Created {len(self.agents)} agents")

        for agent in self.agents:
            logger.info(f"  - {agent.profile.name}: {agent.profile.description}")

    async def _start_agents(self):
        """Start all agents"""
        logger.info("Starting agents...")

        for agent in self.agents:
            await agent.start()

        logger.info("✓ All agents started")

    async def _consume_events(self):
        """Consume events from Kafka and route to agents"""
        logger.info("Starting event consumer...")

        async def route_event(event):
            """Route event to appropriate agents"""
            for agent in self.agents:
                await agent.receive_event(event)

        await self.kafka_service.consume_events(route_event)

    async def _send_initial_trigger(self):
        """Send initial system message to start conversation"""
        logger.info("Sending initial trigger...")

        # Wait a moment for everything to stabilize
        await asyncio.sleep(2)

        # Create initial prompt
        initial_event = create_system_event(
            content="Hello everyone! Let's discuss: What makes a great team collaboration? "
                   "Share your thoughts and perspectives.",
            target_id="all"
        )

        # Publish to Kafka
        await self.kafka_service.publish_event(KafkaTopics.MESSAGES, initial_event)

        logger.info("✓ Initial trigger sent")

    async def stop(self):
        """Stop the system gracefully"""
        logger.info("Stopping Hive Five...")

        # Stop agents
        for agent in self.agents:
            await agent.stop()

        # Close services
        if self.kafka_service:
            await self.kafka_service.close()

        if self.llm_client:
            await self.llm_client.close()

        logger.info("✅ System stopped")


async def main():
    """Main entry point"""
    # Setup logging
    config = Config()
    setup_logging(config.log_level)

    # Check API key
    if not config.glm_api_key or config.glm_api_key == "your-api-key-here":
        logger.error("❌ GLM_API_KEY not set in .env file")
        logger.error("Please copy .env.example to .env and add your API key")
        sys.exit(1)

    # Create and run system
    system = HiveFive(config)

    # Setup signal handlers
    def signal_handler(sig, frame):
        logger.info("Shutdown signal received")
        system._shutdown = True

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    # Run
    try:
        await system.start()
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Interrupted by user")
