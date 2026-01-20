"""Episode-Based History - Conversation Memory Management.

This module provides utilities and patterns for managing conversation
history using episode boundaries, summarization, and context optimization.
"""

from episode_history.episode import Message, Episode, EpisodeStatus
from episode_history.manager import EpisodeManager, EpisodeBoundary
from episode_history.summarizer import Summarizer, SimpleSummarizer
from episode_history.context import ContextBuilder, ContextConfig

__all__ = [
    "Message",
    "Episode",
    "EpisodeStatus",
    "EpisodeManager",
    "EpisodeBoundary",
    "Summarizer",
    "SimpleSummarizer",
    "ContextBuilder",
    "ContextConfig",
]
