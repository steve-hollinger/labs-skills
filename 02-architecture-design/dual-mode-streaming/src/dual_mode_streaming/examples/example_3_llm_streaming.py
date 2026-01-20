"""Example 3: LLM-Style Token Streaming.

This example demonstrates token-by-token streaming similar to ChatGPT/Claude APIs,
implementing the OpenAI-compatible chat completion format.

Run with: make example-3
Or: uv run python -m dual_mode_streaming.examples.example_3_llm_streaming
"""

import asyncio
import json
import time
from typing import AsyncGenerator
from uuid import uuid4

from fastapi import FastAPI
from fastapi.responses import JSONResponse, StreamingResponse
from pydantic import BaseModel

app = FastAPI(title="LLM Streaming Example")


# Request/Response models matching OpenAI format
class ChatMessage(BaseModel):
    """A single message in the conversation."""

    role: str  # "system", "user", or "assistant"
    content: str


class ChatRequest(BaseModel):
    """Chat completion request."""

    messages: list[ChatMessage]
    stream: bool = False
    max_tokens: int = 100


class ChatCompletionChunk(BaseModel):
    """Streaming chunk response."""

    id: str
    object: str = "chat.completion.chunk"
    created: int
    model: str = "demo-model"
    choices: list[dict]


class ChatCompletion(BaseModel):
    """Complete (non-streaming) response."""

    id: str
    object: str = "chat.completion"
    created: int
    model: str = "demo-model"
    choices: list[dict]
    usage: dict


# Simulated LLM responses
DEMO_RESPONSES = {
    "default": "I'm a demo AI assistant. I can help you understand how LLM streaming "
    "works by simulating token-by-token response generation. Each word you see "
    "is delivered as a separate streaming chunk, just like real LLM APIs!",
    "hello": "Hello! It's great to meet you. I'm here to demonstrate streaming "
    "responses. How can I help you today?",
    "explain": "Streaming in LLM APIs works by sending response tokens as they are "
    "generated, rather than waiting for the complete response. This provides "
    "a better user experience as users see the response forming in real-time.",
}


def get_response_text(messages: list[ChatMessage]) -> str:
    """Select appropriate demo response based on user message.

    Args:
        messages: The conversation messages.

    Returns:
        Demo response text.
    """
    if not messages:
        return DEMO_RESPONSES["default"]

    last_user_msg = ""
    for msg in reversed(messages):
        if msg.role == "user":
            last_user_msg = msg.content.lower()
            break

    if "hello" in last_user_msg or "hi" in last_user_msg:
        return DEMO_RESPONSES["hello"]
    if "explain" in last_user_msg or "how" in last_user_msg:
        return DEMO_RESPONSES["explain"]

    return DEMO_RESPONSES["default"]


async def stream_tokens(
    messages: list[ChatMessage],
    completion_id: str,
) -> AsyncGenerator[str, None]:
    """Stream response tokens in OpenAI-compatible format.

    Args:
        messages: Input conversation messages.
        completion_id: Unique ID for this completion.

    Yields:
        SSE-formatted chat completion chunks.
    """
    response_text = get_response_text(messages)
    words = response_text.split()
    created = int(time.time())

    # Stream each word as a token
    for i, word in enumerate(words):
        # Add space after word (except potentially last)
        token = word + " "

        chunk = ChatCompletionChunk(
            id=completion_id,
            created=created,
            choices=[
                {
                    "index": 0,
                    "delta": {"content": token},
                    "finish_reason": None,
                }
            ],
        )
        yield f"data: {chunk.model_dump_json()}\n\n"

        # Simulate token generation delay (faster for demo)
        await asyncio.sleep(0.05)

    # Send final chunk with finish_reason
    final_chunk = ChatCompletionChunk(
        id=completion_id,
        created=created,
        choices=[
            {
                "index": 0,
                "delta": {},
                "finish_reason": "stop",
            }
        ],
    )
    yield f"data: {final_chunk.model_dump_json()}\n\n"

    # Signal stream completion (OpenAI convention)
    yield "data: [DONE]\n\n"


