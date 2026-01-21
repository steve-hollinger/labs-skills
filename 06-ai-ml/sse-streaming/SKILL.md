---
name: streaming-server-sent-events
description: Server-Sent Events (SSE) for streaming LLM responses including the protocol, FastAPI endpoints, and client consumption. Use when writing or improving tests.
---

# Sse Streaming

## Quick Start
```python
async def event_generator():
    for i in range(10):
        yield f"data: Message {i}\n\n"
        await asyncio.sleep(0.1)
    yield "data: [DONE]\n\n"
```


## Key Points
- SSE Protocol
- Event Format
- StreamingResponse

## More Detail
- [docs/concepts.md](docs/concepts.md) - Core concepts and theory
- [docs/patterns.md](docs/patterns.md) - Full code patterns and examples