# Dual-Mode Streaming Concepts

## Overview

Dual-mode streaming is an architectural pattern that allows APIs to serve responses in two distinct ways: as complete batch responses or as incremental streaming responses. This flexibility is crucial for modern applications, especially those involving LLMs, real-time data, or long-running operations.

## Core Concepts

### 1. Response Modes

#### Batch Mode (Synchronous)
- Complete response returned in a single HTTP response body
- Traditional REST pattern
- Client waits for entire response
- Simple to implement and cache

```python
# Batch response
@app.get("/data")
async def get_data():
    result = await process_all_data()
    return {"data": result}  # Single complete response
```

#### Streaming Mode (Asynchronous)
- Response delivered incrementally as chunks
- Client receives data as it becomes available
- Better perceived performance for long operations
- Cannot be cached traditionally

```python
# Streaming response
@app.get("/stream")
async def stream_data():
    async def generate():
        async for chunk in process_data_incrementally():
            yield f"data: {chunk}\n\n"
    return StreamingResponse(generate(), media_type="text/event-stream")
```

### 2. Server-Sent Events (SSE)

SSE is a W3C standard for unidirectional server-to-client streaming over HTTP.

#### SSE Message Format
```
event: message-type
id: unique-id
data: payload-line-1
data: payload-line-2

```

Key rules:
- Each field starts with its name followed by colon and space
- `data:` field contains the payload (can span multiple lines)
- Each line prefixed with `data:` is concatenated with newlines
- Messages end with double newline (`\n\n`)
- `event:` specifies custom event type (default is "message")
- `id:` enables reconnection from last received ID

#### Python SSE Generator
```python
import json

async def sse_generator():
    for i in range(10):
        event_data = {"index": i, "value": f"Item {i}"}
        # Format as SSE
        yield f"data: {json.dumps(event_data)}\n\n"
```

### 3. Mode Detection Strategies

#### Accept Header Detection
```python
def detect_from_headers(request: Request) -> ResponseMode:
    accept = request.headers.get("accept", "application/json")
    if "text/event-stream" in accept:
        return ResponseMode.STREAM
    return ResponseMode.BATCH
```

#### Query Parameter
```python
@app.get("/data")
async def get_data(stream: bool = Query(default=False)):
    if stream:
        return StreamingResponse(...)
    return JSONResponse(...)
```

#### Content Negotiation
```python
def negotiate_mode(request: Request) -> ResponseMode:
    # Priority: explicit param > header > default
    if request.query_params.get("stream") == "true":
        return ResponseMode.STREAM
    if "text/event-stream" in request.headers.get("accept", ""):
        return ResponseMode.STREAM
    return ResponseMode.BATCH
```

### 4. AsyncGenerators in Python

AsyncGenerators are the foundation of streaming in Python:

```python
from typing import AsyncGenerator

async def generate_numbers() -> AsyncGenerator[int, None]:
    for i in range(10):
        await asyncio.sleep(0.1)  # Simulate async work
        yield i  # Yield value to consumer
```

Key characteristics:
- Defined with `async def` and contain `yield`
- Return type is `AsyncGenerator[YieldType, SendType]`
- Consumed with `async for` loops
- Can be cancelled, triggering cleanup

### 5. Backpressure

Backpressure occurs when producers generate data faster than consumers can process it.

#### Problem
```python
# Fast producer, slow consumer = memory growth
async def fast_producer():
    while True:
        yield generate_large_chunk()  # No waiting!
```

#### Solution: Rate Limiting
```python
async def controlled_producer(max_pending: int = 10):
    pending = asyncio.Queue(maxsize=max_pending)
    async for chunk in source:
        await pending.put(chunk)  # Blocks when full
        yield await pending.get()
```

#### Solution: Client-Driven Pace
```python
async def client_paced_stream(request: Request):
    async def generate():
        async for chunk in source:
            if await request.is_disconnected():
                break  # Stop if client gone
            yield chunk
    return StreamingResponse(generate())
```

## Architecture Patterns

### Dual-Mode Service Pattern

```python
class DataService:
    async def get_batch(self) -> list[dict]:
        """Return all data as a list."""
        return [item async for item in self._fetch_items()]

    async def get_stream(self) -> AsyncGenerator[dict, None]:
        """Yield items one at a time."""
        async for item in self._fetch_items():
            yield item

    async def _fetch_items(self) -> AsyncGenerator[dict, None]:
        # Shared implementation
        async for item in database.stream_query():
            yield item
```

### Unified Handler Pattern

```python
@app.get("/items")
async def get_items(
    request: Request,
    service: DataService = Depends(),
    stream: bool = Query(default=False)
):
    mode = ResponseMode.STREAM if stream else detect_mode(request)

    if mode == ResponseMode.STREAM:
        async def generate():
            async for item in service.get_stream():
                yield f"data: {json.dumps(item)}\n\n"
        return StreamingResponse(generate(), media_type="text/event-stream")

    return {"items": await service.get_batch()}
```

### LLM Response Pattern

```python
@dataclass
class StreamChunk:
    id: str
    content: str
    finish_reason: str | None = None

async def stream_llm_response(prompt: str) -> AsyncGenerator[str, None]:
    async for token in llm.generate(prompt):
        chunk = StreamChunk(
            id=f"chunk-{uuid4()}",
            content=token,
            finish_reason=None
        )
        yield f"data: {json.dumps(asdict(chunk))}\n\n"

    # Signal completion
    yield "data: [DONE]\n\n"
```

## Performance Considerations

### When to Use Streaming

| Scenario | Recommendation |
|----------|----------------|
| Response > 1 second | Stream |
| Real-time updates needed | Stream |
| LLM token output | Stream |
| Progress tracking | Stream |
| Response < 100ms | Batch |
| Cacheable data | Batch |
| Transactional data | Batch |

### Memory Efficiency

Streaming reduces memory usage by not buffering entire responses:

```python
# Memory inefficient - holds all in memory
async def batch_large_data():
    all_items = []
    async for item in fetch_millions():
        all_items.append(item)
    return {"items": all_items}

# Memory efficient - streams as processed
async def stream_large_data():
    async def generate():
        async for item in fetch_millions():
            yield f"data: {json.dumps(item)}\n\n"
    return StreamingResponse(generate())
```

## Error Handling

### Errors Before Streaming
```python
@app.get("/stream")
async def stream_with_validation(data_id: str):
    # Validate before streaming starts
    if not await exists(data_id):
        raise HTTPException(404, "Not found")

    # Start streaming only after validation
    return StreamingResponse(generate(data_id))
```

### Errors During Streaming
```python
async def error_aware_generator():
    try:
        async for item in source:
            yield f"data: {json.dumps(item)}\n\n"
    except ProcessingError as e:
        # Send error as event
        error_event = {"type": "error", "message": str(e)}
        yield f"event: error\ndata: {json.dumps(error_event)}\n\n"
```

## Client Integration

### JavaScript EventSource
```javascript
const eventSource = new EventSource('/stream');

eventSource.onmessage = (event) => {
    const data = JSON.parse(event.data);
    console.log('Received:', data);
};

eventSource.onerror = (error) => {
    console.error('Stream error:', error);
    eventSource.close();
};
```

### Python Client with httpx
```python
async with httpx.AsyncClient() as client:
    async with client.stream("GET", "/stream") as response:
        async for line in response.aiter_lines():
            if line.startswith("data: "):
                data = json.loads(line[6:])
                print(f"Received: {data}")
```