@app.post("/v1/chat/completions")
async def chat_completions(request: ChatRequest):
    """OpenAI-compatible chat completion endpoint.

    Supports both streaming and non-streaming modes via the 'stream' parameter.

    Args:
        request: Chat completion request with messages and options.

    Returns:
        Streaming or complete response based on request.stream.
    """
    completion_id = f"chatcmpl-{uuid4().hex[:12]}"
    created = int(time.time())

    if request.stream:
        return StreamingResponse(
            stream_tokens(request.messages, completion_id),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "X-Accel-Buffering": "no",
            },
        )

    # Non-streaming: collect full response
    response_text = get_response_text(request.messages)

    completion = ChatCompletion(
        id=completion_id,
        created=created,
        choices=[
            {
                "index": 0,
                "message": {"role": "assistant", "content": response_text},
                "finish_reason": "stop",
            }
        ],
        usage={
            "prompt_tokens": sum(len(m.content.split()) for m in request.messages),
            "completion_tokens": len(response_text.split()),
            "total_tokens": sum(len(m.content.split()) for m in request.messages)
            + len(response_text.split()),
        },
    )

    return JSONResponse(completion.model_dump())


# Additional endpoint showing simpler streaming pattern
@app.post("/chat/simple")
async def simple_chat(request: ChatRequest):
    """Simplified chat endpoint for demonstration.

    Args:
        request: Chat request.

    Returns:
        Streaming response with simpler format.
    """
    async def generate() -> AsyncGenerator[str, None]:
        response_text = get_response_text(request.messages)

        for word in response_text.split():
            data = {"token": word, "done": False}
            yield f"data: {json.dumps(data)}\n\n"
            await asyncio.sleep(0.05)

        yield f"data: {json.dumps({'token': '', 'done': True})}\n\n"

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
    )


# Demo function
async def demo() -> None:
    """Demonstrate LLM-style streaming."""
    print("=== LLM Streaming Example ===\n")

    messages = [
        ChatMessage(role="user", content="Hello, how are you?"),
    ]
    completion_id = f"chatcmpl-{uuid4().hex[:12]}"

    print("1. Streaming Response (token by token):")
    print("-" * 40)
    print("Assistant: ", end="", flush=True)

    full_response = ""
    async for chunk_str in stream_tokens(messages, completion_id):
        if chunk_str.startswith("data: ") and "[DONE]" not in chunk_str:
            try:
                chunk_data = json.loads(chunk_str[6:])
                content = chunk_data.get("choices", [{}])[0].get("delta", {}).get("content", "")
                if content:
                    print(content, end="", flush=True)
                    full_response += content
            except json.JSONDecodeError:
                pass

    print("\n")

    print("2. Response Statistics:")
    print("-" * 40)
    print(f"  Completion ID: {completion_id}")
    print(f"  Total tokens: {len(full_response.split())}")

    print("\n3. Chunk Format Example:")
    print("-" * 40)
    sample_chunk = ChatCompletionChunk(
        id=completion_id,
        created=int(time.time()),
        choices=[
            {
                "index": 0,
                "delta": {"content": "Hello"},
                "finish_reason": None,
            }
        ],
    )
    print(f"  {json.dumps(sample_chunk.model_dump(), indent=2)}")

    print("\n=== Example Complete ===")
    print("\nTo test with real HTTP requests, run:")
    print("  uvicorn dual_mode_streaming.examples.example_3_llm_streaming:app")
    print("\nThen try (streaming):")
    print("""  curl -X POST localhost:8000/v1/chat/completions \\
    -H "Content-Type: application/json" \\
    -d '{"messages": [{"role": "user", "content": "Hello!"}], "stream": true}'""")
    print("\nOr (non-streaming):")
    print("""  curl -X POST localhost:8000/v1/chat/completions \\
    -H "Content-Type: application/json" \\
    -d '{"messages": [{"role": "user", "content": "Hello!"}], "stream": false}'""")


if __name__ == "__main__":
    asyncio.run(demo())
