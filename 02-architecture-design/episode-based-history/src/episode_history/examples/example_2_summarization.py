"""Example 2: History Summarization.

Demonstrates strategies for summarizing episodes to fit within context limits.

Run with: make example-2
"""

import asyncio

from episode_history.episode import Episode, Message
from episode_history.summarizer import (
    SimpleSummarizer,
    LLMSummarizer,
    LLMSummarizerConfig,
    BatchSummarizer,
)


async def demo_simple_summarizer() -> None:
    """Demonstrate simple extractive summarization."""
    print("=== Simple Summarizer Demo ===\n")

    summarizer = SimpleSummarizer(max_length=150)

    # Create episode with multiple messages
    episode = Episode(topic="API Design")
    messages = [
        ("user", "I'm designing a REST API for a todo app. What endpoints do I need?"),
        ("assistant", "For a todo app, you'll typically need: GET /todos, POST /todos, "
         "GET /todos/{id}, PUT /todos/{id}, DELETE /todos/{id}."),
        ("user", "Should I use PUT or PATCH for updates?"),
        ("assistant", "PATCH is better for partial updates. PUT implies replacing the "
         "entire resource. For todo updates, PATCH /todos/{id} is more appropriate."),
        ("user", "Makes sense. What about authentication?"),
        ("assistant", "Use JWT tokens in the Authorization header. Implement "
         "POST /auth/login and POST /auth/register endpoints."),
    ]

    for role, content in messages:
        episode.add_message(Message(role=role, content=content))

    print(f"Episode: {episode.topic}")
    print(f"Messages: {episode.message_count}")

    summary = await summarizer.summarize(episode)
    print(f"\nSimple Summary:\n  {summary}")


async def demo_llm_summarizer_mock() -> None:
    """Demonstrate LLM summarizer with mock LLM."""
    print("\n=== LLM Summarizer Demo (Mock) ===\n")

    # Mock LLM function
    async def mock_llm(prompt: str) -> str:
        """Simulate LLM summarization."""
        # Extract topic from prompt
        if "API Design" in prompt:
            return ("Discussed REST API design for todo app. Covered essential endpoints "
                   "(CRUD operations), recommended PATCH over PUT for partial updates, "
                   "and JWT-based authentication approach.")
        return "Conversation summary not available."

    config = LLMSummarizerConfig(
        style="concise",
        max_tokens=50,
    )
    summarizer = LLMSummarizer(mock_llm, config)

    # Create episode
    episode = Episode(topic="API Design")
    messages = [
        ("user", "I'm designing a REST API"),
        ("assistant", "Let me help you with that"),
        ("user", "What endpoints do I need?"),
        ("assistant", "You need GET, POST, PUT, DELETE endpoints"),
        ("user", "Thanks!"),
    ]

    for role, content in messages:
        episode.add_message(Message(role=role, content=content))

    summary = await summarizer.summarize(episode)
    print(f"Episode: {episode.topic}")
    print(f"LLM Summary:\n  {summary}")


async def demo_short_episode() -> None:
    """Demonstrate handling of short episodes."""
    print("\n=== Short Episode Handling ===\n")

    summarizer = SimpleSummarizer()

    # Very short episode (1 message)
    ep1 = Episode(topic="Quick Question")
    ep1.add_message(Message(role="user", content="What is Python?"))

    # Two message episode
    ep2 = Episode(topic="Brief Exchange")
    ep2.add_message(Message(role="user", content="Is Python good for web?"))
    ep2.add_message(Message(role="assistant", content="Yes, with frameworks like Django and Flask."))

    print("Single message episode:")
    print(f"  {await summarizer.summarize(ep1)}")

    print("\nTwo message episode:")
    print(f"  {await summarizer.summarize(ep2)}")


async def demo_batch_summarization() -> None:
    """Demonstrate batch summarization of multiple episodes."""
    print("\n=== Batch Summarization Demo ===\n")

    summarizer = SimpleSummarizer()
    batch = BatchSummarizer(summarizer)

    # Create multiple episodes
    episodes = []

    topics = [
        ("Python Lists", [
            ("user", "How do I create a list?"),
            ("assistant", "Use square brackets: my_list = [1, 2, 3]"),
        ]),
        ("Python Dicts", [
            ("user", "How do dictionaries work?"),
            ("assistant", "Dicts are key-value pairs: my_dict = {'key': 'value'}"),
        ]),
        ("Python Classes", [
            ("user", "How do I create a class?"),
            ("assistant", "Use the class keyword: class MyClass: pass"),
        ]),
    ]

    for topic, messages in topics:
        ep = Episode(topic=topic)
        for role, content in messages:
            ep.add_message(Message(role=role, content=content))
        ep.close()
        episodes.append(ep)

    # Batch summarize
    print("Batch summarizing 3 episodes...")
    summaries = await batch.summarize_batch(episodes)

    for ep_id, summary in summaries.items():
        ep = next(e for e in episodes if e.id == ep_id)
        print(f"\n  {ep.topic}:")
        print(f"    {summary}")

    # Demonstrate update in place
    print("\nUpdating episodes with summaries...")
    updated = await batch.summarize_and_update(episodes)
    print(f"  Episodes updated: {updated}")  # Should be 0 since already have summaries


async def demo_progressive_compression() -> None:
    """Demonstrate progressive compression levels."""
    print("\n=== Progressive Compression Demo ===\n")

    # Simulate different compression levels
    episode = Episode(topic="Project Planning")
    messages = [
        ("user", "We need to plan the Q1 roadmap"),
        ("assistant", "Let's start by listing the main initiatives"),
        ("user", "Feature A: User authentication overhaul"),
        ("assistant", "Good. That's critical for security compliance."),
        ("user", "Feature B: Dashboard redesign"),
        ("assistant", "Important for user retention. Priority?"),
        ("user", "Feature C: API versioning"),
        ("assistant", "Essential for backward compatibility"),
        ("user", "A is highest priority, then C, then B"),
        ("assistant", "Got it. A > C > B. I'll draft the timeline."),
    ]

    for role, content in messages:
        episode.add_message(Message(role=role, content=content))

    # Level 0: Full messages
    print("Level 0 (Full messages):")
    for msg in episode.messages[:3]:
        print(f"  {msg.role}: {msg.content[:50]}...")

    # Level 1: Detailed summary
    detailed = ("Planned Q1 roadmap with three features: A) User authentication overhaul "
               "(highest priority, security compliance), B) Dashboard redesign (user retention), "
               "C) API versioning (backward compatibility). Priority order: A > C > B.")
    print(f"\nLevel 1 (Detailed summary):\n  {detailed}")

    # Level 2: Brief summary
    brief = "Q1 roadmap: Auth overhaul (P1), API versioning (P2), Dashboard redesign (P3)."
    print(f"\nLevel 2 (Brief summary):\n  {brief}")

    # Level 3: Key facts
    key_facts = "Q1: 3 features planned, auth highest priority."
    print(f"\nLevel 3 (Key facts):\n  {key_facts}")


async def main() -> None:
    """Run all summarization demos."""
    await demo_simple_summarizer()
    await demo_llm_summarizer_mock()
    await demo_short_episode()
    await demo_batch_summarization()
    await demo_progressive_compression()
    print("\n=== Example Complete ===")


if __name__ == "__main__":
    asyncio.run(main())
