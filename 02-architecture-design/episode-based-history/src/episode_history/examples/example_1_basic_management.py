"""Example 1: Basic Episode Management.

Demonstrates creating, managing, and closing episodes in a conversation.

Run with: make example-1
"""

from datetime import datetime, timedelta

from episode_history.episode import Episode, Message, EpisodeStatus
from episode_history.manager import EpisodeManager, BoundaryConfig


def demo_episode_lifecycle() -> None:
    """Demonstrate basic episode lifecycle."""
    print("=== Episode Lifecycle Demo ===\n")

    # Create an episode
    episode = Episode(topic="Python Help")
    print(f"Created episode: {episode.id[:8]}...")
    print(f"  Topic: {episode.topic}")
    print(f"  Status: {episode.status.value}")
    print(f"  Is Active: {episode.is_active}")

    # Add messages
    episode.add_message(Message(role="user", content="How do I read a file in Python?"))
    episode.add_message(Message(
        role="assistant",
        content="Use the open() function with a context manager: with open('file.txt') as f: ..."
    ))
    episode.add_message(Message(role="user", content="Thanks! What about writing?"))

    print(f"\n  Messages: {episode.message_count}")
    print(f"  Estimated tokens: {episode.total_tokens}")

    # Close the episode
    episode.close(summary="User asked about file I/O in Python. Covered reading and writing files.")
    print(f"\n  Closed at: {episode.closed_at}")
    print(f"  Status: {episode.status.value}")
    print(f"  Summary: {episode.summary}")


def demo_episode_manager() -> None:
    """Demonstrate the episode manager."""
    print("\n=== Episode Manager Demo ===\n")

    # Create manager with custom config
    config = BoundaryConfig(
        max_messages=5,  # Low for demo
        max_tokens=500,
    )
    manager = EpisodeManager(config=config)

    # Register callback for closed episodes
    def on_closed(ep: Episode) -> None:
        print(f"  [Callback] Episode closed: {ep.topic} ({ep.message_count} messages)")

    manager.on_episode_closed(on_closed)

    # Simulate conversation
    conversations = [
        ("user", "Hello, I need help with Python"),
        ("assistant", "Hi! I'd be happy to help with Python. What do you need?"),
        ("user", "How do I create a list?"),
        ("assistant", "You can create a list with square brackets: my_list = [1, 2, 3]"),
        ("user", "How do I add items?"),
        ("assistant", "Use append() method: my_list.append(4)"),
        ("user", "What about dictionaries?"),  # This should trigger new episode
        ("assistant", "Dictionaries use curly braces: my_dict = {'key': 'value'}"),
    ]

    print("Adding messages to conversation:")
    for role, content in conversations:
        msg, boundary = manager.add_message(role, content)
        print(f"  {role}: {content[:40]}...")
        if boundary:
            print(f"    -> New episode started (boundary: {boundary.name})")

    print(f"\nManager state:")
    print(f"  Total episodes: {len(manager.get_all_episodes())}")
    print(f"  Closed episodes: {len(manager.get_episodes_by_status(EpisodeStatus.CLOSED))}")
    print(f"  Total messages: {manager.get_total_messages()}")

    # Close remaining
    if manager.current:
        manager.close_current(summary="Covered lists and dictionaries basics")


def demo_episode_retrieval() -> None:
    """Demonstrate episode retrieval and search."""
    print("\n=== Episode Retrieval Demo ===\n")

    manager = EpisodeManager()

    # Create some episodes
    topics = ["Python basics", "Database design", "API development", "Python testing"]

    for topic in topics:
        manager.start_episode(topic)
        manager.add_message("user", f"Tell me about {topic}")
        manager.add_message("assistant", f"Here's information about {topic}...")
        manager.close_current(summary=f"Covered {topic} fundamentals")

    # Add current active episode
    manager.start_episode("Python async")
    manager.add_message("user", "How does async work?")

    print("All episodes:")
    for ep in manager.get_all_episodes():
        status = "ACTIVE" if ep.is_active else "CLOSED"
        print(f"  [{status}] {ep.topic}")

    print("\nRecent 2 episodes:")
    for ep in manager.get_recent_episodes(2):
        print(f"  {ep.topic}")

    print("\nSearch for 'Python':")
    for ep in manager.find_episodes_by_topic("Python"):
        print(f"  {ep.topic}")


def demo_context_string() -> None:
    """Demonstrate getting context strings."""
    print("\n=== Context String Demo ===\n")

    # Create episode with some messages
    episode = Episode(topic="Code Review")

    messages = [
        ("user", "Can you review this function?"),
        ("assistant", "Sure, I'll review it for you."),
        ("user", "def add(a, b): return a + b"),
        ("assistant", "The function looks good! Consider adding type hints."),
    ]

    for role, content in messages:
        episode.add_message(Message(role=role, content=content))

    print("Active episode context:")
    print("-" * 40)
    print(episode.get_context_string())
    print("-" * 40)

    # Close and add summary
    episode.close(summary="Reviewed add() function, suggested type hints.")

    print("\nClosed episode context (with summary):")
    print("-" * 40)
    print(episode.get_context_string(use_summary=True))
    print("-" * 40)


def main() -> None:
    """Run all basic management demos."""
    demo_episode_lifecycle()
    demo_episode_manager()
    demo_episode_retrieval()
    demo_context_string()
    print("\n=== Example Complete ===")


if __name__ == "__main__":
    main()
