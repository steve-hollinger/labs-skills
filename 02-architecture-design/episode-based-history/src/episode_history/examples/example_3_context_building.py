"""Example 3: Smart Context Building.

Demonstrates building context from multiple episodes based on relevance
and token limits.

Run with: make example-3
"""

from episode_history.episode import Episode, Message
from episode_history.context import (
    ContextBuilder,
    ContextConfig,
    RollingContextBuilder,
)


def create_sample_episodes() -> list[Episode]:
    """Create sample episodes for demos."""
    episodes = []

    # Episode 1: Python basics (closed)
    ep1 = Episode(topic="Python Basics")
    ep1.add_message(Message(role="user", content="What is a list in Python?"))
    ep1.add_message(Message(role="assistant", content="A list is a mutable sequence type."))
    ep1.close(summary="Covered Python list basics - mutable sequences.")
    episodes.append(ep1)

    # Episode 2: Database queries (closed)
    ep2 = Episode(topic="SQL Queries")
    ep2.add_message(Message(role="user", content="How do I join tables?"))
    ep2.add_message(Message(role="assistant", content="Use JOIN clause: SELECT * FROM a JOIN b ON a.id = b.a_id"))
    ep2.close(summary="Explained SQL JOINs for combining tables.")
    episodes.append(ep2)

    # Episode 3: API design (closed)
    ep3 = Episode(topic="REST API Design")
    ep3.add_message(Message(role="user", content="What HTTP methods should I use?"))
    ep3.add_message(Message(role="assistant", content="GET for retrieval, POST for creation, PUT/PATCH for updates, DELETE for removal."))
    ep3.close(summary="Covered HTTP methods for RESTful APIs.")
    episodes.append(ep3)

    # Episode 4: Current conversation (active)
    ep4 = Episode(topic="Python Advanced")
    ep4.add_message(Message(role="user", content="How do decorators work?"))
    ep4.add_message(Message(role="assistant", content="Decorators are functions that wrap other functions to extend behavior."))
    ep4.add_message(Message(role="user", content="Can you show an example?"))
    episodes.append(ep4)

    return episodes


def demo_basic_context_building() -> None:
    """Demonstrate basic context building."""
    print("=== Basic Context Building ===\n")

    episodes = create_sample_episodes()

    config = ContextConfig(
        max_tokens=500,
        use_summaries=True,
    )
    builder = ContextBuilder(config=config)

    context = builder.build(episodes)

    print("Built context:")
    print("-" * 50)
    print(context)
    print("-" * 50)
    print(f"\nEstimated tokens: {len(context) // 4}")


def demo_token_limited_context() -> None:
    """Demonstrate context with tight token limits."""
    print("\n=== Token-Limited Context ===\n")

    episodes = create_sample_episodes()

    # Very tight limit
    config = ContextConfig(
        max_tokens=100,  # Very limited
        use_summaries=True,
    )
    builder = ContextBuilder(config=config)

    context = builder.build(episodes)

    print(f"Token limit: 100")
    print("Built context:")
    print("-" * 50)
    print(context)
    print("-" * 50)
    print(f"Actual estimated tokens: {len(context) // 4}")


def demo_relevance_scoring() -> None:
    """Demonstrate relevance-based context building."""
    print("\n=== Relevance-Based Context ===\n")

    episodes = create_sample_episodes()

    # Simple keyword-based relevance scorer
    def keyword_relevance(query: str, episode: Episode) -> float:
        """Score based on keyword overlap."""
        query_words = set(query.lower().split())
        topic_words = set(episode.topic.lower().split())

        # Check topic overlap
        overlap = len(query_words & topic_words)
        topic_score = overlap / max(len(query_words), 1)

        # Check message content overlap
        content_score = 0.0
        for msg in episode.messages:
            msg_words = set(msg.content.lower().split())
            msg_overlap = len(query_words & msg_words)
            content_score = max(content_score, msg_overlap / max(len(query_words), 1))

        return (topic_score + content_score) / 2

    config = ContextConfig(max_tokens=300)
    builder = ContextBuilder(
        config=config,
        relevance_scorer=keyword_relevance,
    )

    # Query related to Python
    query1 = "Python list operations"
    context1 = builder.build(episodes, current_query=query1)

    print(f"Query: '{query1}'")
    print("Context prioritizes Python-related episodes:")
    print("-" * 50)
    print(context1)
    print("-" * 50)

    # Query related to databases
    query2 = "SQL database join"
    context2 = builder.build(episodes, current_query=query2)

    print(f"\nQuery: '{query2}'")
    print("Context prioritizes SQL-related episodes:")
    print("-" * 50)
    print(context2)
    print("-" * 50)


def demo_context_with_system() -> None:
    """Demonstrate building context with system message."""
    print("\n=== Context with System Message ===\n")

    episodes = create_sample_episodes()

    config = ContextConfig(max_tokens=400)
    builder = ContextBuilder(config=config)

    system_message = "You are a helpful programming tutor. Be concise and use examples."

    messages = builder.build_with_system(
        episodes,
        system_message=system_message,
    )

    print("Message list for API:")
    for msg in messages:
        role = msg["role"]
        content = msg["content"][:80] + "..." if len(msg["content"]) > 80 else msg["content"]
        print(f"  [{role}]: {content}")


def demo_rolling_context() -> None:
    """Demonstrate rolling context with compression."""
    print("\n=== Rolling Context ===\n")

    # Create episodes with more messages
    episodes = []

    # Several closed episodes
    for i in range(3):
        ep = Episode(topic=f"Topic {i + 1}")
        for j in range(4):
            ep.add_message(Message(role="user", content=f"Question {j + 1} about topic {i + 1}"))
            ep.add_message(Message(role="assistant", content=f"Answer {j + 1}"))
        ep.close(summary=f"Covered topic {i + 1} fundamentals.")
        episodes.append(ep)

    # Active episode with recent messages
    active = Episode(topic="Current Discussion")
    for j in range(6):
        active.add_message(Message(role="user", content=f"Current question {j + 1}"))
        active.add_message(Message(role="assistant", content=f"Current answer {j + 1}"))
    episodes.append(active)

    builder = RollingContextBuilder(
        max_recent=4,  # Only last 4 messages from active
        max_summaries=3,
    )

    context = builder.build(episodes, max_tokens=300)

    print("Rolling context (recent full, old summarized):")
    print("-" * 50)
    print(context)
    print("-" * 50)


def demo_empty_and_edge_cases() -> None:
    """Demonstrate handling of edge cases."""
    print("\n=== Edge Cases ===\n")

    builder = ContextBuilder()

    # Empty episodes
    print("Empty episode list:")
    context = builder.build([])
    print(f"  Result: '{context}' (empty)")

    # Single empty episode
    print("\nSingle empty episode:")
    empty_ep = Episode(topic="Empty")
    context = builder.build([empty_ep])
    print(f"  Result: '{context}'")

    # Episode with only system message
    print("\nEpisode with one message:")
    single = Episode(topic="Single")
    single.add_message(Message(role="user", content="Hello"))
    context = builder.build([single])
    print(f"  Result: {context}")


def main() -> None:
    """Run all context building demos."""
    demo_basic_context_building()
    demo_token_limited_context()
    demo_relevance_scoring()
    demo_context_with_system()
    demo_rolling_context()
    demo_empty_and_edge_cases()
    print("\n=== Example Complete ===")


if __name__ == "__main__":
    main()
