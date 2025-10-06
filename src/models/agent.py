"""
Agent Profile and State Models
"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

from .personality import BigFiveProfile
from .emotion import EmotionalState


class AgentProfile(BaseModel):
    """
    Static agent profile information
    """

    id: str = Field(description="Unique agent identifier")
    name: str = Field(description="Agent name")
    personality: BigFiveProfile = Field(description="Big Five personality profile")
    description: Optional[str] = Field(
        None,
        description="Brief description of agent's role/archetype"
    )
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Agent creation timestamp"
    )
    is_active: bool = Field(
        default=True,
        description="Whether agent is currently active"
    )

    def to_prompt_description(self) -> str:
        """
        Generate full description for LLM system prompt

        Returns:
            Description string including name, role, and personality
        """
        parts = [f"You are {self.name}."]

        if self.description:
            parts.append(self.description)

        parts.append(self.personality.to_prompt_description())

        return " ".join(parts)

    class Config:
        json_schema_extra = {
            "example": {
                "id": "agent-1",
                "name": "Alex",
                "personality": {
                    "openness": 85,
                    "conscientiousness": 80,
                    "extraversion": 95,
                    "agreeableness": 60,
                    "neuroticism": 20
                },
                "description": "The Extroverted Leader - takes charge in group discussions",
                "created_at": "2025-01-15T10:00:00.000Z",
                "is_active": True
            }
        }


class AgentState(BaseModel):
    """
    Dynamic agent state (runtime information)

    Stored in Redis with TTL
    """

    agent_id: str = Field(description="Agent identifier")
    status: str = Field(
        default="idle",
        description="Current status: idle, processing, active"
    )
    emotional_state: EmotionalState = Field(
        default_factory=EmotionalState,
        description="Current emotional state"
    )
    last_activity: datetime = Field(
        default_factory=datetime.utcnow,
        description="Last activity timestamp"
    )
    active_conversations: list[str] = Field(
        default_factory=list,
        description="IDs of active conversation threads"
    )
    messages_sent: int = Field(
        default=0,
        description="Total messages sent in current session"
    )
    messages_received: int = Field(
        default=0,
        description="Total messages received in current session"
    )

    def update_activity(self) -> None:
        """Update last activity timestamp"""
        self.last_activity = datetime.utcnow()

    def set_status(self, status: str) -> None:
        """
        Update agent status

        Args:
            status: New status (idle, processing, active)
        """
        self.status = status
        self.update_activity()

    def increment_sent(self) -> None:
        """Increment sent message counter"""
        self.messages_sent += 1
        self.update_activity()

    def increment_received(self) -> None:
        """Increment received message counter"""
        self.messages_received += 1
        self.update_activity()

    def add_conversation(self, conversation_id: str) -> None:
        """Add active conversation"""
        if conversation_id not in self.active_conversations:
            self.active_conversations.append(conversation_id)
        self.update_activity()

    def remove_conversation(self, conversation_id: str) -> None:
        """Remove conversation from active list"""
        if conversation_id in self.active_conversations:
            self.active_conversations.remove(conversation_id)
        self.update_activity()

    class Config:
        json_schema_extra = {
            "example": {
                "agent_id": "agent-1",
                "status": "active",
                "emotional_state": {
                    "valence": 0.6,
                    "arousal": 0.7
                },
                "last_activity": "2025-01-15T10:30:45.123Z",
                "active_conversations": ["conv_123", "conv_456"],
                "messages_sent": 15,
                "messages_received": 23
            }
        }
