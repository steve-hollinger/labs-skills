"""
Solution 1: Chat Endpoint

Complete implementation of a chat streaming endpoint.
"""

import os
import json
import asyncio
from fastapi import FastAPI, Query
from fastapi.responses import StreamingResponse
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="Chat Endpoint Solution")


async def generate_chat_response(prompt: str, system_prompt: str = None):
    """Generate chat response as SSE events."""

    if os.getenv("OPENAI_API_KEY"):
        # Real OpenAI streaming
        from openai import OpenAI
        client = OpenAI()

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        try:
            stream = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
                stream=True,
                max_tokens=500
            )

            token_count = 0
            for chunk in stream:
                if chunk.choices[0].delta.content:
                    content = chunk.choices[0].delta.content
                    token_count += 1
                    data = json.dumps({
                        "content": content,
                        "token_index": token_count
                    })
                    yield f"data: {data}\n\n"

            # Final event with stats
            final = json.dumps({
                "type": "complete",
                "total_tokens": token_count
            })
            yield f"event: complete\ndata: {final}\n\n"

        except Exception as e:
            error = json.dumps({"type": "error", "error": str(e)})
            yield f"event: error\ndata: {error}\n\n"

    else:
        # Mock streaming response
        context = f" (Context: {system_prompt})" if system_prompt else ""
        response = f"Hello! I received your message: '{prompt}'.{context} "
        response += "This is a mock response streaming token by token. "
        response += "In production, this would be from an LLM."

        words = response.split()
        for i, word in enumerate(words):
            data = json.dumps({
                "content": word + " ",
                "token_index": i + 1
            })
            yield f"data: {data}\n\n"
            await asyncio.sleep(0.05)

        # Final event
        final = json.dumps({
            "type": "complete",
            "total_tokens": len(words)
        })
        yield f"event: complete\ndata: {final}\n\n"

    yield "data: [DONE]\n\n"


@app.get("/chat")
async def chat_endpoint(
    prompt: str = Query(..., description="User message"),
    system_prompt: str = Query(None, description="Optional system prompt")
):
    """Chat endpoint that streams responses."""
    return StreamingResponse(
        generate_chat_response(prompt, system_prompt),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        }
    )


@app.get("/")
async def info():
    has_key = bool(os.getenv("OPENAI_API_KEY"))
    return {
        "solution": "Chat Endpoint",
        "openai_configured": has_key,
        "endpoints": {"/chat": "Chat streaming endpoint"},
        "example": "/chat?prompt=Hello&system_prompt=Be+helpful"
    }


if __name__ == "__main__":
    import uvicorn
    print("Solution 1: Chat Endpoint")
    print("=" * 50)
    print('Test: curl -N "http://localhost:8010/chat?prompt=Hello"')
    uvicorn.run(app, host="0.0.0.0", port=8010)
