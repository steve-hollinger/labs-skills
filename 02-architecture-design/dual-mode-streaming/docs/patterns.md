# Dual-Mode Streaming Patterns

## Pattern 1: Simple Mode Switch

The most basic dual-mode pattern using a query parameter.

```python
from fastapi import FastAPI, Query
from fastapi.responses import StreamingResponse, JSONResponse
from typing import AsyncGenerator
import asyncio
import json

app = FastAPI()

async def generate_items() -> AsyncGenerator[dict, None]:
    """Shared generator for both modes."""
    for i in range(10):
        await asyncio.sleep(0.1)
        yield {"id": i, "value": f"item-{i}"}

@app.get("/items")
async def get_items(stream: bool = Query(default=False)):
    if stream:
        async def sse_generator():
            async for item in generate_items():
                yield f"data: {json.dumps(item)}\n\n"
        return StreamingResponse(
            sse_generator(),
            media_type="text/event-stream"
        )

    # Batch mode - collect all items
    items = [item async for item in generate_items()]
    return JSONResponse({"items": items})
```

**When to use**: Simple APIs where explicit client control is preferred.

## Pattern 2: Content Negotiation

Automatic mode detection based on HTTP Accept header.

```python
from fastapi import FastAPI, Request, Depends
from enum import Enum

class ResponseMode(Enum):
    BATCH = "batch"
    STREAM = "stream"

def get_response_mode(request: Request) -> ResponseMode:
    """Detect mode from Accept header."""
    accept = request.headers.get("accept", "application/json")

    if "text/event-stream" in accept:
        return ResponseMode.STREAM
    return ResponseMode.BATCH

@app.get("/data")
async def get_data(mode: ResponseMode = Depends(get_response_mode)):
    if mode == ResponseMode.STREAM:
        return StreamingResponse(stream_generator())
    return {"data": await fetch_all_data()}
```

**When to use**: RESTful APIs following HTTP content negotiation standards.

## Pattern 3: Hybrid Detection

Combines explicit parameters with header detection, explicit taking precedence.

```python
from typing import Literal

def negotiate_mode(
    request: Request,
    format: Literal["stream", "batch", "auto"] = Query(default="auto")
) -> ResponseMode:
    """Negotiate response mode with explicit override."""
    if format == "stream":
        return ResponseMode.STREAM
    if format == "batch":
        return ResponseMode.BATCH

    # Auto-detect from headers
    accept = request.headers.get("accept", "")
    if "text/event-stream" in accept:
        return ResponseMode.STREAM
    return ResponseMode.BATCH

@app.get("/messages")
async def get_messages(mode: ResponseMode = Depends(negotiate_mode)):
    # Handler uses detected mode
    pass
```

**When to use**: APIs needing both automatic and explicit mode control.

## Pattern 4: LLM Chat Completion

OpenAI-compatible streaming pattern for LLM responses.

```python
from pydantic import BaseModel
from uuid import uuid4
from typing import AsyncGenerator
import time

class ChatMessage(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    messages: list[ChatMessage]
    stream: bool = False

class ChatCompletionChunk(BaseModel):
    id: str
    object: str = "chat.completion.chunk"
    created: int
    choices: list[dict]

async def generate_completion(
    messages: list[ChatMessage]
) -> AsyncGenerator[str, None]:
    """Simulate LLM token generation."""
    response_text = "This is a simulated LLM response with multiple tokens."
    words = response_text.split()

    completion_id = f"chatcmpl-{uuid4().hex[:8]}"
    created = int(time.time())

    for i, word in enumerate(words):
        chunk = ChatCompletionChunk(
            id=completion_id,
            created=created,
            choices=[{
                "index": 0,
                "delta": {"content": word + " "},
                "finish_reason": None
            }]
        )
        yield f"data: {chunk.model_dump_json()}\n\n"
        await asyncio.sleep(0.05)

    # Final chunk with finish_reason
    final_chunk = ChatCompletionChunk(
        id=completion_id,
        created=created,
        choices=[{
            "index": 0,
            "delta": {},
            "finish_reason": "stop"
        }]
    )
    yield f"data: {final_chunk.model_dump_json()}\n\n"
    yield "data: [DONE]\n\n"

@app.post("/v1/chat/completions")
async def chat_completions(request: ChatRequest):
    if request.stream:
        return StreamingResponse(
            generate_completion(request.messages),
            media_type="text/event-stream"
        )

    # Batch mode - collect full response
    full_response = ""
    async for chunk_str in generate_completion(request.messages):
        if chunk_str.startswith("data: ") and not chunk_str.strip().endswith("[DONE]"):
            chunk_data = json.loads(chunk_str[6:])
            content = chunk_data.get("choices", [{}])[0].get("delta", {}).get("content", "")
            full_response += content

    return {
        "id": f"chatcmpl-{uuid4().hex[:8]}",
        "object": "chat.completion",
        "created": int(time.time()),
        "choices": [{
            "index": 0,
            "message": {"role": "assistant", "content": full_response.strip()},
            "finish_reason": "stop"
        }]
    }
```

**When to use**: Building LLM APIs or wrappers around language models.

## Pattern 5: Progress Streaming

Stream progress updates for long-running operations.

