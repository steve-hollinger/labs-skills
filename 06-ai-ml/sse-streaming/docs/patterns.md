# Common Patterns

This document covers practical patterns for SSE streaming in production applications.

## Server Patterns

### 1. Basic SSE Generator

```python
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
import asyncio
import json

app = FastAPI()

async def simple_generator():
    """Generate simple SSE messages."""
    for i in range(10):
        data = json.dumps({"count": i, "message": f"Update {i}"})
        yield f"data: {data}\n\n"
        await asyncio.sleep(0.5)
    yield "data: [DONE]\n\n"

@app.get("/stream")
async def stream():
    return StreamingResponse(
        simple_generator(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache"}
    )
```

### 2. LLM Streaming Endpoint

```python
import os
from fastapi import FastAPI, Query, HTTPException
from fastapi.responses import StreamingResponse
import json

app = FastAPI()

async def stream_llm_response(prompt: str):
    """Stream LLM response as SSE."""
    if not os.getenv("OPENAI_API_KEY"):
        # Mock streaming for demo
        words = f"This is a mock response to: {prompt}".split()
        for word in words:
            yield f"data: {json.dumps({'content': word + ' '})}\n\n"
            await asyncio.sleep(0.1)
        yield "data: [DONE]\n\n"
        return

    from openai import OpenAI
    client = OpenAI()

    try:
        stream = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ],
            stream=True
        )

        for chunk in stream:
            if chunk.choices[0].delta.content:
                content = chunk.choices[0].delta.content
                yield f"data: {json.dumps({'content': content})}\n\n"

        yield "data: [DONE]\n\n"

    except Exception as e:
        yield f"event: error\ndata: {json.dumps({'error': str(e)})}\n\n"

@app.get("/chat")
async def chat(prompt: str = Query(...)):
    return StreamingResponse(
        stream_llm_response(prompt),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        }
    )
```

### 3. Progress Streaming

```python
from fastapi import FastAPI, BackgroundTasks
from fastapi.responses import StreamingResponse
import asyncio
import json
import uuid

app = FastAPI()

# Store for tracking jobs
job_status = {}

async def long_running_task(job_id: str):
    """Simulate a long-running task with progress updates."""
    for i in range(101):
        job_status[job_id] = {
            "status": "running",
            "progress": i,
            "message": f"Processing step {i}/100"
        }
        await asyncio.sleep(0.1)

    job_status[job_id] = {
        "status": "completed",
        "progress": 100,
        "message": "Task completed successfully"
    }

async def progress_generator(job_id: str):
    """Stream progress updates for a job."""
    last_progress = -1

    while True:
        if job_id not in job_status:
            yield f"event: error\ndata: {json.dumps({'error': 'Job not found'})}\n\n"
            break

        status = job_status[job_id]

        if status["progress"] != last_progress:
            yield f"data: {json.dumps(status)}\n\n"
            last_progress = status["progress"]

        if status["status"] == "completed":
            yield "data: [DONE]\n\n"
            break

        await asyncio.sleep(0.1)

@app.post("/jobs")
async def create_job(background_tasks: BackgroundTasks):
    """Start a new job and return its ID."""
    job_id = str(uuid.uuid4())
    job_status[job_id] = {"status": "pending", "progress": 0}
    background_tasks.add_task(long_running_task, job_id)
    return {"job_id": job_id}

@app.get("/jobs/{job_id}/progress")
async def job_progress(job_id: str):
    """Stream progress updates for a job."""
    return StreamingResponse(
        progress_generator(job_id),
        media_type="text/event-stream"
    )
```

### 4. Multi-Source Aggregation

```python
import asyncio
from typing import AsyncGenerator

async def source_a() -> AsyncGenerator[dict, None]:
    """Data source A."""
    for i in range(5):
        yield {"source": "A", "value": i}
        await asyncio.sleep(0.3)

async def source_b() -> AsyncGenerator[dict, None]:
    """Data source B."""
    for i in range(5):
        yield {"source": "B", "value": i * 10}
        await asyncio.sleep(0.5)

async def merge_sources():
    """Merge multiple async sources."""
    import asyncio

    async def wrap_source(source, queue):
        async for item in source():
            await queue.put(item)
        await queue.put(None)  # Signal completion

    queue = asyncio.Queue()
    sources = [source_a, source_b]
    completed = 0

    # Start all sources
    tasks = [
        asyncio.create_task(wrap_source(src, queue))
        for src in sources
    ]

    while completed < len(sources):
        item = await queue.get()
        if item is None:
            completed += 1
        else:
            yield f"data: {json.dumps(item)}\n\n"

    yield "data: [DONE]\n\n"

    # Clean up tasks
    for task in tasks:
        task.cancel()
```

### 5. Heartbeat Pattern

