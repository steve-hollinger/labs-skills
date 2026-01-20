# Dual-Mode Streaming

Master synchronous and asynchronous response patterns for building flexible APIs that support both streaming and batch response modes.

## Learning Objectives

After completing this skill, you will be able to:
- Implement dual-mode APIs that support both sync and async responses
- Build streaming endpoints with Server-Sent Events (SSE)
- Design mode detection and automatic switching mechanisms
- Handle backpressure and flow control in streaming responses
- Create unified interfaces that abstract response mode complexity

## Prerequisites

- Python 3.11+
- Understanding of async/await patterns
- Basic FastAPI knowledge
- Familiarity with HTTP response types

## Quick Start

```bash
# Install dependencies
make setup

# Run examples
make examples

# Run tests
make test
```

## Concepts

### What is Dual-Mode Streaming?

Dual-mode streaming allows APIs to serve responses in two ways:
1. **Batch Mode**: Complete response returned at once (traditional REST)
2. **Streaming Mode**: Response delivered incrementally (SSE, WebSockets)

This pattern is essential for:
- LLM applications where tokens arrive incrementally
- Long-running operations with progress updates
- Real-time data feeds
- Responsive UIs that show partial results

### Mode Detection

APIs can determine response mode through:
- HTTP Accept headers (`text/event-stream` vs `application/json`)
- Query parameters (`?stream=true`)
- Request body flags
- Client capability negotiation

### Streaming Patterns

```python
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from typing import AsyncGenerator

app = FastAPI()

async def generate_chunks() -> AsyncGenerator[str, None]:
    for i in range(10):
        yield f"data: chunk {i}\n\n"
        await asyncio.sleep(0.1)

@app.get("/stream")
async def stream_response():
    return StreamingResponse(
        generate_chunks(),
        media_type="text/event-stream"
    )
```

### Batch Patterns

```python
@app.get("/batch")
async def batch_response():
    chunks = [f"chunk {i}" for i in range(10)]
    return {"data": chunks}
```

### Unified Interface

```python
from enum import Enum

class ResponseMode(Enum):
    STREAM = "stream"
    BATCH = "batch"

@app.get("/unified")
async def unified_response(mode: ResponseMode = ResponseMode.BATCH):
    if mode == ResponseMode.STREAM:
        return StreamingResponse(generate_chunks())
    return {"data": list(range(10))}
```

## Examples

### Example 1: Basic Streaming

Demonstrates basic SSE streaming with FastAPI, including proper event formatting and client connection handling.

```bash
make example-1
```

### Example 2: Mode Detection

Shows automatic mode switching based on Accept headers and query parameters.

```bash
make example-2
```

### Example 3: LLM-Style Streaming

Implements token-by-token streaming similar to ChatGPT/Claude APIs with proper SSE formatting.

```bash
make example-3
```

### Example 4: Backpressure Handling

Advanced pattern for handling slow clients and implementing flow control.

```bash
make example-4
```

## Exercises

See the [exercises](./exercises/) directory for practice problems:

1. **Exercise 1**: Implement Basic Dual-Mode Endpoint - Create an endpoint that switches between streaming and batch based on query params
2. **Exercise 2**: Build a Progress Reporter - Stream progress updates for a long-running task
3. **Exercise 3**: Create LLM Response Simulator - Build a streaming response that mimics LLM token generation

Solutions are available in [exercises/solutions/](./exercises/solutions/).

## Common Mistakes

### Not Setting Correct Content-Type

Streaming responses must use `text/event-stream`:

```python
# Correct
StreamingResponse(gen(), media_type="text/event-stream")

# Incorrect - may not work with EventSource
StreamingResponse(gen(), media_type="application/json")
```

### Forgetting SSE Format

Server-Sent Events require specific formatting:

```python
# Correct SSE format
yield f"data: {json.dumps(payload)}\n\n"

# Incorrect - missing data: prefix and double newline
yield json.dumps(payload)
```

### Blocking in Async Generators

```python
# Incorrect - blocks the event loop
async def generate():
    for chunk in chunks:
        time.sleep(1)  # Blocking!
        yield chunk

# Correct - use async sleep
async def generate():
    for chunk in chunks:
        await asyncio.sleep(1)
        yield chunk
```

### Not Handling Client Disconnection

```python
async def generate():
    try:
        for chunk in chunks:
            yield chunk
    except asyncio.CancelledError:
        # Client disconnected - cleanup here
        raise
```

## Further Reading

- [Server-Sent Events Specification](https://html.spec.whatwg.org/multipage/server-sent-events.html)
- [FastAPI StreamingResponse](https://fastapi.tiangolo.com/advanced/custom-response/#streamingresponse)
- Related skills in this repository:
  - [FastAPI Basics](../../01-language-frameworks/python/fastapi-basics/)
  - [Async Python](../../01-language-frameworks/python/async-python/)
