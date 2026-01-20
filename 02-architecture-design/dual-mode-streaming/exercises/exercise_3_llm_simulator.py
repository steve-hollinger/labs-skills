"""Exercise 3: Create LLM Response Simulator.

In this exercise, you'll build a simplified LLM API that streams responses
in an OpenAI-compatible format.

Requirements:
1. Create a POST endpoint at /v1/completions
2. Accept a JSON body with:
   - prompt: string
   - stream: boolean (default True)
   - max_tokens: int (default 50)
3. In stream mode:
   - Generate a response based on the prompt
   - Stream tokens one at a time with proper SSE formatting
   - Use OpenAI-compatible chunk format
   - End with "data: [DONE]"
4. In batch mode:
   - Return complete response in OpenAI-compatible format

Token chunk format:
{
    "id": "cmpl-xxx",
    "object": "text_completion",
    "created": 1234567890,
    "choices": [{
        "text": " token",
        "index": 0,
        "finish_reason": null  // or "stop" for last chunk
    }]
}

Complete response format:
{
    "id": "cmpl-xxx",
    "object": "text_completion",
    "created": 1234567890,
    "choices": [{
        "text": "full response text",
        "index": 0,
        "finish_reason": "stop"
    }],
    "usage": {
        "prompt_tokens": 10,
        "completion_tokens": 20,
        "total_tokens": 30
    }
}

Run your solution with:
    uvicorn exercises.exercise_3_llm_simulator:app --reload

Test with:
    # Streaming
    curl -X POST localhost:8000/v1/completions \\
        -H "Content-Type: application/json" \\
        -d '{"prompt": "Tell me a joke", "stream": true}'

    # Batch
    curl -X POST localhost:8000/v1/completions \\
        -H "Content-Type: application/json" \\
        -d '{"prompt": "Tell me a joke", "stream": false}'
"""

import time
from typing import AsyncGenerator
from uuid import uuid4

from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="Exercise 3: LLM Response Simulator")


class CompletionRequest(BaseModel):
    """Completion request model."""

    prompt: str
    stream: bool = True
    max_tokens: int = 50


# Response templates based on prompt keywords
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
    """Select appropriate response based on prompt content.

    Args:
        prompt: The user's prompt.

    Returns:
        Response text to generate.
    """
    prompt_lower = prompt.lower()
    for keyword, response in RESPONSES.items():
        if keyword in prompt_lower:
            return response
    return RESPONSES["default"]


# TODO: Implement the token streaming generator
async def stream_tokens(
    prompt: str,
    completion_id: str,
    max_tokens: int,
) -> AsyncGenerator[str, None]:
    """Stream response tokens in OpenAI-compatible format.

    Args:
        prompt: The input prompt.
        completion_id: Unique completion ID.
        max_tokens: Maximum tokens to generate.

    Yields:
        SSE-formatted completion chunks.

    Hints:
    - Get response text using get_response_for_prompt()
    - Split response into words (tokens)
    - Limit to max_tokens
    - For each token, create a chunk dict and yield as SSE
    - Add small delay (0.05s) between tokens for effect
    - Send final chunk with finish_reason="stop"
    - End with "data: [DONE]\\n\\n"
    """
    # Your implementation here
    raise NotImplementedError("Implement token streaming")


# TODO: Implement the /v1/completions endpoint
@app.post("/v1/completions")
async def completions(request: CompletionRequest):
    """OpenAI-compatible completions endpoint.

    Args:
        request: Completion request.

    Returns:
        Streaming or batch response based on request.stream.
    """
    # Your implementation here
    # 1. Generate completion_id
    # 2. If stream=True, return StreamingResponse with stream_tokens
    # 3. If stream=False, return complete response as JSON
    raise NotImplementedError("Implement this endpoint")


# Bonus Challenges:
# 1. Add support for 'temperature' parameter that affects response randomness
# 2. Implement proper token counting (hint: words is a simplification)
# 3. Add 'stop' sequences that terminate generation early


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
