# CLAUDE.md - SSE Streaming

This skill teaches Server-Sent Events (SSE) for streaming LLM responses including the protocol, FastAPI endpoints, and client consumption.

## Key Concepts

- **SSE Protocol**: HTTP-based server-to-client streaming with automatic reconnection
- **Event Format**: `data:` lines followed by double newline (`\n\n`)
- **StreamingResponse**: FastAPI response type for async generators
- **Event Types**: Custom event names with `event:` field
- **Keep-Alive**: Comment lines (`:`) to maintain connection
- **Client Consumption**: EventSource API in browsers, httpx in Python

## Common Commands

```bash
make setup      # Install dependencies with UV
make run-server # Start FastAPI server with uvicorn
make test-client # Run test client against server
make examples   # Run all examples
make example-1  # Run basic SSE endpoint example
make example-2  # Run LLM streaming example
make example-3  # Run client consumption example
make example-4  # Run production patterns example
make test       # Run pytest
make lint       # Run ruff and mypy
make clean      # Remove build artifacts
```

## Project Structure

```
sse-streaming/
├── src/sse_streaming/
│   ├── __init__.py
│   ├── server.py            # FastAPI SSE server
│   ├── client.py            # Python SSE client
│   └── examples/
│       ├── example_1_basic_sse.py
│       ├── example_2_llm_streaming.py
│       ├── example_3_client_consumption.py
│       └── example_4_production_patterns.py
├── exercises/
│   ├── exercise_1_chat_endpoint.py
│   ├── exercise_2_progress_streaming.py
│   ├── exercise_3_multi_source.py
│   └── solutions/
├── tests/
│   └── test_examples.py
└── docs/
    ├── concepts.md
    └── patterns.md
```

## Code Patterns

### Pattern 1: Basic SSE Generator
```python
async def event_generator():
    for i in range(10):
        yield f"data: Message {i}\n\n"
        await asyncio.sleep(0.1)
    yield "data: [DONE]\n\n"
```

### Pattern 2: SSE Endpoint with FastAPI
```python
from fastapi import FastAPI
from fastapi.responses import StreamingResponse

@app.get("/stream")
async def stream_endpoint():
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        }
    )
```

### Pattern 3: Streaming LLM Response
```python
import json
from openai import OpenAI

async def stream_llm(prompt: str):
    client = OpenAI()
    stream = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        stream=True
    )

    for chunk in stream:
        if content := chunk.choices[0].delta.content:
            yield f"data: {json.dumps({'content': content})}\n\n"

    yield "data: [DONE]\n\n"
```

### Pattern 4: Python Client
```python
import httpx

async def consume_stream(url: str):
    async with httpx.AsyncClient() as client:
        async with client.stream("GET", url) as response:
            async for line in response.aiter_lines():
                if line.startswith("data: "):
                    data = line[6:]
                    if data != "[DONE]":
                        yield json.loads(data)
```

### Pattern 5: Client Disconnection Handling
```python
from fastapi import Request

async def stream_with_disconnect(request: Request):
    async def generator():
        while True:
            if await request.is_disconnected():
                break
            yield f"data: heartbeat\n\n"
            await asyncio.sleep(1)

    return StreamingResponse(generator(), media_type="text/event-stream")
```

## Common Mistakes

1. **Missing double newline**
   - SSE messages MUST end with `\n\n`
   - Single `\n` will cause buffering

2. **Wrong content type**
   - Must be `text/event-stream`
   - Not `application/json` or `text/plain`

3. **Not handling disconnection**
   - Check `request.is_disconnected()` in loops
   - Clean up resources when client disconnects

4. **Buffering issues with proxies**
   - Add `X-Accel-Buffering: no` for nginx
   - Add `Cache-Control: no-cache, no-transform`

5. **Not sending keep-alive for long gaps**
   - Send `:` comment lines every 15-30 seconds
   - Prevents proxy timeouts

## When Users Ask About...

### "How do I get started?"
Point them to `make setup && make example-1` and README.md. The basic example shows minimal SSE.

### "Why am I not seeing streaming?"
Check:
1. Content-Type is `text/event-stream`
2. Lines end with `\n\n` (double newline)
3. Proxy isn't buffering (add X-Accel-Buffering header)
4. Client is consuming the stream correctly

### "How do I stream LLM responses?"
```python
@app.get("/chat")
async def chat(prompt: str):
    return StreamingResponse(
        stream_llm(prompt),
        media_type="text/event-stream"
    )
```

### "How do I test SSE endpoints?"
Use pytest-asyncio with httpx:
```python
async def test_sse():
    async with httpx.AsyncClient(app=app) as client:
        async with client.stream("GET", "/stream") as response:
            lines = [line async for line in response.aiter_lines()]
            assert any("data:" in line for line in lines)
```

### "SSE vs WebSocket - which should I use?"
- SSE: Server-to-client only, simpler, better proxy support
- WebSocket: Bidirectional, more complex, may need proxy config
- For LLM streaming: SSE is usually the better choice

### "How do I handle errors?"
```python
try:
    async for chunk in stream:
        yield f"data: {chunk}\n\n"
except Exception as e:
    yield f"event: error\ndata: {json.dumps({'error': str(e)})}\n\n"
```

## Testing Notes

- Use pytest-asyncio for async tests
- httpx AsyncClient for streaming tests
- Test both happy path and error cases
- Verify proper event format

## Dependencies

Key dependencies in pyproject.toml:
- fastapi>=0.100.0: Web framework
- uvicorn: ASGI server
- httpx: Async HTTP client
- openai: LLM provider (optional)
- sse-starlette: SSE utilities (optional)

## SSE Message Format Reference

```
: This is a comment (used for keep-alive)

event: custom_event
data: {"type": "custom"}

data: Simple message without event type

id: 123
data: Message with ID for reconnection

retry: 5000
data: Set reconnection timeout to 5 seconds
```

## Browser EventSource API

```javascript
const es = new EventSource('/stream');

// Default message event
es.onmessage = (e) => console.log(e.data);

// Custom events
es.addEventListener('custom_event', (e) => {
    console.log('Custom:', e.data);
});

// Error handling
es.onerror = (e) => {
    console.error('Error:', e);
    es.close();
};
```
