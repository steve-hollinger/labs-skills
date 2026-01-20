"""Exercise 3 Solution: LLM Response Simulator.

This solution demonstrates building an OpenAI-compatible completion
API with streaming support.
"""

import asyncio
import json
import time
from typing import AsyncGenerator
from uuid import uuid4

from fastapi import FastAPI
from fastapi.responses import JSONResponse, StreamingResponse
from pydantic import BaseModel

app = FastAPI(title="Exercise 3 Solution: LLM Simulator")


class CompletionRequest(BaseModel):
    """Completion request model."""

    prompt: str
    stream: bool = True
    max_tokens: int = 50
    temperature: float = 1.0  # Bonus: temperature parameter
    stop: list[str] | None = None  # Bonus: stop sequences


# Response templates
RESPONSES = {
    "joke": "Why don't scientists trust atoms? Because they make up everything! "
    "But seriously, atoms are the building blocks of matter, "
    "and understanding them is fundamental to physics and chemistry.",
    "story": "Once upon a time, in a land of code and algorithms, "
    "there lived a young developer who dreamed of creating the perfect API. "
    "Day and night they worked, until one day, streaming responses were born.",
    "explain": "Let me explain this concept step by step. "
    "First, we need to understand the basics. "
    "Then we can build upon that foundation to grasp more complex ideas. "
    "This methodical approach ensures thorough understanding.",
    "default": "Thank you for your prompt. I'm a simulated language model "
    "demonstrating streaming capabilities. Each word you see arrives as a "
    "separate token, just like real LLM APIs work.",
}


def get_response_for_prompt(prompt: str) -> str:
    """Select appropriate response based on prompt content."""
    prompt_lower = prompt.lower()
    for keyword, response in RESPONSES.items():
        if keyword in prompt_lower:
            return response
    return RESPONSES["default"]


def count_tokens(text: str) -> int:
    """Simple token counting (words as approximation).

    A real implementation would use a proper tokenizer.

    Args:
        text: Text to count tokens for.

    Returns:
        Approximate token count.
    """
    # Simple approximation: words + punctuation
    return len(text.split())


def check_stop_sequence(text: str, stop_sequences: list[str] | None) -> tuple[str, bool]:
    """Check for and handle stop sequences.

    Args:
        text: Text to check.
        stop_sequences: List of stop sequences.

    Returns:
        Tuple of (possibly truncated text, whether stopped).
    """
    if not stop_sequences:
        return text, False

    for seq in stop_sequences:
        if seq in text:
            return text.split(seq)[0], True

    return text, False


async def stream_tokens(
    prompt: str,
    completion_id: str,
    max_tokens: int,
    stop: list[str] | None = None,
) -> AsyncGenerator[str, None]:
    """Stream response tokens in OpenAI-compatible format.

    Args:
        prompt: The input prompt.
        completion_id: Unique completion ID.
        max_tokens: Maximum tokens to generate.
        stop: Optional stop sequences.

    Yields:
        SSE-formatted completion chunks.
    """
    response_text = get_response_for_prompt(prompt)
    tokens = response_text.split()
    created = int(time.time())

    # Limit to max_tokens
    tokens = tokens[:max_tokens]

    accumulated_text = ""
    for i, token in enumerate(tokens):
        # Build accumulated text for stop sequence checking
        accumulated_text += token + " "

        # Check for stop sequence
        _, should_stop = check_stop_sequence(accumulated_text, stop)

        is_last = (i == len(tokens) - 1) or should_stop

        chunk = {
            "id": completion_id,
            "object": "text_completion",
            "created": created,
            "choices": [
                {
                    "text": " " + token if i > 0 else token,
                    "index": 0,
                    "finish_reason": "stop" if is_last else None,
                }
            ],
        }
        yield f"data: {json.dumps(chunk)}\n\n"

        if should_stop:
            break

        # Simulate token generation delay
        await asyncio.sleep(0.05)

    # Signal stream completion
    yield "data: [DONE]\n\n"


