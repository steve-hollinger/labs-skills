"""Example 4: Persistent Episode Storage.

Demonstrates storing and retrieving episodes from persistent storage.

Run with: make example-4
"""

import asyncio
import json
from abc import ABC, abstractmethod
from pathlib import Path
from datetime import datetime

from episode_history.episode import Episode, Message, EpisodeStatus


class EpisodeStore(ABC):
    """Abstract base for episode storage."""

    @abstractmethod
    async def save(self, episode: Episode) -> None:
        """Save an episode."""
        pass

    @abstractmethod
    async def get(self, episode_id: str) -> Episode | None:
        """Get an episode by ID."""
        pass

    @abstractmethod
    async def get_recent(self, limit: int) -> list[Episode]:
        """Get recent episodes."""
        pass

    @abstractmethod
    async def search(self, query: str, limit: int) -> list[Episode]:
        """Search episodes."""
        pass

    @abstractmethod
    async def delete(self, episode_id: str) -> bool:
        """Delete an episode."""
        pass


class InMemoryStore(EpisodeStore):
    """In-memory episode storage for development/testing."""

    def __init__(self) -> None:
        """Initialize empty store."""
        self._episodes: dict[str, Episode] = {}

    async def save(self, episode: Episode) -> None:
        """Save episode to memory."""
        self._episodes[episode.id] = episode

    async def get(self, episode_id: str) -> Episode | None:
        """Get episode by ID."""
        return self._episodes.get(episode_id)

    async def get_recent(self, limit: int) -> list[Episode]:
        """Get most recent episodes."""
        sorted_eps = sorted(
            self._episodes.values(),
            key=lambda e: e.created_at,
            reverse=True,
        )
        return sorted_eps[:limit]

    async def search(self, query: str, limit: int) -> list[Episode]:
        """Search episodes by topic or content."""
        query_lower = query.lower()
        results = []

        for ep in self._episodes.values():
            # Search in topic
            if query_lower in ep.topic.lower():
                results.append(ep)
                continue

            # Search in summary
            if ep.summary and query_lower in ep.summary.lower():
                results.append(ep)
                continue

            # Search in messages
            for msg in ep.messages:
                if query_lower in msg.content.lower():
                    results.append(ep)
                    break

        return results[:limit]

    async def delete(self, episode_id: str) -> bool:
        """Delete episode."""
        if episode_id in self._episodes:
            del self._episodes[episode_id]
            return True
        return False


class FileStore(EpisodeStore):
    """File-based episode storage."""

    def __init__(self, directory: Path | str) -> None:
        """Initialize with storage directory."""
        self.directory = Path(directory)
        self.directory.mkdir(parents=True, exist_ok=True)

    def _episode_path(self, episode_id: str) -> Path:
        """Get path for episode file."""
        return self.directory / f"{episode_id}.json"

    async def save(self, episode: Episode) -> None:
        """Save episode to file."""
        path = self._episode_path(episode.id)
        data = episode.to_dict()
        path.write_text(json.dumps(data, indent=2))

    async def get(self, episode_id: str) -> Episode | None:
        """Load episode from file."""
        path = self._episode_path(episode_id)
        if not path.exists():
            return None
        data = json.loads(path.read_text())
        return Episode.from_dict(data)

    async def get_recent(self, limit: int) -> list[Episode]:
        """Get recent episodes from files."""
        episodes = []
        for path in self.directory.glob("*.json"):
            data = json.loads(path.read_text())
            episodes.append(Episode.from_dict(data))

        episodes.sort(key=lambda e: e.created_at, reverse=True)
        return episodes[:limit]

    async def search(self, query: str, limit: int) -> list[Episode]:
        """Search episodes in files."""
        query_lower = query.lower()
        results = []

        for path in self.directory.glob("*.json"):
            data = json.loads(path.read_text())
            ep = Episode.from_dict(data)

            if query_lower in ep.topic.lower():
                results.append(ep)
            elif ep.summary and query_lower in ep.summary.lower():
                results.append(ep)

            if len(results) >= limit:
                break

        return results

    async def delete(self, episode_id: str) -> bool:
        """Delete episode file."""
        path = self._episode_path(episode_id)
        if path.exists():
            path.unlink()
            return True
        return False


class TieredStore:
    """Multi-tier storage with hot/warm/cold layers."""

    def __init__(
        self,
        hot: EpisodeStore,
        warm: EpisodeStore,
        hot_limit: int = 10,
    ) -> None:
        """Initialize tiered storage.

        Args:
            hot: Fast storage for recent episodes.
            warm: Larger storage for older episodes.
            hot_limit: Maximum episodes in hot storage.
        """
        self.hot = hot
        self.warm = warm
        self.hot_limit = hot_limit
        self._hot_ids: list[str] = []

    async def save(self, episode: Episode) -> None:
        """Save to hot tier, manage overflow to warm."""
        # Always save to hot first
        await self.hot.save(episode)
        self._hot_ids.append(episode.id)

        # Move oldest to warm if over limit
        while len(self._hot_ids) > self.hot_limit:
            old_id = self._hot_ids.pop(0)
            old_ep = await self.hot.get(old_id)
            if old_ep:
                await self.warm.save(old_ep)
                await self.hot.delete(old_id)

    async def get(self, episode_id: str) -> Episode | None:
        """Get from hot, fall back to warm."""
        ep = await self.hot.get(episode_id)
        if ep:
            return ep
        return await self.warm.get(episode_id)

    async def get_recent(self, limit: int) -> list[Episode]:
        """Get recent from hot tier."""
        return await self.hot.get_recent(limit)


