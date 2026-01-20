# CLAUDE.md - Episode-Based History

This skill teaches conversation history management using episode boundaries, summarization strategies, and memory optimization patterns for LLM applications.

## Key Concepts

- **Episode**: A bounded segment of conversation around a topic or time period
- **Episode Boundary**: The point where one episode ends and another begins
- **Summarization**: Compressing closed episodes to preserve meaning in fewer tokens
- **Context Building**: Assembling relevant history within token limits
- **Memory Tiers**: Hot/warm/cold storage for different history ages
- **Rolling Window**: Keeping recent history detailed, older history summarized

## Common Commands

```bash
make setup      # Install dependencies with UV
make examples   # Run all examples
make example-1  # Run basic episode management
make example-2  # Run history summarization
make example-3  # Run smart context building
make example-4  # Run persistent storage
make test       # Run pytest
make lint       # Run ruff and mypy
make clean      # Remove build artifacts
```

## Project Structure

```
episode-based-history/
├── src/episode_history/
│   ├── __init__.py
│   ├── episode.py         # Episode data structures
│   ├── manager.py         # Episode lifecycle management
│   ├── summarizer.py      # Summarization strategies
│   ├── context.py         # Context building utilities
│   └── examples/
│       ├── example_1_basic_management.py
│       ├── example_2_summarization.py
│       ├── example_3_context_building.py
│       └── example_4_persistent_storage.py
├── exercises/
│   ├── exercise_1_episode_manager.py
│   ├── exercise_2_summarizer_pipeline.py
│   ├── exercise_3_context_retrieval.py
│   └── solutions/
├── tests/
│   ├── test_episode.py
│   ├── test_manager.py
│   └── test_summarizer.py
└── docs/
    ├── concepts.md
    └── patterns.md
```

## Code Patterns

### Pattern 1: Episode Data Structure
```python
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

@dataclass
class Message:
    role: str  # "user" or "assistant"
    content: str
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: dict[str, Any] = field(default_factory=dict)

@dataclass
class Episode:
    id: str
    topic: str
    messages: list[Message] = field(default_factory=list)
    summary: str | None = None
    created_at: datetime = field(default_factory=datetime.now)
    closed_at: datetime | None = None

    @property
    def is_closed(self) -> bool:
        return self.closed_at is not None

    @property
    def message_count(self) -> int:
        return len(self.messages)
```

### Pattern 2: Episode Manager
```python
class EpisodeManager:
    def __init__(self, max_messages_per_episode: int = 20):
        self.episodes: list[Episode] = []
        self.current_episode: Episode | None = None
        self.max_messages = max_messages_per_episode

    def add_message(self, message: Message) -> None:
        if self._should_start_new_episode(message):
            self._close_current_episode()
            self._start_new_episode(message.content)
        self.current_episode.messages.append(message)

    def _should_start_new_episode(self, message: Message) -> bool:
        if not self.current_episode:
            return True
        if self.current_episode.message_count >= self.max_messages:
            return True
        return False
```

### Pattern 3: Summarization Strategy
```python
async def summarize_episode(
    episode: Episode,
    style: str = "concise"
) -> str:
    """Summarize an episode for context compression."""
    if episode.message_count <= 2:
        # Very short - just format messages
        return format_as_summary(episode.messages)

    messages_text = "\n".join(
        f"{m.role}: {m.content}" for m in episode.messages
    )

    prompt = f"""
    Summarize this conversation:
    Topic: {episode.topic}

    {messages_text}

    Provide a {style} summary (2-3 sentences) capturing:
    - Main topic discussed
    - Key decisions or conclusions
    - Any action items
    """

    return await llm_complete(prompt)
```

### Pattern 4: Context Building with Token Limits
```python
def build_context(
    episodes: list[Episode],
    max_tokens: int,
    current_message: str,
) -> str:
    """Build context from episodes within token budget."""
    parts = []
    remaining_tokens = max_tokens

    # Always include current message tokens in budget
    remaining_tokens -= estimate_tokens(current_message)

    # Process episodes from newest to oldest
    for episode in reversed(episodes):
        if episode.is_closed:
            # Use summary for closed episodes
            content = f"[Previous conversation: {episode.summary}]"
        else:
            # Full messages for active episode
            content = format_episode_messages(episode)

        tokens = estimate_tokens(content)
        if tokens > remaining_tokens:
            break

        parts.insert(0, content)
        remaining_tokens -= tokens

    return "\n\n".join(parts)
```

## Common Mistakes

1. **No episode boundaries**
   - Creates one giant episode that exceeds context
   - Fix: Implement time, topic, or size-based boundaries

2. **Losing important context in summaries**
   - Over-compressed summaries lose key details
   - Fix: Preserve decisions, conclusions, and action items

3. **Not handling concurrent access**
   - Race conditions when multiple requests modify history
   - Fix: Use locks or episode versioning

4. **Ignoring token limits**
   - Building context that exceeds model's limit
   - Fix: Always count tokens and truncate

5. **Synchronous summarization blocking**
   - Summarization during request slows response
   - Fix: Summarize asynchronously after episode closes

## When Users Ask About...

### "How long should an episode be?"
Depends on use case:
- Task-focused: Until task completes
- Chat: 10-20 messages or topic change
- Support: Until issue resolved
- General: Time-based (30min-1hr gap)

### "When should I summarize?"
- When episode closes (async, background)
- When approaching token limits
- When archiving to cold storage

### "How do I detect topic changes?"
Options:
1. Keyword extraction and comparison
2. Embedding similarity threshold
3. Explicit user signals ("Let's talk about...")
4. Time gaps between messages

### "How do I handle multiple users?"
- Separate episode chains per user/conversation
- Include user ID in episode metadata
- Consider shared vs private history

### "What about sensitive data?"
- Sanitize before summarization
- Consider not storing certain message types
- Implement retention policies

## Testing Notes

- Tests use pytest-asyncio for async functions
- Mock LLM calls for summarization tests
- Test edge cases: empty episodes, single messages
- Test token counting accuracy
- Test concurrent episode modifications

## Dependencies

Key dependencies in pyproject.toml:
- pydantic>=2.5.0: Data validation
- tiktoken>=0.5.0: Token counting
- pytest-asyncio>=0.23.0: Async test support