@app.post("/v1/completions")
async def completions(request: CompletionRequest):
    """OpenAI-compatible completions endpoint.

    Args:
        request: Completion request.

    Returns:
        Streaming or batch response based on request.stream.
    """
    completion_id = f"cmpl-{uuid4().hex[:12]}"
    created = int(time.time())

    if request.stream:
        return StreamingResponse(
            stream_tokens(
                request.prompt,
                completion_id,
                request.max_tokens,
                request.stop,
            ),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "X-Request-ID": completion_id,
            },
        )

    # Non-streaming: return complete response
    response_text = get_response_for_prompt(request.prompt)
    tokens = response_text.split()[:request.max_tokens]
    final_text = " ".join(tokens)

    # Check for stop sequences
    final_text, _ = check_stop_sequence(final_text, request.stop)

    prompt_tokens = count_tokens(request.prompt)
    completion_tokens = count_tokens(final_text)

    response = {
        "id": completion_id,
        "object": "text_completion",
        "created": created,
        "choices": [
            {
                "text": final_text,
                "index": 0,
                "finish_reason": "stop",
            }
        ],
        "usage": {
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "total_tokens": prompt_tokens + completion_tokens,
        },
    }

    return JSONResponse(response)


# Bonus: Chat completions endpoint (more complex format)
class ChatMessage(BaseModel):
    """Chat message model."""

    role: str
    content: str


class ChatRequest(BaseModel):
    """Chat completion request."""

    messages: list[ChatMessage]
    stream: bool = True
    max_tokens: int = 100


async def stream_chat_tokens(
    messages: list[ChatMessage],
    completion_id: str,
    max_tokens: int,
) -> AsyncGenerator[str, None]:
    """Stream chat completion tokens."""
    # Get response based on last user message
    prompt = ""
    for msg in reversed(messages):
        if msg.role == "user":
            prompt = msg.content
            break

    response_text = get_response_for_prompt(prompt)
    tokens = response_text.split()[:max_tokens]
    created = int(time.time())

    for i, token in enumerate(tokens):
        is_last = i == len(tokens) - 1

        chunk = {
            "id": completion_id,
            "object": "chat.completion.chunk",
            "created": created,
            "choices": [
                {
                    "index": 0,
                    "delta": {
                        "role": "assistant" if i == 0 else None,
                        "content": " " + token if i > 0 else token,
                    },
                    "finish_reason": "stop" if is_last else None,
                }
            ],
        }
        # Remove None values from delta
        chunk["choices"][0]["delta"] = {
            k: v for k, v in chunk["choices"][0]["delta"].items() if v is not None
        }
        yield f"data: {json.dumps(chunk)}\n\n"
        await asyncio.sleep(0.05)

    yield "data: [DONE]\n\n"


@app.post("/v1/chat/completions")
async def chat_completions(request: ChatRequest):
    """OpenAI-compatible chat completions endpoint.

    Args:
        request: Chat completion request.

    Returns:
        Streaming or batch chat response.
    """
    completion_id = f"chatcmpl-{uuid4().hex[:12]}"
    created = int(time.time())

    if request.stream:
        return StreamingResponse(
            stream_chat_tokens(request.messages, completion_id, request.max_tokens),
            media_type="text/event-stream",
        )

    # Non-streaming
    prompt = ""
    for msg in reversed(request.messages):
        if msg.role == "user":
            prompt = msg.content
            break

    response_text = get_response_for_prompt(prompt)
    tokens = response_text.split()[:request.max_tokens]
    final_text = " ".join(tokens)

    response = {
        "id": completion_id,
        "object": "chat.completion",
        "created": created,
        "choices": [
            {
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": final_text,
                },
                "finish_reason": "stop",
            }
        ],
        "usage": {
            "prompt_tokens": sum(count_tokens(m.content) for m in request.messages),
            "completion_tokens": count_tokens(final_text),
            "total_tokens": sum(count_tokens(m.content) for m in request.messages)
            + count_tokens(final_text),
        },
    }

    return JSONResponse(response)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