```python
from enum import Enum
import uuid

class TaskStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"

class ProgressEvent(BaseModel):
    task_id: str
    status: TaskStatus
    progress: float  # 0.0 to 1.0
    message: str
    result: dict | None = None

async def process_with_progress(
    task_id: str,
    steps: int = 10
) -> AsyncGenerator[ProgressEvent, None]:
    """Execute task with progress updates."""
    yield ProgressEvent(
        task_id=task_id,
        status=TaskStatus.RUNNING,
        progress=0.0,
        message="Starting task..."
    )

    for i in range(steps):
        await asyncio.sleep(0.5)  # Simulate work
        progress = (i + 1) / steps
        yield ProgressEvent(
            task_id=task_id,
            status=TaskStatus.RUNNING,
            progress=progress,
            message=f"Processing step {i + 1}/{steps}"
        )

    yield ProgressEvent(
        task_id=task_id,
        status=TaskStatus.COMPLETED,
        progress=1.0,
        message="Task completed successfully",
        result={"items_processed": steps}
    )

@app.post("/tasks")
async def create_task(stream: bool = Query(default=True)):
    task_id = str(uuid.uuid4())

    if stream:
        async def progress_stream():
            async for event in process_with_progress(task_id):
                yield f"data: {event.model_dump_json()}\n\n"
        return StreamingResponse(
            progress_stream(),
            media_type="text/event-stream"
        )

    # Batch mode - wait for completion
    final_event = None
    async for event in process_with_progress(task_id):
        final_event = event
    return final_event.model_dump()
```

**When to use**: Long-running tasks where users need progress feedback.

## Pattern 6: Resilient Streaming with Reconnection

Support client reconnection using SSE event IDs.

```python
from fastapi import Header

# Store for last event ID per stream
stream_positions: dict[str, int] = {}

async def resumable_stream(
    stream_id: str,
    last_event_id: int = 0
) -> AsyncGenerator[str, None]:
    """Stream that supports reconnection."""
    items = await get_items_after(stream_id, last_event_id)

    for item in items:
        event_id = item["sequence"]
        yield f"id: {event_id}\ndata: {json.dumps(item)}\n\n"
        stream_positions[stream_id] = event_id

@app.get("/stream/{stream_id}")
async def get_stream(
    stream_id: str,
    last_event_id: str | None = Header(default=None, alias="Last-Event-ID")
):
    start_id = int(last_event_id) if last_event_id else 0

    return StreamingResponse(
        resumable_stream(stream_id, start_id),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no"  # Disable nginx buffering
        }
    )
```

**When to use**: Critical streams where data loss is unacceptable.

## Pattern 7: Typed Event Streams

Multiple event types in a single stream.

```python
from typing import Union
from pydantic import BaseModel

class MessageEvent(BaseModel):
    type: str = "message"
    content: str
    sender: str

class PresenceEvent(BaseModel):
    type: str = "presence"
    user: str
    status: str  # "online" | "offline"

class TypingEvent(BaseModel):
    type: str = "typing"
    user: str
    is_typing: bool

Event = Union[MessageEvent, PresenceEvent, TypingEvent]

async def chat_events(room_id: str) -> AsyncGenerator[str, None]:
    """Stream multiple event types."""
    async for event in event_bus.subscribe(room_id):
        # Use event.type as SSE event name
        yield f"event: {event.type}\ndata: {event.model_dump_json()}\n\n"

@app.get("/rooms/{room_id}/events")
async def room_events(room_id: str):
    return StreamingResponse(
        chat_events(room_id),
        media_type="text/event-stream"
    )
```

Client handling:
```javascript
const es = new EventSource('/rooms/123/events');

es.addEventListener('message', (e) => {
    const msg = JSON.parse(e.data);
    displayMessage(msg);
});

es.addEventListener('presence', (e) => {
    const presence = JSON.parse(e.data);
    updateUserStatus(presence);
});

es.addEventListener('typing', (e) => {
    const typing = JSON.parse(e.data);
    showTypingIndicator(typing);
});
```

**When to use**: Real-time applications with multiple event types.

## Pattern 8: Backpressure with Semaphore

Control concurrent chunk generation.

```python
from asyncio import Semaphore

async def controlled_stream(
    source: AsyncGenerator[dict, None],
    max_concurrent: int = 5
) -> AsyncGenerator[str, None]:
    """Stream with controlled concurrency."""
    semaphore = Semaphore(max_concurrent)

    async def process_with_limit(item: dict) -> str:
        async with semaphore:
            processed = await expensive_processing(item)
            return f"data: {json.dumps(processed)}\n\n"

    async for item in source:
        yield await process_with_limit(item)
```

**When to use**: When processing is expensive and needs rate limiting.

## Anti-Patterns to Avoid

### Anti-Pattern 1: Blocking in Async Generator
```python
# BAD - blocks event loop
async def bad_generator():
    for item in items:
        time.sleep(1)  # Blocks!
        yield item

# GOOD - async sleep
async def good_generator():
    for item in items:
        await asyncio.sleep(1)
        yield item
```

### Anti-Pattern 2: Missing Error Handling
```python
# BAD - errors crash stream silently
async def fragile_stream():
    async for item in source:
        yield process(item)  # What if this fails?

# GOOD - handle errors gracefully
async def robust_stream():
    try:
        async for item in source:
            try:
                yield f"data: {process(item)}\n\n"
            except ProcessingError as e:
                yield f"event: error\ndata: {json.dumps({'error': str(e)})}\n\n"
    except Exception as e:
        yield f"event: fatal\ndata: {json.dumps({'error': str(e)})}\n\n"
```

### Anti-Pattern 3: Ignoring Client Disconnection
```python
# BAD - continues processing after disconnect
async def wasteful_stream():
    async for item in expensive_source():
        yield item  # Client might be gone

# GOOD - check for disconnection
async def efficient_stream(request: Request):
    async for item in expensive_source():
        if await request.is_disconnected():
            break
        yield item
```
