---
name: managing-episode-history
description: This skill teaches conversation history management using episode boundaries, summarization strategies, and memory optimization patterns for LLM applications. Use when writing or improving tests.
---

# Episode Based History

## Quick Start
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
    # ... see docs/patterns.md for more
```

## Commands
```bash
make setup      # Install dependencies with UV
make examples   # Run all examples
make example-1  # Run basic episode management
make example-2  # Run history summarization
make example-3  # Run smart context building
make example-4  # Run persistent storage
```

## Key Points
- Episode
- Episode Boundary
- Summarization

## Common Mistakes
1. **No episode boundaries** - Implement time, topic, or size-based boundaries
2. **Losing important context in summaries** - Preserve decisions, conclusions, and action items
3. **Not handling concurrent access** - Use locks or episode versioning

## More Detail
- [docs/concepts.md](docs/concepts.md) - Core concepts and theory
- [docs/patterns.md](docs/patterns.md) - Full code patterns and examples