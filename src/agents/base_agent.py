"""
Base Agent Implementation

Core agent with personality-driven behavior and event processing.
"""

import asyncio
import logging
from typing import Optional

from ..models.agent import AgentProfile, AgentState
from ..models.event import Event, EventType, EventMetadata
from ..models.emotion import EmotionalState
from ..services.llm_client import GLMClient
from ..services.kafka_service import KafkaService, KafkaTopics
from .memory import SimpleMemory
from .decision_engine import SimpleDecisionEngine

logger = logging.getLogger(__name__)


class Agent:
    """
    Core agent with personality-driven behavior

    Each agent runs in its own event loop, processing incoming events
    and generating responses based on personality and emotional state.
    """

    def __init__(
        self,
        profile: AgentProfile,
        llm_client: GLMClient,
        kafka_service: KafkaService
    ):
        """
        Initialize agent

        Args:
            profile: Agent profile with personality
            llm_client: LLM client for response generation
            kafka_service: Kafka service for communication
        """
        self.profile = profile
        self.llm = llm_client
        self.kafka = kafka_service

        # State
        self.state = AgentState(agent_id=profile.id)
        self.emotional_state = EmotionalState()

        # Components
        self.memory = SimpleMemory(max_size=10)
        self.decision_engine = SimpleDecisionEngine(profile.personality)

        # Runtime
        self.inbox: asyncio.Queue[Event] = asyncio.Queue()
        self._running = False
        self._task: Optional[asyncio.Task] = None

        logger.info(f"Agent {self.profile.name} ({self.profile.id}) initialized")

    async def start(self):
        """Start agent event processing loop"""
        if self._running:
            logger.warning(f"Agent {self.profile.name} already running")
            return

        self._running = True
        self._task = asyncio.create_task(self._run())
        logger.info(f"Agent {self.profile.name} started")

    async def stop(self):
        """Stop agent gracefully"""
        if not self._running:
            return

        self._running = False

        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass

        logger.info(f"Agent {self.profile.name} stopped")

    async def _run(self):
        """Main event processing loop"""
        self.state.set_status("active")

        try:
            while self._running:
                try:
                    # Wait for event with timeout
                    event = await asyncio.wait_for(
                        self.inbox.get(),
                        timeout=1.0
                    )

                    # Process event
                    await self._process_event(event)

                except asyncio.TimeoutError:
                    # No event, continue
                    continue

        except asyncio.CancelledError:
            logger.info(f"Agent {self.profile.name} cancelled")
        except Exception as e:
            logger.error(f"Agent {self.profile.name} error: {e}", exc_info=True)
        finally:
            self.state.set_status("idle")

    async def _process_event(self, event: Event):
        """
        Process incoming event

        Args:
            event: Event to process
        """
        logger.info(f"[{self.profile.name}] Received: {event.to_display_string()}")

        # Update state
        self.state.increment_received()

        # Store in memory
        self.memory.add_event(event)

        # Update emotional state based on event
        self._update_emotion(event)

        # Decide if we should respond
        should_respond = self.decision_engine.should_respond(
            event=event,
            agent_id=self.profile.id
        )

        if not should_respond:
            logger.debug(f"[{self.profile.name}] Decided not to respond")
            return

        # Generate response
        self.state.set_status("processing")
        response_event = await self._generate_response(event)
        self.state.set_status("active")

        if response_event:
            # Send response
            await self._send_event(response_event)

    def _update_emotion(self, event: Event):
        """
        Update emotional state based on event

        Args:
            event: Incoming event
        """
        # Simple emotion update logic
        valence_delta = 0.0
        arousal_delta = 0.0

        if event.type == EventType.AGREE:
            valence_delta = 0.1
            arousal_delta = 0.05
        elif event.type == EventType.DISAGREE:
            valence_delta = -0.1
            arousal_delta = 0.1
        elif event.type == EventType.SUPPORT:
            valence_delta = 0.15
            arousal_delta = -0.05
        elif event.type == EventType.QUESTION:
            arousal_delta = 0.05

        # Apply personality-based reactivity
        neuroticism = self.profile.personality.neuroticism / 100.0

        self.emotional_state.update(
            valence_delta=valence_delta,
            arousal_delta=arousal_delta,
            neuroticism=neuroticism
        )

        logger.debug(
            f"[{self.profile.name}] Emotion: {self.emotional_state.get_emotional_label()} "
            f"(v={self.emotional_state.valence:.2f}, a={self.emotional_state.arousal:.2f})"
        )

    async def _generate_response(self, event: Event) -> Optional[Event]:
        """
        Generate response using LLM

        Args:
            event: Event to respond to

        Returns:
            Response event or None
        """
        try:
            # Get context
            context = self.memory.get_recent_context(n=5)

            # Build prompts
            personality_desc = self.profile.personality.to_prompt_description()
            emotion_desc = self.emotional_state.to_prompt_description()

            # Get response style
            style = self.decision_engine.get_response_style()

            # Call LLM
            response = await self.llm.generate_agent_response(
                agent_name=self.profile.name,
                personality_desc=personality_desc,
                emotion_desc=emotion_desc,
                context=context,
                event_content=event.content,
                event_type=event.type.value,
                source_name=event.source_id,
                temperature=style["temperature"]
            )

            if not response:
                logger.error(f"[{self.profile.name}] LLM returned no response")
                return None

            # Check if agent decided to ignore
            if response.get("action") == "ignore":
                logger.info(f"[{self.profile.name}] Decided to ignore")
                return None

            # Create response event
            response_event = Event(
                type=EventType(response.get("action", "message")),
                source_id=self.profile.id,
                target_id=response.get("target", "all"),
                content=response.get("content", ""),
                metadata=EventMetadata(
                    reasoning=response.get("reasoning"),
                    mood_valence=self.emotional_state.valence,
                    mood_arousal=self.emotional_state.arousal,
                    related_event_id=event.id
                )
            )

            return response_event

        except Exception as e:
            logger.error(f"[{self.profile.name}] Error generating response: {e}")
            return None

    async def _send_event(self, event: Event):
        """
        Send event to Kafka

        Args:
            event: Event to send
        """
        # Store in memory
        self.memory.add_event(event)

        # Update state
        self.state.increment_sent()

        # Publish to Kafka
        success = await self.kafka.publish_event(KafkaTopics.MESSAGES, event)

        if success:
            logger.info(f"[{self.profile.name}] Sent: {event.to_display_string()}")
        else:
            logger.error(f"[{self.profile.name}] Failed to send event")

    async def receive_event(self, event: Event):
        """
        Receive event from Kafka (called by orchestrator)

        Args:
            event: Event to process
        """
        # Only process events targeted to this agent or broadcast
        if event.is_targeted(self.profile.id):
            await self.inbox.put(event)