```python
async def stream_with_heartbeat(data_source, heartbeat_interval: int = 15):
    """Stream with periodic heartbeats to keep connection alive."""
    import time

    last_event_time = time.time()

    async def heartbeat_task():
        nonlocal last_event_time
        while True:
            await asyncio.sleep(heartbeat_interval)
            if time.time() - last_event_time > heartbeat_interval:
                yield ": heartbeat\n\n"

    try:
        async for item in data_source:
            yield f"data: {json.dumps(item)}\n\n"
            last_event_time = time.time()
    finally:
        yield "data: [DONE]\n\n"
```

## Client Patterns

### 1. Python Async Client

```python
import httpx
import json
from typing import AsyncGenerator

async def consume_sse(url: str) -> AsyncGenerator[dict, None]:
    """Consume SSE stream asynchronously."""
    async with httpx.AsyncClient(timeout=None) as client:
        async with client.stream("GET", url) as response:
            async for line in response.aiter_lines():
                line = line.strip()

                if not line:
                    continue

                if line.startswith("data: "):
                    data = line[6:]
                    if data == "[DONE]":
                        break
                    try:
                        yield json.loads(data)
                    except json.JSONDecodeError:
                        yield {"raw": data}

                elif line.startswith("event: "):
                    event_type = line[7:]
                    # Handle custom events
                    pass
```

### 2. Retry with Backoff

```python
import asyncio
from typing import AsyncGenerator

async def consume_with_retry(
    url: str,
    max_retries: int = 5,
    base_delay: float = 1.0
) -> AsyncGenerator[dict, None]:
    """Consume SSE with automatic retry on failure."""
    retries = 0

    while retries < max_retries:
        try:
            async for item in consume_sse(url):
                retries = 0  # Reset on successful data
                yield item
            break  # Stream completed normally
        except (httpx.HTTPError, Exception) as e:
            retries += 1
            if retries >= max_retries:
                raise
            delay = base_delay * (2 ** (retries - 1))
            print(f"Retry {retries}/{max_retries} in {delay}s: {e}")
            await asyncio.sleep(delay)
```

### 3. Buffered Processing

```python
async def process_stream_buffered(
    url: str,
    buffer_size: int = 10,
    process_fn=None
):
    """Buffer stream items and process in batches."""
    buffer = []

    async for item in consume_sse(url):
        buffer.append(item)

        if len(buffer) >= buffer_size:
            if process_fn:
                await process_fn(buffer)
            buffer = []

    # Process remaining items
    if buffer and process_fn:
        await process_fn(buffer)
```

### 4. Stream to File

```python
async def stream_to_file(url: str, filepath: str):
    """Stream SSE data to a file."""
    with open(filepath, "w") as f:
        async for item in consume_sse(url):
            f.write(json.dumps(item) + "\n")
            f.flush()  # Ensure data is written
```

## Error Handling Patterns

### Server-Side Error Events

```python
async def robust_stream(data_source):
    """Stream with comprehensive error handling."""
    try:
        # Send connection established event
        yield f"event: connected\ndata: {json.dumps({'status': 'ok'})}\n\n"

        async for item in data_source:
            try:
                yield f"data: {json.dumps(item)}\n\n"
            except Exception as e:
                yield f"event: item_error\ndata: {json.dumps({'error': str(e)})}\n\n"

        yield "data: [DONE]\n\n"

    except asyncio.CancelledError:
        yield f"event: cancelled\ndata: {json.dumps({'reason': 'client_disconnect'})}\n\n"
        raise

    except Exception as e:
        yield f"event: error\ndata: {json.dumps({'error': str(e), 'fatal': True})}\n\n"
```

### Client-Side Error Recovery

```python
async def resilient_consume(url: str):
    """Consume with error recovery and reconnection."""
    last_id = None

    while True:
        try:
            headers = {}
            if last_id:
                headers["Last-Event-ID"] = last_id

            async for item in consume_sse(url, headers=headers):
                if "id" in item:
                    last_id = item["id"]
                yield item

            break  # Completed successfully

        except httpx.HTTPError as e:
            print(f"Connection error, reconnecting: {e}")
            await asyncio.sleep(3)
```

## Testing Patterns

### Mock SSE Server

```python
from fastapi.testclient import TestClient
import pytest

def test_sse_endpoint():
    """Test SSE endpoint."""
    from your_app import app

    with TestClient(app) as client:
        with client.stream("GET", "/stream") as response:
            lines = list(response.iter_lines())

            data_lines = [l for l in lines if l.startswith("data: ")]
            assert len(data_lines) > 0

            # Check for DONE marker
            assert any("[DONE]" in l for l in data_lines)
```

### Async Test

```python
import pytest
import httpx

@pytest.mark.asyncio
async def test_sse_async():
    """Async test for SSE endpoint."""
    from your_app import app

    async with httpx.AsyncClient(app=app, base_url="http://test") as client:
        items = []
        async with client.stream("GET", "/stream") as response:
            async for line in response.aiter_lines():
                if line.startswith("data: "):
                    data = line[6:]
                    if data != "[DONE]":
                        items.append(json.loads(data))

        assert len(items) > 0
```
