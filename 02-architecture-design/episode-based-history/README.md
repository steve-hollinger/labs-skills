# Episode-Based History

Master conversation history management for LLM applications using episode boundaries, summarization, and memory optimization patterns.

## Learning Objectives

After completing this skill, you will be able to:
- Design episode-based conversation structures
- Implement history summarization strategies
- Optimize memory usage in long conversations
- Handle context window limitations effectively
- Build stateful conversation systems

## Prerequisites

- Python 3.11+
- Understanding of LLM context windows
- Basic async Python patterns
- Familiarity with Pydantic

## Quick Start

```bash
# Install dependencies
make setup

# Run examples
make examples

# Run tests
make test
```

## Core Concepts

### What is Episode-Based History?

Episode-based history organizes conversations into logical segments (episodes) rather than treating them as continuous streams. This approach enables:

- **Memory efficiency**: Summarize old episodes instead of keeping full history
- **Context relevance**: Retrieve only episodes relevant to current conversation
- **Clear boundaries**: Natural breakpoints for conversation topics
- **Scalable storage**: Episodes can be archived and retrieved on demand

### Episode Structure

```python
@dataclass
class Episode:
    id: str
    topic: str
    messages: list[Message]
    summary: str | None
    created_at: datetime
    closed_at: datetime | None
    metadata: dict
```

### Why Episodes?

| Challenge | Episode Solution |
|-----------|-----------------|
| Context window limits | Summarize closed episodes |
| Topic drift | Create new episode on topic change |
| Long conversations | Archive old episodes |
| Relevance | Retrieve only related episodes |
| Cost | Send summaries instead of full history |

## Examples

### Example 1: Basic Episode Management

Demonstrates creating, managing, and closing episodes in a conversation.

```bash
make example-1
```

### Example 2: History Summarization

Shows strategies for summarizing episodes to fit within context limits.

```bash
make example-2
```

### Example 3: Smart Context Building

Advanced pattern for building context from multiple episodes based on relevance.

```bash
make example-3
```

### Example 4: Persistent Episode Storage

Demonstrates storing and retrieving episodes from persistent storage.

```bash
make example-4
```

## Key Patterns

### Episode Boundary Detection

```python
def should_create_new_episode(
    current_episode: Episode,
    new_message: Message,
) -> bool:
    # Time-based boundary
    if time_since_last_message(current_episode) > timedelta(hours=1):
        return True

    # Topic-based boundary (using embedding similarity)
    if topic_similarity(current_episode.topic, new_message.content) < 0.5:
        return True

    # Size-based boundary
    if len(current_episode.messages) > 20:
        return True

    return False
```

### Summarization Strategy

```python
async def summarize_episode(episode: Episode) -> str:
    """Create a concise summary of an episode."""
    if len(episode.messages) <= 3:
        # Short episodes don't need summarization
        return format_messages(episode.messages)

    prompt = f"""
    Summarize this conversation episode:
    Topic: {episode.topic}
    Messages: {format_messages(episode.messages)}

    Create a 2-3 sentence summary capturing key points and decisions.
    """
    return await llm.complete(prompt)
```

### Context Window Management

```python
def build_context(
    episodes: list[Episode],
    max_tokens: int = 4000,
) -> str:
    """Build context from episodes within token limit."""
    context_parts = []
    token_count = 0

    for episode in reversed(episodes):  # Most recent first
        if episode.is_closed and episode.summary:
            content = f"[Previous: {episode.summary}]"
        else:
            content = format_episode(episode)

        episode_tokens = count_tokens(content)
        if token_count + episode_tokens > max_tokens:
            break

        context_parts.insert(0, content)
        token_count += episode_tokens

    return "\n\n".join(context_parts)
```

## Exercises

See the [exercises](./exercises/) directory for practice problems:

1. **Exercise 1**: Implement Episode Manager - Build a class to manage episode lifecycle
2. **Exercise 2**: Build Summarizer Pipeline - Create a multi-stage summarization system
3. **Exercise 3**: Context Retrieval System - Implement relevance-based episode retrieval

Solutions are available in [exercises/solutions/](./exercises/solutions/).

## Common Mistakes

### Not Detecting Topic Changes

```python
# Bad: Always appending to same episode
def add_message(message):
    current_episode.messages.append(message)

# Good: Check for topic changes
def add_message(message):
    if should_create_new_episode(current_episode, message):
        close_episode(current_episode)
        current_episode = create_episode(message)
    current_episode.messages.append(message)
```

### Summarizing Too Aggressively

```python
# Bad: Lose important details
summary = "User asked about Python"

# Good: Preserve key information
summary = """
User asked about Python async patterns. Discussed:
- asyncio basics and event loops
- When to use async vs threading
- Recommended aiohttp for HTTP clients
User will implement async API client.
"""
```

### Ignoring Context Window Limits

```python
# Bad: May exceed context window
context = "\n".join(all_messages)

# Good: Respect limits
context = build_context(episodes, max_tokens=4000)
```

## Memory Optimization Strategies

### 1. Rolling Summarization

As episodes close, create progressively compressed summaries:
- Full messages (active episode)
- Detailed summary (recent closed)
- Brief summary (older closed)
- Key facts only (archived)

### 2. Selective Retrieval

Only include relevant episodes:
- Current episode (full)
- Related episodes (summaries)
- Ignore unrelated episodes

### 3. Hierarchical Storage

```
Hot Storage (Redis):     Active episode, recent summaries
Warm Storage (Database): Recent episode details
Cold Storage (Archive):  Historical episode summaries
```

## Further Reading

- [Context Window Optimization](https://docs.anthropic.com/claude/docs/optimizing-context)
- [Conversation Memory Patterns](https://langchain.com/docs/modules/memory)
- Related skills in this repository:
  - [Four-Layer Prompts](../four-layer-prompts/)
  - [LLM Integration](../../06-ai-ml/llm-integration/)
  - [Valkey Cache](../../05-data-databases/valkey-cache/)
