"""
Simple Memory System for MVP

Tracks recent conversation history for context.
"""

from collections import deque
from typing import List
from ..models.event import Event


class SimpleMemory:
    """
    Simple memory system for MVP

    Keeps track of recent events for context.
    Future: Add long-term memory, semantic search, etc.
    """

    def __init__(self, max_size: int = 10):
        """
        Initialize memory

        Args:
            max_size: Maximum number of events to remember
        """
        self.events: deque[Event] = deque(maxlen=max_size)

    def add_event(self, event: Event):
        """Add event to memory"""
        self.events.append(event)

    def get_recent_context(self, n: int = 5) -> str:
        """
        Get recent conversation context as string

        Args:
            n: Number of recent events to include

        Returns:
            Formatted context string for LLM
        """
        if not self.events:
            return "No previous conversation."

        recent = list(self.events)[-n:]
        context_lines = [event.to_context_string() for event in recent]

        return "\n".join(context_lines)

    def get_all_events(self) -> List[Event]:
        """Get all events in memory"""
        return list(self.events)

    def clear(self):
        """Clear all memory"""
        self.events.clear()
