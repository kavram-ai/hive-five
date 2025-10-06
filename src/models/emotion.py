"""
Emotional State Model

Two-dimensional emotion model (Russell's Circumplex Model):
- Valence: Negative (-1.0) to Positive (1.0)
- Arousal: Calm (0.0) to Excited (1.0)
"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class EmotionalState(BaseModel):
    """
    Two-dimensional emotional state model

    Based on Russell's Circumplex Model of Affect:
    - Valence: How positive/negative the emotion is
    - Arousal: How activated/calm the emotion is

    Examples:
    - Happy: valence=0.8, arousal=0.7
    - Calm: valence=0.5, arousal=0.2
    - Anxious: valence=-0.3, arousal=0.8
    - Sad: valence=-0.7, arousal=0.3
    """

    valence: float = Field(
        default=0.0,
        ge=-1.0,
        le=1.0,
        description="Emotional valence: -1.0 (very negative) to +1.0 (very positive)"
    )
    arousal: float = Field(
        default=0.5,
        ge=0.0,
        le=1.0,
        description="Emotional arousal: 0.0 (very calm) to 1.0 (very excited)"
    )
    last_updated: datetime = Field(
        default_factory=datetime.utcnow,
        description="Last time emotion was updated"
    )

    def update(
        self,
        valence_delta: float,
        arousal_delta: float,
        neuroticism: float
    ) -> None:
        """
        Update emotional state based on an event

        Args:
            valence_delta: Change in valence (-1.0 to 1.0)
            arousal_delta: Change in arousal (-1.0 to 1.0)
            neuroticism: Agent's neuroticism trait (0.0-1.0)
        """
        # Neuroticism amplifies emotional changes
        reactivity = 0.5 + (neuroticism * 0.5)

        self.valence += valence_delta * reactivity
        self.arousal += arousal_delta * reactivity

        # Clamp values
        self.valence = max(-1.0, min(1.0, self.valence))
        self.arousal = max(0.0, min(1.0, self.arousal))

        self.last_updated = datetime.utcnow()

    def decay(self, decay_rate: float = 0.1) -> None:
        """
        Gradually return emotional state to baseline

        Args:
            decay_rate: Rate of decay per time step (0.0-1.0)
        """
        # Return valence to neutral (0.0)
        if self.valence > 0:
            self.valence = max(0.0, self.valence - decay_rate)
        else:
            self.valence = min(0.0, self.valence + decay_rate)

        # Return arousal to baseline (0.5)
        if self.arousal > 0.5:
            self.arousal = max(0.5, self.arousal - decay_rate)
        else:
            self.arousal = min(0.5, self.arousal + decay_rate)

        self.last_updated = datetime.utcnow()

    def get_emotional_label(self) -> str:
        """
        Get human-readable emotion label based on valence/arousal

        Returns:
            Emotion label (e.g., "happy", "anxious", "calm")
        """
        # High arousal
        if self.arousal > 0.7:
            if self.valence > 0.5:
                return "excited"
            elif self.valence > 0:
                return "alert"
            elif self.valence > -0.5:
                return "tense"
            else:
                return "distressed"

        # Medium arousal
        elif self.arousal > 0.3:
            if self.valence > 0.5:
                return "happy"
            elif self.valence > 0:
                return "content"
            elif self.valence > -0.5:
                return "uneasy"
            else:
                return "sad"

        # Low arousal
        else:
            if self.valence > 0.5:
                return "calm"
            elif self.valence > 0:
                return "relaxed"
            elif self.valence > -0.5:
                return "tired"
            else:
                return "depressed"

    def influences_response(self) -> dict:
        """
        Get how current emotion influences response generation

        Returns:
            Dict with response modifiers
        """
        return {
            "tone": "positive" if self.valence > 0.3 else "negative" if self.valence < -0.3 else "neutral",
            "energy_level": "high" if self.arousal > 0.7 else "low" if self.arousal < 0.3 else "medium",
            "verbosity_modifier": 1.0 + (self.arousal - 0.5),  # Higher arousal = more verbose
            "agreement_bias": self.valence * 0.3,  # Positive mood = more agreeable
        }

    def to_prompt_description(self) -> str:
        """Generate description for LLM prompt"""
        emotion = self.get_emotional_label()

        valence_desc = "very positive" if self.valence > 0.7 else \
                       "positive" if self.valence > 0.3 else \
                       "negative" if self.valence < -0.3 else \
                       "very negative" if self.valence < -0.7 else \
                       "neutral"

        arousal_desc = "highly energetic" if self.arousal > 0.7 else \
                       "calm" if self.arousal < 0.3 else \
                       "moderately active"

        return f"You are currently feeling {emotion} ({valence_desc}, {arousal_desc})."

    class Config:
        json_schema_extra = {
            "example": {
                "valence": 0.6,
                "arousal": 0.7,
                "last_updated": "2025-01-15T10:30:45.123Z"
            }
        }
