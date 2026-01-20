# Episode-Based History Concepts

## Overview

Episode-based history is an architectural pattern for managing conversation context in LLM applications. Instead of maintaining a flat list of all messages, conversations are organized into logical episodes that can be independently managed, summarized, and retrieved.

## The Problem with Flat History

Traditional conversation history faces several challenges:

1. **Context Window Limits**: LLMs have finite context windows (4K-200K tokens)
2. **Relevance Decay**: Older messages may not be relevant to current topic
3. **Cost Accumulation**: Larger contexts cost more per API call
4. **Performance Degradation**: Longer contexts increase latency
5. **Topic Confusion**: Mixed topics in history can confuse the model

## Episode-Based Solution

Episodes solve these problems by:

- **Bounding conversations**: Clear start and end points
- **Enabling summarization**: Closed episodes can be compressed
- **Supporting selective retrieval**: Only relevant episodes included
- **Facilitating archival**: Old episodes can be stored separately

## Core Components

### 1. Message

The atomic unit of conversation:

```python
@dataclass
class Message:
    role: str              # "user", "assistant", "system"
    content: str           # The message text
    timestamp: datetime    # When the message was created
    metadata: dict         # Additional data (tokens, model, etc.)
```

### 2. Episode

A bounded segment of conversation:

```python
@dataclass
class Episode:
    id: str                      # Unique identifier
    topic: str                   # Episode topic/title
    messages: list[Message]      # Messages in this episode
    summary: str | None          # Compressed representation
    created_at: datetime         # Start time
    closed_at: datetime | None   # End time (None if active)
    metadata: dict               # Tags, categories, etc.
```

### 3. Episode Manager

Handles episode lifecycle:

```python
class EpisodeManager:
    def start_episode(topic: str) -> Episode
    def add_message(message: Message) -> None
    def close_episode() -> None
    def get_context(max_tokens: int) -> str
```

## Episode Lifecycle

```
         START                ACTIVE               CLOSE              ARCHIVED
           |                    |                   |                    |
    +------+------+      +------+------+     +------+------+     +------+------+
    | Create new  |      | Add messages|     | Generate    |     | Move to     |
    | episode with| ---> | Check for   | --> | summary     | --> | cold storage|
    | topic       |      | boundaries  |     | Mark closed |     | Keep summary|
    +-------------+      +-------------+     +-------------+     +-------------+
```

## Episode Boundaries

### Time-Based Boundaries

Create new episode after inactivity period:

```python
def check_time_boundary(episode: Episode, threshold: timedelta) -> bool:
    if not episode.messages:
        return False
    last_message_time = episode.messages[-1].timestamp
    return datetime.now() - last_message_time > threshold
```

### Topic-Based Boundaries

Detect topic changes using:
- Keyword extraction and comparison
- Embedding similarity
- Explicit topic markers

```python
def check_topic_boundary(
    episode: Episode,
    new_message: Message,
    similarity_threshold: float = 0.7
) -> bool:
    current_embedding = get_embedding(episode.topic)
    message_embedding = get_embedding(new_message.content)
    similarity = cosine_similarity(current_embedding, message_embedding)
    return similarity < similarity_threshold
```

### Size-Based Boundaries

Limit episode message count or token count:

```python
def check_size_boundary(
    episode: Episode,
    max_messages: int = 20,
    max_tokens: int = 3000
) -> bool:
    if len(episode.messages) >= max_messages:
        return True
    total_tokens = sum(count_tokens(m.content) for m in episode.messages)
    return total_tokens >= max_tokens
```

## Summarization Strategies

### Progressive Summarization

Different detail levels based on age:

```
Age 0-1 hour:   Full messages
Age 1-24 hours: Detailed summary (paragraph)
Age 1-7 days:   Brief summary (2-3 sentences)
Age 7+ days:    Key facts only (bullet points)
```

### Hierarchical Summarization

Summarize summaries for very old content:

```python
def hierarchical_summarize(episodes: list[Episode]) -> str:
    # Group episodes by time period
    recent = [e for e in episodes if e.age < timedelta(days=1)]
    older = [e for e in episodes if e.age >= timedelta(days=1)]

    # Summarize older episodes together
    older_summary = summarize_multiple(older)

    # Return combined context
    return f"{older_summary}\n\n{format_recent(recent)}"
```

### Extractive Summarization

Extract key sentences rather than generate:

```python
def extractive_summary(episode: Episode, max_sentences: int = 3) -> str:
    # Score sentences by importance
    sentences = extract_sentences(episode.messages)
    scored = [(s, importance_score(s)) for s in sentences]

    # Return top sentences
    top = sorted(scored, key=lambda x: x[1], reverse=True)[:max_sentences]
    return " ".join(s for s, _ in top)
```

## Context Building

### Token-Aware Building

```python
def build_context(
    episodes: list[Episode],
    max_tokens: int,
    include_system: bool = True
) -> list[dict]:
    messages = []
    remaining = max_tokens

    # Reserve tokens for system message
    if include_system:
        remaining -= SYSTEM_MESSAGE_TOKENS

    # Add episodes newest to oldest
    for episode in reversed(episodes):
        content = episode.summary if episode.is_closed else format_messages(episode)
        tokens = count_tokens(content)

        if tokens > remaining:
            break

        messages.insert(0, {"role": "context", "content": content})
        remaining -= tokens

    return messages
```

### Relevance-Based Retrieval

Include only relevant episodes:

```python
def get_relevant_episodes(
    query: str,
    episodes: list[Episode],
    top_k: int = 3
) -> list[Episode]:
    query_embedding = get_embedding(query)

    scored = []
    for episode in episodes:
        episode_embedding = get_embedding(episode.topic)
        score = cosine_similarity(query_embedding, episode_embedding)
        scored.append((episode, score))

    # Return top-k most relevant
    scored.sort(key=lambda x: x[1], reverse=True)
    return [e for e, _ in scored[:top_k]]
```

## Memory Tiers

### Hot Storage (In-Memory/Redis)

- Active episode
- Recent closed episodes (< 1 hour)
- Frequently accessed episodes

### Warm Storage (Database)

- Episode metadata
- Recent summaries
- Message references

### Cold Storage (Archive)

- Full message history
- Old episode summaries
- Audit logs

### Tier Management

```python
class TieredStorage:
    def __init__(self):
        self.hot = RedisStorage()      # Fast access
        self.warm = PostgresStorage()  # Queryable
        self.cold = S3Storage()        # Archival

    def store_episode(self, episode: Episode) -> None:
        if episode.age < timedelta(hours=1):
            self.hot.store(episode)
        elif episode.age < timedelta(days=7):
            self.warm.store(episode)
            self.hot.delete(episode.id)
        else:
            self.cold.store(episode)
            self.warm.delete_messages(episode.id)
```

## Best Practices

### 1. Always Bound Episodes

Never let episodes grow unbounded:

```python
# Bad: No limits
manager.add_message(message)

# Good: Enforce boundaries
if manager.should_close_episode():
    manager.close_and_summarize()
manager.add_message(message)
```

### 2. Preserve Key Information

When summarizing, keep:
- Decisions made
- Action items
- Important facts
- User preferences learned

### 3. Handle Edge Cases

```python
def get_context_safe(episodes: list[Episode], max_tokens: int) -> str:
    if not episodes:
        return ""

    if len(episodes) == 1 and not episodes[0].messages:
        return ""

    return build_context(episodes, max_tokens)
```

### 4. Monitor and Tune

Track metrics:
- Average episode length
- Summarization quality
- Context retrieval relevance
- Token usage per conversation
