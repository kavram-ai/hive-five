"""
Event Model - Core communication unit between agents
"""

from datetime import datetime
from enum import Enum
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field
import uuid


class EventType(str, Enum):
    """Types of events in the system"""

    # Social Events
    MESSAGE = "message"           # General conversation
    QUESTION = "question"         # Asking for information
    ANSWER = "answer"            # Responding to question

    # Action Events
    PROPOSE = "propose"          # Suggesting an idea/action
    AGREE = "agree"              # Supporting a proposal
    DISAGREE = "disagree"        # Opposing a proposal

    # Emotional Events
    EMOTION = "emotion"          # Expressing feeling
    SUPPORT = "support"          # Emotional support

    # System Events
    JOIN = "join"                # Agent enters conversation
    LEAVE = "leave"              # Agent exits conversation
    SYSTEM = "system"            # System-generated event


class EventMetadata(BaseModel):
    """Metadata attached to events"""

    reasoning: Optional[str] = Field(
        None,
        description="Internal reasoning behind the event (not visible to other agents)"
    )
    confidence: Optional[float] = Field(
        None,
        ge=0.0,
        le=1.0,
        description="Confidence level of the agent (0.0-1.0)"
    )
    mood_valence: Optional[float] = Field(
        None,
        ge=-1.0,
        le=1.0,
        description="Agent's mood valence at time of event (-1.0 to 1.0)"
    )
    mood_arousal: Optional[float] = Field(
        None,
        ge=0.0,
        le=1.0,
        description="Agent's mood arousal at time of event (0.0-1.0)"
    )
    related_event_id: Optional[str] = Field(
        None,
        description="ID of event this is responding to"
    )
    conversation_id: Optional[str] = Field(
        None,
        description="Conversation thread identifier"
    )

    # Additional custom fields
    extra: Dict[str, Any] = Field(default_factory=dict)


class Event(BaseModel):
    """
    Core event model for agent communication

    Events are the fundamental unit of communication in the system.
    All agent interactions happen through events published to Kafka.
    """

    id: str = Field(
        default_factory=lambda: f"evt_{uuid.uuid4().hex[:12]}",
        description="Unique event identifier"
    )
    type: EventType = Field(description="Type of event")
    source_id: str = Field(description="ID of agent sending the event")
    target_id: str = Field(
        default="all",
        description="Target agent ID or 'all' for broadcast"
    )
    content: str = Field(description="Event content/message")
    metadata: EventMetadata = Field(
        default_factory=EventMetadata,
        description="Additional event metadata"
    )
    timestamp: datetime = Field(
        default_factory=datetime.utcnow,
        description="Event creation timestamp (UTC)"
    )

    def is_broadcast(self) -> bool:
        """Check if event is a broadcast to all agents"""
        return self.target_id == "all"

    def is_targeted(self, agent_id: str) -> bool:
        """Check if event targets specific agent"""
        return self.target_id == agent_id or self.is_broadcast()

    def is_direct_message(self, agent_id: str) -> bool:
        """Check if event is a direct message to specific agent"""
        return self.target_id == agent_id

    def to_kafka_message(self) -> str:
        """Serialize event to JSON string for Kafka"""
        return self.model_dump_json()

    @classmethod
    def from_kafka_message(cls, message: str) -> "Event":
        """Deserialize event from Kafka JSON message"""
        return cls.model_validate_json(message)

    def to_display_string(self) -> str:
        """Format event for human-readable display"""
        timestamp_str = self.timestamp.strftime("%H:%M:%S")
        target_str = f"→ {self.target_id}" if not self.is_broadcast() else "→ all"
        return f"[{timestamp_str}] {self.source_id} {target_str}: {self.content}"

    def to_context_string(self) -> str:
        """
        Format event for LLM context
        Simplified version without metadata
        """
        return f"{self.source_id}: {self.content}"

    class Config:
        json_schema_extra = {
            "example": {
                "id": "evt_abc123def456",
                "type": "message",
                "source_id": "agent-1",
                "target_id": "all",
                "content": "What do you all think about implementing feature X?",
                "metadata": {
                    "reasoning": "Taking initiative as group leader",
                    "confidence": 0.85,
                    "mood_valence": 0.7,
                    "mood_arousal": 0.6
                },
                "timestamp": "2025-01-15T10:30:45.123Z"
            }
        }


def create_system_event(content: str, target_id: str = "all") -> Event:
    """Helper to create system-generated events"""
    return Event(
        type=EventType.SYSTEM,
        source_id="system",
        target_id=target_id,
        content=content
    )