async def demo_in_memory_store() -> None:
    """Demonstrate in-memory storage."""
    print("=== In-Memory Store Demo ===\n")

    store = InMemoryStore()

    # Create and save episodes
    for topic in ["Python Basics", "Database Design", "API Development"]:
        ep = Episode(topic=topic)
        ep.add_message(Message(role="user", content=f"Tell me about {topic}"))
        ep.add_message(Message(role="assistant", content=f"Here's info about {topic}..."))
        ep.close(summary=f"Covered {topic} fundamentals.")
        await store.save(ep)
        print(f"Saved: {ep.topic}")

    # Retrieve recent
    print("\nRecent episodes:")
    recent = await store.get_recent(2)
    for ep in recent:
        print(f"  {ep.topic}")

    # Search
    print("\nSearch for 'Python':")
    results = await store.search("Python", limit=5)
    for ep in results:
        print(f"  Found: {ep.topic}")


async def demo_file_store() -> None:
    """Demonstrate file-based storage."""
    print("\n=== File Store Demo ===\n")

    import tempfile

    with tempfile.TemporaryDirectory() as tmpdir:
        store = FileStore(tmpdir)

        # Save episodes
        ep1 = Episode(topic="File Storage Test")
        ep1.add_message(Message(role="user", content="Testing file storage"))
        ep1.add_message(Message(role="assistant", content="File storage works!"))
        ep1.close(summary="Tested file-based episode storage.")

        await store.save(ep1)
        print(f"Saved to file: {ep1.topic}")

        # Load back
        loaded = await store.get(ep1.id)
        if loaded:
            print(f"Loaded back: {loaded.topic}")
            print(f"  Messages: {loaded.message_count}")
            print(f"  Summary: {loaded.summary}")

        # Show file contents
        file_path = Path(tmpdir) / f"{ep1.id}.json"
        print(f"\nFile contents preview:")
        content = json.loads(file_path.read_text())
        print(f"  topic: {content['topic']}")
        print(f"  status: {content['status']}")


async def demo_tiered_store() -> None:
    """Demonstrate tiered storage."""
    print("\n=== Tiered Store Demo ===\n")

    hot = InMemoryStore()
    warm = InMemoryStore()
    tiered = TieredStore(hot=hot, warm=warm, hot_limit=3)

    # Add more than hot_limit episodes
    for i in range(5):
        ep = Episode(topic=f"Episode {i + 1}")
        ep.add_message(Message(role="user", content=f"Content {i + 1}"))
        ep.close(summary=f"Summary {i + 1}")
        await tiered.save(ep)
        print(f"Saved episode {i + 1}")

    print(f"\nHot tier episodes: {len(hot._episodes)}")
    print(f"Warm tier episodes: {len(warm._episodes)}")

    # Get recent (from hot)
    print("\nRecent from hot:")
    for ep in await tiered.get_recent(3):
        print(f"  {ep.topic}")


async def demo_serialization() -> None:
    """Demonstrate episode serialization."""
    print("\n=== Serialization Demo ===\n")

    # Create episode with all fields
    ep = Episode(
        topic="Serialization Test",
        metadata={"user_id": "123", "session": "abc"},
    )
    ep.add_message(Message(
        role="user",
        content="Test message",
        metadata={"tokens": 5},
    ))
    ep.add_message(Message(
        role="assistant",
        content="Response message",
    ))
    ep.close(summary="Tested serialization.")

    # Serialize to dict
    data = ep.to_dict()
    print("Serialized to dict:")
    print(f"  Keys: {list(data.keys())}")
    print(f"  Messages: {len(data['messages'])}")

    # Serialize to JSON
    json_str = json.dumps(data, indent=2)
    print(f"\nJSON length: {len(json_str)} chars")

    # Deserialize
    loaded_data = json.loads(json_str)
    loaded_ep = Episode.from_dict(loaded_data)

    print(f"\nDeserialized episode:")
    print(f"  Topic: {loaded_ep.topic}")
    print(f"  Messages: {loaded_ep.message_count}")
    print(f"  Status: {loaded_ep.status.value}")
    print(f"  Metadata: {loaded_ep.metadata}")


async def main() -> None:
    """Run all storage demos."""
    await demo_in_memory_store()
    await demo_file_store()
    await demo_tiered_store()
    await demo_serialization()
    print("\n=== Example Complete ===")


if __name__ == "__main__":
    asyncio.run(main())
