---
name: implementing-dual-mode-streaming
description: Patterns for building APIs that support both synchronous batch responses and asynchronous streaming responses, essential for modern LLM applications and real-time systems. Use when implementing authentication or verifying tokens.
---

# Dual Mode Streaming

## Quick Start
```python
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from typing import AsyncGenerator
import asyncio
import json

async def event_generator() -> AsyncGenerator[str, None]:
    for i in range(10):
        data = {"index": i, "message": f"Event {i}"}
        yield f"data: {json.dumps(data)}\n\n"
        await asyncio.sleep(0.1)

@app.get("/events")
async def stream_events():
    return StreamingResponse(
    # ... see docs/patterns.md for more
```


## Key Points
- Response Modes
- Server-Sent Events (SSE)
- Mode Detection

## More Detail
- [docs/concepts.md](docs/concepts.md) - Core concepts and theory
- [docs/patterns.md](docs/patterns.md) - Full code patterns and examples