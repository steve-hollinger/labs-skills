# Episode-Based History Patterns

## Pattern 1: Basic Episode Manager

Simple episode management with size-based boundaries.

```python
from dataclasses import dataclass, field
from datetime import datetime
from uuid import uuid4

@dataclass
class Message:
    role: str
    content: str
    timestamp: datetime = field(default_factory=datetime.now)

@dataclass
class Episode:
    id: str = field(default_factory=lambda: str(uuid4()))
    topic: str = "general"
    messages: list[Message] = field(default_factory=list)
    summary: str | None = None
    created_at: datetime = field(default_factory=datetime.now)
    closed_at: datetime | None = None

    @property
    def is_closed(self) -> bool:
        return self.closed_at is not None

class BasicEpisodeManager:
    def __init__(self, max_messages: int = 20):
        self.episodes: list[Episode] = []
        self.current: Episode | None = None
        self.max_messages = max_messages

    def start_episode(self, topic: str = "general") -> Episode:
        self.current = Episode(topic=topic)
        return self.current

    def add_message(self, role: str, content: str) -> None:
        if not self.current:
            self.start_episode()

        if len(self.current.messages) >= self.max_messages:
            self.close_episode()
            self.start_episode()

        self.current.messages.append(Message(role=role, content=content))

    def close_episode(self, summary: str | None = None) -> None:
        if self.current:
            self.current.closed_at = datetime.now()
            self.current.summary = summary
            self.episodes.append(self.current)
            self.current = None

    def get_all_episodes(self) -> list[Episode]:
        all_eps = self.episodes.copy()
        if self.current:
            all_eps.append(self.current)
        return all_eps
```

**When to use**: Simple chatbots, prototypes, applications without complex topic tracking.

## Pattern 2: Topic-Aware Episode Manager

Automatically detects topic changes to create episode boundaries.

```python
from typing import Callable

TopicExtractor = Callable[[str], str]
SimilarityChecker = Callable[[str, str], float]

class TopicAwareManager:
    def __init__(
        self,
        extract_topic: TopicExtractor,
        check_similarity: SimilarityChecker,
        similarity_threshold: float = 0.7,
        max_messages: int = 30,
    ):
        self.extract_topic = extract_topic
        self.check_similarity = check_similarity
        self.threshold = similarity_threshold
        self.max_messages = max_messages
        self.episodes: list[Episode] = []
        self.current: Episode | None = None

    def add_message(self, role: str, content: str) -> None:
        if not self.current:
            topic = self.extract_topic(content)
            self.current = Episode(topic=topic)

        # Check for topic change
        if role == "user":
            new_topic = self.extract_topic(content)
            similarity = self.check_similarity(self.current.topic, new_topic)

            if similarity < self.threshold:
                self.close_episode()
                self.current = Episode(topic=new_topic)

        # Check size limit
        if len(self.current.messages) >= self.max_messages:
            self.close_episode()
            topic = self.extract_topic(content)
            self.current = Episode(topic=topic)

        self.current.messages.append(Message(role=role, content=content))

    def close_episode(self) -> None:
        if self.current and self.current.messages:
            self.current.closed_at = datetime.now()
            self.episodes.append(self.current)
            self.current = None
```

**When to use**: Multi-turn conversations, support systems, any application where topic tracking matters.

## Pattern 3: Async Summarization Pipeline

Background summarization that doesn't block the main conversation flow.

