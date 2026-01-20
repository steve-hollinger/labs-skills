# Core Concepts

This document explains the fundamental concepts of Server-Sent Events (SSE) streaming.

## 1. What is SSE?

Server-Sent Events is a W3C standard that enables servers to push data to clients over a persistent HTTP connection. It's a unidirectional protocol (server to client only) built on top of regular HTTP.

### Key Characteristics

- **HTTP-based**: Uses standard HTTP, works through proxies
- **Unidirectional**: Server pushes to client only
- **Auto-reconnection**: Clients automatically reconnect on disconnect
- **Text-based**: Sends text data (typically JSON)
- **Event types**: Support for custom event types
- **Last-Event-ID**: Enables resumption after disconnection

### When to Use SSE

- Streaming LLM responses token by token
- Real-time notifications and updates
- Progress updates for long-running operations
- Live data feeds (stocks, sports scores)
- Server-initiated updates

## 2. SSE Message Format

### Basic Structure

```
data: Hello, world!\n
\n
```

A complete SSE message consists of:
1. One or more lines starting with a field name followed by `:`
2. The data after the colon
3. A blank line (double newline `\n\n`) to end the message

### Field Types

```
event: custom_event\n
data: {"message": "Hello"}\n
id: 12345\n
retry: 5000\n
\n
```

| Field | Purpose |
|-------|---------|
| `data:` | The message payload (required) |
| `event:` | Event type name (optional, default is "message") |
| `id:` | Event ID for reconnection (optional) |
| `retry:` | Reconnection timeout in milliseconds (optional) |
| `:` | Comment (ignored by client, used for keep-alive) |

### Multi-line Data

```
data: Line 1\n
data: Line 2\n
data: Line 3\n
\n
```

Multiple `data:` lines are concatenated with newlines.

### Event Types

```
event: notification\n
data: {"type": "alert", "message": "New update"}\n
\n

event: progress\n
data: {"percent": 50}\n
\n
```

Clients can listen for specific event types:

```javascript
eventSource.addEventListener('notification', (e) => {
    console.log('Notification:', JSON.parse(e.data));
});
```

## 3. SSE Protocol Flow

### Connection Establishment

```
Client                                Server
   |                                     |
   |  GET /stream HTTP/1.1               |
   |  Accept: text/event-stream          |
   |------------------------------------>|
   |                                     |
   |  HTTP/1.1 200 OK                    |
   |  Content-Type: text/event-stream    |
   |  Cache-Control: no-cache            |
   |<------------------------------------|
   |                                     |
   |  data: Hello\n\n                    |
   |<------------------------------------|
   |                                     |
   |  data: World\n\n                    |
   |<------------------------------------|
   |                                     |
```

### Reconnection

```
Client                                Server
   |                                     |
   |  (Connection lost)                  |
   |  - - - - - - - X - - - - - - - - - |
   |                                     |
   |  (Wait retry ms)                    |
   |                                     |
   |  GET /stream HTTP/1.1               |
   |  Last-Event-ID: 12345               |
   |------------------------------------>|
   |                                     |
   |  (Server resumes from ID 12345)     |
   |<------------------------------------|
```

## 4. FastAPI SSE Implementation

### Basic Endpoint

```python
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
import asyncio

app = FastAPI()

async def event_generator():
    """Generate SSE events."""
    for i in range(10):
        yield f"data: Message {i}\n\n"
        await asyncio.sleep(0.5)
    yield "data: [DONE]\n\n"

@app.get("/stream")
async def stream():
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        }
    )
```

### Required Headers

```python
headers = {
    "Content-Type": "text/event-stream",
    "Cache-Control": "no-cache",
    "Connection": "keep-alive",
    "X-Accel-Buffering": "no",  # Disable nginx buffering
}
```

### Handling Client Disconnection

```python
from fastapi import Request

@app.get("/stream")
async def stream_with_disconnect(request: Request):
    async def generator():
        try:
            while True:
                if await request.is_disconnected():
                    print("Client disconnected")
                    break

                yield f"data: {time.time()}\n\n"
                await asyncio.sleep(1)
        except asyncio.CancelledError:
            print("Stream cancelled")

    return StreamingResponse(
        generator(),
        media_type="text/event-stream"
    )
```

## 5. Client-Side Consumption

### Browser (EventSource API)

```javascript
const eventSource = new EventSource('/stream');

// Handle default message events
eventSource.onmessage = (event) => {
    console.log('Message:', event.data);
};

// Handle custom events
eventSource.addEventListener('progress', (event) => {
    const data = JSON.parse(event.data);
    console.log('Progress:', data.percent);
});

// Handle connection open
eventSource.onopen = () => {
    console.log('Connected');
};

// Handle errors
eventSource.onerror = (error) => {
    console.error('SSE Error:', error);
    if (eventSource.readyState === EventSource.CLOSED) {
        console.log('Connection closed');
    }
};

// Close connection
eventSource.close();
```

### Python (httpx)

```python
import httpx
import json

def consume_sse_sync(url: str):
    """Synchronous SSE consumption."""
    with httpx.stream("GET", url) as response:
        for line in response.iter_lines():
            if line.startswith("data: "):
                data = line[6:]  # Remove "data: " prefix
                if data == "[DONE]":
                    break
                yield json.loads(data)

async def consume_sse_async(url: str):
    """Asynchronous SSE consumption."""
    async with httpx.AsyncClient() as client:
        async with client.stream("GET", url) as response:
            async for line in response.aiter_lines():
                if line.startswith("data: "):
                    data = line[6:]
                    if data == "[DONE]":
                        break
                    yield json.loads(data)
```

## 6. LLM Streaming Integration

### OpenAI Streaming

```python
from openai import OpenAI
import json

async def stream_openai_response(prompt: str):
    """Stream OpenAI response as SSE."""
    client = OpenAI()

    stream = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        stream=True
    )

    for chunk in stream:
        if chunk.choices[0].delta.content:
            content = chunk.choices[0].delta.content
            # Escape content for JSON
            data = json.dumps({"content": content})
            yield f"data: {data}\n\n"

    yield "data: [DONE]\n\n"
```

### FastAPI LLM Endpoint

```python
from fastapi import FastAPI, Query
from fastapi.responses import StreamingResponse

@app.get("/chat")
async def chat_stream(
    prompt: str = Query(..., description="User prompt")
):
    return StreamingResponse(
        stream_openai_response(prompt),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        }
    )
```

## 7. Error Handling

### Server-Side Errors

```python
async def stream_with_error_handling():
    try:
        async for chunk in data_source():
            yield f"data: {json.dumps(chunk)}\n\n"
    except Exception as e:
        error_data = json.dumps({
            "error": True,
            "message": str(e)
        })
        yield f"event: error\ndata: {error_data}\n\n"
    finally:
        yield "data: [DONE]\n\n"
```

### Client-Side Error Handling

```javascript
eventSource.addEventListener('error', (event) => {
    const data = JSON.parse(event.data);
    console.error('Server error:', data.message);
    showErrorToUser(data.message);
});
```

## 8. Keep-Alive and Timeouts

### Server Keep-Alive

```python
import asyncio

async def stream_with_keepalive():
    last_data_time = time.time()

    async for item in slow_data_source():
        yield f"data: {json.dumps(item)}\n\n"
        last_data_time = time.time()

        # Send keep-alive if no data for 15 seconds
        if time.time() - last_data_time > 15:
            yield ": keepalive\n\n"
```

### Timeout Configuration

```
retry: 3000\n
data: Connection established\n
\n
```

The `retry:` field tells the client how long to wait before reconnecting (in milliseconds).
