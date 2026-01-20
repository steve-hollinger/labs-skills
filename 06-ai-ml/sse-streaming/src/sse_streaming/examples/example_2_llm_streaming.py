"""
Example 2: LLM Streaming

This example demonstrates streaming LLM responses through SSE:
- OpenAI streaming integration
- Token-by-token delivery
- Error handling
- Mock fallback for testing

Key concepts:
- Stream tokens as they're generated
- JSON format for client parsing
- Graceful error handling
"""

import os
import json
import asyncio
from dotenv import load_dotenv
from fastapi import FastAPI, Query, Request
from fastapi.responses import StreamingResponse
import uvicorn

load_dotenv()

app = FastAPI(title="LLM Streaming Example")


# ============================================================================
# LLM Streaming Generators
# ============================================================================

async def stream_openai_response(prompt: str, model: str = "gpt-4o-mini"):
    """
    Stream response from OpenAI API.

    Args:
        prompt: User prompt
        model: OpenAI model to use

    Yields:
        SSE formatted messages with content chunks
    """
    if not os.getenv("OPENAI_API_KEY"):
        # Mock streaming for demonstration
        async for chunk in mock_llm_stream(prompt):
            yield chunk
        return

    from openai import OpenAI

    client = OpenAI()

    try:
        stream = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ],
            stream=True,
            max_tokens=500
        )

        for chunk in stream:
            if chunk.choices[0].delta.content:
                content = chunk.choices[0].delta.content
                data = json.dumps({"content": content, "type": "content"})
                yield f"data: {data}\n\n"

        # Send completion marker
        yield f"data: {json.dumps({'type': 'done'})}\n\n"
        yield "data: [DONE]\n\n"

    except Exception as e:
        error_data = json.dumps({"type": "error", "error": str(e)})
        yield f"event: error\ndata: {error_data}\n\n"


async def mock_llm_stream(prompt: str):
    """
    Mock LLM streaming for testing without API key.

    Simulates token-by-token generation.
    """
    response = f"This is a mock response to your prompt: '{prompt}'. "
    response += "In a production environment, this would be streaming "
    response += "from a real language model like GPT-4. "
    response += "Each word is sent as a separate token to simulate "
    response += "the actual streaming behavior you would see."

    words = response.split()

    for i, word in enumerate(words):
        data = json.dumps({
            "content": word + " ",
            "type": "content",
            "token_index": i
        })
        yield f"data: {data}\n\n"
        await asyncio.sleep(0.05)  # Simulate token generation time

    # Send completion
    yield f"data: {json.dumps({'type': 'done', 'total_tokens': len(words)})}\n\n"
    yield "data: [DONE]\n\n"


async def stream_with_metadata(prompt: str):
    """
    Stream response with additional metadata events.

    Shows how to send different event types during streaming.
    """
    # Send start event with metadata
    start_data = {
        "type": "start",
        "model": "gpt-4o-mini" if os.getenv("OPENAI_API_KEY") else "mock",
        "prompt_length": len(prompt)
    }
    yield f"event: metadata\ndata: {json.dumps(start_data)}\n\n"

    # Stream the actual content
    token_count = 0
    async for chunk in (
        stream_openai_response(prompt) if os.getenv("OPENAI_API_KEY")
        else mock_llm_stream(prompt)
    ):
        if "content" in chunk or chunk.startswith("data:"):
            yield chunk
            token_count += 1

            # Send periodic progress updates
            if token_count % 10 == 0:
                progress = {"type": "progress", "tokens_so_far": token_count}
                yield f"event: metadata\ndata: {json.dumps(progress)}\n\n"

    # Send final metadata
    end_data = {
        "type": "complete",
        "total_tokens": token_count
    }
    yield f"event: metadata\ndata: {json.dumps(end_data)}\n\n"


# ============================================================================
# Endpoints
# ============================================================================

@app.get("/chat")
async def chat_stream(
    prompt: str = Query(..., description="User prompt"),
    model: str = Query("gpt-4o-mini", description="Model to use")
):
    """Stream LLM response."""
    return StreamingResponse(
        stream_openai_response(prompt, model),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        }
    )


@app.get("/chat/metadata")
async def chat_with_metadata(
    prompt: str = Query(..., description="User prompt")
):
    """Stream LLM response with metadata events."""
    return StreamingResponse(
        stream_with_metadata(prompt),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        }
    )


@app.get("/chat/disconnection")
async def chat_with_disconnection_handling(
    prompt: str = Query(..., description="User prompt"),
    request: Request = None
):
    """Stream with client disconnection handling."""

    async def stream_with_disconnect_check():
        async for chunk in stream_openai_response(prompt):
            # Check if client is still connected
            if request and await request.is_disconnected():
                print("Client disconnected, stopping stream")
                break
            yield chunk

    return StreamingResponse(
        stream_with_disconnect_check(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        }
    )


@app.get("/")
async def info():
    """API info."""
    has_api_key = bool(os.getenv("OPENAI_API_KEY"))
    return {
        "example": "LLM Streaming",
        "openai_configured": has_api_key,
        "mode": "real" if has_api_key else "mock",
        "endpoints": {
            "/chat": "Basic LLM streaming",
            "/chat/metadata": "Streaming with metadata events",
            "/chat/disconnection": "Streaming with disconnect handling"
        }
    }


# ============================================================================
# Main
# ============================================================================

def main():
    """Run the LLM streaming example."""
    print("=" * 60)
    print("Example 2: LLM Streaming")
    print("=" * 60)

    has_key = bool(os.getenv("OPENAI_API_KEY"))
    print(f"\nOpenAI API Key: {'Configured' if has_key else 'Not set (using mock)'}")

    if not has_key:
        print("\nTo use real OpenAI streaming:")
        print("  export OPENAI_API_KEY=your-key-here")

    print("\n--- Key Concepts ---")
    print("1. Stream tokens as they're generated for responsive UX")
    print("2. Use JSON format for structured data")
    print("3. Send metadata events for progress tracking")
    print("4. Handle client disconnection gracefully")
    print("5. Always end with [DONE] marker")

    print("\n" + "=" * 60)
    print("Starting server on http://localhost:8002")
    print("=" * 60)
    print("\nTest:")
    print('  curl -N "http://localhost:8002/chat?prompt=Tell+me+a+joke"')
    print("\nPress Ctrl+C to stop")

    uvicorn.run(app, host="0.0.0.0", port=8002, log_level="info")


if __name__ == "__main__":
    main()
