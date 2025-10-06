"""
Relationship Model - Tracks relationships between agents
"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class Relationship(BaseModel):
    """
    Dynamic relationship between two agents

    Relationships evolve over time based on interactions:
    - Trust: Built through positive interactions
    - Familiarity: Increases with any interaction
    - Affinity: Can be positive or negative based on agreement/conflict
    """

    agent_id: str = Field(description="Primary agent ID")
    other_agent_id: str = Field(description="Related agent ID")

    trust: float = Field(
        default=0.5,
        ge=0.0,
        le=1.0,
        description="Trust level (0.0-1.0)"
    )
    familiarity: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Familiarity level (0.0-1.0)"
    )
    affinity: float = Field(
        default=0.0,
        ge=-1.0,
        le=1.0,
        description="Affinity/liking (-1.0 to 1.0)"
    )

    interaction_count: int = Field(
        default=0,
        description="Total number of interactions"
    )
    last_contact: Optional[datetime] = Field(
        None,
        description="Last interaction timestamp"
    )

    def update_from_event(
        self,
        event_type: str,
        is_positive: bool,
        agreeableness: float
    ) -> None:
        """
        Update relationship based on an interaction event

        Args:
            event_type: Type of event (message, agree, disagree, etc.)
            is_positive: Whether interaction was positive
            agreeableness: Agent's agreeableness trait (0.0-1.0)
        """
        self.interaction_count += 1
        self.last_contact = datetime.utcnow()

        # Increase familiarity with any interaction
        familiarity_gain = 0.01 + (0.02 * agreeableness)
        self.familiarity = min(1.0, self.familiarity + familiarity_gain)

        # Update trust based on interaction type
        if event_type == "agree":
            self.trust = min(1.0, self.trust + 0.05)
            self.affinity = min(1.0, self.affinity + 0.03)
        elif event_type == "support":
            self.trust = min(1.0, self.trust + 0.08)
            self.affinity = min(1.0, self.affinity + 0.05)
        elif event_type == "disagree":
            # Disagreement doesn't always hurt trust
            # High agreeableness = more sensitive to disagreement
            trust_impact = -0.02 * agreeableness
            self.trust = max(0.0, self.trust + trust_impact)

            affinity_impact = -0.03 * agreeableness
            self.affinity = max(-1.0, self.affinity + affinity_impact)

        # Positive interactions generally improve relationship
        if is_positive:
            self.trust = min(1.0, self.trust + 0.02)
            self.affinity = min(1.0, self.affinity + 0.02)

    def decay(self, days_since_contact: float) -> None:
        """
        Decay relationship strength over time without contact

        Args:
            days_since_contact: Days since last interaction
        """
        if days_since_contact > 1.0:
            # Familiarity decays slowly
            decay_rate = 0.01 * days_since_contact
            self.familiarity = max(0.0, self.familiarity - decay_rate)

            # Trust decays back to neutral
            if self.trust > 0.5:
                self.trust = max(0.5, self.trust - decay_rate)

            # Affinity decays toward neutral
            if self.affinity > 0:
                self.affinity = max(0.0, self.affinity - decay_rate * 0.5)
            elif self.affinity < 0:
                self.affinity = min(0.0, self.affinity + decay_rate * 0.5)

    def get_relationship_strength(self) -> float:
        """
        Calculate overall relationship strength (0.0-1.0)

        Returns:
            Composite relationship strength
        """
        # Weight: trust=40%, familiarity=30%, affinity=30%
        return (
            self.trust * 0.4 +
            self.familiarity * 0.3 +
            (self.affinity + 1.0) / 2.0 * 0.3  # Normalize affinity to 0-1
        )

    def get_relationship_label(self) -> str:
        """
        Get human-readable relationship description

        Returns:
            Relationship label
        """
        strength = self.get_relationship_strength()

        if strength > 0.8:
            return "close friend"
        elif strength > 0.6:
            return "friend"
        elif strength > 0.4:
            return "acquaintance"
        elif strength > 0.2:
            return "distant"
        else:
            if self.affinity < -0.5:
                return "antagonist"
            else:
                return "stranger"

    def influences_response_probability(self) -> float:
        """
        Get modifier for response probability based on relationship

        Returns:
            Multiplier for response probability (0.5-1.5)
        """
        strength = self.get_relationship_strength()

        # Stronger relationships increase response likelihood
        return 0.5 + strength

    def to_prompt_description(self, other_name: str) -> str:
        """
        Generate description for LLM prompt

        Args:
            other_name: Name of the other agent

        Returns:
            Description string
        """
        label = self.get_relationship_label()

        trust_desc = "trust them" if self.trust > 0.7 else \
                     "are wary of them" if self.trust < 0.3 else \
                     "are neutral toward them"

        return f"Your relationship with {other_name}: {label}. You {trust_desc}."

    class Config:
        json_schema_extra = {
            "example": {
                "agent_id": "agent-1",
                "other_agent_id": "agent-2",
                "trust": 0.7,
                "familiarity": 0.8,
                "affinity": 0.5,
                "interaction_count": 42,
                "last_contact": "2025-01-15T10:30:45.123Z"
            }
        }
