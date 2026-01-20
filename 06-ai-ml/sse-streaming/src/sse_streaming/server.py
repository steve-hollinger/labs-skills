"""
FastAPI SSE Server

A demonstration server with various SSE endpoints.
Run with: uvicorn sse_streaming.server:app --reload
"""

import os
import json
import asyncio
from datetime import datetime
from fastapi import FastAPI, Query, Request
from fastapi.responses import StreamingResponse, HTMLResponse
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(
    title="SSE Streaming Demo",
    description="Server-Sent Events streaming demonstration",
    version="1.0.0"
)


# ============================================================================
# SSE Generators
# ============================================================================

async def simple_counter(count: int = 10, delay: float = 0.5):
    """Generate counting messages."""
    for i in range(count):
        data = json.dumps({
            "count": i,
            "timestamp": datetime.now().isoformat()
        })
        yield f"data: {data}\n\n"
        await asyncio.sleep(delay)
    yield "data: [DONE]\n\n"


async def stream_llm_response(prompt: str):
    """Stream LLM response."""
    if not os.getenv("OPENAI_API_KEY"):
        # Mock streaming
        response = f"This is a mock response to your prompt: '{prompt}'. "
        response += "In a real scenario, this would be streamed from an LLM."
        words = response.split()
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


async def stream_with_events():
    """Stream with custom event types."""
    # Connection event
    yield f"event: connected\ndata: {json.dumps({'status': 'ok'})}\n\n"

    for i in range(5):
        # Progress events
        yield f"event: progress\ndata: {json.dumps({'step': i+1, 'total': 5})}\n\n"
        await asyncio.sleep(0.5)

    # Completion event
    yield f"event: complete\ndata: {json.dumps({'message': 'All done!'})}\n\n"


# ============================================================================
# Endpoints
# ============================================================================

@app.get("/")
async def root():
    """Root endpoint with API info."""
    return {
        "message": "SSE Streaming Demo Server",
        "endpoints": {
            "/stream": "Basic SSE stream",
            "/chat": "LLM chat streaming",
            "/events": "Custom event types",
            "/demo": "Interactive demo page"
        }
    }


@app.get("/stream")
async def stream(
    count: int = Query(10, ge=1, le=100, description="Number of messages"),
    delay: float = Query(0.5, ge=0.1, le=5.0, description="Delay between messages")
):
    """Basic SSE stream endpoint."""
    return StreamingResponse(
        simple_counter(count, delay),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        }
    )


@app.get("/chat")
async def chat(
    prompt: str = Query(..., description="User prompt"),
    request: Request = None
):
    """LLM chat streaming endpoint."""
    async def stream_with_disconnect():
        async for chunk in stream_llm_response(prompt):
            if request and await request.is_disconnected():
                break
            yield chunk

    return StreamingResponse(
        stream_with_disconnect(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        }
    )


@app.get("/events")
async def events():
    """Endpoint demonstrating custom event types."""
    return StreamingResponse(
        stream_with_events(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        }
    )


@app.get("/demo", response_class=HTMLResponse)
async def demo_page():
    """Interactive demo page for testing SSE."""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>SSE Demo</title>
        <style>
            body { font-family: Arial, sans-serif; max-width: 800px; margin: 50px auto; padding: 20px; }
            .output { background: #f5f5f5; padding: 20px; border-radius: 8px; white-space: pre-wrap; min-height: 200px; }
            button { padding: 10px 20px; margin: 5px; cursor: pointer; }
            input { padding: 10px; width: 300px; }
            .status { color: #666; margin: 10px 0; }
        </style>
    </head>
    <body>
        <h1>SSE Streaming Demo</h1>

        <h2>Basic Stream</h2>
        <button onclick="testBasic()">Start Basic Stream</button>
        <button onclick="stopStream()">Stop</button>
        <div class="status" id="basic-status">Status: Idle</div>
        <div class="output" id="basic-output"></div>

        <h2>Chat Stream</h2>
        <input type="text" id="prompt" placeholder="Enter your prompt..." value="Tell me a short joke">
        <button onclick="testChat()">Send</button>
        <div class="status" id="chat-status">Status: Idle</div>
        <div class="output" id="chat-output"></div>

        <script>
            let eventSource = null;

            function stopStream() {
                if (eventSource) {
                    eventSource.close();
                    eventSource = null;
                }
            }

            function testBasic() {
                stopStream();
                const output = document.getElementById('basic-output');
                const status = document.getElementById('basic-status');
                output.textContent = '';
                status.textContent = 'Status: Connecting...';

                eventSource = new EventSource('/stream?count=10&delay=0.3');

                eventSource.onopen = () => {
                    status.textContent = 'Status: Connected';
                };

                eventSource.onmessage = (event) => {
                    if (event.data === '[DONE]') {
                        status.textContent = 'Status: Complete';
                        eventSource.close();
                        return;
                    }
                    const data = JSON.parse(event.data);
                    output.textContent += `Count: ${data.count}, Time: ${data.timestamp}\\n`;
                };

                eventSource.onerror = () => {
                    status.textContent = 'Status: Error/Closed';
                };
            }

            function testChat() {
                stopStream();
                const prompt = document.getElementById('prompt').value;
                const output = document.getElementById('chat-output');
                const status = document.getElementById('chat-status');
                output.textContent = '';
                status.textContent = 'Status: Connecting...';

                eventSource = new EventSource('/chat?prompt=' + encodeURIComponent(prompt));

                eventSource.onopen = () => {
                    status.textContent = 'Status: Streaming...';
                };

                eventSource.onmessage = (event) => {
                    if (event.data === '[DONE]') {
                        status.textContent = 'Status: Complete';
                        eventSource.close();
                        return;
                    }
                    const data = JSON.parse(event.data);
                    output.textContent += data.content;
                };

                eventSource.addEventListener('error', (event) => {
                    if (event.data) {
                        const data = JSON.parse(event.data);
                        output.textContent += '\\n[Error: ' + data.error + ']';
                    }
                });

                eventSource.onerror = () => {
                    if (eventSource.readyState === EventSource.CLOSED) {
                        status.textContent = 'Status: Connection closed';
                    }
                };
            }
        </script>
    </body>
    </html>
    """


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