```python
import asyncio
from typing import Protocol

class Summarizer(Protocol):
    async def summarize(self, episode: Episode) -> str:
        ...

class AsyncSummarizationPipeline:
    def __init__(self, summarizer: Summarizer):
        self.summarizer = summarizer
        self.pending_queue: asyncio.Queue[Episode] = asyncio.Queue()
        self._worker_task: asyncio.Task | None = None

    def start(self) -> None:
        """Start the background summarization worker."""
        self._worker_task = asyncio.create_task(self._worker())

    async def stop(self) -> None:
        """Stop the worker and process remaining items."""
        if self._worker_task:
            self._worker_task.cancel()
            try:
                await self._worker_task
            except asyncio.CancelledError:
                pass

    def queue_episode(self, episode: Episode) -> None:
        """Queue an episode for summarization."""
        self.pending_queue.put_nowait(episode)

    async def _worker(self) -> None:
        """Background worker that processes episodes."""
        while True:
            episode = await self.pending_queue.get()
            try:
                summary = await self.summarizer.summarize(episode)
                episode.summary = summary
            except Exception as e:
                # Log error, maybe retry
                print(f"Summarization failed: {e}")
            finally:
                self.pending_queue.task_done()

# Usage
class LLMSummarizer:
    async def summarize(self, episode: Episode) -> str:
        messages_text = "\n".join(
            f"{m.role}: {m.content}" for m in episode.messages
        )
        # Call LLM here
        return f"Summary of: {episode.topic}"

pipeline = AsyncSummarizationPipeline(LLMSummarizer())
pipeline.start()
# When episode closes:
pipeline.queue_episode(closed_episode)
```

**When to use**: High-throughput systems, when summarization latency shouldn't affect user experience.

## Pattern 4: Smart Context Builder

Builds context considering tokens, relevance, and recency.

```python
from dataclasses import dataclass

@dataclass
class ContextConfig:
    max_tokens: int = 4000
    include_current_full: bool = True
    max_recent_episodes: int = 3
    use_summaries_for_old: bool = True
    recency_weight: float = 0.5
    relevance_weight: float = 0.5

class SmartContextBuilder:
    def __init__(
        self,
        config: ContextConfig,
        token_counter: Callable[[str], int],
        relevance_scorer: Callable[[str, Episode], float] | None = None,
    ):
        self.config = config
        self.count_tokens = token_counter
        self.score_relevance = relevance_scorer or (lambda q, e: 0.5)

    def build(
        self,
        episodes: list[Episode],
        current_query: str,
    ) -> str:
        if not episodes:
            return ""

        # Score and sort episodes
        scored = self._score_episodes(episodes, current_query)

        # Build context within token limit
        context_parts = []
        remaining_tokens = self.config.max_tokens

        for episode, score in scored:
            content = self._format_episode(episode)
            tokens = self.count_tokens(content)

            if tokens > remaining_tokens:
                continue

            context_parts.append((score, content))
            remaining_tokens -= tokens

        # Sort by score for final output
        context_parts.sort(key=lambda x: x[0], reverse=True)
        return "\n\n---\n\n".join(content for _, content in context_parts)

    def _score_episodes(
        self,
        episodes: list[Episode],
        query: str
    ) -> list[tuple[Episode, float]]:
        scored = []

        for i, episode in enumerate(episodes):
            # Recency score (higher for newer)
            recency = i / len(episodes)

            # Relevance score
            relevance = self.score_relevance(query, episode)

            # Combined score
            score = (
                self.config.recency_weight * recency +
                self.config.relevance_weight * relevance
            )
            scored.append((episode, score))

        return sorted(scored, key=lambda x: x[1], reverse=True)

    def _format_episode(self, episode: Episode) -> str:
        if episode.is_closed and episode.summary and self.config.use_summaries_for_old:
            return f"[Previous: {episode.topic}]\n{episode.summary}"

        messages = "\n".join(
            f"{m.role}: {m.content}" for m in episode.messages
        )
        return f"[{episode.topic}]\n{messages}"
```

**When to use**: When context quality significantly impacts output quality.

## Pattern 5: Persistent Episode Storage

Store episodes in a database with efficient retrieval.

