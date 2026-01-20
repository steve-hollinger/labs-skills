"""Exercise 2 Solution: Dynamic Context Injection."""

from dataclasses import dataclass, field
from typing import Any

from four_layer_prompts.layers import PromptBuilder


@dataclass
class UserContext:
    """User context information."""

    level: str
    topic: str
    history: list[dict[str, str]] = field(default_factory=list)
    preferences: dict[str, Any] = field(default_factory=dict)


class ContextBuilder:
    """Builder for dynamic context layers."""

    LEVEL_DESCRIPTORS = {
        "beginner": {
            "descriptor": "a beginner learning",
            "tone": "Use simple language and explain basic concepts.",
            "complexity": "basic",
        },
        "intermediate": {
            "descriptor": "an intermediate practitioner working with",
            "tone": "Assume familiarity with fundamentals.",
            "complexity": "moderate",
        },
        "expert": {
            "descriptor": "an expert deeply familiar with",
            "tone": "Use technical terminology freely. Focus on advanced concepts.",
            "complexity": "advanced",
        },
    }

    def __init__(self) -> None:
        """Initialize the builder."""
        self._level: str = "intermediate"
        self._topic: str = ""
        self._history: list[dict[str, str]] = []
        self._preferences: dict[str, Any] = {}

    def with_user_level(self, level: str) -> "ContextBuilder":
        """Set user expertise level."""
        if level not in self.LEVEL_DESCRIPTORS:
            raise ValueError(f"Level must be one of: {list(self.LEVEL_DESCRIPTORS.keys())}")
        self._level = level
        return self

    def with_topic(self, topic: str) -> "ContextBuilder":
        """Set the topic being discussed."""
        self._topic = topic
        return self

    def with_history(self, history: list[dict[str, str]]) -> "ContextBuilder":
        """Add conversation history."""
        self._history = history
        return self

    def with_preferences(self, preferences: dict[str, Any]) -> "ContextBuilder":
        """Add user preferences."""
        self._preferences = preferences
        return self

    def build(self) -> str:
        """Build the context layer string."""
        parts = []

        # User level section
        level_info = self.LEVEL_DESCRIPTORS[self._level]
        parts.append(f"User Profile: The user is {level_info['descriptor']} {self._topic}.")
        parts.append(f"Communication Style: {level_info['tone']}")

        # Topic section
        if self._topic:
            parts.append(f"\nTopic: {self._topic}")
            parts.append(f"Expected Complexity: {level_info['complexity']}")

        # History section (if provided)
        if self._history:
            parts.append("\nConversation History:")
            # Summarize history for context
            for msg in self._history[-5:]:  # Last 5 messages
                role = msg.get("role", "unknown").title()
                content = msg.get("content", "")
                # Truncate long messages
                if len(content) > 100:
                    content = content[:100] + "..."
                parts.append(f"  {role}: {content}")

        # Preferences section (if provided)
        if self._preferences:
            parts.append("\nUser Preferences:")
            for key, value in self._preferences.items():
                parts.append(f"  - {key}: {value}")

        return "\n".join(parts)


def create_adaptive_prompt(user_context: UserContext, question: str) -> str:
    """Create a full prompt that adapts to user context."""
    # Build context using ContextBuilder
    context = (
        ContextBuilder()
        .with_user_level(user_context.level)
        .with_topic(user_context.topic)
        .with_history(user_context.history)
        .with_preferences(user_context.preferences)
        .build()
    )

    # Adapt system layer based on user level
    system_by_level = {
        "beginner": """You are a patient, encouraging tutor who explains concepts clearly.
You use analogies and simple examples to make complex topics accessible.
You never assume prior knowledge and always define technical terms.""",
        "intermediate": """You are a knowledgeable mentor who helps practitioners level up.
You balance explanation with practical application.
You provide context for why things work the way they do.""",
        "expert": """You are a fellow expert engaging in technical discussion.
You can use advanced terminology and assume deep background knowledge.
You focus on nuances, edge cases, and advanced techniques.""",
    }

    system = system_by_level.get(user_context.level, system_by_level["intermediate"])

    # Create instruction
    instruction = f"Answer the following question about {user_context.topic}:\n\n{question}"

    # Adapt constraints based on level and preferences
    constraints = []

    if user_context.level == "beginner":
        constraints.append("Use simple language and avoid jargon")
        constraints.append("Include a simple example")
        constraints.append("Define any technical terms you must use")
    elif user_context.level == "expert":
        constraints.append("Be concise - skip basic explanations")
        constraints.append("Focus on advanced considerations")
        constraints.append("Include technical details and edge cases")

    # Add preference-based constraints
    if user_context.preferences.get("examples", False):
        constraints.append("Include practical code examples")
    if user_context.preferences.get("max_length") == "short":
        constraints.append("Keep response under 100 words")
    elif user_context.preferences.get("max_length") == "medium":
        constraints.append("Keep response between 100-300 words")

    constraint = "Response Guidelines:\n" + "\n".join(f"- {c}" for c in constraints)

    return (
        PromptBuilder()
        .system(system)
        .context(context)
        .instruction(instruction)
        .constraint(constraint)
        .build()
    )


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
    print("Test passed!")


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
    assert "decorators" in context.lower()  # History included
    print("Test passed!")


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

    assert "async" in prompt.lower()
    assert "example" in prompt.lower()  # From preferences
    print("Test passed!")


if __name__ == "__main__":
    test_beginner_context()
    test_expert_with_history()
    test_full_adaptive_prompt()
    print("\nAll tests passed!")
