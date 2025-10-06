"""
Simple Decision Engine for MVP

Determines when and how agents respond based on personality.
"""

import random
import logging
from typing import Optional, Dict, Any

from ..models.personality import BigFiveProfile
from ..models.event import Event, EventType

logger = logging.getLogger(__name__)


class SimpleDecisionEngine:
    """
    Simple decision engine for MVP

    Determines:
    1. Should agent respond to this event?
    2. What type of response is appropriate?

    Future: Add more sophisticated decision logic, learning, etc.
    """

    def __init__(self, personality: BigFiveProfile):
        """
        Initialize decision engine

        Args:
            personality: Agent's personality profile
        """
        self.personality = personality

    def should_respond(
        self,
        event: Event,
        agent_id: str,
        relationship_strength: float = 0.5
    ) -> bool:
        """
        Decide if agent should respond to event

        Args:
            event: Incoming event
            agent_id: This agent's ID
            relationship_strength: Strength of relationship with sender (0-1)

        Returns:
            True if agent should respond
        """
        # Don't respond to own messages
        if event.source_id == agent_id:
            return False

        # Always respond to direct messages
        if event.is_direct_message(agent_id):
            return True

        # System messages - always process
        if event.type == EventType.SYSTEM:
            return True

        # Calculate response probability based on personality
        base_prob = self.personality.get_response_probability(
            event_type=event.type.value,
            is_direct=False
        )

        # Adjust for relationship strength
        adjusted_prob = base_prob * relationship_strength

        # Random decision
        should_respond = random.random() < adjusted_prob

        logger.debug(
            f"Response decision: {should_respond} "
            f"(prob={adjusted_prob:.2f}, base={base_prob:.2f})"
        )

        return should_respond

    def get_response_style(self) -> Dict[str, Any]:
        """
        Get response style based on personality

        Returns:
            Dict with style parameters for LLM
        """
        return {
            "temperature": 0.7 + (self.personality.openness / 200.0),  # 0.7-1.2
            "creativity": self.personality.get_creativity_factor(),
            "verbosity": "high" if self.personality.extraversion > 70 else
                        "low" if self.personality.extraversion < 30 else "medium"
        }
