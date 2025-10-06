"""
Big Five Personality Model

The OCEAN model with five core traits:
- Openness (O): Imagination & Creativity
- Conscientiousness (C): Organization & Dependability
- Extraversion (E): Sociability & Energy
- Agreeableness (A): Cooperation & Empathy
- Neuroticism (N): Emotional Stability (inverted)
"""

from pydantic import BaseModel, Field, field_validator


class BigFiveProfile(BaseModel):
    """
    Big Five personality traits (0-100 scale)

    Each trait influences agent behavior:
    - High Openness: Creative, curious, open to new ideas
    - High Conscientiousness: Organized, responsible, plans ahead
    - High Extraversion: Outgoing, energetic, seeks interaction
    - High Agreeableness: Cooperative, compassionate, trusting
    - High Neuroticism: Anxious, emotionally reactive, sensitive
    """

    openness: int = Field(ge=0, le=100, description="Imagination & creativity")
    conscientiousness: int = Field(ge=0, le=100, description="Organization & dependability")
    extraversion: int = Field(ge=0, le=100, description="Sociability & energy")
    agreeableness: int = Field(ge=0, le=100, description="Cooperation & empathy")
    neuroticism: int = Field(ge=0, le=100, description="Emotional reactivity")

    @field_validator("openness", "conscientiousness", "extraversion", "agreeableness", "neuroticism")
    @classmethod
    def validate_range(cls, v: int) -> int:
        """Ensure traits are within 0-100 range"""
        if not 0 <= v <= 100:
            raise ValueError("Personality traits must be between 0 and 100")
        return v

    def get_response_probability(self, event_type: str, is_direct: bool) -> float:
        """
        Calculate probability of responding based on personality

        Args:
            event_type: Type of event received
            is_direct: Whether the message is directly addressed to agent

        Returns:
            Probability (0.0-1.0) of responding
        """
        if is_direct:
            return 1.0  # Always respond to direct messages

        # Base probability influenced by extraversion
        base_prob = self.extraversion / 100.0

        # Adjust based on other traits
        if event_type == "question":
            base_prob *= (1.0 + self.agreeableness / 200.0)  # More agreeable = more helpful
        elif event_type == "propose":
            base_prob *= (1.0 + self.conscientiousness / 200.0)  # More conscientious = more engaged

        return min(base_prob, 1.0)

    def get_emotional_reactivity(self) -> float:
        """
        Get emotional reactivity coefficient (0.0-1.0)
        Higher neuroticism = more reactive emotions
        """
        return self.neuroticism / 100.0

    def get_creativity_factor(self) -> float:
        """
        Get creativity coefficient (0.0-1.0)
        Higher openness = more creative/unconventional responses
        """
        return self.openness / 100.0

    def get_social_initiative(self) -> float:
        """
        Get likelihood of initiating conversations (0.0-1.0)
        Higher extraversion = more likely to start conversations
        """
        return self.extraversion / 100.0

    def get_conflict_tolerance(self) -> float:
        """
        Get tolerance for disagreement (0.0-1.0)
        Lower agreeableness + lower neuroticism = higher tolerance
        """
        return 1.0 - ((self.agreeableness + self.neuroticism) / 200.0)

    def to_prompt_description(self) -> str:
        """
        Generate natural language description for LLM prompts
        """
        traits = []

        # Openness
        if self.openness >= 70:
            traits.append("highly creative and open to new ideas")
        elif self.openness <= 30:
            traits.append("practical and conventional in thinking")

        # Conscientiousness
        if self.conscientiousness >= 70:
            traits.append("organized, responsible, and detail-oriented")
        elif self.conscientiousness <= 30:
            traits.append("spontaneous and flexible")

        # Extraversion
        if self.extraversion >= 70:
            traits.append("outgoing, energetic, and socially engaged")
        elif self.extraversion <= 30:
            traits.append("reserved, introspective, and thoughtful")

        # Agreeableness
        if self.agreeableness >= 70:
            traits.append("cooperative, empathetic, and harmony-seeking")
        elif self.agreeableness <= 30:
            traits.append("direct, competitive, and willing to challenge others")

        # Neuroticism
        if self.neuroticism >= 70:
            traits.append("emotionally sensitive and reactive")
        elif self.neuroticism <= 30:
            traits.append("emotionally stable and resilient")

        return f"You are {', '.join(traits)}."

    class Config:
        json_schema_extra = {
            "example": {
                "openness": 85,
                "conscientiousness": 80,
                "extraversion": 95,
                "agreeableness": 60,
                "neuroticism": 20
            }
        }
