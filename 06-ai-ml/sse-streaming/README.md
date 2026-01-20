# Server-Sent Events (SSE) Streaming

Master Server-Sent Events for streaming LLM responses to clients. Learn the SSE protocol, build FastAPI endpoints, and implement client-side consumption for real-time AI interactions.

## Learning Objectives

After completing this skill, you will be able to:
- Understand the SSE protocol and message format
- Build SSE endpoints with FastAPI
- Stream LLM responses in real-time
- Handle reconnection and error recovery
- Implement client-side SSE consumption
- Debug and test SSE streams

## Prerequisites

- Python 3.11+
- UV package manager
- [FastAPI Basics](../../01-language-frameworks/python/fastapi-basics/) recommended
- [OpenAI Responses API](../openai-responses-api/) recommended

## Quick Start

```bash
# Install dependencies
make setup

# Run the SSE server
make run-server

# In another terminal, test the stream
make test-client

# Run tests
make test
```

## Concepts

### What is SSE?

Server-Sent Events is a standard for servers to push data to clients over HTTP. Unlike WebSockets, SSE is unidirectional (server to client only) and uses regular HTTP connections.

**Key characteristics:**
- Uses text/event-stream content type
- Built-in reconnection support
- Works through proxies and load balancers
- Perfect for streaming LLM tokens

### SSE Message Format

```
event: message
data: {"content": "Hello"}

event: message
data: {"content": " world"}

event: done
data: [DONE]
```

- Lines starting with `data:` contain the payload
- Lines starting with `event:` define the event type
- Double newline (`\n\n`) separates messages
- Lines starting with `:` are comments (used for keep-alive)

### SSE with FastAPI

```python
from fastapi import FastAPI
from fastapi.responses import StreamingResponse

app = FastAPI()

async def event_generator():
    for i in range(5):
        yield f"data: Token {i}\n\n"
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

### Streaming LLM Responses

```python
from openai import OpenAI

async def stream_llm_response(prompt: str):
    client = OpenAI()

    stream = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        stream=True
    )

    for chunk in stream:
        if chunk.choices[0].delta.content:
            content = chunk.choices[0].delta.content
            yield f"data: {json.dumps({'content': content})}\n\n"

    yield "data: [DONE]\n\n"
```

### Client-Side Consumption

**JavaScript (Browser):**
```javascript
const eventSource = new EventSource('/stream?prompt=Hello');

eventSource.onmessage = (event) => {
    if (event.data === '[DONE]') {
        eventSource.close();
        return;
    }
    const data = JSON.parse(event.data);
    console.log(data.content);
};

eventSource.onerror = (error) => {
    console.error('SSE error:', error);
    eventSource.close();
};
```

**Python (httpx):**
```python
import httpx

with httpx.stream("GET", "http://localhost:8000/stream") as response:
    for line in response.iter_lines():
        if line.startswith("data: "):
            data = line[6:]  # Remove "data: " prefix
            if data != "[DONE]":
                print(json.loads(data)["content"], end="")
```

## Examples

### Example 1: Basic SSE Endpoint

Create a simple SSE endpoint that streams numbered messages.

```bash
make example-1
```

### Example 2: LLM Streaming

Stream responses from OpenAI through an SSE endpoint.

```bash
make example-2
```

### Example 3: Client Consumption

Demonstrate Python client consuming SSE streams.

```bash
make example-3
```

### Example 4: Production Patterns

Error handling, reconnection, and keep-alive patterns.

```bash
make example-4
```

## Exercises

See the [exercises](./exercises/) directory for practice problems:

1. **Exercise 1**: Build a Chat Endpoint - Create an SSE endpoint for a chat interface
2. **Exercise 2**: Progress Streaming - Stream progress updates for a long-running task
3. **Exercise 3**: Multi-Source Stream - Aggregate multiple LLM streams into one

Solutions are available in [exercises/solutions/](./exercises/solutions/).

## SSE vs WebSockets

| Feature | SSE | WebSockets |
|---------|-----|------------|
| Direction | Server -> Client | Bidirectional |
| Protocol | HTTP | WS/WSS |
| Reconnection | Built-in | Manual |
| Browser Support | All modern | All modern |
| Proxy Support | Excellent | May need config |
| Use Case | Streaming updates | Real-time chat |

**Use SSE when:**
- You only need server-to-client updates
- Streaming LLM responses
- Simple notification systems
- Progress updates

**Use WebSockets when:**
- Bidirectional communication needed
- Low-latency gaming
- Real-time collaboration

## Common Mistakes

### Not Setting Correct Headers

Always include proper headers:

```python
return StreamingResponse(
    generator(),
    media_type="text/event-stream",
    headers={
        "Cache-Control": "no-cache",
        "Connection": "keep-alive",
        "X-Accel-Buffering": "no",  # For nginx
    }
)
```

### Missing Double Newline

SSE messages must end with `\n\n`:

```python
# Wrong
yield f"data: {content}\n"

# Correct
yield f"data: {content}\n\n"
```

### Not Handling Client Disconnection

Check if client is still connected:

```python
from fastapi import Request

async def stream(request: Request):
    async def generator():
        while True:
            if await request.is_disconnected():
                break
            yield f"data: update\n\n"
            await asyncio.sleep(1)

    return StreamingResponse(generator(), media_type="text/event-stream")
```

### Buffering Issues

Ensure responses are not buffered:

```python
# Disable buffering in response
headers = {
    "X-Accel-Buffering": "no",  # Nginx
    "Cache-Control": "no-cache, no-transform",
}
```

## Further Reading

- [MDN: Server-Sent Events](https://developer.mozilla.org/en-US/docs/Web/API/Server-sent_events)
- [HTML Living Standard: SSE](https://html.spec.whatwg.org/multipage/server-sent-events.html)
- [FastAPI StreamingResponse](https://fastapi.tiangolo.com/advanced/custom-response/#streamingresponse)
- Related skills in this repository:
  - [OpenAI Responses API](../openai-responses-api/) - LLM streaming source
  - [FastAPI Basics](../../01-language-frameworks/python/fastapi-basics/) - Web framework
  - [LangChain/LangGraph](../../01-language-frameworks/python/langchain-langgraph/) - LLM orchestration
