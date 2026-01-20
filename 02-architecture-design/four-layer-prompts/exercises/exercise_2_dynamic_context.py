"""Exercise 2: Dynamic Context Injection.

In this exercise, you'll build a prompt system that adapts to different contexts
and user characteristics.

Requirements:
1. Create a ContextBuilder class that constructs context layers dynamically
2. Support different user expertise levels (beginner, intermediate, expert)
3. Include optional context sections (history, preferences, constraints)
4. The context should adapt its complexity based on user level

The system should handle these scenarios:
- Beginner user asking about Python basics
- Expert user asking about advanced patterns
- User with conversation history

Implement the ContextBuilder with these methods:
- with_user_level(level)
- with_topic(topic)
- with_history(history) - optional
- with_preferences(prefs) - optional
- build() -> str
"""

from dataclasses import dataclass, field
from typing import Any


@dataclass
class UserContext:
    """User context information."""

    level: str  # "beginner", "intermediate", "expert"
    topic: str
    history: list[dict[str, str]] = field(default_factory=list)
    preferences: dict[str, Any] = field(default_factory=dict)


class ContextBuilder:
    """Builder for dynamic context layers.

    TODO: Implement this class

    The context layer should:
    - Adapt language complexity to user level
    - Include relevant history if provided
    - Incorporate user preferences
    - Format appropriately for the topic
    """

    def __init__(self) -> None:
        """Initialize the builder."""
        # Your implementation here
        raise NotImplementedError("Implement __init__")

    def with_user_level(self, level: str) -> "ContextBuilder":
        """Set user expertise level.

        Args:
            level: One of "beginner", "intermediate", "expert"

        Returns:
            Self for chaining
        """
        # Your implementation here
        raise NotImplementedError("Implement with_user_level")

    def with_topic(self, topic: str) -> "ContextBuilder":
        """Set the topic being discussed.

        Args:
            topic: The subject matter

        Returns:
            Self for chaining
        """
        # Your implementation here
        raise NotImplementedError("Implement with_topic")

    def with_history(self, history: list[dict[str, str]]) -> "ContextBuilder":
        """Add conversation history.

        Args:
            history: List of {"role": "user/assistant", "content": "..."}

        Returns:
            Self for chaining
        """
        # Your implementation here
        raise NotImplementedError("Implement with_history")

    def with_preferences(self, preferences: dict[str, Any]) -> "ContextBuilder":
        """Add user preferences.

        Args:
            preferences: Dict of preference key-value pairs

        Returns:
            Self for chaining
        """
        # Your implementation here
        raise NotImplementedError("Implement with_preferences")

    def build(self) -> str:
        """Build the context layer string.

        Returns:
            Formatted context layer

        The output should include:
        - User level indicator
        - Topic with appropriate framing
        - History summary (if provided)
        - Relevant preferences (if provided)
        """
        # Your implementation here
        raise NotImplementedError("Implement build")


def create_adaptive_prompt(user_context: UserContext, question: str) -> str:
    """Create a full prompt that adapts to user context.

    Args:
        user_context: User context information
        question: The user's question

    Returns:
        Complete four-layer prompt

    TODO: Implement this function

    Hints:
    - Use ContextBuilder to create the context layer
    - Adapt the system layer based on user level
    - Include the question in the instruction layer
    - Adjust constraints based on user level
    """
    # Your implementation here
    raise NotImplementedError("Implement create_adaptive_prompt")


# Test cases
def test_beginner_context() -> None:
    """Test context for beginner user."""
    context = (
        ContextBuilder()
        .with_user_level("beginner")
        .with_topic("Python functions")
        .build()
    )

    print("Beginner Context:")
    print("-" * 50)
    print(context)
    print("-" * 50)

    assert "beginner" in context.lower() or "basic" in context.lower()


def test_expert_with_history() -> None:
    """Test context for expert user with history."""
    history = [
        {"role": "user", "content": "How do decorators work?"},
        {"role": "assistant", "content": "Decorators are functions that..."},
        {"role": "user", "content": "What about class decorators?"},
    ]

    context = (
        ContextBuilder()
        .with_user_level("expert")
        .with_topic("Python metaclasses")
        .with_history(history)
        .build()
    )

    print("\nExpert Context with History:")
    print("-" * 50)
    print(context)
    print("-" * 50)

    assert "expert" in context.lower() or "advanced" in context.lower()


def test_full_adaptive_prompt() -> None:
    """Test full adaptive prompt creation."""
    user = UserContext(
        level="intermediate",
        topic="async programming",
        history=[
            {"role": "user", "content": "What is asyncio?"},
        ],
        preferences={
            "examples": True,
            "max_length": "medium",
        },
    )

    prompt = create_adaptive_prompt(user, "How do I handle multiple async tasks?")

    print("\nFull Adaptive Prompt:")
    print("-" * 50)
    print(prompt)
    print("-" * 50)


if __name__ == "__main__":
    test_beginner_context()
    test_expert_with_history()
    test_full_adaptive_prompt()
    print("\nAll tests passed!")