```python
from abc import ABC, abstractmethod
from typing import AsyncIterator

class EpisodeStore(ABC):
    @abstractmethod
    async def save(self, episode: Episode) -> None:
        pass

    @abstractmethod
    async def get(self, episode_id: str) -> Episode | None:
        pass

    @abstractmethod
    async def get_recent(
        self,
        conversation_id: str,
        limit: int
    ) -> list[Episode]:
        pass

    @abstractmethod
    async def search(
        self,
        conversation_id: str,
        query: str,
        limit: int
    ) -> list[Episode]:
        pass

class InMemoryStore(EpisodeStore):
    """Simple in-memory implementation for testing."""

    def __init__(self):
        self._episodes: dict[str, Episode] = {}

    async def save(self, episode: Episode) -> None:
        self._episodes[episode.id] = episode

    async def get(self, episode_id: str) -> Episode | None:
        return self._episodes.get(episode_id)

    async def get_recent(
        self,
        conversation_id: str,
        limit: int
    ) -> list[Episode]:
        all_episodes = sorted(
            self._episodes.values(),
            key=lambda e: e.created_at,
            reverse=True
        )
        return all_episodes[:limit]

    async def search(
        self,
        conversation_id: str,
        query: str,
        limit: int
    ) -> list[Episode]:
        # Simple keyword search
        query_lower = query.lower()
        matching = [
            e for e in self._episodes.values()
            if query_lower in e.topic.lower() or
               any(query_lower in m.content.lower() for m in e.messages)
        ]
        return matching[:limit]
```

**When to use**: Production systems, multi-session conversations, audit requirements.

## Pattern 6: Rolling Window with Compression

Maintain a rolling window with progressive compression of older content.

```python
@dataclass
class CompressedHistory:
    recent_messages: list[Message]  # Full detail
    recent_summaries: list[str]     # Recent episode summaries
    historical_summary: str         # Compressed old history

class RollingWindowManager:
    def __init__(
        self,
        recent_message_limit: int = 10,
        recent_summary_limit: int = 5,
        summarizer: Summarizer | None = None,
    ):
        self.recent_limit = recent_message_limit
        self.summary_limit = recent_summary_limit
        self.summarizer = summarizer

        self.recent_messages: list[Message] = []
        self.recent_summaries: list[str] = []
        self.historical_summary: str = ""
        self.episodes: list[Episode] = []

    def add_message(self, message: Message) -> None:
        self.recent_messages.append(message)

        # Compress when exceeding limit
        if len(self.recent_messages) > self.recent_limit:
            self._compress_messages()

    def _compress_messages(self) -> None:
        """Move oldest messages to summary."""
        # Take half the messages to summarize
        to_compress = self.recent_messages[:self.recent_limit // 2]
        self.recent_messages = self.recent_messages[self.recent_limit // 2:]

        # Create summary
        summary = self._quick_summary(to_compress)
        self.recent_summaries.append(summary)

        # Compress summaries if needed
        if len(self.recent_summaries) > self.summary_limit:
            self._compress_summaries()

    def _compress_summaries(self) -> None:
        """Merge old summaries into historical summary."""
        to_merge = self.recent_summaries[:self.summary_limit // 2]
        self.recent_summaries = self.recent_summaries[self.summary_limit // 2:]

        merged = " ".join(to_merge)
        if self.historical_summary:
            self.historical_summary = f"{self.historical_summary} {merged}"
        else:
            self.historical_summary = merged

    def _quick_summary(self, messages: list[Message]) -> str:
        """Quick extractive summary without LLM."""
        # Take first and last message as summary
        if not messages:
            return ""
        if len(messages) <= 2:
            return " | ".join(m.content[:100] for m in messages)
        return f"{messages[0].content[:100]} ... {messages[-1].content[:100]}"

    def get_history(self) -> CompressedHistory:
        return CompressedHistory(
            recent_messages=self.recent_messages.copy(),
            recent_summaries=self.recent_summaries.copy(),
            historical_summary=self.historical_summary,
        )
```

**When to use**: Long-running conversations, memory-constrained environments.

## Anti-Patterns to Avoid

### Anti-Pattern 1: Unbounded History
```python
# BAD: No limits
class BadManager:
    def add_message(self, msg):
        self.history.append(msg)  # Grows forever!
```

### Anti-Pattern 2: Synchronous Summarization
```python
# BAD: Blocks user response
def close_episode(self):
    self.summary = llm.summarize(self.messages)  # Slow!
    return response
```

### Anti-Pattern 3: Losing Context on Errors
```python
# BAD: Discards on error
try:
    context = build_context(episodes)
except Exception:
    context = ""  # Lost everything!

# GOOD: Graceful degradation
try:
    context = build_full_context(episodes)
except Exception:
    context = build_minimal_context(episodes)
```
