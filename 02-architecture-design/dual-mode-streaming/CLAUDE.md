# CLAUDE.md - Dual-Mode Streaming

This skill teaches patterns for building APIs that support both synchronous batch responses and asynchronous streaming responses, essential for modern LLM applications and real-time systems.

## Key Concepts

- **Response Modes**: Batch (complete response) vs Streaming (incremental chunks)
- **Server-Sent Events (SSE)**: HTTP-based streaming protocol for unidirectional server push
- **Mode Detection**: Determining response type from headers, params, or negotiation
- **AsyncGenerators**: Python's mechanism for yielding values asynchronously
- **Backpressure**: Flow control when consumers can't keep up with producers
- **Event Formatting**: Proper SSE message structure with data/event/id fields

## Common Commands

```bash
make setup      # Install dependencies with UV
make examples   # Run all examples
make example-1  # Run basic streaming example
make example-2  # Run mode detection example
make example-3  # Run LLM-style streaming example
make example-4  # Run backpressure handling example
make test       # Run pytest
make lint       # Run ruff and mypy
make clean      # Remove build artifacts
```

## Project Structure

```
dual-mode-streaming/
├── src/dual_mode_streaming/
│   ├── __init__.py
│   ├── modes.py           # ResponseMode enum and detection
│   ├── streaming.py       # Streaming utilities
│   └── examples/
│       ├── example_1_basic_streaming.py
│       ├── example_2_mode_detection.py
│       ├── example_3_llm_streaming.py
│       └── example_4_backpressure.py
├── exercises/
│   ├── exercise_1_dual_mode.py
│   ├── exercise_2_progress_reporter.py
│   ├── exercise_3_llm_simulator.py
│   └── solutions/
├── tests/
│   ├── test_streaming.py
│   └── test_mode_detection.py
└── docs/
    ├── concepts.md
    └── patterns.md
```

## Code Patterns

### Pattern 1: Basic SSE Streaming
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
        event_generator(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache"}
    )
```

### Pattern 2: Mode Detection from Headers
```python
from fastapi import Request

def detect_mode(request: Request) -> ResponseMode:
    accept = request.headers.get("accept", "")
    if "text/event-stream" in accept:
        return ResponseMode.STREAM
    return ResponseMode.BATCH
```

### Pattern 3: Unified Dual-Mode Handler
```python
from fastapi import Query

@app.get("/data")
async def get_data(
    request: Request,
    stream: bool = Query(default=False)
):
    mode = ResponseMode.STREAM if stream else detect_mode(request)

    if mode == ResponseMode.STREAM:
        return StreamingResponse(
            generate_stream(),
            media_type="text/event-stream"
        )

    # Batch mode - collect all and return
    return {"data": await collect_all()}
```

### Pattern 4: LLM-Style Token Streaming
```python
async def stream_tokens(text: str) -> AsyncGenerator[str, None]:
    words = text.split()
    for i, word in enumerate(words):
        chunk = {
            "id": f"chunk-{i}",
            "object": "chat.completion.chunk",
            "choices": [{
                "delta": {"content": word + " "},
                "index": 0
            }]
        }
        yield f"data: {json.dumps(chunk)}\n\n"
        await asyncio.sleep(0.05)
    yield "data: [DONE]\n\n"
```

### Pattern 5: Graceful Client Disconnection
```python
async def resilient_generator() -> AsyncGenerator[str, None]:
    try:
        async for chunk in source_generator():
            yield chunk
    except asyncio.CancelledError:
        logger.info("Client disconnected, cleaning up")
        await cleanup_resources()
        raise
```

## Common Mistakes

1. **Wrong Content-Type for SSE**
   - Must use `text/event-stream` for EventSource clients
   - JSON content-type won't work with browser EventSource API

2. **Incorrect SSE Format**
   - Each message must start with `data: `
   - Each message must end with `\n\n` (double newline)
   - Multi-line data needs `data: ` prefix on each line

3. **Blocking in async generators**
   - Use `await asyncio.sleep()` not `time.sleep()`
   - Use async versions of I/O operations

4. **Not handling CancelledError**
   - Clients may disconnect mid-stream
   - Always cleanup resources in finally or except block

5. **Missing Cache-Control headers**
   - SSE responses should have `Cache-Control: no-cache`
   - Prevents proxies from buffering the stream

## When Users Ask About...

### "How do I test streaming endpoints?"
Use pytest with httpx's async client:
```python
async with httpx.AsyncClient(app=app) as client:
    async with client.stream("GET", "/events") as response:
        async for line in response.aiter_lines():
            # Process each SSE event
```

### "How do I add authentication to streaming?"
Add auth as a dependency that runs before streaming:
```python
@app.get("/events")
async def events(user: User = Depends(get_current_user)):
    return StreamingResponse(generate_events(user))
```

### "When should I use streaming vs batch?"
- **Stream**: Long responses, real-time updates, LLM tokens, progress
- **Batch**: Short responses, transactional data, when client needs all data

### "How do I handle errors during streaming?"
Send errors as SSE events:
```python
try:
    yield f"data: {json.dumps(result)}\n\n"
except Exception as e:
    yield f"event: error\ndata: {json.dumps({'error': str(e)})}\n\n"
```

## Testing Notes

- Tests use pytest-asyncio for async test support
- httpx is used for testing streaming responses
- Use `pytest.mark.asyncio` on async test functions
- Integration tests start a test server for end-to-end streaming tests

## Dependencies

Key dependencies in pyproject.toml:
- fastapi>=0.109.0: Web framework with streaming support
- uvicorn>=0.27.0: ASGI server for running examples
- httpx>=0.26.0: Async HTTP client for testing
- pytest-asyncio>=0.23.0: Async test support
