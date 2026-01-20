---
name: implementing-dual-mode-streaming
description: This skill teaches patterns for building APIs that support both synchronous batch responses and asynchronous streaming responses, essential for modern LLM applications and real-time systems. Use when implementing authentication or verifying tokens.
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

## Commands
```bash
make setup      # Install dependencies with UV
make examples   # Run all examples
make example-1  # Run basic streaming example
make example-2  # Run mode detection example
make example-3  # Run LLM-style streaming example
make example-4  # Run backpressure handling example
```

## Key Points
- Response Modes
- Server-Sent Events (SSE)
- Mode Detection

## More Detail
- [docs/concepts.md](docs/concepts.md) - Core concepts and theory
- [docs/patterns.md](docs/patterns.md) - Full code patterns and examples